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