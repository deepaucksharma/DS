# Layer 2: The 20 Production-Tested Primitives

## The Production Reality

These primitives aren't theoretical - they're battle-tested at scale by Google, Netflix, Uber, and Meta. Each includes actual configurations, real performance numbers, and incident data.

Primitives are the fundamental building blocks running in production at billions of requests per second. Each primitive includes triggers from real incidents, implementation patterns from actual deployments, and success criteria from production SLOs.

| **ID** | **Primitive** | **Trigger** | **Provides** | **Implementation** | **Proof** | **Anti-patterns** |
|---|---|---|---|---|---|---|
| P1 | **Partitioning** | >20K writes/sec OR >100GB (Vitess@YouTube) | ElasticScale, HotspotMitigation | Hash: even distribution<br/>Range: ordered scans<br/>Geographic: locality<br/>**Vitess**: 10K MySQL shards | Load variance <2x<br/>No hot partitions >10%<br/>Linear scale to 1000+ shards | Global secondary indexes<br/>Cross-partition transactions |
| P2 | **Replication** | RPO<60s OR RTO<30s (MySQL@Facebook) | Durability, ReadScale | Sync: strong (+5ms latency)<br/>Async: performance<br/>Quorum: W+R>N<br/>**FB**: 5-way replication | Failover <30s<br/>Data loss <RPO<br/>Lag <100ms p99 | Writing to replicas<br/>Ignoring lag |
| P3 | **Durable Log** | Audit OR event sourcing | Replayability, Order | Append-only<br/>Compaction<br/>Retention policies | Replay identical state<br/>No gaps in sequence | Mutable events<br/>Infinite retention |
| P4 | **Specialized Index** | Query diversity >1K | FastLookup, RangeScans | B-tree: range<br/>Hash: exact<br/>Inverted: text<br/>Spatial: geo | Index usage >90%<br/>Maintenance <5% writes | Over-indexing<br/>Unused indexes |
| P5 | **Consensus** | Distributed coordination | Linearizability, LeaderElection | Raft: etcd (10K nodes max)<br/>Paxos: Spanner (5 replicas)<br/>PBFT: Byzantine<br/>Latency: +5-50ms | Jepsen passes<br/>Split-brain prevented<br/>Leader election <10s | Using for data path<br/>Even node count |
| P6 | **Causal Tracking** | User-visible ordering | CausalOrder | Vector clocks: accurate<br/>HLC: bounded size<br/>Session tokens: simple | No causal violations<br/>Bounded clock size | Global ordering attempt<br/>Unbounded vectors |
| P7 | **Idempotency** | Any retry scenario | ExactlyOnceEffect | UUID: simple<br/>Hash: deterministic<br/>Version: optimistic | Duplicate = no-op<br/>Concurrent handling | Weak keys<br/>No TTL |
| P8 | **Retry Logic** | Network operations | FaultTolerance | Exponential backoff<br/>Jitter<br/>Circuit breaking | No retry storms<br/>Budget respected | Infinite retries<br/>No backoff |
| P9 | **Circuit Breaker** | Unreliable dependencies | FailFast, Isolation | Error rate threshold<br/>Latency threshold<br/>Half-open probes | Recovery <1min<br/>Cascades prevented | Global breaker<br/>No fallback |
| P10 | **Bulkheading** | Multi-tenant | Isolation, Fairness | Thread pools<br/>Connection pools<br/>Queue isolation | Noisy neighbor isolated<br/>Fair scheduling | Shared resources<br/>Unbounded queues |
| P11 | **Caching** | Read/Write >10:1 | LatencyReduction | Write-through: consistency<br/>Write-back: performance<br/>Aside: flexibility<br/>**Memcached@FB**: 1B+ req/s | Hit ratio >99% (FB)<br/>Staleness <100ms<br/>p50: 0.2ms (cache hit) | No invalidation<br/>Cache stampede |
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

### Required Combinations (From Production Incidents)
- P7 (Idempotency) + P8 (Retry): Stripe processes $640B/year with exactly-once
- P19 (CDC) + P3 (Log): Debezium@Uber captures 1T events/day from MySQL binlog
- P12 (Load Shedding) + P10 (Bulkhead): Netflix saves 30% capacity during peak
- P9 (Circuit Breaker) + P8 (Retry): Prevents cascade failures (AWS S3 2017)

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

### P11 - Caching (Facebook Memcached Production Checklist)
- [ ] Cache invalidation strategy (McSqueal for MySQL->Memcached)
- [ ] TTL tuned (30s for user data, 5min for static)
- [ ] Cache-aside for reads, write-through for sessions
- [ ] Hit ratio >99% (FB achieves 99.25%)
- [ ] Stampede protection (request coalescing)
- [ ] Hot key detection (>10K req/s/key)
- [ ] Monitoring: hit rate, evictions, get/set latency

## Production Capacity (Real Numbers)

Each primitive has specific capacity characteristics from production:

```yaml
primitive_capacity:
  P1_Partitioning:
    # Vitess@YouTube actual numbers
    write_throughput: 20K per shard (MySQL limit)
    read_throughput: 100K per shard (with replicas)
    storage: 2TB practical per shard
    shards_tested: 10,000+ in production
    cost: $500/shard/month (AWS)

  P2_Replication:
    # Facebook MySQL production
    write_latency_overhead: +2ms same-DC, +50ms cross-region
    storage_overhead: 5x for 5-way replication
    network_overhead: 10Gbps per replica at peak
    lag_p99: 100ms (async), 5ms (semi-sync)

  P5_Consensus:
    # etcd production limits
    write_latency: 10ms p50, 100ms p99 (5 nodes)
    throughput_limit: 10K writes/sec (etcd v3.5)
    node_limit: 5 nodes (99.9% SLA), 7 nodes (99% SLA)
    database_size_limit: 10GB practical
    
  P11_Caching:
    memory_requirement: working_set_size * 1.3
    lookup_latency: <1ms for in-memory
    throughput: 50000+ ops/sec per node
```