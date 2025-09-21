# Netflix Global Streaming Capacity Planning

## Overview

Netflix serves 247 million subscribers across 190+ countries, delivering 1 billion hours of content weekly through 15,000+ CDN servers. This capacity model helped Netflix handle the 50% surge during COVID-19 lockdowns and maintain sub-100ms latencies globally.

**Key Challenge**: Pre-position 15+ PB of content globally while maintaining 99.9% availability and sub-100ms response times during peak viewing hours across all time zones.

**Historical Context**: During "Stranger Things 4" premiere (May 2022), Netflix handled 2.3x normal peak traffic with zero degradation using this capacity model.

## Global Content Delivery Capacity Architecture

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - CDN Global Distribution]
        direction TB

        subgraph USRegion[US Region - 4,200 Servers]
            USEDGE[US Edge Servers<br/>4,200 servers<br/>2.8 PB cache<br/>p99: 15ms]
        end

        subgraph EuropeRegion[Europe Region - 3,800 Servers]
            EUEDGE[EU Edge Servers<br/>3,800 servers<br/>2.1 PB cache<br/>p99: 18ms]
        end

        subgraph AsiaRegion[Asia Region - 3,200 Servers]
            ASIAEDGE[Asia Edge Servers<br/>3,200 servers<br/>1.8 PB cache<br/>p99: 22ms]
        end

        subgraph LatamRegion[LATAM Region - 2,400 Servers]
            LATEDGE[LATAM Edge Servers<br/>2,400 servers<br/>1.2 PB cache<br/>p99: 25ms]
        end

        subgraph APACRegion[APAC Region - 1,400 Servers]
            APACEDGE[APAC Edge Servers<br/>1,400 servers<br/>800 TB cache<br/>p99: 28ms]
        end
    end

    subgraph ServicePlane[Service Plane - Global API Layer]
        direction TB

        subgraph GlobalAPI[Global API Tier]
            APIGATEWAY[API Gateway<br/>Netflix Zuul<br/>12 regions<br/>50K RPS per region<br/>Circuit breaker: 70% error rate]

            MICROSERVICES[Microservices Layer<br/>2,500+ services<br/>100K+ instances<br/>Auto-scale: CPU > 70%<br/>Memory > 80%]
        end

        subgraph StreamingServices[Streaming Core Services]
            PLAYAPI[Play API<br/>500 instances per region<br/>p99: 50ms<br/>Buffer: 30% overhead]

            RECOMMENDATIONS[Recommendation Engine<br/>ML inference: 150ms<br/>Cache hit: 85%<br/>Fallback: trending content]

            MANIFEST[Manifest Service<br/>CDN selection logic<br/>Real-time health checks<br/>Failover: < 2 seconds]
        end
    end

    subgraph StatePlane[State Plane - Global Data Layer]
        direction TB

        subgraph ContentStorage[Content Storage - 45 PB Total]
            ORIGINSTORAGE[Origin Storage<br/>AWS S3 + Glacier<br/>45 PB total<br/>3x replication<br/>Cost: $2.1M/month]

            TRANSCODE[Transcoding Pipeline<br/>10,000+ parallel jobs<br/>200+ video profiles<br/>Processing: 50 hours/minute]
        end

        subgraph MetadataStorage[Metadata & User Data]
            CASSANDRA[Cassandra Clusters<br/>2,500 nodes globally<br/>RF=3, LCS compaction<br/>p99 read: 5ms<br/>p99 write: 10ms]

            ELASTICSEARCH[Search Index<br/>Elasticsearch<br/>1,200 nodes<br/>50TB index data<br/>Query: p99 50ms]
        end

        subgraph CachingLayer[Multi-Tier Caching]
            REDIS[Redis Clusters<br/>EVCache (Memcached)<br/>1,000+ nodes<br/>200TB RAM<br/>Hit rate: 99.2%]
        end
    end

    subgraph ControlPlane[Control Plane - Global Operations]
        direction TB

        subgraph MonitoringStack[Global Monitoring]
            ATLAS[Netflix Atlas<br/>Time series DB<br/>2M metrics/second<br/>7-day retention<br/>Real-time alerting]

            TELEMETRY[Global Telemetry<br/>Distributed tracing<br/>1B spans/day<br/>Jaeger + Zipkin]
        end

        subgraph CapacityMgmt[Capacity Management]
            PREDICTIVE[Predictive Scaling<br/>ML-based forecasting<br/>Content popularity prediction<br/>Regional demand modeling]

            AUTOSCALE[Auto-scaling Policies<br/>Reactive: 2-5 minutes<br/>Predictive: 30 minutes<br/>Manual override: enabled]
        end

        subgraph ChaosEngineering[Chaos Engineering]
            CHAOSMONKEY[Chaos Monkey<br/>Random instance termination<br/>Daily: 100+ failures<br/>Blast radius: single AZ]

            SIMIAN[Simian Army<br/>Latency injection<br/>Dependency failures<br/>Regional outages]
        end
    end

    %% Connections with capacity labels
    USEDGE -->|"Peak: 800 Gbps<br/>Buffer: 1.2 Tbps"| APIGATEWAY
    EUEDGE -->|"Peak: 600 Gbps<br/>Buffer: 900 Gbps"| APIGATEWAY
    ASIAEDGE -->|"Peak: 450 Gbps<br/>Buffer: 675 Gbps"| APIGATEWAY
    LATEDGE -->|"Peak: 300 Gbps<br/>Buffer: 450 Gbps"| APIGATEWAY
    APACEDGE -->|"Peak: 200 Gbps<br/>Buffer: 300 Gbps"| APIGATEWAY

    APIGATEWAY -->|"500K RPS global<br/>Buffer: 750K RPS"| MICROSERVICES
    MICROSERVICES --> PLAYAPI
    MICROSERVICES --> RECOMMENDATIONS
    MICROSERVICES --> MANIFEST

    PLAYAPI -->|"Read: 100K QPS<br/>Write: 10K QPS"| CASSANDRA
    RECOMMENDATIONS -->|"Cache: 99% hit rate<br/>DB: 1% miss rate"| REDIS
    MANIFEST -->|"CDN health: 5s interval<br/>Route update: 30s"| ORIGINSTORAGE

    TRANSCODE -->|"Upload: 10 Gbps<br/>Distribution: hourly"| ORIGINSTORAGE
    CASSANDRA --> REDIS
    REDIS --> ELASTICSEARCH

    %% Monitoring connections
    ATLAS -.->|"Real-time metrics"| USEDGE
    ATLAS -.->|"Performance data"| APIGATEWAY
    ATLAS -.->|"Health checks"| CASSANDRA

    PREDICTIVE -.->|"Scale triggers"| AUTOSCALE
    AUTOSCALE -.->|"Instance management"| MICROSERVICES

    CHAOSMONKEY -.->|"Failure injection"| MICROSERVICES
    SIMIAN -.->|"Regional testing"| USEDGE

    %% Styling with 4-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#1E40AF,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef controlStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff,stroke-width:2px

    class USEDGE,EUEDGE,ASIAEDGE,LATEDGE,APACEDGE edgeStyle
    class APIGATEWAY,MICROSERVICES,PLAYAPI,RECOMMENDATIONS,MANIFEST serviceStyle
    class ORIGINSTORAGE,TRANSCODE,CASSANDRA,ELASTICSEARCH,REDIS stateStyle
    class ATLAS,TELEMETRY,PREDICTIVE,AUTOSCALE,CHAOSMONKEY,SIMIAN controlStyle
```

## Regional Capacity Distribution Model

```mermaid
graph LR
    subgraph CapacityDistribution[Global Capacity Distribution - Peak Hours]
        direction TB

        subgraph PeakHours[Peak Viewing Hours by Region]
            US_PEAK[US Peak: 8-11 PM EST<br/>Concurrent: 80M users<br/>Bandwidth: 800 Gbps<br/>Content requests: 2.5M/min]

            EU_PEAK[EU Peak: 8-11 PM CET<br/>Concurrent: 55M users<br/>Bandwidth: 600 Gbps<br/>Content requests: 1.8M/min]

            ASIA_PEAK[Asia Peak: 8-11 PM JST<br/>Concurrent: 35M users<br/>Bandwidth: 450 Gbps<br/>Content requests: 1.2M/min]

            LATAM_PEAK[LATAM Peak: 8-11 PM BRT<br/>Concurrent: 25M users<br/>Bandwidth: 300 Gbps<br/>Content requests: 800K/min]
        end

        subgraph CapacityBuffers[Capacity Buffers & Scaling]
            BUFFER_CALC[Buffer Calculations<br/>Normal: 100% baseline<br/>Buffer: +50% (1.5x)<br/>Emergency: +100% (2x)<br/>Max surge: +150% (2.5x)]

            SCALE_TRIGGERS[Auto-Scale Triggers<br/>CPU > 70%: +20% capacity<br/>Memory > 80%: +30% capacity<br/>Network > 75%: +25% bandwidth<br/>Queue depth > 100: +50% workers]

            COST_MODEL[Cost Optimization<br/>Reserved: 60% of capacity<br/>On-demand: 30% buffer<br/>Spot: 10% batch jobs<br/>Total: $180M/year infra]
        end
    end

    subgraph ContentStrategy[Content Pre-positioning Strategy]
        direction TB

        subgraph PopularityPrediction[Content Popularity Prediction]
            ML_PREDICT[ML Popularity Model<br/>Features: 200+ signals<br/>Accuracy: 85% for new content<br/>Update frequency: hourly<br/>Prediction horizon: 7 days]

            TRENDING[Trending Analysis<br/>Real-time view tracking<br/>Social media sentiment<br/>Regional preferences<br/>Content aging curves]
        end

        subgraph PrePositioning[Pre-positioning Logic]
            GLOBAL_POPULAR[Global Popular Content<br/>Top 100 titles<br/>100% cache coverage<br/>All quality profiles<br/>6 PB total size]

            REGIONAL_POPULAR[Regional Popular Content<br/>Top 500 per region<br/>85% cache coverage<br/>Primary quality profiles<br/>12 PB total size]

            LONGTAIL[Long Tail Content<br/>Remaining catalog<br/>On-demand fetch<br/>Origin fallback<br/>p99: 2 seconds]
        end
    end

    %% Connections
    US_PEAK --> BUFFER_CALC
    EU_PEAK --> BUFFER_CALC
    ASIA_PEAK --> BUFFER_CALC
    LATAM_PEAK --> BUFFER_CALC

    BUFFER_CALC --> SCALE_TRIGGERS
    SCALE_TRIGGERS --> COST_MODEL

    ML_PREDICT --> TRENDING
    TRENDING --> GLOBAL_POPULAR
    GLOBAL_POPULAR --> REGIONAL_POPULAR
    REGIONAL_POPULAR --> LONGTAIL

    %% Styling
    classDef peakStyle fill:#EF4444,stroke:#DC2626,color:#fff,stroke-width:2px
    classDef bufferStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px
    classDef contentStyle fill:#10B981,stroke:#047857,color:#fff,stroke-width:2px
    classDef predictStyle fill:#8B5CF6,stroke:#6D28D9,color:#fff,stroke-width:2px

    class US_PEAK,EU_PEAK,ASIA_PEAK,LATAM_PEAK peakStyle
    class BUFFER_CALC,SCALE_TRIGGERS,COST_MODEL bufferStyle
    class GLOBAL_POPULAR,REGIONAL_POPULAR,LONGTAIL contentStyle
    class ML_PREDICT,TRENDING predictStyle
```

## Capacity Scaling Scenarios

### Scenario 1: New Content Launch (Stranger Things)
- **Pre-launch**: 2 weeks content pre-positioning to all regions
- **Launch day**: 3x normal traffic expected, 2.5x capacity provisioned
- **Success metrics**: p99 latency < 100ms, 0% error rate increase
- **Cost impact**: +$2.3M for 72-hour surge period

### Scenario 2: Global Event (World Cup Final)
- **Pre-event**: +150% capacity in EU region (8 hours advance)
- **During event**: Real-time scaling based on concurrent users
- **Peak load**: 120M concurrent users globally
- **Infrastructure**: Emergency capacity from other regions

### Scenario 3: Regional Outage
- **Trigger**: AWS region failure affecting 30% of traffic
- **Response**: Automatic traffic rerouting within 90 seconds
- **Capacity**: Neighboring regions absorb +60% load
- **User impact**: <2% user-visible errors

## Cost-Performance Trade-offs

| Scenario | Infrastructure Cost | Performance Impact | Risk Level |
|----------|--------------------|--------------------|------------|
| **Baseline (1x)** | $15M/month | p99: 50ms | Low |
| **1.5x Buffer** | $22M/month | p99: 45ms | Very Low |
| **2x Emergency** | $30M/month | p99: 40ms | Minimal |
| **2.5x Max Surge** | $45M/month | p99: 35ms | None |

## Production Incidents & Lessons

### December 2021: European Traffic Surge
- **Issue**: Unexpected 4x traffic during regional lockdowns
- **Impact**: 15% of users experienced buffering for 45 minutes
- **Root cause**: Pre-positioning algorithm didn't account for lockdown patterns
- **Fix**: Added pandemic-specific demand modeling

### March 2022: Squid Game Global Phenomenon
- **Issue**: 10x normal traffic for specific content
- **Impact**: CDN cache miss rate increased to 15%
- **Solution**: Emergency content replication to all edge servers
- **Outcome**: Maintained service with 2-hour recovery

### October 2023: AWS US-East Outage
- **Issue**: Primary region hosting 40% of API services went down
- **Impact**: 2.3M users affected for 23 minutes
- **Recovery**: Automatic failover to secondary regions
- **Lesson**: Improved cross-region capacity buffers to 2x

## Auto-scaling Policies

### Predictive Scaling (30-minute horizon)
```yaml
triggers:
  content_launch:
    scale_factor: 2.5x
    lead_time: 2_hours
  regional_peak:
    scale_factor: 1.8x
    lead_time: 30_minutes
  weekend_pattern:
    scale_factor: 1.3x
    lead_time: 4_hours
```

### Reactive Scaling (2-5 minute response)
```yaml
metrics:
  cpu_utilization:
    threshold: 70%
    scale_out: +20%
  memory_utilization:
    threshold: 80%
    scale_out: +30%
  queue_depth:
    threshold: 100_requests
    scale_out: +50%
  error_rate:
    threshold: 1%
    scale_out: +25%
```

## Key Capacity Metrics

### Infrastructure Scale
- **Edge servers**: 15,000+ globally
- **Storage capacity**: 45 PB origin + 8.9 PB edge cache
- **Bandwidth capacity**: 3.5 Tbps peak (with buffers)
- **API capacity**: 600K RPS globally
- **Database capacity**: 2,500 Cassandra nodes, 50M ops/sec

### Performance Targets
- **Global p99 latency**: <100ms (achieved: 68ms average)
- **Availability**: 99.9% (achieved: 99.97%)
- **Content start time**: <3 seconds (achieved: 1.2s average)
- **Buffer health**: >95% (achieved: 97.8%)

### Cost Efficiency
- **CDN cost per GB**: $0.02 (industry: $0.05)
- **Compute cost per stream**: $0.004
- **Storage cost per TB/month**: $23
- **Total infrastructure**: $180M/year

This capacity model enables Netflix to serve 1 billion hours of content weekly while maintaining sub-100ms latencies globally and handling traffic surges up to 2.5x normal load.