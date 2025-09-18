# MySQL Performance Profile

## Overview

MySQL performance characteristics in production environments, covering InnoDB optimization, replication, partitioning, and threading models. Based on Uber's Schemaless implementation and other high-scale deployments.

## InnoDB Buffer Pool Optimization

### Buffer Pool Architecture and Sizing

```mermaid
graph TB
    subgraph "InnoDB Buffer Pool Structure"
        BP1[Buffer Pool Instance 1<br/>Size: 2GB<br/>Pages: 131,072<br/>LRU list length: 104,857]

        BP2[Buffer Pool Instance 2<br/>Size: 2GB<br/>Pages: 131,072<br/>Free list length: 26,214]

        BP3[Buffer Pool Instance 8<br/>Size: 2GB<br/>Total pool: 16GB<br/>Hit ratio: 99.8%]

        subgraph "Page Management"
            LRU[LRU List<br/>Old pages: 3/8<br/>Young pages: 5/8<br/>Page age threshold: 1000ms]

            FREE[Free List<br/>Available pages<br/>Background flushing<br/>Adaptive flushing enabled]

            FLUSH[Flush List<br/>Dirty pages<br/>Checkpoint age<br/>Max dirty: 75%]
        end

        BP1 --> LRU
        BP2 --> FREE
        BP3 --> FLUSH
    end

    subgraph "Performance Impact"
        P1[Buffer pool hit ratio<br/>Target: > 99%<br/>Achieved: 99.8%<br/>Physical reads: 2%]

        P2[Page flush rate<br/>Adaptive algorithm<br/>I/O capacity: 20,000 IOPS<br/>Dirty page limit: 12GB]
    end

    classDef poolStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef mgmtStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef perfStyle fill:#00AA00,stroke:#007700,color:#fff

    class BP1,BP2,BP3 poolStyle
    class LRU,FREE,FLUSH mgmtStyle
    class P1,P2 perfStyle
```

### Buffer Pool Tuning Results - Uber Schemaless

```mermaid
graph LR
    subgraph "Before Optimization"
        B1[innodb_buffer_pool_size = 4GB<br/>innodb_buffer_pool_instances = 1<br/>Hit ratio: 95%<br/>Query latency p95: 15ms]
    end

    subgraph "After Optimization"
        A1[innodb_buffer_pool_size = 48GB<br/>innodb_buffer_pool_instances = 16<br/>Hit ratio: 99.8%<br/>Query latency p95: 2ms]
    end

    subgraph "Configuration Changes"
        C1[Buffer pool sizing<br/>75% of available RAM<br/>64GB server → 48GB pool]

        C2[Instance count<br/>16 instances for better concurrency<br/>Reduces mutex contention]

        C3[Page flushing<br/>innodb_io_capacity = 20000<br/>innodb_io_capacity_max = 40000]
    end

    B1 --> A1
    A1 --> C1
    C1 --> C2
    C2 --> C3

    classDef beforeStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef afterStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef configStyle fill:#0066CC,stroke:#004499,color:#fff

    class B1 beforeStyle
    class A1 afterStyle
    class C1,C2,C3 configStyle
```

## Group Replication Performance

### Group Replication Architecture

```mermaid
graph TB
    subgraph "MySQL Group Replication Cluster"
        M1[(Master 1<br/>Primary mode<br/>Write load: 30K TPS<br/>Group communication: 50ms)]

        M2[(Master 2<br/>Secondary<br/>Read load: 100K QPS<br/>Apply lag: 20ms)]

        M3[(Master 3<br/>Secondary<br/>Read load: 80K QPS<br/>Apply lag: 25ms)]

        subgraph "Group Communication"
            GC[XCom Consensus<br/>Paxos protocol<br/>Majority voting<br/>Network partition tolerance]

            GL[Group Logging<br/>Binary log events<br/>GTIDs coordination<br/>Conflict detection]
        end

        M1 <--> GC
        M2 <--> GC
        M3 <--> GC
        GC --> GL
    end

    subgraph "Performance Metrics"
        P1[Transaction certification<br/>Success rate: 99.5%<br/>Conflict rate: 0.5%<br/>Latency overhead: 5ms]

        P2[Network overhead<br/>Bandwidth: 50 Mbps<br/>Message size: 1-2KB avg<br/>Round-trip time: 2ms]
    end

    classDef masterStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef commStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef perfStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class M1,M2,M3 masterStyle
    class GC,GL commStyle
    class P1,P2 perfStyle
```

### Group Replication vs Traditional Replication

```mermaid
graph LR
    subgraph "Traditional Master-Slave"
        T1[Master<br/>Writes: All<br/>Reads: Optional]
        T2[Slave 1<br/>Lag: 100ms<br/>Consistent: Eventually]
        T3[Slave 2<br/>Lag: 200ms<br/>Consistent: Eventually]

        T1 --> T2
        T1 --> T3

        T4[Failover: Manual<br/>RTO: 5-10 minutes<br/>Data loss: Possible]
    end

    subgraph "Group Replication"
        G1[Primary<br/>Writes: All<br/>Synchronous commit]
        G2[Secondary 1<br/>Lag: 20ms<br/>Consistent: Strong]
        G3[Secondary 2<br/>Lag: 25ms<br/>Consistent: Strong]

        G1 <--> G2
        G2 <--> G3
        G3 <--> G1

        G4[Failover: Automatic<br/>RTO: 30 seconds<br/>Data loss: None]
    end

    classDef traditionalStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef groupStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef metricStyle fill:#0066CC,stroke:#004499,color:#fff

    class T1,T2,T3 traditionalStyle
    class G1,G2,G3 groupStyle
    class T4,G4 metricStyle
```

## Partition Pruning Benefits

### Range Partitioning Performance

```mermaid
graph TB
    subgraph "Partitioned Table - Order History"
        P1[Partition 2024_Q1<br/>Rows: 10M<br/>Size: 2GB<br/>Index size: 200MB]

        P2[Partition 2024_Q2<br/>Rows: 12M<br/>Size: 2.4GB<br/>Index size: 240MB]

        P3[Partition 2024_Q3<br/>Rows: 15M<br/>Size: 3GB<br/>Index size: 300MB]

        P4[Partition 2024_Q4<br/>Rows: 18M<br/>Size: 3.6GB<br/>Index size: 360MB]
    end

    subgraph "Query Performance"
        Q1[SELECT * FROM orders<br/>WHERE order_date >= '2024-10-01'<br/>AND order_date < '2024-11-01']

        Q2[Partition pruning<br/>Examines: P4 only<br/>Rows scanned: 3M instead of 55M<br/>Query time: 0.5s vs 8s]

        Q1 --> Q2
    end

    subgraph "Maintenance Benefits"
        M1[Partition dropping<br/>DELETE old data: 0.1s<br/>vs DELETE command: 2 hours]

        M2[Index maintenance<br/>Per-partition indexes<br/>Rebuild time: 10min vs 4 hours]

        M3[Backup strategy<br/>Incremental per partition<br/>Recovery granularity improved]
    end

    classDef partitionStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef queryStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef maintStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class P1,P2,P3,P4 partitionStyle
    class Q1,Q2 queryStyle
    class M1,M2,M3 maintStyle
```

### Hash Partitioning for Load Distribution

```mermaid
graph TB
    subgraph "Hash Partitioned User Table"
        H1[Partition 0<br/>hash user_id % 8 = 0<br/>Rows: 12.5M<br/>Hotness: Even]

        H2[Partition 1<br/>hash user_id % 8 = 1<br/>Rows: 12.5M<br/>Hotness: Even]

        H3[Partition 7<br/>hash user_id % 8 = 7<br/>Rows: 12.5M<br/>Hotness: Even]

        H4[Total: 100M users<br/>Even distribution<br/>No hot partitions]
    end

    subgraph "Load Balancing Results"
        L1[Write distribution<br/>Each partition: 12.5K TPS<br/>No bottlenecks<br/>Linear scaling]

        L2[Read distribution<br/>Cache hit ratio: 95%<br/>Buffer pool efficiency<br/>Parallel query execution]
    end

    subgraph "vs Single Table"
        S1[Single table issues<br/>Lock contention<br/>Buffer pool thrashing<br/>Index hotspots]

        S2[Partition benefits<br/>Parallel processing<br/>Reduced lock scope<br/>Better cache locality]
    end

    classDef hashStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef loadStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef compStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class H1,H2,H3,H4 hashStyle
    class L1,L2 loadStyle
    class S1,S2 compStyle
```

## Thread Pool vs Connection-per-Thread

### Threading Model Comparison

```mermaid
graph LR
    subgraph "Connection-per-Thread (Default)"
        CT1[Client 1] --> T1[Thread 1<br/>Memory: 2MB<br/>Context switches: High]
        CT2[Client 2] --> T2[Thread 2<br/>Memory: 2MB<br/>Dedicated connection]
        CT3[Client 1000] --> T1000[Thread 1000<br/>Memory: 2GB total<br/>Scheduler overhead: High]
    end

    subgraph "Thread Pool"
        TP1[Client 1] --> P1[Thread Pool<br/>Size: 64 threads<br/>Memory: 128MB]
        TP2[Client 2] --> P1
        TP3[Client 1000] --> P1

        P1 --> W1[Worker 1<br/>Multiple clients<br/>Efficient scheduling]
        P1 --> W2[Worker 64<br/>Better CPU utilization<br/>Reduced context switching]
    end

    subgraph "Performance Impact"
        PI1[Connection-per-thread<br/>Max connections: 1000<br/>Memory: 2GB threads<br/>Context switches: 50K/sec]

        PI2[Thread pool<br/>Max connections: 10000<br/>Memory: 128MB threads<br/>Context switches: 5K/sec]
    end

    classDef traditionalStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef poolStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef metricStyle fill:#0066CC,stroke:#004499,color:#fff

    class CT1,CT2,CT3,T1,T2,T1000 traditionalStyle
    class TP1,TP2,TP3,P1,W1,W2 poolStyle
    class PI1,PI2 metricStyle
```

### Thread Pool Configuration Impact

```mermaid
graph TB
    subgraph "Thread Pool Sizing Strategy"
        S1[thread_pool_size = CPU cores<br/>For CPU-bound workloads<br/>64 cores = 64 threads]

        S2[thread_pool_size = 2 × CPU cores<br/>For mixed workloads<br/>64 cores = 128 threads]

        S3[thread_pool_size = 4 × CPU cores<br/>For I/O-bound workloads<br/>64 cores = 256 threads]
    end

    subgraph "Real Performance Results"
        R1[CPU-bound sizing<br/>Latency p95: 5ms<br/>Throughput: 80K QPS<br/>CPU utilization: 95%]

        R2[Mixed workload sizing<br/>Latency p95: 8ms<br/>Throughput: 120K QPS<br/>CPU utilization: 85%]

        R3[I/O-bound sizing<br/>Latency p95: 15ms<br/>Throughput: 150K QPS<br/>CPU utilization: 70%]
    end

    S1 --> R1
    S2 --> R2
    S3 --> R3

    classDef strategyStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef resultStyle fill:#00AA00,stroke:#007700,color:#fff

    class S1,S2,S3 strategyStyle
    class R1,R2,R3 resultStyle
```

## Uber's Schemaless Implementation Metrics

### Schemaless Architecture Performance

```mermaid
graph TB
    subgraph "Uber Schemaless Layer"
        APP[Uber Application<br/>Requests: 1M QPS<br/>Latency target: < 5ms p99]

        SCHEMA[Schemaless Layer<br/>Connection pooling<br/>Intelligent routing<br/>Consistent hashing]

        subgraph "MySQL Shards"
            S1[(Shard 1<br/>Users: 10M<br/>TPS: 50K<br/>Storage: 2TB)]

            S2[(Shard 2<br/>Users: 10M<br/>TPS: 50K<br/>Storage: 2TB)]

            S16[(Shard 16<br/>Users: 10M<br/>TPS: 50K<br/>Storage: 2TB)]
        end

        APP --> SCHEMA
        SCHEMA --> S1
        SCHEMA --> S2
        SCHEMA --> S16
    end

    subgraph "Performance Achievements"
        P1[Total throughput: 800K TPS<br/>Read latency p99: 2ms<br/>Write latency p99: 5ms<br/>Availability: 99.99%]

        P2[Scaling characteristics<br/>Linear scaling to 200+ shards<br/>No cross-shard transactions<br/>Automatic failover: 30s]
    end

    classDef appStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef schemaStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef shardStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef perfStyle fill:#CC0000,stroke:#990000,color:#fff

    class APP appStyle
    class SCHEMA schemaStyle
    class S1,S2,S16 shardStyle
    class P1,P2 perfStyle
```

### Key Configuration Parameters

```mermaid
graph LR
    subgraph "InnoDB Configuration"
        I1[innodb_buffer_pool_size = 48GB<br/>innodb_buffer_pool_instances = 16<br/>innodb_log_file_size = 2GB<br/>innodb_flush_log_at_trx_commit = 1]
    end

    subgraph "Performance Configuration"
        P1[max_connections = 2000<br/>thread_pool_size = 128<br/>query_cache_type = OFF<br/>innodb_io_capacity = 20000]
    end

    subgraph "Replication Configuration"
        R1[log_bin = ON<br/>binlog_format = ROW<br/>sync_binlog = 1<br/>gtid_mode = ON]
    end

    subgraph "Results"
        RES1[Peak QPS: 50K per shard<br/>Buffer pool hit rate: 99.8%<br/>Replication lag: < 1s p99<br/>Crash recovery: < 30s]
    end

    I1 --> RES1
    P1 --> RES1
    R1 --> RES1

    classDef configStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef resultStyle fill:#00AA00,stroke:#007700,color:#fff

    class I1,P1,R1 configStyle
    class RES1 resultStyle
```

## Production Optimization Strategies

### Query Optimization Pipeline

```mermaid
graph TB
    subgraph "Slow Query Analysis"
        SQ1[Enable slow_query_log<br/>long_query_time = 0.1<br/>log_queries_not_using_indexes = ON]

        SQ2[Query analysis tools<br/>pt-query-digest<br/>Performance Schema<br/>sys schema views]

        SQ1 --> SQ2
    end

    subgraph "Index Optimization"
        IO1[Missing index detection<br/>EXPLAIN analysis<br/>Index usage statistics<br/>Duplicate index removal]

        IO2[Composite index strategy<br/>Left-most prefix rule<br/>Covering indexes<br/>Index merge optimization]

        IO1 --> IO2
    end

    subgraph "Results Achieved"
        R1[Query performance<br/>p95 latency: 15ms → 2ms<br/>Index efficiency: 85% → 99%<br/>Full table scans: 5% → 0.1%]
    end

    SQ2 --> IO1
    IO2 --> R1

    classDef analysisStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef optimStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef resultStyle fill:#00AA00,stroke:#007700,color:#fff

    class SQ1,SQ2 analysisStyle
    class IO1,IO2 optimStyle
    class R1 resultStyle
```

### Critical Lessons Learned

1. **Buffer Pool Sizing**: 75% of RAM is optimal for most workloads
2. **Thread Pool**: Essential for high-concurrency applications (> 1000 connections)
3. **Partitioning**: Mandatory for tables > 100GB or high-velocity time-series data
4. **Group Replication**: Adds 5-10ms latency but provides strong consistency
5. **Connection Pooling**: Application-level pooling more effective than MySQL thread pool alone

**Performance Benchmarks**:
- **Small Scale** (< 10K QPS): Single server, basic configuration
- **Medium Scale** (10K-100K QPS): Read replicas, partitioning, optimized configuration
- **Large Scale** (> 100K QPS): Sharding, advanced replication, specialized hardware

**Source**: Based on Uber Schemaless, Shopify, and GitHub MySQL implementations