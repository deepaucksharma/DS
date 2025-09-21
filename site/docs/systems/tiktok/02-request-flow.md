# TikTok Request Flow

## Request Flow - "The Golden Path"

This diagram shows the complete journey from video upload to For You Page delivery, including the critical recommendation pipeline that drives TikTok's engagement.

```mermaid
graph TB
    subgraph UserActions[User Actions - Entry Points]
        UPLOAD[Video Upload<br/>150M+ daily<br/>Mobile App]
        BROWSE[Browse For You<br/>1B+ views daily<br/>Mobile/Web]
        INTERACT[User Interactions<br/>Likes, Comments, Shares<br/>100M+ per minute]
    end

    subgraph EdgeLayer[Edge Plane - Global Entry]
        CDN[BytePlus CDN<br/>400+ PoPs<br/>p95: 15ms RTT]
        LB[Load Balancer<br/>Geographic routing<br/>p99: 5ms]
        WAF[WAF Protection<br/>10M+ req/sec<br/>p99: 2ms]
    end

    subgraph APIGateway[Service Plane - API Layer]
        KONG[Kong Gateway<br/>Rate limiting<br/>p99: 8ms<br/>200K req/sec]
        AUTH[Auth Service<br/>JWT validation<br/>p99: 12ms<br/>Redis-backed]
    end

    subgraph UploadFlow[Video Upload Flow]
        UPLOADAPI[Upload API<br/>Go service<br/>p99: 100ms<br/>Presigned URLs]
        PROCESSOR[Video Processor<br/>FFmpeg pipeline<br/>p95: 30s<br/>Multiple formats]
        MODERATOR[Content Moderation<br/>AI + Human review<br/>p95: 5min<br/>99.5% automated]
        INDEXER[Video Indexer<br/>Metadata extraction<br/>p99: 2s<br/>Features for ML]
    end

    subgraph RecommendationFlow[For You Page Flow]
        RECAPI[Recommendation API<br/>C++ service<br/>p99: 80ms<br/>100K req/sec]
        USERPROFILE[User Profile Service<br/>Java + Redis<br/>p99: 15ms<br/>Cached profiles]
        FEATURESTORE[Feature Store<br/>Redis Cluster<br/>p99: 5ms<br/>Real-time features]
        MLMODEL[ML Model Serving<br/>TensorFlow Serving<br/>p99: 40ms<br/>Batch inference]
        RANKER[Video Ranker<br/>Multi-stage ranking<br/>p99: 25ms<br/>Personalized scoring]
    end

    subgraph InteractionFlow[Interaction Processing]
        INTERACTION_API[Interaction API<br/>Node.js<br/>p99: 50ms<br/>Async processing]
        EVENT_STREAM[Event Streaming<br/>Apache Kafka<br/>p99: 10ms<br/>50M events/sec]
        REALTIME_ML[Real-time ML<br/>Apache Flink<br/>p99: 100ms<br/>Feature updates]
    end

    subgraph DataStorage[State Plane - Storage]
        VIDEODB[(Video Metadata<br/>MySQL Cluster<br/>Sharded by video_id<br/>100M+ records)]
        USERDB[(User Profiles<br/>MySQL Cluster<br/>Sharded by user_id<br/>1B+ users)]
        CACHE[(Redis Cache<br/>Multi-layer<br/>100TB memory<br/>99% hit rate)]
        S3[(Video Storage<br/>AWS S3 + HDFS<br/>50PB+ storage<br/>Multi-region)]
        ANALYTICS[(Analytics Store<br/>Cassandra<br/>Time-series data<br/>Interaction history)]
    end

    %% Upload Flow Path
    UPLOAD --> CDN
    CDN --> LB
    LB --> WAF
    WAF --> KONG
    KONG --> AUTH
    AUTH --> UPLOADAPI
    UPLOADAPI --> S3
    UPLOADAPI --> PROCESSOR
    PROCESSOR --> MODERATOR
    MODERATOR --> INDEXER
    INDEXER --> VIDEODB

    %% Browse Flow Path
    BROWSE --> CDN
    CDN --> KONG
    KONG --> AUTH
    AUTH --> RECAPI
    RECAPI --> USERPROFILE
    USERPROFILE --> USERDB
    USERPROFILE --> CACHE
    RECAPI --> FEATURESTORE
    FEATURESTORE --> CACHE
    RECAPI --> MLMODEL
    MLMODEL --> RANKER
    RANKER --> VIDEODB

    %% Interaction Flow Path
    INTERACT --> CDN
    CDN --> KONG
    KONG --> INTERACTION_API
    INTERACTION_API --> EVENT_STREAM
    EVENT_STREAM --> REALTIME_ML
    EVENT_STREAM --> ANALYTICS
    REALTIME_ML --> FEATURESTORE

    %% Cross-references
    PROCESSOR --> EVENT_STREAM
    MODERATOR --> EVENT_STREAM
    RANKER --> ANALYTICS

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff,stroke-width:2px
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff,stroke-width:2px
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff,stroke-width:2px

    class CDN,LB,WAF edgeStyle
    class KONG,AUTH,UPLOADAPI,PROCESSOR,MODERATOR,INDEXER,RECAPI,USERPROFILE,FEATURESTORE,MLMODEL,RANKER,INTERACTION_API,EVENT_STREAM,REALTIME_ML serviceStyle
    class VIDEODB,USERDB,CACHE,S3,ANALYTICS stateStyle
```

## Request Flow Analysis

### 1. Video Upload Flow (150M+ uploads/day)

**Timeline: Upload to Live (p95: 5 minutes)**

1. **Upload Initiation (0-100ms)**
   - Mobile app requests presigned S3 URL
   - Auth validation through Kong Gateway
   - Geographic routing to nearest upload endpoint

2. **File Transfer (1-30s)**
   - Direct upload to S3 via presigned URL
   - Progress tracking via WebSocket connection
   - Chunked upload for large files (>100MB)

3. **Processing Pipeline (10s-2min)**
   - Video transcoding to multiple formats
   - Thumbnail generation (5 thumbnails per video)
   - Audio extraction and normalization
   - Metadata extraction (duration, resolution, etc.)

4. **Content Moderation (30s-5min)**
   - Automated AI screening (99.5% pass rate)
   - Human review for flagged content
   - Community guidelines compliance check
   - Copyright detection via audio fingerprinting

5. **Indexing & Publishing (5-30s)**
   - Feature extraction for recommendation engine
   - Database updates across sharded MySQL
   - Cache warming for creator's followers
   - Event publication to Kafka for analytics

### 2. For You Page Flow (1B+ views/day)

**Timeline: Request to Video Display (p99: 200ms)**

1. **Request Authentication (0-20ms)**
   - JWT token validation via Redis cache
   - User context retrieval from cached profile
   - Rate limiting check (1000 req/min per user)

2. **User Profile Enrichment (5-30ms)**
   - Recent interaction history (last 7 days)
   - Device capabilities and preferences
   - Geographic and temporal context
   - Creator following status

3. **Candidate Generation (10-50ms)**
   - Collaborative filtering: users with similar preferences
   - Content-based filtering: similar video features
   - Trending video injection: 10-20% of feed
   - Creator diversity: max 2 videos per creator in 10

4. **Feature Computation (5-15ms)**
   - Real-time features from Redis (user activity)
   - Historical features from Cassandra (long-term patterns)
   - Video features (engagement rates, recency)
   - Cross-features (user-video interaction probability)

5. **ML Model Scoring (15-60ms)**
   - Multi-stage ranking pipeline
   - Stage 1: Lightweight model (10K candidates → 500)
   - Stage 2: Deep learning model (500 → 50)
   - Stage 3: Fine-tuned personalization (50 → 10)

6. **Final Ranking & Assembly (10-30ms)**
   - Business logic application (ad insertion)
   - Diversity and fairness constraints
   - Video metadata assembly from cache
   - CDN URL generation for optimal delivery

### 3. User Interaction Flow (100M+ interactions/minute)

**Timeline: Action to System Update (p99: 100ms)**

1. **Interaction Capture (0-10ms)**
   - Like, comment, share, or view completion
   - Immediate acknowledgment to user
   - Async event queuing to Kafka

2. **Real-time Processing (5-50ms)**
   - Event enrichment with context
   - Real-time feature store updates
   - Creator notification triggers
   - Engagement metrics updates

3. **Analytics Pipeline (10-100ms)**
   - Stream processing via Apache Flink
   - Aggregation for trending calculations
   - Model training data preparation
   - Business intelligence updates

## Critical Performance Optimizations

### 1. Recommendation Caching Strategy
- **L1 Cache**: User's recent recommendations (Redis, 1min TTL)
- **L2 Cache**: Pre-computed candidate pools (Redis, 15min TTL)
- **L3 Cache**: Popular video metadata (CDN, 1hr TTL)
- **Cache Hit Rate**: 95%+ for active users

### 2. Video Delivery Optimization
- **Adaptive Bitrate**: 240p to 4K based on network
- **Predictive Prefetching**: Next 3 videos based on scroll pattern
- **Edge Transcoding**: Dynamic format conversion at CDN
- **Smart Preloading**: Audio-first, then video for smooth start

### 3. Database Sharding Strategy
- **User Data**: Sharded by user_id hash (consistent hashing)
- **Video Data**: Sharded by video_id hash
- **Interaction Data**: Time-based partitioning + user_id
- **Cross-shard Queries**: Denormalized aggregation tables

## Latency Budget Breakdown

### For You Page Request (p99: 200ms total)
- CDN/Load Balancer: 20ms
- API Gateway + Auth: 20ms
- User Profile Service: 30ms
- Recommendation Engine: 80ms
- Video Metadata Assembly: 30ms
- Response Assembly: 20ms

### Video Upload (p95: 5min total)
- Upload to S3: 30s
- Transcoding Pipeline: 2min
- Content Moderation: 2min
- Indexing & Publishing: 30s

## Failure Scenarios & Recovery

### 1. Recommendation Engine Failure
- **Fallback**: Trending videos + creator-based recommendations
- **Recovery Time**: 30s (automatic failover)
- **Impact**: Reduced personalization, 15% engagement drop

### 2. CDN Failure
- **Fallback**: Secondary CDN (AWS CloudFront)
- **Recovery Time**: 10s (DNS failover)
- **Impact**: Increased latency, 2-5% user impact

### 3. Database Shard Failure
- **Fallback**: Read replicas, write buffering
- **Recovery Time**: 2-5min (automated failover)
- **Impact**: Degraded experience for affected users

This request flow handles TikTok's massive scale while maintaining the responsive, personalized experience that drives user engagement and creator success.