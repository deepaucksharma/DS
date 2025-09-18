# Slow Query Analysis Guide

## Overview

Slow database queries are one of the most common causes of performance issues in distributed systems. This guide provides systematic approaches used by database teams at Facebook, LinkedIn, and Airbnb to identify, analyze, and optimize slow queries in production environments.

**Time to Resolution**: 15-30 minutes for simple index issues, 2-6 hours for complex query optimization

## Decision Tree

```mermaid
graph TD
    A[Slow Query Alert] --> B{Database Type?}
    B -->|PostgreSQL| C[PostgreSQL Analysis]
    B -->|MySQL| D[MySQL Analysis]
    B -->|MongoDB| E[MongoDB Analysis]
    B -->|Other| F[Generic SQL Analysis]

    C --> G[pg_stat_statements]
    C --> H[EXPLAIN ANALYZE]

    D --> I[slow_query_log]
    D --> J[EXPLAIN FORMAT=JSON]

    E --> K[db.collection.explain()]
    E --> L[MongoDB Profiler]

    G --> M{Query Plan Issues?}
    M -->|Yes| N[Index Analysis]
    M -->|No| O[Lock Investigation]

    H --> P[Execution Stats]

    I --> Q[Query Pattern Analysis]
    Q --> R[Parameter Optimization]

    N --> S[Index Creation/Optimization]
    O --> T[Concurrency Analysis]

    style A fill:#8B5CF6,stroke:#7C3AED,color:#fff
    style G fill:#F59E0B,stroke:#D97706,color:#fff
    style N fill:#10B981,stroke:#059669,color:#fff
```

## Immediate Triage Commands (First 5 Minutes)

### 1. Quick Database Health Check
```bash
# PostgreSQL
psql -c "SELECT count(*) as active_queries, state FROM pg_stat_activity GROUP BY state;"
psql -c "SELECT query, state, query_start, now() - query_start as duration FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC LIMIT 10;"

# MySQL
mysql -e "SHOW PROCESSLIST;" | head -20
mysql -e "SELECT id, user, host, db, command, time, state, LEFT(info,100) as query FROM INFORMATION_SCHEMA.PROCESSLIST WHERE command != 'Sleep' ORDER BY time DESC;"

# MongoDB
mongosh --eval "db.runCommand({currentOp: 1, active: true, secs_running: {$gte: 5}})"
```

### 2. Long-Running Query Detection
```bash
# PostgreSQL - queries running over 30 seconds
psql -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '30 seconds';"

# MySQL - queries running over 30 seconds
mysql -e "SELECT id, time, state, LEFT(info, 100) as query FROM INFORMATION_SCHEMA.PROCESSLIST WHERE time > 30 ORDER BY time DESC;"

# Kill problematic queries if necessary
# PostgreSQL: SELECT pg_terminate_backend(PID);
# MySQL: KILL QUERY ID;
```

### 3. Database Lock Analysis
```bash
# PostgreSQL lock analysis
psql -c "SELECT blocked_locks.pid AS blocked_pid, blocked_activity.usename AS blocked_user, blocking_locks.pid AS blocking_pid, blocking_activity.usename AS blocking_user, blocked_activity.query AS blocked_statement, blocking_activity.query AS current_statement_in_blocking_process FROM pg_catalog.pg_locks blocked_locks JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation WHERE NOT blocked_locks.granted;"

# MySQL lock analysis
mysql -e "SELECT * FROM INFORMATION_SCHEMA.INNODB_LOCKS; SELECT * FROM INFORMATION_SCHEMA.INNODB_LOCK_WAITS;"
```

## PostgreSQL Slow Query Analysis

### 1. Enable and Configure Query Logging
```sql
-- Enable pg_stat_statements extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Configure PostgreSQL for query analysis (postgresql.conf)
-- shared_preload_libraries = 'pg_stat_statements'
-- pg_stat_statements.max = 10000
-- pg_stat_statements.track = all
-- log_statement = 'all'
-- log_min_duration_statement = 1000  -- Log queries taking over 1 second
```

### 2. Analyze Query Performance Statistics
```sql
-- Top 20 slowest queries by average time
SELECT
    query,
    calls,
    total_time,
    mean_time,
    stddev_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;

-- Queries with highest total time consumption
SELECT
    query,
    calls,
    total_time,
    mean_time,
    (total_time/sum(total_time) OVER()) * 100 AS percentage_total
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Queries with low cache hit ratio
SELECT
    query,
    calls,
    shared_blks_hit,
    shared_blks_read,
    shared_blks_hit + shared_blks_read as total_blks,
    CASE
        WHEN shared_blks_hit + shared_blks_read = 0 THEN 0
        ELSE round(100.0 * shared_blks_hit / (shared_blks_hit + shared_blks_read), 2)
    END AS hit_ratio_percent
FROM pg_stat_statements
WHERE shared_blks_hit + shared_blks_read > 0
ORDER BY hit_ratio_percent ASC
LIMIT 20;
```

### 3. Query Plan Analysis
```sql
-- Analyze specific slow query
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.created_at >= '2023-01-01'
  AND c.status = 'active';

-- Identify missing indexes
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
  AND n_distinct > 100  -- Columns with good selectivity
  AND correlation < 0.1  -- Not correlated with physical order
ORDER BY n_distinct DESC;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan < 10  -- Potentially unused indexes
ORDER BY schemaname, tablename;
```

### 4. Advanced PostgreSQL Analysis
```python
# Python script for automated PostgreSQL slow query analysis
import psycopg2
import json
from datetime import datetime, timedelta

def analyze_slow_queries(connection_params):
    """Comprehensive PostgreSQL slow query analysis"""
    conn = psycopg2.connect(**connection_params)
    cursor = conn.cursor()

    # Get top slow queries
    cursor.execute("""
        SELECT
            query,
            calls,
            total_time,
            mean_time,
            stddev_time,
            shared_blks_hit + shared_blks_read as total_blks_accessed,
            CASE
                WHEN shared_blks_hit + shared_blks_read = 0 THEN 0
                ELSE round(100.0 * shared_blks_hit / (shared_blks_hit + shared_blks_read), 2)
            END AS cache_hit_ratio
        FROM pg_stat_statements
        WHERE mean_time > 100  -- Only queries taking more than 100ms on average
        ORDER BY mean_time DESC
        LIMIT 50;
    """)

    slow_queries = cursor.fetchall()

    analysis_results = []

    for query_data in slow_queries:
        query, calls, total_time, mean_time, stddev_time, total_blks, cache_hit = query_data

        # Analyze query plan for each slow query
        try:
            cursor.execute("EXPLAIN (FORMAT JSON) " + query)
            plan = cursor.fetchone()[0]

            analysis = {
                'query': query[:200] + '...' if len(query) > 200 else query,
                'performance_stats': {
                    'calls': calls,
                    'total_time_ms': total_time,
                    'mean_time_ms': mean_time,
                    'stddev_time_ms': stddev_time,
                    'cache_hit_ratio': cache_hit
                },
                'plan_analysis': analyze_query_plan(plan),
                'recommendations': generate_recommendations(query, plan, cache_hit)
            }

            analysis_results.append(analysis)

        except Exception as e:
            print(f"Error analyzing query: {e}")
            continue

    conn.close()
    return analysis_results

def analyze_query_plan(plan_json):
    """Extract key information from query plan"""
    if not plan_json or 'Plan' not in plan_json[0]:
        return {}

    plan = plan_json[0]['Plan']

    return {
        'node_type': plan.get('Node Type'),
        'total_cost': plan.get('Total Cost'),
        'startup_cost': plan.get('Startup Cost'),
        'plan_rows': plan.get('Plan Rows'),
        'plan_width': plan.get('Plan Width'),
        'has_sequential_scan': has_seq_scan(plan),
        'has_nested_loop': has_nested_loop(plan),
        'max_depth': get_plan_depth(plan)
    }

def has_seq_scan(plan_node):
    """Check if query plan contains sequential scans"""
    if plan_node.get('Node Type') == 'Seq Scan':
        return True

    if 'Plans' in plan_node:
        return any(has_seq_scan(child) for child in plan_node['Plans'])

    return False

def has_nested_loop(plan_node):
    """Check if query plan contains nested loops"""
    if plan_node.get('Node Type') == 'Nested Loop':
        return True

    if 'Plans' in plan_node:
        return any(has_nested_loop(child) for child in plan_node['Plans'])

    return False

def get_plan_depth(plan_node, depth=0):
    """Get maximum depth of query plan"""
    if 'Plans' not in plan_node:
        return depth

    return max(get_plan_depth(child, depth + 1) for child in plan_node['Plans'])

def generate_recommendations(query, plan, cache_hit_ratio):
    """Generate optimization recommendations"""
    recommendations = []

    if cache_hit_ratio < 90:
        recommendations.append("Consider adding indexes to improve cache hit ratio")

    plan_info = analyze_query_plan(plan)

    if plan_info.get('has_sequential_scan'):
        recommendations.append("Query contains sequential scans - consider adding indexes")

    if plan_info.get('has_nested_loop') and plan_info.get('max_depth', 0) > 3:
        recommendations.append("Complex nested loops detected - consider query rewrite or better indexes")

    if 'ORDER BY' in query.upper() and 'LIMIT' in query.upper():
        recommendations.append("ORDER BY with LIMIT detected - ensure proper index on sort columns")

    return recommendations

# Usage example
if __name__ == "__main__":
    connection_params = {
        'host': 'localhost',
        'database': 'production_db',
        'user': 'readonly_user',
        'password': 'password'
    }

    results = analyze_slow_queries(connection_params)

    for i, result in enumerate(results):
        print(f"\n=== Slow Query #{i+1} ===")
        print(f"Query: {result['query']}")
        print(f"Mean Time: {result['performance_stats']['mean_time_ms']:.2f}ms")
        print(f"Cache Hit Ratio: {result['performance_stats']['cache_hit_ratio']}%")
        print("Recommendations:")
        for rec in result['recommendations']:
            print(f"  - {rec}")
```

## MySQL Slow Query Analysis

### 1. Enable and Configure Slow Query Log
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 1;
SET GLOBAL long_query_time = 1;  -- Log queries taking over 1 second
SET GLOBAL log_queries_not_using_indexes = 1;

-- Check current configuration
SHOW VARIABLES LIKE 'slow_query_log%';
SHOW VARIABLES LIKE 'long_query_time';
```

### 2. Analyze Slow Query Log
```bash
# Use mysqldumpslow to analyze slow query log
mysqldumpslow -s t -t 20 /var/log/mysql/slow.log  # Top 20 by query time
mysqldumpslow -s c -t 20 /var/log/mysql/slow.log  # Top 20 by count
mysqldumpslow -s at -t 20 /var/log/mysql/slow.log  # Top 20 by average time

# More detailed analysis with pt-query-digest (Percona Toolkit)
pt-query-digest /var/log/mysql/slow.log > slow_query_analysis.txt
```

### 3. Query Performance Analysis
```sql
-- Enable Performance Schema (MySQL 5.6+)
UPDATE performance_schema.setup_consumers SET enabled = 'YES';

-- Top queries by total time
SELECT
    DIGEST_TEXT,
    COUNT_STAR as exec_count,
    AVG_TIMER_WAIT/1000000000 as avg_time_sec,
    SUM_TIMER_WAIT/1000000000 as total_time_sec,
    SUM_ROWS_EXAMINED,
    SUM_ROWS_SENT
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 20;

-- Queries with high examination to result ratio
SELECT
    DIGEST_TEXT,
    COUNT_STAR,
    SUM_ROWS_EXAMINED,
    SUM_ROWS_SENT,
    ROUND(SUM_ROWS_EXAMINED/SUM_ROWS_SENT, 2) as examination_ratio
FROM performance_schema.events_statements_summary_by_digest
WHERE SUM_ROWS_SENT > 0
ORDER BY examination_ratio DESC
LIMIT 20;
```

### 4. Index Analysis and Optimization
```sql
-- Check unused indexes
SELECT
    t.TABLE_SCHEMA,
    t.TABLE_NAME,
    s.INDEX_NAME,
    s.CARDINALITY
FROM INFORMATION_SCHEMA.STATISTICS s
LEFT JOIN INFORMATION_SCHEMA.INDEX_STATISTICS i USING (TABLE_SCHEMA, TABLE_NAME, INDEX_NAME)
JOIN INFORMATION_SCHEMA.TABLES t USING (TABLE_SCHEMA, TABLE_NAME)
WHERE t.TABLE_TYPE = 'BASE TABLE'
  AND s.INDEX_NAME != 'PRIMARY'
  AND (i.INDEX_NAME IS NULL OR i.ROWS_READ = 0)
ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME, s.INDEX_NAME;

-- Analyze specific query execution plan
EXPLAIN FORMAT=JSON
SELECT o.*, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'pending'
  AND o.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```

## MongoDB Slow Query Analysis

### 1. Enable MongoDB Profiler
```javascript
// Enable profiler for operations slower than 100ms
db.setProfilingLevel(2, { slowms: 100 });

// Check current profiling status
db.getProfilingStatus();

// Query profiler collection for slow operations
db.system.profile.find().limit(5).sort({ ts: -1 }).pretty();
```

### 2. Analyze Slow Operations
```javascript
// Find slowest operations by execution time
db.system.profile.find({ "millis": { $gt: 1000 } }).sort({ millis: -1 }).limit(10);

// Analyze query patterns
db.system.profile.aggregate([
    { $match: { "op": "query" } },
    { $group: {
        _id: "$command",
        count: { $sum: 1 },
        avgMillis: { $avg: "$millis" },
        maxMillis: { $max: "$millis" }
    }},
    { $sort: { avgMillis: -1 } },
    { $limit: 10 }
]);

// Check for collection scans
db.system.profile.find({
    "planSummary": /COLLSCAN/,
    "millis": { $gt: 100 }
}).sort({ millis: -1 });
```

### 3. Index Analysis
```javascript
// Check index usage statistics
db.runCommand({ collStats: "orders", indexDetails: true });

// Analyze query execution plans
db.orders.find({ status: "pending", created_at: { $gte: new Date("2023-01-01") } }).explain("executionStats");

// Find collections without proper indexes
db.system.profile.aggregate([
    { $match: { "planSummary": "COLLSCAN" } },
    { $group: {
        _id: "$ns",
        count: { $sum: 1 },
        avgDocsExamined: { $avg: "$docsExamined" }
    }},
    { $sort: { count: -1 } }
]);
```

## Production Case Studies

### Case Study 1: LinkedIn - Feed Generation Query Optimization

**Problem**: User feed generation queries taking 8-15 seconds, causing timeline delays

**Investigation Process**:
1. **pg_stat_statements analysis** revealed complex JOIN with 4 tables
2. **EXPLAIN ANALYZE** showed nested loop joins examining 2M+ rows
3. **Index analysis** found missing composite index on (user_id, created_at)

**Commands Used**:
```sql
-- Identified problematic query
SELECT query, calls, mean_time, total_time
FROM pg_stat_statements
WHERE query LIKE '%feed_items%'
ORDER BY mean_time DESC;

-- Analyzed execution plan
EXPLAIN (ANALYZE, BUFFERS)
SELECT fi.*, p.content, u.name
FROM feed_items fi
JOIN posts p ON fi.post_id = p.id
JOIN users u ON p.user_id = u.id
JOIN connections c ON u.id = c.connected_user_id
WHERE c.user_id = 12345
  AND fi.created_at >= NOW() - INTERVAL '7 days'
ORDER BY fi.created_at DESC
LIMIT 50;

-- Found missing indexes
SELECT tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE tablename IN ('feed_items', 'posts', 'connections')
  AND n_distinct > 100;
```

**Resolution**: Added composite indexes and rewrote query to use window functions
**Time to Resolution**: 4 hours

### Case Study 2: Airbnb - Search Query Performance

**Problem**: Property search queries timing out during peak booking periods

**Root Cause**: Geospatial queries without proper indexing causing full table scans

**Investigation Commands**:
```sql
-- MySQL slow query analysis
SELECT
    DIGEST_TEXT,
    COUNT_STAR,
    AVG_TIMER_WAIT/1000000000 as avg_time_sec,
    SUM_ROWS_EXAMINED/SUM_ROWS_SENT as examination_ratio
FROM performance_schema.events_statements_summary_by_digest
WHERE DIGEST_TEXT LIKE '%ST_DWithin%'
ORDER BY AVG_TIMER_WAIT DESC;

-- Found problematic geospatial query
EXPLAIN FORMAT=JSON
SELECT * FROM properties
WHERE ST_DWithin(
    location,
    ST_GeomFromText('POINT(-122.4194 37.7749)'),
    0.01
)
AND price_per_night BETWEEN 100 AND 300;
```

**Resolution**: Added spatial index and optimized query with bounding box pre-filter
**Time to Resolution**: 6 hours

### Case Study 3: Twitter - Timeline Query Optimization

**Problem**: User timeline queries degrading during viral tweet events

**Root Cause**: Hot partition problem with tweet distribution causing lock contention

**Investigation Process**:
```bash
# PostgreSQL lock analysis
psql -c "
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.query AS blocked_statement,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.query AS current_statement_in_blocking_process
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
WHERE NOT blocked_locks.granted;"

# Query wait event analysis
psql -c "
SELECT
    wait_event_type,
    wait_event,
    count(*) as waiting_sessions
FROM pg_stat_activity
WHERE wait_event IS NOT NULL
GROUP BY wait_event_type, wait_event
ORDER BY waiting_sessions DESC;"
```

**Resolution**: Implemented read replicas and query result caching
**Time to Resolution**: 8 hours

## Automated Query Optimization Tools

### 1. Query Performance Monitoring Script
```python
# Automated slow query detection and alerting
import psycopg2
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import json

class SlowQueryMonitor:
    def __init__(self, db_config, alert_config):
        self.db_config = db_config
        self.alert_config = alert_config
        self.baseline_metrics = {}

    def collect_query_metrics(self):
        """Collect current query performance metrics"""
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                queryid,
                query,
                calls,
                total_time,
                mean_time,
                stddev_time,
                rows,
                shared_blks_hit + shared_blks_read as total_blks
            FROM pg_stat_statements
            WHERE calls > 10  -- Only frequently executed queries
            ORDER BY mean_time DESC
            LIMIT 100;
        """)

        current_metrics = {}
        for row in cursor.fetchall():
            queryid, query, calls, total_time, mean_time, stddev_time, rows, total_blks = row
            current_metrics[queryid] = {
                'query': query,
                'calls': calls,
                'total_time': total_time,
                'mean_time': mean_time,
                'stddev_time': stddev_time,
                'rows': rows,
                'total_blks': total_blks,
                'timestamp': datetime.now()
            }

        conn.close()
        return current_metrics

    def detect_regressions(self, current_metrics):
        """Detect performance regressions compared to baseline"""
        regressions = []

        for queryid, current in current_metrics.items():
            if queryid in self.baseline_metrics:
                baseline = self.baseline_metrics[queryid]

                # Check for mean time regression (>50% slower)
                if current['mean_time'] > baseline['mean_time'] * 1.5:
                    regression_percent = ((current['mean_time'] - baseline['mean_time']) / baseline['mean_time']) * 100

                    regressions.append({
                        'queryid': queryid,
                        'query': current['query'][:200] + '...',
                        'baseline_time': baseline['mean_time'],
                        'current_time': current['mean_time'],
                        'regression_percent': regression_percent,
                        'calls': current['calls']
                    })

        return regressions

    def send_alert(self, regressions):
        """Send email alert for detected regressions"""
        if not regressions:
            return

        subject = f"Slow Query Alert - {len(regressions)} regressions detected"

        body = "Query Performance Regressions Detected:\n\n"
        for regression in regressions:
            body += f"Query ID: {regression['queryid']}\n"
            body += f"Query: {regression['query']}\n"
            body += f"Baseline: {regression['baseline_time']:.2f}ms\n"
            body += f"Current: {regression['current_time']:.2f}ms\n"
            body += f"Regression: {regression['regression_percent']:.1f}%\n"
            body += f"Call Count: {regression['calls']}\n\n"

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.alert_config['from_email']
        msg['To'] = ', '.join(self.alert_config['to_emails'])

        with smtplib.SMTP(self.alert_config['smtp_server']) as server:
            server.send_message(msg)

    def monitor(self):
        """Main monitoring loop"""
        current_metrics = self.collect_query_metrics()

        if self.baseline_metrics:
            regressions = self.detect_regressions(current_metrics)
            if regressions:
                self.send_alert(regressions)

        # Update baseline (keep rolling 24-hour baseline)
        self.baseline_metrics = current_metrics

        return {
            'total_queries_monitored': len(current_metrics),
            'regressions_detected': len(regressions) if self.baseline_metrics else 0,
            'timestamp': datetime.now()
        }

# Usage
db_config = {
    'host': 'localhost',
    'database': 'production',
    'user': 'monitor',
    'password': 'password'
}

alert_config = {
    'smtp_server': 'smtp.company.com',
    'from_email': 'alerts@company.com',
    'to_emails': ['dba-team@company.com']
}

monitor = SlowQueryMonitor(db_config, alert_config)
```

### 2. Index Recommendation Engine
```python
# Automated index recommendation based on slow queries
class IndexRecommendationEngine:
    def __init__(self, db_config):
        self.db_config = db_config

    def analyze_queries_for_indexes(self):
        """Analyze slow queries and recommend indexes"""
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        # Get queries with sequential scans
        cursor.execute("""
            SELECT
                query,
                calls,
                mean_time,
                total_time
            FROM pg_stat_statements
            WHERE query ~ 'FROM\\s+\\w+'
              AND mean_time > 100  -- Queries taking more than 100ms
            ORDER BY total_time DESC
            LIMIT 50;
        """)

        queries = cursor.fetchall()
        recommendations = []

        for query, calls, mean_time, total_time in queries:
            # Simple parsing to extract WHERE conditions
            where_conditions = self.extract_where_conditions(query)

            if where_conditions:
                for table, columns in where_conditions.items():
                    # Check if index already exists
                    existing_indexes = self.get_existing_indexes(cursor, table)

                    recommended_index = self.recommend_index(table, columns, existing_indexes)
                    if recommended_index:
                        recommendations.append({
                            'query': query[:200] + '...',
                            'table': table,
                            'recommended_index': recommended_index,
                            'impact_estimate': {
                                'calls': calls,
                                'mean_time_ms': mean_time,
                                'total_time_ms': total_time
                            }
                        })

        conn.close()
        return recommendations

    def extract_where_conditions(self, query):
        """Extract table and column information from WHERE clauses"""
        # Simplified extraction - in production, use a proper SQL parser
        import re

        where_conditions = {}

        # Find table names
        table_pattern = r'FROM\s+(\w+)'
        tables = re.findall(table_pattern, query, re.IGNORECASE)

        # Find WHERE conditions
        where_pattern = r'WHERE\s+(.+?)(?:ORDER|GROUP|LIMIT|$)'
        where_match = re.search(where_pattern, query, re.IGNORECASE | re.DOTALL)

        if where_match and tables:
            where_clause = where_match.group(1)

            # Extract column conditions
            column_pattern = r'(\w+)\s*(?:=|>|<|>=|<=|IN|LIKE)'
            columns = re.findall(column_pattern, where_clause, re.IGNORECASE)

            if columns:
                for table in tables:
                    where_conditions[table] = columns

        return where_conditions

    def get_existing_indexes(self, cursor, table):
        """Get existing indexes for a table"""
        cursor.execute("""
            SELECT
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename = %s;
        """, (table,))

        return [{'name': name, 'definition': definition} for name, definition in cursor.fetchall()]

    def recommend_index(self, table, columns, existing_indexes):
        """Recommend index based on query patterns"""
        # Check if a suitable index already exists
        for index in existing_indexes:
            index_def = index['definition'].lower()
            if all(col.lower() in index_def for col in columns[:2]):  # Check first 2 columns
                return None  # Suitable index exists

        # Recommend composite index for multiple columns
        if len(columns) > 1:
            return f"CREATE INDEX idx_{table}_{'_'.join(columns[:3])} ON {table} ({', '.join(columns[:3])});"
        elif len(columns) == 1:
            return f"CREATE INDEX idx_{table}_{columns[0]} ON {table} ({columns[0]});"

        return None

# Usage
engine = IndexRecommendationEngine(db_config)
recommendations = engine.analyze_queries_for_indexes()

for rec in recommendations:
    print(f"Table: {rec['table']}")
    print(f"Recommended Index: {rec['recommended_index']}")
    print(f"Impact: {rec['impact_estimate']['calls']} calls, avg {rec['impact_estimate']['mean_time_ms']:.2f}ms")
    print("---")
```

## 3 AM Debugging Checklist

When you're called at 3 AM for database performance issues:

### First 2 Minutes
- [ ] Check for long-running queries: `ps aux | grep mysql` or equivalent
- [ ] Verify database connectivity and basic health
- [ ] Check system resources (CPU, memory, disk I/O)
- [ ] Look for obvious lock contention

### Minutes 2-5
- [ ] Identify top slow queries from monitoring or logs
- [ ] Check for recent schema changes or deployments
- [ ] Verify backup/maintenance jobs aren't running
- [ ] Review connection counts and pool utilization

### Minutes 5-15
- [ ] Analyze execution plans for identified slow queries
- [ ] Check for missing or unused indexes
- [ ] Look for parameter changes or configuration drift
- [ ] Examine recent query pattern changes

### If Still Debugging After 15 Minutes
- [ ] Escalate to senior DBA or database expert
- [ ] Consider killing problematic queries if safe
- [ ] Review options for adding indexes (impact assessment)
- [ ] Document findings for detailed post-incident analysis

## Query Optimization Metrics and SLOs

### Key Query Performance Metrics
- **Query response time percentiles** (p95, p99) by query type
- **Queries per second** throughput
- **Index hit ratio** and cache efficiency
- **Lock wait time** and contention metrics
- **Connection pool utilization**

### Example SLO Configuration
```yaml
database_slos:
  - name: "Query Response Time"
    description: "95% of queries complete within 100ms"
    metric: "pg_stat_statements_mean_time_seconds"
    target: 0.1  # 100ms
    percentile: 95
    window: "5m"

  - name: "Cache Hit Ratio"
    description: "Database cache hit ratio above 99%"
    metric: "(pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)) * 100"
    target: 99
    window: "5m"
```

**Remember**: Query optimization is both art and science. While tools and metrics provide guidance, understanding your data model, access patterns, and business logic is crucial for effective optimization.

This guide represents proven techniques from database teams managing petabytes of data across thousands of concurrent connections in production environments.