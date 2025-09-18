# Kafka Performance Profile

## Overview

Apache Kafka performance characteristics in production environments, covering partition optimization, producer batching, consumer lag patterns, and compression strategies. Based on LinkedIn's implementation handling 7 trillion messages per day and other high-scale deployments.

## Partition Count Optimization

### Partition Distribution Impact

```mermaid
graph TB
    subgraph "3 Partition Topic"
        P3_1[Partition 0<br/>Messages: 33%<br/>Consumer: A<br/>Throughput: 50K msg/sec]

        P3_2[Partition 1<br/>Messages: 33%<br/>Consumer: B<br/>Throughput: 50K msg/sec]

        P3_3[Partition 2<br/>Messages: 34%<br/>Consumer: C<br/>Throughput: 50K msg/sec]

        P3_TOTAL[Total throughput: 150K msg/sec<br/>Parallelism: 3<br/>Load balancing: Good]

        P3_1 --> P3_TOTAL
        P3_2 --> P3_TOTAL
        P3_3 --> P3_TOTAL
    end

    subgraph "12 Partition Topic"
        P12_RANGE[Partitions 0-11<br/>Messages: ~8.3% each<br/>Consumers: 12<br/>Throughput: 600K msg/sec]

        P12_BENEFITS[Benefits<br/>• Higher parallelism<br/>• Better load distribution<br/>• Faster recovery<br/>• More consumer instances]

        P12_COSTS[Costs<br/>• More file handles<br/>• Higher memory usage<br/>• Complex rebalancing<br/>• Leader election overhead]

        P12_RANGE --> P12_BENEFITS
        P12_RANGE --> P12_COSTS
    end

    classDef partitionStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef benefitStyle fill:#10B981,stroke:#059669,color:#fff
    classDef costStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef totalStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class P3_1,P3_2,P3_3,P12_RANGE partitionStyle
    class P3_TOTAL totalStyle
    class P12_BENEFITS benefitStyle
    class P12_COSTS costStyle
```

### Partition Count vs Performance

```mermaid
graph LR
    subgraph "Under-partitioned (3 partitions)"
        UP1[Topic throughput: 150K msg/sec<br/>Producer latency p95: 5ms<br/>Consumer lag: Minimal<br/>Rebalance time: 5 seconds]

        UP2[Limitations<br/>• Max 3 consumers<br/>• Limited parallelism<br/>• Single broker hotspot<br/>• Poor scalability]
    end

    subgraph "Optimal partitioned (30 partitions)"
        OP1[Topic throughput: 1M msg/sec<br/>Producer latency p95: 2ms<br/>Consumer lag: Minimal<br/>Rebalance time: 30 seconds]

        OP2[Benefits<br/>• 30 consumer parallelism<br/>• Even broker distribution<br/>• Good performance<br/>• Manageable complexity]
    end

    subgraph "Over-partitioned (300 partitions)"
        OVP1[Topic throughput: 1.2M msg/sec<br/>Producer latency p95: 8ms<br/>Consumer lag: Variable<br/>Rebalance time: 5 minutes]

        OVP2[Problems<br/>• Rebalancing overhead<br/>• Memory pressure<br/>• File handle exhaustion<br/>• Operational complexity]
    end

    UP1 --> UP2
    OP1 --> OP2
    OVP1 --> OVP2

    classDef underStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef optimalStyle fill:#10B981,stroke:#059669,color:#fff
    classDef overStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class UP1,UP2 underStyle
    class OP1,OP2 optimalStyle
    class OVP1,OVP2 overStyle
```

### Partitioning Strategy Selection

```mermaid
graph TB
    subgraph "Round-Robin Partitioning"
        RR1[Message distribution<br/>Even across partitions<br/>Key: null<br/>Ordering: None]

        RR2[Performance<br/>Throughput: Maximum<br/>Load balance: Perfect<br/>Use case: High throughput logs]

        RR1 --> RR2
    end

    subgraph "Key-Based Partitioning"
        KB1[Message distribution<br/>Hash(key) % partitions<br/>Key: user_id, device_id<br/>Ordering: Per key]

        KB2[Performance<br/>Throughput: Good<br/>Load balance: Variable<br/>Use case: User events, transactions]

        KB1 --> KB2
    end

    subgraph "Custom Partitioning"
        CP1[Message distribution<br/>Business logic based<br/>Key: geographic region<br/>Ordering: Custom]

        CP2[Performance<br/>Throughput: Variable<br/>Load balance: Controlled<br/>Use case: Geographic sharding]

        CP1 --> CP2
    end

    classDef roundRobinStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef keyBasedStyle fill:#10B981,stroke:#059669,color:#fff
    classDef customStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class RR1,RR2 roundRobinStyle
    class KB1,KB2 keyBasedStyle
    class CP1,CP2 customStyle
```

## Producer Batching Impact

### Batch Size vs Latency Trade-off

```mermaid
graph TB
    subgraph "Small Batches (1KB)"
        SB1[Batch size: 1KB<br/>Messages per batch: 1-2<br/>Network calls: High<br/>CPU overhead: High]

        SB2[Performance impact<br/>Latency p95: 2ms<br/>Throughput: 50K msg/sec<br/>Network utilization: 30%]

        SB1 --> SB2
    end

    subgraph "Medium Batches (16KB)"
        MB1[Batch size: 16KB<br/>Messages per batch: 10-20<br/>Network calls: Medium<br/>CPU overhead: Medium]

        MB2[Performance impact<br/>Latency p95: 5ms<br/>Throughput: 200K msg/sec<br/>Network utilization: 60%]

        MB1 --> MB2
    end

    subgraph "Large Batches (1MB)"
        LB1[Batch size: 1MB<br/>Messages per batch: 500-1000<br/>Network calls: Low<br/>CPU overhead: Low]

        LB2[Performance impact<br/>Latency p95: 50ms<br/>Throughput: 1M msg/sec<br/>Network utilization: 95%]

        LB1 --> LB2
    end

    subgraph "Optimization Strategy"
        OPT[Dynamic batching<br/>batch.size: 100KB<br/>linger.ms: 10<br/>Adaptive to load patterns]

        MB2 --> OPT
        LB2 --> OPT
    end

    classDef smallStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef mediumStyle fill:#10B981,stroke:#059669,color:#fff
    classDef largeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef optStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class SB1,SB2 smallStyle
    class MB1,MB2 mediumStyle
    class LB1,LB2 largeStyle
    class OPT optStyle
```

### Producer Configuration Impact

```mermaid
graph LR
    subgraph "Low Latency Configuration"
        LL1[batch.size: 1024<br/>linger.ms: 0<br/>acks: 1<br/>compression.type: none]

        LL2[Results<br/>Latency p95: 1ms<br/>Throughput: 50K msg/sec<br/>CPU usage: High<br/>Network overhead: High]

        LL1 --> LL2
    end

    subgraph "High Throughput Configuration"
        HT1[batch.size: 1048576<br/>linger.ms: 100<br/>acks: 1<br/>compression.type: lz4]

        HT2[Results<br/>Latency p95: 100ms<br/>Throughput: 1M msg/sec<br/>CPU usage: Low<br/>Network overhead: Low]

        HT1 --> HT2
    end

    subgraph "Balanced Configuration"
        BAL1[batch.size: 65536<br/>linger.ms: 10<br/>acks: all<br/>compression.type: snappy]

        BAL2[Results<br/>Latency p95: 15ms<br/>Throughput: 500K msg/sec<br/>CPU usage: Medium<br/>Durability: High]

        BAL1 --> BAL2
    end

    classDef lowLatencyStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef highThroughputStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef balancedStyle fill:#10B981,stroke:#059669,color:#fff

    class LL1,LL2 lowLatencyStyle
    class HT1,HT2 highThroughputStyle
    class BAL1,BAL2 balancedStyle
```

## Consumer Lag Patterns

### Consumer Group Lag Analysis

```mermaid
graph TB
    subgraph "Healthy Consumer Group"
        H1[Consumer A<br/>Partition 0<br/>Current offset: 1000000<br/>High water mark: 1000005<br/>Lag: 5 messages]

        H2[Consumer B<br/>Partition 1<br/>Current offset: 999995<br/>High water mark: 1000000<br/>Lag: 5 messages]

        H3[Consumer C<br/>Partition 2<br/>Current offset: 1000010<br/>High water mark: 1000010<br/>Lag: 0 messages]

        H_TOTAL[Total lag: 10 messages<br/>Processing rate: 10K msg/sec<br/>Recovery time: <1 second<br/>Status: Healthy]

        H1 --> H_TOTAL
        H2 --> H_TOTAL
        H3 --> H_TOTAL
    end

    subgraph "Lagging Consumer Group"
        L1[Consumer A<br/>Partition 0<br/>Current offset: 900000<br/>High water mark: 1000000<br/>Lag: 100K messages]

        L2[Consumer B<br/>Partition 1<br/>Current offset: 950000<br/>High water mark: 1000000<br/>Lag: 50K messages]

        L3[Consumer C<br/>Partition 2<br/>Current offset: 980000<br/>High water mark: 1000000<br/>Lag: 20K messages]

        L_TOTAL[Total lag: 170K messages<br/>Processing rate: 5K msg/sec<br/>Recovery time: 34 seconds<br/>Status: Lagging]

        L1 --> L_TOTAL
        L2 --> L_TOTAL
        L3 --> L_TOTAL
    end

    classDef healthyStyle fill:#10B981,stroke:#059669,color:#fff
    classDef laggingStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef totalStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class H1,H2,H3 healthyStyle
    class L1,L2,L3 laggingStyle
    class H_TOTAL,L_TOTAL totalStyle
```

### Lag Recovery Strategies

```mermaid
graph TB
    subgraph "Scaling Strategy"
        SCALE1[Current: 3 consumers<br/>Lag: 170K messages<br/>Processing rate: 5K msg/sec<br/>Recovery time: 34 seconds]

        SCALE2[Add consumers<br/>New count: 6 consumers<br/>Processing rate: 10K msg/sec<br/>Recovery time: 17 seconds]

        SCALE3[Max consumers = partitions<br/>Consumer count: 12 consumers<br/>Processing rate: 20K msg/sec<br/>Recovery time: 8.5 seconds]

        SCALE1 --> SCALE2 --> SCALE3
    end

    subgraph "Configuration Tuning"
        TUNE1[fetch.min.bytes: 1048576<br/>fetch.max.wait.ms: 100<br/>max.poll.records: 1000<br/>Batch processing optimization]

        TUNE2[session.timeout.ms: 30000<br/>heartbeat.interval.ms: 3000<br/>max.poll.interval.ms: 300000<br/>Rebalance optimization]

        TUNE1 --> TUNE2
    end

    subgraph "Application Optimization"
        APP1[Batch processing<br/>Async processing<br/>Connection pooling<br/>Error handling improvement]

        APP2[Results<br/>Processing rate: +200%<br/>Lag recovery: 3x faster<br/>Resource efficiency: +50%]

        APP1 --> APP2
    end

    classDef scaleStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef tuneStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef appStyle fill:#10B981,stroke:#059669,color:#fff

    class SCALE1,SCALE2,SCALE3 scaleStyle
    class TUNE1,TUNE2 tuneStyle
    class APP1,APP2 appStyle
```

## Compression Algorithm Comparison

### Compression Performance Analysis

```mermaid
graph TB
    subgraph "No Compression"
        NONE1[Message size: 1KB<br/>Compression ratio: 1:1<br/>CPU usage: 0%<br/>Network bandwidth: 100%]

        NONE2[Performance<br/>Throughput: 1M msg/sec<br/>Latency p95: 2ms<br/>Broker CPU: 20%<br/>Network: 1 Gbps]

        NONE1 --> NONE2
    end

    subgraph "Snappy Compression"
        SNAPPY1[Message size: 400 bytes<br/>Compression ratio: 2.5:1<br/>CPU usage: 10%<br/>Network bandwidth: 40%]

        SNAPPY2[Performance<br/>Throughput: 800K msg/sec<br/>Latency p95: 3ms<br/>Broker CPU: 35%<br/>Network: 400 Mbps]

        SNAPPY1 --> SNAPPY2
    end

    subgraph "LZ4 Compression"
        LZ4_1[Message size: 350 bytes<br/>Compression ratio: 2.9:1<br/>CPU usage: 8%<br/>Network bandwidth: 35%]

        LZ4_2[Performance<br/>Throughput: 850K msg/sec<br/>Latency p95: 2.5ms<br/>Broker CPU: 30%<br/>Network: 350 Mbps]

        LZ4_1 --> LZ4_2
    end

    subgraph "GZIP Compression"
        GZIP1[Message size: 250 bytes<br/>Compression ratio: 4:1<br/>CPU usage: 25%<br/>Network bandwidth: 25%]

        GZIP2[Performance<br/>Throughput: 400K msg/sec<br/>Latency p95: 8ms<br/>Broker CPU: 60%<br/>Network: 250 Mbps]

        GZIP1 --> GZIP2
    end

    classDef noneStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef snappyStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef lz4Style fill:#10B981,stroke:#059669,color:#fff
    classDef gzipStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class NONE1,NONE2 noneStyle
    class SNAPPY1,SNAPPY2 snappyStyle
    class LZ4_1,LZ4_2 lz4Style
    class GZIP1,GZIP2 gzipStyle
```

### Compression Use Case Matrix

```mermaid
graph LR
    subgraph "High Throughput / Low Latency"
        HT_LL[Requirements<br/>• < 5ms latency<br/>• > 500K msg/sec<br/>• CPU resources available]

        HT_LL_REC[Recommendation: LZ4<br/>Best balance of compression<br/>and performance<br/>Low CPU overhead]

        HT_LL --> HT_LL_REC
    end

    subgraph "Network Constrained"
        NET_CONST[Requirements<br/>• Limited bandwidth<br/>• Cost optimization<br/>• Acceptable latency increase]

        NET_CONST_REC[Recommendation: GZIP<br/>Maximum compression<br/>Lowest network usage<br/>Higher CPU cost acceptable]

        NET_CONST --> NET_CONST_REC
    end

    subgraph "CPU Constrained"
        CPU_CONST[Requirements<br/>• Limited CPU resources<br/>• Simple deployment<br/>• Maximum throughput]

        CPU_CONST_REC[Recommendation: None<br/>No compression overhead<br/>Maximum producer throughput<br/>Higher network usage]

        CPU_CONST --> CPU_CONST_REC
    end

    subgraph "Balanced Workload"
        BALANCED[Requirements<br/>• Good compression<br/>• Reasonable performance<br/>• Wide compatibility]

        BALANCED_REC[Recommendation: Snappy<br/>Good compression ratio<br/>Widely supported<br/>Moderate CPU usage]

        BALANCED --> BALANCED_REC
    end

    classDef requirementStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef recommendationStyle fill:#10B981,stroke:#059669,color:#fff

    class HT_LL,NET_CONST,CPU_CONST,BALANCED requirementStyle
    class HT_LL_REC,NET_CONST_REC,CPU_CONST_REC,BALANCED_REC recommendationStyle
```

## LinkedIn's 7 Trillion Messages/Day

### LinkedIn's Kafka Infrastructure

```mermaid
graph TB
    subgraph "LinkedIn Kafka Deployment"
        subgraph "Multiple Data Centers"
            DC1[Data Center 1<br/>Clusters: 15<br/>Brokers: 500<br/>Topics: 10,000<br/>Daily volume: 2T messages]

            DC2[Data Center 2<br/>Clusters: 12<br/>Brokers: 400<br/>Topics: 8,000<br/>Daily volume: 1.5T messages]

            DC3[Data Center 3<br/>Clusters: 20<br/>Brokers: 600<br/>Topics: 12,000<br/>Daily volume: 3.5T messages]
        end

        subgraph "Cross-DC Replication"
            MIRROR[MirrorMaker 2.0<br/>Replication lag: < 100ms<br/>Bandwidth: 10 Gbps<br/>Compression: LZ4]

            DC1 <--> MIRROR
            DC2 <--> MIRROR
            DC3 <--> MIRROR
        end
    end

    subgraph "Performance Achievements"
        PERF1[Peak throughput: 20M msg/sec<br/>Average throughput: 80K msg/sec<br/>p99 latency: 10ms<br/>Availability: 99.99%]

        PERF2[Storage efficiency<br/>Total data: 2 PB/day<br/>Retention: 7 days<br/>Compression ratio: 3:1<br/>Cost per TB: $10/month]
    end

    classDef dcStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef mirrorStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef perfStyle fill:#10B981,stroke:#059669,color:#fff

    class DC1,DC2,DC3 dcStyle
    class MIRROR mirrorStyle
    class PERF1,PERF2 perfStyle
```

### Critical Configuration at Scale

```mermaid
graph TB
    subgraph "Broker Configuration"
        BROKER1[num.network.threads: 32<br/>num.io.threads: 64<br/>socket.send.buffer.bytes: 102400<br/>socket.receive.buffer.bytes: 102400]

        BROKER2[num.replica.fetchers: 4<br/>replica.fetch.max.bytes: 1048576<br/>log.segment.bytes: 1073741824<br/>log.retention.hours: 168]

        BROKER3[compression.type: lz4<br/>min.insync.replicas: 2<br/>unclean.leader.election.enable: false<br/>auto.create.topics.enable: false]

        BROKER1 --> BROKER2 --> BROKER3
    end

    subgraph "JVM Configuration"
        JVM1[Heap size: 6GB<br/>GC: G1 with low-latency tuning<br/>Max GC pause: 20ms<br/>Off-heap page cache: 10GB]

        JVM2[GC tuning parameters<br/>-XX:+UseG1GC<br/>-XX:MaxGCPauseMillis=20<br/>-XX:G1HeapRegionSize=16m]

        JVM1 --> JVM2
    end

    subgraph "Operating System"
        OS1[File system: XFS<br/>Mount options: noatime,nodiratime<br/>Dirty ratio: 5%<br/>Swappiness: 1]

        OS2[Network tuning<br/>TCP window scaling: enabled<br/>TCP timestamp: enabled<br/>SO_REUSEPORT: enabled]

        OS1 --> OS2
    end

    subgraph "Hardware Specification"
        HW1[CPU: 24 cores Intel Xeon<br/>Memory: 64GB RAM<br/>Storage: 12 × 2TB NVMe SSD<br/>Network: 25 Gbps]

        HW2[Performance per broker<br/>Peak throughput: 40K msg/sec<br/>Sustained: 25K msg/sec<br/>Storage capacity: 20TB<br/>Network utilization: 80%]

        HW1 --> HW2
    end

    classDef brokerStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef jvmStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef osStyle fill:#10B981,stroke:#059669,color:#fff
    classDef hwStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class BROKER1,BROKER2,BROKER3 brokerStyle
    class JVM1,JVM2 jvmStyle
    class OS1,OS2 osStyle
    class HW1,HW2 hwStyle
```

### Scaling Evolution Timeline

```mermaid
graph LR
    subgraph "Growth Phases"
        PHASE1[2012: 100M messages/day<br/>Brokers: 50<br/>Use cases: Activity tracking<br/>Infrastructure: Basic setup]

        PHASE2[2015: 1T messages/day<br/>Brokers: 200<br/>Use cases: Real-time analytics<br/>Infrastructure: Multi-DC]

        PHASE3[2018: 5T messages/day<br/>Brokers: 800<br/>Use cases: Stream processing<br/>Infrastructure: Optimized]

        PHASE4[2024: 7T messages/day<br/>Brokers: 1500<br/>Use cases: ML pipelines<br/>Infrastructure: Cloud hybrid]

        PHASE1 --> PHASE2 --> PHASE3 --> PHASE4
    end

    subgraph "Key Optimizations"
        OPT1[2012-2015<br/>• Partition optimization<br/>• Compression adoption<br/>• Consumer group tuning]

        OPT2[2015-2018<br/>• Cross-DC replication<br/>• Hardware upgrades<br/>• JVM tuning]

        OPT3[2018-2024<br/>• NVMe storage<br/>• Network optimization<br/>• Application-level batching]
    end

    classDef phaseStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef optStyle fill:#10B981,stroke:#059669,color:#fff

    class PHASE1,PHASE2,PHASE3,PHASE4 phaseStyle
    class OPT1,OPT2,OPT3 optStyle
```

## Production Lessons Learned

### Performance Optimization Hierarchy

```mermaid
graph TB
    subgraph "Level 1: Configuration"
        L1[Producer batching<br/>Consumer fetch sizing<br/>Compression selection<br/>JVM tuning]
    end

    subgraph "Level 2: Architecture"
        L2[Partition count optimization<br/>Topic design patterns<br/>Consumer group sizing<br/>Replication factor tuning]
    end

    subgraph "Level 3: Infrastructure"
        L3[Hardware selection<br/>Network optimization<br/>Storage configuration<br/>Operating system tuning]
    end

    subgraph "Level 4: Application"
        L4[Message schema design<br/>Batch processing patterns<br/>Error handling strategies<br/>Monitoring integration]
    end

    L1 --> L2 --> L3 --> L4

    classDef levelStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class L1,L2,L3,L4 levelStyle
```

### Critical Performance Factors

1. **Partition Strategy**: Right-size partitions for parallelism without overhead
2. **Producer Batching**: Balance latency and throughput through batch configuration
3. **Compression**: LZ4 provides best balance for most workloads
4. **Consumer Scaling**: Scale consumers up to partition count for maximum throughput
5. **Hardware Selection**: NVMe storage and high-bandwidth networking essential at scale

### Performance Benchmarks by Scale

| Scale | Throughput | Partitions | Brokers | Configuration Focus |
|-------|------------|------------|---------|-------------------|
| **Small** | <100K msg/sec | 3-10 | 3 | Basic batching, simple compression |
| **Medium** | 100K-1M msg/sec | 30-100 | 3-10 | Optimized batching, consumer tuning |
| **Large** | >1M msg/sec | 100+ | 10+ | Hardware optimization, JVM tuning |

### Common Pitfalls

1. **Over-partitioning**: Too many partitions cause rebalancing issues
2. **Under-batching**: Small batches reduce throughput significantly
3. **Consumer lag**: Not monitoring and addressing lag accumulation
4. **Poor key distribution**: Hotspot partitions limit scaling
5. **Inadequate compression**: Missing network bandwidth optimization opportunities

**Source**: Based on LinkedIn, Uber, and Netflix Kafka implementations