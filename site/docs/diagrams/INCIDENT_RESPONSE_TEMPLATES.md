# Incident Response Diagram Templates
## For When Production is on Fire at 3 AM

### 🚨 Template 1: Service Down - Where to Look

```mermaid
graph TB
    subgraph "🔴 SERVICE DOWN - Debugging Path"
        Start[Service Unreachable] -->|1| CheckLB[Check Load Balancer<br/>━━━━━<br/>📊 AWS Console → EC2 → LB<br/>✓ Health checks failing?<br/>✓ Target groups healthy?]

        CheckLB -->|Unhealthy| CheckInstances[Check Instances<br/>━━━━━<br/>📊 kubectl get pods<br/>📊 kubectl describe pod<br/>✓ OOMKilled?<br/>✓ CrashLoopBackOff?]

        CheckLB -->|Healthy| CheckApp[Check Application<br/>━━━━━<br/>📊 kubectl logs -f service-*<br/>✓ Panic/Exception?<br/>✓ Deadlock?<br/>✓ Resource exhaustion?]

        CheckInstances -->|OOM| MemoryFix[Increase Memory<br/>━━━━━<br/>🔧 kubectl edit deployment<br/>🔧 resources.limits.memory: 4Gi<br/>🔧 kubectl rollout status]

        CheckInstances -->|Crash| LogAnalysis[Analyze Crash<br/>━━━━━<br/>📊 kubectl logs --previous<br/>📊 Check error tracking<br/>📊 Review recent deploys]

        CheckApp -->|Errors| CheckDeps[Check Dependencies<br/>━━━━━<br/>📊 Database connections?<br/>📊 Redis available?<br/>📊 External APIs?]

        CheckDeps -->|DB Issue| DBDebug[Database Debug<br/>━━━━━<br/>📊 SHOW PROCESSLIST<br/>📊 Check slow query log<br/>📊 Connection pool exhausted?]
    end

    style Start fill:#ff0000,color:#fff
    style CheckLB fill:#ff8800
    style CheckInstances fill:#ff8800
    style CheckApp fill:#ff8800
```

### 🔥 Template 2: Database is Slow

```mermaid
graph LR
    subgraph "🐌 DATABASE SLOW - Investigation Flow"
        Symptom[High Latency<br/>━━━━━<br/>⚠️ p99 > 1s<br/>⚠️ Timeouts] -->|1| Connections[Check Connections<br/>━━━━━<br/>📊 SHOW PROCESSLIST;<br/>📊 Active: 450/500<br/>🚨 Pool exhausted?]

        Connections -->|2| SlowQueries[Find Slow Queries<br/>━━━━━<br/>📊 SHOW SLOW QUERIES;<br/>📊 SELECT * FROM pg_stat_statements<br/>📊 ORDER BY total_time DESC;]

        SlowQueries -->|3| ExplainPlan[Explain Plan<br/>━━━━━<br/>📊 EXPLAIN ANALYZE<br/>✓ Full table scan?<br/>✓ Missing index?<br/>✓ Bad join order?]

        ExplainPlan -->|4| QuickFix[Immediate Actions<br/>━━━━━<br/>🔧 KILL long queries<br/>🔧 Add missing index<br/>🔧 Increase cache<br/>🔧 Scale read replicas]

        Connections -->|If Normal| Resources[Check Resources<br/>━━━━━<br/>📊 CPU: 95%<br/>📊 Memory: 87%<br/>📊 Disk I/O: 10K IOPS<br/>📊 Network: Saturated?]

        Resources -->|5| Scale[Scaling Decision<br/>━━━━━<br/>🔧 Vertical: r5.4xl → r5.8xl<br/>🔧 Horizontal: Add replicas<br/>🔧 Caching: Add Redis]
    end

    style Symptom fill:#ff6600
    style QuickFix fill:#00aa00
    style Scale fill:#00aa00
```

### ⚡ Template 3: Latency Spike - Trace the Path

```mermaid
sequenceDiagram
    participant User
    participant CDN
    participant LB as Load Balancer
    participant API
    participant Cache
    participant DB

    Note over User,DB: 🔴 LATENCY SPIKE - Where is the delay?

    User->>CDN: Request (Browser)<br/>⏱️ +5ms (normal)
    Note right of CDN: ✅ CDN OK<br/>Check: Cache hit rate

    CDN->>LB: Forward (miss)<br/>⏱️ +2ms (normal)
    Note right of LB: ✅ LB OK<br/>Check: Connection pool

    LB->>API: Route request<br/>⏱️ +500ms 🚨 SLOW
    Note right of API: ❌ API SLOW<br/>Check: CPU, Memory<br/>Check: Thread pool<br/>Check: GC pauses

    API->>Cache: Get data<br/>⏱️ +1ms (normal)
    Note right of Cache: ✅ Cache OK<br/>Hit rate: 99%

    API->>DB: Query (cache miss)<br/>⏱️ +2000ms 🚨 VERY SLOW
    Note right of DB: ❌ DB BOTTLENECK<br/>Check: Slow queries<br/>Check: Lock waits<br/>Check: Replication lag

    DB-->>API: Response<br/>⏱️ Total: 2508ms
    API-->>User: Response<br/>⏱️ Total: 2513ms

    Note over User,DB: 🔧 Actions: Check API threads, DB slow query log
```

### 💥 Template 4: Cascade Failure Pattern

```mermaid
graph TB
    subgraph "⚡ CASCADE FAILURE - Timeline"
        T0[Initial Trigger<br/>━━━━━<br/>12:00 - DB replica lag<br/>Lag: 5s → 60s] -->|Slow reads| T1[Service Degradation<br/>━━━━━<br/>12:02 - API timeouts<br/>Error rate: 0.1% → 5%]

        T1 -->|Retries| T2[Load Amplification<br/>━━━━━<br/>12:03 - Retry storm<br/>Request rate: 10K → 50K/s]

        T2 -->|Overload| T3[Service A Fails<br/>━━━━━<br/>12:05 - Circuit breaker open<br/>Availability: 0%]

        T3 -->|Dependency| T4[Service B Fails<br/>━━━━━<br/>12:06 - Dependent on A<br/>Availability: 0%]

        T4 -->|Cascade| T5[Service C Fails<br/>━━━━━<br/>12:07 - Dependent on B<br/>Availability: 0%]

        T5 -->|Platform Down| T6[Full Outage<br/>━━━━━<br/>12:10 - All services affected<br/>Impact: 100% users]
    end

    subgraph "🔧 RECOVERY SEQUENCE"
        R1[Stop Incoming Traffic<br/>━━━━━<br/>🔧 Enable maintenance mode]
        R2[Fix Root Cause<br/>━━━━━<br/>🔧 Restart DB replica]
        R3[Reset Circuit Breakers<br/>━━━━━<br/>🔧 Clear error counts]
        R4[Gradual Traffic Ramp<br/>━━━━━<br/>🔧 10% → 25% → 50% → 100%]

        R1 --> R2 --> R3 --> R4
    end

    style T0 fill:#ffaa00
    style T3 fill:#ff0000
    style T6 fill:#cc0000
    style R1 fill:#00aa00
```

### 🔄 Template 5: Circuit Breaker States

```mermaid
stateDiagram-v2
    [*] --> Closed: Start

    Closed --> Open: Failure Threshold<br/>━━━━━<br/>Errors > 50%<br/>in 10 seconds

    Open --> HalfOpen: Timeout<br/>━━━━━<br/>After 30 seconds

    HalfOpen --> Closed: Success<br/>━━━━━<br/>Test request OK

    HalfOpen --> Open: Failure<br/>━━━━━<br/>Test failed

    state Closed {
        [*] --> Monitoring
        Monitoring --> Monitoring: Success
        Monitoring --> Counting: Error
        Counting --> Monitoring: Error < 50%
        Counting --> [*]: Error >= 50%
    }

    state Open {
        [*] --> FastFailing
        FastFailing --> FastFailing: Reject all<br/>Return cached/default
        FastFailing --> [*]: Timer expires
    }

    state HalfOpen {
        [*] --> Testing
        Testing --> [*]: Single request
    }

    note right of Closed
        📊 Metrics to Monitor:
        - Success rate
        - Response time
        - Error types
    end note

    note right of Open
        🔧 During Open State:
        - Serve from cache
        - Return defaults
        - Queue for retry
    end note
```

### 📊 Template 6: Memory Leak Detection

```mermaid
graph LR
    subgraph "💾 MEMORY LEAK - Investigation"
        Start[OOM Kills<br/>━━━━━<br/>Pods restarting<br/>Every 2-3 hours] --> Heap[Heap Dump<br/>━━━━━<br/>📊 jmap -dump:format=b,file=/tmp/heap.hprof PID<br/>📊 kubectl cp pod:/tmp/heap.hprof ./heap.hprof]

        Heap --> Analyze[Analyze Heap<br/>━━━━━<br/>🔧 Eclipse MAT<br/>🔧 jhat heap.hprof<br/>📊 Dominator tree<br/>📊 Leak suspects]

        Analyze --> Found[Found Leak<br/>━━━━━<br/>📍 HashMap growing<br/>📍 Connection pool<br/>📍 Cache unbounded]

        Found --> Fix[Fix & Deploy<br/>━━━━━<br/>🔧 Add size limit<br/>🔧 Implement LRU<br/>🔧 Close connections<br/>🔧 Deploy canary]

        Start --> Metrics[Memory Metrics<br/>━━━━━<br/>📊 kubectl top pods<br/>📊 Grafana dashboard<br/>📊 Linear growth?]

        Metrics --> Profile[Profiling<br/>━━━━━<br/>🔧 async-profiler<br/>🔧 pprof (Go)<br/>🔧 memory_profiler (Python)]
    end

    style Start fill:#ff6600
    style Fix fill:#00aa00
```

### 🌐 Template 7: Multi-Region Failure

```mermaid
graph TB
    subgraph "US-East-1 🔴 DOWN"
        USE1_LB[Load Balancer<br/>━━━━━<br/>❌ Unhealthy]
        USE1_APP[Application<br/>━━━━━<br/>❌ No response]
        USE1_DB[(Database<br/>━━━━━<br/>❌ Unreachable)]
    end

    subgraph "US-West-2 ✅ FAILOVER"
        USW2_LB[Load Balancer<br/>━━━━━<br/>✅ Healthy<br/>🔧 Receiving traffic]
        USW2_APP[Application<br/>━━━━━<br/>✅ Running<br/>⚠️ 2x normal load]
        USW2_DB[(Database<br/>━━━━━<br/>✅ Promoted to primary<br/>⚠️ Replication lag)]
    end

    subgraph "📋 FAILOVER CHECKLIST"
        Step1[1. Confirm East is down<br/>━━━━━<br/>☐ Multiple availability zones<br/>☐ Not just monitoring]
        Step2[2. Update DNS<br/>━━━━━<br/>☐ Route53 health check<br/>☐ TTL considerations]
        Step3[3. Promote West DB<br/>━━━━━<br/>☐ Check replication lag<br/>☐ Accept data loss?]
        Step4[4. Scale West<br/>━━━━━<br/>☐ Double capacity<br/>☐ Monitor closely]
        Step5[5. Notify<br/>━━━━━<br/>☐ Status page<br/>☐ Customer communication]

        Step1 --> Step2 --> Step3 --> Step4 --> Step5
    end

    style USE1_LB fill:#ff0000
    style USE1_APP fill:#ff0000
    style USE1_DB fill:#ff0000
    style USW2_LB fill:#00aa00
    style USW2_APP fill:#00aa00
```

### 🔍 Template 8: Distributed Tracing Debug

```mermaid
sequenceDiagram
    participant Client
    participant Gateway
    participant ServiceA
    participant ServiceB
    participant Database

    Note over Client,Database: 🔍 TRACE ID: 7f3a2b1c-9d8e-4f5a

    Client->>Gateway: GET /api/order/123<br/>━━━━━<br/>TraceID: 7f3a2b1c<br/>SpanID: 0001<br/>⏱️ 0ms

    Gateway->>ServiceA: CheckInventory()<br/>━━━━━<br/>TraceID: 7f3a2b1c<br/>SpanID: 0002<br/>ParentSpan: 0001<br/>⏱️ 10ms

    ServiceA->>ServiceB: GetPricing()<br/>━━━━━<br/>TraceID: 7f3a2b1c<br/>SpanID: 0003<br/>ParentSpan: 0002<br/>⏱️ 15ms

    ServiceB->>Database: SELECT price<br/>━━━━━<br/>TraceID: 7f3a2b1c<br/>SpanID: 0004<br/>ParentSpan: 0003<br/>⏱️ 20ms

    Database-->>ServiceB: Result<br/>━━━━━<br/>⏱️ 520ms 🚨 SLOW

    ServiceB-->>ServiceA: Price data<br/>━━━━━<br/>⏱️ 525ms

    ServiceA-->>Gateway: Inventory OK<br/>━━━━━<br/>⏱️ 530ms

    Gateway-->>Client: Response<br/>━━━━━<br/>⏱️ 535ms total

    Note over Client,Database: 🔧 Finding: Database query slow (500ms)<br/>🔧 Action: Check query plan, add index
```

---

## 🎯 Usage Guidelines

### When to Use Each Template

| Template | Scenario | Key Metrics |
|----------|----------|-------------|
| Service Down | Complete outage | Health checks, pod status |
| Database Slow | High latency | Query time, connections |
| Latency Spike | Performance degradation | p50, p99, p99.9 |
| Cascade Failure | Spreading outage | Error rates, dependencies |
| Circuit Breaker | Service protection | Failure %, state transitions |
| Memory Leak | OOM kills | Heap size, GC time |
| Multi-Region | DR scenario | RPO, RTO, data loss |
| Distributed Trace | Complex flows | Span timings, bottlenecks |

### Customization Required

For each template:
1. Replace generic names with actual service names
2. Add real metrics from your monitoring
3. Include specific commands for your environment
4. Link to your runbooks and dashboards

### Quality Checklist

- [ ] Shows clear debugging path
- [ ] Includes actual commands to run
- [ ] Has specific metrics to check
- [ ] Provides immediate actions
- [ ] References monitoring tools
- [ ] Helps at 3 AM when tired

---

## 🚨 Remember

**These diagrams are for emergencies.**

They should be:
- **Actionable**: Every box has a command or check
- **Specific**: No generic "check database"
- **Sequential**: Clear order of investigation
- **Practical**: Based on real incidents

**If it doesn't reduce MTTR, it doesn't belong here.**