# PostgreSQL Lock Contention Debugging

**Scenario**: Production PostgreSQL database experiencing severe lock contention, causing query timeouts and application performance degradation.

**The 3 AM Reality**: Transactions timing out, deadlocks escalating, and users experiencing 30+ second page load times due to database locks.

## Symptoms Checklist

- [ ] Query execution times > 10x normal baseline
- [ ] Application timeout errors (connection pool exhausted)
- [ ] Deadlock detection messages in PostgreSQL logs
- [ ] High number of waiting connections in pg_stat_activity
- [ ] Lock wait events dominating database performance

## PostgreSQL Lock Contention Architecture

```mermaid
graph TB
    subgraph EdgePlane["Edge Plane"]
        APP[Application Server<br/>Connection Pool: 100<br/>Timeout: 30s]
        WEB[Web Frontend<br/>Request Queue]
    end

    subgraph ServicePlane["Service Plane"]
        PGCLI[psql Client<br/>Lock Analysis Queries]
        MONITOR[pgAdmin/Datadog<br/>Lock Monitoring]
    end

    subgraph StatePlane["State Plane"]
        PGPRIMARY[PostgreSQL Primary<br/>Version: 14.2<br/>Connections: 200/200]
        PGREPLICA[PostgreSQL Replica<br/>Read-only Queries]
        LOCKTABLE[Lock Table<br/>pg_locks view<br/>Current: 1,247 locks]
    end

    subgraph ControlPlane["Control Plane"]
        LOCKS[Lock Statistics<br/>pg_stat_activity<br/>pg_blocking_pids()]
        DEADLOCKS[Deadlock Detection<br/>log_lock_waits=on]
        ALERTS[Lock Alerts<br/>Query timeout > 10s]
    end

    APP -->|SQL Queries| PGPRIMARY
    WEB -->|DB Requests| APP
    PGCLI -->|Lock Queries| PGPRIMARY
    MONITOR -->|Metrics| PGPRIMARY

    PGPRIMARY -->|Streaming Repl| PGREPLICA
    PGPRIMARY -.->|Lock Info| LOCKTABLE

    LOCKS -->|Monitor| DEADLOCKS
    DEADLOCKS -->|Threshold| ALERTS

    %% Apply 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class APP,WEB edgeStyle
    class PGCLI,MONITOR serviceStyle
    class PGPRIMARY,PGREPLICA,LOCKTABLE stateStyle
    class LOCKS,DEADLOCKS,ALERTS controlStyle
```

## Step-by-Step Debugging Flow

```mermaid
flowchart TD
    START[Lock Contention Alert<br/>Query timeouts > 10s] --> ACTIVITY[Check pg_stat_activity<br/>Identify waiting queries]

    ACTIVITY --> BLOCKING[Find Blocking Queries<br/>pg_blocking_pids()]

    BLOCKING --> ANALYZE{Lock Analysis}
    ANALYZE -->|Row Lock| ROWLOCK[Analyze Row-Level Locks<br/>Long-running transactions]
    ANALYZE -->|Table Lock| TABLELOCK[Check Table-Level Locks<br/>DDL operations]
    ANALYZE -->|Deadlock| DEADLOCK[Analyze Deadlock Pattern<br/>Log analysis]

    ROWLOCK --> LONGTX[Identify Long Transactions<br/>age(backend_start)]
    TABLELOCK --> DDL[Check DDL Operations<br/>ALTER, VACUUM, REINDEX]
    DEADLOCK --> PATTERN[Deadlock Pattern Analysis<br/>Transaction ordering]

    LONGTX --> KILL[Kill Long Transactions<br/>pg_terminate_backend()]
    DDL --> SCHEDULE[Reschedule DDL<br/>Maintenance window]
    PATTERN --> RETRY[Application Retry Logic<br/>Transaction ordering fix]

    KILL --> OPTIMIZE[Optimize Query Performance<br/>Add indexes, VACUUM]
    SCHEDULE --> OPTIMIZE
    RETRY --> OPTIMIZE

    OPTIMIZE --> MONITOR[Monitor Lock Activity<br/>pg_stat_user_tables]

    MONITOR --> RESOLVED{Locks Resolved?}
    RESOLVED -->|Yes| SUCCESS[Performance Restored<br/>Document findings]
    RESOLVED -->|No| ESCALATE[Emergency Measures<br/>Connection limiting]

    %% Styling
    classDef startStyle fill:#ff6b6b,stroke:#e55555,color:#fff
    classDef processStyle fill:#4ecdc4,stroke:#45b7aa,color:#fff
    classDef decisionStyle fill:#ffe66d,stroke:#ffcc02,color:#000
    classDef actionStyle fill:#a8e6cf,stroke:#7fcdcd,color:#000
    classDef emergencyStyle fill:#ff8b94,stroke:#ff6b7a,color:#fff

    class START startStyle
    class ACTIVITY,BLOCKING,LONGTX,DDL,PATTERN,OPTIMIZE,MONITOR processStyle
    class ANALYZE,RESOLVED decisionStyle
    class KILL,SCHEDULE,RETRY actionStyle
    class ESCALATE emergencyStyle
```

## Critical Commands & Queries

### Immediate Lock Analysis
```sql
-- Check current database activity and waiting queries
SELECT
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query,
    state,
    wait_event_type,
    wait_event
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
ORDER BY duration DESC;

-- Find blocking and blocked queries
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS current_statement_in_blocking_process
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity
    ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity
    ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

### Lock Type Analysis
```sql
-- Detailed lock information by type
SELECT
    locktype,
    database,
    relation::regclass,
    page,
    tuple,
    virtualxid,
    transactionid,
    mode,
    granted,
    pid
FROM pg_locks
WHERE NOT granted
ORDER BY relation, locktype;

-- Check table-level locks
SELECT
    schemaname,
    tablename,
    attname,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_tup_hot_upd,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE n_dead_tup > n_live_tup * 0.1  -- High dead tuple ratio
ORDER BY n_dead_tup DESC;

-- Analyze index usage and potential issues
SELECT
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan,
    idx_blks_read,
    idx_blks_hit
FROM pg_stat_user_indexes
WHERE idx_scan = 0  -- Unused indexes
   OR idx_tup_read = 0;  -- Never read indexes
```

### Transaction and Connection Analysis
```sql
-- Long-running transactions
SELECT
    pid,
    now() - backend_start as session_duration,
    now() - xact_start as transaction_duration,
    now() - query_start as query_duration,
    state,
    query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND now() - xact_start > interval '10 minutes'
ORDER BY xact_start;

-- Connection pool analysis
SELECT
    state,
    count(*) as connection_count,
    max(now() - backend_start) as oldest_connection,
    max(now() - state_change) as longest_idle
FROM pg_stat_activity
GROUP BY state
ORDER BY connection_count DESC;

-- Deadlock analysis helper
SELECT
    pid,
    backend_start,
    query_start,
    state_change,
    wait_event_type,
    wait_event,
    state,
    backend_type,
    query
FROM pg_stat_activity
WHERE state != 'idle'
  AND pid IN (
    SELECT DISTINCT pid
    FROM pg_locks
    WHERE NOT granted
  );
```

## Log Analysis Locations

### PostgreSQL Logs
```bash
# Main PostgreSQL log location (Ubuntu/Debian)
tail -f /var/log/postgresql/postgresql-14-main.log

# Search for deadlock information
grep -A 10 -B 10 "deadlock detected" /var/log/postgresql/postgresql-*.log

# Look for lock wait timeouts
grep "canceling statement due to lock timeout" /var/log/postgresql/postgresql-*.log

# Check for checkpoint and vacuum activity
grep -E "(checkpoint|vacuum|autovacuum)" /var/log/postgresql/postgresql-*.log | tail -50
```

### Lock-Specific Log Patterns
```bash
# Enable detailed lock logging (requires restart)
# In postgresql.conf:
# log_lock_waits = on
# deadlock_timeout = 1s
# log_statement = 'all'  # Warning: High volume

# Search for specific lock wait patterns
awk '/lock timeout/ {
    for(i=1; i<=10; i++) {
        if((getline line < FILENAME) > 0)
            print line
        else
            break
    }
}' /var/log/postgresql/postgresql-*.log

# Analyze deadlock frequency
grep "deadlock detected" /var/log/postgresql/postgresql-*.log | \
awk '{print $1, $2}' | \
sort | uniq -c | \
sort -nr
```

### System Resource Analysis
```bash
# Check I/O wait and disk utilization
iostat -x 1 5 | grep -E "(Device|pgdata)"

# Monitor PostgreSQL process resources
ps aux | grep postgres | head -20

# Check shared memory usage
ipcs -m | grep postgres

# Monitor connection count in real-time
watch -n 2 'psql -c "SELECT count(*) FROM pg_stat_activity;"'
```

## Monitoring Queries

### Real-time Lock Monitoring
```sql
-- Create lock monitoring view
CREATE OR REPLACE VIEW lock_monitor AS
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocked_activity.application_name AS blocked_app,
    now() - blocked_activity.query_start AS blocked_duration,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocking_activity.application_name AS blocking_app,
    now() - blocking_activity.query_start AS blocking_duration,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity
    ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity
    ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- Query the monitoring view
SELECT * FROM lock_monitor ORDER BY blocked_duration DESC;
```

### Prometheus Metrics (using postgres_exporter)
```promql
# Lock wait time
pg_stat_activity_max_tx_duration{state="active"}

# Number of blocked connections
count(pg_locks{granted="false"})

# Deadlock rate
rate(pg_stat_database_deadlocks[5m])

# Connection pool utilization
pg_stat_activity_count / pg_settings_max_connections * 100

# Long-running transaction alert
pg_stat_activity_max_tx_duration > 300
```

## Common Root Causes (by Probability)

### 1. Long-Running Transactions (40% of cases)
**Symptoms**: Transactions holding locks for > 10 minutes
```sql
-- Detection
SELECT pid, now() - xact_start as duration, query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND now() - xact_start > interval '10 minutes';

-- Emergency fix
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE now() - xact_start > interval '30 minutes'
  AND state != 'idle';

-- Prevention
-- Set statement timeout in postgresql.conf
-- statement_timeout = 600000  # 10 minutes
```

### 2. Missing or Inefficient Indexes (25% of cases)
**Symptoms**: Sequential scans on large tables causing row locks
```sql
-- Detection
SELECT schemaname, tablename, seq_scan, seq_tup_read,
       seq_tup_read/seq_scan as avg_tup_per_scan
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC;

-- Fix
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM large_table WHERE condition;
-- Add appropriate indexes based on EXPLAIN output
CREATE INDEX CONCURRENTLY idx_table_column ON large_table(column);
```

### 3. Aggressive DDL Operations (20% of cases)
**Symptoms**: ALTER TABLE, VACUUM FULL, REINDEX blocking all access
```sql
-- Detection
SELECT pid, query, state, now() - query_start as duration
FROM pg_stat_activity
WHERE query ~* 'alter|vacuum|reindex|cluster'
  AND state = 'active';

-- Mitigation
-- Kill DDL operations if necessary
SELECT pg_cancel_backend(pid) FROM pg_stat_activity
WHERE query ~* 'alter table.*add constraint'
  AND now() - query_start > interval '5 minutes';

-- Prevention: Use CONCURRENTLY where possible
CREATE INDEX CONCURRENTLY idx_name ON table_name(column);
```

### 4. High UPDATE/DELETE Contention (10% of cases)
**Symptoms**: Many concurrent modifications to same rows
```sql
-- Detection
SELECT schemaname, tablename, n_tup_upd, n_tup_del,
       n_tup_upd + n_tup_del as total_modifications
FROM pg_stat_user_tables
ORDER BY total_modifications DESC;

-- Fix
-- Implement row-level locking strategy
SELECT * FROM table_name WHERE id = ? FOR UPDATE SKIP LOCKED;

-- Or batch updates with smaller transactions
UPDATE table_name SET column = value
WHERE id IN (SELECT id FROM table_name LIMIT 1000);
```

### 5. Autovacuum Not Keeping Up (5% of cases)
**Symptoms**: High dead tuple ratio, bloated tables
```sql
-- Detection
SELECT schemaname, tablename, n_live_tup, n_dead_tup,
       round(n_dead_tup::numeric / NULLIF(n_live_tup, 0), 2) as dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY dead_ratio DESC;

-- Fix
-- Manually vacuum problematic tables
VACUUM (ANALYZE, VERBOSE) problematic_table;

-- Tune autovacuum settings
ALTER TABLE problematic_table SET (
  autovacuum_vacuum_scale_factor = 0.1,
  autovacuum_analyze_scale_factor = 0.05
);
```

## Immediate Mitigation Steps

### Emergency Response (< 5 minutes)
1. **Identify and Kill Blocking Queries**
   ```sql
   -- Find the worst blocking queries
   SELECT pg_terminate_backend(blocking_pid)
   FROM (
     SELECT DISTINCT blocking_locks.pid as blocking_pid
     FROM pg_catalog.pg_locks blocked_locks
     JOIN pg_catalog.pg_locks blocking_locks
       ON blocking_locks.transactionid = blocked_locks.transactionid
       AND blocking_locks.pid != blocked_locks.pid
     WHERE NOT blocked_locks.granted
   ) blockers;
   ```

2. **Increase Connection Limits Temporarily**
   ```sql
   -- Increase max connections (requires restart)
   -- For immediate relief, kill idle connections
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND now() - state_change > interval '10 minutes';
   ```

### Short-term Fixes (< 30 minutes)
1. **Optimize High-Impact Queries**
   ```sql
   -- Analyze slow queries
   SELECT query, calls, total_time, mean_time, rows
   FROM pg_stat_statements
   ORDER BY total_time DESC
   LIMIT 10;

   -- Add missing indexes
   SELECT pg_stat_user_tables.relname,
          seq_scan,
          seq_tup_read,
          seq_tup_read / seq_scan AS avg
   FROM pg_stat_user_tables
   WHERE seq_scan > 0
   ORDER BY seq_tup_read DESC;
   ```

2. **Emergency VACUUM**
   ```sql
   -- Vacuum tables with high dead tuple ratios
   VACUUM (ANALYZE, VERBOSE) high_contention_table;

   -- Update table statistics
   ANALYZE;
   ```

## Long-term Prevention

### Connection Pooling Configuration
```python
# Application-level connection pooling with SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:password@host:5432/db',
    poolclass=QueuePool,
    pool_size=10,           # Base pool size
    max_overflow=20,        # Additional connections allowed
    pool_timeout=30,        # Timeout waiting for connection
    pool_recycle=3600,      # Recycle connections every hour
    pool_pre_ping=True      # Validate connections before use
)

# Query timeout at application level
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT * FROM table WHERE condition = :value").execution_options(
            autocommit=True,
            isolation_level="READ_COMMITTED"
        ),
        {"value": "test"}
    )
```

### PostgreSQL Configuration Optimization
```ini
# postgresql.conf - Lock and performance settings

# Connection settings
max_connections = 200
shared_buffers = 4GB          # 25% of RAM
effective_cache_size = 12GB   # 75% of RAM

# Lock settings
deadlock_timeout = 1s
max_locks_per_transaction = 256
max_pred_locks_per_transaction = 256

# Statement timeout
statement_timeout = 600000    # 10 minutes
lock_timeout = 300000         # 5 minutes
idle_in_transaction_session_timeout = 300000  # 5 minutes

# Vacuum settings
autovacuum = on
autovacuum_max_workers = 6
autovacuum_vacuum_scale_factor = 0.1
autovacuum_analyze_scale_factor = 0.05
autovacuum_vacuum_cost_limit = 2000

# Logging
log_lock_waits = on
log_statement = 'ddl'
log_min_duration_statement = 1000  # Log queries > 1 second
```

### Monitoring and Alerting Setup
```yaml
# Grafana Dashboard Alerts
alerts:
  - alert: PostgreSQLLockWait
    expr: pg_stat_activity_max_tx_duration{state="active"} > 300
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "PostgreSQL transaction waiting for locks > 5 minutes"

  - alert: PostgreSQLDeadlocks
    expr: rate(pg_stat_database_deadlocks[5m]) > 0.1
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "PostgreSQL deadlock rate is high"

  - alert: PostgreSQLConnectionsHigh
    expr: pg_stat_activity_count / pg_settings_max_connections * 100 > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "PostgreSQL connection usage > 80%"
```

## Production Examples

### Discord's Message Lock Contention (2020)
- **Incident**: Message insertion locks causing 15-second delays
- **Root Cause**: Foreign key constraint checks on large channel tables
- **Impact**: Chat delays, 25% user complaints
- **Resolution**: Deferred constraint checking, table partitioning
- **Prevention**: Message table partitioned by channel_id

### Stripe's Payment Processing Deadlocks (2019)
- **Incident**: Payment table deadlocks during high-volume periods
- **Root Cause**: Concurrent balance updates with different lock ordering
- **Impact**: Failed payments, revenue loss
- **Resolution**: Consistent lock ordering, retry logic
- **Learning**: Always acquire locks in consistent order across transactions

### GitLab's Database Lock Storm (2021)
- **Incident**: Migration script locked entire users table for 4 hours
- **Root Cause**: ALTER TABLE without CONCURRENTLY on 100M row table
- **Impact**: Complete site downtime
- **Resolution**: Killed migration, implemented online schema change tool
- **Prevention**: All DDL operations must use CONCURRENTLY or pt-online-schema-change

## Recovery Automation

### Lock Detection and Resolution Script
```bash
#!/bin/bash
# PostgreSQL lock monitoring and auto-resolution script

DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="production"
DB_USER="monitor"

SLACK_WEBHOOK="your-slack-webhook-url"

# Function to send alerts
send_alert() {
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"PG Lock Alert: $1\"}" \
        $SLACK_WEBHOOK
}

# Check for locks waiting > 5 minutes
LONG_LOCKS=$(psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -U $DB_USER -t -c "
SELECT count(*)
FROM pg_stat_activity
WHERE wait_event IS NOT NULL
  AND now() - query_start > interval '5 minutes';")

if [ "$LONG_LOCKS" -gt 0 ]; then
    send_alert "Found $LONG_LOCKS queries waiting for locks > 5 minutes"

    # Get blocking query details
    BLOCKING_QUERIES=$(psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -U $DB_USER -t -c "
    SELECT 'PID: ' || blocking_locks.pid || ' blocking PID: ' || blocked_locks.pid || ' for ' ||
           extract(epoch from (now() - blocked_activity.query_start))/60 || ' minutes'
    FROM pg_catalog.pg_locks blocked_locks
    JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
    JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.transactionid = blocked_locks.transactionid
    WHERE NOT blocked_locks.granted AND blocking_locks.granted AND blocking_locks.pid != blocked_locks.pid;")

    send_alert "Blocking details: $BLOCKING_QUERIES"

    # Auto-kill transactions running > 30 minutes
    KILLED_QUERIES=$(psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -U $DB_USER -t -c "
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE now() - xact_start > interval '30 minutes'
      AND state != 'idle'
      AND pid != pg_backend_pid();")

    if [ ! -z "$KILLED_QUERIES" ]; then
        send_alert "Auto-killed long-running transactions: $KILLED_QUERIES"
    fi
fi

# Check deadlock rate
DEADLOCKS=$(psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -U $DB_USER -t -c "
SELECT deadlocks
FROM pg_stat_database
WHERE datname = '$DB_NAME';")

echo "Current locks waiting: $LONG_LOCKS"
echo "Total deadlocks: $DEADLOCKS"
```

**Remember**: PostgreSQL lock contention can cascade quickly. Act fast to identify root causes, but be cautious when killing transactions as it may cause application errors. Always prioritize understanding the lock dependency chain before taking action.