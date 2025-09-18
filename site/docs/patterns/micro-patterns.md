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
    API -->|p99: 50ms| ORDER
    ORDER -->|p99: 10ms| DB
    DB -->|p99: 5ms| CDC
    CDC -->|p99: 100ms| STREAM

    %% Failure scenarios
    CDC -.->|Processing failure| DLQ
    STREAM -.->|Downstream failure| DLQ
    DB -.->|Transaction rollback, p99: 20ms| ORDER

    %% Monitoring
    CDC -->|Lag: <500ms| MON
    STREAM -->|Throughput: 100K/s| MON
    DLQ -->|Error rate: <0.1%| MON

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

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
    CLIENT -->|p99: 5s timeout| ORCH
    ORCH -->|p99: 500ms| PAY
    ORCH -->|p99: 200ms| INV
    ORCH -->|p99: 1s| SHIP

    %% State management
    ORCH -->|p99: 50ms| SAGA_DB
    ORCH -->|p99: 10ms| EVENT_LOG

    %% Failure compensation
    PAY -.->|Timeout: 30s| COMP_QUEUE
    INV -.->|Insufficient Stock| COMP_QUEUE
    SHIP -.->|Delivery Error| COMP_QUEUE
    COMP_QUEUE -.->|Compensate, p99: 2s| PAY
    COMP_QUEUE -.->|Compensate, p99: 500ms| INV

    %% Monitoring
    ORCH -->|Success rate: 95%| MON
    COMP_QUEUE -->|Compensation rate: 5%| MON

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

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
    LB -->|hash(item_id) % 3, p99: 1ms| INV1
    LB -->|hash(item_id) % 3, p99: 1ms| INV2
    LB -->|hash(item_id) % 3, p99: 1ms| INV3

    %% Storage
    INV1 -->|p99: 5ms| DB1
    INV2 -->|p99: 5ms| DB2
    INV3 -->|p99: 5ms| DB3

    %% Distributed locking
    INV1 -->|Lock timeout: 10s| LOCK_MGR
    INV2 -->|Lock timeout: 10s| LOCK_MGR
    INV3 -->|Lock timeout: 10s| LOCK_MGR

    %% Management
    DB1 -->|TTL: 300s| TTL
    DB2 -->|TTL: 300s| TTL
    DB3 -->|TTL: 300s| TTL
    LOCK_MGR -->|Contention alerts| MON

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

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
    WRITE_API -->|p99: 100ms| COMMAND
    COMMAND -->|p99: 50ms| WRITE_DB
    WRITE_DB -->|p99: 10ms| EVENT_STREAM

    %% Read path
    READ_API -->|p99: 10ms| QUERY
    QUERY -->|Cache hit: p99: 1ms| READ_CACHE
    QUERY -->|Cache miss: p99: 20ms| READ_DB

    %% Event processing
    EVENT_STREAM -->|Lag: <500ms| PROJECTION
    PROJECTION -->|p99: 100ms| READ_DB
    PROJECTION -->|p99: 5ms| READ_CACHE

    %% Fallback path
    QUERY -.->|Cache miss + critical, p99: 200ms| WRITE_DB

    %% Management
    EVENT_STREAM -->|Lag monitoring| LAG_MON
    PROJECTION -->|Processing rate: 10K/s| LAG_MON
    LAG_MON -->|Trigger rebuild| REBUILD
    REBUILD -->|Recovery: 30min| PROJECTION

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

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
    CLIENT -->|Timeout: 30s, Retry: 3x| LB
    LB -->|Health check: 5s| CB
    CB -->|p99: 50ms| SERVER1
    CB -->|p99: 45ms| SERVER2
    CB -.->|Circuit open, Failure: 50%| SERVER3

    %% Data access
    SERVER1 -->|Hit ratio: 85%, p99: 1ms| CACHE
    SERVER2 -->|Hit ratio: 85%, p99: 1ms| CACHE
    SERVER3 -->|Hit ratio: 85%, p99: 1ms| CACHE
    CACHE -.->|Miss, p99: 20ms| DB
    SERVER1 -.->|Cache bypass, p99: 50ms| DB

    %% Monitoring
    LB -->|Health checks: 10s interval| HEALTH
    CB -->|Error rate tracking| METRICS
    SERVER1 -->|Latency: p99: 50ms| METRICS
    SERVER2 -->|Latency: p99: 45ms| METRICS
    SERVER3 -->|Degraded: p99: 200ms| HEALTH

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

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
    PRODUCER -->|1M events/sec| KAFKA
    KAFKA -->|Partition lag: <1s| PROCESSOR1
    KAFKA -->|Partition lag: <1s| PROCESSOR2

    %% State management
    PROCESSOR1 -->|State size: 10GB| STATE_STORE
    PROCESSOR2 -->|Write rate: 50K/s| SINK

    %% Failure handling
    PROCESSOR1 -.->|Failure, Recovery: 30s| REBALANCE
    PROCESSOR2 -.->|Failure, Recovery: 30s| REBALANCE
    REBALANCE -.->|Reassign partitions| PROCESSOR1

    %% Monitoring
    KAFKA -->|Consumer lag tracking| LAG_MON
    PROCESSOR1 -->|Processing rate: 500K/s| LAG_MON
    PROCESSOR2 -->|Processing rate: 500K/s| LAG_MON

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

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
    API -->|p99: 100ms| AGGREGATE
    AGGREGATE -->|p99: 20ms| EVENT_STORE

    %% Event processing
    EVENT_STORE -->|p99: 500ms lag| PROJECTOR
    PROJECTOR -->|p99: 100ms| VIEW_STORE

    %% Snapshots
    AGGREGATE -->|Every 1000 events| SNAPSHOTTER
    SNAPSHOTTER -->|p99: 5s| SNAPSHOT_STORE
    SNAPSHOT_STORE -.->|Load state: 200ms| AGGREGATE

    %% Management
    EVENT_STORE -->|Replay: 10K events/s| REPLAY
    EVENT_STORE -->|Archive after 90 days| ARCHIVE
    REPLAY -->|Rebuild: 30min| VIEW_STORE

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

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
    subgraph EdgePlane[Edge Plane - #3B82F6]
        REQUEST[Single Request<br/>Fan-out coordinator<br/>SLO: p99 <30s]
    end

    subgraph ServicePlane[Service Plane - #10B981]
        SERVICE1[Service A<br/>p99: 10ms, 99% SLA<br/>Cost: $2K/month]
        SERVICE2[Service B<br/>p99: 15ms, 95% SLA<br/>Cost: $3K/month]
        SERVICE3[Service C<br/>p99: 20ms, 98% SLA<br/>Cost: $2.5K/month]
        AGGREGATOR[Result Aggregator<br/>p99: 5ms merge<br/>Partial results: 90%]
    end

    subgraph StatePlane[State Plane - #F59E0B]
        RESULTS[(Aggregated Results<br/>JSON merge, 10GB/day<br/>Failure metadata)]
    end

    %% Fan-out
    REQUEST -->|p99: 10ms| SERVICE1
    REQUEST -->|p99: 15ms| SERVICE2
    REQUEST -->|p99: 20ms| SERVICE3

    %% Gather
    SERVICE1 -->|p99: 10ms, SLA: 99%| AGGREGATOR
    SERVICE2 -->|p99: 15ms, SLA: 95%| AGGREGATOR
    SERVICE3 -.->|Timeout: 30s, SLA: 98%| AGGREGATOR
    AGGREGATOR -->|p99: 30s total| RESULTS

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff

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
    subgraph EdgePlane[Edge Plane - #3B82F6]
        QUERY_API[Analytics API<br/>SQL interface, p99: 2s<br/>10K queries/day]
    end

    subgraph ServicePlane[Service Plane - #10B981]
        QUERY_ENGINE[Query Engine<br/>Apache Spark 3.4<br/>1TB/hour processing]
        ETL[ETL Processor<br/>Airflow orchestration<br/>500GB/day pipeline]
    end

    subgraph StatePlane[State Plane - #F59E0B]
        DWH[(Data Warehouse<br/>Snowflake, 100TB<br/>$50K/month)]
        STAGING[(Staging Area<br/>S3, 10TB buffer<br/>7-day retention)]
        METADATA[(Metadata Store<br/>Apache Atlas<br/>10K entities)]
    end

    subgraph ControlPlane[Control Plane - #8B5CF6]
        WORKLOAD[Workload Manager<br/>Resource allocation<br/>Auto-scaling: 10-100 nodes]
        SCHEDULER[Job Scheduler<br/>Airflow 2.7<br/>1K DAGs, 99.9% SLA]
    end

    %% Query flow
    QUERY_API -->|p99: 2s| QUERY_ENGINE
    QUERY_ENGINE -->|p99: 10s| DWH
    QUERY_ENGINE -->|p99: 100ms| METADATA

    %% ETL flow
    STAGING -->|500GB/day| ETL
    ETL -->|p99: 1 hour batch| DWH
    ETL -->|p99: 1s| METADATA

    %% Management
    QUERY_ENGINE -->|Auto-scale: 10-100 nodes| WORKLOAD
    ETL -->|SLA: 99.9%| SCHEDULER

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

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
    PRODUCER -->|Queue depth: 1K tasks| TASK_QUEUE
    TASK_QUEUE -->|Batch: 10, p99: 500ms| WORKER1
    TASK_QUEUE -->|Batch: 10, p99: 500ms| WORKER2
    TASK_QUEUE -->|Batch: 10, p99: 500ms| WORKER3

    %% Results and failures
    WORKER1 -->|Success rate: 95%| RESULT_STORE
    WORKER2 -->|Success rate: 95%| RESULT_STORE
    WORKER3 -->|Success rate: 95%| RESULT_STORE
    WORKER1 -.->|Max retries: 3| DLQ
    WORKER2 -.->|Max retries: 3| DLQ
    WORKER3 -.->|Max retries: 3| DLQ

    %% Management
    TASK_QUEUE -->|Auto-scale workers| SCHEDULER
    RESULT_STORE -->|Processing metrics| MONITOR
    DLQ -->|Failure rate: <5%| MONITOR

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

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

Optimized graph traversal with caching and distributed storage.

| Component | Technology | Performance | Guarantee | Cost |
|-----------|------------|-------------|-----------|------|
| Graph Store | Neo4j 5.x | 10K traversals/sec | ACID transactions | $5K/month |
| Cache Layer | Redis 7.x | 100K queries/sec | TTL-based consistency | $2K/month |
| Query Engine | GraphQL API | p99: 50ms | Index optimization | $3K/month |
| Partitioner | Consistent hash | 1M nodes/partition | Balanced distribution | Included |

### Ledger Pattern (P3+P5+P13)

Immutable transaction ledger with consensus and strong consistency.

| Component | Technology | Throughput | Consistency | Recovery Time |
|-----------|------------|------------|-------------|---------------|
| Consensus Layer | Raft/etcd 3.5 | 10K TPS | Strong consistency | <5s leader election |
| Lock Manager | Distributed locks | 1M locks/sec | Deadlock detection | 30s timeout |
| Immutable Log | Apache Kafka | 100K writes/sec | Append-only | Partition replication |
| Validation Engine | Business rules | 50K validations/sec | ACID guarantees | Transaction rollback |

### ML Inference Pattern (P11+P12+P4)

Scalable ML model serving with low latency and high availability.

| Component | Technology | Performance | Cache Hit Rate | Monthly Cost |
|-----------|------------|-------------|----------------|---------------|
| Model Cache | Redis + GPU memory | p99: 10ms | 95% | $15K GPU instances |
| Load Balancer | NVIDIA Triton | 10K inferences/sec | N/A | $2K |
| Ensemble Engine | TensorFlow Serving | 5K parallel calls | N/A | $8K |
| Model Store | S3 + CDN | 1GB/s transfer | 90% edge hit | $1K |

### Search Pattern (P18+P11+P4)

Distributed search with indexing, caching, and relevance ranking.

| Component | Technology | Query Rate | Index Size | Relevance Score |
|-----------|------------|------------|------------|------------------|
| Search Engine | Elasticsearch 8.x | 50K queries/sec | 1TB per shard | >95% precision |
| Index Shards | 20 shards/cluster | 2.5K queries/shard | 50GB average | Auto-rebalancing |
| Result Cache | Redis cluster | 100K hits/sec | 10GB cache | 85% hit rate |
| Ranking Engine | ML-based scoring | p99: 20ms | Real-time updates | Learning feedback |

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

    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

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