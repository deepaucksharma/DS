# Overview

## What is a Distributed System?

A distributed system is multiple independent computers appearing as a single coherent system.

```mermaid
graph TB
    subgraph EdgePlane["Edge Plane - CDN & Load Balancing"]
        CDN["Cloudflare CDN<br/>150 POPs globally<br/>p99: 15ms"]
        LB["AWS ALB<br/>50K RPS capacity<br/>99.99% SLA"]
    end

    subgraph ServicePlane["Service Plane - Business Logic"]
        API["API Gateway<br/>Kong Enterprise<br/>10K RPS/instance"]
        MS1["User Service<br/>Java 17, K8s<br/>p99: 50ms"]
        MS2["Order Service<br/>Go 1.21, K8s<br/>p99: 25ms"]
    end

    subgraph StatePlane["State Plane - Data Storage"]
        PG[("PostgreSQL 15<br/>Primary-Replica<br/>db.r6g.2xlarge")]
        REDIS[("Redis Cluster<br/>6 nodes, 64GB<br/>p99: 1ms")]
        S3[("AWS S3<br/>99.999999999%<br/>durability")]
    end

    subgraph ControlPlane["Control Plane - Operations"]
        MON["Datadog APM<br/>200K metrics/min<br/>real-time alerts"]
        LOG["ELK Stack<br/>10TB/day logs<br/>7-day retention"]
    end

    CDN --> LB
    LB --> API
    API --> MS1
    API --> MS2
    MS1 --> PG
    MS1 --> REDIS
    MS2 --> PG
    MS2 --> S3
    MON -.-> MS1
    MON -.-> MS2
    LOG -.-> MS1
    LOG -.-> MS2

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class CDN,LB edgeStyle
    class API,MS1,MS2 serviceStyle
    class PG,REDIS,S3 stateStyle
    class MON,LOG controlStyle
```

## Why This Framework?

This framework provides systematic production-focused guidance instead of theoretical concepts.

```mermaid
flowchart LR
    subgraph Problem["Production Problems"]
        P1["3AM Outage<br/>p99 latency 5000ms<br/>$10K/min revenue loss"]
        P2["Black Friday<br/>100x traffic spike<br/>system collapse"]
        P3["Data Corruption<br/>inconsistent state<br/>financial impact"]
    end

    subgraph Framework["Atlas Framework"]
        F1["15 Universal Laws<br/>mathematical constraints<br/>CAP, Little's, Amdahl's"]
        F2["30 Capabilities<br/>system guarantees<br/>with SLOs"]
        F3["20 Primitives<br/>building blocks<br/>with trade-offs"]
        F4["15 Patterns<br/>proven solutions<br/>with metrics"]
    end

    subgraph Solution["Production Solutions"]
        S1["Automated Design<br/>requirement → architecture<br/>in 5 minutes"]
        S2["Capacity Planning<br/>quantitative models<br/>cost optimization"]
        S3["Incident Response<br/>failure mode maps<br/>recovery procedures"]
    end

    P1 --> F1
    P2 --> F2
    P3 --> F3
    F1 --> S1
    F2 --> S2
    F3 --> S3
    F4 --> S1

    classDef problemStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef frameworkStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef solutionStyle fill:#10B981,stroke:#059669,color:#fff

    class P1,P2,P3 problemStyle
    class F1,F2,F3,F4 frameworkStyle
    class S1,S2,S3 solutionStyle
```

## The Building Blocks

```mermaid
flowchart TB
    subgraph Laws["Universal Laws (15)"]
        CAP["CAP Theorem<br/>consistency vs availability<br/>during partition"]
        LITTLE["Little's Law<br/>users = rate × latency<br/>queueing theory"]
        AMDAHL["Amdahl's Law<br/>speedup = 1/(s+p/n)<br/>parallel limits"]
    end

    subgraph Capabilities["System Capabilities (30)"]
        CONS["Consistency<br/>linearizable: bank transfers<br/>eventual: social feeds"]
        PERF["Performance<br/>p99 < 100ms: user-facing<br/>p99 < 10ms: internal"]
        AVAIL["Availability<br/>99.99%: critical systems<br/>99.9%: internal tools"]
    end

    subgraph Primitives["Building Primitives (20)"]
        P1["P1 Partitioning<br/>10M users → 100 shards<br/>consistent hashing"]
        P2["P2 Replication<br/>3 replicas → 99.99% uptime<br/>async/sync modes"]
        P5["P5 Consensus<br/>Raft: 5-node cluster<br/>majority quorum"]
    end

    subgraph Patterns["Proven Patterns (15)"]
        OUTBOX["Outbox Pattern<br/>dual write problem<br/>transaction + event"]
        SAGA["Saga Pattern<br/>distributed transaction<br/>compensation actions"]
        CQRS["CQRS Pattern<br/>read/write separation<br/>eventual consistency"]
    end

    Laws --> Capabilities
    Capabilities --> Primitives
    Primitives --> Patterns

    classDef lawStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef capStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef primStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef patternStyle fill:#10B981,stroke:#059669,color:#fff

    class CAP,LITTLE,AMDAHL lawStyle
    class CONS,PERF,AVAIL capStyle
    class P1,P2,P5 primStyle
    class OUTBOX,SAGA,CQRS patternStyle
```

| Component | Count | Purpose | Example |
|-----------|-------|---------|----------|
| **Universal Laws** | 15 | Mathematical constraints | CAP Theorem, Little's Law |
| **Capabilities** | 30 | System guarantees | Linearizable writes, p99 < 100ms |
| **Primitives** | 20 | Implementation building blocks | Consensus (Raft), Partitioning (hash) |
| **Patterns** | 15 | Proven architectural solutions | Outbox, Saga, CQRS |

## How to Use This Framework

Systematic 5-step process from requirements to validated architecture.

```mermaid
flowchart LR
    subgraph Step1["1. Requirements"]
        REQ["E-commerce Checkout<br/>10K orders/hour<br/>99.99% availability<br/>$1M/hour revenue"]
    end

    subgraph Step2["2. Capabilities"]
        CAP1["LinearizableWrite<br/>inventory consistency"]
        CAP2["DurableWrite<br/>order persistence"]
        CAP3["SubSecondRead<br/>UI responsiveness"]
    end

    subgraph Step3["3. Primitives"]
        PRIM1["P2 Replication<br/>3 replicas"]
        PRIM2["P5 Consensus<br/>Raft protocol"]
        PRIM3["P11 Caching<br/>Redis cluster"]
    end

    subgraph Step4["4. Patterns"]
        PAT["Outbox Pattern<br/>atomic DB + event<br/>dual-write solution"]
    end

    subgraph Step5["5. Validation"]
        VAL["Throughput: 15K ops/sec ✓<br/>Availability: 99.995% ✓<br/>Latency p99: 45ms ✓"]
    end

    REQ --> CAP1
    REQ --> CAP2
    REQ --> CAP3
    CAP1 --> PRIM1
    CAP2 --> PRIM2
    CAP3 --> PRIM3
    PRIM1 --> PAT
    PRIM2 --> PAT
    PRIM3 --> PAT
    PAT --> VAL

    classDef reqStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef capStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef primStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef patStyle fill:#10B981,stroke:#059669,color:#fff
    classDef valStyle fill:#9900CC,stroke:#660099,color:#fff

    class REQ reqStyle
    class CAP1,CAP2,CAP3 capStyle
    class PRIM1,PRIM2,PRIM3 primStyle
    class PAT patStyle
    class VAL valStyle
```

| Step | Input | Output | Time | Tool |
|------|-------|--------|------|------|
| **Requirements** | Business needs | Quantified SLOs | 15 min | Template |
| **Capabilities** | SLOs | System guarantees | 10 min | Mapping |
| **Primitives** | Capabilities | Building blocks | 15 min | Decision tree |
| **Patterns** | Primitives | Architecture | 20 min | Pattern matcher |
| **Validation** | Architecture | Verified design | 10 min | Quantitative models |

## Learning Path

Three tracks based on experience level and time investment.

| Path | Duration | Focus | Outcome |
|------|----------|-------|----------|
| **Beginner** | 2-4 weeks | Understand constraints | Design simple systems |
| **Intermediate** | 1-2 months | Production realities | Debug and scale systems |
| **Advanced** | 3-6 months | Automated design | Architect complex systems |

### Track Progression

| Week | Beginner | Intermediate | Advanced |
|------|----------|--------------|----------|
| **1-2** | Universal Laws | Primitives deep-dive | Decision algorithms |
| **3-4** | Capabilities overview | System patterns | Proof obligations |
| **5-8** | Micro-patterns | Production reality | API implementation |
| **9-12** | Case studies | Implementation guides | Pitfall analysis |
| **13-24** | - | Advanced patterns | Research & innovation |

## Key Principles

Production-tested principles that prevent 3AM incidents.

| Principle | Production Rule | Example | Cost of Violation |
|-----------|-----------------|---------|-------------------|
| **Design for Failure** | Every component fails | Netflix Chaos Monkey | $10M outage (AWS S3 2017) |
| **Measure Everything** | p99 latency, not average | Stripe's detailed metrics | $100M revenue loss potential |
| **Start Simple** | Boring technology wins | PostgreSQL over NoSQL | 6 months rebuilding complexity |
| **Learn from Production** | Blameless postmortems | Google's SRE culture | Repeated incidents cost 10x |

## Next Steps

Choose your path based on immediate needs and experience level.

| If you want to... | Go to... | Time needed |
|-------------------|----------|-------------|
| **Design a system in 15 minutes** | [Quick Start](quick-start.md) | 15 min |
| **Understand the mathematical foundations** | [Universal Laws](../foundation/universal-laws.md) | 2 hours |
| **Build production systems** | [Decision Engine](../patterns/decision-engine.md) | 1 day |
| **See real implementations** | [Implementation Guides](../examples/implementation.md) | 4 hours |
| **Debug production issues** | [Reality Check](../production/reality.md) | 30 min |

Distributed systems are complex by nature. This framework provides systematic navigation through that complexity.