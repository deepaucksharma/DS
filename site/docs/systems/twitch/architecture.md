# Twitch Complete Architecture - Live Streaming at Scale

## Production Overview

Twitch operates the world's largest live video platform, serving **140M+ monthly active users** and **15M+ daily active users** with **2.8B+ hours watched monthly**. The platform supports **9M+ active streamers** with ultra-low latency streaming and real-time chat.

### Core Infrastructure Metrics
- **Concurrent Viewers**: 15M+ peak
- **Stream Latency**: <3 seconds (Low Latency mode)
- **Chat Messages**: 1M+ messages/second peak
- **Video Quality**: Up to 1080p60 with dynamic bitrate
- **Global PoPs**: 100+ edge locations
- **CDN Bandwidth**: 40+ Tbps peak capacity

## Complete System Architecture

```mermaid
graph TB
    %% Define the four planes with Twitch-specific components

    subgraph EdgePlane[Edge Plane - Global Video Delivery]
        CDN[CloudFront CDN<br/>40+ Tbps capacity<br/>100+ PoPs worldwide]
        VideoEdge[Video Edge Servers<br/>Intel Xeon Scalable<br/>NVMe SSD cache]
        ChatEdge[Chat Edge Proxies<br/>WebSocket terminators<br/>1M+ concurrent connections]
        API_GW[API Gateway<br/>Kong Enterprise<br/>Rate limiting: 1000 req/min]
    end

    subgraph ServicePlane[Service Plane - Live Streaming Services]
        StreamIngestion[Stream Ingestion<br/>RTMP/WebRTC receivers<br/>c5n.9xlarge instances]
        Transcoding[Real-time Transcoding<br/>FFmpeg on c5n.18xlarge<br/>GPU: p3.16xlarge]
        ChatService[Chat Service<br/>Go microservices<br/>Distributed message routing]
        UserService[User Service<br/>Node.js + Redis<br/>40M+ user profiles]
        AuthService[Auth Service<br/>OAuth 2.0 + JWT<br/>Sub-second response]
        BitService[Bits & Monetization<br/>Payment processing<br/>Financial compliance]
        ModService[Moderation Service<br/>AutoMod + ML models<br/>Real-time filtering]
    end

    subgraph StatePlane[State Plane - Data Storage & Processing]
        VideoStorage[Video Storage<br/>S3 Glacier + S3 IA<br/>Exabytes of VODs]
        LiveCache[Live Stream Cache<br/>ElastiCache Redis<br/>r6g.16xlarge clusters]
        ChatDB[Chat Database<br/>DynamoDB + Kinesis<br/>100K+ writes/sec]
        UserDB[User Database<br/>PostgreSQL RDS<br/>db.r6g.12xlarge]
        MetricsDB[Metrics Database<br/>InfluxDB + Grafana<br/>1B+ data points/hour]
        SearchDB[Search Database<br/>Elasticsearch<br/>Stream/user discovery]
        CDNStorage[CDN Storage<br/>S3 + CloudFront<br/>Multi-region replication]
    end

    subgraph ControlPlane[Control Plane - Operations & Analytics]
        StreamMonitor[Stream Health Monitor<br/>Custom Go services<br/>Real-time alerts]
        ChatModerator[Chat Moderation<br/>ML-powered AutoMod<br/>99.5% accuracy]
        Analytics[Analytics Engine<br/>Apache Spark<br/>Viewer behavior analysis]
        Alerting[Alerting System<br/>PagerDuty + Slack<br/>30-second MTTR]
        Deployment[Deployment Pipeline<br/>Kubernetes + Helm<br/>Blue-green deployments]
        ConfigMgmt[Config Management<br/>etcd + Consul<br/>Feature flag system]
    end

    %% External connections
    Streamers[Streamers<br/>OBS Studio/XSplit<br/>RTMP/SRT protocols]
    Viewers[Viewers<br/>140M+ MAU<br/>Web/Mobile/TV apps]
    AWS[AWS Infrastructure<br/>Multi-AZ deployment<br/>99.99% SLA target]

    %% Data flow connections
    Streamers -->|RTMP Stream<br/>30 Mbps max| StreamIngestion
    StreamIngestion -->|Raw Video<br/>H.264/AV1| Transcoding
    Transcoding -->|Multi-bitrate<br/>HLS/DASH segments| VideoEdge
    VideoEdge -->|CDN delivery<br/><3s latency| CDN
    CDN -->|Video stream<br/>Adaptive bitrate| Viewers

    %% Chat flow
    Viewers -->|Chat messages<br/>WebSocket| ChatEdge
    ChatEdge -->|Message routing<br/>Redis pub/sub| ChatService
    ChatService -->|Moderation<br/>AutoMod API| ModService
    ChatService -->|Store messages<br/>Kinesis stream| ChatDB

    %% Authentication flow
    Viewers -->|Login/API<br/>OAuth 2.0| API_GW
    API_GW -->|Token validation<br/>JWT verify| AuthService
    AuthService -->|User lookup<br/>Sub-second| UserService

    %% Storage connections
    Transcoding -->|VOD segments<br/>S3 PUT| VideoStorage
    ChatService -->|Message history<br/>DynamoDB batch| ChatDB
    UserService -->|Profile data<br/>PostgreSQL| UserDB
    StreamIngestion -->|Stream metadata<br/>Real-time metrics| MetricsDB

    %% Control plane monitoring
    StreamIngestion -.->|Health metrics<br/>Prometheus| StreamMonitor
    ChatService -.->|Chat analytics<br/>Kafka streams| Analytics
    Transcoding -.->|Encoding metrics<br/>CloudWatch| Alerting
    CDN -.->|CDN metrics<br/>Real User Monitoring| Analytics

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1D4ED8,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:3px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:3px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:3px

    class CDN,VideoEdge,ChatEdge,API_GW edgeStyle
    class StreamIngestion,Transcoding,ChatService,UserService,AuthService,BitService,ModService serviceStyle
    class VideoStorage,LiveCache,ChatDB,UserDB,MetricsDB,SearchDB,CDNStorage stateStyle
    class StreamMonitor,ChatModerator,Analytics,Alerting,Deployment,ConfigMgmt controlStyle
```

## Infrastructure Specifications

### Video Processing Infrastructure
- **Stream Ingestion**: c5n.9xlarge instances (36 vCPUs, 96 GB RAM, 50 Gbps network)
- **Transcoding**: c5n.18xlarge + p3.16xlarge GPU instances
- **CDN**: CloudFront with 40+ Tbps global capacity
- **Storage**: S3 with Glacier for long-term VOD storage

### Real-time Chat Infrastructure
- **Chat Service**: Distributed Go microservices on c5.4xlarge
- **Message Routing**: Redis Cluster on r6g.16xlarge instances
- **WebSocket Termination**: HAProxy on c5n.large instances
- **Peak Capacity**: 1M+ concurrent chat connections

### Monetization Infrastructure
- **Bits Processing**: Financial-grade payment systems
- **Subscription Management**: Recurring billing with Stripe
- **Ad Serving**: Real-time ad insertion in video streams
- **Creator Payouts**: Automated financial processing

## Critical Performance Metrics

### Latency Requirements
- **Stream Latency**: <3 seconds (Low Latency mode), <15 seconds (standard)
- **Chat Latency**: <500ms message delivery
- **API Response**: <200ms for user operations
- **CDN Hit Ratio**: >95% for video segments

### Availability Targets
- **Stream Uptime**: 99.9% (8.7 hours downtime/year)
- **Chat Availability**: 99.95% (4.4 hours downtime/year)
- **API Availability**: 99.99% (52 minutes downtime/year)
- **CDN Availability**: 99.99% globally distributed

### Scale Metrics
- **Concurrent Streams**: 9M+ active at peak
- **Bandwidth**: 40+ Tbps peak video delivery
- **Chat Volume**: 1M+ messages/second
- **Storage**: Exabytes of video content

## Operational Excellence

### 24/7 Operations
- **NOC**: Global follow-the-sun support model
- **Incident Response**: <2 minutes first response
- **Escalation**: Automatic paging for P0 incidents
- **Recovery**: <15 minutes MTTR for stream outages

### Monitoring & Alerting
- **Stream Health**: Real-time encoder monitoring
- **CDN Performance**: Global edge server metrics
- **Chat Performance**: Message delivery tracking
- **User Experience**: Real User Monitoring (RUM)

## Cost Optimization

### Infrastructure Spend
- **CDN Costs**: $15M+/month for global video delivery
- **Compute**: $8M+/month for transcoding and services
- **Storage**: $3M+/month for VODs and live cache
- **Total Infrastructure**: $30M+/month at current scale

### Optimization Strategies
- **Adaptive Bitrate**: Reduces bandwidth by 30%
- **AI-based Encoding**: Improves compression by 20%
- **Edge Caching**: 95%+ cache hit ratio
- **Reserved Instances**: 60% discount on predictable workloads

This architecture supports Twitch's mission of building the world's most vibrant live streaming community while maintaining ultra-low latency and global scale.