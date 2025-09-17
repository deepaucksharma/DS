# Diagram Specifications v1.0.0
## Ultra-Detailed Requirements for 1,500+ Diagrams

### Overview

This document provides exhaustive specifications for every diagram type in the Atlas. Each specification includes:
- Exact Mermaid syntax templates
- Required nodes and edges
- Mandatory labels and annotations
- Color schemes and styling
- Size constraints and tiling rules
- Quality validation criteria

---

## Diagram Type Catalog

### FL - Flow Diagrams

**Purpose:** System-wide data and control flows

**Mermaid Template:**
```mermaid
flowchart TB
    subgraph Edge["Edge Plane #0066CC"]
        E1[Load Balancer]:::edge
        E2[API Gateway]:::edge
        E3[Rate Limiter]:::edge
    end

    subgraph Service["Service Plane #00AA00"]
        S1[Service A]:::service
        S2[Service B]:::service
        S3[Orchestrator]:::service
    end

    subgraph Stream["Stream Plane #AA00AA"]
        ST1[Event Bus]:::stream
        ST2[Stream Processor]:::stream
    end

    subgraph State["State Plane #FF8800"]
        DB1[(Primary DB)]:::state
        DB2[(Read Replica)]:::state
    end

    subgraph Control["Control Plane #CC0000"]
        C1[Config Service]:::control
        C2[Monitoring]:::control
    end

    E1 -->|"p99: 1ms"| E2
    E2 -->|"rate: 10k/s"| E3
    E3 -->|"p99: 5ms"| S1
    S1 -->|"async"| ST1
    ST1 -->|"batch: 1000"| ST2
    S1 -->|"sync"| DB1
    DB1 -.->|"replica lag: 10ms"| DB2
    C1 -.->|"config push"| S1
    S2 -->|"metrics"| C2

    classDef edge fill:#0066CC,stroke:#004499,color:#fff
    classDef service fill:#00AA00,stroke:#007700,color:#fff
    classDef stream fill:#AA00AA,stroke:#770077,color:#fff
    classDef state fill:#FF8800,stroke:#CC6600,color:#fff
    classDef control fill:#CC0000,stroke:#990000,color:#fff
```

**Requirements:**

| Element | Requirement | Example |
|---------|------------|---------|
| Node Count | L0: 80-120, L1: 40-80, L2: 20-40 | L0: 95 nodes |
| Edge Count | L0: 100-400, L1: 80-200, L2: 40-100 | L0: 250 edges |
| Subgraphs | One per plane (5 total) | Edge, Service, Stream, State, Control |
| Edge Labels | Latency, throughput, or mode | "p99: 10ms", "1000 QPS", "async" |
| Node Labels | Component name + type | "API Gateway", "Primary DB" |
| Colors | Plane-specific (see color map) | Edge=#0066CC |
| Guarantees | On critical paths | "linearizable", "exactly-once" |
| Backpressure | Marked with special edges | Dashed red lines |
| Failures | Red edges for failure paths | --> becomes --x for failures |

---

### SQ - Sequence Diagrams

**Purpose:** Temporal interactions and message flows

**Mermaid Template:**
```mermaid
sequenceDiagram
    participant C as Client
    participant LB as Load Balancer<br/>Edge Plane
    participant API as API Gateway<br/>Edge Plane
    participant S1 as Service A<br/>Service Plane
    participant DB as Database<br/>State Plane
    participant Q as Queue<br/>Stream Plane
    participant W as Worker<br/>Service Plane

    Note over C,W: Happy Path Flow - Request/Response Pattern

    C->>+LB: HTTP Request [0ms]
    LB->>+API: Route Request [1ms]
    Note over API: Rate limit check<br/>Auth validation
    API->>+S1: Process Request [5ms]

    par Synchronous Write
        S1->>+DB: Write to Primary [8ms]
        DB-->>-S1: ACK [10ms]
    and Async Event
        S1--)Q: Publish Event [6ms]
    end

    S1-->>-API: Response [15ms]
    API-->>-LB: Response [16ms]
    LB-->>-C: HTTP 200 OK [17ms]

    Note over Q,W: Async Processing
    Q->>W: Consume Event [+100ms]
    W->>DB: Update Secondary [+108ms]

    Note over C,W: Total Latency: 17ms sync, 108ms async
```

**Requirements:**

| Element | Requirement | Example |
|---------|------------|---------|
| Participants | 5-25 actors | Client, Services, DBs |
| Messages | 10-30 interactions | Requests, responses, events |
| Timing Labels | On every message | "[10ms]", "[+100ms]" |
| Parallel Blocks | For concurrent ops | par...and...end |
| Notes | For guarantees/SLOs | "p99 < 20ms" |
| Activation | Show processing time | +/- on participants |
| Loops | For retries/polling | loop 3 times...end |
| Alt Blocks | For conditionals | alt success...else failure |
| Critical Region | For atomicity | critical...end |

---

### ST - State Machine Diagrams

**Purpose:** State transitions and lifecycle management

**Mermaid Template:**
```mermaid
stateDiagram-v2
    [*] --> Pending: Initialize

    state Pending {
        [*] --> Validating
        Validating --> Scheduled: Valid
        Validating --> Failed: Invalid

        Scheduled --> Queued: Resources Available
        Queued --> Starting: Dequeued
    }

    Pending --> Running: Started

    state Running {
        [*] --> Healthy
        Healthy --> Degraded: Partial Failure<br/>SLO: 30s detection
        Degraded --> Healthy: Auto-Recovery<br/>SLO: 60s MTTR
        Degraded --> Failed: Cascade Failure

        state Healthy {
            [*] --> Serving
            Serving --> Throttling: Load > 80%
            Throttling --> Serving: Load < 60%
        }
    }

    Running --> Completed: Success
    Running --> Failed: Error/Timeout
    Running --> Cancelled: User Abort

    Failed --> Retrying: Retry Policy<br/>Max: 3 attempts
    Retrying --> Running: Backoff Complete
    Retrying --> Terminal: Max Retries

    Completed --> [*]
    Cancelled --> [*]
    Terminal --> [*]

    note right of Running
        Monitors:
        - Health checks: 10s
        - Metrics: 1s
        - Logs: Continuous
    end note

    note left of Failed
        Failure Modes:
        - Timeout: 30s
        - Error: Immediate
        - Resource: 5s
    end note
```

**Requirements:**

| Element | Requirement | Example |
|---------|------------|---------|
| States | 8-25 total states | Pending, Running, Failed |
| Nested States | For complex states | Running { Healthy, Degraded } |
| Transitions | All labeled | "User Abort", "Timeout" |
| Initial State | [*] marker | [*] --> Pending |
| Terminal States | [*] marker | Completed --> [*] |
| Timing Labels | SLOs on transitions | "SLO: 30s detection" |
| Fork/Join | For parallelism | fork --> States --> join |
| History | For state memory | Shallow/Deep history |
| Notes | For monitoring | Health checks, metrics |

---

### CO - Consistency/Causality Diagrams

**Purpose:** Happens-before relationships and consistency boundaries

**Mermaid Template:**
```mermaid
flowchart LR
    subgraph Session1["Session 1 - User A"]
        W1[Write X=1<br/>t=100]:::write
        W2[Write Y=2<br/>t=102]:::write
        R1[Read X<br/>t=104]:::read
    end

    subgraph Session2["Session 2 - User B"]
        R2[Read X<br/>t=101]:::read
        W3[Write Z=3<br/>t=103]:::write
        R3[Read Y<br/>t=105]:::read
    end

    subgraph Consistency["Consistency Boundaries"]
        L[Linearizable<br/>Zone]:::linear
        C[Causal<br/>Zone]:::causal
        E[Eventual<br/>Zone]:::eventual
    end

    W1 -.->|"happens-before"| W2
    W1 ==>|"causal"| R2
    W2 -.->|"session"| R1
    R2 -.->|"happens-before"| W3
    W3 ==>|"causal"| R3

    W1 & W2 --> L
    R2 & W3 --> C
    R1 & R3 --> E

    classDef write fill:#00CC00,stroke:#009900
    classDef read fill:#0099CC,stroke:#006699
    classDef linear fill:#FF0000,stroke:#CC0000
    classDef causal fill:#FF9900,stroke:#CC6600
    classDef eventual fill:#FFCC00,stroke:#CC9900
```

**Requirements:**

| Element | Requirement | Example |
|---------|------------|---------|
| Operations | 10-30 read/writes | Write X=1, Read Y |
| Timestamps | Logical or physical | t=100, LC=5 |
| Sessions | 2-5 concurrent | Session per user/client |
| Happens-Before | Dotted arrows | W1 -.-> W2 |
| Causal Links | Bold arrows | W1 ==> R2 |
| Boundaries | Consistency zones | Linear, Causal, Eventual |
| Conflicts | Marked clearly | Concurrent writes to X |
| Resolution | Show strategy | LWW, CRDT, Quorum |
| Guarantees | Label edges | RYW, MR, MW |

---

### ER - Entity Relationship Diagrams

**Purpose:** Data models and schema relationships

**Mermaid Template:**
```mermaid
erDiagram
    USER {
        uuid user_id PK "Partition: user_id"
        string email UK "Index: email_idx"
        string username UK "Index: username_idx"
        timestamp created_at "Sort: DESC"
        int version "Optimistic lock"
        json metadata "TTL: 30d"
    }

    ORDER {
        uuid order_id PK "Partition: region+date"
        uuid user_id FK "Reference: USER"
        string status "Index: status_idx"
        decimal total "Precision: 10,2"
        timestamp created_at "Sort: DESC"
        uuid idempotency_key UK "Dedup: 24h TTL"
    }

    ORDER_ITEM {
        uuid item_id PK "Composite: order_id+seq"
        uuid order_id FK "Cascade delete"
        uuid product_id FK "Reference: PRODUCT"
        int quantity "Check: > 0"
        decimal price "Precision: 10,2"
        int sequence "Sort: ASC"
    }

    EVENT {
        uuid event_id PK "Partition: stream+date"
        string stream "Index: stream_idx"
        int partition "Range: 0-127"
        bigint offset "Unique per partition"
        binary payload "Compression: snappy"
        timestamp timestamp "Retention: 7d"
    }

    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER ||--o{ EVENT : emits
    USER ||--o{ EVENT : triggers
```

**Requirements:**

| Element | Requirement | Example |
|---------|------------|---------|
| Entities | 5-20 tables/collections | USER, ORDER, EVENT |
| Attributes | Key fields + metadata | user_id PK, email UK |
| Relationships | All cardinalities | 1-1, 1-N, N-M |
| Keys | PK, FK, UK marked | Primary, Foreign, Unique |
| Indices | Marked in comments | "Index: email_idx" |
| Partitioning | Strategy shown | "Partition: user_id" |
| TTL | Retention policies | "TTL: 30d" |
| Constraints | Validation rules | "Check: > 0" |
| Types | Data types specified | uuid, string, decimal |

---

### MR - Multi-Region Diagrams

**Purpose:** Geographic distribution and replication

**Mermaid Template:**
```mermaid
flowchart TB
    subgraph US-EAST["US-EAST (Primary)"]
        USE_LB[Load Balancer]:::primary
        USE_APP[App Servers]:::primary
        USE_DB[(Primary DB<br/>Write Leader)]:::primary
    end

    subgraph US-WEST["US-WEST (Secondary)"]
        USW_LB[Load Balancer]:::secondary
        USW_APP[App Servers]:::secondary
        USW_DB[(Read Replica<br/>Lag: 10ms)]:::secondary
    end

    subgraph EU-WEST["EU-WEST (Secondary)"]
        EUW_LB[Load Balancer]:::secondary
        EUW_APP[App Servers]:::secondary
        EUW_DB[(Read Replica<br/>Lag: 80ms)]:::secondary
    end

    subgraph AP-SOUTH["AP-SOUTH (DR)"]
        APS_LB[Load Balancer]:::dr
        APS_APP[App Servers]:::dr
        APS_DB[(Standby DB<br/>RPO: 1min)]:::dr
    end

    USE_LB -->|"Local writes"| USE_APP
    USE_APP -->|"Sync write"| USE_DB

    USW_LB -->|"Local reads"| USW_APP
    USW_APP -->|"Read only"| USW_DB
    USE_DB -.->|"Async replication<br/>10ms lag"| USW_DB

    EUW_LB -->|"Local reads"| EUW_APP
    EUW_APP -->|"Read only"| EUW_DB
    USE_DB -.->|"Async replication<br/>80ms lag"| EUW_DB

    USE_DB ==>|"Backup stream<br/>RPO: 1min"| APS_DB

    USW_APP & EUW_APP -.->|"Forward writes"| USE_APP

    classDef primary fill:#00CC00,stroke:#009900,color:#fff
    classDef secondary fill:#0099CC,stroke:#006699,color:#fff
    classDef dr fill:#FF9900,stroke:#CC6600,color:#fff
```

**Requirements:**

| Element | Requirement | Example |
|---------|------------|---------|
| Regions | 3-8 geographic zones | US-EAST, EU-WEST, AP-SOUTH |
| Roles | Primary/Secondary/DR | Write leader, Read replica |
| Replication | Sync/async modes | Arrows with lag times |
| RPO/RTO | On DR connections | "RPO: 1min, RTO: 5min" |
| Latency | Inter-region delays | "80ms lag" |
| Failover | Paths marked | Primary → Secondary promotion |
| Consistency | Per-region guarantees | "Eventual: 80ms" |
| Traffic | Request routing | Local reads, forwarded writes |
| Capacity | Per-region limits | "10K QPS", "1M users" |

---

### BP - Backpressure Diagrams

**Purpose:** Flow control and overload management

**Mermaid Template:**
```mermaid
flowchart TB
    subgraph Admission["1. Admission Control"]
        A1[Rate Limiter<br/>10K QPS global]:::control
        A2[Tenant Limiter<br/>1K QPS/tenant]:::control
        A3[Cost Limiter<br/>$100/hour]:::control
    end

    subgraph Queue["2. Queue Management"]
        Q1[Input Queue<br/>Max: 10K<br/>Timeout: 30s]:::queue
        Q2[Priority Queue<br/>Weights: P0=50%]:::queue
        Q3[DLQ<br/>Retry: 3x]:::queue
    end

    subgraph Capacity["3. Capacity Control"]
        C1[Thread Pool<br/>Size: 100<br/>Queue: 1000]:::capacity
        C2[Connection Pool<br/>Max: 50<br/>Timeout: 5s]:::capacity
        C3[Memory Limit<br/>80% threshold]:::capacity
    end

    subgraph Timeout["4. Timeout Cascade"]
        T1[Client Timeout<br/>30s total]:::timeout
        T2[Service Timeout<br/>10s internal]:::timeout
        T3[DB Timeout<br/>5s query]:::timeout
    end

    subgraph Breaker["5. Circuit Breakers"]
        B1[Service Breaker<br/>Threshold: 50%<br/>Window: 10s]:::breaker
        B2[DB Breaker<br/>Threshold: 10 errors<br/>Cooldown: 30s]:::breaker
    end

    subgraph Shedding["6. Load Shedding"]
        S1[Random Drop<br/>>90% CPU]:::shed
        S2[Priority Drop<br/>Keep P0 only]:::shed
        S3[Brownout<br/>Disable features]:::shed
    end

    A1 --> A2 --> A3 --> Q1
    Q1 --> Q2 --> C1
    Q1 -.->|overflow| Q3
    C1 --> C2 --> C3
    C1 --> T1 --> T2 --> T3
    T2 --> B1 --> B2
    C3 -->|>80%| S1 --> S2 --> S3

    classDef control fill:#CC0000,stroke:#990000,color:#fff
    classDef queue fill:#FF9900,stroke:#CC6600,color:#fff
    classDef capacity fill:#0099CC,stroke:#006699,color:#fff
    classDef timeout fill:#9900CC,stroke:#660099,color:#fff
    classDef breaker fill:#CC0099,stroke:#990066,color:#fff
    classDef shed fill:#CCCC00,stroke:#999900
```

**Requirements:**

| Element | Requirement | Example |
|---------|------------|---------|
| Stages | 6 control levels | Admission → Shedding |
| Limits | Numeric thresholds | "10K QPS", "80% CPU" |
| Timeouts | Cascading values | 30s → 10s → 5s |
| Breakers | States and thresholds | Open/Closed/Half-open |
| Queues | Sizes and policies | FIFO, Priority, LIFO |
| Shedding | Strategies | Random, Priority, Feature |
| Metrics | Trigger points | CPU, Memory, Latency |
| Recovery | Return paths | Backoff → Retry → Success |

---

### CS - Case Study Diagrams

#### Purpose
Document real-world architectures of massively scalable systems (2020-2025) with emphasis on scale, guarantees, and failure patterns.

#### Core Diagram Set (10 Required + 5 Optional)

##### CS-L0: Global Architecture Flow
```mermaid
flowchart TB
    subgraph Edge["Edge Plane #0066CC"]
        E1["LB<br/>25M RPS"]:::edge
        E2["Rate Limiter<br/>50/s per user"]:::edge
    end

    subgraph Service["Service Plane #00AA00"]
        S1["Gateway<br/>10M conn"]:::service
        S2["Guild Shard<br/>1000 shards"]:::service
    end

    subgraph Stream["Stream Plane #AA00AA"]
        ST1["Event Bus<br/>100GB/s"]:::stream
        ST2["Fanout<br/>100k recipients"]:::stream
    end

    subgraph State["State Plane #FF8800"]
        D1["Cassandra<br/>8k nodes"]:::state
        D2["Redis<br/>2k nodes"]:::state
    end

    subgraph Control["Control Plane #CC0000"]
        C1[Config Service]:::control
        C2[Chaos Engine]:::control
    end

    E1 -->|"PerKeyOrder<br/>p99: 10ms"| S1
    S1 -->|"BoundedStaleness(2s)"| ST1
    ST1 -->|"AtLeastOnce"| D1
```

##### CS-L1-{PLANE}: Plane Zoom Diagrams (5 total)
- Edge Plane: Load balancing, rate limiting, admission control
- Service Plane: Business logic, orchestration, routing
- Stream Plane: Event processing, async workflows, fanout
- State Plane: Storage, consistency, replication
- Control Plane: Configuration, monitoring, chaos

##### CS-CO: Consistency Boundaries
```mermaid
flowchart LR
    subgraph Linearizable["Linearizable Zone"]
        L1[Config Store]
        L2[Leader Election]
    end

    subgraph Sequential["Sequential Consistency"]
        S1[User State]
        S2[Session Data]
    end

    subgraph Eventual["Eventually Consistent"]
        E1[Metrics]
        E2[Logs]
        E3[Analytics]
    end

    L1 -.->|"Consensus"| S1
    S1 -.->|"Async Replication"| E1
```

##### CS-MR: Multi-Region Strategy
```mermaid
flowchart TB
    subgraph US_WEST["US-West (Primary)"]
        USW[Write Leader]
    end

    subgraph US_EAST["US-East (Secondary)"]
        USE[Read Replica]
    end

    subgraph EU["Europe (Secondary)"]
        EUR[Read Replica]
    end

    USW -->|"Async<br/>RPO: 30s"| USE
    USW -->|"Async<br/>RPO: 30s"| EUR

    Client -->|"Write"| USW
    Client -->|"Read"| USE
```

##### CS-BP: Backpressure Ladder
```mermaid
sequenceDiagram
    participant Client
    participant Edge
    participant Service
    participant State

    Note over Edge: Rate Limit: 50/s
    Client->>Edge: Request

    alt Over Limit
        Edge-->>Client: 429 Too Many
    else Under Limit
        Edge->>Service: Forward
        Note over Service: Queue: 1000

        alt Queue Full
            Service-->>Edge: Backpressure
            Edge-->>Client: 503 Busy
        else Queue Available
            Service->>State: Query
            State-->>Service: Result
            Service-->>Client: 200 OK
        end
    end
```

##### CS-FM: Failure Modes Map
```mermaid
stateDiagram-v2
    [*] --> Normal

    Normal --> CelebrityStorm: High fanout detected
    CelebrityStorm --> PullMode: Switch strategy
    PullMode --> Normal: Storm passes

    Normal --> RegionFailure: Health check fail
    RegionFailure --> Failover: Automatic
    Failover --> Normal: Region recovers

    Normal --> CascadeOverload: Breaker trips
    CascadeOverload --> LoadShed: Drop low-pri
    LoadShed --> Normal: Load decreases
```

##### CS-SL: SLA and Latency Budgets
```mermaid
flowchart LR
    subgraph Request_Path["Request Path"]
        Client["Client<br/>Budget: 100ms"]
        Edge["Edge<br/>Used: 5ms"]
        Service["Service<br/>Used: 20ms"]
        Cache["Cache<br/>Used: 2ms"]
        DB["DB<br/>Used: 50ms"]
    end

    Client -->|"95ms remaining"| Edge
    Edge -->|"90ms remaining"| Service
    Service -->|"70ms remaining"| Cache
    Cache -->|"68ms remaining"| DB
    DB -->|"18ms remaining"| Client

    Note["Total: 77ms<br/>Buffer: 23ms"]
```

#### Optional Extended Diagrams

##### CS-DR: Drill Sequences
```mermaid
sequenceDiagram
    participant Chaos as Chaos Controller
    participant System
    participant Monitor
    participant Team

    Chaos->>System: Inject failure
    System->>Monitor: Alert triggered
    Monitor->>Team: Page sent
    Team->>System: Investigate
    Team->>System: Mitigate
    System->>Monitor: Recovery signal
    Monitor->>Chaos: Success recorded
```

##### CS-FM-{SCENARIO}: Specific Failure Scenarios
- Celebrity Storm
- Region Partition
- Cascade Overload
- DB Hotspot
- Cache Stampede

##### CS-SCALE-{TIER}: Scale Tier Variants
- Startup (< 1K users)
- Growth (1K - 100K users)
- Scale (100K - 10M users)
- Hyperscale (> 10M users)

##### CS-MR-{VARIANT}: Multi-Region Alternatives
- Active-Active
- Active-Passive
- Follow-the-Sun
- Geo-Partitioned

##### CS-MIG: Migration Path
Shows evolution from previous architecture to current.

#### Required Elements Per Diagram

| Element | L0 | L1 | CO | MR | BP | FM | SL |
|---------|----|----|----|----|----|----|----|
| Five Planes | ✓ | ✓ | | | | | |
| Scale Metrics | ✓ | ✓ | | ✓ | ✓ | | ✓ |
| Guarantees | ✓ | ✓ | ✓ | ✓ | | | |
| SLO Labels | ✓ | ✓ | | | | | ✓ |
| Failure Points | | | | ✓ | ✓ | ✓ | |
| Recovery Paths | | | | ✓ | ✓ | ✓ | |
| Latency Budget | | | | | | | ✓ |

#### Scale Annotation Requirements

| Metric | Format | Example |
|--------|--------|----------|
| RPS | "XXM RPS" | "25M RPS" |
| Connections | "XXM conn" | "10M conn" |
| Throughput | "XXX GB/s" | "100 GB/s" |
| Nodes | "XXk nodes" | "8k nodes" |
| Shards | "XXX shards" | "1000 shards" |
| Latency | "pXX: XXms" | "p99: 10ms" |
| RPO/RTO | "RPO: XXs" | "RPO: 30s" |

#### Confidence Level Indicators

| Level | Indicator | Line Style | Annotation |
|-------|-----------|------------|-------------|
| A (Definitive) | Solid | Solid | (verified) |
| B (Strong) | Dashed | Dashed | (inferred) |
| C (Partial) | Dotted | Dotted | (estimated) |

#### Source Attribution

Every diagram must include:
```yaml
metadata:
  sources:
    - url: "https://discord.com/blog/..."
      date: "2023-03-08"
      type: "blog"
  confidence: "A"
  last_verified: "2025-03-10"
  attribution: "© Discord, Inc."
```

---

## Diagram Composition Rules

### Multi-Level Detail (Progressive Disclosure)

| Level | Nodes | Edges | Purpose | Tiling |
|-------|-------|-------|---------|--------|
| L0 | 80-120 | 100-400 | Global architecture | If >120 nodes: 4 tiles |
| L1 | 40-80 | 80-200 | Per-plane detail | If >80 nodes: 2 tiles |
| L2 | 20-40 | 40-100 | Mechanism internals | Single diagram |
| L3 | 10-20 | 15-30 | Configuration detail | Single diagram |
| L4 | 5-15 | 10-20 | Specific scenarios | Single diagram |

### Cross-Diagram Linking

```yaml
links:
  from_node: "Service_A"
  from_diagram: "p-cqrs__FL__v1.0.0"
  to_node: "EventStore"
  to_diagram: "m-p3__FL__v1.0.0"
  relationship: "writes_events"
  guarantee: "exactly_once"
```

### Mandatory Labels Per Node Type

| Node Type | Required Labels | Example |
|-----------|----------------|---------|
| Service | name, plane, slo | "API Gateway, Edge, p99<10ms" |
| Database | name, type, consistency | "UserDB, MySQL, linearizable" |
| Queue | name, size, ordering | "EventQueue, 10K, FIFO" |
| Stream | name, partitions, retention | "Events, 128, 7d" |
| Cache | name, size, ttl | "SessionCache, 1GB, 1h" |

### Mandatory Labels Per Edge Type

| Edge Type | Required Labels | Example |
|-----------|----------------|---------|
| Sync | latency, throughput | "p99: 10ms, 1K QPS" |
| Async | mode, delivery | "at-least-once, batch:100" |
| Replication | lag, consistency | "10ms lag, eventual" |
| Failure | trigger, mitigation | "timeout:30s, retry:3x" |
| Backpressure | limit, action | "80% full, throttle" |

---

## Color Palette Specification

### Plane Colors (Primary)

```css
.edge    { fill: #0066CC; stroke: #004499; } /* Blue */
.service { fill: #00AA00; stroke: #007700; } /* Green */
.stream  { fill: #AA00AA; stroke: #770077; } /* Purple */
.state   { fill: #FF8800; stroke: #CC6600; } /* Orange */
.control { fill: #CC0000; stroke: #990000; } /* Red */
```

### State Colors (Status)

```css
.healthy  { fill: #00CC00; stroke: #009900; } /* Green */
.degraded { fill: #FFAA00; stroke: #CC8800; } /* Amber */
.failed   { fill: #CC0000; stroke: #990000; } /* Red */
.unknown  { fill: #999999; stroke: #666666; } /* Gray */
```

### Flow Colors (Paths)

```css
.normal       { stroke: #000000; stroke-width: 2; } /* Black */
.failure      { stroke: #CC0000; stroke-width: 2; stroke-dasharray: 5,5; } /* Red dashed */
.backpressure { stroke: #880000; stroke-width: 3; } /* Dark red thick */
.recovery     { stroke: #0088CC; stroke-width: 2; stroke-dasharray: 10,5; } /* Blue dashed */
```

### Consistency Colors (Guarantees)

```css
.linearizable { fill: #FF0000; } /* Red - Strongest */
.sequential   { fill: #FF3300; } /* Red-Orange */
.causal       { fill: #FF6600; } /* Orange */
.bounded      { fill: #FF9900; } /* Light Orange */
.eventual     { fill: #FFCC00; } /* Yellow - Weakest */
```

---

## Size and Performance Constraints

### File Size Limits

| Format | Uncompressed | Compressed | Action if Exceeded |
|--------|--------------|------------|-------------------|
| SVG | < 500KB | < 100KB | Split into tiles |
| PNG | < 2MB | < 500KB | Reduce quality to 85% |
| Source (.mmd) | < 50KB | < 10KB | Refactor into modules |

### Rendering Performance

| Metric | Target | Maximum | Action if Exceeded |
|--------|--------|---------|-------------------|
| Parse time | < 50ms | 100ms | Simplify syntax |
| Render time | < 200ms | 500ms | Reduce node count |
| Interaction | < 16ms | 33ms | Disable animations |

### Tiling Strategy

When diagrams exceed size limits:

```yaml
tiling:
  strategy: "quadrant"  # or "horizontal", "vertical"
  tiles:
    - id: "NW"
      nodes: [1-30]
      file: "diagram__FL__v1.0.0__NW.svg"
    - id: "NE"
      nodes: [31-60]
      file: "diagram__FL__v1.0.0__NE.svg"
    - id: "SW"
      nodes: [61-90]
      file: "diagram__FL__v1.0.0__SW.svg"
    - id: "SE"
      nodes: [91-120]
      file: "diagram__FL__v1.0.0__SE.svg"
  index: "diagram__FL__v1.0.0__index.html"
  navigation: "zoom_pan"  # or "tabs", "carousel"
```

---

## Accessibility Requirements

### SVG Accessibility

```xml
<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">CQRS Pattern Global Flow</title>
  <desc id="desc">
    Complete CQRS architecture showing command and query separation
    with 95 nodes across 5 planes: Edge, Service, Stream, State, and Control.
    Primary flow shows commands writing to event store and queries reading
    from materialized views with eventual consistency.
  </desc>
  <!-- Diagram content -->
</svg>
```

### Text Alternatives

| Element | Alternative | Example |
|---------|------------|---------|
| Nodes | aria-label | "API Gateway service in Edge plane" |
| Edges | title element | "Synchronous call, p99: 10ms" |
| Subgraphs | desc element | "Service plane containing business logic" |
| Colors | Pattern/texture | Stripes for degraded, dots for failed |

### Keyboard Navigation

```javascript
// Required keyboard support
{
  "Tab": "Navigate between elements",
  "Enter": "Activate/expand element",
  "Escape": "Close expanded view",
  "Arrow keys": "Pan diagram",
  "+/-": "Zoom in/out",
  "0": "Reset zoom",
  "?": "Show keyboard help"
}
```

---

## Quality Validation Checklist

### Per-Diagram Validation

- [ ] **Structure:** Correct Mermaid syntax
- [ ] **Nodes:** Within count limits (L0: 80-120)
- [ ] **Edges:** Within count limits (L0: 100-400)
- [ ] **Labels:** All mandatory labels present
- [ ] **Colors:** Correct plane/state colors
- [ ] **Size:** Under 500KB uncompressed
- [ ] **Links:** All cross-references valid
- [ ] **Accessibility:** Title and description present
- [ ] **Version:** Semver format (x.y.z)
- [ ] **ID:** Follows naming convention

### Per-Page Validation

- [ ] **Diagrams:** Expected count present (7-15)
- [ ] **Tables:** Required tables included (5+)
- [ ] **Navigation:** Breadcrumbs and links work
- [ ] **Cross-refs:** Related pages linked
- [ ] **Load time:** Under 2 seconds
- [ ] **Responsive:** Works on mobile/tablet
- [ ] **Print:** Printable version available
- [ ] **Search:** Indexed in search
- [ ] **Analytics:** Tracking enabled
- [ ] **Errors:** No console errors

---

## Template Examples

### Flow Diagram Template (flowchart.njk)

```nunjucks
flowchart {{ direction }}
{% for plane in planes %}
    subgraph {{ plane.name }}["{{ plane.label }} #{{ plane.color }}"]
    {% for node in plane.nodes %}
        {{ node.id }}[{{ node.label }}]:::{{ plane.class }}
    {% endfor %}
    end
{% endfor %}

{% for edge in edges %}
    {{ edge.from }} {{ edge.type }}|"{{ edge.label }}"| {{ edge.to }}
{% endfor %}

{% for classdef in classdefs %}
    classDef {{ classdef.name }} {{ classdef.style }}
{% endfor %}
```

### Data Input (YAML)

```yaml
diagram:
  type: "FL"
  version: "1.0.0"
  direction: "TB"

planes:
  - name: "Edge"
    label: "Edge Plane"
    color: "0066CC"
    class: "edge"
    nodes:
      - id: "E1"
        label: "Load Balancer"
      - id: "E2"
        label: "API Gateway"

edges:
  - from: "E1"
    to: "E2"
    type: "-->"
    label: "p99: 1ms"

classdefs:
  - name: "edge"
    style: "fill:#0066CC,stroke:#004499,color:#fff"
```

---

*Version: 1.1.0 | Document 02 of 16 | Last Updated: 2025-03-10*