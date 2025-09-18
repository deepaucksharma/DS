# Twitter/X Request Flow

## Overview
Twitter/X's request flow handles massive real-time traffic with tweet fanout, timeline assembly, trending topics, and search. The system processes 500M+ tweets daily with <400ms timeline generation.

## Tweet Publication and Fanout Flow

```mermaid
sequenceDiagram
    participant USER as User<br/>(Mobile/Web)
    participant CDN as Twitter CDN
    participant LB as Load Balancer
    participant API as API Gateway<br/>(Finagle)
    participant TWEET as Tweet Service
    participant FANOUT as Fanout Service
    participant TIMELINE as Timeline Service
    participant KAFKA as Kafka Queue
    participant REDIS as Redis Cache
    participant MANHATTAN as Manhattan DB
    participant FOLLOWERS as User Service

    Note over USER,MANHATTAN: Tweet Publication Flow

    USER->>CDN: POST /tweet (text, media)
    CDN->>LB: Forward to origin
    LB->>API: Route request
    Note over API: Auth: OAuth validation<br/>Rate limit: 300 tweets/hour

    API->>TWEET: createTweet(userId, content)

    par Tweet Storage
        TWEET->>MANHATTAN: Store tweet data
        Note over MANHATTAN: Snowflake ID generation<br/>Atomic write operation
        MANHATTAN-->>TWEET: Tweet ID + timestamp
    and Media Processing
        alt Media attached
            TWEET->>TWEET: Process media
            Note over TWEET: Image/video validation<br/>Virus scanning<br/>Format conversion
        end
    end

    TWEET->>KAFKA: Publish tweet event
    Note over KAFKA: Topic: tweet-fanout<br/>Partitioned by user_id

    KAFKA->>FANOUT: Process fanout

    FANOUT->>FOLLOWERS: getFollowers(userId)
    FOLLOWERS-->>FANOUT: Follower list (avg: 700)

    alt Small follower count (<5M)
        Note over FANOUT: Push Fanout Strategy
        loop For each follower
            FANOUT->>TIMELINE: addToTimeline(followerId, tweetId)
            TIMELINE->>REDIS: Update timeline cache
        end
    else Large follower count (>5M)
        Note over FANOUT: Pull Fanout Strategy
        FANOUT->>REDIS: Mark celebrity tweet
        Note over REDIS: Timeline computed on read<br/>Avoid overwhelming fanout
    end

    TWEET-->>API: Tweet created successfully
    API-->>LB: Response (201 Created)
    LB-->>CDN: Cache headers
    CDN-->>USER: Tweet confirmation

    Note over USER,MANHATTAN: Total latency: p99 < 300ms
```

## Timeline Assembly Flow

```mermaid
sequenceDiagram
    participant USER as User
    participant CDN as Twitter CDN
    participant API as API Gateway
    participant TIMELINE as Timeline Service
    participant REDIS as Redis Cache
    participant RANKING as Ranking Service
    participant CELEBRITY as Celebrity Service
    participant MANHATTAN as Manhattan DB
    participant ML as ML Service

    Note over USER,ML: Home Timeline Assembly

    USER->>CDN: GET /home_timeline
    CDN->>API: Forward (cache miss)
    API->>TIMELINE: getHomeTimeline(userId, count=20)

    par Base Timeline Assembly
        TIMELINE->>REDIS: getTimelineCache(userId)
        alt Cache hit (80% hit rate)
            REDIS-->>TIMELINE: Cached timeline (last 200 tweets)
        else Cache miss
            TIMELINE->>MANHATTAN: getUserTimeline(userId)
            MANHATTAN-->>TIMELINE: Timeline data
            TIMELINE->>REDIS: Cache timeline (TTL: 1h)
        end
    and Celebrity Tweets
        TIMELINE->>CELEBRITY: getCelebrityTweets(userId)
        Note over CELEBRITY: Pull tweets from high-follower users<br/>Compute on demand
        CELEBRITY-->>TIMELINE: Celebrity tweets (top 50)
    and Promoted Content
        TIMELINE->>ML: getPromotedTweets(userId)
        Note over ML: ML ranking algorithm<br/>Engagement prediction<br/>Relevance scoring
        ML-->>TIMELINE: Promoted tweets (max 5)
    end

    TIMELINE->>RANKING: rankTimeline(tweets, userId)
    Note over RANKING: Ranking algorithm:<br/>• Recency (40%)<br/>• Engagement (30%)<br/>• Relevance (20%)<br/>• Diversity (10%)

    RANKING-->>TIMELINE: Ranked timeline (20 tweets)

    TIMELINE->>TIMELINE: Hydrate tweet data
    Note over TIMELINE: Add user info, media URLs<br/>Engagement counts, metadata

    TIMELINE-->>API: Timeline response (JSON)
    API-->>CDN: Cache response (TTL: 30s)
    CDN-->>USER: Timeline data

    Note over USER,ML: Timeline latency: p99 < 400ms
```

## Real-time Search Flow

```mermaid
sequenceDiagram
    participant USER as User
    participant API as Search API
    participant SEARCH as Search Service
    participant INDEX as Search Index<br/>(Lucene)
    participant TRENDING as Trending Service
    participant REALTIME as Real-time Index
    participant ML as ML Ranking
    participant REDIS as Results Cache

    Note over USER,REDIS: Real-time Search Flow

    USER->>API: GET /search?q="breaking news"
    Note over API: Query parsing<br/>Sanitization<br/>Rate limiting: 180/15min

    API->>SEARCH: searchTweets(query, filters)

    par Historical Search
        SEARCH->>INDEX: search(query, last_24h)
        Note over INDEX: Lucene-based search<br/>Inverted index<br/>BM25 scoring
        INDEX-->>SEARCH: Historical results (1000 candidates)
    and Real-time Search
        SEARCH->>REALTIME: searchRecent(query, last_1h)
        Note over REALTIME: Real-time indexing<br/>Recent tweets<br/>Stream processing
        REALTIME-->>SEARCH: Recent results (200 candidates)
    and Trending Context
        SEARCH->>TRENDING: getTrendingContext(query)
        TRENDING-->>SEARCH: Related trends, hashtags
    end

    SEARCH->>ML: rankResults(candidates, query, userId)
    Note over ML: ML ranking factors:<br/>• Relevance score<br/>• Engagement rate<br/>• Recency boost<br/>• User preferences

    ML-->>SEARCH: Ranked results (top 100)

    SEARCH->>REDIS: Check result cache
    alt Fresh results needed
        SEARCH->>SEARCH: Hydrate tweet metadata
        Note over SEARCH: User info, media, metrics<br/>Reply/retweet counts
        SEARCH->>REDIS: Cache results (TTL: 2min)
    end

    SEARCH-->>API: Search results
    API-->>USER: JSON response (20 tweets)

    Note over USER,REDIS: Search latency: p95 < 100ms
```

## Trending Topics Calculation

```mermaid
graph TB
    subgraph TrendingCalculation[Trending Topics Real-time Calculation]
        subgraph InputStreams[Input Streams]
            TWEET_STREAM[Tweet Stream<br/>500M tweets/day<br/>Real-time ingestion<br/>Text extraction]
            ENGAGEMENT_STREAM[Engagement Stream<br/>Likes, retweets, replies<br/>100B+ events/day<br/>User interactions]
            SEARCH_STREAM[Search Stream<br/>Search queries<br/>500M searches/day<br/>Query patterns]
        end

        subgraph ProcessingPipeline[Processing Pipeline]
            HERON_TOPOLOGY[Heron Topology<br/>Stream processing<br/>Real-time computation<br/>Low-latency spouts]

            subgraph ProcessingSteps[Processing Steps]
                TEXT_EXTRACTION[Text Extraction<br/>Hashtag parsing<br/>Entity recognition<br/>Language detection]
                TREND_DETECTION[Trend Detection<br/>Velocity calculation<br/>Volume analysis<br/>Spike detection]
                GEOGRAPHIC_FILTERING[Geographic Filtering<br/>Location-based trends<br/>Regional variations<br/>Cultural context]
                CONTENT_FILTERING[Content Filtering<br/>Spam detection<br/>Bot filtering<br/>Quality signals]
            end
        end

        subgraph TrendingStorage[Trending Storage]
            TREND_CACHE[Trend Cache<br/>Redis cluster<br/>Hot trending data<br/>1-minute refresh]
            TREND_DB[Trend Database<br/>Cassandra<br/>Historical trends<br/>Analytics storage]
            GEOGRAPHIC_TRENDS[Geographic Trends<br/>Location-specific<br/>Country/city level<br/>Personalized trends]
        end

        subgraph OutputServices[Output Services]
            TREND_API[Trending API<br/>REST endpoints<br/>Real-time updates<br/>Rate limiting]
            PUSH_NOTIFICATIONS[Push Notifications<br/>Breaking news alerts<br/>Personalized trends<br/>Mobile delivery]
            WEB_UPDATES[Web Updates<br/>WebSocket connections<br/>Live trend updates<br/>Browser notifications]
        end
    end

    TWEET_STREAM --> HERON_TOPOLOGY
    ENGAGEMENT_STREAM --> HERON_TOPOLOGY
    SEARCH_STREAM --> HERON_TOPOLOGY

    HERON_TOPOLOGY --> TEXT_EXTRACTION
    TEXT_EXTRACTION --> TREND_DETECTION
    TREND_DETECTION --> GEOGRAPHIC_FILTERING
    GEOGRAPHIC_FILTERING --> CONTENT_FILTERING

    CONTENT_FILTERING --> TREND_CACHE
    CONTENT_FILTERING --> TREND_DB
    CONTENT_FILTERING --> GEOGRAPHIC_TRENDS

    TREND_CACHE --> TREND_API
    GEOGRAPHIC_TRENDS --> PUSH_NOTIFICATIONS
    TREND_CACHE --> WEB_UPDATES

    %% Performance annotations
    HERON_TOPOLOGY -.->|"Processing rate: 1M events/sec<br/>Latency: p99 <100ms<br/>Update frequency: 1 minute"| TEXT_EXTRACTION
    TREND_CACHE -.->|"Refresh rate: Every minute<br/>Global trends: Top 10<br/>Geographic: Top 5 per region"| TREND_API

    classDef inputStyle fill:#E8F5E8,stroke:#388E3C,color:#000
    classDef processStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef storageStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef outputStyle fill:#E3F2FD,stroke:#1976D2,color:#000

    class TWEET_STREAM,ENGAGEMENT_STREAM,SEARCH_STREAM inputStyle
    class HERON_TOPOLOGY,TEXT_EXTRACTION,TREND_DETECTION,GEOGRAPHIC_FILTERING,CONTENT_FILTERING processStyle
    class TREND_CACHE,TREND_DB,GEOGRAPHIC_TRENDS storageStyle
    class TREND_API,PUSH_NOTIFICATIONS,WEB_UPDATES outputStyle
```

## Direct Message Flow

```mermaid
sequenceDiagram
    participant SENDER as Sender
    participant API as API Gateway
    participant DM_SVC as DM Service
    participant ENCRYPT as Encryption Service
    participant QUEUE as Message Queue<br/>(Kafka)
    participant DELIVERY as Delivery Service
    participant PUSH as Push Service
    participant RECIPIENT as Recipient
    participant STORAGE as Manhattan DB

    Note over SENDER,STORAGE: Direct Message Flow

    SENDER->>API: POST /dm/send
    Note over API: Auth validation<br/>Rate limit: 1000 DMs/day<br/>Recipient validation

    API->>DM_SVC: sendMessage(to, from, content)

    DM_SVC->>ENCRYPT: encryptMessage(content, keys)
    Note over ENCRYPT: End-to-end encryption<br/>Signal protocol<br/>Perfect forward secrecy
    ENCRYPT-->>DM_SVC: Encrypted payload

    DM_SVC->>STORAGE: Store message
    Note over STORAGE: Snowflake ID generation<br/>Encrypted storage<br/>GDPR compliance
    STORAGE-->>DM_SVC: Message ID

    DM_SVC->>QUEUE: Publish delivery event
    Note over QUEUE: Topic: dm-delivery<br/>Partitioned by recipient

    QUEUE->>DELIVERY: Process delivery

    par Real-time Delivery
        alt Recipient online
            DELIVERY->>RECIPIENT: WebSocket delivery
            Note over RECIPIENT: Real-time message<br/>Read receipts<br/>Typing indicators
        else Recipient offline
            DELIVERY->>PUSH: Send push notification
            PUSH->>RECIPIENT: Mobile notification
            Note over RECIPIENT: Background delivery<br/>Encrypted preview<br/>Badge update
        end
    and Delivery Confirmation
        DELIVERY->>STORAGE: Update delivery status
        Note over STORAGE: Delivered timestamp<br/>Read timestamp<br/>Delivery receipts
    end

    DM_SVC-->>API: Message sent
    API-->>SENDER: Confirmation response

    Note over SENDER,STORAGE: DM latency: p99 < 500ms<br/>Delivery rate: 99.9%
```

## Performance Characteristics by Request Type

| Request Type | p50 Latency | p99 Latency | Throughput | Cache Hit Rate |
|--------------|-------------|-------------|------------|----------------|
| **Tweet Publication** | 150ms | 300ms | 6K RPS | N/A |
| **Home Timeline** | 180ms | 400ms | 300K RPS | 80% |
| **Search Queries** | 45ms | 100ms | 100K RPS | 70% |
| **User Profile** | 80ms | 200ms | 500K RPS | 95% |
| **Trending Topics** | 25ms | 75ms | 50K RPS | 98% |
| **Direct Messages** | 200ms | 500ms | 20K RPS | 85% |
| **Media Upload** | 800ms | 2000ms | 10K RPS | N/A |

## Error Handling and Fallbacks

```mermaid
graph TB
    subgraph ErrorHandling[Error Handling Strategies]
        subgraph CircuitBreakers[Circuit Breakers]
            TIMELINE_CB[Timeline Circuit Breaker<br/>Failure threshold: 50%<br/>Timeout: 30s<br/>Recovery: 60s]
            SEARCH_CB[Search Circuit Breaker<br/>Failure threshold: 40%<br/>Timeout: 10s<br/>Recovery: 30s]
            DM_CB[DM Circuit Breaker<br/>Failure threshold: 30%<br/>Timeout: 45s<br/>Recovery: 90s]
        end

        subgraph FallbackStrategies[Fallback Strategies]
            CACHED_TIMELINE[Cached Timeline<br/>Stale timeline data<br/>Redis fallback<br/>Graceful degradation]
            SIMPLIFIED_SEARCH[Simplified Search<br/>Basic text matching<br/>Reduced features<br/>Faster response]
            DELAYED_DM[Delayed DM Delivery<br/>Queue for retry<br/>Background processing<br/>Eventually consistent]
        end

        subgraph RetryLogic[Retry Logic]
            EXPONENTIAL_BACKOFF[Exponential Backoff<br/>Base: 100ms<br/>Max: 30s<br/>Jitter: ±25%]
            DEADLINE_PROPAGATION[Deadline Propagation<br/>Request timeouts<br/>Context cancellation<br/>Resource cleanup]
        end
    end

    TIMELINE_CB --> CACHED_TIMELINE
    SEARCH_CB --> SIMPLIFIED_SEARCH
    DM_CB --> DELAYED_DM

    CACHED_TIMELINE --> EXPONENTIAL_BACKOFF
    SIMPLIFIED_SEARCH --> DEADLINE_PROPAGATION
    DELAYED_DM --> EXPONENTIAL_BACKOFF

    %% Error rates and recovery
    TIMELINE_CB -.->|"Error rate: <1%<br/>Recovery time: 60s<br/>Fallback success: 95%"| CACHED_TIMELINE

    classDef cbStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef fallbackStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef retryStyle fill:#E8F5E8,stroke:#388E3C,color:#000

    class TIMELINE_CB,SEARCH_CB,DM_CB cbStyle
    class CACHED_TIMELINE,SIMPLIFIED_SEARCH,DELAYED_DM fallbackStyle
    class EXPONENTIAL_BACKOFF,DEADLINE_PROPAGATION retryStyle
```

## Rate Limiting and API Protection

| API Endpoint | Rate Limit | Window | Burst Allowance |
|--------------|------------|--------|-----------------|
| **Tweet Creation** | 300 tweets | 15 minutes | 50 |
| **Timeline Requests** | 75 requests | 15 minutes | 15 |
| **Search API** | 180 requests | 15 minutes | 30 |
| **Direct Messages** | 1000 messages | 24 hours | 100 |
| **Follow/Unfollow** | 400 actions | 24 hours | 50 |
| **Media Upload** | 25 uploads | 15 minutes | 5 |

## Key Optimizations

1. **Hybrid Fanout**: Smart routing based on follower count
2. **Timeline Caching**: Redis-based hot data caching
3. **Real-time Indexing**: Immediate search availability
4. **Geographic Optimization**: Region-specific trending topics
5. **Predictive Prefetching**: Pre-load likely content
6. **Connection Pooling**: Efficient resource utilization

*Last updated: September 2024*
*Source: Twitter Engineering Blog, Performance analysis, API documentation*