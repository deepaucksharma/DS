# Instacart - Request Flow

## Overview

Instacart's request flow handles 2M+ daily orders through complex workflows involving customer ordering, shopper assignment, real-time inventory management, and multi-party coordination across 80K+ stores.

## Order Placement Request Flow - The Golden Path

```mermaid
sequenceDiagram
    participant Customer as Customer App<br/>10M+ DAU
    participant CDN as CloudFlare CDN<br/>Global edge cache
    participant API as API Gateway<br/>Kong Enterprise
    participant Auth as Auth Service<br/>JWT validation
    participant Cart as Cart Service<br/>Go 1.20
    participant Inventory as Inventory Service<br/>Real-time stock
    participant Pricing as Pricing Service<br/>Dynamic pricing
    participant Order as Order Service<br/>Java 17
    participant Payment as Payment Service<br/>Stripe integration
    participant Dispatch as Dispatch Service<br/>Shopper matching
    participant Notification as Notification Service<br/>Push + SMS
    participant Shopper as Shopper App

    Note over Customer: User adds items to cart<br/>Reviews order<br/>Proceeds to checkout

    Customer->>CDN: POST /api/v1/orders<br/>Latency Budget: 500ms
    CDN->>API: Forward to API Gateway<br/>p99: 20ms
    API->>Auth: Validate customer token<br/>p99: 5ms (Redis cache)
    Auth-->>API: ✓ Valid session<br/>Customer ID: 12345

    API->>Cart: GET /cart/12345<br/>Retrieve cart contents
    Cart->>Inventory: POST /inventory/check<br/>Validate availability<br/>Store: Safeway #1234

    par Real-time Inventory Validation
        Inventory->>Inventory: Check stock levels<br/>5M+ SKUs across stores<br/>p99: 50ms
        Note over Inventory: Items: [Milk: ✓, Bread: ✓, Apples: 2 left]
        Inventory-->>Cart: ✓ All items available<br/>Reserved for 10 minutes
    end

    Cart-->>API: Cart validated<br/>Total: $67.23<br/>Items: 15

    API->>Pricing: POST /pricing/calculate<br/>Apply discounts + fees
    Note over Pricing: Dynamic pricing engine<br/>Surge pricing: 1.2x<br/>Delivery fee: $3.99

    par Pricing Calculation
        Pricing->>Pricing: Calculate final price<br/>Surge pricing: +20%<br/>Promotions: -$5.00<br/>p99: 30ms
        Pricing-->>API: Final total: $72.42<br/>Delivery: $3.99<br/>Service: $2.50<br/>Tax: $4.70
    end

    API->>Payment: POST /payment/authorize<br/>Amount: $72.42<br/>Card: •••• 1234
    Payment->>Payment: Stripe payment auth<br/>Pre-authorization hold<br/>p99: 800ms
    Payment-->>API: ✓ Payment authorized<br/>Auth ID: auth_123456

    API->>Order: POST /orders/create<br/>Customer, cart, payment details

    par Order Creation & Shopper Assignment
        Order->>Order: Create order record<br/>Order ID: IC_789012<br/>Store assignment<br/>p99: 100ms

        Order->>Dispatch: POST /dispatch/assign<br/>Order: IC_789012<br/>Store: Safeway #1234<br/>Priority: Standard

        Note over Dispatch: Shopper matching algorithm<br/>Location-based routing<br/>Skill-based assignment<br/>Real-time optimization

        Dispatch->>Dispatch: Find optimal shopper<br/>Within 15 min drive<br/>Rating > 4.7<br/>Available now<br/>p99: 15 seconds

        Dispatch->>Shopper: Push notification<br/>New order available<br/>$18.50 estimated payout<br/>Accept within 30 seconds
    end

    Shopper-->>Dispatch: Accept order<br/>Shopper ID: 56789<br/>ETA: 45 minutes

    Dispatch-->>Order: ✓ Shopper assigned<br/>Shopper: Jane Smith<br/>ETA: 45 min
    Order-->>API: ✓ Order confirmed<br/>Order ID: IC_789012<br/>Total time: 2.1 seconds

    par Customer & Shopper Notifications
        API->>Notification: Send order confirmation<br/>Customer: SMS + Push + Email
        Notification->>Customer: Order confirmed!<br/>Shopper: Jane Smith<br/>ETA: 45 minutes

        API->>Notification: Send order details<br/>Shopper: Complete order info
        Notification->>Shopper: Order details<br/>15 items, Store layout<br/>Special instructions
    end

    API-->>CDN: 200 OK + Order details
    CDN-->>Customer: Order confirmation<br/>End-to-end: 2.3 seconds

    Note over Customer,Shopper: Real-time tracking begins<br/>Customer can chat with shopper<br/>Live order updates
```

## Real-time Shopping Request Flow

```mermaid
sequenceDiagram
    participant Shopper as Shopper App
    participant API as API Gateway
    participant Order as Order Service
    participant Inventory as Inventory Service
    participant Communication as Communication Service
    participant Customer as Customer App
    participant Payment as Payment Service

    Note over Shopper: Shopper arrives at store<br/>Begins shopping process

    Shopper->>API: POST /orders/IC_789012/start<br/>Location: In store<br/>Shopping begins
    API->>Order: Update order status<br/>Status: SHOPPING_STARTED<br/>Timestamp: now()

    loop For each item in order
        Shopper->>API: GET /items/search<br/>Query: "Organic milk"<br/>Store: Safeway #1234
        API->>Inventory: Search store catalog<br/>Real-time availability<br/>p99: 100ms

        alt Item Available
            Inventory-->>API: Found: Organic Valley Milk<br/>Aisle 12, Section B<br/>Price: $4.99<br/>In stock: 15 units

            API-->>Shopper: Item location + details<br/>Navigate to Aisle 12<br/>Scan barcode to confirm

            Shopper->>API: POST /items/scan<br/>Barcode: 123456789<br/>Confirm item found
            API->>Order: Add item to order<br/>Verified item<br/>Update total

        else Item Out of Stock
            Inventory-->>API: Item unavailable<br/>Suggest alternatives<br/>ML-powered recommendations

            API->>Communication: Request customer approval<br/>Item unavailable<br/>Suggested replacements

            Communication->>Customer: Push notification<br/>"Organic milk unavailable<br/>Suggest: Regular milk?"

            Customer-->>Communication: Approve replacement<br/>Selected: Regular 2% milk

            Communication-->>API: Replacement approved<br/>Customer choice confirmed

            API->>Order: Update item<br/>Replacement logged<br/>Price adjustment
        end
    end

    Note over Shopper: All items collected<br/>Proceed to checkout

    Shopper->>API: POST /orders/IC_789012/checkout<br/>Final item list<br/>Total weight/count
    API->>Order: Calculate final total<br/>Adjustments for replacements<br/>Final amount: $69.87

    par Payment Processing
        Order->>Payment: Adjust payment<br/>Original: $72.42<br/>Final: $69.87<br/>Refund: $2.55

        Payment->>Payment: Process final charge<br/>Capture authorized amount<br/>Issue partial refund<br/>p99: 1 second

        Payment-->>Order: ✓ Payment complete<br/>Charged: $69.87<br/>Refunded: $2.55
    end

    Order-->>API: ✓ Order ready for delivery<br/>Status: READY_FOR_DELIVERY
    API-->>Shopper: Checkout complete<br/>Proceed to delivery

    par Final Notifications
        API->>Communication: Order ready notification<br/>Customer: Delivery starting

        Communication->>Customer: Push notification<br/>"Your order is on the way!<br/>ETA: 15 minutes"
    end
```

## Inventory Synchronization Flow

```mermaid
sequenceDiagram
    participant Store as Store POS System<br/>80K+ stores
    participant StoreAPI as Store Integration API<br/>Kroger/Safeway APIs
    participant Kafka as Kafka Streams<br/>Event processing
    participant Inventory as Inventory Service<br/>Real-time updates
    participant Cache as Redis Cache<br/>300 nodes
    participant ML as ML Pipeline<br/>Demand prediction
    participant Customer as Customer Apps<br/>Live availability

    Note over Store: Store inventory changes<br/>Sales, restocking, price changes

    Store->>StoreAPI: Inventory update webhook<br/>SKU: 123456789<br/>Quantity: 12 → 8<br/>Price: $4.99

    par Multi-store Processing
        StoreAPI->>Kafka: Publish inventory event<br/>Topic: inventory-updates<br/>Partition by store_id<br/>Rate: 50K events/second

        Kafka->>Inventory: Process inventory delta<br/>Store: Safeway #1234<br/>SKU updates: [milk: -4]

        Inventory->>Cache: Update availability cache<br/>SET store:1234:sku:123456<br/>Value: {qty: 8, price: 4.99}<br/>TTL: 15 minutes

        Inventory->>ML: Send usage data<br/>Consumption rate: 4 units/hour<br/>Predicted stockout: 2 hours<br/>Confidence: 85%
    end

    par Real-time Customer Updates
        Cache->>Customer: WebSocket push<br/>Product availability update<br/>Milk: "Low stock (8 left)"

        ML->>Customer: Predictive notifications<br/>"Milk may be out of stock<br/>in 2 hours. Order now?"
    end

    Note over Customer: Customers see real-time<br/>availability and predictions
```

## Shopper Dispatch Algorithm Flow

```mermaid
graph TB
    subgraph "Order Placement"
        ORDER[New Order Created<br/>Store: Safeway #1234<br/>Items: 15<br/>Estimated time: 45 min]
    end

    subgraph "Shopper Eligibility"
        LOCATION[Location Filter<br/>Within 15 min drive<br/>GPS radius: 10 miles<br/>Traffic-aware routing]

        AVAILABILITY[Availability Filter<br/>Currently active<br/>Not on another order<br/>Available next 2 hours]

        SKILLS[Skill Filter<br/>Store familiarity > 80%<br/>Rating > 4.7<br/>Completion rate > 95%]
    end

    subgraph "Optimization Engine"
        BATCH[Batch Optimization<br/>Can this order be batched?<br/>Compatible with existing orders?<br/>Max 3 orders per batch]

        ROUTING[Route Optimization<br/>Google Maps API<br/>Traffic prediction<br/>Delivery efficiency]

        EARNINGS[Earnings Calculation<br/>Base pay + tips + bonuses<br/>Distance multiplier<br/>Peak hour surge]
    end

    subgraph "Assignment Decision"
        RANKING[Shopper Ranking<br/>Multi-factor scoring<br/>Distance: 40%<br/>Rating: 30%<br/>Experience: 30%]

        NOTIFICATION[Push Notification<br/>30-second acceptance window<br/>Order preview<br/>Estimated earnings: $18.50]

        FALLBACK[Fallback Logic<br/>If no acceptance in 30s<br/>Expand radius to 20 miles<br/>Increase pay by 20%]
    end

    ORDER --> LOCATION
    ORDER --> AVAILABILITY
    ORDER --> SKILLS

    LOCATION --> BATCH
    AVAILABILITY --> ROUTING
    SKILLS --> EARNINGS

    BATCH --> RANKING
    ROUTING --> RANKING
    EARNINGS --> RANKING

    RANKING --> NOTIFICATION
    NOTIFICATION --> FALLBACK

    classDef orderStyle fill:#3B82F6,stroke:#1E40AF,color:#fff,stroke-width:2px
    classDef filterStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px
    classDef optimizeStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef decisionStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:2px

    class ORDER orderStyle
    class LOCATION,AVAILABILITY,SKILLS filterStyle
    class BATCH,ROUTING,EARNINGS optimizeStyle
    class RANKING,NOTIFICATION,FALLBACK decisionStyle
```

## Performance Latency Budgets

### Critical Path Latencies

| Operation | Target Latency | P99 Actual | Budget Allocation |
|-----------|----------------|------------|-------------------|
| **Order Placement** | 500ms | 380ms | |
| ↳ Auth validation | 20ms | 5ms | Network: 5ms, DB: 10ms |
| ↳ Cart validation | 100ms | 65ms | Inventory: 50ms, Cache: 15ms |
| ↳ Pricing calculation | 50ms | 30ms | Rules engine: 25ms, DB: 5ms |
| ↳ Payment authorization | 200ms | 180ms | Stripe API: 150ms, Network: 30ms |
| ↳ Order creation | 80ms | 45ms | DB write: 30ms, Validation: 15ms |
| ↳ Shopper assignment | 30000ms | 15000ms | Algorithm: 10s, Notification: 5s |

### Real-time Operation Latencies

| Operation | Target Latency | P99 Actual | Critical? |
|-----------|----------------|------------|-----------|
| Inventory lookup | 100ms | 65ms | ✓ |
| Item search | 150ms | 120ms | ✓ |
| Communication message | 200ms | 180ms | ✓ |
| Location update | 50ms | 35ms | ✓ |
| Payment processing | 2000ms | 1800ms | ✓ |
| Batch optimization | 5000ms | 3200ms | ○ |

## Error Handling and Fallback Patterns

### Circuit Breaker Implementation

```python
# Instacart circuit breaker patterns
class InstacartCircuitBreaker:
    def __init__(self, service_name):
        self.config = {
            'inventory_service': {
                'failure_threshold': 20,    # 20 failures in window
                'timeout_ms': 5000,
                'fallback': 'cached_inventory'
            },
            'payment_service': {
                'failure_threshold': 5,     # Low tolerance for payments
                'timeout_ms': 3000,
                'fallback': 'queue_for_retry'
            },
            'shopper_dispatch': {
                'failure_threshold': 50,    # Higher tolerance
                'timeout_ms': 30000,
                'fallback': 'expand_radius'
            }
        }

    def execute_with_fallback(self, operation, service_type):
        try:
            return operation()
        except CircuitBreakerOpen:
            return self.execute_fallback(service_type)

    def execute_fallback(self, service_type):
        fallback_type = self.config[service_type]['fallback']

        if fallback_type == 'cached_inventory':
            return self.get_cached_inventory()
        elif fallback_type == 'queue_for_retry':
            return self.queue_payment_for_retry()
        elif fallback_type == 'expand_radius':
            return self.expand_shopper_search_radius()
```

### Graceful Degradation Scenarios

#### Inventory Service Degradation
```
Level 1: Show cached availability (15 min stale)
Level 2: Show "availability unknown" for items
Level 3: Disable out-of-stock validation
Level 4: Order-first, validate-later mode
```

#### Payment Service Degradation
```
Level 1: Increase timeout to 5 seconds
Level 2: Queue payments for retry
Level 3: Manual payment processing
Level 4: Cash-on-delivery option
```

#### Shopper Dispatch Degradation
```
Level 1: Expand search radius to 20 miles
Level 2: Increase pay incentive by 50%
Level 3: Manual shopper assignment
Level 4: Delay orders to next available slot
```

## Real-time Communication Architecture

### WebSocket Connection Management

```mermaid
graph TB
    subgraph "Customer Real-time Updates"
        CUSTWS[Customer WebSocket<br/>Order status updates<br/>Shopper location<br/>ETA changes]
    end

    subgraph "Shopper Real-time Updates"
        SHOPWS[Shopper WebSocket<br/>New order notifications<br/>Customer messages<br/>Route updates]
    end

    subgraph "Communication Hub"
        WSGATEWAY[WebSocket Gateway<br/>Socket.io clusters<br/>Redis pub/sub<br/>Connection pooling]

        MSGQUEUE[Message Queue<br/>RabbitMQ<br/>Guaranteed delivery<br/>Message ordering]

        PRESENCE[Presence Service<br/>Online status<br/>Active connections<br/>Heartbeat monitoring]
    end

    CUSTWS --> WSGATEWAY
    SHOPWS --> WSGATEWAY
    WSGATEWAY --> MSGQUEUE
    MSGQUEUE --> PRESENCE

    classDef clientStyle fill:#3B82F6,stroke:#1E40AF,color:#fff,stroke-width:2px
    classDef hubStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px

    class CUSTWS,SHOPWS clientStyle
    class WSGATEWAY,MSGQUEUE,PRESENCE hubStyle
```

This request flow architecture demonstrates Instacart's sophisticated coordination between customers, shoppers, and stores through real-time inventory management, intelligent dispatch algorithms, and robust communication systems handling millions of daily grocery delivery transactions.