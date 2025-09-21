# Dropbox Complete Architecture

## System Overview

Dropbox's complete architecture serves 700M+ registered users with exabytes of storage through their custom-built Magic Pocket infrastructure, delivering file sync with 99.9% uptime and sub-second sync latency.

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - CDN & Access]
        CDN[Akamai CDN<br/>TB/s Global Bandwidth<br/>300+ PoPs]
        LB[HAProxy Load Balancers<br/>m5.24xlarge<br/>100k conn/sec]
        WAF[Cloudflare WAF<br/>DDoS Protection<br/>Rate Limiting]
    end

    subgraph ServicePlane[Service Plane - Application Logic]
        API[API Gateway<br/>Django/Python<br/>c5.9xlarge × 500<br/>p99: 100ms]
        AUTH[Auth Service<br/>OAuth 2.0 + SAML<br/>c5.2xlarge × 50<br/>JWT tokens]
        SYNC[Sync Service<br/>Block-level Delta Sync<br/>c5.12xlarge × 200<br/>p99: 50ms]
        NOTIF[Notification Service<br/>Real-time Updates<br/>Long-polling + WebSocket<br/>c5.4xlarge × 100]
        SHARE[Sharing Service<br/>Team/Public Links<br/>Permissions Engine<br/>c5.4xlarge × 80]
        PREVIEW[Preview Service<br/>Thumbnail Generation<br/>Image/Video Processing<br/>c5.9xlarge × 150]
    end

    subgraph StatePlane[State Plane - Storage & Data]
        NUCLEUS[Nucleus Metadata Store<br/>Distributed Database<br/>100TB+ Metadata<br/>r5.24xlarge × 300]
        MAGIC[Magic Pocket Storage<br/>Custom Exabyte Storage<br/>90% Cost Reduction<br/>Custom Hardware]
        CACHE[Redis Cache Clusters<br/>r6g.8xlarge × 200<br/>99% Cache Hit Rate<br/>Sub-ms Access]
        MYSQL[MySQL Clusters<br/>User/Team Metadata<br/>db.r5.24xlarge × 50<br/>Multi-AZ Setup]
        SEARCH[ElasticSearch<br/>File Content Search<br/>m5.2xlarge × 100<br/>Billions of Files]
    end

    subgraph ControlPlane[Control Plane - Operations]
        MON[Monitoring Stack<br/>Prometheus + Grafana<br/>Custom Metrics<br/>c5.2xlarge × 20]
        LOG[Centralized Logging<br/>ELK Stack<br/>1PB+ Daily Logs<br/>i3.8xlarge × 50]
        DEPLOY[Deployment Pipeline<br/>Continuous Deployment<br/>10k+ Deploys/Month<br/>Blue-Green Strategy]
        ALERT[Alerting System<br/>PagerDuty Integration<br/>ML-based Anomaly Detection<br/>SLO Monitoring]
    end

    %% Client Connections
    WEB[Web Clients<br/>React SPA<br/>100M+ Monthly Active]
    MOBILE[Mobile Apps<br/>iOS/Android<br/>Native Apps<br/>500M+ Installs]
    DESKTOP[Desktop Clients<br/>Windows/Mac/Linux<br/>Smart Sync<br/>200M+ Installs]

    %% Traffic Flow
    WEB --> CDN
    MOBILE --> CDN
    DESKTOP --> CDN

    CDN --> WAF
    WAF --> LB
    LB --> API

    API --> AUTH
    API --> SYNC
    API --> SHARE
    API --> NOTIF
    API --> PREVIEW

    SYNC --> NUCLEUS
    SYNC --> MAGIC
    AUTH --> MYSQL
    SHARE --> MYSQL
    NOTIF --> CACHE
    PREVIEW --> MAGIC

    NUCLEUS --> CACHE
    API --> SEARCH

    %% Control Plane Monitoring
    API -.-> MON
    SYNC -.-> MON
    NUCLEUS -.-> MON
    MAGIC -.-> MON

    MON --> ALERT
    API -.-> LOG
    SYNC -.-> LOG

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:2px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:2px
    classDef clientStyle fill:#9900CC,stroke:#660099,color:#fff,stroke-width:2px

    class CDN,LB,WAF edgeStyle
    class API,AUTH,SYNC,NOTIF,SHARE,PREVIEW serviceStyle
    class NUCLEUS,MAGIC,CACHE,MYSQL,SEARCH stateStyle
    class MON,LOG,DEPLOY,ALERT controlStyle
    class WEB,MOBILE,DESKTOP clientStyle
```

## Key Architecture Metrics

| Component | Scale | Performance | Cost |
|-----------|-------|-------------|------|
| **Magic Pocket** | Exabytes stored | 90% cost reduction vs AWS | $500M+ annual savings |
| **Nucleus** | 100TB+ metadata | Sub-ms queries | Custom distributed DB |
| **Sync Engine** | Billions of files | Block-level delta sync | 95% bandwidth reduction |
| **Global CDN** | 300+ PoPs | Sub-second access | TB/s bandwidth |
| **API Gateway** | 700M+ users | p99: 100ms | 500× c5.9xlarge |

## Production Characteristics

### Scale Indicators
- **700M+ registered users** across all platforms
- **Exabytes of storage** in Magic Pocket infrastructure
- **Billions of files** synchronized daily
- **500M+ mobile app** installations
- **200M+ desktop clients** with Smart Sync

### Performance SLAs
- **99.9% uptime** with 4-minute monthly downtime budget
- **Sub-second sync latency** for file changes
- **p99: 100ms API response** times globally
- **95% bandwidth reduction** through block-level sync
- **99% cache hit rate** for metadata access

### Infrastructure Footprint
- **1000+ servers** for service plane applications
- **Custom Magic Pocket** hardware in 3 regions
- **300+ Redis cache** instances globally
- **50+ MySQL clusters** for metadata
- **Multi-AZ deployment** across AWS regions

## Failure Recovery
- **Automatic failover** for all service components
- **Multi-region replication** for Magic Pocket
- **Circuit breakers** prevent cascading failures
- **Graceful degradation** with offline mode
- **4-hour RTO** for major incidents

*Source: Dropbox Engineering Blog, Magic Pocket Technical Papers, Scale Conference Presentations*