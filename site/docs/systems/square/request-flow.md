# Square Request Flow - Payment Authorization to Settlement

## The Golden Path: From Card Swipe to Bank Settlement

This diagram shows the complete journey of a payment transaction through Square's infrastructure, from the moment a customer swipes their card to final settlement in the merchant's bank account.

```mermaid
sequenceDiagram
    participant Customer
    participant Reader as Square Reader<br/>(Hardware)
    participant POS as Square POS<br/>(iOS/Android)
    participant Edge as Edge Gateway<br/>(ALB + WAF)
    participant API as API Gateway<br/>(Kong)
    participant Auth as Authorization Service<br/>(Java 17)
    participant Risk as Risk Engine<br/>(Python ML)
    participant Vault as Tokenization Vault<br/>(HSM)
    participant Network as Card Network<br/>(Visa/MC)
    participant Settlement as Settlement Service<br/>(Go)
    participant Ledger as Ledger DB<br/>(PostgreSQL)
    participant Bank as Merchant Bank<br/>(External)

    Note over Customer,Bank: Payment Authorization Flow (Target: <200ms end-to-end)

    Customer->>Reader: 1. Card Swipe/Insert/Tap
    Note right of Reader: Encrypt card data immediately<br/>AES-256 encryption

    Reader->>POS: 2. Encrypted card data
    Note right of POS: Local validation<br/>SLA: 10ms

    POS->>Edge: 3. HTTPS Payment Request
    Note right of Edge: Load balancing + DDoS protection<br/>SLA: 5ms

    Edge->>API: 4. Route to payment API
    Note right of API: Rate limiting: 1000 RPS per merchant<br/>SLA: 5ms

    API->>Auth: 5. Authorization request
    Note right of API: JWT validation + routing<br/>Timeout: 30s

    Auth->>Vault: 6. Tokenize card data
    Note right of Vault: PCI-compliant tokenization<br/>SLA: 10ms, p99: 15ms

    Vault-->>Auth: 7. Card token + last 4 digits

    Auth->>Risk: 8. Risk assessment request
    Note right of Risk: Real-time ML scoring<br/>Features: velocity, geography, amount<br/>SLA: 15ms, p99: 25ms

    Risk-->>Auth: 9. Risk score (0-100)
    Note right of Risk: Score >80 = declined<br/>Score 60-80 = additional verification<br/>Score <60 = approved

    alt Risk Score > 80 (High Risk)
        Auth-->>POS: Decline - High Risk
        POS-->>Customer: Payment Declined
    else Risk Score <= 80 (Acceptable Risk)
        Auth->>Network: 10. Card network authorization
        Note right of Network: Route to Visa/Mastercard<br/>Interchange + network fees<br/>SLA: 150ms, p99: 200ms

        Network-->>Auth: 11. Authorization response
        Note right of Network: Approved/Declined + Auth Code<br/>Available balance check

        Auth->>Ledger: 12. Record authorized transaction
        Note right of Ledger: ACID transaction<br/>Merchant balance reservation<br/>SLA: 20ms

        Ledger-->>Auth: 13. Transaction ID

        Auth-->>POS: 14. Authorization success
        Note right of Auth: Include: transaction_id, auth_code<br/>amount, fee_breakdown

        POS-->>Customer: 15. Payment approved
        Note right of POS: Receipt generation<br/>Email/SMS notification

        POS->>Settlement: 16. Mark for settlement
        Note right of Settlement: Batch processing queue<br/>Settlement delay: T+1 business day
    end

    Note over Settlement,Bank: Settlement Flow (Runs every 4 hours)

    Settlement->>Network: 17. Settlement request
    Note right of Settlement: Batch of authorized transactions<br/>Aggregate by merchant

    Network-->>Settlement: 18. Settlement confirmation

    Settlement->>Bank: 19. ACH transfer initiation
    Note right of Bank: Merchant bank account credit<br/>Timeline: T+1 business day<br/>Square fees deducted

    Settlement->>Ledger: 20. Update settlement status
    Note right of Ledger: Final transaction state<br/>Merchant available balance

    Settlement-->>POS: 21. Settlement notification
    Note right of POS: Push notification to merchant<br/>Updated dashboard balances
```

## Performance Metrics & SLAs

### End-to-End Latency Targets
- **Authorization Response**: <200ms (p95)
- **Risk Assessment**: <15ms (p99: 25ms)
- **Tokenization**: <10ms (p99: 15ms)
- **Database Write**: <20ms (p99: 35ms)
- **Network Authorization**: <150ms (p99: 200ms)

### Throughput Specifications
- **Peak TPS**: 50,000 transactions/second (Black Friday)
- **Average TPS**: 15,000 transactions/second
- **API Rate Limits**: 1,000 RPS per merchant
- **Concurrent Authorizations**: 100,000 in-flight
- **Settlement Batch Size**: 1M transactions per batch

## Critical Decision Points

### Risk Engine Decision Matrix
```mermaid
flowchart TD
    Start([Authorization Request]) --> RiskScore{Risk Score}

    RiskScore -->|Score 0-59<br/>Low Risk| AutoApprove[Auto Approve<br/>~85% of transactions]
    RiskScore -->|Score 60-79<br/>Medium Risk| AdditionalAuth[Additional Authentication<br/>SMS/3DS verification<br/>~12% of transactions]
    RiskScore -->|Score 80-100<br/>High Risk| AutoDecline[Auto Decline<br/>~3% of transactions]

    AdditionalAuth --> AuthSuccess{Auth Success?}
    AuthSuccess -->|Yes| Approve[Approve Transaction]
    AuthSuccess -->|No| Decline[Decline Transaction]

    AutoApprove --> NetworkAuth[Send to Card Network]
    Approve --> NetworkAuth
    AutoDecline --> DeclineResponse[Return Decline Response]
    Decline --> DeclineResponse

    NetworkAuth --> NetworkResponse{Network Response}
    NetworkResponse -->|Approved| Success[Transaction Success]
    NetworkResponse -->|Declined| NetworkDecline[Network Decline]

    classDef approveStyle fill:#90EE90,stroke:#006400,color:#000
    classDef declineStyle fill:#FFB6C1,stroke:#DC143C,color:#000
    classDef processStyle fill:#87CEEB,stroke:#4682B4,color:#000

    class AutoApprove,Approve,Success approveStyle
    class AutoDecline,Decline,DeclineResponse,NetworkDecline declineStyle
    class AdditionalAuth,NetworkAuth processStyle
```

### Settlement Timeline
```mermaid
gantt
    title Payment Settlement Timeline
    dateFormat X
    axisFormat %H:%M

    section Authorization
    Card Swipe           :milestone, swipe, 0, 0
    Risk Assessment      :risk, 0, 15
    Network Auth         :network, after risk, 150
    Response to Merchant :response, after network, 35

    section Settlement Batch
    Batch Collection     :batch, 240, 480
    Network Settlement   :settle, after batch, 120
    ACH Initiation      :ach, after settle, 60

    section Bank Transfer
    ACH Processing      :processing, after ach, 1440
    Funds Available     :milestone, available, after processing, 0
```

## Error Handling & Fallback Strategies

### Payment Declination Flow
1. **Network Timeout** (>300ms): Retry once, then decline
2. **Risk Engine Unavailable**: Default to network-only authorization
3. **Tokenization Failure**: Store encrypted PAN temporarily, retry tokenization
4. **Database Unavailable**: Cache authorization, async write on recovery
5. **Settlement Failure**: Automatic retry with exponential backoff

### Offline Payment Support
- **Square Reader**: Store up to 100 offline transactions
- **Offline Limit**: $25 per transaction maximum
- **Sync Window**: 24 hours to reconnect and sync
- **Risk Mitigation**: Enhanced post-authorization review

## Real-World Performance Data

### Black Friday 2023 Metrics
- **Peak TPS**: 47,000 transactions/second
- **Authorization Success Rate**: 97.2%
- **Average Response Time**: 185ms
- **Risk Engine Accuracy**: 99.1% (false positive rate: 0.9%)
- **Settlement Success Rate**: 99.98%

### Geographic Latency (P95)
- **US East Coast**: 45ms
- **US West Coast**: 78ms
- **Canada**: 92ms
- **UK**: 120ms
- **Australia**: 180ms

### Cost Per Transaction
- **Infrastructure Cost**: $0.0012 per transaction
- **Network Fees**: $0.15-0.35 (interchange dependent)
- **Square Processing Fee**: 2.6% + $0.10
- **Risk Assessment**: $0.001 per transaction
- **Settlement Cost**: $0.0008 per transaction

This request flow handles millions of transactions daily while maintaining sub-200ms response times and 99.95% uptime across the global payment infrastructure.