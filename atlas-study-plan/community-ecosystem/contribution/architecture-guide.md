# Architecture Contribution Guide
## Adding New Company Architectures to Atlas

### Purpose

This guide enables community members to contribute high-quality company architecture case studies that meet Atlas production standards. Every contribution should help engineers make better design decisions, debug production issues, and understand trade-offs at scale.

### The 8 Mandatory Diagrams

For each company, you MUST create all 8 diagrams. Incomplete submissions will not be accepted.

## 1. COMPLETE ARCHITECTURE - "The Money Shot"

### Purpose
Show every component in the production system with specific technologies, instance types, and real metrics.

### Requirements
- [ ] All services named and versioned
- [ ] Infrastructure specified (AWS m5.2xlarge, GCP n2-standard-16)
- [ ] Connection patterns (REST, gRPC, async)
- [ ] Network topology (VPCs, subnets, zones)
- [ ] 4-plane color coding (Edge, Service, State, Control)

### Template
```mermaid
graph TB
    subgraph "Edge Plane"
        CDN[Cloudflare CDN<br/>2000 POPs worldwide<br/>$50K/month]
        LB[AWS ALB<br/>10 instances<br/>500K req/sec]
    end

    subgraph "Service Plane"
        API[API Gateway<br/>Kong 3.2<br/>c5.4xlarge × 20<br/>$12K/month]
        AUTH[Auth Service<br/>Go 1.21<br/>Istio mesh<br/>$8K/month]
        CORE[Core Service<br/>Java 17 Spring<br/>200 threads<br/>$15K/month]
    end

    subgraph "State Plane"
        PG[(PostgreSQL 14<br/>db.r6g.8xlarge<br/>Multi-AZ<br/>$25K/month)]
        REDIS[(Redis 7<br/>cache.r6g.2xlarge<br/>3 replicas<br/>$8K/month)]
    end

    subgraph "Control Plane"
        MON[Datadog<br/>Full stack monitoring<br/>$20K/month]
        LOG[Splunk<br/>200GB/day<br/>$15K/month]
    end

    %% Apply colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class CDN,LB edgeStyle
    class API,AUTH,CORE serviceStyle
    class PG,REDIS stateStyle
    class MON,LOG controlStyle
```

### Sources Needed
- Engineering blog architecture posts
- Conference presentations (QCon, Strange Loop)
- Infrastructure diagrams from talks
- GitHub repositories (if open source)
- Job postings (tech stack mentions)

## 2. REQUEST FLOW - "The Golden Path"

### Purpose
Trace a typical user request through the system with latency budgets at each hop.

### Requirements
- [ ] User action to response path
- [ ] Latency at each step (p50, p99, p999)
- [ ] Timeout configurations
- [ ] Retry logic
- [ ] Fallback mechanisms
- [ ] SLO annotations

### Template
```mermaid
sequenceDiagram
    participant User
    participant CDN
    participant LB
    participant API
    participant Auth
    participant Core
    participant DB
    participant Cache

    User->>CDN: HTTP Request
    Note over User,CDN: SLO: p99 < 50ms<br/>Actual: p99 = 42ms

    CDN->>LB: Forward (cache miss)
    Note over CDN,LB: Timeout: 100ms<br/>Retry: 0

    LB->>API: Route request
    Note over LB,API: Health check: 10s<br/>Connection pool: 1000

    API->>Auth: Validate token
    Note over API,Auth: p99: 5ms<br/>Circuit breaker: 50% failure

    Auth->>Cache: Check session
    Note over Auth,Cache: Hit rate: 95%<br/>p99: 2ms

    API->>Core: Business logic
    Note over API,Core: p99: 20ms<br/>Timeout: 500ms

    Core->>DB: Query data
    Note over Core,DB: Connection pool: 200<br/>Query timeout: 100ms

    alt Cache Hit
        Core->>Cache: Get cached data
        Cache-->>Core: Return (2ms)
    else Cache Miss
        Core->>DB: Query database
        DB-->>Core: Return (15ms)
        Core->>Cache: Update cache
    end

    Core-->>API: Response
    API-->>LB: Response
    LB-->>CDN: Response
    CDN-->>User: Final response
    Note over User,CDN: Total p99: 85ms<br/>SLO: < 100ms ✓
```

### Key Metrics to Include
- Request rate (req/sec)
- Latency percentiles (p50, p95, p99, p999)
- Timeout settings
- Retry policies
- Circuit breaker thresholds
- Cache hit rates
- Connection pool sizes

## 3. STORAGE ARCHITECTURE - "The Data Journey"

### Purpose
Show every data store, consistency model, replication strategy, and data flow.

### Requirements
- [ ] All databases with type and size
- [ ] Replication topology
- [ ] Consistency guarantees
- [ ] Backup strategy
- [ ] Data retention policies
- [ ] Migration paths

### Template
```mermaid
graph TB
    subgraph "Write Path"
        APP[Application<br/>10K writes/sec]
        PRIM[(Primary DB<br/>PostgreSQL 14<br/>db.r6g.8xlarge<br/>4TB storage)]
        REP1[(Replica 1<br/>Same AZ<br/>Async replication)]
        REP2[(Replica 2<br/>Different AZ<br/>Async replication)]
    end

    subgraph "Read Path"
        READ1[(Read Replica 1<br/>20K reads/sec<br/>Lag: ~100ms)]
        READ2[(Read Replica 2<br/>15K reads/sec<br/>Lag: ~100ms)]
        CACHE[(Redis Cache<br/>100K reads/sec<br/>95% hit rate)]
    end

    subgraph "Analytics"
        DW[(Snowflake<br/>Daily sync<br/>1TB compressed)]
        S3[(S3 Archives<br/>7 year retention<br/>10TB)]
    end

    subgraph "Backup"
        SNAP[Daily Snapshots<br/>30 day retention]
        PITR[Point-in-time<br/>7 day window]
    end

    APP -->|Write| PRIM
    PRIM -->|Async| REP1
    PRIM -->|Async| REP2
    PRIM -->|CDC| DW

    APP -->|Read| CACHE
    CACHE -->|Cache miss| READ1
    CACHE -->|Cache miss| READ2

    PRIM -->|Backup| SNAP
    PRIM -->|WAL| PITR
    DW -->|Archive| S3

    %% Consistency annotations
    PRIM -.->|"Strong consistency"| APP
    READ1 -.->|"Eventual (100ms lag)"| APP
    CACHE -.->|"Best effort"| APP
```

### Consistency Levels to Document
- Strong consistency: Which operations?
- Eventual consistency: Typical lag?
- Read-your-writes: Guaranteed where?
- Monotonic reads: Implemented how?
- Causal consistency: Which scenarios?

## 4. FAILURE DOMAINS - "The Incident Map"

### Purpose
Show what fails when each component goes down, blast radius, and recovery procedures.

### Requirements
- [ ] Failure scenarios for each component
- [ ] Blast radius visualization
- [ ] Cascading failure paths
- [ ] Circuit breakers and bulkheads
- [ ] Auto-recovery mechanisms
- [ ] Manual recovery procedures

### Template
```mermaid
graph TB
    subgraph "Failure Scenarios"
        F1[CDN Failure<br/>Impact: 0%<br/>Origin serves directly]
        F2[LB Failure<br/>Impact: 100%<br/>DNS failover 30s]
        F3[API Gateway Failure<br/>Impact: 100%<br/>Auto-scale recovery]
        F4[Auth Service Failure<br/>Impact: 100%<br/>Circuit breaker opens]
        F5[Core Service Failure<br/>Impact: Partial<br/>Degraded mode]
        F6[Database Failure<br/>Impact: 100%<br/>Failover 60s]
        F7[Cache Failure<br/>Impact: 20%<br/>Higher latency only]
    end

    F2 -->|Cascades to| F3
    F3 -->|Cascades to| F4
    F3 -->|Cascades to| F5
    F4 -->|Cascades to| F5
    F5 -->|Cascades to| F6

    subgraph "Protection Mechanisms"
        CB1[Circuit Breaker<br/>Auth → Core<br/>Threshold: 50% errors]
        CB2[Circuit Breaker<br/>Core → DB<br/>Threshold: 30% errors]
        BULK[Bulkhead Pattern<br/>Thread pool isolation<br/>25 threads per service]
        RATE[Rate Limiter<br/>1000 req/sec per user<br/>10K req/sec global]
    end

    F4 -.->|Prevents cascade| CB1
    F6 -.->|Prevents cascade| CB2
    F5 -.->|Limits impact| BULK
```

### Real Incidents to Reference
For each failure domain, cite actual incidents:
- "Similar to AWS S3 outage 2017-02-28"
- "Comparable to GitHub database failover 2018-10-21"
- "Pattern seen in Cloudflare routing issue 2020-07-17"

## 5. SCALE EVOLUTION - "The Growth Story"

### Purpose
Show how architecture changed at 1K, 10K, 100K, 1M, 10M users.

### Requirements
- [ ] Architecture at each scale milestone
- [ ] What broke at each level
- [ ] How it was fixed
- [ ] Cost at each milestone
- [ ] Team size at each milestone

### Template
```mermaid
graph TB
    subgraph "1K Users - MVP"
        MVP[Monolith on Heroku<br/>Single dyno<br/>PostgreSQL Hobby<br/>$50/month<br/>1 engineer]
    end

    subgraph "10K Users - Breaking Point"
        BP1[Vertical scale exhausted<br/>Database overwhelmed<br/>Manual sharding required]
        BP2[Solution: Read replicas<br/>Caching layer added<br/>$500/month<br/>2 engineers]
    end

    subgraph "100K Users - Microservices"
        MS1[Monolith split into 5 services<br/>Load balancers added<br/>Multi-AZ deployment<br/>$5K/month<br/>8 engineers]
    end

    subgraph "1M Users - Multi-Region"
        MR1[3 AWS regions<br/>Global load balancing<br/>Data partitioning<br/>$50K/month<br/>25 engineers]
    end

    subgraph "10M Users - Current"
        CUR[10 microservices<br/>5 regions globally<br/>Full observability<br/>$200K/month<br/>60 engineers]
    end

    MVP --> BP1
    BP1 --> BP2
    BP2 --> MS1
    MS1 --> MR1
    MR1 --> CUR
```

### Key Transitions to Document
1. **Monolith → Microservices**: Which service split first?
2. **Single DB → Sharded**: What was the sharding key?
3. **Single Region → Multi-Region**: Why the second region?
4. **Synchronous → Asynchronous**: Which operations first?
5. **Manual → Automated**: When did DevOps mature?

## 6. COST BREAKDOWN - "The Money Graph"

### Purpose
Show infrastructure spend by component and optimization opportunities.

### Requirements
- [ ] Cost per component per month
- [ ] Cost per user/transaction
- [ ] Reserved vs. on-demand split
- [ ] Optimization opportunities identified
- [ ] Cost trend over time
- [ ] ROI of optimizations

### Template
```mermaid
graph TB
    subgraph "Monthly Infrastructure Cost: $200K"
        COMPUTE[Compute: $80K<br/>40% of total<br/>EC2, Lambda, Kubernetes]
        STORAGE[Storage: $40K<br/>20% of total<br/>S3, EBS, RDS storage]
        DATABASE[Database: $35K<br/>17.5% of total<br/>RDS, DynamoDB]
        NETWORK[Network: $20K<br/>10% of total<br/>Data transfer, ALB]
        OTHER[Other: $25K<br/>12.5% of total<br/>Monitoring, logs, tools]
    end

    subgraph "Cost Optimization Opportunities"
        OPT1[Reserved Instances<br/>Save $15K/month<br/>Payback: 6 months]
        OPT2[Spot Instances<br/>Save $10K/month<br/>For batch jobs]
        OPT3[Right-sizing<br/>Save $8K/month<br/>Over-provisioned instances]
        OPT4[S3 Lifecycle<br/>Save $5K/month<br/>Archive old data]
    end

    subgraph "Cost per User Metrics"
        CPU[Cost per active user<br/>$2.00/month<br/>Industry: $1.50]
        CPT[Cost per transaction<br/>$0.005<br/>Target: $0.003]
    end
```

### Cost Data Sources
- AWS Cost Explorer screenshots
- GCP billing reports
- Azure cost management
- Engineering blog cost analyses
- Investor presentations (public companies)
- Job postings mentioning budget

## 7. NOVEL SOLUTIONS - "The Innovation"

### Purpose
Highlight unique problems and solutions invented by this company.

### Requirements
- [ ] Problems unique to their scale
- [ ] Novel solutions they created
- [ ] Open source contributions
- [ ] Patents or papers published
- [ ] Industry influence

### Template
```mermaid
graph TB
    subgraph "Problem Space"
        P1[Real-time matching at global scale<br/>100M requests/second<br/>Sub-100ms latency required]
        P2[Geographic load balancing<br/>Route to closest datacenter<br/>Account for capacity]
    end

    subgraph "Solution: Custom System"
        S1[Ringpop<br/>Distributed hash ring<br/>Gossip-based membership<br/>Open sourced 2015]
        S2[TChannel<br/>Custom RPC protocol<br/>Better than gRPC for use case<br/>Open sourced 2016]
    end

    subgraph "Industry Impact"
        I1[Adopted by 50+ companies<br/>10K GitHub stars<br/>Featured at conferences]
        I2[Influenced gRPC design<br/>Patterns copied by competitors]
    end

    P1 --> S1
    P2 --> S2
    S1 --> I1
    S2 --> I2
```

### Innovation Categories
- **Algorithms**: Novel distributed algorithms
- **Protocols**: Custom network protocols
- **Data Structures**: Specialized structures
- **Deployment**: Infrastructure innovations
- **Observability**: Monitoring breakthroughs
- **Resilience**: Failure handling techniques

## 8. PRODUCTION OPERATIONS - "The Ops View"

### Purpose
Show how the system is deployed, monitored, and maintained.

### Requirements
- [ ] CI/CD pipeline
- [ ] Deployment strategy (blue-green, canary, etc.)
- [ ] Monitoring and alerting
- [ ] On-call procedures
- [ ] Chaos engineering practices
- [ ] Incident response process

### Template
```mermaid
graph TB
    subgraph "CI/CD Pipeline"
        GIT[GitHub<br/>Pull request opened]
        CI[CircleCI<br/>Unit tests<br/>Integration tests]
        BUILD[Docker build<br/>Image scanning<br/>Security checks]
        STAGE[Deploy to staging<br/>E2E tests<br/>Performance tests]
        PROD[Deploy to production<br/>Canary: 1% → 10% → 100%<br/>Automatic rollback on errors]
    end

    subgraph "Monitoring"
        METRICS[Datadog<br/>System metrics<br/>Application metrics<br/>Business metrics]
        LOGS[Splunk<br/>Centralized logging<br/>200GB/day]
        TRACES[Jaeger<br/>Distributed tracing<br/>100% sampling]
        ALERTS[PagerDuty<br/>Alert routing<br/>Escalation policies]
    end

    subgraph "Chaos Engineering"
        CHAOS1[Weekly game days<br/>Simulate failures<br/>Verify recovery]
        CHAOS2[Continuous chaos<br/>1% of requests<br/>Random failures injected]
    end

    subgraph "Incident Response"
        INC1[Detection: < 1 minute<br/>Alerting: < 30 seconds<br/>Response: < 5 minutes]
        INC2[Runbooks: 50+ scenarios<br/>Auto-remediation: 20%<br/>Manual: 80%]
    end

    GIT --> CI --> BUILD --> STAGE --> PROD
    PROD --> METRICS
    PROD --> LOGS
    PROD --> TRACES
    METRICS --> ALERTS
```

### Operations Metrics to Include
- Deployment frequency: Daily? Weekly?
- Lead time: Commit to production?
- MTTR: Mean time to recovery?
- Change failure rate: Percentage?
- On-call load: Pages per week?
- Incident frequency: Count per month?

---

## RESEARCH METHODOLOGY

### Finding Information

**Primary Sources** (Best)
1. Official engineering blogs
2. Conference presentations
3. Academic papers by engineers
4. Open-source repositories
5. Official documentation

**Secondary Sources** (Good)
1. Tech interview podcasts
2. Engineering job postings
3. LinkedIn posts by engineers
4. Twitter threads from insiders
5. Startup showcase presentations

**Tertiary Sources** (Use Cautiously)
1. News articles (verify claims)
2. Industry analyst reports
3. Third-party case studies
4. Forum discussions
5. Speculation posts

### Verification Process

**Cross-Reference Everything**
- Minimum 3 independent sources per major claim
- Check publication dates (recent preferred)
- Verify author credentials
- Look for corroborating evidence

**Red Flags**
- Single source for major claims
- Outdated information (>3 years for architecture)
- Vague language ("high performance", "scales well")
- Missing specifics (instance types, metrics)
- Marketing language without technical depth

### Ethical Research

**Respect Boundaries**
- Use only publicly available information
- Don't reverse engineer closed systems
- Don't share confidential information
- Don't contact engineers for proprietary details
- Attribute all sources properly

**When Uncertain**
- Mark as "estimated" or "approximate"
- Explain reasoning and assumptions
- Invite corrections from insiders
- Update when better information available

---

## SUBMISSION CHECKLIST

Before submitting your PR:

### Completeness
- [ ] All 8 diagrams created
- [ ] Each diagram follows template structure
- [ ] 4-plane colors applied consistently
- [ ] Real metrics included (not placeholders)
- [ ] Failure scenarios documented

### Quality
- [ ] Passes 3 AM Test (helps in production)
- [ ] Passes New Hire Test (understandable)
- [ ] Passes CFO Test (costs included)
- [ ] Passes Incident Test (failures documented)

### Sources
- [ ] Minimum 10 sources cited
- [ ] Each major claim has 3+ sources
- [ ] All links work and are archived
- [ ] Publication dates within 3 years (preferred)
- [ ] Author credentials verified

### Technical Accuracy
- [ ] Mermaid syntax validated
- [ ] Instance types are real (not generic)
- [ ] Metrics are realistic for scale
- [ ] Architecture is feasible
- [ ] Costs align with industry norms

### Documentation
- [ ] README updated with company addition
- [ ] Navigation updated in mkdocs.yml
- [ ] Related diagrams linked
- [ ] Tags and categories assigned

---

**Remember**: Quality over speed. One excellent company architecture is worth ten mediocre ones. Take time to research thoroughly, verify claims, and create diagrams that truly help engineers at 3 AM.

**🚀 [START YOUR RESEARCH →](./research-template.md)**
**📝 [SUBMIT YOUR ARCHITECTURE →](https://github.com/atlas-community/atlas-framework/issues/new?template=new-company.md)**