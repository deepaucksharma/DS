# Spotify - Failure Domains & Incident Response

## Production Incidents: Learning from Real Outages

Spotify's failure domain architecture is designed around real incidents, including the March 8, 2022 global outage that affected 100M+ users for 3 hours.

```mermaid
graph TB
    subgraph EdgeFailures[Edge Plane Failure Domains]
        CDNFail[CDN Failure<br/>Fastly outage<br/>Impact: Global streaming<br/>Duration: 45 minutes<br/>Mitigation: Multi-CDN]
        DNSFail[DNS Failure<br/>Route 53 issues<br/>Impact: Service discovery<br/>Duration: 15 minutes<br/>Mitigation: Multiple providers]
        WAFFail[WAF Failure<br/>Cloudflare bypass<br/>Impact: Security rules<br/>Duration: 20 minutes<br/>Mitigation: Allow-list mode]
    end

    subgraph ServiceFailures[Service Plane Failure Domains]
        APIGatewayFail[API Gateway Cascade<br/>Kong overload<br/>Impact: All API calls<br/>Duration: 30 minutes<br/>Circuit breaker failure]
        AuthFail[Authentication Service<br/>OAuth provider down<br/>Impact: New sessions<br/>Duration: 90 minutes<br/>Existing sessions OK]
        RecommendationFail[ML Pipeline Failure<br/>Model serving crash<br/>Impact: Personalization<br/>Duration: 2 hours<br/>Fallback: Popular tracks]
        SearchFail[Search Degradation<br/>Elasticsearch cluster<br/>Impact: Discovery<br/>Duration: 45 minutes<br/>Partial results served]
    end

    subgraph StateFailures[State Plane Failure Domains]
        CassandraFail[Cassandra Region Failure<br/>March 8, 2022 incident<br/>Impact: User data access<br/>Duration: 3 hours<br/>Root cause: Config change]
        PostgresFail[PostgreSQL Primary Fail<br/>Metadata database<br/>Impact: New song access<br/>Duration: 5 minutes<br/>Auto-failover to replica]
        RedisFail[Redis Cache Cluster<br/>Session store failure<br/>Impact: Re-authentication<br/>Duration: 10 minutes<br/>Cold start performance]
        StorageFail[GCS Regional Outage<br/>Audio file access<br/>Impact: New streams<br/>Duration: 2 hours<br/>Cache kept service up]
    end

    subgraph ControlFailures[Control Plane Failure Domains]
        MonitoringFail[Monitoring Blindness<br/>DataDog outage<br/>Impact: Observability<br/>Duration: 1 hour<br/>Backup: Internal metrics]
        CICDFail[Deployment Pipeline<br/>Jenkins cluster down<br/>Impact: Hotfix deployment<br/>Duration: 4 hours<br/>Manual rollback used]
        ConfigFail[Configuration Service<br/>Feature flag corruption<br/>Impact: A/B tests<br/>Duration: 30 minutes<br/>Static config fallback]
    end

    %% Cascade Failures
    CDNFail -->|Increased load| APIGatewayFail
    APIGatewayFail -->|Auth timeout| AuthFail
    CassandraFail -->|User data loss| RecommendationFail
    PostgresFail -->|Metadata unavailable| SearchFail
    RedisFail -->|Session loss| AuthFail

    %% Recovery Paths
    StorageFail -.->|CDN cache saves day| CDNFail
    PostgresFail -.->|Auto-failover| PostgresFail
    MonitoringFail -.->|Internal metrics| ControlFailures

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff,stroke-width:3px
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff,stroke-width:3px
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff,stroke-width:3px

    class CDNFail,DNSFail,WAFFail edgeStyle
    class APIGatewayFail,AuthFail,RecommendationFail,SearchFail serviceStyle
    class CassandraFail,PostgresFail,RedisFail,StorageFail stateStyle
    class MonitoringFail,CICDFail,ConfigFail controlStyle
```

## Major Incident Analysis: March 8, 2022

### The Global Outage Timeline

**04:32 UTC**: Configuration change deployed to Cassandra cluster
**04:35 UTC**: User login failures begin in EU region
**04:41 UTC**: Cascade failure spreads to US East region
**04:45 UTC**: Complete service outage declared
**05:15 UTC**: Root cause identified (corrupt configuration)
**06:30 UTC**: Gradual service restoration begins
**07:45 UTC**: Full service restored globally

```mermaid
timeline
    title March 8, 2022 - Global Outage Timeline

    04:32 : Config Deploy
          : Cassandra cluster update
          : Automatic deployment
          : No testing in staging

    04:35 : First Failures
          : EU user logins fail
          : Database connection errors
          : Alert fatigue delays response

    04:41 : Cascade Begins
          : US East region affected
          : Cross-region replication lag
          : User data inconsistency

    04:45 : Full Outage
          : Global service down
          : 100M+ users affected
          : Revenue loss: $1M+/hour

    05:15 : Root Cause
          : Corrupt configuration identified
          : Database cluster split-brain
          : Manual intervention required

    06:30 : Recovery Start
          : Gradual region restoration
          : User data consistency checks
          : Limited service availability

    07:45 : Full Recovery
          : All regions operational
          : User experience restored
          : Post-incident review scheduled
```

## Failure Domain Mitigation Strategies

### Edge Plane Resilience
```mermaid
graph TB
    subgraph MultiCDN[Multi-CDN Strategy]
        Primary[Primary CDN: Fastly<br/>Global traffic: 70%<br/>Cache hit rate: 95%]
        Secondary[Secondary CDN: CloudFlare<br/>Failover traffic: 20%<br/>Auto-switch: 30 seconds]
        Tertiary[Tertiary CDN: AWS CloudFront<br/>Emergency fallback: 10%<br/>Basic delivery only]

        Primary -->|Failure detection| Secondary
        Secondary -->|Complete outage| Tertiary

        HealthCheck[Health Check System<br/>Synthetic monitoring<br/>5-second intervals<br/>Global probe network]

        HealthCheck --> Primary
        HealthCheck --> Secondary
        HealthCheck --> Tertiary
    end

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class Primary,Secondary,Tertiary edgeStyle
    class HealthCheck controlStyle
```

### Service Plane Resilience
- **Circuit Breakers**: Trip at 50% error rate, 10-second timeout
- **Bulkhead Pattern**: Separate thread pools per service type
- **Graceful Degradation**: Core playback continues during peripheral failures
- **Timeout Hierarchy**: API: 30s, Service: 10s, Database: 5s

### State Plane Resilience
- **Multi-Region Active-Active**: 3 regions with full data sets
- **Cross-Region Replication**: <100ms replication lag target
- **Automatic Failover**: Database promotion within 60 seconds
- **Data Consistency Checks**: Real-time validation of user data

## Blast Radius Analysis

### High Impact Failures (100M+ users affected)
1. **Cassandra Cluster Failure** - Complete user data loss
2. **API Gateway Overload** - All application functionality
3. **Authentication Service** - New sessions impossible
4. **CDN Global Failure** - No content delivery

### Medium Impact Failures (10-50M users)
1. **Regional Database Outage** - Geographic service degradation
2. **Recommendation Engine Down** - Personalization lost
3. **Search Service Degraded** - Discovery functionality reduced
4. **Payment System Issues** - Subscription management affected

### Low Impact Failures (<10M users)
1. **Single Microservice Failure** - Feature-specific degradation
2. **Cache Cluster Issues** - Performance degradation only
3. **Analytics Pipeline Down** - No user-facing impact
4. **Monitoring System Outage** - Observability reduced

## Recovery Procedures

### Automated Recovery Systems
```mermaid
graph TB
    subgraph AutoRecovery[Automated Recovery Systems]
        HealthMonitor[Health Monitoring<br/>Synthetic transactions<br/>Real user monitoring<br/>SLO tracking]

        DecisionEngine[Recovery Decision Engine<br/>Rule-based automation<br/>Machine learning alerts<br/>Escalation logic]

        subgraph Actions[Recovery Actions]
            AutoScale[Auto-scaling<br/>Horizontal pod scaling<br/>Instance replacement<br/>Load rebalancing]

            Failover[Automated Failover<br/>Database promotion<br/>Region switching<br/>Circuit breaker trips]

            Rollback[Automated Rollback<br/>Deployment reversion<br/>Configuration reset<br/>Feature flag disable]
        end

        Notification[Incident Notification<br/>PagerDuty alerts<br/>Slack integration<br/>Status page updates]
    end

    HealthMonitor --> DecisionEngine
    DecisionEngine --> AutoScale
    DecisionEngine --> Failover
    DecisionEngine --> Rollback
    DecisionEngine --> Notification

    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class DecisionEngine,AutoScale,Failover,Rollback serviceStyle
    class HealthMonitor,Notification controlStyle
```

### Manual Response Procedures

**Severity 1 (Service Down)**:
1. **0-5 minutes**: Incident commander assigned
2. **5-15 minutes**: Root cause investigation
3. **15-30 minutes**: Mitigation deployed
4. **30+ minutes**: Full service restoration

**Severity 2 (Degraded Performance)**:
1. **0-15 minutes**: Engineering team notified
2. **15-60 minutes**: Investigation and fix
3. **1-4 hours**: Monitoring and validation

## Cost of Downtime

### Revenue Impact
- **Peak Hours (6-10 PM)**: $500K/hour revenue loss
- **Off-Peak Hours**: $200K/hour revenue loss
- **Premium Subscriptions**: 60% more sensitive to outages
- **Advertising Revenue**: $100K/hour during peak

### Customer Impact
- **Churn Risk**: 5% increase after 4+ hour outage
- **App Store Reviews**: 2-star average during outages
- **Social Media Sentiment**: -80% during major incidents
- **Customer Support**: 10x normal ticket volume

This failure domain architecture and incident response system ensures Spotify can maintain 99.99% availability while learning from real production failures to continuously improve system resilience.