# Reddit Complete Architecture: The Front Page of the Internet at Scale

## Executive Summary
Reddit serves 500M+ MAU, 50M+ DAU, hosts 100K+ active communities, processes 18B+ votes/year, with 99.9% availability on $35M/month infrastructure.

## Complete System Architecture

```mermaid
graph TB
    subgraph "Reddit Production Architecture - 2024"
        subgraph EdgePlane[Edge Plane - Global Access]
            FASTLY[Fastly CDN<br/>150 PoPs<br/>$2M/month]
            CF[Cloudflare DDoS<br/>Protection<br/>$500K/month]
            ALB[AWS ALB Fleet<br/>50 instances<br/>5M req/sec]
        end

        subgraph ServicePlane[Service Plane - Core Services]
            subgraph WebTier[Web Services]
                MONOLITH[Python Monolith<br/>r2<br/>1000 servers]
                API[Public API<br/>GraphQL<br/>200 servers]
                MOBILE[Mobile API<br/>300 servers<br/>iOS/Android]
            end

            subgraph CommentTree[Comment System]
                COMMENT[Comment Service<br/>Go<br/>500 servers]
                TREE[Tree Builder<br/>Cassandra backed<br/>200 servers]
                SORT[Sorting Service<br/>Hot/Best/Top<br/>100 servers]
            end

            subgraph VotingSystem[Voting Engine]
                VOTE[Vote Processor<br/>Kafka consumer<br/>300 servers]
                ANTICHEAT[Anti-Brigade<br/>ML models<br/>100 servers]
                KARMA[Karma Calculator<br/>Redis backed<br/>50 servers]
            end

            subgraph FeedGeneration[Feed Services]
                HOME[Home Feed<br/>ML ranking<br/>400 servers]
                POPULAR[r/popular<br/>200 servers]
                TRENDING[Trending<br/>Real-time<br/>100 servers]
            end

            subgraph MediaPlatform[Media Services]
                IMAGE[Image Hosting<br/>i.redd.it<br/>200 servers]
                VIDEO[Video Platform<br/>v.redd.it<br/>300 servers]
                GALLERY[Gallery Service<br/>100 servers]
            end
        end

        subgraph StatePlane[State Plane - Data Storage]
            subgraph PrimaryData[Primary Storage]
                POSTGRES[PostgreSQL<br/>100 shards<br/>10TB]
                CASSANDRA[Cassandra<br/>1000 nodes<br/>100TB comments]
                REDIS[Redis Fleet<br/>500 nodes<br/>5TB cache]
            end

            subgraph TimeSeriesData[Time Series]
                DRUID[Apache Druid<br/>Analytics<br/>50 nodes]
                KAFKA[Kafka Cluster<br/>100 brokers<br/>1M msgs/sec]
                HBASE[HBase<br/>Vote history<br/>200 nodes]
            end

            subgraph MediaStorage[Media Storage]
                S3[S3 Storage<br/>Images/videos<br/>1PB]
                IMGIX[Imgix CDN<br/>Image processing<br/>$1M/month]
            end

            subgraph SearchIndex[Search Infrastructure]
                ELASTIC[Elasticsearch<br/>500 nodes<br/>10TB index]
                LUCIDWORKS[Lucidworks Fusion<br/>ML search<br/>50 nodes]
            end
        end

        subgraph ControlPlane[Control Plane - Operations]
            subgraph Monitoring[Observability]
                DATADOG[Datadog<br/>1B metrics/day<br/>$2M/month]
                SENTRY[Sentry<br/>Error tracking<br/>10M events/day]
                GRAFANA[Grafana<br/>Custom dashboards<br/>500 dashboards]
            end

            subgraph Security[Security & Trust]
                AUTOMOD[AutoModerator<br/>100M actions/day]
                CROWD[Crowd Control<br/>Brigade detection]
                SAFETY[Safety Team Tools<br/>Content moderation]
            end

            subgraph MLPlatform[ML Infrastructure]
                MLFLOW[MLflow<br/>Model registry<br/>500 models]
                SAGEMAKER[SageMaker<br/>Training/inference<br/>$1M/month]
                FEATURE[Feature Store<br/>Real-time features]
            end
        end

        %% Connections
        FASTLY --> ALB
        ALB --> MONOLITH
        ALB --> API

        MONOLITH --> POSTGRES
        MONOLITH --> REDIS
        API --> POSTGRES

        COMMENT --> CASSANDRA
        TREE --> CASSANDRA
        VOTE --> KAFKA
        KAFKA --> HBASE

        HOME --> REDIS
        HOME --> MLFLOW
        ANTICHEAT --> SAGEMAKER

        IMAGE --> S3
        VIDEO --> S3
        S3 --> IMGIX
    end

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class FASTLY,CF,ALB edgeStyle
    class MONOLITH,API,MOBILE,COMMENT,TREE,SORT,VOTE,ANTICHEAT,KARMA,HOME,POPULAR,TRENDING,IMAGE,VIDEO,GALLERY serviceStyle
    class POSTGRES,CASSANDRA,REDIS,DRUID,KAFKA,HBASE,S3,IMGIX,ELASTIC,LUCIDWORKS stateStyle
    class DATADOG,SENTRY,GRAFANA,AUTOMOD,CROWD,SAFETY,MLFLOW,SAGEMAKER,FEATURE controlStyle
```

## Infrastructure Scale Metrics

### Traffic Volume
```yaml
user_metrics:
  monthly_active_users: 500M+
  daily_active_users: 50M+
  peak_concurrent: 5M
  pageviews_per_day: 1B+

content_metrics:
  active_communities: 100K+
  posts_per_day: 2M+
  comments_per_day: 10M+
  votes_per_day: 50M+

api_traffic:
  third_party_apps: 10K+
  api_requests_per_day: 10B+
  apollo_users: 1.5M (before shutdown)
  bot_traffic: 20% of total
```

### Hardware Specifications
```python
infrastructure_specs = {
    "web_tier": {
        "server_type": "c5.4xlarge",
        "cpu": "16 vCPUs",
        "memory": "32GB",
        "count": 1000,
        "monthly_cost": "$400K"
    },
    "comment_storage": {
        "cassandra_nodes": 1000,
        "node_type": "i3.4xlarge",
        "storage": "2x 1.9TB NVMe",
        "memory": "122GB",
        "monthly_cost": "$800K"
    },
    "postgresql_cluster": {
        "shards": 100,
        "shard_type": "db.r6g.4xlarge",
        "storage": "100GB SSD each",
        "replicas": 2,
        "monthly_cost": "$200K"
    },
    "redis_fleet": {
        "nodes": 500,
        "node_type": "cache.r6g.xlarge",
        "memory": "13GB each",
        "total_memory": "6.5TB",
        "monthly_cost": "$150K"
    }
}
```

## Unique Architectural Components

### Comment Tree System
```python
class RedditCommentTree:
    """Reddit's nested comment architecture"""

    def __init__(self):
        self.storage = {
            "backend": "Cassandra",
            "partitioning": "By thread_id",
            "sorting": "Hot, Best, Top, New, Controversial",
            "max_depth": 10,  # Comment nesting limit
            "pagination": "Load more comments dynamically"
        }

    def build_comment_tree(self, thread_id):
        # Efficient tree building from flat structure
        comments = self.cassandra.query(
            "SELECT * FROM comments WHERE thread_id = ?",
            thread_id
        )

        # Build tree structure in memory
        tree = self.construct_tree(comments)

        # Apply sorting algorithm
        sorted_tree = self.apply_sort(tree, sort_type="best")

        # Cache in Redis for fast access
        self.redis.setex(
            f"tree:{thread_id}",
            ttl=300,  # 5 minute cache
            value=sorted_tree
        )

        return sorted_tree

    def handle_vote(self, comment_id, vote_type):
        # Real-time vote processing
        return {
            "update_score": self.update_comment_score(comment_id, vote_type),
            "recalculate_position": self.recalculate_tree_position(comment_id),
            "invalidate_cache": self.invalidate_tree_cache(comment_id),
            "anti_brigade_check": self.check_vote_manipulation(comment_id)
        }
```

### Voting System Architecture
```yaml
voting_pipeline:
  ingestion:
    endpoint: "POST /api/vote"
    rate_limit: "100 votes/minute/user"
    authentication: "OAuth2 token required"

  processing:
    queue: "Kafka"
    partitions: 1000
    throughput: "1M votes/second"
    processors: 300

  anti_cheat:
    brigade_detection:
      - "Sudden vote velocity changes"
      - "Coordinated voting patterns"
      - "Account age and karma checks"

    shadowban_system:
      - "Votes appear to count but don't"
      - "Comments visible only to user"
      - "No notification of ban"

  storage:
    hot_votes: "Redis - last 24 hours"
    recent_votes: "PostgreSQL - last 30 days"
    archive: "HBase - all historical votes"
```

### Feed Generation System
```python
class RedditFeedGenerator:
    """Personalized feed generation using ML"""

    def __init__(self):
        self.models = {
            "content_ranking": "XGBoost model",
            "user_interests": "Collaborative filtering",
            "trending_detection": "Time series analysis",
            "nsfw_filtering": "CNN classifier"
        }

    def generate_home_feed(self, user_id):
        # Get user's subscriptions
        subscriptions = self.get_user_subscriptions(user_id)

        # Fetch candidate posts
        candidates = self.fetch_candidate_posts(subscriptions)

        # Apply ML ranking
        ranked_posts = self.ml_rank_posts(candidates, user_id)

        # Apply business rules
        filtered_posts = self.apply_filters(ranked_posts, user_id)

        # Cache feed
        self.cache_feed(user_id, filtered_posts)

        return filtered_posts

    def ml_rank_posts(self, posts, user_id):
        features = self.extract_features(posts, user_id)
        scores = self.ranking_model.predict(features)
        return sorted(zip(posts, scores), key=lambda x: x[1], reverse=True)
```

## Performance Characteristics

### Latency Targets
| Operation | p50 | p95 | p99 | SLO |
|-----------|-----|-----|-----|-----|
| Page Load | 200ms | 500ms | 1s | < 1s |
| Vote Submit | 50ms | 150ms | 300ms | < 500ms |
| Comment Post | 100ms | 300ms | 500ms | < 1s |
| Feed Generation | 150ms | 400ms | 800ms | < 1s |
| Search Query | 200ms | 600ms | 1.5s | < 2s |
| Image Upload | 500ms | 2s | 5s | < 10s |

### Throughput Metrics
```python
throughput_capabilities = {
    "votes_per_second": "50K sustained, 200K peak",
    "comments_per_second": "10K sustained, 50K peak",
    "pageviews_per_second": "1M sustained, 3M peak",
    "api_requests_per_second": "100K sustained",
    "search_queries_per_second": "10K",
    "automod_actions_per_second": "1K"
}
```

## Reliability Engineering

### Multi-Region Architecture
```mermaid
graph LR
    subgraph Primary[US-East Primary]
        USE[Full Stack<br/>PostgreSQL primary<br/>Cassandra primary]
    end

    subgraph Secondary[US-West Secondary]
        USW[Read replicas<br/>Cassandra replica<br/>Failover ready]
    end

    subgraph Cache[Global Cache]
        CDN1[Fastly PoPs<br/>150 locations]
        CDN2[CloudFlare<br/>Backup CDN]
    end

    USE -->|Sync| USW
    USE --> CDN1
    USW --> CDN2

    style USE fill:#10B981
    style USW fill:#F59E0B
    style CDN1 fill:#3B82F6
```

## Cost Breakdown Summary

```python
monthly_infrastructure_costs = {
    "compute": {
        "web_servers": "$2M",
        "api_servers": "$1M",
        "ml_infrastructure": "$1M"
    },
    "storage": {
        "databases": "$1.5M",
        "media_storage": "$2M",
        "backups": "$500K"
    },
    "network": {
        "cdn": "$2.5M",
        "bandwidth": "$3M"
    },
    "services": {
        "monitoring": "$2M",
        "security": "$1M"
    },
    "total": "$35M/month",
    "cost_per_user": "$0.07/month",
    "revenue_per_user": "$0.35/month"
}
```

## The Community-Driven Architecture

### Moderation at Scale
```yaml
moderation_system:
  automod:
    rules_evaluated: 100M/day
    actions_taken: 10M/day
    custom_rules: 1M+ across subreddits

  human_moderators:
    volunteer_mods: 140K+
    mod_actions: 50M/month
    mod_tools: "Custom mod queue, mod mail, toolbox"

  admin_team:
    trust_safety: 200+ employees
    anti_evil_ops: 24/7 coverage
    policy_enforcement: "Site-wide rules"
```

## Key Innovations

1. **ThingDB**: Custom object storage for posts/comments
2. **Vote Fuzzing**: Anti-gaming mechanism for vote counts
3. **Comment Threading**: Efficient nested discussion at scale
4. **AutoModerator**: Community-configurable automation
5. **Brigade Detection**: ML-based coordinated behavior detection
6. **Shadowban System**: Silent account restrictions
7. **Community Points**: Blockchain-based rewards (select subreddits)

*"Reddit's architecture is optimized for community-driven content and democratic voting at massive scale."* - Reddit Principal Engineer