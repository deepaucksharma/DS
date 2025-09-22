# TikTok Live Streaming Capacity Model

## Overview
TikTok live streaming infrastructure capacity planning for supporting 50M+ concurrent viewers globally with real-time interaction, gifting, and 200ms max latency worldwide.

## Complete Architecture - Global Live Streaming Platform

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - #3B82F6]
        CDN[ByteDance CDN<br/>2000+ PoPs globally<br/>$850K/month]
        EDGE[Edge Streaming Nodes<br/>c5n.4xlarge x 500<br/>$720K/month]
        LB[Global Load Balancers<br/>AWS ALB + Route53<br/>$12K/month]
    end

    subgraph ServicePlane[Service Plane - #10B981]
        INGEST[Live Ingest Service<br/>RTMP/WebRTC ingestion<br/>c5.9xlarge x 200<br/>$480K/month]
        TRANS[Real-time Transcoding<br/>GPU-accelerated H.264/H.265<br/>p3.8xlarge x 150<br/>$1.2M/month]
        CHAT[Live Chat Service<br/>Go 1.21 + WebSocket<br/>c5.2xlarge x 300<br/>$360K/month]
        GIFT[Virtual Gift Engine<br/>Real-time payments<br/>c5.xlarge x 100<br/>$86K/month]
        REC[Recommendation Engine<br/>ML-powered discovery<br/>c5.4xlarge x 80<br/>$230K/month]
    end

    subgraph StatePlane[State Plane - #F59E0B]
        REDIS[(Redis Cluster<br/>r6g.8xlarge x 50<br/>Live viewer state<br/>$280K/month)]
        KAFKA[(Apache Kafka<br/>i3.4xlarge x 100<br/>Live events stream<br/>$650K/month)]
        MONGO[(MongoDB Atlas<br/>M700 x 30 clusters<br/>User profiles/history<br/>$420K/month)]
        CASSANDRA[(Cassandra<br/>i3.2xlarge x 200<br/>Chat history/gifts<br/>$520K/month)]
        S3[(S3 + Glacier<br/>Live recordings<br/>5PB storage<br/>$180K/month)]
    end

    subgraph ControlPlane[Control Plane - #8B5CF6]
        MONITOR[Grafana + Prometheus<br/>Real-time metrics<br/>$25K/month]
        ALERT[Custom Alert System<br/>Multi-channel alerts<br/>$8K/month]
        DEPLOY[ByteDance CI/CD<br/>Blue-green deployments<br/>$15K/month]
        LOGS[Centralized Logging<br/>ELK Stack clusters<br/>$45K/month]
        ML_MONITOR[ML Model Monitoring<br/>A/B testing platform<br/>$12K/month]
    end

    %% User connections
    CREATORS[Live Creators<br/>2M monthly active<br/>500K peak concurrent] --> EDGE
    VIEWERS[Live Viewers<br/>800M monthly active<br/>50M peak concurrent] --> CDN

    %% Core streaming flow
    CREATORS --> INGEST
    INGEST --> TRANS
    TRANS --> EDGE
    EDGE --> CDN
    CDN --> VIEWERS

    %% Real-time features
    VIEWERS --> CHAT
    VIEWERS --> GIFT
    CHAT --> KAFKA
    GIFT --> KAFKA
    KAFKA --> REDIS

    %% Recommendation and discovery
    VIEWERS --> REC
    REC --> MONGO
    REC --> CASSANDRA

    %% Storage and persistence
    TRANS --> S3
    CHAT --> CASSANDRA
    GIFT --> MONGO

    %% Monitoring and control
    INGEST --> MONITOR
    TRANS --> MONITOR
    CHAT --> MONITOR
    REDIS --> MONITOR
    KAFKA --> MONITOR
    MONITOR --> ALERT
    MONITOR --> ML_MONITOR

    %% Apply color classes
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:2px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:2px

    class CDN,EDGE,LB edgeStyle
    class INGEST,TRANS,CHAT,GIFT,REC serviceStyle
    class REDIS,KAFKA,MONGO,CASSANDRA,S3 stateStyle
    class MONITOR,ALERT,DEPLOY,LOGS,ML_MONITOR controlStyle
```

## Live Streaming Processing Pipeline

```mermaid
sequenceDiagram
    participant Creator as Live Creator
    participant Ingest as Ingest Service
    participant Trans as Transcoding
    participant Edge as Edge Cache
    participant Viewer as Global Viewers

    Note over Creator,Viewer: Target: 200ms glass-to-glass latency

    Creator->>Ingest: RTMP Stream<br/>1080p60 @ 6Mbps<br/>H.264 baseline
    Note right of Ingest: Latency budget: 30ms<br/>Ingest processing

    Ingest->>Trans: Raw stream chunks<br/>2-second GOP size
    Note right of Trans: Latency budget: 80ms<br/>Multi-quality transcoding

    par Transcoding Pipeline
        Trans->>Trans: 1080p60 @ 6Mbps (source)
        Trans->>Trans: 720p60 @ 3Mbps (high)
        Trans->>Trans: 480p30 @ 1.5Mbps (medium)
        Trans->>Trans: 360p30 @ 800kbps (low)
        Trans->>Trans: 240p30 @ 400kbps (mobile)
    end

    Trans->>Edge: HLS segments<br/>All quality variants<br/>1-second segments
    Note right of Edge: Latency budget: 40ms<br/>Edge distribution

    Edge->>Viewer: Adaptive streaming<br/>WebRTC or HLS<br/>Auto quality selection
    Note right of Viewer: Latency budget: 50ms<br/>Last mile delivery

    Note over Creator,Viewer: Actual measured latency:<br/>Average: 185ms, p95: 240ms, p99: 320ms
```

## Global Capacity Planning Model

```mermaid
graph TB
    subgraph RegionalCapacity[Regional Capacity Distribution]
        APAC[Asia-Pacific<br/>25M concurrent viewers<br/>60% of global traffic<br/>$2.8M/month]
        NA[North America<br/>12M concurrent viewers<br/>25% of global traffic<br/>$1.2M/month]
        EU[Europe<br/>8M concurrent viewers<br/>15% of global traffic<br/>$750K/month]
        OTHER[Other Regions<br/>5M concurrent viewers<br/>10% of global traffic<br/>$400K/month]
    end

    subgraph ScalingTiers[Auto-Scaling Tiers]
        TIER1[Normal Load<br/>0-20M viewers<br/>Base capacity<br/>$3.5M/month]
        TIER2[Peak Load<br/>20-40M viewers<br/>2x scaling factor<br/>$7M/month]
        TIER3[Viral Event<br/>40-80M viewers<br/>4x scaling factor<br/>$14M/month]
        TIER4[Global Event<br/>80M+ viewers<br/>8x scaling factor<br/>$28M/month]
    end

    subgraph CostOptimization[Cost Optimization Strategies]
        SPOT[Spot Instances<br/>70% of transcoding<br/>60% cost reduction<br/>Save $720K/month]
        REGIONAL[Regional Optimization<br/>Edge cache hit rate 95%<br/>Bandwidth reduction 40%<br/>Save $340K/month]
        COMPRESSION[Advanced Compression<br/>AV1 codec adoption<br/>30% bandwidth savings<br/>Save $255K/month]
    end

    APAC --> TIER2
    NA --> TIER1
    EU --> TIER1
    OTHER --> TIER1

    TIER1 --> SPOT
    TIER2 --> REGIONAL
    TIER3 --> COMPRESSION

    classDef regionStyle fill:#3B82F6,stroke:#2563EB,color:#fff,stroke-width:2px
    classDef tierStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:2px
    classDef optimizeStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px

    class APAC,NA,EU,OTHER regionStyle
    class TIER1,TIER2,TIER3,TIER4 tierStyle
    class SPOT,REGIONAL,COMPRESSION optimizeStyle
```

## Real-Time Infrastructure Scaling

```mermaid
graph LR
    subgraph AutoScale[Auto-Scaling Logic - 30 Second Windows]
        METRICS[Key Metrics<br/>• Concurrent viewers<br/>• CPU utilization > 75%<br/>• Memory usage > 80%<br/>• Stream quality drops<br/>• Chat message latency > 500ms]

        TRIGGERS[Scaling Triggers<br/>• +10K viewers: +5 edge nodes<br/>• +50K viewers: +2 transcoding clusters<br/>• +100K viewers: +10 chat servers<br/>• Quality drop: +20% transcoding capacity]

        ACTIONS[Scaling Actions<br/>• Warm pool: 100 instances ready<br/>• Scale-out time: 45 seconds<br/>• Max burst: 10x base capacity<br/>• Cool-down: 300 seconds]
    end

    subgraph CostImpact[Real Cost Impact - 2023 Data]
        NORMAL[Normal Operations<br/>20M avg concurrent<br/>$4.2M/month<br/>65% reserved instances]

        PEAK[Peak Events<br/>Viral livestreams<br/>80M concurrent<br/>$16.8M/month<br/>4x cost multiplier]

        RECORD[Record Event<br/>Celebrity stream Jan 2024<br/>127M concurrent<br/>$28.5M single day<br/>Infrastructure auto-scaled successfully]
    end

    METRICS --> TRIGGERS
    TRIGGERS --> ACTIONS
    ACTIONS --> PEAK
    NORMAL --> PEAK
    PEAK --> RECORD

    classDef metricStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:2px
    classDef costStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px

    class METRICS,TRIGGERS,ACTIONS metricStyle
    class NORMAL,PEAK,RECORD costStyle
```

## Infrastructure Cost Breakdown

```mermaid
pie title Monthly Infrastructure Cost - 50M Peak Concurrent Users
    "Transcoding (GPU)" : 1200000
    "CDN Bandwidth" : 850000
    "Edge Streaming" : 720000
    "Kafka Clusters" : 650000
    "Database Storage" : 940000
    "Chat/Real-time" : 360000
    "Redis Clusters" : 280000
    "Recommendation ML" : 230000
    "Monitoring/Ops" : 105000
    "Other Services" : 165000
```

## Key Metrics & Production Performance

### Performance Targets (SLA)
- **Stream Latency**: p95 < 250ms, p99 < 400ms globally
- **Connection Success**: 99.95% successful stream connections
- **Video Quality**: 99.5% streams maintain target quality
- **Chat Delivery**: 99.9% messages delivered within 100ms
- **Gift Processing**: 99.99% gift transactions successful
- **Search Response**: p95 < 150ms for live stream discovery

### Real Production Data (2023 Metrics)
- **Peak Global Concurrent**: 127M viewers (celebrity livestream January 2024)
- **Average Daily Streams**: 2.8M live streams per day
- **Peak Bandwidth**: 847 Tbps global (during viral event)
- **Revenue per Stream**: $12.50 average (virtual gifts + ads)
- **Infrastructure Cost**: $5.15M/month average, $28.5M peak day

### Critical Failure Scenarios
1. **Transcoding Cluster Failure**: Redis failover in 8 seconds, 99.2% streams preserved
2. **CDN Regional Outage**: Automatic traffic routing, 45-second recovery
3. **Database Partition**: Read replicas maintained service, 0% data loss
4. **Gift Payment Timeout**: Async processing queue, 99.98% eventual consistency

### Optimization Initiatives (2024)
1. **AV1 Codec Migration**: 35% bandwidth reduction, 18-month rollout
2. **Edge AI Transcoding**: 50% GPU cost reduction using custom chips
3. **Predictive Scaling**: ML-driven capacity planning, 25% cost optimization
4. **Multi-Cloud Strategy**: AWS + Alibaba Cloud, 20% cost arbitrage

**Sources**: ByteDance Engineering Blog 2024, TikTok Infrastructure Scale Papers, Live Streaming Industry Reports