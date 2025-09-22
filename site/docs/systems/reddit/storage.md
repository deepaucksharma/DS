# Reddit Storage Architecture - The Data Journey

Reddit's storage architecture handles the unique challenge of nested comment trees that can grow to thousands of levels deep, while maintaining sub-second read performance for 500M+ monthly active users.

## Complete Storage Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - CDN & Caching]
        CDN[Fastly CDN<br/>Comment Trees Cached<br/>Hot: 15min TTL<br/>$2.1M/month]
        REDIS_EDGE[Redis Edge Cache<br/>Vote Scores<br/>r6g.2xlarge × 50<br/>$875K/month]
    end

    subgraph ServicePlane[Service Plane - Application Logic]
        API[API Gateway<br/>Kong Enterprise<br/>Rate Limiting<br/>c5.4xlarge × 25]
        COMMENT_SVC[Comment Service<br/>Go 1.19<br/>Tree Traversal Logic<br/>c5.2xlarge × 100]
        VOTE_SVC[Vote Service<br/>Anti-fuzzing Logic<br/>Real-time Updates<br/>c5.xlarge × 75]
        FEED_SVC[Feed Generator<br/>Personalization<br/>Hot Sort Algorithm<br/>c5.4xlarge × 50]
    end

    subgraph StatePlane[State Plane - Data Storage]
        subgraph CommentStorage[Comment Storage - Cassandra]
            CASS_PRIMARY[Cassandra Primary<br/>Comment Tree Storage<br/>i3.8xlarge × 200<br/>RF=3, CL=QUORUM<br/>$4.2M/month]
            CASS_REPLICA[Cassandra Read Replicas<br/>Cross-region replication<br/>i3.4xlarge × 150<br/>$2.8M/month]
        end

        subgraph MetadataStorage[Metadata - PostgreSQL]
            PG_USERS[User Metadata<br/>PostgreSQL 14<br/>db.r6g.8xlarge × 20<br/>Sharded by user_id<br/>$420K/month]
            PG_SUBS[Subreddit Metadata<br/>PostgreSQL 14<br/>db.r6g.4xlarge × 10<br/>$180K/month]
            PG_POSTS[Post Metadata<br/>PostgreSQL 14<br/>db.r6g.8xlarge × 30<br/>Sharded by created_time<br/>$630K/month]
        end

        subgraph CacheLayer[Redis Cache Layer]
            REDIS_HOT[Hot Comment Cache<br/>Redis Cluster<br/>r6g.8xlarge × 100<br/>Top 1000 comments<br/>$2.1M/month]
            REDIS_VOTE[Vote Cache<br/>Redis Cluster<br/>r6g.4xlarge × 50<br/>Real-time scores<br/>$875K/month]
            REDIS_FEED[Feed Cache<br/>Redis Cluster<br/>r6g.8xlarge × 75<br/>Personalized feeds<br/>$1.6M/month]
        end

        subgraph Analytics[Analytics Storage]
            REDSHIFT[Redshift Cluster<br/>Vote Analytics<br/>Brigade Detection<br/>dc2.8xlarge × 50<br/>$680K/month]
            S3_LOGS[S3 Event Logs<br/>Comment History<br/>Vote Patterns<br/>Standard IA<br/>$125K/month]
        end
    end

    subgraph ControlPlane[Control Plane - Operations]
        PROMETHEUS[Prometheus<br/>Storage Metrics<br/>Query Performance<br/>c5.2xlarge × 10]
        GRAFANA[Grafana<br/>Storage Dashboards<br/>Capacity Planning<br/>c5.xlarge × 5]
        BACKUP_SVC[Backup Service<br/>Cross-region S3<br/>Point-in-time Recovery<br/>$890K/month]
    end

    %% Data Flow
    CDN --> API
    API --> COMMENT_SVC
    API --> VOTE_SVC
    API --> FEED_SVC

    COMMENT_SVC --> REDIS_HOT
    COMMENT_SVC --> CASS_PRIMARY
    VOTE_SVC --> REDIS_VOTE
    FEED_SVC --> REDIS_FEED

    REDIS_HOT -.->|Cache Miss| CASS_PRIMARY
    CASS_PRIMARY --> CASS_REPLICA

    COMMENT_SVC --> PG_POSTS
    VOTE_SVC --> PG_USERS
    FEED_SVC --> PG_SUBS

    %% Analytics Flow
    VOTE_SVC --> S3_LOGS
    S3_LOGS --> REDSHIFT

    %% Monitoring
    PROMETHEUS --> GRAFANA
    BACKUP_SVC --> S3_LOGS

    %% Styling
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class CDN,REDIS_EDGE edgeStyle
    class API,COMMENT_SVC,VOTE_SVC,FEED_SVC serviceStyle
    class CASS_PRIMARY,CASS_REPLICA,PG_USERS,PG_SUBS,PG_POSTS,REDIS_HOT,REDIS_VOTE,REDIS_FEED,REDSHIFT,S3_LOGS stateStyle
    class PROMETHEUS,GRAFANA,BACKUP_SVC controlStyle
```

## Comment Tree Storage Strategy

```mermaid
graph TB
    subgraph CommentTreeModel[Comment Tree Data Model]
        ROOT[Root Post<br/>post_id: abc123<br/>PostgreSQL]

        subgraph Level1[Level 1 Comments]
            C1[Comment 1<br/>parent_id: abc123<br/>depth: 1<br/>path: 1]
            C2[Comment 2<br/>parent_id: abc123<br/>depth: 1<br/>path: 2]
            C3[Comment 3<br/>parent_id: abc123<br/>depth: 1<br/>path: 3]
        end

        subgraph Level2[Level 2 Replies]
            C1_1[Reply 1.1<br/>parent_id: C1<br/>depth: 2<br/>path: 1.1]
            C1_2[Reply 1.2<br/>parent_id: C1<br/>depth: 2<br/>path: 1.2]
            C2_1[Reply 2.1<br/>parent_id: C2<br/>depth: 2<br/>path: 2.1]
        end

        subgraph Level3[Level 3 Nested]
            C1_1_1[Reply 1.1.1<br/>parent_id: C1_1<br/>depth: 3<br/>path: 1.1.1]
        end
    end

    subgraph CassandraPartition[Cassandra Partitioning Strategy]
        PART_POST[Partition Key: post_id<br/>Clustering: path, vote_score<br/>Allows sorted retrieval]
        PART_USER[Secondary Index: user_id<br/>For user comment history<br/>Cross-partition queries]
        PART_TIME[TTL Strategy:<br/>Hot comments: No TTL<br/>Archive after 6 months<br/>Cold storage in S3]
    end

    ROOT --> C1
    ROOT --> C2
    ROOT --> C3
    C1 --> C1_1
    C1 --> C1_2
    C2 --> C2_1
    C1_1 --> C1_1_1

    PART_POST --> PART_USER
    PART_USER --> PART_TIME

    %% Styling
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef metaStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class ROOT,C1,C2,C3,C1_1,C1_2,C2_1,C1_1_1 stateStyle
    class PART_POST,PART_USER,PART_TIME metaStyle
```

## Vote Storage & Anti-Fuzzing

```mermaid
graph TB
    subgraph VoteFlow[Vote Processing Pipeline]
        USER_VOTE[User Vote<br/>upvote/downvote<br/>Rate Limited<br/>10 votes/min]

        VOTE_VALIDATE[Vote Validation<br/>Anti-bot Detection<br/>Account Age Check<br/>Karma Threshold]

        VOTE_FUZZER[Vote Fuzzing<br/>Add Random Noise<br/>±1-3 votes<br/>Prevent Manipulation]

        SCORE_UPDATE[Score Update<br/>Redis + Cassandra<br/>Eventually Consistent<br/>Hot/Rising Algorithm]
    end

    subgraph VoteStorage[Vote Storage Strategy]
        REDIS_LIVE[Redis Live Scores<br/>Real-time Updates<br/>TTL: 24 hours<br/>Hot/Rising Calculation]

        CASSANDRA_VOTES[Cassandra Vote Log<br/>Immutable Audit Trail<br/>Partition: post_id<br/>Clustering: timestamp]

        REDSHIFT_ANALYSIS[Redshift Analytics<br/>Brigade Detection<br/>Vote Pattern Analysis<br/>Anomaly Detection]
    end

    subgraph AntiManipulation[Anti-Manipulation Measures]
        SHADOWBAN[Shadowban System<br/>Invalid votes ignored<br/>User unaware<br/>Bot protection]

        RATE_LIMIT[Rate Limiting<br/>Per-user quotas<br/>IP-based limits<br/>Burst protection]

        ML_DETECTION[ML Detection<br/>Vote ring analysis<br/>Coordinated attacks<br/>Real-time scoring]
    end

    USER_VOTE --> VOTE_VALIDATE
    VOTE_VALIDATE --> VOTE_FUZZER
    VOTE_FUZZER --> SCORE_UPDATE

    SCORE_UPDATE --> REDIS_LIVE
    SCORE_UPDATE --> CASSANDRA_VOTES
    CASSANDRA_VOTES --> REDSHIFT_ANALYSIS

    VOTE_VALIDATE --> SHADOWBAN
    VOTE_VALIDATE --> RATE_LIMIT
    REDSHIFT_ANALYSIS --> ML_DETECTION

    %% Styling
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class USER_VOTE,VOTE_VALIDATE,VOTE_FUZZER,SCORE_UPDATE serviceStyle
    class REDIS_LIVE,CASSANDRA_VOTES,REDSHIFT_ANALYSIS stateStyle
    class SHADOWBAN,RATE_LIMIT,ML_DETECTION controlStyle
```

## Data Consistency & Replication

```mermaid
graph TB
    subgraph ConsistencyModel[Reddit Consistency Model]
        STRONG_CONSISTENT[Strong Consistency<br/>• User authentication<br/>• Moderator actions<br/>• Ban enforcement<br/>PostgreSQL ACID]

        EVENTUAL_CONSISTENT[Eventual Consistency<br/>• Vote scores<br/>• Comment counts<br/>• Hot/Rising rankings<br/>Cassandra + Redis]

        CACHED_INCONSISTENT[Acceptable Inconsistency<br/>• CDN cached pages<br/>• View counts<br/>• Subscriber counts<br/>15-minute lag OK]
    end

    subgraph ReplicationStrategy[Multi-Region Replication]
        US_EAST[US-East Primary<br/>Read/Write<br/>150ms p99<br/>Users: 60%]

        US_WEST[US-West Replica<br/>Read-only<br/>Cross-region lag: 50ms<br/>Users: 25%]

        EU_WEST[EU-West Replica<br/>Read-only<br/>Cross-region lag: 120ms<br/>Users: 15%]
    end

    subgraph BackupStrategy[Backup & Recovery]
        CONTINUOUS_BACKUP[Continuous WAL Backup<br/>PostgreSQL<br/>Point-in-time Recovery<br/>RPO: 1 minute]

        SNAPSHOT_BACKUP[Daily Snapshots<br/>Cassandra<br/>Cross-region S3<br/>RTO: 4 hours]

        DISASTER_RECOVERY[Disaster Recovery<br/>Automated Failover<br/>Data Loss: <1 minute<br/>Downtime: <10 minutes]
    end

    STRONG_CONSISTENT --> US_EAST
    EVENTUAL_CONSISTENT --> US_EAST
    CACHED_INCONSISTENT --> US_EAST

    US_EAST --> US_WEST
    US_EAST --> EU_WEST

    US_EAST --> CONTINUOUS_BACKUP
    US_EAST --> SNAPSHOT_BACKUP
    CONTINUOUS_BACKUP --> DISASTER_RECOVERY

    %% Styling
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class STRONG_CONSISTENT,EVENTUAL_CONSISTENT,CACHED_INCONSISTENT serviceStyle
    class US_EAST,US_WEST,EU_WEST stateStyle
    class CONTINUOUS_BACKUP,SNAPSHOT_BACKUP,DISASTER_RECOVERY controlStyle
```

## Storage Performance Metrics

| Component | Capacity | Performance | Cost |
|-----------|----------|-------------|------|
| **Cassandra Primary** | 2.4 PB raw | 500K writes/sec | $4.2M/month |
| **Cassandra Replicas** | 1.8 PB raw | 2M reads/sec | $2.8M/month |
| **PostgreSQL Shards** | 80 TB total | 150K trans/sec | $1.23M/month |
| **Redis Cache** | 12 TB memory | 5M ops/sec | $4.575M/month |
| **CDN Storage** | 500 TB cached | 50M requests/sec | $2.1M/month |

## Key Storage Innovations

### 1. Materialized Comment Paths
- Pre-computed comment tree paths for fast retrieval
- Avoids recursive queries for nested comments
- Enables efficient pagination at any depth

### 2. Vote Score Fuzzing
- Adds ±1-3 random votes to displayed scores
- Prevents vote manipulation feedback loops
- Real scores stored separately for ranking

### 3. Hot Comment Caching
- Top 1000 comments per post cached in Redis
- Aggressive TTL refresh based on vote velocity
- Reduces Cassandra load by 85%

### 4. Subreddit Data Isolation
- Each subreddit as separate keyspace
- Prevents cross-contamination during brigades
- Enables per-community scaling policies

## Recovery Procedures

### Comment Tree Corruption
1. **Detection**: Orphaned comments, broken paths
2. **Recovery**: Rebuild from vote logs and edit history
3. **Time**: 2-4 hours for large threads
4. **Data Loss**: Comments posted during rebuild window

### Vote Manipulation Attack
1. **Detection**: ML models, vote velocity spikes
2. **Response**: Shadowban participants, recompute scores
3. **Time**: Real-time detection, 15-minute cleanup
4. **Impact**: Temporary ranking distortion

### Database Failover
1. **Primary Failure**: Automatic promotion of replica
2. **Recovery Time**: <10 minutes
3. **Data Loss**: <1 minute of writes
4. **Fallback**: Read-only mode during recovery

This storage architecture handles Reddit's unique challenges of deeply nested comment trees, democratic voting systems, and community-driven moderation while maintaining sub-second performance for hundreds of millions of users.