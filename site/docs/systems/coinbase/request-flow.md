# Coinbase Request Flow - The Golden Path

## Trade Execution Journey
**Flow**: User order → Authentication → Risk checks → Matching → Settlement → Confirmation
**SLO**: Market orders < 50ms end-to-end, Limit orders < 100ms
**Scale**: 1M+ orders/second peak capacity, 50K sustained concurrent users

```mermaid
sequenceDiagram
    participant Client as Mobile App<br/>8M DAU
    participant CDN as CloudFlare CDN<br/>Global Edge<br/>Cache Hit: 95%
    participant LB as AWS ALB<br/>TLS Termination<br/>p99: 2ms
    participant API as Kong Gateway<br/>Rate Limiting<br/>p99: 5ms
    participant Auth as Auth Service<br/>JWT Validation<br/>p99: 3ms
    participant Risk as Risk Engine<br/>AML/KYC Checks<br/>p99: 15ms
    participant Trading as Matching Engine<br/>Order Processing<br/>p99: 10ms
    participant Wallet as Wallet Service<br/>Balance Updates<br/>p99: 8ms
    participant Settlement as Settlement Engine<br/>Trade Clearing<br/>p99: 20ms
    participant Notify as Notification<br/>Push/WebSocket<br/>p99: 5ms
    participant Kafka as Event Stream<br/>Trade Events<br/>Throughput: 2M/sec

    Note over Client,Kafka: Market Order: Buy 1 BTC @ Market Price
    Client->>CDN: POST /api/v1/orders<br/>Latency Budget: 50ms total
    Note right of CDN: Static assets cached<br/>API calls passed through

    CDN->>LB: Forward API request<br/>TLS 1.3, HTTP/2<br/>Budget: 48ms remaining
    LB->>API: Route to Kong instance<br/>Health check: 200 OK<br/>Budget: 46ms remaining

    API->>Auth: Validate JWT token<br/>Redis session lookup<br/>Budget: 43ms remaining
    Auth-->>API: User: 12345678<br/>Permissions: TRADE<br/>2FA: Verified

    API->>Risk: Check order compliance<br/>Amount: $50,000<br/>Budget: 40ms remaining
    Risk->>Risk: Daily limit check: OK<br/>AML scoring: Low risk<br/>Sanctions: Clear
    Risk-->>API: Risk approved<br/>Score: 15/100<br/>Budget: 25ms remaining

    API->>Trading: Submit market order<br/>Symbol: BTC-USD<br/>Budget: 22ms remaining

    Note over Trading: Order Book Matching Process
    Trading->>Trading: Lock order book<br/>Current price: $43,250<br/>Available: 2.5 BTC
    Trading->>Trading: Match against best ask<br/>Price: $43,251<br/>Quantity: 1.0 BTC
    Trading->>Trading: Execute trade<br/>Trade ID: T-987654321<br/>Fee: $21.63

    Trading->>Wallet: Debit USD balance<br/>Amount: $43,271.63<br/>Budget: 12ms remaining
    Trading->>Wallet: Credit BTC balance<br/>Amount: 1.0 BTC<br/>Budget: 10ms remaining

    Wallet->>Wallet: Update hot wallet<br/>BTC balance: +1.0<br/>USD balance: -$43,271.63
    Wallet-->>Trading: Balance updated<br/>New balances confirmed<br/>Budget: 8ms remaining

    Trading->>Settlement: Record trade<br/>Counterparty: Market Maker<br/>Budget: 6ms remaining
    Settlement->>Settlement: Update order book<br/>New best ask: $43,252<br/>Spread: $1.50
    Settlement-->>Trading: Settlement complete<br/>State: FILLED<br/>Budget: 4ms remaining

    Trading->>Kafka: Publish trade event<br/>Topic: trades.btc_usd<br/>Budget: 2ms remaining
    Trading-->>API: Order filled<br/>Status: COMPLETED<br/>Budget: 1ms remaining

    API-->>CDN: 200 OK + Trade details<br/>Fill price: $43,251<br/>Total: 49ms elapsed
    CDN-->>Client: Trade confirmation<br/>Order ID: O-123456789

    Note over Kafka,Notify: Async Notification Flow
    Kafka->>Notify: Trade event consumed<br/>Partition: 7<br/>Offset: 9876543
    Notify->>Notify: Generate notifications<br/>Push: Mobile app<br/>Email: Trade confirm
    Notify->>Client: WebSocket push<br/>Real-time balance update<br/>Latency: +5ms

    Note over Trading,Settlement: Post-Trade Processing (Async)
    Settlement->>Settlement: Update daily PnL<br/>Mark-to-market<br/>Unrealized: +$125
    Settlement->>Settlement: Generate tax records<br/>Cost basis: $43,251<br/>Event: BUY
    Settlement->>Settlement: Compliance reporting<br/>Large trader report<br/>Threshold: $50K+
```

## Request Flow Breakdown

### Phase 1: Authentication & Routing (10ms budget)
```mermaid
graph LR
    subgraph EdgePhase[Edge Processing - 5ms SLO]
        A[Client Request] --> B[CloudFlare CDN<br/>DDoS Protection<br/>Rate: 100K req/sec]
        B --> C[AWS ALB<br/>SSL Termination<br/>Health Checks]
        C --> D[Kong Gateway<br/>JWT Validation<br/>Rate Limiting]
    end

    subgraph AuthPhase[Authentication - 5ms SLO]
        D --> E[Auth Service<br/>Redis Session Store<br/>2FA Verification]
        E --> F[Permission Check<br/>RBAC: Trading Enabled<br/>Account Status: Active]
    end

    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff

    class B,C edgeStyle
    class D,E,F serviceStyle
```

### Phase 2: Risk & Compliance (15ms budget)
```mermaid
graph TD
    subgraph RiskEngine[Risk Assessment Engine]
        A[Order Details<br/>BTC: 1.0<br/>Value: $43K] --> B[Daily Limits<br/>Check: $100K limit<br/>Used: $12K today]
        B --> C[AML Scoring<br/>User Risk: Low<br/>Transaction Pattern: Normal]
        C --> D[Sanctions Check<br/>OFAC List: Clear<br/>PEP Status: No]
        D --> E[Velocity Check<br/>Frequency: Normal<br/>Amount: Within range]
        E --> F[Final Approval<br/>Risk Score: 15/100<br/>Status: APPROVED]
    end

    subgraph ComplianceData[External Data Sources]
        G[OFAC Database<br/>Updated: Hourly<br/>Entries: 30K+]
        H[Internal ML Model<br/>Features: 200+<br/>Accuracy: 99.2%]
        I[Transaction History<br/>Lookback: 90 days<br/>Patterns: Learned]
    end

    C --> H
    D --> G
    E --> I

    classDef riskStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef dataStyle fill:#6B7280,stroke:#374151,color:#fff

    class A,B,C,D,E,F riskStyle
    class G,H,I dataStyle
```

### Phase 3: Order Matching (10ms budget)
```mermaid
graph TB
    subgraph MatchingEngine[Coinbase Matching Engine]
        A[Market Order<br/>Buy 1.0 BTC<br/>Type: MARKET] --> B[Order Book Lock<br/>Symbol: BTC-USD<br/>Atomic Operation]
        B --> C[Best Price Query<br/>Best Ask: $43,251<br/>Quantity: 2.5 BTC]
        C --> D[Price-Time Priority<br/>FIFO Matching<br/>Maker Fee: 0.5%]
        D --> E[Trade Execution<br/>Price: $43,251<br/>Size: 1.0 BTC]
        E --> F[Order Book Update<br/>New Best Ask: $43,252<br/>Remaining: 1.5 BTC]
    end

    subgraph OrderBook[In-Memory Order Book]
        G[Bid Side<br/>$43,250: 0.5 BTC<br/>$43,249: 1.2 BTC<br/>$43,248: 2.0 BTC]
        H[Ask Side<br/>$43,251: 2.5 BTC<br/>$43,252: 1.0 BTC<br/>$43,253: 3.0 BTC]
    end

    B --> G
    B --> H
    F --> H

    classDef engineStyle fill:#10B981,stroke:#047857,color:#fff
    classDef bookStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class A,B,C,D,E,F engineStyle
    class G,H bookStyle
```

### Phase 4: Settlement & Notification (15ms budget)
```mermaid
graph LR
    subgraph Settlement[Trade Settlement - 10ms]
        A[Trade Matched<br/>ID: T-987654321<br/>Price: $43,251] --> B[Wallet Updates<br/>BTC: +1.0<br/>USD: -$43,271.63]
        B --> C[Balance Validation<br/>Sufficient Funds: ✓<br/>Account Limits: ✓]
        C --> D[Settlement Record<br/>State: SETTLED<br/>Timestamp: UTC]
    end

    subgraph Notification[User Notification - 5ms]
        D --> E[Event Stream<br/>Kafka Topic<br/>Partition: 7]
        E --> F[Push Notification<br/>Mobile App<br/>WebSocket Update]
        E --> G[Email Queue<br/>Trade Confirmation<br/>Tax Records]
    end

    classDef settlementStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff
    classDef notifyStyle fill:#10B981,stroke:#047857,color:#fff

    class A,B,C,D settlementStyle
    class E,F,G notifyStyle
```

## Performance Guarantees

### Latency SLOs by Request Type
- **Market Orders**: p50 < 20ms, p95 < 40ms, p99 < 50ms
- **Limit Orders**: p50 < 30ms, p95 < 60ms, p99 < 100ms
- **Cancel Orders**: p50 < 5ms, p95 < 10ms, p99 < 20ms
- **Balance Queries**: p50 < 10ms, p95 < 20ms, p99 < 50ms

### Throughput Capacity
- **Peak Order Rate**: 1M orders/second (stress tested)
- **Sustained Rate**: 100K orders/second (normal operations)
- **WebSocket Connections**: 500K concurrent (market data)
- **API Rate Limits**: 100 requests/second per user

### Error Handling & Timeouts
- **Authentication Timeout**: 5 seconds → 401 Unauthorized
- **Risk Check Timeout**: 10 seconds → Order rejected
- **Matching Timeout**: 2 seconds → Order queued for retry
- **Settlement Timeout**: 30 seconds → Manual intervention

### Failure Recovery
- **Order Book Rebuild**: < 100ms from backup
- **Session Recovery**: Automatic reconnection in 5 seconds
- **Transaction Rollback**: Atomic operations, no partial fills
- **Idempotency**: Duplicate detection within 1 hour window

## Critical Success Metrics

### Business Metrics
- **Order Fill Rate**: 99.95% (excluding user cancellations)
- **Price Improvement**: 0.05% better than quoted (on average)
- **Failed Transactions**: < 0.01% due to system errors
- **Customer Satisfaction**: NPS 65+ for trading experience

### Technical Metrics
- **Database Connections**: 95% utilization max (5% headroom)
- **Memory Usage**: 80% max on matching engine instances
- **CPU Utilization**: 70% average, 90% peak during high volume
- **Network Bandwidth**: 40Gbps peak, 10Gbps sustained

This request flow demonstrates how Coinbase processes millions of trades daily while maintaining strict security, compliance, and performance requirements. Every component is designed for high availability and auditability, essential for handling billions in cryptocurrency transactions.