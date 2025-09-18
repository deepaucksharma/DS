# Layer 3: The 15 Proven Micro-Patterns

Micro-patterns combine 2-4 primitives to solve specific distributed systems problems. Each pattern has been battle-tested in production at Netflix, Uber, Amazon, and other hyperscale companies.

| **Pattern** | **Primitives** | **Problem Solved** | **Guarantees** | **Implementation** | **Proof** |
|---|---|---|---|---|---|
| **Outbox** | P3+P7+P19 | Dual write problem | ExactlyOnceToStream | Same DB transaction writes outbox table | CDC events match DB state |
| **Saga** | P3+P7+P8 | Distributed transaction | EventualConsistency | Forward recovery + compensations | All paths reach consistent state |
| **Escrow** | P1+P5+P13 | Inventory contention | NoOverselling | Pessimistic reservation with timeout | Invariant: sum ≤ total |
| **Event Sourcing** | P3+P14+P7 | Audit + time travel | CompleteHistory | Events as source of truth | Rebuild from events = current |
| **CQRS** | P19+P3+P11 | Read/write separation | OptimizedModels | Write model + read projections | Projection lag < SLO |
| **Hedged Request** | P8+P11 | Tail latency | PredictableTail | Send 2nd request at P95 | P99 reduced, load <2x |
| **Sidecar** | P9+P8+P10 | Cross-cutting concerns | Standardization | Proxy container | Overhead <20ms |
| **Leader-Follower** | P5+P2 | Single writer | Linearizability | Election + replication | Split-brain prevented |
| **Scatter-Gather** | P1+P4+P8 | Parallel query | Completeness | Fan-out + aggregate | All shards respond |
| **Write-Through** | P11+P14 | Cache consistency | StrongConsistency | Write to cache+DB | Cache never stale |
| **Read Repair** | P2+P6 | Eventual consistency | ConvergentRepair | Read from all, repair differences | Divergence detected+fixed |
| **Checkpoint** | P3+P14 | Recovery speed | FastRecovery | Periodic snapshots + incremental | Recovery <1min |
| **Bulkhead** | P10+P9 | Fault isolation | NoContagion | Separate resources per tenant | Isolation verified |
| **Batch** | P3+P7 | Efficiency | HighThroughput | Group operations | 10x throughput gain |
| **Shadow** | P20+P11 | Safe testing | RiskFreeValidation | Duplicate traffic to new version | No production impact |

## Detailed Pattern Analysis

### Outbox Pattern (P3+P7+P19)

The Outbox pattern solves the dual-write problem by using a single database transaction to update business data and publish events atomically.

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane]
        API[Order API<br/>p99: 50ms<br/>10K RPS]
    end

    subgraph ServicePlane[Service Plane]
        ORDER[Order Service<br/>Java 17<br/>Business Logic]
        CDC[CDC Processor<br/>Debezium<br/>Change Capture]
    end

    subgraph StatePlane[State Plane]
        DB[(PostgreSQL<br/>Orders + Outbox<br/>ACID transactions)]
        STREAM[(Kafka<br/>Order Events<br/>Exactly-once)]
        DLQ[(Dead Letter Queue<br/>Failed Events<br/>Retry logic)]
    end

    subgraph ControlPlane[Control Plane]
        MON[Monitoring<br/>Lag tracking<br/>Failure alerts]
    end

    %% Normal flow
    API --> ORDER
    ORDER --> DB
    DB --> CDC
    CDC --> STREAM

    %% Failure scenarios
    CDC -.->|Processing failure| DLQ
    STREAM -.->|Downstream failure| DLQ
    DB -.->|Transaction rollback| ORDER

    %% Monitoring
    CDC --> MON
    STREAM --> MON
    DLQ --> MON

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class API edgeStyle
    class ORDER,CDC serviceStyle
    class DB,STREAM,DLQ stateStyle
    class MON controlStyle
```

## Outbox Pattern Implementation

| Component | Purpose | Configuration | Failure Mode | Recovery |
|-----------|---------|---------------|--------------|----------|
| Business Table | Store order data | PostgreSQL, ACID | Transaction rollback | Retry from client |
| Outbox Table | Event staging | Same DB, event_id PK | Constraint violation | Idempotent retry |
| CDC Process | Event publishing | Debezium connector | Processing lag | Restart with offset |
| Kafka Topic | Event distribution | 3 partitions, RF=3 | Leader failure | Auto failover |
| Dead Letter Queue | Failed events | SQS, 14-day retention | Message loss | Manual replay |

### Saga Pattern (P3+P7+P8)

The Saga pattern manages distributed transactions through forward recovery and compensating actions, ensuring eventual consistency across services.

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane]
        CLIENT[Client Request<br/>Order Placement<br/>p99: 5s timeout]
    end

    subgraph ServicePlane[Service Plane]
        ORCH[Saga Orchestrator<br/>State Machine<br/>Durable Storage]
        PAY[Payment Service<br/>Stripe Integration<br/>Idempotent]
        INV[Inventory Service<br/>Stock Management<br/>Pessimistic Lock]
        SHIP[Shipping Service<br/>Fulfillment API<br/>External Partner]
    end

    subgraph StatePlane[State Plane]
        SAGA_DB[(Saga State DB<br/>MongoDB<br/>Execution Log)]
        EVENT_LOG[(Event Stream<br/>Kafka<br/>Audit Trail)]
        COMP_QUEUE[(Compensation Queue<br/>SQS<br/>Failed Steps)]
    end

    subgraph ControlPlane[Control Plane]
        MON[Saga Monitor<br/>Stuck Detection<br/>SLA Tracking]
    end

    %% Normal flow
    CLIENT --> ORCH
    ORCH --> PAY
    ORCH --> INV
    ORCH --> SHIP

    %% State management
    ORCH --> SAGA_DB
    ORCH --> EVENT_LOG

    %% Failure compensation
    PAY -.->|Timeout/Failure| COMP_QUEUE
    INV -.->|Insufficient Stock| COMP_QUEUE
    SHIP -.->|Delivery Error| COMP_QUEUE
    COMP_QUEUE -.->|Compensate| PAY
    COMP_QUEUE -.->|Compensate| INV

    %% Monitoring
    ORCH --> MON
    COMP_QUEUE --> MON

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class CLIENT edgeStyle
    class ORCH,PAY,INV,SHIP serviceStyle
    class SAGA_DB,EVENT_LOG,COMP_QUEUE stateStyle
    class MON controlStyle
```

## Saga Implementation Components

| Step | Forward Action | Compensation | Timeout | Idempotency | Monitoring |
|------|----------------|--------------|---------|-------------|------------|
| Payment | Charge credit card | Refund amount | 30s | Payment ID | Transaction status |
| Inventory | Reserve items | Release reservation | 15s | Reservation ID | Stock levels |
| Shipping | Create shipment | Cancel order | 60s | Tracking number | Delivery status |
| Notification | Send confirmation | Send cancellation | 5s | Message ID | Delivery receipt |

## Saga State Transitions

| State | Next Action | Failure Response | Timeout | Retry Policy |
|-------|-------------|------------------|---------|--------------|
| STARTED | Charge payment | COMPENSATING | 30s | Exponential backoff |
| PAYMENT_OK | Reserve inventory | COMPENSATING | 15s | 3 retries max |
| INVENTORY_OK | Create shipment | COMPENSATING | 60s | 2 retries max |
| SHIPPING_OK | Send notification | COMPLETED | 5s | 1 retry only |
| COMPENSATING | Run compensation | FAILED | 120s | Manual intervention |

### Escrow Pattern (P1+P5+P13)

The Escrow pattern handles high-contention resources through sharding, distributed locking, and time-based reservations.

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane]
        LB[Load Balancer<br/>Consistent Hashing<br/>Route by item_id]
    end

    subgraph ServicePlane[Service Plane]
        INV1[Inventory Shard 1<br/>Items 0-333<br/>Distributed Lock]
        INV2[Inventory Shard 2<br/>Items 334-666<br/>Distributed Lock]
        INV3[Inventory Shard 3<br/>Items 667-999<br/>Distributed Lock]
    end

    subgraph StatePlane[State Plane]
        DB1[(PostgreSQL 1<br/>Inventory + Escrow<br/>ACID guarantees)]
        DB2[(PostgreSQL 2<br/>Inventory + Escrow<br/>ACID guarantees)]
        DB3[(PostgreSQL 3<br/>Inventory + Escrow<br/>ACID guarantees)]
        LOCK_MGR[(Consensus Group<br/>etcd cluster<br/>Distributed locks)]
    end

    subgraph ControlPlane[Control Plane]
        TTL[TTL Manager<br/>Cleanup expired<br/>reservations]
        MON[Lock Monitor<br/>Contention alerts<br/>Performance SLA]
    end

    %% Request routing
    LB -->|hash(item_id) % 3| INV1
    LB -->|hash(item_id) % 3| INV2
    LB -->|hash(item_id) % 3| INV3

    %% Storage
    INV1 --> DB1
    INV2 --> DB2
    INV3 --> DB3

    %% Distributed locking
    INV1 --> LOCK_MGR
    INV2 --> LOCK_MGR
    INV3 --> LOCK_MGR

    %% Management
    DB1 --> TTL
    DB2 --> TTL
    DB3 --> TTL
    LOCK_MGR --> MON

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class LB edgeStyle
    class INV1,INV2,INV3 serviceStyle
    class DB1,DB2,DB3,LOCK_MGR stateStyle
    class TTL,MON controlStyle
```

## Escrow Implementation

| Component | Purpose | Configuration | Invariants | Failure Recovery |
|-----------|---------|---------------|------------|------------------|
| Shard Router | Distribute load | Consistent hashing | Even distribution | Failover to replica |
| Distributed Lock | Prevent races | 10s timeout, consensus | Single writer | Lock timeout release |
| Reservation Table | Temporary hold | TTL 300s, item_id index | reserved + available ≤ total | TTL expiration |
| Inventory Table | Current stock | ACID transactions | No negative values | Rollback on constraint |
| Cleanup Process | Expire old reservations | Run every 60s | Release expired locks | Manual intervention |

### CQRS Pattern (P19+P3+P11)

CQRS separates read and write models to optimize each for their specific workload characteristics and scaling requirements.

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane]
        WRITE_API[Write API<br/>Orders/Commands<br/>p99: 100ms]
        READ_API[Read API<br/>Queries/GraphQL<br/>p99: 10ms]
    end

    subgraph ServicePlane[Service Plane]
        COMMAND[Command Handler<br/>Business Rules<br/>Validation]
        PROJECTION[Projection Builder<br/>Event Processing<br/>Multiple views]
        QUERY[Query Handler<br/>Read Optimization<br/>Caching]
    end

    subgraph StatePlane[State Plane]
        WRITE_DB[(Write Store<br/>PostgreSQL<br/>Normalized, ACID)]
        EVENT_STREAM[(Event Stream<br/>Kafka<br/>Change events)]
        READ_CACHE[(Read Cache<br/>Redis<br/>Query optimization)]
        READ_DB[(Read Store<br/>Elasticsearch<br/>Denormalized)]
    end

    subgraph ControlPlane[Control Plane]
        LAG_MON[Lag Monitor<br/>Projection delay<br/>SLA tracking]
        REBUILD[Rebuild Service<br/>Projection recovery<br/>Event replay]
    end

    %% Write path
    WRITE_API --> COMMAND
    COMMAND --> WRITE_DB
    WRITE_DB --> EVENT_STREAM

    %% Read path
    READ_API --> QUERY
    QUERY --> READ_CACHE
    QUERY --> READ_DB

    %% Event processing
    EVENT_STREAM --> PROJECTION
    PROJECTION --> READ_DB
    PROJECTION --> READ_CACHE

    %% Fallback path
    QUERY -.->|Cache miss + critical| WRITE_DB

    %% Management
    EVENT_STREAM --> LAG_MON
    PROJECTION --> LAG_MON
    LAG_MON --> REBUILD
    REBUILD --> PROJECTION

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class WRITE_API,READ_API edgeStyle
    class COMMAND,PROJECTION,QUERY serviceStyle
    class WRITE_DB,EVENT_STREAM,READ_CACHE,READ_DB stateStyle
    class LAG_MON,REBUILD controlStyle
```

## CQRS Implementation Matrix

| Aspect | Write Side | Read Side | Event Stream | Cache Layer |
|--------|------------|-----------|--------------|-------------|
| Purpose | Business logic | Query optimization | State sync | Performance |
| Technology | PostgreSQL | Elasticsearch | Kafka | Redis |
| Consistency | Strong (ACID) | Eventual | At-least-once | TTL-based |
| Scaling | Vertical | Horizontal | Partition-based | Memory-bound |
| Latency | 50-100ms | 1-10ms | 100-500ms lag | Sub-millisecond |
| Failure Mode | Transaction rollback | Stale data served | Event replay | Cache miss fallback |

### Request-Response Pattern (P1+P8+P9+P12)

The Request-Response pattern provides reliable synchronous communication with fault tolerance, load distribution, and performance optimization.

```mermaid
graph LR
    subgraph EdgePlane[Edge Plane]
        CLIENT[Client<br/>Timeout: 30s<br/>Retry: 3x]
        LB[Load Balancer<br/>Health checks<br/>Round-robin]
    end

    subgraph ServicePlane[Service Plane]
        CB[Circuit Breaker<br/>Failure threshold: 50%<br/>Recovery: 30s]
        SERVER1[Server Instance 1<br/>Healthy<br/>p99: 50ms]
        SERVER2[Server Instance 2<br/>Healthy<br/>p99: 45ms]
        SERVER3[Server Instance 3<br/>Degraded<br/>p99: 200ms]
    end

    subgraph StatePlane[State Plane]
        CACHE[(Cache<br/>Redis<br/>Hit ratio: 85%)]
        DB[(Database<br/>PostgreSQL<br/>Connection pool)]
    end

    subgraph ControlPlane[Control Plane]
        HEALTH[Health Monitor<br/>Endpoint checks<br/>Auto-scaling]
        METRICS[Metrics<br/>Latency tracking<br/>Error rates]
    end

    %% Request flow
    CLIENT --> LB
    LB --> CB
    CB --> SERVER1
    CB --> SERVER2
    CB -.->|Circuit open| SERVER3

    %% Data access
    SERVER1 --> CACHE
    SERVER2 --> CACHE
    SERVER3 --> CACHE
    CACHE -.->|Miss| DB
    SERVER1 -.->|Cache bypass| DB

    %% Monitoring
    LB --> HEALTH
    CB --> METRICS
    SERVER1 --> METRICS
    SERVER2 --> METRICS
    SERVER3 --> HEALTH

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class CLIENT,LB edgeStyle
    class CB,SERVER1,SERVER2,SERVER3 serviceStyle
    class CACHE,DB stateStyle
    class HEALTH,METRICS controlStyle
```

## Request-Response Scale Evolution

| Scale Stage | Architecture | Throughput | Latency p99 | Monthly Cost | Complexity |
|-------------|--------------|------------|-------------|--------------|------------|
| Startup | Direct connection | 100 RPS | 100ms | $500 | Low |
| Growth | Load balancer + circuit breaker | 1K RPS | 50ms | $2K | Medium |
| Scale | Multi-region + auto-scaling | 10K RPS | 20ms | $10K | High |
| Hyperscale | Global distribution + edge | 100K RPS | 10ms | $50K | Very High |

### Streaming Pattern (P3+P7+P19)

The Streaming pattern processes continuous data streams with guaranteed ordering, fault tolerance, and exactly-once semantics.

```mermaid
graph LR
    subgraph EdgePlane[Edge Plane]
        PRODUCER[Event Producers<br/>Multiple sources<br/>1M events/sec]
    end

    subgraph ServicePlane[Service Plane]
        PROCESSOR1[Stream Processor 1<br/>Consumer Group A<br/>Stateful processing]
        PROCESSOR2[Stream Processor 2<br/>Consumer Group B<br/>Analytics pipeline]
    end

    subgraph StatePlane[State Plane]
        KAFKA[(Kafka Cluster<br/>3 partitions<br/>Replication: 3)]
        STATE_STORE[(RocksDB<br/>Local state<br/>Changelog backup)]
        SINK[(Output Sink<br/>Elasticsearch<br/>Time series)]
    end

    subgraph ControlPlane[Control Plane]
        LAG_MON[Lag Monitor<br/>Consumer offset<br/>Processing delay]
        REBALANCE[Rebalancer<br/>Partition assignment<br/>Failure detection]
    end

    %% Data flow
    PRODUCER --> KAFKA
    KAFKA --> PROCESSOR1
    KAFKA --> PROCESSOR2

    %% State management
    PROCESSOR1 --> STATE_STORE
    PROCESSOR2 --> SINK

    %% Failure handling
    PROCESSOR1 -.->|Failure| REBALANCE
    PROCESSOR2 -.->|Failure| REBALANCE
    REBALANCE -.->|Reassign| PROCESSOR1

    %% Monitoring
    KAFKA --> LAG_MON
    PROCESSOR1 --> LAG_MON
    PROCESSOR2 --> LAG_MON

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class PRODUCER edgeStyle
    class PROCESSOR1,PROCESSOR2 serviceStyle
    class KAFKA,STATE_STORE,SINK stateStyle
    class LAG_MON,REBALANCE controlStyle
```

## Streaming Implementation

| Component | Purpose | Guarantees | Failure Mode | Recovery |
|-----------|---------|------------|--------------|----------|
| Kafka Partitions | Ordered event log | Per-partition ordering | Leader failure | Follower promotion |
| Consumer Groups | Load distribution | At-least-once delivery | Consumer crash | Partition rebalance |
| State Stores | Stateful processing | Local consistency | Disk failure | Changelog replay |
| Offset Management | Progress tracking | No message loss | Coordinator failure | Offset reset |
| Dead Letter Topic | Error handling | Poison message isolation | Processing failure | Manual replay |

### Event Sourcing Pattern (P3+P14+P7)

Event Sourcing stores all state changes as immutable events, enabling complete audit trails, time travel, and deterministic replay.

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane]
        API[Command API<br/>Business operations<br/>Validation]
    end

    subgraph ServicePlane[Service Plane]
        AGGREGATE[Aggregate Root<br/>Business logic<br/>Event generation]
        PROJECTOR[Event Projector<br/>View generation<br/>Real-time updates]
        SNAPSHOTTER[Snapshot Service<br/>Performance optimization<br/>Periodic saves]
    end

    subgraph StatePlane[State Plane]
        EVENT_STORE[(Event Store<br/>Kafka/EventStore<br/>Immutable log)]
        SNAPSHOT_STORE[(Snapshot Store<br/>S3/MongoDB<br/>Point-in-time state)]
        VIEW_STORE[(View Store<br/>PostgreSQL<br/>Query optimization)]
    end

    subgraph ControlPlane[Control Plane]
        REPLAY[Replay Service<br/>Event rebuilding<br/>Migration support]
        ARCHIVE[Archive Manager<br/>Old event cleanup<br/>Compliance]
    end

    %% Command flow
    API --> AGGREGATE
    AGGREGATE --> EVENT_STORE

    %% Event processing
    EVENT_STORE --> PROJECTOR
    PROJECTOR --> VIEW_STORE

    %% Snapshots
    AGGREGATE --> SNAPSHOTTER
    SNAPSHOTTER --> SNAPSHOT_STORE
    SNAPSHOT_STORE -.->|Load state| AGGREGATE

    %% Management
    EVENT_STORE --> REPLAY
    EVENT_STORE --> ARCHIVE
    REPLAY --> VIEW_STORE

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class API edgeStyle
    class AGGREGATE,PROJECTOR,SNAPSHOTTER serviceStyle
    class EVENT_STORE,SNAPSHOT_STORE,VIEW_STORE stateStyle
    class REPLAY,ARCHIVE controlStyle
```

## Event Sourcing Components

| Component | Purpose | Storage | Performance | Failure Recovery |
|-----------|---------|---------|-------------|------------------|
| Event Store | Immutable event log | Kafka topics | 100K events/sec | Partition replication |
| Snapshots | Performance optimization | S3/MongoDB | 1000 snapshots/sec | Snapshot rebuilding |
| Projections | Query-optimized views | PostgreSQL/ES | 10K queries/sec | Event replay |
| Command Handler | Business logic | Stateless | 50K commands/sec | Retry with idempotency |
| Event Handler | View updates | Stateless | 100K events/sec | Dead letter queue |

### Fan-out Pattern (P1+P4+P8)

```mermaid
graph LR
    subgraph EdgePlane[Edge Plane]
        REQUEST[Single Request<br/>Fan-out coordinator<br/>Timeout: 30s]
    end

    subgraph ServicePlane[Service Plane]
        SERVICE1[Service A<br/>Processing time: 10ms<br/>Success rate: 99%]
        SERVICE2[Service B<br/>Processing time: 15ms<br/>Success rate: 95%]
        SERVICE3[Service C<br/>Processing time: 20ms<br/>Success rate: 98%]
        AGGREGATOR[Result Aggregator<br/>Partial results OK<br/>Timeout handling]
    end

    subgraph StatePlane[State Plane]
        RESULTS[(Aggregated Results<br/>JSON merge<br/>Failure metadata)]
    end

    %% Fan-out
    REQUEST --> SERVICE1
    REQUEST --> SERVICE2
    REQUEST --> SERVICE3

    %% Gather
    SERVICE1 --> AGGREGATOR
    SERVICE2 --> AGGREGATOR
    SERVICE3 -.->|Timeout| AGGREGATOR
    AGGREGATOR --> RESULTS

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class REQUEST edgeStyle
    class SERVICE1,SERVICE2,SERVICE3,AGGREGATOR serviceStyle
    class RESULTS stateStyle
```

| Component | Timeout | Success Rate | Failure Handling | Aggregation Strategy |
|-----------|---------|--------------|------------------|---------------------|
| Service A | 30s | 99% | Return partial | Include in result |
| Service B | 30s | 95% | Log and continue | Include in result |
| Service C | 30s | 98% | Fallback data | Include fallback |
| Aggregator | 35s total | Depends on services | Best-effort merge | JSON combination |

### Analytics Pattern (P4+P5+P10+P12)

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane]
        QUERY_API[Analytics API<br/>SQL interface<br/>Query optimization]
    end

    subgraph ServicePlane[Service Plane]
        QUERY_ENGINE[Query Engine<br/>Distributed processing<br/>Columnar format]
        ETL[ETL Processor<br/>Data transformation<br/>Schema evolution]
    end

    subgraph StatePlane[State Plane]
        DWH[(Data Warehouse<br/>Columnar storage<br/>Parquet files)]
        STAGING[(Staging Area<br/>Raw data buffer<br/>Temporary storage)]
        METADATA[(Metadata Store<br/>Schema registry<br/>Lineage tracking)]
    end

    subgraph ControlPlane[Control Plane]
        WORKLOAD[Workload Manager<br/>Resource allocation<br/>Query prioritization]
        SCHEDULER[Job Scheduler<br/>ETL orchestration<br/>Dependency management]
    end

    %% Query flow
    QUERY_API --> QUERY_ENGINE
    QUERY_ENGINE --> DWH
    QUERY_ENGINE --> METADATA

    %% ETL flow
    STAGING --> ETL
    ETL --> DWH
    ETL --> METADATA

    %% Management
    QUERY_ENGINE --> WORKLOAD
    ETL --> SCHEDULER

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class QUERY_API edgeStyle
    class QUERY_ENGINE,ETL serviceStyle
    class DWH,STAGING,METADATA stateStyle
    class WORKLOAD,SCHEDULER controlStyle
```

## Analytics Pattern Variants

| Variant | Latency | Throughput | Consistency | Use Case | Technology |
|---------|---------|------------|-------------|----------|------------|
| Real-Time | <1s | 10K queries/sec | Near real-time | Dashboards | Apache Druid |
| Batch | Hours | 1M records/sec | Eventually consistent | Reports | Apache Spark |
| Hybrid (Lambda) | 1s-1min | 100K queries/sec | Configurable | Mixed workload | Spark + Druid |
| Streaming | <100ms | 1K queries/sec | Event-time | Live monitoring | Apache Flink |

### Async Task Pattern (P7+P16+P8)

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane]
        PRODUCER[Task Producer<br/>Job submission<br/>Priority queuing]
    end

    subgraph ServicePlane[Service Plane]
        WORKER1[Worker 1<br/>Batch size: 10<br/>Max retries: 3]
        WORKER2[Worker 2<br/>Batch size: 10<br/>Max retries: 3]
        WORKER3[Worker 3<br/>Batch size: 10<br/>Max retries: 3]
    end

    subgraph StatePlane[State Plane]
        TASK_QUEUE[(Task Queue<br/>SQS/RabbitMQ<br/>FIFO with priority)]
        DLQ[(Dead Letter Queue<br/>Failed tasks<br/>Manual retry)]
        RESULT_STORE[(Result Store<br/>Task outcomes<br/>Status tracking)]
    end

    subgraph ControlPlane[Control Plane]
        SCHEDULER[Task Scheduler<br/>Worker scaling<br/>Load balancing]
        MONITOR[Task Monitor<br/>Progress tracking<br/>SLA alerts]
    end

    %% Task flow
    PRODUCER --> TASK_QUEUE
    TASK_QUEUE --> WORKER1
    TASK_QUEUE --> WORKER2
    TASK_QUEUE --> WORKER3

    %% Results and failures
    WORKER1 --> RESULT_STORE
    WORKER2 --> RESULT_STORE
    WORKER3 --> RESULT_STORE
    WORKER1 -.->|Max retries| DLQ
    WORKER2 -.->|Max retries| DLQ
    WORKER3 -.->|Max retries| DLQ

    %% Management
    TASK_QUEUE --> SCHEDULER
    RESULT_STORE --> MONITOR
    DLQ --> MONITOR

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class PRODUCER edgeStyle
    class WORKER1,WORKER2,WORKER3 serviceStyle
    class TASK_QUEUE,DLQ,RESULT_STORE stateStyle
    class SCHEDULER,MONITOR controlStyle
```

| Task Type | Processing Time | Retry Strategy | Batch Size | Failure Rate | Recovery |
|-----------|-----------------|----------------|------------|--------------|----------|
| Email Send | 100ms | 3 retries, exp backoff | 50 | 1% | DLQ replay |
| Image Resize | 2s | 2 retries, linear | 10 | 5% | Manual retry |
| Data Export | 30s | 1 retry only | 1 | 10% | Alert ops team |
| Report Generation | 5min | No retries | 1 | 15% | Customer notification |

### Graph Pattern (P1+P18+P11)

**Problem**: How to efficiently query and traverse graph data structures?

**Solution**:
```python
class GraphQueryEngine:
    def __init__(self, graph_store, cache):
        self.store = graph_store
        self.cache = cache

    async def traverse_graph(self, start_node, traversal_pattern):
        # Check cache first
        cache_key = f"traversal:{start_node}:{hash(traversal_pattern)}"
        if cached_result := await self.cache.get(cache_key):
            return cached_result

        # Partition-aware traversal
        visited = set()
        results = []
        queue = deque([start_node])

        while queue:
            node = queue.popleft()
            if node in visited:
                continue

            visited.add(node)

            # Load node data with index optimization
            node_data = await self.store.get_node_with_edges(node)
            results.append(node_data)

            # Add neighbors to queue based on pattern
            for neighbor in self.apply_pattern(node_data, traversal_pattern):
                queue.append(neighbor)

        # Cache results for future queries
        await self.cache.set(cache_key, results, ttl=300)
        return results
```

**Guarantees**:
- Index-optimized queries
- Distributed traversal capability
- Cached performance

### Ledger Pattern (P3+P5+P13)

**Problem**: How to implement immutable transaction ledger with strong consistency?

**Solution**:
```python
class DistributedLedger:
    def __init__(self, consensus_group):
        self.consensus = consensus_group
        self.lock_manager = DistributedLockManager()
        self.log = ImmutableLog()

    async def record_transaction(self, transaction):
        # Acquire locks for all affected accounts
        locks = []
        for account in transaction.accounts:
            lock = await self.lock_manager.acquire(f"account:{account}")
            locks.append(lock)

        try:
            # Validate transaction
            if not await self.validate_transaction(transaction):
                raise InvalidTransactionError()

            # Achieve consensus on transaction
            consensus_result = await self.consensus.propose(transaction)

            if consensus_result.accepted:
                # Append to immutable log
                entry = LedgerEntry(
                    transaction=transaction,
                    timestamp=consensus_result.timestamp,
                    sequence=consensus_result.sequence
                )
                await self.log.append(entry)

                return entry.sequence
            else:
                raise ConsensusFailedError()

        finally:
            # Release all locks
            for lock in locks:
                await lock.release()
```

**Guarantees**:
- Immutable transaction history
- Strong consistency through consensus
- ACID properties for financial operations

### ML Inference Pattern (P11+P12+P4)

**Problem**: How to serve machine learning models at scale with low latency?

**Solution**:
```python
class MLInferenceService:
    def __init__(self, model_cache, load_balancer):
        self.cache = model_cache
        self.balancer = load_balancer

    async def predict(self, model_id, features):
        # Load model from cache
        model = await self.cache.get_model(model_id)
        if not model:
            model = await self.load_model(model_id)
            await self.cache.set_model(model_id, model)

        # Fan-out for ensemble models
        if model.is_ensemble:
            predictions = await self.ensemble_predict(model, features)
            return self.aggregate_predictions(predictions)
        else:
            return await model.predict(features)

    async def ensemble_predict(self, ensemble_model, features):
        tasks = []
        for sub_model in ensemble_model.models:
            task = asyncio.create_task(sub_model.predict(features))
            tasks.append(task)

        return await asyncio.gather(*tasks)
```

**Guarantees**:
- Low latency through caching
- High availability through load balancing
- Parallel inference for ensemble models

### Search Pattern (P18+P11+P4)

**Problem**: How to implement fast, relevant search across large datasets?

**Solution**:
```python
class DistributedSearchEngine:
    def __init__(self, index_shards, cache):
        self.shards = index_shards
        self.cache = cache

    async def search(self, query, filters=None):
        # Check cache for popular queries
        cache_key = f"search:{hash(query)}:{hash(filters)}"
        if cached_results := await self.cache.get(cache_key):
            return cached_results

        # Fan-out search to all shards
        shard_tasks = []
        for shard in self.shards:
            task = asyncio.create_task(
                shard.search(query, filters, limit=100)
            )
            shard_tasks.append(task)

        # Gather results from all shards
        shard_results = await asyncio.gather(*shard_tasks)

        # Merge and rank results globally
        merged_results = self.merge_and_rank(shard_results)

        # Cache popular results
        if self.is_popular_query(query):
            await self.cache.set(cache_key, merged_results, ttl=600)

        return merged_results
```

**Guarantees**:
- Fast lookup through indexing
- Distributed scalability
- Relevance ranking

## Pattern Selection Decision Matrix

```mermaid
flowchart TD
    START[System Requirement] --> TYPE{Problem Type}

    TYPE -->|Data Consistency| CONSISTENCY{Consistency Level}
    TYPE -->|Performance| PERFORMANCE{Bottleneck Type}
    TYPE -->|Reliability| RELIABILITY{Failure Type}
    TYPE -->|Scale| SCALE{Scale Dimension}

    CONSISTENCY -->|Strong| STRONG_PATTERNS[Event Sourcing<br/>CQRS with sync<br/>Escrow]
    CONSISTENCY -->|Eventual| EVENTUAL_PATTERNS[Outbox<br/>Saga<br/>CQRS]

    PERFORMANCE -->|Read Heavy| READ_PATTERNS[CQRS<br/>Cache-aside<br/>Read Replicas]
    PERFORMANCE -->|Write Heavy| WRITE_PATTERNS[Sharding<br/>Escrow<br/>Batch]
    PERFORMANCE -->|Latency| LATENCY_PATTERNS[Cache<br/>CDN<br/>Hedged Requests]

    RELIABILITY -->|Service Failures| SERVICE_PATTERNS[Circuit Breaker<br/>Saga<br/>Bulkhead]
    RELIABILITY -->|Data Loss| DATA_PATTERNS[Event Sourcing<br/>Replication<br/>Backup]

    SCALE -->|Horizontal| SCALE_PATTERNS[Sharding<br/>CQRS<br/>Microservices]
    SCALE -->|Global| GLOBAL_PATTERNS[CDN<br/>Edge Computing<br/>Multi-region]

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class START,TYPE edgeStyle
    class CONSISTENCY,PERFORMANCE,RELIABILITY,SCALE serviceStyle
    class STRONG_PATTERNS,EVENTUAL_PATTERNS,READ_PATTERNS,WRITE_PATTERNS stateStyle
    class LATENCY_PATTERNS,SERVICE_PATTERNS,DATA_PATTERNS,SCALE_PATTERNS,GLOBAL_PATTERNS controlStyle
```

| **Requirement** | **Primary Pattern** | **Supporting Patterns** | **Anti-Pattern** | **Metrics** |
|---|---|---|---|---|
| Multi-service transactions | Saga | Outbox + Event Sourcing | Two-phase commit | 99% success rate |
| High-contention resources | Escrow | Sharding + Consensus | Global locks | <10ms lock time |
| Complete audit trail | Event Sourcing | CQRS + Snapshots | CRUD with logs | 100% event capture |
| Read/write optimization | CQRS | Cache + Projections | Shared database | 10:1 read/write ratio |
| Tail latency reduction | Hedged Requests | Cache + CDN | Synchronous chains | p99 <100ms |
| Service isolation | Bulkhead | Circuit Breaker + Rate Limit | Shared resources | Failure isolation |
| Cache consistency | Write-Through | Invalidation + TTL | Cache-aside | Zero stale reads |
| Geographic distribution | Edge Computing | CDN + Replication | Central deployment | <50ms global |

## Anti-Pattern Detection

### Common Mistakes

1. **Distributed Transactions**: Using 2PC instead of Saga
   - Detection: XA transaction monitoring
   - Fix: Replace with Saga pattern

2. **Dual Writes**: Writing to DB and message broker separately  
   - Detection: Inconsistency between DB and events
   - Fix: Use Outbox pattern

3. **Global Locks**: Single lock for high-contention resource
   - Detection: Lock wait time monitoring
   - Fix: Use Escrow with sharding

4. **Synchronous Saga**: Calling all saga steps synchronously
   - Detection: High latency for complex operations
   - Fix: Asynchronous orchestration

5. **Unbounded Queues**: No backpressure in event processing
   - Detection: Memory growth, processing lag
   - Fix: Add Bulkhead pattern

## Pattern Performance Matrix

```mermaid
quadrantChart
    title Pattern Performance vs Complexity
    x-axis Low Complexity --> High Complexity
    y-axis Low Latency --> High Latency

    Hedged Request: [0.2, 0.1]
    Sidecar: [0.4, 0.2]
    Request-Response: [0.3, 0.3]
    Outbox: [0.5, 0.4]
    Escrow: [0.5, 0.3]
    CQRS: [0.8, 0.6]
    Saga: [0.9, 0.8]
    Event Sourcing: [0.9, 0.7]
```

## Production Metrics Summary

| **Pattern** | **Latency Impact** | **Throughput** | **Consistency** | **Operational Overhead** | **Monthly Cost** |
|---|---|---|---|---|---|
| Outbox | +5-10ms | 50K TPS | Strong (DB) | Medium | +$2K |
| Saga | +50-200ms | 20K TPS | Eventual | High | +$5K |
| Escrow | +1-5ms | 100K TPS | Strong (locks) | Medium | +$3K |
| Event Sourcing | +10-20ms | 80K TPS | Strong (append) | High | +$8K |
| CQRS | Read: <1ms, Write: +5ms | 200K QPS reads | Eventual | High | +$10K |
| Hedged Request | P99: -50% | 150% load | N/A | Low | +$1K |
| Request-Response | +2-10ms | 50K RPS | Strong (sync) | Medium | +$2K |
| Streaming | +100-500ms lag | 1M events/sec | Eventual | Medium | +$4K |

Each micro-pattern solves specific distributed systems challenges with quantified trade-offs in performance, consistency, and operational complexity. Choose patterns based on your actual requirements, not theoretical ideals.