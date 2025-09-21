# Dropbox Failure Domains

## Sync and Storage Failure Analysis

Dropbox's failure domain design ensures 99.9% uptime despite handling billions of file operations daily. The system isolates failures across multiple dimensions to prevent cascading outages while maintaining data durability.

```mermaid
graph TB
    subgraph ClientLayer[Client Layer Failures]
        CF1[Network Connectivity Loss<br/>Impact: Single User<br/>Mitigation: Offline Mode<br/>Recovery: Auto-resume]
        CF2[Client Application Crash<br/>Impact: Single User<br/>Mitigation: Auto-restart<br/>Recovery: State persistence]
        CF3[Local Storage Full<br/>Impact: Single User<br/>Mitigation: Smart Sync<br/>Recovery: Cloud-only mode]
        CF4[Authentication Failure<br/>Impact: Single User<br/>Mitigation: Token refresh<br/>Recovery: Re-auth flow]
    end

    subgraph EdgeFailures[Edge Layer Failures]
        EF1[CDN Node Failure<br/>Impact: Regional<br/>Blast Radius: 1M users<br/>RTO: 30 seconds<br/>Mitigation: Multi-CDN]
        EF2[Load Balancer Failure<br/>Impact: Datacenter<br/>Blast Radius: 100M users<br/>RTO: 2 minutes<br/>Mitigation: HA pairs]
        EF3[DDoS Attack<br/>Impact: Global<br/>Blast Radius: All users<br/>RTO: 5 minutes<br/>Mitigation: WAF + Rate limiting]
    end

    subgraph ServiceFailures[Service Layer Failures]
        SF1[API Gateway Overload<br/>Impact: Global<br/>Blast Radius: All operations<br/>RTO: 5 minutes<br/>Mitigation: Auto-scaling]
        SF2[Sync Service Crash<br/>Impact: Regional<br/>Blast Radius: 200M users<br/>RTO: 3 minutes<br/>Mitigation: Process restart]
        SF3[Auth Service Down<br/>Impact: Global<br/>Blast Radius: New sessions<br/>RTO: 2 minutes<br/>Mitigation: Token caching]
        SF4[Notification Service Lag<br/>Impact: Global<br/>Blast Radius: Real-time sync<br/>RTO: 1 minute<br/>Mitigation: Fallback polling]
    end

    subgraph StateFailures[State Layer Failures]
        STF1[Nucleus Metadata Corruption<br/>Impact: Global<br/>Blast Radius: File operations<br/>RTO: 15 minutes<br/>Mitigation: Backup restore]
        STF2[Magic Pocket Drive Failure<br/>Impact: Shard<br/>Blast Radius: 1% of files<br/>RTO: 1 hour<br/>Mitigation: 3× replication]
        STF3[Cache Cluster Down<br/>Impact: Regional<br/>Blast Radius: Read latency<br/>RTO: 5 minutes<br/>Mitigation: Cache rebuild]
        STF4[Cross-DC Network Partition<br/>Impact: Regional<br/>Blast Radius: Sync delays<br/>RTO: 30 minutes<br/>Mitigation: Local operations]
    end

    subgraph CascadingFailures[Cascading Failure Scenarios]
        CASCADE1[Primary DC Power Loss<br/>→ Traffic surge to backup DC<br/>→ Backup DC overload<br/>→ Global degradation<br/>Prevention: Circuit breakers]

        CASCADE2[Metadata DB Corruption<br/>→ File operations fail<br/>→ Client retry storms<br/>→ API gateway overload<br/>Prevention: Rate limiting]

        CASCADE3[Storage Backend Slow<br/>→ API timeouts increase<br/>→ Load balancer marks unhealthy<br/>→ Traffic concentration<br/>Prevention: Bulkhead pattern]
    end

    %% Failure propagation paths
    EF2 -.->|Traffic shift| SF1
    SF1 -.->|Cascade| STF1
    STF2 -.->|Replica reads| STF3
    STF4 -.->|Network split| CASCADE1

    %% Mitigation connections
    CF1 --> CF2
    EF1 --> EF2
    SF2 --> SF3
    STF1 --> STF2

    %% Apply failure domain colors
    classDef clientFailure fill:#FFE0E0,stroke:#8B5CF6,color:#000,stroke-width:2px
    classDef edgeFailure fill:#FFE5CC,stroke:#FF6600,color:#000,stroke-width:2px
    classDef serviceFailure fill:#FFF2CC,stroke:#FF9900,color:#000,stroke-width:2px
    classDef stateFailure fill:#FFE0F0,stroke:#CC0066,color:#000,stroke-width:2px
    classDef cascadeFailure fill:#E0E0E0,stroke:#666666,color:#000,stroke-width:3px

    class CF1,CF2,CF3,CF4 clientFailure
    class EF1,EF2,EF3 edgeFailure
    class SF1,SF2,SF3,SF4 serviceFailure
    class STF1,STF2,STF3,STF4 stateFailure
    class CASCADE1,CASCADE2,CASCADE3 cascadeFailure
```

## Historical Incident Analysis

### Major Outages (2018-2024)

| Date | Duration | Root Cause | Impact | Resolution |
|------|----------|------------|---------|------------|
| **2019-01-15** | 4.2 hours | Nucleus metadata corruption | 40% of users unable to sync | Restore from backup |
| **2020-06-23** | 2.1 hours | Magic Pocket network partition | West Coast sync delays | Reroute traffic |
| **2021-03-08** | 1.8 hours | API gateway memory leak | Global performance degradation | Rolling restart |
| **2022-09-14** | 3.5 hours | DDoS attack on auth service | Login failures | Traffic filtering |
| **2023-11-02** | 45 minutes | Load balancer configuration error | East Coast access issues | Config rollback |

### Failure Pattern Analysis

```mermaid
pie title Failure Root Causes (2023)
    "Configuration Errors" : 35
    "Hardware Failures" : 25
    "Software Bugs" : 20
    "Network Issues" : 12
    "External Dependencies" : 8
```

## Failure Isolation Mechanisms

### Circuit Breaker Configuration

```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open : Failure threshold exceeded<br/>(5 failures in 30s)
    Open --> HalfOpen : Timeout period<br/>(30 seconds)
    HalfOpen --> Closed : Success<br/>(3 consecutive)
    HalfOpen --> Open : Failure<br/>(1 failure)

    Closed : Normal operation<br/>All requests pass through
    Open : Fail fast<br/>Reject requests immediately
    HalfOpen : Probe state<br/>Allow limited requests
```

### Bulkhead Patterns

| Service | Thread Pool | Connection Pool | Timeout | Circuit Breaker |
|---------|-------------|-----------------|---------|-----------------|
| **Sync Service** | 200 threads | 1000 connections | 30s | 5 failures/30s |
| **Auth Service** | 100 threads | 500 connections | 10s | 3 failures/15s |
| **Storage API** | 500 threads | 2000 connections | 60s | 10 failures/60s |
| **Notification** | 150 threads | 800 connections | 15s | 5 failures/30s |

## Data Consistency During Failures

### Conflict Resolution Strategy
```
1. Detect conflicting file versions
2. Apply last-writer-wins for metadata
3. Create conflict copy for user resolution
4. Maintain version history for rollback
5. Sync conflict resolution across devices
```

### Split-Brain Scenarios
```mermaid
sequenceDiagram
    participant Client1 as Client A
    participant Client2 as Client B
    participant DC1 as Primary DC
    participant DC2 as Secondary DC
    participant Resolver as Conflict Resolver

    Note over DC1,DC2: Network partition occurs

    Client1->>DC1: Update file.txt (v1→v2)
    Client2->>DC2: Update file.txt (v1→v3)

    Note over DC1,DC2: Partition heals

    DC1->>DC2: Sync metadata
    DC2->>DC1: Sync metadata

    DC1->>Resolver: Conflict detected<br/>v2 vs v3
    Resolver->>Resolver: Apply conflict resolution<br/>Last-writer-wins + backup

    Resolver->>Client1: file.txt (v4 - merged)
    Resolver->>Client1: file (Client A's conflicted copy).txt
    Resolver->>Client2: file.txt (v4 - merged)
    Resolver->>Client2: file (Client B's conflicted copy).txt
```

## Recovery Procedures

### Automated Recovery Workflows

| Failure Type | Detection Time | Recovery Action | RTO Target |
|--------------|---------------|-----------------|------------|
| **Service Crash** | 10 seconds | Process restart + health check | 30 seconds |
| **Storage Drive** | 5 minutes | Rebuild from replicas | 1 hour |
| **Network Partition** | 30 seconds | Reroute traffic | 2 minutes |
| **Metadata Corruption** | 2 minutes | Restore from backup | 15 minutes |
| **DDoS Attack** | 15 seconds | Activate DDoS protection | 1 minute |

### Manual Escalation Triggers

1. **RTO Exceeded**: Automatic page to on-call engineer
2. **Multiple Failures**: Page incident commander
3. **Customer Impact**: Activate customer communications
4. **Data Loss Risk**: Page database team + leadership
5. **Security Breach**: Page security team + executives

## Monitoring and Alerting

### Critical Health Metrics

```yaml
SLI Thresholds:
  sync_success_rate: > 99.5%
  api_latency_p99: < 100ms
  storage_availability: > 99.9%
  auth_success_rate: > 99.8%

Alert Conditions:
  - sync_success_rate < 95% (5 minutes) → PAGE
  - api_latency_p99 > 500ms (2 minutes) → PAGE
  - storage_errors > 100/minute → EMAIL
  - auth_failures > 1000/minute → PAGE
```

### Runbook Integration

Each failure domain has automated runbooks with:
- **Symptom Detection**: Specific metrics and log patterns
- **Impact Assessment**: Blast radius calculation
- **Escalation Path**: On-call rotation and communication
- **Recovery Steps**: Automated and manual procedures
- **Post-Mortem**: Blameless analysis template

*Source: Dropbox Engineering Blog, SRE Documentation, Post-Mortem Database, Incident Response Playbooks*