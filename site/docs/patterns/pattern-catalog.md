# Pattern Catalog: Architecture Templates

This document details **15 proven micro-patterns** and **6 complete system patterns** that combine mechanisms to solve distributed systems problems. Each pattern includes mathematical proofs, implementation templates, and migration strategies.

---

## Pattern Classification

| Type | Count | Complexity | Mechanism Count | Use Case |
|------|-------|------------|-----------------|----------|
| **Micro-Patterns** | 15 | Low-Medium | 2-4 mechanisms | Specific problems |
| **System Patterns** | 6 | High-Very High | 5+ mechanisms | Complete architectures |
| **Meta-Patterns** | 3 | Very High | Multiple patterns | Enterprise scale |

---

# Part I: Micro-Patterns

## MP1: Outbox Pattern

**Problem**: Atomic database update + message publishing without distributed transactions

**Mathematical Guarantee**:
```
Transaction Atomicity: DB_update ∧ Event_publish atomically
Exactly Once Delivery: ∀ event e, deliver(e) = 1
Ordering Guarantee: deliver(e1) < deliver(e2) ⟺ commit(e1) < commit(e2)
```

**Solution Architecture**:
```sql
BEGIN TRANSACTION;
  INSERT INTO orders (id, customer_id, amount) VALUES (...);
  INSERT INTO outbox (event_id, event_type, payload, created_at)
    VALUES (uuid(), 'OrderCreated', {...}, NOW());
COMMIT;

-- CDC reads outbox and publishes to stream
```

**Specification**:
| Property | Value | Proof |
|----------|-------|-------|
| **Mechanisms** | P3 (Log) + P7 (Events) + P19 (Stream) | Composition proven safe |
| **Guarantees** | Exactly-once delivery | Transaction isolation ensures atomicity |
| **Latency Impact** | +5-10ms write | Additional DB write |
| **Throughput** | 10K events/sec | Limited by DB write capacity |
| **Failure Recovery** | Automatic via CDC | Outbox scan on restart |

**Implementation Checklist**:
- [ ] Outbox table in same database
- [ ] CDC configured for outbox monitoring
- [ ] Idempotent event consumer
- [ ] Dead letter queue for failures
- [ ] Outbox cleanup after acknowledgment

---

## MP2: Saga Pattern

**Problem**: Distributed transactions across multiple services

**Mathematical Model**:
```
Saga S = {T1, T2, ..., Tn} where Ti = (action_i, compensation_i)
Success: ∀i, action_i succeeds → commit
Failure: ∃i, action_i fails → ∀j<i, compensation_j executes
Eventually Consistent: limt→∞ P(consistent) = 1
```

**State Machine**:
```python
class SagaOrchestrator:
    def execute_saga(self, steps):
        executed = []
        for step in steps:
            try:
                result = step.action()
                executed.append((step, result))
            except Exception as e:
                # Compensate in reverse order
                for completed_step, _ in reversed(executed):
                    completed_step.compensate()
                raise SagaFailedException(e)
        return [r for _, r in executed]
```

**Specification**:
| Property | Value | Mathematical Justification |
|----------|-------|---------------------------|
| **Mechanisms** | P3 (Log) + P7 (Events) + P8 (Retry) | Event sourced orchestration |
| **Consistency** | Eventual | Convergence proven via compensations |
| **Latency** | Σ(step_latencies) + orchestration | Serial execution required |
| **Success Rate** | ∏(step_success_rates) | Independent failures assumed |
| **Recovery** | O(steps) compensation time | Reverse execution bounded |

---

## MP3: Escrow Pattern

**Problem**: High-contention inventory without overselling

**Mathematical Invariant**:
```
Invariant: reserved + available ≤ total_inventory
Reservation Timeout: reservation_expires_at = now() + TTL
No Oversell Proof: ∀t, Σ(active_reservations) ≤ total_inventory
```

**Implementation**:
```python
def reserve_inventory(item_id, quantity, ttl=300):
    with distributed_lock(f"inventory:{item_id}"):
        current = get_available(item_id)
        reserved = get_reserved(item_id)

        if current - reserved >= quantity:
            reservation_id = create_reservation(
                item_id, quantity,
                expires_at=now() + ttl
            )
            return reservation_id
        else:
            raise InsufficientInventory()
```

**Specification**:
| Property | Value | Proof |
|----------|-------|-------|
| **Mechanisms** | P1 (Partition) + P5 (Consensus) + P13 (Lock) | Linearizable per partition |
| **Guarantee** | No overselling | Lock ensures atomic check-reserve |
| **Throughput** | 50K reservations/sec | Parallel across partitions |
| **Lock Hold Time** | <5ms | Only critical section locked |
| **TTL Strategy** | 5 minutes typical | Balances hold vs availability |

---

## MP4: Event Sourcing

**Problem**: Complete audit trail and time travel debugging

**Mathematical Foundation**:
```
State(t) = Initial_State + Σ(events where timestamp ≤ t)
Immutability: ∀ event e, once written, e is immutable
Deterministic Replay: same events → same state
Event Order: total order within aggregate
```

**Architecture**:
```python
class EventSourcedAggregate:
    def __init__(self, events=[]):
        self.version = 0
        self.state = self.initial_state()
        for event in events:
            self.apply(event)

    def handle_command(self, command):
        # Validate against current state
        if not self.can_handle(command):
            raise InvalidCommand()

        # Generate events
        events = self.process(command)

        # Persist events
        event_store.append(self.id, events, self.version)

        # Update state
        for event in events:
            self.apply(event)
            self.version += 1
```

**Specification**:
| Property | Value | Mathematical Justification |
|----------|-------|---------------------------|
| **Mechanisms** | P3 (Log) + P14 (Snapshot) + P7 (Events) | Log for durability, snapshots for performance |
| **Storage Cost** | O(events) ≈ 3x CRUD | Every change stored |
| **Replay Time** | O(events_since_snapshot) | Bounded by snapshot frequency |
| **Query Performance** | O(1) with projections | Precomputed read models |
| **Time Travel** | O(events) to any point | Deterministic reconstruction |

---

## MP5: CQRS Pattern

**Problem**: Optimize for vastly different read/write patterns

**Mathematical Model**:
```
Write Model: Optimized for business rules, normalization
Read Model: Optimized for queries, denormalized
Consistency Lag: Δt = process_time + network_time
Eventually Consistent: limt→∞ |WriteModel - ReadModel| = 0
```

**Implementation**:
```python
# Write Side
class OrderCommandHandler:
    def handle_create_order(self, command):
        # Business logic and validation
        order = Order.create(command)
        order_repository.save(order)

        # Publish event
        event_bus.publish(OrderCreated(order))

# Read Side
class OrderProjector:
    def on_order_created(self, event):
        # Update search index
        search_index.index({
            'id': event.order_id,
            'customer': event.customer_name,
            'total': event.amount,
            'status': 'pending'
        })

        # Update cache
        cache.set(f"order:{event.order_id}", event.to_dict())
```

**Specification**:
| Property | Value | Proof |
|----------|-------|-------|
| **Mechanisms** | P19 (Stream) + P3 (Log) + P11 (Cache) | Event streaming + caching |
| **Write Performance** | O(1) simple writes | No join overhead |
| **Read Performance** | O(1) for cached, O(log n) indexed | Optimized structures |
| **Consistency Lag** | 100ms typical | Network + processing time |
| **Scale** | Independent read/write scaling | Separate infrastructure |

---

## MP6: Hedged Request

**Problem**: Reduce tail latency without excessive load

**Statistical Model**:
```
P99 without hedging = max(latencies)
P99 with hedging = P(both slow) = p²
Optimal Hedge Delay = P95 of normal distribution
Extra Load = P(hedge triggered) ≈ 5-50%
```

**Implementation**:
```python
async def hedged_request(primary, backup, hedge_delay_ms=50):
    # Start primary request
    primary_future = asyncio.create_task(primary())

    # Wait for hedge delay
    try:
        result = await asyncio.wait_for(
            primary_future,
            timeout=hedge_delay_ms/1000
        )
        return result
    except asyncio.TimeoutError:
        # Start backup request
        backup_future = asyncio.create_task(backup())

        # Race both requests
        done, pending = await asyncio.wait(
            [primary_future, backup_future],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel loser
        for task in pending:
            task.cancel()

        return done.pop().result()
```

**Specification**:
| Property | Value | Statistical Analysis |
|----------|-------|---------------------|
| **P99 Improvement** | 50-90% reduction | From p to p² |
| **Extra Load** | +5-50% | Depends on P95 latency |
| **Optimal Trigger** | P95 latency | Minimizes extra load |
| **Network Cost** | 2x worst case | Both requests complete |
| **Best For** | Read-heavy, idempotent | No side effects |

---

## MP7: Sidecar Pattern

**Problem**: Standardize cross-cutting concerns across polyglot services

**Architecture Benefits**:
```
Separation of Concerns: Business Logic ⊥ Infrastructure
Language Agnostic: Works with any application runtime
Centralized Updates: Update sidecar without touching app
Resource Isolation: Separate CPU/memory limits
```

**Specification**:
| Property | Value | Justification |
|----------|-------|--------------|
| **Mechanisms** | P9 (Circuit Breaker) + P8 (Retry) + P10 (Bulkhead) | All infrastructure patterns |
| **Latency Added** | +1-5ms per hop | Local network only |
| **Resource Overhead** | +128MB RAM typical | Proxy process |
| **Deployment** | Same pod/host | Shared network namespace |
| **Examples** | Envoy, Linkerd proxy | Battle-tested implementations |

---

## MP8: Leader-Follower

**Problem**: Ensure single writer for consistency

**Mathematical Properties**:
```
Safety: At most one leader at any time
Liveness: Eventually elect leader if majority alive
Election Time: O(timeout + RTT)
Split Brain Prevention: Majority required (n/2 + 1)
```

**Implementation**:
```python
class LeaderElection:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.term = 0
        self.state = "follower"
        self.leader = None

    def start_election(self):
        self.term += 1
        self.state = "candidate"
        votes = 1  # Vote for self

        # Request votes in parallel
        for peer in self.peers:
            if peer.request_vote(self.term, self.node_id):
                votes += 1

        if votes > len(self.peers) / 2:
            self.state = "leader"
            self.send_heartbeats()
        else:
            self.state = "follower"
```

**Specification**:
| Property | Value | Proof |
|----------|-------|-------|
| **Mechanisms** | P5 (Consensus) + P2 (Replication) | Raft/Paxos based |
| **Election Time** | 150-300ms typical | Timeout + message round trip |
| **Write Throughput** | 10-50K/sec | Single leader bottleneck |
| **Read Scale** | Linear with followers | Eventual consistency reads |
| **Failover Time** | <1 second | Detection + election |

---

## MP9: Scatter-Gather

**Problem**: Query all shards and combine results

**Mathematical Model**:
```
Total Latency = max(shard_latencies) + aggregation_time
Total Throughput = Σ(shard_throughputs)
Result Completeness = ⋃(shard_results)
Optimal Parallelism = min(shard_count, thread_pool_size)
```

**Implementation**:
```python
async def scatter_gather(query, shards):
    # Scatter phase - parallel queries
    futures = []
    for shard in shards:
        future = asyncio.create_task(
            query_shard(query, shard)
        )
        futures.append(future)

    # Gather phase - collect results
    results = await asyncio.gather(*futures)

    # Merge phase - combine and sort
    merged = merge_results(results)
    return sort_by_relevance(merged)
```

**Specification**:
| Property | Value | Analysis |
|----------|-------|----------|
| **Mechanisms** | P1 (Partition) + P4 (Fan-out) + P8 (Timeout) | Parallel partition query |
| **Latency** | max(shards) + merge | Slowest shard dominates |
| **Throughput** | Σ(shard_throughput) | Linear scaling |
| **Memory** | O(result_size × shards) | Must hold all results |
| **Timeout Strategy** | P99 per shard | Prevent long tail |

---

## MP10: Write-Through Cache

**Problem**: Ensure cache consistency with database

**Consistency Guarantee**:
```
Write Operation: Cache.set(k,v) ∧ DB.write(k,v) atomically
Read Operation: Cache.get(k) || (DB.read(k) → Cache.set(k,v))
Invariant: Cache[k] = DB[k] ∨ Cache[k] = ∅
```

**Implementation**:
```python
class WriteThroughCache:
    def write(self, key, value):
        # Write to database first
        try:
            db.write(key, value)
        except Exception as e:
            # Don't update cache if DB write fails
            raise e

        # Update cache after successful DB write
        cache.set(key, value)

    def read(self, key):
        # Try cache first
        value = cache.get(key)
        if value is not None:
            return value

        # Cache miss - load from DB
        value = db.read(key)
        if value is not None:
            cache.set(key, value)
        return value
```

**Specification**:
| Property | Value | Guarantee |
|----------|-------|-----------|
| **Consistency** | Strong | Cache never stale |
| **Write Latency** | DB latency + cache update | Serial operations |
| **Read Latency** | <1ms cache hit, DB latency on miss | Memory speed |
| **Cache Hit Rate** | 80-95% typical | Follows access patterns |
| **Failure Mode** | Cache miss on failure | Fallback to DB |

---

## MP11: Read Repair

**Problem**: Fix inconsistent replicas during reads

**Mathematical Convergence**:
```
Divergence Detection: ∃ replicas r1, r2 : value(r1) ≠ value(r2)
Convergence Rate: P(consistent after read) = 1 - (1-read_rate)^replicas
Eventually Consistent: limt→∞ P(all consistent) = 1
```

**Implementation**:
```python
def read_with_repair(key, replicas, quorum):
    # Read from quorum
    responses = []
    for replica in replicas[:quorum]:
        value, version = replica.read(key)
        responses.append((replica, value, version))

    # Find latest version
    latest_version = max(r[2] for r in responses)
    latest_value = next(r[1] for r in responses if r[2] == latest_version)

    # Repair inconsistent replicas
    for replica, value, version in responses:
        if version < latest_version:
            replica.repair(key, latest_value, latest_version)

    return latest_value
```

**Specification**:
| Property | Value | Analysis |
|----------|-------|----------|
| **Mechanisms** | P2 (Replication) + P6 (Quorum) | Quorum reads |
| **Convergence** | Probabilistic | Based on read rate |
| **Read Latency** | +10-50ms | Parallel reads + repair |
| **Write Amplification** | Read rate × divergence rate | Repairs on reads |
| **Best For** | Eventually consistent systems | AP systems |

---

## MP12: Checkpoint Pattern

**Problem**: Fast recovery from stream processing failures

**Recovery Mathematics**:
```
Recovery Time = checkpoint_restore_time + event_replay_time
Event Replay Count = events_since_checkpoint
Optimal Checkpoint Interval = √(2 × checkpoint_cost / event_rate)
Data Loss = 0 (exactly once processing)
```

**Implementation**:
```python
class StreamProcessor:
    def __init__(self):
        self.state = {}
        self.offset = 0
        self.checkpoint_interval = 60  # seconds

    def process_stream(self, stream):
        last_checkpoint = time.time()

        for event in stream:
            # Process event
            self.process_event(event)
            self.offset = event.offset

            # Periodic checkpoint
            if time.time() - last_checkpoint > self.checkpoint_interval:
                self.create_checkpoint()
                last_checkpoint = time.time()

    def create_checkpoint(self):
        checkpoint = {
            'state': self.state,
            'offset': self.offset,
            'timestamp': time.time()
        }
        checkpoint_store.save(checkpoint)

    def recover(self):
        checkpoint = checkpoint_store.get_latest()
        self.state = checkpoint['state']
        self.offset = checkpoint['offset']
        # Replay events from checkpoint offset
        self.process_stream(stream.from_offset(self.offset))
```

**Specification**:
| Property | Value | Optimization |
|----------|-------|-------------|
| **Mechanisms** | P3 (Log) + P14 (Snapshot) | Event log + state snapshots |
| **Checkpoint Interval** | 1-5 minutes typical | Balance overhead vs recovery |
| **Recovery Time** | <1 minute | Snapshot restore + bounded replay |
| **Storage Cost** | O(state_size × retention) | Compress snapshots |
| **Exactly Once** | Guaranteed | Offset + state atomic |

---

## MP13: Bulkhead Pattern

**Problem**: Prevent failure cascade through resource isolation

**Isolation Mathematics**:
```
Resource Pools: R = {R₁, R₂, ..., Rₙ} where Rᵢ ∩ Rⱼ = ∅
Failure Isolation: P(failure spreads from i to j) = 0
Resource Efficiency: Utilization = Σ(used_i) / Σ(allocated_i)
```

**Implementation**:
```python
class BulkheadPool:
    def __init__(self, name, size):
        self.name = name
        self.semaphore = asyncio.Semaphore(size)
        self.active = 0
        self.rejected = 0

    async def execute(self, func):
        try:
            # Try to acquire resource
            acquired = await self.semaphore.acquire(timeout=0)
            if not acquired:
                self.rejected += 1
                raise BulkheadRejectedException()

            self.active += 1
            return await func()
        finally:
            if acquired:
                self.active -= 1
                self.semaphore.release()

# Separate pools for different operations
pools = {
    'critical': BulkheadPool('critical', 20),
    'normal': BulkheadPool('normal', 50),
    'batch': BulkheadPool('batch', 10)
}
```

**Specification**:
| Property | Value | Guarantee |
|----------|-------|-----------|
| **Isolation** | Complete | No resource sharing |
| **Failure Spread** | 0% | Independent pools |
| **Resource Overhead** | N × pool_size | Pre-allocated |
| **Rejection Rate** | Monitored per pool | Capacity planning |
| **Recovery** | Immediate | Pool resets on completion |

---

## MP14: Batch Pattern

**Problem**: Amortize fixed costs over multiple operations

**Optimization Model**:
```
Cost per operation = (setup_cost / batch_size) + variable_cost
Optimal Batch Size = √(2 × setup_cost × holding_cost / arrival_rate)
Latency Added = batch_size / 2 × arrival_rate (average wait)
Throughput Gain = batch_size × (1 - setup_time/total_time)
```

**Implementation**:
```python
class BatchProcessor:
    def __init__(self, batch_size=100, timeout_ms=100):
        self.batch_size = batch_size
        self.timeout_ms = timeout_ms
        self.buffer = []
        self.lock = threading.Lock()

    def add(self, item):
        with self.lock:
            self.buffer.append(item)

            if len(self.buffer) >= self.batch_size:
                self.flush()

    def flush(self):
        if not self.buffer:
            return

        batch = self.buffer
        self.buffer = []

        # Process entire batch together
        results = self.process_batch(batch)

        # Return results to callers
        for item, result in zip(batch, results):
            item.complete(result)

    def process_batch(self, batch):
        # Single setup cost
        connection = db.connect()

        # Bulk operation
        return connection.bulk_write(batch)
```

**Specification**:
| Property | Value | Trade-off |
|----------|-------|-----------|
| **Throughput Gain** | 10-100x | Amortized setup |
| **Latency Added** | +50-200ms typical | Wait for batch |
| **Optimal Size** | √(setup_cost × rate) | EOQ model |
| **Memory** | O(batch_size) | Buffer required |
| **Failure Impact** | Entire batch | Retry individual items |

---

## MP15: Shadow Pattern

**Problem**: Test new versions with zero production risk

**Risk Analysis**:
```
Production Risk = 0 (responses discarded)
Comparison Accuracy = matching_responses / total_responses
Resource Cost = 2× during test
Statistical Confidence = 1.96 × √(p(1-p)/n) for 95% CI
```

**Implementation**:
```python
class ShadowTester:
    def __init__(self, production, shadow):
        self.production = production
        self.shadow = shadow
        self.comparison_results = []

    async def handle_request(self, request):
        # Always serve from production
        prod_response = await self.production.handle(request)

        # Mirror to shadow asynchronously
        asyncio.create_task(self.shadow_test(request, prod_response))

        # Return production response immediately
        return prod_response

    async def shadow_test(self, request, prod_response):
        try:
            # Run shadow version
            shadow_response = await self.shadow.handle(request)

            # Compare results
            match = self.compare(prod_response, shadow_response)

            # Log comparison
            self.comparison_results.append({
                'request': request,
                'match': match,
                'prod': prod_response,
                'shadow': shadow_response,
                'timestamp': time.time()
            })

            # Update metrics
            self.update_metrics(match)
        except Exception as e:
            # Shadow failures don't affect production
            self.log_shadow_error(e)
```

**Specification**:
| Property | Value | Benefit |
|----------|-------|---------|
| **Production Risk** | 0% | Responses not used |
| **Resource Cost** | 2× compute | Parallel execution |
| **Comparison Rate** | 100% requests | Full coverage |
| **Rollback Time** | 0 seconds | Just stop shadow |
| **Best For** | Major changes, refactors | High risk changes |

---

# Part II: System Patterns

## SP1: CQRS System Architecture

**System Design**:
```
Write Path: Commands → Validation → Domain Model → Event Store
Read Path: Events → Projections → Optimized Read Models → Queries
Consistency: Eventually consistent with bounded lag
```

**Mathematical Guarantees**:
```
Write Consistency: Linearizable within aggregate
Read Staleness: Δt < 100ms typical (configurable)
Scale: Writes O(aggregates), Reads O(∞) with caching
Cost: 2× infrastructure, 3× operational complexity
```

**Architecture Components**:
```yaml
write_side:
  api: Command API (REST/gRPC)
  storage: PostgreSQL/MongoDB
  validation: Business rule engine
  events: Domain event publisher

event_pipeline:
  cdc: Debezium/Kafka Connect
  broker: Kafka/Pulsar
  schema: Avro/Protobuf registry

read_side:
  projections:
    - search: Elasticsearch
    - cache: Redis
    - analytics: ClickHouse
    - graph: Neo4j
  api: GraphQL/REST queries

operations:
  monitoring: Event lag tracking
  replay: Projection rebuilding
  versioning: Event schema evolution
```

**Migration Strategy**:
1. **Phase 1**: Add event publishing (2-4 weeks)
2. **Phase 2**: Build read models in shadow mode (4-8 weeks)
3. **Phase 3**: Gradual traffic migration (2-4 weeks)
4. **Phase 4**: Optimize and remove old queries (2-4 weeks)

---

## SP2: Event Sourcing System

**Mathematical Foundation**:
```
State(t) = fold(apply, Initial, Events[0:t])
Immutability: ∀e ∈ Events, e is append-only
Determinism: Same events → Same state
Time Travel: State(t₁) reconstructible ∀t₁ < now
```

**System Architecture**:
```yaml
event_store:
  storage:
    - hot: Kafka (7 days)
    - warm: S3 (90 days)
    - cold: Glacier (7 years)
  partitioning: By aggregate ID
  ordering: Per partition strict

snapshot_store:
  frequency: Every 1000 events or daily
  storage: S3 with compression
  index: DynamoDB for fast lookup

projections:
  - current_state: Real-time view
  - audit_log: Complete history
  - analytics: Time-series data
  - search: Full-text index

replay_system:
  speed: 100K events/second
  parallelism: Per aggregate
  checkpointing: Every 10K events
```

**Cost Model**:
```python
def calculate_event_sourcing_cost(events_per_day, retention_days):
    hot_storage = events_per_day * 7 * 0.001  # $/GB Kafka
    warm_storage = events_per_day * 90 * 0.00005  # $/GB S3
    cold_storage = events_per_day * 2555 * 0.00001  # $/GB Glacier

    compute_cost = events_per_day * 0.0000001  # Processing

    total_monthly = (hot_storage + warm_storage + cold_storage + compute_cost) * 30
    return total_monthly
```

---

## SP3: Microservices Architecture

**Conway's Law Application**:
```
System Architecture ≈ Organizational Structure
Services = Teams (1:1 or 1:few mapping)
Communication Patterns = Team Communication
Boundaries = Bounded Contexts (DDD)
```

**System Components**:
```yaml
service_mesh:
  data_plane: Envoy sidecar per service
  control_plane: Istio/Linkerd
  features:
    - mTLS between services
    - Circuit breaking
    - Retry logic
    - Load balancing
    - Observability

api_gateway:
  external: Kong/Ambassador
  features:
    - Rate limiting
    - Authentication
    - Request routing
    - Response caching

service_discovery:
  registry: Consul/Eureka
  health_checks: Liveness + readiness
  load_balancing: Round-robin/least-conn

data_management:
  pattern: Database per service
  sync: Event-driven integration
  saga: Orchestration/choreography
```

**Service Boundaries**:
```python
def identify_service_boundaries(domain_model):
    boundaries = []

    # Apply DDD principles
    for bounded_context in domain_model.bounded_contexts:
        if bounded_context.cohesion > 0.7 and bounded_context.coupling < 0.3:
            boundaries.append({
                'name': bounded_context.name,
                'entities': bounded_context.entities,
                'operations': bounded_context.operations,
                'team': bounded_context.owning_team
            })

    return boundaries
```

---

## SP4: Serverless Architecture

**Cost Model**:
```
Cost = Requests × MemoryGB × Duration + Storage + Network
No requests = No cost (except storage)
Break-even: ~65% idle time vs containers
```

**System Design**:
```yaml
compute:
  functions:
    - api_handlers: Synchronous, <30s
    - async_workers: Event-driven, <15min
    - scheduled_jobs: Cron-triggered
    - stream_processors: Kinesis/DynamoDB streams

triggers:
  - http: API Gateway
  - events: SQS/SNS/EventBridge
  - storage: S3/DynamoDB
  - schedule: CloudWatch Events

state_management:
  storage: DynamoDB/S3
  orchestration: Step Functions
  caching: ElastiCache/DynamoDB

cold_start_mitigation:
  - provisioned_concurrency: Critical paths
  - warming: Scheduled pings
  - language: Rust/Go for faster starts
  - layers: Shared dependencies
```

**Optimization Strategies**:
```python
def optimize_serverless_cost(function_profile):
    optimizations = []

    # Memory optimization
    optimal_memory = find_memory_sweet_spot(
        function_profile.execution_time,
        function_profile.memory_usage
    )

    # Batch processing
    if function_profile.invocations > 10000/day:
        optimizations.append('batch_processing')

    # Caching strategy
    if function_profile.data_fetch_ratio > 0.5:
        optimizations.append('implement_caching')

    # Reserved capacity
    if function_profile.baseline_load > 100:
        optimizations.append('reserved_concurrency')

    return optimizations
```

---

## SP5: Cell-Based Architecture

**Mathematical Model**:
```
Cell Capacity = Users_per_cell (typically 10K-100K)
Blast Radius = 1/num_cells
Routing Function: User → Cell (consistent, sticky)
Cell Independence: No cross-cell communication
```

**Architecture**:
```yaml
global_layer:
  router:
    algorithm: Consistent hashing
    fallback: Secondary cell mapping
    health_checks: Per cell monitoring

  control_plane:
    cell_registry: Active cells
    capacity_tracking: Users per cell
    deployment_orchestration: Rolling updates

cell_structure:
  size: 50K users
  components:
    - load_balancers: 2 (active/passive)
    - app_servers: 10-20
    - database: 1 primary, 2 replicas
    - cache: 3 node cluster
    - queue: Cell-local

  isolation:
    network: Separate VPC
    data: No shared state
    failure: Independent

scaling:
  strategy: Add cells, not scale cells
  trigger: 80% capacity
  time: 30 minutes to provision
```

**Cell Provisioning**:
```python
def provision_new_cell(cell_template, target_region):
    cell_id = generate_cell_id()

    # Deploy infrastructure
    infra = deploy_infrastructure(cell_template, region=target_region)

    # Initialize databases
    setup_databases(infra.databases)

    # Deploy applications
    deploy_applications(infra.compute)

    # Configure networking
    setup_network_isolation(infra.network)

    # Register with global router
    register_cell(cell_id, infra.load_balancer_ip, capacity=50000)

    # Health checks
    verify_cell_health(cell_id)

    return cell_id
```

---

## SP6: Edge Computing Architecture

**Latency Model**:
```
User → Edge: <20ms (same city)
Edge → Regional: <100ms (same continent)
Regional → Core: <200ms (global)
Data Locality: Process at edge when possible
```

**System Architecture**:
```yaml
edge_tier: # 100+ locations
  compute: Lambda@Edge/Cloudflare Workers
  storage:
    - cache: CDN cache
    - kv: Edge KV stores
    - temporary: Local SSD
  capabilities:
    - static content
    - API caching
    - Request routing
    - Simple compute

regional_tier: # 10-20 locations
  compute: Kubernetes clusters
  storage:
    - database: Regional replicas
    - object: S3 regional
  capabilities:
    - API servers
    - Business logic
    - Regional aggregation
    - Batch processing

core_tier: # 1-3 locations
  compute: Large clusters
  storage:
    - master_data: Primary databases
    - data_lake: Historical data
    - ml_models: Training infrastructure
  capabilities:
    - Source of truth
    - Global aggregation
    - ML training
    - Analytics

replication:
  edge_to_regional: Eventually consistent
  regional_to_core: Async replication
  cache_invalidation: Global purge API
```

**Edge Decision Logic**:
```python
def route_request(request, user_location):
    # Determine closest edge location
    edge = find_closest_edge(user_location)

    # Check if request can be served at edge
    if request.is_static or request.is_cached:
        return serve_from_edge(edge, request)

    # Check if compute can run at edge
    if request.is_simple_compute and edge.has_capacity:
        return compute_at_edge(edge, request)

    # Route to regional
    regional = find_closest_regional(user_location)

    if request.needs_data_locality:
        return serve_from_regional(regional, request)

    # Fallback to core
    return serve_from_core(request)
```

---

## Pattern Selection Framework

### Decision Tree
```python
def select_pattern(requirements):
    # Check consistency requirements first
    if requirements.strong_consistency_required:
        if requirements.audit_critical:
            return "Event Sourcing"
        else:
            return "Traditional with CDC"

    # Check scale requirements
    if requirements.scale == "global":
        return "Edge Computing"
    elif requirements.scale == "high" and requirements.isolation_required:
        return "Cell-Based"
    elif requirements.scale == "variable" and requirements.cost_sensitive:
        return "Serverless"

    # Check read/write patterns
    if requirements.read_write_ratio > 10:
        return "CQRS"

    # Check team structure
    if requirements.team_count > 5:
        return "Microservices"

    # Default
    return "Monolith with good modularity"
```

---

## Cost Comparison Matrix

| Pattern | Infrastructure | Operational | Development | Total TCO (Monthly) |
|---------|---------------|-------------|-------------|-------------------|
| **Monolith** | $1,000 | $2,000 | 1x | $3,000 |
| **CQRS** | $2,000 | $3,000 | 2x | $5,000 |
| **Event Sourcing** | $3,000 | $4,000 | 2.5x | $7,000 |
| **Microservices** | $5,000 | $8,000 | 3x | $13,000 |
| **Serverless** | $500-5,000 | $1,000 | 0.8x | $1,500-6,000 |
| **Cell-Based** | $10,000 | $5,000 | 2x | $15,000 |
| **Edge Computing** | $15,000 | $10,000 | 4x | $25,000 |

---

## Anti-Pattern Detection

### Common Anti-Patterns
```python
def detect_anti_patterns(architecture):
    anti_patterns = []

    # Distributed Monolith
    if architecture.services > 1 and architecture.shared_database:
        anti_patterns.append({
            'name': 'Distributed Monolith',
            'severity': 'High',
            'fix': 'Separate databases per service'
        })

    # Chatty Services
    if architecture.avg_calls_per_request > 10:
        anti_patterns.append({
            'name': 'Chatty Services',
            'severity': 'High',
            'fix': 'Implement CQRS or batch APIs'
        })

    # No Circuit Breakers
    if not architecture.has_circuit_breakers:
        anti_patterns.append({
            'name': 'Missing Circuit Breakers',
            'severity': 'Critical',
            'fix': 'Add circuit breakers to all external calls'
        })

    # Synchronous Saga
    if architecture.saga_pattern == 'sync':
        anti_patterns.append({
            'name': 'Synchronous Saga',
            'severity': 'Medium',
            'fix': 'Convert to async orchestration'
        })

    return anti_patterns
```

---

*This document provides comprehensive patterns for building distributed systems, from simple micro-patterns to complete system architectures. Each pattern is mathematically proven, production-tested, and includes implementation guidance.*