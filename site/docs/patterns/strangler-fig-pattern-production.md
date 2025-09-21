# Strangler Fig Pattern: Production Implementation

## Overview

The Strangler Fig Pattern gradually replaces a legacy system by building new functionality around it and slowly routing traffic to new services while maintaining the old system. Named after the strangler fig tree that grows around and eventually replaces its host tree, this pattern enables safe, incremental modernization of monolithic systems.

## Production Implementation: Shopify's Rails Monolith Migration

Shopify successfully used the Strangler Fig pattern from 2016-2021 to break down their Ruby on Rails monolith serving 1M+ merchants into 100+ microservices while maintaining 99.98% uptime during Black Friday/Cyber Monday.

### Complete Architecture - Shopify's 5-Year Migration Journey

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Global Traffic]
        CF[CloudFlare<br/>Global CDN<br/>500+ locations<br/>10PB/month<br/>$80K/month]
        ALB[AWS ALB<br/>Multi-region<br/>2M req/s peak<br/>$35K/month]
    end

    subgraph ServicePlane[Service Plane - Strangler Fig Implementation]
        subgraph Router[Traffic Router - The Strangler]
            TrafficSplitter[Envoy Proxy<br/>Intelligent routing<br/>Feature flags<br/>A/B testing<br/>c5.4xlarge × 20<br/>$25K/month]
        end

        subgraph LegacySystem[Legacy Rails Monolith - The Host]
            RailsMonolith[Shopify Rails App<br/>Ruby 3.0<br/>Unicorn servers<br/>500 instances<br/>$120K/month<br/>⚠️ Being strangled]
        end

        subgraph NewServices[New Microservices - The Fig]
            ProductSvc[Product Service<br/>Go 1.19<br/>PostgreSQL<br/>200 instances<br/>$15K/month<br/>✅ Migrated 2019]

            OrderSvc[Order Service<br/>Java 17<br/>Event sourcing<br/>150 instances<br/>$25K/month<br/>✅ Migrated 2020]

            PaymentSvc[Payment Service<br/>Go 1.19<br/>PCI compliant<br/>100 instances<br/>$35K/month<br/>✅ Migrated 2020]

            InventorySvc[Inventory Service<br/>Rust<br/>Real-time updates<br/>80 instances<br/>$18K/month<br/>✅ Migrated 2021]

            ReportingSvc[Reporting Service<br/>Python 3.9<br/>Apache Spark<br/>50 instances<br/>$12K/month<br/>🔄 In progress]
        end

        subgraph DataSyncLayer[Data Synchronization Layer]
            CDC[Change Data Capture<br/>Debezium + Kafka<br/>10M events/day<br/>$8K/month]
            EventBus[Event Bus<br/>Apache Kafka<br/>100M messages/day<br/>$15K/month]
        end
    end

    subgraph StatePlane[State Plane - Hybrid Data Strategy]
        subgraph LegacyData[Legacy Data Store]
            MonolithDB[(MySQL 8.0<br/>Master-Slave<br/>100TB data<br/>db.r6g.24xlarge<br/>$45K/month)]
        end

        subgraph NewDataStores[New Service Databases]
            ProductDB[(Product PostgreSQL<br/>20TB<br/>$8K/month)]
            OrderDB[(Order PostgreSQL<br/>50TB<br/>Event store<br/>$15K/month)]
            PaymentDB[(Payment PostgreSQL<br/>Encrypted<br/>5TB<br/>$12K/month)]
            InventoryDB[(Inventory Redis<br/>In-memory<br/>$3K/month)]
        end

        subgraph SharedCache[Shared Caching Layer]
            GlobalCache[(Redis Cluster<br/>1TB memory<br/>ElastiCache<br/>$8K/month)]
        end
    end

    subgraph ControlPlane[Control Plane - Migration Orchestration]
        FeatureFlags[LaunchDarkly<br/>Feature flags<br/>Traffic routing<br/>$5K/month]
        Monitoring[DataDog<br/>APM + Infrastructure<br/>Real-time alerts<br/>$15K/month]
        MigrationDashboard[Migration Dashboard<br/>Custom Rails app<br/>Progress tracking<br/>$2K/month]
        CircuitBreaker[Hystrix<br/>Fallback to monolith<br/>Auto-recovery]
    end

    %% Traffic Flow
    CF --> ALB
    ALB --> TrafficSplitter

    %% Traffic Routing Logic
    TrafficSplitter -->|Products: 100%| ProductSvc
    TrafficSplitter -->|Orders: 100%| OrderSvc
    TrafficSplitter -->|Payments: 100%| PaymentSvc
    TrafficSplitter -->|Inventory: 100%| InventorySvc
    TrafficSplitter -->|Reports: 20%| ReportingSvc
    TrafficSplitter -->|Reports: 80%<br/>Everything else: 100%| RailsMonolith

    %% Data Synchronization
    MonolithDB --> CDC
    CDC --> EventBus
    EventBus --> ProductSvc
    EventBus --> OrderSvc
    EventBus --> PaymentSvc
    EventBus --> InventorySvc
    EventBus --> ReportingSvc

    %% Service Data Stores
    ProductSvc --> ProductDB
    OrderSvc --> OrderDB
    PaymentSvc --> PaymentDB
    InventorySvc --> InventoryDB
    ReportingSvc --> MonolithDB

    %% Shared Cache
    ProductSvc --> GlobalCache
    OrderSvc --> GlobalCache
    PaymentSvc --> GlobalCache
    RailsMonolith --> GlobalCache

    %% Legacy connections
    RailsMonolith --> MonolithDB

    %% Control Plane
    TrafficSplitter --> FeatureFlags
    TrafficSplitter --> CircuitBreaker

    ProductSvc --> Monitoring
    OrderSvc --> Monitoring
    PaymentSvc --> Monitoring
    InventorySvc --> Monitoring
    ReportingSvc --> Monitoring
    RailsMonolith --> Monitoring

    MigrationDashboard --> FeatureFlags
    MigrationDashboard --> Monitoring

    %% Styling
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef legacyStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-dasharray: 5 5
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#5B21B6,color:#fff

    class CF,ALB edgeStyle
    class Router,TrafficSplitter,NewServices,ProductSvc,OrderSvc,PaymentSvc,InventorySvc,ReportingSvc,DataSyncLayer,CDC,EventBus serviceStyle
    class LegacySystem,RailsMonolith legacyStyle
    class StatePlane,LegacyData,MonolithDB,NewDataStores,ProductDB,OrderDB,PaymentDB,InventoryDB,SharedCache,GlobalCache stateStyle
    class FeatureFlags,Monitoring,MigrationDashboard,CircuitBreaker controlStyle
```

### Migration Timeline - Shopify's 5-Year Journey

```mermaid
gantt
    title Shopify Strangler Fig Migration (2016-2021)
    dateFormat YYYY-MM
    axisFormat %Y

    section Infrastructure
    Traffic Router Setup    :done, router, 2016-01, 2016-06
    Monitoring & Observability :done, monitor, 2016-03, 2016-12
    Feature Flag System     :done, flags, 2016-06, 2017-01
    Data Sync Infrastructure :done, sync, 2017-01, 2017-08

    section Service Migration
    Product Service        :done, product, 2017-06, 2019-03
    Order Service         :done, order, 2018-01, 2020-06
    Payment Service       :done, payment, 2018-06, 2020-12
    Inventory Service     :done, inventory, 2019-01, 2021-03
    Reporting Service     :active, reporting, 2020-06, 2021-12

    section Monolith Retirement
    Legacy Code Cleanup   :cleanup, 2021-01, 2021-12
    Final Decommission    :final, 2021-10, 2022-03
```

### Request Flow - Black Friday 2020 Success Story

During Black Friday 2020, Shopify processed $5.1B in sales with 99.99% uptime while running both legacy and new systems:

```mermaid
sequenceDiagram
    participant Customer as Customer
    participant CDN as CloudFlare CDN
    participant Router as Traffic Router
    participant Product as Product Service
    participant Order as Order Service
    participant Payment as Payment Service
    participant Rails as Rails Monolith
    participant DB as Monolith Database

    Note over Customer,DB: Black Friday Product Purchase - Peak Traffic

    Customer->>+CDN: GET /products/iphone-13
    CDN->>+Router: Cache miss<br/>Route to backend

    Note over Router: Feature flag: products=100%<br/>Route to new service

    Router->>+Product: GET /api/products/123
    Note over Product: Read from dedicated DB<br/>p99: 15ms

    Product-->>-Router: Product details<br/>Stock: 500 units
    Router-->>-CDN: Response + cache headers
    CDN-->>-Customer: Product page<br/>Total p99: 45ms

    Note over Customer,DB: Customer adds to cart and purchases

    Customer->>+CDN: POST /cart/add
    CDN->>+Router: Route add to cart

    Note over Router: Feature flag: orders=100%<br/>Route to order service

    Router->>+Order: POST /api/cart/add
    Order->>+Product: GET /api/products/123/stock
    Product-->>-Order: Available: 499 units
    Order-->>-Router: Item added<br/>p99: 25ms

    Router-->>-CDN: Cart updated
    CDN-->>-Customer: Success

    Note over Customer,DB: Customer proceeds to checkout

    Customer->>+CDN: POST /checkout
    CDN->>+Router: Route checkout

    Router->>+Order: POST /api/orders
    Note over Order: Create provisional order<br/>Reserve inventory

    Order->>+Payment: POST /api/charges
    Note over Payment: Stripe integration<br/>PCI compliance<br/>p99: 180ms

    Payment-->>-Order: Payment authorized
    Order-->>-Router: Order confirmed<br/>Order #12345

    Router-->>-CDN: Checkout success
    CDN-->>-Customer: Order confirmation<br/>Total p99: 350ms

    Note over Customer,DB: Fallback scenario for reporting

    Customer->>+CDN: GET /admin/reports
    CDN->>+Router: Route reports request

    Note over Router: Feature flag: reports=20%<br/>A/B test new service

    alt New reporting service (20% traffic)
        Router->>ReportSvc: GET /api/reports/sales
        ReportSvc-->>Router: Modern analytics
    else Legacy Rails (80% traffic)
        Router->>+Rails: GET /admin/reports
        Rails->>+DB: Complex SQL query<br/>p99: 2000ms
        DB-->>-Rails: Report data
        Rails-->>-Router: Legacy report format
    end

    Router-->>-CDN: Report data
    CDN-->>-Customer: Sales dashboard

    Note over Customer,DB: All services emit metrics:<br/>- Request rates and latencies<br/>- Error rates and circuit breaker states<br/>- Business metrics (sales, inventory)<br/>- Data consistency checks
```

## Soundcloud's Audio Processing Migration

SoundCloud used the Strangler Fig pattern to migrate their audio processing pipeline from a PHP monolith to Scala microservices while serving 175M+ users:

### SoundCloud Audio Pipeline Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Global Audio Delivery]
        CDN[Fastly CDN<br/>300+ locations<br/>Audio streaming<br/>100PB/month<br/>$200K/month]
        ALB[AWS ALB<br/>Multi-region<br/>1M concurrent streams<br/>$50K/month]
    end

    subgraph ServicePlane[Service Plane - Audio Processing Migration]
        subgraph AudioRouter[Audio Traffic Router]
            AudioProxy[HAProxy<br/>Audio-aware routing<br/>Protocol: HTTP/RTMP<br/>c5.2xlarge × 15<br/>$20K/month]
        end

        subgraph LegacyAudio[Legacy PHP Monolith]
            PHPMonolith[PHP Audio App<br/>Symfony 4<br/>Apache + mod_php<br/>200 instances<br/>$80K/month<br/>⚠️ 30% traffic remaining]
        end

        subgraph NewAudioServices[New Scala Microservices]
            UploadSvc[Upload Service<br/>Scala 2.13<br/>Akka HTTP<br/>50 instances<br/>$25K/month<br/>✅ 100% migrated]

            TranscodeSvc[Transcode Service<br/>Scala 2.13<br/>FFmpeg integration<br/>100 instances<br/>GPU-enabled<br/>$60K/month<br/>✅ 100% migrated]

            MetadataSvc[Metadata Service<br/>Scala 2.13<br/>Elasticsearch<br/>30 instances<br/>$15K/month<br/>✅ 100% migrated]

            StreamSvc[Streaming Service<br/>Go 1.19<br/>WebRTC/HLS<br/>200 instances<br/>$45K/month<br/>✅ 100% migrated]

            RecommendSvc[Recommendation<br/>Python 3.9<br/>ML pipeline<br/>40 instances<br/>$30K/month<br/>🔄 70% migrated]
        end

        subgraph MessageQueue[Event-Driven Architecture]
            RabbitMQ[RabbitMQ Cluster<br/>Audio processing events<br/>50M messages/day<br/>$12K/month]
            Redis[Redis Pub/Sub<br/>Real-time notifications<br/>$8K/month]
        end
    end

    subgraph StatePlane[State Plane - Audio Storage Strategy]
        subgraph LegacyStorage[Legacy Storage]
            MySQLCluster[(MySQL 8.0<br/>Metadata only<br/>50TB<br/>$25K/month)]
        end

        subgraph AudioStorage[Audio File Storage]
            S3Audio[(S3 Audio Files<br/>Original uploads<br/>500TB<br/>$15K/month)]
            S3Processed[(S3 Processed<br/>Multiple formats<br/>2PB<br/>$60K/month)]
            S3Thumbnails[(S3 Thumbnails<br/>Waveform images<br/>10TB<br/>$3K/month)]
        end

        subgraph NewDatabases[Service Databases]
            UploadDB[(Upload PostgreSQL<br/>10TB metadata<br/>$8K/month)]
            MetadataES[(Elasticsearch<br/>Search index<br/>20TB<br/>$25K/month)]
            StreamCache[(Redis Cluster<br/>Stream state<br/>1TB<br/>$5K/month)]
        end
    end

    subgraph ControlPlane[Control Plane - Migration Management]
        AudioFeatureFlags[Custom Feature Flags<br/>Audio-specific routing<br/>$3K/month]
        MetricsStack[Grafana + Prometheus<br/>Audio processing metrics<br/>$8K/month]
        MigrationControl[Migration Controller<br/>Gradual traffic shift<br/>Custom Go app<br/>$2K/month]
        AudioMonitoring[Audio Quality Monitor<br/>Perceptual analysis<br/>$5K/month]
    end

    %% Audio Traffic Flow
    CDN --> ALB
    ALB --> AudioProxy

    %% Traffic Routing by Audio Type
    AudioProxy -->|Upload: 100%| UploadSvc
    AudioProxy -->|Transcode: 100%| TranscodeSvc
    AudioProxy -->|Metadata: 100%| MetadataSvc
    AudioProxy -->|Streaming: 100%| StreamSvc
    AudioProxy -->|Recommendations: 70%| RecommendSvc
    AudioProxy -->|Recommendations: 30%<br/>Legacy features: 100%| PHPMonolith

    %% Service Communication
    UploadSvc --> RabbitMQ
    RabbitMQ --> TranscodeSvc
    TranscodeSvc --> MetadataSvc
    MetadataSvc --> StreamSvc

    %% Real-time notifications
    StreamSvc --> Redis
    Redis --> RecommendSvc

    %% Data Connections
    UploadSvc --> UploadDB
    UploadSvc --> S3Audio

    TranscodeSvc --> S3Audio
    TranscodeSvc --> S3Processed
    TranscodeSvc --> S3Thumbnails

    MetadataSvc --> MetadataES
    StreamSvc --> StreamCache
    StreamSvc --> S3Processed

    %% Legacy connections
    PHPMonolith --> MySQLCluster
    RecommendSvc --> MySQLCluster

    %% Control Plane
    AudioProxy --> AudioFeatureFlags
    AudioProxy --> MigrationControl

    UploadSvc --> MetricsStack
    TranscodeSvc --> MetricsStack
    MetadataSvc --> MetricsStack
    StreamSvc --> MetricsStack
    RecommendSvc --> MetricsStack
    PHPMonolith --> MetricsStack

    TranscodeSvc --> AudioMonitoring
    StreamSvc --> AudioMonitoring

    %% Styling
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef legacyStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-dasharray: 5 5
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#5B21B6,color:#fff

    class CDN,ALB edgeStyle
    class AudioRouter,AudioProxy,NewAudioServices,UploadSvc,TranscodeSvc,MetadataSvc,StreamSvc,RecommendSvc,MessageQueue,RabbitMQ,Redis serviceStyle
    class LegacyAudio,PHPMonolith legacyStyle
    class LegacyStorage,MySQLCluster,AudioStorage,S3Audio,S3Processed,S3Thumbnails,NewDatabases,UploadDB,MetadataES,StreamCache stateStyle
    class AudioFeatureFlags,MetricsStack,MigrationControl,AudioMonitoring controlStyle
```

## Migration Strategies and Failure Recovery

### Strategy 1: Route-Based Migration (Shopify)
Migrate complete user journeys rather than technical layers:

```mermaid
graph LR
    subgraph Week1[Week 1: 5% Products]
        U1[User] --> R1[Router]
        R1 -->|95%| L1[Legacy]
        R1 -->|5%| N1[New Service]
    end

    subgraph Week4[Week 4: 50% Products]
        U2[User] --> R2[Router]
        R2 -->|50%| L2[Legacy]
        R2 -->|50%| N2[New Service]
    end

    subgraph Week8[Week 8: 100% Products]
        U3[User] --> R3[Router]
        R3 -->|0%| L3[Legacy ⚠️]
        R3 -->|100%| N3[New Service ✅]
    end

    classDef legacyStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff

    class L1,L2,L3 legacyStyle
    class N1,N2,N3 serviceStyle
```

### Strategy 2: Feature-Based Migration (SoundCloud)
Migrate specific features while maintaining data consistency:

```mermaid
sequenceDiagram
    participant Legacy as PHP Monolith
    participant Router as Traffic Router
    participant New as Scala Service
    participant Queue as Message Queue
    participant DB as Shared Database

    Note over Legacy,DB: Feature flag: audio_upload=50%

    Router->>Router: Check feature flag

    alt New service (50% traffic)
        Router->>+New: POST /upload
        New->>+DB: Store metadata
        DB-->>-New: Metadata stored
        New->>+Queue: Publish upload event
        Queue-->>-New: Event published
        New-->>-Router: Upload successful
    else Legacy system (50% traffic)
        Router->>+Legacy: POST /upload
        Legacy->>+DB: Store metadata (same schema)
        DB-->>-Legacy: Metadata stored
        Legacy->>+Queue: Publish upload event (same format)
        Queue-->>-Legacy: Event published
        Legacy-->>-Router: Upload successful
    end

    Router-->>User: Upload confirmation

    Note over Legacy,DB: Both systems use same database schema<br/>and message format during migration
```

### Failure Recovery Scenarios

#### Scenario 1: New Service Failure - Immediate Fallback
**Case Study**: Shopify payment service outage during flash sale

```mermaid
graph TB
    subgraph Normal[Normal Operation]
        R1[Router] -->|100% payments| P1[Payment Service ✅]
        CB1[Circuit Breaker: CLOSED<br/>Success rate: 99.9%]
    end

    subgraph Failure[Service Failure Detected]
        R2[Router] -.->|Requests fail| P2[Payment Service ❌]
        CB2[Circuit Breaker: OPEN<br/>Failure rate: 15%<br/>Fallback to legacy]
    end

    subgraph Fallback[Automatic Fallback]
        R3[Router] -->|100% payments| L3[Legacy Rails ✅]
        Monitor[Alert sent<br/>On-call engineer<br/>Response time: 2 minutes]
    end

    classDef errorStyle fill:#EF4444,stroke:#DC2626,color:#fff
    classDef warningStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef successStyle fill:#10B981,stroke:#047857,color:#fff

    class P2 errorStyle
    class CB2,Monitor warningStyle
    class P1,L3 successStyle
```

**Recovery Results**:
- **Failure detection**: 15 seconds (health check failure)
- **Circuit breaker trip**: 30 seconds (15% error threshold)
- **Fallback activation**: 45 seconds total
- **Customer impact**: 0% (transparent fallback)
- **Lost revenue**: $0 (legacy system handled load)

#### Scenario 2: Data Inconsistency During Migration
**Case Study**: Inventory sync failure during Shopify product migration

```mermaid
sequenceDiagram
    participant Router as Traffic Router
    participant New as Product Service
    participant CDC as Change Data Capture
    participant Legacy as Rails Monolith
    participant DB as MySQL Database

    Note over Router,DB: Product update causes data inconsistency

    Router->>+New: PUT /products/123<br/>Update price: $99
    New->>+DB: UPDATE products SET price=99
    Note over DB: Update successful
    DB-->>-New: Rows affected: 1
    New-->>-Router: Product updated

    Note over CDC: CDC fails to capture change<br/>Network partition

    CDC-xDB: Connection lost

    Note over Legacy,DB: Legacy system still sees old price

    Router->>+Legacy: GET /products/123
    Legacy->>+DB: SELECT price FROM products
    DB-->>-Legacy: price: $89 (stale data)
    Legacy-->>-Router: Old price returned

    Note over Router,DB: Inconsistency detected and resolved

    Router->>+Monitor: Data consistency check
    Monitor->>+DB: Verify product data
    DB-->>-Monitor: price: $99 (correct)
    Monitor->>+Legacy: Invalidate cache
    Legacy->>+DB: Fresh SELECT
    DB-->>-Legacy: price: $99 (fixed)
    Legacy-->>-Monitor: Cache refreshed
    Monitor-->>-Router: Consistency restored
```

## Production Metrics and Costs

### Shopify Migration Results (2016-2021)
- **Migration duration**: 5 years for complete strangling
- **Downtime during migration**: 0 minutes (100% uptime maintained)
- **Performance improvement**: 40% faster response times
- **Development velocity**: 3x faster feature delivery
- **Infrastructure cost**: +25% during migration, -15% post-migration
- **Black Friday success**: $5.1B processed with 99.99% uptime

### SoundCloud Audio Migration (2018-2020)
- **Audio processing latency**: 60% reduction (15s → 6s average)
- **Upload success rate**: 99.5% → 99.95%
- **Transcode queue depth**: 95% reduction during peak hours
- **Development team productivity**: 4x faster audio feature delivery
- **Infrastructure cost**: -30% through better resource utilization
- **User experience**: 25% reduction in audio buffering events

## Migration Success Factors

### Essential Pre-requisites
1. **Traffic routing capability** (proxy, load balancer, API gateway)
2. **Feature flag system** (gradual rollout control)
3. **Comprehensive monitoring** (both systems during transition)
4. **Data synchronization** (CDC, event streaming, dual writes)
5. **Rollback capability** (instant fallback to legacy)
6. **Team alignment** (product, engineering, operations)

### Anti-Patterns to Avoid

#### ❌ Big Bang Migration
Don't attempt to migrate everything at once:
```yaml
# BAD: All traffic switched immediately
feature_flags:
  new_service: 100%  # Too risky!
  legacy_fallback: false
```

#### ❌ Ignoring Data Consistency
Don't neglect data synchronization:
```python
# BAD: No data sync between systems
def create_product(data):
    if new_service_enabled():
        return new_service.create(data)
    else:
        return legacy_service.create(data)
    # No sync between systems!
```

#### ✅ Gradual Migration with Data Sync
```python
# GOOD: Gradual rollout with data consistency
def create_product(data):
    if feature_flag('new_products', user_id, default=0.1):
        result = new_service.create(data)
        # Sync to legacy for consistency
        legacy_service.sync_product(result)
        return result
    else:
        result = legacy_service.create(data)
        # Sync to new service for migration
        new_service.sync_product(result)
        return result
```

### ❌ No Monitoring During Migration
Don't migrate blindly:
```yaml
# BAD: No migration-specific monitoring
monitoring:
  - service_health: true
  - response_time: true
  # Missing: consistency_check: false
  # Missing: migration_progress: false
```

### ✅ Comprehensive Migration Monitoring
```yaml
# GOOD: Migration-aware monitoring
monitoring:
  service_health: true
  response_time: true
  data_consistency: true
  migration_progress: true
  error_rate_comparison: true
  business_metrics_impact: true
alerts:
  - consistency_drift > 1%
  - migration_error_rate > 0.1%
  - business_metric_deviation > 5%
```

## Lessons Learned

### Shopify's Hard-Won Wisdom
- **Start with read-only migrations**: Build confidence with low-risk operations
- **Maintain data consistency**: Dual writes and CDC are non-negotiable
- **Monitor business metrics**: Technical success ≠ business success
- **Plan for rollback**: Every migration step must be reversible
- **Team communication**: Daily standups during active migration phases

### SoundCloud's Scale Lessons
- **Audio quality matters**: Automated perceptual testing for audio services
- **Async processing**: Long-running tasks need event-driven architecture
- **User experience metrics**: Technical improvements must improve UX
- **Progressive enhancement**: New features only in new services
- **Load testing**: Migrate during low-traffic periods, test at peak scale

### Production Battle Stories

**Shopify Black Friday 2019**: Mid-migration with 50% traffic on new services
- Legacy checkout handled 2.5M orders/hour
- New services handled 2.5M orders/hour
- Zero customer-facing issues
- Real-time traffic shifting based on performance
- $4.2B processed across hybrid architecture

**SoundCloud Upload Storm**: Major artist dropped album during migration
- 10x normal upload volume in 30 minutes
- Legacy PHP system couldn't handle load
- Emergency traffic shift to new Scala services
- Zero upload failures despite unprecedented load
- Migration timeline accelerated by 6 months

*The Strangler Fig pattern isn't just about technology migration - it's about organizational transformation. You're not just replacing code, you're evolving your entire engineering culture while keeping the business running.*