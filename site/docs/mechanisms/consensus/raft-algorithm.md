# Raft Consensus Algorithm

## Complete Raft Flow with Leader Election

The Raft consensus algorithm ensures linearizable consistency across distributed nodes through leader election, log replication, and safety guarantees.

### Leader Election Flow

```mermaid
sequenceDiagram
    participant N1 as Node 1 (Follower)
    participant N2 as Node 2 (Follower)
    participant N3 as Node 3 (Candidate)
    participant N4 as Node 4 (Follower)
    participant N5 as Node 5 (Follower)

    Note over N1,N5: Initial state: All nodes are followers

    N3->>N3: Election timeout (150-300ms)
    N3->>N3: Increment term, become candidate

    N3->>N1: RequestVote(term=2, candidateId=3)
    N3->>N2: RequestVote(term=2, candidateId=3)
    N3->>N4: RequestVote(term=2, candidateId=3)
    N3->>N5: RequestVote(term=2, candidateId=3)

    N1-->>N3: VoteGranted(term=2, voteGranted=true)
    N2-->>N3: VoteGranted(term=2, voteGranted=true)
    N4-->>N3: VoteGranted(term=2, voteGranted=true)
    N5-->>N3: VoteGranted(term=2, voteGranted=false)

    Note over N3: Received majority (3/5), become leader
    N3->>N3: Become leader for term 2

    N3->>N1: AppendEntries(heartbeat, term=2)
    N3->>N2: AppendEntries(heartbeat, term=2)
    N3->>N4: AppendEntries(heartbeat, term=2)
    N3->>N5: AppendEntries(heartbeat, term=2)
```

### Complete State Machine

```mermaid
stateDiagram-v2
    [*] --> Follower

    Follower --> Candidate: Election timeout
    Candidate --> Leader: Wins election (majority votes)
    Candidate --> Follower: Discovers higher term
    Candidate --> Candidate: Split vote, new election

    Leader --> Follower: Discovers higher term

    state Follower {
        [*] --> WaitingHeartbeat
        WaitingHeartbeat --> ResetTimer: Receives AppendEntries
        WaitingHeartbeat --> StartElection: Election timeout (150-300ms)
    }

    state Candidate {
        [*] --> RequestVotes
        RequestVotes --> CountVotes: Send RequestVote RPCs
        CountVotes --> BecomeLeader: Majority votes
        CountVotes --> StepDown: Higher term discovered
        CountVotes --> StartNewElection: Split vote timeout
    }

    state Leader {
        [*] --> SendHeartbeats
        SendHeartbeats --> ReplicateEntries: Client request
        ReplicateEntries --> CommitEntries: Majority acknowledgment
        SendHeartbeats --> StepDown: Higher term discovered
    }
```

### Log Replication Protocol

```mermaid
sequenceDiagram
    participant C as Client
    participant L as Leader (Node 3)
    participant F1 as Follower (Node 1)
    participant F2 as Follower (Node 2)
    participant F3 as Follower (Node 4)
    participant F4 as Follower (Node 5)

    C->>L: SET key=value
    L->>L: Append to local log [term=2, index=5]

    par Replicate to all followers
        L->>F1: AppendEntries(term=2, prevLogIndex=4, entries=[{key=value}])
        L->>F2: AppendEntries(term=2, prevLogIndex=4, entries=[{key=value}])
        L->>F3: AppendEntries(term=2, prevLogIndex=4, entries=[{key=value}])
        L->>F4: AppendEntries(term=2, prevLogIndex=4, entries=[{key=value}])
    end

    par Responses
        F1-->>L: Success(term=2, index=5)
        F2-->>L: Success(term=2, index=5)
        F3-->>L: Success(term=2, index=5)
        F4-->>L: Failure(term=2, conflict=true)
    end

    Note over L: Majority (3/5) succeeded, commit entry
    L->>L: commitIndex = 5, apply to state machine

    L->>C: OK

    par Send commit notifications
        L->>F1: AppendEntries(commitIndex=5)
        L->>F2: AppendEntries(commitIndex=5)
        L->>F3: AppendEntries(commitIndex=5)
        L->>F4: AppendEntries(prevLogIndex=3, entries=[...])
    end
```

### Configuration Parameters

```yaml
# Production Raft Configuration (etcd style)
raft_config:
  # Election timing
  election_timeout_min: 150ms    # Minimum election timeout
  election_timeout_max: 300ms    # Maximum election timeout (randomized)
  heartbeat_interval: 50ms       # Leader heartbeat frequency

  # Log compaction
  snapshot_count: 10000          # Entries before snapshot
  max_log_size: 100MB           # Maximum log file size

  # Network timeouts
  append_entries_timeout: 1s     # AppendEntries RPC timeout
  request_vote_timeout: 500ms    # RequestVote RPC timeout

  # Batch settings
  max_append_entries: 1000       # Max entries per AppendEntries
  max_inflight_rpcs: 64          # Max concurrent RPCs
```

### Safety Properties

```mermaid
graph TB
    subgraph Raft_Safety_Guarantees[Raft Safety Guarantees]
        LE[Leader Election Safety]
        LAS[Leader Append-Only Safety]
        LM[Log Matching Property]
        LCS[Leader Completeness Safety]
        SM[State Machine Safety]
    end

    LE --> |"At most one leader per term"| LE_DESC[• Only candidate with majority votes becomes leader<br/>• Split votes trigger new election<br/>• Higher term always wins]

    LAS --> |"Leaders never overwrite log entries"| LAS_DESC[• Leaders only append new entries<br/>• Never delete or modify existing entries<br/>• Committed entries are permanent]

    LM --> |"Matching entries are identical"| LM_DESC[• Same index + term → same command<br/>• All preceding entries are identical<br/>• Consistency check on AppendEntries]

    LCS --> |"All committed entries are in new leader logs"| LCS_DESC[• Election restriction ensures this<br/>• Candidate must have all committed entries<br/>• Voters reject outdated candidates]

    SM --> |"Applied entries are identical on all nodes"| SM_DESC[• Only committed entries are applied<br/>• Deterministic state machine<br/>• Same sequence produces same state]

    %% Apply control plane color for safety properties
    classDef controlStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    class LE,LAS,LM,LCS,SM controlStyle
```

### Production Metrics

```mermaid
graph LR
    subgraph Key_Raft_Metrics[Key Raft Metrics]
        TPS[Transactions/sec]
        LAT[Commit Latency p99]
        LEF[Leader Election Frequency]
        LRF[Log Replication Factor]
    end

    subgraph Typical_Production_Values[Typical Production Values]
        TPS_VAL[10,000-50,000 TPS<br/>(etcd: ~10k, Consul: ~5k)]
        LAT_VAL[1-10ms p99<br/>(LAN: 1-3ms, WAN: 5-10ms)]
        LEF_VAL[< 1 per day<br/>(Healthy: 0, Issues: > 10/day)]
        LRF_VAL[3-5 replicas<br/>(Odd numbers only)]
    end

    TPS --> TPS_VAL
    LAT --> LAT_VAL
    LEF --> LEF_VAL
    LRF --> LRF_VAL

    %% Apply state plane color for metrics
    classDef stateStyle fill:#F59E0B,stroke:#D97706,color:#fff
    class TPS,LAT,LEF,LRF,TPS_VAL,LAT_VAL,LEF_VAL,LRF_VAL stateStyle
```

### Implementation Checklist

### Production Cost-Benefit Analysis

| Benefit | Cost | Production Evidence |
|---------|------|---------------------|
| **Linearizable consistency** | 30-50% throughput reduction | etcd: 10K vs 30K ops/sec |
| **Operational simplicity** | Complex implementation | 6-12 months development |
| **Proven safety guarantees** | Higher latency (consensus overhead) | +10-50ms p99 latency |
| **Strong community support** | Resource requirements (odd cluster sizes) | 3-5 nodes minimum |
| **Battle-tested reliability** | Network partition sensitivity | 99.9%+ availability |

Raft has become the consensus algorithm of choice for modern distributed systems, powering trillions of dollars in database transactions and managing millions of Kubernetes clusters worldwide with exceptional safety and reliability guarantees.