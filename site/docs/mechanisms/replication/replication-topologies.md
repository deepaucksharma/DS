# Replication Topologies

## Primary-Secondary (Master-Slave) Topology

The most common replication pattern where one node accepts writes and replicates to read-only secondaries.

### Single Primary Architecture

```mermaid
graph TB
    subgraph "Primary-Secondary Topology"
        subgraph "Write Path"
            CLIENT_W[Write Clients]
            PRIMARY[Primary Node<br/>- Accepts all writes<br/>- Source of truth<br/>- Coordinates replication]
        end

        subgraph "Read Path"
            CLIENT_R[Read Clients]
            SECONDARY1[Secondary 1<br/>- Read-only replica<br/>- Async replication<br/>- Geographic: US-East]
            SECONDARY2[Secondary 2<br/>- Read-only replica<br/>- Async replication<br/>- Geographic: US-West]
            SECONDARY3[Secondary 3<br/>- Read-only replica<br/>- Sync replication<br/>- Failover candidate]
        end

        subgraph "Replication Flow"
            WAL[Write-Ahead Log]
            STREAM[Replication Stream]
        end
    end

    CLIENT_W --> PRIMARY
    PRIMARY --> WAL
    WAL --> STREAM

    STREAM --> SECONDARY1
    STREAM --> SECONDARY2
    STREAM --> SECONDARY3

    CLIENT_R --> SECONDARY1
    CLIENT_R --> SECONDARY2
    CLIENT_R --> SECONDARY3

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class CLIENT_W,CLIENT_R edgeStyle
    class PRIMARY serviceStyle
    class SECONDARY1,SECONDARY2,SECONDARY3,WAL,STREAM stateStyle
```

### Primary-Secondary with Automatic Failover

```mermaid
sequenceDiagram
    participant C as Clients
    participant LB as Load Balancer
    participant P as Primary
    participant S1 as Secondary 1
    participant S2 as Secondary 2
    participant MON as Monitor/Orchestrator

    Note over C,MON: Normal Operations

    C->>LB: Write Request
    LB->>P: Forward to Primary
    P->>S1: Replicate
    P->>S2: Replicate
    P->>LB: Success
    LB->>C: Response

    Note over C,MON: Primary Failure Detected

    MON->>P: Health Check
    P--X MON: No Response (failure)

    MON->>MON: Initiate Failover
    MON->>S1: Promote to Primary
    S1->>S1: Accept Write Role

    MON->>LB: Update Primary Endpoint
    LB->>LB: Route writes to S1

    Note over C,MON: Service Restored

    C->>LB: Write Request
    LB->>S1: Forward to New Primary
    S1->>S2: Replicate
    S1->>LB: Success
    LB->>C: Response

    Note over P: Old primary recovers as secondary
    MON->>P: Rejoin as Secondary
    P->>S1: Request replication stream
```

## Multi-Primary (Multi-Master) Topology

Multiple nodes can accept writes concurrently, requiring conflict resolution mechanisms.

### Active-Active Multi-Primary

```mermaid
graph TB
    subgraph "Multi-Primary Topology"
        subgraph "US-East Datacenter"
            CLIENT_US[US Clients]
            PRIMARY_US[Primary US<br/>- Local writes<br/>- Geographic partition<br/>- Conflict resolution]
        end

        subgraph "EU-West Datacenter"
            CLIENT_EU[EU Clients]
            PRIMARY_EU[Primary EU<br/>- Local writes<br/>- Geographic partition<br/>- Conflict resolution]
        end

        subgraph "Asia-Pacific Datacenter"
            CLIENT_AP[AP Clients]
            PRIMARY_AP[Primary AP<br/>- Local writes<br/>- Geographic partition<br/>- Conflict resolution]
        end

        subgraph "Cross-Region Replication"
            CONFLICT_RES[Conflict Resolution<br/>- Vector clocks<br/>- Last-writer-wins<br/>- Application merge]
            GOSSIP[Gossip Protocol<br/>- Change propagation<br/>- Failure detection<br/>- Membership]
        end
    end

    CLIENT_US --> PRIMARY_US
    CLIENT_EU --> PRIMARY_EU
    CLIENT_AP --> PRIMARY_AP

    PRIMARY_US <--> PRIMARY_EU
    PRIMARY_EU <--> PRIMARY_AP
    PRIMARY_AP <--> PRIMARY_US

    PRIMARY_US --> CONFLICT_RES
    PRIMARY_EU --> CONFLICT_RES
    PRIMARY_AP --> CONFLICT_RES

    CONFLICT_RES --> GOSSIP

    %% Apply colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class CLIENT_US,CLIENT_EU,CLIENT_AP edgeStyle
    class PRIMARY_US,PRIMARY_EU,PRIMARY_AP serviceStyle
    class CONFLICT_RES stateStyle
    class GOSSIP controlStyle
```

### Conflict Resolution in Multi-Primary

```mermaid
sequenceDiagram
    participant U1 as User 1 (US)
    participant P1 as Primary US
    participant P2 as Primary EU
    participant U2 as User 2 (EU)

    Note over U1,U2: Concurrent writes to same record

    U1->>P1: UPDATE user SET name='John' WHERE id=123
    U2->>P2: UPDATE user SET name='Jonathan' WHERE id=123

    P1->>P1: Apply locally (vector clock: US=5, EU=3)
    P2->>P2: Apply locally (vector clock: US=4, EU=6)

    Note over P1,P2: Cross-replication with conflict

    P1->>P2: Replicate: name='John', clock=(US=5, EU=3)
    P2->>P1: Replicate: name='Jonathan', clock=(US=4, EU=6)

    Note over P1,P2: Conflict Resolution

    P1->>P1: Compare vector clocks - concurrent update detected
    P2->>P2: Compare vector clocks - concurrent update detected

    alt Last-Writer-Wins (timestamp-based)
        P1->>P1: Keep 'Jonathan' (newer timestamp)
        P2->>P2: Keep 'Jonathan' (newer timestamp)
    else Application-Level Resolution
        P1->>P1: Merge: name='John Jonathan'
        P2->>P2: Merge: name='John Jonathan'
    else Manual Resolution Required
        P1->>P1: Flag for manual resolution
        P2->>P2: Flag for manual resolution
    end

    Note over P1,P2: Converged state achieved
```

## Chain Replication Topology

Linear chain of replicas where writes flow through the chain sequentially.

### Chain Replication Flow

```mermaid
graph LR
    subgraph "Chain Replication Architecture"
        CLIENT[Client]
        HEAD[Head Node<br/>- Receives writes<br/>- First in chain<br/>- Forwards to next]
        MIDDLE1[Middle Node 1<br/>- Processes in order<br/>- Forwards to next<br/>- Maintains state]
        MIDDLE2[Middle Node 2<br/>- Processes in order<br/>- Forwards to next<br/>- Maintains state]
        TAIL[Tail Node<br/>- Last in chain<br/>- Sends ack to client<br/>- Handles reads]

        subgraph "Chain Master"
            MASTER[Chain Master<br/>- Monitors health<br/>- Handles failures<br/>- Reconfigures chain]
        end
    end

    CLIENT -->|Write| HEAD
    HEAD --> MIDDLE1
    MIDDLE1 --> MIDDLE2
    MIDDLE2 --> TAIL
    TAIL -->|ACK| CLIENT

    CLIENT -->|Read| TAIL

    MASTER -.-> HEAD
    MASTER -.-> MIDDLE1
    MASTER -.-> MIDDLE2
    MASTER -.-> TAIL

    %% Apply colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class CLIENT edgeStyle
    class HEAD,MIDDLE1,MIDDLE2,TAIL serviceStyle
    class MASTER controlStyle
```

### Chain Failure Recovery

```mermaid
sequenceDiagram
    participant C as Client
    participant H as Head
    participant M1 as Middle 1
    participant M2 as Middle 2
    participant T as Tail
    participant CM as Chain Master

    Note over C,CM: Normal operation

    C->>H: Write Request
    H->>M1: Forward
    M1->>M2: Forward
    M2->>T: Forward
    T->>C: ACK

    Note over M1: Middle node 1 fails

    M1--X M2: Connection lost
    CM->>M1: Health check fails
    CM->>CM: Detect M1 failure

    Note over CM: Reconfigure chain (bypass M1)

    CM->>H: Update next = M2
    CM->>M2: Update prev = H

    Note over C,CM: Continue with shorter chain

    C->>H: Write Request
    H->>M2: Forward (skip M1)
    M2->>T: Forward
    T->>C: ACK

    Note over CM: M1 recovers and rejoins

    CM->>M1: Rejoin chain
    CM->>H: Update next = M1
    CM->>M1: Update next = M2
    CM->>M2: Update prev = M1
```

## Topology Selection Criteria

```mermaid
graph TB
    subgraph "Topology Decision Matrix"
        subgraph "Primary-Secondary Best For"
            PS_SIMPLE[Simple Consistency Model]
            PS_SINGLE[Single Write Region]
            PS_SCALE[Read Scaling]
            PS_FAILOVER[Automatic Failover]
        end

        subgraph "Multi-Primary Best For"
            MP_GLOBAL[Global Distribution]
            MP_LATENCY[Low Write Latency]
            MP_PARTITION[Partition Tolerance]
            MP_AVAILABILITY[High Availability]
        end

        subgraph "Chain Replication Best For"
            CR_ORDERED[Ordered Processing]
            CR_SIMPLE[Simple Protocol]
            CR_RECOVERY[Fast Recovery]
            CR_BROADCAST[Reliable Broadcast]
        end

        subgraph "Trade-offs"
            COMPLEXITY[Implementation Complexity<br/>Chain < Primary-Secondary < Multi-Primary]
            CONSISTENCY[Consistency Guarantees<br/>Chain = Primary-Secondary > Multi-Primary]
            AVAILABILITY[Availability<br/>Multi-Primary > Primary-Secondary > Chain]
            PERFORMANCE[Write Performance<br/>Multi-Primary > Primary-Secondary > Chain]
        end
    end

    %% Apply colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class PS_SIMPLE,PS_SINGLE,PS_SCALE,PS_FAILOVER edgeStyle
    class MP_GLOBAL,MP_LATENCY,MP_PARTITION,MP_AVAILABILITY serviceStyle
    class CR_ORDERED,CR_SIMPLE,CR_RECOVERY,CR_BROADCAST stateStyle
    class COMPLEXITY,CONSISTENCY,AVAILABILITY,PERFORMANCE controlStyle
```

## Real-World Topology Examples

### PostgreSQL Streaming Replication (Primary-Secondary)

```yaml
# PostgreSQL streaming replication configuration
postgresql_topology:
  primary:
    host: "pg-primary.internal"
    port: 5432
    configuration:
      wal_level: "replica"
      max_wal_senders: 10
      wal_keep_segments: 100
      synchronous_standby_names: "pg-standby-1"

  secondaries:
    - name: "pg-standby-1"
      host: "pg-standby-1.internal"
      type: "synchronous"
      lag_threshold: "1MB"

    - name: "pg-standby-2"
      host: "pg-standby-2.internal"
      type: "asynchronous"
      lag_threshold: "100MB"

    - name: "pg-standby-3"
      host: "pg-standby-3.internal"
      type: "asynchronous"
      geographic_location: "different_dc"
      lag_threshold: "500MB"

  failover:
    tool: "patroni"
    health_check_interval: "5s"
    failover_timeout: "30s"
    automatic: true
```

### CockroachDB Multi-Region (Multi-Primary)

```yaml
# CockroachDB multi-region configuration
cockroachdb_topology:
  regions:
    - name: "us-east1"
      zones: ["us-east1-a", "us-east1-b", "us-east1-c"]
      nodes: 3
      primary_for: ["users_east", "orders_east"]

    - name: "us-west1"
      zones: ["us-west1-a", "us-west1-b", "us-west1-c"]
      nodes: 3
      primary_for: ["users_west", "orders_west"]

    - name: "europe-west1"
      zones: ["europe-west1-a", "europe-west1-b", "europe-west1-c"]
      nodes: 3
      primary_for: ["users_eu", "orders_eu"]

  survival_goals:
    database: "region"
    tables:
      - name: "users"
        survival_goal: "zone"
        placement: "restricted"

      - name: "orders"
        survival_goal: "region"
        placement: "restricted"

  conflict_resolution:
    strategy: "timestamp_ordering"
    clock_skew_tolerance: "500ms"
```

### HDFS NameNode HA (Chain-like with Quorum)

```yaml
# HDFS NameNode High Availability
hdfs_topology:
  nameservice: "mycluster"
  namenodes:
    - id: "nn1"
      host: "namenode1.example.com"
      rpc_port: 8020
      http_port: 50070
      role: "active"

    - id: "nn2"
      host: "namenode2.example.com"
      rpc_port: 8020
      http_port: 50070
      role: "standby"

  journal_nodes:
    - host: "journalnode1.example.com"
      port: 8485
    - host: "journalnode2.example.com"
      port: 8485
    - host: "journalnode3.example.com"
      port: 8485

  automatic_failover:
    enabled: true
    zookeeper_quorum: "zk1:2181,zk2:2181,zk3:2181"
    failover_controller: "zkfc"

  shared_storage:
    type: "qjournal"
    journal_uri: "qjournal://journalnode1:8485;journalnode2:8485;journalnode3:8485/mycluster"
```

## Performance Characteristics

```mermaid
graph LR
    subgraph "Topology Performance Comparison"
        subgraph "Write Latency (p99)"
            PS_W_LAT["Primary-Secondary<br/>5-15ms<br/>(depends on sync mode)"]
            MP_W_LAT["Multi-Primary<br/>10-50ms<br/>(includes conflict resolution)"]
            CR_W_LAT["Chain Replication<br/>N × single_node_latency<br/>(proportional to chain length)"]
        end

        subgraph "Read Latency (p99)"
            PS_R_LAT["Primary-Secondary<br/>1-3ms<br/>(local reads from secondary)"]
            MP_R_LAT["Multi-Primary<br/>1-5ms<br/>(local reads, may need consensus)"]
            CR_R_LAT["Chain Replication<br/>1-3ms<br/>(reads from tail only)"]
        end

        subgraph "Throughput (writes/sec)"
            PS_THRU["Primary-Secondary<br/>Single primary bottleneck<br/>10,000-50,000 TPS"]
            MP_THRU["Multi-Primary<br/>Scales with regions<br/>100,000+ TPS total"]
            CR_THRU["Chain Replication<br/>Sequential processing<br/>5,000-20,000 TPS"]
        end
    end

    %% Apply state plane color for performance metrics
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    class PS_W_LAT,MP_W_LAT,CR_W_LAT,PS_R_LAT,MP_R_LAT,CR_R_LAT,PS_THRU,MP_THRU,CR_THRU stateStyle
```

## Monitoring and Alerting

```yaml
# Topology-specific monitoring
monitoring_by_topology:
  primary_secondary:
    metrics:
      - replication_lag_seconds
      - primary_availability
      - secondary_count_healthy
      - failover_time_seconds
    alerts:
      - name: "ReplicationLagHigh"
        condition: "lag > 10s"
        severity: "warning"
      - name: "PrimaryDown"
        condition: "primary_up == 0"
        severity: "critical"

  multi_primary:
    metrics:
      - conflict_resolution_rate
      - cross_region_latency
      - node_availability_per_region
      - consensus_time_p99
    alerts:
      - name: "HighConflictRate"
        condition: "conflicts/sec > 100"
        severity: "warning"
      - name: "RegionPartitioned"
        condition: "region_connectivity < 0.5"
        severity: "critical"

  chain_replication:
    metrics:
      - chain_length
      - head_to_tail_latency
      - node_position_in_chain
      - chain_reconfiguration_count
    alerts:
      - name: "ChainTooLong"
        condition: "chain_length > 5"
        severity: "warning"
      - name: "ChainBroken"
        condition: "chain_integrity == false"
        severity: "critical"
```

This comprehensive overview of replication topologies provides the foundation for choosing the right architecture based on consistency requirements, geographic distribution, and operational complexity.