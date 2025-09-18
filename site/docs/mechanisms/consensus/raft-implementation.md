# Raft Production Implementations

## etcd - The Kubernetes Backbone

etcd implements Raft to provide the distributed key-value store that powers Kubernetes cluster state.

### etcd Raft Architecture

```mermaid
graph TB
    subgraph "etcd Cluster (3 nodes)"
        subgraph "etcd-1 (Leader)"
            RAFT1[Raft Module]
            STORE1[MVCC Store]
            API1[gRPC API]
        end

        subgraph "etcd-2 (Follower)"
            RAFT2[Raft Module]
            STORE2[MVCC Store]
            API2[gRPC API]
        end

        subgraph "etcd-3 (Follower)"
            RAFT3[Raft Module]
            STORE3[MVCC Store]
            API3[gRPC API]
        end
    end

    subgraph "Kubernetes Control Plane"
        KAPI[kube-apiserver]
        SCHED[kube-scheduler]
        CM[kube-controller-manager]
    end

    subgraph "Client Applications"
        CLIENT1[kubectl]
        CLIENT2[Custom Operators]
        CLIENT3[Monitoring Tools]
    end

    %% Client connections
    CLIENT1 --> KAPI
    CLIENT2 --> KAPI
    CLIENT3 --> KAPI

    %% Kubernetes components to etcd
    KAPI --> API1
    SCHED --> API1
    CM --> API1

    %% Raft replication
    RAFT1 <--> RAFT2
    RAFT1 <--> RAFT3
    RAFT2 <--> RAFT3

    %% Internal connections
    API1 --> RAFT1
    RAFT1 --> STORE1
    API2 --> RAFT2
    RAFT2 --> STORE2
    API3 --> RAFT3
    RAFT3 --> STORE3

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class CLIENT1,CLIENT2,CLIENT3 edgeStyle
    class KAPI,SCHED,CM,API1,API2,API3 serviceStyle
    class STORE1,STORE2,STORE3 stateStyle
    class RAFT1,RAFT2,RAFT3 controlStyle
```

### etcd Configuration (Production)

```yaml
# /etc/etcd/etcd.conf
name: etcd-1
data-dir: /var/lib/etcd
wal-dir: /var/lib/etcd/wal

# Cluster configuration
initial-advertise-peer-urls: https://10.0.1.10:2380
listen-peer-urls: https://10.0.1.10:2380
listen-client-urls: https://10.0.1.10:2379,https://127.0.0.1:2379
advertise-client-urls: https://10.0.1.10:2379
initial-cluster: etcd-1=https://10.0.1.10:2380,etcd-2=https://10.0.1.11:2380,etcd-3=https://10.0.1.12:2380
initial-cluster-state: new
initial-cluster-token: etcd-cluster-1

# Raft timing (production tuned)
heartbeat-interval: 100
election-timeout: 1000

# Performance tuning
quota-backend-bytes: 8589934592  # 8GB
auto-compaction-retention: 1h
max-request-bytes: 1572864       # 1.5MB
grpc-keepalive-min-time: 5s
grpc-keepalive-interval: 2h
grpc-keepalive-timeout: 20s

# Security
cert-file: /etc/etcd/server.crt
key-file: /etc/etcd/server.key
peer-cert-file: /etc/etcd/peer.crt
peer-key-file: /etc/etcd/peer.key
trusted-ca-file: /etc/etcd/ca.crt
peer-trusted-ca-file: /etc/etcd/ca.crt
```

### Consul - Service Discovery with Raft

Consul uses Raft for its service catalog and key-value store, providing service discovery and configuration.

### Consul Raft Architecture

```mermaid
graph TB
    subgraph "Consul Datacenter"
        subgraph "Server Nodes (Raft Cluster)"
            subgraph "consul-1 (Leader)"
                LEADER[Raft Leader]
                KV1[KV Store]
                CATALOG1[Service Catalog]
                DNS1[DNS Interface]
                HTTP1[HTTP API]
            end

            subgraph "consul-2 (Follower)"
                FOLLOWER1[Raft Follower]
                KV2[KV Store]
                CATALOG2[Service Catalog]
                DNS2[DNS Interface]
                HTTP2[HTTP API]
            end

            subgraph "consul-3 (Follower)"
                FOLLOWER2[Raft Follower]
                KV3[KV Store]
                CATALOG3[Service Catalog]
                DNS3[DNS Interface]
                HTTP3[HTTP API]
            end
        end

        subgraph "Client Nodes"
            CLIENT1[consul-client-1]
            CLIENT2[consul-client-2]
            CLIENT3[consul-client-3]
        end

        subgraph "Services"
            WEB[Web Service]
            API[API Service]
            DB[Database Service]
        end
    end

    %% Service registration
    WEB --> CLIENT1
    API --> CLIENT2
    DB --> CLIENT3

    %% Client to server communication
    CLIENT1 --> LEADER
    CLIENT2 --> LEADER
    CLIENT3 --> LEADER

    %% Raft consensus
    LEADER <--> FOLLOWER1
    LEADER <--> FOLLOWER2
    FOLLOWER1 <--> FOLLOWER2

    %% Internal connections
    LEADER --> KV1
    LEADER --> CATALOG1
    FOLLOWER1 --> KV2
    FOLLOWER1 --> CATALOG2
    FOLLOWER2 --> KV3
    FOLLOWER2 --> CATALOG3

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class WEB,API,DB,CLIENT1,CLIENT2,CLIENT3 edgeStyle
    class DNS1,DNS2,DNS3,HTTP1,HTTP2,HTTP3 serviceStyle
    class KV1,KV2,KV3,CATALOG1,CATALOG2,CATALOG3 stateStyle
    class LEADER,FOLLOWER1,FOLLOWER2 controlStyle
```

### Consul Configuration (Production)

```hcl
# /etc/consul/consul.hcl
datacenter = "dc1"
data_dir = "/opt/consul"
log_level = "INFO"
node_name = "consul-1"
bind_addr = "10.0.1.10"
client_addr = "0.0.0.0"

# Server mode with Raft
server = true
bootstrap_expect = 3
retry_join = ["10.0.1.11", "10.0.1.12"]

# Raft performance tuning
raft_protocol = 3
raft_snapshot_threshold = 8192
raft_snapshot_interval = "5s"
raft_trailing_logs = 10000

# Performance
performance {
  raft_multiplier = 1
}

# Connect for service mesh
connect {
  enabled = true
}

# TLS configuration
verify_incoming = true
verify_outgoing = true
verify_server_hostname = true
ca_file = "/etc/consul/ca.pem"
cert_file = "/etc/consul/consul.pem"
key_file = "/etc/consul/consul-key.pem"

# Monitoring
telemetry {
  prometheus_retention_time = "24h"
  disable_hostname = false
}
```

### CockroachDB - Distributed SQL with Raft

CockroachDB uses Raft for replicating ranges of data across multiple nodes.

### CockroachDB Raft per Range

```mermaid
graph TB
    subgraph "CockroachDB Cluster"
        subgraph "Node 1"
            R1_1[Range 1 Replica]
            R2_1[Range 2 Replica]
            R3_1[Range 3 Replica]
            SQL1[SQL Layer]
        end

        subgraph "Node 2"
            R1_2[Range 1 Replica]
            R2_2[Range 2 Replica]
            R4_2[Range 4 Replica]
            SQL2[SQL Layer]
        end

        subgraph "Node 3"
            R1_3[Range 1 Replica]
            R3_3[Range 3 Replica]
            R4_3[Range 4 Replica]
            SQL3[SQL Layer]
        end
    end

    subgraph "Range 1 Raft Group"
        R1_1 <--> R1_2
        R1_1 <--> R1_3
        R1_2 <--> R1_3
    end

    subgraph "Range 2 Raft Group"
        R2_1 <--> R2_2
    end

    subgraph "Range 3 Raft Group"
        R3_1 <--> R3_3
    end

    subgraph "Range 4 Raft Group"
        R4_2 <--> R4_3
    end

    subgraph "Client Applications"
        APP1[Application 1]
        APP2[Application 2]
    end

    APP1 --> SQL1
    APP2 --> SQL2

    %% Apply 4-plane colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class APP1,APP2 edgeStyle
    class SQL1,SQL2,SQL3 serviceStyle
    class R1_1,R1_2,R1_3,R2_1,R2_2,R3_1,R3_3,R4_2,R4_3 stateStyle
```

### Performance Comparison

```mermaid
graph LR
    subgraph "Production Raft Performance"
        subgraph "etcd (Kubernetes)"
            ETCD_TPS["10,000 writes/sec"]
            ETCD_LAT["< 10ms p99"]
            ETCD_SIZE["8GB recommended"]
        end

        subgraph "Consul (Service Discovery)"
            CONSUL_TPS["5,000 writes/sec"]
            CONSUL_LAT["< 20ms p99"]
            CONSUL_SIZE["No limit"]
        end

        subgraph "CockroachDB (per range)"
            CRDB_TPS["1,000 writes/sec"]
            CRDB_LAT["< 50ms p99"]
            CRDB_SIZE["64MB ranges"]
        end

        subgraph "Factors Affecting Performance"
            FACTORS["• Network latency<br/>• Disk I/O (fsync)<br/>• Batch size<br/>• Cluster size<br/>• Geographic distribution"]
        end
    end

    %% Apply state plane color for performance metrics
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    class ETCD_TPS,ETCD_LAT,ETCD_SIZE,CONSUL_TPS,CONSUL_LAT,CONSUL_SIZE,CRDB_TPS,CRDB_LAT,CRDB_SIZE,FACTORS stateStyle
```

### Deployment Patterns

#### High Availability Setup (5 nodes)

```mermaid
graph TB
    subgraph "Multi-AZ Raft Deployment"
        subgraph "AZ-1 (us-east-1a)"
            N1[Node 1]
            N2[Node 2]
        end

        subgraph "AZ-2 (us-east-1b)"
            N3[Node 3]
            N4[Node 4]
        end

        subgraph "AZ-3 (us-east-1c)"
            N5[Node 5]
        end
    end

    subgraph "Failure Scenarios"
        SINGLE["Single node failure:<br/>4/5 nodes = majority"]
        AZ_FAIL["AZ failure:<br/>3/5 nodes = majority"]
        NETWORK["Network partition:<br/>Largest partition wins"]
    end

    N1 <--> N3
    N1 <--> N4
    N1 <--> N5
    N2 <--> N3
    N2 <--> N4
    N2 <--> N5
    N3 <--> N5
    N4 <--> N5

    %% Apply colors
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff

    class N1,N2,N3,N4,N5 edgeStyle
    class SINGLE,AZ_FAIL,NETWORK controlStyle
```

### Monitoring and Alerting

```yaml
# Prometheus alerts for Raft health
groups:
- name: raft.rules
  rules:
  - alert: RaftLeaderElection
    expr: increase(raft_leader_elections_total[5m]) > 0
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Raft leader election occurred"

  - alert: RaftNoLeader
    expr: raft_leader_last_contact_seconds > 5
    for: 30s
    labels:
      severity: critical
    annotations:
      summary: "Raft cluster has no leader"

  - alert: RaftHighCommitLatency
    expr: histogram_quantile(0.99, raft_commit_duration_seconds_bucket) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High Raft commit latency"

  - alert: RaftLogReplicationLag
    expr: raft_replication_append_entries_rpc_duration_seconds > 0.05
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Slow log replication"
```

### Production Tuning Guidelines

#### Network Optimization
```bash
# Increase TCP buffer sizes
echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem = 4096 65536 134217728' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem = 4096 65536 134217728' >> /etc/sysctl.conf

# Reduce TCP timeouts for faster failure detection
echo 'net.ipv4.tcp_keepalive_time = 30' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_keepalive_intvl = 5' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_keepalive_probes = 3' >> /etc/sysctl.conf
```

#### Disk I/O Optimization
```bash
# Use dedicated SSD for Raft log (WAL)
# Mount with appropriate options
mount -o noatime,nodiratime /dev/nvme1n1 /var/lib/raft/wal

# Ensure fsync performance
echo deadline > /sys/block/nvme1n1/queue/scheduler

# Set appropriate I/O scheduler
echo 1 > /sys/block/nvme1n1/queue/iosched/fifo_batch
```

This covers the major production implementations of Raft, showing how real systems like etcd, Consul, and CockroachDB use Raft to achieve strong consistency in their distributed architectures.