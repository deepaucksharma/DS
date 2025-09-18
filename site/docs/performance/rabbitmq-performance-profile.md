# RabbitMQ Performance Profile

## Overview

RabbitMQ performance characteristics in production environments, covering queue depth management, clustering overhead, lazy queues, and message acknowledgment patterns. Based on Deliveroo's implementation and other high-scale deployments.

## Queue Depth Impact

### Queue Depth vs Performance Relationship

```mermaid
graph TB
    subgraph Shallow_Queue____1K_messages["Shallow Queue (< 1K messages)"]
        SHALLOW1[Queue depth: 500 messages<br/>Memory usage: 50MB<br/>Enqueue rate: 10K msg/sec<br/>Dequeue rate: 10K msg/sec]

        SHALLOW2[Performance characteristics<br/>Latency p95: 2ms<br/>Memory overhead: Low<br/>Paging to disk: None<br/>Status: Optimal]

        SHALLOW1 --> SHALLOW2
    end

    subgraph Medium_Queue__1K___100K_messages[Medium Queue (1K - 100K messages)]
        MEDIUM1[Queue depth: 50K messages<br/>Memory usage: 500MB<br/>Enqueue rate: 8K msg/sec<br/>Dequeue rate: 7K msg/sec]

        MEDIUM2[Performance characteristics<br/>Latency p95: 10ms<br/>Memory overhead: Medium<br/>Paging to disk: Minimal<br/>Status: Acceptable]

        MEDIUM1 --> MEDIUM2
    end

    subgraph Deep_Queue____100K_messages["Deep Queue (> 100K messages)"]
        DEEP1[Queue depth: 1M messages<br/>Memory usage: 2GB<br/>Enqueue rate: 5K msg/sec<br/>Dequeue rate: 4K msg/sec]

        DEEP2[Performance characteristics<br/>Latency p95: 100ms<br/>Memory overhead: High<br/>Paging to disk: Aggressive<br/>Status: Degraded]

        DEEP1 --> DEEP2
    end

    subgraph Critical_Queue____1M_messages["Critical Queue (> 1M messages)"]
        CRITICAL1[Queue depth: 10M messages<br/>Memory usage: 8GB<br/>Enqueue rate: 1K msg/sec<br/>Dequeue rate: 500 msg/sec]

        CRITICAL2[Performance characteristics<br/>Latency p95: 1000ms<br/>Memory overhead: Critical<br/>Paging to disk: Constant<br/>Status: System at risk]

        CRITICAL1 --> CRITICAL2
    end

    classDef shallowStyle fill:#10B981,stroke:#059669,color:#fff
    classDef mediumStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef deepStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef criticalStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class SHALLOW1,SHALLOW2 shallowStyle
    class MEDIUM1,MEDIUM2 mediumStyle
    class DEEP1,DEEP2 deepStyle
    class CRITICAL1,CRITICAL2 criticalStyle
```

### Queue Depth Management Strategies

```mermaid
graph TB
    subgraph Producer_Flow_Control[Producer Flow Control]
        PFC1[Connection blocked<br/>Trigger: Memory alarm<br/>Action: Stop accepting messages<br/>Recovery: Memory below threshold]

        PFC2[Publisher confirms<br/>Mode: Synchronous<br/>Impact: Reduced throughput<br/>Benefit: Backpressure signal]

        PFC3[Max queue length<br/>Policy: x-max-length: 100000<br/>Overflow: Drop head/reject<br/>Protection: Memory exhaustion]

        PFC1 --> PFC2 --> PFC3
    end

    subgraph Consumer_Scaling[Consumer Scaling]
        CS1[Auto-scaling consumers<br/>Metric: Queue depth<br/>Scale up: > 10K messages<br/>Scale down: < 1K messages]

        CS2[Prefetch optimization<br/>QoS: 100 messages<br/>Balance: Memory vs throughput<br/>Tuning: Consumer capability]

        CS1 --> CS2
    end

    subgraph Queue_Design_Patterns[Queue Design Patterns]
        QDP1[Work queues<br/>Pattern: Competing consumers<br/>Depth management: Critical<br/>Scaling: Horizontal]

        QDP2[Topic exchanges<br/>Pattern: Pub/sub<br/>Depth management: Per subscriber<br/>Scaling: Queue-specific]

        QDP1 --> QDP2
    end

    classDef flowControlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef consumerStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef designStyle fill:#10B981,stroke:#059669,color:#fff

    class PFC1,PFC2,PFC3 flowControlStyle
    class CS1,CS2 consumerStyle
    class QDP1,QDP2 designStyle
```

## Clustering Overhead

### RabbitMQ Cluster Architecture

```mermaid
graph TB
    subgraph sg_3_Node_RabbitMQ_Cluster[3-Node RabbitMQ Cluster]
        subgraph Node_1___Primary[Node 1 - Primary]
            N1[Node rabbit@node1<br/>RAM usage: 4GB<br/>CPU usage: 60%<br/>Disk I/O: 200 IOPS]

            N1Q[Queues: 500<br/>Messages/sec: 20K<br/>Connections: 1000<br/>Role: Queue master]
        end

        subgraph Node_2___Replica[Node 2 - Replica]
            N2[Node rabbit@node2<br/>RAM usage: 3GB<br/>CPU usage: 40%<br/>Disk I/O: 150 IOPS]

            N2Q[Queues: 300 (replicas)<br/>Messages/sec: 15K<br/>Connections: 800<br/>Role: Replica + new queues]
        end

        subgraph Node_3___Replica[Node 3 - Replica]
            N3[Node rabbit@node3<br/>RAM usage: 3GB<br/>CPU usage: 40%<br/>Disk I/O: 150 IOPS]

            N3Q[Queues: 300 (replicas)<br/>Messages/sec: 15K<br/>Connections: 800<br/>Role: Replica + new queues]
        end

        subgraph Cluster_Communication[Cluster Communication]
            COMM[Erlang distribution<br/>Port: 25672<br/>Heartbeat: 60s<br/>Network overhead: 50 Mbps]
        end

        N1 <--> COMM
        N2 <--> COMM
        N3 <--> COMM
    end

    subgraph Performance_Impact[Performance Impact]
        PI1[Replication overhead<br/>Network: 25% increase<br/>CPU: 15% increase<br/>Memory: 10% increase]

        PI2[Failover characteristics<br/>Detection time: 60 seconds<br/>Recovery time: 30 seconds<br/>Message loss: None (with confirms)]
    end

    classDef nodeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef queueStyle fill:#10B981,stroke:#059669,color:#fff
    classDef commStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef perfStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class N1,N2,N3 nodeStyle
    class N1Q,N2Q,N3Q queueStyle
    class COMM commStyle
    class PI1,PI2 perfStyle
```

### Single Node vs Cluster Performance

```mermaid
graph LR
    subgraph Single_Node_Setup[Single Node Setup]
        SINGLE1[Node configuration<br/>RAM: 8GB<br/>CPU cores: 8<br/>Network: 1 Gbps]

        SINGLE2[Performance<br/>Messages/sec: 50K<br/>Latency p95: 5ms<br/>Max connections: 2000<br/>Availability: 99.5%]

        SINGLE1 --> SINGLE2
    end

    subgraph sg_3_Node_Cluster[3-Node Cluster]
        CLUSTER1[Cluster configuration<br/>RAM per node: 4GB<br/>CPU cores per node: 4<br/>Network per node: 1 Gbps]

        CLUSTER2[Performance<br/>Messages/sec: 40K total<br/>Latency p95: 8ms<br/>Max connections: 3000<br/>Availability: 99.9%]

        CLUSTER1 --> CLUSTER2
    end

    subgraph Trade_off_Analysis[Trade-off Analysis]
        TRADEOFF1[Clustering benefits<br/>• High availability<br/>• Load distribution<br/>• Horizontal scaling<br/>• Disaster recovery]

        TRADEOFF2[Clustering costs<br/>• 20% throughput reduction<br/>• 60% latency increase<br/>• Network overhead<br/>• Operational complexity]

        SINGLE2 --> TRADEOFF1
        CLUSTER2 --> TRADEOFF2
    end

    classDef singleStyle fill:#10B981,stroke:#059669,color:#fff
    classDef clusterStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef tradeoffStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class SINGLE1,SINGLE2 singleStyle
    class CLUSTER1,CLUSTER2 clusterStyle
    class TRADEOFF1,TRADEOFF2 tradeoffStyle
```

### Network Partition Handling

```mermaid
graph TB
    subgraph Cluster_Partition_Scenario[Cluster Partition Scenario]
        BEFORE[Normal operation<br/>Nodes: 3 connected<br/>Queues: Replicated<br/>Messages: Flowing normally]

        PARTITION[Network partition<br/>Node 1: Isolated<br/>Nodes 2+3: Connected<br/>Split brain risk]

        AFTER[Partition handling<br/>Minority node: Paused<br/>Majority nodes: Continue<br/>Automatic recovery on heal]

        BEFORE --> PARTITION --> AFTER
    end

    subgraph Partition_Modes[Partition Modes]
        MODE1[pause_minority (default)<br/>Minority nodes pause<br/>Majority continues<br/>CAP: Consistency + Partition tolerance]

        MODE2[ignore<br/>Both sides continue<br/>Split brain allowed<br/>CAP: Availability + Partition tolerance]

        MODE3[autoheal<br/>Automatic healing<br/>Restart minority<br/>CAP: Eventual consistency]
    end

    subgraph Performance_Impact[Performance Impact]
        PERF1[Partition detection: 60s<br/>Recovery time: 120s<br/>Message loss: None<br/>Downtime: Minority nodes only]
    end

    classDef scenarioStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef modeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#10B981,stroke:#059669,color:#fff

    class BEFORE,PARTITION,AFTER scenarioStyle
    class MODE1,MODE2,MODE3 modeStyle
    class PERF1 perfStyle
```

## Lazy Queues vs Normal Queues

### Memory Usage Comparison

```mermaid
graph TB
    subgraph Normal_Queue_Behavior[Normal Queue Behavior]
        NORMAL1[Message flow<br/>1. Receive message<br/>2. Store in RAM<br/>3. Optionally persist<br/>4. Deliver from RAM]

        NORMAL2[Memory usage pattern<br/>RAM per message: 1KB<br/>1M messages: 1GB RAM<br/>Paging threshold: 40% RAM<br/>Performance: High until paging]

        NORMAL1 --> NORMAL2
    end

    subgraph Lazy_Queue_Behavior[Lazy Queue Behavior]
        LAZY1[Message flow<br/>1. Receive message<br/>2. Write to disk immediately<br/>3. Keep minimal RAM buffer<br/>4. Read from disk for delivery]

        LAZY2[Memory usage pattern<br/>RAM per message: 100 bytes<br/>1M messages: 100MB RAM<br/>Disk I/O: Always active<br/>Performance: Consistent]

        LAZY1 --> LAZY2
    end

    subgraph Performance_Characteristics[Performance Characteristics]
        PERF_NORMAL[Normal queue<br/>Throughput: 50K msg/sec (light)<br/>Throughput: 5K msg/sec (heavy)<br/>Memory: Variable<br/>Predictability: Poor]

        PERF_LAZY[Lazy queue<br/>Throughput: 20K msg/sec (consistent)<br/>Memory: Constant<br/>Disk I/O: Predictable<br/>Predictability: Excellent]

        NORMAL2 --> PERF_NORMAL
        LAZY2 --> PERF_LAZY
    end

    classDef normalStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef lazyStyle fill:#10B981,stroke:#059669,color:#fff
    classDef perfStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class NORMAL1,NORMAL2 normalStyle
    class LAZY1,LAZY2 lazyStyle
    class PERF_NORMAL,PERF_LAZY perfStyle
```

### Use Case Decision Matrix

```mermaid
graph LR
    subgraph High_Throughput__Low_Latency[High Throughput, Low Latency]
        HT_LL[Requirements<br/>• < 5ms latency<br/>• > 30K msg/sec<br/>• Predictable load<br/>• Sufficient RAM]

        HT_LL_REC[Recommendation: Normal<br/>Keep messages in RAM<br/>Avoid disk I/O overhead<br/>Scale RAM with load]

        HT_LL --> HT_LL_REC
    end

    subgraph Large_Queues__Memory_Constrained[Large Queues, Memory Constrained]
        LQ_MC[Requirements<br/>• > 100K queued messages<br/>• Limited RAM<br/>• Acceptable latency trade-off<br/>• Predictable performance]

        LQ_MC_REC[Recommendation: Lazy<br/>Consistent memory usage<br/>Predictable performance<br/>Better resource utilization]

        LQ_MC --> LQ_MC_REC
    end

    subgraph Variable_Load_Patterns[Variable Load Patterns]
        VLP[Requirements<br/>• Unpredictable bursts<br/>• Memory stability critical<br/>• Multiple queue priorities<br/>• Operational simplicity]

        VLP_REC[Recommendation: Lazy<br/>Stable memory footprint<br/>No paging surprises<br/>Easier capacity planning]

        VLP --> VLP_REC
    end

    classDef requirementStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef normalRecStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef lazyRecStyle fill:#10B981,stroke:#059669,color:#fff

    class HT_LL,LQ_MC,VLP requirementStyle
    class HT_LL_REC normalRecStyle
    class LQ_MC_REC,VLP_REC lazyRecStyle
```

## Message Acknowledgment Patterns

### Acknowledgment Mode Performance

```mermaid
graph TB
    subgraph Auto_Acknowledge[Auto-Acknowledge]
        AUTO1[Message delivery<br/>1. Send to consumer<br/>2. Mark as delivered<br/>3. Remove from queue<br/>4. No confirmation needed]

        AUTO2[Performance characteristics<br/>Throughput: 100K msg/sec<br/>Latency p95: 1ms<br/>Memory usage: Minimal<br/>Reliability: At-most-once]

        AUTO1 --> AUTO2
    end

    subgraph Manual_Acknowledge[Manual Acknowledge]
        MANUAL1[Message delivery<br/>1. Send to consumer<br/>2. Wait for ack/nack<br/>3. Process acknowledgment<br/>4. Remove from queue]

        MANUAL2[Performance characteristics<br/>Throughput: 50K msg/sec<br/>Latency p95: 3ms<br/>Memory usage: Moderate<br/>Reliability: At-least-once]

        MANUAL1 --> MANUAL2
    end

    subgraph Publisher_Confirms[Publisher Confirms]
        PUB_CONFIRM1[Message publishing<br/>1. Send to exchange<br/>2. Route to queues<br/>3. Persist to disk<br/>4. Send confirmation]

        PUB_CONFIRM2[Performance characteristics<br/>Throughput: 20K msg/sec<br/>Latency p95: 10ms<br/>Memory usage: High<br/>Reliability: Guaranteed delivery]

        PUB_CONFIRM1 --> PUB_CONFIRM2
    end

    subgraph Transactions
        TXN1[Transactional publishing<br/>1. Begin transaction<br/>2. Send messages<br/>3. Commit transaction<br/>4. Confirm all or none]

        TXN2[Performance characteristics<br/>Throughput: 5K msg/sec<br/>Latency p95: 50ms<br/>Memory usage: High<br/>Reliability: ACID properties]

        TXN1 --> TXN2
    end

    classDef autoStyle fill:#10B981,stroke:#059669,color:#fff
    classDef manualStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef confirmStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef txnStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class AUTO1,AUTO2 autoStyle
    class MANUAL1,MANUAL2 manualStyle
    class PUB_CONFIRM1,PUB_CONFIRM2 confirmStyle
    class TXN1,TXN2 txnStyle
```

### Acknowledgment Batching Optimization

```mermaid
graph LR
    subgraph Individual_Acknowledgments[Individual Acknowledgments]
        INDIVIDUAL1[Ack pattern<br/>One ack per message<br/>Network calls: High<br/>CPU overhead: High]

        INDIVIDUAL2[Performance<br/>Throughput: 10K msg/sec<br/>Network utilization: 50%<br/>CPU usage: 40%<br/>Latency: 2ms]

        INDIVIDUAL1 --> INDIVIDUAL2
    end

    subgraph Batched_Acknowledgments[Batched Acknowledgments]
        BATCH1[Ack pattern<br/>Multiple ack enabled<br/>Batch size: 100 messages<br/>Network calls: Reduced]

        BATCH2[Performance<br/>Throughput: 40K msg/sec<br/>Network utilization: 20%<br/>CPU usage: 15%<br/>Latency: 5ms]

        BATCH1 --> BATCH2
    end

    subgraph Optimized_Batching[Optimized Batching]
        OPT_BATCH1[Ack pattern<br/>Dynamic batch size<br/>Time-based batching: 10ms<br/>Load-adaptive sizing]

        OPT_BATCH2[Performance<br/>Throughput: 60K msg/sec<br/>Network utilization: 15%<br/>CPU usage: 12%<br/>Latency: 8ms average]

        OPT_BATCH1 --> OPT_BATCH2
    end

    classDef individualStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef batchStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef optimizedStyle fill:#10B981,stroke:#059669,color:#fff

    class INDIVIDUAL1,INDIVIDUAL2 individualStyle
    class BATCH1,BATCH2 batchStyle
    class OPT_BATCH1,OPT_BATCH2 optimizedStyle
```

## Deliveroo's Implementation

### Deliveroo's RabbitMQ Architecture

```mermaid
graph TB
    subgraph Deliveroo_Message_Processing[Deliveroo Message Processing]
        subgraph Order_Processing_Flow[Order Processing Flow]
            ORDER[Order Service<br/>Publishes: Order events<br/>Volume: 100K orders/day<br/>Peak: 2K orders/hour]

            RESTAURANT[Restaurant Service<br/>Consumes: Order events<br/>Publishes: Prep updates<br/>SLA: < 30 seconds]

            DELIVERY[Delivery Service<br/>Consumes: Ready events<br/>Publishes: Pickup/delivery<br/>Real-time updates]

            ORDER --> RESTAURANT --> DELIVERY
        end

        subgraph RabbitMQ_Infrastructure[RabbitMQ Infrastructure]
            CLUSTER[3-Node Cluster<br/>Node size: 4GB RAM each<br/>Queue type: Lazy queues<br/>Replication: All queues]

            EXCHANGES[Topic exchanges<br/>order.* routing<br/>restaurant.* routing<br/>delivery.* routing]

            QUEUES[Queue configuration<br/>x-queue-type: lazy<br/>x-message-ttl: 300000<br/>x-max-length: 50000]

            CLUSTER --> EXCHANGES --> QUEUES
        end
    end

    subgraph Performance_Achievements[Performance Achievements]
        PERF1[Message throughput: 50K msg/sec<br/>End-to-end latency: p95 < 5s<br/>Queue depth: avg 1K messages<br/>Availability: 99.95%]

        PERF2[Resource utilization<br/>CPU: 60% average<br/>Memory: 80% utilization<br/>Network: 100 Mbps<br/>Disk I/O: 500 IOPS]
    end

    classDef serviceStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef infraStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef configStyle fill:#10B981,stroke:#059669,color:#fff
    classDef perfStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class ORDER,RESTAURANT,DELIVERY serviceStyle
    class CLUSTER,EXCHANGES,QUEUES infraStyle
    class PERF1,PERF2 perfStyle
```

### Critical Configuration Parameters

```mermaid
graph TB
    subgraph Memory_Management[Memory Management]
        MEM1[vm_memory_high_watermark: 0.6<br/>vm_memory_high_watermark_paging_ratio: 0.5<br/>disk_free_limit: 50GB<br/>Memory alarms trigger at 60%]
    end

    subgraph Queue_Configuration[Queue Configuration]
        QUEUE1[Default queue type: lazy<br/>x-max-length: 100000<br/>x-message-ttl: 86400000<br/>x-expires: 1800000]

        QUEUE2[Consumer prefetch: 100<br/>Publisher confirms: enabled<br/>Manual acknowledgment: true<br/>Durable: true]

        QUEUE1 --> QUEUE2
    end

    subgraph Clustering_Configuration[Clustering Configuration]
        CLUSTER1[cluster_formation.peer_discovery_backend: rabbit_peer_discovery_k8s<br/>cluster_partition_handling: pause_minority<br/>heartbeat: 60<br/>net_ticktime: 60]
    end

    subgraph Performance_Tuning[Performance Tuning]
        PERF1[tcp_listen_options.nodelay: true<br/>tcp_listen_options.sndbuf: 196608<br/>tcp_listen_options.recbuf: 196608<br/>collect_statistics_interval: 60000]
    end

    classDef memStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef queueStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef clusterStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef perfStyle fill:#10B981,stroke:#059669,color:#fff

    class MEM1 memStyle
    class QUEUE1,QUEUE2 queueStyle
    class CLUSTER1 clusterStyle
    class PERF1 perfStyle
```

### Monitoring and Alerting Strategy

```mermaid
graph LR
    subgraph Key_Metrics[Key Metrics]
        METRICS1[Queue depth<br/>Alert: > 10K messages<br/>Critical: > 50K messages<br/>Action: Scale consumers]

        METRICS2[Memory usage<br/>Alert: > 70%<br/>Critical: > 85%<br/>Action: Flow control activation]

        METRICS3[Message rates<br/>Publish rate: 1K/sec<br/>Consume rate: 1K/sec<br/>Monitor: Rate imbalance]
    end

    subgraph Performance_Indicators[Performance Indicators]
        PI1[Consumer utilization<br/>Target: > 80%<br/>Scale trigger: < 60%<br/>Method: Consumer count adjustment]

        PI2[Connection count<br/>Limit: 1000 per node<br/>Alert: > 800<br/>Action: Connection pooling review]

        PI3[Disk space<br/>Alert: < 20% free<br/>Critical: < 10% free<br/>Action: Log rotation, cleanup]
    end

    subgraph Alerting_Actions[Alerting Actions]
        ACTIONS1[Auto-scaling<br/>Kubernetes HPA<br/>Based on queue depth<br/>Consumer pod scaling]

        ACTIONS2[Circuit breaker<br/>Producer flow control<br/>Prevent cascade failures<br/>Graceful degradation]
    end

    METRICS1 --> PI1 --> ACTIONS1
    METRICS2 --> PI2 --> ACTIONS2
    METRICS3 --> PI3

    classDef metricsStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef piStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef actionStyle fill:#10B981,stroke:#059669,color:#fff

    class METRICS1,METRICS2,METRICS3 metricsStyle
    class PI1,PI2,PI3 piStyle
    class ACTIONS1,ACTIONS2 actionStyle
```

## Production Lessons Learned

### Performance Optimization Checklist

```mermaid
graph TB
    subgraph Queue_Design[Queue Design]
        QD1[Use lazy queues for<br/>• Large message backlogs<br/>• Unpredictable load<br/>• Memory-constrained systems]

        QD2[Use normal queues for<br/>• Low-latency requirements<br/>• Predictable small loads<br/>• Abundant RAM available]

        QD1 --> QD2
    end

    subgraph Consumer_Optimization[Consumer Optimization]
        CO1[Prefetch sizing<br/>• High throughput: 100-1000<br/>• Low memory: 10-50<br/>• Balance throughput vs memory]

        CO2[Acknowledgment strategy<br/>• High reliability: Manual ack<br/>• High throughput: Auto ack<br/>• Batch acknowledgments when possible]

        CO1 --> CO2
    end

    subgraph Infrastructure_Sizing[Infrastructure Sizing]
        IS1[Single node sufficient for<br/>• < 10K msg/sec<br/>• < 99.5% availability requirement<br/>• Development/testing]

        IS2[Clustering required for<br/>• > 10K msg/sec<br/>• > 99.9% availability<br/>• Production workloads]

        IS1 --> IS2
    end

    classDef queueStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef consumerStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef infraStyle fill:#10B981,stroke:#059669,color:#fff

    class QD1,QD2 queueStyle
    class CO1,CO2 consumerStyle
    class IS1,IS2 infraStyle
```

### Critical Performance Factors

1. **Queue Type Selection**: Lazy queues for large backlogs, normal for low-latency
2. **Consumer Prefetch**: Balance throughput and memory usage (50-200 optimal range)
3. **Clustering Strategy**: 3-node clusters provide best availability vs complexity
4. **Memory Management**: Monitor and alert on 70% memory usage
5. **Acknowledgment Patterns**: Batch acknowledgments improve throughput significantly

### Performance Benchmarks by Configuration

| Configuration | Throughput | Latency p95 | Memory Usage | Use Case |
|---------------|------------|-------------|--------------|----------|
| **Single Node, Normal** | 50K msg/sec | 2ms | High | Development, low-latency |
| **Single Node, Lazy** | 20K msg/sec | 10ms | Low | Large queues, memory-constrained |
| **Cluster, Normal** | 40K msg/sec | 8ms | High | High availability, low-latency |
| **Cluster, Lazy** | 15K msg/sec | 15ms | Low | High availability, large queues |

### Common Pitfalls

1. **Deep queues without lazy setting**: Memory exhaustion and performance degradation
2. **Over-clustering**: Unnecessary complexity for simple workloads
3. **High prefetch on memory-constrained systems**: OOM conditions
4. **No publisher confirms in critical systems**: Message loss during failures
5. **Inadequate monitoring**: Performance issues discovered too late

**Source**: Based on Deliveroo, Shopify, and RabbitMQ production implementations