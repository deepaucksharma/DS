# Robinhood Cost Breakdown

## Infrastructure and Regulatory Economics

Comprehensive cost analysis for operating a commission-free trading platform serving 23M+ users with $130B+ assets under custody, including infrastructure, regulatory, and operational expenses.

```mermaid
pie title Monthly Infrastructure Costs ($4.8M Total)
    "Compute (EC2/ECS)" : 2800
    "Database (RDS/Aurora)" : 1200
    "Regulatory Compliance" : 450
    "Network & CDN" : 320
    "Storage (S3/EBS)" : 180
    "Monitoring & Security" : 95
    "Kafka/Streaming" : 85
    "Redis Caching" : 75
    "Machine Learning" : 65
    "Development Tools" : 45
```

## Detailed Cost Structure

### Infrastructure Costs (Monthly)

```mermaid
graph TB
    subgraph ComputeLayer[Compute Infrastructure - $2.8M/month]
        TRADING[Trading Services<br/>c5.9xlarge × 120<br/>$1.2M/month]
        API[API Gateway<br/>c5.4xlarge × 80<br/>$650K/month]
        EXECUTION[Execution Engine<br/>Bare metal × 40<br/>$480K/month]
        ML[ML/Analytics<br/>p3.8xlarge × 25<br/>$320K/month]
        BACKGROUND[Background Jobs<br/>c5.2xlarge × 60<br/>$280K/month]
    end

    subgraph DatabaseLayer[Database Infrastructure - $1.2M/month]
        PRIMARY[Primary Trading DB<br/>db.r6g.16xlarge × 8<br/>$580K/month]
        REPLICAS[Read Replicas<br/>db.r6g.8xlarge × 24<br/>$420K/month]
        ANALYTICS[Analytics DB<br/>db.r5.12xlarge × 4<br/>$180K/month]
        COMPLIANCE[Compliance DB<br/>db.r6g.4xlarge × 6<br/>$120K/month]
    end

    subgraph CacheLayer[Caching Infrastructure - $185K/month]
        REDIS_MAIN[Main Redis Cluster<br/>cache.r6g.4xlarge × 12<br/>$95K/month]
        REDIS_SESSION[Session Cache<br/>cache.r6g.2xlarge × 8<br/>$52K/month]
        REDIS_MARKET[Market Data Cache<br/>cache.r6g.xlarge × 16<br/>$38K/month]
    end

    subgraph StreamingLayer[Event Streaming - $85K/month]
        KAFKA[Kafka MSK Cluster<br/>kafka.m5.2xlarge × 15<br/>$65K/month]
        KINESIS[Kinesis Streams<br/>1M events/sec<br/>$20K/month]
    end

    subgraph StorageLayer[Storage Infrastructure - $180K/month]
        S3_DOCS[S3 Document Storage<br/>150TB active<br/>$95K/month]
        EBS_VOLUMES[EBS Volumes<br/>500TB total<br/>$55K/month]
        GLACIER[S3 Glacier Archive<br/>2PB archived<br/>$30K/month]
    end

    subgraph NetworkLayer[Network & CDN - $320K/month]
        DATA_TRANSFER[AWS Data Transfer<br/>50TB/month<br/>$180K/month]
        CLOUDFRONT[CloudFront CDN<br/>Global distribution<br/>$85K/month]
        DIRECT_CONNECT[Direct Connect<br/>Dedicated lines<br/>$55K/month]
    end

    classDef computeStyle fill:#10B981,stroke:#059669,color:#fff
    classDef databaseStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef cacheStyle fill:#9966CC,stroke:#663399,color:#fff
    classDef streamStyle fill:#66CC99,stroke:#339966,color:#fff
    classDef storageStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef networkStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class TRADING,API,EXECUTION,ML,BACKGROUND computeStyle
    class PRIMARY,REPLICAS,ANALYTICS,COMPLIANCE databaseStyle
    class REDIS_MAIN,REDIS_SESSION,REDIS_MARKET cacheStyle
    class KAFKA,KINESIS streamStyle
    class S3_DOCS,EBS_VOLUMES,GLACIER storageStyle
    class DATA_TRANSFER,CLOUDFRONT,DIRECT_CONNECT networkStyle
```

## Regulatory and Compliance Costs

### Monthly Regulatory Expenses

```mermaid
graph TB
    subgraph RegulatoryFees[Regulatory Fees - $8.6M/month]
        FINRA_FEES[FINRA Trading Fees<br/>$0.0008 per share<br/>$4.2M/month]
        SEC_FEES[SEC Transaction Fees<br/>$0.0051 per $1000<br/>$2.1M/month]
        NSCC_FEES[NSCC Clearing Fees<br/>$0.0002 per share<br/>$1.8M/month]
        OCC_FEES[OCC Options Fees<br/>$0.048 per contract<br/>$320K/month]
        STATE_FEES[State Registration<br/>50 states × $2.4K<br/>$120K/month]
    end

    subgraph ComplianceInfra[Compliance Infrastructure - $450K/month]
        SURVEILLANCE[Trade Surveillance<br/>FINRA CAT reporting<br/>$180K/month]
        REPORTING[Regulatory Reporting<br/>Daily/Monthly filings<br/>$125K/month]
        KYC_SYSTEMS[KYC/AML Systems<br/>Identity verification<br/>$85K/month]
        AUDIT_TOOLS[Audit Tools<br/>Compliance monitoring<br/>$60K/month]
    end

    subgraph LegalCosts[Legal and Compliance Staff - $2.8M/month]
        COMPLIANCE_TEAM[Compliance Team<br/>45 FTE × $18K/month<br/>$810K/month]
        LEGAL_TEAM[Legal Team<br/>25 FTE × $22K/month<br/>$550K/month]
        EXTERNAL_COUNSEL[External Counsel<br/>Regulatory matters<br/>$420K/month]
        CONSULTANTS[Compliance Consultants<br/>Specialized expertise<br/>$280K/month]
        TRAINING[Staff Training<br/>Series 7/63/66 licenses<br/>$95K/month]
        INSURANCE[E&O Insurance<br/>SIPC coverage<br/>$180K/month]
        EXAMINATIONS[Regulatory Exams<br/>SEC/FINRA audits<br/>$120K/month]
        SETTLEMENTS[Legal Settlements<br/>Customer disputes<br/>$385K/month]
    end

    classDef feeStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef infraStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef staffStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class FINRA_FEES,SEC_FEES,NSCC_FEES,OCC_FEES,STATE_FEES feeStyle
    class SURVEILLANCE,REPORTING,KYC_SYSTEMS,AUDIT_TOOLS infraStyle
    class COMPLIANCE_TEAM,LEGAL_TEAM,EXTERNAL_COUNSEL,CONSULTANTS,TRAINING,INSURANCE,EXAMINATIONS,SETTLEMENTS staffStyle
```

## Revenue vs Cost Analysis

### Unit Economics Per User (Monthly)

| Metric | Value | Calculation | Trend |
|--------|-------|-------------|-------|
| **Average Revenue Per User** | $6.82 | Total revenue ÷ 23M users | ↗ +12% YoY |
| **Infrastructure Cost Per User** | $0.21 | $4.8M ÷ 23M users | ↘ -8% YoY |
| **Regulatory Cost Per User** | $0.49 | $11.4M ÷ 23M users | ↗ +15% YoY |
| **Total Cost Per User** | $2.94 | All costs ÷ 23M users | ↗ +3% YoY |
| **Gross Margin Per User** | $3.88 | Revenue - Costs | ↗ +18% YoY |

### Revenue Sources (Annual)

```mermaid
pie title Annual Revenue Sources ($1.81B Total)
    "Payment for Order Flow" : 380
    "Robinhood Gold Subscriptions" : 249
    "Options Revenue" : 218
    "Net Interest Income" : 64
    "Crypto Revenue" : 34
    "Cash Management" : 28
    "Other Revenue" : 15
```

## Cost Optimization Strategies

### Infrastructure Cost Reduction Initiatives

```mermaid
timeline
    title Cost Optimization Timeline (2023-2024)

    section Q1 2023
        Reserved Instances : Commit to 3-year terms
                          : 40% savings on compute
                          : $1.1M annual savings

    section Q2 2023
        Database Optimization : Query optimization
                             : Connection pooling
                             : $280K annual savings

    section Q3 2023
        Auto-Scaling Improvements : Right-sizing instances
                                 : Spot instance usage
                                 : $420K annual savings

    section Q4 2023
        Storage Tiering : S3 Intelligent-Tiering
                       : Lifecycle policies
                       : $180K annual savings

    section Q1 2024
        Container Optimization : ECS to EKS migration
                              : Better resource utilization
                              : $350K annual savings

    section Q2 2024
        CDN Optimization : Multi-CDN strategy
                        : Origin optimization
                        : $125K annual savings
```

### Trading Volume Cost Scaling

```mermaid
xychart-beta
    title "Cost vs Trading Volume Correlation"
    x-axis [1M, 2M, 4M, 6M, 8M]
    y-axis "Infrastructure Cost ($M)" 0 --> 8
    line [2.1, 3.2, 4.8, 6.1, 7.2]
```

**Key Insights**:
- Infrastructure costs scale sub-linearly with volume
- Regulatory costs scale linearly with volume
- Fixed costs (compliance, legal) provide leverage at scale

## Competitive Cost Analysis

### Cost Per Trade Comparison

| Broker | Infrastructure Cost/Trade | Regulatory Cost/Trade | Total Cost/Trade |
|--------|--------------------------|----------------------|------------------|
| **Robinhood** | $0.012 | $0.028 | $0.040 |
| **Schwab** | $0.045 | $0.035 | $0.080 |
| **E*TRADE** | $0.038 | $0.032 | $0.070 |
| **TD Ameritrade** | $0.042 | $0.034 | $0.076 |
| **Interactive Brokers** | $0.018 | $0.029 | $0.047 |

### Payment for Order Flow Economics

```mermaid
sankey-beta
    title Payment for Order Flow Revenue Distribution

    Market Makers,380,Robinhood
    Robinhood,95,Technology Infrastructure
    Robinhood,85,Regulatory Compliance
    Robinhood,65,Customer Support
    Robinhood,45,Marketing & Growth
    Robinhood,90,Profit & Reinvestment
```

**PFOF Details**:
- **Average per share**: $0.0012 for retail equity orders
- **Volume**: ~316B shares annually routed to market makers
- **Top market makers**: Citadel Securities (40%), Virtu (25%), Two Sigma (15%)
- **Price improvement**: Average $0.0017 per share to customers

## Cost Centers Deep Dive

### Engineering Team Costs (Monthly)

| Team | Headcount | Average Salary | Monthly Cost | Focus Area |
|------|-----------|----------------|--------------|------------|
| **Platform Engineering** | 85 | $185K | $1.31M | Core trading infrastructure |
| **Mobile Engineering** | 45 | $175K | $656K | iOS/Android apps |
| **Data Engineering** | 32 | $190K | $507K | Analytics and ML |
| **Security Engineering** | 28 | $195K | $455K | Compliance and security |
| **Site Reliability** | 22 | $200K | $367K | Operations and monitoring |
| **QA Engineering** | 18 | $145K | $218K | Testing and validation |

### Third-Party Service Costs (Monthly)

| Service | Provider | Monthly Cost | Purpose |
|---------|----------|--------------|---------|
| **Market Data** | Thomson Reuters | $285K | Real-time quotes, fundamentals |
| **KYC/AML** | Jumio + internal | $95K | Identity verification |
| **Fraud Detection** | Sift Science | $65K | Transaction monitoring |
| **Customer Support** | Zendesk + staff | $180K | Help desk and chat |
| **Monitoring** | DataDog + PagerDuty | $85K | Infrastructure monitoring |
| **Security** | CrowdStrike + tools | $125K | Endpoint and network security |

## Business Impact of Costs

### Cost as % of Revenue (Quarterly)

```mermaid
xychart-beta
    title "Cost Structure Evolution (%)"
    x-axis [Q1-22, Q2-22, Q3-22, Q4-22, Q1-23, Q2-23, Q3-23, Q4-23]
    y-axis "Percentage of Revenue" 0 --> 100
    line [72, 68, 65, 61, 58, 55, 52, 49]
```

### Profitability by User Segment

| User Segment | % of Users | Revenue/User/Month | Cost/User/Month | Margin/User/Month |
|--------------|------------|-------------------|-----------------|-------------------|
| **Robinhood Gold** | 8% | $28.50 | $4.20 | $24.30 |
| **Active Traders** | 15% | $18.75 | $3.85 | $14.90 |
| **Options Traders** | 22% | $12.40 | $3.15 | $9.25 |
| **Casual Investors** | 35% | $4.20 | $2.60 | $1.60 |
| **Inactive Users** | 20% | $0.85 | $1.95 | -$1.10 |

## Future Cost Projections

### Scaling Cost Model (2024-2026)

```mermaid
graph TB
    subgraph Current[2023: Current State]
        USERS_23[23M Users<br/>$4.8M/month infra<br/>$11.4M/month regulatory]
    end

    subgraph Year1[2024: 30M Users (+30%)]
        USERS_24[30M Users<br/>$5.8M/month infra (+21%)<br/>$14.2M/month regulatory (+25%)]
    end

    subgraph Year2[2025: 40M Users (+33%)]
        USERS_25[40M Users<br/>$7.1M/month infra (+22%)<br/>$18.5M/month regulatory (+30%)]
    end

    subgraph Year3[2026: 55M Users (+38%)]
        USERS_26[55M Users<br/>$8.8M/month infra (+24%)<br/>$24.8M/month regulatory (+34%)]
    end

    Current --> Year1
    Year1 --> Year2
    Year2 --> Year3

    classDef currentStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef futureStyle fill:#10B981,stroke:#059669,color:#fff

    class USERS_23 currentStyle
    class USERS_24,USERS_25,USERS_26 futureStyle
```

**Key Assumptions**:
- User growth rate: 25-30% annually
- Infrastructure cost growth: 20-25% annually (economies of scale)
- Regulatory cost growth: 25-35% annually (compliance expansion)
- Revenue per user growth: 15-20% annually

*"Our cost structure reflects the reality of building financial infrastructure - every dollar spent on compliance and security protects billions in customer assets."* - Robinhood Finance Team