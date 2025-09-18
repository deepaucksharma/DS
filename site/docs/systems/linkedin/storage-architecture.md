# LinkedIn Storage Architecture

## Overview
LinkedIn's storage architecture handles 1B+ member profiles, 30B+ connections, and 7 trillion Kafka messages daily. The system uses specialized databases for different data patterns with strong consistency guarantees.

## Complete Storage Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Data Access]
        API[API Gateway<br/>Kong Enterprise<br/>Request routing]
        LB[Load Balancers<br/>F5 + AWS ALB<br/>Health checking]
    end

    subgraph ServicePlane[Service Plane - Data Services]
        subgraph ReadServices[Read Services]
            FEED_R[Feed Read Service<br/>Venice client<br/>Read-optimized views]
            PROFILE_R[Profile Read Service<br/>Espresso client<br/>Consistent reads]
            SEARCH_R[Search Read Service<br/>Galene client<br/>Full-text search]
        end

        subgraph WriteServices[Write Services]
            PROFILE_W[Profile Write Service<br/>Espresso client<br/>ACID transactions]
            CONNECT_W[Connection Write Service<br/>Graph mutations<br/>Bi-directional updates]
            ACTIVITY_W[Activity Write Service<br/>Kafka producer<br/>Event streaming]
        end
    end

    subgraph StatePlane[State Plane - Storage Systems]
        subgraph PrimaryStorage[Primary Storage - Source of Truth]
            ESPRESSO[Espresso Database<br/>Timeline-consistent NoSQL<br/>1000+ TB<br/>Multi-master replication]
            GRAPH_DB[Neo4j Clusters<br/>Social graph storage<br/>30B+ connections<br/>100+ TB]
            VOLDEMORT[Voldemort<br/>Distributed key-value<br/>DHT-based sharding<br/>500+ TB]
        end

        subgraph DerivedStorage[Derived Storage - Read Optimizations]
            VENICE[Venice Platform<br/>Derived data serving<br/>Read-only views<br/>300+ TB]
            PINOT[Apache Pinot<br/>Real-time analytics<br/>OLAP queries<br/>200+ TB]
            GALENE[Galene Search<br/>Lucene-based<br/>Full-text indexing<br/>150+ TB]
        end

        subgraph SpecializedStorage[Specialized Storage]
            AMBRY[Ambry<br/>Media/blob storage<br/>Photos, videos, docs<br/>2+ PB]
            COUCHBASE[Couchbase<br/>Session + messaging<br/>Hot data store<br/>50+ TB]
            KAFKA_STORE[Kafka Storage<br/>Event streaming<br/>7 trillion msgs/day<br/>Log compaction: 3 days]
        end

        subgraph CacheLayers[Cache Layers]
            REDIS[Redis Clusters<br/>Hot data cache<br/>Session, connections<br/>200+ GB]
            MEMCACHED[Memcached<br/>Query result cache<br/>15-min TTL<br/>500+ GB]
        end
    end

    subgraph ControlPlane[Control Plane - Data Management]
        subgraph DataPipeline[Data Pipeline]
            DATABUS[Databus<br/>Change data capture<br/>Real-time replication]
            BROOKLIN[Brooklin<br/>Data streaming<br/>Cross-datacenter sync]
            SAMZA[Samza Jobs<br/>Stream processing<br/>Data transformations]
        end

        subgraph BatchProcessing[Batch Processing]
            HDFS[HDFS Data Lake<br/>Historical data<br/>100+ PB storage]
            SPARK[Spark Clusters<br/>ETL processing<br/>ML feature generation]
            PRESTO[Presto SQL<br/>Interactive queries<br/>Federation layer]
        end
    end

    %% Edge to Service connections
    API --> FEED_R
    API --> PROFILE_R
    API --> SEARCH_R
    API --> PROFILE_W
    API --> CONNECT_W
    API --> ACTIVITY_W

    %% Read service connections
    FEED_R --> VENICE
    FEED_R --> REDIS
    PROFILE_R --> ESPRESSO
    PROFILE_R --> MEMCACHED
    SEARCH_R --> GALENE

    %% Write service connections
    PROFILE_W --> ESPRESSO
    CONNECT_W --> GRAPH_DB
    ACTIVITY_W --> KAFKA_STORE

    %% Data replication flows
    ESPRESSO --> DATABUS
    GRAPH_DB --> DATABUS
    VOLDEMORT --> DATABUS
    KAFKA_STORE --> SAMZA

    DATABUS --> VENICE
    DATABUS --> PINOT
    SAMZA --> VENICE
    SAMZA --> GALENE

    %% Cross-datacenter replication
    BROOKLIN --> ESPRESSO
    BROOKLIN --> KAFKA_STORE

    %% Batch processing
    ESPRESSO --> HDFS
    KAFKA_STORE --> HDFS
    HDFS --> SPARK
    SPARK --> PRESTO

    %% Media storage
    ACTIVITY_W --> AMBRY
    PROFILE_W --> AMBRY

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff,stroke-width:2px
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff,stroke-width:2px
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff,stroke-width:2px

    class API,LB edgeStyle
    class FEED_R,PROFILE_R,SEARCH_R,PROFILE_W,CONNECT_W,ACTIVITY_W serviceStyle
    class ESPRESSO,GRAPH_DB,VOLDEMORT,VENICE,PINOT,GALENE,AMBRY,COUCHBASE,KAFKA_STORE,REDIS,MEMCACHED stateStyle
    class DATABUS,BROOKLIN,SAMZA,HDFS,SPARK,PRESTO controlStyle
```

## Espresso Database - LinkedIn's Crown Jewel

```mermaid
graph TB
    subgraph EspressoArchitecture[Espresso Database Architecture]
        subgraph ClientLayer[Client Layer]
            ESP_CLIENT[Espresso Client<br/>Java library<br/>Connection pooling<br/>Retry logic]
        end

        subgraph RouterLayer[Router Layer]
            ROUTER[Espresso Router<br/>Request routing<br/>Load balancing<br/>Health monitoring]
        end

        subgraph StorageLayer[Storage Layer]
            subgraph Partition1[Partition 1]
                LEADER1[Leader Node<br/>MySQL 8.0<br/>Write operations<br/>Binlog streaming]
                FOLLOWER1A[Follower 1A<br/>Async replication<br/>Read operations]
                FOLLOWER1B[Follower 1B<br/>Async replication<br/>Read operations]
            end

            subgraph Partition2[Partition 2]
                LEADER2[Leader Node<br/>MySQL 8.0<br/>Write operations<br/>Binlog streaming]
                FOLLOWER2A[Follower 2A<br/>Async replication<br/>Read operations]
                FOLLOWER2B[Follower 2B<br/>Async replication<br/>Read operations]
            end

            subgraph PartitionN[Partition N]
                LEADERN[Leader Node<br/>MySQL 8.0<br/>Write operations<br/>Binlog streaming]
                FOLLOWERNA[Follower NA<br/>Async replication<br/>Read operations]
                FOLLOWERNB[Follower NB<br/>Async replication<br/>Read operations]
            end
        end

        subgraph ReplicationLayer[Replication Layer]
            DATABUS_ESP[Databus<br/>Change capture<br/>Ordered delivery<br/>At-least-once semantics]
        end
    end

    ESP_CLIENT --> ROUTER
    ROUTER --> LEADER1
    ROUTER --> LEADER2
    ROUTER --> LEADERN

    LEADER1 --> FOLLOWER1A
    LEADER1 --> FOLLOWER1B
    LEADER2 --> FOLLOWER2A
    LEADER2 --> FOLLOWER2B
    LEADERN --> FOLLOWERNA
    LEADERN --> FOLLOWERNB

    LEADER1 --> DATABUS_ESP
    LEADER2 --> DATABUS_ESP
    LEADERN --> DATABUS_ESP

    %% Partition strategy
    ESP_CLIENT -.->|"Partition by userId<br/>Hash-based routing"| ROUTER

    classDef clientStyle fill:#E3F2FD,stroke:#1976D2,color:#000
    classDef routerStyle fill:#E8F5E8,stroke:#388E3C,color:#000
    classDef leaderStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef followerStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef replicationStyle fill:#F3E5F5,stroke:#7B1FA2,color:#000

    class ESP_CLIENT clientStyle
    class ROUTER routerStyle
    class LEADER1,LEADER2,LEADERN leaderStyle
    class FOLLOWER1A,FOLLOWER1B,FOLLOWER2A,FOLLOWER2B,FOLLOWERNA,FOLLOWERNB followerStyle
    class DATABUS_ESP replicationStyle
```

## Social Graph Storage (Neo4j)

```mermaid
graph TB
    subgraph SocialGraphArchitecture[Social Graph Architecture]
        subgraph ApplicationLayer[Application Layer]
            GRAPH_API[Graph API<br/>Connection service<br/>Cypher queries<br/>Bulk operations]
        end

        subgraph CacheLayer[Cache Layer]
            GRAPH_CACHE[Redis Graph Cache<br/>Hot connections<br/>1-degree lookups<br/>95% hit rate]
        end

        subgraph DatabaseClusters[Neo4j Database Clusters]
            subgraph Cluster1[Cluster 1 - Americas]
                NEO4J_1_LEADER[Neo4j Leader<br/>Core server<br/>Write operations<br/>Causal clustering]
                NEO4J_1_READ1[Read Replica 1<br/>Read operations<br/>Eventually consistent]
                NEO4J_1_READ2[Read Replica 2<br/>Read operations<br/>Eventually consistent]
            end

            subgraph Cluster2[Cluster 2 - EMEA]
                NEO4J_2_LEADER[Neo4j Leader<br/>Core server<br/>Write operations<br/>Causal clustering]
                NEO4J_2_READ1[Read Replica 1<br/>Read operations<br/>Eventually consistent]
                NEO4J_2_READ2[Read Replica 2<br/>Read operations<br/>Eventually consistent]
            end

            subgraph Cluster3[Cluster 3 - APAC]
                NEO4J_3_LEADER[Neo4j Leader<br/>Core server<br/>Write operations<br/>Causal clustering]
                NEO4J_3_READ1[Read Replica 1<br/>Read operations<br/>Eventually consistent]
                NEO4J_3_READ2[Read Replica 2<br/>Read operations<br/>Eventually consistent]
            end
        end

        subgraph ReplicationLayer[Cross-Cluster Replication]
            CROSS_REP[Brooklin Replication<br/>Cross-datacenter sync<br/>Eventual consistency<br/>Conflict resolution]
        end
    end

    GRAPH_API --> GRAPH_CACHE
    GRAPH_CACHE --> NEO4J_1_LEADER
    GRAPH_CACHE --> NEO4J_1_READ1

    GRAPH_API --> NEO4J_1_LEADER
    GRAPH_API --> NEO4J_2_LEADER
    GRAPH_API --> NEO4J_3_LEADER

    NEO4J_1_LEADER --> NEO4J_1_READ1
    NEO4J_1_LEADER --> NEO4J_1_READ2
    NEO4J_2_LEADER --> NEO4J_2_READ1
    NEO4J_2_LEADER --> NEO4J_2_READ2
    NEO4J_3_LEADER --> NEO4J_3_READ1
    NEO4J_3_LEADER --> NEO4J_3_READ2

    NEO4J_1_LEADER --> CROSS_REP
    NEO4J_2_LEADER --> CROSS_REP
    NEO4J_3_LEADER --> CROSS_REP

    %% Connection patterns
    GRAPH_API -.->|"1-degree: O(500) avg<br/>2-degree: O(250K) avg<br/>3-degree: O(125M) avg"| GRAPH_CACHE

    classDef apiStyle fill:#E3F2FD,stroke:#1976D2,color:#000
    classDef cacheStyle fill:#E8F5E8,stroke:#388E3C,color:#000
    classDef leaderStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef readStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef replicationStyle fill:#F3E5F5,stroke:#7B1FA2,color:#000

    class GRAPH_API apiStyle
    class GRAPH_CACHE cacheStyle
    class NEO4J_1_LEADER,NEO4J_2_LEADER,NEO4J_3_LEADER leaderStyle
    class NEO4J_1_READ1,NEO4J_1_READ2,NEO4J_2_READ1,NEO4J_2_READ2,NEO4J_3_READ1,NEO4J_3_READ2 readStyle
    class CROSS_REP replicationStyle
```

## Venice Derived Data Platform

```mermaid
graph TB
    subgraph VeniceArchitecture[Venice Derived Data Platform]
        subgraph SourceSystems[Source Systems]
            ESP_SOURCE[Espresso<br/>Member profiles<br/>Primary source]
            KAFKA_SOURCE[Kafka Topics<br/>Activity events<br/>Stream source]
            VOLDEMORT_SOURCE[Voldemort<br/>Key-value data<br/>Batch source]
        end

        subgraph VeniceCore[Venice Core Components]
            CONTROLLER[Venice Controller<br/>Cluster management<br/>Schema evolution<br/>Push coordination]

            subgraph VeniceServers[Venice Server Fleet]
                VS1[Venice Server 1<br/>RocksDB storage<br/>Read-only serving]
                VS2[Venice Server 2<br/>RocksDB storage<br/>Read-only serving]
                VSN[Venice Server N<br/>RocksDB storage<br/>Read-only serving]
            end

            ROUTER_V[Venice Router<br/>Client requests<br/>Read routing<br/>Load balancing]
        end

        subgraph DataProcessing[Data Processing Pipeline]
            BATCH_JOB[Batch Push Job<br/>Hadoop MapReduce<br/>Full data rebuild<br/>Daily/Weekly runs]
            STREAM_JOB[Stream Processing<br/>Samza jobs<br/>Incremental updates<br/>Real-time changes]
        end

        subgraph ClientLayer[Client Layer]
            VENICE_CLIENT[Venice Client<br/>Java library<br/>Connection pooling<br/>Fallback logic]
        end
    end

    %% Data flow from sources
    ESP_SOURCE --> BATCH_JOB
    KAFKA_SOURCE --> STREAM_JOB
    VOLDEMORT_SOURCE --> BATCH_JOB

    %% Processing to Venice
    BATCH_JOB --> CONTROLLER
    STREAM_JOB --> CONTROLLER

    CONTROLLER --> VS1
    CONTROLLER --> VS2
    CONTROLLER --> VSN

    %% Client access
    VENICE_CLIENT --> ROUTER_V
    ROUTER_V --> VS1
    ROUTER_V --> VS2
    ROUTER_V --> VSN

    %% Data characteristics
    ESP_SOURCE -.->|"1B+ profiles<br/>Daily full rebuild"| BATCH_JOB
    KAFKA_SOURCE -.->|"7T msgs/day<br/>Real-time updates"| STREAM_JOB
    VENICE_CLIENT -.->|"Read-only access<br/>p99: 5ms latency"| ROUTER_V

    classDef sourceStyle fill:#E3F2FD,stroke:#1976D2,color:#000
    classDef veniceStyle fill:#E8F5E8,stroke:#388E3C,color:#000
    classDef processStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef clientStyle fill:#F3E5F5,stroke:#7B1FA2,color:#000

    class ESP_SOURCE,KAFKA_SOURCE,VOLDEMORT_SOURCE sourceStyle
    class CONTROLLER,VS1,VS2,VSN,ROUTER_V veniceStyle
    class BATCH_JOB,STREAM_JOB processStyle
    class VENICE_CLIENT clientStyle
```

## Storage Performance Metrics

| Storage System | Read Latency (p99) | Write Latency (p99) | Throughput | Consistency Model |
|----------------|---------------------|---------------------|------------|-------------------|
| **Espresso** | 15ms | 25ms | 2M QPS | Timeline-consistent |
| **Neo4j Graph** | 10ms | 50ms | 500K QPS | Eventually consistent |
| **Voldemort** | 5ms | 8ms | 5M QPS | Eventually consistent |
| **Venice** | 5ms | N/A (read-only) | 10M QPS | Eventually consistent |
| **Redis Cache** | 1ms | 1ms | 50M QPS | No persistence |
| **Pinot OLAP** | 100ms | N/A (read-only) | 100K QPS | Eventually consistent |

## Data Consistency Guarantees

```mermaid
graph TB
    subgraph ConsistencyLevels[Consistency Levels by Use Case]
        subgraph StrongConsistency[Strong Consistency - Espresso]
            PROFILE_DATA[Profile Updates<br/>Timeline-consistent<br/>ACID transactions]
            FINANCIAL[Premium payments<br/>Strong consistency<br/>No data loss]
        end

        subgraph EventualConsistency[Eventual Consistency]
            CONNECTIONS[Connection graph<br/>Neo4j clusters<br/>Cross-region: <1min]
            FEED_DATA[Feed generation<br/>Venice views<br/>Acceptable: <5min]
            SEARCH_INDEX[Search indexing<br/>Galene updates<br/>Acceptable: <10min]
        end

        subgraph CacheConsistency[Cache Consistency]
            REDIS_TTL[Redis expiration<br/>TTL-based invalidation<br/>Max staleness: 1-2h]
            MEMCACHED_TTL[Memcached invalidation<br/>TTL-based expiration<br/>Max staleness: 15min]
        end
    end

    PROFILE_DATA -.->|"Propagation time:<br/>Immediate"| FEED_DATA
    PROFILE_DATA -.->|"Propagation time:<br/>1-5 minutes"| SEARCH_INDEX
    CONNECTIONS -.->|"Propagation time:<br/>30 seconds"| FEED_DATA

    classDef strongStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef eventualStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef cacheStyle fill:#E8F5E8,stroke:#388E3C,color:#000

    class PROFILE_DATA,FINANCIAL strongStyle
    class CONNECTIONS,FEED_DATA,SEARCH_INDEX eventualStyle
    class REDIS_TTL,MEMCACHED_TTL cacheStyle
```

## Disaster Recovery & Backup Strategy

| System | Backup Frequency | RTO | RPO | Backup Size |
|--------|------------------|-----|-----|-------------|
| **Espresso** | Continuous binlog + Daily snapshot | 15 minutes | 5 minutes | 50TB/day |
| **Neo4j Graph** | Daily full backup | 30 minutes | 1 hour | 5TB/day |
| **Voldemort** | Continuous replication | 5 minutes | 1 minute | 25TB/day |
| **Venice** | Rebuild from source | 2 hours | 0 (derived data) | N/A |
| **Kafka** | Log segments to S3 | 10 minutes | 30 seconds | 100TB/day |

## Key Storage Innovations

1. **Timeline Consistency**: Espresso's unique consistency model
2. **Venice Platform**: Batch + stream processing for derived data
3. **Databus**: Change data capture with ordering guarantees
4. **Voldemort**: Dynamo-inspired distributed hash table
5. **Brooklin**: Cross-datacenter streaming replication

*Last updated: September 2024*
*Source: LinkedIn Engineering Blog, QCon presentations*