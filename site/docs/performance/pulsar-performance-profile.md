# Pulsar Performance Profile

## Overview

Apache Pulsar performance characteristics in production environments, covering tiered storage, geo-replication, function processing, and segment-based architecture benefits. Based on Yahoo's multi-tenant implementation and other high-scale deployments.

## Tiered Storage Performance

### Hot vs Cold Storage Architecture

```mermaid
graph TB
    subgraph Pulsar_Tiered_Storage[Pulsar Tiered Storage]
        subgraph BookKeeper__Hot_Storage[BookKeeper (Hot Storage)]
            BK1[Bookie 1<br/>NVMe SSD: 2TB<br/>IOPS: 100K<br/>Latency: 0.1ms]
            BK2[Bookie 2<br/>NVMe SSD: 2TB<br/>IOPS: 100K<br/>Latency: 0.1ms]
            BK3[Bookie 3<br/>NVMe SSD: 2TB<br/>IOPS: 100K<br/>Latency: 0.1ms]
        end

        subgraph Cold_Storage__S3_GCS[Cold Storage (S3/GCS)]
            COLD[Object Storage<br/>Capacity: Unlimited<br/>Cost: $0.023/GB/month<br/>Access latency: 100ms]
        end

        subgraph Broker_Management[Broker Management]
            BROKER[Pulsar Broker<br/>Offload threshold: 1GB<br/>Offload age: 4 hours<br/>Prefetch buffer: 100MB]
        end

        BK1 --> BROKER
        BK2 --> BROKER
        BK3 --> BROKER
        BROKER --> COLD
    end

    subgraph Performance_Characteristics[Performance Characteristics]
        PC1[Hot storage access<br/>Throughput: 1M msg/sec<br/>Latency p95: 2ms<br/>Cost: $100/TB/month]

        PC2[Cold storage access<br/>Throughput: 10K msg/sec<br/>Latency p95: 150ms<br/>Cost: $0.023/GB/month]

        PC3[Automatic tiering<br/>Recent data: Hot storage<br/>Historical data: Cold storage<br/>Transparent to clients]
    end

    classDef hotStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef coldStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef brokerStyle fill:#10B981,stroke:#059669,color:#fff
    classDef perfStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class BK1,BK2,BK3 hotStyle
    class COLD coldStyle
    class BROKER brokerStyle
    class PC1,PC2,PC3 perfStyle
```

### Tiered Storage Configuration Impact

```mermaid
graph LR
    subgraph Aggressive_Offloading[Aggressive Offloading]
        AGG1[Configuration<br/>managedLedgerOffloadThresholdInBytes: 100MB<br/>managedLedgerOffloadDeletionLagInMillis: 1h<br/>Strategy: Cost optimization]

        AGG2[Performance impact<br/>Hot storage usage: 10%<br/>Cold access frequency: High<br/>Average latency: 50ms<br/>Cost savings: 80%]

        AGG1 --> AGG2
    end

    subgraph Conservative_Offloading[Conservative Offloading]
        CONS1[Configuration<br/>managedLedgerOffloadThresholdInBytes: 10GB<br/>managedLedgerOffloadDeletionLagInMillis: 24h<br/>Strategy: Performance optimization]

        CONS2[Performance impact<br/>Hot storage usage: 90%<br/>Cold access frequency: Low<br/>Average latency: 5ms<br/>Cost savings: 20%]

        CONS1 --> CONS2
    end

    subgraph Balanced_Approach[Balanced Approach]
        BAL1[Configuration<br/>managedLedgerOffloadThresholdInBytes: 1GB<br/>managedLedgerOffloadDeletionLagInMillis: 6h<br/>Strategy: Balanced performance/cost]

        BAL2[Performance impact<br/>Hot storage usage: 50%<br/>Cold access frequency: Medium<br/>Average latency: 15ms<br/>Cost savings: 60%]

        BAL1 --> BAL2
    end

    classDef aggStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef consStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef balStyle fill:#10B981,stroke:#059669,color:#fff

    class AGG1,AGG2 aggStyle
    class CONS1,CONS2 consStyle
    class BAL1,BAL2 balStyle
```

## Geo-Replication Overhead

### Cross-Region Replication Architecture

```mermaid
graph TB
    subgraph Multi_Region_Pulsar_Deployment[Multi-Region Pulsar Deployment]
        subgraph US_East_Region[US-East Region]
            USE1[Pulsar Cluster US-East<br/>Brokers: 6<br/>BookKeepers: 9<br/>ZooKeepers: 3]
        end

        subgraph US_West_Region[US-West Region]
            USW1[Pulsar Cluster US-West<br/>Brokers: 4<br/>BookKeepers: 6<br/>ZooKeepers: 3]
        end

        subgraph EU_West_Region[EU-West Region]
            EUW1[Pulsar Cluster EU-West<br/>Brokers: 4<br/>BookKeepers: 6<br/>ZooKeepers: 3]
        end

        subgraph Replication_Configuration[Replication Configuration]
            REPL[Global ZooKeeper<br/>Configuration store<br/>Cluster coordination<br/>Metadata sync]
        end

        USE1 <--> REPL
        USW1 <--> REPL
        EUW1 <--> REPL

        USE1 <-.->|80ms RTT| USW1
        USW1 <-.->|150ms RTT| EUW1
        EUW1 <-.->|120ms RTT| USE1
    end

    subgraph Replication_Performance[Replication Performance]
        RP1[Asynchronous replication<br/>Replication lag: 100-500ms<br/>Network utilization: 20%<br/>Impact on local writes: Minimal]

        RP2[Message ordering<br/>Per-producer ordering: Maintained<br/>Cross-region ordering: Best effort<br/>Conflict resolution: Timestamp-based]
    end

    classDef regionStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef replStyle fill:#10B981,stroke:#059669,color:#fff
    classDef perfStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class USE1,USW1,EUW1 regionStyle
    class REPL replStyle
    class RP1,RP2 perfStyle
```

### Geo-Replication vs Local Performance

```mermaid
graph LR
    subgraph Local_Only[Local Only]
        LOCAL1[Single region deployment<br/>Write latency p95: 2ms<br/>Read latency p95: 1ms<br/>Throughput: 1M msg/sec<br/>Availability: 99.9%]
    end

    subgraph Geo_Replicated[Geo-Replicated]
        GEO1[Multi-region deployment<br/>Local write latency p95: 3ms<br/>Global read latency p95: 150ms<br/>Throughput: 800K msg/sec<br/>Availability: 99.99%]
    end

    subgraph Overhead_Analysis[Overhead Analysis]
        OVERHEAD1[Performance impact<br/>• 50% latency increase locally<br/>• 150x latency for cross-region reads<br/>• 20% throughput reduction<br/>• 10x availability improvement]

        OVERHEAD2[Resource overhead<br/>• 50% additional storage<br/>• 20% additional network<br/>• 30% additional CPU for replication<br/>• 3x operational complexity]
    end

    LOCAL1 --> OVERHEAD1
    GEO1 --> OVERHEAD1
    OVERHEAD1 --> OVERHEAD2

    classDef localStyle fill:#10B981,stroke:#059669,color:#fff
    classDef geoStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef overheadStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class LOCAL1 localStyle
    class GEO1 geoStyle
    class OVERHEAD1,OVERHEAD2 overheadStyle
```

## Function Processing Latency

### Pulsar Functions Performance

```mermaid
graph TB
    subgraph Function_Execution_Models[Function Execution Models]
        subgraph Thread_Based_Functions[Thread-Based Functions]
            THREAD1[Thread model<br/>Isolation: Thread-level<br/>Startup time: <10ms<br/>Memory overhead: 50MB<br/>Parallelism: Thread pool]

            THREAD2[Performance<br/>Throughput: 100K msg/sec<br/>Latency p95: 5ms<br/>CPU efficiency: High<br/>Resource sharing: Yes]

            THREAD1 --> THREAD2
        end

        subgraph Process_Based_Functions[Process-Based Functions]
            PROCESS1[Process model<br/>Isolation: Process-level<br/>Startup time: 100ms<br/>Memory overhead: 200MB<br/>Parallelism: Multi-process]

            PROCESS2[Performance<br/>Throughput: 50K msg/sec<br/>Latency p95: 15ms<br/>CPU efficiency: Medium<br/>Resource sharing: No]

            PROCESS1 --> PROCESS2
        end

        subgraph Kubernetes_Functions[Kubernetes Functions]
            K8S1[Kubernetes model<br/>Isolation: Container-level<br/>Startup time: 2 seconds<br/>Memory overhead: 500MB<br/>Parallelism: Pod-based]

            K8S2[Performance<br/>Throughput: 10K msg/sec<br/>Latency p95: 100ms<br/>CPU efficiency: Low<br/>Resource sharing: Isolated]

            K8S1 --> K8S2
        end
    end

    subgraph Function_Types_Performance[Function Types Performance]
        SIMPLE[Simple transformations<br/>CPU usage: 10%<br/>Latency: 1ms<br/>Example: JSON field extraction]

        COMPLEX[Complex processing<br/>CPU usage: 80%<br/>Latency: 50ms<br/>Example: ML inference]

        IO_BOUND[I/O bound functions<br/>CPU usage: 20%<br/>Latency: 200ms<br/>Example: Database lookup]

        SIMPLE --> COMPLEX --> IO_BOUND
    end

    classDef threadStyle fill:#10B981,stroke:#059669,color:#fff
    classDef processStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef k8sStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef funcStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class THREAD1,THREAD2 threadStyle
    class PROCESS1,PROCESS2 processStyle
    class K8S1,K8S2 k8sStyle
    class SIMPLE,COMPLEX,IO_BOUND funcStyle
```

### Function Scaling Performance

```mermaid
graph TB
    subgraph Auto_scaling_Configuration[Auto-scaling Configuration]
        AS1[Scale trigger<br/>CPU utilization > 70%<br/>Queue backlog > 1000<br/>Processing latency > 100ms<br/>Scale-up time: 30 seconds]

        AS2[Scale-down criteria<br/>CPU utilization < 30%<br/>Queue backlog < 100<br/>Processing latency < 10ms<br/>Scale-down time: 300 seconds]

        AS1 --> AS2
    end

    subgraph Scaling_Performance[Scaling Performance]
        SP1[1 instance performance<br/>Throughput: 1K msg/sec<br/>Latency p95: 10ms<br/>CPU usage: 50%<br/>Memory usage: 100MB]

        SP2[5 instances performance<br/>Throughput: 5K msg/sec<br/>Latency p95: 10ms<br/>CPU usage: 50% each<br/>Memory usage: 500MB total]

        SP3[10 instances performance<br/>Throughput: 8K msg/sec<br/>Latency p95: 15ms<br/>CPU usage: 40% each<br/>Coordination overhead: 20%]

        SP1 --> SP2 --> SP3
    end

    subgraph Scaling_Limitations[Scaling Limitations]
        SL1[Resource contention<br/>Shared resources become bottleneck<br/>Diminishing returns after 10 instances<br/>Coordination overhead increases]

        SL2[State management<br/>Stateless functions: Linear scaling<br/>Stateful functions: Limited scaling<br/>External dependencies: Bottlenecks]

        SL1 --> SL2
    end

    classDef scaleConfigStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#10B981,stroke:#059669,color:#fff
    classDef limitStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class AS1,AS2 scaleConfigStyle
    class SP1,SP2,SP3 perfStyle
    class SL1,SL2 limitStyle
```

## Segment-Based Architecture Benefits

### Segment vs Partition Comparison

```mermaid
graph LR
    subgraph Traditional_Partition_Model__Kafka[Traditional Partition Model (Kafka)]
        KAFKA1[Partition structure<br/>Single log file<br/>Sequential writes<br/>Segment rotation<br/>Hot partition concept]

        KAFKA2[Performance characteristics<br/>Write throughput: High<br/>Tail reads: Slow<br/>Rebalancing: Expensive<br/>Storage: Monolithic]

        KAFKA1 --> KAFKA2
    end

    subgraph Pulsar_Segment_Model[Pulsar Segment Model]
        PULSAR1[Segment structure<br/>Multiple bookies<br/>Parallel writes<br/>Individual segments<br/>No hot bookie]

        PULSAR2[Performance characteristics<br/>Write throughput: Higher<br/>Tail reads: Fast<br/>Rebalancing: Instant<br/>Storage: Distributed]

        PULSAR1 --> PULSAR2
    end

    subgraph Architectural_Benefits[Architectural Benefits]
        BENEFITS1[Pulsar advantages<br/>• No broker data storage<br/>• Instant topic creation<br/>• Unlimited topic scaling<br/>• Independent scaling layers]

        BENEFITS2[Operational benefits<br/>• Faster broker recovery<br/>• No data rebalancing<br/>• Simpler capacity planning<br/>• Better resource utilization]

        KAFKA2 --> BENEFITS1
        PULSAR2 --> BENEFITS1
        BENEFITS1 --> BENEFITS2
    end

    classDef kafkaStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef pulsarStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef benefitStyle fill:#10B981,stroke:#059669,color:#fff

    class KAFKA1,KAFKA2 kafkaStyle
    class PULSAR1,PULSAR2 pulsarStyle
    class BENEFITS1,BENEFITS2 benefitStyle
```

### BookKeeper Performance Characteristics

```mermaid
graph TB
    subgraph BookKeeper_Write_Path[BookKeeper Write Path]
        WRITE1[Write request<br/>Client: Pulsar broker<br/>Ensemble: 3 bookies<br/>Write quorum: 2<br/>Ack quorum: 2]

        WRITE2[Parallel writes<br/>Bookie 1: Write + sync<br/>Bookie 2: Write + sync<br/>Bookie 3: Write (async)<br/>Response time: p95 < 5ms]

        WRITE3[Durability guarantee<br/>WAL: Immediate write<br/>Index: Async update<br/>Fsync: Configurable<br/>Data safety: Guaranteed]

        WRITE1 --> WRITE2 --> WRITE3
    end

    subgraph BookKeeper_Read_Path[BookKeeper Read Path]
        READ1[Read request<br/>LAC: Last Add Confirmed<br/>Available bookies: Check<br/>Parallel reads: Enabled]

        READ2[Read optimization<br/>Local reads: Preferred<br/>Read-ahead: Enabled<br/>Caching: Memory + disk<br/>Response time: p95 < 2ms]

        READ1 --> READ2
    end

    subgraph Performance_Tuning[Performance Tuning]
        TUNE1[Journal configuration<br/>journalSyncData: true<br/>journalBufferedWritesThreshold: 512KB<br/>journalFlushWhenQueueEmpty: false]

        TUNE2[Storage optimization<br/>sortedLedgerStorageEnabled: true<br/>skipReplicasCheck: false<br/>openFileLimit: 20000<br/>readBufferSizeBytes: 4096]

        TUNE1 --> TUNE2
    end

    classDef writeStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef readStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef tuneStyle fill:#10B981,stroke:#059669,color:#fff

    class WRITE1,WRITE2,WRITE3 writeStyle
    class READ1,READ2 readStyle
    class TUNE1,TUNE2 tuneStyle
```

## Yahoo's Multi-Tenant Usage

### Yahoo's Pulsar Deployment Scale

```mermaid
graph TB
    subgraph Yahoo_Production_Deployment[Yahoo Production Deployment]
        SCALE1[Deployment metrics<br/>Messages/day: 100 billion<br/>Topics: 1 million+<br/>Tenants: 1000+<br/>Clusters: 50+]

        SCALE2[Infrastructure<br/>Brokers: 500+<br/>BookKeepers: 1500+<br/>Total storage: 10 PB<br/>Peak throughput: 50M msg/sec]

        SCALE1 --> SCALE2
    end

    subgraph Multi_tenancy_Performance[Multi-tenancy Performance]
        MT1[Tenant isolation<br/>Resource quotas enforced<br/>Network bandwidth limits<br/>Storage quotas per tenant<br/>CPU isolation per namespace]

        MT2[Performance isolation<br/>Noisy neighbor protection<br/>Independent scaling per tenant<br/>Fair resource allocation<br/>SLA enforcement per tenant]

        MT1 --> MT2
    end

    subgraph Operational_Achievements[Operational Achievements]
        OA1[Availability: 99.99%<br/>Mean recovery time: 30 seconds<br/>Zero-downtime upgrades<br/>Automatic failover < 10 seconds]

        OA2[Cost efficiency<br/>Hardware utilization: 85%<br/>Storage efficiency: 90%<br/>Operational overhead: 50% vs single-tenant]

        OA1 --> OA2
    end

    classDef scaleStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef tenantStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef operationalStyle fill:#10B981,stroke:#059669,color:#fff

    class SCALE1,SCALE2 scaleStyle
    class MT1,MT2 tenantStyle
    class OA1,OA2 operationalStyle
```

### Multi-tenant Resource Management

```mermaid
graph LR
    subgraph Tenant_Resource_Allocation[Tenant Resource Allocation]
        TENANT1[Tenant A<br/>Quota: 10K msg/sec<br/>Storage: 1TB<br/>Topics: 100<br/>Priority: High]

        TENANT2[Tenant B<br/>Quota: 5K msg/sec<br/>Storage: 500GB<br/>Topics: 50<br/>Priority: Medium]

        TENANT3[Tenant C<br/>Quota: 20K msg/sec<br/>Storage: 2TB<br/>Topics: 200<br/>Priority: Low]
    end

    subgraph Resource_Enforcement[Resource Enforcement]
        ENFORCE1[Rate limiting<br/>Message rate per producer<br/>Bandwidth throttling<br/>Backpressure to clients<br/>Fair queuing algorithms]

        ENFORCE2[Storage management<br/>Per-tenant quotas<br/>Retention policy enforcement<br/>Auto-cleanup old data<br/>Tiered storage policies]

        TENANT1 --> ENFORCE1
        TENANT2 --> ENFORCE1
        TENANT3 --> ENFORCE1
        ENFORCE1 --> ENFORCE2
    end

    subgraph Performance_Isolation[Performance Isolation]
        ISOLATION1[CPU isolation<br/>CFS quota groups<br/>Namespace-based limits<br/>Function resource limits<br/>JVM heap isolation]

        ISOLATION2[Network isolation<br/>Virtual networks<br/>Bandwidth allocation<br/>Traffic shaping<br/>QoS policies]

        ENFORCE2 --> ISOLATION1
        ISOLATION1 --> ISOLATION2
    end

    classDef tenantStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef enforceStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef isolationStyle fill:#10B981,stroke:#059669,color:#fff

    class TENANT1,TENANT2,TENANT3 tenantStyle
    class ENFORCE1,ENFORCE2 enforceStyle
    class ISOLATION1,ISOLATION2 isolationStyle
```

## Production Lessons Learned

### Critical Performance Factors

1. **Tiered Storage Strategy**: Balance performance and cost with appropriate offload thresholds
2. **Geo-replication Configuration**: Asynchronous replication minimizes local performance impact
3. **Function Execution Model**: Thread-based functions provide best performance/isolation balance
4. **BookKeeper Tuning**: Journal and storage configuration critical for write performance
5. **Multi-tenant Resource Management**: Proper quotas and isolation prevent noisy neighbor issues

### Performance Optimization Pipeline

```mermaid
graph TB
    subgraph Monitoring
        MON1[Broker metrics<br/>Message rates<br/>Latency percentiles<br/>Resource utilization]

        MON2[BookKeeper metrics<br/>Write latency<br/>Read latency<br/>Storage utilization]

        MON1 --> MON2
    end

    subgraph Analysis
        ANALYSIS1[Bottleneck identification<br/>Hot topics/partitions<br/>Resource constraints<br/>Configuration issues]

        ANALYSIS2[Workload characterization<br/>Message patterns<br/>Access patterns<br/>Growth trends]

        MON2 --> ANALYSIS1 --> ANALYSIS2
    end

    subgraph Optimization
        OPT1[Configuration tuning<br/>Broker settings<br/>BookKeeper parameters<br/>Client configuration]

        OPT2[Architecture changes<br/>Scaling decisions<br/>Topology adjustments<br/>Function optimization]

        ANALYSIS2 --> OPT1 --> OPT2
    end

    classDef monStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef analysisStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef optStyle fill:#10B981,stroke:#059669,color:#fff

    class MON1,MON2 monStyle
    class ANALYSIS1,ANALYSIS2 analysisStyle
    class OPT1,OPT2 optStyle
```

### Performance Benchmarks by Scale

| Scale | Throughput | Latency p95 | Storage Tier | Use Case |
|-------|------------|-------------|--------------|----------|
| **Small** | <10K msg/sec | 5ms | Hot only | Development, testing |
| **Medium** | 10K-100K msg/sec | 10ms | Hot + warm | Production workloads |
| **Large** | >100K msg/sec | 20ms | Hot + cold tiered | Enterprise, multi-tenant |

### Common Pitfalls

1. **Aggressive tiered storage**: Too quick offloading hurts read performance
2. **Over-replication**: Unnecessary geo-replication increases complexity and cost
3. **Wrong function execution model**: Process/container models for simple functions
4. **Inadequate BookKeeper tuning**: Default settings insufficient for production loads
5. **Poor tenant isolation**: Resource contention in multi-tenant environments

**Source**: Based on Yahoo, Splunk, and Datastax Pulsar implementations