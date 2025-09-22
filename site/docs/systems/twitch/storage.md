# Twitch Storage Architecture - Video, VODs, and Clips at Scale

## Data Journey: From Live Stream to Permanent Archive

Twitch's storage architecture manages **exabytes of video content** with **2.8B+ hours watched monthly**, handling everything from live stream buffering to permanent VOD storage and user-generated clips.

### Storage Scale Metrics
- **Total Storage**: 100+ exabytes across all tiers
- **Live Stream Cache**: 50+ petabytes (Redis + SSD)
- **VOD Storage**: 90+ exabytes (S3 Glacier + Intelligent Tiering)
- **Clip Generation**: 1M+ clips created daily
- **Thumbnail Storage**: 500+ TB of preview images
- **Chat Archives**: 10+ TB daily message storage

## Complete Storage Architecture

```mermaid
graph TB
    subgraph LiveIngestion[Live Stream Ingestion Layer]
        StreamBuffer[Stream Buffer<br/>Redis Cluster<br/>r6g.16xlarge instances<br/>10GB RAM per stream]
        SegmentCache[Segment Cache<br/>NVMe SSD arrays<br/>i3en.24xlarge<br/>60TB local storage]
    end

    subgraph HotStorage[Hot Storage Tier - Active Content]
        LiveCache[Live Stream Cache<br/>ElastiCache Redis<br/>50+ TB capacity<br/>Sub-millisecond access]
        RecentVODs[Recent VODs<br/>S3 Standard<br/>30-day retention<br/>Instant access]
        PopularClips[Popular Clips<br/>S3 Standard<br/>High-frequency access<br/>CloudFront optimized]
        ChatRecent[Recent Chat<br/>DynamoDB<br/>On-demand billing<br/>500K+ writes/sec]
    end

    subgraph WarmStorage[Warm Storage Tier - Regular Access]
        VODArchive[VOD Archive<br/>S3 Intelligent-Tiering<br/>Auto-optimization<br/>90-day frequent access]
        ClipArchive[Clip Archive<br/>S3 Standard-IA<br/>30-day minimum<br/>Cost-optimized]
        Thumbnails[Thumbnail Store<br/>S3 Standard<br/>CloudFront CDN<br/>Global distribution]
        ChatHistory[Chat History<br/>DynamoDB<br/>Global tables<br/>7-day hot, 30-day warm]
    end

    subgraph ColdStorage[Cold Storage Tier - Long-term Archive]
        VODGlacier[VOD Glacier<br/>S3 Glacier Flexible<br/>1-5 minute retrieval<br/>90% cost savings]
        VODDeepArchive[VOD Deep Archive<br/>S3 Glacier Deep<br/>12-hour retrieval<br/>Compliance retention]
        ChatArchive[Chat Deep Archive<br/>S3 Glacier<br/>Compliance storage<br/>7-year retention]
        MetadataArchive[Metadata Archive<br/>RDS snapshots<br/>Point-in-time recovery<br/>Automated backups]
    end

    subgraph ProcessingStorage[Processing & Analytics Storage]
        TranscodeQueue[Transcode Queue<br/>SQS FIFO<br/>Dead letter queues<br/>Retry logic]
        AnalyticsData[Analytics Data<br/>S3 Data Lake<br/>Parquet format<br/>Athena queries]
        MLModels[ML Model Store<br/>S3 + EFS<br/>AutoMod models<br/>Version control]
        SearchIndex[Search Index<br/>Elasticsearch<br/>m6g.2xlarge nodes<br/>7-day retention]
    end

    subgraph MetadataStorage[Metadata & Configuration Storage]
        StreamMeta[Stream Metadata<br/>PostgreSQL RDS<br/>db.r6g.12xlarge<br/>Multi-AZ deployment]
        UserProfiles[User Profiles<br/>DynamoDB<br/>Global tables<br/>Eventually consistent]
        ConfigStore[Configuration<br/>Parameter Store<br/>Feature flags<br/>Real-time updates]
        GameMetadata[Game Metadata<br/>DocumentDB<br/>Game categories<br/>Real-time search]
    end

    %% Data flow connections - Live streaming
    StreamBuffer -->|2-second segments<br/>HLS/DASH| SegmentCache
    SegmentCache -->|Live delivery<br/>CDN cache| LiveCache
    StreamBuffer -->|Stream end<br/>Automatic processing| TranscodeQueue

    %% VOD creation flow
    TranscodeQueue -->|VOD generation<br/>Multiple qualities| RecentVODs
    RecentVODs -->|30-day lifecycle<br/>Auto-transition| VODArchive
    VODArchive -->|90-day lifecycle<br/>Intelligent tiering| VODGlacier
    VODGlacier -->|Compliance<br/>Long-term retention| VODDeepArchive

    %% Clip creation flow
    StreamBuffer -->|Clip request<br/>30-second window| PopularClips
    PopularClips -->|Aging policy<br/>30-day transition| ClipArchive

    %% Chat storage flow
    ChatRecent -->|Real-time writes<br/>Message indexing| ChatHistory
    ChatHistory -->|Compliance<br/>Automated archival| ChatArchive

    %% Thumbnail generation
    RecentVODs -->|Thumbnail extraction<br/>10-second intervals| Thumbnails

    %% Analytics pipeline
    StreamBuffer -.->|Stream metrics<br/>Real-time analytics| AnalyticsData
    ChatRecent -.->|Chat analytics<br/>Sentiment analysis| AnalyticsData
    RecentVODs -.->|View analytics<br/>Engagement metrics| AnalyticsData

    %% Metadata relationships
    StreamMeta -->|Stream lookup<br/>Relational data| StreamBuffer
    UserProfiles -->|User context<br/>Profile data| ChatRecent
    GameMetadata -->|Game classification<br/>Content tagging| SearchIndex

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1D4ED8,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:3px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:3px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:3px

    class LiveCache,SegmentCache edgeStyle
    class TranscodeQueue,SearchIndex serviceStyle
    class StreamBuffer,RecentVODs,PopularClips,ChatRecent,VODArchive,ClipArchive,Thumbnails,ChatHistory,VODGlacier,VODDeepArchive,ChatArchive,MetadataArchive,AnalyticsData,MLModels,StreamMeta,UserProfiles,ConfigStore,GameMetadata stateStyle
```

## Storage Tier Details

### Live Stream Storage Pipeline
```mermaid
graph LR
    subgraph StreamIngestion[Stream Ingestion - Edge Plane]
        RTMP[RTMP Input<br/>Raw stream data<br/>30 Mbps max]
        Buffer[Ingestion Buffer<br/>3-second window<br/>Redis Streams]
    end

    subgraph SegmentGeneration[Segment Generation - Service Plane]
        Segmenter[Stream Segmenter<br/>2-second HLS segments<br/>FFmpeg processing]
        Packager[Stream Packager<br/>Multi-quality output<br/>6 bitrate levels]
    end

    subgraph DistributionCache[Distribution Cache - State Plane]
        LocalSSD[Local NVMe Cache<br/>i3en.24xlarge<br/>60TB capacity]
        RedisCluster[Redis Cluster<br/>r6g.16xlarge<br/>10GB per stream]
        S3Buffer[S3 Buffer<br/>Temporary storage<br/>5-minute lifecycle]
    end

    RTMP -->|Live stream<br/>H.264 + AAC| Buffer
    Buffer -->|Raw segments<br/>2-second GOP| Segmenter
    Segmenter -->|HLS segments<br/>.ts files| Packager
    Packager -->|Multi-bitrate<br/>6 quality levels| LocalSSD
    LocalSSD -->|Cache warming<br/>Edge distribution| RedisCluster
    Packager -->|Backup storage<br/>Disaster recovery| S3Buffer

    classDef edgeStyle fill:#3B82F6,stroke:#1D4ED8,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class RTMP,Buffer edgeStyle
    class Segmenter,Packager serviceStyle
    class LocalSSD,RedisCluster,S3Buffer stateStyle
```

### VOD Storage Lifecycle
```mermaid
graph TB
    subgraph VODCreation[VOD Creation Pipeline]
        StreamEnd[Stream End Event<br/>Automatic trigger<br/>Lambda function]
        Concatenator[Segment Concatenator<br/>Join HLS segments<br/>FFmpeg processing]
        Transcoder[VOD Transcoder<br/>Multiple qualities<br/>H.264 + AV1 encoding]
    end

    subgraph StorageTiers[Storage Tier Progression]
        S3Standard[S3 Standard<br/>Immediate access<br/>0-30 days<br/>$0.023/GB/month]
        S3IA[S3 Intelligent-Tiering<br/>Auto-optimization<br/>30-90 days<br/>$0.0125/GB/month]
        S3Glacier[S3 Glacier Flexible<br/>1-5 min retrieval<br/>90+ days<br/>$0.004/GB/month]
        S3DeepArchive[S3 Glacier Deep<br/>12-hour retrieval<br/>Long-term storage<br/>$0.00099/GB/month]
    end

    subgraph AccessPatterns[Access Optimization]
        CloudFront[CloudFront CDN<br/>Global edge cache<br/>95%+ hit ratio]
        ElasticCache[ElastiCache<br/>Frequently accessed<br/>Sub-ms latency]
        Prewarming[Cache Pre-warming<br/>Predictive loading<br/>ML-based]
    end

    StreamEnd -->|Process trigger<br/>SQS message| Concatenator
    Concatenator -->|Complete stream<br/>Raw video file| Transcoder
    Transcoder -->|Multi-quality VOD<br/>6 bitrate levels| S3Standard

    S3Standard -->|30-day lifecycle<br/>Access pattern analysis| S3IA
    S3IA -->|90-day lifecycle<br/>Infrequent access| S3Glacier
    S3Glacier -->|Compliance requirement<br/>7-year retention| S3DeepArchive

    S3Standard -->|Popular content<br/>High access frequency| CloudFront
    S3Standard -->|Hot content<br/>Recent uploads| ElasticCache
    S3IA -.->|Predictive loading<br/>ML recommendations| Prewarming

    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class Concatenator,Transcoder serviceStyle
    class S3Standard,S3IA,S3Glacier,S3DeepArchive,ElasticCache stateStyle
    class CloudFront,PreWarming controlStyle
```

## Chat Storage Architecture

### Real-time Chat Storage
```mermaid
graph TB
    subgraph ChatIngestion[Chat Message Ingestion]
        WebSocket[WebSocket Input<br/>1M+ concurrent<br/>Real-time messages]
        IRCProcessor[IRC Processor<br/>Message validation<br/>Rate limiting]
        AutoMod[AutoMod Filter<br/>ML text analysis<br/>Spam detection]
    end

    subgraph ChatStorage[Chat Storage Tiers]
        DynamoHot[DynamoDB Hot<br/>Recent messages<br/>500K+ writes/sec<br/>Sub-ms reads]
        DynamoWarm[DynamoDB Warm<br/>Message history<br/>7-day retention<br/>Global tables]
        S3Archive[S3 Chat Archive<br/>Compliance storage<br/>Parquet format<br/>Cost-optimized]
    end

    subgraph ChatIndexing[Chat Search & Analytics]
        ElasticSearch[Elasticsearch<br/>Message search<br/>Real-time indexing<br/>7-day window]
        AnalyticsStream[Kinesis Analytics<br/>Real-time metrics<br/>Sentiment analysis<br/>Trend detection]
    end

    WebSocket -->|Raw messages<br/>JSON format| IRCProcessor
    IRCProcessor -->|Validated messages<br/>User context| AutoMod
    AutoMod -->|Approved messages<br/>Clean content| DynamoHot

    DynamoHot -->|Message aging<br/>7-day lifecycle| DynamoWarm
    DynamoWarm -->|Compliance archive<br/>30-day lifecycle| S3Archive

    DynamoHot -->|Real-time indexing<br/>Search optimization| ElasticSearch
    DynamoHot -->|Stream processing<br/>Analytics pipeline| AnalyticsStream

    classDef edgeStyle fill:#3B82F6,stroke:#1D4ED8,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class WebSocket edgeStyle
    class IRCProcessor,AutoMod,ElasticSearch,AnalyticsStream serviceStyle
    class DynamoHot,DynamoWarm,S3Archive stateStyle
```

## Clip Storage System

### User-Generated Clips
```mermaid
graph LR
    subgraph ClipCreation[Clip Creation Process]
        UserRequest[User Clip Request<br/>30-second window<br/>Real-time selection]
        ClipExtractor[Clip Extractor<br/>Segment analysis<br/>Keyframe alignment]
        ClipProcessor[Clip Processor<br/>Video encoding<br/>Multiple qualities]
    end

    subgraph ClipStorage[Clip Storage Management]
        ClipHot[S3 Standard<br/>Popular clips<br/>High access<br/>CloudFront cache]
        ClipWarm[S3 Standard-IA<br/>Moderate access<br/>30-day minimum<br/>Cost transition]
        ClipCold[S3 Glacier<br/>Archive clips<br/>Long-term storage<br/>Retrieval on demand]
    end

    subgraph ClipMetadata[Clip Metadata]
        ClipDB[PostgreSQL<br/>Clip metadata<br/>Creator info<br/>View counts]
        ClipSearch[Elasticsearch<br/>Clip discovery<br/>Tag search<br/>Content indexing]
        ClipThumbs[Thumbnail Store<br/>S3 Standard<br/>Preview images<br/>CloudFront CDN]
    end

    UserRequest -->|Clip timestamp<br/>30-second window| ClipExtractor
    ClipExtractor -->|Raw video segment<br/>Keyframe bounded| ClipProcessor
    ClipProcessor -->|Encoded clip<br/>Multiple qualities| ClipHot

    ClipHot -->|Access pattern<br/>30-day analysis| ClipWarm
    ClipWarm -->|Long-term storage<br/>Archive policy| ClipCold

    ClipProcessor -->|Metadata creation<br/>Clip information| ClipDB
    ClipDB -->|Search indexing<br/>Content discovery| ClipSearch
    ClipProcessor -->|Thumbnail generation<br/>Preview images| ClipThumbs

    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class ClipExtractor,ClipProcessor serviceStyle
    class ClipHot,ClipWarm,ClipCold,ClipDB,ClipSearch,ClipThumbs stateStyle
```

## Storage Performance Metrics

### Throughput Specifications
- **Live Stream Writes**: 100+ GB/second during peak
- **VOD Reads**: 40+ Tbps global CDN delivery
- **Chat Writes**: 500K+ messages/second to DynamoDB
- **Clip Creation**: 1M+ clips generated daily
- **Thumbnail Generation**: 10M+ images created daily

### Latency Requirements
- **Live Stream Access**: <50ms from cache
- **VOD Start Time**: <2 seconds (recent content)
- **Chat Message Retrieval**: <100ms for recent messages
- **Clip Access**: <500ms for popular clips
- **Search Results**: <200ms for content discovery

### Durability & Availability
- **Live Stream Buffer**: 99.9% availability (Redis Cluster)
- **VOD Storage**: 99.999999999% durability (S3)
- **Chat Storage**: 99.99% availability (DynamoDB)
- **CDN Delivery**: 99.9% global availability
- **Backup Strategy**: Multi-region replication

## Cost Optimization Strategies

### Storage Cost Breakdown
- **S3 Standard**: $8M+/month (hot content, recent VODs)
- **S3 Intelligent-Tiering**: $12M+/month (automatic optimization)
- **S3 Glacier**: $2M+/month (archive content)
- **DynamoDB**: $3M+/month (chat and metadata)
- **ElastiCache**: $1M+/month (live stream cache)
- **CloudFront**: $15M+/month (global CDN delivery)

### Optimization Techniques
- **Intelligent Tiering**: Automatic cost optimization saves 40%
- **Lifecycle Policies**: Automated transitions reduce storage costs
- **Compression**: AV1 encoding reduces storage by 30%
- **Deduplication**: Identical segment detection saves 15%
- **Predictive Caching**: ML-based pre-warming improves hit ratios

## Data Governance & Compliance

### Retention Policies
- **Live Stream Segments**: 5 minutes (disaster recovery only)
- **VODs**: 60 days (creator control), 7 years (compliance)
- **Chat Messages**: 30 days (active), 7 years (archive)
- **User Data**: Per GDPR requirements
- **Analytics Data**: 13 months (business intelligence)

### Security Measures
- **Encryption at Rest**: AES-256 for all storage tiers
- **Encryption in Transit**: TLS 1.3 for all data transfers
- **Access Control**: IAM policies with least privilege
- **Audit Logging**: CloudTrail for all storage operations
- **Data Classification**: Automated PII detection and protection

This storage architecture enables Twitch to handle massive scale while maintaining performance, cost efficiency, and regulatory compliance across its global platform.