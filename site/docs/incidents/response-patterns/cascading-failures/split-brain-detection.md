# Split-Brain Detection and Resolution

> **3 AM Emergency Protocol**: Split-brain scenarios create multiple "active" masters, leading to data corruption and conflicting state. This diagram shows how to quickly detect and resolve split-brain conditions.

## Quick Detection Checklist
- [ ] Check cluster membership: `kubectl get nodes | grep -E "(NotReady|Unknown)"`
- [ ] Verify leader election: `etcdctl endpoint status --write-out=table`
- [ ] Monitor partition detection: `redis-cli cluster nodes | grep -E "(fail|pfail)"`
- [ ] Alert on multiple masters: Count active masters != 1

## Split-Brain Detection and Emergency Resolution

```mermaid
graph TB
    subgraph EdgePlane[Edge Plane - Client Perspective]
        CLIENT_A[Client Group A<br/>Connected to: Partition 1<br/>Sees: Master-1 as leader]
        CLIENT_B[Client Group B<br/>Connected to: Partition 2<br/>Sees: Master-2 as leader]
        LB[Load Balancer<br/>Health checks failing<br/>Routing inconsistently]
    end

    subgraph ServicePlane[Service Plane - Split Services]
        subgraph PARTITION_1[Network Partition 1]
            MASTER_1[Master Node 1<br/>State: ACTIVE LEADER<br/>Last heartbeat: Self<br/>Cluster size: 2/5 nodes]
            SERVICE_A1[Service Instance A1<br/>Connected to: Master-1<br/>Accepting writes: YES]
            SERVICE_B1[Service Instance B1<br/>Connected to: Master-1<br/>Data version: v1.234]
        end

        subgraph PARTITION_2[Network Partition 2]
            MASTER_2[Master Node 2<br/>State: ACTIVE LEADER<br/>Last heartbeat: Self<br/>Cluster size: 3/5 nodes]
            SERVICE_A2[Service Instance A2<br/>Connected to: Master-2<br/>Accepting writes: YES]
            SERVICE_B2[Service Instance B2<br/>Connected to: Master-2<br/>Data version: v1.235]
        end

        QUORUM_LOST[Quorum Detection<br/>Expected: 3/5 nodes<br/>Partition 1: 2/5 (LOST)<br/>Partition 2: 3/5 (VALID)]
    end

    subgraph StatePlane[State Plane - Conflicting Data]
        subgraph DATA_PARTITION_1[Data Partition 1]
            DB_1[(Database Instance 1<br/>Leader: YES<br/>Last write: 10:03:45<br/>Transaction ID: 1001)]
            REDIS_1[(Redis Instance 1<br/>Role: master<br/>Replication: STOPPED<br/>Memory: diverging)]
        end

        subgraph DATA_PARTITION_2[Data Partition 2]
            DB_2[(Database Instance 2<br/>Leader: YES<br/>Last write: 10:03:47<br/>Transaction ID: 1002)]
            REDIS_2[(Redis Instance 2<br/>Role: master<br/>Replication: STOPPED<br/>Memory: diverging)]
        end

        CONFLICT[Data Conflict<br/>Same key, different values<br/>Resolution needed<br/>Manual intervention required]
    end

    subgraph ControlPlane[Control Plane - Resolution]
        DETECTION[Split-Brain Detection<br/>Network partition monitoring<br/>Leader election conflicts<br/>Quorum validation]

        RESOLUTION[Automatic Resolution<br/>Fence minority partition<br/>Promote majority leader<br/>Block minority writes]

        MANUAL[Manual Intervention<br/>Data conflict resolution<br/>Service restart coordination<br/>Client redirection]

        RECOVERY[Recovery Orchestration<br/>Network healing<br/>Data synchronization<br/>Service restoration]
    end

    %% Client connections
    CLIENT_A --> MASTER_1
    CLIENT_B --> MASTER_2
    LB -.->|"Inconsistent routing"| MASTER_1
    LB -.->|"Inconsistent routing"| MASTER_2

    %% Service connections
    SERVICE_A1 --> DB_1
    SERVICE_B1 --> REDIS_1
    SERVICE_A2 --> DB_2
    SERVICE_B2 --> REDIS_2

    %% Split-brain scenario
    MASTER_1 -.->|"Network partition"| MASTER_2
    DB_1 -.->|"Replication broken"| DB_2
    REDIS_1 -.->|"Cluster split"| REDIS_2

    %% Conflict detection
    DB_1 --> CONFLICT
    DB_2 --> CONFLICT
    REDIS_1 --> CONFLICT
    REDIS_2 --> CONFLICT

    %% Monitoring and resolution
    MASTER_1 --> DETECTION
    MASTER_2 --> DETECTION
    QUORUM_LOST --> DETECTION
    DETECTION -->|"Split detected"| RESOLUTION
    RESOLUTION -->|"Complex conflicts"| MANUAL
    MANUAL --> RECOVERY
    RECOVERY -.->|"Restore connectivity"| MASTER_1
    RECOVERY -.->|"Sync data"| DB_1

    %% Emergency actions
    RESOLUTION -.->|"Fence minority"| MASTER_1
    RESOLUTION -->|"Promote majority"| MASTER_2
    MANUAL -.->|"Block writes"| SERVICE_A1

    %% 4-plane styling
    classDef edgeStyle fill:#0066CC,stroke:#004499,color:#fff
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff
    classDef stateStyle fill:#FF8800,stroke:#CC6600,color:#fff
    classDef controlStyle fill:#CC0000,stroke:#990000,color:#fff
    classDef errorStyle fill:#FF0000,stroke:#CC0000,color:#fff
    classDef warningStyle fill:#FFA500,stroke:#CC8800,color:#fff

    class CLIENT_A,CLIENT_B,LB edgeStyle
    class MASTER_1,MASTER_2,SERVICE_A1,SERVICE_B1,SERVICE_A2,SERVICE_B2,QUORUM_LOST serviceStyle
    class DB_1,DB_2,REDIS_1,REDIS_2 stateStyle
    class DETECTION,RESOLUTION,MANUAL,RECOVERY controlStyle
    class CONFLICT errorStyle
    class MASTER_1 warningStyle
```

## 3 AM Emergency Response Commands

### 1. Split-Brain Detection (30 seconds)
```bash
# Check cluster node status
kubectl get nodes -o wide
kubectl describe nodes | grep -E "(Condition|Ready)"

# Verify etcd cluster health
etcdctl --endpoints=node1:2379,node2:2379,node3:2379 endpoint status --write-out=table
etcdctl --endpoints=node1:2379,node2:2379,node3:2379 endpoint health

# Check Redis cluster split
redis-cli cluster nodes | grep -E "(master|slave|fail)"
redis-cli cluster info | grep cluster_state
```

### 2. Emergency Fencing (60 seconds)
```bash
# Identify minority partition (fewer nodes)
TOTAL_NODES=$(kubectl get nodes --no-headers | wc -l)
READY_NODES=$(kubectl get nodes --no-headers | grep " Ready" | wc -l)
echo "Ready: $READY_NODES / Total: $TOTAL_NODES"

# Fence minority partition nodes (if quorum lost)
if [ $READY_NODES -lt $((TOTAL_NODES / 2 + 1)) ]; then
    echo "Quorum lost - manual intervention required"
    kubectl cordon node-minority-1
    kubectl cordon node-minority-2
fi

# Force leadership on majority partition
etcdctl move-leader [majority-node-id]
```

### 3. Data Conflict Resolution (90 seconds)
```bash
# Compare database states
mysql -h db-1 -e "SELECT MAX(id), MAX(updated_at) FROM transactions;"
mysql -h db-2 -e "SELECT MAX(id), MAX(updated_at) FROM transactions;"

# Check Redis memory usage and keys
redis-cli -h redis-1 info memory | grep used_memory_human
redis-cli -h redis-2 info memory | grep used_memory_human
redis-cli -h redis-1 dbsize
redis-cli -h redis-2 dbsize

# Identify conflicting transactions (manual inspection needed)
mysql -h db-1 -e "SELECT * FROM transactions WHERE updated_at > '2024-01-01 10:03:00';"
mysql -h db-2 -e "SELECT * FROM transactions WHERE updated_at > '2024-01-01 10:03:00';"
```

## Split-Brain Detection Patterns

### Network Partition Detection
```
Time    Node1_View    Node2_View    Node3_View    Cluster_State
10:00   [1,2,3,4,5]   [1,2,3,4,5]   [1,2,3,4,5]   HEALTHY
10:01   [1,2]         [3,4,5]       [3,4,5]       PARTITION
10:02   Leader: 1     Leader: 3     Leader: 3     SPLIT-BRAIN
10:03   Quorum: NO    Quorum: YES   Quorum: YES   CONFLICT
```

### Database Leadership Conflict
```
Instance    Role        Last_Write           WAL_Position    Accepting_Writes
db-1        PRIMARY     2024-01-01 10:03:45  1001           YES
db-2        PRIMARY     2024-01-01 10:03:47  1002           YES
Status: SPLIT-BRAIN DETECTED - Multiple primaries active
```

### Redis Cluster Split
```
Node         Role      Slots     Last_Ping    Status
redis-1:6379 master    0-5460    0            connected
redis-2:6379 master    5461-10922 0           connected
redis-3:6379 master    10923-16383 1500       disconnected
Cluster State: FAIL - Split into multiple partitions
```

## Error Message Patterns

### Kubernetes Split-Brain
```
ERROR: Multiple masters detected in cluster
PATTERN: Multiple nodes claiming to be master
LOCATION: kubectl describe nodes, etcd logs
ACTION: Check network connectivity, verify quorum
COMMAND: etcdctl member list --write-out=table
```

### Database Split-Brain
```
ERROR: Conflicting primary servers detected
PATTERN: "Multiple servers claiming primary role"
LOCATION: PostgreSQL logs, MySQL error logs
ACTION: Fence minority, promote majority primary
COMMAND: pg_promote() or mysqladmin start-slave
```

### Redis Cluster Split
```
ERROR: Cluster is down - partitioned
PATTERN: "CLUSTERDOWN The cluster is down"
LOCATION: Redis cluster logs, application logs
ACTION: Reset cluster, restore from backup
COMMAND: redis-cli cluster reset hard
```

## Automatic Resolution Strategies

### Quorum-Based Fencing
```yaml
# Kubernetes admission controller
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionWebhook
metadata:
  name: quorum-validator
webhooks:
- name: quorum.validator
  rules:
  - operations: ["CREATE", "UPDATE"]
    resources: ["pods"]
  admissionReviewVersions: ["v1"]
  clientConfig:
    service:
      name: quorum-validator
      namespace: kube-system
  failurePolicy: Fail
```

### Database Automatic Failover
```bash
#!/bin/bash
# Patroni-based PostgreSQL split-brain resolution
patronictl -c /etc/patroni.yml list
patronictl -c /etc/patroni.yml switchover --master current-master --candidate best-replica
patronictl -c /etc/patroni.yml restart postgresql
```

### Redis Cluster Auto-Recovery
```bash
#!/bin/bash
# Redis cluster split-brain auto-recovery
redis-cli cluster nodes | grep fail | awk '{print $1}' | while read node; do
    redis-cli cluster forget $node
done
redis-cli cluster meet [majority-node-ip] [port]
```

## Manual Resolution Procedures

### Phase 1: Assessment (0-5 minutes)
- [ ] Identify network partition boundaries
- [ ] Determine which partition has quorum
- [ ] Count active masters in each partition
- [ ] Assess data divergence between partitions

### Phase 2: Immediate Fencing (5-10 minutes)
- [ ] Fence minority partition (block writes)
- [ ] Promote majority partition leader
- [ ] Redirect all traffic to majority partition
- [ ] Document divergent transactions

### Phase 3: Data Reconciliation (10-60 minutes)
- [ ] Export conflicting data from minority partition
- [ ] Analyze transaction conflicts manually
- [ ] Merge or resolve data conflicts
- [ ] Restore network connectivity gradually

## Data Conflict Resolution Strategies

### Last-Writer-Wins
```sql
-- Resolve conflicts by timestamp
UPDATE transactions t1
SET amount = t2.amount, updated_at = t2.updated_at
FROM transactions_conflict t2
WHERE t1.id = t2.id
AND t2.updated_at > t1.updated_at;
```

### Manual Conflict Resolution
```sql
-- Create conflict resolution table
CREATE TABLE transaction_conflicts AS
SELECT t1.id, t1.amount as amount_db1, t1.updated_at as time_db1,
       t2.amount as amount_db2, t2.updated_at as time_db2
FROM db1.transactions t1
JOIN db2.transactions t2 ON t1.id = t2.id
WHERE t1.amount != t2.amount OR t1.updated_at != t2.updated_at;
```

### Business Logic Resolution
```python
# Python conflict resolution logic
def resolve_transaction_conflict(t1, t2):
    if t1['type'] == 'deposit' and t2['type'] == 'withdrawal':
        # Business rule: deposits take precedence
        return t1
    elif t1['amount'] > t2['amount']:
        # Business rule: larger amount wins
        return t1
    else:
        return t2
```

## Recovery Verification Checklist

### Network Healing Verification
- [ ] All nodes report healthy cluster membership
- [ ] Network partitions resolved (ping tests pass)
- [ ] Cluster quorum restored and stable
- [ ] Leadership election completed successfully

### Data Consistency Verification
- [ ] All replicas report same data checksums
- [ ] Transaction logs synchronized
- [ ] No orphaned or conflicting records
- [ ] Application state consistency validated

### Service Restoration Verification
- [ ] All services connected to single master
- [ ] Client traffic routing correctly
- [ ] No split-brain monitoring alerts
- [ ] Response times back to baseline

## Real-World Split-Brain Incidents

### GitHub MySQL Split-Brain (2018)
- **Trigger**: Network partition between data centers
- **Impact**: Multiple MySQL masters accepting writes
- **Detection**: Replication lag monitoring + manual discovery
- **Resolution**: Fenced East Coast DC, promoted West Coast
- **Data Loss**: 6 hours of conflicting commits required manual merge

### MongoDB Replica Set Split (2019)
- **Trigger**: DNS resolution failure caused node isolation
- **Impact**: Primary election in two separate partitions
- **Detection**: Replica set status monitoring
- **Resolution**: Manual intervention to remove duplicate primaries
- **Prevention**: Improved network monitoring and heartbeat tuning

### Consul Cluster Split (2020)
- **Trigger**: AWS availability zone network issues
- **Impact**: Service discovery returned conflicting results
- **Detection**: Consul leader election logs
- **Resolution**: Raft log truncation and cluster rebuild
- **Lesson**: Implement proper fencing mechanisms for distributed consensus

---
*Last Updated: Based on GitHub, MongoDB, Consul split-brain incidents*
*Next Review: Update detection thresholds based on network stability patterns*