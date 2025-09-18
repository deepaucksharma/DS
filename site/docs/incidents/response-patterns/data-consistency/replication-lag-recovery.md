# Replication Lag Recovery Emergency Response

> **3 AM Emergency Protocol**: Replication lag can cause data inconsistency, read-after-write failures, and user-facing bugs. This diagram shows how to detect, measure, and recover from replication lag issues.

## Quick Detection Checklist
- [ ] Monitor replication delay: `SHOW SLAVE STATUS` for MySQL, `pg_stat_replication` for PostgreSQL
- [ ] Check read-after-write consistency: Test immediate reads after writes
- [ ] Watch lag metrics: `replica_lag_seconds > 30` for typical workloads
- [ ] Alert on lag spikes: `rate(replication_lag[5m]) > threshold`

## Replication Lag Detection and Recovery

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Application Layer]
        WRITE_APP[Write Operations<br/>User registration: 1000/min<br/>Payment processing: 500/min<br/>Content updates: 2000/min<br/>Target: Primary database]
        READ_APP[Read Operations<br/>User profiles: 10,000/min<br/>Search queries: 5,000/min<br/>Analytics: 15,000/min<br/>Target: Read replicas]
        CRITICAL_READS[Critical Reads<br/>Balance checks: 200/min<br/>Auth verification: 800/min<br/>Recent orders: 300/min<br/>Requirement: Fresh data]
    end

    subgraph ServicePlane[Service Plane - Database Layer]
        subgraph WRITE_PATH[Write Path]
            LOAD_BALANCER[Write Load Balancer<br/>Routes to primary only<br/>Health checks: Active<br/>Failover time: 30s]
            PRIMARY_PROXY[Primary DB Proxy<br/>Connection pooling: 100 connections<br/>Query routing: Write-only<br/>Status: Healthy]
        end

        subgraph READ_PATH[Read Path]
            READ_BALANCER[Read Load Balancer<br/>Routes to replicas<br/>Lag-aware routing: Enabled<br/>Fallback to primary: Auto]
            REPLICA_PROXY[Replica DB Proxy<br/>Connection pooling: 200 connections<br/>Lag monitoring: Real-time<br/>Status: Some lag detected]
        end

        subgraph REPLICATION[Replication Management]
            REPL_MONITOR[Replication Monitor<br/>Lag measurement: Every 10s<br/>Alert threshold: 30s<br/>Auto-failover: Disabled]
            CONFLICT_RESOLVER[Conflict Resolver<br/>Multi-master conflicts: None<br/>Read preference: Primary<br/>Consistency level: Eventual]
        end
    end

    subgraph StatePlane[State Plane - Database Infrastructure]
        subgraph PRIMARY_CLUSTER[Primary Database Cluster]
            PRIMARY_DB[(Primary Database<br/>PostgreSQL 14<br/>Write load: 2000 TPS<br/>CPU: 60%, Memory: 70%<br/>Status: HEALTHY)]
            WAL_SENDER[WAL Sender Process<br/>Streaming replication: Active<br/>Sent location: 16/B374D848<br/>Flush location: 16/B374D848]
        end

        subgraph REPLICA_CLUSTER[Replica Database Cluster]
            REPLICA_1[(Read Replica 1<br/>Region: Same as primary<br/>Lag: 2 seconds (NORMAL)<br/>Applied: 16/B374D840<br/>Status: HEALTHY)]
            REPLICA_2[(Read Replica 2<br/>Region: Cross-region<br/>Lag: 45 seconds (HIGH)<br/>Applied: 16/B374D000<br/>Status: DEGRADED)]
            REPLICA_3[(Read Replica 3<br/>Region: Same as primary<br/>Lag: 120 seconds (CRITICAL)<br/>Applied: 16/B374C000<br/>Status: UNHEALTHY)]
        end

        subgraph LAG_MONITORING[Lag Monitoring]
            LAG_METRICS[Lag Metrics<br/>Current max lag: 120s<br/>Average lag: 55s<br/>Lag trend: INCREASING<br/>Alert status: FIRING]
            CONSISTENCY_CHECK[Consistency Checker<br/>Read-after-write tests: 15% failing<br/>Cross-replica comparison: Mismatches found<br/>Data freshness: Compromised]
        end
    end

    subgraph ControlPlane[Control Plane - Lag Management]
        DETECTION[Lag Detection<br/>Monitoring frequency: 10s<br/>Measurement: WAL position diff<br/>Historical tracking: 24 hours]

        subgraph ANALYSIS[Lag Analysis]
            BOTTLENECK_ID[Bottleneck Identification<br/>Network latency: 5ms<br/>Disk I/O: 80% utilization<br/>CPU load: 60%<br/>Root cause: Disk I/O]
            TREND_ANALYSIS[Trend Analysis<br/>Pattern: Business hours spike<br/>Growth rate: 10s per hour<br/>Projection: 300s in 6 hours]
            IMPACT_ASSESSMENT[Impact Assessment<br/>Affected reads: 25%<br/>User experience: Degraded<br/>Business impact: HIGH]
        end

        subgraph RECOVERY[Lag Recovery]
            TRAFFIC_ROUTING[Traffic Routing<br/>Route to low-lag replicas<br/>Fallback to primary<br/>Load redistribution]
            REPLICA_OPTIMIZATION[Replica Optimization<br/>Disk I/O tuning<br/>WAL segment sizing<br/>Parallel apply workers]
            EMERGENCY_SCALING[Emergency Scaling<br/>Add new replica<br/>Promote replica to primary<br/>Horizontal read scaling]
        end
    end

    %% Application traffic flow
    WRITE_APP --> LOAD_BALANCER
    READ_APP --> READ_BALANCER
    CRITICAL_READS --> READ_BALANCER

    %% Write path
    LOAD_BALANCER --> PRIMARY_PROXY
    PRIMARY_PROXY --> PRIMARY_DB

    %% Read path with lag awareness
    READ_BALANCER --> REPLICA_PROXY
    REPLICA_PROXY --> REPLICA_1
    REPLICA_PROXY -.->|"High lag - reduced traffic"| REPLICA_2
    REPLICA_PROXY -.->|"Critical lag - blocked"| REPLICA_3

    %% Replication flow
    PRIMARY_DB --> WAL_SENDER
    WAL_SENDER --> REPLICA_1
    WAL_SENDER -.->|"Slow replication"| REPLICA_2
    WAL_SENDER -.->|"Replication stalled"| REPLICA_3

    %% Monitoring and metrics
    REPL_MONITOR --> LAG_METRICS
    REPLICA_1 --> LAG_METRICS
    REPLICA_2 --> LAG_METRICS
    REPLICA_3 --> LAG_METRICS
    READ_APP --> CONSISTENCY_CHECK

    %% Lag detection and analysis
    LAG_METRICS --> DETECTION
    CONSISTENCY_CHECK --> DETECTION
    DETECTION --> BOTTLENECK_ID
    DETECTION --> TREND_ANALYSIS
    DETECTION --> IMPACT_ASSESSMENT

    %% Recovery actions
    BOTTLENECK_ID --> TRAFFIC_ROUTING
    TREND_ANALYSIS --> REPLICA_OPTIMIZATION
    IMPACT_ASSESSMENT --> EMERGENCY_SCALING

    %% Recovery effects
    TRAFFIC_ROUTING -.->|"Route away from lagged replicas"| READ_BALANCER
    REPLICA_OPTIMIZATION -.->|"Performance tuning"| REPLICA_2
    EMERGENCY_SCALING -.->|"Add capacity"| REPLICA_CLUSTER

    %% 4-plane styling
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef healthyStyle fill:#00FF00,stroke:#00CC00,color:#fff
    classDef degradedStyle fill:#FFA500,stroke:#CC8800,color:#fff
    classDef criticalStyle fill:#FF0000,stroke:#CC0000,color:#fff

    class WRITE_APP,READ_APP,CRITICAL_READS edgeStyle
    class LOAD_BALANCER,PRIMARY_PROXY,READ_BALANCER,REPLICA_PROXY,REPL_MONITOR,CONFLICT_RESOLVER serviceStyle
    class PRIMARY_DB,WAL_SENDER,REPLICA_1,REPLICA_2,REPLICA_3,LAG_METRICS,CONSISTENCY_CHECK stateStyle
    class DETECTION,BOTTLENECK_ID,TREND_ANALYSIS,IMPACT_ASSESSMENT,TRAFFIC_ROUTING,REPLICA_OPTIMIZATION,EMERGENCY_SCALING controlStyle
    class PRIMARY_DB,REPLICA_1 healthyStyle
    class REPLICA_2 degradedStyle
    class REPLICA_3,LAG_METRICS criticalStyle
```

## 3 AM Emergency Response Commands

### 1. Replication Lag Assessment (30 seconds)
```sql
-- PostgreSQL replication lag check
SELECT
    client_addr,
    application_name,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;

-- Check replica lag from replica side
SELECT
    CASE WHEN pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn()
         THEN 0
         ELSE EXTRACT (EPOCH FROM now() - pg_last_xact_replay_timestamp())
    END AS lag_seconds;

-- MySQL replication lag check
SHOW SLAVE STATUS\G
-- Look for Seconds_Behind_Master

-- Check binary log position differences
SHOW MASTER STATUS;  -- On primary
SHOW SLAVE STATUS;   -- On replica
```

### 2. Emergency Lag Mitigation (60 seconds)
```bash
# Immediately route critical reads to primary
# Update application configuration
kubectl patch configmap app-config -p '{"data":{"read_preference":"primary"}}'
kubectl rollout restart deployment api-service

# PostgreSQL - Increase parallel apply workers
psql -h replica-host -c "ALTER SYSTEM SET max_parallel_workers = 8;"
psql -h replica-host -c "ALTER SYSTEM SET max_logical_replication_workers = 8;"
psql -h replica-host -c "SELECT pg_reload_conf();"

# MySQL - Increase slave parallel workers
mysql -h replica-host -e "SET GLOBAL slave_parallel_workers = 8;"
mysql -h replica-host -e "SET GLOBAL slave_pending_jobs_size_max = 134217728;"

# Check current replication processes
ps aux | grep "wal receiver\|wal sender"
ps aux | grep "slave_io\|slave_sql"
```

### 3. Scale and Recovery Actions (90 seconds)
```bash
# Launch new read replica with better specs
aws rds create-db-instance-read-replica \
    --db-instance-identifier "production-replica-emergency" \
    --source-db-instance-identifier "production-primary" \
    --db-instance-class "db.r6g.2xlarge" \
    --availability-zone "us-east-1a"

# Temporarily promote a replica to reduce load on primary
# WARNING: This breaks replication - use only in emergency
kubectl exec postgres-replica-1 -- psql -c "SELECT pg_promote();"

# Scale up existing replica resources
kubectl patch deployment postgres-replica -p '{"spec":{"template":{"spec":{"containers":[{"name":"postgres","resources":{"limits":{"cpu":"4","memory":"16Gi"}}}]}}}}'

# Update load balancer to remove lagged replicas
kubectl patch endpoints postgres-read --type='json' -p='[{"op": "remove", "path": "/subsets/0/addresses/1"}]'
```

## Replication Lag Pattern Analysis

### Lag Progression Timeline
```
Time    Primary_TPS    Replica_1_Lag    Replica_2_Lag    Replica_3_Lag    Trend
08:00   500           2s               3s               5s               Baseline
09:00   1500          5s               8s               15s              Business hours start
10:00   2500          15s              25s              60s              Peak load
11:00   3000          30s              60s              120s             Critical threshold
12:00   2000          25s              45s              90s              Load decreasing
13:00   1000          10s              20s              40s              Recovery phase
```

### Cross-Region Lag Comparison
```
Region          Network_RTT    Disk_IOPS    CPU_Usage    Replication_Lag    Status
us-east-1a      1ms           10,000       45%          2s                HEALTHY
us-east-1b      2ms           8,000        55%          8s                WARNING
us-west-2       45ms          12,000       40%          45s               DEGRADED
eu-west-1       85ms          9,000        60%          120s              CRITICAL
```

### Lag by Workload Type
```
Workload_Type       Primary_Load    Replication_Impact    Lag_Sensitivity
OLTP_Updates        HIGH           HIGH                  CRITICAL
Bulk_Inserts        MEDIUM         VERY_HIGH            MEDIUM
Read_Queries        LOW            NONE                 LOW
Analytics_ETL       LOW            MEDIUM               LOW
User_Sessions       MEDIUM         HIGH                 HIGH
```

## Error Message Patterns

### PostgreSQL Replication Lag Errors
```
ERROR: WAL receiver process terminated unexpectedly
PATTERN: "terminating walreceiver process due to administrator command"
LOCATION: PostgreSQL replica logs
CAUSE: Network interruption, primary restart, configuration changes
ACTION: Check network connectivity, restart WAL receiver
```

### MySQL Replication Lag Errors
```
ERROR: Slave SQL thread retrying transaction
PATTERN: "Slave SQL for channel '' thread retried transaction 10 time(s)"
LOCATION: MySQL error log on replica
CAUSE: Lock contention, deadlocks, constraint violations
ACTION: Check for blocking queries, optimize conflicting operations
```

### Read-After-Write Consistency Failures
```
ERROR: Record not found immediately after creation
PATTERN: Application reports missing data that was just inserted
LOCATION: Application logs, user experience reports
CAUSE: Read routed to lagged replica
ACTION: Route critical reads to primary, implement read-your-writes consistency
```

## Replication Lag Optimization

### PostgreSQL Streaming Replication Tuning
```postgresql
-- Primary database optimization
-- postgresql.conf on primary
wal_level = replica
max_wal_senders = 10
wal_keep_segments = 100  -- Or wal_keep_size = 1GB for v13+
wal_segment_size = 64MB
checkpoint_segments = 32
checkpoint_completion_target = 0.9

-- Replica database optimization
-- postgresql.conf on replica
max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
random_page_cost = 1.1
effective_io_concurrency = 200

-- Enable parallel apply for logical replication
max_logical_replication_workers = 8
max_parallel_workers = 8
max_worker_processes = 16

-- Hot standby settings
hot_standby = on
max_standby_streaming_delay = 30s
max_standby_archive_delay = 60s

-- Monitor replication status
SELECT
    pid,
    application_name,
    client_addr,
    state,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;
```

### MySQL Replication Optimization
```mysql
-- Primary database configuration
-- my.cnf on primary
[mysqld]
server-id = 1
log-bin = mysql-bin
binlog-format = ROW
binlog-row-image = MINIMAL
expire-logs-days = 7
max-binlog-size = 1GB
sync-binlog = 1

-- Replica database configuration
-- my.cnf on replica
[mysqld]
server-id = 2
relay-log = relay-bin
log-slave-updates = 1
read-only = 1

-- Parallel replication settings
slave-parallel-type = LOGICAL_CLOCK
slave-parallel-workers = 8
slave-pending-jobs-size-max = 134217728
slave-preserve-commit-order = 1

-- Performance tuning
innodb-buffer-pool-size = 8GB
innodb-log-file-size = 2GB
innodb-flush-log-at-trx-commit = 2
innodb-flush-method = O_DIRECT

-- Monitor replication lag
SHOW SLAVE STATUS\G

-- Check binary log events
SHOW BINLOG EVENTS IN 'mysql-bin.000001' LIMIT 10;
```

### Application-Level Lag Handling
```python
# Python application with lag-aware read routing
import time
import random
from enum import Enum
from typing import Optional

class ReadPreference(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SECONDARY_PREFERRED = "secondary_preferred"

class DatabaseRouter:
    def __init__(self, primary_conn, replica_conns, max_lag_seconds=30):
        self.primary = primary_conn
        self.replicas = replica_conns
        self.max_lag_seconds = max_lag_seconds
        self.replica_lag_cache = {}
        self.last_lag_check = {}

    def get_replica_lag(self, replica_conn) -> float:
        """Get current replication lag for a replica"""
        cache_key = id(replica_conn)
        current_time = time.time()

        # Cache lag measurements for 10 seconds
        if (cache_key in self.last_lag_check and
            current_time - self.last_lag_check[cache_key] < 10):
            return self.replica_lag_cache.get(cache_key, float('inf'))

        try:
            cursor = replica_conn.cursor()

            # PostgreSQL lag query
            cursor.execute("""
                SELECT CASE WHEN pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn()
                       THEN 0
                       ELSE EXTRACT(EPOCH FROM now() - pg_last_xact_replay_timestamp())
                       END AS lag_seconds
            """)

            lag_seconds = cursor.fetchone()[0] or 0

            self.replica_lag_cache[cache_key] = lag_seconds
            self.last_lag_check[cache_key] = current_time

            return lag_seconds

        except Exception as e:
            print(f"Error checking replica lag: {e}")
            return float('inf')

    def get_healthy_replicas(self):
        """Return list of replicas with acceptable lag"""
        healthy_replicas = []

        for replica in self.replicas:
            lag = self.get_replica_lag(replica)
            if lag <= self.max_lag_seconds:
                healthy_replicas.append((replica, lag))

        # Sort by lag (lowest first)
        healthy_replicas.sort(key=lambda x: x[1])
        return [replica for replica, lag in healthy_replicas]

    def get_connection(self, read_preference: ReadPreference = ReadPreference.SECONDARY_PREFERRED):
        """Get database connection based on read preference and lag"""

        if read_preference == ReadPreference.PRIMARY:
            return self.primary

        elif read_preference == ReadPreference.SECONDARY:
            healthy_replicas = self.get_healthy_replicas()
            if healthy_replicas:
                return random.choice(healthy_replicas)
            else:
                raise Exception("No healthy replicas available")

        elif read_preference == ReadPreference.SECONDARY_PREFERRED:
            healthy_replicas = self.get_healthy_replicas()
            if healthy_replicas:
                return random.choice(healthy_replicas)
            else:
                print("WARNING: No healthy replicas, falling back to primary")
                return self.primary

    def execute_read(self, query: str, params=None, read_preference: ReadPreference = ReadPreference.SECONDARY_PREFERRED):
        """Execute read query with lag-aware routing"""
        conn = self.get_connection(read_preference)
        cursor = conn.cursor()

        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()

    def execute_write(self, query: str, params=None):
        """Execute write query (always goes to primary)"""
        cursor = self.primary.cursor()

        try:
            cursor.execute(query, params or ())
            self.primary.commit()
            return cursor.rowcount
        except Exception as e:
            self.primary.rollback()
            raise e
        finally:
            cursor.close()

    def read_your_writes(self, user_id: str, query: str, params=None, timeout: float = 5.0):
        """Ensure read-your-writes consistency for a specific user"""
        # Check if user has recent writes
        if self.has_recent_writes(user_id):
            # Force read from primary for consistency
            return self.execute_read(query, params, ReadPreference.PRIMARY)
        else:
            # Can use replica for this user
            return self.execute_read(query, params, ReadPreference.SECONDARY_PREFERRED)

    def has_recent_writes(self, user_id: str, window_seconds: int = 30) -> bool:
        """Check if user has recent write operations"""
        # This would typically check a cache or session store
        # For example, Redis with user write timestamps
        try:
            import redis
            r = redis.Redis()
            last_write = r.get(f"last_write:{user_id}")

            if last_write:
                last_write_time = float(last_write)
                return time.time() - last_write_time < window_seconds

        except Exception:
            pass

        return False

# Usage example
router = DatabaseRouter(primary_conn, [replica1_conn, replica2_conn])

# Regular read (uses healthy replica)
users = router.execute_read("SELECT * FROM users WHERE active = %s", (True,))

# Critical read (uses primary)
balance = router.execute_read(
    "SELECT balance FROM accounts WHERE user_id = %s",
    (user_id,),
    ReadPreference.PRIMARY
)

# Write operation
router.execute_write("UPDATE accounts SET balance = %s WHERE user_id = %s", (new_balance, user_id))

# Read-your-writes consistency
recent_orders = router.read_your_writes(
    user_id,
    "SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC",
    (user_id,)
)
```

## Monitoring and Alerting

### Prometheus Replication Metrics
```yaml
# Prometheus rules for replication lag monitoring
groups:
- name: replication_lag
  rules:
  - alert: ReplicationLagHigh
    expr: postgres_replication_lag_seconds > 30
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "PostgreSQL replication lag high"
      description: "Replication lag is {{ $value }} seconds on {{ $labels.instance }}"

  - alert: ReplicationLagCritical
    expr: postgres_replication_lag_seconds > 120
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "PostgreSQL replication lag critical"
      description: "Replication lag is {{ $value }} seconds on {{ $labels.instance }}"

  - alert: ReplicationBroken
    expr: postgres_replication_connected == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "PostgreSQL replication disconnected"
      description: "Replication connection lost on {{ $labels.instance }}"

  - alert: ReadAfterWriteFailure
    expr: rate(read_after_write_failures_total[5m]) > 0.01
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Read-after-write consistency failures"
      description: "{{ $value }} read-after-write failures per second"
```

## Recovery Procedures

### Phase 1: Immediate Impact Mitigation (0-5 minutes)
- [ ] Route critical reads to primary database
- [ ] Increase connection limits on primary if needed
- [ ] Remove severely lagged replicas from load balancer
- [ ] Monitor primary database performance impact

### Phase 2: Replication Optimization (5-30 minutes)
- [ ] Tune replication parameters (parallel workers, WAL settings)
- [ ] Identify and resolve replication bottlenecks
- [ ] Scale up replica resources (CPU, memory, disk I/O)
- [ ] Add new replicas in different availability zones

### Phase 3: Long-term Stability (30+ minutes)
- [ ] Implement lag-aware read routing in applications
- [ ] Set up comprehensive replication monitoring
- [ ] Review and optimize database schema for replication
- [ ] Test failover procedures and recovery time

## Real-World Replication Lag Incidents

### Instagram Photo Feed Lag (2016)
- **Trigger**: Bulk photo processing caused primary database overload
- **Impact**: Users couldn't see recently posted photos, 30% of reads stale
- **Detection**: User reports + read-after-write monitoring
- **Resolution**: Read routing optimization + photo processing throttling

### GitHub Repository Lag (2020)
- **Trigger**: Large repository operations overwhelmed replication
- **Impact**: Git operations showed stale repository state
- **Detection**: Repository consistency checks + user reports
- **Resolution**: Replication tuning + operation batching

### Shopify Order Lag During Black Friday (2019)
- **Trigger**: Massive order volume caused replication lag spikes
- **Impact**: Order status pages showed outdated information
- **Detection**: Real-time lag monitoring + customer complaints
- **Resolution**: Emergency read routing + infrastructure scaling

---
*Last Updated: Based on Instagram, GitHub, Shopify replication lag incidents*
*Next Review: Monitor for new replication optimization patterns and lag detection methods*