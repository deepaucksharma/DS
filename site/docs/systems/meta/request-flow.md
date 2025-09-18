# Meta (Facebook) - Request Flow Architecture

## News Feed Generation: The Golden Path

The News Feed is Meta's most critical service, generating personalized content for 2.1B daily active users. Every page load triggers a complex cascade of machine learning, graph traversal, and content ranking that must complete in <200ms.

## Complete Request Flow

```mermaid
sequenceDiagram
    participant U as User (iOS/Android)
    participant CDN as Facebook CDN
    participant LB as Load Balancer
    participant WEB as Web Tier (HHVM)
    participant FEED as Feed Service
    participant TAO as TAO Graph Store
    participant ML as ML Ranking
    participant ADS as Ads Service
    participant CACHE as Memcached

    Note over U,CACHE: News Feed Request (Target: p99 < 200ms)

    U->>CDN: GET /feed (HTTP/2)
    Note right of CDN: Cache Hit: 85% static assets
    CDN->>LB: Forward dynamic request
    Note right of LB: GLB routing (p99: 5ms)

    LB->>WEB: Route to closest datacenter
    Note right of WEB: HHVM process (500 concurrent)
    WEB->>CACHE: Check feed cache
    Note right of CACHE: Hit ratio: 60% for feeds

    alt Cache Miss - Generate Feed
        WEB->>FEED: Generate feed for user_id
        Note right of FEED: EdgeRank algorithm v5.2

        FEED->>TAO: Get user friends (limit 5000)
        TAO-->>FEED: Friend IDs + metadata (p99: 5ms)

        FEED->>TAO: Get recent posts (last 24h)
        TAO-->>FEED: ~500 candidate posts (p99: 10ms)

        FEED->>ML: Rank posts with ML model
        Note right of ML: PyTorch inference (p99: 50ms)
        ML-->>FEED: Ranked post scores

        FEED->>ADS: Get sponsored content
        Note right of ADS: 1-2 ads per 20 posts
        ADS-->>FEED: Ad units (p99: 20ms)

        FEED->>WEB: Merged feed (20 posts)
        WEB->>CACHE: Store feed (TTL: 15min)
    end

    WEB-->>CDN: Rendered feed HTML + JSON
    CDN-->>U: Feed response (gzip compressed)

    Note over U: Total latency: p50=120ms, p99=200ms
```

## Photo Upload & Serving Path

```mermaid
graph TB
    subgraph Upload[Photo Upload Pipeline]
        APP[Mobile App]
        UP[Upload Service]
        PROC[Image Processing]
        HAY[Haystack Storage]
    end

    subgraph Serving[Photo Serving Pipeline]
        REQ[Photo Request]
        EDGE[Edge Cache]
        ORIGIN[Haystack Cluster]
        CDN[Global CDN]
    end

    %% Upload flow
    APP -->|"12MP photo (4MB)"| UP
    UP -->|"Resize: 8 variants"| PROC
    PROC -->|"Store variants"| HAY

    %% Serving flow
    REQ -->|"Photo URL"| EDGE
    EDGE -->|"Cache miss (5%)"| ORIGIN
    ORIGIN -->|"Retrieve photo"| HAY
    HAY -->|"Serve photo"| CDN
    CDN -->|"Deliver to user"| REQ

    %% Annotations
    UP -.->|"Upload rate: 350M/day"| HAY
    EDGE -.->|"Hit ratio: 95%"| CDN
    HAY -.->|"Storage: 500B+ photos"| HAY

    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class UP,PROC serviceStyle
    class APP,EDGE,CDN edgeStyle
    class HAY,ORIGIN stateStyle
```

## WhatsApp Real-time Messaging Flow

```mermaid
graph TB
    subgraph Sender[Sender Path]
        S_APP[WhatsApp Client]
        S_EDGE[Edge Server]
        S_MSG[Message Service]
    end

    subgraph Core[Core Infrastructure]
        ROUTER[Message Router]
        QUEUE[Message Queue]
        CRYPTO[E2E Encryption]
    end

    subgraph Receiver[Receiver Path]
        R_MSG[Message Service]
        R_EDGE[Edge Server]
        R_APP[WhatsApp Client]
        PUSH[Push Notification]
    end

    %% Message flow
    S_APP -->|"Encrypted message"| S_EDGE
    S_EDGE -->|"p99: 10ms"| S_MSG
    S_MSG -->|"Route message"| ROUTER
    ROUTER -->|"Queue for delivery"| QUEUE
    QUEUE -->|"End-to-end encrypted"| CRYPTO

    CRYPTO -->|"Decrypt & route"| R_MSG
    R_MSG -->|"p99: 15ms"| R_EDGE
    R_EDGE -->|"WebSocket/TCP"| R_APP

    %% Offline path
    R_MSG -->|"User offline"| PUSH
    PUSH -->|"APNs/FCM"| R_APP

    %% Annotations
    S_APP -.->|"2B+ users"| R_APP
    QUEUE -.->|"100B+ msgs/day"| QUEUE
    CRYPTO -.->|"Signal Protocol"| CRYPTO

    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class S_MSG,R_MSG,ROUTER serviceStyle
    class S_EDGE,R_EDGE,PUSH edgeStyle
    class QUEUE,CRYPTO stateStyle
```

## Graph API Request Processing

```mermaid
graph LR
    subgraph Client[Client Applications]
        MOBILE[Mobile Apps]
        WEB[Web Apps]
        THIRD[3rd Party Apps]
    end

    subgraph Gateway[API Gateway Layer]
        GRAPHQL[GraphQL Endpoint]
        REST[REST API v18.0]
        RATE[Rate Limiting]
        AUTH[OAuth 2.0]
    end

    subgraph Processing[Request Processing]
        RESOLVER[Field Resolvers]
        BATCH[Request Batching]
        CACHE_L[L1 Cache]
        TAO_Q[TAO Queries]
    end

    subgraph Data[Data Layer]
        TAO_G[TAO Graph Store]
        MYSQL_B[MySQL Backing]
        MEMCACHE_G[Memcached]
    end

    %% Request flow
    MOBILE --> GRAPHQL
    WEB --> REST
    THIRD --> REST

    GRAPHQL --> AUTH
    REST --> AUTH
    AUTH --> RATE
    RATE --> RESOLVER

    RESOLVER --> BATCH
    BATCH --> CACHE_L
    CACHE_L --> TAO_Q
    TAO_Q --> TAO_G

    TAO_G --> MYSQL_B
    TAO_G --> MEMCACHE_G

    %% Performance annotations
    AUTH -.->|"p99: 5ms"| RATE
    RATE -.->|"10M RPS limit"| RESOLVER
    CACHE_L -.->|"Hit ratio: 80%"| TAO_Q
    TAO_G -.->|"p99: 1ms"| MYSQL_B

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class MOBILE,WEB,THIRD edgeStyle
    class GRAPHQL,REST,RATE,AUTH,RESOLVER,BATCH serviceStyle
    class CACHE_L,TAO_Q,TAO_G,MYSQL_B,MEMCACHE_G stateStyle
```

## Live Video Streaming Flow

```mermaid
graph TB
    subgraph Broadcaster[Live Broadcaster]
        CREATOR[Content Creator]
        ENCODER[Video Encoder]
        INGEST[Ingest Service]
    end

    subgraph Processing[Video Processing]
        TRANSCODE[Transcoding Farm]
        SEGMENTS[Segment Storage]
        MANIFEST[Manifest Service]
    end

    subgraph Delivery[Content Delivery]
        ORIGIN[Origin Servers]
        CDN_L[Live CDN]
        VIEWERS[Live Viewers]
    end

    subgraph Realtime[Real-time Features]
        CHAT[Live Chat]
        REACTIONS[Reactions]
        ANALYTICS[Live Analytics]
    end

    %% Video pipeline
    CREATOR -->|"RTMP stream"| ENCODER
    ENCODER -->|"H.264/HEVC"| INGEST
    INGEST -->|"Chunk to workers"| TRANSCODE
    TRANSCODE -->|"Multiple bitrates"| SEGMENTS
    SEGMENTS -->|"HLS/DASH"| MANIFEST

    %% Delivery pipeline
    MANIFEST --> ORIGIN
    ORIGIN --> CDN_L
    CDN_L --> VIEWERS

    %% Real-time features
    VIEWERS --> CHAT
    VIEWERS --> REACTIONS
    INGEST --> ANALYTICS

    %% Performance metrics
    INGEST -.->|"Latency: <3s"| TRANSCODE
    CDN_L -.->|"Global: 200+ PoPs"| VIEWERS
    CHAT -.->|"Messages: 1M/min"| REACTIONS

    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class ENCODER,INGEST,TRANSCODE,MANIFEST serviceStyle
    class CREATOR,CDN_L,VIEWERS edgeStyle
    class SEGMENTS,ORIGIN,CHAT,REACTIONS,ANALYTICS stateStyle
```

## Request Performance Targets

### Latency SLOs by Service
| Service | p50 Target | p99 Target | p99.9 Target |
|---------|------------|------------|--------------|
| News Feed | 80ms | 200ms | 500ms |
| Photo Load | 50ms | 150ms | 300ms |
| Graph API | 20ms | 100ms | 250ms |
| WhatsApp Message | 30ms | 100ms | 200ms |
| Video Stream Start | 1s | 3s | 5s |

### Throughput Metrics
- **Graph API**: 10M requests/second peak
- **Photo Requests**: 1M photos/second served
- **Messages**: 100B+ messages/day (WhatsApp)
- **Feed Refreshes**: 500M+ per minute peak
- **Live Video**: 1M+ concurrent streams

## Critical Optimizations

### EdgeRank Algorithm Efficiency
```mermaid
graph LR
    subgraph Inputs[Algorithm Inputs]
        AFFINITY[User Affinity Score]
        WEIGHT[Content Weight]
        DECAY[Time Decay Factor]
    end

    subgraph Computation[Score Computation]
        MULTIPLY[Score = Affinity × Weight × Decay]
        NORMALIZE[Normalization]
        RANK[Final Ranking]
    end

    subgraph Caching[Result Caching]
        USER_CACHE[Per-user Cache]
        GLOBAL_CACHE[Global Content Cache]
        PREFETCH[Predictive Prefetch]
    end

    AFFINITY --> MULTIPLY
    WEIGHT --> MULTIPLY
    DECAY --> MULTIPLY
    MULTIPLY --> NORMALIZE
    NORMALIZE --> RANK
    RANK --> USER_CACHE
    RANK --> GLOBAL_CACHE
    GLOBAL_CACHE --> PREFETCH

    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class MULTIPLY,NORMALIZE,RANK serviceStyle
    class AFFINITY,WEIGHT,DECAY,USER_CACHE,GLOBAL_CACHE,PREFETCH stateStyle
```

## Production Lessons

### Key Insights
1. **Feed Generation**: Machine learning inference is the bottleneck (50ms of 200ms total)
2. **Photo Serving**: 95% cache hit rate is critical for cost efficiency
3. **Real-time Messaging**: Connection management scales linearly with active users
4. **API Rate Limiting**: Prevents cascade failures during traffic spikes
5. **Global Distribution**: Edge computing reduces latency by 60%+

### The WhatsApp Scale Challenge
- **Problem**: 100B+ messages/day with <100ms end-to-end latency
- **Solution**: Erlang/OTP for massive concurrency, custom protocol optimization
- **Result**: Single server handles 2M+ concurrent connections

*"Every millisecond of latency costs user engagement - News Feed generation must be faster than human perception."*

**Sources**: Meta Engineering Blog, WhatsApp Engineering Blog, F8 Conference Talks 2024