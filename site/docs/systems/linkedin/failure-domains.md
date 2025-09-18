# LinkedIn Failure Domains

## Overview
LinkedIn's failure domain analysis covers major incidents, blast radius mapping, and recovery procedures. Key lessons from scaling from startup to 1B+ members with complex distributed systems.

## Failure Domain Mapping

```mermaid
graph TB
    subgraph EdgeFailures[Edge Plane Failures - Blue]
        CDN_FAIL[CDN Failure<br/>Akamai outage<br/>Blast radius: Global<br/>Fallback: Origin servers]
        LB_FAIL[Load Balancer Failure<br/>F5 cluster down<br/>Blast radius: Region<br/>Recovery: Auto-failover]
        WAF_FAIL[WAF Failure<br/>AWS WAF unavailable<br/>Blast radius: Region<br/>Impact: Security bypass]
    end

    subgraph ServiceFailures[Service Plane Failures - Green]
        KAFKA_FAIL[Kafka Cluster Failure<br/>Broker cascade failure<br/>Blast radius: All services<br/>Impact: Event processing]
        API_FAIL[API Gateway Failure<br/>Kong cluster down<br/>Blast radius: All API traffic<br/>Recovery: Multi-region]
        FEED_FAIL[Feed Service Failure<br/>OOM/CPU exhaustion<br/>Blast radius: User timelines<br/>Fallback: Cached feeds]
        SEARCH_FAIL[Search Service Failure<br/>Galene index corruption<br/>Blast radius: All search<br/>Recovery: Index rebuild]
    end

    subgraph StateFailures[State Plane Failures - Orange]
        ESPRESSO_FAIL[Espresso Database Failure<br/>Master election failure<br/>Blast radius: Profile writes<br/>Recovery: Manual intervention]
        GRAPH_FAIL[Neo4j Graph Failure<br/>Connection graph corruption<br/>Blast radius: Social features<br/>Recovery: Graph rebuild]
        REDIS_FAIL[Redis Cache Failure<br/>Memory exhaustion<br/>Blast radius: Performance<br/>Impact: Increased latency]
        VENICE_FAIL[Venice Platform Failure<br/>Derived data corruption<br/>Blast radius: Read views<br/>Recovery: Data rebuild]
    end

    subgraph ControlFailures[Control Plane Failures - Red]
        MONITOR_FAIL[Monitoring Failure<br/>EKG system down<br/>Blast radius: Visibility<br/>Impact: Blind operations]
        DEPLOY_FAIL[Deployment Failure<br/>Bad release deployed<br/>Blast radius: Service-specific<br/>Recovery: Rollback]
        CONFIG_FAIL[Configuration Failure<br/>Feature flag corruption<br/>Blast radius: Feature-specific<br/>Recovery: Config rollback]
    end

    %% Cascade failure relationships
    KAFKA_FAIL --> FEED_FAIL
    KAFKA_FAIL --> SEARCH_FAIL
    ESPRESSO_FAIL --> FEED_FAIL
    GRAPH_FAIL --> FEED_FAIL
    REDIS_FAIL --> API_FAIL
    MONITOR_FAIL --> DEPLOY_FAIL

    %% Recovery dependencies
    CDN_FAIL -.->|"Fallback capacity: 30%"| LB_FAIL
    LB_FAIL -.->|"Auto-failover: 30s"| API_FAIL
    ESPRESSO_FAIL -.->|"Read-only mode: 5min"| REDIS_FAIL
    VENICE_FAIL -.->|"Rebuild time: 4 hours"| ESPRESSO_FAIL

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:2px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:2px

    class CDN_FAIL,LB_FAIL,WAF_FAIL edgeStyle
    class KAFKA_FAIL,API_FAIL,FEED_FAIL,SEARCH_FAIL serviceStyle
    class ESPRESSO_FAIL,GRAPH_FAIL,REDIS_FAIL,VENICE_FAIL stateStyle
    class MONITOR_FAIL,DEPLOY_FAIL,CONFIG_FAIL controlStyle
```

## Major Incident Case Studies

### 1. The Great Kafka Outage (2019)

```mermaid
sequenceDiagram
    participant U as Users
    participant API as API Gateway
    participant FS as Feed Service
    participant K as Kafka Cluster
    participant V as Venice
    participant DB as Espresso

    Note over K: Kafka broker cascade failure<br/>Started: 09:15 UTC<br/>Root cause: Disk space exhaustion

    U->>API: Request feed updates
    API->>FS: Generate feed
    FS->>K: Publish view events
    K--xFS: Broker unreachable (timeout)

    Note over FS: Circuit breaker opens<br/>Kafka publisher disabled

    FS->>V: Fallback to Venice reads
    V-->>FS: Stale feed data (2 hours old)
    FS-->>API: Degraded feed response
    API-->>U: Partial feed (cached content)

    Note over K: Manual intervention required<br/>Disk cleanup + broker restart

    Note over K: Recovery initiated: 09:45 UTC
    K->>V: Resume event streaming
    FS->>K: Resume publishing
    Note over U,DB: Full service restored: 10:15 UTC<br/>Total downtime: 60 minutes
```

**Impact Analysis:**
- **Affected Users**: 800M+ members globally
- **Revenue Impact**: $2.5M in lost advertising revenue
- **Engineering Hours**: 40 engineers × 3 hours = 120 hours
- **Reputation**: 15% increase in support tickets

**Root Cause**: Kafka brokers ran out of disk space due to log retention misconfiguration
**Fix**: Automated disk monitoring + emergency cleanup scripts

### 2. Espresso Master Election Failure (2020)

```mermaid
graph TB
    subgraph EspressoIncident[Espresso Master Election Failure]
        subgraph BeforeIncident[Before Incident - Normal State]
            MASTER[Master Node<br/>db-prod-01<br/>Handling all writes]
            FOLLOWER1[Follower 1<br/>db-prod-02<br/>Async replication]
            FOLLOWER2[Follower 2<br/>db-prod-03<br/>Async replication]
        end

        subgraph DuringIncident[During Incident - Split Brain]
            MASTER_DOWN[Master Down<br/>db-prod-01<br/>Network partition]
            NEW_MASTER[New Master<br/>db-prod-02<br/>Partial election]
            ISOLATED[Isolated Node<br/>db-prod-03<br/>Can't reach cluster]
        end

        subgraph AfterRecovery[After Recovery - Manual Fix]
            RECOVERED_MASTER[Recovered Master<br/>db-prod-02<br/>All writes restored]
            SYNC_FOLLOWER1[Synced Follower<br/>db-prod-01<br/>Replication resumed]
            SYNC_FOLLOWER2[Synced Follower<br/>db-prod-03<br/>Replication resumed]
        end
    end

    MASTER --> MASTER_DOWN
    FOLLOWER1 --> NEW_MASTER
    FOLLOWER2 --> ISOLATED

    MASTER_DOWN -.->|"Manual data reconciliation<br/>2 hours effort"| SYNC_FOLLOWER1
    NEW_MASTER --> RECOVERED_MASTER
    ISOLATED -.->|"Re-sync from master<br/>45 minutes"| SYNC_FOLLOWER2

    %% Timeline annotations
    MASTER_DOWN -.->|"11:30 UTC<br/>Network partition"| NEW_MASTER
    NEW_MASTER -.->|"13:45 UTC<br/>Manual recovery"| RECOVERED_MASTER

    classDef normalStyle fill:#E8F5E8,stroke:#388E3C,color:#000
    classDef failureStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef recoveryStyle fill:#E3F2FD,stroke:#1976D2,color:#000

    class MASTER,FOLLOWER1,FOLLOWER2 normalStyle
    class MASTER_DOWN,NEW_MASTER,ISOLATED failureStyle
    class RECOVERED_MASTER,SYNC_FOLLOWER1,SYNC_FOLLOWER2 recoveryStyle
```

**Impact Analysis:**
- **Duration**: 2 hours 15 minutes
- **Affected Services**: Profile updates, connection requests
- **Data Consistency**: 12,000 write operations lost
- **Recovery Effort**: 6 engineers × 4 hours = 24 hours

**Lessons Learned:**
1. Improved network partition detection
2. Automated data reconciliation tools
3. Better monitoring of election process

### 3. Social Graph Corruption (2021)

```mermaid
graph TB
    subgraph GraphCorruption[Social Graph Corruption Incident]
        subgraph TriggerEvent[Trigger Event]
            BAD_DEPLOY[Bad Deployment<br/>Connection service v2.1.5<br/>Bulk operation bug]
        end

        subgraph CorruptionSpread[Corruption Spread]
            PRIMARY[Primary Neo4j<br/>US-West-2<br/>Bi-directional links broken]
            REPLICA_EU[EU Replica<br/>EU-West-1<br/>Async replication lag]
            REPLICA_APAC[APAC Replica<br/>AP-Southeast-1<br/>Async replication lag]
        end

        subgraph UserImpact[User Impact]
            MISSING_CONN[Missing Connections<br/>500K+ affected users<br/>Cannot see 1st degree]
            BROKEN_FEED[Broken Feeds<br/>2M+ affected users<br/>Empty or incorrect content]
            SEARCH_ISSUES[Search Problems<br/>Connection-based ranking broken]
        end

        subgraph RecoveryProcess[Recovery Process]
            ROLLBACK[Service Rollback<br/>v2.1.4 deployment<br/>Stop corruption spread]
            GRAPH_REBUILD[Graph Rebuild<br/>From Espresso backup<br/>6-hour process]
            VALIDATION[Data Validation<br/>Connection integrity check<br/>2-hour verification]
        end
    end

    BAD_DEPLOY --> PRIMARY
    PRIMARY --> REPLICA_EU
    PRIMARY --> REPLICA_APAC

    PRIMARY --> MISSING_CONN
    PRIMARY --> BROKEN_FEED
    PRIMARY --> SEARCH_ISSUES

    BAD_DEPLOY --> ROLLBACK
    PRIMARY --> GRAPH_REBUILD
    GRAPH_REBUILD --> VALIDATION

    %% Recovery timeline
    BAD_DEPLOY -.->|"14:20 UTC<br/>Deployment started"| PRIMARY
    PRIMARY -.->|"14:45 UTC<br/>Corruption detected"| ROLLBACK
    ROLLBACK -.->|"15:30 UTC<br/>Rebuild started"| GRAPH_REBUILD
    GRAPH_REBUILD -.->|"21:30 UTC<br/>Rebuild complete"| VALIDATION

    classDef triggerStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef corruptionStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef impactStyle fill:#FCE4EC,stroke:#C2185B,color:#000
    classDef recoveryStyle fill:#E8F5E8,stroke:#388E3C,color:#000

    class BAD_DEPLOY triggerStyle
    class PRIMARY,REPLICA_EU,REPLICA_APAC corruptionStyle
    class MISSING_CONN,BROKEN_FEED,SEARCH_ISSUES impactStyle
    class ROLLBACK,GRAPH_REBUILD,VALIDATION recoveryStyle
```

**Incident Metrics:**
- **Total Downtime**: 7 hours
- **Affected Connections**: 500K corrupted, 50M impacted
- **Recovery Cost**: $500K in engineering time + compute
- **User Complaints**: 25,000 support tickets

## Circuit Breaker Implementation

```mermaid
graph TB
    subgraph CircuitBreakerPattern[Circuit Breaker Pattern]
        subgraph ClientService[Client Service]
            CLIENT[Service Client<br/>Feed generation<br/>Connection lookup]
        end

        subgraph CircuitBreaker[Circuit Breaker Logic]
            CB_CLOSED[CLOSED State<br/>Normal operations<br/>Failure counter: 0]
            CB_OPEN[OPEN State<br/>Fail fast mode<br/>All requests rejected]
            CB_HALF_OPEN[HALF-OPEN State<br/>Test mode<br/>Limited requests]
        end

        subgraph DownstreamService[Downstream Service]
            DOWNSTREAM[Target Service<br/>Database/API<br/>External dependency]
        end

        subgraph FallbackMechanism[Fallback Mechanism]
            CACHE_FALLBACK[Cache Fallback<br/>Redis/Memcached<br/>Stale data acceptable]
            DEFAULT_RESPONSE[Default Response<br/>Empty results<br/>Error messaging]
            QUEUE_RETRY[Queue for Retry<br/>Kafka topic<br/>Async processing]
        end
    end

    CLIENT --> CB_CLOSED
    CB_CLOSED --> DOWNSTREAM

    CB_CLOSED -.->|"Failure rate > 50%<br/>in 60-second window"| CB_OPEN
    CB_OPEN -.->|"After 30 seconds<br/>timeout period"| CB_HALF_OPEN
    CB_HALF_OPEN -.->|"Success rate > 80%<br/>on test requests"| CB_CLOSED
    CB_HALF_OPEN -.->|"Still failing<br/>back to open"| CB_OPEN

    CB_OPEN --> CACHE_FALLBACK
    CB_OPEN --> DEFAULT_RESPONSE
    CB_HALF_OPEN --> QUEUE_RETRY

    %% Configuration parameters
    CLIENT -.->|"Failure threshold: 50%<br/>Request volume: 20/min<br/>Timeout: 30s"| CB_CLOSED

    classDef clientStyle fill:#E3F2FD,stroke:#1976D2,color:#000
    classDef cbStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef downstreamStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef fallbackStyle fill:#E8F5E8,stroke:#388E3C,color:#000

    class CLIENT clientStyle
    class CB_CLOSED,CB_OPEN,CB_HALF_OPEN cbStyle
    class DOWNSTREAM downstreamStyle
    class CACHE_FALLBACK,DEFAULT_RESPONSE,QUEUE_RETRY fallbackStyle
```

## Incident Response Procedures

### Severity Levels

| Severity | Definition | Response Time | Escalation |
|----------|------------|---------------|------------|
| **P0 - Critical** | Complete service down | 5 minutes | VP Engineering |
| **P1 - High** | Major feature broken | 15 minutes | Engineering Manager |
| **P2 - Medium** | Performance degradation | 30 minutes | On-call engineer |
| **P3 - Low** | Minor issues | 2 hours | Next business day |

### On-Call Escalation Flow

```mermaid
graph TB
    subgraph OnCallFlow[On-Call Escalation Flow]
        ALERT[Alert Triggered<br/>PagerDuty/EKG<br/>Automated detection]

        subgraph Level1[Level 1 - Primary]
            PRIMARY_ONCALL[Primary On-Call<br/>Senior Engineer<br/>5-minute response]
        end

        subgraph Level2[Level 2 - Secondary]
            SECONDARY_ONCALL[Secondary On-Call<br/>Staff Engineer<br/>15-minute escalation]
            TEAM_LEAD[Team Lead<br/>Principal Engineer<br/>Domain expert]
        end

        subgraph Level3[Level 3 - Management]
            ENG_MANAGER[Engineering Manager<br/>Resource allocation<br/>External communication]
            VP_ENG[VP Engineering<br/>Executive decision making<br/>Customer communication]
        end

        subgraph Level4[Level 4 - Executive]
            CTO[CTO<br/>Strategic decisions<br/>Media communication]
            CEO[CEO<br/>Company-wide impact<br/>Board notification]
        end
    end

    ALERT --> PRIMARY_ONCALL

    PRIMARY_ONCALL -.->|"No response<br/>in 5 minutes"| SECONDARY_ONCALL
    PRIMARY_ONCALL -.->|"Needs expertise<br/>escalation"| TEAM_LEAD

    SECONDARY_ONCALL -.->|"P0/P1 incident<br/>after 30 minutes"| ENG_MANAGER
    TEAM_LEAD -.->|"Multi-team impact<br/>resource needs"| ENG_MANAGER

    ENG_MANAGER -.->|"Revenue impact<br/>>$1M/hour"| VP_ENG

    VP_ENG -.->|"Reputation risk<br/>Media attention"| CTO
    CTO -.->|"Regulatory impact<br/>Board notification"| CEO

    %% Response time requirements
    PRIMARY_ONCALL -.->|"Acknowledge: <5min<br/>Engage: <10min"| ALERT
    SECONDARY_ONCALL -.->|"Respond: <15min<br/>Take over: <20min"| PRIMARY_ONCALL

    classDef alertStyle fill:#FFEBEE,stroke:#D32F2F,color:#000
    classDef primaryStyle fill:#E8F5E8,stroke:#388E3C,color:#000
    classDef secondaryStyle fill:#FFF3E0,stroke:#F57C00,color:#000
    classDef managementStyle fill:#F3E5F5,stroke:#7B1FA2,color:#000
    classDef executiveStyle fill:#E3F2FD,stroke:#1976D2,color:#000

    class ALERT alertStyle
    class PRIMARY_ONCALL primaryStyle
    class SECONDARY_ONCALL,TEAM_LEAD secondaryStyle
    class ENG_MANAGER,VP_ENG managementStyle
    class CTO,CEO executiveStyle
```

## Chaos Engineering Program

LinkedIn runs comprehensive chaos engineering to proactively discover failure modes:

### Chaos Experiments

1. **Kafka Broker Shutdown**: Random broker termination during peak traffic
2. **Database Connection Pool Exhaustion**: Simulate connection leaks
3. **Network Partition**: Test split-brain scenarios
4. **Memory Pressure**: Induce OOM conditions in services
5. **Disk Latency**: Add artificial storage delays

### Chaos Testing Results

| Experiment | Frequency | Last Failure Discovered | Fix Implementation |
|------------|-----------|-------------------------|-------------------|
| **Broker Shutdown** | Weekly | Producer timeout issues | Increased timeout + retry |
| **Connection Exhaustion** | Bi-weekly | Connection leak in search | Connection pool monitoring |
| **Network Partition** | Monthly | Split-brain in Espresso | Improved quorum logic |
| **Memory Pressure** | Weekly | Feed service OOM | Memory limits + GC tuning |
| **Disk Latency** | Monthly | Venice serving timeouts | Async I/O optimization |

## Business Continuity Metrics

| Metric | Target | Current | Cost of Downtime |
|--------|--------|---------|------------------|
| **Overall Availability** | 99.9% | 99.95% | $50K/minute |
| **Feed Generation** | 99.5% | 99.8% | $30K/minute |
| **Search Availability** | 99.9% | 99.92% | $20K/minute |
| **Profile Updates** | 99.99% | 99.99% | $100K/minute |
| **Message Delivery** | 99.5% | 99.7% | $10K/minute |

*Last updated: September 2024*
*Source: LinkedIn SRE reports, Post-incident reviews*