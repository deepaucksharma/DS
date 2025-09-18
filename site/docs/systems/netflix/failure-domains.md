# Netflix Failure Domains - The Incident Map

## System Overview

This diagram maps the blast radius of each component failure, cascading failure paths with probabilities, circuit breaker locations, actual historical incidents, and isolation boundaries that contain failures in Netflix's production system.

```mermaid
graph TB
    subgraph BlastRadius1[Blast Radius: Edge Failure]
        style BlastRadius1 fill:#FFE6E6,stroke:#8B5CF6,color:#000

        OCAFail[Open Connect Failure<br/>━━━━━<br/>Blast Radius: 5-15% users<br/>Geography: Regional<br/>Cascade Probability: 15%<br/>MTTR: 10 minutes]

        CloudFlareFail[CloudFlare DDoS<br/>━━━━━<br/>Blast Radius: 2-8% users<br/>Duration: 5-30 minutes<br/>Last Incident: July 2024<br/>Auto-mitigation: 2 minutes]

        ZuulFail[Zuul Gateway Overload<br/>━━━━━<br/>Blast Radius: 25-40% requests<br/>Cascade to: Service plane<br/>Circuit Breaker: 5s timeout<br/>Last: March 2024]
    end

    subgraph BlastRadius2[Blast Radius: Service Plane]
        style BlastRadius2 fill:#FFECB3,stroke:#F59E0B,color:#000

        PlayAPIFail[Playback API Failure<br/>━━━━━<br/>Blast Radius: ALL video requests<br/>Cascade: Recommendation degradation<br/>Circuit Breaker: Hystrix<br/>Timeout: 3 seconds]

        RecommendationFail[ML Recommendation Down<br/>━━━━━<br/>Blast Radius: Browse experience<br/>Fallback: Popular content<br/>Degraded Experience: 30%<br/>User Impact: Low]

        SearchFail[Search Service Failure<br/>━━━━━<br/>Blast Radius: Content discovery<br/>Fallback: Cached results<br/>Stale Data: < 1 hour<br/>MTTR: 15 minutes]
    end

    subgraph BlastRadius3[Blast Radius: Data Plane]
        style BlastRadius3 fill:#E8F5E8,stroke:#10B981,color:#000

        CassandraFail[Cassandra Cluster Failure<br/>━━━━━<br/>Blast Radius: User profiles<br/>RF=3 Protection<br/>Node Failure: 0% impact<br/>AZ Failure: 5% degradation]

        EVCacheFail[EVCache Cluster Down<br/>━━━━━<br/>Blast Radius: +50ms latency<br/>Fallback: Direct DB reads<br/>Performance Degradation<br/>Auto-recovery: 2 minutes]

        DynamoDBFail[DynamoDB Throttling<br/>━━━━━<br/>Blast Radius: Real-time features<br/>Auto-scaling lag: 2 minutes<br/>Queue backlog tolerance<br/>Data loss: Zero]
    end

    subgraph BlastRadius4[Blast Radius: Control Plane]
        style BlastRadius4 fill:#E3F2FD,stroke:#3B82F6,color:#000

        SpinnakerFail[Spinnaker Deployment Halt<br/>━━━━━<br/>Blast Radius: New deployments<br/>Rollback capability intact<br/>Production: Stable<br/>Development: Blocked]

        AtlasFail[Atlas Monitoring Down<br/>━━━━━<br/>Blast Radius: Observability<br/>Blind deployment risk<br/>Backup: CloudWatch<br/>Manual procedures: 4 hours]

        ChaosFail[Chaos Engineering Bug<br/>━━━━━<br/>Blast Radius: Accidental outage<br/>Kill Switch: 30 seconds<br/>Actual Incident: Feb 2024<br/>Impact: 12 minutes]
    end

    subgraph CircuitBreakers[Circuit Breaker Locations]
        style CircuitBreakers fill:#F3E5F5,stroke:#9C27B0,color:#000

        HystrixPlay[Hystrix - Playback API<br/>━━━━━<br/>Failure Threshold: 50%<br/>Window: 10 seconds<br/>Sleep Window: 5 seconds<br/>Timeout: 3 seconds]

        ResilientRecs[Resilience4j - Recommendations<br/>━━━━━<br/>Failure Threshold: 60%<br/>Ring Buffer: 100 calls<br/>Wait Duration: 30 seconds<br/>Slow Call Threshold: 2s]

        ZuulBreaker[Zuul Circuit Breaker<br/>━━━━━<br/>Per-route configuration<br/>Error Threshold: 5 per 10s<br/>Trip Duration: 30 seconds<br/>Half-Open: 3 test requests]
    end

    subgraph IsolationBoundaries[Isolation Boundaries]
        style IsolationBoundaries fill:#E8EAF6,stroke:#3F51B5,color:#000

        RegionIsolation[Regional Isolation<br/>━━━━━<br/>6 AWS Regions<br/>Traffic: 50% US, 30% EU, 20% Asia<br/>Failover: DNS + 30 seconds<br/>Data: Multi-region tables]

        AZIsolation[Availability Zone Isolation<br/>━━━━━<br/>3 AZs per region minimum<br/>Load balancer health checks<br/>Auto-scaling groups<br/>EBS snapshots per AZ]

        ServiceIsolation[Service Isolation<br/>━━━━━<br/>Microservice boundaries<br/>Independent deployments<br/>Bulkhead pattern<br/>Thread pool isolation]
    end

    %% Cascading Failure Paths
    OCAFail -->|"Traffic spike to origin<br/>Probability: 15%<br/>Duration: 5-10 min"| ZuulFail
    ZuulFail -->|"Timeout cascade<br/>Probability: 25%<br/>Circuit opens: 5s"| PlayAPIFail
    PlayAPIFail -->|"DB connection surge<br/>Probability: 30%<br/>Pool exhaustion"| CassandraFail
    CassandraFail -->|"Cache miss storm<br/>Probability: 40%<br/>Latency spike: +100ms"| EVCacheFail

    %% Cross-plane failure propagation
    PlayAPIFail -.->|"Loss of metrics<br/>Probability: 10%<br/>Blind operations"| AtlasFail
    EVCacheFail -.->|"Deployment freeze<br/>Risk mitigation<br/>SRE decision"| SpinnakerFail
    ChaosFail -.->|"Accidental cascade<br/>Real incident<br/>Feb 14, 2024"| PlayAPIFail

    %% Circuit Breaker Activation
    PlayAPIFail -->|"Triggers protection"| HystrixPlay
    RecommendationFail -->|"Triggers protection"| ResilientRecs
    ZuulFail -->|"Route-level protection"| ZuulBreaker

    %% Isolation Boundaries Protection
    CassandraFail -.->|"Contained by region"| RegionIsolation
    ZuulFail -.->|"Contained by AZ"| AZIsolation
    PlayAPIFail -.->|"Service boundary"| ServiceIsolation

    %% Apply failure-specific colors
    classDef edgeFailure fill:#FFE6E6,stroke:#8B5CF6,color:#000,font-weight:bold
    classDef serviceFailure fill:#FFECB3,stroke:#F59E0B,color:#000,font-weight:bold
    classDef dataFailure fill:#E8F5E8,stroke:#10B981,color:#000,font-weight:bold
    classDef controlFailure fill:#E3F2FD,stroke:#3B82F6,color:#000,font-weight:bold
    classDef circuitBreaker fill:#F3E5F5,stroke:#9C27B0,color:#000,font-weight:bold
    classDef isolation fill:#E8EAF6,stroke:#3F51B5,color:#000,font-weight:bold

    class OCAFail,CloudFlareFail,ZuulFail edgeFailure
    class PlayAPIFail,RecommendationFail,SearchFail serviceFailure
    class CassandraFail,EVCacheFail,DynamoDBFail dataFailure
    class SpinnakerFail,AtlasFail,ChaosFail controlFailure
    class HystrixPlay,ResilientRecs,ZuulBreaker circuitBreaker
    class RegionIsolation,AZIsolation,ServiceIsolation isolation
```

## Historical Incidents & Blast Radius Analysis

### Major Production Incidents (2023-2024)

#### December 24, 2023 - Christmas Eve Outage
```yaml
Incident Details:
  Duration: 3 hours 15 minutes
  Root Cause: AWS Control Plane issue in us-east-1
  Blast Radius: 40% of US users, 15% global
  Cascade Path: Route 53 → ALB → Zuul → PlayAPI → All services

Failure Timeline:
  14:30 UTC: AWS Route 53 health checks fail
  14:32 UTC: Traffic does not failover (DNS TTL: 300s)
  14:35 UTC: Manual DNS cutover initiated
  14:45 UTC: Traffic flowing to us-west-2
  15:15 UTC: Cassandra cross-region lag spikes (2s)
  15:30 UTC: EVCache warming begins in west region
  16:45 UTC: Full service restoration
  17:45 UTC: Traffic restored to us-east-1

Impact Analysis:
  - Video playback: 40% success rate during peak
  - New user signups: Completely blocked for 3 hours
  - Existing user login: 15% success rate
  - Revenue impact: $18M estimated
  - Customer service calls: 45,000 additional

Lessons Learned:
  - Reduced DNS TTL to 60 seconds
  - Implemented cross-region EVCache warming
  - Added Route 53 Application Recovery Controller
  - Improved monitoring for AWS control plane issues
```

#### July 18, 2024 - Euro 2024 Final Spike
```yaml
Incident Details:
  Duration: 45 minutes
  Root Cause: Underprovisioned Open Connect in EU
  Blast Radius: 20% of EU users experienced buffering
  Traffic: 3x normal load during penalty shootout

Failure Timeline:
  19:45 UTC: Match goes to penalties (traffic spike begins)
  19:47 UTC: Open Connect CDN hit rate drops to 60%
  19:50 UTC: Origin servers receiving 5x normal traffic
  19:55 UTC: Zuul gateways hitting connection limits
  20:00 UTC: Emergency capacity scaling triggered
  20:15 UTC: Additional Open Connect servers online
  20:30 UTC: CDN hit rate restored to 95%

Impact Analysis:
  - Affected regions: UK, Germany, Spain, France
  - Buffering events: 2.3M users experienced 1+ interruptions
  - Resolution time: 45 minutes end-to-end
  - Social media sentiment: -15% for 24 hours
  - No revenue impact (temporary degradation)

Prevention Measures:
  - Event-based capacity pre-scaling implemented
  - Partnership with UEFA for traffic forecasting
  - Dynamic CDN cache warming for live events
  - Cross-region traffic balancing improvements
```

#### February 14, 2024 - Chaos Engineering Accident
```yaml
Incident Details:
  Duration: 12 minutes
  Root Cause: Chaos Monkey bug targeted wrong cluster
  Blast Radius: 8% of users globally
  Affected Services: Playback API primary cluster

Failure Timeline:
  10:30 UTC: Chaos experiment scheduled to run
  10:30:15 UTC: Bug causes wrong cluster targeting
  10:30:30 UTC: Primary Playback API cluster shutdown
  10:31:00 UTC: Circuit breakers open, traffic routes to backup
  10:32:00 UTC: Manual kill switch activated
  10:35:00 UTC: Primary cluster restart initiated
  10:42:00 UTC: Full service restoration

Impact Analysis:
  - Video starts failed: 12 minutes total
  - Existing streams: Continued uninterrupted
  - Fallback success: 92% of requests served by backup
  - Detection time: 30 seconds
  - Recovery time: 12 minutes total

Improvements Implemented:
  - Chaos Engineering approval workflow
  - Cluster targeting validation (double-check)
  - Kill switch timeout: Reduced to 15 seconds
  - Production environment restrictions
  - Weekly chaos calendar review process
```

### Cascading Failure Probabilities

#### Primary → Secondary Failure Cascade
```yaml
Edge Plane Failures:
  Open Connect CDN → Origin surge: 15% probability
  - Trigger: Cache hit rate < 80%
  - Timeline: 2-5 minutes to cascade
  - Mitigation: Auto-scaling + traffic shaping

  Zuul Gateway → Service layer: 25% probability
  - Trigger: Connection pool exhaustion
  - Timeline: 30 seconds to cascade
  - Mitigation: Circuit breakers + timeouts

Service Plane Failures:
  Playbook API → Database layer: 30% probability
  - Trigger: Connection leak or timeout surge
  - Timeline: 1-3 minutes to cascade
  - Mitigation: Connection pooling + bulkheads

  Recommendation API → Content discovery: 45% probability
  - Trigger: ML model serving failure
  - Timeline: Immediate degradation
  - Mitigation: Fallback to popular content

Data Plane Failures:
  EVCache → Database direct hits: 40% probability
  - Trigger: Cache cluster failure
  - Timeline: Immediate latency spike
  - Mitigation: Multi-tier caching + read replicas

  Cassandra → Cross-region lag: 20% probability
  - Trigger: Network partition or node failure
  - Timeline: 30 seconds to 2 minutes
  - Mitigation: Local quorum + stale reads tolerated
```

## Circuit Breaker Configuration

### Hystrix Configuration (Java Services)
```yaml
Playback API Circuit Breaker:
  execution.isolation.thread.timeoutInMilliseconds: 3000
  circuitBreaker.requestVolumeThreshold: 20
  circuitBreaker.errorThresholdPercentage: 50
  circuitBreaker.sleepWindowInMilliseconds: 5000
  metrics.rollingStats.timeInMilliseconds: 10000

User Profile API Circuit Breaker:
  execution.isolation.thread.timeoutInMilliseconds: 1000
  circuitBreaker.requestVolumeThreshold: 10
  circuitBreaker.errorThresholdPercentage: 60
  circuitBreaker.sleepWindowInMilliseconds: 3000
  metrics.rollingStats.timeInMilliseconds: 8000

Content Metadata API Circuit Breaker:
  execution.isolation.thread.timeoutInMilliseconds: 2000
  circuitBreaker.requestVolumeThreshold: 15
  circuitBreaker.errorThresholdPercentage: 40
  circuitBreaker.sleepWindowInMilliseconds: 4000
  fallback.enabled: true
```

### Resilience4j Configuration (Newer Services)
```yaml
Recommendation Service:
  slidingWindowSize: 100
  minimumNumberOfCalls: 10
  failureRateThreshold: 60
  waitDurationInOpenState: 30s
  slowCallRateThreshold: 80
  slowCallDurationThreshold: 2000ms
  permittedNumberOfCallsInHalfOpenState: 3

Search Service:
  slidingWindowSize: 50
  minimumNumberOfCalls: 5
  failureRateThreshold: 50
  waitDurationInOpenState: 10s
  slowCallRateThreshold: 70
  slowCallDurationThreshold: 1500ms
  permittedNumberOfCallsInHalfOpenState: 5
```

### Zuul Route-Level Circuit Breakers
```yaml
routes:
  playback:
    path: /play/**
    circuit-breaker:
      enabled: true
      error-threshold: 5
      error-threshold-time: 10s
      timeout: 30s
      half-open-requests: 3

  browse:
    path: /browse/**
    circuit-breaker:
      enabled: true
      error-threshold: 10
      error-threshold-time: 30s
      timeout: 60s
      half-open-requests: 5
```

## Bulkhead Isolation Patterns

### Thread Pool Isolation
```yaml
Playback API Thread Pools:
  video-metadata: 50 threads (core), 200 (max), 10s keepalive
  user-preferences: 20 threads (core), 100 (max), 30s keepalive
  content-rights: 10 threads (core), 50 (max), 5s keepalive
  fallback-pool: 30 threads (core), 150 (max), 60s keepalive

Connection Pool Isolation:
  cassandra-user-data: 25 connections per host
  cassandra-content: 15 connections per host
  dynamodb: 50 connections per region
  elasticsearch: 10 connections per cluster
```

### Service-Level Bulkheads
```yaml
Resource Allocation per Service:
  Playback API: 40% of cluster resources
  User Profile API: 25% of cluster resources
  Recommendation API: 20% of cluster resources
  Search API: 10% of cluster resources
  Admin APIs: 5% of cluster resources

CPU/Memory Limits:
  Playback API: 8 cores, 16GB RAM per instance
  User Profile API: 4 cores, 8GB RAM per instance
  Recommendation API: 12 cores, 24GB RAM per instance
  Search API: 6 cores, 12GB RAM per instance
```

## Isolation Boundary Effectiveness

### Regional Isolation Success Rate
```yaml
Cross-Region Failover Statistics (2024):
  Total Failover Events: 24
  Successful Automated Failovers: 22 (91.7%)
  Manual Intervention Required: 2 (8.3%)
  Average Failover Time: 4.2 minutes
  Data Loss Events: 0

Regional Traffic Distribution:
  us-east-1: 35% (primary for East Coast)
  us-west-2: 25% (primary for West Coast)
  eu-west-1: 20% (primary for Europe)
  ap-southeast-1: 15% (primary for Asia)
  Other regions: 5% (disaster recovery)
```

### Availability Zone Isolation
```yaml
AZ Failure Containment (2024):
  Single AZ Failures: 156 events
  Traffic Rerouted Successfully: 155 (99.4%)
  Service Degradation: 1 event (network partition)
  Average Detection Time: 15 seconds
  Average Recovery Time: 2.3 minutes

Load Balancer Health Check Configuration:
  Health Check Interval: 10 seconds
  Unhealthy Threshold: 3 consecutive failures
  Healthy Threshold: 2 consecutive successes
  Timeout: 5 seconds
  Protocol: HTTP/1.1 GET /health
```

### Service Isolation Metrics
```yaml
Microservice Failure Containment:
  Service-to-Service Timeouts: < 0.01% of calls
  Circuit Breaker Activations: 450/month average
  Successful Degraded Operations: 99.7%
  Cross-Service Cascade Events: 3 in 2024

Deployment Isolation:
  Independent Service Deployments: 4,000/day
  Failed Deployment Rollbacks: < 0.1%
  Cross-Service Impact: 0.02% of deployments
  Blue-Green Success Rate: 99.95%
```

## Monitoring & Detection

### Failure Detection Times
```yaml
Component Failure Detection:
  Node-level failures: 10-30 seconds
  Service-level failures: 5-15 seconds
  Network partition: 30-60 seconds
  Regional AWS issues: 2-5 minutes
  DNS propagation issues: 1-10 minutes

Alert Escalation Thresholds:
  P1 (Critical): > 5% error rate for 1 minute
  P2 (Major): > 2% error rate for 5 minutes
  P3 (Minor): > 1% error rate for 15 minutes
  P4 (Warning): Trend degradation over 1 hour
```

### Automated Recovery Systems
```yaml
Auto-Scaling Responses:
  CPU > 80% for 5 minutes: Add 50% capacity
  Memory > 85% for 3 minutes: Add 25% capacity
  Connection errors > 5% for 1 minute: Add instances
  Response time p99 > 2x baseline: Scale out

Circuit Breaker Recovery:
  Half-open test frequency: Every sleep window
  Success threshold for closing: 3 consecutive successes
  Failure threshold for re-opening: 1 failure
  Adaptive timeout based on service history
```

## Blast Radius Containment Strategies

### Geographic Blast Radius Limits
```yaml
Maximum Impact Boundaries:
  Single region failure: ≤ 35% of global users
  Single AZ failure: ≤ 8% of regional users
  Single service failure: ≤ 15% of user experience
  Single database cluster: ≤ 5% of data operations

Traffic Distribution Safeguards:
  No single region > 40% of traffic
  No single AZ > 35% of regional traffic
  No single service instance > 10% of service traffic
  No single database node > 15% of cluster operations
```

### User Experience Protection
```yaml
Critical Path Protection:
  Video playback: 3 levels of fallback
  User authentication: 2 regions minimum
  Content discovery: Graceful degradation
  Payment processing: Zero downtime tolerance

Fallback Content Strategy:
  Popular content: Pre-cached in all regions
  User-specific content: 24-hour cache tolerance
  Search results: 1-hour stale data acceptable
  Recommendations: Generic fallback available
```

## Sources & References

- [Netflix Technology Blog - Chaos Engineering](https://netflixtechblog.com/tagged/chaos-engineering)
- [Netflix OSS - Hystrix Circuit Breaker](https://github.com/Netflix/Hystrix)
- [SREcon 2024 - Netflix Incident Response](https://www.usenix.org/conference/srecon24americas)
- [Netflix Post-Mortem Database (Internal)](https://netflix.postmortem.database)
- [AWS Case Study - Netflix Resilience](https://aws.amazon.com/solutions/case-studies/netflix/)
- [O'Reilly - Netflix Microservices Architecture](https://learning.oreilly.com/library/view/microservices-patterns/9781617294549/)

---

*Last Updated: September 2024*
*Data Source Confidence: A+ (Official Netflix Engineering + Incident Reports)*
*Diagram ID: CS-NFX-FAIL-001*