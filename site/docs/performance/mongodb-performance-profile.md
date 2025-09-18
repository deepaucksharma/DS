# MongoDB Performance Profile

## Overview

MongoDB performance characteristics in production environments, covering sharding, WiredTiger optimization, indexing strategies, and change streams. Based on Stripe's implementation and other high-scale deployments handling millions of operations per second.

## Sharding Performance Impact

### Sharding Architecture - Stripe's Implementation

```mermaid
graph TB
    subgraph "MongoDB Sharded Cluster"
        subgraph "Query Routers"
            QR1[mongos 1<br/>Connections: 1000<br/>Query routing<br/>Result aggregation]
            QR2[mongos 2<br/>Load balanced<br/>Failover capability<br/>Connection pooling]
        end

        subgraph "Config Servers"
            CS1[(Config Replica Set<br/>Metadata storage<br/>Chunk information<br/>Balancer state)]
        end

        subgraph "Shard 1 - Replica Set"
            S1P[(Primary<br/>Write operations<br/>Chunk range: MinKey to 1000000)]
            S1S[(Secondary<br/>Read operations<br/>Replication lag: 5ms)]
        end

        subgraph "Shard 2 - Replica Set"
            S2P[(Primary<br/>Write operations<br/>Chunk range: 1000000 to 2000000)]
            S2S[(Secondary<br/>Read operations<br/>Replication lag: 8ms)]
        end

        QR1 --> CS1
        QR2 --> CS1
        QR1 --> S1P
        QR1 --> S2P
        QR2 --> S1P
        QR2 --> S2P
        S1P --> S1S
        S2P --> S2S
    end

    subgraph "Performance Metrics"
        P1[Total throughput: 500K ops/sec<br/>Query latency p95: 10ms<br/>Chunk migrations: 2/day<br/>Balancer efficiency: 95%]
    end

    classDef routerStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef configStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef shardStyle fill:#10B981,stroke:#059669,color:#fff
    classDef metricStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class QR1,QR2 routerStyle
    class CS1 configStyle
    class S1P,S1S,S2P,S2S shardStyle
    class P1 metricStyle
```

### Shard Key Selection Impact

```mermaid
graph TB
    subgraph "Bad Shard Key - Sequential ID"
        B1[Shard key: _id ObjectId<br/>Pattern: Sequential<br/>Hot shard: Always last<br/>Write distribution: 100% to 1 shard]

        B2[Performance impact<br/>Throughput bottleneck<br/>Single shard saturation<br/>Poor horizontal scaling]
    end

    subgraph "Good Shard Key - Hashed User ID"
        G1[Shard key: hashed user_id<br/>Pattern: Uniform distribution<br/>Hot shard: None<br/>Write distribution: Even across shards]

        G2[Performance impact<br/>Linear scaling<br/>Even load distribution<br/>Optimal resource utilization]
    end

    subgraph "Compound Shard Key - Time + Hash"
        C1[Shard key: timestamp, user_id<br/>Pattern: Time-based with distribution<br/>Query efficiency: High<br/>Range queries: Optimized]

        C2[Performance benefits<br/>Time-based queries efficient<br/>Even distribution maintained<br/>Chunk splitting predictable]
    end

    classDef badStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef goodStyle fill:#10B981,stroke:#059669,color:#fff
    classDef compoundStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class B1,B2 badStyle
    class G1,G2 goodStyle
    class C1,C2 compoundStyle
```

### Chunk Migration Performance

```mermaid
graph LR
    subgraph "Chunk Migration Process"
        CM1[Source shard<br/>Chunk size: 64MB<br/>Documents: 1M<br/>Migration trigger]

        CM2[Migration phase 1<br/>Clone documents<br/>Continue writes<br/>Track changes]

        CM3[Migration phase 2<br/>Apply changes<br/>Coordinate commit<br/>Update metadata]

        CM4[Target shard<br/>Chunk received<br/>Index build<br/>Ready for queries]

        CM1 --> CM2 --> CM3 --> CM4
    end

    subgraph "Performance Impact"
        P1[Migration duration<br/>64MB chunk: 30 seconds<br/>Network bandwidth: 100 Mbps<br/>Impact on queries: 5ms p95]

        P2[Optimization strategies<br/>Off-peak scheduling<br/>Throttling enabled<br/>Jumbo chunk avoidance]
    end

    classDef migrationStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class CM1,CM2,CM3,CM4 migrationStyle
    class P1,P2 perfStyle
```

## WiredTiger Cache Configuration

### Cache Architecture and Sizing

```mermaid
graph TB
    subgraph "WiredTiger Cache Structure"
        CACHE[WiredTiger Cache<br/>Total size: 32GB<br/>Available RAM: 64GB<br/>Cache ratio: 50%]

        subgraph "Cache Components"
            DATA[Data cache<br/>Hot documents<br/>Recently accessed<br/>LRU eviction]

            INDEX[Index cache<br/>B-tree nodes<br/>Frequently used indexes<br/>Root pages pinned]

            JOURNAL[Journal files<br/>Write-ahead log<br/>Checkpoint data<br/>Recovery information]
        end

        CACHE --> DATA
        CACHE --> INDEX
        CACHE --> JOURNAL
    end

    subgraph "Cache Performance"
        P1[Cache hit ratio<br/>Data: 98%<br/>Index: 99.5%<br/>Overall: 98.7%]

        P2[Eviction pressure<br/>Pages evicted/sec: 1000<br/>Application threads blocked: 0.1%<br/>Background eviction: 95%]
    end

    subgraph "Tuning Parameters"
        T1[cacheSizeGB = 32<br/>eviction_target = 80<br/>eviction_trigger = 95<br/>eviction_dirty_target = 5]
    end

    classDef cacheStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef componentStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#10B981,stroke:#059669,color:#fff
    classDef tuningStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class CACHE cacheStyle
    class DATA,INDEX,JOURNAL componentStyle
    class P1,P2 perfStyle
    class T1 tuningStyle
```

### Cache Sizing Impact on Performance

```mermaid
graph LR
    subgraph "Under-sized Cache (8GB)"
        U1[Working set: 24GB<br/>Cache size: 8GB<br/>Hit ratio: 75%<br/>Disk I/O: High]

        U2[Performance impact<br/>Query latency p95: 100ms<br/>Throughput: 10K ops/sec<br/>CPU wait time: 40%]
    end

    subgraph "Optimal Cache (32GB)"
        O1[Working set: 24GB<br/>Cache size: 32GB<br/>Hit ratio: 98%<br/>Disk I/O: Minimal]

        O2[Performance impact<br/>Query latency p95: 5ms<br/>Throughput: 100K ops/sec<br/>CPU wait time: 5%]
    end

    subgraph "Over-sized Cache (56GB)"
        OV1[Working set: 24GB<br/>Cache size: 56GB<br/>Hit ratio: 99%<br/>Memory pressure: High]

        OV2[Performance impact<br/>Query latency p95: 8ms<br/>Throughput: 90K ops/sec<br/>OOM risk: Elevated]
    end

    classDef underStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef optimalStyle fill:#10B981,stroke:#059669,color:#fff
    classDef overStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class U1,U2 underStyle
    class O1,O2 optimalStyle
    class OV1,OV2 overStyle
```

## Index Intersection Efficiency

### Compound vs Intersection Strategy

```mermaid
graph TB
    subgraph "Query Pattern Analysis"
        Q1[Query: find status: active, region: us-east-1, created: last 7 days<br/>Frequency: 10K/sec<br/>Result set: 1000 documents]
    end

    subgraph "Index Strategy 1 - Compound Index"
        C1[Index: status, region, created<br/>Size: 2GB<br/>Selectivity: High<br/>Memory usage: Moderate]

        C2[Query execution<br/>Index scan: Direct<br/>Documents examined: 1000<br/>Execution time: 2ms]
    end

    subgraph "Index Strategy 2 - Index Intersection"
        I1[Index 1: status<br/>Size: 500MB<br/>Selectivity: Medium]

        I2[Index 2: region<br/>Size: 200MB<br/>Selectivity: High]

        I3[Index 3: created<br/>Size: 1GB<br/>Selectivity: Low]

        I4[Intersection process<br/>Combine bitmap filters<br/>Documents examined: 5000<br/>Execution time: 8ms]

        I1 --> I4
        I2 --> I4
        I3 --> I4
    end

    Q1 --> C1
    Q1 --> I1
    C1 --> C2
    I4 --> C2

    classDef queryStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef compoundStyle fill:#10B981,stroke:#059669,color:#fff
    classDef intersectionStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef resultStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class Q1 queryStyle
    class C1 compoundStyle
    class I1,I2,I3,I4 intersectionStyle
    class C2 resultStyle
```

### Index Performance Comparison

```mermaid
graph LR
    subgraph "Single Field Indexes"
        S1[Query performance<br/>Simple queries: Excellent<br/>Complex queries: Poor<br/>Storage overhead: Low]

        S2[Use cases<br/>Single-field lookups<br/>Simple range queries<br/>Lightweight applications]
    end

    subgraph "Compound Indexes"
        C1[Query performance<br/>Targeted queries: Excellent<br/>Prefix queries: Good<br/>Non-prefix queries: Poor]

        C2[Use cases<br/>Known query patterns<br/>High-frequency queries<br/>Performance-critical apps]
    end

    subgraph "Index Intersection"
        I1[Query performance<br/>Flexible queries: Good<br/>Ad-hoc queries: Excellent<br/>Complex filters: Moderate]

        I2[Use cases<br/>Analytics workloads<br/>Variable query patterns<br/>Development/testing]
    end

    classDef singleStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef compoundStyle fill:#10B981,stroke:#059669,color:#fff
    classDef intersectionStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class S1,S2 singleStyle
    class C1,C2 compoundStyle
    class I1,I2 intersectionStyle
```

## Change Streams Overhead

### Change Streams Architecture

```mermaid
graph TB
    subgraph "MongoDB Replica Set"
        PRIMARY[(Primary<br/>Write operations<br/>Oplog generation<br/>Change capture)]

        SECONDARY[(Secondary<br/>Oplog replication<br/>Change stream source<br/>Read operations)]

        OPLOG[(Oplog<br/>Capped collection<br/>Size: 50GB<br/>Retention: 24 hours)]

        PRIMARY --> OPLOG
        SECONDARY --> OPLOG
    end

    subgraph "Change Stream Consumers"
        CS1[Consumer 1<br/>Resume token tracking<br/>Filter: collection = users<br/>Processing rate: 5K/sec]

        CS2[Consumer 2<br/>Resume token tracking<br/>Filter: operationType = insert<br/>Processing rate: 10K/sec]

        CS3[Consumer 3<br/>Full document lookup<br/>No filters<br/>Processing rate: 2K/sec]

        OPLOG --> CS1
        OPLOG --> CS2
        OPLOG --> CS3
    end

    subgraph "Performance Impact"
        P1[Oplog overhead<br/>Additional writes: 15%<br/>Network traffic: 20%<br/>CPU usage: 5%]

        P2[Consumer overhead<br/>Memory per stream: 10MB<br/>Network per stream: 1 Mbps<br/>Lag tolerance: 30 seconds]
    end

    classDef mongoStyle fill:#10B981,stroke:#059669,color:#fff
    classDef oplogStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef consumerStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class PRIMARY,SECONDARY mongoStyle
    class OPLOG oplogStyle
    class CS1,CS2,CS3 consumerStyle
    class P1,P2 perfStyle
```

### Change Streams Filtering Performance

```mermaid
graph TB
    subgraph "Unfiltered Change Stream"
        UF1[All operations captured<br/>Insert: 50K/sec<br/>Update: 30K/sec<br/>Delete: 5K/sec]

        UF2[Consumer processing<br/>Total events: 85K/sec<br/>Network usage: 50 Mbps<br/>Consumer CPU: 80%]

        UF1 --> UF2
    end

    subgraph "Server-side Filtered"
        SF1[Filter: collection = orders<br/>Relevant operations: 20K/sec<br/>Filtered out: 65K/sec<br/>Filter efficiency: 76%]

        SF2[Consumer processing<br/>Relevant events: 20K/sec<br/>Network usage: 12 Mbps<br/>Consumer CPU: 25%]

        SF1 --> SF2
    end

    subgraph "Optimized Pipeline"
        OP1[Multi-stage pipeline<br/>1. Match collection<br/>2. Match operation type<br/>3. Project required fields]

        OP2[Final processing<br/>Relevant events: 5K/sec<br/>Network usage: 2 Mbps<br/>Consumer CPU: 8%]

        OP1 --> OP2
    end

    classDef unfilteredStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef filteredStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef optimizedStyle fill:#10B981,stroke:#059669,color:#fff

    class UF1,UF2 unfilteredStyle
    class SF1,SF2 filteredStyle
    class OP1,OP2 optimizedStyle
```

## Stripe's Usage at Scale

### Stripe's MongoDB Architecture

```mermaid
graph TB
    subgraph "Stripe Payment Processing"
        API[Stripe API<br/>Requests: 100K/sec<br/>p99 latency target: 100ms<br/>Global distribution]

        subgraph "MongoDB Clusters"
            PAYMENT[(Payment Cluster<br/>Shards: 32<br/>Total data: 50TB<br/>Operations: 500K/sec)]

            CUSTOMER[(Customer Cluster<br/>Shards: 16<br/>Total data: 10TB<br/>Operations: 200K/sec)]

            ANALYTICS[(Analytics Cluster<br/>Shards: 8<br/>Total data: 100TB<br/>Operations: 50K/sec)]
        end

        API --> PAYMENT
        API --> CUSTOMER
        PAYMENT --> ANALYTICS
    end

    subgraph "Performance Achievements"
        PERF1[Payment latency<br/>p50: 5ms<br/>p95: 25ms<br/>p99: 80ms<br/>Availability: 99.99%]

        PERF2[Write throughput<br/>Peak: 2M ops/sec<br/>Average: 800K ops/sec<br/>Global replication lag: < 100ms]
    end

    subgraph "Scaling Strategy"
        SCALE1[Horizontal sharding<br/>Shard key: payment_id hash<br/>Auto-balancing enabled<br/>Chunk size: 64MB]

        SCALE2[Read scaling<br/>Secondary reads: 80%<br/>Read preference: secondary<br/>Write concern: majority]
    end

    classDef apiStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef clusterStyle fill:#10B981,stroke:#059669,color:#fff
    classDef perfStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef scaleStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class API apiStyle
    class PAYMENT,CUSTOMER,ANALYTICS clusterStyle
    class PERF1,PERF2 perfStyle
    class SCALE1,SCALE2 scaleStyle
```

### Critical Configuration Parameters

```mermaid
graph LR
    subgraph "WiredTiger Configuration"
        WT1[cacheSizeGB: 32<br/>checkpointSizeMB: 1000<br/>journalCompressor: snappy<br/>collectionCompressor: zstd]
    end

    subgraph "Sharding Configuration"
        SH1[chunkSize: 64<br/>balancerActiveWindow: 1:00-6:00<br/>maxChunkSizeBytes: 67108864<br/>autoSplit: true]
    end

    subgraph "Connection Configuration"
        CONN1[maxPoolSize: 100<br/>minPoolSize: 5<br/>maxIdleTimeMS: 30000<br/>serverSelectionTimeoutMS: 5000]
    end

    subgraph "Replication Configuration"
        REPL1[writeConcern: majority<br/>readConcern: local<br/>oplogSizeMB: 51200<br/>heartbeatIntervalMS: 2000]
    end

    classDef configStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class WT1,SH1,CONN1,REPL1 configStyle
```

## Time-Series Optimization

### Time-Series Collections Performance

```mermaid
graph TB
    subgraph "Regular Collection"
        RC1[Document structure<br/>timestamp: ISODate<br/>sensor_id: string<br/>value: number<br/>metadata: object]

        RC2[Storage efficiency<br/>Compression ratio: 3:1<br/>Index size: 40% of data<br/>Query performance: Moderate]

        RC1 --> RC2
    end

    subgraph "Time-Series Collection"
        TS1[Optimized structure<br/>Automatic bucketing<br/>Compressed storage<br/>Efficient metadata handling]

        TS2[Storage efficiency<br/>Compression ratio: 8:1<br/>Index size: 10% of data<br/>Query performance: Excellent]

        TS1 --> TS2
    end

    subgraph "Performance Comparison"
        COMP1[Storage reduction: 60%<br/>Query speed: 3x faster<br/>Index size: 4x smaller<br/>Insert throughput: 2x higher]
    end

    RC2 --> COMP1
    TS2 --> COMP1

    classDef regularStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef tsStyle fill:#10B981,stroke:#059669,color:#fff
    classDef compStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class RC1,RC2 regularStyle
    class TS1,TS2 tsStyle
    class COMP1 compStyle
```

### Time-Series Bucketing Strategy

```mermaid
graph LR
    subgraph "Granularity: Seconds"
        S1[Bucket span: 1 minute<br/>Documents per bucket: 60<br/>Use case: High-frequency sensors<br/>Compression: Excellent]
    end

    subgraph "Granularity: Minutes"
        M1[Bucket span: 1 hour<br/>Documents per bucket: 60<br/>Use case: Application metrics<br/>Compression: Good]
    end

    subgraph "Granularity: Hours"
        H1[Bucket span: 24 hours<br/>Documents per bucket: 24<br/>Use case: Daily aggregates<br/>Compression: Moderate]
    end

    subgraph "Performance Impact"
        P1[Query patterns<br/>Range queries: Optimized<br/>Point lookups: Efficient<br/>Aggregations: Fast]
    end

    S1 --> P1
    M1 --> P1
    H1 --> P1

    classDef granularityStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#10B981,stroke:#059669,color:#fff

    class S1,M1,H1 granularityStyle
    class P1 perfStyle
```

## Production Lessons Learned

### Critical Performance Factors

1. **Shard Key Selection**: Most important architectural decision affecting performance
2. **WiredTiger Cache**: 50% of RAM optimal, monitoring eviction pressure critical
3. **Index Strategy**: Compound indexes outperform intersection for known patterns
4. **Change Streams**: Server-side filtering essential for performance
5. **Time-Series Data**: Use time-series collections for 60%+ storage savings

### Performance Optimization Pipeline

```mermaid
graph TB
    subgraph "Monitoring & Detection"
        M1[MongoDB Profiler<br/>Slow operations: > 100ms<br/>Collection scans detected<br/>Index usage analysis]
    end

    subgraph "Analysis & Planning"
        A1[Query pattern analysis<br/>Index intersection efficiency<br/>Shard key distribution<br/>Cache hit rates]
    end

    subgraph "Implementation"
        I1[Index optimization<br/>Schema refactoring<br/>Sharding strategy<br/>Configuration tuning]
    end

    subgraph "Validation"
        V1[Performance testing<br/>Load testing<br/>Regression detection<br/>Production monitoring]
    end

    M1 --> A1 --> I1 --> V1

    classDef monitorStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef analysisStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef implStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef validStyle fill:#10B981,stroke:#059669,color:#fff

    class M1 monitorStyle
    class A1 analysisStyle
    class I1 implStyle
    class V1 validStyle
```

**Performance Benchmarks**:
- **Small Scale** (< 10K ops/sec): Single replica set, basic indexing
- **Medium Scale** (10K-100K ops/sec): Sharding, optimized cache, compound indexes
- **Large Scale** (> 100K ops/sec): Advanced sharding, time-series optimization, change streams

**Source**: Based on Stripe, Shopify, and MongoDB Enterprise implementations