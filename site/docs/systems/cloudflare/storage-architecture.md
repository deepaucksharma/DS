# Cloudflare Storage Architecture - "The Edge Data Journey"

## Overview

Cloudflare's storage architecture is designed for edge computing at global scale, featuring multiple storage systems optimized for different consistency and performance requirements. The architecture includes R2 object storage, Workers KV, Durable Objects, and a sophisticated caching hierarchy.

## Complete Storage Architecture

```mermaid
graph TB
    subgraph "Edge Plane - Data Access Layer #0066CC"
        subgraph "285+ Global PoPs"
            CACHE_L1[L1 Cache<br/>RAM: 32GB/server<br/>Latency: 0.1ms]
            CACHE_L2[L2 Cache<br/>SSD: 100TB/PoP<br/>Latency: 1-5ms]
            WORKER_MEM[Workers Memory<br/>128MB/isolate<br/>V8 heap]
        end

        subgraph "Edge Storage"
            DURABLE_EDGE[Durable Objects<br/>SQLite at Edge<br/>Strong consistency]
            KV_EDGE[KV Cache<br/>Local copies<br/>Eventually consistent]
        end
    end

    subgraph "Service Plane - Storage Services #00AA00"
        subgraph "Workers Storage APIs"
            KV_API[Workers KV API<br/>REST + JavaScript]
            R2_API[R2 S3-Compatible API<br/>GetObject/PutObject]
            DURABLE_API[Durable Objects API<br/>WebSocket + HTTP]
        end

        subgraph "Data Processing"
            ANALYTICS_PROC[Analytics Processing<br/>Stream processing]
            COMPRESS[Compression Service<br/>Brotli/Gzip/LZ4]
            ENCRYPT[Encryption Service<br/>AES-256-GCM]
        end
    end

    subgraph "State Plane - Persistent Storage #FF8800"
        subgraph "R2 Object Storage"
            R2_GLOBAL[R2 Global Storage<br/>Multi-region replication<br/>99.999999999% durability]
            R2_METADATA[R2 Metadata Store<br/>Object index<br/>Strong consistency]
            R2_LIFECYCLE[R2 Lifecycle<br/>Auto-tiering<br/>Deletion policies]
        end

        subgraph "Workers KV Global"
            KV_GLOBAL[KV Global Store<br/>400+ edge locations<br/>Eventually consistent]
            KV_REPLICATION[KV Replication<br/>60s propagation<br/>Anti-entropy]
        end

        subgraph "Durable Objects Global"
            DO_PERSISTENCE[DO Persistent Storage<br/>SQLite + WAL<br/>Automatic snapshots]
            DO_MIGRATION[DO Migration System<br/>Live object movement<br/>Zero-downtime]
        end

        subgraph "Analytics Storage"
            CLICKHOUSE[ClickHouse Cluster<br/>Time-series data<br/>100TB+ daily]
            LOGS_STORAGE[Log Storage<br/>Compressed archives<br/>90-day retention]
        end
    end

    subgraph "Control Plane - Storage Management #CC0000"
        subgraph "Replication Control"
            REPLICA_MGR[Replication Manager<br/>Multi-region coordination]
            CONSISTENCY[Consistency Manager<br/>Conflict resolution]
            BACKUP[Backup Controller<br/>Point-in-time recovery]
        end

        subgraph "Performance Monitoring"
            STORAGE_METRICS[Storage Metrics<br/>Latency/Throughput]
            QUOTA_MGR[Quota Management<br/>Per-account limits]
            HEALTH_CHECK[Health Monitoring<br/>Storage node status]
        end
    end

    %% Data Flow Connections
    WORKER_MEM --> KV_API
    WORKER_MEM --> R2_API
    WORKER_MEM --> DURABLE_API

    KV_API --> KV_EDGE
    KV_EDGE --> KV_GLOBAL
    KV_GLOBAL --> KV_REPLICATION

    R2_API --> R2_GLOBAL
    R2_GLOBAL --> R2_METADATA
    R2_GLOBAL --> R2_LIFECYCLE

    DURABLE_API --> DURABLE_EDGE
    DURABLE_EDGE --> DO_PERSISTENCE
    DO_PERSISTENCE --> DO_MIGRATION

    CACHE_L1 --> CACHE_L2
    CACHE_L2 --> R2_GLOBAL

    ANALYTICS_PROC --> CLICKHOUSE
    CLICKHOUSE --> LOGS_STORAGE

    %% Control Connections
    REPLICA_MGR --> KV_REPLICATION
    REPLICA_MGR --> R2_GLOBAL
    CONSISTENCY --> DO_PERSISTENCE
    BACKUP --> R2_GLOBAL

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class CACHE_L1,CACHE_L2,WORKER_MEM,DURABLE_EDGE,KV_EDGE edgeStyle
    class KV_API,R2_API,DURABLE_API,ANALYTICS_PROC,COMPRESS,ENCRYPT serviceStyle
    class R2_GLOBAL,R2_METADATA,R2_LIFECYCLE,KV_GLOBAL,KV_REPLICATION,DO_PERSISTENCE,DO_MIGRATION,CLICKHOUSE,LOGS_STORAGE stateStyle
    class REPLICA_MGR,CONSISTENCY,BACKUP,STORAGE_METRICS,QUOTA_MGR,HEALTH_CHECK controlStyle
```

## Storage System Deep Dive

### 1. R2 Object Storage

```mermaid
graph TB
    subgraph "R2 Architecture"
        CLIENT[Client Applications] --> R2_GATEWAY[R2 Gateway<br/>S3-Compatible API]
        R2_GATEWAY --> AUTH[Authentication<br/>API Keys/IAM]
        AUTH --> BUCKET_MGR[Bucket Manager<br/>Namespace isolation]

        BUCKET_MGR --> METADATA[Metadata Store<br/>Object index<br/>Strong consistency]
        BUCKET_MGR --> BLOB_STORE[Blob Storage<br/>Multi-region<br/>Erasure coding]

        METADATA --> META_REPLICA[Metadata Replicas<br/>3+ regions<br/>Consensus protocol]
        BLOB_STORE --> BLOB_REPLICA[Blob Replicas<br/>Multi-region<br/>Reed-Solomon]

        BLOB_STORE --> LIFECYCLE[Lifecycle Management<br/>Auto-tiering<br/>Deletion policies]
        LIFECYCLE --> GLACIER[Cold Storage<br/>Archive tier<br/>Lower cost]
    end

    %% Apply colors
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff

    class CLIENT,R2_GATEWAY,AUTH,BUCKET_MGR serviceStyle
    class METADATA,BLOB_STORE,META_REPLICA,BLOB_REPLICA,LIFECYCLE,GLACIER stateStyle
```

**R2 Specifications:**
- **Durability**: 99.999999999% (11 9s)
- **Availability**: 99.9% SLA
- **Max Object Size**: 5TB
- **API Compatibility**: S3-compatible
- **Pricing**: $0.015/GB/month, no egress fees

### 2. Workers KV Store

```mermaid
graph TB
    subgraph "Workers KV Architecture"
        WORKER[Workers Runtime] --> KV_CLIENT[KV Client API<br/>JavaScript bindings]
        KV_CLIENT --> KV_GATEWAY[KV Gateway<br/>Load balancing]

        KV_GATEWAY --> LOCAL_CACHE[Local PoP Cache<br/>Fast reads<br/>1-5ms latency]
        KV_GATEWAY --> REGIONAL[Regional Store<br/>Strong consistency<br/>Write coordination]

        REGIONAL --> GLOBAL_STORE[Global KV Store<br/>Distributed hash table<br/>Eventually consistent]
        GLOBAL_STORE --> REPLICATION[Anti-Entropy Replication<br/>60s propagation<br/>400+ locations]

        REPLICATION --> CONFLICT[Conflict Resolution<br/>Last-write-wins<br/>Vector clocks]
    end

    %% Apply colors
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class WORKER,KV_CLIENT,KV_GATEWAY serviceStyle
    class LOCAL_CACHE,REGIONAL,GLOBAL_STORE,REPLICATION,CONFLICT stateStyle
```

**KV Performance:**
- **Read Latency**: 1-5ms from edge
- **Write Latency**: 50-200ms (global propagation)
- **Consistency**: Eventually consistent
- **Storage Limit**: 25MB per key, 1GB per namespace

### 3. Durable Objects

```mermaid
graph TB
    subgraph "Durable Objects Architecture"
        WORKER_REQ[Workers Request] --> DO_RUNTIME[DO Runtime<br/>V8 Isolate + State]
        DO_RUNTIME --> SQLITE[SQLite Instance<br/>In-memory + WAL<br/>ACID transactions]

        SQLITE --> PERSISTENCE[Persistent Storage<br/>Local SSD<br/>Automatic snapshots]
        PERSISTENCE --> BACKUP[Backup System<br/>Point-in-time recovery<br/>Cross-region replication]

        DO_RUNTIME --> MIGRATION[Live Migration<br/>Zero-downtime movement<br/>State transfer]
        MIGRATION --> LOAD_BALANCER[Load-Based Migration<br/>Automatic optimization]

        SQLITE --> WEBSOCKET[WebSocket Support<br/>Persistent connections<br/>Real-time state]
    end

    %% Apply colors
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class WORKER_REQ,DO_RUNTIME,MIGRATION,LOAD_BALANCER,WEBSOCKET serviceStyle
    class SQLITE,PERSISTENCE,BACKUP stateStyle
```

**Durable Objects Features:**
- **Consistency**: Strong consistency per object
- **State**: Persistent JavaScript heap + SQLite
- **Isolation**: One object instance globally
- **Migration**: Live migration with zero downtime

### 4. Analytics Data Pipeline

```mermaid
graph TB
    subgraph "Analytics Architecture"
        REQUESTS[50M+ requests/sec] --> SAMPLING[Smart Sampling<br/>1% to 100%<br/>Adaptive rates]
        SAMPLING --> PIPELINE[Stream Processing<br/>Real-time aggregation]

        PIPELINE --> CLICKHOUSE[ClickHouse Cluster<br/>100TB+ daily<br/>Columnar storage]
        CLICKHOUSE --> RETENTION[Data Retention<br/>90 days standard<br/>Configurable]

        PIPELINE --> REAL_TIME[Real-time Analytics<br/>Sub-second queries<br/>Dashboard updates]
        CLICKHOUSE --> HISTORICAL[Historical Analytics<br/>Long-term trends<br/>Data warehousing]

        CLICKHOUSE --> EXPORT[Data Export<br/>Customer APIs<br/>Third-party integration]
    end

    %% Apply colors
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff

    class REQUESTS,SAMPLING,PIPELINE,REAL_TIME,EXPORT serviceStyle
    class CLICKHOUSE,RETENTION,HISTORICAL stateStyle
```

## Storage Performance Metrics

### Latency Characteristics
```mermaid
graph LR
    subgraph "Read Latency by Storage Type"
        L1[L1 Cache<br/>0.1ms<br/>RAM access]
        L2[L2 Cache<br/>1-5ms<br/>SSD access]
        KV[Workers KV<br/>1-5ms<br/>Edge read]
        R2[R2 Storage<br/>10-50ms<br/>Regional read]
        DO[Durable Objects<br/>1-10ms<br/>SQLite read]
    end

    %% Performance indicators
    L1 -.->|Fastest| L2
    L2 -.->|Fast| KV
    KV -.->|Medium| DO
    DO -.->|Medium| R2

    %% Apply colors
    classDef fastStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef mediumStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef slowStyle fill:#CC0000,stroke:#990000,color:#fff

    class L1,L2 fastStyle
    class KV,DO mediumStyle
    class R2 slowStyle
```

### Consistency Models
- **Strong Consistency**: Durable Objects, R2 metadata
- **Eventually Consistent**: Workers KV (60s propagation)
- **Cache Consistency**: TTL-based with purge capabilities
- **Cross-Region**: Async replication with conflict resolution

### Storage Limits and Quotas
- **Workers KV**: 1GB per namespace, 25MB per key
- **R2 Storage**: Unlimited, 5TB max object size
- **Durable Objects**: 128MB heap, unlimited SQLite storage
- **Cache Storage**: 100TB SSD per PoP

## Data Durability and Backup

### Backup Strategies
```mermaid
graph TB
    subgraph "Backup and Recovery"
        PRIMARY[Primary Storage] --> SYNC_REPLICA[Synchronous Replicas<br/>Same region<br/>0 RPO]
        PRIMARY --> ASYNC_REPLICA[Asynchronous Replicas<br/>Cross-region<br/><60s RPO]

        SYNC_REPLICA --> SNAPSHOT[Automated Snapshots<br/>Hourly/Daily<br/>Point-in-time recovery]
        ASYNC_REPLICA --> ARCHIVE[Long-term Archive<br/>90-day retention<br/>Compliance storage]

        SNAPSHOT --> RESTORE[Restore Service<br/>Self-service<br/>API-driven]
        ARCHIVE --> COMPLIANCE[Compliance Export<br/>GDPR/CCPA<br/>Data sovereignty]
    end

    %% Apply colors
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class PRIMARY,SYNC_REPLICA,ASYNC_REPLICA,SNAPSHOT,ARCHIVE stateStyle
    class RESTORE,COMPLIANCE controlStyle
```

### Recovery Time Objectives
- **Cache Recovery**: Immediate (traffic rerouting)
- **KV Recovery**: <5 minutes (replica promotion)
- **R2 Recovery**: <15 minutes (metadata reconstruction)
- **Durable Objects**: <30 seconds (migration to healthy node)

This storage architecture provides the foundation for Cloudflare's edge computing platform, delivering sub-10ms data access globally while maintaining enterprise-grade durability and consistency guarantees.