# DoorDash Request Flow - The Golden Path

## Executive Summary

DoorDash's order flow handles the complete journey from order placement to delivery completion, orchestrating interactions between 30M+ consumers, 1M+ drivers, and 500K+ merchants. The system processes 2M+ orders daily during peak periods with sub-second response times and real-time tracking.

**Critical SLOs**:
- **Order Placement**: p99 < 500ms
- **Driver Assignment**: p99 < 2 seconds
- **Real-time Tracking**: p99 < 100ms updates
- **Payment Processing**: p99 < 3 seconds
- **End-to-end**: 30-35 minute average delivery

## Complete Order Flow - Customer Journey

```mermaid
sequenceDiagram
    participant C as Customer App<br/>(iOS/Android)
    participant E as Edge Layer<br/>(Cloudflare + ALB)
    participant G as API Gateway<br/>(Kong)
    participant O as Order Service<br/>(Java 17)
    participant R as Restaurant Service<br/>(Java 17)
    participant P as Payment Service<br/>(Java 17)
    participant D as Dispatch Service<br/>(DeepRed ML)
    participant DR as Driver App<br/>(React Native)
    participant K as Kafka<br/>(Event Streaming)
    participant DB as PostgreSQL<br/>(Orders DB)
    participant DDB as DynamoDB<br/>(Driver Locations)
    participant RD as Redis<br/>(Caching)

    Note over C,RD: Phase 1: Order Placement (Target: <2 seconds)

    C->>E: POST /api/v1/orders<br/>SLO: p99 < 100ms
    E->>G: Forward request<br/>CDN bypass for dynamic
    G->>O: Create order<br/>Rate limit: 100 req/min/user

    par Restaurant Validation
        O->>R: Validate restaurant<br/>GET /restaurants/{id}/availability
        R->>RD: Check cache<br/>TTL: 60 seconds
        alt Cache Miss
            R->>DB: Query restaurant status<br/>p99 < 50ms
            R->>RD: Cache result
        end
        R-->>O: Restaurant available<br/>Menu items in stock
    and Payment Processing
        O->>P: Process payment<br/>POST /payments/authorize
        P->>P: Fraud detection<br/>ML model: <100ms
        P->>P: Call Stripe API<br/>p99 < 1.5s
        P-->>O: Payment authorized<br/>Auth token returned
    end

    O->>DB: INSERT order<br/>Async write, p99 < 100ms
    O->>K: Publish OrderCreated event<br/>Partition by zone
    O-->>C: Order confirmed<br/>{"orderId": "123", "eta": "35min"}

    Note over C,RD: Phase 2: Restaurant Notification (Target: <5 seconds)

    K->>R: OrderCreated event<br/>Consumer group: restaurants
    R->>R: Calculate prep time<br/>ML model based on kitchen load
    R->>DR: Push notification<br/>via FCM, p99 < 2s
    R->>K: Publish OrderAccepted event<br/>Include prep_time_minutes

    Note over C,RD: Phase 3: Driver Dispatch (Target: <30 seconds)

    K->>D: OrderAccepted event<br/>Consumer group: dispatch
    D->>DDB: Query available drivers<br/>Geohash radius search
    D->>D: Run DeepRed algorithm<br/>ML inference: <100ms
    Note over D: Factors: distance, ratings,<br/>traffic, driver preferences

    D->>DR: Dispatch request<br/>WebSocket push
    DR->>D: Accept delivery<br/>POST /dispatch/accept
    D->>DDB: Update driver status<br/>BUSY state
    D->>K: Publish DriverAssigned event

    Note over C,RD: Phase 4: Real-time Tracking (Throughout delivery)

    loop Every 5 seconds
        DR->>D: GPS location update<br/>POST /drivers/location
        D->>DDB: Store location<br/>TTL: 24 hours
        D->>RD: Update ETA cache<br/>ML-based calculation
    end

    loop Every 10 seconds
        C->>O: GET /orders/{id}/tracking
        O->>RD: Fetch cached ETA<br/>p99 < 10ms
        O-->>C: Location + ETA update<br/>WebSocket or polling
    end

    Note over C,RD: Phase 5: Pickup & Delivery

    DR->>R: Arrived at restaurant<br/>POST /drivers/arrived
    R->>C: Driver arrived notification<br/>Push via FCM

    DR->>R: Order picked up<br/>POST /orders/{id}/pickup
    R->>K: Publish OrderPickedUp event
    K->>O: Update order status<br/>PICKED_UP
    O->>C: Pickup notification<br/>"Your order is on the way!"

    DR->>O: Delivered<br/>POST /orders/{id}/delivered
    O->>P: Capture payment<br/>Settle authorized amount
    O->>K: Publish OrderDelivered event
    O->>C: Delivery confirmation<br/>"Your order has arrived!"

    Note over C,RD: Phase 6: Post-delivery

    C->>O: Rate experience<br/>POST /orders/{id}/rating
    O->>K: Publish RatingReceived event<br/>Analytics pipeline
    K->>D: Update driver metrics<br/>For future dispatch decisions
```

## Detailed Service Interactions

### Order Service Flow Details

```mermaid
graph LR
    subgraph OrderValidation[Order Validation - p99 < 200ms]
        OV1[Validate Cart<br/>Item availability]
        OV2[Check Delivery Zone<br/>Geofencing]
        OV3[Validate Promo Codes<br/>Rules engine]
        OV4[Calculate Fees<br/>Dynamic pricing]

        OV1 --> OV2 --> OV3 --> OV4
    end

    subgraph PaymentFlow[Payment Processing - p99 < 3s]
        PF1[Fraud Detection<br/>ML model scoring]
        PF2[Payment Authorization<br/>Stripe API call]
        PF3[Store Payment Method<br/>Tokenization]
        PF4[Reserve Funds<br/>Pre-authorization]

        PF1 --> PF2 --> PF3 --> PF4
    end

    subgraph OrderPersistence[Order Persistence - p99 < 100ms]
        OP1[Generate Order ID<br/>UUID v4]
        OP2[Write to PostgreSQL<br/>ACID transaction]
        OP3[Cache Order Details<br/>Redis TTL: 1 hour]
        OP4[Publish Event<br/>Kafka async]

        OP1 --> OP2 --> OP3 --> OP4
    end

    OrderValidation --> PaymentFlow
    PaymentFlow --> OrderPersistence

    classDef validationStyle fill:#10B981,stroke:#047857,color:#fff
    classDef paymentStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef persistenceStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class OV1,OV2,OV3,OV4 validationStyle
    class PF1,PF2,PF3,PF4 paymentStyle
    class OP1,OP2,OP3,OP4 persistenceStyle
```

## Real-time Tracking Architecture

```mermaid
graph TB
    subgraph DriverApps[Driver Apps - 100K+ concurrent]
        DA1[Driver App 1<br/>GPS every 5s]
        DA2[Driver App 2<br/>GPS every 5s]
        DA3[Driver App N<br/>GPS every 5s]
    end

    subgraph LocationIngestion[Location Ingestion - 5M updates/sec]
        LB[Load Balancer<br/>Geographic routing]
        LS[Location Service<br/>Go, Auto-scaling]
        KDS[Kinesis Data Streams<br/>1000 shards]
    end

    subgraph Processing[Real-time Processing]
        KA[Kinesis Analytics<br/>Windowed aggregation]
        ETA[ETA Calculator<br/>ML model inference]
        GEO[Geofencing Service<br/>Arrival detection]
    end

    subgraph Storage[Location Storage]
        DDB[(DynamoDB<br/>Driver locations<br/>5M writes/sec)]
        RDS[(Redis<br/>Hot location cache<br/>TTL: 30s)]
    end

    subgraph CustomerApps[Customer Apps - 10M+ concurrent]
        CA1[Customer App 1<br/>Poll every 10s]
        CA2[Customer App 2<br/>WebSocket conn]
        CA3[Customer App N<br/>Hybrid approach]
    end

    DA1 --> LB
    DA2 --> LB
    DA3 --> LB
    LB --> LS
    LS --> KDS
    LS --> DDB

    KDS --> KA
    KA --> ETA
    KA --> GEO
    ETA --> RDS
    GEO --> RDS

    CA1 --> RDS
    CA2 --> RDS
    CA3 --> RDS

    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class DA1,DA2,DA3,LB edgeStyle
    class LS,KA,ETA,GEO serviceStyle
    class KDS,DDB,RDS stateStyle
```

## Critical Performance Metrics

### Latency Breakdown (Production SLOs)

| Service Component | p50 | p99 | p99.9 | Max | Timeout |
|------------------|-----|-----|-------|-----|---------|
| **Order Placement** | 150ms | 500ms | 1.2s | 5s | 10s |
| **Payment Authorization** | 800ms | 3s | 5s | 15s | 30s |
| **Driver Assignment** | 300ms | 2s | 5s | 30s | 60s |
| **Location Updates** | 50ms | 100ms | 200ms | 1s | 5s |
| **ETA Calculation** | 80ms | 150ms | 300ms | 2s | 10s |
| **Push Notifications** | 200ms | 2s | 5s | 30s | 60s |

### Throughput Characteristics

| Operation | Peak RPS | Daily Volume | Storage Impact |
|-----------|----------|--------------|----------------|
| **Order Placement** | 5,000 | 2M orders | 500GB/day |
| **Location Updates** | 50,000 | 100M updates | 2TB/day |
| **Tracking Requests** | 100,000 | 500M requests | Read-heavy |
| **Push Notifications** | 20,000 | 50M messages | Stateless |

## Error Handling & Recovery

### Circuit Breaker Patterns
- **Payment Service**: 5% error rate threshold, 30s timeout
- **Restaurant Service**: 10% error rate, 60s recovery
- **Dispatch Service**: 3% error rate, immediate fallback

### Fallback Strategies
- **Payment Failure**: Retry with backup processor
- **Dispatch Timeout**: Manual driver assignment
- **Location Service**: Use cached last-known position
- **ETA Failure**: Static time estimates based on distance

### Data Consistency
- **Order State**: Event sourcing with Kafka
- **Payment State**: Two-phase commit with compensation
- **Location Data**: Eventually consistent, TTL-based cleanup

## Business Impact Metrics

### Order Completion Rates
- **Overall Success**: 96.5% (industry-leading)
- **Payment Success**: 98.2% first attempt
- **Driver Assignment**: 94% within 60 seconds
- **On-time Delivery**: 85% within promised window

### Customer Experience
- **App Responsiveness**: 4.8/5 rating
- **Real-time Accuracy**: 92% ETA accuracy within 5 minutes
- **Support Tickets**: <2% of orders require support intervention

**Source**: DoorDash Engineering Blog, Mobile Engineering Talks, Real-time Architecture Presentations (2023-2024)