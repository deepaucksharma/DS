# TikTok Storage Architecture

## Storage Architecture - "The Data Journey"

TikTok's storage architecture handles 50PB+ of video content with 150M+ daily uploads, serving 1B+ daily video views with global distribution and multi-tier storage optimization.

```mermaid
graph TB
    subgraph VideoIngestion[Video Ingestion Pipeline]
        UPLOAD[Video Upload<br/>150M+ files/day<br/>100TB+ new content]
        VALIDATE[Validation Service<br/>Format, size, duration<br/>p99: 500ms]
        TRANSCODE[Transcoding Pipeline<br/>FFmpeg clusters<br/>Multiple resolutions]
    end

    subgraph PrimaryStorage[Primary Storage - Hot Data]
        S3_HOT[AWS S3 Standard<br/>Recent videos (30 days)<br/>10PB storage<br/>$2.3M/month]
        HDFS_HOT[Hadoop HDFS<br/>On-premise hot storage<br/>15PB capacity<br/>$800K/month capex]
        REDIS_CACHE[Redis Clusters<br/>Video metadata cache<br/>100TB memory<br/>$1.2M/month]
    end

    subgraph WarmStorage[Warm Storage - Medium Access]
        S3_IA[AWS S3 Infrequent Access<br/>Videos 30-180 days<br/>15PB storage<br/>$1.1M/month]
        HDFS_WARM[HDFS Warm Tier<br/>Compressed storage<br/>20PB capacity<br/>$600K/month capex]
    end

    subgraph ColdStorage[Cold Storage - Archive]
        GLACIER[AWS Glacier<br/>Videos 180+ days<br/>25PB+ storage<br/>$250K/month]
        TAPE[LTO Tape Archive<br/>Compliance backup<br/>50PB+ capacity<br/>$100K/month]
    end

    subgraph GlobalCDN[Global CDN Distribution]
        BYTEPLUS[BytePlus CDN<br/>Primary distribution<br/>400+ PoPs<br/>$8M/month]
        CLOUDFRONT[AWS CloudFront<br/>Fallback CDN<br/>200+ PoPs<br/>$2M/month]
        EDGE_CACHE[Edge Caching<br/>Popular content<br/>90%+ hit rate<br/>500TB+ total]
    end

    subgraph MetadataStores[Metadata & Index Storage]
        MYSQL_VIDEO[MySQL Video DB<br/>Video metadata<br/>Sharded by video_id<br/>100M+ records]
        MYSQL_USER[MySQL User DB<br/>User data<br/>Sharded by user_id<br/>1B+ users]
        CASSANDRA[Cassandra Cluster<br/>Time-series analytics<br/>i3.16xlarge × 300<br/>10PB+ data]
        ELASTICSEARCH[Elasticsearch<br/>Search index<br/>Video content search<br/>r5.4xlarge × 100]
    end

    subgraph MLDataStorage[ML & Analytics Storage]
        FEATURE_STORE[Feature Store<br/>Redis + Cassandra<br/>Real-time features<br/>1TB+ active]
        TRAINING_DATA[Training Data<br/>HDFS + S3<br/>Historical interactions<br/>100PB+ total]
        MODEL_STORE[Model Storage<br/>S3 + Artifacts<br/>200+ ML models<br/>10TB+ models]
    end

    %% Data Flow Paths
    UPLOAD --> VALIDATE
    VALIDATE --> TRANSCODE
    TRANSCODE --> S3_HOT
    TRANSCODE --> HDFS_HOT
    TRANSCODE --> REDIS_CACHE

    %% Storage Lifecycle
    S3_HOT --> S3_IA
    S3_IA --> GLACIER
    HDFS_HOT --> HDFS_WARM
    HDFS_WARM --> TAPE

    %% CDN Distribution
    S3_HOT --> BYTEPLUS
    HDFS_HOT --> BYTEPLUS
    BYTEPLUS --> EDGE_CACHE
    S3_HOT --> CLOUDFRONT
    HDFS_HOT --> CLOUDFRONT

    %% Metadata Storage
    TRANSCODE --> MYSQL_VIDEO
    UPLOAD --> MYSQL_USER
    TRANSCODE --> CASSANDRA
    TRANSCODE --> ELASTICSEARCH

    %% ML Pipeline
    CASSANDRA --> FEATURE_STORE
    MYSQL_VIDEO --> TRAINING_DATA
    MYSQL_USER --> TRAINING_DATA
    TRAINING_DATA --> MODEL_STORE

    %% Cache Warming
    MYSQL_VIDEO --> REDIS_CACHE
    FEATURE_STORE --> REDIS_CACHE

    %% Apply storage-specific styling
    classDef hotStorage fill:#FF4444,stroke:#8B5CF6,color:#fff,stroke-width:3px
    classDef warmStorage fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef coldStorage fill:#4444FF,stroke:#0000CC,color:#fff,stroke-width:2px
    classDef cdnStorage fill:#10B981,stroke:#059669,color:#fff,stroke-width:2px
    classDef metadataStorage fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:2px
    classDef mlStorage fill:#00AAAA,stroke:#007777,color:#fff,stroke-width:2px

    class S3_HOT,HDFS_HOT,REDIS_CACHE hotStorage
    class S3_IA,HDFS_WARM warmStorage
    class GLACIER,TAPE coldStorage
    class BYTEPLUS,CLOUDFRONT,EDGE_CACHE cdnStorage
    class MYSQL_VIDEO,MYSQL_USER,CASSANDRA,ELASTICSEARCH metadataStorage
    class FEATURE_STORE,TRAINING_DATA,MODEL_STORE mlStorage
```

## Storage Tier Strategy

### Hot Storage (0-30 days) - 25PB
**Access Pattern**: High frequency, low latency required
- **AWS S3 Standard**: 10PB for global access
- **HDFS On-premise**: 15PB for ML pipeline access
- **SLA**: p99 < 10ms for metadata, p95 < 100ms for video
- **Cost**: $3.1M/month total

### Warm Storage (30-180 days) - 35PB
**Access Pattern**: Medium frequency, moderate latency acceptable
- **AWS S3 IA**: 15PB with 30s retrieval time
- **HDFS Warm**: 20PB compressed with async access
- **SLA**: p99 < 1s for retrieval
- **Cost**: $1.7M/month total

### Cold Storage (180+ days) - 75PB+
**Access Pattern**: Low frequency, high latency acceptable
- **AWS Glacier**: 25PB with 1-5min retrieval
- **LTO Tape**: 50PB+ for compliance and disaster recovery
- **SLA**: p99 < 5min for retrieval
- **Cost**: $350K/month total

## Global CDN Architecture

### Primary CDN: BytePlus (ByteDance's own)
- **Points of Presence**: 400+ globally
- **Cache Capacity**: 300TB+ per major PoP
- **Hit Rate**: 92% for videos, 98% for thumbnails
- **Geographic Coverage**:
  - Asia-Pacific: 180 PoPs
  - North America: 120 PoPs
  - Europe: 80 PoPs
  - Rest of World: 20 PoPs

### Fallback CDN: AWS CloudFront
- **Points of Presence**: 200+ globally
- **Usage**: 8% of total traffic (fallback + specific regions)
- **Integration**: Real-time failover in 10s
- **Cost**: $2M/month for redundancy

### Edge Caching Strategy
```
Popular Videos (Top 10%): 99% hit rate, 72hr TTL
Trending Videos: 95% hit rate, 24hr TTL
Regular Videos: 85% hit rate, 12hr TTL
Long-tail Videos: 60% hit rate, 6hr TTL
```

## Database Sharding & Consistency

### Video Metadata (MySQL)
**Sharding Strategy**: Hash-based on video_id
- **Shard Count**: 1,000 shards
- **Instance Type**: db.r6g.16xlarge
- **Replication**: Master-slave with 2 read replicas per shard
- **Consistency**: Strong consistency for writes, eventual for reads
- **Backup**: Point-in-time recovery, 7-day retention

### User Data (MySQL)
**Sharding Strategy**: Hash-based on user_id
- **Shard Count**: 500 shards
- **Cross-shard Queries**: Denormalized tables for common patterns
- **Hot Shard Handling**: Dynamic shard splitting for popular creators
- **Geographic Distribution**: Regional replicas for compliance

### Analytics Data (Cassandra)
**Partitioning Strategy**: Time-based + user_id
- **Partition Key**: (year_month, user_id)
- **Clustering Key**: timestamp
- **Retention**: 2 years online, archive to cold storage
- **Compaction**: Size-tiered for write-heavy workload
- **Replication Factor**: 3 with LOCAL_QUORUM

## Video Processing Pipeline

### 1. Upload Processing
```
Original Upload → Validation → Virus Scan → Metadata Extraction
                ↓
Multiple Format Transcoding:
- 240p (H.264): 500 Kbps
- 360p (H.264): 800 Kbps
- 480p (H.264): 1.2 Mbps
- 720p (H.264): 2.5 Mbps
- 1080p (H.264): 5 Mbps
- 1080p (H.265): 3 Mbps (newer devices)
```

### 2. Thumbnail Generation
- **Count**: 5 thumbnails per video at key moments
- **Formats**: JPEG (80% quality) + WebP (modern browsers)
- **Sizes**: 150x150, 300x300, 600x600 pixels
- **Processing Time**: p95 < 10s

### 3. Audio Processing
- **Extraction**: Separate audio track for music detection
- **Fingerprinting**: Copyright detection via acoustic fingerprinting
- **Compression**: AAC 128 Kbps for standard quality
- **Music Library**: Integration with licensed music catalog

## ML Data Storage Architecture

### Feature Store (Real-time)
**Technology**: Redis Cluster + Cassandra backup
- **Hot Features**: User activity last 24h (Redis)
- **Warm Features**: User activity last 30d (Cassandra)
- **Cold Features**: User activity 30d+ (HDFS)
- **Update Frequency**: Real-time for interactions, hourly for aggregates

### Training Data Pipeline
**Daily Volume**: 10TB+ of interaction data
- **Real-time Stream**: Kafka → Flink → Feature Store
- **Batch Processing**: Daily ETL jobs via Spark
- **Model Training**: Weekly full retrain, daily incremental
- **Data Retention**: 2 years for compliance, 5 years for research

### Model Artifact Storage
- **Model Versions**: 200+ active models
- **A/B Testing**: 10-20 model variants live simultaneously
- **Rollback Capability**: 30-day model version history
- **Distribution**: Automated deployment to 12 regions

## Storage Economics & Optimization

### Cost Breakdown (Monthly)
- **Hot Storage**: $3.1M (S3 + HDFS operations)
- **CDN Bandwidth**: $10M (primary + fallback)
- **Database Operations**: $2.5M (compute + storage)
- **Cold Storage**: $350K (archival + compliance)
- **Total Storage Costs**: $15.95M/month

### Optimization Strategies

#### 1. Intelligent Tiering
- **ML-Based Predictions**: Predict video popularity for tier placement
- **Cost Savings**: 40% reduction through optimal tier placement
- **Performance**: Maintain p99 < 100ms for 95% of requests

#### 2. Compression Optimization
- **H.265 Adoption**: 60% bandwidth reduction for supported devices
- **Progressive Download**: Load video segments based on watch likelihood
- **Dynamic Quality**: Adaptive bitrate based on network conditions

#### 3. Deduplication
- **Video-level**: Detect identical uploads (5% dedup rate)
- **Segment-level**: Reuse common video segments
- **Audio-level**: Deduplicate popular music tracks

## Disaster Recovery & Backup

### Geographic Replication
- **Primary Regions**: US-East, Asia-Pacific, Europe
- **Backup Regions**: US-West, Asia-Southeast, Europe-Central
- **Replication Lag**: 15 minutes for hot data, 4 hours for warm data
- **Recovery Time**: RTO 1 hour, RPO 15 minutes

### Data Protection
- **Video Content**: 3 copies minimum (primary + 2 backups)
- **Metadata**: Real-time replication across regions
- **User Data**: Encrypted at rest with region-specific keys
- **Compliance**: GDPR, CCPA data residency requirements

This storage architecture enables TikTok to handle massive scale while optimizing costs through intelligent tiering, maintaining global performance through strategic CDN placement, and ensuring data durability through comprehensive backup and replication strategies.