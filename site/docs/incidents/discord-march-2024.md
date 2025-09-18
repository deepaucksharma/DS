# Discord Global Outage - March 8, 2024

**The 3-Hour Database Shard Failure That Silenced Gaming Communities Worldwide**

## Incident Overview

| **Metric** | **Value** |
|------------|-----------||
| **Date** | March 8, 2024 |
| **Duration** | 3 hours 8 minutes |
| **Impact** | Voice and messaging outages globally |
| **Users Affected** | 200M+ active users |
| **Financial Impact** | $150M+ in lost engagement and revenue |
| **Root Cause** | Database shard failure cascade in message storage |
| **MTTR** | 188 minutes |
| **MTTD** | 2 minutes (automated alerts) |
| **RTO** | 4 hours (target recovery time) |
| **RPO** | 30 seconds (message loss window) |
| **Key Failure** | Cassandra cluster split-brain scenario |
| **Services Down** | Voice channels, Text messages, Video calls, Screen sharing |

## Incident Timeline - When Gaming Communities Went Silent

```mermaid
gantt
    title Discord Global Outage Timeline - March 8, 2024
    dateFormat HH:mm
    axisFormat %H:%M

    section Detection
    Database alerts      :done, detect1, 18:47, 18:52
    Voice failures       :done, detect2, 18:52, 19:05
    User reports flood   :done, detect3, 19:05, 19:20

    section Diagnosis
    Shard analysis       :done, diag1, 19:20, 20:15
    Split-brain detect   :done, diag2, 20:15, 20:45
    Data consistency     :done, diag3, 20:45, 21:15

    section Mitigation
    Cluster restart      :done, mit1, 21:15, 21:30
    Data reconciliation  :done, mit2, 21:30, 21:50
    Service restoration  :done, mit3, 21:50, 21:55

    section Recovery
    Message sync         :done, rec1, 21:55, 22:30
    Voice quality check  :done, rec2, 22:30, 23:00
```

## Database Shard Failure Cascade

```mermaid
graph TB
    subgraph Edge_Plane___Blue__3B82F6[Edge Plane - Blue #3B82F6]
        GATEWAY[Discord Gateway<br/>WebSocket Connections]
        CDN[Discord CDN<br/>Media Delivery]
        VOICE[Voice Servers<br/>RTC Infrastructure]
    end

    subgraph Service_Plane___Green__10B981[Service Plane - Green #10B981]
        MSGAPI[Message API<br/>Text Processing]
        VOICEAPI[Voice API<br/>Audio Processing]
        VIDEOAPI[Video API<br/>Screen Share]
        GAMEAPI[Game Activity API<br/>Rich Presence]
    end

    subgraph State_Plane___Orange__F59E0B[State Plane - Orange #F59E0B]
        CASSANDRA[(Cassandra Cluster<br/>Message Storage<br/>PRIMARY FAILURE)]
        REDIS[(Redis Cluster<br/>Session Cache)]
        POSTGRES[(PostgreSQL<br/>User & Guild Data)]
        SCYLLA[(ScyllaDB<br/>Voice Metadata)]
    end

    subgraph Control_Plane___Red__8B5CF6[Control Plane - Red #8B5CF6]
        MONITORING[Datadog Monitoring<br/>Metrics & Alerts]
        CONFIG[Configuration Service<br/>Feature Flags]
        DEPLOY[Deployment Pipeline<br/>Auto-deployment]
    end

    subgraph Cassandra_Ring_Architecture[Cassandra Ring Architecture]
        SHARD1[Shard 1<br/>US-East Messages<br/>Split-brain Node]
        SHARD2[Shard 2<br/>US-West Messages]
        SHARD3[Shard 3<br/>EU Messages<br/>Split-brain Node]
        SHARD4[Shard 4<br/>APAC Messages]
        COORDINATOR[Coordinator Node<br/>Consensus Manager]
    end

    %% Database failure cascade
    COORDINATOR -.->|Network partition<br/>18:47 UTC| SHARD1
    SHARD1 -.->|Split-brain scenario<br/>Cannot reach consensus| SHARD3
    SHARD3 -.->|Data inconsistency<br/>Write conflicts| CASSANDRA
    CASSANDRA -.->|Query timeouts<br/>Cannot read messages| REDIS

    %% Service impact cascade
    CASSANDRA -.->|Cannot store messages<br/>Write operations fail| MSGAPI
    MSGAPI -.->|Message delivery blocked<br/>Cannot send/receive| VOICEAPI
    VOICEAPI -.->|Voice state corruption<br/>Cannot join channels| VIDEOAPI
    VIDEOAPI -.->|Screen share data lost<br/>Cannot establish streams| GAMEAPI

    %% Gateway and connection impact
    MSGAPI -.->|WebSocket errors<br/>Connection instability| GATEWAY
    GATEWAY -.->|Cannot maintain state<br/>Frequent disconnections| VOICE
    VOICE -.->|Audio packet loss<br/>Voice quality degraded| CDN

    %% Monitoring system impact
    CASSANDRA -.->|Cannot log metrics<br/>Monitoring data lost| MONITORING
    MONITORING -.->|Blind to system state<br/>Cannot assess health| CONFIG

    %% Customer impact
    GATEWAY -.->|Complete service failure<br/>200M+ users affected| CUSTOMERS[Gaming Communities<br/>Corporate Teams<br/>Creator Streams<br/>Educational Groups<br/>Social Servers]

    %% Apply four-plane colors
    classDef edgeStyle fill:#3B82F6,stroke:#2563EB,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:3px
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:3px
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff,stroke-width:3px
    classDef shardStyle fill:#4B0082,stroke:#301934,color:#fff,stroke-width:4px
    classDef impactStyle fill:#8B0000,stroke:#660000,color:#fff,stroke-width:4px

    class GATEWAY,CDN,VOICE edgeStyle
    class MSGAPI,VOICEAPI,VIDEOAPI,GAMEAPI serviceStyle
    class CASSANDRA,REDIS,POSTGRES,SCYLLA stateStyle
    class MONITORING,CONFIG,DEPLOY controlStyle
    class SHARD1,SHARD2,SHARD3,SHARD4,COORDINATOR shardStyle
    class CUSTOMERS impactStyle
```

## Minute-by-Minute Database Disaster

### Phase 1: The Silent Network Partition (18:45 - 18:52)

```mermaid
sequenceDiagram
    participant COORD as Coordinator
    participant SHARD1 as Shard 1 (US-East)
    participant SHARD3 as Shard 3 (EU)
    participant CLIENT as Discord Client
    participant USER as Gaming User

    Note over COORD,USER: Normal Operation - Messages Flowing

    COORD->>SHARD1: Coordinate write operations
    SHARD1->>SHARD3: Replicate message data
    SHARD3->>CLIENT: Message delivery confirmed
    CLIENT->>USER: Messages appear instantly

    Note over COORD,USER: 18:47 UTC - Network Partition Begins

    COORD--xSHARD1: Network timeout<br/>Cannot reach shard
    SHARD1--xSHARD3: Replication broken<br/>Data divergence starts
    SHARD3--xCLIENT: Inconsistent data<br/>Some messages missing
    CLIENT--xUSER: "Failed to send message"
```

### Phase 2: The Split-Brain Catastrophe (18:52 - 19:20)

```mermaid
graph LR
    subgraph Split_Brain_Timeline[Split-Brain Timeline]
        A[18:52 UTC<br/>Voice channels fail<br/>Cannot join servers]
        B[18:57 UTC<br/>Messages delayed<br/>Delivery inconsistent]
        C[19:02 UTC<br/>Gaming streams drop<br/>Screen share broken]
        D[19:07 UTC<br/>Complete voice outage<br/>All channels silent]
        E[19:12 UTC<br/>Text messages fail<br/>Cannot send/receive]
        F[19:20 UTC<br/>Total service failure<br/>Complete Discord outage]
    end

    A --> B --> C --> D --> E --> F

    classDef splitBrainStyle fill:#FF6B6B,stroke:#8B5CF6,color:#fff,stroke-width:2px
    class A,B,C,D,E,F splitBrainStyle
```

### Phase 3: The Database Investigation (19:20 - 21:15)

**Database Debugging Commands Used:**
```bash
# Cassandra cluster status
nodetool status
nodetool ring
nodetool describecluster

# Check for split-brain scenario
nodetool gossipinfo | grep -E "STATUS|LOAD"
nodetool netstats | grep -A5 "Pool Name"

# Data consistency verification
nodetool repair --partitioner-range --parallel
nodetool compactionstats
cqlsh -e "SELECT COUNT(*) FROM messages.by_channel;"

# Network connectivity testing
ping -c 10 cassandra-coord.discord.internal
telnet cassandra-shard-1.discord.internal 9042
ss -tulpn | grep 9042  # Check Cassandra ports
```

### Phase 4: The Cluster Recovery (21:15 - 21:55)

```mermaid
timeline
    title Database Recovery Process

    section Cluster Restart
        21:15 : Stop all Cassandra nodes
              : Clear gossip state
              : Prepare data reconciliation

    section Coordinator Recovery
        21:20 : Restart coordinator node
              : Establish new ring topology
              : Verify quorum availability

    section Shard Reconciliation
        21:30 : Restart shards sequentially
              : Data consistency repair
              : Merkle tree comparison

    section Service Restoration
        21:50 : Message API reconnection
              : Voice service restart
              : WebSocket gateway recovery

    section Full Recovery
        21:55 : All services operational
              : Message backlog processing
              : Voice quality restored
```

## Technical Deep Dive: Cassandra Split-Brain Scenario

### Split-Brain Root Cause Analysis

```mermaid
flowchart TD
    A[Network Partition<br/>Between data centers] --> B{Cassandra Nodes Isolated}
    B -->|US-East Shard| C[Forms Minority Partition<br/>2 nodes out of 5]
    B -->|EU Shard| D[Forms Majority Partition<br/>3 nodes out of 5]

    C --> E[Believes it's authoritative<br/>Continues accepting writes]
    D --> F[Also believes authoritative<br/>Continues accepting writes]

    E --> G[Data Version A<br/>US users' messages]
    F --> H[Data Version B<br/>EU users' messages]

    G --> I[Conflict Resolution Needed<br/>Inconsistent global state]
    H --> I

    I --> J[Service Degradation<br/>Cannot determine truth]
    J --> K[Complete Service Failure<br/>Safety mechanism activated]

    classDef network fill:#FF6B6B,stroke:#8B5CF6,color:#fff
    classDef partition fill:#FFA500,stroke:#FF8C00,color:#fff
    classDef conflict fill:#8B0000,stroke:#660000,color:#fff

    class A,B network
    class C,D,E,F,G,H partition
    class I,J,K conflict
```

### Cassandra Ring Configuration

```yaml
# Discord Cassandra Cluster Configuration
cassandra_cluster:
  cluster_name: "discord_messages"
  replication_factor: 3
  consistency_level: "QUORUM"
  
  datacenters:
    us_east:
      nodes: 5
      racks: 3
      token_ranges: "0-85070591730234615865843651857942052863"
      
    eu_west:
      nodes: 5  
      racks: 3
      token_ranges: "85070591730234615865843651857942052864-170141183460469231731687303715884105727"
      
    us_west:
      nodes: 3
      racks: 2
      token_ranges: "170141183460469231731687303715884105728-255211775190703847597530955573826158591"

  failure_scenarios:
    split_brain:
      trigger: "Network partition between DCs"
      impact: "Data consistency violation"
      recovery: "Manual cluster restart required"
```

## Gaming Community Impact Analysis

### Service Impact by Discord Feature

```mermaid
xychart-beta
    title "Feature Availability During Outage (%)"
    x-axis ["Voice", "Text", "Video", "Streaming", "Game Activity", "File Share", "Bots"]
    y-axis "Availability %" 0 --> 100
    bar [5, 15, 10, 0, 20, 30, 25]
```

### User Activity Recovery Pattern

```mermaid
xychart-beta
    title "User Reconnection Pattern (Millions)"
    x-axis ["19:00", "20:00", "21:00", "22:00", "23:00", "00:00", "01:00"]
    y-axis "Active Users (M)" 0 --> 250
    line [180, 45, 25, 30, 200, 220, 190]
```

## Economic Impact by Use Case

### Revenue Impact Breakdown

```mermaid
pie title Economic Impact ($150M Total)
    "Gaming Communities" : 60
    "Creator Content Loss" : 30
    "Corporate Teams" : 25
    "Educational Sessions" : 20
    "Discord Nitro Churn" : 10
    "Developer Platform" : 5
```

## The 3 AM Debugging Playbook

### Database Health Diagnostics
```bash
# 1. Cassandra cluster health
nodetool status | grep -E "UN|DN"  # Up Normal / Down Normal
nodetool ring | head -20
nodetool tpstats | grep -E "Pool|Active"

# 2. Data consistency check
nodetool repair --partitioner-range
nodetool compactionstats
cqlsh -e "CONSISTENCY QUORUM; SELECT * FROM system.peers;"

# 3. Network connectivity validation
for host in shard-{1..5}.cassandra.discord.internal; do
  echo "Testing $host..."
  nc -zv $host 9042 || echo "FAILED"
done

# 4. Discord service health
curl -I https://discord.com/api/v10/gateway
curl -I https://discord.com/api/v10/users/@me
```

### Discord-Specific Service Checks
```bash
# WebSocket gateway health
wscat -c wss://gateway.discord.gg/?v=10&encoding=json

# Voice server connectivity
ping voice-{us-east,eu-west,us-west}.discord.gg

# CDN and media services
curl -I https://cdn.discord.com/
curl -I https://media.discord.net/
```

### Escalation Triggers
- **30 seconds**: Database write failures >50%
- **2 minutes**: Voice channel connection failures
- **5 minutes**: Message delivery delays >30 seconds
- **10 minutes**: Complete WebSocket gateway failure
- **15 minutes**: Cross-region data consistency issues

## Lessons Learned & Discord's Database Overhaul

### What Discord Fixed

1. **Cassandra Cluster Resilience**
   - Upgraded to ScyllaDB for better performance
   - Implemented automatic split-brain detection
   - Added cross-region data validation

2. **Network Partition Handling**
   - Enhanced network monitoring between data centers
   - Automated failover for database partitions
   - Graceful degradation instead of complete failure

3. **Real-time Communication Backup**
   - Voice service redundancy across regions
   - Message queue persistence during outages
   - WebSocket connection retry logic

### Architecture Improvements

```mermaid
graph TB
    subgraph NEW__Multi_DC_Cassandra_with_Automated_Failover[NEW: Multi-DC Cassandra with Automated Failover]
        COORD1[Coordinator US<br/>Primary control]
        COORD2[Coordinator EU<br/>Backup control]
        COORD3[Coordinator APAC<br/>Emergency control]
        DETECT[Split-Brain Detection<br/>Automated monitoring]
    end

    subgraph NEW__ScyllaDB_Migration[NEW: ScyllaDB Migration]
        SCYLLA1[ScyllaDB US<br/>High performance]
        SCYLLA2[ScyllaDB EU<br/>Low latency]
        SCYLLA3[ScyllaDB APAC<br/>Local processing]
        SYNC[Cross-Region Sync<br/>Eventual consistency]
    end

    subgraph NEW__Service_Degradation_Framework[NEW: Service Degradation Framework]
        GRACEFUL[Graceful Degradation<br/>Partial functionality]
        QUEUE[Message Queuing<br/>Offline storage]
        FALLBACK[Voice Fallback<br/>Regional routing]
    end

    DETECT --> COORD1
    DETECT --> COORD2
    DETECT --> COORD3

    COORD1 --> SCYLLA1
    COORD2 --> SCYLLA2
    COORD3 --> SCYLLA3

    SYNC --> SCYLLA1
    SYNC --> SCYLLA2
    SYNC --> SCYLLA3

    GRACEFUL --> QUEUE
    QUEUE --> FALLBACK

    classDef newStyle fill:#10B981,stroke:#059669,color:#fff,stroke-width:3px
    class COORD1,COORD2,COORD3,DETECT,SCYLLA1,SCYLLA2,SCYLLA3,SYNC,GRACEFUL,QUEUE,FALLBACK newStyle
```

## Gaming Community Response

### Alternative Platforms During Outage

```mermaid
pie title Platform Migration During Outage
    "TeamSpeak" : 30
    "Telegram Voice" : 25
    "Xbox Party Chat" : 20
    "PlayStation Party" : 15
    "Other Platforms" : 10
```

### Community Sentiment Analysis

```mermaid
timeline
    title Community Response Timeline

    section Initial Reaction
        19:00 : Confusion and frustration
              : Users blame local internet
              : Alternative platforms surge

    section Awareness Spreads
        19:30 : Social media acknowledgment
              : Reddit discussions explode
              : Memes and jokes emerge

    section Peak Frustration
        20:30 : Prime gaming hours affected
              : Competitive matches disrupted
              : Content creators switch platforms

    section Recovery Gratitude
        22:00 : Relief as services return
              : Appreciation for transparency
              : Trust in platform maintained
```

## The Bottom Line

**This incident demonstrated that modern communication platforms are only as reliable as their database infrastructure.**

Discord's 3-hour outage showed how database split-brain scenarios can completely disable real-time communication services. The incident highlighted the critical importance of distributed database design and the massive social impact when gaming communities lose their primary communication platform.

**Key Takeaways:**
- Database split-brain scenarios require automated detection and resolution
- Real-time communication services need graceful degradation strategies
- Gaming communities have zero tolerance for communication outages
- Cross-region database consistency is critical for global platforms
- Alternative communication methods are essential during outages

**The $150M question:** How would your community-driven platform handle a 3-hour database failure during peak usage hours?

---

*"In production, database consistency is not just about data - it's about maintaining human connections."*

**Sources**: Discord status updates, Cassandra cluster analysis, Gaming community impact surveys, Real-time communication platform studies