# Instacart - Complete Architecture

## Overview

Instacart's architecture handles 10M+ active users, 500K+ shoppers, and 80K+ stores with real-time inventory management, intelligent order batching, and dynamic pricing across North America's largest grocery delivery platform.

## Complete System Architecture

```mermaid
graph TB
    subgraph "Edge Plane - Customer-Facing"
        CDN[CloudFlare CDN<br/>Global PoPs<br/>$800K/month<br/>Image optimization]
        WAF[CloudFlare WAF<br/>Bot protection<br/>$200K/month<br/>API security]
        LB[AWS ALB<br/>Multi-region<br/>300K+ rps capacity<br/>Health checks]
    end

    subgraph "Service Plane - Core Platform"
        API[API Gateway<br/>Kong Enterprise<br/>200K+ rps<br/>p99: 20ms]

        subgraph "Customer Services"
            CATALOG[Catalog Service<br/>Java 17<br/>3000 instances<br/>c5.4xlarge]
            SEARCH[Search Service<br/>Elasticsearch<br/>1000 instances<br/>c5.2xlarge]
            CART[Cart Service<br/>Go 1.20<br/>2000 instances<br/>c5.2xlarge]
            ORDER[Order Service<br/>Java 17<br/>4000 instances<br/>c5.4xlarge]
        end

        subgraph "Shopper Services"
            DISPATCH[Dispatch Service<br/>Python 3.11<br/>1500 instances<br/>c5.4xlarge]
            BATCH[Batching Engine<br/>Go 1.20<br/>500 instances<br/>c5.9xlarge]
            NAVIGATION[Navigation Service<br/>Java 17<br/>800 instances<br/>c5.2xlarge]
            COMMUNICATION[Communication Service<br/>Node.js 18<br/>1000 instances<br/>c5.2xlarge]
        end

        subgraph "Store Services"
            INVENTORY[Inventory Service<br/>Go 1.20<br/>2500 instances<br/>c5.4xlarge]
            PRICING[Pricing Service<br/>Java 17<br/>1200 instances<br/>c5.4xlarge]
            FULFILLMENT[Fulfillment Service<br/>Python 3.11<br/>1800 instances<br/>c5.4xlarge]
        end

        subgraph "Platform Services"
            PAYMENT[Payment Service<br/>Java 17<br/>800 instances<br/>c5.2xlarge]
            NOTIFICATION[Notification Service<br/>Go 1.20<br/>600 instances<br/>c5.xlarge]
            ANALYTICS[Analytics Service<br/>Scala 2.13<br/>400 instances<br/>c5.2xlarge]
        end
    end

    subgraph "State Plane - Data Layer"
        subgraph "Primary Databases"
            ORDERDB[(Order Database<br/>PostgreSQL 14<br/>200 shards<br/>db.r6g.12xlarge)]
            INVENTORYDB[(Inventory Database<br/>MongoDB 6.0<br/>500 shards<br/>r6g.8xlarge)]
            USERDB[(User Database<br/>PostgreSQL 14<br/>100 shards<br/>db.r6g.8xlarge)]
            STOREDB[(Store Database<br/>PostgreSQL 14<br/>50 shards<br/>db.r6g.4xlarge)]
        end

        subgraph "Real-time Storage"
            REDIS[Redis Cluster<br/>300 nodes<br/>10TB memory<br/>r6g.4xlarge<br/>p99: 1ms]
            KAFKA[Kafka Cluster<br/>150 brokers<br/>1PB retention<br/>i3.4xlarge]
            ELASTICSEARCH[Elasticsearch<br/>200 nodes<br/>100TB<br/>r6g.4xlarge]
        end

        subgraph "Object Storage"
            S3IMAGES[S3 Product Images<br/>50PB<br/>Standard/IA<br/>$300K/month]
            S3DATA[S3 Analytics Data<br/>100PB<br/>Parquet format<br/>$200K/month]
            S3BACKUP[S3 Backups<br/>20PB<br/>Glacier<br/>$50K/month]
        end

        subgraph "Analytics Platform"
            SNOWFLAKE[Snowflake DW<br/>5PB<br/>Real-time ETL<br/>$800K/month]
            SPARK[Spark Clusters<br/>ML training<br/>2000 nodes<br/>c5.9xlarge]
        end
    end

    subgraph "Control Plane - Operations"
        MONITORING[DataDog + New Relic<br/>Full-stack monitoring<br/>$150K/month]
        LOGGING[Splunk Enterprise<br/>50TB/day<br/>$200K/month]
        DEPLOYMENT[Spinnaker + Jenkins<br/>100+ deploys/day<br/>Blue-green]
        SECRETS[HashiCorp Vault<br/>5K+ secrets<br/>Auto-rotation]
        CHAOS[Chaos Engineering<br/>Gremlin platform<br/>Automated testing]
    end

    %% Edge Connections
    CDN --> WAF
    WAF --> LB
    LB --> API

    %% Service Connections
    API --> CATALOG
    API --> SEARCH
    API --> CART
    API --> ORDER

    ORDER --> DISPATCH
    DISPATCH --> BATCH
    BATCH --> NAVIGATION
    NAVIGATION --> COMMUNICATION

    CATALOG --> INVENTORY
    INVENTORY --> PRICING
    PRICING --> FULFILLMENT

    ORDER --> PAYMENT
    PAYMENT --> NOTIFICATION
    NOTIFICATION --> ANALYTICS

    %% Data Connections
    ORDER --> ORDERDB
    INVENTORY --> INVENTORYDB
    CATALOG --> USERDB
    FULFILLMENT --> STOREDB

    CART --> REDIS
    SEARCH --> ELASTICSEARCH
    ANALYTICS --> KAFKA

    INVENTORY --> S3IMAGES
    ANALYTICS --> S3DATA
    ORDERDB --> S3BACKUP

    KAFKA --> SNOWFLAKE
    ANALYTICS --> SPARK

    %% Monitoring Connections
    MONITORING -.-> ORDER
    MONITORING -.-> INVENTORY
    LOGGING -.-> DISPATCH
    DEPLOYMENT -.-> API

    %% Apply 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:2px

    class CDN,WAF,LB edgeStyle
    class API,CATALOG,SEARCH,CART,ORDER,DISPATCH,BATCH,NAVIGATION,COMMUNICATION,INVENTORY,PRICING,FULFILLMENT,PAYMENT,NOTIFICATION,ANALYTICS serviceStyle
    class ORDERDB,INVENTORYDB,USERDB,STOREDB,REDIS,KAFKA,ELASTICSEARCH,S3IMAGES,S3DATA,S3BACKUP,SNOWFLAKE,SPARK stateStyle
    class MONITORING,LOGGING,DEPLOYMENT,SECRETS,CHAOS controlStyle
```

## Key Architectural Components

### Order Management System
- **Order Service**: Handles 2M+ orders daily with sub-100ms response times
- **Batching Engine**: Groups orders for efficient shopper routing (2.3 orders/batch average)
- **Payment Processing**: Integrates with Stripe for instant payment authorization
- **Real-time Updates**: WebSocket connections for order status tracking

### Inventory Management
- **Real-time Sync**: Updates from 80K+ stores every 15 minutes
- **Availability Prediction**: ML models predict stock-outs 2 hours ahead
- **Dynamic Pricing**: Surge pricing during high demand (up to 30% markup)
- **Store Integration**: APIs with major chains (Kroger, Safeway, Costco)

### Shopper Dispatch Algorithm
- **Location-based Matching**: Assigns orders within 15-minute drive radius
- **Skill-based Routing**: Considers shopper experience and ratings
- **Real-time Optimization**: Adjusts assignments based on traffic and demand
- **Batch Optimization**: Groups compatible orders to maximize efficiency

## Global Scale Architecture

### Regional Distribution

```mermaid
pie title Order Volume by Region
    "California" : 25
    "New York/New Jersey" : 15
    "Texas" : 12
    "Florida" : 10
    "Illinois" : 8
    "Other US States" : 25
    "Canada" : 5
```

### Multi-Region Setup
- **Primary**: US-West-2 (Oregon) - 40% traffic
- **Secondary**: US-East-1 (Virginia) - 35% traffic
- **Tertiary**: CA-Central-1 (Canada) - 15% traffic
- **Edge**: US-Central-1 (Iowa) - 10% traffic

## Production Metrics

### Scale Indicators
- **Daily Active Users**: 10M+ (peak 15M during COVID)
- **Orders per Day**: 2M+ (peak 5M during pandemic)
- **Active Shoppers**: 500K+ independent contractors
- **Partner Stores**: 80K+ across North America
- **Product Catalog**: 5M+ SKUs across all stores

### Performance SLAs
- **Order Placement**: p99 < 500ms
- **Shopper Assignment**: p99 < 30 seconds
- **Inventory Updates**: Real-time, <15 minutes staleness
- **Search Results**: p99 < 100ms
- **Payment Processing**: p99 < 2 seconds

### Availability Targets
- **Customer App**: 99.95% uptime
- **Shopper App**: 99.9% uptime
- **Store Integrations**: 99.5% uptime
- **Payment System**: 99.99% uptime

## Infrastructure Costs

### Monthly Operational Costs
- **Compute**: $8M (AWS EC2, Auto Scaling Groups)
- **Databases**: $3M (RDS, MongoDB Atlas, Redis)
- **Storage**: $1M (S3, EBS volumes)
- **Network**: $800K (CloudFront, Data Transfer)
- **Analytics**: $1.2M (Snowflake, Spark clusters)
- **Monitoring**: $200K (DataDog, New Relic, Splunk)
- **Total**: $14.2M/month infrastructure spend

### Cost Per Transaction
- **Order Processing**: $0.12 per order
- **Inventory Sync**: $0.008 per product update
- **Search Query**: $0.001 per search
- **Payment Processing**: $0.30 + 2.9% (Stripe fees)

## Security and Compliance

### Data Protection
- **PCI DSS Level 1**: Payment card industry compliance
- **SOC 2 Type II**: Annual security audits
- **Encryption**: AES-256 at rest, TLS 1.3 in transit
- **API Security**: OAuth 2.0 + JWT tokens, rate limiting

### Privacy Controls
- **GDPR Compliance**: EU user data protection
- **CCPA Compliance**: California consumer privacy
- **Data Retention**: Orders purged after 7 years
- **Location Privacy**: Shopper location encrypted, customer addresses hashed

## Disaster Recovery

### Business Continuity
- **RTO**: 2 hours for full service restoration
- **RPO**: 5 minutes for order data
- **Geographic Redundancy**: Multi-region active-active
- **Data Backup**: 3-2-1 strategy with cross-region replication

### Critical Failure Scenarios
1. **AWS Region Outage**: Automatic failover to secondary region
2. **Database Failure**: Read replicas promoted, eventual consistency
3. **Payment System Down**: Queue orders for retry, notify customers
4. **Store API Failure**: Fallback to cached inventory, mark uncertain

## Integration Ecosystem

### External Partners
- **Retailers**: 80K+ stores (Kroger, Safeway, CVS, Costco)
- **Payment Processors**: Stripe, Adyen for credit cards
- **Identity Verification**: Jumio for shopper onboarding
- **Mapping Services**: Google Maps API for navigation
- **Communication**: Twilio for SMS, SendGrid for email

### API Architecture
- **RESTful APIs**: JSON over HTTPS, OpenAPI 3.0 specs
- **GraphQL**: Customer-facing queries for mobile apps
- **Webhooks**: Real-time store inventory updates
- **Rate Limiting**: 1000 requests/minute per API key
- **SDK Support**: iOS, Android, React Native libraries