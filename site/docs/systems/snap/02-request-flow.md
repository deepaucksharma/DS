# Snap (Snapchat) - Request Flow

## Overview

The Snap request flow handles 6 billion snaps daily with ephemeral messaging requiring sub-500ms end-to-end delivery and real-time AR filter processing.

## Snap Sending Request Flow - The Golden Path

```mermaid
sequenceDiagram
    participant Client as iOS/Android App<br/>375M DAU
    participant CDN as CloudFlare CDN<br/>2000+ PoPs
    participant LB as F5 Load Balancer<br/>1M+ rps capacity
    participant API as Kong API Gateway<br/>300K+ rps
    participant Auth as Auth Service<br/>JWT + Redis
    participant Upload as Upload Service<br/>Go 1.20
    participant Filter as Filter Engine<br/>C++/OpenCV
    participant Snap as Snap Service<br/>Go 1.20
    participant Redis as Redis Cache<br/>500+ nodes
    participant SnapDB as Cassandra<br/>2000 nodes
    participant S3 as S3 Media Storage<br/>100PB+
    participant Push as Push Service<br/>FCM/APNs
    participant Recipient as Recipient Device

    Note over Client: User takes photo/video<br/>Applies AR filter

    Client->>CDN: 1. POST /snap/upload<br/>Latency Budget: 50ms
    CDN->>LB: Forward to nearest region<br/>p99: 10ms
    LB->>API: Route to upload endpoint<br/>p99: 5ms
    API->>Auth: Validate JWT token<br/>p99: 2ms (Redis hit)
    Auth-->>API: ✓ Valid user session<br/>User: 12345, Plan: Premium

    API->>Upload: POST /media/upload<br/>p99: 15ms
    Note over Upload: Media validation<br/>Size: <100MB<br/>Duration: <60s

    Upload->>S3: PUT media object<br/>Bucket: snap-media-us-east<br/>p99: 100ms
    S3-->>Upload: ✓ Upload complete<br/>Object: s3://snap-media/user123/snap456.mp4

    par AR Filter Processing
        Upload->>Filter: POST /filter/apply<br/>Filter ID: lens_birthday_2024
        Note over Filter: Real-time processing<br/>OpenCV + ML models<br/>p99: 200ms
        Filter-->>Upload: ✓ Filtered media<br/>New S3 key: snap456_filtered.mp4
    end

    Upload->>Snap: POST /snap/create<br/>Metadata + S3 keys

    par Database Operations
        Snap->>Redis: SET snap:456 metadata<br/>TTL: 24 hours<br/>p99: 0.5ms
        Snap->>SnapDB: INSERT snap metadata<br/>Partition: user_123<br/>p99: 10ms
    end

    par Recipient Notification
        Snap->>Push: POST /notify/snap<br/>Recipients: [user789, user101]
        Push->>Recipient: FCM/APNs push<br/>Delivery: 95% within 1s
    end

    Snap-->>API: ✓ Snap created<br/>ID: snap_456<br/>Total time: 380ms
    API-->>CDN: Response with snap ID
    CDN-->>Client: 200 OK + snap_id<br/>End-to-end: 430ms

    Note over Client,Recipient: Recipients receive notification<br/>Can view for 1-10 seconds
```

## Chat Message Request Flow

```mermaid
sequenceDiagram
    participant Sender as Sender App
    participant API as API Gateway
    participant Chat as Chat Service<br/>Erlang/OTP
    participant Redis as Redis Cache
    participant DDB as DynamoDB<br/>Chat Storage
    participant Push as Push Service
    participant Receiver as Receiver App

    Sender->>API: POST /chat/send<br/>Message: "Hey!"<br/>Thread: thread_789
    API->>Chat: Forward message<br/>p99: 5ms

    par Real-time Processing
        Chat->>Redis: GET thread:789 participants<br/>p99: 0.5ms
        Redis-->>Chat: [user123, user456]<br/>Online status: both active

        Chat->>DDB: PUT message<br/>Partition: thread_789<br/>Sort: timestamp<br/>p99: 8ms

        Chat->>Push: Notify recipients<br/>Online users get WebSocket<br/>Offline get push notification
    end

    Push->>Receiver: WebSocket delivery<br/>Real-time: <50ms same region

    Chat-->>API: ✓ Message sent<br/>ID: msg_12345<br/>Total: 45ms
    API-->>Sender: 200 OK + message_id

    Note over Receiver: Message displayed<br/>Auto-delete after read
```

## Snap Map Location Update Flow

```mermaid
sequenceDiagram
    participant App as Snapchat App
    participant API as API Gateway
    participant Geo as Geo Service<br/>Go 1.20
    participant Redis as Redis Geo Cache
    participant Map as Map Service
    participant Friends as Friend Graph<br/>MySQL

    App->>API: PUT /location/update<br/>Lat: 37.7749, Lng: -122.4194<br/>Accuracy: 5m
    API->>Geo: Update user location<br/>p99: 10ms

    par Location Processing
        Geo->>Redis: GEOADD user_locations<br/>user123 -122.4194 37.7749<br/>p99: 1ms

        Geo->>Friends: GET friends for user123<br/>Cache hit rate: 95%<br/>p99: 5ms
        Friends-->>Geo: [user456, user789, user101]
    end

    par Friend Notifications
        Geo->>Map: Update visible locations<br/>For friends within 1km radius
        Map->>Redis: SET map_updates:user456<br/>New location for user123<br/>TTL: 300s
    end

    Geo-->>API: ✓ Location updated<br/>Visible to: 3 friends<br/>Total: 25ms
    API-->>App: 200 OK

    Note over App: Location shared with friends<br/>Updates every 30s when app active
```

## Story Upload Request Flow

```mermaid
sequenceDiagram
    participant App as Snapchat App
    participant CDN as CloudFlare CDN
    participant API as API Gateway
    participant Story as Story Service<br/>Java 17
    participant Transcode as Video Transcode<br/>FFmpeg
    participant S3 as S3 Storage
    participant Redis as Redis Cache
    participant SnapDB as Cassandra

    App->>CDN: POST /story/upload<br/>Video: 30s HD (50MB)
    CDN->>API: Route to story service
    API->>Story: POST /story/create<br/>Duration: 30s<br/>Resolution: 1080p

    par Media Processing
        Story->>S3: PUT raw video<br/>Bucket: story-raw-media<br/>p99: 2s for 50MB

        Story->>Transcode: POST /transcode<br/>Profiles: [1080p, 720p, 480p]<br/>p99: 10s for 30s video

        par Multiple Quality Processing
            Transcode->>S3: PUT story_1080p.mp4<br/>Size: 40MB
            Transcode->>S3: PUT story_720p.mp4<br/>Size: 25MB
            Transcode->>S3: PUT story_480p.mp4<br/>Size: 15MB
        end
    end

    par Metadata Storage
        Story->>SnapDB: INSERT story metadata<br/>Partition: user_stories_123<br/>TTL: 24 hours<br/>p99: 10ms

        Story->>Redis: SET story:789 metadata<br/>Views: 0, TTL: 24h<br/>p99: 1ms
    end

    Story-->>API: ✓ Story published<br/>ID: story_789<br/>Total: 12s
    API-->>CDN: Response with story ID
    CDN-->>App: 200 OK<br/>Story live for 24 hours

    Note over App: Story appears in friends' feeds<br/>Auto-delete after 24 hours
```

## Performance SLAs and Latency Budgets

### Critical Path Latencies
- **Snap Send Total**: 500ms (p99)
  - Upload: 100ms
  - Filter Processing: 200ms
  - Database Write: 50ms
  - Notification: 100ms
  - Network/API: 50ms

- **Chat Message**: 100ms (p99)
  - Database Write: 20ms
  - Real-time Delivery: 50ms
  - Network/API: 30ms

- **Location Update**: 50ms (p99)
  - Geo Processing: 20ms
  - Friend Lookup: 15ms
  - Cache Update: 10ms
  - Network/API: 5ms

### Fallback Scenarios

#### Filter Service Failure
```
IF Filter Engine unavailable:
  THEN send original media
  AND queue for async filter retry
  AND notify user of processing delay
```

#### Database Write Failure
```
IF Primary DB write fails:
  THEN write to backup Redis
  AND queue for async DB retry
  AND maintain user experience
```

#### Push Notification Failure
```
IF FCM/APNs unavailable:
  THEN store notification in queue
  AND retry with exponential backoff
  AND deliver on next app open
```

## Regional Failover Flow

```mermaid
graph TD
    A[US-East Primary] -->|Failure| B[Detect Health Check Failure<br/>30s timeout]
    B --> C[Route53 DNS Failover<br/>TTL: 60s]
    C --> D[US-West Secondary<br/>Active-Active]
    D --> E[Sync User Sessions<br/>Redis Cross-Region]
    E --> F[Continue Service<br/>5min RTO]

    classDef failureStyle fill:#EF4444,stroke:#DC2626,color:#fff
    classDef recoveryStyle fill:#10B981,stroke:#047857,color:#fff

    class A,B failureStyle
    class D,E,F recoveryStyle
```

## Error Handling and Recovery

### Circuit Breaker Pattern
- **Filter Service**: Opens after 50 failures in 1 minute
- **Database**: Opens after 20 failures in 30 seconds
- **Push Service**: Opens after 100 failures in 2 minutes

### Retry Policies
- **Exponential Backoff**: 100ms, 200ms, 400ms, 800ms
- **Max Retries**: 3 for critical path, 5 for async operations
- **Jitter**: ±25% to prevent thundering herd

### Data Consistency
- **Eventual Consistency**: Acceptable for story views, friend counts
- **Strong Consistency**: Required for message delivery, snap viewing
- **Conflict Resolution**: Last-write-wins for location updates