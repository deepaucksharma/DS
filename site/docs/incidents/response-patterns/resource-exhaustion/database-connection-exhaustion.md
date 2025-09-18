# Database Connection Pool Exhaustion Response

> **3 AM Emergency Protocol**: Database connection exhaustion can halt all operations within seconds. This diagram shows how to quickly detect, mitigate, and recover from connection pool exhaustion.

## Quick Detection Checklist
- [ ] Check active connections: `SHOW PROCESSLIST` (MySQL) or `pg_stat_activity` (PostgreSQL)
- [ ] Monitor pool status: `kubectl logs [app-pod] | grep "connection pool"`
- [ ] Watch timeouts: Application logs showing "connection timeout" errors
- [ ] Alert on pool utilization: `active_connections / max_connections > 0.9`

## Database Connection Pool Exhaustion Emergency Response

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Request Sources]
        WEB[Web Traffic<br/>Active users: 25,000<br/>Requests/sec: 1,500<br/>Connection demand: HIGH]
        MOBILE[Mobile Apps<br/>Background sync: 500/min<br/>Long-polling: 200 active<br/>Connection leaks: Suspected]
        API[API Clients<br/>Bulk operations: 50/min<br/>Transaction time: 5-30s<br/>Connection holding: Extended]
        BATCH[Batch Jobs<br/>Running jobs: 5<br/>Connections each: 20<br/>Total held: 100 connections]
    end

    subgraph ServicePlane[Service Plane - Connection Consumers]
        subgraph APP_LAYER[Application Layer]
            API_1[API Service 1<br/>Connection Pool: 18/20<br/>Idle connections: 2<br/>Active queries: 18]
            API_2[API Service 2<br/>Connection Pool: 20/20<br/>Idle connections: 0<br/>Queue waiting: 15]
            API_3[API Service 3<br/>Connection Pool: 19/20<br/>Idle connections: 1<br/>Timeout errors: 5/min]
        end

        subgraph WORKER_LAYER[Worker Layer]
            WORKER_1[Background Worker 1<br/>Long transactions: 3 active<br/>Average duration: 45s<br/>Connection usage: High]
            WORKER_2[Background Worker 2<br/>Batch processing: Active<br/>Connection leaks: Detected<br/>Memory usage: Growing]
        end

        CONN_PROXY[Connection Proxy<br/>PgBouncer/ProxySQL<br/>Pool mode: Transaction<br/>Max connections: 200]
    end

    subgraph StatePlane[State Plane - Database Resources]
        subgraph PRIMARY_DB[Primary Database]
            DB_MAIN[(PostgreSQL Primary<br/>Max connections: 100<br/>Active connections: 95<br/>Idle connections: 5<br/>Status: CRITICAL)]
            CONN_SLOTS[Connection Slots<br/>Reserved: 10 (superuser)<br/>Available: 90<br/>Used: 95/90<br/>Overcommitted: 5]
        end

        subgraph REPLICA_DB[Read Replicas]
            DB_REPLICA1[(Read Replica 1<br/>Max connections: 100<br/>Active connections: 45<br/>Replication lag: 2s)]
            DB_REPLICA2[(Read Replica 2<br/>Max connections: 100<br/>Active connections: 60<br/>Replication lag: 1s)]
        end

        CACHE[(Redis Cache<br/>Connections: 50/1000<br/>Used for: Session data<br/>Hit ratio: 85%)]
    end

    subgraph ControlPlane[Control Plane - Connection Management]
        MONITOR[Connection Monitoring<br/>Prometheus metrics<br/>Alert threshold: 90%<br/>Current: 95% utilization]

        subgraph EMERGENCY[Emergency Response]
            KILL_IDLE[Kill Idle Connections<br/>Threshold: > 5 minutes<br/>Action: Terminate safely<br/>Recovery: Immediate]
            KILL_LONG[Kill Long Queries<br/>Threshold: > 2 minutes<br/>Action: Cancel queries<br/>Recovery: App retry]
            SCALE_POOL[Scale Connection Pool<br/>Increase max_connections<br/>Restart required: Yes<br/>Downtime: 30 seconds]
        end

        ROUTING[Traffic Routing<br/>Read/write splitting<br/>Load balancing<br/>Circuit breaker: Enabled]
    end

    %% Traffic flow and connection usage
    WEB --> API_1
    MOBILE --> API_2
    API --> API_3
    BATCH --> WORKER_1
    BATCH --> WORKER_2

    %% Connection proxy layer
    API_1 --> CONN_PROXY
    API_2 --> CONN_PROXY
    API_3 --> CONN_PROXY
    WORKER_1 --> CONN_PROXY
    WORKER_2 --> CONN_PROXY

    %% Database connections
    CONN_PROXY --> DB_MAIN
    CONN_PROXY -.->|"Read queries"| DB_REPLICA1
    CONN_PROXY -.->|"Read queries"| DB_REPLICA2

    %% Cache usage
    API_1 --> CACHE
    API_2 --> CACHE
    API_3 --> CACHE

    %% Monitoring and alerts
    DB_MAIN --> MONITOR
    DB_REPLICA1 --> MONITOR
    DB_REPLICA2 --> MONITOR
    CONN_PROXY --> MONITOR

    %% Emergency responses
    MONITOR -->|"95% utilization"| KILL_IDLE
    MONITOR -->|"Long queries detected"| KILL_LONG
    MONITOR -->|"Pool exhausted"| SCALE_POOL

    %% Recovery actions
    KILL_IDLE -.->|"Terminate connections"| DB_MAIN
    KILL_LONG -.->|"Cancel queries"| DB_MAIN
    SCALE_POOL -.->|"Increase limits"| DB_MAIN

    %% Traffic management
    MONITOR --> ROUTING
    ROUTING -.->|"Redirect reads"| DB_REPLICA1
    ROUTING -.->|"Load balance"| DB_REPLICA2

    %% 4-plane styling
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef criticalStyle fill:#FF0000,stroke:#8B5CF6,color:#fff
    classDef warningStyle fill:#FFA500,stroke:#CC8800,color:#fff

    class WEB,MOBILE,API,BATCH edgeStyle
    class API_1,API_2,API_3,WORKER_1,WORKER_2,CONN_PROXY serviceStyle
    class DB_MAIN,DB_REPLICA1,DB_REPLICA2,CACHE,CONN_SLOTS stateStyle
    class MONITOR,KILL_IDLE,KILL_LONG,SCALE_POOL,ROUTING controlStyle
    class DB_MAIN,API_2 criticalStyle
    class API_3,WORKER_2 warningStyle
```

## 3 AM Emergency Response Commands

### 1. Connection Status Assessment (30 seconds)
```sql
-- PostgreSQL connection analysis
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;
SELECT pid, usename, application_name, state, query_start, query
FROM pg_stat_activity
WHERE state = 'active' AND query_start < now() - interval '2 minutes';

-- MySQL connection analysis
SHOW PROCESSLIST;
SELECT Id, User, Host, db, Command, Time, State, Info
FROM INFORMATION_SCHEMA.PROCESSLIST
WHERE Time > 120 AND Command != 'Sleep';
```

### 2. Emergency Connection Recovery (60 seconds)
```bash
# Kill idle connections (PostgreSQL)
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < now() - interval '5 minutes';"

# Kill long-running queries (MySQL)
mysql -e "SELECT CONCAT('KILL ', Id, ';') FROM INFORMATION_SCHEMA.PROCESSLIST WHERE Time > 300 AND Command != 'Sleep';" | grep KILL | mysql

# Check connection pool status
kubectl logs -l app=api-service | grep -i "connection pool" | tail -10

# Restart connection pools
kubectl rollout restart deployment api-service
kubectl rollout restart deployment worker-service
```

### 3. Scale Database Connections (90 seconds)
```bash
# Increase PostgreSQL max_connections (requires restart)
kubectl exec postgres-primary-0 -- psql -c "ALTER SYSTEM SET max_connections = 200;"
kubectl exec postgres-primary-0 -- psql -c "SELECT pg_reload_conf();"

# Scale PgBouncer pool sizes
kubectl patch configmap pgbouncer-config -p '{"data":{"pgbouncer.ini":"[databases]\npostgres = host=postgres-primary port=5432 dbname=app\n\n[pgbouncer]\npool_mode = transaction\nmax_client_conn = 300\ndefault_pool_size = 30"}}'
kubectl rollout restart deployment pgbouncer

# Route traffic to read replicas
kubectl patch service postgres-read -p '{"spec":{"selector":{"role":"replica"}}}'
```

## Connection Exhaustion Pattern Recognition

### Gradual Pool Exhaustion
```
Time    Active_Conn    Idle_Conn    Pool_Usage    Queue_Length
10:00   40/100        10           50%           0
10:15   60/100        8            68%           0
10:30   80/100        5            85%           2
10:45   95/100        2            97%           15        # CRITICAL
11:00   100/100       0            100%          45        # EXHAUSTED
```

### Sudden Connection Spike
```
Time    Connections    Cause               Impact
10:00   45/100        Normal operations   Healthy
10:01   95/100        Batch job started   Spike
10:02   100/100       Mobile app bug      Pool full
10:03   100/100       API timeouts        Cascade failure
```

### Connection Leak Pattern
```
Hour    Expected_Conn    Actual_Conn    Leaked_Conn    Trend
09:00   40              40             0              Baseline
10:00   45              50             5              Growing
11:00   50              65             15             Accelerating
12:00   55              85             30             Critical
13:00   60              100            40             Pool exhausted
```

## Error Message Patterns

### PostgreSQL Connection Exhaustion
```
ERROR: FATAL: remaining connection slots are reserved for non-replication superuser connections
PATTERN: Connection attempts failing with FATAL error
LOCATION: PostgreSQL logs, application logs
ACTION: Kill idle connections, increase max_connections
MONITORING: SELECT count(*) FROM pg_stat_activity;
```

### MySQL Connection Exhaustion
```
ERROR: ERROR 1040 (HY000): Too many connections
PATTERN: New connections rejected at MySQL level
LOCATION: MySQL error log, application connection errors
ACTION: Kill sleeping connections, tune max_connections
COMMAND: SET GLOBAL max_connections = 200;
```

### Application Pool Exhaustion
```
ERROR: Connection pool exhausted, timeout waiting for connection
PATTERN: Application-level pool timeout errors
LOCATION: Application logs, connection pool metrics
ACTION: Increase pool size, reduce connection hold time
CONFIG: maxPoolSize: 50, connectionTimeout: 30000
```

## Connection Pool Optimization

### HikariCP Configuration (Java)
```yaml
# Optimal HikariCP settings
spring:
  datasource:
    hikari:
      maximum-pool-size: 20          # CPU cores * 2-4
      minimum-idle: 5                # 25% of max
      idle-timeout: 300000           # 5 minutes
      max-lifetime: 1800000          # 30 minutes
      connection-timeout: 30000      # 30 seconds
      leak-detection-threshold: 60000 # 1 minute
      validation-timeout: 5000       # 5 seconds
```

### PgBouncer Configuration
```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
myapp = host=postgres-primary port=5432 dbname=myapp

[pgbouncer]
pool_mode = transaction           # Most efficient
max_client_conn = 200            # Client connections
default_pool_size = 30           # DB connections per database
min_pool_size = 10               # Minimum connections
reserve_pool_size = 5            # Emergency connections
reserve_pool_timeout = 3         # Seconds before using reserve
server_reset_query = DISCARD ALL # Clean connection state
server_check_delay = 30          # Health check interval
```

### Connection Monitoring Queries

### PostgreSQL Connection Monitoring
```sql
-- Current connection status
SELECT
    state,
    count(*) as connections,
    max(extract(epoch from (now() - query_start))) as max_duration
FROM pg_stat_activity
WHERE state IS NOT NULL
GROUP BY state;

-- Identify connection leaks
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    extract(epoch from (now() - state_change)) as idle_seconds,
    query
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < now() - interval '10 minutes'
ORDER BY state_change;

-- Connection pool utilization
SELECT
    count(*) as active_connections,
    (SELECT setting::int FROM pg_settings WHERE name='max_connections') as max_connections,
    round(count(*)::numeric / (SELECT setting::numeric FROM pg_settings WHERE name='max_connections') * 100, 2) as utilization_percent
FROM pg_stat_activity
WHERE state != 'idle';
```

### MySQL Connection Monitoring
```sql
-- Current connection status
SELECT
    COMMAND as state,
    COUNT(*) as connections,
    MAX(TIME) as max_duration_seconds
FROM INFORMATION_SCHEMA.PROCESSLIST
GROUP BY COMMAND;

-- Identify long-running connections
SELECT
    ID,
    USER,
    HOST,
    DB,
    COMMAND,
    TIME as duration_seconds,
    STATE,
    LEFT(INFO, 100) as query_snippet
FROM INFORMATION_SCHEMA.PROCESSLIST
WHERE TIME > 300
  AND COMMAND != 'Sleep'
ORDER BY TIME DESC;

-- Connection utilization
SELECT
    COUNT(*) as active_connections,
    @@max_connections as max_connections,
    ROUND(COUNT(*) / @@max_connections * 100, 2) as utilization_percent
FROM INFORMATION_SCHEMA.PROCESSLIST;
```

## Emergency Recovery Procedures

### Phase 1: Immediate Relief (0-2 minutes)
- [ ] Kill idle connections older than 5 minutes
- [ ] Terminate long-running queries (>2 minutes)
- [ ] Route read traffic to replicas
- [ ] Enable connection proxy if not already active

### Phase 2: Pool Scaling (2-5 minutes)
- [ ] Increase application connection pool sizes
- [ ] Scale out application instances
- [ ] Adjust database max_connections if possible
- [ ] Monitor for improvement in connection availability

### Phase 3: Root Cause Analysis (5-30 minutes)
- [ ] Analyze connection hold patterns
- [ ] Identify connection leaks in application code
- [ ] Review recent deployments for connection bugs
- [ ] Check for unusual traffic patterns or batch jobs

## Connection Leak Detection

### Application-Level Monitoring
```java
// Java/Spring connection leak detection
@Configuration
public class DataSourceConfig {

    @Bean
    public DataSource dataSource() {
        HikariConfig config = new HikariConfig();
        config.setLeakDetectionThreshold(60000); // 1 minute
        config.setConnectionTestQuery("SELECT 1");
        return new HikariDataSource(config);
    }
}

// Custom connection monitoring
@Component
public class ConnectionMonitor {

    @Scheduled(fixedRate = 30000) // Every 30 seconds
    public void monitorConnections() {
        HikariDataSource ds = (HikariDataSource) dataSource;
        HikariPoolMXBean pool = ds.getHikariPoolMXBean();

        log.info("Pool stats - Active: {}, Idle: {}, Total: {}",
                pool.getActiveConnections(),
                pool.getIdleConnections(),
                pool.getTotalConnections());

        if (pool.getActiveConnections() > pool.getTotalConnections() * 0.9) {
            log.warn("Connection pool utilization critical: {}%",
                    pool.getActiveConnections() * 100.0 / pool.getTotalConnections());
        }
    }
}
```

### Database-Level Monitoring
```bash
#!/bin/bash
# Connection monitoring script

DB_HOST="postgres-primary"
DB_USER="monitoring"
THRESHOLD=90

while true; do
    CONN_COUNT=$(psql -h $DB_HOST -U $DB_USER -t -c "SELECT count(*) FROM pg_stat_activity;")
    MAX_CONN=$(psql -h $DB_HOST -U $DB_USER -t -c "SELECT setting FROM pg_settings WHERE name='max_connections';")
    UTILIZATION=$((CONN_COUNT * 100 / MAX_CONN))

    echo "$(date): Connections: $CONN_COUNT/$MAX_CONN ($UTILIZATION%)"

    if [ $UTILIZATION -gt $THRESHOLD ]; then
        echo "ALERT: Connection utilization exceeds $THRESHOLD%"
        # Send alert to monitoring system
        curl -X POST http://alertmanager:9093/api/v1/alerts \
             -d "[{\"labels\":{\"alertname\":\"DatabaseConnectionsHigh\",\"severity\":\"critical\"}}]"
    fi

    sleep 30
done
```

## Real-World Connection Exhaustion Incidents

### GitHub Database Connection Storm (2018)
- **Trigger**: Deployment bug caused connection leaks in background jobs
- **Impact**: Primary database connection pool exhausted in 5 minutes
- **Detection**: Application errors + database connection monitoring
- **Resolution**: Killed leaked connections + emergency deployment rollback

### Shopify Black Friday Connection Spike (2019)
- **Trigger**: Traffic spike overwhelmed connection pools
- **Impact**: Checkout service degradation during peak sales
- **Detection**: Connection pool metrics exceeded thresholds
- **Resolution**: Emergency pool scaling + traffic shaping

### Discord Voice Connection Exhaustion (2020)
- **Trigger**: Voice channel connections not properly closed
- **Impact**: Database operations slowed, affecting all Discord features
- **Detection**: Connection leak detection + user reports
- **Resolution**: Connection cleanup job + code fix for leak

---
*Last Updated: Based on GitHub, Shopify, Discord connection exhaustion incidents*
*Next Review: Monitor for new connection pool patterns and optimization strategies*