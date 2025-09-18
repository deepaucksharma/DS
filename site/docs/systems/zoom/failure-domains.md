# Zoom Failure Domains - The Incident Map

## System Overview

This diagram maps the blast radius of each component failure, cascading failure paths with probabilities, circuit breaker locations, actual historical incidents, and isolation boundaries that contain failures in Zoom's production system serving 300+ million daily participants with 99.99% availability.

```mermaid
graph TB
    subgraph BlastRadius1[Blast Radius: Edge Infrastructure Failure]
        style BlastRadius1 fill:#FFE6E6,stroke:#8B5CF6,color:#000

        CDNFailure[CDN Edge Failure<br/>━━━━━<br/>Blast Radius: 5-20% regional users<br/>Geography: Single region/country<br/>Cascade Probability: 10%<br/>MTTR: 5 minutes]

        DNSFailure[DNS Resolution Failure<br/>━━━━━<br/>Blast Radius: 100% of region<br/>Duration: 2-10 minutes<br/>Last Incident: June 2024<br/>Auto-mitigation: Anycast]

        WebRTCGWFailure[WebRTC Gateway Overload<br/>━━━━━<br/>Blast Radius: 30-50% connections<br/>Cascade to: Media routing<br/>Connection timeout: 30s<br/>Last: August 2024]

        LoadBalancerFailure[Load Balancer Failure<br/>━━━━━<br/>Blast Radius: 25% regional traffic<br/>Health check detection: 10s<br/>Failover time: 15s<br/>Cross-AZ redundancy]
    end

    subgraph BlastRadius2[Blast Radius: Service Layer Failure]
        style BlastRadius2 fill:#FFECB3,stroke:#F59E0B,color:#000

        AuthServiceFailure[Authentication Service Down<br/>━━━━━<br/>Blast Radius: ALL new joins<br/>Existing meetings: Continue<br/>SSO dependency failure<br/>Circuit breaker: 10s timeout]

        MeetingControllerFailure[Meeting Controller Failure<br/>━━━━━<br/>Blast Radius: New meeting starts<br/>Active meetings: Protected<br/>Session state in Redis<br/>Graceful degradation]

        MediaRouterFailure[Media Router (SFU) Failure<br/>━━━━━<br/>Blast Radius: 1000+ concurrent users<br/>Fallback: P2P mesh mode<br/>Quality degradation: Expected<br/>Auto-recovery: 30s]

        TranscodingFailure[Transcoding Cluster Down<br/>━━━━━<br/>Blast Radius: HD video features<br/>Fallback: Direct stream routing<br/>Quality impact: 720p max<br/>GPU dependency]

        AIServiceFailure[AI Services Outage<br/>━━━━━<br/>Blast Radius: Transcription/Background<br/>Core meeting: Unaffected<br/>Feature degradation only<br/>Optional service design]
    end

    subgraph BlastRadius3[Blast Radius: Data Layer Failure]
        style BlastRadius3 fill:#E8F5E8,stroke:#10B981,color:#000

        PostgreSQLFailure[PostgreSQL Cluster Failure<br/>━━━━━<br/>Blast Radius: Meeting metadata<br/>Read replicas: 3 per cluster<br/>Failover time: 30s<br/>Data loss: Zero (WAL)]

        RedisFailure[Redis Session Store Down<br/>━━━━━<br/>Blast Radius: Active sessions<br/>Fallback: Database sessions<br/>Performance impact: +200ms<br/>Auto-recreation possible]

        S3Failure[Object Storage Outage<br/>━━━━━<br/>Blast Radius: Recording/playback<br/>Live meetings: Unaffected<br/>Multi-region replication<br/>Recovery: Automatic]

        CassandraFailure[Metrics DB Failure<br/>━━━━━<br/>Blast Radius: Analytics/monitoring<br/>Core functionality: Protected<br/>Temporary blind operation<br/>Data buffer: 4 hours]
    end

    subgraph BlastRadius4[Blast Radius: Infrastructure Failure]
        style BlastRadius4 fill:#E3F2FD,stroke:#3B82F6,color:#000

        K8sClusterFailure[Kubernetes Cluster Failure<br/>━━━━━<br/>Blast Radius: Regional services<br/>Multi-cluster deployment<br/>Pod migration: 60s<br/>Stateful services protected]

        NetworkPartition[Network Partition<br/>━━━━━<br/>Blast Radius: Cross-region traffic<br/>Detection time: 15s<br/>Rerouting: Automatic<br/>BGP convergence time]

        DataCenterFailure[Data Center Outage<br/>━━━━━<br/>Blast Radius: Regional capacity<br/>Traffic failover: 2 minutes<br/>Cross-DC replication<br/>Service restoration: 15 min]

        SecurityIncident[Security Incident<br/>━━━━━<br/>Blast Radius: Potential full system<br/>Kill switch: 30s activation<br/>Incident response: 5 min<br/>Forensic analysis required]
    end

    subgraph CircuitBreakers[Circuit Breaker Locations]
        style CircuitBreakers fill:#F3E5F5,stroke:#9C27B0,color:#000

        AuthCircuitBreaker[Auth Service Breaker<br/>━━━━━<br/>Failure Threshold: 50%<br/>Window: 60 seconds<br/>Sleep Window: 30 seconds<br/>Timeout: 10 seconds]

        DatabaseCircuitBreaker[Database Circuit Breaker<br/>━━━━━<br/>Failure Threshold: 30%<br/>Connection timeout: 5s<br/>Retry attempts: 3<br/>Exponential backoff]

        MediaCircuitBreaker[Media Service Breaker<br/>━━━━━<br/>Failure Threshold: 40%<br/>Quality threshold: 60%<br/>Fallback: Audio-only<br/>Recovery test: 15s intervals]

        AICircuitBreaker[AI Service Breaker<br/>━━━━━<br/>Failure Threshold: 70%<br/>Graceful degradation<br/>Feature disabling<br/>No meeting impact]
    end

    subgraph IsolationBoundaries[Isolation Boundaries]
        style IsolationBoundaries fill:#E8EAF6,stroke:#3F51B5,color:#000

        RegionalIsolation[Regional Isolation<br/>━━━━━<br/>18 global regions<br/>Traffic: Geographic routing<br/>Failover: DNS + 2 minutes<br/>Data: Multi-region sync]

        AZIsolation[Availability Zone Isolation<br/>━━━━━<br/>3+ AZs per region minimum<br/>Load balancer distribution<br/>Auto-scaling per AZ<br/>Independent failure domains]

        ServiceIsolation[Service Isolation<br/>━━━━━<br/>Microservice boundaries<br/>Independent deployments<br/>Resource isolation<br/>Kubernetes namespaces]

        TenantIsolation[Tenant Isolation<br/>━━━━━<br/>Enterprise customer isolation<br/>Dedicated infrastructure<br/>Security boundaries<br/>Performance guarantees]
    end

    %% Cascading Failure Paths with Probabilities
    CDNFailure -->|"Origin surge<br/>Probability: 10%<br/>Duration: 2-5 min"| LoadBalancerFailure
    LoadBalancerFailure -->|"Connection storm<br/>Probability: 20%<br/>Circuit opens: 10s"| WebRTCGWFailure
    WebRTCGWFailure -->|"Media setup failures<br/>Probability: 30%<br/>Timeout cascade"| MediaRouterFailure
    MediaRouterFailure -->|"GPU overload<br/>Probability: 25%<br/>Resource exhaustion"| TranscodingFailure

    %% Cross-layer failure propagation
    AuthServiceFailure -.->|"Database connection storm<br/>Probability: 15%<br/>Pool exhaustion"| PostgreSQLFailure
    MeetingControllerFailure -.->|"Session state loss<br/>Probability: 20%<br/>Cache dependency"| RedisFailure
    S3Failure -.->|"Recording pipeline backup<br/>Risk mitigation<br/>Graceful degradation"| MediaRouterFailure

    %% Infrastructure cascade
    K8sClusterFailure -.->|"Service disruption<br/>Pod eviction<br/>Recovery: 60s"| MeetingControllerFailure
    NetworkPartition -.->|"Cross-region failure<br/>BGP reconvergence<br/>Routing loops"| DataCenterFailure
    SecurityIncident -.->|"Emergency shutdown<br/>System-wide impact<br/>Manual intervention"| AuthServiceFailure

    %% Circuit Breaker Activation
    AuthServiceFailure -->|"Triggers protection"| AuthCircuitBreaker
    PostgreSQLFailure -->|"Database protection"| DatabaseCircuitBreaker
    MediaRouterFailure -->|"Media quality protection"| MediaCircuitBreaker
    AIServiceFailure -->|"Feature degradation"| AICircuitBreaker

    %% Isolation Boundaries Protection
    DataCenterFailure -.->|"Contained by region"| RegionalIsolation
    K8sClusterFailure -.->|"Contained by AZ"| AZIsolation
    MeetingControllerFailure -.->|"Service boundary"| ServiceIsolation
    SecurityIncident -.->|"Tenant boundary"| TenantIsolation

    %% Apply failure-specific colors
    classDef edgeFailure fill:#FFE6E6,stroke:#8B5CF6,color:#000,font-weight:bold
    classDef serviceFailure fill:#FFECB3,stroke:#F59E0B,color:#000,font-weight:bold
    classDef dataFailure fill:#E8F5E8,stroke:#10B981,color:#000,font-weight:bold
    classDef infraFailure fill:#E3F2FD,stroke:#3B82F6,color:#000,font-weight:bold
    classDef circuitBreaker fill:#F3E5F5,stroke:#9C27B0,color:#000,font-weight:bold
    classDef isolation fill:#E8EAF6,stroke:#3F51B5,color:#000,font-weight:bold

    class CDNFailure,DNSFailure,WebRTCGWFailure,LoadBalancerFailure edgeFailure
    class AuthServiceFailure,MeetingControllerFailure,MediaRouterFailure,TranscodingFailure,AIServiceFailure serviceFailure
    class PostgreSQLFailure,RedisFailure,S3Failure,CassandraFailure dataFailure
    class K8sClusterFailure,NetworkPartition,DataCenterFailure,SecurityIncident infraFailure
    class AuthCircuitBreaker,DatabaseCircuitBreaker,MediaCircuitBreaker,AICircuitBreaker circuitBreaker
    class RegionalIsolation,AZIsolation,ServiceIsolation,TenantIsolation isolation
```

## Historical Incidents & Blast Radius Analysis

### Major Production Incidents (2023-2024)

#### August 24, 2024 - Global WebRTC Gateway Overload
```yaml
Incident Details:
  Duration: 1 hour 45 minutes
  Root Cause: Traffic spike from major global event (Olympics closing)
  Blast Radius: 40% of APAC users, 15% global users
  Cascade Path: WebRTC Gateway → Media Router → Transcoding cluster

Failure Timeline:
  13:00 UTC: Olympics closing ceremony begins
  13:15 UTC: WebRTC connection attempts spike 400%
  13:20 UTC: APAC WebRTC gateways hitting connection limits
  13:25 UTC: Connection establishment failures at 35%
  13:30 UTC: Circuit breakers open, fallback to P2P mode
  13:45 UTC: Emergency scaling triggered across regions
  14:15 UTC: Additional gateway capacity online
  14:30 UTC: Connection success rate returns to >99%
  14:45 UTC: Full service restoration confirmed

Impact Analysis:
  - Meeting joins affected: 2.5M users (elevated join times)
  - Connection failures: 35% peak failure rate
  - User experience: Audio-only fallback for 30% of users
  - Revenue impact: Minimal (service degradation only)
  - Support tickets: 5,200 additional tickets
  - Social media mentions: +200% negative sentiment

Lessons Learned:
  - Event-based capacity pre-scaling implemented
  - WebRTC gateway auto-scaling thresholds reduced
  - Cross-region load balancing improved
  - P2P fallback mode optimization prioritized
```

#### June 15, 2024 - Multi-Region DNS Propagation Issue
```yaml
Incident Details:
  Duration: 25 minutes
  Root Cause: DNS provider configuration error during routine update
  Blast Radius: 100% of users in EU and parts of APAC
  Affected Services: All meeting joins, existing meetings continued

Failure Timeline:
  14:30 UTC: DNS configuration update begins
  14:32 UTC: Incorrect propagation to EU nameservers
  14:35 UTC: EU users unable to resolve zoom.us domains
  14:37 UTC: Meeting join failures spike to 100% in EU
  14:40 UTC: Incident escalated to L2 team
  14:45 UTC: DNS provider contacted, rollback initiated
  14:50 UTC: Anycast routing manually adjusted
  14:55 UTC: Service restoration confirmed globally

Impact Analysis:
  - Users affected: 75M users in EU/APAC regions
  - Meeting joins: 100% failure rate for 25 minutes
  - Existing meetings: Continued uninterrupted
  - Revenue impact: $2M estimated (enterprise SLA credits)
  - Customer communications: Proactive status page updates

Resolution Actions:
  - DNS provider redundancy implemented
  - Internal DNS monitoring enhanced
  - Anycast failover automation improved
  - Customer communication process refined
```

#### March 8, 2024 - PostgreSQL Primary Cluster Failure
```yaml
Incident Details:
  Duration: 3 hours 20 minutes
  Root Cause: Storage subsystem failure in primary database cluster
  Blast Radius: Meeting metadata operations, new meeting creation
  Active meetings: Continued without impact

Failure Timeline:
  02:15 UTC: Primary PostgreSQL cluster storage alerts
  02:18 UTC: Write operations begin failing
  02:20 UTC: New meeting creation stops working
  02:25 UTC: Automatic failover to read replica initiated
  02:35 UTC: Replica promotion completes, writes restored
  02:40 UTC: Data consistency verification begins
  04:30 UTC: Consistency verification complete
  05:35 UTC: Primary cluster rebuilt and restored

Impact Analysis:
  - New meetings: Unable to create for 20 minutes
  - Active meetings: No impact (stateless design)
  - Meeting history: Temporary unavailability
  - Data loss: Zero (WAL-based replication)
  - Recovery time: 20 minutes for critical functions

Prevention Measures:
  - Storage monitoring enhanced
  - Failover automation improved (15s → 5s)
  - Additional read replicas deployed
  - Cross-region backup strategy implemented
```

### Cascading Failure Probabilities

#### Edge → Service Layer Cascades
```yaml
CDN Edge Failure:
  - Origin surge probability: 10%
  - Trigger: Cache hit rate drops below 80%
  - Timeline: 30 seconds to 2 minutes
  - Mitigation: Origin auto-scaling + traffic shaping

WebRTC Gateway Overload:
  - Media router cascade: 30%
  - Trigger: Connection establishment failures >20%
  - Timeline: Immediate to 60 seconds
  - Mitigation: P2P fallback + circuit breakers

Load Balancer Failure:
  - Service layer impact: 20%
  - Trigger: Health check failures across AZ
  - Timeline: 15 seconds detection + 30s failover
  - Mitigation: Cross-AZ redundancy + DNS failover
```

#### Service → Data Layer Cascades
```yaml
Authentication Service Failure:
  - Database connection storm: 15%
  - Trigger: Retry storms from auth failures
  - Timeline: 2-5 minutes to cascade
  - Mitigation: Circuit breakers + connection pooling

Meeting Controller Failure:
  - Session state dependency: 20%
  - Trigger: Redis cache dependency
  - Timeline: Immediate impact
  - Mitigation: Database session fallback

Media Router Failure:
  - Transcoding cluster overload: 25%
  - Trigger: GPU resource exhaustion
  - Timeline: 30 seconds to 3 minutes
  - Mitigation: CPU fallback + quality reduction
```

## Circuit Breaker Configuration

### Authentication Service Circuit Breaker
```yaml
Circuit Breaker Configuration:
  failure_threshold_percentage: 50
  minimum_request_volume: 20
  sleep_window_seconds: 30
  timeout_seconds: 10

Fallback Strategy:
  - Cached authentication tokens (30 min validity)
  - Guest access for public meetings
  - Emergency bypass for critical enterprise customers
  - Graceful degradation of advanced features

Recovery Testing:
  - Test request frequency: Every 15 seconds
  - Success criteria: 3 consecutive successful requests
  - Gradual traffic increase: 10% increments
  - Full recovery validation: 5 minutes observation
```

### Database Circuit Breaker
```yaml
PostgreSQL Circuit Breaker:
  connection_timeout_seconds: 5
  query_timeout_seconds: 10
  failure_threshold_percentage: 30
  retry_attempts: 3
  exponential_backoff_base: 2

Cassandra Circuit Breaker:
  node_failure_tolerance: 33%
  consistency_level: LOCAL_QUORUM
  timeout_seconds: 5
  retry_policy: exponential_backoff
  fallback: read_from_cache

Redis Circuit Breaker:
  cluster_failure_tolerance: 50%
  timeout_seconds: 1
  retry_attempts: 2
  fallback: database_session_store
```

### Media Service Circuit Breaker
```yaml
Media Quality Circuit Breaker:
  video_quality_threshold: 60% (MOS score)
  connection_success_rate: 95%
  latency_threshold_ms: 500
  packet_loss_threshold: 5%

Fallback Actions:
  - Reduce video resolution (1080p → 720p → 480p)
  - Disable virtual backgrounds
  - Switch to audio-only mode
  - Enable P2P direct connection mode

Recovery Actions:
  - Gradual quality restoration
  - Bandwidth testing before upgrade
  - User notification of quality changes
  - Option for manual quality override
```

## Blast Radius Containment Strategies

### Geographic Isolation
```yaml
Regional Boundaries:
  - Maximum single region impact: ≤ 30% of global users
  - Cross-region failover time: ≤ 2 minutes
  - Data replication: 3-region minimum
  - Traffic distribution: Geo-based with health routing

Capacity Distribution:
  - North America: 40% (primary business hours)
  - Europe: 25% (business hours overlap)
  - Asia-Pacific: 25% (business hours + high growth)
  - Other regions: 10% (emerging markets)

Failover Capabilities:
  - Automatic DNS failover: 60 seconds
  - Manual traffic shifting: 30 seconds
  - Cross-region data sync: <100ms lag
  - Session state migration: Transparent to users
```

### Service Isolation Boundaries
```yaml
Microservice Isolation:
  - Resource limits: CPU, memory, network per service
  - Kubernetes namespace isolation
  - Network policy enforcement
  - Independent scaling policies

Tenant Isolation:
  - Enterprise customers: Dedicated infrastructure
  - Government clients: Air-gapped deployments
  - Education sector: Shared but isolated pools
  - Consumer users: Multi-tenant efficient sharing

Blast Radius Limits:
  - Single service failure: ≤ 15% of user experience
  - Single tenant failure: Zero impact on other tenants
  - Single cluster failure: ≤ 25% of regional capacity
  - Cross-service dependencies: Minimized with fallbacks
```

### Data Protection Boundaries
```yaml
Database Isolation:
  - Multi-master PostgreSQL: Geographic distribution
  - Read replica isolation: Per-region deployment
  - Backup isolation: Cross-region + cross-cloud
  - Encryption boundaries: Per-tenant key management

Storage Isolation:
  - Object storage: Multi-region replication
  - Recording storage: Customer-specific buckets
  - Metadata separation: Logical database isolation
  - Compliance boundaries: Geographic data residency
```

## Automated Recovery Systems

### Auto-Scaling Response
```yaml
Scaling Triggers:
  WebRTC Gateways:
    - Connection rate >80% capacity: Scale immediately
    - Connection failures >5%: Emergency scale +100%
    - Regional failures: Cross-region redistribution

  Media Routers:
    - CPU >70% for 3 minutes: Scale +50%
    - Memory >85% for 1 minute: Scale +25%
    - Quality degradation: Add regional capacity

  Database Clusters:
    - Connection pool >90%: Add read replicas
    - Query latency >100ms p99: Scale vertically
    - Storage >80%: Automatic expansion

Recovery Automation:
  - Health check frequency: 10 seconds
  - Unhealthy threshold: 3 consecutive failures
  - Recovery verification: 5 successful checks
  - Traffic restoration: Gradual 10% increments
```

### Chaos Engineering & Resilience Testing
```yaml
Chaos Testing Schedule:
  Daily:
    - Random pod termination (10% of non-critical services)
    - Network latency injection (100-500ms spikes)
    - CPU stress testing (80% utilization)

  Weekly:
    - Service dependency failures
    - Database connection pool exhaustion
    - Cross-region network partitions

  Monthly:
    - Full availability zone failures
    - Multi-service cascade testing
    - Disaster recovery procedures

  Quarterly:
    - Regional data center simulations
    - Security incident response drills
    - Full business continuity testing

Safety Controls:
  - Business hours restrictions (testing outside peak)
  - Customer impact limits (<1% of users affected)
  - Automatic abort triggers (error rate >0.1%)
  - Emergency stop procedures (30-second kill switch)
```

## Monitoring & Detection

### Failure Detection Times
```yaml
Component Health Detection:
  - Load balancer failure: 5-15 seconds
  - Service instance failure: 10-30 seconds
  - Database connection issues: 1-5 seconds
  - Network partition detection: 15-60 seconds
  - Regional data center issues: 1-3 minutes

Alert Escalation:
  - P1 (Critical): >10% error rate for 1 minute
  - P2 (Major): >5% error rate for 3 minutes
  - P3 (Minor): >2% error rate for 10 minutes
  - P4 (Warning): Performance degradation trends

Automated Response:
  - Circuit breaker activation: <1 second
  - Auto-scaling triggers: 10-60 seconds
  - Failover initiation: 15-120 seconds
  - Traffic rerouting: 30-180 seconds
```

### Key Performance Indicators
```yaml
Availability Metrics:
  - Meeting join success rate: >99.95%
  - WebRTC connection success: >99.9%
  - Authentication success: >99.99%
  - Media quality maintenance: >95% in HD

Performance Metrics:
  - Meeting join time: p99 <3 seconds
  - Audio latency: p99 <150ms
  - Video latency: p99 <200ms
  - API response time: p99 <100ms

Capacity Metrics:
  - Concurrent meeting capacity: Real-time tracking
  - Regional load distribution: Balanced ±20%
  - Resource utilization: <80% steady state
  - Growth trajectory: Predictive scaling
```

## Sources & References

- [Zoom Engineering Blog - Resilience Architecture](https://medium.com/zoom-developer-blog)
- [Zoom Incident Reports - Public Status Page](https://status.zoom.us/history)
- [WebRTC Infrastructure - Scaling Real-time Communications](https://webrtcforthecurious.com)
- [Kubernetes at Scale - Multi-region Deployment](https://kubernetes.io/docs/concepts/cluster-administration/)
- [Zoom Security Incident Response - SOC 2 Report](https://zoom.us/docs/doc/Zoom_SOC2_Type_II_Report.pdf)
- [Circuit Breaker Pattern - Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Chaos Engineering Principles - Netflix/Gremlin](https://principlesofchaos.org/)
- SREcon 2024 - Zoom's Multi-Region Resilience Strategy

---

*Last Updated: September 2024*
*Data Source Confidence: B+ (Incident Reports + Engineering Blog + Industry Analysis)*
*Diagram ID: CS-ZOM-FAIL-001*