# Diagram Specifications v2.0.0
## Semantic, Educational Diagrams for Distributed Systems

### Core Philosophy
Every diagram must **teach something specific** about distributed systems. No generic templates. No abstract examples. Real systems, real metrics, real failures.

---

## Diagram Categories and Requirements

### 1. CONCEPT DIAGRAMS (What Is It?)
**Purpose:** Explain the core concept in a way that creates an "aha!" moment

#### For Guarantees
Each guarantee needs a diagram showing:
- **The specific behavior** that guarantee provides
- **Counter-examples** showing what it prevents
- **Timeline visualization** of operations
- **Real-world analogy** if applicable

**Example: Linearizability Concept**
```yaml
diagram:
  type: timeline
  title: "Linearizability: Operations Appear Atomic"
  scenarios:
    correct:
      - client1: "SET x=1" at t0, completes at t1
      - client2: "GET x" at t2 (after t1), MUST see x=1
      - annotation: "Real-time ordering preserved"

    incorrect_prevented:
      - client1: "SET x=1" at t0, completes at t1
      - client2: "GET x" at t2, sees x=0
      - annotation: "VIOLATION - This cannot happen with linearizability"

  key_insight: "Once a write completes, ALL subsequent reads must see it"
```

#### For Mechanisms
Each mechanism needs a diagram showing:
- **Core components** and their roles
- **The protocol** in action
- **Why it works** (the invariants maintained)

**Example: Raft Consensus Concept**
```yaml
diagram:
  type: protocol
  title: "Raft: Achieving Consensus Through Leader Election"
  components:
    - leader: "Single source of truth for ordering"
    - followers: "Replicate leader's decisions"
    - candidate: "Aspiring leader during election"

  key_protocol_steps:
    1: "Leader sends heartbeats to maintain authority"
    2: "No heartbeat → follower becomes candidate"
    3: "Candidate requests votes from majority"
    4: "First to get majority becomes new leader"

  invariants:
    - "At most one leader per term"
    - "Logs only flow from leader to followers"
    - "Committed entries never lost"
```

---

### 2. IMPLEMENTATION DIAGRAMS (How It Works in Practice)
**Purpose:** Show actual system architectures, not abstract concepts

#### Requirements
- **Use real component names** (etcd, Kafka, PostgreSQL)
- **Include actual metrics** from production systems
- **Show configuration parameters** that matter
- **Mark critical paths** and bottlenecks

**Example: etcd Architecture**
```yaml
diagram:
  type: architecture
  title: "etcd: Production Linearizable Key-Value Store"

  components:
    client_layer:
      - grpc_server:
          max_connections: 10000
          tls: required

    consensus_layer:
      - raft_leader:
          term: 42
          commit_index: 1000000
          metrics:
            writes_per_sec: 10000
            fsync_latency_p99: 10ms

      - raft_followers:
          count: 2  # Total cluster size: 3
          replication_lag_p99: 5ms

    storage_layer:
      - bbolt_db:
          size: 8GB
          page_size: 4KB
      - wal:
          sync: every_commit
          rotation: 64MB

  critical_paths:
    write_path:
      latency_budget:
        - client_to_leader: 1ms
        - leader_consensus: 10ms
        - leader_to_storage: 5ms
        - storage_fsync: 10ms
        - response_to_client: 1ms
        total_p99: 27ms
```

---

### 3. COMPARISON DIAGRAMS (Trade-offs and Choices)
**Purpose:** Help engineers choose between alternatives

#### Requirements
- **Side-by-side comparison** of approaches
- **Quantitative metrics** for each option
- **Clear trade-offs** highlighted
- **Decision criteria** specified

**Example: Consistency Models Comparison**
```yaml
diagram:
  type: comparison
  title: "Strong vs Eventual Consistency: The Trade-off"

  options:
    linearizable:
      implementation: "etcd with Raft"
      latency:
        p50: 10ms
        p99: 50ms
      availability: "Fails during partition (CP)"
      throughput: "10K writes/sec"
      use_when:
        - "Configuration management"
        - "Distributed locking"
        - "Leader election"

    eventually_consistent:
      implementation: "Cassandra with quorum"
      latency:
        p50: 2ms
        p99: 10ms
      availability: "Available during partition (AP)"
      throughput: "100K writes/sec"
      use_when:
        - "User activity feeds"
        - "Shopping carts"
        - "View counts"

  key_trade_off: "10x latency for guaranteed consistency"
```

---

### 4. FAILURE SCENARIO DIAGRAMS (What Happens When Things Break)
**Purpose:** Show system behavior during failures

#### Requirements
- **Specific failure types** (not generic "node failure")
- **Detection mechanisms** and timeouts
- **Recovery procedures** step by step
- **Data loss/inconsistency risks** if any

**Example: Kafka Partition Leader Failure**
```yaml
diagram:
  type: failure_sequence
  title: "Kafka Leader Failure: Detection and Recovery"

  initial_state:
    partition_0:
      leader: broker_1
      isr: [broker_1, broker_2, broker_3]
      leo: 1000000  # Log end offset

  failure_event:
    type: "Broker 1 crashes (OOM)"
    time: t0

  detection:
    mechanism: "ZooKeeper session timeout"
    timeout: 6000ms  # session.timeout.ms
    detected_at: "t0 + 6s"

  recovery_steps:
    1:
      action: "Controller detects broker_1 offline"
      time: "t0 + 6s"
    2:
      action: "Controller selects broker_2 from ISR as new leader"
      time: "t0 + 6.1s"
    3:
      action: "Controller updates metadata"
      time: "t0 + 6.2s"
    4:
      action: "Producers/consumers receive metadata update"
      time: "t0 + 6.5s"
    5:
      action: "Production resumes with broker_2 as leader"
      time: "t0 + 7s"

  impact:
    unavailability_window: "7 seconds"
    data_loss: "None (ISR was in sync)"
    client_errors: "Retriable NotLeaderForPartition"
```

---

### 5. PERFORMANCE PROFILE DIAGRAMS (Cost and Scale)
**Purpose:** Show realistic performance characteristics

#### Requirements
- **Actual benchmark data** (not theoretical)
- **Resource consumption** at different scales
- **Bottlenecks identified**
- **Optimization opportunities** marked

**Example: PostgreSQL Replication Performance**
```yaml
diagram:
  type: performance
  title: "PostgreSQL Streaming Replication: Performance Profile"

  workload:
    write_tps: 10000
    read_tps: 50000
    database_size: 100GB

  primary:
    cpu_usage: 60%
    memory: 32GB (25GB buffer pool)
    disk:
      wal_write_rate: 100MB/s
      checkpoint_io: 500MB every 5min
    network_out: 100MB/s (to replicas)

  replicas:
    count: 3
    lag:
      normal: 50ms
      under_load: 500ms
      during_checkpoint: 5s
    cpu_usage: 40%

  bottlenecks:
    1:
      component: "WAL fsync"
      impact: "Limits write TPS"
      optimization: "Use NVMe, increase wal_buffers"
    2:
      component: "Network bandwidth"
      impact: "Replica lag during bulk loads"
      optimization: "Compression, parallel workers"
    3:
      component: "Checkpoint I/O"
      impact: "Latency spikes every 5min"
      optimization: "Spread checkpoint writes"

  scaling_limits:
    vertical:
      max_write_tps: 50000  # With 96 cores
      limiting_factor: "Lock contention"
    horizontal:
      max_read_replicas: 10
      limiting_factor: "Primary network bandwidth"
```

---

### 6. DECISION TREE DIAGRAMS (When to Use What)
**Purpose:** Guide architectural decisions

#### Requirements
- **Clear decision points** with criteria
- **Concrete examples** for each path
- **Cost implications** noted
- **Migration paths** if decision changes

**Example: Choosing a Message Queue**
```yaml
diagram:
  type: decision_tree
  title: "Selecting a Message Queue System"

  start: "Message volume?"

  decisions:
    high_volume:
      question: "> 100K msgs/sec?"
      yes:
        question: "Need exactly-once?"
        yes:
          answer: "Kafka with transactions"
          examples: ["Payment events", "Financial trades"]
          cost: "$$$"
        no:
          answer: "Kafka without transactions"
          examples: ["Clickstream", "Metrics"]
          cost: "$$"
      no:
        next: "ordering_requirements"

    ordering_requirements:
      question: "Strict ordering needed?"
      yes:
        question: "Global or per-key?"
        global:
          answer: "Redis Streams or RabbitMQ"
          examples: ["Audit logs", "Change events"]
          cost: "$"
        per_key:
          answer: "Kafka with key partitioning"
          examples: ["User events", "Device telemetry"]
          cost: "$$"
      no:
        answer: "SQS or RabbitMQ"
        examples: ["Task queue", "Email sending"]
        cost: "$"
```

---

### 7. EVOLUTION DIAGRAMS (How Systems Grow)
**Purpose:** Show how architectures evolve with scale

#### Requirements
- **Clear scale points** where architecture changes
- **Migration strategy** between stages
- **What breaks** at each scale point
- **Real examples** of companies at each stage

**Example: From Monolith to Microservices**
```yaml
diagram:
  type: evolution
  title: "Evolution of an E-commerce Platform"

  stage_1:
    name: "Startup (0-1K users)"
    architecture:
      - "Single Rails app"
      - "PostgreSQL database"
      - "Deployed on Heroku"
    scale_limits:
      - "Database connections exhausted"
      - "Slow page loads"
    cost: "$100/month"
    examples: ["Early Shopify", "Etsy 2005"]

  stage_2:
    name: "Growth (1K-100K users)"
    architecture:
      - "Rails app with read replicas"
      - "Redis cache"
      - "CDN for assets"
      - "Background jobs with Sidekiq"
    changes_from_stage_1:
      - "Add caching layer"
      - "Separate read/write databases"
      - "Extract background processing"
    scale_limits:
      - "Write throughput bottleneck"
      - "Cache invalidation complexity"
    cost: "$5K/month"
    examples: ["Shopify 2008", "Etsy 2008"]

  stage_3:
    name: "Scale (100K-10M users)"
    architecture:
      - "Service-oriented architecture"
      - "Sharded databases"
      - "Kafka for events"
      - "Elasticsearch for search"
    changes_from_stage_2:
      - "Extract services (checkout, inventory, user)"
      - "Shard database by customer"
      - "Event-driven architecture"
    scale_limits:
      - "Cross-service transactions"
      - "Distributed system complexity"
    cost: "$200K/month"
    examples: ["Shopify 2015", "Etsy 2012"]
```

---

## Diagram Quality Checklist

Before accepting any diagram, verify:

### Educational Value
- [ ] Teaches a specific concept clearly
- [ ] Uses real-world examples
- [ ] Shows why not just what
- [ ] Includes counter-examples or anti-patterns

### Technical Accuracy
- [ ] Uses actual system names and versions
- [ ] Includes realistic metrics (not made up)
- [ ] Shows genuine trade-offs
- [ ] Technically reviewed by expert

### Visual Clarity
- [ ] Progressive disclosure (not everything at once)
- [ ] Consistent color coding with meaning
- [ ] Clear labels with units
- [ ] Appropriate level of detail

### Completeness
- [ ] Shows normal operation
- [ ] Shows failure scenarios
- [ ] Shows performance characteristics
- [ ] Shows evolution/migration path

---

## Specific Requirements by Type

### For Each Guarantee (18 total)
Must have these 6 diagrams:

1. **CONCEPT**: What the guarantee means (timeline/ordering)
2. **VIOLATION**: What it prevents (counter-examples)
3. **IMPLEMENTATION**: Real system providing it (etcd, Cassandra)
4. **COMPARISON**: vs other guarantees (trade-offs)
5. **FAILURE**: Behavior during partition/failures
6. **DECISION**: When to use this guarantee

### For Each Mechanism (22 total)
Must have these 6 diagrams:

1. **ARCHITECTURE**: Components and structure
2. **PROTOCOL**: Step-by-step operation
3. **CONFIGURATION**: Key parameters and tuning
4. **FAILURE**: Failure detection and recovery
5. **PERFORMANCE**: Resource usage and limits
6. **DEPLOYMENT**: How to deploy at scale

### For Each Pattern (12 total)
Must have these 5 diagrams:

1. **STRUCTURE**: Component organization
2. **BEHAVIOR**: Runtime interactions
3. **ANTI-PATTERN**: Common mistakes
4. **EVOLUTION**: How to adopt incrementally
5. **EXAMPLES**: Real systems using it

### For Each Case Study (120+ systems)
Must have these 8 diagrams:

1. **GLOBAL**: 10,000 foot architecture
2. **REQUEST FLOW**: How requests traverse the system
3. **DATA FLOW**: How data moves and transforms
4. **FAILURE DOMAINS**: Blast radius and isolation
5. **SCALING STRATEGY**: How they handle growth
6. **EVOLUTION**: How architecture changed over time
7. **BOTTLENECKS**: Current limitations
8. **INNOVATIONS**: Novel solutions they created

---

## Anti-Patterns to Avoid

### ❌ DO NOT Create These Diagrams:
- Generic "Client → Service → Database" flows
- Abstract "Write A, Read B" operations
- Unnamed "Service 1, Service 2" components
- Theoretical performance numbers
- Happy-path-only scenarios

### ✅ DO Create These Instead:
- "Mobile App → Envoy → Cart Service → DynamoDB"
- "SET user:123:cart = {items: [...]}"
- "Shopify Checkout Service, Inventory Service"
- "p99: 47ms measured on Black Friday 2023"
- "What happens when DynamoDB throttles"

---

## Validation Rules

### Automatic Rejection If:
1. Uses generic component names ("Service A")
2. No metrics or uses fake metrics ("X ms")
3. Shows only happy path
4. Doesn't answer "why" or "when"
5. Could apply to any system (not specific)

### Automatic Approval If:
1. References specific technologies with versions
2. Includes measured metrics with units
3. Shows failure handling
4. Helps make architectural decisions
5. Could only apply to this specific concept

---

## Next Steps

1. **Audit existing diagrams** against these criteria
2. **Delete non-compliant diagrams** (probably 90%)
3. **Create exemplars** for each category
4. **Build generators** that enforce these requirements
5. **Review with experts** before publishing

Remember: **Quality > Quantity**

100 diagrams that teach > 2000 that don't.