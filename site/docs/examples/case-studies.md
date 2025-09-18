# Case Studies

Real-world production architectures from companies handling massive scale.

## Netflix: Global Video Streaming

Netflix serves 200M+ subscribers with 99.99% uptime during 15% of global internet traffic.

### Complete Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Global CDN]
        CDN_US[US Edge - 150ms p99]
        CDN_EU[EU Edge - 120ms p99]
        CDN_ASIA[Asia Edge - 180ms p99]
        AWS_CF[CloudFront - 45 locations]
    end

    subgraph ServicePlane[Service Plane - Microservices]
        API_GW[API Gateway - Kong]
        USER_SVC[User Service - Java]
        REC_SVC[Recommendation - Scala]
        STREAM_SVC[Streaming Service - Go]
        BILLING_SVC[Billing Service - Python]
    end

    subgraph StatePlane[State Plane - Data Layer]
        CASSANDRA[(Cassandra - User Data)]
        MYSQL[(MySQL - Billing)]
        ES[(ElasticSearch - Search)]
        S3[(S3 - Content)]
    end

    subgraph ControlPlane[Control Plane - Operations]
        ATLAS[Atlas - Monitoring]
        SPINNAKER[Spinnaker - Deployment]
        EUREKA[Eureka - Discovery]
        HYSTRIX[Hystrix - Circuit Breaker]
    end

    %% Request flow
    USER[iPhone App] --> CDN_US
    CDN_US --> API_GW
    API_GW --> USER_SVC
    API_GW --> REC_SVC
    API_GW --> STREAM_SVC

    %% Data connections
    USER_SVC --> CASSANDRA
    BILLING_SVC --> MYSQL
    REC_SVC --> ES
    STREAM_SVC --> S3

    %% Control connections
    USER_SVC --> EUREKA
    API_GW --> HYSTRIX

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class CDN_US,CDN_EU,CDN_ASIA,AWS_CF edgeStyle
    class API_GW,USER_SVC,REC_SVC,STREAM_SVC,BILLING_SVC serviceStyle
    class CASSANDRA,MYSQL,ES,S3 stateStyle
    class ATLAS,SPINNAKER,EUREKA,HYSTRIX controlStyle
```

### Global Content Distribution

```mermaid
graph TB
    subgraph ContentPipeline[Content Processing Pipeline]
        STUDIO[Netflix Studios]
        ENCODING[Encoding - AWS Elemental]
        CDN_ORIGIN[CDN Origin - AWS S3]
    end

    subgraph GlobalCDN[Global CDN - Open Connect]
        ISP1[Comcast ISP Cache - 10TB]
        ISP2[Verizon ISP Cache - 8TB]
        ISP3[AT&T ISP Cache - 12TB]
        EDGE1[Netflix Edge - US East]
        EDGE2[Netflix Edge - EU West]
        EDGE3[Netflix Edge - Asia Pacific]
    end

    subgraph Metrics[Performance Metrics]
        LATENCY[Video Start: <100ms p99]
        REBUFFER[Rebuffer Rate: <0.5%]
        QUALITY[4K Streams: 25% of traffic]
        COST[CDN Cost: $0.02/GB delivered]
    end

    STUDIO --> ENCODING
    ENCODING --> CDN_ORIGIN
    CDN_ORIGIN --> EDGE1
    CDN_ORIGIN --> EDGE2
    CDN_ORIGIN --> EDGE3

    EDGE1 --> ISP1
    EDGE1 --> ISP2
    EDGE2 --> ISP3

    classDef contentStyle fill:#9966CC,stroke:#663399,color:#fff
    classDef cdnStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef metricStyle fill:#FF6600,stroke:#CC3300,color:#fff

    class STUDIO,ENCODING,CDN_ORIGIN contentStyle
    class ISP1,ISP2,ISP3,EDGE1,EDGE2,EDGE3 cdnStyle
    class LATENCY,REBUFFER,QUALITY,COST metricStyle
```

### Chaos Engineering Architecture

```mermaid
graph TB
    subgraph ChaosTools[Chaos Engineering Tools]
        MONKEY[Chaos Monkey - Instance Termination]
        GORILLA[Chaos Gorilla - AZ Failures]
        KONG[Chaos Kong - Region Failures]
        LATENCY[Latency Monkey - Network Delays]
    end

    subgraph ProductionEnv[Production Environment]
        AZ1[Availability Zone 1]
        AZ2[Availability Zone 2]
        AZ3[Availability Zone 3]
        REGION_US[US Region]
        REGION_EU[EU Region]
    end

    subgraph Monitoring[Monitoring & Response]
        ALERT[PagerDuty Alerts]
        RUNBOOK[Automated Runbooks]
        ROLLBACK[Automated Rollback]
        DASHBOARD[Real-time Dashboards]
    end

    MONKEY -.->|Random Instance Kill| AZ1
    GORILLA -.->|Zone Failure| AZ2
    KONG -.->|Region Failure| REGION_US
    LATENCY -.->|Network Chaos| AZ3

    AZ1 --> ALERT
    AZ2 --> DASHBOARD
    REGION_US --> RUNBOOK
    AZ3 --> ROLLBACK

    classDef chaosStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef prodStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef monitorStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class MONKEY,GORILLA,KONG,LATENCY chaosStyle
    class AZ1,AZ2,AZ3,REGION_US,REGION_EU prodStyle
    class ALERT,RUNBOOK,ROLLBACK,DASHBOARD monitorStyle
```

### Cost & Scale Metrics

| Component | Technology | Scale | Cost/Month | SLA |
|-----------|------------|--------|------------|-----|
| CDN | Open Connect | 45 locations | $15M | 99.95% |
| Compute | AWS EC2 | 100K+ instances | $25M | 99.9% |
| Storage | AWS S3 | 100PB+ content | $5M | 99.99% |
| Database | Cassandra | 1000+ nodes | $3M | 99.95% |
| Monitoring | Atlas | 2M+ metrics/sec | $1M | 99.9% |

---

## Uber: Real-time Matching Platform

Uber matches 100M+ users with <5 second latency across 60+ countries using geospatial indexing.

### Complete Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Mobile & Web]
        RIDER_APP[Rider App - React Native]
        DRIVER_APP[Driver App - Native iOS/Android]
        WEB_APP[Web Portal - React]
        LOAD_BAL[Load Balancer - ALB]
    end

    subgraph ServicePlane[Service Plane - Microservices]
        API_GATEWAY[API Gateway - Kong]
        MATCHING_SVC[Matching Service - Go]
        LOCATION_SVC[Location Service - C++]
        TRIP_SVC[Trip Service - Java]
        PAYMENT_SVC[Payment Service - Python]
        PRICING_SVC[Pricing Service - Scala]
    end

    subgraph StatePlane[State Plane - Data Stores]
        REDIS[(Redis - Location Cache)]
        CASSANDRA[(Cassandra - Trip Data)]
        MYSQL[(MySQL - User Data)]
        S3[(S3 - Analytics)]
        KAFKA[(Kafka - Event Stream)]
    end

    subgraph ControlPlane[Control Plane - Platform]
        JAEGER[Jaeger - Tracing]
        PROMETHEUS[Prometheus - Metrics]
        CONSUL[Consul - Service Discovery]
        RINGPOP[RingPop - Consistent Hashing]
    end

    %% Request flows
    RIDER_APP --> LOAD_BAL
    DRIVER_APP --> LOAD_BAL
    LOAD_BAL --> API_GATEWAY
    API_GATEWAY --> MATCHING_SVC
    API_GATEWAY --> LOCATION_SVC
    API_GATEWAY --> TRIP_SVC

    %% Data flows
    LOCATION_SVC --> REDIS
    TRIP_SVC --> CASSANDRA
    PAYMENT_SVC --> MYSQL
    MATCHING_SVC --> KAFKA

    %% Control flows
    MATCHING_SVC --> RINGPOP
    LOCATION_SVC --> CONSUL

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class RIDER_APP,DRIVER_APP,WEB_APP,LOAD_BAL edgeStyle
    class API_GATEWAY,MATCHING_SVC,LOCATION_SVC,TRIP_SVC,PAYMENT_SVC,PRICING_SVC serviceStyle
    class REDIS,CASSANDRA,MYSQL,S3,KAFKA stateStyle
    class JAEGER,PROMETHEUS,CONSUL,RINGPOP controlStyle
```

### Real-time Matching Algorithm

```mermaid
graph TB
    subgraph GeoIndexing[Geospatial Indexing - S2 Geometry]
        S2_CELL[S2 Cell Grid]
        DRIVER_INDEX[Driver Index by Cell]
        LOCATION_UPDATE[Location Updates - 4Hz]
    end

    subgraph MatchingEngine[Matching Engine]
        REQUEST[Ride Request]
        RADIUS_SEARCH[Search 2km Radius]
        FILTER[Filter Available Drivers]
        RANK[Rank by ETA + Rating]
        DISPATCH[Dispatch to Best Driver]
    end

    subgraph EventStream[Event Processing]
        KAFKA_TOPIC[driver.location.updated]
        LOCATION_PROCESSOR[Location Processor]
        TRIP_PROCESSOR[Trip State Processor]
        NOTIFICATION[Push Notifications]
    end

    REQUEST --> RADIUS_SEARCH
    RADIUS_SEARCH --> S2_CELL
    S2_CELL --> DRIVER_INDEX
    DRIVER_INDEX --> FILTER
    FILTER --> RANK
    RANK --> DISPATCH

    DISPATCH --> KAFKA_TOPIC
    KAFKA_TOPIC --> TRIP_PROCESSOR
    TRIP_PROCESSOR --> NOTIFICATION

    LOCATION_UPDATE --> LOCATION_PROCESSOR
    LOCATION_PROCESSOR --> DRIVER_INDEX

    classDef geoStyle fill:#9966CC,stroke:#663399,color:#fff
    classDef matchStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef eventStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class S2_CELL,DRIVER_INDEX,LOCATION_UPDATE geoStyle
    class REQUEST,RADIUS_SEARCH,FILTER,RANK,DISPATCH matchStyle
    class KAFKA_TOPIC,LOCATION_PROCESSOR,TRIP_PROCESSOR,NOTIFICATION eventStyle
```

### Evolution from Monolith to Microservices

```mermaid
graph TB
    subgraph Phase1[Phase 1: Monolith (2009-2013)]
        MONO[Single Python App]
        MONO_DB[(Single PostgreSQL)]
        PROB1[Problems: Single Point of Failure]
        PROB2[Deployment Bottlenecks]
    end

    subgraph Phase2[Phase 2: SOA (2013-2016)]
        USER_SVC[User Service]
        TRIP_SVC[Trip Service]
        PAY_SVC[Payment Service]
        MATCH_SVC[Matching Service]
        HTTP[HTTP/REST APIs]
    end

    subgraph Phase3[Phase 3: Platform (2016+)]
        MESH[Service Mesh - Envoy]
        PLATFORM[Platform Services]
        OBSERVABILITY[Distributed Tracing]
        ASYNC[Event-Driven Architecture]
    end

    Phase1 --> Phase2
    Phase2 --> Phase3

    classDef phase1Style fill:#CC0000,stroke:#990000,color:#fff
    classDef phase2Style fill:#FF8800,stroke:#CC6600,color:#fff
    classDef phase3Style fill:#00AA00,stroke:#007700,color:#fff

    class MONO,MONO_DB,PROB1,PROB2 phase1Style
    class USER_SVC,TRIP_SVC,PAY_SVC,MATCH_SVC,HTTP phase2Style
    class MESH,PLATFORM,OBSERVABILITY,ASYNC phase3Style
```

### Hot Partition Handling

```mermaid
graph TB
    subgraph HotSpots[Hot Partition Detection]
        AIRPORT[Airport - 10x Normal Traffic]
        STADIUM[Stadium - 20x Normal Traffic]
        MONITOR[Load Monitor - Real-time]
        THRESHOLD[Threshold: >1000 requests/sec]
    end

    subgraph LoadBalancing[Dynamic Load Balancing]
        SPLIT[Split Hot Partition]
        REDISTRIBUTE[Redistribute Load]
        SHED[Load Shedding - Drop Low Priority]
        CIRCUIT[Circuit Breaker - Fail Fast]
    end

    subgraph Recovery[Recovery Strategy]
        SCALE_OUT[Auto-scale Instances]
        CACHE_WARM[Warm Cache]
        TRAFFIC_SHAPE[Traffic Shaping]
        DEGRADE[Graceful Degradation]
    end

    AIRPORT --> MONITOR
    STADIUM --> MONITOR
    MONITOR --> THRESHOLD
    THRESHOLD --> SPLIT
    SPLIT --> REDISTRIBUTE
    REDISTRIBUTE --> SHED

    SHED --> SCALE_OUT
    SCALE_OUT --> CACHE_WARM
    CACHE_WARM --> TRAFFIC_SHAPE

    classDef hotStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef balanceStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef recoveryStyle fill:#00AA00,stroke:#007700,color:#fff

    class AIRPORT,STADIUM,MONITOR,THRESHOLD hotStyle
    class SPLIT,REDISTRIBUTE,SHED,CIRCUIT balanceStyle
    class SCALE_OUT,CACHE_WARM,TRAFFIC_SHAPE,DEGRADE recoveryStyle
```

### Cost & Performance Metrics

| Component | Technology | Scale | Latency | Cost/Month |
|-----------|------------|--------|---------|------------|
| Matching | Go Services | 1M matches/hour | <3s p99 | $2M |
| Location | C++ Services | 10M updates/sec | <50ms p99 | $5M |
| Database | Cassandra | 500TB data | <10ms read | $1.5M |
| Cache | Redis Cluster | 100TB memory | <1ms p99 | $800K |
| CDN | CloudFlare | 50 regions | <100ms p99 | $500K |

---

## Amazon: E-commerce Platform

Amazon handles 1B+ items with 99.95% uptime where every minute down costs $1M during Prime Day.

### Complete Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Global Frontend]
        CF[CloudFront - 400+ Locations]
        ALB[Application Load Balancer]
        WAF[Web Application Firewall]
        ROUTE53[Route 53 DNS]
    end

    subgraph ServicePlane[Service Plane - SOA Services]
        GATEWAY[API Gateway]
        CATALOG[Catalog Service - Java]
        CART[Cart Service - DynamoDB]
        ORDER[Order Service - C++]
        INVENTORY[Inventory Service - Rust]
        PAYMENT[Payment Service - Java]
        SHIPPING[Shipping Service - Python]
    end

    subgraph StatePlane[State Plane - Data Layer]
        DYNAMODB[(DynamoDB - Cart/Session)]
        RDS[(RDS Aurora - Orders)]
        REDSHIFT[(Redshift - Analytics)]
        S3_CATALOG[(S3 - Product Images)]
        ELASTICSEARCH[(Elasticsearch - Search)]
    end

    subgraph ControlPlane[Control Plane - AWS Services]
        CLOUDWATCH[CloudWatch - Monitoring]
        XRAY[X-Ray - Tracing]
        CONFIG[AWS Config - Compliance]
        AUTOSCALING[Auto Scaling Groups]
    end

    %% Request flows
    ROUTE53 --> CF
    CF --> WAF
    WAF --> ALB
    ALB --> GATEWAY
    GATEWAY --> CATALOG
    GATEWAY --> CART
    GATEWAY --> ORDER

    %% Data flows
    CART --> DYNAMODB
    ORDER --> RDS
    CATALOG --> S3_CATALOG
    INVENTORY --> ELASTICSEARCH

    %% Control flows
    GATEWAY --> CLOUDWATCH
    ORDER --> XRAY

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class CF,ALB,WAF,ROUTE53 edgeStyle
    class GATEWAY,CATALOG,CART,ORDER,INVENTORY,PAYMENT,SHIPPING serviceStyle
    class DYNAMODB,RDS,REDSHIFT,S3_CATALOG,ELASTICSEARCH stateStyle
    class CLOUDWATCH,XRAY,CONFIG,AUTOSCALING controlStyle
```

### Prime Day Traffic Handling

```mermaid
graph TB
    subgraph TrafficPrediction[Traffic Prediction & Pre-scaling]
        FORECAST[Historical Data + ML Forecasting]
        CAPACITY[Capacity Planning - 10x Normal]
        PRESCALE[Pre-scale 30min Before Event]
        WARMUP[Cache Warming Strategy]
    end

    subgraph LoadManagement[Load Management]
        PRIORITY[Request Priority Classification]
        SHED[Load Shedding - Drop Low Priority]
        QUEUE[Request Queuing with Backpressure]
        CIRCUIT[Circuit Breakers per Service]
    end

    subgraph ResponseStrategy[Response Strategy]
        STALE[Serve Stale Data vs Error]
        DEGRADE[Graceful Feature Degradation]
        CACHE[Aggressive Caching - 99.9% Hit Rate]
        STATIC[Static Fallback Pages]
    end

    FORECAST --> CAPACITY
    CAPACITY --> PRESCALE
    PRESCALE --> WARMUP

    WARMUP --> PRIORITY
    PRIORITY --> SHED
    SHED --> QUEUE
    QUEUE --> CIRCUIT

    CIRCUIT --> STALE
    STALE --> DEGRADE
    DEGRADE --> CACHE
    CACHE --> STATIC

    classDef predictionStyle fill:#9966CC,stroke:#663399,color:#fff
    classDef loadStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef responseStyle fill:#00AA00,stroke:#007700,color:#fff

    class FORECAST,CAPACITY,PRESCALE,WARMUP predictionStyle
    class PRIORITY,SHED,QUEUE,CIRCUIT loadStyle
    class STALE,DEGRADE,CACHE,STATIC responseStyle
```

### Shopping Cart Architecture

```mermaid
graph TB
    subgraph CartOperations[Shopping Cart Operations]
        ADD[Add Item - Optimistic Write]
        UPDATE[Update Quantity - Last Write Wins]
        REMOVE[Remove Item - Idempotent]
        CHECKOUT[Checkout - Two-Phase Commit]
    end

    subgraph DataConsistency[Data Consistency Strategy]
        EVENTUAL[Eventually Consistent Reads]
        CONFLICT[Conflict Resolution - Business Rules]
        BACKUP[Cross-Region Backup]
        SESSION[Session Affinity to Reduce Conflicts]
    end

    subgraph Performance[Performance Optimizations]
        CACHE[DynamoDB DAX - μs Latency]
        COMPRESS[Gzip Compression]
        BATCH[Batch Operations]
        PRELOAD[Preload Related Items]
    end

    ADD --> EVENTUAL
    UPDATE --> CONFLICT
    REMOVE --> BACKUP
    CHECKOUT --> SESSION

    EVENTUAL --> CACHE
    CONFLICT --> COMPRESS
    BACKUP --> BATCH
    SESSION --> PRELOAD

    classDef operationStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef consistencyStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef perfStyle fill:#00AA00,stroke:#007700,color:#fff

    class ADD,UPDATE,REMOVE,CHECKOUT operationStyle
    class EVENTUAL,CONFLICT,BACKUP,SESSION consistencyStyle
    class CACHE,COMPRESS,BATCH,PRELOAD perfStyle
```

### Recommendation Engine Pipeline

```mermaid
graph LR
    subgraph DataIngestion[Data Ingestion - Real-time]
        CLICK[Click Events - 100M/hour]
        VIEW[Page Views - 500M/hour]
        PURCHASE[Purchases - 10M/hour]
        KINESIS[Kinesis Data Streams]
    end

    subgraph Processing[ML Processing Pipeline]
        SPARK[Spark Streaming - Feature Extraction]
        SAGEMAKER[SageMaker - Model Training]
        LAMBDA[Lambda - Real-time Inference]
        BATCH[EMR - Batch Processing]
    end

    subgraph Serving[Recommendation Serving]
        ELASTICACHE[ElastiCache - Hot Recommendations]
        PERSONALIZE[Amazon Personalize - Real-time API]
        AB_TEST[A/B Testing Framework]
        FALLBACK[Fallback to Popular Items]
    end

    CLICK --> KINESIS
    VIEW --> KINESIS
    PURCHASE --> KINESIS
    KINESIS --> SPARK

    SPARK --> SAGEMAKER
    SAGEMAKER --> LAMBDA
    LAMBDA --> ELASTICACHE
    SPARK --> BATCH

    ELASTICACHE --> PERSONALIZE
    PERSONALIZE --> AB_TEST
    AB_TEST --> FALLBACK

    classDef dataStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef processStyle fill:#9966CC,stroke:#663399,color:#fff
    classDef servingStyle fill:#00AA00,stroke:#007700,color:#fff

    class CLICK,VIEW,PURCHASE,KINESIS dataStyle
    class SPARK,SAGEMAKER,LAMBDA,BATCH processStyle
    class ELASTICACHE,PERSONALIZE,AB_TEST,FALLBACK servingStyle
```

### Cost & Performance Metrics

| Component | Technology | Scale | Availability | Cost/Month |
|-----------|------------|--------|--------------|------------|
| CDN | CloudFront | 400+ locations | 99.99% | $50M |
| Compute | EC2 + Lambda | 1M+ instances | 99.9% | $200M |
| Database | DynamoDB | 100TB+ | 99.99% | $30M |
| Storage | S3 | 1000PB+ | 99.999% | $20M |
| Analytics | Redshift | 100PB warehouse | 99.9% | $10M |

---

## WhatsApp: Global Messaging Platform

WhatsApp delivers 100B+ messages/day to 2B users with just 50 engineers using Erlang's actor model.

### Complete Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Global Access]
        DNS[DNS Load Balancing]
        NGINX[Nginx - FreeBSD]
        SSL[SSL Termination]
        GEOIP[GeoIP Routing]
    end

    subgraph ServicePlane[Service Plane - Erlang/OTP]
        CONN_MGR[Connection Manager - 1M connections/server]
        MSG_ROUTER[Message Router - Actor Model]
        PRESENCE[Presence Service - Online Status]
        GROUP_MGR[Group Manager - Broadcast Logic]
        MEDIA_SVC[Media Service - File Uploads]
    end

    subgraph StatePlane[State Plane - Minimal Storage]
        MNESIA[(Mnesia - User Sessions)]
        MYSQL[(MySQL - User Registration)]
        FILE_STORE[(FreeBSD - Message Storage)]
        MEDIA_STORE[(S3 - Media Files)]
    end

    subgraph ControlPlane[Control Plane - Operations]
        STATS[Custom Erlang Stats]
        ALERTS[Custom Monitoring]
        DEPLOY[Hot Code Deploy]
        BACKUP[Incremental Backup]
    end

    %% Flows
    DNS --> NGINX
    NGINX --> SSL
    SSL --> CONN_MGR
    CONN_MGR --> MSG_ROUTER
    MSG_ROUTER --> PRESENCE
    MSG_ROUTER --> GROUP_MGR

    %% Data
    CONN_MGR --> MNESIA
    MSG_ROUTER --> FILE_STORE
    MEDIA_SVC --> MEDIA_STORE

    %% Control
    MSG_ROUTER --> STATS
    CONN_MGR --> ALERTS

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class DNS,NGINX,SSL,GEOIP edgeStyle
    class CONN_MGR,MSG_ROUTER,PRESENCE,GROUP_MGR,MEDIA_SVC serviceStyle
    class MNESIA,MYSQL,FILE_STORE,MEDIA_STORE stateStyle
    class STATS,ALERTS,DEPLOY,BACKUP controlStyle
```

### Actor Model Message Delivery

```mermaid
graph TB
    subgraph ConnectionLayer[Connection Layer - Massive Concurrency]
        USER1[User 1 Process - PID: 12345]
        USER2[User 2 Process - PID: 12346]
        USER3[User 3 Process - PID: 12347]
        USERN[User N Process - PID: 99999]
        REGISTRY[Process Registry - ETS Table]
    end

    subgraph MessageFlow[Message Flow - Async Delivery]
        RECEIVE[Receive Message]
        LOOKUP[Lookup Recipient Process]
        DELIVER[Send to Process Mailbox]
        OFFLINE[Store if Offline]
        ACK[Send Delivery Ack]
    end

    subgraph FaultTolerance[Fault Tolerance - Let It Crash]
        SUPERVISOR[Supervisor Tree]
        RESTART[Restart Failed Process]
        ISOLATE[Isolate Failures]
        PRESERVE[Preserve System State]
    end

    USER1 --> REGISTRY
    USER2 --> REGISTRY
    USER3 --> REGISTRY
    USERN --> REGISTRY

    REGISTRY --> LOOKUP
    LOOKUP --> DELIVER
    DELIVER --> ACK
    LOOKUP --> OFFLINE

    SUPERVISOR --> RESTART
    RESTART --> ISOLATE
    ISOLATE --> PRESERVE

    classDef actorStyle fill:#9966CC,stroke:#663399,color:#fff
    classDef flowStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef faultStyle fill:#CC0000,stroke:#990000,color:#fff

    class USER1,USER2,USER3,USERN,REGISTRY actorStyle
    class RECEIVE,LOOKUP,DELIVER,OFFLINE,ACK flowStyle
    class SUPERVISOR,RESTART,ISOLATE,PRESERVE faultStyle
```

### Global Distribution Strategy

```mermaid
graph TB
    subgraph RegionUS[US Region - Primary]
        US_LB[Load Balancer - 500 servers]
        US_CHAT[Chat Servers - 1M connections each]
        US_DB[(User Registry - Sharded)]
        US_METRICS[Metrics Collection]
    end

    subgraph RegionEU[EU Region - GDPR Compliant]
        EU_LB[Load Balancer - 300 servers]
        EU_CHAT[Chat Servers - 800K connections each]
        EU_DB[(User Registry - Local)]
        EU_METRICS[Metrics Collection]
    end

    subgraph RegionASIA[Asia Region - High Density]
        ASIA_LB[Load Balancer - 400 servers]
        ASIA_CHAT[Chat Servers - 1.2M connections each]
        ASIA_DB[(User Registry - Sharded)]
        ASIA_METRICS[Metrics Collection]
    end

    subgraph CrossRegion[Cross-Region Messaging]
        ROUTE[Message Routing Logic]
        PRESENCE_SYNC[Presence Synchronization]
        FEDERATION[Server-to-Server Protocol]
        BACKUP_SYNC[Backup Synchronization]
    end

    US_CHAT -.->|Cross-region message| EU_CHAT
    EU_CHAT -.->|Cross-region message| ASIA_CHAT
    ASIA_CHAT -.->|Cross-region message| US_CHAT

    ROUTE --> PRESENCE_SYNC
    PRESENCE_SYNC --> FEDERATION
    FEDERATION --> BACKUP_SYNC

    classDef regionStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef crossStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class US_LB,US_CHAT,US_DB,US_METRICS,EU_LB,EU_CHAT,EU_DB,EU_METRICS,ASIA_LB,ASIA_CHAT,ASIA_DB,ASIA_METRICS regionStyle
    class ROUTE,PRESENCE_SYNC,FEDERATION,BACKUP_SYNC crossStyle
```

### Performance Optimizations

```mermaid
graph TB
    subgraph MemoryOpt[Memory Optimization - Aggressive GC]
        SMALL_HEAP[Small Heap Sizes - 233 words]
        FREQ_GC[Frequent GC - Every 10 operations]
        BINARY_OPT[Binary Optimization - Large binaries off-heap]
        SHARED_TERMS[Share Terms Between Processes]
    end

    subgraph NetworkOpt[Network Optimization - Low Latency]
        TCP_NODELAY[TCP_NODELAY - Disable Nagle]
        LARGE_BUFFERS[Large Socket Buffers - 8MB]
        KEEPALIVE[TCP Keepalive - Connection Health]
        COMPRESSION[Message Compression - Zlib]
    end

    subgraph ConcurrencyOpt[Concurrency Optimization]
        SCHEDULER[SMP Scheduler - Multi-core Usage]
        PROCESS_SPAWN[Fast Process Spawn - μs latency]
        MESSAGE_PASS[Message Passing - Copy-free]
        LOCK_FREE[Lock-free Data Structures]
    end

    SMALL_HEAP --> FREQ_GC
    FREQ_GC --> BINARY_OPT
    BINARY_OPT --> SHARED_TERMS

    TCP_NODELAY --> LARGE_BUFFERS
    LARGE_BUFFERS --> KEEPALIVE
    KEEPALIVE --> COMPRESSION

    SCHEDULER --> PROCESS_SPAWN
    PROCESS_SPAWN --> MESSAGE_PASS
    MESSAGE_PASS --> LOCK_FREE

    classDef memStyle fill:#9966CC,stroke:#663399,color:#fff
    classDef netStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef concStyle fill:#00AA00,stroke:#007700,color:#fff

    class SMALL_HEAP,FREQ_GC,BINARY_OPT,SHARED_TERMS memStyle
    class TCP_NODELAY,LARGE_BUFFERS,KEEPALIVE,COMPRESSION netStyle
    class SCHEDULER,PROCESS_SPAWN,MESSAGE_PASS,LOCK_FREE concStyle
```

### Cost & Performance Metrics

| Component | Technology | Scale | Latency | Cost/Month |
|-----------|------------|--------|---------|------------|
| Servers | FreeBSD | 1200 servers | <50ms p99 | $2M |
| Connections | Erlang/OTP | 2B concurrent | <10ms local | $500K |
| Storage | Custom | 1PB messages | <1ms write | $200K |
| Bandwidth | Global ISPs | 100Gbps peak | Regional | $1M |
| Team | Engineers | 50 people | 24/7 support | $800K |

---

## Architecture Patterns Summary

### Common Evolution Path

```mermaid
graph LR
    subgraph Phase1[Phase 1: Startup (0-1M users)]
        MONOLITH[Monolithic Application]
        SINGLE_DB[(Single Database)]
        SIMPLE[Simple Deployment]
    end

    subgraph Phase2[Phase 2: Growth (1M-10M users)]
        SERVICES[Microservices]
        MULTI_DB[(Multiple Databases)]
        LOAD_BAL[Load Balancers]
    end

    subgraph Phase3[Phase 3: Scale (10M-100M users)]
        PLATFORM[Platform Services]
        SHARDED[(Sharded Data)]
        REGIONS[Multi-Region]
    end

    subgraph Phase4[Phase 4: Global (100M+ users)]
        ECOSYSTEM[Service Ecosystem]
        GLOBAL_DB[(Global Distribution)]
        EDGE[Edge Computing]
    end

    Phase1 --> Phase2
    Phase2 --> Phase3
    Phase3 --> Phase4

    classDef phase1Style fill:#CC0000,stroke:#990000,color:#fff
    classDef phase2Style fill:#FF8800,stroke:#CC6600,color:#fff
    classDef phase3Style fill:#00AA00,stroke:#007700,color:#fff
    classDef phase4Style fill:#0066CC,stroke:#004499,color:#fff

    class MONOLITH,SINGLE_DB,SIMPLE phase1Style
    class SERVICES,MULTI_DB,LOAD_BAL phase2Style
    class PLATFORM,SHARDED,REGIONS phase3Style
    class ECOSYSTEM,GLOBAL_DB,EDGE phase4Style
```

### Universal Principles

| Principle | Netflix | Uber | Amazon | WhatsApp |
|-----------|---------|------|--------|----------|
| **Embrace Failure** | Chaos Engineering | Circuit Breakers | Load Shedding | Let It Crash |
| **Eventual Consistency** | Multi-region CDN | Location Updates | Shopping Cart | Message Delivery |
| **Horizontal Scaling** | Microservices | Geospatial Sharding | Service-Oriented | Process Per User |
| **Observability** | Atlas + Jaeger | Prometheus + Jaeger | CloudWatch + X-Ray | Custom Erlang Tools |
| **Automation** | Spinnaker CI/CD | Auto-scaling | Infrastructure as Code | Hot Code Deploy |

These companies demonstrate that while technologies differ, fundamental distributed systems principles remain constant across domains and scales.