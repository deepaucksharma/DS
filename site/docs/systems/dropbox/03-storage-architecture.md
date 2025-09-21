# Dropbox Storage Architecture

## Magic Pocket Custom Infrastructure

Dropbox's Magic Pocket represents the world's largest custom-built exabyte storage system, delivering 90% cost reduction compared to AWS S3 while maintaining 99.9999% durability and sub-second access times.

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Access Layer]
        API[Storage API Gateway<br/>Custom Protocol<br/>Load Balancing<br/>c5.9xlarge × 200]
        PROXY[Storage Proxy<br/>Request Routing<br/>Health Checking<br/>c5.4xlarge × 100]
    end

    subgraph ServicePlane[Service Plane - Storage Logic]
        COORD[Storage Coordinator<br/>Placement Decisions<br/>Replication Logic<br/>c5.12xlarge × 50]
        SHARD[Shard Manager<br/>Consistent Hashing<br/>Ring Management<br/>c5.4xlarge × 30]
        COMPACT[Compaction Service<br/>Garbage Collection<br/>Defragmentation<br/>c5.9xlarge × 20]
        REPAIR[Repair Service<br/>Integrity Checking<br/>Auto-healing<br/>c5.4xlarge × 15]
    end

    subgraph StatePlane[State Plane - Physical Storage]
        subgraph DC1[Data Center 1 - East Coast]
            MP1_RACK1[Magic Pocket Rack 1<br/>480× SMR Drives<br/>16TB each = 7.68PB<br/>Custom Rust Software]
            MP1_RACK2[Magic Pocket Rack 2<br/>480× SMR Drives<br/>16TB each = 7.68PB<br/>Erasure Coding]
            MP1_RACK3[Magic Pocket Rack 3<br/>480× SMR Drives<br/>16TB each = 7.68PB<br/>Local Replication]
            MP1_META[Metadata Cluster<br/>SSD-based<br/>Nucleus Integration<br/>r5.24xlarge × 20]
        end

        subgraph DC2[Data Center 2 - West Coast]
            MP2_RACK1[Magic Pocket Rack 1<br/>480× SMR Drives<br/>16TB each = 7.68PB<br/>Async Replication]
            MP2_RACK2[Magic Pocket Rack 2<br/>480× SMR Drives<br/>16TB each = 7.68PB<br/>Cross-region Backup]
            MP2_RACK3[Magic Pocket Rack 3<br/>480× SMR Drives<br/>16TB each = 7.68PB<br/>Disaster Recovery]
            MP2_META[Metadata Cluster<br/>SSD-based<br/>Cross-DC Sync<br/>r5.24xlarge × 20]
        end

        subgraph DC3[Data Center 3 - Europe]
            MP3_RACK1[Magic Pocket Rack 1<br/>480× SMR Drives<br/>16TB each = 7.68PB<br/>GDPR Compliance]
            MP3_RACK2[Magic Pocket Rack 2<br/>480× SMR Drives<br/>16TB each = 7.68PB<br/>Local Regulations]
            MP3_META[Metadata Cluster<br/>SSD-based<br/>Regional Isolation<br/>r5.24xlarge × 15]
        end
    end

    subgraph ControlPlane[Control Plane - Storage Management]
        MONITOR[Storage Monitoring<br/>Drive Health Tracking<br/>Performance Metrics<br/>c5.2xlarge × 10]
        BALANCE[Load Balancer<br/>Shard Distribution<br/>Hot Spot Detection<br/>c5.2xlarge × 5]
        BACKUP[Backup Controller<br/>Cross-DC Replication<br/>Point-in-time Recovery<br/>c5.4xlarge × 8]
        PROVISION[Auto-provisioning<br/>Capacity Planning<br/>Hardware Lifecycle<br/>c5.2xlarge × 3]
    end

    %% Request Flow
    API --> PROXY
    PROXY --> COORD
    COORD --> SHARD

    %% Storage Operations
    SHARD --> MP1_RACK1
    SHARD --> MP1_RACK2
    SHARD --> MP1_RACK3
    SHARD --> MP2_RACK1
    SHARD --> MP3_RACK1

    %% Metadata Management
    COORD --> MP1_META
    COORD --> MP2_META
    COORD --> MP3_META

    %% Background Operations
    COMPACT --> MP1_RACK1
    COMPACT --> MP2_RACK1
    REPAIR --> MP1_RACK2
    REPAIR --> MP2_RACK2

    %% Cross-DC Replication
    MP1_RACK1 -.-> MP2_RACK1
    MP1_RACK2 -.-> MP3_RACK1
    MP2_RACK1 -.-> MP3_RACK2

    %% Metadata Synchronization
    MP1_META -.-> MP2_META
    MP2_META -.-> MP3_META
    MP1_META -.-> MP3_META

    %% Control Plane Monitoring
    MONITOR --> MP1_RACK1
    MONITOR --> MP2_RACK1
    MONITOR --> MP3_RACK1
    BALANCE --> SHARD
    BACKUP --> MP1_META
    PROVISION --> COORD

    %% Apply four-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff,stroke-width:2px
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff,stroke-width:2px
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff,stroke-width:2px
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff,stroke-width:2px

    class API,PROXY edgeStyle
    class COORD,SHARD,COMPACT,REPAIR serviceStyle
    class MP1_RACK1,MP1_RACK2,MP1_RACK3,MP2_RACK1,MP2_RACK2,MP2_RACK3,MP3_RACK1,MP3_RACK2,MP1_META,MP2_META,MP3_META stateStyle
    class MONITOR,BALANCE,BACKUP,PROVISION controlStyle
```

## Storage Architecture Specifications

### Magic Pocket Hardware Design

| Component | Specification | Scale | Purpose |
|-----------|---------------|-------|---------|
| **SMR Drives** | 16TB Shingled Magnetic Recording | 10,000+ drives | High-density storage |
| **Storage Nodes** | Custom-built servers | 480 drives per rack | Cost optimization |
| **Network** | 100Gbps per rack | Redundant switches | High throughput |
| **Power** | Custom PDU design | 50% power reduction | Energy efficiency |

### Data Placement Strategy

```mermaid
graph LR
    subgraph FileIngestion[File Ingestion Process]
        FILE[Original File<br/>100MB example]
        CHUNK[Block Chunking<br/>4MB blocks × 25]
        HASH[Content Hashing<br/>SHA256 per block]
        DEDUP[Global Deduplication<br/>95% hit rate]
    end

    subgraph PlacementLogic[Placement Logic]
        RING[Consistent Hash Ring<br/>10,000 virtual nodes]
        REPLICA[3× Replication<br/>Different failure domains]
        ERASURE[Erasure Coding<br/>6+3 for cold data]
        LOCALITY[Data Locality<br/>Geographic placement]
    end

    subgraph PhysicalStorage[Physical Storage]
        PRIMARY[Primary Copy<br/>Local SSD cache<br/>Sub-ms access]
        SECONDARY[Secondary Copy<br/>Different rack<br/>Same datacenter]
        TERTIARY[Tertiary Copy<br/>Different datacenter<br/>Async replication]
        COLD[Cold Storage<br/>Erasure coded<br/>Long-term retention]
    end

    FILE --> CHUNK
    CHUNK --> HASH
    HASH --> DEDUP
    DEDUP --> RING
    RING --> REPLICA
    REPLICA --> ERASURE
    ERASURE --> LOCALITY
    LOCALITY --> PRIMARY
    LOCALITY --> SECONDARY
    LOCALITY --> TERTIARY
    LOCALITY --> COLD

    classDef processStyle fill:#E1F5FE,stroke:#0277BD,color:#000
    classDef logicStyle fill:#F3E5F5,stroke:#7B1FA2,color:#000
    classDef storageStyle fill:#FFF3E0,stroke:#F57C00,color:#000

    class FILE,CHUNK,HASH,DEDUP processStyle
    class RING,REPLICA,ERASURE,LOCALITY logicStyle
    class PRIMARY,SECONDARY,TERTIARY,COLD storageStyle
```

## Storage Performance Metrics

| Metric | Value | Comparison | Notes |
|--------|-------|------------|-------|
| **Total Capacity** | Exabytes | 10× larger than Netflix | Custom SMR drives |
| **Durability** | 99.9999% | Same as AWS S3 | 3× replication + erasure |
| **Access Latency** | <1 second | 90% faster than tape | SSD caching layer |
| **Cost per GB** | 90% reduction | vs AWS S3 | Custom hardware ROI |
| **Bandwidth** | 100GB/s per rack | Sustained throughput | Parallel I/O design |

## Data Consistency Model

### Write Path Consistency
```
1. Client writes block → Storage Coordinator
2. Coordinator selects 3 replicas (different failure domains)
3. Parallel writes to all 3 replicas
4. Success requires 2/3 acknowledgments (quorum)
5. Metadata updated atomically in Nucleus
6. Background repair ensures 3× replication
```

### Read Path Optimization
```
1. Read request → Check SSD cache (90% hit rate)
2. Cache miss → Query 3 replicas in parallel
3. Return from fastest responding replica
4. Background prefetch for related blocks
5. Update cache with read-ahead data
```

## Storage Economics

### Infrastructure Cost Breakdown
- **Hardware**: 60% - Custom servers and drives
- **Power**: 20% - 50% reduction vs traditional
- **Cooling**: 10% - Efficient datacenter design
- **Network**: 5% - Custom interconnect
- **Personnel**: 5% - Automation reduces ops

### Cost Comparison (per TB/month)
- **AWS S3 Standard**: $23/TB/month
- **Magic Pocket**: $2.3/TB/month (90% savings)
- **Break-even**: 18 months for hardware ROI
- **Annual Savings**: $500M+ at current scale

## Reliability Engineering

### Failure Domain Isolation
- **Drive Level**: RAID-like protection within node
- **Node Level**: Multiple nodes per rack
- **Rack Level**: Cross-rack replication
- **Datacenter Level**: Cross-DC async replication
- **Region Level**: Geographic distribution

### Auto-Healing Mechanisms
- **Drive Failure**: Auto-detect and rebuild (1 hour)
- **Node Failure**: Migrate shards to healthy nodes
- **Rack Failure**: Cross-rack replica activation
- **Datacenter Failure**: Promote secondary DC
- **Data Corruption**: Checksum validation and repair

*Source: Dropbox Magic Pocket Technical Papers, Infrastructure Engineering Blog, USENIX FAST Papers*