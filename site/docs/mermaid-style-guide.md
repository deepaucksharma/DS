# Mermaid Diagram Style Guide

## Interactive, Beautiful Diagrams with Zoom & Pan

This style guide demonstrates the new Mermaid design system with interactive zoom/pan features.

### How to Use Interactive Features

- **Zoom**: Use `Ctrl/Cmd + Scroll` or the zoom buttons
- **Pan**: Click and drag on the diagram
- **Reset**: Double-click or use the reset button
- **Fullscreen**: Press `F` key or use the fullscreen button
- **Keyboard Shortcuts**:
  - `+` or `=`: Zoom in
  - `-`: Zoom out
  - `0`: Reset view
  - `F`: Toggle fullscreen

---

## Example 1: Complete System Architecture

```mermaid
graph TB
    subgraph EdgePlane["🌐 Edge Plane - CDN & Security"]
        CDN["CDN/CloudFlare<br/>📊 500 Gbps<br/>💰 $5K/month"]
        WAF["WAF Rules<br/>🛡️ 10K rules<br/>⚡ <1ms"]
        LB["Load Balancer<br/>ALB<br/>🎯 10ms p99"]
    end

    subgraph ServicePlane["⚙️ Service Plane - Business Logic"]
        API["API Gateway<br/>Kong 3.4<br/>🔐 OAuth2/JWT"]
        MESH["Service Mesh<br/>Istio 1.19<br/>🔄 mTLS"]
        SVC1["Order Service<br/>Java 17<br/>📦 50 pods"]
        SVC2["Payment Service<br/>Go 1.21<br/>💳 PCI DSS"]
    end

    subgraph StatePlane["💾 State Plane - Data Layer"]
        DB[("PostgreSQL 16<br/>💽 10TB<br/>📈 5K TPS")]
        CACHE[("Redis 7.2<br/>⚡ 1ms p50<br/>💰 $2K/month")]
        QUEUE[("Kafka 3.6<br/>📬 1M msg/s<br/>💾 7 days")]
    end

    subgraph ControlPlane["🎛️ Control Plane - Operations"]
        MON["Prometheus<br/>📊 10K metrics/s<br/>💾 30d retention"]
        LOG["ELK Stack<br/>📝 1TB/day<br/>🔍 Full-text search"]
        TRACE["Jaeger<br/>🔗 100K traces/s<br/>⏱️ p99 tracking"]
    end

    CDN --> WAF
    WAF --> LB
    LB --> API
    API --> MESH
    MESH --> SVC1
    MESH --> SVC2
    SVC1 --> DB
    SVC1 --> CACHE
    SVC2 --> QUEUE
    SVC1 --> MON
    SVC2 --> LOG
    API --> TRACE

    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff,stroke-width:2px
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff,stroke-width:2px
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff,stroke-width:2px

    class CDN,WAF,LB edgeStyle
    class API,MESH,SVC1,SVC2 serviceStyle
    class DB,CACHE,QUEUE stateStyle
    class MON,LOG,TRACE controlStyle

    click CDN "https://example.com/docs/cdn" "CDN Documentation"
    click DB "https://example.com/docs/database" "Database Schema"
```

---

## Example 2: Request Flow Timeline

```mermaid
sequenceDiagram
    participant U as User 📱
    participant CDN as CDN 🌐
    participant LB as Load Balancer ⚖️
    participant API as API Gateway 🔐
    participant SVC as Service 💼
    participant DB as Database 💾
    participant CACHE as Cache ⚡

    Note over U,CACHE: 🎯 SLA: <50ms p99 latency

    U->>+CDN: HTTPS Request
    Note right of CDN: Cache Check<br/>HIT Rate: 80%

    alt Cache Hit
        CDN-->>U: Cached Response<br/>⏱️ 5ms
    else Cache Miss
        CDN->>+LB: Forward Request<br/>⏱️ +2ms

        LB->>+API: Route to API<br/>⏱️ +1ms

        API->>API: Auth Validation<br/>JWT Check<br/>⏱️ +3ms

        API->>+SVC: Business Logic<br/>⏱️ +5ms

        par Database Query
            SVC->>+DB: SELECT * FROM orders<br/>⏱️ +10ms
            DB-->>-SVC: 142 rows
        and Cache Lookup
            SVC->>+CACHE: GET user:123<br/>⏱️ +1ms
            CACHE-->>-SVC: User profile
        end

        SVC-->>-API: Response data
        API-->>-LB: HTTP 200 OK
        LB-->>-CDN: Response
        CDN-->>U: Final Response<br/>⏱️ Total: 35ms

        CDN->>CDN: Update Cache<br/>TTL: 300s
    end

    Note over U,CACHE: ✅ Success Rate: 99.95%<br/>📊 Throughput: 10K req/s
```

---

## Example 3: Failure Detection State Machine

```mermaid
stateDiagram-v2
    [*] --> Healthy: System Start

    Healthy --> Degraded: Component Failure<br/>Error Rate > 0.1%
    Healthy --> Healthy: Health Check OK<br/>Every 10s

    Degraded --> Recovering: Auto-healing Triggered<br/>Circuit Breaker Open
    Degraded --> Critical: Multiple Failures<br/>Error Rate > 1%

    Recovering --> Healthy: Recovery Complete<br/>Error Rate < 0.1%
    Recovering --> Degraded: Recovery Failed<br/>Timeout 60s

    Critical --> Emergency: Total Failure<br/>All replicas down
    Critical --> Recovering: Manual Intervention<br/>Operator action

    Emergency --> [*]: System Down

    note right of Healthy
        📊 Metrics:
        • CPU: <70%
        • Memory: <80%
        • Latency: <50ms p99
        • Error Rate: <0.1%
        • Throughput: 10K req/s
    end note

    note right of Degraded
        ⚠️ Warnings:
        • CPU: 70-85%
        • Memory: 80-90%
        • Latency: 50-200ms p99
        • Error Rate: 0.1-1%
        • Throughput: 5-10K req/s
    end note

    note right of Critical
        🚨 Alerts:
        • CPU: >85%
        • Memory: >90%
        • Latency: >200ms p99
        • Error Rate: >1%
        • Throughput: <5K req/s
        • PagerDuty triggered
    end note

    note right of Emergency
        ☠️ Disaster:
        • Total system failure
        • Data loss risk
        • Revenue impact
        • Executive escalation
        • War room activated
    end note
```

---

## Example 4: Cost Breakdown Pie Chart

```mermaid
pie title Monthly Infrastructure Costs ($250K Total)
    "Compute (EC2/K8s)" : 80000
    "Storage (S3/EBS)" : 45000
    "Database (RDS/DynamoDB)" : 35000
    "Network (CloudFront/ALB)" : 30000
    "Monitoring (Datadog)" : 25000
    "Security (WAF/Shield)" : 20000
    "Backup & DR" : 15000
```

---

## Example 5: Scale Evolution Journey

```mermaid
graph LR
    subgraph "Phase 1: Startup (0-10K users)"
        A1[Monolith<br/>1 Server<br/>$100/mo]
        A2[MySQL<br/>Single DB<br/>1GB]
        A1 --> A2
    end

    subgraph "Phase 2: Growth (10K-100K users)"
        B1[3 App Servers<br/>Load Balanced<br/>$1K/mo]
        B2[MySQL Primary<br/>Read Replica<br/>100GB]
        B3[Redis Cache<br/>2GB<br/>$200/mo]
        B1 --> B2
        B1 --> B3
    end

    subgraph "Phase 3: Scale (100K-1M users)"
        C1[Microservices<br/>20 Services<br/>$10K/mo]
        C2[PostgreSQL<br/>Sharded<br/>1TB]
        C3[Redis Cluster<br/>32GB<br/>$2K/mo]
        C4[Kafka<br/>3 Brokers<br/>$3K/mo]
        C1 --> C2
        C1 --> C3
        C1 --> C4
    end

    subgraph "Phase 4: Enterprise (1M+ users)"
        D1[200 Microservices<br/>Multi-region<br/>$100K/mo]
        D2[Multi-DB<br/>Postgres+Cassandra<br/>50TB]
        D3[Redis Clusters<br/>500GB RAM<br/>$20K/mo]
        D4[Kafka Fleet<br/>30 Brokers<br/>$30K/mo]
        D1 --> D2
        D1 --> D3
        D1 --> D4
    end

    A1 -.->|Growing Pains| B1
    B1 -.->|Scaling Issues| C1
    C1 -.->|Global Expansion| D1

    classDef phase1 fill:#4CAF50,stroke:#388E3C,color:#fff
    classDef phase2 fill:#2196F3,stroke:#1976D2,color:#fff
    classDef phase3 fill:#FF9800,stroke:#F57C00,color:#fff
    classDef phase4 fill:#F44336,stroke:#D32F2F,color:#fff

    class A1,A2 phase1
    class B1,B2,B3 phase2
    class C1,C2,C3,C4 phase3
    class D1,D2,D3,D4 phase4
```

---

## Example 6: GitOps Deployment Pipeline

```mermaid
gitGraph
    commit id: "Initial commit"
    commit id: "Add service A"
    branch feature/service-b
    checkout feature/service-b
    commit id: "Create service B"
    commit id: "Add tests"
    checkout main
    commit id: "Fix security issue"
    merge feature/service-b
    commit id: "Deploy v1.0"
    branch hotfix/db-conn
    checkout hotfix/db-conn
    commit id: "Fix connection pool"
    checkout main
    merge hotfix/db-conn
    commit id: "Deploy v1.0.1"
    branch feature/monitoring
    checkout feature/monitoring
    commit id: "Add Prometheus"
    commit id: "Add Grafana"
    checkout main
    merge feature/monitoring
    commit id: "Deploy v1.1"
```

---

## Example 7: Gantt Chart - Migration Timeline

```mermaid
gantt
    title Database Migration Timeline
    dateFormat  YYYY-MM-DD
    section Planning
    Requirements Analysis    :done,    des1, 2024-01-01, 7d
    Architecture Design      :done,    des2, after des1, 10d
    Risk Assessment         :done,    des3, after des2, 5d

    section Development
    Schema Migration Tool    :active,  dev1, 2024-01-20, 14d
    Data Sync Service       :active,  dev2, after dev1, 10d
    Validation Scripts      :         dev3, after dev2, 7d

    section Testing
    Unit Testing            :         test1, after dev1, 5d
    Integration Testing     :         test2, after dev2, 7d
    Load Testing           :         test3, after test2, 5d

    section Deployment
    Staging Deployment      :         dep1, after test3, 3d
    Production Prep        :         dep2, after dep1, 2d
    Go Live               :crit,     dep3, after dep2, 1d
    Monitoring            :         dep4, after dep3, 7d
```

---

## Color Palette Reference

### 4-Plane Architecture Colors

| Plane | Light Mode | Dark Mode | Usage |
|-------|------------|-----------|--------|
| **Edge** | `#0066CC` | `#64B5F6` | CDN, WAF, Load Balancers |
| **Service** | `#00AA00` | `#66BB6A` | API Gateway, Microservices |
| **State** | `#FF8800` | `#FFB74D` | Databases, Caches, Storage |
| **Control** | `#CC0000` | `#EF5350` | Monitoring, Logging, Alerts |

### Semantic Colors

| Purpose | Color | Usage |
|---------|-------|--------|
| **Success** | `#4CAF50` | Healthy states, successful operations |
| **Warning** | `#FF9800` | Degraded states, warnings |
| **Error** | `#F44336` | Failures, critical issues |
| **Info** | `#2196F3` | Informational states, metrics |

---

## Best Practices

### 1. Always Use Production Metrics
```mermaid
graph LR
    Bad["Service<br/>High Performance"]
    Good["Service<br/>p99: 45ms<br/>10K req/s<br/>$2K/month"]

    Bad -.->|❌ Vague| X[Don't Use]
    Good -.->|✅ Specific| Y[Do Use]

    style Bad fill:#ffcccc
    style Good fill:#ccffcc
```

### 2. Include Failure Scenarios
```mermaid
graph TB
    Service[Service A] --> DB[(Database)]
    Service -.->|Timeout 30s| Fallback[Fallback Cache]
    Service -.->|Circuit Breaker| Error[Error Handler]

    style Fallback fill:#FFA726
    style Error fill:#EF5350
```

### 3. Show Cost Information
```mermaid
graph LR
    subgraph Monthly Costs
        Compute["EC2<br/>m5.xlarge x10<br/>💰 $1,400"]
        Storage["S3<br/>10TB<br/>💰 $230"]
        Network["CloudFront<br/>1TB transfer<br/>💰 $85"]
    end
```

### 4. Add Interactive Elements
- Make important nodes clickable with documentation links
- Use clear labels that indicate interaction possibilities
- Add hover effects for better user experience

---

## Testing the Features

1. **Test Zoom**: Try zooming in/out on any diagram above
2. **Test Pan**: Click and drag to move the diagram
3. **Test Reset**: Double-click to reset the view
4. **Test Fullscreen**: Press F key while hovering over a diagram
5. **Test Mobile**: If on mobile, try pinch-to-zoom

---

## Troubleshooting

If diagrams aren't interactive:
1. Ensure JavaScript is enabled
2. Check browser console for errors
3. Verify files are loaded:
   - `/javascripts/mermaid-interactive.js`
   - `/stylesheets/mermaid-beautiful.css`
4. Clear browser cache and reload

---

*This style guide is part of the Distributed Systems Architecture Framework v5.0*