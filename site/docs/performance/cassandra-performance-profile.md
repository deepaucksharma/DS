# Cassandra Performance Profile

## Overview

Apache Cassandra performance characteristics in production environments, covering compaction strategies, consistency levels, token ring rebalancing, and time-series optimization. Based on Netflix's implementation achieving 1M writes/sec and other high-scale deployments.

## Compaction Strategies Comparison

### Size-Tiered Compaction Strategy (STCS)

```mermaid
graph TB
    subgraph STCS_Compaction_Process[STCS Compaction Process]
        STCS1[L0: 4 SSTables<br/>Size: 100MB each<br/>Age: Recent writes<br/>Overlap: High]

        STCS2[L1: 1 SSTable<br/>Size: 400MB<br/>Age: 1 hour<br/>Overlap: Medium]

        STCS3[L2: 1 SSTable<br/>Size: 1.6GB<br/>Age: 4 hours<br/>Overlap: Low]

        STCS4[L3: 1 SSTable<br/>Size: 6.4GB<br/>Age: 16 hours<br/>Overlap: None]

        STCS1 --> STCS2 --> STCS3 --> STCS4
    end

    subgraph STCS_Performance[STCS Performance]
        STCS_PERF1[Write amplification: 3x<br/>Read amplification: 4x<br/>Space amplification: 2x<br/>Compaction I/O: High bursts]

        STCS_PERF2[Best for: Write-heavy<br/>Worst for: Read-heavy<br/>Space efficiency: Poor<br/>Operational complexity: Low]
    end

    classDef levelStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class STCS1,STCS2,STCS3,STCS4 levelStyle
    class STCS_PERF1,STCS_PERF2 perfStyle
```

### Leveled Compaction Strategy (LCS)

```mermaid
graph TB
    subgraph LCS_Compaction_Process[LCS Compaction Process]
        LCS1[L0: 4 SSTables<br/>Size: 100MB each<br/>Overlap: Allowed<br/>Compaction trigger: 4 files]

        LCS2[L1: 10 SSTables<br/>Size: 100MB each<br/>Overlap: None<br/>Total size: 1GB]

        LCS3[L2: 100 SSTables<br/>Size: 100MB each<br/>Overlap: None<br/>Total size: 10GB]

        LCS4[L3: 1000 SSTables<br/>Size: 100MB each<br/>Overlap: None<br/>Total size: 100GB]

        LCS1 --> LCS2
        LCS2 --> LCS3
        LCS3 --> LCS4
    end

    subgraph LCS_Performance[LCS Performance]
        LCS_PERF1[Write amplification: 10x<br/>Read amplification: 1x<br/>Space amplification: 1.1x<br/>Compaction I/O: Steady]

        LCS_PERF2[Best for: Read-heavy<br/>Worst for: Write-heavy<br/>Space efficiency: Excellent<br/>Operational complexity: High]
    end

    classDef levelStyle fill:#10B981,stroke:#059669,color:#fff
    classDef perfStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class LCS1,LCS2,LCS3,LCS4 levelStyle
    class LCS_PERF1,LCS_PERF2 perfStyle
```

### Time-Window Compaction Strategy (TWCS)

```mermaid
graph TB
    subgraph TWCS_Time_Windows[TWCS Time Windows]
        TW1[Window 1: Last hour<br/>SSTables: 4<br/>Size: 400MB<br/>Compaction: Active]

        TW2[Window 2: Hour -2<br/>SSTables: 1<br/>Size: 400MB<br/>Compaction: Complete]

        TW3[Window 3: Hour -3<br/>SSTables: 1<br/>Size: 400MB<br/>Compaction: Complete]

        TW4[Window 4+: Older<br/>SSTables: 1 each<br/>Size: 400MB each<br/>Compaction: Rare]

        subgraph Time_based_Optimization[Time-based Optimization]
            TTL[TTL Expiration<br/>Whole SSTable deletion<br/>No compaction needed<br/>Instant space reclamation]
        end

        TW1 --> TW2 --> TW3 --> TW4
        TW4 --> TTL
    end

    subgraph TWCS_Performance[TWCS Performance]
        TWCS_PERF1[Write amplification: 2x<br/>Read amplification: 2x<br/>Space amplification: 1.5x<br/>TTL efficiency: Excellent]

        TWCS_PERF2[Best for: Time-series<br/>Optimal for: TTL data<br/>Space efficiency: Good<br/>Query patterns: Time-range]
    end

    classDef windowStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef ttlStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class TW1,TW2,TW3,TW4 windowStyle
    class TTL ttlStyle
    class TWCS_PERF1,TWCS_PERF2 perfStyle
```

### Compaction Strategy Performance Comparison

```mermaid
graph LR
    subgraph Write_Heavy_Workload[Write-Heavy Workload]
        WH1[STCS Performance<br/>Throughput: 100K ops/sec<br/>Latency p99: 10ms<br/>Compaction overhead: 15%]

        WH2[LCS Performance<br/>Throughput: 40K ops/sec<br/>Latency p99: 25ms<br/>Compaction overhead: 40%]

        WH3[TWCS Performance<br/>Throughput: 90K ops/sec<br/>Latency p99: 12ms<br/>Compaction overhead: 10%]
    end

    subgraph Read_Heavy_Workload[Read-Heavy Workload]
        RH1[STCS Performance<br/>Throughput: 20K ops/sec<br/>Latency p99: 50ms<br/>SSTables scanned: 4-8]

        RH2[LCS Performance<br/>Throughput: 80K ops/sec<br/>Latency p99: 5ms<br/>SSTables scanned: 1-2]

        RH3[TWCS Performance<br/>Throughput: 60K ops/sec<br/>Latency p99: 15ms<br/>SSTables scanned: 2-4]
    end

    classDef stcsStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef lcsStyle fill:#10B981,stroke:#059669,color:#fff
    classDef twcsStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class WH1,RH1 stcsStyle
    class WH2,RH2 lcsStyle
    class WH3,RH3 twcsStyle
```

## Consistency Level Trade-offs

### Consistency Level Performance Impact

```mermaid
graph TB
    subgraph Write_Operations[Write Operations]
        W1[Consistency Level: ONE<br/>Replicas required: 1<br/>Latency p99: 2ms<br/>Durability: Weak]

        W2[Consistency Level: QUORUM<br/>Replicas required: 2 of 3<br/>Latency p99: 8ms<br/>Durability: Strong]

        W3[Consistency Level: ALL<br/>Replicas required: 3<br/>Latency p99: 25ms<br/>Durability: Strongest]

        W4[Consistency Level: LOCAL_QUORUM<br/>Replicas required: 2 of 3 local<br/>Latency p99: 5ms<br/>Durability: Datacenter-strong]
    end

    subgraph Read_Operations[Read Operations]
        R1[Consistency Level: ONE<br/>Replicas consulted: 1<br/>Latency p99: 1ms<br/>Consistency: Eventual]

        R2[Consistency Level: QUORUM<br/>Replicas consulted: 2<br/>Latency p99: 6ms<br/>Consistency: Strong]

        R3[Consistency Level: ALL<br/>Replicas consulted: 3<br/>Latency p99: 20ms<br/>Consistency: Strongest]
    end

    subgraph Availability_Impact[Availability Impact]
        A1[Node failures tolerated<br/>CL=ONE: 2 nodes can fail<br/>CL=QUORUM: 1 node can fail<br/>CL=ALL: 0 nodes can fail]
    end

    classDef oneStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef quorumStyle fill:#10B981,stroke:#059669,color:#fff
    classDef allStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef availStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class W1,R1 oneStyle
    class W2,R2,W4 quorumStyle
    class W3,R3 allStyle
    class A1 availStyle
```

### Read Repair and Anti-Entropy

```mermaid
graph TB
    subgraph Read_Repair_Process[Read Repair Process]
        RR1[Client read request<br/>CL = QUORUM<br/>2 replicas consulted<br/>Timestamp comparison]

        RR2[Replica A response<br/>Value: user_email = old@example.com<br/>Timestamp: 1000]

        RR3[Replica B response<br/>Value: user_email = new@example.com<br/>Timestamp: 2000]

        RR4[Read repair triggered<br/>Background write to A<br/>Consistency restored<br/>Client gets new value]

        RR1 --> RR2
        RR1 --> RR3
        RR2 --> RR4
        RR3 --> RR4
    end

    subgraph Anti_Entropy__Repair[Anti-Entropy (Repair)]
        AE1[Scheduled repair<br/>Frequency: Weekly<br/>Resource intensive<br/>Cluster-wide operation]

        AE2[Incremental repair<br/>Only changed data<br/>Reduced I/O impact<br/>Faster completion]

        AE3[Performance impact<br/>CPU usage: +30%<br/>Network usage: +50%<br/>Duration: 4-8 hours]

        AE1 --> AE2 --> AE3
    end

    classDef readRepairStyle fill:#10B981,stroke:#059669,color:#fff
    classDef antiEntropyStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfImpactStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class RR1,RR2,RR3,RR4 readRepairStyle
    class AE1,AE2 antiEntropyStyle
    class AE3 perfImpactStyle
```

## Token Ring Rebalancing Cost

### Token Ring Architecture

```mermaid
graph TB
    subgraph Cassandra_Ring___6_Nodes[Cassandra Ring - 6 Nodes]
        N1[Node 1<br/>Token range: 0 - 166<br/>Virtual nodes: 256<br/>Data: 500GB]

        N2[Node 2<br/>Token range: 167 - 333<br/>Virtual nodes: 256<br/>Data: 480GB]

        N3[Node 3<br/>Token range: 334 - 500<br/>Virtual nodes: 256<br/>Data: 520GB]

        N4[Node 4<br/>Token range: 501 - 667<br/>Virtual nodes: 256<br/>Data: 510GB]

        N5[Node 5<br/>Token range: 668 - 833<br/>Virtual nodes: 256<br/>Data: 490GB]

        N6[Node 6<br/>Token range: 834 - 999<br/>Virtual nodes: 256<br/>Data: 495GB]

        N1 --> N2 --> N3 --> N4 --> N5 --> N6 --> N1
    end

    subgraph Replication_Strategy[Replication Strategy]
        RF[Replication Factor: 3<br/>Strategy: NetworkTopologyStrategy<br/>DC1: 3 replicas<br/>Consistency: QUORUM]

        RF --> N1
        RF --> N2
        RF --> N3
    end

    classDef nodeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef replicationStyle fill:#10B981,stroke:#059669,color:#fff

    class N1,N2,N3,N4,N5,N6 nodeStyle
    class RF replicationStyle
```

### Node Addition Rebalancing

```mermaid
graph LR
    subgraph Before__6_Nodes[Before: 6 Nodes]
        B1[Node 1: 500GB<br/>Token ownership: 16.67%<br/>Load distribution: Even]
        B2[Node 2: 480GB<br/>Token ownership: 16.67%<br/>Load distribution: Even]
        B3[Nodes 3-6: ~500GB each<br/>Total data: 3000GB<br/>Average per node: 500GB]
    end

    subgraph During_Rebalancing[During Rebalancing]
        D1[New Node 7 joins<br/>Token ranges reallocated<br/>Data streaming begins<br/>Performance impact starts]

        D2[Data movement<br/>~430GB streamed to Node 7<br/>Network utilization: 70%<br/>Cluster performance: -25%]

        D3[Duration: 4-6 hours<br/>Compaction triggered<br/>Disk I/O increased<br/>CPU usage elevated]
    end

    subgraph After__7_Nodes[After: 7 Nodes]
        A1[Node 1-7: ~430GB each<br/>Token ownership: 14.28%<br/>Load distribution: Rebalanced]

        A2[Performance recovery<br/>Throughput restored<br/>Latency normalized<br/>Cluster capacity increased]
    end

    B1 --> D1 --> A1
    B2 --> D2 --> A2
    B3 --> D3

    classDef beforeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef duringStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef afterStyle fill:#10B981,stroke:#059669,color:#fff

    class B1,B2,B3 beforeStyle
    class D1,D2,D3 duringStyle
    class A1,A2 afterStyle
```

### Virtual Nodes (vnodes) Performance Impact

```mermaid
graph TB
    subgraph Traditional_Token_Assignment[Traditional Token Assignment]
        T1[1 token per node<br/>Manual token assignment<br/>Uneven data distribution<br/>Hotspots common]

        T2[Rebalancing challenges<br/>Manual intervention<br/>Longer streaming times<br/>Complex operations]
    end

    subgraph Virtual_Nodes__vnodes[Virtual Nodes (vnodes)]
        V1[256 vnodes per node<br/>Automatic token assignment<br/>Even data distribution<br/>Reduced hotspots]

        V2[Rebalancing benefits<br/>Faster convergence<br/>Better load distribution<br/>Automatic optimization]
    end

    subgraph Performance_Comparison[Performance Comparison]
        P1[Traditional approach<br/>Rebalance time: 8-12 hours<br/>Manual intervention: Required<br/>Data distribution: ±20%]

        P2[vnodes approach<br/>Rebalance time: 4-6 hours<br/>Manual intervention: None<br/>Data distribution: ±5%]
    end

    T1 --> P1
    V1 --> P2
    T2 --> P1
    V2 --> P2

    classDef traditionalStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef vnodesStyle fill:#10B981,stroke:#059669,color:#fff
    classDef perfStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class T1,T2 traditionalStyle
    class V1,V2 vnodesStyle
    class P1,P2 perfStyle
```

## Time-Series Optimization

### Time-Series Data Modeling

```mermaid
graph TB
    subgraph Optimal_Time_Series_Schema[Optimal Time-Series Schema]
        TS1[Table: sensor_data<br/>Partition key: sensor_id, date<br/>Clustering key: timestamp<br/>TTL: 30 days]

        TS2[Partition sizing<br/>Size per partition: 100MB<br/>Rows per partition: 100K<br/>Time span: 1 day]

        TS3[Query patterns<br/>Range queries: Efficient<br/>Latest value: Fast<br/>Aggregations: Supported]

        TS1 --> TS2 --> TS3
    end

    subgraph Anti_patterns[Anti-patterns]
        AP1[Single partition<br/>All data in one partition<br/>Hotspot creation<br/>Poor performance]

        AP2[Wide partitions<br/>Partition size: >1GB<br/>Query timeouts<br/>Compaction issues]

        AP3[No TTL<br/>Data grows indefinitely<br/>Storage costs increase<br/>Performance degrades]
    end

    classDef optimalStyle fill:#10B981,stroke:#059669,color:#fff
    classDef antipatternStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class TS1,TS2,TS3 optimalStyle
    class AP1,AP2,AP3 antipatternStyle
```

### Time-Series Query Performance

```mermaid
graph LR
    subgraph Efficient_Queries[Efficient Queries]
        EQ1[SELECT * FROM sensor_data<br/>WHERE sensor_id = 'temp_01'<br/>AND date = '2024-01-15'<br/>AND timestamp >= '2024-01-15 10:00']

        EQ2[Query performance<br/>Partition hit: 1<br/>Rows scanned: 1000<br/>Latency p95: 5ms]

        EQ1 --> EQ2
    end

    subgraph Inefficient_Queries[Inefficient Queries]
        IQ1[SELECT * FROM sensor_data<br/>WHERE timestamp >= '2024-01-15 10:00'<br/>ALLOW FILTERING]

        IQ2[Query performance<br/>Partitions hit: ALL<br/>Rows scanned: 1M+<br/>Latency p95: 5000ms]

        IQ1 --> IQ2
    end

    subgraph Optimization_Strategies[Optimization Strategies]
        OS1[Materialized views<br/>Pre-aggregated data<br/>Different partition keys<br/>Query-specific optimization]

        OS2[Secondary indexes<br/>SASI indexes<br/>Custom index types<br/>Selective filtering]

        EQ2 --> OS1
        IQ2 --> OS2
    end

    classDef efficientStyle fill:#10B981,stroke:#059669,color:#fff
    classDef inefficientStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef optimizationStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class EQ1,EQ2 efficientStyle
    class IQ1,IQ2 inefficientStyle
    class OS1,OS2 optimizationStyle
```

## Netflix's 1M Writes/sec Achievement

### Netflix's Cassandra Architecture

```mermaid
graph TB
    subgraph Netflix_Global_Deployment[Netflix Global Deployment]
        subgraph US_East_1[US-East-1]
            USE1[Cassandra Cluster<br/>Nodes: 300<br/>Instance type: i3.2xlarge<br/>Total capacity: 600TB]
        end

        subgraph US_West_2[US-West-2]
            USW2[Cassandra Cluster<br/>Nodes: 200<br/>Instance type: i3.2xlarge<br/>Total capacity: 400TB]
        end

        subgraph EU_West_1[EU-West-1]
            EUW1[Cassandra Cluster<br/>Nodes: 150<br/>Instance type: i3.2xlarge<br/>Total capacity: 300TB]
        end

        USE1 <--> USW2
        USW2 <--> EUW1
        EUW1 <--> USE1
    end

    subgraph Workload_Characteristics[Workload Characteristics]
        WC1[Write throughput: 1M ops/sec<br/>Read throughput: 500K ops/sec<br/>Data ingestion: 10TB/day<br/>Use cases: Viewing history, recommendations]

        WC2[Consistency levels<br/>Writes: LOCAL_QUORUM<br/>Reads: LOCAL_ONE<br/>Cross-DC: Eventual consistency]
    end

    subgraph Performance_Optimizations[Performance Optimizations]
        PO1[JVM tuning: G1GC<br/>Heap size: 24GB<br/>Off-heap cache: 16GB<br/>Compaction: Custom strategy]

        PO2[Hardware optimization<br/>Local NVMe SSDs<br/>25Gbps networking<br/>Dedicated compaction nodes]
    end

    classDef clusterStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef workloadStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef optimStyle fill:#10B981,stroke:#059669,color:#fff

    class USE1,USW2,EUW1 clusterStyle
    class WC1,WC2 workloadStyle
    class PO1,PO2 optimStyle
```

### Critical Configuration for Scale

```mermaid
graph TB
    subgraph JVM_Configuration[JVM Configuration]
        JVM1[Heap size: 24GB<br/>GC: G1 with low-latency<br/>NewRatio: 1<br/>GCTimeRatio: 9]

        JVM2[Off-heap settings<br/>Row cache: 8GB<br/>Key cache: 2GB<br/>Counter cache: 1GB]
    end

    subgraph Cassandra_Configuration[Cassandra Configuration]
        CASS1[concurrent_writes: 128<br/>concurrent_reads: 128<br/>commitlog_segment_size: 64MB<br/>memtable_heap_space: 2GB]

        CASS2[compaction_throughput: 64MB/s<br/>stream_throughput_outbound: 400Mbps<br/>read_request_timeout: 10000ms<br/>write_request_timeout: 5000ms]
    end

    subgraph Hardware_Optimization[Hardware Optimization]
        HW1[Instance: i3.2xlarge<br/>vCPUs: 8<br/>Memory: 61GB<br/>NVMe SSD: 1.9TB]

        HW2[Network: 25 Gbps<br/>EBS optimized: Yes<br/>Placement group: Cluster<br/>NUMA topology: Optimized]
    end

    subgraph Performance_Results[Performance Results]
        PERF1[Write latency p95: 3ms<br/>Read latency p95: 2ms<br/>Throughput per node: 3.3K ops/sec<br/>Total cluster: 1M ops/sec]
    end

    JVM1 --> PERF1
    JVM2 --> PERF1
    CASS1 --> PERF1
    CASS2 --> PERF1
    HW1 --> PERF1
    HW2 --> PERF1

    classDef jvmStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef cassStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef hwStyle fill:#10B981,stroke:#059669,color:#fff
    classDef perfStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class JVM1,JVM2 jvmStyle
    class CASS1,CASS2 cassStyle
    class HW1,HW2 hwStyle
    class PERF1 perfStyle
```

### Scaling Timeline and Lessons

```mermaid
graph LR
    subgraph Evolution_Phases[Evolution Phases]
        P1[Phase 1: 10K ops/sec<br/>Single datacenter<br/>50 nodes<br/>Basic configuration]

        P2[Phase 2: 100K ops/sec<br/>Multi-datacenter<br/>150 nodes<br/>Tuned JVM and compaction]

        P3[Phase 3: 500K ops/sec<br/>Global deployment<br/>400 nodes<br/>Custom monitoring]

        P4[Phase 4: 1M ops/sec<br/>Optimized hardware<br/>650 nodes<br/>Advanced operations]

        P1 --> P2 --> P3 --> P4
    end

    subgraph Key_Optimizations[Key Optimizations]
        O1[10K → 100K<br/>• Multi-DC replication<br/>• JVM tuning<br/>• Compaction optimization]

        O2[100K → 500K<br/>• Hardware upgrade<br/>• Custom monitoring<br/>• Operational automation]

        O3[500K → 1M<br/>• NVMe storage<br/>• Network optimization<br/>• Application-level tuning]
    end

    classDef phaseStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef optimStyle fill:#10B981,stroke:#059669,color:#fff

    class P1,P2,P3,P4 phaseStyle
    class O1,O2,O3 optimStyle
```

## Production Lessons Learned

### Critical Performance Factors

1. **Compaction Strategy Selection**: STCS for writes, LCS for reads, TWCS for time-series
2. **Consistency Level Tuning**: LOCAL_QUORUM provides best balance of performance and consistency
3. **Token Ring Management**: vnodes essential for operational simplicity and performance
4. **JVM Tuning**: G1GC with proper heap sizing critical for low-latency operations
5. **Hardware Selection**: Local NVMe SSDs provide 10x better performance than EBS

### Performance Optimization Checklist

| Component | Small Scale | Medium Scale | Large Scale | Critical Settings |
|-----------|-------------|--------------|-------------|-------------------|
| Heap Size | 8GB | 16GB | 24-32GB | Max 50% of RAM |
| Compaction | STCS | LCS/TWCS | Custom | Workload dependent |
| Consistency | QUORUM | LOCAL_QUORUM | LOCAL_QUORUM | Balance perf/consistency |
| Concurrent Ops | 32/32 | 64/64 | 128/128 | CPU core dependent |
| Network | 1 Gbps | 10 Gbps | 25 Gbps | Inter-node communication |

### Common Pitfalls

1. **Under-tuned JVM**: Default settings inadequate for production loads
2. **Wrong compaction strategy**: STCS for read-heavy workloads causes high latency
3. **Large partitions**: >100MB partitions cause performance degradation
4. **No monitoring**: Performance issues discovered too late
5. **Insufficient hardware**: CPU and network bottlenecks limit scalability

**Source**: Based on Netflix, Apple, and Instagram Cassandra implementations