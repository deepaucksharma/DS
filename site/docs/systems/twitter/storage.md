# Twitter/X Storage Architecture

## Overview
Twitter/X's storage architecture handles 500M+ tweets daily, billions of social connections, and petabytes of media content. The system uses Manhattan (distributed database), FlockDB (social graph), and specialized storage systems for different data patterns.

## Complete Storage Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Data Access Layer]
        API[API Gateway<br/>Finagle framework<br/>Request routing<br/>Authentication]
        CACHE_PROXY[Cache Proxy<br/>Intelligent caching<br/>Hot data routing<br/>Cache warming]
    end

    subgraph ServicePlane[Service Plane - Data Services]
        subgraph ReadServices[Read Services]
            TIMELINE_READ[Timeline Read Service<br/>Manhattan client<br/>Cache-first reads<br/>Fanout optimization]
            TWEET_READ[Tweet Read Service<br/>Manhattan client<br/>Content hydration<br/>Media resolution]
            GRAPH_READ[Graph Read Service<br/>FlockDB client<br/>Social relationships<br/>Following/follower queries]
            SEARCH_READ[Search Read Service<br/>Lucene client<br/>Real-time indexing<br/>Full-text search]
        end

        subgraph WriteServices[Write Services]
            TWEET_WRITE[Tweet Write Service<br/>Manhattan client<br/>Snowflake ID generation<br/>Atomic operations]
            GRAPH_WRITE[Graph Write Service<br/>FlockDB client<br/>Relationship updates<br/>Bi-directional edges]
            MEDIA_WRITE[Media Write Service<br/>Blobstore client<br/>Upload processing<br/>Format conversion]
        end
    end

    subgraph StatePlane[State Plane - Storage Systems]
        subgraph PrimaryStorage[Primary Storage - Source of Truth]
            MANHATTAN[Manhattan Database<br/>Distributed NoSQL<br/>Multi-tenant storage<br/>1000+ TB<br/>Strong consistency]
            MYSQL[MySQL Clusters<br/>Relational data<br/>User accounts<br/>Financial data<br/>ACID compliance]
        end

        subgraph GraphStorage[Social Graph Storage]
            FLOCKDB[FlockDB<br/>Distributed graph database<br/>Social relationships<br/>Billions of edges<br/>High write throughput]
            GIZMODUCK[Gizmoduck<br/>User identity service<br/>Profile management<br/>Authentication data<br/>Privacy settings]
        end

        subgraph MediaStorage[Media Storage]
            BLOBSTORE[Blobstore<br/>Distributed object storage<br/>Photos, videos, GIFs<br/>2+ PB capacity<br/>Multi-region replication]
            TWIMG[twimg.com CDN<br/>Global media delivery<br/>Image optimization<br/>Video transcoding<br/>Format adaptation]
        end

        subgraph SearchStorage[Search & Analytics Storage]
            LUCENE[Lucene Indexes<br/>Real-time search<br/>Tweet content indexing<br/>150+ TB<br/>Distributed shards]
            CASSANDRA[Cassandra<br/>Time-series data<br/>Analytics storage<br/>Trending calculations<br/>300+ TB]
            DRUID[Apache Druid<br/>Real-time analytics<br/>OLAP queries<br/>Dashboard data<br/>Sub-second response]
        end

        subgraph CacheLayers[Cache Layers]
            MEMCACHED[Memcached<br/>Hot data cache<br/>Timeline fragments<br/>User sessions<br/>500+ GB]
            REDIS[Redis Clusters<br/>Real-time cache<br/>Trending data<br/>Counters & sets<br/>200+ GB]
        end
    end

    subgraph ControlPlane[Control Plane - Data Management]
        subgraph ReplicationLayer[Replication Layer]
            REPLICATOR[Manhattan Replicator<br/>Cross-region sync<br/>Async replication<br/>Conflict resolution]
            BACKUP_SERVICE[Backup Service<br/>Automated backups<br/>Point-in-time recovery<br/>S3 archival]
        end

        subgraph StreamingLayer[Streaming Layer]
            KAFKA[Apache Kafka<br/>Change data capture<br/>Event streaming<br/>100B+ events/day<br/>Real-time processing]
            HERON[Heron Topology<br/>Stream processing<br/>Real-time aggregations<br/>Low-latency computation]
        end

        subgraph BatchProcessing[Batch Processing]
            HADOOP[Hadoop Clusters<br/>Batch analytics<br/>100+ PB storage<br/>MapReduce jobs<br/>Historical processing]
            VERTICA[Vertica<br/>Columnar analytics<br/>Business intelligence<br/>Reporting queries<br/>Data warehouse]
        end
    end

    %% Edge to Service connections
    API --> TIMELINE_READ
    API --> TWEET_READ
    API --> GRAPH_READ
    API --> SEARCH_READ
    API --> TWEET_WRITE
    API --> GRAPH_WRITE
    API --> MEDIA_WRITE

    CACHE_PROXY --> TIMELINE_READ
    CACHE_PROXY --> MEMCACHED
    CACHE_PROXY --> REDIS

    %% Read service connections
    TIMELINE_READ --> MANHATTAN
    TIMELINE_READ --> MEMCACHED
    TWEET_READ --> MANHATTAN
    TWEET_READ --> BLOBSTORE
    GRAPH_READ --> FLOCKDB
    GRAPH_READ --> GIZMODUCK
    SEARCH_READ --> LUCENE

    %% Write service connections
    TWEET_WRITE --> MANHATTAN
    TWEET_WRITE --> KAFKA
    GRAPH_WRITE --> FLOCKDB
    MEDIA_WRITE --> BLOBSTORE
    MEDIA_WRITE --> TWIMG

    %% Replication and streaming
    MANHATTAN --> REPLICATOR
    MYSQL --> BACKUP_SERVICE
    FLOCKDB --> KAFKA
    MANHATTAN --> KAFKA

    KAFKA --> HERON
    HERON --> CASSANDRA
    HERON --> DRUID
    HERON --> REDIS

    %% Batch processing
    MANHATTAN --> HADOOP
    KAFKA --> HADOOP
    HADOOP --> VERTICA

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:2px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:2px

    class API,CACHE_PROXY edgeStyle
    class TIMELINE_READ,TWEET_READ,GRAPH_READ,SEARCH_READ,TWEET_WRITE,GRAPH_WRITE,MEDIA_WRITE serviceStyle
    class MANHATTAN,MYSQL,FLOCKDB,GIZMODUCK,BLOBSTORE,TWIMG,LUCENE,CASSANDRA,DRUID,MEMCACHED,REDIS stateStyle
    class REPLICATOR,BACKUP_SERVICE,KAFKA,HERON,HADOOP,VERTICA controlStyle
```

## Manhattan Database - Twitter's Crown Jewel

```mermaid
graph TB
    subgraph ManhattanArchitecture[Manhattan Database Architecture]
        subgraph ClientLayer[Client Layer]
            MANHATTAN_CLIENT[Manhattan Client<br/>Java/Scala library<br/>Connection pooling<br/>Retry mechanisms<br/>Load balancing]
        end

        subgraph ProxyLayer[Proxy Layer]
            MANHATTAN_PROXY[Manhattan Proxy<br/>Request routing<br/>Query optimization<br/>Connection multiplexing<br/>Protocol translation]
        end

        subgraph ShardingLayer[Sharding Layer]
            subgraph Shard1[Shard 1 - Range: 0-100M]
                LEADER1[Leader Node<br/>MySQL backend<br/>Write operations<br/>Read replicas: 3]
                REPLICA1A[Read Replica 1A<br/>Async replication<br/>Read operations<br/>Local SSD storage]
                REPLICA1B[Read Replica 1B<br/>Async replication<br/>Read operations<br/>Local SSD storage]
                REPLICA1C[Read Replica 1C<br/>Async replication<br/>Read operations<br/>Local SSD storage]
            end

            subgraph Shard2[Shard 2 - Range: 100M-200M]
                LEADER2[Leader Node<br/>MySQL backend<br/>Write operations<br/>Read replicas: 3]
                REPLICA2A[Read Replica 2A<br/>Async replication<br/>Read operations<br/>Local SSD storage]
                REPLICA2B[Read Replica 2B<br/>Async replication<br/>Read operations<br/>Local SSD storage]
                REPLICA2C[Read Replica 2C<br/>Async replication<br/>Read operations<br/>Local SSD storage]
            end

            subgraph ShardN[Shard N - Range: NM-(N+1)M]
                LEADERN[Leader Node<br/>MySQL backend<br/>Write operations<br/>Read replicas: 3]
                REPLICANA[Read Replica NA<br/>Async replication<br/>Read operations<br/>Local SSD storage]
                REPLICANB[Read Replica NB<br/>Async replication<br/>Read operations<br/>Local SSD storage]
                REPLICANC[Read Replica NC<br/>Async replication<br/>Read operations<br/>Local SSD storage]
            end
        end

        subgraph ConsistencyLayer[Consistency Layer]
            CDC[Change Data Capture<br/>Binlog streaming<br/>Event publishing<br/>Kafka integration]
        end
    end

    MANHATTAN_CLIENT --> MANHATTAN_PROXY
    MANHATTAN_PROXY --> LEADER1
    MANHATTAN_PROXY --> LEADER2
    MANHATTAN_PROXY --> LEADERN

    LEADER1 --> REPLICA1A
    LEADER1 --> REPLICA1B
    LEADER1 --> REPLICA1C
    LEADER2 --> REPLICA2A
    LEADER2 --> REPLICA2B
    LEADER2 --> REPLICA2C
    LEADERN --> REPLICANA
    LEADERN --> REPLICANB
    LEADERN --> REPLICANC

    LEADER1 --> CDC
    LEADER2 --> CDC
    LEADERN --> CDC

    %% Sharding strategy
    MANHATTAN_PROXY -.->|"Sharding by tweet_id<br/>Consistent hashing<br/>Auto-rebalancing"| LEADER1

    classDef clientStyle fill:#E8F5E8,stroke:#388E3C,color:#000
    classDef proxyStyle fill:#E3F2FD,stroke:#1976D2,color:#000
    classDef leaderStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef replicaStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef consistencyStyle fill:#F3E5F5,stroke:#7B1FA2,color:#000

    class MANHATTAN_CLIENT clientStyle
    class MANHATTAN_PROXY proxyStyle
    class LEADER1,LEADER2,LEADERN leaderStyle
    class REPLICA1A,REPLICA1B,REPLICA1C,REPLICA2A,REPLICA2B,REPLICA2C,REPLICANA,REPLICANB,REPLICANC replicaStyle
    class CDC consistencyStyle
```

## FlockDB - Social Graph Database

```mermaid
graph TB
    subgraph FlockDBArchitecture[FlockDB Social Graph Architecture]
        subgraph ApplicationLayer[Application Layer]
            FLOCK_CLIENT[FlockDB Client<br/>Thrift protocol<br/>Graph operations<br/>Batch queries<br/>Connection pooling]
        end

        subgraph ServiceLayer[Service Layer]
            FLOCK_SERVICE[FlockDB Service<br/>Graph query engine<br/>Edge management<br/>Relationship logic<br/>Pagination support]
        end

        subgraph ShardingLayer[Graph Sharding Layer]
            subgraph FollowingShard[Following Shard - Forward Edges]
                FOLLOWING_LEADER[Following Leader<br/>MySQL storage<br/>user_id → following_ids<br/>Write operations]
                FOLLOWING_REPLICA1[Following Replica 1<br/>Read operations<br/>Query optimization<br/>Index management]
                FOLLOWING_REPLICA2[Following Replica 2<br/>Read operations<br/>Load distribution<br/>Backup serving]
            end

            subgraph FollowerShard[Follower Shard - Reverse Edges]
                FOLLOWER_LEADER[Follower Leader<br/>MySQL storage<br/>user_id → follower_ids<br/>Write operations]
                FOLLOWER_REPLICA1[Follower Replica 1<br/>Read operations<br/>Count queries<br/>Pagination support]
                FOLLOWER_REPLICA2[Follower Replica 2<br/>Read operations<br/>Analytics queries<br/>Batch processing]
            end

            subgraph BlockingShard[Blocking Shard - Block Relationships]
                BLOCKING_LEADER[Blocking Leader<br/>MySQL storage<br/>user_id → blocked_ids<br/>Privacy enforcement]
                BLOCKING_REPLICA1[Blocking Replica 1<br/>Read operations<br/>Privacy checks<br/>Content filtering]
            end
        end

        subgraph CacheLayer[Cache Layer]
            FLOCK_CACHE[FlockDB Cache<br/>Redis clusters<br/>Hot relationships<br/>Follower counts<br/>Following lists]
        end
    end

    FLOCK_CLIENT --> FLOCK_SERVICE

    FLOCK_SERVICE --> FOLLOWING_LEADER
    FLOCK_SERVICE --> FOLLOWER_LEADER
    FLOCK_SERVICE --> BLOCKING_LEADER

    FOLLOWING_LEADER --> FOLLOWING_REPLICA1
    FOLLOWING_LEADER --> FOLLOWING_REPLICA2
    FOLLOWER_LEADER --> FOLLOWER_REPLICA1
    FOLLOWER_LEADER --> FOLLOWER_REPLICA2
    BLOCKING_LEADER --> BLOCKING_REPLICA1

    FLOCK_SERVICE --> FLOCK_CACHE

    %% Graph operations
    FLOCK_CLIENT -.->|"Operations:<br/>• follow(user_a, user_b)<br/>• unfollow(user_a, user_b)<br/>• followers(user_id)<br/>• following(user_id)<br/>• mutual_follow(user_a, user_b)"| FLOCK_SERVICE

    classDef clientStyle fill:#E8F5E8,stroke:#388E3C,color:#000
    classDef serviceStyle fill:#E3F2FD,stroke:#1976D2,color:#000
    classDef leaderStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef replicaStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef cacheStyle fill:#F3E5F5,stroke:#7B1FA2,color:#000

    class FLOCK_CLIENT clientStyle
    class FLOCK_SERVICE serviceStyle
    class FOLLOWING_LEADER,FOLLOWER_LEADER,BLOCKING_LEADER leaderStyle
    class FOLLOWING_REPLICA1,FOLLOWING_REPLICA2,FOLLOWER_REPLICA1,FOLLOWER_REPLICA2,BLOCKING_REPLICA1 replicaStyle
    class FLOCK_CACHE cacheStyle
```

## Blobstore - Media Storage System

```mermaid
graph TB
    subgraph BlobstoreArchitecture[Blobstore Media Storage Architecture]
        subgraph UploadPipeline[Upload Pipeline]
            UPLOAD_PROXY[Upload Proxy<br/>Load balancing<br/>Upload validation<br/>Size limits<br/>Format checking]
            VIRUS_SCAN[Virus Scanner<br/>Security scanning<br/>Malware detection<br/>Content validation<br/>Policy enforcement]
            TRANSCODE[Transcoding Service<br/>Video processing<br/>Format conversion<br/>Quality optimization<br/>Thumbnail generation]
        end

        subgraph StorageLayer[Storage Layer]
            subgraph HotStorage[Hot Storage - Frequent Access]
                HOT_STORE1[Hot Store 1<br/>SSD storage<br/>Recent media<br/>High IOPS<br/>Sub-100ms access]
                HOT_STORE2[Hot Store 2<br/>SSD storage<br/>Popular content<br/>Cache optimization<br/>Multi-region]
            end

            subgraph WarmStorage[Warm Storage - Regular Access]
                WARM_STORE1[Warm Store 1<br/>HDD storage<br/>Older media<br/>Cost optimized<br/>200-500ms access]
                WARM_STORE2[Warm Store 2<br/>HDD storage<br/>Archive transition<br/>Compression enabled<br/>Batch access]
            end

            subgraph ColdStorage[Cold Storage - Archival]
                COLD_STORE[Cold Storage<br/>S3 Glacier<br/>Long-term archive<br/>Compliance storage<br/>Minutes to hours access]
            end
        end

        subgraph DeliveryLayer[Delivery Layer]
            CDN_ORIGIN[CDN Origin Servers<br/>twimg.com<br/>Global distribution<br/>Edge optimization<br/>Format adaptation]
            IMAGE_PROCESSOR[Image Processor<br/>Real-time resizing<br/>Format conversion<br/>Quality optimization<br/>WebP/AVIF support]
        end

        subgraph MetadataLayer[Metadata Layer]
            BLOB_METADATA[Blob Metadata<br/>Manhattan storage<br/>File properties<br/>Access patterns<br/>Lifecycle policies]
        end
    end

    UPLOAD_PROXY --> VIRUS_SCAN
    VIRUS_SCAN --> TRANSCODE

    TRANSCODE --> HOT_STORE1
    TRANSCODE --> HOT_STORE2

    HOT_STORE1 --> WARM_STORE1
    HOT_STORE2 --> WARM_STORE2
    WARM_STORE1 --> COLD_STORE
    WARM_STORE2 --> COLD_STORE

    HOT_STORE1 --> CDN_ORIGIN
    HOT_STORE2 --> CDN_ORIGIN
    CDN_ORIGIN --> IMAGE_PROCESSOR

    TRANSCODE --> BLOB_METADATA
    BLOB_METADATA --> CDN_ORIGIN

    %% Storage lifecycle
    HOT_STORE1 -.->|"Lifecycle: 30 days<br/>Auto-migration to warm<br/>Access pattern based"| WARM_STORE1
    WARM_STORE1 -.->|"Lifecycle: 180 days<br/>Archive to cold storage<br/>Compliance requirements"| COLD_STORE

    classDef uploadStyle fill:#E8F5E8,stroke:#388E3C,color:#000
    classDef hotStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef warmStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef coldStyle fill:#E3F2FD,stroke:#1976D2,color:#000
    classDef deliveryStyle fill:#F3E5F5,stroke:#7B1FA2,color:#000
    classDef metadataStyle fill:#E1F5FE,stroke:#0288D1,color:#000

    class UPLOAD_PROXY,VIRUS_SCAN,TRANSCODE uploadStyle
    class HOT_STORE1,HOT_STORE2 hotStyle
    class WARM_STORE1,WARM_STORE2 warmStyle
    class COLD_STORE coldStyle
    class CDN_ORIGIN,IMAGE_PROCESSOR deliveryStyle
    class BLOB_METADATA metadataStyle
```

## Real-time Search Index

```mermaid
graph TB
    subgraph SearchIndexArchitecture[Real-time Search Index Architecture]
        subgraph IndexingPipeline[Indexing Pipeline]
            TWEET_STREAM[Tweet Stream<br/>Kafka consumer<br/>Real-time ingestion<br/>500M tweets/day<br/>Content extraction]
            TEXT_PROCESSOR[Text Processor<br/>Tokenization<br/>Language detection<br/>Entity extraction<br/>Hashtag parsing]
            INDEX_BUILDER[Index Builder<br/>Lucene indexing<br/>Inverted index<br/>Term frequency<br/>Position information]
        end

        subgraph IndexStorage[Index Storage]
            subgraph RecentIndex[Recent Index - Hot Data]
                RECENT_SHARD1[Recent Shard 1<br/>Last 7 days<br/>High write rate<br/>Real-time updates<br/>SSD storage]
                RECENT_SHARD2[Recent Shard 2<br/>Last 7 days<br/>Load distribution<br/>Replica serving<br/>Query optimization]
                RECENT_SHARD3[Recent Shard 3<br/>Last 7 days<br/>Backup serving<br/>Failover ready<br/>Index warming]
            end

            subgraph HistoricalIndex[Historical Index - Archive Data]
                HISTORICAL_SHARD1[Historical Shard 1<br/>Older tweets<br/>Read-optimized<br/>Compressed storage<br/>HDD backend]
                HISTORICAL_SHARD2[Historical Shard 2<br/>Archive data<br/>Batch access<br/>Cost optimized<br/>Long-term storage]
            end
        end

        subgraph QueryLayer[Query Layer]
            QUERY_PARSER[Query Parser<br/>Query analysis<br/>Term expansion<br/>Filter application<br/>Optimization rules]
            SEARCH_COORDINATOR[Search Coordinator<br/>Shard selection<br/>Parallel execution<br/>Result merging<br/>Ranking application]
            RESULT_AGGREGATOR[Result Aggregator<br/>Score combination<br/>Duplicate removal<br/>Personalization<br/>Result formatting]
        end

        subgraph CachingLayer[Caching Layer]
            QUERY_CACHE[Query Cache<br/>Redis cluster<br/>Popular queries<br/>Result caching<br/>2-minute TTL]
            INDEX_CACHE[Index Cache<br/>Hot index segments<br/>Memory mapping<br/>OS page cache<br/>Fast access]
        end
    end

    TWEET_STREAM --> TEXT_PROCESSOR
    TEXT_PROCESSOR --> INDEX_BUILDER

    INDEX_BUILDER --> RECENT_SHARD1
    INDEX_BUILDER --> RECENT_SHARD2
    INDEX_BUILDER --> RECENT_SHARD3

    RECENT_SHARD1 --> HISTORICAL_SHARD1
    RECENT_SHARD2 --> HISTORICAL_SHARD2

    QUERY_PARSER --> SEARCH_COORDINATOR
    SEARCH_COORDINATOR --> RECENT_SHARD1
    SEARCH_COORDINATOR --> RECENT_SHARD2
    SEARCH_COORDINATOR --> HISTORICAL_SHARD1

    SEARCH_COORDINATOR --> RESULT_AGGREGATOR
    RESULT_AGGREGATOR --> QUERY_CACHE

    RECENT_SHARD1 --> INDEX_CACHE
    RECENT_SHARD2 --> INDEX_CACHE

    %% Search performance
    TEXT_PROCESSOR -.->|"Processing rate: 6K tweets/sec<br/>Indexing latency: <10 seconds<br/>Search availability: 99.95%"| INDEX_BUILDER

    classDef pipelineStyle fill:#E8F5E8,stroke:#388E3C,color:#000
    classDef recentStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef historicalStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef queryStyle fill:#E3F2FD,stroke:#1976D2,color:#000
    classDef cacheStyle fill:#F3E5F5,stroke:#7B1FA2,color:#000

    class TWEET_STREAM,TEXT_PROCESSOR,INDEX_BUILDER pipelineStyle
    class RECENT_SHARD1,RECENT_SHARD2,RECENT_SHARD3 recentStyle
    class HISTORICAL_SHARD1,HISTORICAL_SHARD2 historicalStyle
    class QUERY_PARSER,SEARCH_COORDINATOR,RESULT_AGGREGATOR queryStyle
    class QUERY_CACHE,INDEX_CACHE cacheStyle
```

## Storage Performance Metrics

| Storage System | Read Latency (p99) | Write Latency (p99) | Throughput | Consistency Model |
|----------------|---------------------|---------------------|------------|-------------------|
| **Manhattan** | 20ms | 50ms | 1M QPS | Eventually consistent |
| **FlockDB** | 15ms | 30ms | 500K QPS | Eventually consistent |
| **MySQL** | 10ms | 25ms | 200K QPS | ACID consistent |
| **Blobstore** | 100ms | 200ms | 100K QPS | Eventually consistent |
| **Memcached** | 1ms | 1ms | 10M QPS | No persistence |
| **Lucene Search** | 50ms | N/A (read-only) | 100K QPS | Eventually consistent |

## Data Lifecycle Management

```mermaid
graph TB
    subgraph DataLifecycle[Data Lifecycle Management]
        subgraph HotData[Hot Data - Active Usage]
            ACTIVE_TWEETS[Active Tweets<br/>Last 30 days<br/>High read/write<br/>SSD storage<br/>Real-time access]
            TRENDING_CONTENT[Trending Content<br/>Viral tweets<br/>Cached heavily<br/>Memory storage<br/>Sub-ms access]
        end

        subgraph WarmData[Warm Data - Regular Access]
            RECENT_TWEETS[Recent Tweets<br/>30-180 days<br/>Moderate access<br/>Hybrid storage<br/>Batch optimization]
            USER_TIMELINES[User Timelines<br/>Personal history<br/>Occasional access<br/>Compressed storage<br/>Cost optimized]
        end

        subgraph ColdData[Cold Data - Archival]
            ARCHIVED_TWEETS[Archived Tweets<br/>180+ days<br/>Compliance storage<br/>Glacier archive<br/>Retrieval on demand]
            DELETED_CONTENT[Deleted Content<br/>Legal retention<br/>Encrypted storage<br/>Access restricted<br/>Audit logging]
        end

        subgraph LifecyclePolicies[Lifecycle Policies]
            AUTO_MIGRATION[Auto Migration<br/>Time-based rules<br/>Access pattern analysis<br/>Cost optimization<br/>Performance monitoring]
            COMPLIANCE_RULES[Compliance Rules<br/>Legal requirements<br/>Data retention<br/>Privacy regulations<br/>Right to deletion]
        end
    end

    ACTIVE_TWEETS --> RECENT_TWEETS
    TRENDING_CONTENT --> RECENT_TWEETS
    RECENT_TWEETS --> ARCHIVED_TWEETS
    USER_TIMELINES --> ARCHIVED_TWEETS

    AUTO_MIGRATION --> ACTIVE_TWEETS
    AUTO_MIGRATION --> RECENT_TWEETS
    COMPLIANCE_RULES --> ARCHIVED_TWEETS
    COMPLIANCE_RULES --> DELETED_CONTENT

    %% Migration patterns
    ACTIVE_TWEETS -.->|"Migration trigger:<br/>Age > 30 days OR<br/>Access frequency < 1/week"| RECENT_TWEETS
    RECENT_TWEETS -.->|"Archive trigger:<br/>Age > 180 days OR<br/>Access frequency < 1/month"| ARCHIVED_TWEETS

    classDef hotStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef warmStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef coldStyle fill:#E3F2FD,stroke:#1976D2,color:#000
    classDef policyStyle fill:#E8F5E8,stroke:#388E3C,color:#000

    class ACTIVE_TWEETS,TRENDING_CONTENT hotStyle
    class RECENT_TWEETS,USER_TIMELINES warmStyle
    class ARCHIVED_TWEETS,DELETED_CONTENT coldStyle
    class AUTO_MIGRATION,COMPLIANCE_RULES policyStyle
```

## Disaster Recovery & Backup Strategy

| System | Backup Frequency | RTO | RPO | Backup Size |
|--------|------------------|-----|-----|-------------|
| **Manhattan** | Continuous replication + 6hr snapshots | 30 minutes | 10 minutes | 200TB/day |
| **FlockDB** | Daily full + hourly incremental | 1 hour | 30 minutes | 50TB/day |
| **MySQL** | Continuous binlog + daily snapshots | 15 minutes | 5 minutes | 20TB/day |
| **Blobstore** | 3x replication + weekly archive | 2 hours | 0 (replicated) | 500TB/week |
| **Search Index** | Rebuild from source | 4 hours | 0 (derived data) | N/A |

## Key Storage Innovations

1. **Manhattan Database**: Multi-tenant distributed NoSQL at massive scale
2. **FlockDB**: Purpose-built social graph database
3. **Snowflake IDs**: Globally unique, time-ordered identifiers
4. **Hybrid Storage Tiers**: Hot/warm/cold data lifecycle management
5. **Real-time Search**: Immediate indexing of new content
6. **Blobstore Optimization**: Intelligent media storage and delivery

*Last updated: September 2024*
*Source: Twitter Engineering Blog, High Scalability presentations*