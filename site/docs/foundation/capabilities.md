# Layer 1: The 30 Capabilities

Capabilities define what guarantees a distributed system provides. Netflix needs LinearizableWrite for billing, Uber needs EventualConsistency for ride matching, Discord needs SubMillisecondRead for real-time chat.

## Capability Categories

```mermaid
graph TB
    subgraph Consistency["Consistency Guarantees"]
        LW[LinearizableWrite]
        ST[SerializableTransaction]
        RYW[ReadYourWrites]
        MR[MonotonicReads]
        BS[BoundedStaleness]
        EC[EventualConsistency]
    end

    subgraph Order["Ordering Guarantees"]
        PKO[PerKeyOrder]
        CO[CausalOrder]
        TO[TotalOrder]
    end

    subgraph Durability["Durability Guarantees"]
        DW[DurableWrite]
        EOE[ExactlyOnceEffect]
        ALOD[AtLeastOnceDelivery]
        AMOD[AtMostOnceDelivery]
    end

    subgraph Performance["Performance Guarantees"]
        SMR[SubMillisecondRead]
        PT[PredictableTail]
        ES[ElasticScale]
        CT[ConstantTime]
    end

    subgraph Availability["Availability Guarantees"]
        HA[HighAvailability]
        FT[FaultTolerance]
        GD[GracefulDegradation]
    end

    %% Apply colors
    classDef consistencyStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef orderStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef durabilityStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef performanceStyle fill:#CC0000,stroke:#990000,color:#fff

    class LW,ST,RYW,MR,BS,EC consistencyStyle
    class PKO,CO,TO orderStyle
    class DW,EOE,ALOD,AMOD durabilityStyle
    class SMR,PT,ES,CT performanceStyle
```

## Capability Trade-offs

```mermaid
graph TB
    subgraph CAP["CAP Theorem Trade-offs"]
        CP["Consistency + Partition Tolerance<br/>Banks, Financial Systems"]
        AP["Availability + Partition Tolerance<br/>Social Media, Gaming"]
        CA["Consistency + Availability<br/>Single Datacenter Only"]
    end

    subgraph PACELC["PACELC Extension"]
        PC["Partition: Consistency<br/>Else: Consistency<br/>Example: Spanner"]
        PA["Partition: Availability<br/>Else: Availability<br/>Example: Cassandra"]
        PL["Partition: Availability<br/>Else: Latency<br/>Example: DynamoDB"]
    end

    CP --> PC
    AP --> PA
    AP --> PL

    %% Apply colors
    classDef strongStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef weakStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef balanceStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class CP,PC strongStyle
    class AP,PA weakStyle
    class CA,PL balanceStyle
```

## Production Usage Patterns

```mermaid
graph LR
    subgraph Financial["Financial Systems"]
        F1[LinearizableWrite]
        F2[SerializableTransaction]
        F3[DurableWrite]
        F4[FullAuditTrail]
    end

    subgraph Social["Social Media"]
        S1[EventualConsistency]
        S2[ElasticScale]
        S3[HighAvailability]
        S4[BoundedStaleness]
    end

    subgraph Gaming["Real-time Gaming"]
        G1[SubMillisecondRead]
        G2[PredictableTail]
        G3[ElasticScale]
        G4[PerKeyOrder]
    end

    subgraph Analytics["Big Data Analytics"]
        A1[HorizontalScale]
        A2[ElasticCapacity]
        A3[FullAuditTrail]
        A4[EventualConsistency]
    end

    %% Real examples
    Financial --> |Stripe, PayPal| Money[Payment Processing]
    Social --> |Instagram, TikTok| Feed[Social Feeds]
    Gaming --> |Discord, Riot| Realtime[Real-time Systems]
    Analytics --> |Netflix, Uber| Data[Data Platforms]

    %% Apply colors
    classDef financialStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef socialStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef gamingStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef analyticsStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class F1,F2,F3,F4 financialStyle
    class S1,S2,S3,S4 socialStyle
    class G1,G2,G3,G4 gamingStyle
    class A1,A2,A3,A4 analyticsStyle
```

## Real-World Examples

| System | Primary Capabilities | Why These Matter |
|--------|---------------------|------------------|
| **Stripe** | LinearizableWrite, DurableWrite | Money transfers must be atomic and never lost |
| **Instagram** | EventualConsistency, ElasticScale | Likes/comments can be eventually consistent |
| **Discord** | SubMillisecondRead, PerKeyOrder | Chat messages need instant delivery in order |
| **Uber** | BoundedStaleness, HighAvailability | Ride location can be 5s stale but must be available |
| **Netflix** | ElasticScale, GracefulDegradation | Must handle traffic spikes, degrade video quality gracefully |
| **Coinbase** | SerializableTransaction, FullAuditTrail | Crypto trades need ACID properties and complete audit |

## Measurement in Production

| Capability | How to Measure | Alert Threshold | Production Impact |
|------------|----------------|-----------------|-------------------|
| **LinearizableWrite** | Jepsen continuous testing | Any violation | Data corruption, lost money |
| **SubMillisecondRead** | P99 latency histograms | >1ms for 5min | User experience degradation |
| **HighAvailability** | Success rate monitoring | <99.9% for 1min | User-facing outages |
| **BoundedStaleness** | Data age tracking | >SLO for 5min | Stale data decisions |
| **ElasticScale** | Throughput vs load curve | Non-linear scaling | Resource waste, bottlenecks |