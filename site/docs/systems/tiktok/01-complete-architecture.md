# TikTok Complete Architecture

## Complete System Overview - "The Money Shot"

TikTok's architecture serves 1B+ users with 1B+ videos watched daily and 150M+ daily uploads. The system processes 100TB+ of new video content daily while delivering personalized For You Page experiences with sub-100ms latency for recommendation serving.

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - CDN & Load Balancing]
        CDN1[BytePlus CDN<br/>400+ PoPs Global<br/>$8M/month]
        CDN2[AWS CloudFront<br/>Fallback CDN<br/>$2M/month]
        LB[Global Load Balancer<br/>AWS ALB + Route 53<br/>99.99% uptime]
        WAF[CloudFlare WAF<br/>DDoS Protection<br/>10M+ req/sec capacity]
    end

    subgraph ServicePlane[Service Plane - Business Logic]
        APIGW[Kong API Gateway<br/>c5.24xlarge × 50<br/>200K req/sec]

        subgraph CoreServices[Core Services]
            VS[Video Service<br/>Go + gRPC<br/>c5.18xlarge × 200]
            RS[Recommendation Engine<br/>C++ + TensorFlow<br/>p3.16xlarge × 150]
            US[User Service<br/>Java Spring Boot<br/>c5.12xlarge × 100]
            IS[Interaction Service<br/>Node.js<br/>c5.9xlarge × 80]
        end

        subgraph MLPipeline[ML Pipeline]
            FS[Feature Store<br/>Redis Cluster<br/>r6g.16xlarge × 50]
            MS[Model Serving<br/>TensorFlow Serving<br/>p3.8xlarge × 200]
            TR[Real-time Training<br/>PyTorch on k8s<br/>p4d.24xlarge × 30]
        end
    end

    subgraph StatePlane[State Plane - Data & Storage]
        subgraph VideoStorage[Video Storage]
            S3[AWS S3<br/>Petabyte-scale<br/>Standard + IA + Glacier<br/>$12M/month]
            HDFS[Hadoop HDFS<br/>On-premise clusters<br/>50PB+ storage]
        end

        subgraph Databases[Databases]
            MYSQL[MySQL Clusters<br/>Master-Slave<br/>db.r6g.16xlarge × 200<br/>Sharded by user_id]
            REDIS[Redis Clusters<br/>Session + Cache<br/>r6g.16xlarge × 100<br/>100TB+ memory]
            CASSANDRA[Cassandra<br/>Time-series data<br/>i3.16xlarge × 300]
        end

        subgraph Analytics[Analytics & ML Data]
            KAFKA[Apache Kafka<br/>Event streaming<br/>r5.12xlarge × 80<br/>50M+ events/sec]
            SPARK[Spark Clusters<br/>Batch processing<br/>r5.24xlarge × 500]
            FLINK[Apache Flink<br/>Real-time processing<br/>c5.18xlarge × 100]
        end
    end

    subgraph ControlPlane[Control Plane - Operations]
        MON[DataDog + Grafana<br/>Custom metrics<br/>$500K/month]
        LOG[ELK Stack<br/>c5.18xlarge × 50<br/>100TB+ logs/day]
        CONFIG[Consul + Vault<br/>Service discovery<br/>m5.2xlarge × 20]
        DEPLOY[Jenkins + ArgoCD<br/>CI/CD Pipeline<br/>10K+ deploys/day]
    end

    %% User Flow
    USERS[1B+ Active Users<br/>150M+ creators<br/>Peak: 15M concurrent] --> CDN1
    USERS --> CDN2
    CDN1 --> LB
    CDN2 --> LB

    %% Edge to Service Flow
    WAF --> APIGW
    LB --> WAF
    APIGW --> VS
    APIGW --> RS
    APIGW --> US
    APIGW --> IS

    %% Service to ML Flow
    RS --> FS
    RS --> MS
    MS --> TR

    %% Service to State Flow
    VS --> S3
    VS --> HDFS
    US --> MYSQL
    IS --> REDIS
    RS --> CASSANDRA

    %% Analytics Flow
    VS --> KAFKA
    US --> KAFKA
    IS --> KAFKA
    KAFKA --> SPARK
    KAFKA --> FLINK
    SPARK --> TR
    FLINK --> FS

    %% Control Plane Monitoring
    MON -.-> APIGW
    MON -.-> VS
    MON -.-> RS
    LOG -.-> KAFKA
    CONFIG -.-> CoreServices
    DEPLOY -.-> CoreServices

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff,stroke-width:2px
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff,stroke-width:2px
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff,stroke-width:2px

    class CDN1,CDN2,LB,WAF edgeStyle
    class APIGW,VS,RS,US,IS,FS,MS,TR edgeStyle
    class S3,HDFS,MYSQL,REDIS,CASSANDRA,KAFKA,SPARK,FLINK stateStyle
    class MON,LOG,CONFIG,DEPLOY controlStyle
```

## Key Architecture Metrics

### Scale Metrics
- **Daily Active Users**: 1B+ (peak 1.2B)
- **Video Uploads**: 150M+ per day
- **Video Views**: 1B+ per day
- **Peak Concurrent Users**: 15M+
- **Global Data Centers**: 12 primary regions
- **CDN Points of Presence**: 400+ globally

### Performance SLAs
- **For You Page Load**: p99 < 200ms
- **Video Start Time**: p95 < 1s
- **Recommendation Latency**: p99 < 100ms
- **Upload Processing**: p95 < 30s
- **Search Results**: p99 < 150ms

### Infrastructure Scale
- **Compute Instances**: 3,000+ EC2 instances
- **Storage**: 50PB+ across S3 + HDFS
- **Memory Cache**: 100TB+ Redis
- **Network**: 500Gbps+ peak bandwidth
- **ML Models**: 200+ production models

### Cost Breakdown (Monthly)
- **Compute (EC2/GPU)**: $45M
- **Storage (S3/EBS)**: $12M
- **CDN & Bandwidth**: $10M
- **ML Infrastructure**: $8M
- **Monitoring & Tools**: $1M
- **Total**: ~$76M/month

## Critical Components

### 1. Recommendation Engine (Heart of TikTok)
- **Technology**: C++ with TensorFlow for inference
- **Scale**: 1B+ recommendations per day
- **Latency**: p99 < 100ms for recommendation scoring
- **Features**: 10,000+ features per user/video pair
- **Models**: Collaborative filtering + Deep learning hybrid

### 2. Video Processing Pipeline
- **Ingestion**: 150M+ videos per day
- **Transcoding**: Multiple resolutions (240p to 4K)
- **Compression**: H.264/H.265 with 40-60% size reduction
- **Effects**: Real-time filters and AR processing
- **Moderation**: AI-powered content screening

### 3. Global CDN Strategy
- **Primary**: BytePlus CDN (ByteDance's own)
- **Fallback**: AWS CloudFront for reliability
- **Cache Strategy**: 90%+ hit rate for popular videos
- **Geographic Distribution**: Sub-50ms latency globally

### 4. Real-time Data Pipeline
- **Event Volume**: 50M+ events per second
- **Processing**: Apache Kafka + Flink for real-time
- **Batch Processing**: Spark for model training data
- **Feature Updates**: Real-time feature store updates

## Novel Technical Solutions

### 1. Multi-Armed Bandit Recommendations
- Exploration vs exploitation for new videos
- Real-time learning from user interactions
- Cold start problem for new users/creators

### 2. Edge-based Video Processing
- Distributed transcoding at CDN edge
- Reduces origin server load by 70%
- Faster video availability globally

### 3. Predictive Prefetching
- ML-powered prediction of next videos
- Preloads videos before user swipe
- Reduces perceived latency to near-zero

### 4. Cross-Border Data Optimization
- Regional data residency compliance
- Optimized cross-region replication
- Smart routing based on data sovereignty

This architecture enables TikTok to serve personalized video content to over 1 billion users while maintaining sub-second video start times and highly engaging recommendation accuracy, all while processing 100TB+ of new content daily.