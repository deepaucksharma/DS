# Slack Request Flow - Message Delivery Pipeline

## Overview
Complete message delivery flow from user send to recipient receipt, handling 116K messages/second peak with 99.95% delivery guarantee and sub-100ms p99 latency.

## Message Send Flow - The Golden Path

```mermaid
sequenceDiagram
    participant User as Slack Client<br/>(Desktop/Mobile)
    participant CDN as Cloudflare CDN<br/>Edge Cache
    participant ALB as AWS ALB<br/>Load Balancer
    participant WS as WebSocket Server<br/>c5.4xlarge
    participant API as Message API<br/>Go Service
    participant AUTH as Auth Service<br/>OAuth Validation
    participant SHARD as MySQL Shard<br/>Channel Data
    participant CACHE as Redis Cache<br/>Message Buffer
    participant SEARCH as Elasticsearch<br/>Search Index
    participant KAFKA as Kafka<br/>Event Stream
    participant PUSH as Push Service<br/>Mobile Notifications

    Note over User,PUSH: Message Send Flow - p99: 89ms end-to-end

    User->>CDN: POST /api/chat.postMessage
    Note right of User: HTTP/2 connection<br/>TLS 1.3 encrypted<br/>Auth token in header

    CDN->>ALB: Route to API tier
    Note right of CDN: Latency: p99 8ms<br/>Cache miss: API calls<br/>Cache hit: Static assets

    ALB->>API: Forward message request
    Note right of ALB: Health check: 30s interval<br/>Connection draining: 300s<br/>Target group: 380 instances

    API->>AUTH: Validate auth token
    Note right of API: JWT validation<br/>User permissions<br/>Channel membership

    AUTH-->>API: User authorized
    Note right of AUTH: Response: p99 5ms<br/>Token cache: 15min TTL<br/>Rate limit: 60 req/min

    API->>SHARD: SELECT channel metadata
    Note right of API: Channel ID: C1234567890<br/>Shard key: channel_id % 180<br/>Read replica routing

    SHARD-->>API: Channel exists, user has access
    Note right of SHARD: Query time: p99 12ms<br/>Connection pool: 50 conns<br/>Read preference: secondary

    API->>API: Generate message ID
    Note right of API: Snowflake ID: 64-bit<br/>Timestamp + worker + sequence<br/>Guaranteed uniqueness

    API->>SHARD: INSERT INTO messages
    Note right of API: Message data:<br/>- ID: 1234567890123456<br/>- Channel: C1234567890<br/>- User: U0987654321<br/>- Text: "Hello team!"<br/>- Timestamp: 1640995200.123

    SHARD-->>API: Message stored
    Note right of SHARD: Write time: p99 18ms<br/>Auto-commit enabled<br/>Binlog replication: async

    API->>CACHE: LPUSH channel:messages
    Note right of API: Redis command<br/>Message + metadata<br/>TTL: 24 hours

    CACHE-->>API: Added to message buffer
    Note right of CACHE: Pipeline: 10 commands<br/>Memory usage: 72%<br/>Cluster: 120 nodes

    API->>SEARCH: Index message async
    Note right of API: Elasticsearch bulk API<br/>Index: messages-2024-01<br/>Routing: channel_id

    API->>KAFKA: Publish message event
    Note right of API: Topic: message-events<br/>Partition: channel_id hash<br/>Replication: 3x

    API-->>User: HTTP 200 + message ID
    Note right of API: Response payload:<br/>{"ok": true,<br/>"ts": "1640995200.123",<br/>"message": {...}}

    Note over User,PUSH: Real-time Delivery Phase

    KAFKA->>WS: Consume message event
    Note right of KAFKA: Consumer group: websocket<br/>Offset commit: manual<br/>Batch size: 100

    WS->>WS: Find channel subscribers
    Note right of WS: In-memory connection map<br/>Channel: C1234567890<br/>Active connections: 12

    loop For each subscriber
        WS->>User: WebSocket message
        Note right of WS: Frame type: text<br/>Compression: deflate<br/>Heartbeat: 30s
    end

    WS->>PUSH: Queue mobile notifications
    Note right of WS: Offline users only<br/>APNs + FCM delivery<br/>Badge count update

    SEARCH-->>SEARCH: Message indexed
    Note right of SEARCH: Bulk indexing: 5s interval<br/>Refresh: 1s<br/>Replica count: 2

    PUSH->>User: Mobile push notification
    Note right of PUSH: Delivery rate: 98.5%<br/>Latency: p99 2.1s<br/>Retry: 3 attempts
```

## Performance Metrics

### End-to-End Latency
- **p50 latency**: 12ms (send to WebSocket delivery)
- **p99 latency**: 89ms (including all subscribers)
- **p999 latency**: 340ms (including retries)
- **Peak throughput**: 116K messages/second

### Component Breakdown
| Component | p50 | p99 | p999 | Notes |
|-----------|-----|-----|------|-------|
| CDN Routing | 2ms | 8ms | 18ms | Edge cache hit: 94% |
| Load Balancer | 1ms | 3ms | 8ms | Health check overhead |
| Auth Validation | 2ms | 5ms | 12ms | Token cache hit: 89% |
| Database Write | 8ms | 18ms | 45ms | Including replication |
| Cache Update | 1ms | 3ms | 8ms | Redis cluster mode |
| WebSocket Delivery | 3ms | 12ms | 28ms | Fan-out to subscribers |

## Message Delivery Guarantees

### At-Least-Once Delivery
```mermaid
graph TB
    subgraph "Delivery Pipeline"
        SEND[Message Send]
        DB[Database Write<br/>MySQL with binlog]
        KAFKA[Kafka Event<br/>min.insync.replicas=2]
        WS[WebSocket Delivery<br/>Ack tracking]
        MOBILE[Mobile Push<br/>APNs/FCM]
    end

    subgraph "Failure Handling"
        RETRY[Retry Logic<br/>Exponential backoff]
        DLQ[Dead Letter Queue<br/>Manual investigation]
        ALERT[PagerDuty Alert<br/>On-call escalation]
    end

    SEND --> DB
    DB --> KAFKA
    KAFKA --> WS
    KAFKA --> MOBILE

    WS -.->|Failure| RETRY
    MOBILE -.->|Failure| RETRY
    RETRY -.->|Max attempts| DLQ
    DLQ --> ALERT

    classDef deliveryStyle fill:#10B981,stroke:#059669,color:#fff
    classDef failureStyle fill:#EF4444,stroke:#DC2626,color:#fff

    class SEND,DB,KAFKA,WS,MOBILE deliveryStyle
    class RETRY,DLQ,ALERT failureStyle
```

### Duplicate Prevention
- **Idempotency keys** for message deduplication
- **Snowflake IDs** ensure uniqueness across shards
- **Client-side dedup** using message timestamps
- **99.999% accuracy** (< 1 duplicate per 100K messages)

## Message Ordering

### Channel-Level Ordering
```mermaid
graph LR
    subgraph "Message Ordering Pipeline"
        CLIENT[Client Send<br/>Sequential]
        SHARD[MySQL Shard<br/>Auto-increment ID]
        CACHE[Redis LPUSH<br/>Channel queue]
        KAFKA[Kafka Partition<br/>Channel hash]
        WS[WebSocket Delivery<br/>FIFO per connection]
    end

    CLIENT -->|HTTP/2 pipeline| SHARD
    SHARD -->|Ordered writes| CACHE
    CACHE -->|Queue ordering| KAFKA
    KAFKA -->|Partition ordering| WS

    classDef orderStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class CLIENT,SHARD,CACHE,KAFKA,WS orderStyle
```

### Ordering Guarantees
- **Per-channel ordering** maintained end-to-end
- **MySQL auto-increment** provides database ordering
- **Kafka partitioning** by channel_id maintains event order
- **WebSocket FIFO** ensures client delivery order
- **99.98% correct ordering** (measured by client timestamps)

## Error Handling & Retries

### Retry Strategy
| Error Type | Initial Delay | Max Attempts | Backoff | Timeout |
|------------|---------------|--------------|---------|---------|
| Database timeout | 100ms | 3 | Exponential | 5s |
| Cache failure | 50ms | 2 | Linear | 2s |
| WebSocket disconnect | 1s | 5 | Exponential | 30s |
| Mobile push failure | 2s | 3 | Exponential | 60s |

### Circuit Breaker Configuration
```mermaid
graph TB
    subgraph "Circuit Breaker States"
        CLOSED[CLOSED<br/>Normal operation<br/>Error threshold: 5%]
        OPEN[OPEN<br/>Fail fast<br/>Duration: 30s]
        HALF[HALF-OPEN<br/>Test recovery<br/>Success threshold: 3]
    end

    CLOSED -->|Error rate > 5%| OPEN
    OPEN -->|After 30s| HALF
    HALF -->|3 successes| CLOSED
    HALF -->|1 failure| OPEN

    classDef normalStyle fill:#10B981,stroke:#059669,color:#fff
    classDef errorStyle fill:#EF4444,stroke:#DC2626,color:#fff
    classDef testStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class CLOSED normalStyle
    class OPEN errorStyle
    class HALF testStyle
```

## Rate Limiting

### User Rate Limits
- **Standard users**: 1 message/second sustained, 10/second burst
- **Bot users**: 1 message/second per channel
- **Enterprise**: Custom limits up to 100/second
- **API calls**: 60 requests/minute per user token

### Implementation
```mermaid
graph TB
    subgraph "Rate Limiting Pipeline"
        REQ[Incoming Request]
        REDIS[Redis Counter<br/>Sliding window]
        CHECK{Rate OK?}
        ALLOW[Process Request]
        REJECT[429 Too Many Requests]
    end

    REQ --> REDIS
    REDIS --> CHECK
    CHECK -->|Yes| ALLOW
    CHECK -->|No| REJECT

    classDef allowStyle fill:#10B981,stroke:#059669,color:#fff
    classDef rejectStyle fill:#EF4444,stroke:#DC2626,color:#fff

    class REQ,REDIS,ALLOW allowStyle
    class REJECT rejectStyle
```

## Mobile & Offline Handling

### Push Notification Flow
- **Online users**: WebSocket delivery only
- **Offline users**: Push notification + badge update
- **Do Not Disturb**: Queued for later delivery
- **Delivery rate**: 98.5% within 5 seconds

### Sync on Reconnect
- **Message gap detection** using last seen timestamp
- **Bulk message fetch** for offline period
- **Progressive loading** for large gaps (> 1000 messages)
- **Conflict resolution** for simultaneous edits

## Monitoring & Alerting

### Key Metrics
- **Message delivery rate**: Target 99.95%, Alert < 99.9%
- **End-to-end latency**: Target p99 < 100ms, Alert > 150ms
- **WebSocket connection health**: Target 98% active, Alert < 95%
- **Database replication lag**: Target < 1s, Alert > 5s

### Incident Response
- **PagerDuty integration** for critical alerts
- **Automated rollback** for deployment issues
- **Circuit breaker activation** for downstream failures
- **Graceful degradation** during peak load

*Based on Slack engineering blog posts, Strange Loop presentations, and production incident reports. Latency targets and error rates from publicly shared SLA commitments.*