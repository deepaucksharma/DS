# Meta (Facebook) - Failure Domains Architecture

## The October 4, 2021 Global Outage: A Case Study

On October 4, 2021, Meta experienced its worst outage in company history - a 6-hour global blackout affecting Facebook, Instagram, WhatsApp, and Messenger. This incident revealed critical failure domains and reshaped Meta's approach to infrastructure resilience.

## Failure Domain Hierarchy

```mermaid
graph TB
    subgraph Global[Global Failure Domain]
        BGP[BGP Routing Layer]
        DNS[DNS Infrastructure]
        BACKBONE[Meta Backbone Network]
    end

    subgraph Regional[Regional Failure Domains]
        DC_US_WEST[US West Datacenter]
        DC_US_EAST[US East Datacenter]
        DC_EUROPE[Europe Datacenter]
        DC_ASIA[Asia Datacenter]
    end

    subgraph Datacenter[Datacenter Failure Domains]
        POWER[Power Grid A/B]
        COOLING[Cooling Systems]
        NETWORK[Network Fabric]
        COMPUTE[Compute Clusters]
    end

    subgraph Service[Service Failure Domains]
        LB_CLUSTER[Load Balancer Cluster]
        APP_CLUSTER[Application Cluster]
        DB_CLUSTER[Database Cluster]
        CACHE_CLUSTER[Cache Cluster]
    end

    %% Failure cascades
    BGP -->|"Route withdrawal"| DC_US_WEST
    BGP -->|"Route withdrawal"| DC_US_EAST
    BGP -->|"Route withdrawal"| DC_EUROPE
    BGP -->|"Route withdrawal"| DC_ASIA

    DC_US_WEST -->|"Power failure"| POWER
    POWER -->|"Cooling loss"| COOLING
    COOLING -->|"Overheat"| COMPUTE

    NETWORK -->|"Switch failure"| LB_CLUSTER
    LB_CLUSTER -->|"Health check fail"| APP_CLUSTER
    APP_CLUSTER -->|"Connection timeout"| DB_CLUSTER

    %% Blast radius annotations
    BGP -.->|"Blast radius: Global"| BACKBONE
    DC_US_WEST -.->|"Blast radius: Regional"| DC_US_EAST
    POWER -.->|"Blast radius: Datacenter"| COOLING
    LB_CLUSTER -.->|"Blast radius: Service"| APP_CLUSTER

    %% Apply colors for failure severity
    classDef criticalStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef highStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef mediumStyle fill:#FFCC00,stroke:#CC9900,color:#fff
    classDef lowStyle fill:#10B981,stroke:#059669,color:#fff

    class BGP,DNS,BACKBONE criticalStyle
    class DC_US_WEST,DC_US_EAST,DC_EUROPE,DC_ASIA highStyle
    class POWER,COOLING,NETWORK,COMPUTE mediumStyle
    class LB_CLUSTER,APP_CLUSTER,DB_CLUSTER,CACHE_CLUSTER lowStyle
```

## The October 2021 Outage Timeline

```mermaid
gantt
    title Meta Global Outage - October 4, 2021
    dateFormat HH:mm
    axisFormat %H:%M

    section BGP Configuration
    Routine BGP update    :done, config, 15:39, 15:40
    Configuration error   :crit, error, 15:40, 15:41

    section Immediate Impact
    Route withdrawal      :crit, withdraw, 15:41, 15:42
    Global disconnection  :crit, disconnect, 15:42, 21:00

    section Recovery Attempts
    Remote diagnostics    :active, remote, 15:45, 17:00
    Physical datacenter access :active, physical, 17:00, 20:30
    Manual BGP restoration :done, restore, 20:30, 21:00

    section Service Recovery
    DNS propagation       :done, dns, 21:00, 21:30
    Service health checks :done, health, 21:30, 22:00
    Full service restored :milestone, 22:00, 22:00
```

## BGP Configuration Failure Analysis

```mermaid
graph TB
    subgraph ConfigChange[Configuration Change Process]
        ENGINEER[Network Engineer]
        REVIEW[Peer Review]
        AUTOMATION[Automation System]
        DEPLOYMENT[BGP Deployment]
    end

    subgraph BGPLayer[BGP Infrastructure]
        BACKBONE_ROUTERS[Backbone Routers]
        PEERING[ISP Peering Points]
        INTERNAL[Internal BGP]
        EXTERNAL[External BGP]
    end

    subgraph FailurePoints[Critical Failure Points]
        WITHDRAW[Route Withdrawal]
        ISOLATION[Network Isolation]
        CASCADING[Cascading Failures]
        RECOVERY[Recovery Impossibility]
    end

    subgraph Impact[Global Impact]
        NO_DNS[DNS Resolution Failed]
        NO_ACCESS[No Remote Access]
        NO_MONITORING[Monitoring Blind]
        PHYSICAL_ONLY[Physical Access Only]
    end

    %% Normal flow
    ENGINEER --> REVIEW
    REVIEW --> AUTOMATION
    AUTOMATION --> DEPLOYMENT
    DEPLOYMENT --> BACKBONE_ROUTERS

    %% Failure cascade
    BACKBONE_ROUTERS -->|"Invalid config"| WITHDRAW
    WITHDRAW --> PEERING
    WITHDRAW --> INTERNAL
    WITHDRAW --> EXTERNAL

    PEERING --> ISOLATION
    ISOLATION --> CASCADING
    CASCADING --> RECOVERY

    %% Impact chain
    ISOLATION --> NO_DNS
    NO_DNS --> NO_ACCESS
    NO_ACCESS --> NO_MONITORING
    NO_MONITORING --> PHYSICAL_ONLY

    %% Annotations
    WITHDRAW -.->|"All routes withdrawn"| PEERING
    CASCADING -.->|"6 hour outage"| RECOVERY
    PHYSICAL_ONLY -.->|"Manual intervention required"| RECOVERY

    classDef normalStyle fill:#10B981,stroke:#059669,color:#fff
    classDef warningStyle fill:#FFCC00,stroke:#CC9900,color:#fff
    classDef criticalStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class ENGINEER,REVIEW,AUTOMATION normalStyle
    class DEPLOYMENT,BACKBONE_ROUTERS,PEERING warningStyle
    class WITHDRAW,ISOLATION,CASCADING,RECOVERY,NO_DNS,NO_ACCESS,NO_MONITORING,PHYSICAL_ONLY criticalStyle
```

## Service-Level Failure Domains

### News Feed Service Failure Isolation

```mermaid
graph TB
    subgraph LoadBalancer[Load Balancer Layer]
        LB1[LB Primary]
        LB2[LB Secondary]
        LB3[LB Tertiary]
        HEALTH_CHECK[Health Checks]
    end

    subgraph FeedService[Feed Service Pods]
        FEED_A[Feed Cluster A - 100 pods]
        FEED_B[Feed Cluster B - 100 pods]
        FEED_C[Feed Cluster C - 100 pods]
        CIRCUIT_BREAKER[Circuit Breakers]
    end

    subgraph Dependencies[Downstream Dependencies]
        TAO_PRIMARY[TAO Primary]
        TAO_SECONDARY[TAO Secondary]
        ML_RANKING[ML Ranking Service]
        ADS_SERVICE[Ads Service]
    end

    subgraph FailureScenarios[Failure Scenarios]
        CLUSTER_FAIL[Cluster A Fails]
        TAO_SLOW[TAO Slowdown]
        ML_TIMEOUT[ML Timeout]
        ADS_DOWN[Ads Service Down]
    end

    %% Normal routing
    LB1 --> FEED_A
    LB2 --> FEED_B
    LB3 --> FEED_C
    HEALTH_CHECK --> LB1

    %% Service dependencies
    FEED_A --> TAO_PRIMARY
    FEED_B --> TAO_SECONDARY
    FEED_A --> ML_RANKING
    FEED_A --> ADS_SERVICE

    %% Failure handling
    CLUSTER_FAIL -->|"Traffic shift"| FEED_B
    TAO_SLOW -->|"Circuit breaker"| CIRCUIT_BREAKER
    ML_TIMEOUT -->|"Fallback ranking"| FEED_A
    ADS_DOWN -->|"Organic posts only"| FEED_A

    %% Performance annotations
    HEALTH_CHECK -.->|"5s interval"| LB1
    CIRCUIT_BREAKER -.->|"50% error rate trigger"| TAO_PRIMARY
    ML_TIMEOUT -.->|"200ms timeout"| ML_RANKING

    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef failureStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class LB1,LB2,LB3,FEED_A,FEED_B,FEED_C,CIRCUIT_BREAKER serviceStyle
    class TAO_PRIMARY,TAO_SECONDARY,ML_RANKING,ADS_SERVICE,HEALTH_CHECK stateStyle
    class CLUSTER_FAIL,TAO_SLOW,ML_TIMEOUT,ADS_DOWN failureStyle
```

## WhatsApp Encryption Failure Domain

```mermaid
graph TB
    subgraph MessageFlow[Message Flow Path]
        SENDER[Sender Client]
        ENCRYPT[E2E Encryption]
        RELAY[Message Relay]
        DECRYPT[E2E Decryption]
        RECEIVER[Receiver Client]
    end

    subgraph KeyManagement[Key Management]
        KEY_STORE[Key Store]
        KEY_ROTATION[Key Rotation]
        KEY_BACKUP[Key Backup]
        KEY_RECOVERY[Key Recovery]
    end

    subgraph FailureModes[Encryption Failure Modes]
        KEY_CORRUPTION[Key Corruption]
        ROTATION_FAIL[Rotation Failure]
        SYNC_LOSS[Key Sync Loss]
        BACKUP_FAIL[Backup Failure]
    end

    subgraph Mitigation[Failure Mitigation]
        RETRY_MECHANISM[Retry Mechanism]
        FALLBACK_KEY[Fallback Key]
        MANUAL_RESET[Manual Reset]
        SUPPORT_ESCALATION[Support Escalation]
    end

    %% Normal flow
    SENDER --> ENCRYPT
    ENCRYPT --> RELAY
    RELAY --> DECRYPT
    DECRYPT --> RECEIVER

    %% Key management
    ENCRYPT --> KEY_STORE
    DECRYPT --> KEY_STORE
    KEY_STORE --> KEY_ROTATION
    KEY_ROTATION --> KEY_BACKUP

    %% Failure scenarios
    KEY_CORRUPTION --> RETRY_MECHANISM
    ROTATION_FAIL --> FALLBACK_KEY
    SYNC_LOSS --> MANUAL_RESET
    BACKUP_FAIL --> SUPPORT_ESCALATION

    %% Recovery paths
    RETRY_MECHANISM --> KEY_RECOVERY
    FALLBACK_KEY --> KEY_STORE
    MANUAL_RESET --> KEY_ROTATION

    %% Annotations
    KEY_CORRUPTION -.->|"0.001% of keys"| RETRY_MECHANISM
    ROTATION_FAIL -.->|"24h retry window"| FALLBACK_KEY
    SYNC_LOSS -.->|"Requires new key exchange"| MANUAL_RESET

    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef failureStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class ENCRYPT,DECRYPT,RELAY,RETRY_MECHANISM serviceStyle
    class KEY_STORE,KEY_ROTATION,KEY_BACKUP,KEY_RECOVERY,FALLBACK_KEY stateStyle
    class KEY_CORRUPTION,ROTATION_FAIL,SYNC_LOSS,BACKUP_FAIL,MANUAL_RESET,SUPPORT_ESCALATION failureStyle
```

## Datacenter Infrastructure Failures

### Power and Cooling Cascade

```mermaid
graph TB
    subgraph PowerGrid[Power Grid Infrastructure]
        UTILITY[Utility Power Grid]
        SUBSTATION[Datacenter Substation]
        UPS_PRIMARY[UPS Primary]
        UPS_SECONDARY[UPS Secondary]
        GENERATOR[Backup Generators]
    end

    subgraph CoolingSystem[Cooling Infrastructure]
        CHILLER[Chiller Plant]
        COOLING_TOWER[Cooling Towers]
        AIR_HANDLER[Air Handlers]
        PRECISION_AC[Precision AC Units]
    end

    subgraph ComputeInfra[Compute Infrastructure]
        SERVER_RACKS[Server Racks]
        NETWORK_SWITCHES[Network Switches]
        STORAGE_ARRAYS[Storage Arrays]
        THERMAL_MONITORING[Thermal Monitoring]
    end

    subgraph FailureCascade[Failure Cascade Scenarios]
        POWER_OUTAGE[Utility Power Outage]
        UPS_FAILURE[UPS Failure]
        GENERATOR_FAIL[Generator Failure]
        COOLING_LOSS[Cooling System Loss]
        THERMAL_SHUTDOWN[Thermal Shutdown]
    end

    %% Normal power flow
    UTILITY --> SUBSTATION
    SUBSTATION --> UPS_PRIMARY
    UPS_PRIMARY --> SERVER_RACKS
    UPS_SECONDARY --> NETWORK_SWITCHES

    %% Normal cooling flow
    CHILLER --> COOLING_TOWER
    COOLING_TOWER --> AIR_HANDLER
    AIR_HANDLER --> PRECISION_AC
    PRECISION_AC --> SERVER_RACKS

    %% Failure cascades
    POWER_OUTAGE --> UPS_FAILURE
    UPS_FAILURE --> GENERATOR_FAIL
    GENERATOR_FAIL --> COOLING_LOSS
    COOLING_LOSS --> THERMAL_SHUTDOWN

    %% Monitoring and shutdown
    THERMAL_MONITORING --> THERMAL_SHUTDOWN
    THERMAL_SHUTDOWN --> SERVER_RACKS

    %% Annotations
    UPS_PRIMARY -.->|"15 minute runtime"| GENERATOR
    GENERATOR -.->|"72 hour fuel supply"| UPS_SECONDARY
    THERMAL_MONITORING -.->|"85°F shutdown"| PRECISION_AC

    classDef powerStyle fill:#FFCC00,stroke:#CC9900,color:#fff
    classDef coolingStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef computeStyle fill:#10B981,stroke:#059669,color:#fff
    classDef failureStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class UTILITY,SUBSTATION,UPS_PRIMARY,UPS_SECONDARY,GENERATOR powerStyle
    class CHILLER,COOLING_TOWER,AIR_HANDLER,PRECISION_AC coolingStyle
    class SERVER_RACKS,NETWORK_SWITCHES,STORAGE_ARRAYS,THERMAL_MONITORING computeStyle
    class POWER_OUTAGE,UPS_FAILURE,GENERATOR_FAIL,COOLING_LOSS,THERMAL_SHUTDOWN failureStyle
```

## Circuit Breaker Implementation

```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open : Failure threshold exceeded
    Open --> HalfOpen : Timeout period elapsed
    HalfOpen --> Closed : Request succeeds
    HalfOpen --> Open : Request fails

    state Closed {
        [*] --> Monitoring
        Monitoring --> CountingFailures : Request fails
        CountingFailures --> Monitoring : Request succeeds
        CountingFailures --> [*] : Threshold reached
    }

    state Open {
        [*] --> RejectingRequests
        RejectingRequests --> WaitingTimeout : Time passes
        WaitingTimeout --> [*] : Timeout elapsed
    }

    state HalfOpen {
        [*] --> TestingService
        TestingService --> [*] : Single request result
    }

    note right of Closed : Normal operation\n50% failure rate = threshold
    note right of Open : Fail fast mode\n30 second timeout
    note right of HalfOpen : Recovery test\nSingle request probe
```

## Recovery Time Objectives (RTO)

### Service Recovery Targets
| Failure Type | Detection Time | Recovery Time | Business Impact |
|--------------|----------------|---------------|-----------------|
| Single Server | 30 seconds | 2 minutes | None (auto-failover) |
| Service Cluster | 1 minute | 5 minutes | Partial degradation |
| Datacenter Power | 2 minutes | 15 minutes | Regional outage |
| BGP Misconfiguration | 5 minutes | 4-6 hours | Global outage |
| Database Corruption | 10 minutes | 2-4 hours | Service-specific |

### Blast Radius by Failure Domain
```mermaid
pie title Failure Impact Distribution
    "Single Service (10% users)" : 45
    "Datacenter Region (25% users)" : 30
    "Cross-Region (50% users)" : 20
    "Global Infrastructure (100% users)" : 5
```

## Production Lessons from Major Incidents

### Key Insights from October 2021 Outage
1. **BGP as Single Point of Failure**: Network routing became critical dependency
2. **Remote Management Dependency**: Lost ability to manage infrastructure remotely
3. **Physical Access Bottleneck**: Manual intervention required onsite presence
4. **DNS Propagation Delays**: Recovery took hours due to DNS caching
5. **Monitoring Blindness**: Lost observability when network isolated

### Implemented Improvements Post-Outage
1. **BGP Configuration Safeguards**: Multi-step verification for routing changes
2. **Out-of-band Management**: Separate network for emergency access
3. **Physical Access Procedures**: Faster datacenter access protocols
4. **DNS Architecture**: Reduced dependency on single DNS infrastructure
5. **Chaos Engineering**: Regular testing of failure scenarios

### Instagram Outage - March 2019
- **Duration**: 14 hours partial outage
- **Root Cause**: Database shard rebalancing gone wrong
- **Impact**: 50% of users couldn't upload photos
- **Fix**: Manual database restoration from backups
- **Lesson**: Database operations need more gradual rollout procedures

### WhatsApp New Year's Eve 2020
- **Duration**: 2 hours messaging delays
- **Root Cause**: Message queue overload during peak usage
- **Impact**: Messages delayed by 30+ minutes
- **Fix**: Emergency capacity scaling and queue optimization
- **Lesson**: Holiday traffic patterns require 10x normal capacity planning

## Failure Prevention Strategies

### Chaos Engineering at Meta
```mermaid
graph LR
    subgraph ChaosTools[Chaos Engineering Tools]
        STORM[Storm - Network Chaos]
        DNSCHAOS[DNS Chaos Testing]
        POWERCHAOS[Power Failure Simulation]
        DBCHAOS[Database Chaos]
    end

    subgraph TestScenarios[Regular Test Scenarios]
        DATACENTER_FAIL[Datacenter Failure]
        SERVICE_DEGRADE[Service Degradation]
        NETWORK_PARTITION[Network Partitions]
        CAPACITY_SURGE[Traffic Surge Testing]
    end

    subgraph Monitoring[Monitoring & Alerting]
        METRICS[Real-time Metrics]
        ALERTS[Automated Alerts]
        RUNBOOKS[Incident Runbooks]
        ONCALL[On-call Procedures]
    end

    STORM --> DATACENTER_FAIL
    DNSCHAOS --> SERVICE_DEGRADE
    POWERCHAOS --> NETWORK_PARTITION
    DBCHAOS --> CAPACITY_SURGE

    DATACENTER_FAIL --> METRICS
    SERVICE_DEGRADE --> ALERTS
    NETWORK_PARTITION --> RUNBOOKS
    CAPACITY_SURGE --> ONCALL

    classDef chaosStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef testStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef monitorStyle fill:#10B981,stroke:#059669,color:#fff

    class STORM,DNSCHAOS,POWERCHAOS,DBCHAOS chaosStyle
    class DATACENTER_FAIL,SERVICE_DEGRADE,NETWORK_PARTITION,CAPACITY_SURGE testStyle
    class METRICS,ALERTS,RUNBOOKS,ONCALL monitorStyle
```

*"The October 2021 outage taught us that even the most robust systems can fail catastrophically when fundamental infrastructure assumptions break."*

**Sources**: Meta Engineering Blog, October 2021 Outage Report, WhatsApp Engineering Blog, Instagram Engineering Blog