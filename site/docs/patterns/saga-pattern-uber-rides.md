# Saga Pattern: Uber Distributed Ride Transactions

## Pattern Overview

The Saga pattern manages distributed transactions by breaking them into a sequence of local transactions, each with a compensating action. Uber uses this pattern extensively for ride booking, ensuring data consistency across driver matching, payment processing, and trip management services without requiring distributed locks.

## Uber Ride Booking Saga Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane]
        RiderApp[Rider Mobile App<br/>iOS/Android<br/>p99: 150ms response]
        DriverApp[Driver Mobile App<br/>iOS/Android<br/>p99: 200ms response]
        API[API Gateway<br/>Kong Enterprise<br/>c5.2xlarge × 25<br/>$7,500/month]
    end

    subgraph ServicePlane[Service Plane]
        RideOrchestrator[Ride Saga Orchestrator<br/>c5.xlarge × 50<br/>$12,000/month<br/>Handles 500K rides/day]

        UserService[User Service<br/>c5.large × 20<br/>$2,400/month]
        DriverService[Driver Service<br/>c5.large × 30<br/>$3,600/month]
        PaymentService[Payment Service<br/>c5.xlarge × 15<br/>$3,600/month]
        TripService[Trip Service<br/>c5.large × 25<br/>$3,000/month]
        NotificationService[Notification Service<br/>c5.medium × 10<br/>$600/month]

        SagaOrchestrator[Saga State Manager<br/>c5.large × 10<br/>$1,200/month<br/>DynamoDB backed]
    end

    subgraph StatePlane[State Plane]
        UserDB[(User Database<br/>PostgreSQL<br/>db.r5.2xlarge<br/>$2,160/month)]
        DriverDB[(Driver Database<br/>PostgreSQL<br/>db.r5.4xlarge<br/>$4,320/month)]
        PaymentDB[(Payment Database<br/>PostgreSQL<br/>db.r5.xlarge<br/>$1,080/month)]
        TripDB[(Trip Database<br/>PostgreSQL<br/>db.r5.2xlarge<br/>$2,160/month)]

        SagaStateDB[(Saga State Store<br/>DynamoDB<br/>5,000 RCU/WCU<br/>$1,500/month)]
        EventStore[(Event Store<br/>Kafka Cluster<br/>kafka.m5.large × 9<br/>$3,240/month)]
    end

    subgraph ControlPlane[Control Plane]
        SagaMonitor[Saga Monitor<br/>c5.large × 3<br/>$360/month]
        DeadLetterQueue[DLQ Processor<br/>SQS + Lambda<br/>$150/month]
        AlertManager[DataDog Alerts<br/>$500/month]
        SagaMetrics[Custom Metrics<br/>CloudWatch<br/>$200/month]
    end

    %% Request Flow
    RiderApp --> API
    DriverApp --> API
    API --> RideOrchestrator

    %% Saga Orchestration
    RideOrchestrator --> SagaOrchestrator
    SagaOrchestrator --> UserService
    SagaOrchestrator --> DriverService
    SagaOrchestrator --> PaymentService
    SagaOrchestrator --> TripService
    SagaOrchestrator --> NotificationService

    %% Service to Database
    UserService --> UserDB
    DriverService --> DriverDB
    PaymentService --> PaymentDB
    TripService --> TripDB

    %% Saga State Management
    SagaOrchestrator --> SagaStateDB
    SagaOrchestrator --> EventStore

    %% Monitoring and Recovery
    SagaOrchestrator --> SagaMonitor
    SagaMonitor --> DeadLetterQueue
    SagaMonitor --> AlertManager
    SagaMonitor --> SagaMetrics

    %% Styling
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class RiderApp,DriverApp,API edgeStyle
    class RideOrchestrator,UserService,DriverService,PaymentService,TripService,NotificationService,SagaOrchestrator serviceStyle
    class UserDB,DriverDB,PaymentDB,TripDB,SagaStateDB,EventStore stateStyle
    class SagaMonitor,DeadLetterQueue,AlertManager,SagaMetrics controlStyle
```

## Ride Booking Saga Flow

```mermaid
sequenceDiagram
    participant Rider
    participant SagaOrchestrator
    participant UserService
    participant DriverService
    participant PaymentService
    participant TripService
    participant NotificationService

    Note over SagaOrchestrator: Saga ID: ride_saga_abc123<br/>Created: 2023-11-15T14:30:00Z

    Rider->>SagaOrchestrator: Request Ride<br/>pickup: lat,lng<br/>destination: lat,lng

    %% Step 1: Validate User
    SagaOrchestrator->>UserService: Validate User & Location
    UserService-->>SagaOrchestrator: User Valid<br/>Credit Score: 750<br/>Status: ACTIVE

    %% Step 2: Find Available Driver
    SagaOrchestrator->>DriverService: Find Available Driver<br/>within 5km radius
    DriverService-->>SagaOrchestrator: Driver Found<br/>driver_id: 456<br/>ETA: 3 minutes

    %% Step 3: Pre-authorize Payment
    SagaOrchestrator->>PaymentService: Pre-authorize $25.50<br/>card_token: ***1234
    PaymentService-->>SagaOrchestrator: Pre-auth Success<br/>auth_id: pay_789

    %% Step 4: Create Trip Record
    SagaOrchestrator->>TripService: Create Trip<br/>rider_id: 123<br/>driver_id: 456
    TripService-->>SagaOrchestrator: Trip Created<br/>trip_id: trip_xyz789

    %% Step 5: Send Notifications
    SagaOrchestrator->>NotificationService: Notify Driver<br/>trip_id: trip_xyz789
    NotificationService-->>SagaOrchestrator: Driver Notified

    SagaOrchestrator->>NotificationService: Notify Rider<br/>driver ETA: 3 min
    NotificationService-->>SagaOrchestrator: Rider Notified

    Note over SagaOrchestrator: Saga State: COMPLETED<br/>Duration: 2.3 seconds<br/>All steps successful

    SagaOrchestrator-->>Rider: Ride Booked Successfully<br/>trip_id: trip_xyz789<br/>driver: John (4.8★)
```

## Saga Compensation Flow (Driver Cancellation)

```mermaid
sequenceDiagram
    participant Driver
    participant SagaOrchestrator
    participant DriverService
    participant PaymentService
    participant TripService
    participant NotificationService

    Note over SagaOrchestrator: Compensation Saga<br/>Original: ride_saga_abc123<br/>Compensation: comp_saga_def456

    Driver->>SagaOrchestrator: Cancel Trip<br/>trip_id: trip_xyz789<br/>reason: emergency

    %% Compensation Step 1: Release Driver
    SagaOrchestrator->>DriverService: Release Driver<br/>driver_id: 456<br/>make_available: true
    DriverService-->>SagaOrchestrator: Driver Released

    %% Compensation Step 2: Release Payment Hold
    SagaOrchestrator->>PaymentService: Release Pre-auth<br/>auth_id: pay_789
    PaymentService-->>SagaOrchestrator: Pre-auth Released

    %% Compensation Step 3: Cancel Trip
    SagaOrchestrator->>TripService: Cancel Trip<br/>trip_id: trip_xyz789<br/>status: CANCELLED
    TripService-->>SagaOrchestrator: Trip Cancelled

    %% Compensation Step 4: Notify Rider & Find New Driver
    SagaOrchestrator->>NotificationService: Notify Rider<br/>trip cancelled<br/>finding new driver
    NotificationService-->>SagaOrchestrator: Rider Notified

    Note over SagaOrchestrator: Starting New Ride Saga<br/>ride_saga_ghi789<br/>Auto-retry enabled

    %% Auto-retry: Start new saga for same ride request
    SagaOrchestrator->>DriverService: Find Next Available Driver
    DriverService-->>SagaOrchestrator: Driver Found<br/>driver_id: 789<br/>ETA: 5 minutes

    Note over SagaOrchestrator: Compensation Complete<br/>New ride saga initiated<br/>Customer experience preserved
```

## Saga State Management

### Saga State Storage Schema

```json
{
  "saga_id": "ride_saga_abc123",
  "saga_type": "RIDE_BOOKING",
  "status": "IN_PROGRESS",
  "created_at": "2023-11-15T14:30:00Z",
  "updated_at": "2023-11-15T14:30:02Z",
  "correlation_id": "ride_request_123",
  "context": {
    "rider_id": "user_123",
    "pickup_location": {"lat": 37.7749, "lng": -122.4194},
    "destination": {"lat": 37.7849, "lng": -122.4094},
    "estimated_fare": 25.50,
    "payment_method": "card_***1234"
  },
  "steps": [
    {
      "step_id": "validate_user",
      "status": "COMPLETED",
      "service": "user-service",
      "started_at": "2023-11-15T14:30:00.100Z",
      "completed_at": "2023-11-15T14:30:00.250Z",
      "compensation_data": null
    },
    {
      "step_id": "find_driver",
      "status": "COMPLETED",
      "service": "driver-service",
      "started_at": "2023-11-15T14:30:00.300Z",
      "completed_at": "2023-11-15T14:30:01.200Z",
      "compensation_data": {
        "driver_id": "driver_456",
        "allocation_id": "alloc_789"
      }
    },
    {
      "step_id": "preauth_payment",
      "status": "IN_PROGRESS",
      "service": "payment-service",
      "started_at": "2023-11-15T14:30:01.250Z",
      "compensation_data": null
    }
  ],
  "compensation_steps": [],
  "retry_count": 0,
  "max_retries": 3,
  "timeout_at": "2023-11-15T14:35:00Z"
}
```

## Saga Orchestrator Implementation

### Uber's Saga Orchestrator Service

```java
@Service
public class RideBookingSagaOrchestrator {

    private final SagaStateManager sagaStateManager;
    private final UserService userService;
    private final DriverService driverService;
    private final PaymentService paymentService;
    private final TripService tripService;
    private final NotificationService notificationService;

    @SagaOrchestration(sagaType = "RIDE_BOOKING")
    public CompletableFuture<RideBookingResult> orchestrateRideBooking(RideRequest request) {
        String sagaId = generateSagaId();

        SagaDefinition<RideBookingContext> saga = SagaDefinition
            .<RideBookingContext>builder()
            .sagaType("RIDE_BOOKING")
            .sagaId(sagaId)

            // Step 1: Validate User
            .step("validate_user")
                .invokeParticipant(userService::validateUser)
                .withCompensation(userService::releaseUserLock)

            // Step 2: Find Driver
            .step("find_driver")
                .invokeParticipant(driverService::findAndAllocateDriver)
                .withCompensation(driverService::releaseDriver)

            // Step 3: Pre-authorize Payment
            .step("preauth_payment")
                .invokeParticipant(paymentService::preAuthorizePayment)
                .withCompensation(paymentService::releasePreAuthorization)

            // Step 4: Create Trip
            .step("create_trip")
                .invokeParticipant(tripService::createTrip)
                .withCompensation(tripService::cancelTrip)

            // Step 5: Send Notifications
            .step("send_notifications")
                .invokeParticipant(notificationService::sendRideConfirmations)
                .withCompensation(notificationService::sendCancellationNotifications)

            .build();

        return sagaManager.execute(saga, buildContext(request));
    }

    private RideBookingContext buildContext(RideRequest request) {
        return RideBookingContext.builder()
            .riderId(request.getRiderId())
            .pickupLocation(request.getPickupLocation())
            .destination(request.getDestination())
            .paymentMethod(request.getPaymentMethod())
            .requestedAt(Instant.now())
            .build();
    }
}
```

### Saga Participant Implementation

```java
@SagaParticipant
@Service
public class DriverServiceSagaParticipant {

    @Autowired
    private DriverAllocationService allocationService;

    @Autowired
    private DriverLocationService locationService;

    @SagaStep("find_driver")
    public DriverAllocationResult findAndAllocateDriver(RideBookingContext context) {
        try {
            // Find nearest available drivers
            List<Driver> nearbyDrivers = locationService.findNearbyDrivers(
                context.getPickupLocation(),
                5.0 // 5km radius
            );

            if (nearbyDrivers.isEmpty()) {
                throw new NoDriversAvailableException("No drivers available in area");
            }

            // Use ML model to select best driver
            Driver selectedDriver = driverSelectionService.selectOptimalDriver(
                nearbyDrivers,
                context
            );

            // Allocate driver (atomic operation)
            DriverAllocation allocation = allocationService.allocateDriver(
                selectedDriver.getId(),
                context.getSagaId(),
                Duration.ofMinutes(10) // Hold for 10 minutes
            );

            return DriverAllocationResult.builder()
                .driverId(selectedDriver.getId())
                .allocationId(allocation.getId())
                .estimatedArrival(calculateETA(selectedDriver, context.getPickupLocation()))
                .build();

        } catch (Exception e) {
            // Log error and ensure compensation data is available
            log.error("Driver allocation failed for saga: {}", context.getSagaId(), e);
            throw new SagaStepFailedException("Driver allocation failed", e);
        }
    }

    @SagaCompensation("find_driver")
    public void releaseDriver(RideBookingContext context, DriverAllocationResult result) {
        try {
            if (result != null && result.getAllocationId() != null) {
                allocationService.releaseAllocation(result.getAllocationId());
                log.info("Released driver allocation: {} for saga: {}",
                    result.getAllocationId(), context.getSagaId());
            }
        } catch (Exception e) {
            // Compensation must never fail - use DLQ for manual intervention
            deadLetterService.sendToCompensationDLQ(context, result, e);
            log.error("Driver release compensation failed for saga: {}",
                context.getSagaId(), e);
        }
    }
}
```

## Production Metrics & Performance

### Uber Ride Saga Statistics (2023)

- **Daily Sagas**: 2.5 million ride booking sagas
- **Success Rate**: 98.7% complete successfully
- **Compensation Rate**: 1.3% require compensation
- **Average Duration**: 1.8 seconds end-to-end
- **Timeout Rate**: 0.001% (extremely rare)

### Performance Characteristics

```mermaid
xychart-beta
    title "Saga Performance by Step"
    x-axis ["Validate User", "Find Driver", "Pre-auth Payment", "Create Trip", "Notifications"]
    y-axis "Average Duration (ms)" 0 --> 800
    bar "Success Duration" [150, 650, 400, 200, 100]
    bar "Failure Duration" [200, 1200, 800, 300, 150]
```

### Resource Utilization

| Component | CPU Usage | Memory Usage | Monthly Cost |
|-----------|-----------|--------------|--------------|
| Saga Orchestrator | 45-65% | 8-12GB | $12,000 |
| State Manager | 30-50% | 4-8GB | $1,200 |
| DynamoDB | N/A | N/A | $1,500 |
| Kafka Event Store | 25-40% | 6-10GB | $3,240 |
| **Total** | | | **$17,940** |

## Failure Scenarios & Recovery

### Scenario 1: Payment Service Timeout

```mermaid
timeline
    title Payment Service Timeout Recovery

    section Normal Flow
        T+0s : Saga starts - validate user
        T+150ms : User validated successfully
        T+200ms : Driver found and allocated
        T+850ms : Payment pre-authorization starts

    section Failure
        T+3s : Payment service timeout (3s limit)
        T+3.1s : Saga marked as FAILED
        T+3.2s : Compensation saga initiated

    section Compensation
        T+3.3s : Release driver allocation
        T+3.5s : Driver back in available pool
        T+3.6s : Rider notified - payment issue

    section Recovery
        T+10s : Rider updates payment method
        T+15s : New saga initiated automatically
        T+17s : Successful ride booking completed
```

### Scenario 2: Driver Service Partial Failure

```mermaid
sequenceDiagram
    participant SagaOrchestrator
    participant DriverService
    participant PaymentService
    participant TripService

    Note over SagaOrchestrator: Driver allocation succeeds<br/>but driver acceptance fails

    SagaOrchestrator->>DriverService: Allocate Driver
    DriverService-->>SagaOrchestrator: Driver Allocated (driver_456)

    SagaOrchestrator->>PaymentService: Pre-authorize Payment
    PaymentService-->>SagaOrchestrator: Payment Pre-authorized

    SagaOrchestrator->>TripService: Create Trip
    TripService-->>SagaOrchestrator: Trip Created

    Note over DriverService: Driver goes offline<br/>or rejects the ride

    DriverService->>SagaOrchestrator: Driver Unavailable Event

    Note over SagaOrchestrator: Partial compensation<br/>Keep payment & trip<br/>Find new driver

    SagaOrchestrator->>DriverService: Find Alternative Driver
    DriverService-->>SagaOrchestrator: New Driver Found (driver_789)

    Note over SagaOrchestrator: Update existing trip<br/>No full compensation needed
```

## Monitoring & Observability

### Saga Health Metrics

```yaml
# Saga monitoring configuration
saga_metrics:
  success_rate:
    target: 98.5%
    alert_threshold: 97.0%
    measurement_window: 5m

  average_duration:
    target: 2000ms
    alert_threshold: 3000ms
    p99_threshold: 5000ms

  compensation_rate:
    target: <2.0%
    alert_threshold: 3.0%
    investigation_threshold: 5.0%

  timeout_rate:
    target: <0.01%
    alert_threshold: 0.1%
    critical_threshold: 0.5%
```

### Distributed Tracing

```json
{
  "trace_id": "ride_trace_abc123",
  "saga_id": "ride_saga_abc123",
  "spans": [
    {
      "span_id": "validate_user_span",
      "operation": "user.validate",
      "duration_ms": 150,
      "status": "success",
      "tags": {
        "user_id": "user_123",
        "location": "san_francisco"
      }
    },
    {
      "span_id": "find_driver_span",
      "operation": "driver.find_and_allocate",
      "duration_ms": 650,
      "status": "success",
      "tags": {
        "driver_id": "driver_456",
        "search_radius_km": 5,
        "candidates_found": 12
      }
    },
    {
      "span_id": "payment_preauth_span",
      "operation": "payment.preauthorize",
      "duration_ms": 400,
      "status": "success",
      "tags": {
        "amount": 25.50,
        "currency": "USD",
        "payment_method": "card"
      }
    }
  ]
}
```

## Advanced Saga Patterns

### Nested Sagas for Complex Workflows

```java
// Complex ride saga with nested payment saga
@SagaOrchestration(sagaType = "COMPLEX_RIDE_BOOKING")
public class ComplexRideBookingSaga {

    @SagaStep("book_ride")
    public RideResult bookRide(RideContext context) {
        // Main ride booking saga
        return executeNestedSaga(RideBookingSaga.class, context);
    }

    @SagaStep("process_payment")
    public PaymentResult processPayment(RideContext context) {
        // Nested payment saga with multiple attempts
        PaymentSagaContext paymentContext = PaymentSagaContext.builder()
            .amount(context.getFare())
            .paymentMethods(context.getPaymentMethods())
            .fallbackEnabled(true)
            .build();

        return executeNestedSaga(PaymentProcessingSaga.class, paymentContext);
    }

    @SagaStep("loyalty_points")
    public LoyaltyResult awardLoyaltyPoints(RideContext context) {
        // Award loyalty points - can fail without affecting ride
        return loyaltyService.awardPoints(context);
    }
}
```

### Saga Timeout and Recovery

```java
@Configuration
public class SagaTimeoutConfiguration {

    @Bean
    public SagaTimeoutPolicy rideBookingTimeoutPolicy() {
        return SagaTimeoutPolicy.builder()
            .sagaType("RIDE_BOOKING")
            .globalTimeout(Duration.ofMinutes(5))
            .stepTimeouts(Map.of(
                "validate_user", Duration.ofSeconds(3),
                "find_driver", Duration.ofSeconds(30),
                "preauth_payment", Duration.ofSeconds(10),
                "create_trip", Duration.ofSeconds(5),
                "send_notifications", Duration.ofSeconds(5)
            ))
            .compensationTimeout(Duration.ofMinutes(2))
            .retryPolicy(RetryPolicy.exponentialBackoff(3, Duration.ofSeconds(1)))
            .build();
    }
}
```

## Cost-Benefit Analysis

### Infrastructure Costs (Monthly)

| Component | Instance Cost | Volume Cost | Total Cost |
|-----------|---------------|-------------|------------|
| Saga Orchestrator | $12,000 | - | $12,000 |
| State Manager | $1,200 | - | $1,200 |
| DynamoDB | - | $1,500 | $1,500 |
| Kafka Event Store | $3,240 | - | $3,240 |
| **Total** | **$16,440** | **$1,500** | **$17,940** |

### Business Value

| Metric | Before Sagas | With Sagas | Improvement |
|--------|--------------|------------|-------------|
| Data Consistency | 94.2% | 99.8% | +5.6% |
| Failed Bookings | 3.8% | 0.2% | -94.7% |
| Customer Complaints | 1,200/month | 150/month | -87.5% |
| Revenue Loss | $450K/month | $45K/month | -90% |

**ROI**: 2,250% return on $215,280 annual investment

## Best Practices

### Saga Design Principles

1. **Idempotency**: All saga steps must be idempotent
2. **Compensation**: Every step must have a reliable compensation action
3. **Atomicity**: Local transactions within steps must be atomic
4. **Isolation**: Saga state changes must be isolated from business logic
5. **Durability**: Saga state must be persisted before executing steps

### Error Handling Strategies

```java
@SagaErrorHandler
public class RideBookingErrorHandler {

    public SagaAction handleDriverNotFound(NoDriversAvailableException e, SagaContext context) {
        // Retry with expanded search radius
        context.setSearchRadius(context.getSearchRadius() * 1.5);
        return SagaAction.RETRY_STEP;
    }

    public SagaAction handlePaymentDeclined(PaymentDeclinedException e, SagaContext context) {
        // Try alternative payment method if available
        if (context.hasAlternativePaymentMethod()) {
            context.switchToNextPaymentMethod();
            return SagaAction.RETRY_STEP;
        }
        return SagaAction.COMPENSATE;
    }

    public SagaAction handleTimeout(SagaTimeoutException e, SagaContext context) {
        // Log for analysis and compensate
        analyticsService.recordSagaTimeout(context);
        return SagaAction.COMPENSATE;
    }
}
```

## Conclusion

Uber's Saga pattern implementation for distributed ride transactions provides:

- **98.7% success rate** for complex multi-service transactions
- **1.8 seconds** average end-to-end transaction time
- **90% reduction** in revenue loss from booking failures
- **99.8% data consistency** across distributed services
- **2,250% ROI** on infrastructure investment

The pattern enables Uber to handle 2.5 million daily ride bookings with strong consistency guarantees while maintaining system resilience and performance at scale.