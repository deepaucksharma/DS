# Meta (Facebook) - Complete Architecture

## The Social Graph Empire at 3B+ Users

Meta operates one of the world's largest distributed systems, serving 3+ billion monthly active users across Facebook, Instagram, WhatsApp, and Messenger. This architecture powers everything from News Feed generation to real-time messaging, photo storage, and content delivery.

## Complete System Overview

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Blue #3B82F6]
        style EdgePlane fill:#3B82F6,stroke:#2563EB,color:#fff

        CDN[Meta CDN Network v4<br/>━━━━━<br/>200+ PoPs globally<br/>150 Tbps capacity<br/>p99: 35ms globally<br/>HTTP/3 QUIC enabled]

        EdgeCache[Haystack Edge Cache<br/>━━━━━<br/>Photo/video cache<br/>1M+ photos/sec<br/>95% cache hit rate<br/>Local SSD storage]

        WAF[Meta WAF v3.2<br/>━━━━━<br/>DDoS protection<br/>15M+ requests/sec<br/>ML-based detection<br/>Real-time blocking]
    end

    subgraph ServicePlane[Service Plane - Green #10B981]
        style ServicePlane fill:#10B981,stroke:#059669,color:#fff

        LoadBalancer[Katran Load Balancer<br/>━━━━━<br/>C++ XDP/eBPF<br/>100M+ packets/sec<br/>ECMP load balancing<br/>Health check automation]

        WebTier[HHVM/Hack v4.172<br/>━━━━━<br/>PHP 8.1 compatible<br/>JIT compilation<br/>2B+ requests/day<br/>Sub-10ms p99]

        GraphAPI[Graph API v18.0<br/>━━━━━<br/>GraphQL endpoint<br/>Rate limiting enabled<br/>10M+ RPS peak<br/>OAuth 2.0 auth]

        NewsFeed[News Feed Ranking<br/>━━━━━<br/>PyTorch 2.0 ML<br/>Real-time inference<br/>50K+ features<br/>Personalized ranking]

        Messaging[WhatsApp/Messenger<br/>━━━━━<br/>Erlang/C++ backend<br/>100B+ messages/day<br/>End-to-end encryption<br/>Signal protocol]

        VideoProcessing[Video Processing Pipeline<br/>━━━━━<br/>FFmpeg 5.1<br/>Transcoding cluster<br/>H.264/H.265/AV1<br/>4K+ uploads/sec]
    end

    subgraph StatePlane[State Plane - Orange #F59E0B]
        style StatePlane fill:#F59E0B,stroke:#D97706,color:#fff

        TAO[TAO Social Graph v7<br/>━━━━━<br/>Distributed cache/DB<br/>1 trillion objects<br/>Sub-ms p99 reads<br/>Graph query engine]

        MySQL[MySQL 8.0 Clusters<br/>━━━━━<br/>InnoDB storage engine<br/>10,000+ shards<br/>Multi-master setup<br/>Percona XtraDB]

        Haystack[Haystack Photo Store v5<br/>━━━━━<br/>Custom blob storage<br/>500 PB+ photos<br/>1M+ photos/sec write<br/>Erasure coding]

        F4[F4 Warm Storage v3<br/>━━━━━<br/>Reed-Solomon coding<br/>Exabyte scale<br/>Archive tier storage<br/>Geographic replication]

        Memcached[Memcached Clusters<br/>━━━━━<br/>28 TB+ total RAM<br/>1B+ operations/sec<br/>99.9% hit rate<br/>Consistent hashing]

        RocksDB[RocksDB v7.10<br/>━━━━━<br/>LSM-tree storage<br/>Hot data tier<br/>NVMe SSD backend<br/>Compression enabled]
    end

    subgraph ControlPlane[Control Plane - Red #8B5CF6]
        style ControlPlane fill:#8B5CF6,stroke:#7C3AED,color:#fff

        Scuba[Scuba Analytics v3<br/>━━━━━<br/>Real-time OLAP<br/>Trillions of rows<br/>Sub-second queries<br/>Columnar storage]

        Prophet[Prophet Forecasting<br/>━━━━━<br/>Time series analysis<br/>Capacity planning<br/>Trend detection<br/>R/Python libraries]

        Tupperware[Tupperware Container v4<br/>━━━━━<br/>Container orchestration<br/>Resource allocation<br/>Service mesh<br/>Auto-scaling]

        ServiceRouter[Service Router v2<br/>━━━━━<br/>Traffic management<br/>Circuit breakers<br/>Load shedding<br/>Canary deployments]

        Monitoring[Meta Monitoring v5<br/>━━━━━<br/>Metrics collection<br/>Alert management<br/>SLO tracking<br/>Distributed tracing]
    end

    %% Connections with real metrics
    CDN -->|"Global CDN<br/>p99: 35ms<br/>150 Tbps"| EdgeCache
    EdgeCache -->|"Cache hit: 95%<br/>p99: 10ms"| WAF
    WAF -->|"DDoS filtered<br/>15M+ req/sec"| LoadBalancer

    LoadBalancer -->|"Load balanced<br/>p99: 5ms"| WebTier
    WebTier -->|"Graph queries<br/>p99: 8ms"| GraphAPI
    GraphAPI -->|"Social graph<br/>1T objects"| TAO

    NewsFeed -->|"Ranking model<br/>p99: 100ms"| TAO
    NewsFeed -->|"ML inference<br/>50K features"| RocksDB

    Messaging -->|"Message storage<br/>100B/day"| TAO
    Messaging -->|"Media files"| Haystack

    VideoProcessing -->|"Video storage<br/>Exabyte scale"| F4
    VideoProcessing -->|"Metadata"| MySQL

    %% Data layer interactions
    TAO -->|"Backing store<br/>p99: 1ms"| MySQL
    TAO -->|"Cache layer<br/>99.9% hit"| Memcached

    WebTier -->|"Session cache<br/>p99: 0.5ms"| Memcached
    GraphAPI -->|"Hot data<br/>p99: 2ms"| RocksDB

    %% Photo/video serving
    EdgeCache -->|"Media serving<br/>1M photos/sec"| Haystack
    Haystack -->|"Archive tier<br/>cold storage"| F4

    %% Control plane monitoring
    WebTier -.->|"Metrics/logs<br/>1M/sec"| Scuba
    NewsFeed -.->|"Performance data"| Monitoring
    Messaging -.->|"Service metrics"| Prophet

    Tupperware -.->|"Container mgmt"| WebTier
    ServiceRouter -.->|"Traffic routing"| GraphAPI

    %% Apply 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,font-weight:bold
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,font-weight:bold
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,font-weight:bold
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,font-weight:bold

    class CDN,EdgeCache,WAF edgeStyle
    class LoadBalancer,WebTier,GraphAPI,NewsFeed,Messaging,VideoProcessing serviceStyle
    class TAO,MySQL,Haystack,F4,Memcached,RocksDB stateStyle
    class Scuba,Prophet,Tupperware,ServiceRouter,Monitoring controlStyle
```

## Global Infrastructure Scale

### Datacenter Footprint
- **Primary Regions**: 15+ global datacenters
- **Edge Locations**: 200+ Points of Presence (PoPs)
- **Subsea Cables**: 15+ owned submarine cables
- **Total Servers**: 2.5M+ servers globally
- **Power Consumption**: 5+ TWh annually

### Traffic Metrics (2024)
- **Daily Active Users**: 2.1B across all platforms
- **Photos Uploaded**: 350M+ per day
- **Messages Sent**: 100B+ per day (WhatsApp)
- **Video Hours**: 1B+ hours watched daily
- **API Requests**: 5B+ per day

## Core Technology Stack

### Computing Infrastructure
```mermaid
graph LR
    subgraph Compute[Compute Layer]
        HHVM[HHVM - PHP/Hack Runtime]
        PYTORCH[PyTorch - ML Framework]
        PRESTO[Presto - SQL Engine]
    end

    subgraph Storage[Storage Layer]
        TAO2[TAO - Social Graph]
        HAYSTACK2[Haystack - Photos]
        HIVE[Hive - Data Warehouse]
    end

    subgraph Network[Network Layer]
        EXPRESS[Express Backbone]
        TERRAGRAPH[Terragraph - Wireless]
        CONNECTIVITY[Internet.org]
    end

    %% Apply colors
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class HHVM,PYTORCH,PRESTO serviceStyle
    class TAO2,HAYSTACK2,HIVE stateStyle
    class EXPRESS,TERRAGRAPH,CONNECTIVITY edgeStyle
```

### Programming Languages & Frameworks
- **Hack**: Type-safe PHP variant (80% of codebase)
- **C++**: Performance-critical systems
- **Python**: ML/AI infrastructure
- **JavaScript/React**: Frontend (created by Meta)
- **Rust**: Security-critical components
- **Go**: Infrastructure tooling

## Revenue & Cost Metrics (2024)

### Financial Scale
- **Annual Revenue**: $134.9B (2023)
- **Infrastructure Spend**: $30B+ annually
- **R&D Investment**: $38B+ annually
- **Revenue per User**: ~$40 globally

### Cost Breakdown by Component
```mermaid
pie title Infrastructure Cost Distribution ($30B+/year)
    "Content Delivery (CDN)" : 35
    "Compute Infrastructure" : 25
    "Storage Systems" : 20
    "Network & Connectivity" : 10
    "AI/ML Training" : 10
```

## Security & Compliance

### Data Protection
- **Encryption**: AES-256 at rest, TLS 1.3 in transit
- **Key Management**: Hardware Security Modules (HSMs)
- **Access Controls**: Zero-trust architecture
- **Audit Logging**: Immutable audit trails

### Privacy Engineering
- **Data Minimization**: Automated PII detection
- **Consent Management**: Global privacy controls
- **Right to Deletion**: Automated data purging
- **Cross-border Transfers**: Regional data residency

## Innovation Highlights

### Open Source Contributions
- **React**: Frontend framework (50M+ weekly downloads)
- **PyTorch**: ML framework (adopted by OpenAI, Tesla)
- **Presto**: Distributed SQL engine
- **RocksDB**: Embedded database
- **GraphQL**: API query language

### Research Breakthroughs
- **TAO**: Distributed social graph store
- **Haystack**: Efficient photo storage
- **Prophet**: Time series forecasting
- **DeepFace**: Facial recognition AI
- **FAIR**: Fundamental AI Research

## Production Wisdom

### Key Learnings
1. **Social Graph Complexity**: Friendships create 6 degrees of separation globally
2. **Photo Storage Economics**: Optimization saves millions in storage costs
3. **Real-time Messaging**: WhatsApp handles 100B messages/day with <100ms latency
4. **ML at Scale**: Recommendation systems process 1PB+ data daily
5. **Global Regulations**: GDPR compliance requires architectural changes

### The October 2021 Outage Lesson
- **Duration**: 6 hours global outage
- **Root Cause**: BGP configuration error
- **Impact**: $60M revenue loss, $7B market cap drop
- **Fix**: Manual datacenter access to restore BGP
- **Prevention**: Enhanced change management, gradual rollouts

*"Building for 3 billion users means every architectural decision impacts global communication."*

**Sources**: Meta Engineering Blog, Meta Transparency Reports, SEC Filings 2024