# Cloudflare Request Flow - "The Global Golden Path"

## Overview

Cloudflare processes 50+ million HTTP requests per second through their global edge network. This diagram shows the complete request journey from user to origin, including anycast routing, DDoS mitigation, Workers execution, and cache hierarchy.

## Request Flow Diagram

```mermaid
sequenceDiagram
    participant User as User Device<br/>(Global)
    participant DNS as 1.1.1.1 DNS<br/>(14ms avg)
    participant Edge as Nearest PoP<br/>(285+ locations)
    participant WAF as Web App Firewall<br/>(L3/L4/L7 protection)
    participant Worker as Workers Runtime<br/>(V8 Isolates)
    participant Cache as Edge Cache<br/>(100TB SSD/PoP)
    participant KV as Workers KV<br/>(400+ locations)
    participant Origin as Origin Server<br/>(Customer)

    Note over User,Origin: 50M+ requests/second globally

    %% DNS Resolution Phase
    User->>DNS: DNS Query for example.com
    Note right of DNS: Anycast routing to nearest resolver<br/>1.8 trillion queries/day
    DNS-->>User: IP Address (Anycast)<br/>Latency: <20ms

    %% Request Routing Phase
    User->>Edge: HTTPS Request<br/>SSL/TLS Termination
    Note right of Edge: Anycast directs to optimal PoP<br/>99% of users <50ms away

    %% Security Layer
    Edge->>WAF: Security Inspection
    Note right of WAF: DDoS Protection: 76M attacks/day<br/>Bot Management: 99.9% accuracy<br/>Rate Limiting: Custom rules

    alt Malicious Traffic
        WAF-->>Edge: Block Request
        Edge-->>User: 403 Forbidden<br/>Latency: 10ms
    else Clean Traffic
        WAF->>Cache: Pass to Cache Layer
    end

    %% Cache Layer Processing
    Cache->>Cache: Cache Lookup
    Note right of Cache: Hit Rate: 96% global average<br/>TTL: Customer configured<br/>Purge: <30s global propagation

    alt Cache Hit
        Cache-->>Edge: Serve from Cache
        Edge-->>User: Response (200 OK)<br/>TTFB: 14ms avg
    else Cache Miss
        Cache->>Worker: Execute Workers (if configured)

        %% Workers Execution
        Note right of Worker: V8 Isolates: 50k/server<br/>CPU Limit: 50ms/request<br/>Memory: 128MB max<br/>Cold Start: <1ms

        Worker->>KV: Fetch from Workers KV
        Note right of KV: Eventually consistent<br/>Global replication: 60s<br/>Read latency: 1-5ms
        KV-->>Worker: KV Data

        Worker->>Origin: Fetch from Origin (if needed)
        Note right of Origin: Smart routing via Argo<br/>30% performance improvement<br/>Connection pooling
        Origin-->>Worker: Origin Response<br/>Latency: 50-200ms

        Worker->>Worker: Process Response<br/>(Transform, enrich, etc.)
        Worker-->>Cache: Transformed Response

        Cache->>Cache: Store in Cache<br/>(Based on Cache-Control)
        Cache-->>Edge: Response Data
        Edge-->>User: Final Response<br/>Total: 50-250ms
    end

    %% Performance Optimizations
    Note over Edge: Automatic optimizations:<br/>- Brotli/Gzip compression<br/>- Auto minification<br/>- Image optimization<br/>- HTTP/2, HTTP/3 support
```

## Detailed Request Processing

### 1. DNS Resolution (20ms budget)
```mermaid
graph LR
    subgraph "DNS Resolution Flow"
        A[User Query] --> B[Local Resolver]
        B --> C{Cached?}
        C -->|Yes| D[Return IP]
        C -->|No| E[1.1.1.1 Query]
        E --> F[Anycast Routing]
        F --> G[Nearest DNS Server]
        G --> H[Authoritative Lookup]
        H --> I[Return Cloudflare IP]
        I --> D
    end

    %% Apply colors
    classDef dnsStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    class A,B,C,D,E,F,G,H,I dnsStyle
```

**Key Metrics:**
- **Response Time**: 14ms global average
- **Cache Hit Rate**: 95%+ for popular domains
- **Daily Queries**: 1.8 trillion to 1.1.1.1
- **Global Coverage**: 99% of users <20ms away

### 2. Anycast Routing (5ms budget)
```mermaid
graph TB
    subgraph "Anycast Network"
        USER[User Request] --> INTERNET[Internet Backbone]
        INTERNET --> BGP[BGP Best Path Selection]
        BGP --> POP1[PoP: San Francisco<br/>Latency: 5ms]
        BGP --> POP2[PoP: London<br/>Latency: 25ms]
        BGP --> POP3[PoP: Tokyo<br/>Latency: 15ms]

        POP1 --> OPTIMAL[Route to Optimal PoP<br/>Lowest latency + capacity]
    end

    %% Apply colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    class USER,INTERNET,BGP,POP1,POP2,POP3,OPTIMAL edgeStyle
```

**Routing Factors:**
- **Latency**: RTT measurement
- **Capacity**: Server utilization
- **Health**: PoP availability
- **Policy**: Customer preferences

### 3. Security Processing (10ms budget)
```mermaid
graph TB
    subgraph "Security Layers"
        REQUEST[Incoming Request] --> L3[Layer 3/4 DDoS<br/>Volumetric attacks]
        L3 --> L7[Layer 7 DDoS<br/>Application attacks]
        L7 --> BOT[Bot Management<br/>ML-based detection]
        BOT --> WAF[WAF Rules<br/>Custom + Managed]
        WAF --> RATE[Rate Limiting<br/>Per IP/User/API]
        RATE --> PASS[Pass to Cache]

        L3 --> BLOCK1[Block: Too much traffic]
        L7 --> BLOCK2[Block: HTTP flood]
        BOT --> BLOCK3[Block: Bad bot]
        WAF --> BLOCK4[Block: Attack pattern]
        RATE --> BLOCK5[Block: Rate exceeded]
    end

    %% Apply colors
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    classDef blockStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class REQUEST,L3,L7,BOT,WAF,RATE,PASS serviceStyle
    class BLOCK1,BLOCK2,BLOCK3,BLOCK4,BLOCK5 blockStyle
```

**Security Metrics:**
- **DDoS Attacks**: 76 million mitigated daily
- **Bot Traffic**: 40% of all internet traffic
- **Block Rate**: <0.01% false positives
- **Processing Time**: 5-10ms additional latency

### 4. Workers Execution (50ms budget)
```mermaid
graph TB
    subgraph "Workers Runtime Environment"
        TRIGGER[Cache Miss Trigger] --> ISOLATE[Create V8 Isolate<br/>Cold start: <1ms]
        ISOLATE --> FETCH[Fetch Event Handler]
        FETCH --> KV_READ[Workers KV Read<br/>1-5ms latency]
        KV_READ --> ORIGIN[Origin Request<br/>Connection pooling]
        ORIGIN --> PROCESS[Response Processing<br/>Transform/Enrich]
        PROCESS --> KV_WRITE[Workers KV Write<br/>Eventually consistent]
        KV_WRITE --> RESPONSE[Return Response]
    end

    %% Apply colors
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff
    class TRIGGER,ISOLATE,FETCH,KV_READ,ORIGIN,PROCESS,KV_WRITE,RESPONSE serviceStyle
```

**Workers Performance:**
- **Cold Start**: <1ms (vs 100ms+ containers)
- **Memory Limit**: 128MB per isolate
- **CPU Time**: 50ms per request
- **Concurrency**: 50,000 isolates per server

### 5. Cache Processing (5ms budget)
```mermaid
graph LR
    subgraph "Cache Hierarchy"
        REQUEST[Request] --> L1[L1 Cache<br/>RAM: 32GB]
        L1 --> L2[L2 Cache<br/>SSD: 100TB]
        L2 --> ORIGIN[Origin Fetch]

        L1 --> HIT1[Cache Hit<br/>0.1ms]
        L2 --> HIT2[Cache Hit<br/>1-5ms]
        ORIGIN --> MISS[Cache Miss<br/>50-200ms]
    end

    %% Apply colors
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef hitStyle fill:#10B981,stroke:#059669,color:#fff
    classDef missStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class REQUEST,L1,L2,ORIGIN stateStyle
    class HIT1,HIT2 hitStyle
    class MISS missStyle
```

**Cache Performance:**
- **Hit Rate**: 96% global average
- **Storage**: 100TB SSD per PoP
- **Bandwidth**: 400Gbps+ per server
- **Purge Time**: <30 seconds globally

## Performance Guarantees

### Latency SLAs
- **Global TTFB**: <50ms for 99% of requests
- **Cache Hit**: <10ms response time
- **Workers Execution**: <100ms total including origin
- **DNS Resolution**: <20ms globally

### Throughput Capabilities
- **Peak Traffic**: 100+ Tbps global capacity
- **Requests/Second**: 50M+ HTTP requests
- **Concurrent Connections**: 100M+ active
- **New Connections**: 10M+ per second

### Reliability Metrics
- **Uptime**: 99.99%+ (4 9s SLA)
- **Error Rate**: <0.01% platform errors
- **Failover Time**: <30 seconds
- **Recovery Time**: <5 minutes for major incidents

This request flow represents the most optimized path for web traffic globally, with sub-second response times and industry-leading security protection at massive scale.