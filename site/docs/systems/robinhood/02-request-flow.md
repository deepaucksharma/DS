# Robinhood Request Flow

## Order Placement to Execution Journey

Critical path analysis for stock order processing from mobile app to market execution, including all latency budgets and fallback mechanisms.

```mermaid
sequenceDiagram
    participant User as Mobile App<br/>(iOS/Android)
    participant Edge as AWS CloudFront<br/>CDN
    participant ALB as Application LB<br/>AWS ALB
    participant API as API Gateway<br/>Kong Enterprise
    participant Auth as Auth Service<br/>Redis Sessions
    participant Order as Order Management<br/>Java/Spring
    participant Risk as Risk Engine<br/>Real-time Checks
    participant Exec as Execution Engine<br/>C++ HFT
    participant Market as Market Maker<br/>Citadel Securities
    participant Exchange as Stock Exchange<br/>NYSE/NASDAQ
    participant Kafka as Event Bus<br/>Kafka MSK
    participant DB as Order Database<br/>PostgreSQL 14
    participant Port as Portfolio Service<br/>Real-time P&L

    Note over User,Port: Latency Budget: p99 < 50ms total

    User->>+Edge: POST /orders/equity<br/>SLA: 5ms
    Edge->>+ALB: Route to API<br/>SLA: 2ms
    ALB->>+API: Load balance<br/>SLA: 3ms

    API->>+Auth: Validate JWT token<br/>SLA: 5ms (Redis lookup)
    Auth-->>-API: User authenticated<br/>Session valid

    API->>+Order: Create order request<br/>SLA: 8ms

    Note over Order,Risk: Pre-trade Risk Checks
    Order->>+Risk: Validate buying power<br/>Pattern Day Trader rules
    Risk->>Risk: Check position limits<br/>Reg T compliance
    Risk->>Risk: Verify account status<br/>GFV restrictions
    Risk-->>-Order: Risk approved<br/>3ms total

    Order->>+DB: Persist order<br/>INSERT with ACID guarantees
    DB-->>-Order: Order ID: 789123456<br/>2ms write latency

    Order->>+Exec: Route for execution<br/>Smart Order Router

    Note over Exec,Exchange: Execution Decision Tree
    alt Payment for Order Flow (95% of retail orders)
        Exec->>+Market: Send order to market maker<br/>Sub-millisecond latency
        Market->>Market: Price improvement analysis<br/>NBBO + $0.001 typical
        Market-->>-Exec: Fill confirmation<br/>Average: 0.3ms
    else Direct Exchange (Large orders/Options)
        Exec->>+Exchange: Submit to exchange<br/>FIX 4.4 protocol
        Exchange->>Exchange: Match in order book<br/>FIFO matching
        Exchange-->>-Exec: Execution report<br/>Average: 1.2ms
    end

    Exec-->>-Order: Fill notification<br/>Price: $150.25, Qty: 100

    Note over Order,Port: Post-trade Processing
    Order->>+Kafka: Publish trade event<br/>Async processing
    Kafka->>+Port: Update portfolio<br/>Real-time P&L calculation
    Port->>Port: Calculate new position<br/>Cost basis adjustment
    Port-->>-Kafka: Portfolio updated

    Order->>+DB: Update order status<br/>FILLED timestamp
    DB-->>-Order: Status persisted<br/>1ms update

    Order-->>-API: Order confirmation<br/>Fill price and time
    API-->>-ALB: HTTP 200 response<br/>Order filled
    ALB-->>-Edge: Response with trade details
    Edge-->>-User: Push notification<br/>Order filled at $150.25

    Note over User,Port: Total latency: p50: 12ms, p99: 47ms

    %% Async settlement flow
    Note over Kafka,Port: T+2 Settlement (Async)
    Kafka->>Kafka: Settlement event<br/>2 business days
    Kafka->>+DB: Update cleared status
    DB-->>-Kafka: Settlement recorded
    Kafka->>+Port: Final position update
    Port-->>-Kafka: Cash available updated
```

## Latency Budget Breakdown

### Critical Path Performance (SLA: p99 < 50ms)

| Component | Service | p50 Latency | p99 Latency | Timeout |
|-----------|---------|-------------|-------------|---------|
| **CDN Lookup** | CloudFront | 3ms | 8ms | 10s |
| **Load Balancing** | AWS ALB | 1ms | 3ms | 30s |
| **API Gateway** | Kong Enterprise | 2ms | 5ms | 10s |
| **Authentication** | Redis Sessions | 1ms | 4ms | 5s |
| **Order Validation** | Spring Boot | 3ms | 8ms | 15s |
| **Risk Checks** | Risk Engine | 2ms | 6ms | 10s |
| **Database Write** | PostgreSQL | 1ms | 3ms | 5s |
| **Execution Routing** | C++ Engine | 0.5ms | 1.5ms | 2s |
| **Market Fill** | Market Maker | 0.3ms | 0.8ms | 1s |
| **Response Path** | Full Stack | 2ms | 7ms | - |
| **TOTAL** | **End-to-End** | **16ms** | **46ms** | **N/A** |

## Risk Management Checks

### Pre-Trade Validation (Required < 10ms)

```mermaid
flowchart TD
    START[Order Received] --> ACCT{Account Status}
    ACCT -->|Active| FUNDS{Sufficient Funds?}
    ACCT -->|Restricted| REJECT1[Reject: Account Restricted]

    FUNDS -->|Yes| PDT{Pattern Day Trader?}
    FUNDS -->|No| REJECT2[Reject: Insufficient Buying Power]

    PDT -->|Yes| PDT_CHECK{< 3 Day Trades?}
    PDT -->|No| REG_T{Reg T Compliant?}

    PDT_CHECK -->|Yes| REG_T
    PDT_CHECK -->|No| REJECT3[Reject: PDT Violation]

    REG_T -->|Yes| POSITION{Position Limits OK?}
    REG_T -->|No| REJECT4[Reject: Reg T Violation]

    POSITION -->|Yes| GFV{Good Faith Violation?}
    POSITION -->|No| REJECT5[Reject: Position Limit]

    GFV -->|No| APPROVE[Approve Order]
    GFV -->|Yes| REJECT6[Reject: GFV Risk]

    REJECT1 --> LOG[Log Rejection Reason]
    REJECT2 --> LOG
    REJECT3 --> LOG
    REJECT4 --> LOG
    REJECT5 --> LOG
    REJECT6 --> LOG

    LOG --> USER_NOTIFY[Notify User of Rejection]
    APPROVE --> ROUTE[Route to Execution]

    classDef approveStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef rejectStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef checkStyle fill:#0066CC,stroke:#004499,color:#fff

    class APPROVE,ROUTE approveStyle
    class REJECT1,REJECT2,REJECT3,REJECT4,REJECT5,REJECT6 rejectStyle
    class ACCT,FUNDS,PDT,PDT_CHECK,REG_T,POSITION,GFV checkStyle
```

## Execution Routing Logic

### Smart Order Router Decision Tree

```mermaid
flowchart TD
    ORDER[New Order] --> SIZE{Order Size}

    SIZE -->|< 100 shares| RETAIL[Retail Order Flow]
    SIZE -->|100-1000 shares| MIXED[Mixed Routing]
    SIZE -->|> 1000 shares| INSTITUTIONAL[Institutional Flow]

    RETAIL --> PFOF{Market Maker Available?}
    PFOF -->|Yes| CITADEL[Route to Citadel<br/>Payment for Order Flow]
    PFOF -->|No| BACKUP_MM[Route to Backup MM<br/>Two Sigma/Virtu]

    MIXED --> PRICE_IMPROVE{Price Improvement > $0.001?}
    PRICE_IMPROVE -->|Yes| CITADEL
    PRICE_IMPROVE -->|No| EXCHANGE[Route to Exchange]

    INSTITUTIONAL --> EXCHANGE
    EXCHANGE --> VENUE{Best Venue?}

    VENUE -->|Liquidity| NYSE[NYSE Arca<br/>Deep liquidity]
    VENUE -->|Speed| NASDAQ[NASDAQ<br/>Low latency]
    VENUE -->|Price| BATS[BATS EDGX<br/>Maker rebates]

    CITADEL --> FILL_CHECK{Fill Confirmed?}
    BACKUP_MM --> FILL_CHECK
    NYSE --> FILL_CHECK
    NASDAQ --> FILL_CHECK
    BATS --> FILL_CHECK

    FILL_CHECK -->|Yes| SETTLEMENT[T+2 Settlement]
    FILL_CHECK -->|No| RETRY[Retry Different Venue]

    RETRY --> VENUE

    classDef routingStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef venueStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef settleStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class CITADEL,BACKUP_MM,NYSE,NASDAQ,BATS routingStyle
    class PFOF,PRICE_IMPROVE,VENUE venueStyle
    class SETTLEMENT settleStyle
```

## Error Handling and Fallbacks

### Circuit Breaker Patterns

| Service | Failure Threshold | Recovery Time | Fallback Action |
|---------|------------------|---------------|-----------------|
| **Market Maker** | 3 failures/10s | 30s | Route to exchange |
| **Risk Engine** | 5 failures/30s | 60s | Use cached risk profile |
| **Order Database** | 2 failures/5s | 10s | Queue in memory |
| **Auth Service** | 10 failures/60s | 120s | Use backup auth |
| **Portfolio Service** | 5 failures/30s | 45s | Stale position data |

### Market Hours Handling

```mermaid
gantt
    title Trading Hours and System Behavior
    dateFormat HH:mm
    axisFormat %H:%M

    section Pre-Market
    Queue Orders    :04:00, 09:30

    section Regular Hours
    Active Trading  :09:30, 16:00

    section After Hours
    Extended Trading :16:00, 20:00

    section Maintenance
    System Updates   :20:00, 04:00
```

## Performance Monitoring

### Key SLIs (Service Level Indicators)

- **Order Latency**: p99 < 50ms end-to-end
- **Fill Rate**: > 99.5% of market orders filled
- **Reject Rate**: < 0.1% false risk rejections
- **System Availability**: 99.95% during market hours
- **Data Freshness**: Market data < 100ms delayed

### Alerting Thresholds

- **CRITICAL**: Order latency p99 > 100ms
- **WARNING**: Fill rate < 99.0%
- **CRITICAL**: System availability < 99.9%
- **WARNING**: Risk check latency > 15ms

*"Every millisecond matters when your users are trading their life savings. Our request flow is optimized for the 23 million people who trust us with their financial future."* - Robinhood Execution Team