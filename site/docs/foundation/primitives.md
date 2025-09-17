# Layer 2: The 20 Primitives (Extended)

Primitives are the fundamental building blocks that provide capabilities. Each primitive has clear triggers for when to use it, implementation patterns, and success criteria.

| **ID** | **Primitive** | **Trigger** | **Provides** | **Implementation** | **Proof** | **Anti-patterns** |
|---|---|---|---|---|---|---|
| P1 | **Partitioning** | >20K writes/sec OR >100GB | ElasticScale, HotspotMitigation | Hash: even distribution<br/>Range: ordered scans<br/>Geographic: locality | Load variance <2x<br/>No hot partitions >10% | Global secondary indexes<br/>Cross-partition transactions |
| P2 | **Replication** | RPO<60s OR RTO<30s | Durability, ReadScale | Sync: strong consistency<br/>Async: performance<br/>Quorum: balance | Failover <RTO<br/>Data loss <RPO | Writing to replicas<br/>Ignoring lag |
| P3 | **Durable Log** | Audit OR event sourcing | Replayability, Order | Append-only<br/>Compaction<br/>Retention policies | Replay identical state<br/>No gaps in sequence | Mutable events<br/>Infinite retention |
| P4 | **Specialized Index** | Query diversity >1K | FastLookup, RangeScans | B-tree: range<br/>Hash: exact<br/>Inverted: text<br/>Spatial: geo | Index usage >90%<br/>Maintenance <5% writes | Over-indexing<br/>Unused indexes |
| P5 | **Consensus** | Distributed coordination | Linearizability, LeaderElection | Raft: understandable<br/>Paxos: proven<br/>PBFT: Byzantine | Jepsen passes<br/>Split-brain prevented | Using for data path<br/>Even node count |
| P6 | **Causal Tracking** | User-visible ordering | CausalOrder | Vector clocks: accurate<br/>HLC: bounded size<br/>Session tokens: simple | No causal violations<br/>Bounded clock size | Global ordering attempt<br/>Unbounded vectors |
| P7 | **Idempotency** | Any retry scenario | ExactlyOnceEffect | UUID: simple<br/>Hash: deterministic<br/>Version: optimistic | Duplicate = no-op<br/>Concurrent handling | Weak keys<br/>No TTL |
| P8 | **Retry Logic** | Network operations | FaultTolerance | Exponential backoff<br/>Jitter<br/>Circuit breaking | No retry storms<br/>Budget respected | Infinite retries<br/>No backoff |
| P9 | **Circuit Breaker** | Unreliable dependencies | FailFast, Isolation | Error rate threshold<br/>Latency threshold<br/>Half-open probes | Recovery <1min<br/>Cascades prevented | Global breaker<br/>No fallback |
| P10 | **Bulkheading** | Multi-tenant | Isolation, Fairness | Thread pools<br/>Connection pools<br/>Queue isolation | Noisy neighbor isolated<br/>Fair scheduling | Shared resources<br/>Unbounded queues |
| P11 | **Caching** | Read/Write >10:1 | LatencyReduction | Write-through: consistency<br/>Write-back: performance<br/>Aside: flexibility | Hit ratio >90%<br/>Staleness <SLO | No invalidation<br/>Cache-only state |
| P12 | **Load Shedding** | Overload risk | GracefulDegradation | Random: simple<br/>Priority: smart<br/>Adaptive: dynamic | Critical preserved<br/>Graceful degradation | Silent drops<br/>All-or-nothing |
| P13 | **Sharded Locks** | High contention | Concurrency | Partition locks<br/>Range locks<br/>Hierarchical | Deadlock <1%<br/>Fair acquisition | Global locks<br/>No timeout |
| P14 | **Write-Ahead Log** | Durability+Performance | CrashRecovery | Sequential writes<br/>Group commit<br/>Checkpointing | Recovery correct<br/>Performance gain | Sync every write<br/>No checkpoints |
| P15 | **Bloom Filter** | Existence checks | SpaceSaving | False positive OK<br/>No false negatives<br/>Size calculation | Error rate <target<br/>Space saved >10x | When FP unacceptable<br/>Dynamic sets |
| P16 | **Merkle Tree** | Data verification | EfficientSync | Hash tree<br/>Diff detection<br/>Proof generation | Sync bandwidth <10%<br/>Corruption detected | Frequent updates<br/>Small datasets |
| P17 | **Vector Clock** | Distributed ordering | CausalTracking | Per-node counter<br/>Merge on receive<br/>Prune old entries | Causality preserved<br/>Size bounded | When timestamp enough<br/>Many nodes |
| P18 | **Gossip Protocol** | Information spread | EventualDelivery | Epidemic spread<br/>Anti-entropy<br/>Rumor mongering | Convergence <O(log N)<br/>Message overhead low | Urgent updates<br/>Large messages |
| P19 | **Change Data Capture** | Stream from DB | EventStream | Logical replication<br/>Binlog tailing<br/>Triggers (avoid) | No events lost<br/>Order preserved | Dual writes<br/>Polling |
| P20 | **Feature Flags** | Progressive rollout | SafeDeployment | Percentage rollout<br/>User targeting<br/>Circuit breaker | Instant rollback<br/>No restart needed | Complex nesting<br/>Permanent flags |

## Primitive Interactions

### Incompatible Combinations
- P5 (Consensus) + P11 (Caching) in critical path → Latency violation
- P1 (Partitioning) + P5 (Consensus) across partitions → Deadlock risk
- P7 (Idempotency) + P11 (Caching) without invalidation → Stale state

### Synergistic Combinations
- P3 (Durable Log) + P19 (CDC) → Event sourcing foundation
- P1 (Partitioning) + P4 (Indexes) → Distributed query capability
- P8 (Retry) + P9 (Circuit Breaker) → Robust failure handling
- P2 (Replication) + P5 (Consensus) → Strong consistency with availability

### Required Combinations
- P7 (Idempotency) always needs P8 (Retry Logic)
- P19 (CDC) requires P3 (Durable Log) or P14 (WAL)
- P12 (Load Shedding) needs P10 (Bulkheading) for isolation

## Implementation Checklist

For each primitive, verify:

### P1 - Partitioning
- [ ] Partition key chosen to avoid hotspots
- [ ] Rebalancing strategy defined
- [ ] Cross-partition query strategy
- [ ] Monitoring partition distribution

### P2 - Replication  
- [ ] Replication factor matches durability needs
- [ ] Lag monitoring implemented
- [ ] Failover procedures tested
- [ ] Read preference strategy defined

### P3 - Durable Log
- [ ] Append-only storage verified
- [ ] Compaction policy implemented
- [ ] Retention policy defined
- [ ] Replay procedure tested

### P5 - Consensus
- [ ] Odd number of nodes
- [ ] Network partition handling tested
- [ ] Leadership election timeout tuned
- [ ] Split-brain prevention verified

### P11 - Caching
- [ ] Cache invalidation strategy implemented
- [ ] TTL appropriate for data freshness needs
- [ ] Cache-aside vs write-through chosen correctly
- [ ] Hit ratio monitoring implemented

## Capacity Planning

Each primitive has specific capacity characteristics:

```yaml
primitive_capacity:
  P1_Partitioning:
    write_throughput: 20000 per partition
    read_throughput: 100000 per partition
    storage: unlimited per partition
    
  P2_Replication:
    write_latency_overhead: 1-5ms per replica
    storage_overhead: replication_factor * base
    network_overhead: replication_factor * write_size
    
  P5_Consensus:
    write_latency: 2-10ms (network + consensus)
    throughput_limit: 10000 writes/sec typical
    node_limit: 5-7 nodes practical maximum
    
  P11_Caching:
    memory_requirement: working_set_size * 1.3
    lookup_latency: <1ms for in-memory
    throughput: 50000+ ops/sec per node
```