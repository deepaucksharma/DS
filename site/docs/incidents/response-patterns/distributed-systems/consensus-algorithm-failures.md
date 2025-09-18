# Consensus Algorithm Failure Emergency Response

> **3 AM Emergency Protocol**: Consensus algorithm failures can cause split-brain scenarios, data inconsistency, and total system unavailability. This diagram shows how to detect, diagnose, and recover from consensus failures.

## Quick Detection Checklist
- [ ] Check leader election status: `etcdctl endpoint status --write-out=table`
- [ ] Monitor vote counts and terms: Look for election storms or stuck elections
- [ ] Verify quorum health: Ensure majority of nodes are reachable
- [ ] Alert on consensus timeouts: Extended periods without successful elections

## Consensus Algorithm Failure Detection and Recovery

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Client Requests]
        WRITES[Write Requests<br/>Rate: 1000/sec<br/>Requirement: Strong consistency<br/>Status: BLOCKED]
        READS[Read Requests<br/>Rate: 5000/sec<br/>Tolerance: Eventual consistency<br/>Status: DEGRADED]
        CONFIG[Configuration Changes<br/>Cluster membership updates<br/>Schema changes<br/>Status: PROHIBITED]
    end

    subgraph ServicePlane[Service Plane - Consensus Participants]
        subgraph RAFT_CLUSTER[Raft Consensus Cluster]
            NODE_1[Node 1 (East)<br/>State: CANDIDATE<br/>Term: 47<br/>Votes received: 1/3<br/>Last heartbeat: 5s ago]
            NODE_2[Node 2 (Central)<br/>State: CANDIDATE<br/>Term: 48<br/>Votes received: 1/3<br/>Last heartbeat: 3s ago]
            NODE_3[Node 3 (West)<br/>State: CANDIDATE<br/>Term: 47<br/>Votes received: 1/3<br/>Last heartbeat: 7s ago]
            NODE_4[Node 4 (Central)<br/>State: FOLLOWER<br/>Term: 46<br/>Leader: UNKNOWN<br/>Status: CONFUSED]
            NODE_5[Node 5 (East)<br/>State: FOLLOWER<br/>Term: 45<br/>Leader: UNKNOWN<br/>Status: PARTITIONED]
        end

        ELECTION[Election Process<br/>Algorithm: Raft<br/>Status: STORM DETECTED<br/>Duration: 5 minutes<br/>Issue: Split votes]
    end

    subgraph StatePlane[State Plane - Consensus State]
        subgraph LEADER_STATE[Leadership State]
            NO_LEADER[No Current Leader<br/>Election timeout: 150ms<br/>Heartbeat timeout: 50ms<br/>Network latency: 200ms<br/>Issue: Timeouts too aggressive]
            TERM_CHAOS[Term Number Chaos<br/>Node 1: Term 47<br/>Node 2: Term 48<br/>Node 3: Term 47<br/>Inconsistent state: YES]
        end

        subgraph LOG_STATE[Log Replication State]
            LOG_DIVERGENCE[Log Divergence<br/>Node 1 last index: 1000<br/>Node 2 last index: 998<br/>Node 3 last index: 1001<br/>Consistency: BROKEN]
            COMMIT_INDEX[Commit Index Issues<br/>Majority commit: STALLED<br/>Last committed: 5 minutes ago<br/>Pending entries: 50]
        end

        QUORUM[Quorum Status<br/>Required: 3/5 nodes<br/>Available: 2/5 healthy<br/>Network partitions: 2<br/>Status: QUORUM LOST]
    end

    subgraph ControlPlane[Control Plane - Consensus Management]
        MONITOR[Consensus Monitoring<br/>Election timeout tracking<br/>Term progression analysis<br/>Log consistency verification]

        subgraph DETECTION[Failure Detection]
            ELECTION_STORM[Election Storm Detection<br/>Multiple candidates<br/>Split vote scenarios<br/>Timeout cascade detection]
            NETWORK_PARTITION[Partition Detection<br/>Node reachability matrix<br/>Heartbeat failure analysis<br/>Quorum calculation]
            LOG_INCONSISTENCY[Log Inconsistency Detection<br/>Index comparison<br/>Checksum validation<br/>Divergence analysis]
        end

        subgraph RECOVERY[Recovery Mechanisms]
            MANUAL_INTERVENTION[Manual Intervention<br/>Force leader promotion<br/>Cluster reset procedures<br/>Data reconciliation]
            TIMEOUT_TUNING[Timeout Adjustment<br/>Election timeout increase<br/>Heartbeat frequency adjustment<br/>Network latency adaptation]
            QUORUM_ADJUSTMENT[Quorum Adjustment<br/>Temporary quorum reduction<br/>Node removal from cluster<br/>Emergency procedures]
        end
    end

    %% Client request flow
    WRITES -.->|"Blocked - no leader"| NODE_1
    READS -.->|"Stale data"| NODE_2
    CONFIG -.->|"Prohibited - no consensus"| NODE_3

    %% Election process
    NODE_1 -.->|"Request vote"| NODE_2
    NODE_2 -.->|"Request vote"| NODE_3
    NODE_3 -.->|"Request vote"| NODE_1
    NODE_4 -.->|"Split vote"| NODE_1
    NODE_5 -.->|"Network partition"| ELECTION

    %% Consensus state issues
    NODE_1 --> NO_LEADER
    NODE_2 --> TERM_CHAOS
    NODE_3 --> LOG_DIVERGENCE
    NODE_4 --> COMMIT_INDEX
    NODE_5 -.->|"Isolated"| QUORUM

    %% Monitoring and detection
    ELECTION --> MONITOR
    NO_LEADER --> MONITOR
    TERM_CHAOS --> MONITOR
    LOG_DIVERGENCE --> MONITOR
    QUORUM --> MONITOR

    %% Failure detection
    MONITOR --> ELECTION_STORM
    MONITOR --> NETWORK_PARTITION
    MONITOR --> LOG_INCONSISTENCY

    %% Recovery responses
    ELECTION_STORM --> MANUAL_INTERVENTION
    NETWORK_PARTITION --> TIMEOUT_TUNING
    LOG_INCONSISTENCY --> QUORUM_ADJUSTMENT

    %% Recovery actions
    MANUAL_INTERVENTION -.->|"Force elect leader"| NODE_2
    TIMEOUT_TUNING -.->|"Increase timeouts"| ELECTION
    QUORUM_ADJUSTMENT -.->|"Reduce quorum requirement"| QUORUM

    %% 4-plane styling
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef failedStyle fill:#FF0000,stroke:#CC0000,color:#fff
    classDef candidateStyle fill:#FFA500,stroke:#CC8800,color:#fff
    classDef followerStyle fill:#CCCCCC,stroke:#999999,color:#000

    class WRITES,READS,CONFIG edgeStyle
    class ELECTION serviceStyle
    class NO_LEADER,TERM_CHAOS,LOG_DIVERGENCE,COMMIT_INDEX,QUORUM stateStyle
    class MONITOR,ELECTION_STORM,NETWORK_PARTITION,LOG_INCONSISTENCY,MANUAL_INTERVENTION,TIMEOUT_TUNING,QUORUM_ADJUSTMENT controlStyle
    class NODE_1,NODE_2,NODE_3 candidateStyle
    class NODE_4,NODE_5 followerStyle
```

## 3 AM Emergency Response Commands

### 1. Consensus Status Assessment (30 seconds)
```bash
# Check etcd cluster status
etcdctl --endpoints=node1:2379,node2:2379,node3:2379 endpoint status --write-out=table
etcdctl --endpoints=node1:2379,node2:2379,node3:2379 endpoint health

# Check Raft state for each node
etcdctl --endpoints=node1:2379 endpoint status --write-out=json | jq '.[] | {endpoint, leader}'

# Monitor election activity
journalctl -u etcd --since "5 minutes ago" | grep -E "(election|candidate|leader)"

# Check consensus logs for Consul/other systems
consul operator raft list-peers
consul monitor -log-level=DEBUG | grep raft
```

### 2. Emergency Leader Election (60 seconds)
```bash
# Force leader election in etcd (DANGEROUS - use carefully)
# First, identify the most up-to-date node
etcdctl --endpoints=all endpoint status --write-out=table

# Remove problematic members if necessary
etcdctl member list
etcdctl member remove [member-id]

# Add them back after network issues resolved
etcdctl member add node3 --peer-urls=http://node3:2380

# For database clusters with consensus issues
# MySQL Group Replication
mysql -e "STOP GROUP_REPLICATION; START GROUP_REPLICATION;"

# PostgreSQL with Patroni
patronictl -c /etc/patroni.yml switchover --master current-master --candidate best-replica
```

### 3. Quorum Recovery (90 seconds)
```bash
# Temporary quorum reduction (emergency procedure)
# Edit etcd configuration to reduce cluster size
export ETCD_INITIAL_CLUSTER="node1=http://node1:2380,node2=http://node2:2380"  # Remove problematic nodes

# Restart etcd with new configuration
systemctl restart etcd

# For Kubernetes clusters
kubectl get nodes
kubectl cordon [unreachable-nodes]
kubectl delete node [unreachable-nodes]  # Remove from cluster

# Verify new quorum
etcdctl endpoint status --write-out=table
kubectl get nodes  # Should show only healthy nodes
```

## Consensus Failure Pattern Recognition

### Election Storm Pattern
```
Time    Node1_State    Node2_State    Node3_State    Election_Term    Leader
10:00   Follower      Leader         Follower       42              Node2
10:01   Candidate     Candidate      Follower       43              None
10:02   Candidate     Candidate      Candidate      44              None
10:03   Candidate     Candidate      Candidate      45              None
10:04   Candidate     Candidate      Candidate      46              None
Status: Election storm - no majority agreement
```

### Log Divergence Pattern
```
Node    Last_Index    Last_Term    Committed_Index    Status
Node1   1000         42           995               Behind
Node2   998          43           990               Diverged
Node3   1001         42           1000              Ahead
Node4   997          41           985               Very behind
Node5   999          42           998               Catching up
Issue: Log entries not properly replicated, consensus broken
```

### Network Partition Impact
```
Partition    Nodes        Quorum    Leader_Capability    Write_Status
East         Node1,Node5  2/5 (No)  Cannot elect         Blocked
Central      Node2,Node4  2/5 (No)  Cannot elect         Blocked
West         Node3        1/5 (No)  Cannot elect         Blocked
Total        0 nodes      0/5       No leader            System down
```

## Error Message Patterns

### Raft Election Timeout
```
ERROR: raft election timeout
PATTERN: "election timeout" or "no heartbeat from leader"
LOCATION: etcd logs, consensus system logs
CAUSE: Network latency, overloaded nodes, split votes
ACTION: Increase election timeout, check network health
```

### Split Vote Scenario
```
ERROR: raft split vote detected
PATTERN: Multiple candidates in same term, no majority
LOCATION: Election logs, term progression tracking
CAUSE: Network timing issues, simultaneous candidate declarations
ACTION: Adjust election randomization, check network stability
```

### Log Replication Failure
```
ERROR: log replication failed
PATTERN: "failed to replicate to majority" or "commit index stuck"
LOCATION: Raft logs, replication monitoring
CAUSE: Slow followers, network issues, disk I/O problems
ACTION: Check follower health, optimize disk performance
```

## Consensus Algorithm Debugging

### Raft State Analysis
```bash
#!/bin/bash
# Raft cluster analysis script

ENDPOINTS="node1:2379,node2:2379,node3:2379"

echo "=== Raft Cluster Analysis ==="
echo

# Basic health check
echo "Cluster Health:"
etcdctl --endpoints=$ENDPOINTS endpoint health
echo

# Leader and term information
echo "Leadership Status:"
etcdctl --endpoints=$ENDPOINTS endpoint status --write-out=table
echo

# Member list
echo "Cluster Members:"
etcdctl --endpoints=$ENDPOINTS member list --write-out=table
echo

# Check for election activity
echo "Recent Election Activity:"
for endpoint in $(echo $ENDPOINTS | tr ',' ' '); do
    echo "Node $endpoint:"
    etcdctl --endpoints=$endpoint endpoint status --write-out=json | \
        jq -r '.[0] | "Term: \(.Status.raftTerm), Index: \(.Status.raftIndex), Leader: \(.Status.leader)"'
done
echo

# Log compaction status
echo "Log Status:"
for endpoint in $(echo $ENDPOINTS | tr ',' ' '); do
    echo "Node $endpoint log entries:"
    etcdctl --endpoints=$endpoint get "" --prefix --keys-only | wc -l
done
```

### Election Timeout Optimization
```yaml
# etcd configuration for network partition tolerance
# /etc/etcd/etcd.conf.yml
name: 'node1'
data-dir: /var/lib/etcd
wal-dir: /var/lib/etcd/wal
snapshot-count: 10000
heartbeat-interval: 100    # Increased from default 100ms
election-timeout: 2000     # Increased from default 1000ms
quota-backend-bytes: 0
listen-peer-urls: http://0.0.0.0:2380
listen-client-urls: http://0.0.0.0:2379
max-snapshots: 5
max-wals: 5
cors:
initial-advertise-peer-urls: http://node1:2380
advertise-client-urls: http://node1:2379
discovery:
initial-cluster: node1=http://node1:2380,node2=http://node2:2380,node3=http://node3:2380
initial-cluster-token: 'etcd-cluster'
initial-cluster-state: 'new'
strict-reconfig-check: false
enable-v2: true
```

### Consensus Monitoring with Prometheus
```yaml
# Prometheus rules for consensus monitoring
groups:
- name: consensus_health
  rules:
  - alert: EtcdNoLeader
    expr: etcd_server_has_leader == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "etcd cluster has no leader"
      description: "etcd cluster has been without a leader for more than 1 minute"

  - alert: EtcdElectionStorm
    expr: rate(etcd_server_leader_changes_seen_total[5m]) > 0.5
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "etcd leader election storm"
      description: "etcd cluster experiencing frequent leader changes"

  - alert: EtcdLogReplicationLag
    expr: etcd_server_proposals_pending > 50
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "etcd log replication lag"
      description: "etcd has {{ $value }} pending proposals"
```

## Consensus Algorithm Tuning

### Raft Parameter Optimization
```go
// Go Raft configuration for different network conditions
type RaftConfig struct {
    // Election timeout range
    ElectionTimeoutMin time.Duration  // 150ms for local networks
    ElectionTimeoutMax time.Duration  // 300ms for local networks

    // Heartbeat interval
    HeartbeatTimeout time.Duration    // 50ms for local networks

    // Log replication
    MaxAppendEntries int              // Number of entries per append
    LogLevel        string            // Debug level for troubleshooting

    // Network conditions
    LocalNetworkLatency  time.Duration  // <1ms for local
    WANNetworkLatency   time.Duration  // 50-200ms for WAN
    UnreliableNetwork   bool           // Adjust timeouts accordingly
}

// Network-aware timeout calculation
func calculateTimeouts(avgLatency time.Duration) RaftConfig {
    // Rule of thumb: election timeout should be 10x network latency
    minElection := avgLatency * 10
    maxElection := avgLatency * 20
    heartbeat := avgLatency * 2

    return RaftConfig{
        ElectionTimeoutMin: minElection,
        ElectionTimeoutMax: maxElection,
        HeartbeatTimeout:   heartbeat,
        MaxAppendEntries:   100,
        LogLevel:          "INFO",
    }
}
```

### Multi-Raft for Scalability
```yaml
# Kubernetes StatefulSet for Multi-Raft deployment
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: multi-raft-cluster
spec:
  serviceName: "raft-cluster"
  replicas: 3
  selector:
    matchLabels:
      app: multi-raft
  template:
    metadata:
      labels:
        app: multi-raft
    spec:
      containers:
      - name: raft-node
        image: raft-consensus:latest
        env:
        - name: RAFT_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: RAFT_CLUSTER_SIZE
          value: "3"
        - name: ELECTION_TIMEOUT_MIN
          value: "500ms"    # Increased for network tolerance
        - name: ELECTION_TIMEOUT_MAX
          value: "1000ms"
        - name: HEARTBEAT_INTERVAL
          value: "100ms"
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Emergency Consensus Recovery Procedures

### Phase 1: Immediate Assessment (0-2 minutes)
- [ ] Check cluster quorum status and node reachability
- [ ] Identify current leader (if any) and election state
- [ ] Verify log consistency across all nodes
- [ ] Assess network connectivity between consensus nodes

### Phase 2: Emergency Stabilization (2-10 minutes)
- [ ] Adjust consensus timeouts for network conditions
- [ ] Remove unreachable nodes from cluster temporarily
- [ ] Force leader election if cluster is leaderless
- [ ] Enable read-only mode if writes are critical

### Phase 3: Data Consistency Restoration (10+ minutes)
- [ ] Verify log replication is working correctly
- [ ] Reconcile any divergent logs between nodes
- [ ] Re-add removed nodes back to cluster
- [ ] Validate full cluster functionality and consistency

## Advanced Consensus Patterns

### Byzantine Fault Tolerance (PBFT)
```python
# Simplified PBFT implementation for Byzantine fault tolerance
class PBFTNode:
    def __init__(self, node_id, total_nodes):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.byzantine_threshold = (total_nodes - 1) // 3
        self.view = 0
        self.sequence_number = 0
        self.state = "normal"
        self.pending_requests = {}

    def can_tolerate_failures(self):
        """PBFT can tolerate up to f Byzantine failures in 3f+1 nodes"""
        max_byzantine_faults = (self.total_nodes - 1) // 3
        return max_byzantine_faults

    def initiate_consensus(self, request):
        """Three-phase consensus: pre-prepare, prepare, commit"""
        if self.state != "normal":
            return False

        # Phase 1: Pre-prepare
        pre_prepare_msg = {
            'view': self.view,
            'sequence': self.sequence_number,
            'request': request,
            'node_id': self.node_id
        }

        # Broadcast to all nodes
        prepare_votes = self.broadcast_pre_prepare(pre_prepare_msg)

        # Phase 2: Prepare (need 2f+1 votes)
        required_votes = 2 * self.byzantine_threshold + 1
        if len(prepare_votes) >= required_votes:
            commit_votes = self.broadcast_prepare(pre_prepare_msg)

            # Phase 3: Commit (need 2f+1 votes)
            if len(commit_votes) >= required_votes:
                self.execute_request(request)
                return True

        return False

    def detect_byzantine_behavior(self, messages):
        """Detect inconsistent or malicious messages"""
        message_counts = {}
        for msg in messages:
            key = (msg['view'], msg['sequence'], hash(str(msg['request'])))
            message_counts[key] = message_counts.get(key, 0) + 1

        # If we see conflicting messages from same node
        for node_id in set(msg['node_id'] for msg in messages):
            node_messages = [msg for msg in messages if msg['node_id'] == node_id]
            if len(set((msg['view'], msg['sequence']) for msg in node_messages)) > 1:
                return node_id  # Potential Byzantine node

        return None
```

### Consensus with Witness Nodes
```yaml
# Witness node configuration for tie-breaking
apiVersion: v1
kind: ConfigMap
metadata:
  name: consensus-config
data:
  cluster.yaml: |
    consensus:
      algorithm: raft
      total_nodes: 5
      voting_nodes: 3      # Full consensus participants
      witness_nodes: 2     # Lightweight tie-breakers

    nodes:
      - id: 1
        type: voting
        region: us-east
        weight: 1
      - id: 2
        type: voting
        region: us-central
        weight: 1
      - id: 3
        type: voting
        region: us-west
        weight: 1
      - id: 4
        type: witness
        region: eu-west
        weight: 0.5    # Reduced weight for tie-breaking only
      - id: 5
        type: witness
        region: ap-southeast
        weight: 0.5

    quorum:
      voting_quorum: 2      # Majority of voting nodes
      witness_threshold: 1   # At least one witness for tie-breaking
      total_quorum: 3       # Combined quorum requirement
```

## Real-World Consensus Algorithm Failures

### etcd Split-Brain at Kubernetes Control Plane (2020)
- **Trigger**: Network partition isolated etcd leader
- **Impact**: Kubernetes API became read-only, no pod scheduling
- **Detection**: etcd health checks failing, no leader elected
- **Resolution**: Network restoration + manual etcd member removal/addition

### MongoDB Replica Set Election Storm (2019)
- **Trigger**: Aggressive timeout settings during network instability
- **Impact**: Constant primary elections, write operations blocked
- **Detection**: Election frequency monitoring + write latency spikes
- **Resolution**: Timeout tuning + network stability improvements

### Consul Raft Consensus Failure (2021)
- **Trigger**: Disk I/O saturation caused log replication delays
- **Impact**: Service discovery became inconsistent across nodes
- **Detection**: Raft log replication lag monitoring
- **Resolution**: Disk performance optimization + log compaction tuning

---
*Last Updated: Based on etcd, MongoDB, Consul consensus algorithm failures*
*Next Review: Monitor for new consensus patterns and Byzantine fault tolerance implementations*