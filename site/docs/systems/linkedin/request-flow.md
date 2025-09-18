# LinkedIn Request Flow

## Overview
LinkedIn's request flow handles massive scale with feed generation, job recommendations, search, and messaging. The system serves 2M+ requests per second with <200ms feed refresh times.

## Feed Generation Request Flow

```mermaid
sequenceDiagram
    participant U as User<br/>(Mobile/Web)
    participant CDN as Akamai CDN
    participant LB as Load Balancer
    participant GW as API Gateway
    participant FS as Feed Service
    participant CS as Connection Service
    participant JS as Job Service
    participant K as Kafka
    participant V as Venice<br/>(Read Views)
    participant E as Espresso<br/>(Primary DB)
    participant R as Redis Cache

    Note over U,R: Feed Generation Flow (Following + Interest Feed)

    U->>CDN: GET /feed/updates
    CDN->>LB: Cache miss (dynamic content)
    LB->>GW: Route request
    Note over GW: Auth: JWT validation<br/>Rate limit: 100 req/min

    GW->>FS: GET feed(userId, limit=20)
    Note over FS: Feed scoring algorithm<br/>Following + Interest signals

    par Following Feed Generation
        FS->>CS: getConnections(userId)
        CS->>R: Check connection cache
        alt Cache hit (95% hit rate)
            R-->>CS: Return connections
        else Cache miss
            CS->>E: Query connections table
            E-->>CS: Connection list
            CS->>R: Cache connections (TTL: 1h)
        end
        CS-->>FS: User connections (avg: 500)

        FS->>V: getRecentPosts(connectionIds)
        V-->>FS: Recent posts (1000 candidates)
    and Interest Feed Generation
        FS->>JS: getJobRecommendations(userId)
        JS->>R: Check job cache
        alt Cache hit (85% hit rate)
            R-->>JS: Job recommendations
        else Cache miss
            JS->>E: ML scoring query
            E-->>JS: Scored jobs
            JS->>R: Cache jobs (TTL: 30min)
        end
        JS-->>FS: Job recommendations (50 jobs)
    end

    Note over FS: Feed ranking algorithm<br/>ML scoring: engagement prediction<br/>Diversity constraints

    FS->>K: Publish view event
    FS-->>GW: Ranked feed (20 items)
    GW-->>LB: JSON response (avg: 45KB)
    LB-->>CDN: Cache static assets only
    CDN-->>U: Feed data + cached assets

    Note over U,R: Total latency: p99 < 200ms
```

## Job Recommendation Pipeline

```mermaid
graph TB
    subgraph UserRequest[User Request Flow]
        USER[User Profile View]
        JOB_API[Jobs API Gateway<br/>Kong: rate limit 500/hour]
    end

    subgraph RecommendationEngine[ML Recommendation Engine]
        PROFILE[Profile Analysis<br/>Skills, experience, location]
        SCORING[ML Scoring Service<br/>TensorFlow Serving<br/>Real-time inference]
        RANKING[Ranking Algorithm<br/>CTR + Apply Rate prediction]
    end

    subgraph DataSources[Data Sources]
        JOB_DB[Job Database<br/>Espresso: 20M+ active jobs]
        USER_DB[User Database<br/>Espresso: 1B+ profiles]
        INTERACTION[Interaction Events<br/>Venice: click/apply history]
        COMPANY[Company Data<br/>500K+ companies]
    end

    subgraph CacheLayer[Cache Layer]
        REDIS_JOB[Redis Jobs Cache<br/>Hot jobs: 100K<br/>TTL: 30 minutes]
        REDIS_USER[Redis User Cache<br/>Profile vectors<br/>TTL: 2 hours]
    end

    USER --> JOB_API
    JOB_API --> PROFILE

    PROFILE --> USER_DB
    PROFILE --> REDIS_USER

    PROFILE --> SCORING
    SCORING --> JOB_DB
    SCORING --> INTERACTION
    SCORING --> COMPANY

    SCORING --> RANKING
    RANKING --> REDIS_JOB

    RANKING --> JOB_API

    %% Latency annotations
    USER -.->|"p95: 150ms"| JOB_API
    PROFILE -.->|"p99: 50ms"| SCORING
    SCORING -.->|"p99: 80ms"| RANKING

    %% Apply styles
    classDef userStyle fill:#E1F5FE,stroke:#0288D1,color:#000
    classDef mlStyle fill:#E8F5E8,stroke:#4CAF50,color:#000
    classDef dataStyle fill:#FFF3E0,stroke:#FF9800,color:#000
    classDef cacheStyle fill:#FCE4EC,stroke:#E91E63,color:#000

    class USER,JOB_API userStyle
    class PROFILE,SCORING,RANKING mlStyle
    class JOB_DB,USER_DB,INTERACTION,COMPANY dataStyle
    class REDIS_JOB,REDIS_USER cacheStyle
```

## Search Request Flow (Galene Search Engine)

```mermaid
sequenceDiagram
    participant U as User
    participant GW as API Gateway
    participant SS as Search Service<br/>(Galene)
    participant IDX as Search Index<br/>(Lucene-based)
    participant AGG as Aggregation Service
    participant REDIS as Redis Cache
    participant PINOT as Pinot Analytics

    U->>GW: Search query: "software engineer"
    Note over GW: Query validation<br/>Sanitization<br/>Rate limiting: 50/min

    GW->>SS: search(query, filters, pagination)

    par Query Processing
        SS->>IDX: Execute search
        Note over IDX: Lucene scoring<br/>Relevance + recency<br/>Personalization signals
        IDX-->>SS: Search results (1000 candidates)
    and Analytics Tracking
        SS->>PINOT: Log search event
        Note over PINOT: Real-time analytics<br/>Search quality metrics
    end

    SS->>AGG: Aggregate results by type
    Note over AGG: People, Jobs, Companies, Posts<br/>Apply diversity constraints

    AGG->>REDIS: Check result cache
    alt Fresh results available (cache hit: 70%)
        REDIS-->>AGG: Cached enriched data
    else Cache miss or stale
        par Enrich Results
            AGG->>GW: Fetch profile summaries
        and
            AGG->>GW: Fetch company data
        and
            AGG->>GW: Fetch job details
        end
        AGG->>REDIS: Cache results (TTL: 15min)
    end

    AGG-->>SS: Enriched results
    SS-->>GW: Formatted response
    GW-->>U: Search results JSON

    Note over U,PINOT: Search latency: p95 < 100ms<br/>50M+ searches per day
```

## InMail Delivery System

```mermaid
graph TB
    subgraph MessageFlow[InMail Message Flow]
        SENDER[Sender<br/>Premium user]
        MSG_API[Messaging API<br/>Rate limit: 50/day premium]
        MSG_SVC[Message Service<br/>Akka actors<br/>Async processing]
    end

    subgraph DeliveryPipeline[Delivery Pipeline]
        VALIDATE[Message Validation<br/>Spam detection<br/>Content filtering]
        QUEUE[Kafka Message Queue<br/>Topic: inmail-delivery<br/>Partitioned by recipientId]
        DELIVERY[Delivery Service<br/>Guaranteed delivery<br/>Retry logic: 3 attempts]
    end

    subgraph NotificationSystem[Notification System]
        PUSH[Push Service<br/>Mobile notifications<br/>APNs/FCM]
        EMAIL[Email Service<br/>SendGrid integration<br/>Fallback delivery]
        WS[WebSocket Service<br/>Real-time web notifications]
    end

    subgraph Storage[Message Storage]
        COUCHBASE[Couchbase<br/>Message storage<br/>TTL: 2 years]
        SEARCH_IDX[Search Index<br/>Message search<br/>Elasticsearch]
    end

    SENDER --> MSG_API
    MSG_API --> MSG_SVC
    MSG_SVC --> VALIDATE

    VALIDATE --> QUEUE
    QUEUE --> DELIVERY

    DELIVERY --> COUCHBASE
    DELIVERY --> SEARCH_IDX

    par Notification Delivery
        DELIVERY --> PUSH
        DELIVERY --> EMAIL
        DELIVERY --> WS
    end

    %% Success metrics
    DELIVERY -.->|"Delivery rate: 99.5%"| COUCHBASE
    PUSH -.->|"Open rate: 35%"| DELIVERY
    EMAIL -.->|"Fallback rate: 5%"| DELIVERY

    %% Apply styles
    classDef senderStyle fill:#E3F2FD,stroke:#1976D2,color:#000
    classDef pipelineStyle fill:#E8F5E8,stroke:#388E3C,color:#000
    classDef notifyStyle fill:#FFF8E1,stroke:#F57C00,color:#000
    classDef storageStyle fill:#FCE4EC,stroke:#C2185B,color:#000

    class SENDER,MSG_API,MSG_SVC senderStyle
    class VALIDATE,QUEUE,DELIVERY pipelineStyle
    class PUSH,EMAIL,WS notifyStyle
    class COUCHBASE,SEARCH_IDX storageStyle
```

## Performance Characteristics

| Request Type | p50 Latency | p99 Latency | Throughput | Cache Hit Rate |
|--------------|-------------|-------------|------------|----------------|
| **Feed Generation** | 85ms | 200ms | 500K RPS | 95% (connections) |
| **Job Recommendations** | 120ms | 250ms | 200K RPS | 85% (jobs) |
| **Search Queries** | 45ms | 100ms | 150K RPS | 70% (results) |
| **Profile Views** | 25ms | 75ms | 800K RPS | 98% (profiles) |
| **InMail Delivery** | 200ms | 500ms | 50K RPS | N/A (async) |
| **Connection Requests** | 50ms | 150ms | 100K RPS | 90% (mutual) |

## Error Handling & Fallbacks

```mermaid
graph TB
    subgraph ErrorHandling[Error Handling Strategy]
        CIRCUIT[Circuit Breaker<br/>Failure threshold: 50%<br/>Recovery: 30s]
        RETRY[Retry Logic<br/>Exponential backoff<br/>Max: 3 attempts]
        FALLBACK[Fallback Responses<br/>Cached data<br/>Simplified view]
    end

    subgraph MonitoringAlerts[Monitoring & Alerts]
        LATENCY[Latency Alerts<br/>p99 > 500ms<br/>PagerDuty: P1]
        ERROR[Error Rate Alerts<br/>>1% error rate<br/>Slack notification]
        CAPACITY[Capacity Alerts<br/>>80% CPU/Memory<br/>Auto-scaling trigger]
    end

    CIRCUIT --> RETRY
    RETRY --> FALLBACK

    CIRCUIT --> LATENCY
    RETRY --> ERROR
    FALLBACK --> CAPACITY

    classDef errorStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef monitorStyle fill:#E8EAF6,stroke:#3F51B5,color:#000

    class CIRCUIT,RETRY,FALLBACK errorStyle
    class LATENCY,ERROR,CAPACITY monitorStyle
```

## Key Optimizations

1. **Connection Graph Caching**: 95% hit rate, 1-hour TTL
2. **Feed Pre-computation**: Background jobs for active users
3. **ML Model Caching**: Feature vectors cached for 2 hours
4. **Search Index Warming**: Popular queries pre-loaded
5. **Content Compression**: GZIP + Brotli for 60% size reduction
6. **Database Sharding**: User-based sharding for horizontal scale

*Last updated: September 2024*
*Source: LinkedIn Engineering Blog, Production metrics*