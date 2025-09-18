# Linearizability Failures: What Happens When It Breaks

## Overview

Understanding how linearizability fails in production is crucial for building robust distributed systems. This guide examines real failure scenarios from major companies and their impact on system behavior.

## Failure Taxonomy

```mermaid
graph TB
    subgraph NetworkFailures[Network Failures - Blue]
        NF1[Partition Tolerance<br/>Split brain scenarios]
        NF2[Packet Loss<br/>Consensus message drops]
        NF3[Latency Spikes<br/>Timeout-based failures]
        NF4[Asymmetric Partitions<br/>Unidirectional connectivity]
    end

    subgraph NodeFailures[Node Failures - Green]
        NoF1[Leader Crashes<br/>Election delays]
        NoF2[Follower Failures<br/>Quorum loss]
        NoF3[Cascading Failures<br/>Resource exhaustion]
        NoF4[Byzantine Failures<br/>Corrupted nodes]
    end

    subgraph SystemFailures[System Failures - Orange]
        SF1[Clock Skew<br/>Timestamp inconsistencies]
        SF2[Disk Corruption<br/>WAL integrity loss]
        SF3[Memory Pressure<br/>OOM during consensus]
        SF4[Software Bugs<br/>Implementation errors]
    end

    subgraph ApplicationFailures[Application Failures - Red]
        AF1[Client Timeouts<br/>False failure detection]
        AF2[Retry Storms<br/>Amplification effects]
        AF3[Configuration Errors<br/>Incorrect cluster setup]
        AF4[Load Patterns<br/>Hot spotting issues]
    end

    %% Apply 4-plane colors
    classDef networkStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef nodeStyle fill:#10B981,stroke:#059669,color:#fff
    classDef systemStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef appStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class NF1,NF2,NF3,NF4 networkStyle
    class NoF1,NoF2,NoF3,NoF4 nodeStyle
    class SF1,SF2,SF3,SF4 systemStyle
    class AF1,AF2,AF3,AF4 appStyle
```

## Split Brain Scenario

```mermaid
sequenceDiagram
    participant C1 as Client 1
    participant C2 as Client 2
    participant L as Leader (Node A)
    participant F1 as Follower (Node B)
    participant F2 as Follower (Node C)

    Note over C1,F2: Normal Operation

    C1->>L: write(x, 1)
    L->>F1: replicate(x, 1)
    L->>F2: replicate(x, 1)
    F1->>L: ack
    F2->>L: ack
    L->>C1: success

    Note over L,F2: Network partition occurs
    Note over L: Partition 1: Leader + Node B
    Note over F2: Partition 2: Node C (minority)

    Note over L,F1: Majority partition continues
    C1->>L: write(x, 2)
    L->>F1: replicate(x, 2)
    F1->>L: ack
    L->>C1: success

    Note over F2: Minority partition blocks
    C2->>F2: write(x, 3)
    F2-->>C2: error: no quorum

    Note over L,F2: Partition heals

    F2->>L: rejoin cluster
    L->>F2: sync logs (x=2)

    Note over C1,F2: ✅ Linearizability preserved
    Note over C1,F2: Minority writes rejected
```

## MongoDB Rollback Incident

```mermaid
graph TB
    subgraph BeforePartition[Before Network Partition]
        P1[Primary<br/>write({_id: 1, x: 5})<br/>acknowledged]
        S1[Secondary 1<br/>replicated x=5]
        S2[Secondary 2<br/>not yet replicated]
    end

    subgraph DuringPartition[During Partition]
        PP[Primary (isolated)<br/>steps down<br/>no majority]
        SP1[Secondary 1<br/>becomes primary<br/>continues operations]
        SP2[Secondary 2<br/>joins new primary]
    end

    subgraph AfterPartition[After Partition Heals]
        OP[Old Primary<br/>rollback file created<br/>x=5 rolled back]
        NP[New Primary<br/>x=5 never existed<br/>linearizability violation]
    end

    P1 --> PP
    S1 --> SP1
    S2 --> SP2

    PP --> OP
    SP1 --> NP

    classDef beforeStyle fill:#10B981,stroke:#059669,color:#fff
    classDef duringStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef afterStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class P1,S1,S2 beforeStyle
    class PP,SP1,SP2 duringStyle
    class OP,NP afterStyle
```

## Cassandra LWT Race Condition

```mermaid
sequenceDiagram
    participant C1 as Client 1
    participant C2 as Client 2
    participant N1 as Node 1 (Coordinator)
    participant N2 as Node 2
    participant N3 as Node 3

    Note over C1,N3: Cassandra Lightweight Transaction Bug

    C1->>N1: INSERT INTO users (id, email) VALUES (1, 'user@example.com') IF NOT EXISTS
    C2->>N1: INSERT INTO users (id, email) VALUES (1, 'admin@example.com') IF NOT EXISTS

    Note over N1,N3: Paxos Phase 1: Prepare

    par Parallel Prepares
        N1->>N2: prepare(ballot=1)
        N1->>N3: prepare(ballot=2)
    end

    par Promise Responses
        N2->>N1: promise(ballot=1, no previous value)
        N3->>N1: promise(ballot=2, no previous value)
    end

    Note over N1,N3: Paxos Phase 2: Accept (Race condition)

    par Concurrent Accepts
        N1->>N2: accept(ballot=1, 'user@example.com')
        N1->>N3: accept(ballot=2, 'admin@example.com')
    end

    par Accept Responses
        N2->>N1: accepted(ballot=1)
        N3->>N1: accepted(ballot=2)
    end

    Note over N1,N3: ❌ VIOLATION: Both operations succeeded
    Note over N1,N3: Expected: Only one should succeed

    N1-->>C1: [applied=true] (incorrect)
    N1-->>C2: [applied=true] (incorrect)

    Note over C1,N3: Root cause: Inconsistent ballot numbers across replicas
```

## Clock Skew Impact

```mermaid
graph LR
    subgraph ClockSkew[Clock Skew Scenario]
        N1[Node 1<br/>Clock: 10:00:00<br/>Fast by 30s]
        N2[Node 2<br/>Clock: 09:59:30<br/>Correct time]
        N3[Node 3<br/>Clock: 09:59:25<br/>Slow by 5s]
    end

    subgraph TimestampOrdering[Timestamp Ordering Issue]
        O1[Operation 1<br/>Node 1: 10:00:00<br/>Appears "latest"]
        O2[Operation 2<br/>Node 2: 09:59:30<br/>Actually latest]
        O3[Ordering Violation<br/>O1 before O2<br/>Breaks linearizability]
    end

    subgraph SpannerSolution[Google Spanner Solution]
        TT[TrueTime API<br/>GPS + Atomic clocks<br/>Uncertainty bounds]
        WU[Wait Uncertainty<br/>Delay commit until<br/>timestamp certainty]
        GO[Global Ordering<br/>Consistent timestamps<br/>across datacenters]
    end

    N1 --> O1
    N2 --> O2
    O1 --> O3
    O2 --> O3

    TT --> WU
    WU --> GO

    classDef skewStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef orderStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef solutionStyle fill:#10B981,stroke:#059669,color:#fff

    class N1,N2,N3 skewStyle
    class O1,O2,O3 orderStyle
    class TT,WU,GO solutionStyle
```

## Disk Corruption Failures

```mermaid
graph TB
    subgraph CorruptionTypes[Disk Corruption Types]
        C1[WAL Corruption<br/>Write-ahead log damaged<br/>Cannot replay operations]
        C2[Snapshot Corruption<br/>State machine backup<br/>Inconsistent checkpoint]
        C3[Index Corruption<br/>B-tree structure damaged<br/>Cannot find keys]
        C4[Silent Corruption<br/>Data changed without detection<br/>Checksum failures]
    end

    subgraph ImpactAnalysis[Impact on Linearizability]
        I1[Lost Operations<br/>Committed writes disappear<br/>Acknowledged data lost]
        I2[Inconsistent State<br/>Replicas diverge<br/>Different read results]
        I3[Split Brain<br/>Corrupted node believes<br/>it has authority]
        I4[Data Resurrection<br/>Old values reappear<br/>After newer writes]
    end

    subgraph MitigationStrategies[Mitigation Strategies]
        M1[Checksums<br/>End-to-end verification<br/>CRC32, SHA256]
        M2[Replication<br/>Multiple copies<br/>Voting on correct data]
        M3[Regular Verification<br/>Background scrubbing<br/>Detect corruption early]
        M4[Hardware Monitoring<br/>SMART data analysis<br/>Predictive replacement]
    end

    C1 --> I1
    C2 --> I2
    C3 --> I3
    C4 --> I4

    I1 --> M1
    I2 --> M2
    I3 --> M3
    I4 --> M4

    classDef corruptionStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef impactStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef mitigationStyle fill:#10B981,stroke:#059669,color:#fff

    class C1,C2,C3,C4 corruptionStyle
    class I1,I2,I3,I4 impactStyle
    class M1,M2,M3,M4 mitigationStyle
```

## Real-World Failure Examples

### GitHub MySQL Outage (2018)

```mermaid
sequenceDiagram
    participant US as US East (Primary)
    participant EU as EU West (Replica)
    participant APP as Applications

    Note over US,APP: Normal replication

    US->>EU: Binary log replication
    APP->>US: writes
    APP->>EU: reads (with lag)

    Note over US,EU: Network connectivity issues

    US--xEU: Replication lag increases to 5+ minutes

    Note over US: Primary becomes overloaded

    US->>US: Promotes EU to primary (incorrect decision)

    Note over EU: Now accepting writes

    APP->>EU: writes (data written to old snapshot)

    Note over US,EU: Split brain condition

    par Concurrent Writes
        APP->>US: write(user_1, data_a)
        APP->>EU: write(user_1, data_b)
    end

    Note over US,EU: Manual intervention required
    Note over US,APP: Result: Data loss and inconsistency
    Note over US,APP: Linearizability violation: reads returned stale data
```

### etcd Network Asymmetry Bug

```mermaid
graph TB
    subgraph NetworkTopology[Network Topology]
        L[Leader (Node A)<br/>Can send to B, C<br/>Cannot receive from C]
        F1[Follower B<br/>Full connectivity]
        F2[Follower C<br/>Can send to A, B<br/>A cannot receive]
    end

    subgraph FailureScenario[Asymmetric Partition]
        S1[Leader sends heartbeats<br/>to both followers]
        S2[Follower C cannot<br/>acknowledge heartbeats]
        S3[Leader thinks C is down<br/>but C thinks leader is up]
        S4[Split brain potential<br/>Both accept writes]
    end

    subgraph Resolution[Bug Fix]
        R1[Bidirectional heartbeats<br/>Required for leadership]
        R2[Jepsen testing<br/>Discovered the issue]
        R3[Improved failure detection<br/>More robust networking]
    end

    L --> S1
    F1 --> S1
    F2 --> S2

    S1 --> S3
    S2 --> S3
    S3 --> S4

    S4 --> R1
    R1 --> R2
    R2 --> R3

    classDef networkStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef failureStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef resolutionStyle fill:#10B981,stroke:#059669,color:#fff

    class L,F1,F2 networkStyle
    class S1,S2,S3,S4 failureStyle
    class R1,R2,R3 resolutionStyle
```

## Failure Detection and Recovery

```mermaid
graph LR
    subgraph Detection[Failure Detection - Blue]
        FD1[Heartbeat Monitoring<br/>Regular liveness checks<br/>Timeout-based detection]
        FD2[Health Checks<br/>Application-level probes<br/>Deep health validation]
        FD3[External Monitoring<br/>Third-party observers<br/>Avoid false positives]
    end

    subgraph Response[Failure Response - Green]
        FR1[Leader Election<br/>Automatic failover<br/>Raft/Paxos protocols]
        FR2[Client Redirection<br/>Route to new leader<br/>Transparent recovery]
        FR3[State Reconciliation<br/>Sync divergent replicas<br/>Conflict resolution]
    end

    subgraph Recovery[Recovery Process - Orange]
        RC1[Node Rejoin<br/>Catch-up replication<br/>Log replay mechanism]
        RC2[Split Brain Resolution<br/>Quorum-based decisions<br/>Epoch/term numbers]
        RC3[Data Repair<br/>Checksum verification<br/>Anti-entropy protocols]
    end

    subgraph Prevention[Prevention - Red]
        PV1[Circuit Breakers<br/>Fail fast mechanisms<br/>Prevent cascading failures]
        PV2[Chaos Engineering<br/>Regular failure injection<br/>Validate assumptions]
        PV3[Monitoring & Alerting<br/>Early warning systems<br/>Proactive intervention]
    end

    classDef detectionStyle fill:#3B82F6,stroke:#2563EB,color:#fff
    classDef responseStyle fill:#10B981,stroke:#059669,color:#fff
    classDef recoveryStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef preventionStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff

    class FD1,FD2,FD3 detectionStyle
    class FR1,FR2,FR3 responseStyle
    class RC1,RC2,RC3 recoveryStyle
    class PV1,PV2,PV3 preventionStyle
```

## Testing Failure Scenarios

```python
# Jepsen test for linearizability violations
def test_partition_during_write():
    """Test linearizability during network partition"""

    # Setup: 3-node cluster
    cluster = setup_cluster(nodes=3)

    # Step 1: Normal operation
    client1.write("key1", "value1")
    assert client2.read("key1") == "value1"

    # Step 2: Inject network partition
    # Isolate node3 from nodes 1,2
    nemesis.partition([node1, node2], [node3])

    # Step 3: Concurrent operations
    future1 = async_write(client1, "key2", "value2")  # to majority
    future2 = async_write(client2, "key2", "value3")  # to minority

    # Step 4: Heal partition
    nemesis.heal_partition()

    # Step 5: Validate linearizability
    result1 = future1.get()
    result2 = future2.get()

    # Only one write should succeed
    assert (result1.success and not result2.success) or \
           (not result1.success and result2.success)

    # All nodes should converge to same value
    assert cluster.validate_convergence()

def test_leader_crash_during_consensus():
    """Test behavior when leader crashes during consensus"""

    cluster = setup_cluster(nodes=5)

    # Start write operation
    write_future = async_write(client, "key", "value")

    # Crash leader after log entry but before commit
    time.sleep(0.01)  # Let log entry propagate
    nemesis.crash_node(cluster.leader)

    # Wait for leader election
    cluster.wait_for_leader_election()

    # Verify operation outcome
    result = write_future.get()

    if result.success:
        # If write succeeded, all nodes must have the value
        assert all(node.read("key") == "value" for node in cluster.nodes)
    else:
        # If write failed, no node should have the value
        assert all(node.read("key") is None for node in cluster.nodes)
```

## Common Anti-Patterns

```mermaid
graph TB
    subgraph AntiPatterns[Common Anti-Patterns]
        AP1[❌ Ignoring Timeouts<br/>Assuming operations succeed<br/>No retry logic]
        AP2[❌ Split Brain Acceptance<br/>Allowing multiple leaders<br/>Last writer wins]
        AP3[❌ Optimistic Assumptions<br/>Assuming network reliability<br/>No failure handling]
        AP4[❌ Inadequate Testing<br/>Only happy path testing<br/>No chaos engineering]
    end

    subgraph Consequences[Consequences]
        C1[Data Loss<br/>Acknowledged writes lost<br/>Customer impact]
        C2[Inconsistent Reads<br/>Different clients see<br/>different values]
        C3[Availability Impact<br/>System unavailable<br/>during failures]
        C4[Corruption<br/>Invalid system state<br/>Recovery required]
    end

    subgraph BestPractices[Best Practices]
        BP1[✅ Proper Error Handling<br/>Handle all failure modes<br/>Graceful degradation]
        BP2[✅ Comprehensive Testing<br/>Jepsen-style validation<br/>All failure scenarios]
        BP3[✅ Monitoring & Alerting<br/>Real-time health checks<br/>Early failure detection]
        BP4[✅ Clear Consistency Model<br/>Document guarantees<br/>Client expectations]
    end

    AP1 --> C1
    AP2 --> C2
    AP3 --> C3
    AP4 --> C4

    C1 --> BP1
    C2 --> BP2
    C3 --> BP3
    C4 --> BP4

    classDef antiStyle fill:#8B5CF6,stroke:#7C3AED,color:#fff
    classDef consequenceStyle fill:#F59E0B,stroke:#D97706,color:#fff
    classDef practiceStyle fill:#10B981,stroke:#059669,color:#fff

    class AP1,AP2,AP3,AP4 antiStyle
    class C1,C2,C3,C4 consequenceStyle
    class BP1,BP2,BP3,BP4 practiceStyle
```

## Incident Response Playbook

### Immediate Response (0-15 minutes)
1. **Detect the Issue**
   - Monitor alerts for consensus failures
   - Check leader election frequency
   - Validate read/write success rates

2. **Assess Impact**
   - Determine affected operations
   - Check data consistency across replicas
   - Identify client impact

3. **Contain the Issue**
   - Stop writes if data corruption suspected
   - Redirect traffic to healthy nodes
   - Prevent cascading failures

### Investigation (15-60 minutes)
1. **Gather Data**
   - Collect consensus logs from all nodes
   - Check network connectivity between nodes
   - Analyze timing of operations

2. **Identify Root Cause**
   - Network partition vs node failure
   - Software bug vs hardware issue
   - Configuration error vs load spike

### Recovery (60+ minutes)
1. **Restore Service**
   - Heal network partitions
   - Restart failed nodes
   - Rebuild corrupted data

2. **Validate Consistency**
   - Run linearizability tests
   - Check data integrity
   - Verify all nodes converged

3. **Post-Incident**
   - Document lessons learned
   - Update monitoring and alerting
   - Improve testing coverage

## Key Takeaways

1. **Linearizability failures are subtle** - Often appear as data inconsistencies rather than obvious errors
2. **Network partitions are the primary threat** - Split brain scenarios violate linearizability
3. **Testing is crucial** - Jepsen and chaos engineering find real bugs
4. **Implementation matters** - Even well-designed algorithms can have bugs
5. **Monitoring is essential** - Early detection prevents data corruption
6. **Recovery procedures must be tested** - Incident response requires practice
7. **Human factors are significant** - Operational errors often cause violations

Understanding these failure modes is essential for operating linearizable systems in production and maintaining data consistency guarantees.