# Pinterest Complete Architecture

## The Visual Discovery Money Shot

Pinterest operates as the world's largest visual discovery platform, serving 450M+ monthly active users with 200B+ pins through a sophisticated visual search and recommendation system built on graph neural networks.

```mermaid
graph TB
    subgraph "Edge Plane - Global CDN & Security"
        CDN[CloudFlare CDN<br/>300+ POPs<br/>p99: 15ms]
        LB[F5 BigIP LTM<br/>100Gbps<br/>99.99% SLA]
        WAF[Fastly Shield<br/>DDoS Protection<br/>500k RPS]
    end

    subgraph "Service Plane - Application Layer"
        AG[Kong API Gateway<br/>30k RPS per node<br/>Circuit breakers]
        WEB[Web Frontend<br/>React/Node.js<br/>300 instances]
        MOBILE[Mobile API<br/>Java Spring Boot<br/>500 instances]
        FEED[Feed Service<br/>Go 1.19<br/>200 instances]
        SEARCH[Search Service<br/>Elasticsearch<br/>100 instances]
        RECOM[Recommendation<br/>PinSage GraphSAGE<br/>50 GPU instances]
        VISION[Visual Search<br/>PyTorch/CUDA<br/>Tesla V100 GPUs]
        ML[ML Pipeline<br/>Airflow + Spark<br/>1000 cores]
    end

    subgraph "State Plane - Data & Storage"
        MYSQL[(MySQL 8.0<br/>Master-Slave<br/>1TB+ per shard)]
        HBASE[(HBase 2.4<br/>Pin Metadata<br/>100TB+ cluster)]
        REDIS[(Redis Cluster<br/>Hot Pins Cache<br/>256GB RAM)]
        S3[(AWS S3<br/>Image Storage<br/>50PB+ data)]
        ES[(Elasticsearch 7.x<br/>Search Index<br/>10TB cluster)]
        GRAPH[(Graph Database<br/>Neo4j + Custom<br/>200B edges)]
        KAFKA[(Kafka Cluster<br/>Event Streaming<br/>1M msgs/sec)]
        SPARK[(Spark Cluster<br/>Batch Processing<br/>2000 cores)]
    end

    subgraph "Control Plane - Operations"
        MON[DataDog + Custom<br/>100k metrics/sec<br/>p99 alerts]
        LOG[ELK Stack<br/>500GB/day logs<br/>7 day retention]
        DEPLOY[Spinnaker CD<br/>Blue-Green<br/>1000 deploys/day]
        CONFIG[ZooKeeper<br/>Config Management<br/>5-node cluster]
    end

    %% User flows
    USER[450M MAU<br/>Mobile: 85%<br/>Web: 15%] --> CDN
    CDN --> LB
    LB --> WAF
    WAF --> AG

    %% API routing
    AG --> WEB
    AG --> MOBILE
    AG --> FEED
    AG --> SEARCH

    %% Service interconnections
    FEED --> RECOM
    SEARCH --> VISION
    RECOM --> ML
    VISION --> ML

    %% Data layer connections
    WEB --> REDIS
    WEB --> MYSQL
    MOBILE --> REDIS
    MOBILE --> MYSQL
    FEED --> HBASE
    FEED --> REDIS
    SEARCH --> ES
    RECOM --> GRAPH
    RECOM --> HBASE
    VISION --> S3
    ML --> KAFKA
    ML --> SPARK

    %% Storage interconnections
    MYSQL --> KAFKA
    HBASE --> KAFKA
    KAFKA --> SPARK
    SPARK --> GRAPH
    SPARK --> ES

    %% Monitoring connections
    MON -.-> WEB
    MON -.-> MOBILE
    MON -.-> FEED
    MON -.-> SEARCH
    MON -.-> RECOM
    LOG -.-> KAFKA
    DEPLOY -.-> CONFIG

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:3px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:3px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:3px

    class CDN,LB,WAF edgeStyle
    class AG,WEB,MOBILE,FEED,SEARCH,RECOM,VISION,ML serviceStyle
    class MYSQL,HBASE,REDIS,S3,ES,GRAPH,KAFKA,SPARK stateStyle
    class MON,LOG,DEPLOY,CONFIG controlStyle
```

## Production Metrics & Scale

### Performance Characteristics
- **Pin Discovery Feed**: p99 < 150ms (global)
- **Visual Search**: p95 < 300ms (computer vision inference)
- **Pin Save**: p99 < 50ms (write path)
- **Image Upload**: p95 < 2s (including CDN propagation)

### Infrastructure Scale
- **Compute**: 5,000+ EC2 instances (c5.4xlarge - c5.24xlarge)
- **Storage**: 50PB+ in S3, 100TB+ in HBase
- **Network**: 100Gbps backbone, 300+ CDN POPs
- **GPUs**: 200+ Tesla V100s for ML inference

### Business Impact
- **Monthly Cost**: ~$45M infrastructure spend
- **Revenue**: $2.8B annually (2022)
- **Cost per MAU**: ~$8.33/month
- **Ad Revenue per User**: ~$5.20/month

## Critical Production Dependencies

### Core Data Flow
1. **Pin Creation**: User uploads → S3 → Vision AI → Metadata → HBase
2. **Feed Generation**: User request → PinSage GNN → Ranking → Redis cache
3. **Visual Search**: Image query → CNN feature extraction → Similarity search
4. **Shopping Flow**: Product detection → Shopping graph → Recommendation

### Failure Recovery
- **Image CDN**: 99.99% availability with multi-region failover
- **Recommendation**: Graceful degradation to popularity-based ranking
- **Search**: Elasticsearch cluster with cross-region replication
- **Database**: MySQL with 5-second failover, HBase with automatic region balancing

## Real Production Incidents

### October 2022: PinSage Model Corruption
- **Impact**: 30% drop in engagement for 45 minutes
- **Root Cause**: Corrupted model weights during A/B test deployment
- **Resolution**: Automatic rollback to previous model version
- **Learning**: Added model validation checksums

### March 2023: Visual Search Overload
- **Impact**: 200% increase in visual search latency
- **Root Cause**: Viral pin caused 10x traffic spike
- **Resolution**: Auto-scaling GPU instances + circuit breaker
- **Learning**: Added predictive scaling based on pin virality

*Sources: Pinterest Engineering Blog, QCon presentations, SREcon talks*