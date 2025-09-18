# Implementation Guides

Production-ready architectures for implementing distributed systems patterns with real-world examples.

## Implementing the Outbox Pattern

Ensures atomic database updates and event publishing without distributed transactions, used by Uber for ride state management.

### Complete Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - API Layer]
        API[REST API - Spring Boot]
        VALIDATE[Request Validation]
        AUTH[Authentication]
        RATE_LIMIT[Rate Limiting]
    end

    subgraph ServicePlane[Service Plane - Business Logic]
        ORDER_SVC[Order Service]
        INVENTORY_SVC[Inventory Service]
        EMAIL_SVC[Email Service]
        PAYMENT_SVC[Payment Service]
    end

    subgraph StatePlane[State Plane - Data Storage]
        PRIMARY_DB[(PostgreSQL - Primary)]
        OUTBOX_TABLE[(Outbox Table)]
        KAFKA[(Kafka - Event Stream)]
        CONSUMER_OFFSET[(Consumer Offsets)]
    end

    subgraph ControlPlane[Control Plane - Event Processing]
        CDC[Change Data Capture]
        EVENT_PUBLISHER[Event Publisher]
        DEAD_LETTER[Dead Letter Queue]
        MONITORING[Event Monitoring]
    end

    %% Request flow
    API --> VALIDATE
    VALIDATE --> ORDER_SVC
    ORDER_SVC --> PRIMARY_DB
    ORDER_SVC --> OUTBOX_TABLE

    %% Event flow
    CDC --> OUTBOX_TABLE
    CDC --> EVENT_PUBLISHER
    EVENT_PUBLISHER --> KAFKA
    KAFKA --> INVENTORY_SVC
    KAFKA --> EMAIL_SVC

    %% Failure handling
    EVENT_PUBLISHER --> DEAD_LETTER
    MONITORING --> DEAD_LETTER

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class API,VALIDATE,AUTH,RATE_LIMIT edgeStyle
    class ORDER_SVC,INVENTORY_SVC,EMAIL_SVC,PAYMENT_SVC serviceStyle
    class PRIMARY_DB,OUTBOX_TABLE,KAFKA,CONSUMER_OFFSET stateStyle
    class CDC,EVENT_PUBLISHER,DEAD_LETTER,MONITORING controlStyle
```

### Atomic Transaction Pattern

```mermaid
sequenceDiagram
    participant Client
    participant OrderService
    participant Database
    participant OutboxTable
    participant EventPublisher
    participant EventConsumer

    Client->>OrderService: POST /orders
    OrderService->>Database: BEGIN TRANSACTION

    Note over OrderService,OutboxTable: Single Atomic Transaction
    OrderService->>Database: INSERT INTO orders
    OrderService->>OutboxTable: INSERT INTO outbox
    OrderService->>Database: COMMIT

    OrderService->>Client: 201 Created (order_id)

    Note over EventPublisher: Async Processing
    EventPublisher->>OutboxTable: Poll for new events
    EventPublisher->>EventConsumer: Publish OrderCreated
    EventPublisher->>OutboxTable: Mark event published

    EventConsumer->>EventConsumer: Process event
    EventConsumer->>EventPublisher: Ack processed
```

### Data Schema Design

```mermaid
erDiagram
    ORDERS {
        uuid id PK
        uuid customer_id
        jsonb items
        decimal total
        varchar status
        timestamp created_at
        timestamp updated_at
    }

    OUTBOX {
        bigserial id PK
        uuid event_id UK
        varchar event_type
        jsonb payload
        timestamp created_at
        timestamp published_at
        boolean published
    }

    EVENT_LOG {
        bigserial id PK
        uuid event_id FK
        varchar consumer_name
        varchar status
        timestamp processed_at
        text error_message
    }

    ORDERS ||--o{ OUTBOX : generates
    OUTBOX ||--o{ EVENT_LOG : tracks
```

### Event Processing Pipeline

```mermaid
graph TB
    subgraph EventGeneration[Event Generation - Transactional]
        ORDER_CREATE[Order Creation]
        BUSINESS_LOGIC[Business Logic Execution]
        OUTBOX_INSERT[Outbox Entry Creation]
        TRANSACTION_COMMIT[Atomic Commit]
    end

    subgraph EventPublishing[Event Publishing - Asynchronous]
        POLL[Poll Outbox Table]
        BATCH[Batch Event Retrieval]
        SERIALIZE[Event Serialization]
        KAFKA_PUBLISH[Kafka Publication]
        MARK_PUBLISHED[Mark as Published]
    end

    subgraph EventConsumption[Event Consumption - Idempotent]
        CONSUME[Consume from Kafka]
        DUPLICATE_CHECK[Idempotency Check]
        BUSINESS_PROCESS[Business Processing]
        ACK[Acknowledge Message]
        ERROR_HANDLE[Error Handling]
    end

    ORDER_CREATE --> BUSINESS_LOGIC
    BUSINESS_LOGIC --> OUTBOX_INSERT
    OUTBOX_INSERT --> TRANSACTION_COMMIT

    TRANSACTION_COMMIT --> POLL
    POLL --> BATCH
    BATCH --> SERIALIZE
    SERIALIZE --> KAFKA_PUBLISH
    KAFKA_PUBLISH --> MARK_PUBLISHED

    MARK_PUBLISHED --> CONSUME
    CONSUME --> DUPLICATE_CHECK
    DUPLICATE_CHECK --> BUSINESS_PROCESS
    BUSINESS_PROCESS --> ACK
    BUSINESS_PROCESS --> ERROR_HANDLE

    classDef genStyle fill:#9966CC,stroke:#663399,color:#fff
    classDef pubStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef conStyle fill:#10B981,stroke:#059669,color:#fff

    class ORDER_CREATE,BUSINESS_LOGIC,OUTBOX_INSERT,TRANSACTION_COMMIT genStyle
    class POLL,BATCH,SERIALIZE,KAFKA_PUBLISH,MARK_PUBLISHED pubStyle
    class CONSUME,DUPLICATE_CHECK,BUSINESS_PROCESS,ACK,ERROR_HANDLE conStyle
```

### Monitoring & Operations Dashboard

| Metric | Healthy Range | Alert Threshold | Action Required |
|--------|---------------|----------------|-----------------|
| Unpublished Events | 0-100 | >1000 | Scale publisher |
| Publishing Lag | <30s | >2min | Investigate bottleneck |
| Consumer Lag | <5s | >30s | Scale consumers |
| Error Rate | <1% | >5% | Check error logs |
| Throughput | 1K-10K/sec | <100/sec | Check system health |

---

## Implementing CQRS (Command Query Responsibility Segregation)

Separates read and write models for optimal performance, used by LinkedIn for their feed architecture at massive scale.

### Complete Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - API Gateway]
        CLIENT[Client Applications]
        API_GW[API Gateway - Kong]
        LOAD_BAL[Load Balancer]
        CDN[CDN - Static Content]
    end

    subgraph ServicePlane[Service Plane - Segregated APIs]
        COMMAND_API[Command API - Write Operations]
        QUERY_API[Query API - Read Operations]
        DOMAIN_SVC[Domain Services]
        PROJECTION_SVC[Projection Services]
    end

    subgraph StatePlane[State Plane - Dual Storage]
        WRITE_DB[(Write DB - PostgreSQL)]
        READ_DB[(Read DB - ElasticSearch)]
        EVENT_STORE[(Event Store - Kafka)]
        CACHE[(Redis Cache)]
    end

    subgraph ControlPlane[Control Plane - Event Processing]
        EVENT_PROCESSOR[Event Processor]
        PROJECTOR[View Projector]
        SNAPSHOT[Snapshot Manager]
        MONITOR[Performance Monitor]
    end

    %% Client flows
    CLIENT --> API_GW
    API_GW --> COMMAND_API
    API_GW --> QUERY_API

    %% Command flow (writes)
    COMMAND_API --> DOMAIN_SVC
    DOMAIN_SVC --> WRITE_DB
    DOMAIN_SVC --> EVENT_STORE

    %% Query flow (reads)
    QUERY_API --> CACHE
    CACHE --> READ_DB

    %% Event processing
    EVENT_STORE --> EVENT_PROCESSOR
    EVENT_PROCESSOR --> PROJECTOR
    PROJECTOR --> READ_DB

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class CLIENT,API_GW,LOAD_BAL,CDN edgeStyle
    class COMMAND_API,QUERY_API,DOMAIN_SVC,PROJECTION_SVC serviceStyle
    class WRITE_DB,READ_DB,EVENT_STORE,CACHE stateStyle
    class EVENT_PROCESSOR,PROJECTOR,SNAPSHOT,MONITOR controlStyle
```

### Command-Query Segregation Flow

```mermaid
sequenceDiagram
    participant Client
    participant CommandAPI
    participant WriteDB
    participant EventStore
    participant Projector
    participant ReadDB
    participant QueryAPI

    Note over Client,QueryAPI: Write Path (Commands)
    Client->>CommandAPI: POST /orders
    CommandAPI->>WriteDB: Save order (normalized)
    CommandAPI->>EventStore: Publish OrderCreated event
    CommandAPI->>Client: 201 Created

    Note over EventStore,ReadDB: Async Projection
    EventStore->>Projector: OrderCreated event
    Projector->>ReadDB: Update denormalized view
    Projector->>EventStore: Ack processed

    Note over Client,QueryAPI: Read Path (Queries)
    Client->>QueryAPI: GET /orders/{id}
    QueryAPI->>ReadDB: Query denormalized view
    ReadDB->>QueryAPI: Order details
    QueryAPI->>Client: 200 OK with data
```

### Data Model Separation

```mermaid
erDiagram
    %% Write Model (Normalized)
    ORDERS_WRITE {
        uuid id PK
        uuid customer_id FK
        varchar status
        timestamp created_at
        timestamp updated_at
    }

    ORDER_ITEMS_WRITE {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        decimal price
    }

    %% Read Model (Denormalized)
    ORDER_VIEW_READ {
        uuid order_id PK
        uuid customer_id
        varchar customer_name
        varchar customer_email
        varchar status
        jsonb items_summary
        decimal total_amount
        int item_count
        timestamp created_at
    }

    CUSTOMER_SUMMARY_READ {
        uuid customer_id PK
        varchar name
        varchar email
        int total_orders
        decimal total_spent
        timestamp last_order_date
    }

    ORDERS_WRITE ||--o{ ORDER_ITEMS_WRITE : contains
    ORDERS_WRITE ||--|| ORDER_VIEW_READ : projects_to
    ORDER_VIEW_READ }o--|| CUSTOMER_SUMMARY_READ : aggregates_to
```

### Event-Driven Projections

```mermaid
graph TB
    subgraph EventSourcing[Event Sourcing Pipeline]
        COMMAND[Command Execution]
        EVENT_GEN[Event Generation]
        EVENT_PERSIST[Event Persistence]
        EVENT_PUBLISH[Event Publication]
    end

    subgraph Projections[View Projections]
        ORDER_VIEW[Order Detail View]
        CUSTOMER_VIEW[Customer Summary View]
        ANALYTICS_VIEW[Analytics View]
        SEARCH_INDEX[Search Index]
    end

    subgraph Optimization[Performance Optimization]
        SNAPSHOT[Snapshot Creation]
        REPLAY[Event Replay]
        COMPACTION[Event Compaction]
        CACHING[Multi-level Caching]
    end

    COMMAND --> EVENT_GEN
    EVENT_GEN --> EVENT_PERSIST
    EVENT_PERSIST --> EVENT_PUBLISH

    EVENT_PUBLISH --> ORDER_VIEW
    EVENT_PUBLISH --> CUSTOMER_VIEW
    EVENT_PUBLISH --> ANALYTICS_VIEW
    EVENT_PUBLISH --> SEARCH_INDEX

    ORDER_VIEW --> SNAPSHOT
    CUSTOMER_VIEW --> REPLAY
    ANALYTICS_VIEW --> COMPACTION
    SEARCH_INDEX --> CACHING

    classDef eventStyle fill:#9966CC,stroke:#663399,color:#fff
    classDef projectionStyle fill:#10B981,stroke:#059669,color:#fff
    classDef optimizeStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class COMMAND,EVENT_GEN,EVENT_PERSIST,EVENT_PUBLISH eventStyle
    class ORDER_VIEW,CUSTOMER_VIEW,ANALYTICS_VIEW,SEARCH_INDEX projectionStyle
    class SNAPSHOT,REPLAY,COMPACTION,CACHING optimizeStyle
```

### API Design Patterns

```mermaid
graph TB
    subgraph CommandAPI[Command API - Write Operations]
        CREATE_ORDER[POST /orders - Create Order]
        UPDATE_ORDER[PUT /orders/{id} - Update Order]
        CANCEL_ORDER[DELETE /orders/{id} - Cancel Order]
        ADD_ITEM[POST /orders/{id}/items - Add Item]
    end

    subgraph QueryAPI[Query API - Read Operations]
        GET_ORDER[GET /orders/{id} - Order Details]
        SEARCH_ORDERS[GET /orders?filter - Search Orders]
        CUSTOMER_ORDERS[GET /customers/{id}/orders - Customer Orders]
        ORDER_ANALYTICS[GET /analytics/orders - Order Analytics]
    end

    subgraph ResponsePatterns[Response Patterns]
        ASYNC_COMMANDS[Commands: 202 Accepted + Location Header]
        FAST_QUERIES[Queries: 200 OK + Cached Data]
        EVENTUAL_CONSISTENCY[Eventual Consistency Warnings]
        HYPERMEDIA[HATEOAS Links for Navigation]
    end

    CREATE_ORDER --> ASYNC_COMMANDS
    UPDATE_ORDER --> ASYNC_COMMANDS
    CANCEL_ORDER --> ASYNC_COMMANDS
    ADD_ITEM --> ASYNC_COMMANDS

    GET_ORDER --> FAST_QUERIES
    SEARCH_ORDERS --> FAST_QUERIES
    CUSTOMER_ORDERS --> FAST_QUERIES
    ORDER_ANALYTICS --> FAST_QUERIES

    ASYNC_COMMANDS --> EVENTUAL_CONSISTENCY
    FAST_QUERIES --> HYPERMEDIA

    classDef commandStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef queryStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef responseStyle fill:#10B981,stroke:#059669,color:#fff

    class CREATE_ORDER,UPDATE_ORDER,CANCEL_ORDER,ADD_ITEM commandStyle
    class GET_ORDER,SEARCH_ORDERS,CUSTOMER_ORDERS,ORDER_ANALYTICS queryStyle
    class ASYNC_COMMANDS,FAST_QUERIES,EVENTUAL_CONSISTENCY,HYPERMEDIA responseStyle
```

### Performance Comparison

| Operation | Traditional CRUD | CQRS Implementation | Improvement |
|-----------|------------------|---------------------|-------------|
| Write Latency | 50ms (complex joins) | 10ms (simple insert) | **5x faster** |
| Read Latency | 200ms (joins + calc) | 5ms (pre-computed) | **40x faster** |
| Throughput | 1K req/sec | 10K req/sec | **10x better** |
| Scalability | Coupled read/write | Independent scaling | **Unlimited** |
| Availability | 99.9% (single DB) | 99.99% (segregated) | **10x better** |

---

## Implementing Circuit Breaker Pattern

Prevents cascading failures by failing fast when dependencies are unhealthy, used by Netflix Hystrix for microservice protection.

### Complete Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Client Interface]
        CLIENT[Client Application]
        PROXY[Service Proxy]
        TIMEOUT[Timeout Handler]
        RETRY[Retry Logic]
    end

    subgraph ServicePlane[Service Plane - Protected Services]
        PRIMARY_SVC[Primary Service]
        FALLBACK_SVC[Fallback Service]
        HEALTH_CHECK[Health Checker]
        METRICS_COL[Metrics Collector]
    end

    subgraph StatePlane[State Plane - Circuit State]
        CIRCUIT_STATE[(Circuit State Store)]
        METRICS_DB[(Metrics Database)]
        CONFIG_STORE[(Configuration Store)]
        ALERT_STORE[(Alert History)]
    end

    subgraph ControlPlane[Control Plane - Circuit Management]
        STATE_MACHINE[State Machine]
        THRESHOLD_MONITOR[Threshold Monitor]
        DASHBOARD[Circuit Dashboard]
        ALERT_MGR[Alert Manager]
    end

    %% Request flow
    CLIENT --> PROXY
    PROXY --> TIMEOUT
    TIMEOUT --> STATE_MACHINE
    STATE_MACHINE --> PRIMARY_SVC
    STATE_MACHINE --> FALLBACK_SVC

    %% Monitoring flow
    PRIMARY_SVC --> METRICS_COL
    METRICS_COL --> THRESHOLD_MONITOR
    THRESHOLD_MONITOR --> STATE_MACHINE

    %% Data flow
    STATE_MACHINE --> CIRCUIT_STATE
    METRICS_COL --> METRICS_DB
    THRESHOLD_MONITOR --> ALERT_MGR

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class CLIENT,PROXY,TIMEOUT,RETRY edgeStyle
    class PRIMARY_SVC,FALLBACK_SVC,HEALTH_CHECK,METRICS_COL serviceStyle
    class CIRCUIT_STATE,METRICS_DB,CONFIG_STORE,ALERT_STORE stateStyle
    class STATE_MACHINE,THRESHOLD_MONITOR,DASHBOARD,ALERT_MGR controlStyle
```

### Circuit Breaker State Machine

```mermaid
stateDiagram-v2
    [*] --> Closed

    Closed --> Open : Failure threshold exceeded
    Open --> HalfOpen : Recovery timeout elapsed
    HalfOpen --> Closed : Success threshold met
    HalfOpen --> Open : Any failure detected

    state Closed {
        [*] --> MonitoringCalls
        MonitoringCalls --> CountingFailures
        CountingFailures --> MonitoringCalls
        CountingFailures --> [*] : Threshold exceeded
    }

    state Open {
        [*] --> FailingFast
        FailingFast --> WaitingForTimeout
        WaitingForTimeout --> [*] : Timeout elapsed
    }

    state HalfOpen {
        [*] --> TestingRecovery
        TestingRecovery --> CountingSuccesses
        CountingSuccesses --> [*] : Success/Failure
    }
```

### Failure Detection & Recovery Flow

```mermaid
sequenceDiagram
    participant Client
    participant CircuitBreaker
    participant PrimaryService
    participant FallbackService
    participant Monitor

    Note over Client,Monitor: Normal Operation (Closed State)
    Client->>CircuitBreaker: Request
    CircuitBreaker->>PrimaryService: Forward request
    PrimaryService->>CircuitBreaker: Success response
    CircuitBreaker->>Client: Return response
    CircuitBreaker->>Monitor: Record success metric

    Note over Client,Monitor: Failure Detection
    Client->>CircuitBreaker: Request
    CircuitBreaker->>PrimaryService: Forward request
    PrimaryService->>CircuitBreaker: Failure/Timeout
    CircuitBreaker->>Monitor: Record failure metric
    Monitor->>CircuitBreaker: Threshold exceeded
    CircuitBreaker->>CircuitBreaker: Transition to OPEN

    Note over Client,Monitor: Fast Fail (Open State)
    Client->>CircuitBreaker: Request
    CircuitBreaker->>FallbackService: Use fallback
    FallbackService->>CircuitBreaker: Fallback response
    CircuitBreaker->>Client: Return fallback

    Note over Client,Monitor: Recovery Attempt (Half-Open)
    CircuitBreaker->>CircuitBreaker: Recovery timeout
    Client->>CircuitBreaker: Request
    CircuitBreaker->>PrimaryService: Test request
    PrimaryService->>CircuitBreaker: Success
    CircuitBreaker->>CircuitBreaker: Transition to CLOSED
```

### Multi-Level Circuit Protection

```mermaid
graph TB
    subgraph ApplicationLevel[Application Level - Coarse Grained]
        APP_CIRCUIT[Application Circuit Breaker]
        APP_FALLBACK[Application Fallback]
        APP_HEALTH[Application Health Check]
    end

    subgraph ServiceLevel[Service Level - Fine Grained]
        AUTH_CIRCUIT[Auth Service Circuit]
        DB_CIRCUIT[Database Circuit]
        CACHE_CIRCUIT[Cache Circuit]
        API_CIRCUIT[External API Circuit]
    end

    subgraph ResourceLevel[Resource Level - Ultra Fine]
        CPU_CIRCUIT[CPU Overload Circuit]
        MEMORY_CIRCUIT[Memory Circuit]
        DISK_CIRCUIT[Disk I/O Circuit]
        NETWORK_CIRCUIT[Network Circuit]
    end

    subgraph FallbackStrategies[Fallback Strategies]
        CACHED_DATA[Serve Cached Data]
        DEFAULT_RESPONSE[Default Response]
        DEGRADED_MODE[Degraded Functionality]
        QUEUE_REQUEST[Queue for Later]
    end

    APP_CIRCUIT --> AUTH_CIRCUIT
    APP_CIRCUIT --> DB_CIRCUIT
    AUTH_CIRCUIT --> CPU_CIRCUIT
    DB_CIRCUIT --> MEMORY_CIRCUIT

    APP_FALLBACK --> CACHED_DATA
    AUTH_CIRCUIT --> DEFAULT_RESPONSE
    DB_CIRCUIT --> DEGRADED_MODE
    API_CIRCUIT --> QUEUE_REQUEST

    classDef appStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef serviceStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef resourceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef fallbackStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class APP_CIRCUIT,APP_FALLBACK,APP_HEALTH appStyle
    class AUTH_CIRCUIT,DB_CIRCUIT,CACHE_CIRCUIT,API_CIRCUIT serviceStyle
    class CPU_CIRCUIT,MEMORY_CIRCUIT,DISK_CIRCUIT,NETWORK_CIRCUIT resourceStyle
    class CACHED_DATA,DEFAULT_RESPONSE,DEGRADED_MODE,QUEUE_REQUEST fallbackStyle
```

### Configuration & Tuning Matrix

| Service Type | Failure Threshold | Recovery Timeout | Success Threshold | Fallback Strategy |
|--------------|------------------|------------------|-------------------|-------------------|
| **Payment API** | 3 failures | 60 seconds | 2 successes | Cached exchange rates |
| **User Database** | 5 failures | 30 seconds | 3 successes | Read-only replica |
| **Image Service** | 10 failures | 120 seconds | 5 successes | Default placeholder |
| **Email Service** | 2 failures | 300 seconds | 1 success | Queue for retry |
| **Analytics API** | 15 failures | 60 seconds | 10 successes | Drop requests |

### Real-time Monitoring Dashboard

```mermaid
graph TB
    subgraph Metrics[Key Metrics - Real-time]
        SUCCESS_RATE[Success Rate: 99.5%]
        FAILURE_RATE[Failure Rate: 0.5%]
        LATENCY_P99[Latency p99: 150ms]
        CIRCUIT_STATUS[Circuit Status: CLOSED]
    end

    subgraph Alerts[Alert Conditions]
        DEGRADED[Degraded: >5% failure rate]
        CRITICAL[Critical: Circuit OPEN]
        RECOVERING[Recovering: Circuit HALF_OPEN]
        HEALTHY[Healthy: <1% failure rate]
    end

    subgraph Actions[Automated Actions]
        SCALE_OUT[Auto-scale instances]
        ENABLE_FALLBACK[Enable fallback mode]
        NOTIFY_ONCALL[Notify on-call engineer]
        INCIDENT_CREATE[Create incident ticket]
    end

    SUCCESS_RATE --> HEALTHY
    FAILURE_RATE --> DEGRADED
    CIRCUIT_STATUS --> CRITICAL
    CIRCUIT_STATUS --> RECOVERING

    HEALTHY --> SCALE_OUT
    DEGRADED --> ENABLE_FALLBACK
    CRITICAL --> NOTIFY_ONCALL
    RECOVERING --> INCIDENT_CREATE

    classDef metricStyle fill:#10B981,stroke:#059669,color:#fff
    classDef alertStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef actionStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class SUCCESS_RATE,FAILURE_RATE,LATENCY_P99,CIRCUIT_STATUS metricStyle
    class DEGRADED,CRITICAL,RECOVERING,HEALTHY alertStyle
    class SCALE_OUT,ENABLE_FALLBACK,NOTIFY_ONCALL,INCIDENT_CREATE actionStyle
```

These implementation patterns provide battle-tested approaches for building resilient distributed systems that can handle failures gracefully and recover automatically.