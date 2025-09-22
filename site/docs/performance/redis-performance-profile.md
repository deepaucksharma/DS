# Redis Performance Profile

## Overview

Redis performance characteristics in production environments, covering clustering vs sentinel architectures, persistence strategies, Lua scripting, and memory optimization. Based on Twitter's Timeline caching implementation and other high-scale deployments.

## Cluster vs Sentinel Performance

### Redis Cluster Architecture

```mermaid
graph TB
    subgraph Redis_Cluster___6_Node_Setup[Redis Cluster - 6 Node Setup"
        subgraph Master Nodes"
            M1[Master 1<br/>Slots: 0-5460<br/>Memory: 16GB<br/>Connections: 10K"
            M2[Master 2<br/>Slots: 5461-10922<br/>Memory: 16GB<br/>Connections: 10K"
            M3[Master 3<br/>Slots: 10923-16383<br/>Memory: 16GB<br/>Connections: 10K"
        end

        subgraph Replica Nodes"
            R1[Replica 1<br/>Master: M1<br/>Replication lag: 1ms<br/>Read operations: 50K/sec"
            R2[Replica 2<br/>Master: M2<br/>Replication lag: 2ms<br/>Read operations: 45K/sec"
            R3[Replica 3<br/>Master: M3<br/>Replication lag: 1ms<br/>Read operations: 55K/sec"
        end

        M1 --> R1
        M2 --> R2
        M3 --> R3

        M1 <--> M2
        M2 <--> M3
        M3 <--> M1
    end

    subgraph Performance Characteristics"
        P1[Total operations: 300K/sec<br/>Write latency p95: 1ms<br/>Read latency p95: 0.5ms<br/>Failover time: 15 seconds"

        P2[Scaling benefits<br/>Linear read scaling<br/>Automatic sharding<br/>No single point of failure"
    end

    classDef masterStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef replicaStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#10B981,stroke:#059669,color:#fff

    class M1,M2,M3 masterStyle
    class R1,R2,R3 replicaStyle
    class P1,P2 perfStyle
```

### Redis Sentinel Architecture

```mermaid
graph TB
    subgraph Redis Sentinel Setup"
        subgraph Sentinel Nodes"
            S1[Sentinel 1<br/>Monitor: redis-master<br/>Quorum: 2<br/>Status: Active"
            S2[Sentinel 2<br/>Monitor: redis-master<br/>Quorum: 2<br/>Status: Active"
            S3[Sentinel 3<br/>Monitor: redis-master<br/>Quorum: 2<br/>Status: Active"
        end

        subgraph Redis Instances"
            MASTER[Redis Master<br/>Memory: 48GB<br/>Operations: 100K/sec<br/>Role: Read+Write"

            SLAVE1[Redis Replica 1<br/>Memory: 48GB<br/>Operations: 50K/sec<br/>Role: Read-only"

            SLAVE2[Redis Replica 2<br/>Memory: 48GB<br/>Operations: 50K/sec<br/>Role: Read-only"
        end

        S1 --> MASTER
        S2 --> MASTER
        S3 --> MASTER

        MASTER --> SLAVE1
        MASTER --> SLAVE2
    end

    subgraph Failover Performance"
        F1[Detection time: 30 seconds<br/>Election time: 5 seconds<br/>Reconfiguration: 10 seconds<br/>Total failover: 45 seconds"

        F2[Split-brain prevention<br/>Quorum enforcement<br/>Automatic promotion<br/>Client reconnection"
    end

    classDef sentinelStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef masterStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef replicaStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef failoverStyle fill:#10B981,stroke:#059669,color:#fff

    class S1,S2,S3 sentinelStyle
    class MASTER masterStyle
    class SLAVE1,SLAVE2 replicaStyle
    class F1,F2 failoverStyle
```

### Cluster vs Sentinel Comparison

```mermaid
graph LR
    subgraph Redis Cluster"
        RC1[Automatic sharding<br/>16,384 hash slots<br/>No single point of failure<br/>Client-side routing"

        RC2[Performance<br/>Linear scaling<br/>Max nodes: 1000<br/>Failover: 15 seconds<br/>Complexity: High"
    end

    subgraph Redis Sentinel"
        RS1[Master-replica setup<br/>Automatic failover<br/>Single master writes<br/>Server-side routing"

        RS2[Performance<br/>Vertical scaling<br/>Max nodes: 3-5<br/>Failover: 45 seconds<br/>Complexity: Low"
    end

    subgraph Use Case Recommendations"
        UC1[Cluster best for:<br/>• Large datasets (>100GB)<br/>• High write throughput<br/>• Geographic distribution"

        UC2[Sentinel best for:<br/>• Smaller datasets (<100GB)<br/>• Read-heavy workloads<br/>• Simple operations"
    end

    RC1 --> UC1
    RS1 --> UC2
    RC2 --> UC1
    RS2 --> UC2

    classDef clusterStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef sentinelStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef usecaseStyle fill:#10B981,stroke:#059669,color:#fff

    class RC1,RC2 clusterStyle
    class RS1,RS2 sentinelStyle
    class UC1,UC2 usecaseStyle
```

## Persistence Impact: RDB vs AOF

### Redis Database (RDB) Snapshots

```mermaid
graph TB
    subgraph RDB Snapshot Process"
        RDB1[Trigger conditions<br/>save 900 1<br/>save 300 10<br/>save 60 10000"

        RDB2[Fork process<br/>Copy-on-write<br/>Background save<br/>Memory doubling risk"

        RDB3[Disk I/O impact<br/>Duration: 5-30 seconds<br/>Size: 4GB snapshot<br/>I/O bandwidth: 200MB/s"

        RDB1 --> RDB2 --> RDB3
    end

    subgraph RDB Performance Impact"
        RDBP1[Memory usage spike<br/>Peak: 200% of dataset<br/>Duration: Save process<br/>OOM risk: High"

        RDBP2[Latency impact<br/>p95 increase: 50ms<br/>Duration: Fork process<br/>Recovery: Immediate"

        RDBP3[Data loss window<br/>Maximum: Save interval<br/>Typical: 5-15 minutes<br/>Acceptable for: Caches"
    end

    classDef processStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef impactStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class RDB1,RDB2,RDB3 processStyle
    class RDBP1,RDBP2,RDBP3 impactStyle
```

### Append Only File (AOF)

```mermaid
graph TB
    subgraph AOF Write Process"
        AOF1[Write commands<br/>Buffer in memory<br/>appendfsync policy<br/>Disk write timing"

        AOF2[Sync policies<br/>always: Every command<br/>everysec: Every second<br/>no: OS controlled"

        AOF3[Rewrite process<br/>Triggered by size<br/>Background operation<br/>Compact log file"

        AOF1 --> AOF2 --> AOF3
    end

    subgraph AOF Performance Characteristics"
        AOFP1[appendfsync=always<br/>Latency p95: 5ms<br/>Throughput: 10K ops/sec<br/>Durability: Maximum"

        AOFP2[appendfsync=everysec<br/>Latency p95: 0.5ms<br/>Throughput: 100K ops/sec<br/>Data loss: <1 second"

        AOFP3[appendfsync=no<br/>Latency p95: 0.2ms<br/>Throughput: 200K ops/sec<br/>Data loss: 30+ seconds"

        AOF2 --> AOFP1
        AOF2 --> AOFP2
        AOF2 --> AOFP3
    end

    classDef processStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef alwaysStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef everysecStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef noStyle fill:#10B981,stroke:#059669,color:#fff

    class AOF1,AOF2,AOF3 processStyle
    class AOFP1 alwaysStyle
    class AOFP2 everysecStyle
    class AOFP3 noStyle
```

### Persistence Strategy Comparison

```mermaid
graph LR
    subgraph RDB Only"
        RDB_ONLY1[Disk usage: Minimal<br/>Recovery time: Fast<br/>Data loss risk: High<br/>Performance impact: Periodic"
    end

    subgraph AOF Only"
        AOF_ONLY1[Disk usage: High<br/>Recovery time: Slow<br/>Data loss risk: Low<br/>Performance impact: Constant"
    end

    subgraph RDB + AOF"
        BOTH1[Disk usage: High<br/>Recovery time: Fast (RDB first)<br/>Data loss risk: Minimal<br/>Performance impact: Both"
    end

    subgraph No Persistence"
        NONE1[Disk usage: None<br/>Recovery time: N/A<br/>Data loss risk: Total<br/>Performance impact: None"
    end

    classDef rdbStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef aofStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef bothStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef noneStyle fill:#10B981,stroke:#059669,color:#fff

    class RDB_ONLY1 rdbStyle
    class AOF_ONLY1 aofStyle
    class BOTH1 bothStyle
    class NONE1 noneStyle
```

## Lua Scripting Overhead

### Lua Script Performance Characteristics

```mermaid
graph TB
    subgraph Lua Script Execution"
        LUA1[Script loading<br/>SCRIPT LOAD command<br/>SHA1 hash generation<br/>Server-side caching"

        LUA2[Script execution<br/>EVALSHA command<br/>Atomic operation<br/>Single-threaded processing"

        LUA3[Performance impact<br/>Compilation: 0.1ms<br/>Execution: Variable<br/>Blocking: Complete"

        LUA1 --> LUA2 --> LUA3
    end

    subgraph Script Complexity Analysis"
        SIMPLE[Simple scripts<br/>1-10 operations<br/>Execution: <1ms<br/>Overhead: Minimal"

        COMPLEX[Complex scripts<br/>100+ operations<br/>Execution: 5-50ms<br/>Overhead: Significant"

        LOOPS[Loop-heavy scripts<br/>1000+ iterations<br/>Execution: 100ms+<br/>Overhead: Blocking"

        SIMPLE --> COMPLEX --> LOOPS
    end

    subgraph Best Practices"
        BP1[Keep scripts short<br/>Avoid loops<br/>Use pipelining alternative<br/>Monitor execution time"

        BP2[Script optimization<br/>Minimize key access<br/>Batch operations<br/>Consider alternative approaches"
    end

    classDef scriptStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef complexityStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef practicesStyle fill:#10B981,stroke:#059669,color:#fff

    class LUA1,LUA2,LUA3 scriptStyle
    class SIMPLE,COMPLEX,LOOPS complexityStyle
    class BP1,BP2 practicesStyle
```

### Lua vs Alternative Approaches

```mermaid
graph LR
    subgraph Lua Script Approach"
        LUA_APP1[Single network round-trip<br/>Atomic operations<br/>Server-side logic<br/>Complex operations possible"

        LUA_APP2[Performance<br/>Latency: 1-5ms<br/>Throughput: Dependent on complexity<br/>Blocking: All operations"
    end

    subgraph Pipeline Approach"
        PIPE_APP1[Multiple commands batched<br/>No server-side logic<br/>Client-side complexity<br/>Non-atomic by default"

        PIPE_APP2[Performance<br/>Latency: 0.5ms per command<br/>Throughput: Higher<br/>Blocking: Per command"
    end

    subgraph Transaction Approach"
        TRANS_APP1[MULTI/EXEC blocks<br/>Queued commands<br/>Atomic execution<br/>Limited logic"

        TRANS_APP2[Performance<br/>Latency: Sum of commands<br/>Throughput: Good<br/>Blocking: Transaction only"
    end

    classDef luaStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef pipelineStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef transStyle fill:#10B981,stroke:#059669,color:#fff

    class LUA_APP1,LUA_APP2 luaStyle
    class PIPE_APP1,PIPE_APP2 pipelineStyle
    class TRANS_APP1,TRANS_APP2 transStyle
```

## Memory Optimization Techniques

### Memory Usage Patterns

```mermaid
graph TB
    subgraph Redis Memory Breakdown"
        MEM1[Dataset: 80%<br/>Application data<br/>Keys and values<br/>Primary memory usage"

        MEM2[Overhead: 15%<br/>Key expiration<br/>Data structure metadata<br/>Redis internals"

        MEM3[Fragmentation: 5%<br/>Memory allocator overhead<br/>Deleted key gaps<br/>Operating system pages"

        MEM_TOTAL[Total Memory: 32GB<br/>Dataset: 25.6GB<br/>Overhead: 4.8GB<br/>Fragmentation: 1.6GB"

        MEM1 --> MEM_TOTAL
        MEM2 --> MEM_TOTAL
        MEM3 --> MEM_TOTAL
    end

    subgraph Memory Optimization"
        OPT1[Key naming optimization<br/>Short key names<br/>Consistent prefixes<br/>Hash tags for clustering"

        OPT2[Data structure optimization<br/>Hash vs String choice<br/>List vs Set selection<br/>Compressed data structures"

        OPT3[Expiration optimization<br/>TTL policies<br/>LRU eviction<br/>Memory monitoring"
    end

    classDef memoryStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef optimStyle fill:#10B981,stroke:#059669,color:#fff

    class MEM1,MEM2,MEM3,MEM_TOTAL memoryStyle
    class OPT1,OPT2,OPT3 optimStyle
```

### Data Structure Performance Comparison

```mermaid
graph TB
    subgraph String vs Hash Comparison"
        STR1[String approach<br/>user:1001:name = John Doe<br/>user:1001:email = john@example.com<br/>user:1001:age = 30"

        STR2[Memory usage<br/>Keys: 48 bytes each<br/>Values: Variable<br/>Total overhead: High"

        HASH1[Hash approach<br/>HSET user:1001 name John Doe<br/>HSET user:1001 email john@example.com<br/>HSET user:1001 age 30"

        HASH2[Memory usage<br/>Hash overhead: 48 bytes<br/>Field overhead: 8 bytes each<br/>Total overhead: Lower"

        STR1 --> STR2
        HASH1 --> HASH2
    end

    subgraph Performance Impact"
        PERF1[String operations<br/>GET latency: 0.1ms<br/>MGET 100 keys: 0.5ms<br/>Memory per field: 64 bytes"

        PERF2[Hash operations<br/>HGET latency: 0.1ms<br/>HMGET 100 fields: 0.3ms<br/>Memory per field: 24 bytes"
    end

    STR2 --> PERF1
    HASH2 --> PERF2

    classDef stringStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef hashStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#10B981,stroke:#059669,color:#fff

    class STR1,STR2 stringStyle
    class HASH1,HASH2 hashStyle
    class PERF1,PERF2 perfStyle
```

### Memory Eviction Policies

```mermaid
graph LR
    subgraph LRU Policies"
        LRU1[allkeys-lru<br/>Evict least recently used<br/>All keys considered<br/>Best for general cache"

        LRU2[volatile-lru<br/>Evict LRU with TTL<br/>Only keys with expiration<br/>Mix of cache and persistent data"
    end

    subgraph LFU Policies"
        LFU1[allkeys-lfu<br/>Evict least frequently used<br/>All keys considered<br/>Better for access patterns"

        LFU2[volatile-lfu<br/>Evict LFU with TTL<br/>Only keys with expiration<br/>Frequency-based with TTL"
    end

    subgraph Other Policies"
        OTHER1[volatile-ttl<br/>Evict shortest TTL first<br/>TTL-based eviction<br/>Predictable expiration"

        OTHER2[allkeys-random<br/>Random eviction<br/>No pattern consideration<br/>Lowest CPU overhead"
    end

    classDef lruStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef lfuStyle fill:#10B981,stroke:#059669,color:#fff
    classDef otherStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class LRU1,LRU2 lruStyle
    class LFU1,LFU2 lfuStyle
    class OTHER1,OTHER2 otherStyle
```

## Twitter's Timeline Caching Metrics

### Twitter Timeline Architecture

```mermaid
graph TB
    subgraph Twitter Timeline System"
        USER[User Request<br/>Timeline fetch<br/>User ID: 12345<br/>Timeline type: Home"

        subgraph Redis Cluster"
            REDIS1[Redis Node 1<br/>Slots: 0-5460<br/>Timeline cache<br/>Memory: 64GB"

            REDIS2[Redis Node 2<br/>Slots: 5461-10922<br/>Timeline cache<br/>Memory: 64GB"

            REDIS3[Redis Node 3<br/>Slots: 10923-16383<br/>Timeline cache<br/>Memory: 64GB"
        end

        FALLBACK[Fallback System<br/>Timeline generation<br/>Database queries<br/>Real-time computation"

        USER --> REDIS1
        USER --> REDIS2
        USER --> REDIS3
        REDIS1 -.-> FALLBACK
        REDIS2 -.-> FALLBACK
        REDIS3 -.-> FALLBACK
    end

    subgraph Performance Metrics"
        METRICS1[Cache hit rate: 95%<br/>p95 latency: 1ms<br/>p99 latency: 3ms<br/>Throughput: 500K ops/sec"

        METRICS2[Memory efficiency<br/>Storage per timeline: 2KB<br/>Compression ratio: 3:1<br/>Total cached timelines: 100M"
    end

    classDef userStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef redisStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef fallbackStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef metricsStyle fill:#10B981,stroke:#059669,color:#fff

    class USER userStyle
    class REDIS1,REDIS2,REDIS3 redisStyle
    class FALLBACK fallbackStyle
    class METRICS1,METRICS2 metricsStyle
```

### Timeline Cache Strategy

```mermaid
graph TB
    subgraph Cache Key Structure"
        KEY1[timeline:home:user_id<br/>timeline:mentions:user_id<br/>timeline:search:query_hash<br/>Consistent hashing distribution"

        KEY2[Value structure<br/>List of tweet IDs<br/>Compressed format<br/>TTL: 30 minutes"

        KEY1 --> KEY2
    end

    subgraph Cache Population"
        POP1[Push strategy<br/>Fan-out on write<br/>Pre-compute timelines<br/>High write amplification"

        POP2[Pull strategy<br/>Compute on read<br/>Cache after computation<br/>High read latency"

        POP3[Hybrid strategy<br/>Push for active users<br/>Pull for inactive users<br/>Optimized for both"

        POP1 --> POP3
        POP2 --> POP3
    end

    subgraph Performance Results"
        RESULTS1[Push strategy<br/>Read latency: 1ms<br/>Write amplification: 1000x<br/>Storage: High"

        RESULTS2[Pull strategy<br/>Read latency: 50ms<br/>Write amplification: 1x<br/>Storage: Low"

        RESULTS3[Hybrid strategy<br/>Read latency: 5ms<br/>Write amplification: 100x<br/>Storage: Medium"

        POP1 --> RESULTS1
        POP2 --> RESULTS2
        POP3 --> RESULTS3
    end

    classDef keyStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef strategyStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef resultStyle fill:#10B981,stroke:#059669,color:#fff

    class KEY1,KEY2 keyStyle
    class POP1,POP2,POP3 strategyStyle
    class RESULTS1,RESULTS2,RESULTS3 resultStyle
```

### Critical Configuration for Scale

```mermaid
graph LR
    subgraph Memory Configuration"
        MEM_CONF1[maxmemory: 60GB<br/>maxmemory-policy: allkeys-lru<br/>Hash-max-ziplist-entries: 512<br/>Hash-max-ziplist-value: 64"
    end

    subgraph Network Configuration"
        NET_CONF1[tcp-keepalive: 300<br/>timeout: 0<br/>tcp-backlog: 511<br/>maxclients: 50000"
    end

    subgraph Performance Configuration"
        PERF_CONF1[save: disabled<br/>appendonly: no<br/>cluster-enabled: yes<br/>cluster-config-file: nodes.conf"
    end

    subgraph Monitoring Configuration"
        MON_CONF1[latency-monitor-threshold: 100<br/>slowlog-log-slower-than: 10000<br/>slowlog-max-len: 128<br/>client-output-buffer-limit: 256mb"
    end

    classDef configStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class MEM_CONF1,NET_CONF1,PERF_CONF1,MON_CONF1 configStyle
```

## Production Lessons Learned

### Critical Performance Factors

1. **Architecture Choice**: Cluster for scale, Sentinel for simplicity
2. **Persistence Strategy**: No persistence for pure cache, AOF everysec for durability
3. **Memory Management**: LRU eviction essential, monitor fragmentation
4. **Key Design**: Short keys, consistent naming, appropriate data structures
5. **Monitoring**: Track slow queries, memory usage, and hit rates

### Performance Optimization Pipeline

```mermaid
graph TB
    subgraph Monitoring & Detection"
        MON1[Redis INFO command<br/>Memory usage tracking<br/>Slow query log<br/>Latency monitoring"
    end

    subgraph Analysis & Tuning"
        TUNE1[Key analysis<br/>Data structure optimization<br/>Memory allocation tuning<br/>Connection pool sizing"
    end

    subgraph Implementation
        IMPL1[Configuration changes<br/>Application optimizations<br/>Infrastructure scaling<br/>Monitoring setup"
    end

    subgraph Validation
        VAL1[Performance testing<br/>Load testing<br/>Production monitoring<br/>Alert configuration"
    end

    MON1 --> TUNE1 --> IMPL1 --> VAL1

    classDef monitorStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef tuneStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef implStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef valStyle fill:#10B981,stroke:#059669,color:#fff

    class MON1 monitorStyle
    class TUNE1 tuneStyle
    class IMPL1 implStyle
    class VAL1 valStyle
```

### Scaling Patterns

| Scale | Architecture | Memory | Persistence | Key Patterns |
|-------|-------------|--------|-------------|--------------|
| **Small** (<1GB) | Single instance | <8GB | RDB snapshots | Simple strings |
| **Medium** (1-50GB) | Sentinel setup | 8-64GB | AOF everysec | Hash optimization |
| **Large** (>50GB) | Redis Cluster | 64GB+ | No persistence | Consistent hashing |

### Common Pitfalls

1. **Memory overcommit**: No eviction policy configured
2. **Blocking operations**: Long-running Lua scripts
3. **Network saturation**: Too many connections per instance
4. **Poor key design**: Long keys, inappropriate data structures
5. **No monitoring**: Performance degradation undetected

**Performance Benchmarks**:
- **Single Instance**: 100K ops/sec, <1ms latency
- **Sentinel Setup**: 200K ops/sec, automatic failover
- **Redis Cluster**: 1M+ ops/sec, horizontal scaling

**Source**: Based on Twitter, GitHub, and Stack Overflow Redis implementations