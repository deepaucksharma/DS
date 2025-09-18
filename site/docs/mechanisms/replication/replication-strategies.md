# Replication Strategies

## Overview of Replication Types

Database replication strategies determine how data consistency, availability, and performance trade-offs are handled across distributed systems.

### Strategy Comparison Matrix

```mermaid
graph TB
    subgraph Replication Strategy Trade-offs
        subgraph Synchronous Replication
            SYNC_CONS[Strong Consistency<br/>✅ Immediate consistency<br/>❌ Higher latency<br/>❌ Reduced availability]
            SYNC_PERF[Performance Impact<br/>Latency: 2x-5x higher<br/>Throughput: 50-80% of async]
        end

        subgraph Asynchronous Replication
            ASYNC_CONS[Eventual Consistency<br/>✅ High performance<br/>✅ High availability<br/>❌ Potential data loss]
            ASYNC_PERF[Performance Benefit<br/>Latency: Minimal impact<br/>Throughput: Near single-node]
        end

        subgraph Semi-Synchronous Replication
            SEMI_CONS[Balanced Approach<br/>✅ Durability guarantee<br/>✅ Reasonable performance<br/>⚠️ Complex configuration]
            SEMI_PERF[Performance Balance<br/>Latency: 1.5x-2x higher<br/>Throughput: 70-90% of async]
        end
    end

    %% Apply 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class SYNC_CONS,ASYNC_CONS,SEMI_CONS serviceStyle
    class SYNC_PERF,ASYNC_PERF,SEMI_PERF stateStyle
```

### Synchronous Replication Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant P as Primary
    participant S1 as Secondary 1
    participant S2 as Secondary 2
    participant S3 as Secondary 3

    Note over C,S3: Synchronous Replication - All replicas confirm before commit

    C->>P: Write Transaction
    P->>P: Begin Transaction

    par Replicate to all secondaries
        P->>S1: Replicate WAL entry
        P->>S2: Replicate WAL entry
        P->>S3: Replicate WAL entry
    end

    par Wait for all confirmations
        S1->>S1: Apply to WAL
        S1-->>P: ACK
        S2->>S2: Apply to WAL
        S2-->>P: ACK
        S3->>S3: Apply to WAL
        S3-->>P: ACK
    end

    P->>P: Commit transaction
    P->>C: SUCCESS

    Note over C,S3: Total latency: Max(network_latency + disk_write_time) across all replicas
```

### Asynchronous Replication Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant P as Primary
    participant S1 as Secondary 1
    participant S2 as Secondary 2
    participant S3 as Secondary 3

    Note over C,S3: Asynchronous Replication - Commit locally first, replicate later

    C->>P: Write Transaction
    P->>P: Apply locally + Commit
    P->>C: SUCCESS (immediate)

    Note over P,S3: Replication happens asynchronously

    par Async replication
        P->>S1: Replicate WAL entry
        P->>S2: Replicate WAL entry
        P->>S3: Replicate WAL entry
    end

    par Async acknowledgments (optional)
        S1->>S1: Apply to WAL
        S1-->>P: ACK (ignored for commit decision)
        S2->>S2: Apply to WAL
        S2-->>P: ACK (ignored for commit decision)
        S3->>S3: Apply to WAL
        S3-->>P: ACK (ignored for commit decision)
    end

    Note over C,S3: Client latency: Only primary write time
    Note over P,S3: Replication lag: Network + secondary processing time
```

### Semi-Synchronous Replication Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant P as Primary
    participant S1 as Secondary 1 (Semi-sync)
    participant S2 as Secondary 2 (Semi-sync)
    participant S3 as Secondary 3 (Async)

    Note over C,S3: Semi-Synchronous - Wait for subset of replicas

    C->>P: Write Transaction
    P->>P: Begin Transaction

    par Replicate to all secondaries
        P->>S1: Replicate WAL entry
        P->>S2: Replicate WAL entry
        P->>S3: Replicate WAL entry (async)
    end

    par Wait for semi-sync confirmations only
        S1->>S1: Apply to WAL
        S1-->>P: ACK
        S2->>S2: Apply to WAL
        S2-->>P: ACK
        S3->>S3: Apply to WAL (no wait)
    end

    Note over P: Wait for N semi-sync ACKs (e.g., 1 out of 2)
    P->>P: Commit transaction
    P->>C: SUCCESS

    S3-->>P: ACK (processed later)

    Note over C,S3: Latency: Fastest N semi-sync replicas
```

### Replication Strategy Configuration

#### PostgreSQL Streaming Replication

```sql
-- Primary server configuration (postgresql.conf)
wal_level = replica
max_wal_senders = 10
wal_keep_segments = 32
synchronous_standby_names = 'standby1,standby2'

-- Synchronous replication
synchronous_commit = on  -- Wait for sync standby

-- Semi-synchronous replication
synchronous_commit = remote_write  -- Wait for WAL write on standby

-- Asynchronous replication
synchronous_commit = local  -- Don't wait for standby
```

#### MySQL Replication Modes

```sql
-- MySQL 8.0 Group Replication configuration

-- Synchronous (Group Replication)
SET GLOBAL group_replication_single_primary_mode = ON;
SET GLOBAL group_replication_consistency = 'BEFORE_ON_PRIMARY_FAILOVER';

-- Semi-synchronous replication
INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';
SET GLOBAL rpl_semi_sync_master_enabled = 1;
SET GLOBAL rpl_semi_sync_master_wait_for_slave_count = 1;
SET GLOBAL rpl_semi_sync_master_timeout = 1000; -- 1 second

-- Asynchronous replication (default)
-- Standard master-slave replication without semi-sync plugin
```

### Performance Benchmarks

```mermaid
graph LR
    subgraph Performance Comparison (3-node cluster)
        subgraph Synchronous
            SYNC_TPS[5,000 TPS]
            SYNC_LAT[15ms p99]
            SYNC_AVAIL[99.9% (fails if any replica down)]
        end

        subgraph Semi-Synchronous
            SEMI_TPS[8,000 TPS]
            SEMI_LAT[8ms p99]
            SEMI_AVAIL[99.95% (tolerates 1 replica down)]
        end

        subgraph Asynchronous
            ASYNC_TPS[12,000 TPS]
            ASYNC_LAT[3ms p99]
            ASYNC_AVAIL[99.99% (primary only dependency)]
        end

        subgraph Trade-off Analysis
            CONSISTENCY[Data Loss Risk<br/>Sync: 0<br/>Semi-sync: Minimal<br/>Async: Up to RPO]
            PERFORMANCE[Performance Impact<br/>Sync: Highest<br/>Semi-sync: Moderate<br/>Async: Minimal]
        end
    end

    %% Apply state plane color for metrics
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    class SYNC_TPS,SYNC_LAT,SYNC_AVAIL,SEMI_TPS,SEMI_LAT,SEMI_AVAIL,ASYNC_TPS,ASYNC_LAT,ASYNC_AVAIL,CONSISTENCY,PERFORMANCE stateStyle
```

### Real-World Use Cases

```yaml
# Production replication strategy selection
use_case_patterns:
  financial_transactions:
    strategy: "Synchronous"
    rationale: "Zero data loss requirement"
    configuration:
      replicas: 3
      sync_mode: "all"
      timeout: "5s"
      fallback: "block_writes"
    examples:
      - "Payment processing"
      - "Account balance updates"
      - "Audit trail recording"

  content_management:
    strategy: "Semi-synchronous"
    rationale: "Balance between consistency and performance"
    configuration:
      replicas: 5
      sync_replicas: 2
      timeout: "1s"
      fallback: "async_mode"
    examples:
      - "Blog posts and articles"
      - "User profile updates"
      - "Catalog management"

  analytics_data:
    strategy: "Asynchronous"
    rationale: "High throughput, eventual consistency acceptable"
    configuration:
      replicas: 6
      lag_tolerance: "5min"
      batch_size: "10MB"
      compression: "enabled"
    examples:
      - "Event logging"
      - "Metrics collection"
      - "Clickstream data"

  session_storage:
    strategy: "Semi-synchronous"
    rationale: "User experience + some durability"
    configuration:
      replicas: 3
      sync_replicas: 1
      timeout: "100ms"
      fallback: "async_mode"
    examples:
      - "User sessions"
      - "Shopping carts"
      - "Temporary data"
```

### Failure Scenarios and Handling

```mermaid
graph TB
    subgraph Replication Failure Scenarios
        subgraph Synchronous Failures
            SYNC_FAIL[Secondary Down]
            SYNC_EFFECT[Write Blocking]
            SYNC_RECOVERY[Wait or Timeout]
        end

        subgraph Semi-Sync Failures
            SEMI_FAIL[Some Secondaries Down]
            SEMI_EFFECT[Degraded Performance]
            SEMI_RECOVERY[Fallback to Async]
        end

        subgraph Async Failures
            ASYNC_FAIL[Secondary Down]
            ASYNC_EFFECT[No Impact on Writes]
            ASYNC_RECOVERY[Catchup When Available]
        end

        subgraph Network Partition
            PARTITION[Primary Isolated]
            SPLIT_BRAIN[Split-Brain Risk]
            FENCING[Fencing Required]
        end
    end

    SYNC_FAIL --> SYNC_EFFECT
    SYNC_EFFECT --> SYNC_RECOVERY

    SEMI_FAIL --> SEMI_EFFECT
    SEMI_EFFECT --> SEMI_RECOVERY

    ASYNC_FAIL --> ASYNC_EFFECT
    ASYNC_EFFECT --> ASYNC_RECOVERY

    PARTITION --> SPLIT_BRAIN
    SPLIT_BRAIN --> FENCING

    %% Apply colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class SYNC_FAIL,SEMI_FAIL,ASYNC_FAIL,PARTITION edgeStyle
    class SYNC_EFFECT,SEMI_EFFECT,ASYNC_EFFECT serviceStyle
    class SYNC_RECOVERY,SEMI_RECOVERY,ASYNC_RECOVERY stateStyle
    class SPLIT_BRAIN,FENCING controlStyle
```

### Monitoring and Alerting

```yaml
# Prometheus alerts for replication health
replication_alerts:
  - alert: ReplicationLagHigh
    expr: mysql_slave_lag_seconds > 30
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "MySQL replication lag is high"
      description: "Replication lag is {{ $value }} seconds"

  - alert: SemiSyncSlaveCount
    expr: mysql_semi_sync_master_clients < 1
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "No semi-sync slaves available"

  - alert: ReplicationBroken
    expr: mysql_slave_sql_running == 0 or mysql_slave_io_running == 0
    for: 30s
    labels:
      severity: critical
    annotations:
      summary: "MySQL replication is broken"

  - alert: SynchronousCommitTimeout
    expr: increase(postgresql_sync_commit_timeouts_total[5m]) > 0
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "PostgreSQL synchronous commit timeouts detected"
```

### Best Practices

#### Synchronous Replication
- **Use for**: Financial data, critical system state
- **Monitoring**: Track commit latency and timeout rates
- **Tuning**: Minimize network latency between replicas
- **Failover**: Plan for all-or-nothing availability

#### Semi-Synchronous Replication
- **Use for**: User-facing applications requiring durability
- **Monitoring**: Track which replicas are sync vs async
- **Tuning**: Configure appropriate timeouts and fallback behavior
- **Failover**: Ensure minimum sync replica count

#### Asynchronous Replication
- **Use for**: Analytics, logging, non-critical data
- **Monitoring**: Track replication lag and catch-up speed
- **Tuning**: Optimize batch sizes and network bandwidth
- **Failover**: Plan for potential data loss during failover

### Decision Framework

```mermaid
flowchart TD
    START[Choose Replication Strategy]

    CONSISTENCY{Can tolerate<br/>data loss?}
    LATENCY{Latency<br/>sensitive?}
    AVAILABILITY{High availability<br/>required?}
    REPLICAS{How many<br/>replicas?}

    SYNC[Synchronous<br/>Replication]
    SEMI[Semi-Synchronous<br/>Replication]
    ASYNC[Asynchronous<br/>Replication]

    START --> CONSISTENCY
    CONSISTENCY -->|No| LATENCY
    CONSISTENCY -->|Yes| AVAILABILITY

    LATENCY -->|High sensitivity| SEMI
    LATENCY -->|Low sensitivity| SYNC

    AVAILABILITY -->|Critical| ASYNC
    AVAILABILITY -->|Moderate| SEMI

    %% Apply colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class START edgeStyle
    class CONSISTENCY,LATENCY,AVAILABILITY,REPLICAS serviceStyle
    class SYNC,SEMI,ASYNC controlStyle
```

This comprehensive overview of replication strategies provides the foundation for making informed architectural decisions based on consistency, performance, and availability requirements.