# Airbnb - Failure Domains & Incident Response

## Production Resilience: Managing Global Marketplace Reliability

Airbnb's failure domain architecture is designed around real marketplace scenarios where any service degradation directly impacts millions of travelers and hosts worldwide.

```mermaid
graph TB
    subgraph EdgeFailures[Edge Plane Failure Domains]
        CDNOutage[CDN Global Outage<br/>CloudFlare incident<br/>Impact: Image loading<br/>Duration: 2 hours<br/>Mitigation: Multi-CDN failover]

        ImageProcessingFail[Image Processing Failure<br/>Cloudinary service down<br/>Impact: Photo uploads<br/>Duration: 45 minutes<br/>Mitigation: Direct S3 upload]

        DNSResolutionFail[DNS Resolution Issues<br/>Route 53 problems<br/>Impact: Service discovery<br/>Duration: 15 minutes<br/>Mitigation: Multiple DNS providers]
    end

    subgraph ServiceFailures[Service Plane Failure Domains]
        SearchServiceDown[Search Service Outage<br/>Elasticsearch cluster failure<br/>Impact: Property discovery<br/>Duration: 1.5 hours<br/>Blast radius: 100% guests]

        BookingServiceDegraded[Booking Service Degraded<br/>Payment gateway timeout<br/>Impact: Reservation completion<br/>Duration: 30 minutes<br/>Revenue impact: $2M+]

        RecommendationFailure[ML Recommendation Failure<br/>TensorFlow serving crash<br/>Impact: Personalization<br/>Duration: 3 hours<br/>Fallback: Popular listings]

        MessageServiceIssues[Messaging Service Issues<br/>Host-guest communication<br/>Impact: Trip coordination<br/>Duration: 45 minutes<br/>Alternative: Email notifications]
    end

    subgraph StateFailures[State Plane Failure Domains]
        MySQLPrimaryFailure[MySQL Primary Failure<br/>Database corruption<br/>Impact: Core business logic<br/>Duration: 4 hours<br/>Recovery: Replica promotion]

        HBaseRegionFailure[HBase Region Server Failure<br/>Analytics data loss<br/>Impact: Reporting delays<br/>Duration: 2 hours<br/>Data recovery: HDFS backup]

        RedisClusterFailure[Redis Cluster Failure<br/>Session store unavailable<br/>Impact: User re-authentication<br/>Duration: 20 minutes<br/>Cold start performance hit]

        S3RegionalOutage[S3 Regional Outage<br/>Image storage inaccessible<br/>Impact: Listing photos<br/>Duration: 3 hours<br/>Fallback: Cross-region sync]
    end

    subgraph ControlFailures[Control Plane Failure Domains]
        MonitoringBlackout[Monitoring System Blackout<br/>DataDog infrastructure failure<br/>Impact: Observability loss<br/>Duration: 1 hour<br/>Backup: Internal metrics]

        DeploymentPipelineDown[CI/CD Pipeline Failure<br/>Spinnaker cluster issues<br/>Impact: Hotfix deployment<br/>Duration: 6 hours<br/>Manual deployment used]

        ConfigServiceCorruption[Configuration Service Failure<br/>Feature flag corruption<br/>Impact: A/B tests<br/>Duration: 30 minutes<br/>Static config rollback]

        BackupSystemFailure[Backup System Failure<br/>Cross-region sync broken<br/>Impact: Disaster recovery<br/>Duration: 8 hours<br/>Manual backup verification]
    end

    %% Cascade Failure Paths
    CDNOutage -->|Increased origin load| S3RegionalOutage
    SearchServiceDown -->|Load spillover| RecommendationFailure
    MySQLPrimaryFailure -->|Session invalidation| RedisClusterFailure
    BookingServiceDegraded -->|Payment retry storm| MySQLPrimaryFailure

    %% Recovery Dependencies
    ImageProcessingFail -.->|Fallback path| S3RegionalOutage
    RecommendationFailure -.->|Graceful degradation| SearchServiceDown
    MonitoringBlackout -.->|Blind recovery| DeploymentPipelineDown

    %% Apply four-plane colors with thicker borders for failures
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:3px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:3px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:3px

    class CDNOutage,ImageProcessingFail,DNSResolutionFail edgeStyle
    class SearchServiceDown,BookingServiceDegraded,RecommendationFailure,MessageServiceIssues serviceStyle
    class MySQLPrimaryFailure,HBaseRegionFailure,RedisClusterFailure,S3RegionalOutage stateStyle
    class MonitoringBlackout,DeploymentPipelineDown,ConfigServiceCorruption,BackupSystemFailure controlStyle
```

## Major Incident Case Study: June 2019 Search Outage

### Timeline: Complete Search Service Failure

**14:23 PST**: Elasticsearch cluster upgrade begins (planned maintenance)
**14:35 PST**: Primary search index becomes corrupted during rolling upgrade
**14:37 PST**: Search queries return zero results globally
**14:39 PST**: Incident declared - complete search functionality loss
**14:45 PST**: Traffic spike as users retry searches, cascading to recommendation service
**15:10 PST**: Emergency rollback initiated to previous Elasticsearch version
**15:45 PST**: Index rebuild begins from MySQL master data
**16:30 PST**: Partial search functionality restored (50% of listings)
**17:15 PST**: Full search functionality restored globally

```mermaid
timeline
    title June 2019 Search Outage - $8M Revenue Impact

    14:23 : Planned Upgrade
          : Elasticsearch 6.8 → 7.0
          : Rolling upgrade strategy
          : Expected 15-minute window

    14:35 : Index Corruption
          : Mapping incompatibility
          : Shard allocation failure
          : Zero search results

    14:39 : Incident Declaration
          : P0 incident declared
          : War room activated
          : Engineering teams mobilized

    14:45 : Cascade Failure
          : Recommendation service overload
          : User retry storm
          : API gateway throttling

    15:10 : Emergency Rollback
          : Elasticsearch downgrade
          : Data consistency checks
          : Service restart sequence

    15:45 : Index Rebuild
          : MySQL data export
          : Parallel index creation
          : Gradual traffic restoration

    17:15 : Full Recovery
          : All services operational
          : Performance normalized
          : Post-incident review scheduled
```

**Impact Analysis:**
- **Revenue Loss**: $8M in bookings during 4-hour outage
- **User Impact**: 100% of guests unable to search properties
- **Geographic Scope**: Global outage affecting all markets
- **Recovery Strategy**: Complete rollback + index rebuild (52 minutes)

## Failure Domain Mitigation Architecture

### Multi-Region Resilience Strategy

```mermaid
graph TB
    subgraph MultiRegionFailover[Multi-Region Failover Architecture]
        subgraph USEast[US-East-1 Primary Region]
            USEastAPI[API Gateway<br/>Primary traffic<br/>70% global load<br/>Active-active mode]

            USEastDB[MySQL Primary<br/>Write operations<br/>Real-time replication<br/>Cross-region sync]

            USEastSearch[Elasticsearch Primary<br/>Full search index<br/>Real-time updates<br/>Master cluster]

            USEastCache[Redis Primary<br/>Session store<br/>Hot data cache<br/>Cross-region replication]
        end

        subgraph USWest[US-West-2 Backup Region]
            USWestAPI[API Gateway<br/>Failover traffic<br/>20% global capacity<br/>Hot standby mode]

            USWestDB[MySQL Replica<br/>Read operations<br/>Async replication<br/>Promotion capable]

            USWestSearch[Elasticsearch Replica<br/>Backup search index<br/>30-second lag<br/>Automatic failover]

            USWestCache[Redis Replica<br/>Session backup<br/>Warm cache<br/>Failover ready]
        end

        subgraph Europe[EU-West-1 Regional]
            EuropeAPI[API Gateway<br/>European traffic<br/>GDPR compliance<br/>Local data processing]

            EuropeDB[MySQL Regional<br/>EU user data<br/>Data residency<br/>Local compliance]

            EuropeSearch[Elasticsearch EU<br/>Localized search<br/>Regional content<br/>Language optimization]

            EuropeCache[Redis EU<br/>Regional sessions<br/>Low-latency cache<br/>GDPR compliant]
        end

        subgraph FailoverLogic[Automated Failover Logic]
            HealthChecks[Health Check System<br/>5-second intervals<br/>Multi-metric validation<br/>Automated decisions]

            TrafficManager[Traffic Manager<br/>Route 53 health checks<br/>Weighted routing<br/>Automatic failover]

            DatabaseFailover[Database Failover<br/>Automated promotion<br/>Data consistency checks<br/>Connection rerouting]

            CacheWarming[Cache Warming<br/>Predictive pre-loading<br/>Session replication<br/>Hot data migration]
        end
    end

    %% Primary connections
    USEastAPI --> USEastDB
    USEastAPI --> USEastSearch
    USEastAPI --> USEastCache

    %% Replication connections
    USEastDB --> USWestDB
    USEastSearch --> USWestSearch
    USEastCache --> USWestCache

    %% Regional independence
    EuropeAPI --> EuropeDB
    EuropeAPI --> EuropeSearch
    EuropeAPI --> EuropeCache

    %% Failover orchestration
    HealthChecks --> TrafficManager
    TrafficManager --> DatabaseFailover
    DatabaseFailover --> CacheWarming

    %% Failover paths
    USEastAPI -.->|Failure detected| USWestAPI
    USEastDB -.->|Auto-promotion| USWestDB
    USEastSearch -.->|Index switch| USWestSearch

    classDef primaryStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef backupStyle fill:#10B981,stroke:#059669,color:#fff
    classDef regionalStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef failoverStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class USEastAPI,USEastDB,USEastSearch,USEastCache primaryStyle
    class USWestAPI,USWestDB,USWestSearch,USWestCache backupStyle
    class EuropeAPI,EuropeDB,EuropeSearch,EuropeCache regionalStyle
    class HealthChecks,TrafficManager,DatabaseFailover,CacheWarming failoverStyle
```

### Circuit Breaker Implementation

```mermaid
graph TB
    subgraph CircuitBreakerPattern[Circuit Breaker Pattern Implementation]
        subgraph ExternalServices[External Service Dependencies]
            PaymentGateway[Payment Gateway<br/>Stripe/Braintree<br/>Timeout: 30s<br/>Failure threshold: 50%]

            EmailService[Email Service<br/>SendGrid/Mailgun<br/>Timeout: 10s<br/>Failure threshold: 30%]

            SMSService[SMS Service<br/>Twilio/Nexmo<br/>Timeout: 5s<br/>Failure threshold: 40%]

            MapService[Map Service<br/>Google Maps API<br/>Timeout: 15s<br/>Failure threshold: 20%]
        end

        subgraph CircuitBreakerStates[Circuit Breaker States]
            ClosedState[Closed State<br/>Normal operation<br/>All requests pass<br/>Monitor failure rate<br/>Reset on success threshold]

            OpenState[Open State<br/>Fail fast mode<br/>Reject all requests<br/>Return cached response<br/>Check every 30 seconds]

            HalfOpenState[Half-Open State<br/>Test recovery<br/>Allow limited requests<br/>Monitor success rate<br/>Transition based on results]
        end

        subgraph FallbackStrategies[Fallback Strategies]
            CachedResponse[Cached Response<br/>Return last known good<br/>Redis-backed cache<br/>Stale data acceptable<br/>Degraded experience]

            DefaultResponse[Default Response<br/>Generic content<br/>Safe defaults<br/>Minimal functionality<br/>Service continuity]

            AlternativeService[Alternative Service<br/>Backup provider<br/>Different API<br/>Reduced features<br/>Automatic switching]

            GracefulDegradation[Graceful Degradation<br/>Disable feature<br/>Maintain core function<br/>User notification<br/>Manual override]
        end
    end

    %% State transitions
    ClosedState -->|Failure threshold exceeded| OpenState
    OpenState -->|Timeout elapsed| HalfOpenState
    HalfOpenState -->|Success threshold met| ClosedState
    HalfOpenState -->|Failures continue| OpenState

    %% Service connections
    PaymentGateway --> ClosedState
    EmailService --> OpenState
    SMSService --> HalfOpenState
    MapService --> ClosedState

    %% Fallback connections
    OpenState --> CachedResponse
    OpenState --> DefaultResponse
    OpenState --> AlternativeService
    OpenState --> GracefulDegradation

    classDef serviceStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef stateStyle fill:#10B981,stroke:#059669,color:#fff
    classDef fallbackStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class PaymentGateway,EmailService,SMSService,MapService serviceStyle
    class ClosedState,OpenState,HalfOpenState stateStyle
    class CachedResponse,DefaultResponse,AlternativeService,GracefulDegradation fallbackStyle
```

## Incident Response Procedures

### Severity Classification & Response

```mermaid
graph TB
    subgraph IncidentSeverity[Incident Severity Classification]
        subgraph P0Incidents[P0 - Critical Service Down]
            P0Criteria[P0 Criteria<br/>Booking flow broken<br/>Payment processing down<br/>Global search failure<br/>Data corruption detected]

            P0Response[P0 Response<br/>Immediate escalation<br/>War room activation<br/>Executive notification<br/>All hands on deck]

            P0SLA[P0 SLA<br/>Response: 5 minutes<br/>Update: Every 15 minutes<br/>Resolution: 2 hours<br/>Post-mortem: 48 hours]
        end

        subgraph P1Incidents[P1 - Major Degradation]
            P1Criteria[P1 Criteria<br/>High error rates<br/>Performance degradation<br/>Regional outages<br/>Feature unavailable]

            P1Response[P1 Response<br/>Primary team activation<br/>On-call escalation<br/>Manager notification<br/>Focused response]

            P1SLA[P1 SLA<br/>Response: 15 minutes<br/>Update: Every 30 minutes<br/>Resolution: 4 hours<br/>Post-mortem: 72 hours]
        end

        subgraph P2Incidents[P2 - Minor Issues]
            P2Criteria[P2 Criteria<br/>Isolated failures<br/>Non-critical features<br/>Performance slowdown<br/>Monitoring alerts]

            P2Response[P2 Response<br/>Standard on-call<br/>Business hours priority<br/>Team lead notification<br/>Normal procedures]

            P2SLA[P2 SLA<br/>Response: 1 hour<br/>Update: Daily<br/>Resolution: 24 hours<br/>Post-mortem: Optional]
        end
    end

    subgraph EscalationPaths[Escalation Paths]
        OnCallEngineer[On-Call Engineer<br/>First responder<br/>Initial assessment<br/>Immediate actions<br/>Status updates]

        TeamLead[Team Lead<br/>Technical guidance<br/>Resource coordination<br/>Escalation decisions<br/>Communication hub]

        IncidentCommander[Incident Commander<br/>Overall coordination<br/>External communication<br/>Resource allocation<br/>Decision authority]

        ExecutiveTeam[Executive Team<br/>Business impact<br/>PR coordination<br/>Customer communication<br/>Strategic decisions]
    end

    P0Criteria --> P0Response
    P0Response --> P0SLA
    P1Criteria --> P1Response
    P1Response --> P1SLA
    P2Criteria --> P2Response
    P2Response --> P2SLA

    %% Escalation flow
    OnCallEngineer --> TeamLead
    TeamLead --> IncidentCommander
    IncidentCommander --> ExecutiveTeam

    %% Cross-severity escalation
    P2Response -.->|Escalation needed| P1Response
    P1Response -.->|Major impact| P0Response

    classDef p0Style fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef p1Style fill:#F59E0B,stroke:#D97706,color:#fff
    classDef p2Style fill:#10B981,stroke:#059669,color:#fff
    classDef escalationStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class P0Criteria,P0Response,P0SLA p0Style
    class P1Criteria,P1Response,P1SLA p1Style
    class P2Criteria,P2Response,P2SLA p2Style
    class OnCallEngineer,TeamLead,IncidentCommander,ExecutiveTeam escalationStyle
```

## Business Impact Analysis

### Revenue Impact by Failure Type

**Critical Service Failures (P0)**:
- **Search Service Down**: $2M/hour (zero new bookings)
- **Payment Processing Failure**: $1.5M/hour (existing bookings lost)
- **Database Corruption**: $3M/hour + recovery costs
- **Global CDN Outage**: $500K/hour (user experience degradation)

**Regional Service Degradation (P1)**:
- **Single Region Down**: $400K/hour (20% traffic impact)
- **Mobile App Issues**: $600K/hour (60% mobile traffic)
- **Messaging Service Down**: $200K/hour (trip coordination issues)
- **Recommendation Engine Failure**: $100K/hour (conversion reduction)

### Customer Experience Impact

**Trust & Safety Implications**:
- **Identity Verification Down**: New host onboarding blocked
- **Review System Failure**: Trust signals unavailable
- **Fraud Detection Offline**: Increased risk exposure
- **Background Checks Failed**: Safety compliance issues

**Host Business Impact**:
- **Calendar Sync Issues**: Double booking risks
- **Pricing Tool Failure**: Revenue optimization lost
- **Payout Delays**: Cash flow problems for hosts
- **Analytics Unavailable**: Business decision delays

This comprehensive failure domain architecture enables Airbnb to maintain marketplace reliability while minimizing the business impact of inevitable infrastructure failures across the global platform.