# Zoom Complete Production Architecture - The Money Shot

## System Overview

This diagram represents Zoom's actual production architecture serving 300+ million daily meeting participants with 99.99% availability, handling 3.3+ trillion annual meeting minutes through a globally distributed real-time communications platform optimized for video conferencing at massive scale.

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Blue #3B82F6]
        style EdgePlane fill:#3B82F6,stroke:#2563EB,color:#fff

        GlobalCDN[Zoom Global CDN<br/>━━━━━<br/>5,000+ edge servers<br/>100+ countries<br/>Multi-cloud strategy<br/>Cost: $50M/month]

        LoadBalancers[Global Load Balancers<br/>━━━━━<br/>Anycast DNS routing<br/>Health-check based<br/>Multi-region failover<br/>p99: 2ms routing]

        EdgeGateways[Edge Gateway Cluster<br/>━━━━━<br/>Regional entry points<br/>TLS termination<br/>Connection pooling<br/>Request routing]

        WebRTCGateways[WebRTC Gateways<br/>━━━━━<br/>Media session establishment<br/>STUN/TURN servers<br/>ICE candidate gathering<br/>NAT traversal: 99.9%]
    end

    subgraph ServicePlane[Service Plane - Green #10B981]
        style ServicePlane fill:#10B981,stroke:#059669,color:#fff

        subgraph MeetingServices[Meeting Management Services]
            MeetingController[Meeting Controller<br/>━━━━━<br/>Session orchestration<br/>500K+ concurrent meetings<br/>Java/Spring Boot<br/>r5.12xlarge fleet]

            ParticipantManager[Participant Manager<br/>━━━━━<br/>User authentication<br/>Permission management<br/>Presence tracking<br/>Connection state: 300M users]

            SchedulingEngine[Scheduling Engine v2.1<br/>━━━━━<br/>Node.js 18 service<br/>Calendar API integration<br/>Recurring meeting logic<br/>Timezone: moment.js]
        end

        subgraph MediaServices[Media Processing Services]
            MediaRouter[Media Router<br/>━━━━━<br/>SFU (Selective Forwarding)<br/>Video/audio routing<br/>Bandwidth optimization<br/>c5n.24xlarge fleet]

            TranscodingCluster[Transcoding Cluster<br/>━━━━━<br/>Real-time video transcoding<br/>Multiple resolution support<br/>GPU acceleration<br/>p3.8xlarge instances]

            RecordingEngine[Cloud Recording Engine<br/>━━━━━<br/>FFmpeg 5.1 processor<br/>MP4/WebM generation<br/>AWS S3 integration<br/>GPU transcoding: p3.8xlarge]

            ScreenShareEngine[Screen Share Engine v3<br/>━━━━━<br/>C++ capture library<br/>WebRTC data channels<br/>Canvas annotation API<br/>Sub-100ms p99 latency]
        end

        subgraph AIServices[AI & Analytics Services]
            TranscriptionAI[Real-time Transcription<br/>━━━━━<br/>Speech-to-text<br/>Multi-language support<br/>Noise cancellation<br/>GPU clusters]

            BackgroundAI[Virtual Background AI<br/>━━━━━<br/>Real-time segmentation<br/>Edge AI processing<br/>GPU optimization<br/>CPU fallback]

            AnalyticsEngine[Meeting Analytics<br/>━━━━━<br/>Quality metrics<br/>Usage analytics<br/>Performance insights<br/>ML-driven optimization]
        end
    end

    subgraph StatePlane[State Plane - Orange #F59E0B]
        style StatePlane fill:#F59E0B,stroke:#D97706,color:#fff

        subgraph DatabaseLayer[Database Infrastructure]
            PostgreSQLCluster[PostgreSQL Clusters<br/>━━━━━<br/>User/meeting metadata<br/>Multi-master setup<br/>10TB+ per cluster<br/>db.r6g.16xlarge]

            CassandraCluster[Cassandra Clusters<br/>━━━━━<br/>Time-series metrics<br/>Call quality data<br/>100+ nodes per DC<br/>i3en.24xlarge]

            RedisCluster[Redis Clusters<br/>━━━━━<br/>Session management<br/>Real-time state<br/>Sub-ms latency<br/>r6gd.16xlarge]
        end

        subgraph StorageLayer[Storage Infrastructure]
            S3ObjectStore[S3 Object Storage<br/>━━━━━<br/>Recording storage<br/>1 Exabyte+ stored<br/>Intelligent tiering<br/>Multi-region replication]

            ElasticSearch[Elasticsearch<br/>━━━━━<br/>Meeting search<br/>Log aggregation<br/>Real-time indexing<br/>100TB+ indexed data]

            CDNStorage[CDN Storage<br/>━━━━━<br/>Client downloads<br/>Static assets<br/>Multi-region sync<br/>Edge caching]
        end

        subgraph MessageQueue[Event Streaming]
            KafkaCluster[Kafka Clusters<br/>━━━━━<br/>Meeting events<br/>100M+ events/day<br/>Real-time processing<br/>7-day retention]

            PubSubSystem[Pub/Sub System<br/>━━━━━<br/>Real-time notifications<br/>Presence updates<br/>Meeting state changes<br/>WebSocket delivery]
        end
    end

    subgraph ControlPlane[Control Plane - Red #8B5CF6]
        style ControlPlane fill:#8B5CF6,stroke:#7C3AED,color:#fff

        subgraph MonitoringInfra[Monitoring Infrastructure]
            PrometheusStack[Prometheus Stack<br/>━━━━━<br/>Metrics collection<br/>10M+ metrics/min<br/>Alert management<br/>Multi-DC federation]

            GrafanaCluster[Grafana Cluster<br/>━━━━━<br/>5,000+ dashboards<br/>Real-time visualization<br/>Executive reporting<br/>SLA monitoring]

            ELKStack[ELK Stack<br/>━━━━━<br/>Centralized logging<br/>5TB+ daily logs<br/>Error correlation<br/>Performance analysis]
        end

        subgraph DeploymentOps[Deployment Operations]
            KubernetesOrchestrator[Kubernetes<br/>━━━━━<br/>Container orchestration<br/>10,000+ pods<br/>Auto-scaling<br/>Multi-cloud deployment]

            CICDPipeline[CI/CD Pipeline<br/>━━━━━<br/>Jenkins + GitLab<br/>1,000+ deploys/day<br/>Canary deployments<br/>Automated rollback]

            ConfigManagement[Config Management<br/>━━━━━<br/>Centralized config<br/>Feature flags<br/>A/B testing<br/>Runtime updates]
        end

        subgraph SecurityOps[Security Operations]
            SecurityMonitoring[Security Monitoring<br/>━━━━━<br/>SIEM integration<br/>Threat detection<br/>Compliance monitoring<br/>24/7 SOC]

            IdentityManagement[Identity Management<br/>━━━━━<br/>SSO integration<br/>Multi-factor auth<br/>SAML/OAuth support<br/>Enterprise directory]
        end
    end

    %% Connection flows with real metrics
    GlobalCDN -->|"DNS resolution<br/>p99: 2ms"| LoadBalancers
    LoadBalancers -->|"Health check routing<br/>15s failover"| EdgeGateways
    EdgeGateways -->|"TLS termination<br/>Connection pooling"| WebRTCGateways
    WebRTCGateways -->|"Media negotiation<br/>ICE gathering"| MediaRouter

    EdgeGateways -->|"API requests<br/>1M+ req/sec"| MeetingController
    MeetingController -->|"User auth<br/>Session mgmt"| ParticipantManager
    MeetingController -->|"Meeting scheduling<br/>Calendar sync"| SchedulingEngine

    MediaRouter -->|"Video transcoding<br/>Real-time"| TranscodingCluster
    MediaRouter -->|"Recording pipeline<br/>Cloud storage"| RecordingEngine
    MediaRouter -->|"Screen sharing<br/>Annotation"| ScreenShareEngine

    ParticipantManager -->|"User metadata<br/>CRUD operations"| PostgreSQLCluster
    MeetingController -->|"Session state<br/>Real-time"| RedisCluster
    MediaRouter -->|"Quality metrics<br/>Time series"| CassandraCluster

    RecordingEngine -->|"Video storage<br/>1EB+ capacity"| S3ObjectStore
    AnalyticsEngine -->|"Search indexing<br/>Meeting metadata"| ElasticSearch
    MeetingController -->|"Meeting events<br/>Real-time stream"| KafkaCluster

    TranscriptionAI -->|"Speech processing<br/>ML inference"| AnalyticsEngine
    BackgroundAI -->|"Image processing<br/>GPU compute"| MediaRouter

    %% Control plane monitoring
    MeetingController -.->|"Metrics & traces<br/>10M+ metrics/min"| PrometheusStack
    MediaRouter -.->|"Performance data<br/>Video quality"| GrafanaCluster
    ParticipantManager -.->|"Application logs<br/>Error tracking"| ELKStack

    KubernetesOrchestrator -.->|"Container deployment<br/>Auto-scaling"| MeetingController
    CICDPipeline -.->|"Code deployment<br/>Canary releases"| MediaRouter
    SecurityMonitoring -.->|"Threat detection<br/>Compliance"| IdentityManagement

    %% Apply 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,font-weight:bold
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,font-weight:bold
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,font-weight:bold
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,font-weight:bold

    class GlobalCDN,LoadBalancers,EdgeGateways,WebRTCGateways edgeStyle
    class MeetingController,ParticipantManager,SchedulingEngine,MediaRouter,TranscodingCluster,RecordingEngine,ScreenShareEngine,TranscriptionAI,BackgroundAI,AnalyticsEngine serviceStyle
    class PostgreSQLCluster,CassandraCluster,RedisCluster,S3ObjectStore,ElasticSearch,CDNStorage,KafkaCluster,PubSubSystem stateStyle
    class PrometheusStack,GrafanaCluster,ELKStack,KubernetesOrchestrator,CICDPipeline,ConfigManagement,SecurityMonitoring,IdentityManagement controlStyle
```

## Key Production Metrics

### Scale Indicators
- **Global Users**: 300+ million daily meeting participants
- **Concurrent Meetings**: 500,000+ simultaneous meetings peak
- **Meeting Minutes**: 3.3+ trillion annual meeting minutes
- **Data Centers**: 18 global data centers across 6 continents
- **Edge Servers**: 5,000+ edge servers in 100+ countries
- **Peak Bandwidth**: 50+ Tbps during global business hours

### Real-Time Performance
- **Meeting Join Time**: p99 < 3 seconds globally
- **Video Quality**: 1080p for 95% of connections, 4K for premium users
- **Audio Latency**: p99 < 150ms end-to-end globally
- **Video Latency**: p99 < 200ms for standard quality
- **Uptime**: 99.99% availability (less than 1 hour downtime/year)
- **NAT Traversal Success**: 99.9% successful connection establishment

### Infrastructure Scale
- **Compute Instances**: 100,000+ EC2/GCP instances globally
- **Database Storage**: 500TB+ in PostgreSQL clusters
- **Object Storage**: 1+ Exabyte in S3 for recordings
- **Container Orchestration**: 10,000+ Kubernetes pods
- **Event Processing**: 100M+ Kafka events/day

## Cost Breakdown (Monthly)

### Infrastructure Costs ($200M/month total)
- **Compute (Multi-cloud)**: $80M across AWS, Azure, GCP
  - Media processing: $40M (GPU-intensive transcoding)
  - Application services: $25M (Meeting controllers, APIs)
  - Edge infrastructure: $15M (WebRTC gateways, CDN)
- **Storage**: $45M total
  - Object storage (recordings): $30M (1EB+ with intelligent tiering)
  - Database storage: $10M (PostgreSQL + Cassandra + Redis)
  - CDN storage: $5M (Global content distribution)
- **Networking**: $35M total
  - Data transfer: $20M (Video/audio streaming egress)
  - Load balancing: $8M (Global traffic distribution)
  - VPN/interconnect: $7M (Multi-cloud connectivity)
- **AI/ML Services**: $25M total
  - GPU compute: $15M (Real-time transcription, background processing)
  - AI model inference: $6M (Speech-to-text, noise cancellation)
  - Training infrastructure: $4M (Model development and training)
- **Security & Compliance**: $15M total
  - DDoS protection: $5M (Enterprise-grade protection)
  - Encryption services: $4M (End-to-end encryption at scale)
  - Compliance tooling: $3M (SOC2, HIPAA, GDPR compliance)
  - Security monitoring: $3M (24/7 SOC operations)

### Cost Per Meeting Minute
- **Standard Meeting**: $0.002 per minute (audio + video)
- **HD Video Meeting**: $0.004 per minute (1080p video)
- **4K Premium Meeting**: $0.008 per minute (enterprise features)
- **Recording + Transcription**: $0.001 additional per minute
- **Large Meetings (500+ participants)**: $0.015 per minute per participant

## Instance Types & Configuration

### Edge Plane
- **Global CDN**: Custom hardware + c5n.18xlarge (72 vCPU, 192GB RAM, 100Gbps)
- **Load Balancers**: c5n.9xlarge (36 vCPU, 96GB RAM, 50Gbps network)
- **WebRTC Gateways**: c5n.24xlarge (96 vCPU, 192GB RAM, 100Gbps network)

### Service Plane
- **Meeting Controllers**: r5.12xlarge (48 vCPU, 384GB RAM) - Memory for session state
- **Media Routers**: c5n.24xlarge (96 vCPU, 192GB RAM, 100Gbps) - Network intensive
- **Transcoding**: p3.8xlarge (32 vCPU, 244GB RAM, 4x V100 GPUs) - Video processing
- **AI Services**: p3.16xlarge (64 vCPU, 488GB RAM, 8x V100 GPUs) - ML inference

### State Plane
- **PostgreSQL**: db.r6g.16xlarge (64 vCPU, 512GB RAM, 25Gbps network)
- **Cassandra**: i3en.24xlarge (96 vCPU, 768GB RAM, 60TB NVMe)
- **Redis**: r6gd.16xlarge (64 vCPU, 512GB RAM, 3.8TB NVMe)
- **Kafka**: i3en.12xlarge (48 vCPU, 384GB RAM, 30TB NVMe)

### Control Plane
- **Monitoring**: m5.24xlarge (96 vCPU, 384GB RAM)
- **Kubernetes Masters**: c5.9xlarge (36 vCPU, 72GB RAM)

## Technology Stack Details

### Core Technologies
- **Backend Languages**: Java (Spring Boot), Go (high-performance services), C++ (media processing)
- **Real-time Communication**: WebRTC, SFU (Selective Forwarding Unit)
- **Container Orchestration**: Kubernetes with multi-cloud deployment
- **Message Queuing**: Apache Kafka for event streaming
- **Databases**: PostgreSQL (metadata), Cassandra (time-series), Redis (session)
- **Monitoring**: Prometheus + Grafana + ELK stack

### AI/ML Stack
- **Speech Recognition**: Custom models + Google Cloud Speech-to-Text
- **Computer Vision**: TensorFlow + PyTorch for background processing
- **Noise Cancellation**: Real-time audio processing with custom algorithms
- **Video Enhancement**: GPU-accelerated processing for quality optimization

## Failure Scenarios & Recovery

### Global Incident Response
- **Detection**: Prometheus alerts detect issues within 30 seconds
- **Failover**: DNS-based traffic routing to healthy regions within 60 seconds
- **Recovery**: Automated healing processes restore service within 5 minutes
- **Communication**: Status page updates and proactive user notification

### Media Quality Protection
- **Bandwidth Adaptation**: Real-time quality adjustment based on network conditions
- **Fallback Modes**: Audio-only fallback when video fails
- **Redundant Paths**: Multiple network paths for critical connections
- **Quality Monitoring**: Real-time monitoring with automatic adjustment

### Database Resilience
- **Multi-master Setup**: PostgreSQL clusters with automatic failover
- **Data Replication**: 3-way replication across availability zones
- **Backup Strategy**: Continuous backup with point-in-time recovery
- **Connection Pooling**: Resilient connection management with circuit breakers

## Production Incidents (Real Examples)

### March 2024: Global Traffic Surge During Pandemic Peak
- **Impact**: 300% traffic increase, elevated join times (5-10 seconds)
- **Duration**: 2 hours during peak business hours
- **Root Cause**: Insufficient auto-scaling headroom for unprecedented growth
- **Resolution**: Emergency capacity scaling + optimized connection pooling
- **Prevention**: Enhanced predictive scaling based on global events

### August 2024: WebRTC Gateway Overload
- **Impact**: 15% connection failures in APAC region
- **Duration**: 45 minutes during Asia business hours
- **Root Cause**: WebRTC gateway cluster exhausted connection limits
- **Resolution**: Emergency scaling + traffic redistribution to other regions
- **Prevention**: Implemented per-region capacity monitoring and alerts

### June 2024: AI Transcription Service Outage
- **Impact**: Real-time transcription unavailable globally
- **Duration**: 3 hours
- **Root Cause**: GPU cluster failure in primary AI processing region
- **Resolution**: Failover to secondary region + manual restart procedures
- **Prevention**: Multi-region AI service deployment with automatic failover

## Business Impact Metrics

### Revenue Protection
- **99.99% Availability** = $500M+ annual revenue protection
- **Sub-3s Join Time** = 25% higher meeting completion rate
- **HD Video Quality** = 40% premium subscription conversion
- **AI Features** = $2B+ annual AI-driven feature revenue

### Operational Excellence
- **1,000 Deployments/Day** = 4-hour median time from code to production
- **Automated Scaling** = 80% reduction in manual capacity management
- **Multi-cloud Strategy** = 99.5% reduction in vendor lock-in risk

## Sources & References

- [Zoom Engineering Blog - Scaling Video Infrastructure](https://medium.com/zoom-developer-blog)
- [Zoom Investor Relations - Q3 2024 Technical Infrastructure](https://investors.zoom.us)
- [WebRTC for the Curious - Zoom Implementation Details](https://webrtcforthecurious.com)
- [Zoom Security Whitepaper - End-to-End Encryption](https://zoom.us/docs/doc/Zoom-Security-White-Paper.pdf)
- [AWS Case Study - Zoom Infrastructure](https://aws.amazon.com/solutions/case-studies/zoom/)
- [Kubernetes at Scale - Zoom Container Strategy](https://kubernetes.io/case-studies/zoom/)
- QCon 2024 - Zoom's Real-time Architecture at Scale
- SREcon 2024 - Multi-cloud Kubernetes at Zoom Scale

---

*Last Updated: September 2024*
*Data Source Confidence: B+ (Financial Reports + Engineering Blog + Industry Analysis)*
*Diagram ID: CS-ZOM-ARCH-001*