# Twitter/X Complete Architecture

## Overview
Twitter/X's architecture handles 500M+ tweets daily, serving 300B+ tweets annually to a global audience. The platform focuses on real-time information distribution with massive scale and low latency requirements.

## Complete System Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Global Distribution]
        CDN[Twitter CDN<br/>Global: 150+ locations<br/>Static content: 90% hit ratio<br/>Video/image optimization]
        LB[Load Balancers<br/>Citrix NetScaler<br/>AWS ALB/NLB<br/>Peak: 5M RPS]
        WAF[Web Application Firewall<br/>DDoS protection<br/>Rate limiting: Bot detection<br/>API protection]
    end

    subgraph ServicePlane[Service Plane - Real-time Processing]
        API_GW[API Gateway<br/>Finagle-based<br/>100K+ endpoints<br/>OAuth 2.0/Bearer tokens]

        subgraph CoreServices[Core Services - 500+ microservices]
            TWEET_SVC[Tweet Service<br/>Scala + Finagle<br/>500M+ tweets/day<br/>Snowflake ID generation]
            TIMELINE_SVC[Timeline Service<br/>Java + Scala<br/>Home/User timelines<br/>Real-time fanout]
            SEARCH_SVC[Search Service<br/>Java + Lucene<br/>Real-time indexing<br/>Trending topics]
            USER_SVC[User Service<br/>Scala + Thrift<br/>400M+ profiles<br/>Follow/unfollow]
            TREND_SVC[Trending Service<br/>Storm + Heron<br/>Real-time analytics<br/>Geographic trends]
            MEDIA_SVC[Media Service<br/>Scala + Akka<br/>Photos/videos/GIFs<br/>Transcoding pipeline]
        end

        subgraph StreamProcessing[Stream Processing - Real-time]
            HERON[Heron<br/>Stream processing<br/>Twitter's Storm successor<br/>Low latency topology]
            STORM[Apache Storm<br/>Legacy processing<br/>Real-time computation<br/>Spout/bolt topology]
            KAFKA[Apache Kafka<br/>Event streaming<br/>100B+ events/day<br/>Real-time fanout]
        end
    end

    subgraph StatePlane[State Plane - Distributed Storage]
        subgraph PrimaryStorage[Primary Storage]
            MANHATTAN[Manhattan<br/>Distributed database<br/>Multi-tenant storage<br/>1000+ TB]
            MYSQL[MySQL Clusters<br/>Sharded databases<br/>User data<br/>500+ TB]
            CASSANDRA[Cassandra<br/>Time-series data<br/>Analytics storage<br/>300+ TB]
        end

        subgraph GraphStorage[Social Graph Storage]
            FLOCKDB[FlockDB<br/>Social graph database<br/>Following relationships<br/>Billions of edges]
            GIZMODUCK[Gizmoduck<br/>User service<br/>Profile management<br/>Identity service]
        end

        subgraph MediaStorage[Media Storage]
            BLOBSTORE[Blobstore<br/>Media storage<br/>Photos/videos<br/>2+ PB]
            TWIMG[twimg.com<br/>Image serving<br/>CDN integration<br/>Multiple formats]
        end

        subgraph CacheLayers[Cache Layers]
            MEMCACHED[Memcached<br/>Hot data cache<br/>Timeline cache<br/>500+ GB]
            REDIS[Redis Clusters<br/>Real-time cache<br/>Session storage<br/>200+ GB]
        end
    end

    subgraph ControlPlane[Control Plane - Operations & Analytics]
        subgraph Monitoring[Monitoring & Observability]
            OBSERVABILITY[Observability Platform<br/>Custom monitoring<br/>Real-time metrics<br/>Alert management]
            ZIPKIN[Zipkin<br/>Distributed tracing<br/>Request flow analysis<br/>Performance monitoring]
            ELK[ELK Stack<br/>Log aggregation<br/>Search & analysis<br/>Debug support]
        end

        subgraph Analytics[Analytics Platform]
            HADOOP[Hadoop Clusters<br/>Batch processing<br/>100+ PB data<br/>MapReduce jobs]
            VERTICA[Vertica<br/>Columnar analytics<br/>Real-time dashboards<br/>Business intelligence]
            DRUID[Apache Druid<br/>Real-time analytics<br/>Time-series queries<br/>Interactive dashboards]
        end

        subgraph MLPlatform[ML Platform]
            CORTEX[Cortex<br/>ML platform<br/>Model training<br/>Feature store]
            TENSORFLOW[TensorFlow<br/>Recommendation models<br/>Trend prediction<br/>Content classification]
        end
    end

    %% Edge Plane Connections
    CDN --> LB
    LB --> WAF
    WAF --> API_GW

    %% Service Plane Connections
    API_GW --> TWEET_SVC
    API_GW --> TIMELINE_SVC
    API_GW --> SEARCH_SVC
    API_GW --> USER_SVC
    API_GW --> TREND_SVC
    API_GW --> MEDIA_SVC

    %% Core Services to Storage
    TWEET_SVC --> MANHATTAN
    TWEET_SVC --> KAFKA
    TIMELINE_SVC --> MANHATTAN
    TIMELINE_SVC --> MEMCACHED
    SEARCH_SVC --> CASSANDRA
    USER_SVC --> FLOCKDB
    USER_SVC --> GIZMODUCK
    MEDIA_SVC --> BLOBSTORE
    MEDIA_SVC --> TWIMG

    %% Stream Processing
    KAFKA --> HERON
    KAFKA --> STORM
    HERON --> TIMELINE_SVC
    STORM --> TREND_SVC

    %% Analytics Pipeline
    MANHATTAN --> HADOOP
    KAFKA --> HADOOP
    HADOOP --> VERTICA
    HERON --> DRUID

    %% ML Platform
    HADOOP --> CORTEX
    CORTEX --> TENSORFLOW
    TENSORFLOW --> TREND_SVC

    %% Monitoring
    OBSERVABILITY -.-> TWEET_SVC
    OBSERVABILITY -.-> TIMELINE_SVC
    ZIPKIN -.-> API_GW
    ELK -.-> HERON

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff,stroke-width:2px
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff,stroke-width:2px
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff,stroke-width:2px

    class CDN,LB,WAF edgeStyle
    class API_GW,TWEET_SVC,TIMELINE_SVC,SEARCH_SVC,USER_SVC,TREND_SVC,MEDIA_SVC,HERON,STORM,KAFKA serviceStyle
    class MANHATTAN,MYSQL,CASSANDRA,FLOCKDB,GIZMODUCK,BLOBSTORE,TWIMG,MEMCACHED,REDIS stateStyle
    class OBSERVABILITY,ZIPKIN,ELK,HADOOP,VERTICA,DRUID,CORTEX,TENSORFLOW controlStyle
```

## Production Scale Metrics

| Component | Scale | Technology | Instance Type |
|-----------|-------|------------|---------------|
| **API Gateway** | 5M RPS peak | Finagle (Scala) | AWS c6i.8xlarge |
| **Tweet Service** | 500M tweets/day | Scala + Finagle | AWS c6i.4xlarge |
| **Timeline Service** | 300B timelines/year | Java + Scala | AWS r6i.8xlarge |
| **Manhattan DB** | 1000+ TB | Custom distributed DB | AWS i4i.8xlarge |
| **Search Service** | 500M searches/day | Java + Lucene | AWS c6i.8xlarge |
| **Kafka Clusters** | 100B events/day | Apache Kafka | AWS i4i.4xlarge |

## Regional Architecture

```mermaid
graph TB
    subgraph GlobalDistribution[Global Distribution Architecture]
        subgraph Americas[Americas Region]
            US_EAST[US-East-1<br/>Primary datacenter<br/>50% global traffic<br/>Full stack deployment]
            US_WEST[US-West-2<br/>Hot standby<br/>20% global traffic<br/>Failover ready]
        end

        subgraph Europe[Europe Region]
            EU_WEST[EU-West-1<br/>Regional deployment<br/>20% global traffic<br/>GDPR compliance]
        end

        subgraph AsiaPacific[Asia Pacific Region]
            AP_NORTHEAST[AP-Northeast-1<br/>Regional deployment<br/>10% global traffic<br/>Local regulations]
        end

        subgraph ReplicationLayer[Global Replication]
            GLOBAL_REPLICATION[Manhattan Replication<br/>Cross-region sync<br/>Eventual consistency<br/>Conflict resolution]
        end
    end

    US_EAST <--> US_WEST
    US_EAST --> EU_WEST
    US_EAST --> AP_NORTHEAST

    US_EAST --> GLOBAL_REPLICATION
    US_WEST --> GLOBAL_REPLICATION
    EU_WEST --> GLOBAL_REPLICATION
    AP_NORTHEAST --> GLOBAL_REPLICATION

    %% Traffic distribution
    US_EAST -.->|"Read/Write: 50%<br/>Latency: <50ms<br/>Availability: 99.9%"| US_WEST

    classDef primaryStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef regionStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef replicationStyle fill:#CC0000,stroke:#990000,color:#fff

    class US_EAST primaryStyle
    class US_WEST,EU_WEST,AP_NORTHEAST regionStyle
    class GLOBAL_REPLICATION replicationStyle
```

## Cost Structure (Annual)

| Category | Cost | Percentage | Details |
|----------|------|------------|---------|
| **Compute** | $600M | 40% | EC2 instances, auto-scaling |
| **Storage** | $300M | 20% | Manhattan, Blobstore, backups |
| **Network** | $300M | 20% | CDN, data transfer, bandwidth |
| **Stream Processing** | $150M | 10% | Kafka, Heron, Storm clusters |
| **Analytics/ML** | $75M | 5% | Hadoop, ML training, Cortex |
| **Monitoring/Tools** | $75M | 5% | Observability, third-party tools |
| **Total** | **$1.5B** | **100%** | **Cost per MAU: $0.42/month** |

## Snowflake ID Generation

```mermaid
graph TB
    subgraph SnowflakeID[Snowflake ID Generation System]
        subgraph IDStructure[ID Structure - 64 bits]
            TIMESTAMP[Timestamp<br/>41 bits<br/>Milliseconds since epoch<br/>69 years capacity]
            DATACENTER[Datacenter ID<br/>5 bits<br/>32 datacenters<br/>Geographic distribution]
            WORKER[Worker ID<br/>5 bits<br/>32 workers per DC<br/>Process identification]
            SEQUENCE[Sequence<br/>12 bits<br/>4096 IDs per ms<br/>Per worker counter]
        end

        subgraph GenerationFlow[Generation Flow]
            REQUEST[ID Request<br/>From tweet service<br/>High throughput<br/>Low latency]
            GENERATOR[Snowflake Generator<br/>Local generation<br/>No coordination<br/>Monotonic ordering]
            VALIDATION[ID Validation<br/>Uniqueness check<br/>Time ordering<br/>Format validation]
        end

        subgraph Benefits[Benefits]
            SORTABLE[Time Sortable<br/>Natural ordering<br/>No additional sorting<br/>Timeline efficiency]
            SCALABLE[Highly Scalable<br/>No central bottleneck<br/>1000+ generators<br/>4M+ IDs per second]
            DEBUGGABLE[Debuggable<br/>Timestamp extraction<br/>Source identification<br/>Issue diagnosis]
        end
    end

    TIMESTAMP --> REQUEST
    DATACENTER --> GENERATOR
    WORKER --> VALIDATION
    SEQUENCE --> GENERATOR

    REQUEST --> GENERATOR
    GENERATOR --> VALIDATION
    VALIDATION --> SORTABLE

    SORTABLE --> SCALABLE
    SCALABLE --> DEBUGGABLE

    %% Performance metrics
    GENERATOR -.->|"Latency: <1ms p99<br/>Throughput: 4M+ IDs/sec<br/>Uniqueness: 100%"| VALIDATION

    classDef structureStyle fill:#E8F5E8,stroke:#388E3C,color:#000
    classDef flowStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef benefitStyle fill:#E3F2FD,stroke:#1976D2,color:#000

    class TIMESTAMP,DATACENTER,WORKER,SEQUENCE structureStyle
    class REQUEST,GENERATOR,VALIDATION flowStyle
    class SORTABLE,SCALABLE,DEBUGGABLE benefitStyle
```

## Real-time Features

### Tweet Fanout Architecture

```mermaid
graph TB
    subgraph TweetFanout[Tweet Fanout System]
        subgraph FanoutStrategies[Fanout Strategies]
            PUSH_FANOUT[Push Fanout<br/>Pre-compute timelines<br/>For users with <5M followers<br/>Real-time delivery]
            PULL_FANOUT[Pull Fanout<br/>Compute on read<br/>For celebrities >5M followers<br/>Celebrity tweet handling]
            HYBRID_FANOUT[Hybrid Fanout<br/>Best of both<br/>Smart routing<br/>Performance optimization]
        end

        subgraph FanoutExecution[Fanout Execution]
            FANOUT_QUEUE[Fanout Queue<br/>Kafka-based<br/>Ordered processing<br/>Retry logic]
            FANOUT_WORKERS[Fanout Workers<br/>Parallel processing<br/>1000+ workers<br/>Rate limiting]
            TIMELINE_CACHE[Timeline Cache<br/>Redis clusters<br/>Hot timeline data<br/>Fast access]
        end
    end

    PUSH_FANOUT --> FANOUT_QUEUE
    PULL_FANOUT --> FANOUT_QUEUE
    HYBRID_FANOUT --> FANOUT_QUEUE

    FANOUT_QUEUE --> FANOUT_WORKERS
    FANOUT_WORKERS --> TIMELINE_CACHE

    %% Fanout performance
    FANOUT_WORKERS -.->|"Processing rate: 50K tweets/sec<br/>Latency: p99 <400ms<br/>Success rate: 99.9%"| TIMELINE_CACHE

    classDef strategyStyle fill:#E8F5E8,stroke:#388E3C,color:#000
    classDef executionStyle fill:#FFF3E0,stroke:#F57C00,color:#000

    class PUSH_FANOUT,PULL_FANOUT,HYBRID_FANOUT strategyStyle
    class FANOUT_QUEUE,FANOUT_WORKERS,TIMELINE_CACHE executionStyle
```

## SLA Guarantees

- **Tweet Publishing**: p99 < 300ms
- **Timeline Generation**: p99 < 400ms
- **Search Queries**: p95 < 100ms
- **Trending Topics**: Update frequency < 5 minutes
- **Overall Availability**: 99.9% (8.76 hours downtime/year)
- **Media Upload**: p99 < 2s (photos), p99 < 10s (videos)

## Key Innovations

1. **Snowflake ID Generation**: Globally unique, time-ordered IDs
2. **Finagle Framework**: Fault-tolerant RPC system
3. **Heron Stream Processing**: Low-latency successor to Storm
4. **Manhattan Database**: Multi-tenant distributed storage
5. **Real-time Fanout**: Hybrid push/pull timeline generation
6. **Pelikan Cache**: High-performance caching framework

## Performance Characteristics

| Feature | Latency Target | Throughput | Availability |
|---------|----------------|------------|--------------|
| **Tweet Publication** | p99 < 300ms | 6K tweets/sec | 99.95% |
| **Home Timeline** | p99 < 400ms | 300K loads/sec | 99.9% |
| **Search** | p95 < 100ms | 100K queries/sec | 99.95% |
| **User Profile** | p99 < 200ms | 500K loads/sec | 99.9% |
| **Trending Topics** | Updated < 5min | Real-time | 99.9% |
| **Media Serving** | p99 < 100ms | 1M requests/sec | 99.99% |

*Last updated: September 2024*
*Source: Twitter Engineering Blog, Public presentations, Performance reports*