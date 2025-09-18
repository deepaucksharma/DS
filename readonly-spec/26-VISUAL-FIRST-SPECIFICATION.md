# Visual-First Specification v2.0: The Atlas Evolution

## Executive Mandate: Diagrams Over Text

```mermaid
graph LR
    subgraph Input["Information Input"]
        I1[Engineering Blogs]
        I2[Incident Reports]
        I3[Architecture Docs]
    end

    subgraph Transform["Transformation"]
        T1[Extract Metrics]
        T2[Map to 4-Plane]
        T3[Calculate Costs]
        T4[Document Failures]
    end

    subgraph Output["Visual Output"]
        O1[Mermaid Diagrams]
        O2[Metrics Tables]
        O3[Failure Matrices]
        O4[Cost Analysis]
    end

    I1 --> T1 --> O1
    I2 --> T2 --> O2
    I3 --> T3 --> O3
    I3 --> T4 --> O4

    style Input fill:#FFE5E5
    style Transform fill:#FFFACD
    style Output fill:#E5FFE5
```

## The New Specification Rules

### Rule 1: Maximum Text Limits

| Content Type | Old Limit | New Limit | Example |
|--------------|-----------|-----------|---------|
| **Section Intro** | No limit | 2 sentences | "Netflix serves 260M users. Here's how." |
| **Diagram Caption** | Paragraph | 1 sentence | "Request flow with latency budgets." |
| **Table Header** | Multiple lines | 5 words max | "Failure Recovery Matrix" |
| **Bullet Points** | Unlimited | 5 items max | Only critical points |

### Rule 2: Mandatory Visual Elements

Every topic MUST include:

```mermaid
graph TD
    subgraph Required["Required Elements"]
        R1[4-Plane Architecture Diagram]
        R2[Metrics Performance Table]
        R3[Failure Scenario Matrix]
        R4[Cost Breakdown Table]
        R5[Recovery Procedure Flow]
    end

    subgraph Optional["Optional Elements"]
        O1[Sequence Diagrams]
        O2[State Machines]
        O3[Gantt Charts]
    end

    R1 --> R2 --> R3 --> R4 --> R5
```

### Rule 3: The 4-Plane Color Mandate

| Plane | Color Code | RGB | Components | Metrics Required |
|-------|------------|-----|------------|------------------|
| **Edge** | #0066CC | (0,102,204) | CDN, LB, WAF | Latency, Bandwidth |
| **Service** | #00AA00 | (0,170,0) | API, Logic | RPS, Error Rate |
| **State** | #FF8800 | (255,136,0) | DB, Cache | IOPS, Storage |
| **Control** | #CC0000 | (204,0,0) | Monitor, Config | Metrics/sec |

### Rule 4: Metrics Are Mandatory

| Metric Type | Required Format | Example | Banned Words |
|-------------|----------------|---------|--------------|
| **Latency** | p50/p99/p999 | p99: 10ms | "Fast", "Quick" |
| **Throughput** | Exact number + unit | 100K RPS | "High", "Scalable" |
| **Availability** | Percentage + downtime | 99.95% (26 min/year) | "Reliable", "Stable" |
| **Cost** | $/unit + total | $0.001/req ($100K/mo) | "Cheap", "Expensive" |
| **Scale** | Exact numbers | 10M users, 1B requests | "Large", "Massive" |

## Content Transformation Templates

### Template 1: System Architecture (Visual Only)

```mermaid
graph TB
    subgraph Edge["Edge #0066CC - $40K/mo"]
        CDN["Cloudflare<br/>285 PoPs<br/>p99: 10ms"]
        LB["HAProxy<br/>10K conn<br/>p99: 2ms"]
    end

    subgraph Service["Service #00AA00 - $60K/mo"]
        API["Kong 3.4<br/>1M RPS<br/>p99: 20ms"]
        Auth["Auth0<br/>10K/min<br/>p99: 100ms"]
    end

    subgraph State["State #FF8800 - $80K/mo"]
        DB["PostgreSQL 14<br/>100K TPS<br/>p99: 5ms"]
        Cache["Redis 7.0<br/>1M ops/sec<br/>p99: 0.5ms"]
    end

    subgraph Control["Control #CC0000 - $20K/mo"]
        Monitor["Prometheus<br/>10M metrics<br/>30d retention"]
    end

    CDN -->|"5ms"| LB -->|"2ms"| API
    API -->|"5ms"| DB
    API -->|"0.5ms"| Cache
    API -.->|"Async"| Monitor

    style Edge fill:#0066CC,color:#fff
    style Service fill:#00AA00,color:#fff
    style State fill:#FF8800,color:#fff
    style Control fill:#CC0000,color:#fff
```

### Template 2: Incident Timeline (No Text Needed)

| T+ | Phase | System State | Metric | Action | Cost |
|----|-------|--------------|--------|--------|------|
| 0 | Normal | ✅ All Green | 0.01% errors | - | $0 |
| 30s | Detection | 🟡 Alerts firing | 5% errors | Page on-call | $1K/min |
| 2m | Diagnosis | 🔴 DB CPU 100% | 50% errors | Check queries | $5K/min |
| 5m | Mitigation | 🟡 Failover started | 10% errors | Route to replica | $2K/min |
| 10m | Recovery | 🟢 Service restored | 0.1% errors | Monitor stability | $0 |
| 30m | Resolution | ✅ Root cause fixed | 0.01% errors | Deploy fix | -$50K credit |

### Template 3: Capacity Model (Pure Numbers)

| Resource | Now | +3mo | +6mo | +1yr | Break Point | Action |
|----------|-----|------|------|------|-------------|--------|
| **RPS** | 50K | 75K | 110K | 200K | 150K | Scale @ 100K |
| **DB Size** | 5TB | 7TB | 10TB | 18TB | 20TB | Shard @ 15TB |
| **Cost** | $100K | $130K | $180K | $320K | $400K | Optimize @ $250K |
| **Latency p99** | 10ms | 12ms | 15ms | 25ms | 50ms | Cache @ 20ms |

## Examples: Before vs After

### ❌ OLD: Text-Heavy Explanation

"Our system uses a sophisticated caching strategy that significantly improves performance. We implement a multi-tier cache architecture with Redis as the primary cache layer, which helps reduce database load. The cache uses an LRU eviction policy and maintains high hit rates through intelligent prefetching algorithms..."

### ✅ NEW: Visual + Metrics

```mermaid
graph LR
    Request -->|"p50: 0.5ms<br/>95% hit"| L1[L1: Redis<br/>Memory: 50GB<br/>Cost: $5K/mo]
    L1 -->|"Miss<br/>5%"| L2[L2: PostgreSQL<br/>Read Replica<br/>Cost: $10K/mo]
    L2 -->|"Miss<br/>0.1%"| L3[L3: Primary DB<br/>Source of Truth<br/>Cost: $30K/mo]

    style L1 fill:#90EE90
    style L2 fill:#FFD700
    style L3 fill:#FF6B6B
```

| Cache Layer | Hit Rate | Latency | Cost/Month | Failure Mode |
|-------------|----------|---------|------------|--------------|
| L1: Redis 7.0 | 95% | p99: 0.5ms | $5K | Fallback to L2 |
| L2: Read Replica | 4.9% | p99: 5ms | $10K | Fallback to L3 |
| L3: Primary DB | 0.1% | p99: 10ms | $30K | Service degraded |

## The 5 Commandments of Visual Documentation

### 1. Show the Money

```mermaid
pie title "Infrastructure Cost Breakdown - $200K/month"
    "CDN" : 40
    "Compute" : 60
    "Storage" : 50
    "Network" : 30
    "Monitoring" : 20
```

### 2. Show the Failures

```mermaid
graph TD
    Normal[Normal: $10K/hour revenue] -->|DB Fails| Degraded[Degraded: $5K/hour]
    Degraded -->|Cache Fails| Emergency[Emergency: $1K/hour]
    Emergency -->|Everything Fails| Down[Down: -$50K/hour LOSS]

    style Normal fill:#90EE90
    style Degraded fill:#FFD700
    style Emergency fill:#FFA500
    style Down fill:#FF6B6B
```

### 3. Show the Scale

| Company | Scale Metric | Infrastructure | Cost/User | Incident Cost |
|---------|--------------|----------------|-----------|---------------|
| Netflix | 260M users | 100K servers | $0.48/mo | $2.6M/hour down |
| Uber | 25M trips/day | 4K services | $0.30/trip | $1M/hour down |
| Stripe | 1M+ businesses | 99.999% uptime | $0.0001/txn | $10M/hour down |

### 4. Show the Timeline

```mermaid
gantt
    title Incident Response Timeline
    dateFormat HH:mm
    axisFormat %H:%M

    section Detection
    Alert Fires           :done, 00:00, 1m
    Page On-Call         :done, 00:01, 1m

    section Diagnosis
    Check Metrics        :active, 00:02, 3m
    Find Root Cause      :active, 00:05, 5m

    section Mitigation
    Execute Failover     :crit, 00:10, 5m
    Verify Recovery      :crit, 00:15, 5m

    section Resolution
    Deploy Fix          :00:20, 10m
    Monitor Stability   :00:30, 30m
```

### 5. Show the Architecture

Never describe architecture in words. Always show it with metrics:

```mermaid
graph TB
    subgraph Production["Production - 10M users - $125K/mo"]
        subgraph us_east["US-East - Primary"]
            API1[API: 100K RPS]
            DB1[(DB: 10TB)]
        end

        subgraph us_west["US-West - Secondary"]
            API2[API: 50K RPS]
            DB2[(DB: 10TB replica)]
        end

        subgraph eu_west["EU-West - Edge"]
            API3[API: 30K RPS]
            DB3[(DB: 5TB cache)]
        end
    end

    API1 -.->|"50ms sync"| DB2
    API1 -.->|"150ms async"| DB3
```

## Validation Checklist

Every document MUST pass:

- [ ] **Text Limit**: <10% of content is text
- [ ] **Diagram First**: Mermaid diagram in first 100 lines
- [ ] **Metrics Table**: Real numbers, no adjectives
- [ ] **4-Plane Colors**: Exact hex codes used
- [ ] **Failure Documented**: What breaks and recovery
- [ ] **Cost Included**: $ amounts for everything
- [ ] **Company Example**: Real incident or architecture
- [ ] **3AM Test**: Usable during incident
- [ ] **No Code Blocks**: Tables only
- [ ] **No Generic Terms**: Specific versions always

## Enforcement Rules

1. **Reject PRs** that don't meet visual-first criteria
2. **Automated validation** for diagram:text ratio
3. **Metrics required** - no vague descriptions
4. **Real examples only** - no hypotheticals
5. **Cost analysis mandatory** - show the money

---

*"A diagram is worth a thousand words. A metric is worth a thousand guesses. A real incident is worth a thousand theories."*

**Visual-First Specification v2.0 - Effective Immediately**