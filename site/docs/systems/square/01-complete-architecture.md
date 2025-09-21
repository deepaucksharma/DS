# Square Complete Architecture - Payment Platform for Millions of Merchants

## The Money Shot: Full Stack Payment Infrastructure

Square operates one of the largest integrated payment platforms globally, processing $200B+ annually across hardware, software, and financial services.

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - CDN & Load Balancing]
        CDN[Cloudflare CDN<br/>120+ PoPs<br/>$2M/year]
        ALB[AWS ALB<br/>Multi-AZ<br/>$800K/year]
        WAF[AWS WAF<br/>DDoS Protection<br/>$200K/year]
    end

    subgraph ServicePlane[Service Plane - Payment Processing]
        AGW[API Gateway<br/>Kong Enterprise<br/>100K RPS<br/>$400K/year]

        subgraph PaymentServices[Payment Core Services]
            AUTH[Authorization Service<br/>Java 17, Spring Boot<br/>p99: 50ms<br/>$1.2M/year]
            SETTLE[Settlement Service<br/>Go 1.21<br/>Batch Processing<br/>$800K/year]
            RISK[Risk Engine<br/>Python ML<br/>Real-time Scoring<br/>$2M/year]
            MERCHANT[Merchant Service<br/>Node.js<br/>Account Management<br/>$600K/year]
        end

        subgraph CashAppServices[Cash App Services]
            P2P[P2P Payments<br/>Kotlin<br/>50M users<br/>$1.5M/year]
            CRYPTO[Crypto Trading<br/>Rust<br/>Bitcoin/Ethereum<br/>$1M/year]
            BANKING[Banking Services<br/>Java<br/>Direct Deposits<br/>$800K/year]
        end

        subgraph HardwareServices[Hardware Integration]
            POS[POS Integration<br/>C++/Embedded<br/>Reader Management<br/>$500K/year]
            DEVICE[Device Management<br/>IoT Hub<br/>Fleet Monitoring<br/>$300K/year]
        end
    end

    subgraph StatePlane[State Plane - Data Storage]
        subgraph TransactionDBs[Transaction Databases]
            TXNDB[(Payment DB<br/>PostgreSQL 15<br/>Multi-master<br/>50TB<br/>$3M/year)]
            LEDGER[(Ledger DB<br/>PostgreSQL 15<br/>ACID Compliance<br/>100TB<br/>$4M/year)]
            CASHDB[(Cash App DB<br/>DynamoDB<br/>Global Tables<br/>25TB<br/>$2M/year)]
        end

        subgraph Analytics[Analytics & Reporting]
            DWH[(Data Warehouse<br/>Snowflake<br/>Petabyte Scale<br/>$5M/year)]
            STREAM[(Kafka Streams<br/>100M events/day<br/>30-day retention<br/>$1M/year)]
            REDIS[(Redis Cluster<br/>Session Cache<br/>100GB<br/>$200K/year)]
        end

        subgraph Compliance[Compliance Storage]
            AUDIT[(Audit Store<br/>S3 Glacier<br/>7-year retention<br/>$800K/year)]
            PCI[(PCI Vault<br/>HSM Encrypted<br/>Tokenization<br/>$2M/year)]
        end
    end

    subgraph ControlPlane[Control Plane - Operations]
        MON[Datadog Monitoring<br/>Full Stack<br/>$500K/year]
        LOG[Centralized Logging<br/>ELK Stack<br/>$300K/year]
        ALERT[PagerDuty<br/>24/7 Alerting<br/>$100K/year]
        DEPLOY[CI/CD Pipeline<br/>Jenkins/GitLab<br/>$200K/year]
        CONFIG[Configuration<br/>Consul/Vault<br/>$150K/year]
    end

    %% External Systems
    BANKS[Card Networks<br/>Visa/Mastercard<br/>Interchange Fees<br/>$50M/year]
    REGULATORS[Regulators<br/>PCI DSS, SOX<br/>Compliance<br/>$10M/year]
    PARTNERS[Banking Partners<br/>Sutton Bank<br/>Lincoln Savings<br/>$20M/year]

    %% Connections
    CDN --> ALB
    ALB --> AGW
    AGW --> AUTH
    AGW --> P2P
    AGW --> POS

    AUTH --> TXNDB
    AUTH --> RISK
    AUTH --> BANKS

    SETTLE --> LEDGER
    SETTLE --> PARTNERS

    P2P --> CASHDB
    CRYPTO --> CASHDB

    RISK --> DWH
    MERCHANT --> TXNDB

    POS --> DEVICE
    DEVICE --> CONFIG

    %% All services connect to monitoring
    AUTH --> MON
    SETTLE --> MON
    RISK --> MON
    P2P --> MON

    %% Audit trails
    TXNDB --> AUDIT
    LEDGER --> AUDIT
    CASHDB --> AUDIT

    %% Real-time analytics
    TXNDB --> STREAM
    CASHDB --> STREAM
    STREAM --> DWH

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef externalStyle fill:#9999CC,stroke:#666699,color:#fff

    class CDN,ALB,WAF edgeStyle
    class AGW,AUTH,SETTLE,RISK,MERCHANT,P2P,CRYPTO,BANKING,POS,DEVICE serviceStyle
    class TXNDB,LEDGER,CASHDB,DWH,STREAM,REDIS,AUDIT,PCI stateStyle
    class MON,LOG,ALERT,DEPLOY,CONFIG controlStyle
    class BANKS,REGULATORS,PARTNERS externalStyle
```

## Production Architecture Metrics

### Scale & Performance
- **Payment Volume**: $200B+ annually processed
- **Transaction Rate**: 50,000 TPS peak (Black Friday)
- **Merchants**: 4M+ active merchants globally
- **Cash App Users**: 50M+ monthly active users
- **Hardware Devices**: 3M+ Square Readers deployed
- **API Requests**: 2B+ daily across all services

### Infrastructure Costs (Annual)
- **Total Infrastructure**: $28M/year
- **Compute (AWS EC2)**: $15M/year
- **Storage & Data**: $8M/year
- **Networking & CDN**: $3M/year
- **Monitoring & Tools**: $2M/year

### Reliability Metrics
- **Payment Uptime**: 99.95% (21.9 minutes downtime/year)
- **Cash App Uptime**: 99.9% (8.76 hours downtime/year)
- **Mean Time to Recovery**: 12 minutes
- **P99 Authorization Latency**: 50ms
- **P99 Settlement Time**: 2 business days

## Critical Production Components

### Payment Authorization Flow
1. **Card Swipe/Dip**: Hardware reader encrypts card data
2. **Risk Scoring**: Real-time ML fraud detection (15ms)
3. **Network Routing**: Visa/Mastercard authorization (200ms)
4. **Merchant Notification**: Real-time update to POS (50ms)
5. **Settlement Initiation**: Batch processing every 4 hours

### Cash App Integration
- **P2P Payments**: Instant transfers between users
- **Cryptocurrency**: Real-time Bitcoin/Ethereum trading
- **Banking Services**: Direct deposit, savings accounts
- **Debit Card**: Square Cash Card with instant funding

### Hardware Ecosystem
- **Square Reader**: Magnetic stripe, chip, contactless
- **Square Terminal**: All-in-one payment device
- **Square Register**: iPad-based POS system
- **Square Stand**: Card reader + receipt printer

## Compliance & Security Architecture

### PCI DSS Level 1 Compliance
- **Tokenization**: Card data never stored in plaintext
- **HSM Integration**: Hardware security modules for key management
- **Network Segmentation**: Isolated cardholder data environment
- **Vulnerability Scanning**: Continuous security monitoring

### Financial Regulations
- **SOX Compliance**: Financial reporting controls
- **AML/KYC**: Anti-money laundering monitoring
- **FFIEC Guidelines**: Banking regulation compliance
- **State Licensing**: Money transmitter licenses in all 50 states

## Disaster Recovery & Business Continuity

### Multi-Region Deployment
- **Primary**: US East (N. Virginia)
- **Secondary**: US West (Oregon)
- **Failover Time**: 15 minutes RTO
- **Data Replication**: Synchronous for payment data

### Backup Strategy
- **Transaction Data**: Real-time replication + hourly snapshots
- **Configuration**: Version-controlled infrastructure as code
- **Disaster Recovery Testing**: Monthly drills
- **Business Continuity**: 4-hour RPO maximum

This architecture processes over $200 billion in payments annually while maintaining 99.95% uptime and strict financial compliance requirements.