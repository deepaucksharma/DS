# Layer 4: Complete System Patterns

System patterns combine multiple micro-patterns and primitives to address architectural requirements at the system level. Each pattern represents a proven approach used by major technology companies.

| **Pattern** | **When to Use** | **Architecture** | **Guarantees** | **Scale Limits** | **Cost Model** | **Migration Path** |
|---|---|---|---|---|---|---|
| **CQRS** | Read/Write >10:1<br/>Different models needed | Write: PostgreSQL<br/>CDC: Debezium<br/>Stream: Kafka<br/>Read: Redis/ES | Write: Linearizable<br/>Read: BoundedStaleness(100ms-5s) | Write: 50K TPS<br/>Read: 1M QPS | 2x infrastructure<br/>3x complexity | 1. Add CDC<br/>2. Build projections<br/>3. Shadow reads<br/>4. Switch reads<br/>5. Optimize |
| **Event Sourcing** | Audit requirements<br/>Time travel needed | Events: Kafka<br/>Snapshots: S3<br/>State: Derived | Immutable history<br/>Replayable | 100K events/sec<br/>90 day retention | 3x storage<br/>2x compute | 1. Add events<br/>2. Dual write<br/>3. Event as truth<br/>4. Remove CRUD |
| **Microservices** | Team autonomy<br/>Independent deployment | Services: 10-100<br/>Mesh: Istio<br/>Gateway: Kong | Service autonomy<br/>Fault isolation | 100s of services<br/>10K RPS/service | Nx operational<br/>Network costs | 1. Identify boundaries<br/>2. Extract services<br/>3. Add mesh<br/>4. Decompose DB |
| **Serverless** | Spiky loads<br/>Low baseline | Functions: Lambda<br/>Gateway: APIG<br/>Storage: DynamoDB | Auto-scaling<br/>Pay-per-use | 10K concurrent<br/>15min timeout | $0.20/M requests<br/>+compute time | 1. Extract functions<br/>2. Add triggers<br/>3. Remove servers |
| **Cell-Based** | Blast radius control<br/>Multi-tenant | Cells: 100s<br/>Router: Global<br/>State: Per-cell | Fault isolation<br/>Predictable performance | 100K users/cell<br/>1000 cells | Linear with cells<br/>Router complexity | 1. Define cell size<br/>2. Build router<br/>3. Migrate cohorts<br/>4. Add cells |
| **Edge Computing** | Global latency<br/>Bandwidth costs | CDN: CloudFront<br/>Compute: Lambda@Edge<br/>Data: DynamoDB Global | <50ms globally<br/>Data locality | 100s of edges<br/>Limited compute | High fixed cost<br/>Complexity | 1. Static to CDN<br/>2. Add compute<br/>3. Replicate data<br/>4. Full edge |

## Detailed Pattern Analysis

### CQRS (Command Query Responsibility Segregation)

**Architecture Components**:
```yaml
write_side:
  database: PostgreSQL with strong consistency
  api: RESTful commands
  processing: Synchronous validation and persistence
  
stream_processing:
  cdc: Debezium capturing DB changes
  broker: Apache Kafka for event streaming
  routing: Topic per aggregate type
  
read_side:
  stores: 
    - Redis for fast lookups
    - Elasticsearch for search
    - Cassandra for time-series
  apis: GraphQL for flexible queries
  processing: Asynchronous projection building
```

**Guarantees**:
- Write consistency: Linearizable within aggregates
- Read performance: Sub-millisecond for cached data
- Eventually consistent: Projection lag typically <100ms
- Independent scaling: Read and write sides scale independently

**Implementation Checklist**:
- [ ] Command validation in write model
- [ ] Event schema evolution strategy
- [ ] Projection rebuilding mechanism
- [ ] Monitoring projection lag
- [ ] Fallback to write side for critical reads
- [ ] Dead letter queue for failed projections

### Event Sourcing

**Architecture Components**:
```yaml
event_store:
  primary: Apache Kafka (permanent retention)
  partitioning: By aggregate ID
  ordering: Per-partition ordering guaranteed
  
snapshot_store:
  storage: S3/GCS for large snapshots
  format: Protobuf/Avro for efficiency
  frequency: Every 1000 events or daily
  
query_side:
  projections: Multiple read models
  materialization: Real-time and batch
  caching: Redis for hot data
```

**Guarantees**:
- Complete audit trail: Every state change recorded
- Time travel: Reconstruct state at any point
- Replayability: Rebuild any projection from events
- Immutability: Events never modified, only appended

**Implementation Checklist**:
- [ ] Event schema versioning strategy
- [ ] Snapshot generation and restoration
- [ ] Event upcasting for schema evolution
- [ ] Projection rebuilding procedures
- [ ] Event retention and archival policies
- [ ] Monitoring event throughput and lag

### Microservices

**Architecture Components**:
```yaml
service_mesh:
  proxy: Envoy sidecar per service
  control_plane: Istio for traffic management
  security: mTLS between all services
  observability: Distributed tracing
  
api_gateway:
  external: Kong/Ambassador for public APIs
  internal: Service-to-service direct calls
  rate_limiting: Per-service and global limits
  
data_layer:
  pattern: Database per service
  sharing: Event-driven integration
  consistency: Eventual via events
```

**Guarantees**:
- Service autonomy: Independent deployment and scaling
- Fault isolation: Service failures don't cascade
- Technology diversity: Different stacks per service
- Team ownership: Clear service boundaries

**Implementation Checklist**:
- [ ] Service boundary definition (Domain-Driven Design)
- [ ] Inter-service communication patterns
- [ ] Distributed transaction handling (Saga pattern)
- [ ] Service discovery and load balancing
- [ ] Monitoring and distributed tracing
- [ ] CI/CD per service

### Cell-Based Architecture

**Architecture Components**:
```yaml
cell_structure:
  size: 10K-100K users per cell
  isolation: No shared state between cells
  replication: 3 cells per region minimum
  
global_router:
  placement: User ID hash or geographic
  failover: Automatic cell routing
  monitoring: Cell health and capacity
  
cell_internal:
  services: Full application stack
  database: Independent per cell
  cache: Local to cell
```

**Guarantees**:
- Blast radius: Failure affects only one cell
- Predictable performance: Known user count per cell
- Horizontal scaling: Add cells as needed
- Operational simplicity: Smaller fault domains

**Implementation Checklist**:
- [ ] Cell placement strategy
- [ ] Cross-cell data sharing patterns
- [ ] Cell provisioning automation
- [ ] Global data consistency requirements
- [ ] Cell evacuation procedures
- [ ] Monitoring cell utilization

## Pattern Selection Decision Tree

```
Start: What are your primary requirements?

1. Strong Consistency Required?
   ├─ Yes → Financial/Critical Data
   │   ├─ High Read Volume? → CQRS + Strong Write Side
   │   └─ Audit Critical? → Event Sourcing
   └─ No → Can Accept Eventual Consistency
       ├─ Team Autonomy Important? → Microservices
       ├─ Spiky/Variable Load? → Serverless
       ├─ Global Users? → Edge Computing
       └─ Large Scale + Isolation? → Cell-Based

2. Scale Requirements?
   ├─ <10K QPS → Monolith or Simple Services
   ├─ 10K-100K QPS → CQRS or Microservices
   ├─ 100K-1M QPS → Cell-Based or Edge
   └─ >1M QPS → Combination of patterns

3. Team Structure?
   ├─ Single Team → Monolith or CQRS
   ├─ 2-5 Teams → Microservices
   └─ >5 Teams → Cell-Based + Microservices
```

## Cost Analysis Framework

### Infrastructure Costs

```python
def calculate_pattern_cost(pattern, requirements):
    base_cost = {
        'CQRS': {
            'write_db': requirements.write_volume * 0.001,  # $1/1K writes
            'read_stores': requirements.read_volume * 0.0001,  # $0.1/1K reads
            'streaming': requirements.events * 0.0001,  # $0.1/1K events
            'multiplier': 2.0  # Dual infrastructure
        },
        'EventSourcing': {
            'event_store': requirements.events * 0.002,  # $2/1K events
            'snapshots': requirements.aggregates * 0.01,  # $10/1K aggregates
            'projections': requirements.read_models * 500,  # $500/read model
            'multiplier': 3.0  # Storage overhead
        },
        'Microservices': {
            'services': requirements.services * 1000,  # $1K/service/month
            'mesh': requirements.services * 200,  # $200/service for mesh
            'networking': requirements.inter_service_calls * 0.00001,
            'multiplier': requirements.services * 0.1  # Operational overhead
        },
        'Serverless': {
            'requests': requirements.requests * 0.0000002,  # $0.20/1M requests
            'duration': requirements.compute_seconds * 0.0000167,  # $16.67/1M GB-seconds
            'storage': requirements.storage_gb * 0.25,  # $0.25/GB/month
            'multiplier': 1.0  # Pay per use
        }
    }
    
    return base_cost[pattern]
```

### Operational Costs

| **Pattern** | **Engineering Overhead** | **Operational Complexity** | **Learning Curve** |
|---|---|---|---|
| CQRS | +50% development time | Medium | 3-6 months |
| Event Sourcing | +100% development time | High | 6-12 months |
| Microservices | +200% development time | Very High | 12+ months |
| Serverless | -20% development time | Low | 1-3 months |
| Cell-Based | +150% development time | High | 6-12 months |
| Edge Computing | +300% development time | Very High | 12+ months |

## Migration Strategies

### Safe Migration Patterns

1. **Strangler Fig**: Gradually replace old system
2. **Parallel Run**: Run old and new systems simultaneously  
3. **Database Decomposition**: Split data before services
4. **Event Bridge**: Use events to connect old and new
5. **Feature Flags**: Toggle between implementations

### Risk Mitigation

| **Risk** | **Mitigation** | **Detection** | **Rollback** |
|---|---|---|---|
| Data Loss | Dual write during migration | Data consistency checks | Restore from backup |
| Performance Degradation | Load testing in production | Latency monitoring | Feature flag off |
| Complexity Explosion | Incremental rollout | Error rate monitoring | Service rollback |
| Team Productivity Loss | Training and documentation | Velocity metrics | Temporary consultants |

Each system pattern represents a fundamental architectural approach proven at scale. Choose based on your specific requirements, team capabilities, and acceptable complexity trade-offs.