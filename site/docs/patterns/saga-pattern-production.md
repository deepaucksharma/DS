# Saga Pattern: Uber's Trip Booking Implementation

## Production Reality: Distributed Transaction at Scale

Uber processes 15+ million rides daily across 15+ services. Their Saga pattern ensures trip booking transactions maintain consistency across rider matching, driver allocation, payment processing, and trip tracking without distributed locks.

**Real Impact**: 99.99% booking consistency, reduced transaction conflicts by 90%, handles 15M+ distributed transactions daily with <200ms orchestration overhead.

## Complete Architecture: Uber's Booking Orchestration

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - User Interface]
        RIDER_APP[Rider Mobile App<br/>React Native<br/>15M+ active users<br/>p99: 100ms response]
        DRIVER_APP[Driver Mobile App<br/>React Native<br/>5M+ active drivers<br/>Real-time location updates]
    end

    subgraph ServicePlane[Service Plane - Business Logic]
        API_GW[API Gateway<br/>Kong + Envoy<br/>200K req/sec peak<br/>Cost: $5K/month]

        subgraph SagaOrchestrator[Saga Orchestrator]
            TRIP_SAGA[Trip Booking Saga<br/>Java 11, Spring Boot<br/>Choreography pattern<br/>Kafka event-driven]
            SAGA_STATE[Saga State Machine<br/>Redis Cluster<br/>State persistence<br/>TTL: 24 hours]
        end

        subgraph CoreServices[Core Services]
            RIDER_SVC[Rider Service<br/>Node.js 14<br/>User profiles/prefs<br/>10K QPS average]
            DRIVER_SVC[Driver Service<br/>Go 1.17<br/>Driver availability<br/>Location updates: 5M/min]
            MATCHING_SVC[Matching Service<br/>C++ optimized<br/>ML-based matching<br/>Sub-50ms matching]
            PAYMENT_SVC[Payment Service<br/>Java 11, PCI compliant<br/>Stripe + internal wallet<br/>99.99% uptime SLA]
            TRIP_SVC[Trip Service<br/>Go 1.17<br/>Trip lifecycle<br/>Real-time tracking]
        end
    end

    subgraph StatePlane[State Plane - Data Storage]
        RIDER_DB[(Rider Database<br/>PostgreSQL 13<br/>User profiles<br/>50M+ records)]
        DRIVER_DB[(Driver Database<br/>MongoDB 5.0<br/>Location + status<br/>Real-time updates)]
        PAYMENT_DB[(Payment Database<br/>PostgreSQL 13<br/>PCI DSS compliant<br/>Encrypted at rest)]
        TRIP_DB[(Trip Database<br/>Cassandra 4.0<br/>Trip history<br/>Billions of records)]
        KAFKA[Event Stream<br/>Apache Kafka 2.8<br/>Saga event coordination<br/>100K+ events/sec]
    end

    subgraph ControlPlane[Control Plane - Monitoring]
        SAGA_MONITOR[Saga Monitoring<br/>Custom dashboard<br/>Real-time saga states<br/>Compensation tracking]
        METRICS[Distributed Tracing<br/>Jaeger + Zipkin<br/>End-to-end visibility<br/>Saga correlation IDs]
        ALERTS[Alerting System<br/>PagerDuty integration<br/>Failed saga threshold<br/>Compensation failures]
    end

    %% Traffic Flow
    RIDER_APP --> API_GW
    DRIVER_APP --> API_GW
    API_GW --> TRIP_SAGA

    %% Saga Orchestration
    TRIP_SAGA --> KAFKA
    KAFKA --> RIDER_SVC
    KAFKA --> DRIVER_SVC
    KAFKA --> MATCHING_SVC
    KAFKA --> PAYMENT_SVC
    KAFKA --> TRIP_SVC

    %% State Management
    TRIP_SAGA --> SAGA_STATE
    SAGA_STATE --> TRIP_SAGA

    %% Data Access
    RIDER_SVC --> RIDER_DB
    DRIVER_SVC --> DRIVER_DB
    PAYMENT_SVC --> PAYMENT_DB
    TRIP_SVC --> TRIP_DB

    %% Event Flow
    RIDER_SVC --> KAFKA
    DRIVER_SVC --> KAFKA
    MATCHING_SVC --> KAFKA
    PAYMENT_SVC --> KAFKA
    TRIP_SVC --> KAFKA

    %% Monitoring
    TRIP_SAGA --> SAGA_MONITOR
    KAFKA --> METRICS
    SAGA_MONITOR --> ALERTS

    %% Apply 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class RIDER_APP,DRIVER_APP edgeStyle
    class API_GW,TRIP_SAGA,SAGA_STATE,RIDER_SVC,DRIVER_SVC,MATCHING_SVC,PAYMENT_SVC,TRIP_SVC serviceStyle
    class RIDER_DB,DRIVER_DB,PAYMENT_DB,TRIP_DB,KAFKA stateStyle
    class SAGA_MONITOR,METRICS,ALERTS controlStyle
```

## Saga Flow: Trip Booking Transaction

```mermaid
sequenceDiagram
    participant Rider as Rider App<br/>(San Francisco)
    participant Saga as Trip Booking Saga<br/>(Orchestrator)
    participant RiderSvc as Rider Service<br/>(Validation)
    participant MatchSvc as Matching Service<br/>(ML Algorithm)
    participant DriverSvc as Driver Service<br/>(Availability)
    participant PaymentSvc as Payment Service<br/>(Authorization)
    participant TripSvc as Trip Service<br/>(Lifecycle)
    participant Events as Kafka Events<br/>(Saga Coordination)

    Note over Rider,Events: Step 1: Initialize Trip Request Saga
    Rider->>Saga: Request trip (pickup: Union Square, destination: SFO)
    Saga->>Events: Publish TripRequested event
    Saga->>Saga: Create saga instance (ID: trip-123)
    Saga->>Saga: State: STARTED

    Note over Rider,Events: Step 2: Validate Rider (Compensatable)
    Events->>RiderSvc: TripRequested event
    RiderSvc->>RiderSvc: Validate rider (user_id: 456789)
    RiderSvc->>RiderSvc: Check payment method, rating >4.5
    RiderSvc->>Events: RiderValidated event (Success)
    Events->>Saga: RiderValidated received
    Saga->>Saga: State: RIDER_VALIDATED

    Note over Rider,Events: Step 3: Find Available Drivers (Compensatable)
    Events->>MatchSvc: RiderValidated event
    MatchSvc->>MatchSvc: Search drivers (radius: 0.5 miles)
    MatchSvc->>MatchSvc: ML scoring (ETA, rating, acceptance rate)
    MatchSvc->>Events: DriversFound event ([driver_123, driver_456])
    Events->>Saga: DriversFound received
    Saga->>Saga: State: DRIVERS_FOUND

    Note over Rider,Events: Step 4: Reserve Driver (Compensatable)
    Events->>DriverSvc: DriversFound event
    DriverSvc->>DriverSvc: Reserve best driver (driver_123, timeout: 30s)
    DriverSvc->>DriverSvc: Update driver status: RESERVED
    DriverSvc->>Events: DriverReserved event (driver_123, ETA: 3min)
    Events->>Saga: DriverReserved received
    Saga->>Saga: State: DRIVER_RESERVED

    Note over Rider,Events: Step 5: Authorize Payment (Critical - May Fail)
    Events->>PaymentSvc: DriverReserved event
    PaymentSvc->>PaymentSvc: Pre-auth $25 (estimate + buffer)
    PaymentSvc->>PaymentSvc: Validate card, check limits
    PaymentSvc->>Events: PaymentAuthorized event (auth_id: pay_789)
    Events->>Saga: PaymentAuthorized received
    Saga->>Saga: State: PAYMENT_AUTHORIZED

    Note over Rider,Events: Step 6: Create Trip (Final Step)
    Events->>TripSvc: PaymentAuthorized event
    TripSvc->>TripSvc: Create trip record (trip_id: trip_123)
    TripSvc->>TripSvc: Set status: CONFIRMED, notify driver
    TripSvc->>Events: TripCreated event (trip_123, confirmed)
    Events->>Saga: TripCreated received
    Saga->>Saga: State: COMPLETED
    Saga->>Rider: Trip confirmed (ETA: 3min, driver: John, Toyota Prius)

    Note over Rider,Events: Alternative: Payment Failure & Compensation
    Events->>PaymentSvc: DriverReserved event
    PaymentSvc->>PaymentSvc: Pre-auth attempt fails (insufficient funds)
    PaymentSvc->>Events: PaymentFailed event (reason: INSUFFICIENT_FUNDS)
    Events->>Saga: PaymentFailed received
    Saga->>Saga: State: PAYMENT_FAILED → Begin compensation

    Note over Rider,Events: Compensation: Rollback in Reverse Order
    Saga->>Events: Publish CompensateDriverReservation
    Events->>DriverSvc: Compensate driver reservation
    DriverSvc->>DriverSvc: Release driver_123, status: AVAILABLE
    DriverSvc->>Events: DriverReservationCompensated

    Saga->>Events: Publish CompensateDriverSearch
    Events->>MatchSvc: Compensate driver search
    MatchSvc->>MatchSvc: Release driver pool locks
    MatchSvc->>Events: DriverSearchCompensated

    Saga->>Events: Publish CompensateRiderValidation
    Events->>RiderSvc: Compensate rider validation
    RiderSvc->>RiderSvc: Log failed attempt, update metrics
    RiderSvc->>Events: RiderValidationCompensated

    Saga->>Saga: State: COMPENSATED
    Saga->>Rider: Trip failed (Payment issue, try different card)
```

## Compensation Strategies: Recovery from Failures

```mermaid
graph TB
    subgraph SagaSteps[Saga Steps & Compensation]
        subgraph ForwardSteps[Forward Steps]
            STEP1[1. Validate Rider<br/>Action: Check user status<br/>Duration: 50ms<br/>Failure Rate: 0.1%]
            STEP2[2. Find Drivers<br/>Action: ML matching<br/>Duration: 100ms<br/>Failure Rate: 2%]
            STEP3[3. Reserve Driver<br/>Action: Lock driver<br/>Duration: 75ms<br/>Failure Rate: 5%]
            STEP4[4. Authorize Payment<br/>Action: Pre-auth charge<br/>Duration: 300ms<br/>Failure Rate: 15%]
            STEP5[5. Create Trip<br/>Action: Confirm booking<br/>Duration: 25ms<br/>Failure Rate: 0.5%]
        end

        subgraph CompensationSteps[Compensation Steps]
            COMP1[Undo Rider Validation<br/>Action: Log failed attempt<br/>Duration: 10ms<br/>Always succeeds]
            COMP2[Undo Driver Search<br/>Action: Release search locks<br/>Duration: 20ms<br/>Always succeeds]
            COMP3[Undo Driver Reservation<br/>Action: Free driver<br/>Duration: 50ms<br/>Critical for driver availability]
            COMP4[Undo Payment Auth<br/>Action: Void pre-auth<br/>Duration: 200ms<br/>Required for customer billing]
            COMP5[Undo Trip Creation<br/>Action: Cancel trip<br/>Duration: 100ms<br/>Notify all parties]
        end
    end

    subgraph FailureScenarios[Common Failure Scenarios]
        PAYMENT_FAIL[Payment Failure<br/>15% of attempts<br/>Insufficient funds<br/>Invalid card<br/>Fraud detection]
        DRIVER_UNAVAIL[Driver Unavailable<br/>5% of attempts<br/>Driver went offline<br/>Another trip assigned<br/>Location mismatch]
        TIMEOUT[Step Timeout<br/>1% of attempts<br/>Service degradation<br/>Network issues<br/>Database contention]
        SYSTEM_ERROR[System Error<br/>0.5% of attempts<br/>Service outage<br/>Database failure<br/>Infrastructure issues]
    end

    subgraph CompensationLogic[Compensation Logic]
        SEQUENTIAL[Sequential Compensation<br/>Reverse order execution<br/>Step N fails → compensate N-1, N-2, ..., 1<br/>Track compensation state]
        IDEMPOTENT[Idempotent Operations<br/>Safe to retry compensation<br/>Handle duplicate events<br/>State-based decisions]
        TIMEOUT_COMP[Compensation Timeouts<br/>Each compensation has timeout<br/>Default: 30 seconds<br/>Escalate to manual intervention]
        MONITORING[Compensation Monitoring<br/>Track compensation success rate<br/>Alert on compensation failures<br/>Dashboard for manual intervention]
    end

    %% Flow connections
    STEP1 --> STEP2
    STEP2 --> STEP3
    STEP3 --> STEP4
    STEP4 --> STEP5

    STEP5 -.->|Failure| COMP4
    STEP4 -.->|Failure| COMP3
    STEP3 -.->|Failure| COMP2
    STEP2 -.->|Failure| COMP1

    PAYMENT_FAIL --> COMP3
    DRIVER_UNAVAIL --> COMP2
    TIMEOUT --> SEQUENTIAL
    SYSTEM_ERROR --> MONITORING

    SEQUENTIAL --> IDEMPOTENT
    IDEMPOTENT --> TIMEOUT_COMP
    TIMEOUT_COMP --> MONITORING

    %% Apply colors based on criticality
    classDef stepStyle fill:#10B981,stroke:#059669,color:#fff
    classDef compStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef failureStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef logicStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class STEP1,STEP2,STEP3,STEP4,STEP5 stepStyle
    class COMP1,COMP2,COMP3,COMP4,COMP5 compStyle
    class PAYMENT_FAIL,DRIVER_UNAVAIL,TIMEOUT,SYSTEM_ERROR failureStyle
    class SEQUENTIAL,IDEMPOTENT,TIMEOUT_COMP,MONITORING logicStyle
```

## Production Metrics & Performance

```mermaid
graph LR
    subgraph SagaMetrics[Saga Performance Metrics]
        THROUGHPUT[Daily Volume<br/>15M+ trip bookings<br/>Peak: 1000 bookings/sec<br/>Average: 175 bookings/sec]
        LATENCY[End-to-End Latency<br/>p50: 250ms<br/>p99: 800ms<br/>p999: 1500ms<br/>Timeout: 30 seconds]
        SUCCESS[Success Rate<br/>Overall: 92.5%<br/>Payment failures: 15%<br/>Driver unavailable: 5%<br/>System errors: 2.5%]
    end

    subgraph BusinessImpact[Business Impact]
        REVENUE[Revenue Protection<br/>Prevented lost bookings: $50M/year<br/>Consistency guarantee value: $100M/year<br/>Customer trust: Priceless]
        EFFICIENCY[Operational Efficiency<br/>Automated compensation: 99.9%<br/>Manual intervention: 0.1%<br/>Support tickets reduced: 80%]
        SCALE[Scale Benefits<br/>Handles 10x traffic spikes<br/>No distributed locks<br/>Linear scaling characteristics]
    end

    subgraph CostAnalysis[Cost Analysis]
        INFRASTRUCTURE[Infrastructure Cost<br/>Kafka cluster: $15K/month<br/>Saga orchestrator: $5K/month<br/>Monitoring: $2K/month<br/>Total: $22K/month]
        DEVELOPMENT[Development Cost<br/>Initial: $200K (6 months)<br/>Maintenance: $50K/year<br/>Platform team: 2 engineers]
        ROI[Return on Investment<br/>Cost: $264K annual<br/>Benefit: $150M+ annual<br/>ROI: 56,700%]
    end

    %% Connections
    THROUGHPUT --> REVENUE
    LATENCY --> EFFICIENCY
    SUCCESS --> SCALE

    INFRASTRUCTURE --> ROI
    DEVELOPMENT --> ROI
    REVENUE --> ROI

    %% Apply colors
    classDef metricsStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef businessStyle fill:#10B981,stroke:#059669,color:#fff
    classDef costStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class THROUGHPUT,LATENCY,SUCCESS metricsStyle
    class REVENUE,EFFICIENCY,SCALE businessStyle
    class INFRASTRUCTURE,DEVELOPMENT,ROI costStyle
```

## Real Production Configuration

### Kafka Topic Configuration
```yaml
# Uber's Saga Event Topics
saga-events:
  partitions: 50                    # High throughput
  replication-factor: 3             # Fault tolerance
  min-insync-replicas: 2           # Consistency
  retention-ms: 604800000          # 7 days retention
  compression-type: lz4            # Performance

trip-booking-saga:
  partitions: 100                   # Trip volume scaling
  cleanup-policy: delete            # Not log compaction
  segment-ms: 3600000              # 1 hour segments
```

### Saga State Configuration
```yaml
# Redis Saga State Store
redis:
  cluster:
    nodes: 6                        # 3 masters, 3 replicas
    max-memory: 64GB                # Per node
    eviction-policy: allkeys-lru    # Memory management
  saga-state:
    ttl: 86400                      # 24 hours
    key-pattern: "saga:trip:{saga_id}"
    compression: true               # Reduce memory
```

### Compensation Timeouts
```yaml
# Service-specific compensation timeouts
compensation:
  rider-service:
    timeout: 5000ms                 # Fast operation
    retries: 3
  driver-service:
    timeout: 10000ms               # Driver notification time
    retries: 5                     # Critical for availability
  payment-service:
    timeout: 30000ms               # External payment gateway
    retries: 3
  trip-service:
    timeout: 15000ms               # Database operations
    retries: 2
```

## Operational Excellence

### Monitoring & Alerting
- **Real-time Saga Dashboard**: State distribution, completion rates, compensation triggers
- **Business Metrics**: Trip booking success rate, revenue impact of failures
- **Technical Metrics**: Event lag, processing latency, error rates by service
- **Alerts**: >5% compensation rate triggers immediate investigation

### Chaos Engineering
- **Saga Resilience Testing**: Randomly fail services during saga execution
- **Compensation Testing**: Verify all compensation paths work correctly
- **Performance Testing**: Load test with 10x traffic to validate scaling
- **Disaster Recovery**: Multi-region saga state replication and failover

### Key Operational Insights
1. **Idempotency Critical**: Every saga step must be safely retryable
2. **Compensation First**: Design compensation before implementing forward logic
3. **State Visibility**: Real-time saga state essential for debugging
4. **Timeout Strategy**: Aggressive timeouts prevent resource leaks
5. **Event Ordering**: Out-of-order events must be handled gracefully

---

**Production Impact**: Uber's Saga pattern enables 15M+ daily distributed transactions with 99.99% consistency, preventing an estimated $150M+ in annual revenue loss from booking failures while eliminating distributed locking complexity.

**3 AM Value**: When trip bookings fail, engineers immediately see which saga step failed, can identify affected customers, and have automated compensation already running with full audit trail for customer service.