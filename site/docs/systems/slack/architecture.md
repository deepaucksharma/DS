# Slack Complete Architecture - Enterprise Messaging at Scale

## Overview
Slack's complete production architecture handling 20M daily active users, 10B+ messages per day, and 750K+ organizations with 99.99% uptime SLA.

## Complete System Architecture

```mermaid
graph TB
    subgraph "Edge Plane - CDN & Load Balancing"
        CDN[Cloudflare CDN<br/>2000+ edge locations<br/>$2.1M/month]
        ALB[AWS ALB<br/>Multi-AZ<br/>$180K/month]
        CF[CloudFront<br/>Asset delivery<br/>$420K/month]
    end

    subgraph "Service Plane - Application Layer"
        subgraph "WebSocket Services"
            WS1[WebSocket Servers<br/>c5.4xlarge × 450<br/>Java + Netty<br/>$1.8M/month]
            WS2[Connection Manager<br/>r5.2xlarge × 120<br/>Redis Cluster<br/>$480K/month]
        end

        subgraph "API Services"
            API[REST API Gateway<br/>c5.2xlarge × 380<br/>Node.js + Express<br/>$1.5M/month]
            MSG[Message Service<br/>c5.4xlarge × 200<br/>Go microservice<br/>$800K/month]
            FILE[File Service<br/>c5.xlarge × 150<br/>Multipart upload<br/>$600K/month]
            SEARCH[Search Service<br/>m5.2xlarge × 90<br/>Elasticsearch<br/>$540K/month]
            AUTH[Auth Service<br/>c5.large × 60<br/>OAuth + SAML<br/>$180K/month]
        end

        subgraph "Integration Platform"
            APP[App Platform<br/>c5.xlarge × 80<br/>10K+ integrations<br/>$320K/month]
            BOT[Bot Framework<br/>c5.large × 50<br/>Workflow engine<br/>$150K/month]
            WEBHOOK[Webhook Service<br/>c5.large × 40<br/>Event delivery<br/>$120K/month]
        end
    end

    subgraph "State Plane - Data & Storage"
        subgraph "Primary Storage"
            MYSQL[MySQL 8.0<br/>db.r5.24xlarge × 24<br/>Master-Replica<br/>$2.4M/month]
            SHARD[MySQL Shards<br/>db.r5.12xlarge × 180<br/>Channel partitioning<br/>$9.6M/month]
        end

        subgraph "Message Storage"
            ELASTIC[Elasticsearch<br/>r5.4xlarge × 300<br/>Message search<br/>$4.8M/month]
            S3[AWS S3<br/>500+ TB storage<br/>File attachments<br/>$2.1M/month]
            GLACIER[S3 Glacier<br/>50+ PB archive<br/>Compliance<br/>$1.2M/month]
        end

        subgraph "Caching Layer"
            REDIS[Redis Cluster<br/>r6g.2xlarge × 120<br/>Session + metadata<br/>$960K/month]
            MEMCACHE[ElastiCache<br/>r6g.xlarge × 80<br/>Message cache<br/>$480K/month]
        end

        subgraph "Analytics"
            ANALYTICS[ClickHouse<br/>r5.8xlarge × 60<br/>Usage analytics<br/>$1.8M/month]
            KAFKA[Kafka Cluster<br/>r5.2xlarge × 80<br/>Event streaming<br/>$640K/month]
        end
    end

    subgraph "Control Plane - Operations"
        subgraph "Monitoring"
            PROM[Prometheus<br/>c5.2xlarge × 40<br/>Metrics collection<br/>$320K/month]
            GRAFANA[Grafana<br/>c5.large × 20<br/>Dashboards<br/>$60K/month]
            DD[DataDog<br/>APM + Logging<br/>$890K/month]
        end

        subgraph "Infrastructure"
            K8S[Kubernetes<br/>EKS clusters × 12<br/>Service orchestration<br/>$240K/month]
            CONSUL[Consul<br/>Service discovery<br/>$80K/month]
            VAULT[HashiCorp Vault<br/>Secrets management<br/>$120K/month]
        end

        subgraph "CI/CD"
            JENKINS[Jenkins<br/>c5.xlarge × 30<br/>Build pipeline<br/>$180K/month]
            DEPLOY[Deployment<br/>Blue-green<br/>$90K/month]
        end
    end

    %% Connections
    CDN --> ALB
    ALB --> API
    ALB --> WS1
    CF --> FILE

    API --> MSG
    API --> FILE
    API --> SEARCH
    API --> AUTH
    MSG --> APP
    APP --> BOT
    APP --> WEBHOOK

    WS1 --> WS2
    WS2 --> REDIS

    MSG --> MYSQL
    MSG --> SHARD
    MSG --> ELASTIC
    FILE --> S3
    SEARCH --> ELASTIC

    MSG --> KAFKA
    KAFKA --> ANALYTICS

    MYSQL --> GLACIER
    S3 --> GLACIER

    %% Apply 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:3px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:3px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:3px

    class CDN,ALB,CF edgeStyle
    class WS1,WS2,API,MSG,FILE,SEARCH,AUTH,APP,BOT,WEBHOOK serviceStyle
    class MYSQL,SHARD,ELASTIC,S3,GLACIER,REDIS,MEMCACHE,ANALYTICS,KAFKA stateStyle
    class PROM,GRAFANA,DD,K8S,CONSUL,VAULT,JENKINS,DEPLOY controlStyle
```

## Architecture Highlights

### Real-Time Messaging Engine
- **450 WebSocket servers** (c5.4xlarge) handling 12M+ concurrent connections
- **Connection pooling** with sticky sessions for message ordering
- **Netty-based Java** application with custom protocol optimization
- **99.95% message delivery** SLA with < 100ms p99 latency

### Massive Scale Numbers
- **20M daily active users** across 750K+ organizations
- **10B+ messages per day** (116K messages/second peak)
- **2.5B file uploads per month** (97GB/second peak throughput)
- **500TB+ active storage** with 50PB+ archived data

### Enterprise Features
- **Data residency** across 15+ AWS regions for compliance
- **SSO integration** with 200+ identity providers
- **Advanced security** with SOC2, HIPAA, FedRAMP compliance
- **99.99% uptime SLA** with < 4 minutes downtime/month

### Cost Optimization
- **$78M/month total infrastructure** cost (20M DAU = $3.90/user/month)
- **MySQL sharding** reduces storage costs by 40% vs single cluster
- **S3 Glacier** archives 85% of data for 90% cost reduction
- **Reserved instances** save $18M/year (23% total reduction)

## Production Metrics

### Performance
- **Message latency**: p50: 12ms, p99: 89ms, p999: 340ms
- **File upload**: p99: 2.1s for 10MB files
- **Search response**: p99: 180ms for full-text queries
- **WebSocket connections**: 12M+ concurrent, 2% churn/hour

### Reliability
- **Uptime**: 99.993% (26 minutes downtime/year)
- **Message durability**: 99.999% (< 1 in 100K messages lost)
- **Recovery time**: < 5 minutes for regional failures
- **Backup restoration**: < 15 minutes RTO for critical data

### Resource Utilization
- **CPU**: 68% average across application tier
- **Memory**: 72% average with 20% headroom
- **Database**: 78% connection utilization peak
- **Network**: 2.1 Gbps average, 45 Gbps peak

## Technology Stack

### Core Technologies
- **Backend**: Java (WebSocket), Node.js (API), Go (messaging)
- **Database**: MySQL 8.0 with custom sharding
- **Search**: Elasticsearch 7.x with custom analyzers
- **Cache**: Redis Cluster 6.x, ElastiCache Memcached
- **Storage**: AWS S3, Glacier for archival

### Infrastructure
- **Cloud**: AWS (primary), multi-region deployment
- **Orchestration**: Kubernetes (EKS) with 12 production clusters
- **Service Discovery**: Consul with health checking
- **Load Balancing**: AWS ALB + Cloudflare for DDoS protection

## Security & Compliance

### Data Protection
- **Encryption**: AES-256 at rest, TLS 1.3 in transit
- **Key management**: HashiCorp Vault with HSM
- **Access controls**: RBAC with principle of least privilege
- **Audit logging**: All actions logged with 7-year retention

### Compliance Standards
- **SOC 2 Type II**: Annual audits with clean reports
- **HIPAA**: Healthcare customer compliance
- **FedRAMP**: Government customer authorization
- **GDPR**: EU data protection compliance

## Integration Ecosystem

### App Platform
- **10K+ published apps** in Slack App Directory
- **Custom integrations** for 95% of Fortune 100 companies
- **Webhook delivery**: 99.8% success rate, 3 retry attempts
- **Rate limiting**: 1K requests/minute per app by default

### Enterprise Connectors
- **Identity providers**: Okta, Azure AD, Ping Identity
- **Productivity tools**: Google Workspace, Microsoft 365
- **Development tools**: GitHub, Jira, Jenkins, PagerDuty
- **Business systems**: Salesforce, Workday, ServiceNow

*Based on Slack Engineering blog posts, QCon presentations, and public architecture discussions. Infrastructure costs estimated from AWS pricing for described instance types and usage patterns.*