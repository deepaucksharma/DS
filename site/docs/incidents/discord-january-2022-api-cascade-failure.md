# Discord January 2022 - API Cascade Failure & Database Cluster Meltdown

*"A Redis primary migration triggered API failures, exposing cascading database cluster dependencies across 400M users"*

## Incident Overview

| Attribute | Value |
|-----------|-------|
| **Date** | January 2022 |
| **Duration** | 4 hours, 23 minutes |
| **Trigger Time** | 14:30 UTC |
| **Resolution Time** | 18:53 UTC |
| **Impact** | Global Discord service disruption |
| **Users Affected** | 150M+ active users |
| **Servers Affected** | 19M+ Discord servers |
| **Message Delivery** | 95% failure rate |
| **Estimated Cost** | $18M+ in lost engagement |
| **Root Cause** | Google Cloud Platform Redis migration cascade |

## The Great Discord Meltdown

```mermaid
gantt
    title Discord January 2022 - API & Database Cluster Catastrophe
    dateFormat HH:mm
    axisFormat %H:%M UTC

    section Normal Operations
    Standard API Performance :done, normal, 14:00, 14:30

    section Primary Incident
    Redis Primary Migration :crit, redis, 14:30, 14:35
    API Service Degradation :crit, api, 14:35, 15:30
    Database Cluster Issues :crit, db, 15:00, 17:30

    section Secondary Failures
    WebSocket Disconnections :crit, ws, 14:45, 16:30
    Message Queue Backlog :crit, queue, 15:00, 18:00
    Voice Channel Failures :crit, voice, 15:15, 17:45

    section Recovery Operations
    Database Cluster Recovery :active, dbfix, 17:30, 18:30
    API Service Restoration :active, apifix, 18:00, 18:45
    Full Service Recovery :done, recover, 18:45, 18:53
```

## Architecture Under Siege

```mermaid
graph TB
    subgraph Users[400M Global Users]
        DESKTOP[Desktop App<br/>💻 Connection drops]
        MOBILE[Mobile App<br/>📱 Push notifications fail]
        WEB[Web Client<br/>🌐 Constant reconnects]
        BOTS[Bot Ecosystem<br/>🤖 API failures]
    end

    subgraph EdgePlane["Edge Plane"]
        GATEWAY[Discord Gateway<br/>✅ Accepting connections<br/>⚠️ WebSocket drops]
        CDN[CloudFlare CDN<br/>✅ Static assets OK<br/>📊 API requests timing out]
    end

    subgraph ServicePlane["Service Plane"]
        subgraph APILayer[API Layer - CRITICAL FAILURE]
            API1[API Server 1<br/>❌ Redis connection lost]
            API2[API Server 2<br/>❌ Redis connection lost]
            API3[API Server N<br/>❌ Redis connection lost]
        end

        subgraph CoreServices[Core Services - DEGRADED]
            MSG[Message Service<br/>❌ 95% failure rate<br/>📊 Queue backing up]
            GUILD[Guild Service<br/>❌ Server list loading fails]
            USER[User Service<br/>❌ Profile/auth issues]
            VOICE[Voice Service<br/>❌ Channel join failures]
        end

        subgraph RealtimeLayer[Real-time Layer]
            WS[WebSocket Handlers<br/>❌ Mass disconnections<br/>🔄 Reconnect storm]
            PRES[Presence Service<br/>❌ Status updates fail]
        end
    end

    subgraph StatePlane["State Plane"]
        subgraph RedisCluster[Redis HA Cluster - EPICENTER]
            REDIS_OLD[Redis Primary (Old)<br/>❌ GCP migrated away<br/>💀 Node offline]
            REDIS_NEW[Redis Primary (New)<br/>⚠️ Promoting to primary<br/>🔄 Failover in progress]
            REDIS_R1[Redis Replica 1<br/>⚠️ Lag: 30+ seconds]
            REDIS_R2[Redis Replica 2<br/>⚠️ Lag: 30+ seconds]
        end

        subgraph DatabaseCluster[Database Cluster - SECONDARY FAILURE]
            POSTGRES1[PostgreSQL Primary<br/>❌ Connection pool exhausted<br/>📊 Slow queries: 5s+]
            POSTGRES2[PostgreSQL Replica<br/>❌ Replication lag: 2 minutes]
            CASSANDRA[Cassandra Cluster<br/>❌ Message storage degraded<br/>📚 Read timeouts]
        end

        subgraph MessageQueue[Message Queue System]
            KAFKA[Kafka Cluster<br/>⚠️ Consumer lag growing<br/>📈 2M+ backlogged messages]
        end
    end

    subgraph ControlPlane["Control Plane"]
        subgraph Monitoring[Monitoring - OVERWHELMED]
            METRICS[Prometheus<br/>❌ High cardinality explosion<br/>📊 Scrape timeouts]
            DASH[Grafana<br/>⚠️ Dashboard loading slowly<br/>📈 Alert fatigue]
        end

        subgraph Deployment[Deployment & Config]
            K8S[Kubernetes<br/>✅ Pods healthy<br/>⚠️ Service discovery issues]
            CONFIG[Config Service<br/>❌ Redis dependency<br/>❌ Can't update configs]
        end
    end

    %% Critical failure paths
    REDIS_OLD -.->|❌ GCP MIGRATION| REDIS_NEW
    REDIS_NEW -.->|❌ FAILOVER DELAY| API1
    REDIS_NEW -.->|❌ FAILOVER DELAY| API2
    REDIS_NEW -.->|❌ FAILOVER DELAY| API3

    API1 -.->|❌ OVERLOAD| POSTGRES1
    API2 -.->|❌ OVERLOAD| POSTGRES1
    API3 -.->|❌ OVERLOAD| POSTGRES1

    POSTGRES1 -.->|❌ SLOW QUERIES| MSG
    POSTGRES1 -.->|❌ SLOW QUERIES| GUILD
    POSTGRES1 -.->|❌ SLOW QUERIES| USER

    %% User experience degradation
    DESKTOP --> GATEWAY
    MOBILE --> GATEWAY
    WEB --> GATEWAY
    BOTS --> CDN

    GATEWAY --> WS
    CDN --> API1

    WS -.->|❌ MASS DISCONNECTS| PRES
    API1 -.->|❌ FAILURES| MSG

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class GATEWAY,CDN edgeStyle
    class API1,API2,API3,MSG,GUILD,USER,VOICE,WS,PRES serviceStyle
    class REDIS_OLD,REDIS_NEW,REDIS_R1,REDIS_R2,POSTGRES1,POSTGRES2,CASSANDRA,KAFKA stateStyle
    class METRICS,DASH,K8S,CONFIG controlStyle
```

## Detailed Failure Sequence

### Phase 1: The Redis Migration Trigger (14:30-14:35 UTC)
```mermaid
sequenceDiagram
    participant GCP as Google Cloud Platform
    participant REDIS_OLD as Redis Primary (Old)
    participant REDIS_NEW as Redis Primary (New)
    participant API as Discord API Servers
    participant HEALTH as Health Checks

    Note over GCP,HEALTH: 14:30 UTC - Routine GCP Maintenance

    GCP->>REDIS_OLD: 🔧 Planned node migration
    REDIS_OLD->>REDIS_OLD: Begin graceful shutdown
    REDIS_OLD->>REDIS_NEW: Trigger failover process

    Note over REDIS_NEW: Promote replica to primary
    REDIS_NEW->>REDIS_NEW: ⚠️ Failover taking longer than expected

    API->>REDIS_OLD: Connection attempt
    REDIS_OLD--xAPI: ❌ Connection refused (migrated)
    API->>REDIS_NEW: Connection attempt
    REDIS_NEW--xAPI: ❌ Still promoting, not ready

    HEALTH->>API: Health check
    API->>HEALTH: ❌ Redis dependency unavailable

    Note over GCP,HEALTH: 14:35 UTC - API services start failing
```

### Phase 2: The API Cascade (14:35-15:30 UTC)
```mermaid
sequenceDiagram
    participant USERS as Discord Users
    participant API as API Gateway
    participant REDIS as Redis (Struggling)
    participant POSTGRES as PostgreSQL
    participant QUEUE as Message Queue

    Note over USERS,QUEUE: 14:35 UTC - API Failures Begin

    USERS->>API: Send message request
    API->>REDIS: Check rate limits
    REDIS--xAPI: ❌ Timeout (failover still happening)
    API->>API: Fallback to database for rate limits

    API->>POSTGRES: Rate limit check (expensive query)
    POSTGRES->>POSTGRES: ⚠️ Query taking 3+ seconds
    API--xUSERS: ❌ Request timeout (30s limit)

    Note over API: API servers start queuing requests
    USERS->>API: Retry message send
    API->>QUEUE: Queue message for later
    QUEUE->>QUEUE: ❌ Queue backing up (500k+ messages)

    Note over USERS,QUEUE: 15:00 UTC - 95% API failure rate
```

### Phase 3: The Database Overload (15:00-17:30 UTC)
```mermaid
sequenceDiagram
    participant API as API Servers
    participant REDIS as Redis (Recovering)
    participant POSTGRES as PostgreSQL Primary
    participant REPLICA as PostgreSQL Replica
    participant CACHE as Application Cache

    Note over API,CACHE: 15:00 UTC - Database Cluster Under Siege

    REDIS->>API: ✅ Redis primary online
    API->>API: Resume normal operations

    Note over API: Massive retry storm from users
    API->>POSTGRES: Flood of deferred requests
    POSTGRES->>POSTGRES: ❌ Connection pool exhausted
    POSTGRES->>POSTGRES: ❌ Slow queries: 5+ seconds

    API->>REPLICA: Attempt read fallback
    REPLICA->>REPLICA: ❌ Replication lag: 2+ minutes
    REPLICA--xAPI: ❌ Stale data, inconsistent state

    CACHE->>CACHE: ❌ Cache invalidation storm
    API->>POSTGRES: Re-populate cache (expensive)
    POSTGRES->>POSTGRES: ❌ Even more load

    Note over API,CACHE: 17:30 UTC - Database cluster at breaking point
```

### Phase 4: The Recovery (17:30-18:53 UTC)
```mermaid
sequenceDiagram
    participant SRE as Discord SRE
    participant POSTGRES as PostgreSQL
    participant API as API Services
    participant QUEUE as Message Queue
    participant USERS as Users

    Note over SRE,USERS: 17:30 UTC - Emergency Response

    SRE->>POSTGRES: Add read replicas
    SRE->>POSTGRES: Optimize slow queries
    SRE->>API: Implement circuit breakers

    API->>API: Enable degraded mode
    API->>QUEUE: Process backlog gradually
    QUEUE->>QUEUE: ✅ Processing 2M+ queued messages

    Note over POSTGRES: 18:00 UTC - DB performance stabilizing
    POSTGRES->>API: Response times < 500ms
    API->>USERS: ✅ Messages starting to deliver

    SRE->>SRE: Gradual traffic increase
    Note over SRE,USERS: 18:53 UTC - Full service restored
```

## Impact Analysis & Metrics

### Service Degradation Timeline
```mermaid
graph LR
    subgraph ServiceHealth[Service Health Over Time]
        T1[14:30 UTC<br/>100% Healthy<br/>Normal operations]
        T2[14:35 UTC<br/>40% Degraded<br/>API failures begin]
        T3[15:00 UTC<br/>5% Functional<br/>Mass failures]
        T4[17:30 UTC<br/>30% Recovering<br/>DB stabilizing]
        T5[18:53 UTC<br/>100% Restored<br/>Full recovery]
    end

    T1 --> T2
    T2 --> T3
    T3 --> T4
    T4 --> T5

    style T1 fill:#00AA00
    style T2 fill:#FF8800
    style T3 fill:#CC0000
    style T4 fill:#FF8800
    style T5 fill:#00AA00
```

### Business Impact Breakdown
| Component | Impact | Duration | Est. Cost |
|-----------|--------|----------|-----------|
| **User Engagement** | 150M users disconnected | 4h 23m | $8M |
| **Gaming Communities** | 19M servers disrupted | 4h 23m | $4M |
| **Discord Nitro** | Subscription issues | 4h 23m | $2M |
| **Bot Ecosystem** | API-dependent bots down | 4h 23m | $1.5M |
| **Content Creators** | Stream disruptions | 4h 23m | $1M |
| **Enterprise** | Business communication down | 4h 23m | $1M |
| **SLA Credits** | Enterprise customers | 4h 23m | $0.5M |
| **Total Estimated Cost** | | | **$18M** |

## Technical Deep Dive

### Redis HA Failover Process
```mermaid
graph TB
    subgraph BeforeFailover[Before Failover - Normal State]
        RP1[Redis Primary<br/>GCP Node A<br/>✅ Serving requests]
        RR1[Redis Replica 1<br/>GCP Node B<br/>✅ Syncing]
        RR2[Redis Replica 2<br/>GCP Node C<br/>✅ Syncing]

        RP1 --> RR1
        RP1 --> RR2
    end

    subgraph DuringFailover[During Failover - The Gap]
        RP2[Redis Primary<br/>❌ Node migrated<br/>💀 Offline]
        RR3[Redis Replica 1<br/>⚠️ Promoting to primary<br/>🔄 Not ready yet]
        RR4[Redis Replica 2<br/>⚠️ Waiting for new primary<br/>📊 Stale data]

        RP2 -.->|❌ Connection lost| RR3
    end

    subgraph AfterFailover[After Failover - New Topology]
        RP3[Redis Primary<br/>✅ New primary online<br/>GCP Node B]
        RR5[Redis Replica 1<br/>✅ Syncing with new primary<br/>GCP Node C]
        RR6[Redis Replica 2<br/>✅ New replica provisioned<br/>GCP Node D]

        RP3 --> RR5
        RP3 --> RR6
    end

    BeforeFailover ==> DuringFailover
    DuringFailover ==> AfterFailover

    style RP2 fill:#CC0000
    style RR3 fill:#FF8800
    style RR4 fill:#FF8800
```

### API Dependency Cascade
```mermaid
graph TD
    A[Redis Unavailable] --> B[Rate Limiting Fails]
    B --> C[Fallback to Database]
    C --> D[Database Overload]
    D --> E[Slow Query Performance]
    E --> F[API Timeouts]
    F --> G[User Retry Storm]
    G --> H[More Database Load]
    H --> I[Cascading Failure]

    A --> J[Session Storage Fails]
    J --> K[User Auth Issues]
    K --> L[Re-authentication Requests]
    L --> G

    A --> M[Cache Invalidation]
    M --> N[Cache Miss Storm]
    N --> O[Database Read Spike]
    O --> H

    style A fill:#CC0000
    style I fill:#CC0000
```

## Root Cause Analysis

### Contributing Factors Analysis
```mermaid
mindmap
  root)Discord Jan 2022 RCA(
    Infrastructure
      GCP Redis Migration
      Failover Duration
      Single Point of Failure
    Architecture
      API Redis Dependency
      Database Fallback Patterns
      Rate Limiting Design
    Operations
      Insufficient Monitoring
      Manual Intervention Delay
      Capacity Planning
    External
      GCP Maintenance Window
      User Retry Behavior
      Traffic Patterns
```

### The Dependency Chain Problem
```mermaid
graph TD
    subgraph CriticalPath[Critical Dependency Chain]
        A[User Request] --> B[API Gateway]
        B --> C[Redis Rate Limit Check]
        C --> D[Business Logic]
        D --> E[Database Write]
        E --> F[Message Queue]
        F --> G[WebSocket Delivery]
    end

    subgraph FailureMode[Single Point of Failure]
        C -.->|❌ Redis fails| H[Fallback to Database]
        H --> I[Expensive SQL Query]
        I --> J[Database Overload]
        J --> K[API Timeouts]
        K --> L[User Retry Storm]
        L --> M[System Collapse]
    end

    style C fill:#CC0000
    style M fill:#CC0000
```

## Remediation & Prevention

### Immediate Actions (Completed)
- [x] **Database Scaling**: Added emergency read replicas
- [x] **Circuit Breakers**: Implemented API-level circuit breakers
- [x] **Queue Processing**: Gradual processing of 2M+ message backlog
- [x] **Query Optimization**: Fixed slow PostgreSQL queries

### Short-term Fixes (30 days)
- [x] **Redis Cluster Upgrade**: Multi-region Redis deployment
- [x] **Fallback Improvement**: Better database fallback patterns
- [x] **Rate Limiting**: Distributed rate limiting without Redis dependency
- [x] **Monitoring Enhancement**: Redis failover detection and alerting

### Long-term Solutions (6 months)
- [ ] **Microservice Isolation**: Reduce cross-service dependencies
- [ ] **Graceful Degradation**: Per-feature circuit breakers
- [ ] **Regional Failover**: Multi-region active-active architecture
- [ ] **Chaos Engineering**: Regular failover testing

## Prevention Framework

### Dependency Management Strategy
```mermaid
flowchart TD
    A[New Feature Design] --> B{Single Point of Failure?}
    B -->|Yes| C[Design Fallback Pattern]
    B -->|No| D[Implement Feature]

    C --> E{Fallback Graceful?}
    E -->|Yes| F[Add Circuit Breaker]
    E -->|No| G[Redesign Architecture]

    F --> H[Add Monitoring]
    G --> C

    H --> I[Chaos Testing]
    I --> J[Production Deployment]

    style C fill:#FF8800
    style G fill:#CC0000
    style I fill:#00AA00
```

### Redis HA Best Practices
```mermaid
graph LR
    A[Redis Design] --> B[Multi-Region Deployment]
    B --> C[Automated Failover < 30s]
    C --> D[Connection Pooling]
    D --> E[Circuit Breakers]
    E --> F[Graceful Degradation]

    F --> G[Regular Failover Testing]
    G --> H[Monitoring & Alerting]
    H --> I[Disaster Recovery Plan]

    style B fill:#00AA00
    style C fill:#00AA00
    style F fill:#00AA00
```

## Engineering Lessons

### The Redis Dependency Anti-Pattern
```mermaid
sequenceDiagram
    participant API as API Service
    participant REDIS as Redis
    participant DB as Database
    participant USER as User

    Note over API,USER: Anti-Pattern: Hard Redis Dependency

    USER->>API: Request
    API->>REDIS: Required operation
    REDIS--xAPI: ❌ Unavailable
    API--xUSER: ❌ 500 Error (no fallback)

    Note over API,USER: Better Pattern: Graceful Degradation

    USER->>API: Request
    API->>REDIS: Try Redis first
    REDIS--xAPI: ❌ Unavailable
    API->>DB: Fallback to database
    DB->>API: ✅ Response (slower but works)
    API->>USER: ✅ Success (degraded performance)
```

### The Thundering Herd Problem
```mermaid
graph TD
    A[Service Restored] --> B[All Users Retry Simultaneously]
    B --> C[10x Normal Traffic]
    C --> D[Service Overload Again]
    D --> E[Second Failure]
    E --> F[More Retries]
    F --> G[Cascading Failures]

    H[Better: Exponential Backoff] --> I[Staggered Retries]
    I --> J[Jitter Added]
    J --> K[Gradual Recovery]

    style G fill:#CC0000
    style K fill:#00AA00
```

## War Stories & Lessons for 3 AM Engineers

### 🚨 Critical Warning Signs
1. **Redis failover taking >30 seconds** = architectural problem
2. **API timeouts + database slow queries** = dependency cascade
3. **Message queue backlog growing** = downstream bottleneck
4. **WebSocket mass disconnections** = session storage issue

### 🛠️ Emergency Procedures
```mermaid
flowchart TD
    A[Redis/Cache Failure] --> B{API Still Responding?}
    B -->|No| C[Enable Degraded Mode]
    B -->|Yes| D[Monitor Database Load]

    C --> E[Bypass Cache Dependencies]
    E --> F[Scale Database Read Replicas]
    F --> G[Implement Rate Limiting]

    D --> H{Database Overloaded?}
    H -->|Yes| F
    H -->|No| I[Monitor and Wait]

    style C fill:#CC0000
    style E fill:#FF8800
    style F fill:#FF8800
```

### 💡 Key Takeaways
- **Cloud provider migrations** can trigger **unexpected failovers**
- **Rate limiting dependencies** become **single points of failure**
- **Database fallbacks** must be **performance-tested** under load
- **Thundering herds** amplify **recovery difficulties**
- **Circuit breakers** are essential for **dependency management**

---

*"The issue was identified as a Redis instance acting as the primary for a highly-available cluster used by Discord's API services. This node was migrated automatically by Google's Cloud Platform, which caused the node to drop offline and trigger failover issues."*

**Critical Quote**: *"We have identified the underlying issue with the API outage but are dealing with a secondary issue on one of our database clusters."*

**Impact**: This incident led to Discord's comprehensive dependency mapping and implementation of graceful degradation patterns across their entire service architecture, establishing industry patterns for handling cloud provider migrations.