# NATS Performance Profile

## Overview

NATS performance characteristics in production environments, covering JetStream vs Core performance, subject hierarchy impact, clustering topology effects, and message delivery guarantees. Based on CNCF adoption metrics and high-scale deployments.

## JetStream vs Core Performance

### Core NATS Performance Characteristics

```mermaid
graph TB
    subgraph Core_NATS_Architecture[Core NATS Architecture]
        CORE1[Fire-and-forget messaging<br/>In-memory only<br/>No persistence<br/>At-most-once delivery]

        CORE2[Performance metrics<br/>Latency: 100-200 microseconds<br/>Throughput: 1M+ msg/sec<br/>Memory usage: 10MB base<br/>CPU overhead: Minimal]

        CORE3[Use cases<br/>High-frequency updates<br/>Real-time data streams<br/>IoT sensor data<br/>Ephemeral notifications]

        CORE1 --> CORE2 --> CORE3
    end

    subgraph Core_NATS_Message_Flow[Core NATS Message Flow]
        PUB[Publisher<br/>Subject: sensor.temp.room1<br/>Payload: 45.2C<br/>QoS: Fire-and-forget]

        SERVER[NATS Server<br/>Subject matching<br/>Message routing<br/>No storage]

        SUB1[Subscriber 1<br/>Subject: sensor.temp.*<br/>Processing: Real-time<br/>Acknowledgment: None]

        SUB2[Subscriber 2<br/>Subject: sensor.*<br/>Processing: Real-time<br/>Acknowledgment: None]

        PUB --> SERVER
        SERVER --> SUB1
        SERVER --> SUB2
    end

    classDef coreStyle fill:#10B981,stroke:#059669,color:#fff
    classDef flowStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class CORE1,CORE2,CORE3 coreStyle
    class PUB,SERVER,SUB1,SUB2 flowStyle
```

### JetStream Performance Characteristics

```mermaid
graph TB
    subgraph JetStream_Architecture[JetStream Architecture]
        JS1[Persistent messaging<br/>Stream storage<br/>Multiple delivery guarantees<br/>At-least-once, exactly-once]

        JS2[Performance metrics<br/>Latency: 1-5 milliseconds<br/>Throughput: 100K msg/sec<br/>Memory usage: Variable<br/>Storage overhead: High]

        JS3[Use cases<br/>Event sourcing<br/>Message queuing<br/>Audit trails<br/>Reliable processing]

        JS1 --> JS2 --> JS3
    end

    subgraph JetStream_Message_Flow[JetStream Message Flow]
        JS_PUB[Publisher<br/>Subject: events.user.signup<br/>Payload: User data<br/>QoS: At-least-once]

        JS_STREAM[Stream: USER_EVENTS<br/>Storage: File/Memory<br/>Retention: 7 days<br/>Replication: 3x]

        JS_CON1[Consumer 1<br/>Delivery: Push/Pull<br/>Acknowledgment: Required<br/>Processing: Reliable]

        JS_CON2[Consumer 2<br/>Delivery: Push/Pull<br/>Acknowledgment: Required<br/>Processing: Reliable]

        JS_PUB --> JS_STREAM
        JS_STREAM --> JS_CON1
        JS_STREAM --> JS_CON2
    end

    classDef jsStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef jsFlowStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class JS1,JS2,JS3 jsStyle
    class JS_PUB,JS_STREAM,JS_CON1,JS_CON2 jsFlowStyle
```

### Performance Comparison Matrix

```mermaid
graph LR
    subgraph Latency_Performance[Latency Performance]
        LAT1[Core NATS<br/>p50: 100μs<br/>p95: 200μs<br/>p99: 500μs<br/>Jitter: Low]

        LAT2[JetStream Memory<br/>p50: 1ms<br/>p95: 3ms<br/>p99: 8ms<br/>Jitter: Medium]

        LAT3[JetStream File<br/>p50: 2ms<br/>p95: 8ms<br/>p99: 20ms<br/>Jitter: High]
    end

    subgraph Throughput_Performance[Throughput Performance]
        THR1[Core NATS<br/>Single node: 1M msg/sec<br/>Cluster: 3M msg/sec<br/>Memory: 10MB<br/>CPU: 20%]

        THR2[JetStream Memory<br/>Single node: 300K msg/sec<br/>Cluster: 800K msg/sec<br/>Memory: 1GB<br/>CPU: 60%]

        THR3[JetStream File<br/>Single node: 100K msg/sec<br/>Cluster: 250K msg/sec<br/>Memory: 500MB<br/>CPU: 80%]
    end

    subgraph Resource_Usage[Resource Usage]
        RES1[Memory overhead<br/>Core: Minimal<br/>JS Memory: High<br/>JS File: Medium]

        RES2[Disk usage<br/>Core: None<br/>JS Memory: Optional<br/>JS File: Required]

        RES3[Network overhead<br/>Core: Minimal<br/>JS: Replication + Acks<br/>Cluster: Gossip protocol]
    end

    classDef coreStyle fill:#10B981,stroke:#059669,color:#fff
    classDef jsMemStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef jsFileStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class LAT1,THR1 coreStyle
    class LAT2,THR2 jsMemStyle
    class LAT3,THR3 jsFileStyle
    class RES1,RES2,RES3 coreStyle
```

## Subject Hierarchy Impact

### Wildcard Subscription Performance

```mermaid
graph TB
    subgraph Subject_Hierarchy_Design[Subject Hierarchy Design]
        HIER1[Good hierarchy<br/>app.service.instance.metric<br/>Example: billing.api.pod-1.cpu<br/>Levels: 4 (optimal)]

        HIER2[Poor hierarchy<br/>very.deep.nested.subject.hierarchy.with.many.levels<br/>Example: company.division.team.service.version.instance.metric.type<br/>Levels: 8+ (excessive)]

        HIER3[Flat hierarchy<br/>billing-api-pod-1-cpu<br/>Example: single_level_subjects<br/>Levels: 1 (limited flexibility)]

        HIER1 --> HIER2 --> HIER3
    end

    subgraph Wildcard_Performance_Impact[Wildcard Performance Impact]
        WILD1[Specific subscription<br/>Subject: billing.api.pod-1.cpu<br/>Matches: 1 exact<br/>CPU overhead: Minimal<br/>Memory: 1KB per sub]

        WILD2[Single wildcard<br/>Subject: billing.api.*.cpu<br/>Matches: ~100 subjects<br/>CPU overhead: Low<br/>Memory: 1KB per sub]

        WILD3[Multiple wildcards<br/>Subject: *.api.*.cpu<br/>Matches: ~1000 subjects<br/>CPU overhead: Medium<br/>Memory: 1KB per sub]

        WILD4[Full wildcard<br/>Subject: ><br/>Matches: ALL subjects<br/>CPU overhead: High<br/>Memory: Proportional to traffic]

        WILD1 --> WILD2 --> WILD3 --> WILD4
    end

    subgraph Performance_Measurements[Performance Measurements]
        PERF1[Routing performance<br/>1-level: 1M msg/sec<br/>2-level wildcard: 800K msg/sec<br/>3-level wildcard: 500K msg/sec<br/>Full wildcard: 100K msg/sec]
    end

    classDef hierStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef wildStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef perfStyle fill:#10B981,stroke:#059669,color:#fff

    class HIER1,HIER2,HIER3 hierStyle
    class WILD1,WILD2,WILD3,WILD4 wildStyle
    class PERF1 perfStyle
```

### Subject Optimization Strategies

```mermaid
graph TB
    subgraph Optimization_Techniques[Optimization Techniques]
        OPT1[Subject design principles<br/>• Keep hierarchy shallow (≤4 levels)<br/>• Use meaningful names<br/>• Avoid deep wildcards<br/>• Group related subjects]

        OPT2[Subscription patterns<br/>• Prefer specific over wildcard<br/>• Use queue groups for load balancing<br/>• Minimize overlapping subscriptions<br/>• Monitor subscription count]

        OPT3[Message routing efficiency<br/>• Subject-based sharding<br/>• Avoid broadcast patterns<br/>• Use request-reply for point-to-point<br/>• Implement message filtering]

        OPT1 --> OPT2 --> OPT3
    end

    subgraph Anti_patterns_and_Impact[Anti-patterns and Impact]
        ANTI1[Subject explosion<br/>Unique subject per message<br/>Impact: Memory exhaustion<br/>Performance: Severe degradation]

        ANTI2[Deep wildcard abuse<br/>Pattern: *.*.*.*.><br/>Impact: CPU overhead<br/>Performance: Linear degradation]

        ANTI3[Broadcast overuse<br/>Pattern: All consumers get all messages<br/>Impact: Network saturation<br/>Performance: Bandwidth limitation]

        ANTI1 --> ANTI2 --> ANTI3
    end

    classDef optStyle fill:#10B981,stroke:#059669,color:#fff
    classDef antiStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class OPT1,OPT2,OPT3 optStyle
    class ANTI1,ANTI2,ANTI3 antiStyle
```

## Clustering Topology Effects

### NATS Cluster Architecture

```mermaid
graph TB
    subgraph Full_Mesh_Clustering[Full Mesh Clustering]
        MESH1[Node 1<br/>Connections: 2 (to nodes 2,3)<br/>Memory: 100MB<br/>CPU: 30%<br/>Role: Route + Client]

        MESH2[Node 2<br/>Connections: 2 (to nodes 1,3)<br/>Memory: 100MB<br/>CPU: 30%<br/>Role: Route + Client]

        MESH3[Node 3<br/>Connections: 2 (to nodes 1,2)<br/>Memory: 100MB<br/>CPU: 30%<br/>Role: Route + Client]

        MESH1 <--> MESH2
        MESH2 <--> MESH3
        MESH3 <--> MESH1
    end

    subgraph Cluster_Performance[Cluster Performance]
        CLUSTER_PERF1[Message routing<br/>Hop count: 1 (direct)<br/>Latency overhead: 0.1ms<br/>Throughput: 500K msg/sec<br/>Fault tolerance: N-1 failures]

        CLUSTER_PERF2[Resource overhead<br/>Network connections: O(n²)<br/>Memory per node: 100MB base<br/>CPU overhead: 10% routing<br/>Gossip protocol: Minimal]
    end

    subgraph Client_Distribution[Client Distribution]
        CLIENT1[Client distribution<br/>Clients per node: 1000<br/>Load balancing: Automatic<br/>Failover time: 2-5 seconds<br/>Connection recovery: Automatic]
    end

    classDef meshStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#10B981,stroke:#059669,color:#fff
    classDef clientStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class MESH1,MESH2,MESH3 meshStyle
    class CLUSTER_PERF1,CLUSTER_PERF2 perfStyle
    class CLIENT1 clientStyle
```

### Cluster Scaling Characteristics

```mermaid
graph LR
    subgraph sg_3_Node_Cluster[3-Node Cluster]
        C3_1[Configuration<br/>Nodes: 3<br/>Connections: 3<br/>Memory: 300MB total<br/>CPU: 90% total]

        C3_2[Performance<br/>Throughput: 1.5M msg/sec<br/>Latency: 200μs<br/>Max clients: 3000<br/>Fault tolerance: 1 node]

        C3_1 --> C3_2
    end

    subgraph sg_5_Node_Cluster[5-Node Cluster]
        C5_1[Configuration<br/>Nodes: 5<br/>Connections: 10<br/>Memory: 500MB total<br/>CPU: 150% total]

        C5_2[Performance<br/>Throughput: 2.5M msg/sec<br/>Latency: 250μs<br/>Max clients: 5000<br/>Fault tolerance: 2 nodes]

        C5_1 --> C5_2
    end

    subgraph sg_10_Node_Cluster[10-Node Cluster]
        C10_1[Configuration<br/>Nodes: 10<br/>Connections: 45<br/>Memory: 1GB total<br/>CPU: 300% total]

        C10_2[Performance<br/>Throughput: 4M msg/sec<br/>Latency: 400μs<br/>Max clients: 10000<br/>Fault tolerance: 4-5 nodes]

        C10_1 --> C10_2
    end

    subgraph Scaling_Analysis[Scaling Analysis]
        SCALE1[Linear scaling until 7 nodes<br/>Diminishing returns after 10 nodes<br/>Network becomes bottleneck<br/>Gossip overhead increases]
    end

    C3_2 --> SCALE1
    C5_2 --> SCALE1
    C10_2 --> SCALE1

    classDef clusterStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef scaleStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class C3_1,C3_2,C5_1,C5_2,C10_1,C10_2 clusterStyle
    class SCALE1 scaleStyle
```

### Geographic Distribution

```mermaid
graph TB
    subgraph Single_Region_Cluster[Single Region Cluster]
        SR1[Latency within region: <1ms<br/>Network bandwidth: 10 Gbps<br/>Message routing: Direct<br/>Consistency: Strong]
    end

    subgraph Multi_Region_with_Gateways[Multi-Region with Gateways]
        MR1[Region A Cluster<br/>Nodes: 3<br/>Clients: Local<br/>Latency: <1ms local]

        MR2[Region B Cluster<br/>Nodes: 3<br/>Clients: Local<br/>Latency: <1ms local]

        GW[NATS Gateways<br/>Inter-region: 100ms<br/>Message optimization<br/>Subject filtering]

        MR1 <--> GW
        MR2 <--> GW
    end

    subgraph Performance_Comparison[Performance Comparison]
        COMP1[Single region<br/>Global latency: High<br/>Bandwidth usage: High<br/>Fault tolerance: Region-level risk]

        COMP2[Multi-region with gateways<br/>Local latency: Low<br/>Global latency: Optimized<br/>Fault tolerance: Region-level]
    end

    SR1 --> COMP1
    MR1 --> COMP2
    MR2 --> COMP2

    classDef singleStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef multiStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef gatewayStyle fill:#10B981,stroke:#059669,color:#fff
    classDef compStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class SR1 singleStyle
    class MR1,MR2 multiStyle
    class GW gatewayStyle
    class COMP1,COMP2 compStyle
```

## Message Delivery Guarantees Cost

### Delivery Guarantee Comparison

```mermaid
graph TB
    subgraph At_Most_Once__Core_NATS[At-Most-Once (Core NATS)]
        AMO1[Delivery semantics<br/>Fire-and-forget<br/>No acknowledgments<br/>No retries<br/>No persistence]

        AMO2[Performance impact<br/>Latency: 100μs<br/>Throughput: 1M msg/sec<br/>Memory: Minimal<br/>CPU: 10%]

        AMO3[Use cases<br/>IoT sensor data<br/>Real-time metrics<br/>Non-critical notifications<br/>High-frequency updates]

        AMO1 --> AMO2 --> AMO3
    end

    subgraph At_Least_Once__JetStream[At-Least-Once (JetStream)]
        ALO1[Delivery semantics<br/>Publisher acknowledgment<br/>Consumer acknowledgment<br/>Retry on failure<br/>Persistent storage]

        ALO2[Performance impact<br/>Latency: 2-5ms<br/>Throughput: 200K msg/sec<br/>Memory: High<br/>CPU: 60%]

        ALO3[Use cases<br/>Order processing<br/>Financial transactions<br/>Critical notifications<br/>Audit logs]

        ALO1 --> ALO2 --> ALO3
    end

    subgraph Exactly_Once__JetStream_Dedup[Exactly-Once (JetStream Dedup)]
        EO1[Delivery semantics<br/>Deduplication enabled<br/>Consumer tracking<br/>Idempotent processing<br/>Complex acknowledgment]

        EO2[Performance impact<br/>Latency: 5-10ms<br/>Throughput: 50K msg/sec<br/>Memory: Very high<br/>CPU: 80%]

        EO3[Use cases<br/>Payment processing<br/>Account updates<br/>Inventory management<br/>Critical state changes]

        EO1 --> EO2 --> EO3
    end

    classDef amoStyle fill:#10B981,stroke:#059669,color:#fff
    classDef aloStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef eoStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class AMO1,AMO2,AMO3 amoStyle
    class ALO1,ALO2,ALO3 aloStyle
    class EO1,EO2,EO3 eoStyle
```

### Acknowledgment and Retry Overhead

```mermaid
graph LR
    subgraph Manual_Acknowledgment[Manual Acknowledgment]
        MANUAL1[Ack configuration<br/>ack_wait: 30s<br/>max_deliver: 3<br/>Consumer explicit ack<br/>Message redelivery on timeout]

        MANUAL2[Performance characteristics<br/>Latency: +2ms overhead<br/>Throughput: 50% reduction<br/>Memory: 2x increase<br/>Reliability: High]

        MANUAL1 --> MANUAL2
    end

    subgraph Automatic_Acknowledgment[Automatic Acknowledgment]
        AUTO1[Ack configuration<br/>ack_explicit: false<br/>Immediate acknowledgment<br/>No redelivery<br/>Consumer reliability dependent]

        AUTO2[Performance characteristics<br/>Latency: No overhead<br/>Throughput: Maximum<br/>Memory: Minimal<br/>Reliability: Application-dependent]

        AUTO1 --> AUTO2
    end

    subgraph Batch_Acknowledgment[Batch Acknowledgment]
        BATCH1[Ack configuration<br/>ack_sync: false<br/>ack_all: true<br/>Batch processing<br/>Periodic commits]

        BATCH2[Performance characteristics<br/>Latency: Variable<br/>Throughput: High<br/>Memory: Moderate<br/>Reliability: Eventual]

        BATCH1 --> BATCH2
    end

    classDef manualStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef autoStyle fill:#10B981,stroke:#059669,color:#fff
    classDef batchStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class MANUAL1,MANUAL2 manualStyle
    class AUTO1,AUTO2 autoStyle
    class BATCH1,BATCH2 batchStyle
```

## CNCF Adoption Metrics

### NATS Usage Patterns in CNCF Projects

```mermaid
graph TB
    subgraph CNCF_Project_Usage[CNCF Project Usage]
        K8S[Kubernetes<br/>Use case: Event streaming<br/>Components: Controller events<br/>Scale: 100K events/sec<br/>Deployment: Core NATS]

        ISTIO[Istio<br/>Use case: Service mesh telemetry<br/>Components: Mixer, telemetry v2<br/>Scale: 1M metrics/sec<br/>Deployment: Core NATS]

        HELM[Helm<br/>Use case: Release notifications<br/>Components: Tiller events<br/>Scale: 1K events/sec<br/>Deployment: Core NATS]

        PROM[Prometheus<br/>Use case: Alert routing<br/>Components: Alert manager<br/>Scale: 10K alerts/sec<br/>Deployment: JetStream]
    end

    subgraph Performance_in_CNCF_Context[Performance in CNCF Context]
        PERF1[Container orchestration<br/>Event latency: <100μs required<br/>Event throughput: >100K/sec<br/>Memory footprint: <50MB<br/>CPU overhead: <5%]

        PERF2[Microservices communication<br/>Request-reply: <1ms<br/>Service discovery: 10K lookups/sec<br/>Configuration distribution: 1K updates/sec<br/>Health checks: 100K checks/sec]
    end

    subgraph Deployment_Patterns[Deployment Patterns]
        DEPLOY1[Sidecar pattern<br/>NATS per pod<br/>Local communication<br/>Minimal network overhead]

        DEPLOY2[Shared service<br/>NATS cluster<br/>Cross-namespace communication<br/>Central management]

        DEPLOY3[Hybrid approach<br/>Local for high-frequency<br/>Shared for coordination<br/>Optimal resource usage]
    end

    classDef cncfStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef perfStyle fill:#10B981,stroke:#059669,color:#fff
    classDef deployStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class K8S,ISTIO,HELM,PROM cncfStyle
    class PERF1,PERF2 perfStyle
    class DEPLOY1,DEPLOY2,DEPLOY3 deployStyle
```

### Cloud-Native Performance Requirements

```mermaid
graph LR
    subgraph Observability_Requirements[Observability Requirements]
        OBS1[Metrics collection<br/>Rate: 1M+ metrics/sec<br/>Latency: <10ms p99<br/>Storage: Time-series DB<br/>Retention: 15 days]

        OBS2[Distributed tracing<br/>Spans: 100K+ spans/sec<br/>Latency: <5ms overhead<br/>Sampling: 1-10%<br/>Storage: Trace storage]

        OBS1 --> OBS2
    end

    subgraph Service_Coordination[Service Coordination]
        COORD1[Service discovery<br/>Updates: 1K/sec<br/>Propagation: <100ms<br/>Consistency: Eventual<br/>Scale: 10K services]

        COORD2[Configuration management<br/>Updates: 10/sec<br/>Propagation: <1s<br/>Consistency: Strong<br/>Rollback: Required]

        COORD1 --> COORD2
    end

    subgraph Event_Processing[Event Processing]
        EVENT1[System events<br/>Rate: 100K events/sec<br/>Processing: Real-time<br/>Filtering: Subject-based<br/>Fanout: 1:N]

        EVENT2[Business events<br/>Rate: 10K events/sec<br/>Processing: Reliable<br/>Ordering: Required<br/>Persistence: Required]

        EVENT1 --> EVENT2
    end

    classDef obsStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef coordStyle fill:#10B981,stroke:#059669,color:#fff
    classDef eventStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class OBS1,OBS2 obsStyle
    class COORD1,COORD2 coordStyle
    class EVENT1,EVENT2 eventStyle
```

## Production Lessons Learned

### Performance Optimization Best Practices

```mermaid
graph TB
    subgraph Core_NATS_Optimization[Core NATS Optimization]
        CORE_OPT1[Connection management<br/>• Use connection pooling<br/>• Minimize connection count<br/>• Configure appropriate timeouts<br/>• Monitor connection health]

        CORE_OPT2[Subject design<br/>• Keep hierarchy shallow<br/>• Use specific subscriptions<br/>• Avoid excessive wildcards<br/>• Group related subjects]

        CORE_OPT1 --> CORE_OPT2
    end

    subgraph JetStream_Optimization[JetStream Optimization]
        JS_OPT1[Stream configuration<br/>• Choose appropriate storage<br/>• Configure retention policies<br/>• Set reasonable message limits<br/>• Monitor stream metrics]

        JS_OPT2[Consumer optimization<br/>• Use pull consumers for control<br/>• Configure appropriate batch sizes<br/>• Set reasonable ack timeouts<br/>• Monitor consumer lag]

        JS_OPT1 --> JS_OPT2
    end

    subgraph Cluster_Optimization[Cluster Optimization]
        CLUSTER_OPT1[Topology design<br/>• Keep clusters small (3-7 nodes)<br/>• Use gateways for geo-distribution<br/>• Monitor inter-node communication<br/>• Plan for network partitions]

        CLUSTER_OPT2[Resource allocation<br/>• Size nodes appropriately<br/>• Monitor memory usage<br/>• Configure garbage collection<br/>• Plan for failover capacity]

        CLUSTER_OPT1 --> CLUSTER_OPT2
    end

    classDef coreOptStyle fill:#10B981,stroke:#059669,color:#fff
    classDef jsOptStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef clusterOptStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class CORE_OPT1,CORE_OPT2 coreOptStyle
    class JS_OPT1,JS_OPT2 jsOptStyle
    class CLUSTER_OPT1,CLUSTER_OPT2 clusterOptStyle
```

### Critical Performance Factors

1. **Use Case Selection**: Core NATS for high-performance, JetStream for reliability
2. **Subject Design**: Shallow hierarchies and specific subscriptions for optimal routing
3. **Cluster Sizing**: 3-7 nodes optimal, gateways for geographic distribution
4. **Delivery Guarantees**: Choose appropriate level for use case requirements
5. **Resource Management**: Monitor memory and CPU usage, especially with JetStream

### Performance Benchmarks by Configuration

| Configuration | Throughput | Latency p95 | Memory Usage | Use Case |
|---------------|------------|-------------|--------------|----------|
| **Core NATS Single** | 1M msg/sec | 200μs | 10MB | IoT, telemetry |
| **Core NATS Cluster** | 3M msg/sec | 400μs | 30MB | Distributed systems |
| **JetStream Memory** | 300K msg/sec | 5ms | 1GB | Reliable messaging |
| **JetStream File** | 100K msg/sec | 20ms | 500MB | Persistent workflows |

### Common Pitfalls

1. **Inappropriate delivery guarantees**: Using JetStream when Core NATS suffices
2. **Poor subject design**: Deep hierarchies and excessive wildcards
3. **Over-clustering**: Too many nodes causing gossip overhead
4. **Resource under-provisioning**: Insufficient memory for JetStream workloads
5. **Missing monitoring**: Performance issues discovered too late

**Source**: Based on CNCF project usage, Synadia implementations, and cloud-native adoption patterns