# Layer 3: The 15 Proven Micro-Patterns

Micro-patterns combine 2-4 primitives to solve specific distributed systems problems. Each has been proven in production across multiple organizations.

| **Pattern** | **Primitives** | **Problem Solved** | **Guarantees** | **Implementation** | **Proof** |
|---|---|---|---|---|---|
| **Outbox** | P3+P7+P19 | Dual write problem | ExactlyOnceToStream | Same DB transaction writes outbox table | CDC events match DB state |
| **Saga** | P3+P7+P8 | Distributed transaction | EventualConsistency | Forward recovery + compensations | All paths reach consistent state |
| **Escrow** | P1+P5+P13 | Inventory contention | NoOverselling | Pessimistic reservation with timeout | Invariant: sum ≤ total |
| **Event Sourcing** | P3+P14+P7 | Audit + time travel | CompleteHistory | Events as source of truth | Rebuild from events = current |
| **CQRS** | P19+P3+P11 | Read/write separation | OptimizedModels | Write model + read projections | Projection lag < SLO |
| **Hedged Request** | P8+P11 | Tail latency | PredictableTail | Send 2nd request at P95 | P99 reduced, load <2x |
| **Sidecar** | P9+P8+P10 | Cross-cutting concerns | Standardization | Proxy container | Overhead <20ms |
| **Leader-Follower** | P5+P2 | Single writer | Linearizability | Election + replication | Split-brain prevented |
| **Scatter-Gather** | P1+P4+P8 | Parallel query | Completeness | Fan-out + aggregate | All shards respond |
| **Write-Through** | P11+P14 | Cache consistency | StrongConsistency | Write to cache+DB | Cache never stale |
| **Read Repair** | P2+P6 | Eventual consistency | ConvergentRepair | Read from all, repair differences | Divergence detected+fixed |
| **Checkpoint** | P3+P14 | Recovery speed | FastRecovery | Periodic snapshots + incremental | Recovery <1min |
| **Bulkhead** | P10+P9 | Fault isolation | NoContagion | Separate resources per tenant | Isolation verified |
| **Batch** | P3+P7 | Efficiency | HighThroughput | Group operations | 10x throughput gain |
| **Shadow** | P20+P11 | Safe testing | RiskFreeValidation | Duplicate traffic to new version | No production impact |

## Detailed Pattern Analysis

### Outbox Pattern (P3+P7+P19)

**Problem**: How to atomically update database and publish event without distributed transactions?

**Solution**:
```sql
BEGIN TRANSACTION;
  INSERT INTO orders (id, customer_id, amount) VALUES (...);
  INSERT INTO outbox (event_id, event_type, payload) VALUES (...);
COMMIT;
```

**Guarantees**:
- Either both DB update and event occur, or neither
- Events published exactly once
- Events published in order of transaction commit

**Implementation Checklist**:
- [ ] Outbox table in same database as business data
- [ ] CDC configured to monitor outbox table
- [ ] Event deduplication using event_id
- [ ] Dead letter queue for failed processing
- [ ] Outbox cleanup after successful publication

### Saga Pattern (P3+P7+P8)

**Problem**: How to manage distributed transactions across multiple services?

**Solution**:
```yaml
saga_definition:
  name: "order_fulfillment"
  steps:
    - service: "payment"
      action: "charge_card"
      compensation: "refund_card"
    - service: "inventory" 
      action: "reserve_items"
      compensation: "release_items"
    - service: "shipping"
      action: "create_shipment" 
      compensation: "cancel_shipment"
```

**Guarantees**:
- Either all steps complete successfully, or all effects are compensated
- Progress despite individual service failures
- Audit trail of all operations

**Implementation Checklist**:
- [ ] Saga orchestrator with durable state
- [ ] Compensation actions for every forward action
- [ ] Timeout handling for each step
- [ ] Idempotency for all operations
- [ ] Monitoring for stuck sagas

### Escrow Pattern (P1+P5+P13)

**Problem**: How to handle high-contention resources like inventory?

**Solution**:
```python
def reserve_inventory(item_id, quantity):
    shard = hash(item_id) % NUM_SHARDS
    with distributed_lock(f"inventory:{shard}:{item_id}"):
        current = get_inventory(item_id)
        if current >= quantity:
            escrow_reservation(item_id, quantity, ttl=300)
            return reservation_id
        else:
            raise InsufficientInventory()
```

**Guarantees**:
- No overselling (invariant: reserved + available ≤ total)
- Reservations expire automatically
- Highly concurrent reservations possible

**Implementation Checklist**:
- [ ] Inventory sharded by item_id
- [ ] Reservations have TTL
- [ ] Lock timeout < reservation TTL
- [ ] Monitoring for lock contention
- [ ] Graceful degradation under extreme load

### CQRS Pattern (P19+P3+P11)

**Problem**: How to optimize for both write and read workloads?

**Solution**:
```python
# Write side - optimized for consistency
class OrderService:
    def create_order(self, order):
        with transaction():
            order_repo.save(order)
            outbox.publish(OrderCreated(order))

# Read side - optimized for queries
class OrderProjectionService:
    def handle(self, event: OrderCreated):
        projection = {
            'order_id': event.order_id,
            'customer_name': customer_service.get_name(event.customer_id),
            'total_amount': event.amount,
            'status': 'pending'
        }
        read_store.upsert(projection)
```

**Guarantees**:
- Write model optimized for business rules
- Read models optimized for specific queries
- Eventual consistency between write and read sides
- Independent scaling of read and write workloads

**Implementation Checklist**:
- [ ] Clear separation of write and read models
- [ ] Event streaming from write to read side
- [ ] Projection rebuilding capability
- [ ] Monitoring projection lag
- [ ] Fallback to write side for critical reads

### Request-Response Pattern (P1+P8+P9+P12)

**Problem**: How to implement reliable synchronous communication between client and server?

**Solution**:
```python
class RequestResponseClient:
    def __init__(self, load_balancer, circuit_breaker, timeout=30):
        self.load_balancer = load_balancer
        self.circuit_breaker = circuit_breaker
        self.timeout = timeout

    async def make_request(self, path, data):
        with timeout_context(self.timeout):
            with self.circuit_breaker:
                server = self.load_balancer.get_healthy_server()
                return await server.send_request(path, data)
```

**Guarantees**:
- Sequential ordering per client
- Linearizable operations
- Total order guarantee within single client session

**Scale Variants**:
- **Startup**: Direct connections, basic timeouts
- **Growth**: Load balancer, circuit breaker, retry logic
- **Scale**: Regional load balancing, auto-scaling groups
- **Hyperscale**: Global load balancers, intelligent routing

### Streaming Pattern (P3+P7+P19)

**Problem**: How to process continuous data streams with ordering and fault tolerance?

**Solution**:
```python
class StreamProcessor:
    def __init__(self, stream_name, processing_function):
        self.stream = KafkaStream(stream_name)
        self.processor = processing_function
        self.state = StreamState()

    async def process_stream(self):
        async for event in self.stream:
            try:
                result = await self.processor(event, self.state)
                await self.commit_offset(event.offset)
                self.state.update(result)
            except Exception as e:
                await self.handle_failure(event, e)
```

**Guarantees**:
- Eventual consistency
- Partition ordering preserved
- Multi-reader capability

**Use Cases**:
- Real-time analytics
- Event processing pipelines
- Log aggregation
- Change data capture

### Event Sourcing Pattern (P3+P14+P7)

**Problem**: How to maintain complete audit trail and enable time-travel debugging?

**Solution**:
```python
class EventSourcedAggregate:
    def __init__(self, aggregate_id):
        self.id = aggregate_id
        self.version = 0
        self.state = {}

    def handle_command(self, command):
        # Validate command against current state
        events = self.validate_and_generate_events(command)

        # Persist events atomically
        event_store.append_events(self.id, events, self.version)

        # Apply events to update state
        for event in events:
            self.apply_event(event)
            self.version += 1

    def rebuild_from_events(self, events):
        for event in events:
            self.apply_event(event)
```

**Guarantees**:
- Complete history preservation
- Deterministic state reconstruction
- Event immutability

### Fan-out Pattern (P1+P4+P8)

**Problem**: How to distribute single request to multiple services and aggregate results?

**Solution**:
```python
async def fan_out_gather(request, services):
    # Fan-out phase
    tasks = []
    for service in services:
        task = asyncio.create_task(
            service.process_with_timeout(request, timeout=30)
        )
        tasks.append(task)

    # Gather phase
    results = []
    for task in asyncio.as_completed(tasks):
        try:
            result = await task
            results.append(result)
        except Exception as e:
            # Handle partial failures
            logger.warning(f"Service failed: {e}")

    return aggregate_results(results)
```

**Guarantees**:
- Parallel processing
- Completeness (when all services respond)
- Partial results on failures

### Analytics Pattern (P4+P5+P10+P12)

**Problem**: How to build high-performance analytical processing system?

**Solution**:
```yaml
architecture:
  edge:
    - Analytics API (query interface)
  service:
    - Query Engine (parallel processing)
    - ETL Processor (data preparation)
  state:
    - Data Warehouse (columnar storage)
    - Staging Area (temporary storage)
  control:
    - Workload Manager (resource optimization)
```

**Guarantees**:
- Eventual consistency for analytics data
- Parallel processing for queries
- Multi-dimensional aggregation

**Variants**:
- **Real-Time**: Low latency, limited complexity
- **Batch**: High throughput, complex queries
- **Hybrid**: Balanced approach with lambda architecture

### Async Task Pattern (P7+P16+P8)

**Problem**: How to process long-running tasks asynchronously with reliability?

**Solution**:
```python
class AsyncTaskProcessor:
    def __init__(self, queue, batch_size=10):
        self.queue = queue
        self.batch_size = batch_size

    async def process_tasks(self):
        while True:
            # Batch tasks for efficiency
            tasks = await self.queue.get_batch(self.batch_size)

            # Process with retry logic
            for task in tasks:
                await self.process_with_retry(task, max_retries=3)

    async def process_with_retry(self, task, max_retries):
        for attempt in range(max_retries):
            try:
                result = await self.execute_task(task)
                await self.mark_complete(task, result)
                return
            except RetryableException as e:
                if attempt == max_retries - 1:
                    await self.mark_failed(task, e)
                else:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

**Guarantees**:
- Eventual completion
- Worker failure tolerance
- Batch efficiency

### Graph Pattern (P1+P18+P11)

**Problem**: How to efficiently query and traverse graph data structures?

**Solution**:
```python
class GraphQueryEngine:
    def __init__(self, graph_store, cache):
        self.store = graph_store
        self.cache = cache

    async def traverse_graph(self, start_node, traversal_pattern):
        # Check cache first
        cache_key = f"traversal:{start_node}:{hash(traversal_pattern)}"
        if cached_result := await self.cache.get(cache_key):
            return cached_result

        # Partition-aware traversal
        visited = set()
        results = []
        queue = deque([start_node])

        while queue:
            node = queue.popleft()
            if node in visited:
                continue

            visited.add(node)

            # Load node data with index optimization
            node_data = await self.store.get_node_with_edges(node)
            results.append(node_data)

            # Add neighbors to queue based on pattern
            for neighbor in self.apply_pattern(node_data, traversal_pattern):
                queue.append(neighbor)

        # Cache results for future queries
        await self.cache.set(cache_key, results, ttl=300)
        return results
```

**Guarantees**:
- Index-optimized queries
- Distributed traversal capability
- Cached performance

### Ledger Pattern (P3+P5+P13)

**Problem**: How to implement immutable transaction ledger with strong consistency?

**Solution**:
```python
class DistributedLedger:
    def __init__(self, consensus_group):
        self.consensus = consensus_group
        self.lock_manager = DistributedLockManager()
        self.log = ImmutableLog()

    async def record_transaction(self, transaction):
        # Acquire locks for all affected accounts
        locks = []
        for account in transaction.accounts:
            lock = await self.lock_manager.acquire(f"account:{account}")
            locks.append(lock)

        try:
            # Validate transaction
            if not await self.validate_transaction(transaction):
                raise InvalidTransactionError()

            # Achieve consensus on transaction
            consensus_result = await self.consensus.propose(transaction)

            if consensus_result.accepted:
                # Append to immutable log
                entry = LedgerEntry(
                    transaction=transaction,
                    timestamp=consensus_result.timestamp,
                    sequence=consensus_result.sequence
                )
                await self.log.append(entry)

                return entry.sequence
            else:
                raise ConsensusFailedError()

        finally:
            # Release all locks
            for lock in locks:
                await lock.release()
```

**Guarantees**:
- Immutable transaction history
- Strong consistency through consensus
- ACID properties for financial operations

### ML Inference Pattern (P11+P12+P4)

**Problem**: How to serve machine learning models at scale with low latency?

**Solution**:
```python
class MLInferenceService:
    def __init__(self, model_cache, load_balancer):
        self.cache = model_cache
        self.balancer = load_balancer

    async def predict(self, model_id, features):
        # Load model from cache
        model = await self.cache.get_model(model_id)
        if not model:
            model = await self.load_model(model_id)
            await self.cache.set_model(model_id, model)

        # Fan-out for ensemble models
        if model.is_ensemble:
            predictions = await self.ensemble_predict(model, features)
            return self.aggregate_predictions(predictions)
        else:
            return await model.predict(features)

    async def ensemble_predict(self, ensemble_model, features):
        tasks = []
        for sub_model in ensemble_model.models:
            task = asyncio.create_task(sub_model.predict(features))
            tasks.append(task)

        return await asyncio.gather(*tasks)
```

**Guarantees**:
- Low latency through caching
- High availability through load balancing
- Parallel inference for ensemble models

### Search Pattern (P18+P11+P4)

**Problem**: How to implement fast, relevant search across large datasets?

**Solution**:
```python
class DistributedSearchEngine:
    def __init__(self, index_shards, cache):
        self.shards = index_shards
        self.cache = cache

    async def search(self, query, filters=None):
        # Check cache for popular queries
        cache_key = f"search:{hash(query)}:{hash(filters)}"
        if cached_results := await self.cache.get(cache_key):
            return cached_results

        # Fan-out search to all shards
        shard_tasks = []
        for shard in self.shards:
            task = asyncio.create_task(
                shard.search(query, filters, limit=100)
            )
            shard_tasks.append(task)

        # Gather results from all shards
        shard_results = await asyncio.gather(*shard_tasks)

        # Merge and rank results globally
        merged_results = self.merge_and_rank(shard_results)

        # Cache popular results
        if self.is_popular_query(query):
            await self.cache.set(cache_key, merged_results, ttl=600)

        return merged_results
```

**Guarantees**:
- Fast lookup through indexing
- Distributed scalability
- Relevance ranking

## Pattern Selection Matrix

| **Requirement** | **Recommended Pattern** | **Alternative** | **Avoid** |
|---|---|---|---|
| Atomic multi-service operation | Saga | Two-phase commit | Distributed transactions |
| High-throughput inventory | Escrow | Global locks | Optimistic concurrency |
| Audit requirements | Event Sourcing | Change logs | CRUD with audit table |
| Read/write performance gap | CQRS | Read replicas | Single model |
| Tail latency sensitive | Hedged Request | Caching only | Synchronous calls |
| Cross-cutting concerns | Sidecar | Library per service | Embedded logic |
| Cache consistency | Write-Through | Eventual consistency | Cache-aside |
| Fault isolation | Bulkhead | Global resources | Shared thread pools |

## Anti-Pattern Detection

### Common Mistakes

1. **Distributed Transactions**: Using 2PC instead of Saga
   - Detection: XA transaction monitoring
   - Fix: Replace with Saga pattern

2. **Dual Writes**: Writing to DB and message broker separately  
   - Detection: Inconsistency between DB and events
   - Fix: Use Outbox pattern

3. **Global Locks**: Single lock for high-contention resource
   - Detection: Lock wait time monitoring
   - Fix: Use Escrow with sharding

4. **Synchronous Saga**: Calling all saga steps synchronously
   - Detection: High latency for complex operations
   - Fix: Asynchronous orchestration

5. **Unbounded Queues**: No backpressure in event processing
   - Detection: Memory growth, processing lag
   - Fix: Add Bulkhead pattern

## Performance Characteristics

| **Pattern** | **Latency** | **Throughput** | **Consistency** | **Complexity** |
|---|---|---|---|---|
| Outbox | +5-10ms | High | Strong | Medium |
| Saga | +50-200ms | Medium | Eventual | High |
| Escrow | +1-5ms | High | Strong | Medium |
| Event Sourcing | +10-20ms | High | Strong | High |
| CQRS | Read: <1ms, Write: +5ms | Very High | Eventual | High |
| Hedged Request | P99 improved | +50% load | N/A | Low |
| Sidecar | +1-5ms | High | N/A | Medium |
| Leader-Follower | +2-10ms | High | Strong | Medium |