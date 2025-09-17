# Guarantees Diagram Specifications v2.0
## Meaningful Visualizations for Consistency Models

### Overview
Each of the 18 guarantees needs 6 specific diagrams that actually explain what the guarantee means, how it works, and when to use it. Total: 108 diagrams.

---

## Example: Linearizability (Complete Specification)

### Diagram 1: CONCEPT - What Linearizability Means
```yaml
id: G-LIN-CONCEPT
type: timeline
title: "Linearizability: Operations Appear Atomic"
purpose: "Show that operations appear to happen instantaneously at some point between start and end"

timeline:
  clients:
    - id: alice
      operations:
        - op: "SET x=1"
          start: t0
          end: t2
          linearization_point: t1  # The "atomic" moment
    - id: bob
      operations:
        - op: "GET x"
          start: t3  # After Alice's operation completes
          end: t4
          result: "x=1"  # MUST see Alice's write

  violation_example:
    description: "What linearizability prevents"
    - alice: "SET x=1" completes at t2
    - bob: "GET x" at t3 returns x=0
    - annotation: "IMPOSSIBLE with linearizability - Bob must see x=1"

key_insight: |
  Linearizability provides the illusion that each operation happens
  instantaneously at some point between its start and completion.
  Once an operation completes, ALL subsequent operations must see its effects.

real_world_analogy: |
  Like a physical lock on a door - once you turn the key (operation completes),
  everyone who tries the door afterward sees it as locked. There's no delay
  or eventual consistency - the state change is immediate and visible to all.
```

### Diagram 2: IMPLEMENTATION - etcd/Raft in Production
```yaml
id: G-LIN-IMPLEMENTATION
type: architecture
title: "etcd: Production Linearizable Key-Value Store"
purpose: "Show how Raft consensus provides linearizability in practice"

components:
  client_layer:
    etcd_client:
      library: "etcd-client-go v3.5"
      features:
        - "Automatic endpoint discovery"
        - "Client-side load balancing"
        - "Retry with backoff"

  api_layer:
    grpc_server:
      port: 2379
      max_connections: 10000
      tls: "required for production"
      rate_limits:
        per_client: "10K ops/sec"

  consensus_layer:
    raft_cluster:
      nodes: 5  # Tolerates 2 failures
      leader:
        term: 42
        commit_index: 1000000
        applied_index: 999998
        performance:
          writes_per_sec: 10000
          fsync_p99: "10ms (NVMe SSD)"

      followers:
        count: 4
        replication:
          protocol: "Streaming AppendEntries"
          batch_size: 64KB
          lag_p99: "5ms"

      election:
        timeout: "1000-2000ms (randomized)"
        heartbeat_interval: "100ms"

  storage_layer:
    bbolt:
      database_size: "8GB"
      page_size: "4KB"
      b+tree_depth: 4

    wal:
      segment_size: "64MB"
      sync_policy: "every_commit"
      compression: "snappy"

critical_path_latency:
  write_operation:
    1_client_to_leader: "1ms (same DC)"
    2_leader_log_append: "0.5ms"
    3_leader_to_followers: "2ms"
    4_followers_log_append: "0.5ms"
    5_followers_ack: "2ms"
    6_leader_commit: "0.5ms"
    7_leader_apply: "1ms"
    8_leader_fsync: "10ms (NVMe)"
    9_response_to_client: "1ms"
    total_p50: "15ms"
    total_p99: "50ms"

production_examples:
  - company: "Kubernetes"
    usage: "Cluster state storage"
    scale: "5000 nodes, 150K pods"

  - company: "CoreOS/RedHat"
    usage: "Configuration management"
    scale: "10K writes/sec sustained"
```

### Diagram 3: COMPARISON - Linearizable vs Eventually Consistent
```yaml
id: G-LIN-COMPARISON
type: side_by_side
title: "Linearizability vs Eventual Consistency: The Trade-off"
purpose: "Show the concrete trade-offs between consistency models"

linearizable_side:
  implementation: "etcd with Raft"

  guarantees:
    consistency: "Strong - all reads see latest write"
    ordering: "Total order of all operations"
    causality: "Preserves real-time ordering"

  performance:
    write_latency:
      p50: "15ms"
      p99: "50ms"
      p999: "200ms"
    read_latency:
      p50: "2ms (from leader)"
      p99: "5ms"
    throughput:
      writes: "10K/sec (leader bottleneck)"
      reads: "50K/sec (with follower reads)"

  availability:
    during_partition: "Minority partition: UNAVAILABLE"
    failure_tolerance: "N/2-1 nodes can fail"
    CAP_choice: "CP - Consistency over Availability"

  use_cases:
    perfect_for:
      - "Configuration management (Kubernetes)"
      - "Distributed locking (Consul)"
      - "Service discovery (etcd)"
      - "Leader election"

    avoid_for:
      - "High-volume metrics"
      - "Shopping carts"
      - "Social media feeds"

eventually_consistent_side:
  implementation: "Cassandra with Quorum"

  guarantees:
    consistency: "Eventual - temporary divergence allowed"
    ordering: "Per-partition ordering only"
    causality: "Not preserved across partitions"

  performance:
    write_latency:
      p50: "2ms"
      p99: "10ms"
      p999: "50ms"
    read_latency:
      p50: "2ms"
      p99: "10ms"
    throughput:
      writes: "100K/sec (horizontal scaling)"
      reads: "500K/sec (horizontal scaling)"

  availability:
    during_partition: "All partitions: AVAILABLE"
    failure_tolerance: "N-1 nodes can fail"
    CAP_choice: "AP - Availability over Consistency"

  use_cases:
    perfect_for:
      - "User activity feeds"
      - "Product catalogs"
      - "Metrics and logs"
      - "Shopping carts"

    avoid_for:
      - "Bank accounts"
      - "Distributed locks"
      - "Configuration data"

key_trade_off: |
  10x latency penalty for strong consistency
  10x throughput advantage for eventual consistency

  Choose based on your consistency requirements, not default preferences!
```

### Diagram 4: FAILURE - Behavior During Network Partition
```yaml
id: G-LIN-FAILURE
type: failure_scenario
title: "Linearizability During Network Partition"
purpose: "Show how linearizability behaves when the network splits"

scenario:
  initial_state:
    cluster: [node1(leader), node2, node3, node4, node5]
    writes_per_sec: 1000
    read_per_sec: 5000

  failure_event:
    type: "Network partition"
    time: "T0"
    result:
      partition_a: [node1(leader), node2]  # Minority - 2 nodes
      partition_b: [node3, node4, node5]   # Majority - 3 nodes

  behavior:
    partition_a_minority:
      T0_to_T1:
        duration: "1 second (election timeout)"
        status: "Still thinks it's leader"
        writes: "ACCEPTING (but will be rolled back)"
        reads: "SERVING (stale, about to lose leadership)"

      after_T1:
        status: "Realizes lost quorum"
        leader: "Steps down"
        writes: "REJECTING - 'no leader' error"
        reads: "REJECTING - could return stale data"
        client_errors: "etcdserver: no leader"

    partition_b_majority:
      T0_to_T1:
        duration: "1-2 seconds"
        status: "Detecting leader timeout"
        writes: "REJECTING - no leader"
        reads: "REJECTING - safety first"

      T1_to_T2:
        duration: "0.5 seconds"
        status: "Election in progress"
        new_leader: "node3 wins election"

      after_T2:
        status: "New leader elected"
        writes: "ACCEPTING - full functionality"
        reads: "SERVING - linearizable"
        note: "Continues without minority"

  data_consistency:
    minority_writes: "Lost - never committed"
    majority_writes: "Preserved - continue normally"
    split_brain: "IMPOSSIBLE - only majority can have leader"

  client_experience:
    connected_to_minority:
      errors: "No leader available"
      required_action: "Reconnect to majority partition"
      data_loss: "Any uncomitted writes lost"

    connected_to_majority:
      errors: "Brief unavailability (2-3 seconds)"
      required_action: "Retry with exponential backoff"
      data_loss: "None"

recovery:
  when_partition_heals:
    1_reconnect: "Nodes reconnect at T_heal"
    2_log_comparison: "Minority nodes discover divergent logs"
    3_rollback: "Minority discards uncommitted entries"
    4_catch_up: "Minority replicates from new leader"
    5_normal_operation: "Cluster fully functional again"
    time_to_recover: "< 1 second after network heals"
```

### Diagram 5: PERFORMANCE - Cost of Linearizability
```yaml
id: G-LIN-PERFORMANCE
type: performance_profile
title: "The Cost of Linearizability"
purpose: "Show the performance characteristics and limits"

benchmark_setup:
  hardware:
    nodes: 5
    cpu: "16 cores @ 2.4GHz"
    memory: "32GB"
    disk: "NVMe SSD (100K IOPS)"
    network: "10Gbps within DC"

  cluster:
    etcd_version: "3.5.5"
    raft_implementation: "etcd-raft"
    configuration:
      snapshot_count: 100000
      heartbeat_ms: 100
      election_timeout_ms: 1000

performance_results:
  throughput:
    small_values_256B:
      writes: "15K ops/sec"
      reads_from_leader: "50K ops/sec"
      reads_follower_linearizable: "30K ops/sec"

    large_values_1MB:
      writes: "500 ops/sec"
      reads: "2K ops/sec"
      bottleneck: "Network bandwidth"

  latency:
    writes:
      p50: "15ms"
      p99: "50ms"
      p999: "200ms"
      max: "5000ms (during leader election)"

    reads:
      p50: "2ms"
      p99: "5ms"
      p999: "20ms"

  resource_usage:
    cpu:
      leader: "60% (serialization + replication)"
      follower: "20% (replication + snapshots)"

    memory:
      per_node: "2GB heap + 8GB page cache"
      growth_rate: "100MB per million keys"

    disk:
      write_rate: "50MB/s sustained"
      iops: "5000 sustained, 20K burst"
      wal_size: "8GB (before compaction)"

    network:
      intra_cluster: "100Mbps per follower"
      client_traffic: "200Mbps"

bottlenecks:
  1_leader_cpu:
    issue: "Single-threaded Raft loop"
    impact: "Limits to ~15K writes/sec"
    mitigation: "Multi-raft (shard keyspace)"

  2_disk_fsync:
    issue: "Every commit requires fsync"
    impact: "Adds 10ms to write latency"
    mitigation: "Use faster NVMe, batch commits"

  3_network_rtt:
    issue: "Replication to followers"
    impact: "Cross-region adds 100ms+"
    mitigation: "Regional clusters with federation"

scaling_limits:
  vertical:
    max_single_cluster_writes: "30K/sec (with tuning)"
    limiting_factor: "Leader CPU saturation"

  horizontal:
    sharding_strategy: "Hash keyspace into ranges"
    shards: "Can scale to 100+ shards"
    complexity: "Client routing, cross-shard transactions"

comparison_with_alternatives:
  vs_mysql:
    writes: "MySQL: 50K/sec, etcd: 15K/sec"
    consistency: "MySQL: configurable, etcd: always strong"
    failure_handling: "MySQL: manual failover, etcd: automatic"

  vs_dynamodb:
    writes: "DynamoDB: 1M/sec, etcd: 15K/sec"
    consistency: "DynamoDB: eventual, etcd: linearizable"
    cost: "DynamoDB: $$$, etcd: $ (self-hosted)"
```

### Diagram 6: DECISION - When to Use Linearizability
```yaml
id: G-LIN-DECISION
type: decision_tree
title: "Should You Use Linearizability?"
purpose: "Guide the choice of consistency model"

start: "What are you building?"

decision_tree:
  configuration_management:
    question: "Storing configuration?"
    yes:
      answer: "✅ USE LINEARIZABLE"
      reason: "Config must be consistent across cluster"
      examples:
        - "Kubernetes → etcd"
        - "Consul → Raft consensus"
        - "Apache Kafka → ZooKeeper (moving to KRaft)"
    no: → next_question

  distributed_coordination:
    question: "Need distributed locks/leaders?"
    yes:
      answer: "✅ USE LINEARIZABLE"
      reason: "Prevents split-brain, ensures single leader"
      examples:
        - "Service mesh leader election"
        - "Distributed cron (only one runs)"
        - "Database primary selection"
    no: → next_question

  financial_transactions:
    question: "Handling money/credits?"
    yes:
      question: "Need strict ordering?"
      yes:
        answer: "✅ USE LINEARIZABLE"
        reason: "Prevent double-spending, ensure order"
        examples:
          - "Payment processing"
          - "Account balances"
          - "Inventory decrement"
      no:
        answer: "⚠️ DEPENDS"
        reason: "May use eventual + compensations"
        examples:
          - "PayPal (eventual + reconciliation)"
          - "Stripe (mixed models)"
    no: → next_question

  user_data:
    question: "Storing user content?"
    yes:
      question: "OK with temporary inconsistency?"
      yes:
        answer: "❌ USE EVENTUAL"
        reason: "Better performance, availability"
        examples:
          - "Social media posts → Cassandra"
          - "Shopping carts → DynamoDB"
          - "User profiles → MongoDB"
      no:
        answer: "✅ USE LINEARIZABLE"
        examples:
          - "Password changes"
          - "Privacy settings"
          - "Account deletion"
    no: → next_question

  metrics_and_logs:
    question: "Collecting metrics/logs?"
    yes:
      answer: "❌ USE EVENTUAL"
      reason: "Volume too high, loss acceptable"
      examples:
        - "Prometheus → local storage + eventual"
        - "Elasticsearch → eventual consistency"
        - "CloudWatch → eventual delivery"

  cache_layer:
    question: "Building a cache?"
    yes:
      answer: "❌ USE EVENTUAL (OR NONE)"
      reason: "Stale data acceptable by definition"
      examples:
        - "Redis → async replication"
        - "Memcached → no replication"
        - "CDN → eventual propagation"

migration_paths:
  from_eventual_to_linear:
    difficulty: "Hard"
    approach:
      1: "Add linearizable store alongside"
      2: "Migrate critical paths first"
      3: "Keep eventual for high-volume"
    example: "Twitter: Eventually consistent timeline + linearizable for payments"

  from_linear_to_eventual:
    difficulty: "Easier"
    approach:
      1: "Identify data that can be stale"
      2: "Add caching layer"
      3: "Move to eventual storage"
    example: "Netflix: Moved viewing history from consistent to eventual"

rule_of_thumb: |
  Start with eventual consistency (faster, simpler, cheaper)
  Add linearizability only where required (coordination, config, critical data)

  Most systems: 95% eventual, 5% linearizable
```

---

## Template for Other Guarantees

### Sequential Consistency
Focus on: "Operations appear in program order, but not real-time order"
- Show how it differs from linearizability (no real-time requirement)
- Implementation: Most SQL databases in "read committed" mode
- Use cases: Where order matters but exact timing doesn't

### Eventual Consistency
Focus on: "All nodes converge to the same value eventually"
- Show divergence and convergence over time
- Implementation: Cassandra, DynamoDB, S3
- Include anti-entropy mechanisms

### Causal Consistency
Focus on: "Preserves causally related operations"
- Show happens-before relationships
- Implementation: MongoDB with causal sessions
- Vector clocks or hybrid logical clocks

### Read-Your-Writes
Focus on: "You always see your own writes"
- Show session stickiness requirements
- Implementation: DynamoDB with consistent reads
- Cost vs eventual reads

### Monotonic Reads
Focus on: "Never go backward in time"
- Show the problem it prevents (seeing old data after new)
- Implementation: Bounded staleness in CosmosDB
- Token/timestamp tracking

---

## Quality Checklist for Guarantee Diagrams

### Must Have:
- [ ] Shows specific guarantee behavior (not generic consistency)
- [ ] Includes real implementation (etcd, Cassandra, etc.)
- [ ] Has production metrics (latency, throughput)
- [ ] Shows failure behavior
- [ ] Includes decision criteria
- [ ] References actual use cases

### Must NOT Have:
- [ ] Generic "Service A, Service B"
- [ ] Abstract "Write X, Read Y"
- [ ] Made-up metrics
- [ ] Happy path only
- [ ] No real examples

---

## The Goal

After viewing these 6 diagrams for any guarantee, an engineer should:
1. Understand exactly what the guarantee provides
2. Know how to implement it in production
3. Understand the performance implications
4. Know how it behaves during failures
5. Be able to decide if they need it

If the diagrams don't achieve ALL of these, they need revision.