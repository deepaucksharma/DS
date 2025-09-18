# PostgreSQL Performance Profile

## Overview

PostgreSQL performance characteristics in production environments, covering connection pooling, query optimization, replication, and maintenance operations. Based on real-world deployments handling 100K+ TPS.

## Connection Pooling Impact - PgBouncer Analysis

### Before vs After PgBouncer Implementation

```mermaid
graph TB
    subgraph Before PgBouncer - Direct Connections
        APP1[App Server 1<br/>100 connections]
        APP2[App Server 2<br/>100 connections]
        APP3[App Server 3<br/>100 connections]

        PG1[(PostgreSQL<br/>max_connections=300<br/>Context switches: 15K/sec<br/>Memory: 2.4GB)]

        APP1 --> PG1
        APP2 --> PG1
        APP3 --> PG1
    end

    subgraph After PgBouncer - Pooled Connections
        APP4[App Server 1<br/>100 connections]
        APP5[App Server 2<br/>100 connections]
        APP6[App Server 3<br/>100 connections]

        PB[PgBouncer<br/>pool_size=25<br/>max_client_conn=400]

        PG2[(PostgreSQL<br/>Active connections: 25<br/>Context switches: 2K/sec<br/>Memory: 800MB)]

        APP4 --> PB
        APP5 --> PB
        APP6 --> PB
        PB --> PG2
    end

    classDef appStyle fill:#10B981,stroke:#059669,color:#fff
    classDef poolStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef dbStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class APP1,APP2,APP3,APP4,APP5,APP6 appStyle
    class PB poolStyle
    class PG1,PG2 dbStyle
```

**Performance Improvement:**
- **Latency**: p99 reduced from 45ms to 12ms
- **Throughput**: 40K TPS to 100K TPS
- **Memory**: 60% reduction in PostgreSQL memory usage
- **CPU**: 70% reduction in context switching overhead

### PgBouncer Configuration Comparison

```mermaid
graph LR
    subgraph Session Pooling
        S1[Client] --> S2[PgBouncer<br/>Session Mode]
        S2 --> S3[PostgreSQL<br/>1:1 mapping]
        S4[Latency: 2ms overhead<br/>Transactions: All supported<br/>Memory: High]
    end

    subgraph Transaction Pooling
        T1[Client] --> T2[PgBouncer<br/>Transaction Mode]
        T2 --> T3[PostgreSQL<br/>Shared connections]
        T4[Latency: 0.5ms overhead<br/>Transactions: Limited<br/>Memory: Low]
    end

    subgraph Statement Pooling
        ST1[Client] --> ST2[PgBouncer<br/>Statement Mode]
        ST2 --> ST3[PostgreSQL<br/>Highly shared]
        ST4[Latency: 0.2ms overhead<br/>Transactions: None<br/>Memory: Minimal]
    end

    classDef clientStyle fill:#10B981,stroke:#059669,color:#fff
    classDef poolStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef dbStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef metricStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class S1,T1,ST1 clientStyle
    class S2,T2,ST2 poolStyle
    class S3,T3,ST3 dbStyle
    class S4,T4,ST4 metricStyle
```

## Query Performance: OLTP vs OLAP Patterns

### OLTP Optimization Pattern

```mermaid
graph TB
    subgraph OLTP Query Pattern - Instagram Photo Upload
        Q1[SELECT user_id, username<br/>FROM users<br/>WHERE user_id = $1]
        Q1 --> I1[B-tree index on user_id<br/>Rows examined: 1<br/>Execution time: 0.2ms]

        Q2[INSERT INTO photos<br/>user_id, photo_url, created_at<br/>VALUES $1, $2, NOW]
        Q2 --> I2[Primary key + foreign key<br/>Lock time: 0.1ms<br/>WAL write: 0.3ms]

        Q3[UPDATE user_stats<br/>SET photo_count = photo_count + 1<br/>WHERE user_id = $1]
        Q3 --> I3[Row-level lock<br/>Index update: 0.2ms<br/>Total: 0.8ms]
    end

    subgraph Performance Characteristics
        P1[Target: < 1ms p95<br/>Achieved: 0.8ms p95<br/>QPS: 50K per core<br/>Index size: 2GB]
    end

    classDef queryStyle fill:#10B981,stroke:#059669,color:#fff
    classDef indexStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef metricStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class Q1,Q2,Q3 queryStyle
    class I1,I2,I3 indexStyle
    class P1 metricStyle
```

### OLAP Optimization Pattern

```mermaid
graph TB
    subgraph OLAP Query Pattern - Daily Analytics
        Q1[SELECT date_trunc 'day', created_at,<br/>COUNT, AVG revenue<br/>FROM orders<br/>WHERE created_at >= NOW - INTERVAL '30 days'<br/>GROUP BY 1 ORDER BY 1]

        Q1 --> P1[Parallel Query Plan<br/>Workers: 8<br/>Shared buffers: 2GB<br/>Work_mem: 256MB per worker]

        P1 --> I1[Parallel Seq Scan<br/>Rows: 10M<br/>Filtering: date range]

        P1 --> I2[Parallel Hash Aggregate<br/>Groups: 30<br/>Memory: 512MB]

        I1 --> R1[Result<br/>Execution: 15 seconds<br/>Rows returned: 30]
        I2 --> R1
    end

    subgraph Optimization Strategy
        O1[Partitioning by date<br/>Index on created_at<br/>Materialized views<br/>Columnar storage pg_column]
        O1 --> O2[Before: 45 seconds<br/>After: 3 seconds<br/>Memory: 4GB → 1GB]
    end

    classDef queryStyle fill:#10B981,stroke:#059669,color:#fff
    classDef planStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef optimStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef metricStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class Q1 queryStyle
    class P1,I1,I2 planStyle
    class O1 optimStyle
    class R1,O2 metricStyle
```

## Replication Lag Under Load

### Streaming Replication Performance

```mermaid
graph LR
    subgraph Primary Database
        P1[(Primary<br/>Write load: 50K TPS<br/>WAL generation: 2GB/hour<br/>Checkpoint frequency: 5min)]
    end

    subgraph Synchronous Replica
        S1[(Sync Replica<br/>Apply lag: 2ms p95<br/>Network: 1Gbps<br/>Disk: NVMe SSD)]
    end

    subgraph Asynchronous Replicas
        A1[(Async Replica 1<br/>Apply lag: 100ms p95<br/>Network: 100Mbps<br/>Disk: SSD)]
        A2[(Async Replica 2<br/>Apply lag: 500ms p95<br/>Network: 10Mbps<br/>Disk: HDD)]
    end

    P1 -->|WAL streaming<br/>Latency: 1ms| S1
    P1 -->|WAL streaming<br/>Latency: 50ms| A1
    P1 -->|WAL streaming<br/>Latency: 200ms| A2

    subgraph Lag Monitoring
        M1[pg_stat_replication<br/>sent_lsn - flush_lsn<br/>Alert: > 1GB lag<br/>Critical: > 5GB lag]
    end

    classDef primaryStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef syncStyle fill:#10B981,stroke:#059669,color:#fff
    classDef asyncStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef monitorStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class P1 primaryStyle
    class S1 syncStyle
    class A1,A2 asyncStyle
    class M1 monitorStyle
```

### Replication Conflict Resolution

```mermaid
graph TB
    subgraph Hot Standby Conflicts
        C1[Long running query<br/>on standby: 10 minutes]
        C2[Vacuum cleanup<br/>on primary removes rows]
        C3[WAL record conflicts<br/>with standby query]

        C1 --> C2
        C2 --> C3

        C3 --> R1[Query cancellation<br/>max_standby_streaming_delay<br/>Default: 30s]
        C3 --> R2[WAL apply delay<br/>Recovery may lag behind<br/>Risk: Replica divergence]
    end

    subgraph Conflict Resolution Settings
        S1[hot_standby_feedback = on<br/>Prevents cleanup conflicts<br/>Side effect: Primary bloat]

        S2[max_standby_streaming_delay = 5min<br/>Allows longer queries<br/>Side effect: Replication lag]

        S3[Application-level retry<br/>Catch 40001 error code<br/>Retry on read replica]
    end

    classDef conflictStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef resolutionStyle fill:#10B981,stroke:#059669,color:#fff
    classDef settingStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class C1,C2,C3 conflictStyle
    class R1,R2 resolutionStyle
    class S1,S2,S3 settingStyle
```

## Vacuum and Autovacuum Tuning

### Vacuum Performance Impact

```mermaid
graph TB
    subgraph Table Growth Pattern
        T1[Initial state<br/>1M rows, 500MB<br/>Dead tuples: 0]
        T2[After updates<br/>1M rows, 750MB<br/>Dead tuples: 30%]
        T3[After vacuum<br/>1M rows, 500MB<br/>Dead tuples: 0]
        T4[Vacuum stats<br/>Duration: 45 seconds<br/>I/O: 2GB read/write]

        T1 --> T2 --> T3
        T3 --> T4
    end

    subgraph Autovacuum Configuration
        A1[autovacuum_vacuum_threshold = 50<br/>autovacuum_vacuum_scale_factor = 0.2<br/>Trigger at 20% dead tuples]

        A2[autovacuum_max_workers = 4<br/>autovacuum_work_mem = 1GB<br/>Parallel maintenance]

        A3[autovacuum_naptime = 1min<br/>Check frequency<br/>Balance between lag and overhead]
    end

    subgraph Performance Impact
        P1[Before optimization<br/>Query performance degrades 40%<br/>Autovacuum blocks reads]

        P2[After optimization<br/>Query performance stable<br/>Background maintenance]
    end

    classDef tableStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef configStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#10B981,stroke:#059669,color:#fff

    class T1,T2,T3,T4 tableStyle
    class A1,A2,A3 configStyle
    class P1,P2 perfStyle
```

### VACUUM vs VACUUM FULL Comparison

```mermaid
graph LR
    subgraph VACUUM (Standard)
        V1[Operation: Mark dead tuples<br/>Lock level: Share Update Exclusive<br/>Duration: Minutes<br/>Space reclaim: Partial]

        V2[I/O Pattern<br/>Sequential reads<br/>Minimal writes<br/>Index updates only]

        V3[Concurrent access<br/>Reads: Allowed<br/>Writes: Allowed<br/>DDL: Blocked]
    end

    subgraph VACUUM FULL
        VF1[Operation: Rewrite table<br/>Lock level: Access Exclusive<br/>Duration: Hours<br/>Space reclaim: Complete]

        VF2[I/O Pattern<br/>Full table rewrite<br/>Heavy I/O load<br/>Rebuild all indexes]

        VF3[Concurrent access<br/>Reads: Blocked<br/>Writes: Blocked<br/>DDL: Blocked]
    end

    subgraph Production Usage
        U1[Standard VACUUM<br/>Daily automated<br/>Low impact<br/>Maintenance windows not required]

        U2[VACUUM FULL<br/>Monthly/quarterly<br/>Scheduled downtime<br/>Major space reclamation]
    end

    classDef standardStyle fill:#10B981,stroke:#059669,color:#fff
    classDef fullStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef usageStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class V1,V2,V3,U1 standardStyle
    class VF1,VF2,VF3,U2 fullStyle
    class U1,U2 usageStyle
```

## Real Benchmarks: 100K TPS Achievement

### Hardware Configuration - Instagram Scale

```mermaid
graph TB
    subgraph Database Server Configuration
        HW1[Server: AWS RDS db.r6i.24xlarge<br/>CPU: 96 vCPUs Intel Xeon<br/>Memory: 768 GB<br/>Network: 50 Gbps<br/>Storage: gp3 20,000 IOPS]
    end

    subgraph PostgreSQL Configuration
        PG1[shared_buffers = 192GB<br/>effective_cache_size = 576GB<br/>work_mem = 256MB<br/>maintenance_work_mem = 2GB]

        PG2[max_connections = 400<br/>max_wal_size = 16GB<br/>checkpoint_timeout = 15min<br/>checkpoint_completion_target = 0.9]

        PG3[random_page_cost = 1.1<br/>effective_io_concurrency = 200<br/>max_worker_processes = 96<br/>max_parallel_workers = 32]
    end

    subgraph Workload Characteristics
        W1[Read/Write ratio: 95/5<br/>Average query time: 0.8ms<br/>Connection lifetime: 30 minutes<br/>Peak QPS: 100,000]

        W2[Primary use cases<br/>User profile lookups<br/>Timeline generation<br/>Photo metadata queries<br/>Like/comment counts]
    end

    classDef hwStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef configStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef workloadStyle fill:#10B981,stroke:#059669,color:#fff

    class HW1 hwStyle
    class PG1,PG2,PG3 configStyle
    class W1,W2 workloadStyle
```

### Performance Scaling Timeline

```mermaid
graph LR
    subgraph Scale Evolution
        S1[Week 1<br/>1K TPS<br/>Single server<br/>Basic config]

        S2[Month 1<br/>10K TPS<br/>Read replicas added<br/>Connection pooling]

        S3[Month 6<br/>50K TPS<br/>Partitioning<br/>Optimized queries]

        S4[Month 12<br/>100K TPS<br/>Sharding<br/>Advanced tuning]

        S1 --> S2 --> S3 --> S4
    end

    subgraph Key Optimizations
        O1[1K → 10K TPS<br/>• PgBouncer deployment<br/>• Read replica scaling<br/>• Query optimization]

        O2[10K → 50K TPS<br/>• Table partitioning<br/>• Index optimization<br/>• Connection pooling tuning]

        O3[50K → 100K TPS<br/>• Application-level sharding<br/>• Hardware scaling<br/>• Advanced PostgreSQL tuning]
    end

    classDef scaleStyle fill:#10B981,stroke:#059669,color:#fff
    classDef optimStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class S1,S2,S3,S4 scaleStyle
    class O1,O2,O3 optimStyle
```

## Production Lessons Learned

### Critical Configuration Parameters

| Parameter | Small Scale | Medium Scale | Large Scale | Reasoning |
|-----------|-------------|--------------|-------------|-----------|
| shared_buffers | 128MB | 8GB | 192GB | 25% of available RAM |
| max_connections | 100 | 200 | 400 | Balance with connection pooling |
| work_mem | 4MB | 64MB | 256MB | Query complexity dependent |
| checkpoint_timeout | 5min | 10min | 15min | Balance durability vs performance |
| effective_cache_size | 4GB | 32GB | 576GB | 75% of available RAM |

### Common Performance Pitfalls

1. **Under-configured shared_buffers**: Default 128MB insufficient for production
2. **No connection pooling**: Direct connections exhaust server resources
3. **Missing indexes**: Query performance degrades exponentially
4. **Aggressive autovacuum**: Can block operations during peak hours
5. **Inadequate monitoring**: Problems discovered too late

**Source**: Based on Instagram, Uber, and Stripe PostgreSQL implementations