# Spotify - Request Flow Architecture

## The Golden Path: From User Tap to Audio Stream in <200ms

This diagram shows how Spotify delivers music with sub-200ms latency to 600M+ users while generating real-time recommendations and tracking royalties.

```mermaid
sequenceDiagram
    participant U as User Device<br/>iOS/Android/Web<br/>600M+ active users
    participant CF as Cloudflare<br/>DDoS Protection<br/>Global WAF
    participant CDN as Fastly CDN<br/>200+ PoPs<br/>95% cache hit
    participant ALB as AWS ALB<br/>Traffic Director<br/>Auto-scaling
    participant GW as API Gateway<br/>Kong Enterprise<br/>Rate limiting: 10K/min
    participant US as User Service<br/>Session Management<br/>100K req/s peak
    participant SS as Stream Service<br/>Content Delivery<br/>p99: 100ms
    participant RS as Recommendation<br/>ML Pipeline<br/>3B predictions/day
    participant MS as Metadata Service<br/>Song Information<br/>100M+ tracks
    participant LS as Licensing Service<br/>Royalty Tracking<br/>Real-time payments
    participant Cache as Redis Cache<br/>Hot Content<br/>100M sessions
    participant GCS as Google Storage<br/>Audio Files<br/>Multi-bitrate
    participant Analytics as Event Pipeline<br/>Kafka + BigQuery<br/>50M events/sec

    Note over U,Analytics: Music Stream Request Flow - p99: 200ms end-to-end

    %% Authentication & Routing
    U->>+CF: Play track request<br/>User ID + Track ID
    CF->>+CDN: Route to nearest PoP<br/>Geographic optimization
    CDN-->>CDN: Check audio cache<br/>95% hit rate for popular tracks

    alt Audio in CDN cache
        CDN->>U: Return cached audio<br/>Latency: 20-50ms
        Note over U,CDN: Cache hit - immediate playback
    else Audio not cached
        CDN->>+ALB: Forward to application<br/>Route to least loaded region
        ALB->>+GW: Load balance request<br/>Health check validation

        %% Session & Authentication
        GW->>+US: Validate session<br/>JWT token verification
        US->>+Cache: Check session cache<br/>100M active sessions
        Cache-->>US: Return user context<br/>Premium status, preferences
        US-->>GW: Session validated<br/>User permissions confirmed

        %% Stream Authorization
        GW->>+SS: Authorize stream request<br/>User ID + Track ID + Quality
        SS->>+LS: Check licensing<br/>Geographic restrictions
        LS-->>SS: License confirmed<br/>Royalty tracking initiated

        %% Metadata & Recommendations
        SS->>+MS: Get track metadata<br/>Bitrates, duration, artwork
        MS->>Cache: Cache metadata<br/>TTL: 24 hours
        MS-->>SS: Return track info<br/>All available formats

        %% Generate Recommendations
        SS->>+RS: Request related tracks<br/>User listening history
        RS-->>SS: Return recommendations<br/>Next 10 suggested tracks

        %% Content Delivery
        SS->>+GCS: Request audio file<br/>User quality preference
        GCS-->>SS: Return audio stream<br/>320kbps for Premium, 128kbps Free
        SS-->>CDN: Stream audio + cache<br/>TTL: 7 days popular, 24h others
        CDN-->>U: Deliver audio stream<br/>Adaptive bitrate
    end

    %% Analytics & Tracking
    par Stream Analytics
        U->>Analytics: Stream start event<br/>Timestamp, track, user
    and Royalty Tracking
        SS->>LS: Log stream completion<br/>30 second minimum
    and Recommendation Learning
        U->>RS: Implicit feedback<br/>Skip, replay, like events
    end

    Note over U,Analytics: Post-Stream Processing

    %% Background Updates
    par Background Processing
        Analytics->>Analytics: Update user profile<br/>Listening patterns
    and
        LS->>LS: Calculate royalties<br/>Artist payment queue
    and
        RS->>RS: Retrain models<br/>Nightly batch updates
    end

    Note over U,Analytics: Latency Breakdown (p99)
    Note over CF,CDN: CDN Lookup: 10ms
    Note over ALB,GW: Load Balancing: 15ms
    Note over US,Cache: Authentication: 25ms
    Note over SS,MS: Authorization: 30ms
    Note over GCS: Storage Retrieval: 45ms
    Note over CDN,U: Audio Delivery: 75ms
    Note over U,Analytics: Total p99: 200ms
```

## Stream Request Performance Metrics

### Response Time Breakdown (99th Percentile)
- **CDN Cache Hit**: 20-50ms (95% of requests)
- **Authentication**: 25ms (JWT validation + session lookup)
- **Authorization**: 30ms (licensing + geographic checks)
- **Metadata Retrieval**: 15ms (cached metadata lookup)
- **Audio File Access**: 45ms (Google Cloud Storage)
- **Total End-to-End**: <200ms (p99 SLA)

### Request Volume & Scale
- **Peak Concurrent Streams**: 100M+ users
- **Daily Stream Requests**: 500M+ globally
- **API Gateway Throughput**: 100K requests/second
- **Cache Hit Rates**: 95% (audio), 99% (metadata)
- **Geographic Distribution**: 180+ markets

## Recommendation Flow Deep-Dive

```mermaid
graph TB
    subgraph RecommendationPipeline[Real-time Recommendation Generation]
        UserEvent[User Play Event<br/>Track, timestamp, context]
        FeatureExtractor[Feature Extraction<br/>Audio analysis, user history<br/>100+ features per track]
        MLModel[ML Model Inference<br/>TensorFlow Serving<br/>3B predictions/day]
        Personalization[Personalization Layer<br/>User preferences, time of day<br/>Collaborative filtering]
        RankingService[Ranking Service<br/>Business rules, diversity<br/>Fresh content boost]
    end

    subgraph EdgeOptimization[Edge Optimization]
        RegionalCache[Regional Rec Cache<br/>Popular recommendations<br/>TTL: 1 hour]
        PersonalCache[Personal Rec Cache<br/>User-specific<br/>TTL: 15 minutes]
        FallbackRecs[Fallback Recommendations<br/>Genre-based defaults<br/>When ML unavailable]
    end

    UserEvent --> FeatureExtractor
    FeatureExtractor --> MLModel
    MLModel --> Personalization
    Personalization --> RankingService
    RankingService --> RegionalCache
    RankingService --> PersonalCache
    RegionalCache --> FallbackRecs

    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class UserEvent,FeatureExtractor,MLModel,Personalization,RankingService serviceStyle
    class RegionalCache,PersonalCache,FallbackRecs stateStyle
```

## Critical Performance Optimizations

### CDN Strategy
- **Popular Content Pre-positioning**: Top 1% tracks cached globally
- **Regional Popularity Caching**: Local hits cached regionally
- **User Pattern Prediction**: Cache based on user listening patterns
- **Adaptive Bitrate**: Stream quality adjusts to connection speed

### Session Management
- **Persistent Connections**: WebSocket for real-time updates
- **Session Stickiness**: Route users to same backend region
- **Graceful Degradation**: Offline mode with downloaded content
- **Background Prefetch**: Next 3 tracks pre-loaded

### Quality of Service
- **Premium User Priority**: Dedicated processing lanes
- **Peak Hour Scaling**: Auto-scale during evening hours (6-10 PM)
- **Regional Failover**: Automatic region switching on failures
- **Circuit Breakers**: Fail fast on downstream service issues

This request flow architecture ensures Spotify can deliver instant music streaming to hundreds of millions of users while maintaining real-time recommendations and accurate royalty tracking.