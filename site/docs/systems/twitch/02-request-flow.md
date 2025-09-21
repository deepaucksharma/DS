# Twitch Request Flow - Stream Ingestion to Viewer Delivery

## The Golden Path: Stream to Screen in <3 Seconds

Twitch's request flow represents one of the most complex real-time media pipelines in the world, handling **9M+ concurrent streams** and delivering to **15M+ concurrent viewers** with ultra-low latency.

### Critical Path Metrics
- **Stream Ingestion**: <100ms processing latency
- **Transcoding**: <500ms for all quality levels
- **CDN Propagation**: <200ms to edge servers
- **Viewer Delivery**: <3 seconds end-to-end (Low Latency mode)
- **Chat Delivery**: <500ms message propagation

## Complete Request Flow Architecture

```mermaid
sequenceDiagram
    participant S as Streamer<br/>(OBS Studio)
    participant I as Ingestion Layer<br/>(RTMP Servers)
    participant T as Transcoding<br/>(FFmpeg Farm)
    participant M as Manifest Generator<br/>(HLS/DASH)
    participant E as Edge Servers<br/>(CloudFront)
    participant V as Viewer<br/>(Web/Mobile App)
    participant C as Chat Service<br/>(WebSocket)
    participant A as Analytics<br/>(Real-time metrics)

    Note over S,A: Live Stream Ingestion Flow (Critical Path)

    S->>+I: RTMP Stream Push<br/>1080p60, 8000 kbps<br/>H.264 + AAC
    Note right of I: Latency Budget: <100ms
    I->>I: Stream validation<br/>Keyframe detection<br/>GOP: 2 seconds
    I->>+T: Raw video stream<br/>TCP socket<br/>Chunk size: 188 bytes

    Note over T: Transcoding Farm (c5n.18xlarge + p3.16xlarge)
    T->>T: Parallel encoding<br/>6 quality levels<br/>160p → 1080p60
    T->>T: Adaptive bitrate<br/>500 kbps → 8000 kbps<br/>H.264/AV1 codecs
    Note right of T: Latency Budget: <500ms

    T->>+M: Multi-bitrate streams<br/>6 quality variants<br/>2s segment duration
    M->>M: Generate manifests<br/>HLS m3u8 + DASH mpd<br/>Update every 2s
    M->>+E: Stream segments<br/>S3 PUT operations<br/>Multi-region upload

    Note over E: CDN Distribution (100+ PoPs)
    E->>E: Edge cache warming<br/>95%+ hit ratio<br/>NVMe SSD storage
    Note right of E: Latency Budget: <200ms

    V->>+E: Video request<br/>GET /playlist.m3u8<br/>Accept-Encoding: gzip
    E-->>V: Manifest response<br/>200 OK<br/>Cache-Control: max-age=2

    loop Video Segment Delivery
        V->>E: Segment request<br/>GET /segment_N.ts<br/>Range: bytes=0-
        E-->>V: Video segment<br/>2MB avg size<br/>206 Partial Content
        Note right of V: Player buffer: 6-10 seconds
    end

    Note over S,A: Real-time Chat Flow (Parallel to Video)

    V->>+C: WebSocket connect<br/>wss://irc-ws.chat.twitch.tv<br/>TLS 1.3
    C->>C: Authentication<br/>OAuth token validation<br/>Rate limit: 20 msg/30s

    V->>C: Chat message<br/>PRIVMSG #channel<br/>Max 500 characters
    C->>C: Message validation<br/>AutoMod filtering<br/>Spam detection
    C->>C: Broadcast message<br/>Redis pub/sub<br/>Fan-out: 100K+ viewers
    C-->>V: Message delivery<br/>IRC protocol<br/>Sub-500ms latency

    Note over S,A: Analytics & Monitoring (Continuous)

    I->>+A: Ingestion metrics<br/>Stream health<br/>Keyframe intervals
    T->>A: Encoding metrics<br/>CPU usage: 80%<br/>Queue depth: <10
    E->>A: CDN metrics<br/>Cache hit ratio: 95%<br/>Origin requests: 5%
    V->>A: Viewer metrics<br/>Buffering events<br/>Quality changes
    C->>A: Chat metrics<br/>Message volume<br/>Moderation actions

    Note over A: Real-time alerting for P0 incidents
    A->>A: Anomaly detection<br/>ML-based thresholds<br/>Auto-escalation
```

## Stream Ingestion Flow Details

### RTMP Processing Pipeline
```mermaid
graph LR
    subgraph StreamerDevice[Streamer Device]
        OBS[OBS Studio<br/>x264 encoder<br/>CBR 8000 kbps]
        Bandwidth[Upload Bandwidth<br/>10+ Mbps required<br/>Stable connection]
    end

    subgraph IngestionLayer[Ingestion Layer - c5n.9xlarge]
        RTMP[RTMP Server<br/>nginx-rtmp<br/>Port 1935]
        Validator[Stream Validator<br/>Keyframe analysis<br/>GOP validation]
        Buffer[Ingestion Buffer<br/>Redis stream<br/>3-second window]
    end

    subgraph TranscodingFarm[Transcoding Farm]
        GPU1[GPU Transcoder 1<br/>p3.16xlarge<br/>8x V100 GPUs]
        GPU2[GPU Transcoder 2<br/>NVENC encoding<br/>H.264 + AV1]
        CPU[CPU Transcoder<br/>c5n.18xlarge<br/>x264 software]
    end

    OBS -->|RTMP push<br/>TCP 1935<br/>Persistent connection| RTMP
    RTMP -->|Stream validation<br/>H.264 + AAC<br/>GOP: 2 seconds| Validator
    Validator -->|Raw video<br/>YUV 4:2:0<br/>30/60 fps| Buffer

    Buffer -->|High priority<br/>GPU encoding| GPU1
    Buffer -->|Standard quality<br/>GPU encoding| GPU2
    Buffer -->|Fallback encoding<br/>CPU encoding| CPU

    classDef edgeStyle fill:#3B82F6,stroke:#1D4ED8,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class RTMP,Validator edgeStyle
    class GPU1,GPU2,CPU serviceStyle
    class Buffer stateStyle
```

## Video Delivery Pipeline

### Multi-Quality Transcoding
```mermaid
graph TB
    subgraph Input[Source Stream]
        Source[1080p60 Source<br/>8000 kbps<br/>H.264 High Profile]
    end

    subgraph TranscodingOutputs[Transcoding Outputs]
        Q1[160p30<br/>500 kbps<br/>Mobile fallback]
        Q2[360p30<br/>1000 kbps<br/>Low bandwidth]
        Q3[480p30<br/>2000 kbps<br/>Standard quality]
        Q4[720p30<br/>3500 kbps<br/>HD quality]
        Q5[720p60<br/>5000 kbps<br/>HD 60fps]
        Q6[1080p60<br/>8000 kbps<br/>Source quality]
    end

    subgraph PackagingLayer[Packaging Layer]
        HLS[HLS Packager<br/>2-second segments<br/>.m3u8 playlist]
        DASH[DASH Packager<br/>2-second segments<br/>.mpd manifest]
        Thumb[Thumbnail Generator<br/>Preview images<br/>Every 10 seconds]
    end

    Source --> Q1
    Source --> Q2
    Source --> Q3
    Source --> Q4
    Source --> Q5
    Source --> Q6

    Q1 --> HLS
    Q2 --> HLS
    Q3 --> HLS
    Q4 --> HLS
    Q5 --> HLS
    Q6 --> HLS

    Q1 --> DASH
    Q2 --> DASH
    Q3 --> DASH
    Q4 --> DASH
    Q5 --> DASH
    Q6 --> DASH

    Source --> Thumb

    classDef sourceStyle fill:#3B82F6,stroke:#1D4ED8,color:#fff
    classDef qualityStyle fill:#10B981,stroke:#047857,color:#fff
    classDef packageStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class Source sourceStyle
    class Q1,Q2,Q3,Q4,Q5,Q6 qualityStyle
    class HLS,DASH,Thumb packageStyle
```

## Chat Message Flow

### Real-time Chat Architecture
```mermaid
graph TB
    subgraph ViewerClients[Viewer Clients - 100K+ concurrent]
        Web[Web Client<br/>WebSocket connection<br/>wss://irc-ws.chat.twitch.tv]
        Mobile[Mobile App<br/>WebSocket over HTTP/2<br/>TLS 1.3]
        Third[Third-party Bots<br/>IRC connection<br/>Rate limited: 20/30s]
    end

    subgraph ChatEdge[Chat Edge Layer]
        WSProxy[WebSocket Proxy<br/>HAProxy<br/>c5n.large instances]
        LoadBalancer[Chat Load Balancer<br/>Application Layer<br/>Sticky sessions]
    end

    subgraph ChatService[Chat Service Core]
        IRCServer[IRC Server<br/>Go implementation<br/>Channel routing]
        MessageQueue[Message Queue<br/>Redis pub/sub<br/>100K+ subscribers]
        AutoMod[AutoMod Service<br/>ML text analysis<br/>99.5% accuracy]
    end

    subgraph ChatStorage[Chat Storage]
        RecentCache[Recent Messages<br/>Redis cache<br/>Last 500 messages]
        MessageDB[Message Archive<br/>DynamoDB<br/>30-day retention]
    end

    Web -->|Chat message<br/>PRIVMSG #channel| WSProxy
    Mobile -->|Chat message<br/>JSON over WS| WSProxy
    Third -->|IRC PRIVMSG<br/>Raw IRC protocol| LoadBalancer

    WSProxy --> LoadBalancer
    LoadBalancer --> IRCServer

    IRCServer -->|Message validation<br/>User permissions| AutoMod
    AutoMod -->|Approved message<br/>JSON format| MessageQueue
    MessageQueue -->|Fan-out delivery<br/>To all subscribers| WSProxy

    IRCServer --> RecentCache
    MessageQueue --> MessageDB

    WSProxy -.->|Message broadcast<br/>Sub-500ms delivery| Web
    WSProxy -.->|Message broadcast<br/>Push notification| Mobile

    classDef edgeStyle fill:#3B82F6,stroke:#1D4ED8,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class WSProxy,LoadBalancer edgeStyle
    class IRCServer,MessageQueue,AutoMod serviceStyle
    class RecentCache,MessageDB stateStyle
```

## API Request Flows

### User Authentication Flow
```mermaid
sequenceDiagram
    participant U as User Browser
    participant LB as Load Balancer
    participant API as API Gateway
    participant Auth as Auth Service
    participant User as User Service
    participant Cache as Redis Cache

    U->>+LB: Login request<br/>POST /auth/login<br/>username + password
    LB->>+API: Route request<br/>Rate limit: 1000/min<br/>DDoS protection
    API->>+Auth: Validate credentials<br/>bcrypt + salt<br/>Password hash check

    Auth->>Auth: Generate JWT<br/>RS256 signature<br/>2-hour expiry
    Auth->>+Cache: Store session<br/>JWT ID mapping<br/>TTL: 2 hours
    Auth-->>-API: JWT token<br/>200 OK<br/>Set-Cookie: secure

    API-->>-LB: Auth response<br/>JWT in header<br/>CSRF token
    LB-->>-U: Login success<br/>Redirect to dashboard<br/>Secure cookies

    Note over U,Cache: Subsequent API requests with JWT

    U->>+LB: API request<br/>GET /api/user/profile<br/>Authorization: Bearer JWT
    LB->>+API: Forwarded request<br/>JWT validation<br/>Rate limiting applied

    API->>+Auth: Verify JWT<br/>Signature validation<br/>Expiry check
    Auth->>+Cache: Session lookup<br/>JWT ID check<br/>User permissions
    Cache-->>-Auth: Session valid<br/>User ID: 12345<br/>Roles: [user, subscriber]
    Auth-->>-API: Auth success<br/>User context<br/>Permission grants

    API->>+User: Get profile<br/>User ID: 12345<br/>Include preferences
    User-->>-API: Profile data<br/>JSON response<br/>Personal settings
    API-->>-LB: API response<br/>200 OK<br/>Cache-Control: private
    LB-->>-U: Profile data<br/>JSON payload<br/>User dashboard
```

## Performance Characteristics

### Latency Breakdown (Low Latency Mode)
- **Encoder to Ingestion**: 50-100ms (network + processing)
- **Ingestion to Transcoding**: 100-200ms (validation + queuing)
- **Transcoding Processing**: 300-500ms (GPU encoding)
- **Packaging to CDN**: 100-200ms (segment creation + upload)
- **CDN to Viewer**: 200-500ms (edge delivery)
- **Total End-to-End**: <3 seconds (2.8s average)

### Throughput Metrics
- **Stream Ingestion**: 9M+ concurrent streams
- **Transcoding Capacity**: 54M+ quality variants
- **CDN Requests**: 100M+ requests/second
- **Chat Messages**: 1M+ messages/second peak
- **API Requests**: 10M+ requests/minute

### Error Handling
- **Stream Failures**: Automatic failover to backup ingestion
- **Transcoding Failures**: CPU fallback for GPU failures
- **CDN Failures**: Multi-CDN redundancy
- **Chat Failures**: Graceful degradation to view-only mode

This request flow architecture ensures Twitch maintains its position as the world's leading live streaming platform while delivering ultra-low latency and global scale.