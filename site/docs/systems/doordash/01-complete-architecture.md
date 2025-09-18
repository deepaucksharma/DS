# DoorDash Complete Architecture - The Money Shot

## Executive Summary

DoorDash operates the largest food delivery platform in the US, serving 30M+ monthly active consumers across 7,000+ cities. Their architecture handles 1B+ orders per year with a real-time logistics network processing millions of location updates per second.

**Key Production Metrics (2024)**:
- **Peak Orders**: 2M orders/day during major events
- **Driver Updates**: 5M location updates/second during peak
- **Real-time Tracking**: Sub-second location updates for 1M+ active drivers
- **Infrastructure Cost**: ~$400M annually (estimated)
- **Delivery Time**: Average 30-35 minutes, 90% under 45 minutes

## Complete System Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - CDN & Load Balancing]
        CF[Cloudflare CDN<br/>Global Edge<br/>~$2M/year]
        ALB[AWS ALB<br/>Multi-AZ<br/>~$500K/year]

        CF --> ALB
    end

    subgraph ServicePlane[Service Plane - Business Logic]
        APIG[Kong API Gateway<br/>Rate Limiting: 10K RPS<br/>~$300K/year]

        subgraph CoreServices[Core Services - c5.9xlarge Fleet]
            ORDER[Order Service<br/>Java 17, 512 instances<br/>~$8M/year]
            DISPATCH[Dispatch Service (DeepRed)<br/>Scala, ML Models<br/>~$12M/year]
            DRIVER[Driver Service<br/>Go, Real-time tracking<br/>~$6M/year]
            RESTAURANT[Restaurant Service<br/>Java 17, Menu mgmt<br/>~$4M/year]
            PAYMENT[Payment Service<br/>Java 17, PCI compliant<br/>~$3M/year]
            PRICING[Dynamic Pricing<br/>Python ML, Real-time<br/>~$2M/year]
        end

        subgraph MicroServices[Supporting Microservices]
            NOTIFICATION[Push Notifications<br/>SQS + SNS<br/>~$800K/year]
            FRAUD[Fraud Detection<br/>Real-time ML<br/>~$1.5M/year]
            SEARCH[Restaurant Search<br/>Elasticsearch<br/>~$1M/year]
            ANALYTICS[Analytics Service<br/>Kafka + Spark<br/>~$2M/year]
        end

        ALB --> APIG
        APIG --> ORDER
        APIG --> DISPATCH
        APIG --> DRIVER
        APIG --> RESTAURANT
        APIG --> PAYMENT
        APIG --> PRICING
    end

    subgraph StatePlane[State Plane - Data Storage]
        subgraph PrimaryDatabases[Primary Databases]
            ORDERS_DB[(Orders DB<br/>PostgreSQL 14<br/>db.r6g.8xlarge<br/>Multi-AZ, 50TB<br/>~$15M/year)]
            DRIVERS_DB[(Driver Locations<br/>DynamoDB<br/>On-demand billing<br/>5M writes/sec<br/>~$8M/year)]
            RESTAURANTS_DB[(Restaurant DB<br/>PostgreSQL 14<br/>Menu, availability<br/>~$2M/year)]
            USER_DB[(User DB<br/>PostgreSQL 14<br/>Profiles, preferences<br/>~$3M/year)]
        end

        subgraph Caching[Caching Layer]
            REDIS[(Redis Cluster<br/>ElastiCache<br/>r6g.4xlarge × 20<br/>~$2M/year)]
            MEMCACHED[(Memcached<br/>Driver location cache<br/>~$500K/year)]
        end

        subgraph Streaming[Real-time Streaming]
            KAFKA[Kafka Cluster<br/>MSK, 3 AZ<br/>kafka.m5.4xlarge × 30<br/>~$3M/year]
            KINESIS[Kinesis Data Streams<br/>Location tracking<br/>1000 shards<br/>~$2M/year]
        end

        ORDER --> ORDERS_DB
        DISPATCH --> DRIVERS_DB
        DRIVER --> DRIVERS_DB
        RESTAURANT --> RESTAURANTS_DB
        PAYMENT --> USER_DB

        ORDER --> REDIS
        DISPATCH --> REDIS
        DRIVER --> MEMCACHED

        DRIVER --> KINESIS
        ORDER --> KAFKA
        DISPATCH --> KAFKA
    end

    subgraph ControlPlane[Control Plane - Operations]
        subgraph Monitoring[Monitoring & Observability]
            DATADOG[Datadog<br/>APM, Infrastructure<br/>~$2M/year]
            GRAFANA[Grafana<br/>Custom dashboards<br/>~$100K/year]
            PAGERDUTY[PagerDuty<br/>Incident management<br/>~$200K/year]
        end

        subgraph Deployment[Deployment & Config]
            KUBE[Kubernetes<br/>EKS, 200 nodes<br/>~$5M/year]
            CONSUL[HashiCorp Consul<br/>Service discovery<br/>~$300K/year]
            VAULT[HashiCorp Vault<br/>Secrets management<br/>~$200K/year]
        end

        subgraph ML_Infrastructure[ML Infrastructure]
            SAGEMAKER[AWS SageMaker<br/>Model training<br/>~$8M/year]
            AIRFLOW[Apache Airflow<br/>ML pipelines<br/>~$500K/year]
            MLFLOW[MLflow<br/>Model registry<br/>~$200K/year]
        end

        KUBE --> ORDER
        KUBE --> DISPATCH
        KUBE --> DRIVER
        DATADOG --> KUBE
        PAGERDUTY --> DATADOG
    end

    %% Real-time Data Flows
    DRIVER -.->|5M GPS updates/sec| KINESIS
    KINESIS -.->|Stream processing| DISPATCH
    DISPATCH -.->|ETA updates| REDIS
    ORDER -.->|Order events| KAFKA
    KAFKA -.->|Event sourcing| ANALYTICS

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:2px

    class CF,ALB edgeStyle
    class APIG,ORDER,DISPATCH,DRIVER,RESTAURANT,PAYMENT,PRICING,NOTIFICATION,FRAUD,SEARCH,ANALYTICS edgeStyle
    class ORDERS_DB,DRIVERS_DB,RESTAURANTS_DB,USER_DB,REDIS,MEMCACHED,KAFKA,KINESIS stateStyle
    class DATADOG,GRAFANA,PAGERDUTY,KUBE,CONSUL,VAULT,SAGEMAKER,AIRFLOW,MLFLOW controlStyle
```

## Key Architecture Principles

### 1. Real-time Everything
- **Driver Locations**: Sub-second updates via Kinesis Data Streams
- **Order Tracking**: Real-time ETAs with WebSocket connections
- **Dispatch Decisions**: ML models making decisions in <100ms

### 2. Multi-sided Marketplace
- **Consumers**: Order placement and tracking
- **Drivers**: Real-time dispatch and navigation
- **Restaurants**: Order management and preparation time estimates

### 3. Geographic Partitioning
- **Regional Sharding**: Orders partitioned by delivery zone
- **Edge Computing**: Restaurant data cached regionally
- **Dispatch Optimization**: Local algorithms per metropolitan area

## Production Reality

### Peak Load Characteristics
- **Super Bowl Sunday**: 2M orders, 300% normal traffic
- **Dinner Rush**: 6-8 PM, 5x baseline load
- **Rainy Days**: 40% increase in demand, driver shortage
- **Holiday Events**: Christmas Eve 400% spike

### Critical Dependencies
- **Payment Processing**: Stripe primary, backup systems
- **Maps & Navigation**: Google Maps API with Mapbox fallback
- **SMS/Push**: Twilio for notifications, FCM for mobile
- **Machine Learning**: Real-time inference on SageMaker

### Disaster Recovery
- **RTO**: 15 minutes for core services
- **RPO**: 5 minutes for order data
- **Multi-Region**: Active-passive setup (US-East primary)
- **Data Replication**: Cross-region PostgreSQL replication

## Cost Optimization Strategies

### Reserved Instance Strategy
- **70% Reserved**: Predictable workloads (databases, core services)
- **20% Spot**: Batch processing, ML training
- **10% On-demand**: Peak traffic handling

### Data Tiering
- **Hot Data**: Last 24 hours in Redis/DynamoDB
- **Warm Data**: Last 30 days in PostgreSQL
- **Cold Data**: Historical in S3 with Glacier lifecycle

## Business Impact

### Revenue Metrics
- **Order Volume**: 1B+ orders annually
- **Take Rate**: 15-20% commission from restaurants
- **Delivery Fee**: $2-5 per order
- **DashPass**: Subscription revenue $2B+ annually

### Operational Excellence
- **Uptime**: 99.95% for core order flow
- **P99 Latency**: <500ms for order placement
- **Driver Utilization**: 85% during peak hours
- **Customer Satisfaction**: 4.7/5 average rating

**Source**: DoorDash Engineering Blog, SEC Filings, Conference Presentations (2023-2024)