# Meta (Facebook) - Production Operations

## Operating the World's Largest Social Platform

Meta's production operations manage 3B+ users across multiple platforms with 99.95%+ uptime requirements. This involves orchestrating millions of servers, deploying 50K+ times per day, and maintaining service quality through sophisticated automation and monitoring systems.

## Tupperware: Container Orchestration at Scale

Tupperware is Meta's custom container orchestration platform, predating Kubernetes and designed specifically for Meta's scale and requirements.

```mermaid
graph TB
    subgraph TupperwareCore[Tupperware Orchestration Core]
        SCHEDULER[Global Scheduler]
        RESOURCE_MGR[Resource Manager]
        PLACEMENT[Intelligent Placement Engine]
        HEALTH_MONITOR[Health Monitoring]
    end

    subgraph ContainerRuntime[Container Runtime Layer]
        CONTAINER_ENGINE[Container Engine]
        IMAGE_REGISTRY[Image Registry - 100TB+]
        NETWORKING[Container Networking]
        STORAGE_VOLUMES[Persistent Volumes]
    end

    subgraph ClusterManagement[Cluster Management]
        FLEET_CONTROLLER[Fleet Controller]
        NODE_MANAGER[Node Manager]
        CAPACITY_PLANNER[Capacity Planner]
        UPGRADE_ORCHESTRATOR[Rolling Upgrade Orchestrator]
    end

    subgraph ServiceMesh[Service Mesh Integration]
        LOAD_BALANCING[Smart Load Balancing]
        SERVICE_DISCOVERY[Service Discovery]
        TRAFFIC_ROUTING[Traffic Routing]
        CIRCUIT_BREAKERS[Circuit Breakers]
    end

    %% Core orchestration flow
    SCHEDULER --> RESOURCE_MGR
    RESOURCE_MGR --> PLACEMENT
    PLACEMENT --> HEALTH_MONITOR

    %% Container management
    SCHEDULER --> CONTAINER_ENGINE
    CONTAINER_ENGINE --> IMAGE_REGISTRY
    IMAGE_REGISTRY --> NETWORKING
    NETWORKING --> STORAGE_VOLUMES

    %% Cluster operations
    FLEET_CONTROLLER --> NODE_MANAGER
    NODE_MANAGER --> CAPACITY_PLANNER
    CAPACITY_PLANNER --> UPGRADE_ORCHESTRATOR

    %% Service mesh integration
    PLACEMENT --> LOAD_BALANCING
    HEALTH_MONITOR --> SERVICE_DISCOVERY
    SERVICE_DISCOVERY --> TRAFFIC_ROUTING
    TRAFFIC_ROUTING --> CIRCUIT_BREAKERS

    %% Scale annotations
    SCHEDULER -.->|"2.5M+ containers"| RESOURCE_MGR
    IMAGE_REGISTRY -.->|"100K+ images"| NETWORKING
    FLEET_CONTROLLER -.->|"100K+ nodes"| NODE_MANAGER
    LOAD_BALANCING -.->|"10M+ RPS"| SERVICE_DISCOVERY

    %% Apply four-plane colors
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class SCHEDULER,RESOURCE_MGR,PLACEMENT,CONTAINER_ENGINE,LOAD_BALANCING,SERVICE_DISCOVERY,TRAFFIC_ROUTING serviceStyle
    class IMAGE_REGISTRY,NETWORKING,STORAGE_VOLUMES,CIRCUIT_BREAKERS stateStyle
    class HEALTH_MONITOR,FLEET_CONTROLLER,NODE_MANAGER,CAPACITY_PLANNER,UPGRADE_ORCHESTRATOR controlStyle
```

## Delos: Distributed Coordination Service

Delos provides strongly consistent coordination for Meta's distributed systems, serving as the foundation for configuration management, leader election, and distributed locks.

```mermaid
graph TB
    subgraph DelosCore[Delos Core Architecture]
        CONSENSUS[Multi-Paxos Consensus]
        LOG_STORE[Distributed Log Store]
        STATE_MACHINE[Replicated State Machine]
        LEADER_ELECTION[Leader Election Service]
    end

    subgraph DelosClients[Client Applications]
        CONFIG_SERVICE[Configuration Service]
        LOCK_SERVICE[Distributed Lock Service]
        COORDINATION[Service Coordination]
        METADATA_STORE[Metadata Storage]
    end

    subgraph DelosOperations[Operational Features]
        RECONFIGURATION[Dynamic Reconfiguration]
        FAILURE_RECOVERY[Automatic Failure Recovery]
        SNAPSHOT_RESTORE[Snapshot & Restore]
        MONITORING[Real-time Monitoring]
    end

    subgraph Performance[Performance Characteristics]
        LATENCY_1MS[1ms p99 latency]
        THROUGHPUT_100K[100K ops/sec]
        DURABILITY_5NINES[99.999% durability]
        AVAILABILITY_6NINES[99.9999% availability]
    end

    %% Core flow
    CONSENSUS --> LOG_STORE
    LOG_STORE --> STATE_MACHINE
    STATE_MACHINE --> LEADER_ELECTION

    %% Client integration
    CONSENSUS --> CONFIG_SERVICE
    LOG_STORE --> LOCK_SERVICE
    STATE_MACHINE --> COORDINATION
    LEADER_ELECTION --> METADATA_STORE

    %% Operational capabilities
    CONFIG_SERVICE --> RECONFIGURATION
    LOCK_SERVICE --> FAILURE_RECOVERY
    COORDINATION --> SNAPSHOT_RESTORE
    METADATA_STORE --> MONITORING

    %% Performance metrics
    RECONFIGURATION --> LATENCY_1MS
    FAILURE_RECOVERY --> THROUGHPUT_100K
    SNAPSHOT_RESTORE --> DURABILITY_5NINES
    MONITORING --> AVAILABILITY_6NINES

    %% Reliability annotations
    CONSENSUS -.->|"5-node clusters"| LOG_STORE
    CONFIG_SERVICE -.->|"Global configuration"| LOCK_SERVICE
    LATENCY_1MS -.->|"Cross-datacenter"| THROUGHPUT_100K

    classDef coreStyle fill:#10B981,stroke:#059669,color:#fff
    classDef clientStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef opsStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef perfStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class CONSENSUS,LOG_STORE,STATE_MACHINE,LEADER_ELECTION coreStyle
    class CONFIG_SERVICE,LOCK_SERVICE,COORDINATION,METADATA_STORE clientStyle
    class RECONFIGURATION,FAILURE_RECOVERY,SNAPSHOT_RESTORE,MONITORING opsStyle
    class LATENCY_1MS,THROUGHPUT_100K,DURABILITY_5NINES,AVAILABILITY_6NINES perfStyle
```

## Deployment Pipeline: 50K Deployments Daily

Meta's deployment system handles massive scale with safety mechanisms to prevent global outages.

```mermaid
graph LR
    subgraph Development[Development Pipeline]
        CODE_COMMIT[Code Commit]
        PEER_REVIEW[Peer Review]
        AUTOMATED_TESTS[Automated Testing]
        BUILD_SYSTEM[Build & Package]
    end

    subgraph Staging[Staging Environment]
        CANARY_INTERNAL[Internal Canary - 1%]
        SHADOW_TRAFFIC[Shadow Traffic Testing]
        INTEGRATION_TEST[Integration Testing]
        PERFORMANCE_TEST[Performance Testing]
    end

    subgraph Production[Production Rollout]
        CANARY_PROD[Production Canary - 0.1%]
        GRADUAL_ROLLOUT[Gradual Rollout - 1%, 5%, 25%]
        FULL_DEPLOYMENT[Full Deployment - 100%]
        MONITORING[Real-time Monitoring]
    end

    subgraph SafetyMechanisms[Safety Mechanisms]
        AUTO_ROLLBACK[Automatic Rollback]
        CIRCUIT_BREAKER[Circuit Breakers]
        FEATURE_FLAGS[Feature Flags]
        KILL_SWITCH[Emergency Kill Switch]
    end

    %% Development flow
    CODE_COMMIT --> PEER_REVIEW
    PEER_REVIEW --> AUTOMATED_TESTS
    AUTOMATED_TESTS --> BUILD_SYSTEM

    %% Staging flow
    BUILD_SYSTEM --> CANARY_INTERNAL
    CANARY_INTERNAL --> SHADOW_TRAFFIC
    SHADOW_TRAFFIC --> INTEGRATION_TEST
    INTEGRATION_TEST --> PERFORMANCE_TEST

    %% Production flow
    PERFORMANCE_TEST --> CANARY_PROD
    CANARY_PROD --> GRADUAL_ROLLOUT
    GRADUAL_ROLLOUT --> FULL_DEPLOYMENT
    FULL_DEPLOYMENT --> MONITORING

    %% Safety integration
    CANARY_PROD --> AUTO_ROLLBACK
    GRADUAL_ROLLOUT --> CIRCUIT_BREAKER
    FULL_DEPLOYMENT --> FEATURE_FLAGS
    MONITORING --> KILL_SWITCH

    %% Safety feedback loops
    AUTO_ROLLBACK -->|"Metrics degradation"| CANARY_PROD
    CIRCUIT_BREAKER -->|"Error rate spike"| GRADUAL_ROLLOUT
    KILL_SWITCH -->|"Emergency stop"| FULL_DEPLOYMENT

    %% Deployment metrics
    CODE_COMMIT -.->|"50K+ daily commits"| PEER_REVIEW
    CANARY_INTERNAL -.->|"0.1% traffic"| SHADOW_TRAFFIC
    GRADUAL_ROLLOUT -.->|"4-hour rollout"| FULL_DEPLOYMENT

    classDef devStyle fill:#10B981,stroke:#059669,color:#fff
    classDef stageStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef prodStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef safetyStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class CODE_COMMIT,PEER_REVIEW,AUTOMATED_TESTS,BUILD_SYSTEM devStyle
    class CANARY_INTERNAL,SHADOW_TRAFFIC,INTEGRATION_TEST,PERFORMANCE_TEST stageStyle
    class CANARY_PROD,GRADUAL_ROLLOUT,FULL_DEPLOYMENT,MONITORING prodStyle
    class AUTO_ROLLBACK,CIRCUIT_BREAKER,FEATURE_FLAGS,KILL_SWITCH safetyStyle
```

## Scuba: Real-time Analytics Engine

Scuba powers Meta's real-time operational analytics, processing billions of events for monitoring, debugging, and business insights.

```mermaid
graph TB
    subgraph DataIngestion[Data Ingestion Layer]
        REAL_TIME_STREAMS[Real-time Streams]
        BATCH_INGESTION[Batch Ingestion]
        SCHEMA_REGISTRY[Schema Registry]
        DATA_VALIDATION[Data Validation]
    end

    subgraph ScubaCore[Scuba Core Engine]
        COLUMNAR_STORE[Columnar Storage]
        QUERY_ENGINE[Distributed Query Engine]
        AGGREGATION[Real-time Aggregation]
        INDEX_MANAGEMENT[Index Management]
    end

    subgraph QueryInterface[Query Interfaces]
        WEB_UI[Web-based Query UI]
        SQL_INTERFACE[SQL Interface]
        API_ENDPOINTS[REST API Endpoints]
        ALERTING[Real-time Alerting]
    end

    subgraph PerformanceOpt[Performance Optimizations]
        COLUMNAR_COMPRESSION[Columnar Compression]
        PARALLEL_PROCESSING[Parallel Processing]
        RESULT_CACHING[Result Caching]
        ADAPTIVE_INDEXING[Adaptive Indexing]
    end

    %% Data flow
    REAL_TIME_STREAMS --> SCHEMA_REGISTRY
    BATCH_INGESTION --> SCHEMA_REGISTRY
    SCHEMA_REGISTRY --> DATA_VALIDATION
    DATA_VALIDATION --> COLUMNAR_STORE

    %% Query processing
    COLUMNAR_STORE --> QUERY_ENGINE
    QUERY_ENGINE --> AGGREGATION
    AGGREGATION --> INDEX_MANAGEMENT

    %% User interfaces
    QUERY_ENGINE --> WEB_UI
    AGGREGATION --> SQL_INTERFACE
    INDEX_MANAGEMENT --> API_ENDPOINTS
    API_ENDPOINTS --> ALERTING

    %% Performance features
    COLUMNAR_STORE --> COLUMNAR_COMPRESSION
    QUERY_ENGINE --> PARALLEL_PROCESSING
    AGGREGATION --> RESULT_CACHING
    INDEX_MANAGEMENT --> ADAPTIVE_INDEXING

    %% Scale metrics
    REAL_TIME_STREAMS -.->|"1TB/hour ingestion"| SCHEMA_REGISTRY
    QUERY_ENGINE -.->|"<1s query response"| AGGREGATION
    WEB_UI -.->|"10K+ concurrent users"| SQL_INTERFACE
    PARALLEL_PROCESSING -.->|"1000x parallelism"| RESULT_CACHING

    classDef ingestStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef coreStyle fill:#10B981,stroke:#059669,color:#fff
    classDef interfaceStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef perfStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class REAL_TIME_STREAMS,BATCH_INGESTION,SCHEMA_REGISTRY,DATA_VALIDATION ingestStyle
    class COLUMNAR_STORE,QUERY_ENGINE,AGGREGATION,INDEX_MANAGEMENT coreStyle
    class WEB_UI,SQL_INTERFACE,API_ENDPOINTS,ALERTING interfaceStyle
    class COLUMNAR_COMPRESSION,PARALLEL_PROCESSING,RESULT_CACHING,ADAPTIVE_INDEXING perfStyle
```

## On-Call and Incident Response

### Incident Response Organization
```mermaid
graph TB
    subgraph IncidentTiers[Incident Severity Tiers]
        SEV1[SEV1 - Global Outage]
        SEV2[SEV2 - Major Feature Down]
        SEV3[SEV3 - Degraded Performance]
        SEV4[SEV4 - Minor Issues]
    end

    subgraph ResponseTeams[Response Team Structure]
        IC[Incident Commander]
        PRIMARY_ONCALL[Primary On-call Engineer]
        SECONDARY_ONCALL[Secondary On-call Engineer]
        SUBJECT_EXPERTS[Subject Matter Experts]
    end

    subgraph ResponseProcess[Response Process]
        DETECTION[Automated Detection]
        ESCALATION[Escalation Procedures]
        MITIGATION[Immediate Mitigation]
        RESOLUTION[Root Cause Resolution]
    end

    subgraph PostIncident[Post-Incident Process]
        POSTMORTEM[Blameless Postmortem]
        ACTION_ITEMS[Actionable Improvements]
        FOLLOW_UP[Follow-up Implementation]
        PREVENTION[Prevention Measures]
    end

    %% Incident flow
    SEV1 --> IC
    SEV2 --> PRIMARY_ONCALL
    SEV3 --> SECONDARY_ONCALL
    SEV4 --> SUBJECT_EXPERTS

    %% Response coordination
    IC --> DETECTION
    PRIMARY_ONCALL --> ESCALATION
    SECONDARY_ONCALL --> MITIGATION
    SUBJECT_EXPERTS --> RESOLUTION

    %% Post-incident learning
    DETECTION --> POSTMORTEM
    ESCALATION --> ACTION_ITEMS
    MITIGATION --> FOLLOW_UP
    RESOLUTION --> PREVENTION

    %% Response time targets
    SEV1 -.->|"5 min response"| IC
    SEV2 -.->|"15 min response"| PRIMARY_ONCALL
    DETECTION -.->|"<2 min detection"| ESCALATION
    POSTMORTEM -.->|"72 hour timeline"| ACTION_ITEMS

    classDef sevStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef teamStyle fill:#10B981,stroke:#059669,color:#fff
    classDef processStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef postStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class SEV1,SEV2,SEV3,SEV4 sevStyle
    class IC,PRIMARY_ONCALL,SECONDARY_ONCALL,SUBJECT_EXPERTS teamStyle
    class DETECTION,ESCALATION,MITIGATION,RESOLUTION processStyle
    class POSTMORTEM,ACTION_ITEMS,FOLLOW_UP,PREVENTION postStyle
```

## Chaos Engineering and Resilience Testing

### Chaos Engineering Program
```mermaid
graph LR
    subgraph ChaosTools[Chaos Engineering Tools]
        STORM[Storm - Network Chaos]
        LEGION[Legion - Service Chaos]
        GREMLINS[Gremlins - Infrastructure Chaos]
        CHAOS_AUTOMATION[Automated Chaos Injection]
    end

    subgraph TestScenarios[Regular Test Scenarios]
        DATACENTER_LOSS[Datacenter Failure]
        SERVICE_DEGRADATION[Service Degradation]
        NETWORK_PARTITION[Network Partitions]
        DATABASE_LATENCY[Database Latency Spikes]
    end

    subgraph SafetyMechanisms[Safety Controls]
        BLAST_RADIUS[Blast Radius Control]
        AUTO_RECOVERY[Automatic Recovery]
        MANUAL_OVERRIDE[Manual Override]
        MONITORING_GUARD[Monitoring Guards]
    end

    subgraph Results[Chaos Results]
        RESILIENCE_IMPROVEMENT[Resilience Improvements]
        WEAKNESS_DISCOVERY[Weakness Discovery]
        CONFIDENCE_BUILDING[Team Confidence]
        AUTOMATION_ENHANCEMENT[Automation Enhancement]
    end

    %% Tool to scenario mapping
    STORM --> DATACENTER_LOSS
    LEGION --> SERVICE_DEGRADATION
    GREMLINS --> NETWORK_PARTITION
    CHAOS_AUTOMATION --> DATABASE_LATENCY

    %% Safety integration
    DATACENTER_LOSS --> BLAST_RADIUS
    SERVICE_DEGRADATION --> AUTO_RECOVERY
    NETWORK_PARTITION --> MANUAL_OVERRIDE
    DATABASE_LATENCY --> MONITORING_GUARD

    %% Outcome measurement
    BLAST_RADIUS --> RESILIENCE_IMPROVEMENT
    AUTO_RECOVERY --> WEAKNESS_DISCOVERY
    MANUAL_OVERRIDE --> CONFIDENCE_BUILDING
    MONITORING_GUARD --> AUTOMATION_ENHANCEMENT

    %% Chaos metrics
    STORM -.->|"Weekly datacenter tests"| DATACENTER_LOSS
    LEGION -.->|"Daily service tests"| SERVICE_DEGRADATION
    BLAST_RADIUS -.->|"<1% user impact"| AUTO_RECOVERY
    RESILIENCE_IMPROVEMENT -.->|"50% incident reduction"| WEAKNESS_DISCOVERY

    classDef toolStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef scenarioStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef safetyStyle fill:#10B981,stroke:#059669,color:#fff
    classDef resultStyle fill:#3B82F6,stroke:#2563EB,color:#fff

    class STORM,LEGION,GREMLINS,CHAOS_AUTOMATION toolStyle
    class DATACENTER_LOSS,SERVICE_DEGRADATION,NETWORK_PARTITION,DATABASE_LATENCY scenarioStyle
    class BLAST_RADIUS,AUTO_RECOVERY,MANUAL_OVERRIDE,MONITORING_GUARD safetyStyle
    class RESILIENCE_IMPROVEMENT,WEAKNESS_DISCOVERY,CONFIDENCE_BUILDING,AUTOMATION_ENHANCEMENT resultStyle
```

## Operational Metrics and SLOs

### Service Level Objectives (SLOs)
| Service | Availability SLO | Latency SLO (p99) | Error Rate SLO |
|---------|------------------|-------------------|----------------|
| News Feed | 99.95% | 200ms | <0.1% |
| Photo Upload | 99.9% | 500ms | <0.5% |
| Messaging | 99.99% | 100ms | <0.01% |
| Video Streaming | 99.9% | 3s start time | <1% |
| Graph API | 99.95% | 100ms | <0.1% |

### Operational Excellence Metrics
```mermaid
xychart-beta
    title "Meta Operational Excellence (2024)"
    x-axis [Availability, MTTR, Deployment Success, Change Failure Rate]
    y-axis "Percentage" 0 --> 100
    bar [99.95, 15, 99.8, 0.2]
```

### Capacity Planning Automation
- **Predictive Scaling**: AI-driven capacity predictions 6 months ahead
- **Auto-scaling**: Real-time resource allocation based on traffic
- **Cost Optimization**: Automatic right-sizing saves 30% on compute costs
- **Global Load Balancing**: Traffic routing optimization reduces latency by 20%

## Production Operations Team Structure

### Team Organization (2000+ Engineers)
```mermaid
pie title Production Operations Team Distribution
    "Site Reliability Engineering" : 35
    "Platform Engineering" : 25
    "Security Operations" : 15
    "Network Operations" : 10
    "Datacenter Operations" : 10
    "Release Engineering" : 5
```

### Key Operational Practices
1. **Blameless Postmortems**: Focus on system improvements, not individual blame
2. **Chaos Engineering**: Proactive failure testing builds resilience
3. **Automated Remediation**: 80% of incidents auto-resolve without human intervention
4. **Continuous Deployment**: 50K+ deployments daily with <0.2% failure rate
5. **Observability First**: Every system instrumented with metrics, logs, and traces

## Production Lessons Learned

### Key Operational Insights
1. **Automation is Essential**: Manual operations don't scale to Meta's size
2. **Observability Prevents Outages**: Good monitoring catches issues before users notice
3. **Gradual Rollouts Save the Day**: Canary deployments catch 95% of issues
4. **Chaos Engineering Works**: Proactive failure testing reduces real incidents by 60%
5. **Blameless Culture Improves Reliability**: Psychological safety leads to better incident reporting

### The October 2021 Outage Lessons
- **External Dependencies**: BGP configuration became single point of failure
- **Physical Access**: Need out-of-band management for emergency access
- **Communication**: Internal systems couldn't communicate during outage
- **Recovery Process**: Manual intervention required clear escalation paths
- **Prevention**: Enhanced change management prevents configuration errors

### Scale-Specific Challenges
- **Testing at Scale**: Staging environments can't replicate production scale
- **Global Coordination**: Time zone differences complicate incident response
- **Vendor Dependencies**: Third-party services become reliability bottlenecks
- **Cultural Scaling**: Maintaining engineering culture across 100K+ employees
- **Knowledge Transfer**: Preserving operational knowledge across team changes

*"Operating at Meta's scale means every operational practice must be automated, monitored, and tested - there's no room for manual processes when serving 3 billion users."*

**Sources**: Meta Engineering Blog, SRE Practices Documentation, Chaos Engineering Reports, Production Operations Handbook