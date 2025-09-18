# Cloudflare Failure Domains - "The Incident Blast Radius Map"

## Overview

Cloudflare's global architecture is designed with multiple failure domains to ensure that localized failures don't cascade into global outages. With 285+ PoPs worldwide, the platform automatically routes around failures within 30 seconds while maintaining service availability.

## Global Failure Domain Architecture

```mermaid
graph TB
    subgraph "Global Failure Domains"
        subgraph "Tier 1: Regional Failures #8B5CF6"
            REGION_NA[North America<br/>100+ PoPs<br/>Blast radius: 15% traffic]
            REGION_EU[Europe<br/>80+ PoPs<br/>Blast radius: 25% traffic]
            REGION_ASIA[Asia Pacific<br/>70+ PoPs<br/>Blast radius: 35% traffic]
            REGION_OTHER[Other Regions<br/>35+ PoPs<br/>Blast radius: 25% traffic]
        end

        subgraph "Tier 2: Metro Failures #F59E0B"
            METRO_NYC[NYC Metro<br/>4 PoPs<br/>Blast radius: 2% traffic]
            METRO_LON[London Metro<br/>3 PoPs<br/>Blast radius: 3% traffic]
            METRO_SIN[Singapore Metro<br/>2 PoPs<br/>Blast radius: 4% traffic]
        end

        subgraph "Tier 3: PoP Failures #F59E0B"
            POP_JFK[JFK PoP<br/>20 servers<br/>400 Gbps capacity]
            POP_LHR[LHR PoP<br/>30 servers<br/>600 Gbps capacity]
            POP_NRT[NRT PoP<br/>15 servers<br/>300 Gbps capacity]
        end

        subgraph "Tier 4: Server Failures #FFCC00"
            SERVER_1[Server Rack A<br/>10 servers<br/>40 Gbps]
            SERVER_2[Server Rack B<br/>10 servers<br/>40 Gbps]
            SERVER_3[Server Rack C<br/>10 servers<br/>40 Gbps]
        end
    end

    subgraph "Cascading Failure Prevention #10B981"
        CIRCUIT[Circuit Breakers<br/>Per-service protection]
        BULKHEAD[Bulkhead Isolation<br/>Resource partitioning]
        BACKPRESSURE[Backpressure Control<br/>Load shedding]
        FALLBACK[Fallback Mechanisms<br/>Degraded service mode]
    end

    %% Failure relationships
    REGION_NA -.->|Contains| METRO_NYC
    METRO_NYC -.->|Contains| POP_JFK
    POP_JFK -.->|Contains| SERVER_1

    %% Protection mechanisms
    CIRCUIT --> REGION_NA
    BULKHEAD --> METRO_NYC
    BACKPRESSURE --> POP_JFK
    FALLBACK --> SERVER_1

    %% Apply colors based on blast radius
    classDef criticalStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef highStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef mediumStyle fill:#FFCC00,stroke:#CC9900,color:#000
    classDef protectionStyle fill:#10B981,stroke:#059669,color:#fff

    class REGION_NA,REGION_EU,REGION_ASIA,REGION_OTHER criticalStyle
    class METRO_NYC,METRO_LON,METRO_SIN,POP_JFK,POP_LHR,POP_NRT highStyle
    class SERVER_1,SERVER_2,SERVER_3 mediumStyle
    class CIRCUIT,BULKHEAD,BACKPRESSURE,FALLBACK protectionStyle
```

## Historical Incident Analysis

### July 2, 2019 - The Regex Outage

```mermaid
graph TB
    subgraph "Regex Outage Timeline"
        T1[13:42 UTC<br/>WAF Rule Deployment] --> T2[13:43 UTC<br/>CPU Spike to 100%<br/>All PoPs affected]
        T2 --> T3[13:45 UTC<br/>Service Degradation<br/>Global impact]
        T3 --> T4[14:02 UTC<br/>Rule Identified<br/>Emergency rollback]
        T4 --> T5[14:07 UTC<br/>Traffic Recovery<br/>27-minute outage]

        subgraph "Root Cause"
            REGEX[WAF Regex Rule<br/>.?=.*<br/>Catastrophic backtracking]
            CPU[CPU Exhaustion<br/>100% utilization<br/>All worker processes]
        end

        subgraph "Blast Radius"
            GLOBAL[Global Impact<br/>100% of traffic<br/>All services affected]
            REVENUE[Revenue Impact<br/>$2M+ estimated<br/>Customer SLA credits]
        end

        T2 --> REGEX
        REGEX --> CPU
        CPU --> GLOBAL
        GLOBAL --> REVENUE
    end

    %% Apply incident colors
    classDef incidentStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef impactStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class T1,T2,T3,T4,T5,REGEX,CPU incidentStyle
    class GLOBAL,REVENUE impactStyle
```

**Lessons Learned:**
- **Testing**: Regex patterns must be tested for performance impact
- **Gradual Rollout**: Security rules need staged deployment
- **Circuit Breakers**: CPU-based protection for runaway processes
- **Monitoring**: Real-time alerting for resource exhaustion

### June 21, 2022 - BGP Route Leak

```mermaid
graph TB
    subgraph "BGP Route Leak Incident"
        CHANGE[Route Change<br/>Internal backbone] --> LEAK[BGP Route Leak<br/>Incorrect advertisements]
        LEAK --> BLACKHOLE[Traffic Blackholing<br/>19 PoPs affected]
        BLACKHOLE --> DETECTION[Automated Detection<br/>5-minute delay]
        DETECTION --> MITIGATION[Route Withdrawal<br/>Traffic recovery]

        subgraph "Affected Services"
            DNS_IMPACT[1.1.1.1 DNS<br/>Resolver unavailable]
            CDN_IMPACT[CDN Services<br/>Cache misses]
            WORKERS_IMPACT[Workers Runtime<br/>Execution failures]
        end

        BLACKHOLE --> DNS_IMPACT
        BLACKHOLE --> CDN_IMPACT
        BLACKHOLE --> WORKERS_IMPACT
    end

    %% Apply colors
    classDef incidentStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef serviceStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class CHANGE,LEAK,BLACKHOLE,DETECTION,MITIGATION incidentStyle
    class DNS_IMPACT,CDN_IMPACT,WORKERS_IMPACT serviceStyle
```

**Impact Metrics:**
- **Duration**: 47 minutes total
- **Affected PoPs**: 19 out of 285+ locations
- **Traffic Impact**: 7% of global traffic
- **Recovery Time**: 15 minutes after detection

## Failure Detection and Response

### Automated Failure Detection

```mermaid
graph TB
    subgraph "Detection Systems"
        HEALTH[Health Checks<br/>Every 10 seconds<br/>HTTP/TCP/ICMP]
        METRICS[Metrics Monitoring<br/>Real-time telemetry<br/>Latency/Error rates]
        TRAFFIC[Traffic Monitoring<br/>Request patterns<br/>Anomaly detection]
    end

    subgraph "Response Actions"
        ALERT[Alert Generation<br/>PagerDuty/Slack<br/>Severity classification]
        REROUTE[Traffic Rerouting<br/>BGP withdrawal<br/>DNS failover]
        SCALE[Auto Scaling<br/>Capacity increase<br/>Load distribution]
    end

    subgraph "Recovery Procedures"
        INVESTIGATE[Root Cause Analysis<br/>Log correlation<br/>Performance profiling]
        REPAIR[Automated Repair<br/>Service restart<br/>Configuration reload]
        VALIDATE[Service Validation<br/>Health verification<br/>Performance testing]
    end

    HEALTH --> ALERT
    METRICS --> REROUTE
    TRAFFIC --> SCALE

    ALERT --> INVESTIGATE
    REROUTE --> REPAIR
    SCALE --> VALIDATE

    %% Apply colors
    classDef detectionStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef responseStyle fill:#10B981,stroke:#059669,color:#fff
    classDef recoveryStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class HEALTH,METRICS,TRAFFIC detectionStyle
    class ALERT,REROUTE,SCALE responseStyle
    class INVESTIGATE,REPAIR,VALIDATE recoveryStyle
```

### Failover Mechanisms

```mermaid
graph TB
    subgraph "Anycast Failover"
        PRIMARY[Primary PoP<br/>Normal operation] --> FAILURE[PoP Failure<br/>Health check fails]
        FAILURE --> BGP_WITHDRAW[BGP Route Withdrawal<br/>30-second timeout]
        BGP_WITHDRAW --> REROUTE[Traffic Rerouting<br/>Next closest PoP]
        REROUTE --> SECONDARY[Secondary PoP<br/>Increased load]
    end

    subgraph "Service Failover"
        SERVICE_A[Service Instance A] --> CIRCUIT_OPEN[Circuit Breaker Open<br/>Error threshold exceeded]
        CIRCUIT_OPEN --> SERVICE_B[Service Instance B<br/>Healthy backup]
        SERVICE_B --> LOAD_SHED[Load Shedding<br/>Priority traffic only]
    end

    %% Apply colors
    classDef normalStyle fill:#10B981,stroke:#059669,color:#fff
    classDef failureStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef recoveryStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class PRIMARY,SERVICE_A normalStyle
    class FAILURE,CIRCUIT_OPEN failureStyle
    class BGP_WITHDRAW,REROUTE,SECONDARY,SERVICE_B,LOAD_SHED recoveryStyle
```

## Blast Radius Containment

### Geographic Isolation

| Failure Type | Affected Area | Traffic Impact | Recovery Time | Mitigation |
|--------------|---------------|----------------|---------------|------------|
| Server Failure | Single rack | 0.01% | 10 seconds | Load balancer failover |
| PoP Failure | City/Metro | 0.1-2% | 30 seconds | BGP rerouting |
| Metro Failure | Metropolitan area | 1-5% | 2 minutes | Regional failover |
| Regional Failure | Continent | 15-35% | 5 minutes | Cross-region failover |
| Cable Cut | Ocean region | 5-15% | 15 minutes | Satellite backup |

### Service Isolation

```mermaid
graph LR
    subgraph "Service Isolation Strategy"
        CDN[CDN Service<br/>Isolated resources]
        DNS[DNS Service<br/>Dedicated infra]
        WORKERS[Workers Platform<br/>Separate compute]
        SECURITY[Security Services<br/>Independent processing]

        CDN -.->|No impact| DNS
        DNS -.->|No impact| WORKERS
        WORKERS -.->|No impact| SECURITY
    end

    subgraph "Resource Partitioning"
        CPU_CDN[CPU: 40%<br/>CDN processing]
        CPU_WORKERS[CPU: 30%<br/>Workers execution]
        CPU_SECURITY[CPU: 20%<br/>Security filtering]
        CPU_MGMT[CPU: 10%<br/>Management/monitoring]
    end

    %% Apply colors
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef resourceStyle fill:#F59E0B,stroke:#D97706,color:#fff

    class CDN,DNS,WORKERS,SECURITY serviceStyle
    class CPU_CDN,CPU_WORKERS,CPU_SECURITY,CPU_MGMT resourceStyle
```

## Circuit Breaker Implementation

### Per-Service Protection

```mermaid
stateDiagram-v2
    [*] --> Closed: Normal Operation
    Closed --> Open: Error Rate > 50%
    Open --> HalfOpen: 60s timeout
    HalfOpen --> Closed: Success Rate > 90%
    HalfOpen --> Open: Error Rate > 20%

    state Closed {
        [*] --> AllowTraffic
        AllowTraffic --> MonitorErrors
        MonitorErrors --> AllowTraffic
    }

    state Open {
        [*] --> RejectTraffic
        RejectTraffic --> FallbackMode
        FallbackMode --> RejectTraffic
    }

    state HalfOpen {
        [*] --> LimitedTraffic
        LimitedTraffic --> TestHealth
        TestHealth --> LimitedTraffic
    }
```

### Fallback Strategies

- **CDN Fallback**: Direct origin connection when edge fails
- **DNS Fallback**: Secondary resolver when primary unavailable
- **Workers Fallback**: Static response when compute fails
- **Security Fallback**: Allow traffic when WAF unavailable

## Recovery Procedures

### Incident Response Timeline

```mermaid
gantt
    title Cloudflare Incident Response
    dateFormat X
    axisFormat %M:%S

    section Detection
    Automated monitoring :done, monitoring, 0, 30s
    Alert generation :done, alert, 30s, 60s
    On-call notification :done, oncall, 60s, 90s

    section Assessment
    Initial triage :done, triage, 90s, 3m
    Impact assessment :done, impact, 3m, 5m
    Escalation decision :done, escalate, 5m, 7m

    section Mitigation
    Traffic rerouting :done, reroute, 7m, 9m
    Service isolation :done, isolate, 9m, 12m
    Fallback activation :done, fallback, 12m, 15m

    section Recovery
    Root cause fix :done, fix, 15m, 25m
    Service restoration :done, restore, 25m, 30m
    Post-incident review :done, review, 30m, 60m
```

### Recovery Time Objectives (RTO)

- **Detection**: <30 seconds for critical failures
- **Notification**: <60 seconds to on-call team
- **Mitigation**: <5 minutes for traffic rerouting
- **Recovery**: <15 minutes for service restoration
- **Communication**: <10 minutes for status page update

This failure domain architecture ensures that Cloudflare maintains 99.99%+ uptime despite operating one of the world's largest distributed systems, with automatic failover and recovery capabilities that minimize the blast radius of any single failure.