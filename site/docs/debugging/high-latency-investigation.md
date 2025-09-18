# High Latency Investigation Guide

## Overview

High latency in distributed systems manifests in multiple forms - from database queries taking 10x longer than expected to API endpoints timing out during peak traffic. This guide provides systematic debugging approaches used by production teams at Netflix, Uber, and other scale companies.

**Time to Resolution**: 15-45 minutes for basic cases, 2-4 hours for complex distributed issues

## Decision Tree

```mermaid
graph TD
    A[High Latency Alert] --> B{Frontend or Backend?}
    B -->|Frontend| C[Check CDN/Edge Latency]
    B -->|Backend| D[Check Service Latency]

    C --> E[Examine Browser Network Tab]
    C --> F[Check CDN Cache Hit Ratios]

    D --> G{Database Query Time > 100ms?}
    G -->|Yes| H[Database Query Analysis]
    G -->|No| I[Service Processing Analysis]

    H --> J[Query Plan Examination]
    H --> K[Index Usage Check]

    I --> L[CPU/Memory Profiling]
    I --> M[Network Latency Check]

    style A fill:#CC0000,stroke:#990000,color:#fff
    style H fill:#FF8800,stroke:#CC6600,color:#fff
    style I fill:#00AA00,stroke:#007700,color:#fff
```

## Immediate Triage Commands (First 5 Minutes)

### 1. Quick Latency Snapshot
```bash
# Check current system load
uptime
iostat 1 5

# Network latency to dependencies
ping -c 5 database-host.internal
ping -c 5 redis-cluster.internal
ping -c 5 api-gateway.internal

# Application metrics (assuming Prometheus)
curl -s "http://localhost:9090/api/v1/query?query=histogram_quantile(0.99,http_request_duration_seconds_bucket)" | jq '.data.result[0].value[1]'
```

### 2. Database Quick Check
```bash
# PostgreSQL active queries
psql -c "SELECT query, state, query_start, now() - query_start as duration FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC LIMIT 10;"

# MySQL process list
mysql -e "SHOW PROCESSLIST;"

# Redis latency
redis-cli --latency-history -i 1
```

### 3. Application Server Status
```bash
# Java thread dumps (for CPU investigation)
jstack $(pgrep java) > threaddump_$(date +%s).txt

# Python/gunicorn worker status
ps aux | grep gunicorn | head -10

# Node.js event loop lag
node -e "const { performance, PerformanceObserver } = require('perf_hooks'); setInterval(() => console.log('Event Loop Lag:', process.hrtime.bigint() - performance.now() + 'ms'), 1000)"
```

## Deep Dive Analysis

### Distributed Tracing Analysis

```bash
# Jaeger query for slow traces (adjust time range and service)
curl -G "http://jaeger-query:16686/api/traces" \
  --data-urlencode "service=order-service" \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)000000" \
  --data-urlencode "end=$(date +%s)000000" \
  --data-urlencode "limit=50" \
  --data-urlencode "minDuration=5s" | jq '.data[0].spans[] | select(.duration > 5000000) | {operationName, duration}'
```

### Network vs Processing Time Separation

```python
# Python script for latency breakdown analysis
import requests
import time

def measure_latency_breakdown(url, iterations=10):
    """Measure DNS, TCP, TLS, and processing time separately"""
    results = []

    for i in range(iterations):
        start_time = time.perf_counter()

        try:
            response = requests.get(url, timeout=30)
            total_time = time.perf_counter() - start_time

            # Extract timing information
            results.append({
                'total_time': total_time,
                'status_code': response.status_code,
                'response_size': len(response.content),
                'headers': dict(response.headers)
            })
        except Exception as e:
            results.append({'error': str(e), 'total_time': time.perf_counter() - start_time})

    return results

# Usage
results = measure_latency_breakdown('https://api.example.com/health')
avg_latency = sum(r.get('total_time', 0) for r in results) / len(results)
print(f"Average latency: {avg_latency:.3f}s")
```

### Database Query Performance Deep Dive

```sql
-- PostgreSQL query performance analysis
SELECT
    query,
    calls,
    total_time,
    mean_time,
    stddev_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
WHERE mean_time > 100  -- queries taking more than 100ms on average
ORDER BY mean_time DESC
LIMIT 20;

-- Index usage verification
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan < 10  -- potentially unused indexes
ORDER BY schemaname, tablename;
```

### Cache Performance Investigation

```bash
# Redis cache hit ratio
redis-cli info stats | grep -E "(hits|misses)"

# Memcached statistics
echo "stats" | nc memcached-host 11211 | grep -E "(get_hits|get_misses|cmd_get)"

# Application-level cache analysis (example for Python with Redis)
python -c "
import redis
r = redis.Redis()
info = r.info('stats')
hit_rate = info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses']) * 100
print(f'Cache hit rate: {hit_rate:.2f}%')
"
```

## Platform-Specific Debugging

### AWS

```bash
# CloudWatch metrics for latency investigation
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --dimensions Name=LoadBalancer,Value=app/my-loadbalancer/1234567890123456 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum

# RDS performance insights
aws rds describe-db-log-files --db-instance-identifier mydb-instance
aws rds download-db-log-file-portion --db-instance-identifier mydb-instance --log-file-name slow-query-log

# X-Ray trace analysis
aws xray get-trace-summaries --time-range-type TimeRangeByStartTime --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) --end-time $(date -u +%Y-%m-%dT%H:%M:%S) --filter-expression 'ResponseTime > 5'
```

### GCP

```bash
# Cloud Monitoring for latency metrics
gcloud monitoring metrics list --filter="metric.type:appengine.googleapis.com/http/server/response_latencies"

# Cloud SQL query insights
gcloud sql operations list --instance=my-instance --filter="operationType=UPDATE_DATABASE"

# Cloud Trace analysis
gcloud trace list-traces --start-time=$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S.%3NZ) --filter="latency:>5s"
```

### Azure

```bash
# Application Insights query for high latency
az monitor app-insights query --app my-app-insights --analytics-query "
requests
| where timestamp > ago(1h)
| where duration > 5000
| summarize percentiles(duration, 50, 95, 99) by bin(timestamp, 5m)
"

# Azure SQL Database query performance
az sql db query-performance list --resource-group myResourceGroup --server myServer --database myDatabase
```

## Production Case Studies

### Case Study 1: Netflix - Microservice Chain Latency

**Problem**: API latency spiked from 50ms p99 to 2.5s during peak hours

**Investigation Process**:
1. **Distributed tracing** revealed the recommendation service was the bottleneck
2. **Database analysis** showed recommendation queries weren't using proper indexes
3. **Cache analysis** revealed cache invalidation storm during user preference updates

**Commands Used**:
```bash
# Identified slow spans in Jaeger
curl -G "http://jaeger:16686/api/traces" --data-urlencode "service=recommendation-service" --data-urlencode "minDuration=2s"

# Found missing indexes in PostgreSQL
psql -c "SELECT schemaname,tablename,attname,inherited,n_distinct,correlation FROM pg_stats WHERE schemaname='recommendations' AND n_distinct > 100;"

# Discovered cache stampede
redis-cli monitor | grep -E "(DEL|EXPIRED)"
```

**Resolution**: Added composite indexes, implemented cache warming, reduced cache invalidation scope
**Time to Resolution**: 3.5 hours

### Case Study 2: Uber - Database Connection Pool Exhaustion

**Problem**: Ride booking latency increased 10x during surge pricing events

**Root Cause**: Connection pool exhaustion causing request queuing

**Investigation Commands**:
```bash
# Connection pool statistics
psql -c "SELECT state, count(*) FROM pg_stat_activity GROUP BY state;"

# Application connection pool metrics (HikariCP example)
curl http://app-metrics:8080/actuator/metrics/hikaricp.connections.active
curl http://app-metrics:8080/actuator/metrics/hikaricp.connections.pending
```

**Resolution**: Increased connection pool size, implemented connection retry with exponential backoff
**Time to Resolution**: 45 minutes

### Case Study 3: Stripe - Payment Processing Delays

**Problem**: Payment confirmations delayed by 15-30 seconds during Black Friday

**Root Cause**: Third-party payment gateway latency plus inadequate timeout configuration

**Key Metrics**:
- Payment gateway response time: 12-15 seconds (normal: 1-2s)
- Internal timeout: 30 seconds
- User abandonment: 23% increase

**Resolution**: Implemented parallel payment processing, reduced timeouts, added fallback gateways
**Time to Resolution**: 2 hours

## Prevention Strategies

### 1. Proactive Monitoring Setup

```yaml
# Prometheus alerting rules for latency
groups:
- name: latency_alerts
  rules:
  - alert: HighLatency
    expr: histogram_quantile(0.99, http_request_duration_seconds_bucket) > 1.0
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High latency detected ({{ $value }}s)"

  - alert: DatabaseSlowQuery
    expr: pg_stat_statements_mean_time_seconds > 0.5
    for: 1m
    labels:
      severity: critical
```

### 2. Synthetic Monitoring

```python
# Synthetic transaction monitoring
import requests
import time
from datetime import datetime

def synthetic_transaction_test():
    """Simulate user journey and measure latency at each step"""
    steps = [
        {"name": "login", "url": "https://api.company.com/auth/login", "method": "POST"},
        {"name": "profile", "url": "https://api.company.com/user/profile", "method": "GET"},
        {"name": "search", "url": "https://api.company.com/search?q=test", "method": "GET"}
    ]

    session = requests.Session()
    results = {}

    for step in steps:
        start_time = time.perf_counter()
        try:
            response = session.request(step["method"], step["url"], timeout=10)
            duration = time.perf_counter() - start_time
            results[step["name"]] = {
                "duration": duration,
                "status_code": response.status_code,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            results[step["name"]] = {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    return results
```

### 3. Capacity Planning Based on Latency

```bash
# Load testing with latency focus (using wrk)
wrk -t12 -c400 -d30s --script=lua/latency-test.lua http://api.example.com/endpoint

# JMeter command line for latency testing
jmeter -n -t latency_test.jmx -l results.jtl -e -o report_folder
```

## 3 AM Debugging Checklist

When you're called at 3 AM for high latency issues:

### First 2 Minutes
- [ ] Check overall system load: `uptime && iostat 1 1`
- [ ] Verify database connectivity: `pg_isready` or equivalent
- [ ] Check recent deployments: `git log --oneline -5`
- [ ] Look at error logs: `tail -100 /var/log/application.log | grep ERROR`

### Minutes 2-5
- [ ] Query current latency percentiles from monitoring
- [ ] Identify if issue is widespread or isolated to specific endpoints
- [ ] Check for ongoing database migrations or maintenance
- [ ] Verify cache service health

### Minutes 5-15
- [ ] Run distributed tracing query for recent slow requests
- [ ] Check connection pool status
- [ ] Examine recent database query performance changes
- [ ] Review recent configuration changes

### If Still Debugging After 15 Minutes
- [ ] Escalate to senior engineer or team lead
- [ ] Consider rollback if recent deployment is suspected
- [ ] Implement temporary circuit breakers if appropriate
- [ ] Document findings for post-incident review

## Metrics and SLOs

### Key Latency Metrics to Track
- **p50, p95, p99 response times** by service and endpoint
- **Database query response times** by query type
- **Cache hit ratios** and cache response times
- **Network latency** between services
- **Connection pool utilization** percentages

### Example SLO Configuration
```yaml
service_level_objectives:
  - name: "API Response Time"
    description: "99% of API requests complete within 500ms"
    metric: "http_request_duration_seconds"
    target: 0.5
    percentile: 99
    window: "5m"

  - name: "Database Query Performance"
    description: "95% of database queries complete within 100ms"
    metric: "db_query_duration_seconds"
    target: 0.1
    percentile: 95
    window: "5m"
```

**Remember**: In production incidents, every second counts. Focus on quick wins first - restart services, clear caches, or implement circuit breakers - while you investigate root causes.

This guide is battle-tested across companies processing billions of requests daily. The goal is not just to fix the immediate issue, but to understand why it happened and prevent recurrence.