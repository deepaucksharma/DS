# Layer 2: The 20 Primitives

Primitives are implementation building blocks that deliver capabilities. Instagram uses Partitioning (P1) for photo storage, Netflix uses Caching (P11) for content delivery, Uber uses Consensus (P5) for driver assignment.

## Core Infrastructure Primitives

```mermaid
graph TB
    subgraph StatePlane["State Plane - Data Primitives"]
        P1[P1: Partitioning<br/>Split data across nodes]
        P2[P2: Replication<br/>Copy data for durability]
        P3[P3: Durable Log<br/>Append-only storage]
        P4[P4: Specialized Index<br/>Fast data access]
        P14[P14: Write-Ahead Log<br/>Crash recovery]
    end

    subgraph ServicePlane["Service Plane - Coordination Primitives"]
        P5[P5: Consensus<br/>Distributed agreement]
        P6[P6: Causal Tracking<br/>Event ordering]
        P7[P7: Idempotency<br/>Safe retries]
        P8[P8: Retry Logic<br/>Fault tolerance]
        P19[P19: Change Data Capture<br/>Event streaming]
    end

    subgraph EdgePlane["Edge Plane - Performance Primitives"]
        P11[P11: Caching<br/>Latency reduction]
        P15[P15: Bloom Filter<br/>Existence checks]
        P16[P16: Merkle Tree<br/>Data verification]
        P18[P18: Gossip Protocol<br/>Information spread]
    end

    subgraph ControlPlane["Control Plane - Resilience Primitives"]
        P9[P9: Circuit Breaker<br/>Failure isolation]
        P10[P10: Bulkheading<br/>Resource isolation]
        P12[P12: Load Shedding<br/>Overload protection]
        P13[P13: Sharded Locks<br/>Concurrency control]
        P20[P20: Feature Flags<br/>Safe deployment]
    end

    %% Apply four-plane colors
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class P1,P2,P3,P4,P14 stateStyle
    class P5,P6,P7,P8,P19 serviceStyle
    class P11,P15,P16,P18 edgeStyle
    class P9,P10,P12,P13,P20 controlStyle
```

## Primitive Trigger Thresholds

```mermaid
graph TB
    subgraph ScaleTriggers["Scale-Driven Triggers"]
        P1T[">20K writes/sec<br/>OR >100GB data<br/>→ Partitioning"]
        P2T["RPO <60s OR RTO <30s<br/>→ Replication"]
        P11T["Read/Write ratio >10:1<br/>→ Caching"]
        P10T["Multi-tenant system<br/>→ Bulkheading"]
    end

    subgraph ReliabilityTriggers["Reliability-Driven Triggers"]
        P5T["Distributed coordination<br/>→ Consensus"]
        P8T["Network operations<br/>→ Retry Logic"]
        P9T["Unreliable dependencies<br/>→ Circuit Breaker"]
        P12T["Overload risk<br/>→ Load Shedding"]
    end

    subgraph PerformanceTriggers["Performance-Driven Triggers"]
        P4T["Query diversity >1K<br/>→ Specialized Index"]
        P15T["Existence checks<br/>→ Bloom Filter"]
        P7T["Any retry scenario<br/>→ Idempotency"]
        P13T["High contention<br/>→ Sharded Locks"]
    end

    %% Real examples
    P1T --> |Instagram Photos| Instagram
    P11T --> |Netflix CDN| Netflix
    P5T --> |Uber Driver Assignment| Uber
    P9T --> |Stripe Payment Gateway| Stripe

    %% Apply colors
    classDef scaleStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef reliabilityStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef performanceStyle fill:#0066CC,stroke:#004499,color:#fff

    class P1T,P2T,P11T,P10T scaleStyle
    class P5T,P8T,P9T,P12T reliabilityStyle
    class P4T,P15T,P7T,P13T performanceStyle
```

## Production Implementation Examples

```mermaid
graph LR
    subgraph Netflix["Netflix Architecture"]
        N1[P11: CDN Caching<br/>Edge locations]
        N2[P1: Content Partitioning<br/>Geographic shards]
        N3[P12: Load Shedding<br/>Video quality degradation]
        N4[P20: Feature Flags<br/>A/B testing]
    end

    subgraph Uber["Uber Architecture"]
        U1[P5: Consensus<br/>Driver assignment]
        U2[P1: Geo Partitioning<br/>City-based shards]
        U3[P6: Causal Tracking<br/>Ride state ordering]
        U4[P9: Circuit Breaker<br/>Maps API protection]
    end

    subgraph Instagram["Instagram Architecture"]
        I1[P1: Photo Partitioning<br/>User-based sharding]
        I2[P11: Feed Caching<br/>Redis clusters]
        I3[P19: CDC<br/>Activity streams]
        I4[P15: Bloom Filter<br/>Duplicate photo detection]
    end

    %% Apply colors
    classDef netflixStyle fill:#E50914,stroke:#B20710,color:#fff
    classDef uberStyle fill:#000000,stroke:#333333,color:#fff
    classDef instagramStyle fill:#E4405F,stroke:#C13584,color:#fff

    class N1,N2,N3,N4 netflixStyle
    class U1,U2,U3,U4 uberStyle
    class I1,I2,I3,I4 instagramStyle
```

## Critical Primitive Combinations

| Combination | Why Needed | Production Example | Anti-Pattern |
|-------------|------------|--------------------|--------------|
| **P7 + P8** | Idempotency + Retry | Stripe payment retries | Retry without idempotency key |
| **P1 + P4** | Partitioning + Indexes | Instagram photo lookup | Global secondary indexes |
| **P2 + P5** | Replication + Consensus | Spanner strong consistency | Async replication only |
| **P8 + P9** | Retry + Circuit Breaker | Netflix API resilience | Infinite retries |
| **P3 + P19** | Durable Log + CDC | Kafka event streaming | Dual writes to downstream |

## Capacity Planning

| Primitive | Throughput Limit | Latency Impact | When It Breaks |
|-----------|------------------|----------------|----------------|
| **P1 Partitioning** | 20K writes/partition | None if balanced | Hot partitions, celebrity users |
| **P5 Consensus** | 10K writes/sec | +2-10ms | Network partitions, >7 nodes |
| **P11 Caching** | 50K+ ops/node | <1ms hits | Cache misses, invalidation storms |
| **P2 Replication** | Unlimited | +1-5ms/replica | Network lag, replica failure |
| **P9 Circuit Breaker** | No limit | Fail-fast | Cascading failures, no fallback |

## Implementation Checklist

| Primitive | Must Have | Must Monitor | Common Mistake |
|-----------|-----------|--------------|----------------|
| **P1 Partitioning** | Even distribution strategy | Hot partition detection | Celebrity user hotspots |
| **P5 Consensus** | Odd node count | Split-brain monitoring | Even number of nodes |
| **P11 Caching** | Invalidation strategy | Hit ratio tracking | No cache invalidation |
| **P8 Retry Logic** | Exponential backoff | Retry storm detection | No jitter, infinite retries |
| **P9 Circuit Breaker** | Fallback mechanism | Recovery time tracking | Global circuit breaker |