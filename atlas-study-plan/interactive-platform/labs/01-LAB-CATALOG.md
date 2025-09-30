# Hands-On Lab Catalog
## 100+ Production-Realistic Distributed Systems Laboratories

### Executive Summary

The Lab Catalog provides 100+ hands-on experiments where learners build, break, and fix distributed systems using real infrastructure. Each lab runs actual microservices in Kubernetes, generates realistic load, injects failures, and measures performance - exactly like production engineering.

**Philosophy**: Learn by doing. Break things safely. Build muscle memory for 3 AM incidents.

---

## 🎯 Lab Categories

### Foundation Labs (20 labs)
**Focus**: Core distributed systems concepts
**Duration**: 30-45 minutes each
**Infrastructure**: Docker Compose

### Pattern Implementation Labs (25 labs)
**Focus**: Implement architectural patterns from scratch
**Duration**: 1-2 hours each
**Infrastructure**: Kubernetes + Docker

### Company Architecture Labs (30 labs)
**Focus**: Recreate real-world systems (Netflix, Uber, etc.)
**Duration**: 2-3 hours each
**Infrastructure**: Kubernetes + Cloud resources

### Incident Response Labs (15 labs)
**Focus**: Debug production failures
**Duration**: 1-2 hours each
**Infrastructure**: Pre-broken systems

### Performance Tuning Labs (10 labs)
**Focus**: Optimize for throughput/latency
**Duration**: 2-3 hours each
**Infrastructure**: Load testing + monitoring

---

## 📚 Complete Lab Catalog

### Category 1: Foundation Labs (20 labs)

#### Lab 101: CAP Theorem in Action
**Objective**: Experience CAP theorem trade-offs firsthand

**What You'll Build**:
- 3-node distributed database cluster
- Network partition simulator
- Consistency verification tool

**Scenario**:
1. Start 3-node cluster with strong consistency
2. Generate write traffic
3. Inject network partition
4. Observe split-brain behavior
5. Choose CP vs. AP resolution

**Technologies**:
- etcd (CP system)
- Cassandra (AP system)
- Toxiproxy (network chaos)

**Learning Outcomes**:
- Understand consistency vs. availability trade-offs
- Experience network partitions
- Implement partition detection
- Design partition recovery

**Lab Structure**:
```yaml
lab-101-cap-theorem/
├── docker-compose.yml        # 3-node setup
├── setup.sh                  # Initialize cluster
├── inject-partition.sh       # Create network split
├── verify-consistency.sh     # Check data consistency
├── scenarios/
│   ├── scenario-1-cp.md     # Choose consistency
│   ├── scenario-2-ap.md     # Choose availability
│   └── scenario-3-heal.md   # Partition healing
├── monitoring/
│   ├── prometheus.yml       # Metrics collection
│   └── grafana-dashboard.json
└── README.md                # Lab instructions
```

**Success Criteria**:
- [ ] Successfully partition cluster
- [ ] Observe different behaviors in CP vs AP
- [ ] Implement quorum reads
- [ ] Restore consistency after partition heals

---

#### Lab 102: Consensus with Raft
**Objective**: Implement and understand Raft consensus algorithm

**What You'll Build**:
- 5-node Raft cluster
- Leader election simulator
- Log replication visualizer

**Scenario**:
1. Deploy 5-node etcd cluster
2. Kill leader, observe election
3. Generate log entries
4. Partition network, force split vote
5. Measure convergence time

**Technologies**:
- etcd (Raft implementation)
- Chaos Mesh (failure injection)
- Prometheus (metrics)

**Lab Structure**:
```yaml
lab-102-raft-consensus/
├── kubernetes/
│   ├── etcd-cluster.yaml
│   ├── chaos-experiments.yaml
│   └── monitoring.yaml
├── scripts/
│   ├── kill-leader.sh
│   ├── split-vote.sh
│   └── measure-convergence.sh
├── visualizer/
│   └── raft-visualizer.html  # Real-time visualization
└── exercises/
    ├── exercise-1-election.md
    ├── exercise-2-replication.md
    └── exercise-3-safety.md
```

**Learning Outcomes**:
- Understand leader election
- Visualize log replication
- Measure commit latency
- Handle split-brain scenarios

---

#### Lab 103: Sharding Strategies
**Objective**: Implement and compare different sharding approaches

**What You'll Build**:
- Range-based sharding system
- Hash-based sharding system
- Consistent hashing with virtual nodes
- Rebalancing automation

**Technologies**:
- PostgreSQL (range sharding)
- Redis Cluster (hash sharding)
- Vitess (consistent hashing)

**Scenario**:
1. Implement range sharding for user data
2. Generate hotspot on one shard
3. Migrate to consistent hashing
4. Add/remove nodes, observe rebalancing
5. Measure query performance

**Lab Structure**:
```yaml
lab-103-sharding/
├── implementations/
│   ├── range-sharding/
│   │   ├── schema.sql
│   │   └── proxy.py
│   ├── hash-sharding/
│   │   └── consistent-hash.py
│   └── vitess-setup/
│       └── vschema.json
├── benchmarks/
│   ├── workload-generator.py
│   └── compare-strategies.py
└── exercises/
    ├── exercise-1-implement-range.md
    ├── exercise-2-fix-hotspot.md
    └── exercise-3-rebalance.md
```

---

### Category 2: Pattern Implementation Labs (25 labs)

#### Lab 201: CQRS Pattern from Scratch
**Objective**: Build complete CQRS system with event sourcing

**What You'll Build**:
- Command API (write operations)
- Query API (read operations)
- Event store (Kafka)
- Read model projections
- Eventually consistent views

**Technologies**:
- Node.js (APIs)
- Kafka (event stream)
- PostgreSQL (write store)
- MongoDB (read projections)
- Redis (materialized views)

**Scenario**:
1. Implement command handler for orders
2. Publish domain events to Kafka
3. Build projection for order history
4. Handle out-of-order events
5. Implement snapshot optimization

**Lab Structure**:
```yaml
lab-201-cqrs-pattern/
├── services/
│   ├── command-api/
│   │   ├── src/
│   │   │   ├── handlers/
│   │   │   ├── aggregates/
│   │   │   └── events/
│   │   └── Dockerfile
│   ├── query-api/
│   │   ├── src/
│   │   │   ├── projections/
│   │   │   └── queries/
│   │   └── Dockerfile
│   └── projector/
│       ├── src/
│       │   ├── event-handlers/
│       │   └── snapshot-manager/
│       └── Dockerfile
├── infrastructure/
│   ├── kafka/
│   ├── postgres/
│   └── mongodb/
├── tests/
│   ├── integration/
│   └── performance/
└── exercises/
    ├── exercise-1-implement-command.md
    ├── exercise-2-build-projection.md
    ├── exercise-3-handle-eventual-consistency.md
    └── exercise-4-optimize-reads.md
```

**Learning Outcomes**:
- Separate read/write models
- Implement event sourcing
- Handle eventual consistency
- Build materialized views
- Optimize query performance

---

#### Lab 202: Circuit Breaker Pattern
**Objective**: Implement and tune circuit breaker for fault tolerance

**What You'll Build**:
- Microservice with external dependencies
- Circuit breaker library
- Failure injection system
- Monitoring dashboard

**Technologies**:
- Go (microservices)
- Resilience4j (circuit breaker)
- Toxiproxy (failure injection)
- Grafana (visualization)

**Scenario**:
1. Deploy service with flaky dependency
2. Implement circuit breaker
3. Tune failure threshold and timeout
4. Inject failures, observe state transitions
5. Measure impact on availability

**Lab Structure**:
```yaml
lab-202-circuit-breaker/
├── services/
│   ├── api-gateway/
│   ├── user-service/       # Stable service
│   └── payment-service/    # Flaky service
├── circuit-breaker/
│   ├── implementation.go
│   └── configuration.yaml
├── chaos/
│   ├── inject-latency.yaml
│   └── inject-errors.yaml
└── exercises/
    ├── exercise-1-implement-breaker.md
    ├── exercise-2-tune-parameters.md
    └── exercise-3-measure-impact.md
```

---

### Category 3: Company Architecture Labs (30 labs)

#### Lab 301: Netflix Microservices Architecture
**Objective**: Recreate Netflix's microservices platform

**What You'll Build**:
- 15-microservice system
- API Gateway (Zuul)
- Service discovery (Eureka)
- Circuit breakers (Hystrix)
- Chaos engineering (Simian Army)

**Technologies**:
- Spring Boot (microservices)
- Netflix OSS stack
- Kubernetes
- Prometheus + Grafana

**Scenario**:
1. Deploy complete microservices ecosystem
2. Route traffic through API gateway
3. Inject random pod failures (Chaos Monkey)
4. Observe circuit breaker behavior
5. Measure system resilience

**Lab Structure**:
```yaml
lab-301-netflix-architecture/
├── microservices/
│   ├── api-gateway/        # Zuul
│   ├── discovery-server/   # Eureka
│   ├── config-server/      # Spring Cloud Config
│   ├── user-service/
│   ├── video-catalog/
│   ├── recommendation/
│   └── ... (15 services total)
├── chaos/
│   ├── chaos-monkey.yaml
│   └── experiments/
├── monitoring/
│   ├── prometheus/
│   ├── grafana/
│   └── turbine/            # Hystrix dashboard
└── exercises/
    ├── exercise-1-deploy-all.md
    ├── exercise-2-chaos-experiment.md
    └── exercise-3-measure-resilience.md
```

**Learning Outcomes**:
- Build microservices architecture
- Implement service discovery
- Use circuit breakers
- Run chaos experiments
- Measure availability

---

#### Lab 302: Uber Real-Time Matching System
**Objective**: Build geo-distributed matching engine

**What You'll Build**:
- Geo-sharded database
- Real-time matching algorithm
- Location update stream processor
- Surge pricing calculator

**Technologies**:
- PostgreSQL + PostGIS
- Redis Geo
- Kafka Streams
- Go (matching service)

**Scenario**:
1. Ingest rider location updates
2. Query available drivers in radius
3. Implement matching algorithm
4. Handle high-density areas
5. Measure match latency

**Lab Structure**:
```yaml
lab-302-uber-matching/
├── services/
│   ├── location-ingestor/    # Kafka producer
│   ├── matching-engine/       # Core algorithm
│   ├── driver-tracker/        # Redis Geo
│   └── surge-calculator/      # Pricing
├── databases/
│   ├── postgres-postgis/
│   └── redis-cluster/
├── load-generator/
│   └── simulate-city.py      # 10K drivers + riders
└── exercises/
    ├── exercise-1-implement-matching.md
    ├── exercise-2-optimize-latency.md
    └── exercise-3-handle-surge.md
```

---

### Category 4: Incident Response Labs (15 labs)

#### Lab 401: Database Cascade Failure
**Objective**: Debug and resolve cascading database failure

**What You'll Build**: None - system is pre-broken!

**Scenario** (Real incident recreation):
```
09:00 - System running normally, 50K req/s
09:15 - Slow query detected, P99 latency spikes
09:20 - Connection pool exhausted on API servers
09:25 - API servers start crashing (OOM)
09:30 - Load balancer marks all servers unhealthy
09:35 - Complete service outage

Your mission: Debug and fix within 30 minutes
```

**Lab Structure**:
```yaml
lab-401-cascade-failure/
├── broken-system/           # Pre-deployed broken state
├── monitoring/
│   ├── grafana/            # Metrics dashboard
│   ├── logs/               # Aggregated logs
│   └── traces/             # Distributed traces
├── debugging-tools/
│   ├── query-analyzer.sh
│   ├── connection-pool-monitor.sh
│   └── heap-dump-analyzer.py
└── solution-guide.md       # Sealed until attempt complete
```

**Learning Outcomes**:
- Identify cascade patterns
- Use monitoring tools
- Fix root cause
- Implement safeguards

---

### Category 5: Performance Tuning Labs (10 labs)

#### Lab 501: Database Query Optimization
**Objective**: Optimize slow queries under production load

**What You'll Build**:
- Load generator (realistic queries)
- Performance profiler
- Index optimizer

**Scenario**:
1. Run production-like workload
2. Identify slowest queries (P99 > 100ms)
3. Add indexes, measure impact
4. Optimize schema design
5. Implement caching layer

**Technologies**:
- PostgreSQL
- pg_stat_statements
- EXPLAIN ANALYZE
- Redis (caching)

**Lab Structure**:
```yaml
lab-501-query-optimization/
├── database/
│   ├── schema.sql          # Unoptimized schema
│   └── seed-data.sql       # 10M rows
├── workload/
│   ├── generate-load.py    # Realistic queries
│   └── query-patterns.yaml
├── optimization/
│   ├── analyze-slow-queries.sh
│   ├── suggest-indexes.py
│   └── verify-improvement.sh
└── exercises/
    ├── exercise-1-find-slow-queries.md
    ├── exercise-2-add-indexes.md
    └── exercise-3-implement-caching.md
```

---

## 🎯 Lab Difficulty Progression

### Beginner Labs (1-10)
- **Prerequisites**: Basic Docker knowledge
- **Guidance**: Step-by-step instructions
- **Hints**: Available immediately
- **Solutions**: Provided after attempt

### Intermediate Labs (11-50)
- **Prerequisites**: Kubernetes basics, programming
- **Guidance**: High-level objectives
- **Hints**: Available after 15 minutes
- **Solutions**: Provided after 30 minutes

### Advanced Labs (51-100)
- **Prerequisites**: Production experience
- **Guidance**: Problem statement only
- **Hints**: Minimal, on request
- **Solutions**: Provided after completion or 2 hours

---

## 🏗️ Lab Infrastructure

### Required Resources Per User
```yaml
Minimum Compute:
  CPU: 4 cores
  Memory: 8 GB
  Storage: 50 GB

Recommended Compute:
  CPU: 8 cores
  Memory: 16 GB
  Storage: 100 GB

Network:
  Bandwidth: 10 Mbps
  Latency: < 50ms to lab infrastructure
```

### Auto-Provisioning System
```typescript
class LabProvisioner {
  async provisionLab(userId: string, labId: string): Promise<LabEnvironment> {
    // 1. Check resource availability
    const available = await this.checkResourceQuota(userId);
    if (!available) throw new QuotaExceededError();

    // 2. Clone lab template
    const template = await this.getLabTemplate(labId);

    // 3. Create isolated namespace
    const namespace = await this.createKubernetesNamespace(
      `user-${userId}-lab-${labId}`
    );

    // 4. Deploy lab infrastructure
    const resources = await this.deployLabResources(namespace, template);

    // 5. Wait for ready state
    await this.waitForReady(resources);

    // 6. Generate access credentials
    const credentials = await this.generateCredentials(namespace);

    // 7. Setup monitoring
    await this.setupMonitoring(namespace, userId, labId);

    return {
      namespace,
      resources,
      credentials,
      endpoints: this.getServiceEndpoints(resources),
      monitoring: this.getMonitoringDashboard(namespace)
    };
  }

  async cleanupLab(userId: string, labId: string): Promise<void> {
    const namespace = `user-${userId}-lab-${labId}`;

    // 1. Backup lab progress
    await this.backupLabState(namespace);

    // 2. Delete all resources
    await this.deleteNamespace(namespace);

    // 3. Release quota
    await this.releaseResourceQuota(userId);
  }
}
```

---

## 📊 Lab Analytics

### Tracking Metrics
- **Completion Rate**: % of users who finish lab
- **Time to Complete**: Average duration
- **Hint Usage**: How many users need hints
- **Error Patterns**: Common mistakes
- **Success Paths**: Optimal solution approaches

### Learning Insights
```typescript
interface LabAnalytics {
  labId: string;
  metrics: {
    attempts: number;
    completions: number;
    completionRate: number;
    avgTimeToComplete: number;
    hintsRequested: number;
    commonErrors: ErrorPattern[];
  };
  learningOutcomes: {
    conceptUnderstanding: number; // 1-5 rating
    practicalApplication: number;
    retentionAfter30Days: number;
  };
}
```

---

## 🎓 Lab Certification

### Completion Criteria
- [ ] Complete all exercises
- [ ] Pass automated tests
- [ ] Submit working solution
- [ ] Explain approach in writeup
- [ ] Answer comprehension questions

### Lab Badges
- **Foundation Master**: Complete all 20 foundation labs
- **Pattern Architect**: Complete all 25 pattern labs
- **Company Expert**: Complete 10+ company labs
- **Incident Commander**: Complete all 15 incident labs
- **Performance Engineer**: Complete all 10 performance labs
- **Atlas Master**: Complete all 100 labs

---

## 🔗 Related Documentation

- [02-KUBERNETES-SETUP.md](./02-KUBERNETES-SETUP.md) - Cluster configuration
- [03-DOCKER-ENVIRONMENTS.md](./03-DOCKER-ENVIRONMENTS.md) - Container images
- [04-TERRAFORM-MODULES.md](./04-TERRAFORM-MODULES.md) - IaC templates
- [05-CHAOS-EXPERIMENTS.md](./05-CHAOS-EXPERIMENTS.md) - Failure injection
- [06-PERFORMANCE-TESTING.md](./06-PERFORMANCE-TESTING.md) - Load testing
- [07-LAB-PROVISIONING.md](./07-LAB-PROVISIONING.md) - Auto-provisioning system

---

*"Read about distributed systems. Break them yourself. Fix them confidently."*

**100+ Labs. 1000+ Hours. Production-Ready Skills.**