# Layer 1: The 30 Capabilities (Complete Taxonomy)

Capabilities are the fundamental guarantees a distributed system can provide. Every system requirement maps to one or more of these 30 capabilities.

| **Category** | **Capability** | **Formal Definition** | **Measurement** | **Common Implementations** |
|---|---|---|---|---|
| **Consistency** | LinearizableWrite | ∀ ops: real_time_order = observed_order | Jepsen linearizability checker | Raft, Paxos, Zab |
| | SerializableTransaction | No cycles in serialization graph | TPC-C consistency checker | 2PL, SSI, Calvin |
| | ReadYourWrites | session.read reflects session.writes | Custom test harness | Session affinity, causal tokens |
| | MonotonicReads | Reads never go backward in time | Version number tracking | Bounded staleness, version vectors |
| | BoundedStaleness(t) | Age(data) ≤ t at read time | now() - data_timestamp ≤ t | TTL, refresh intervals |
| | EventualConsistency | limt→∞ P(all_equal) = 1 | Convergence time measurement | Anti-entropy, gossip |
| **Order** | PerKeyOrder | Events with same key processed in order | Sequence number validation | Kafka partitions, Kinesis shards |
| | CausalOrder | If a→b then observed(a) before observed(b) | Happens-before validator | Vector clocks, HLC |
| | TotalOrder | Global agreement on event order | Gap detection in sequence | Single partition, consensus |
| **Durability** | DurableWrite | Data survives planned/unplanned failures | Backup recovery test | Replicated logs, snapshots |
| | ExactlyOnceEffect | Operation effect applied exactly once | Duplicate injection test | Idempotency, deduplication |
| | AtLeastOnceDelivery | Message delivered ≥1 times | Missing message detection | Retry with ack |
| | AtMostOnceDelivery | Message delivered ≤1 times | Duplicate detection | No retry, fire-and-forget |
| **Performance** | SubMillisecondRead | P99 read < 1ms | Latency histograms | Memory stores, caching |
| | PredictableTail | P99/P50 < 10 | Latency percentile ratios | Bounded queues, timeouts |
| | ElasticScale | Linear scaling to 10x load | Load test scaling curve | Horizontal partitioning |
| | ConstantTime | O(1) operations | Algorithm analysis | Hash tables, indexes |
| **Availability** | HighAvailability | Uptime ≥ 99.9% | Success rate monitoring | Redundancy, failover |
| | FaultTolerance | Survives f failures | Chaos testing | Replication factor > f |
| | GracefulDegradation | Partial service > no service | Feature flag testing | Circuit breakers, bulkheads |
| **Security** | Confidentiality | Data readable only by authorized | Penetration testing | Encryption, access control |
| | Integrity | Data not tampered | Checksum validation | HMAC, digital signatures |
| | Authenticity | Source verification | Auth testing | mTLS, JWT |
| | NonRepudiation | Can't deny actions | Audit log completeness | Signed logs, blockchain |
| **Scalability** | HorizontalScale | Add nodes for more capacity | Linear scaling validation | Sharding, partitioning |
| | ElasticCapacity | Auto-scale with demand | Response time under load | Auto-scaling groups |
| | MultiTenancy | Isolated resource sharing | Tenant isolation testing | Resource quotas, namespaces |
| **Observability** | FullAuditTrail | Complete action history | Audit completeness check | Event sourcing, logs |
| | RealTimeMetrics | Current system state | Metric freshness | Time-series databases |
| | DistributedTracing | Request flow visibility | Trace completeness | Jaeger, Zipkin |

## Capability Relationships

### Mutual Exclusions
- `LinearizableWrite` ⟷ `HighAvailability` (during partitions)
- `SerializableTransaction` ⟷ `ElasticScale` (coordination overhead)
- `StrongConsistency` ⟷ `SubMillisecondRead` (consensus latency)

### Dependencies
- `SerializableTransaction` → `LinearizableWrite`
- `ReadYourWrites` → `MonotonicReads`
- `ExactlyOnceEffect` → `DurableWrite`
- `FaultTolerance` → `HighAvailability`

### Reinforcements
- `PredictableTail` + `BoundedQueues` → `SubMillisecondRead`
- `HorizontalScale` + `LoadBalancing` → `ElasticScale`
- `Encryption` + `AccessControl` → `Confidentiality`

## Usage Patterns

### Financial Systems
Required: `LinearizableWrite`, `SerializableTransaction`, `DurableWrite`, `FullAuditTrail`
Optional: `BoundedStaleness(1s)`, `HighAvailability`

### Social Media
Required: `EventualConsistency`, `ElasticScale`, `HighAvailability`
Optional: `PerKeyOrder`, `BoundedStaleness(5s)`

### Gaming
Required: `SubMillisecondRead`, `PredictableTail`, `ElasticScale`
Optional: `EventualConsistency`, `PerKeyOrder`

### Analytics
Required: `HorizontalScale`, `ElasticCapacity`, `FullAuditTrail`
Optional: `EventualConsistency`, `BoundedStaleness(1h)`

## Measurement Framework

Each capability must be continuously measured in production:

```yaml
capability_monitoring:
  LinearizableWrite:
    method: jepsen_continuous_checker
    frequency: sample_1_percent
    alert: any_violation
    
  BoundedStaleness:
    method: synthetic_timestamp_writes
    frequency: every_60_seconds
    alert: age > bound_for_5_minutes
    
  SubMillisecondRead:
    method: latency_histogram
    frequency: every_request
    alert: p99 > 1ms_for_5_minutes
```