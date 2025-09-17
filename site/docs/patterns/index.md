# Atlas Patterns: Complete Architecture Framework

The Atlas framework provides a comprehensive catalog of proven distributed systems patterns, organized by complexity and scope. This index helps you navigate the pattern hierarchy and select the right architectural approaches for your requirements.

## Pattern Hierarchy

```
📁 Atlas Framework
├── 🔧 Mechanisms (22) - Building blocks
├── 🧩 Micro-Patterns (15) - Specific solutions
├── 🏗️ System Patterns (6) - Complete architectures
└── 🌐 Meta-Patterns (3) - Enterprise scale
```

## Quick Navigation

### By Complexity Level

| **Level** | **Count** | **Purpose** | **When to Use** |
|-----------|-----------|-------------|-----------------|
| **[Mechanisms](mechanisms.md)** | 22 | Infrastructure building blocks | All distributed systems |
| **[Micro-Patterns](micro-patterns.md)** | 15 | Specific problem solutions | Targeted issues |
| **[System Patterns](system-patterns.md)** | 6 | Complete architectures | Greenfield or major refactor |
| **[Meta-Patterns](pattern-catalog.md)** | 3 | Enterprise frameworks | Global, multi-system scale |

### By Problem Domain

| **Domain** | **Patterns** | **Primary Use Cases** |
|------------|--------------|---------------------|
| **Reliability** | Circuit Breaker, Retry, Timeout, Bulkhead | Fault tolerance, system stability |
| **Consistency** | Outbox, Saga, Event Sourcing, CQRS | Data integrity, audit trails |
| **Performance** | Caching, Load Balancer, Hedge, Batch | Low latency, high throughput |
| **Scalability** | Partitioning, Streaming, Fan-out, Cell-Based | Horizontal scaling, global reach |
| **Data Processing** | Analytics, Search, ML Inference, Graph | Complex queries, real-time processing |

## Decision Guide

### Quick Pattern Selection

Use this decision tree to quickly identify suitable patterns:

```
1. What's your primary challenge?
   ├─ 🔥 Reliability Issues → Start with Mechanisms
   ├─ ⚡ Performance Problems → Micro-Patterns + Caching
   ├─ 📈 Scale Requirements → System Patterns
   └─ 🏢 Enterprise Complexity → Meta-Patterns

2. How complex is your current system?
   ├─ 🏠 Single Application → Add Mechanisms
   ├─ 🏢 Multiple Services → Implement Micro-Patterns
   ├─ 🏙️ Distributed System → Adopt System Patterns
   └─ 🌍 Global Platform → Design Meta-Patterns

3. What's your team's experience?
   ├─ 👶 Beginner → Start with 3-5 core mechanisms
   ├─ 🧑‍💼 Intermediate → Implement 2-3 micro-patterns
   ├─ 👨‍💻 Advanced → Design system patterns
   └─ 🧙‍♂️ Expert → Architect meta-patterns
```

### By Scale Requirements

| **Scale Tier** | **QPS Range** | **Recommended Patterns** | **Infrastructure** |
|----------------|---------------|-------------------------|-------------------|
| **Startup** | < 1K QPS | Timeout, Retry, Cache | Single region, basic monitoring |
| **Growth** | 1K - 50K QPS | + Circuit Breaker, Load Balancer | Multi-AZ, comprehensive monitoring |
| **Scale** | 50K - 500K QPS | + CQRS, Microservices | Multi-region, auto-scaling |
| **Hyperscale** | > 500K QPS | + Cell-Based, Edge Computing | Global distribution, ML-driven ops |

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
**Essential Mechanisms**
- [ ] [Timeout](mechanisms.md#timeout) - Bound all operations
- [ ] [Retry](mechanisms.md#retry) - Handle transient failures
- [ ] [Circuit Breaker](mechanisms.md#circuit-breaker) - Prevent cascading failures
- [ ] [Load Balancer](mechanisms.md#load-balancer) - Distribute traffic

**Success Criteria**: 99.9% availability, P99 latency < 500ms

### Phase 2: Optimization (Weeks 5-12)
**Performance Patterns**
- [ ] [Caching](micro-patterns.md#caching) - Reduce latency
- [ ] [Bulkhead](mechanisms.md#bulkhead) - Isolate failures
- [ ] [Rate Limiter](mechanisms.md#rate-limiter) - Control traffic

**Success Criteria**: 99.95% availability, P99 latency < 200ms

### Phase 3: Consistency (Weeks 13-24)
**Data Patterns**
- [ ] [Outbox](micro-patterns.md#outbox-pattern) - Atomic operations
- [ ] [CQRS](micro-patterns.md#cqrs-pattern) - Separate read/write models
- [ ] [Event Sourcing](micro-patterns.md#event-sourcing) - Complete audit trail

**Success Criteria**: Strong consistency, complete audit trail

### Phase 4: Scale (Months 7-12)
**System Patterns**
- [ ] [Microservices](system-patterns.md#microservices) - Service autonomy
- [ ] [Event-Driven](micro-patterns.md#streaming-pattern) - Async processing
- [ ] [Cell-Based](system-patterns.md#cell-based-architecture) - Fault isolation

**Success Criteria**: Independent scaling, regional fault isolation

## Pattern Compatibility Matrix

### Safe Combinations ✅

| **Primary** | **Secondary** | **Benefit** | **Complexity** |
|-------------|---------------|-------------|----------------|
| Circuit Breaker + Retry | Timeout | Complete failure handling | Low |
| Load Balancer + Health Checks | Bulkhead | Traffic distribution + isolation | Medium |
| CQRS + Event Sourcing | Outbox | Read optimization + audit | High |
| Microservices + Service Mesh | Event-Driven | Service autonomy + communication | Very High |

### Incompatible Combinations ❌

| **Pattern A** | **Pattern B** | **Conflict** | **Resolution** |
|---------------|---------------|--------------|----------------|
| Sync Saga | High Latency SLA | Blocking operations | Use async orchestration |
| Shared Database | Microservices | Tight coupling | Database per service |
| Global Locks | Partitioning | Coordination overhead | Use escrow pattern |

## Reference Quick Card

### Core Mechanisms (Must Have)
```
🛡️ Reliability: Timeout + Retry + Circuit Breaker
⚖️ Load: Load Balancer + Rate Limiter
🔒 Isolation: Bulkhead + Service Mesh
💾 Caching: Multi-level cache hierarchy
```

### Essential Micro-Patterns
```
📤 Outbox: Atomic DB + events
🔄 Saga: Distributed transactions
📊 CQRS: Read/write separation
📝 Event Sourcing: Complete history
```

### System Pattern Selection
```
🏢 Microservices: Team autonomy (>5 teams)
💨 Serverless: Variable load patterns
🏭 Cell-Based: Blast radius control
🌐 Edge: Global low latency
```

## Getting Started

### For New Projects
1. **Start Simple**: Begin with [core mechanisms](mechanisms.md)
2. **Identify Needs**: Use the [decision guide](#decision-guide)
3. **Implement Gradually**: Follow the [roadmap](#implementation-roadmap)
4. **Monitor & Iterate**: Measure before optimizing

### For Existing Systems
1. **Assessment**: Review current architecture against patterns
2. **Risk Mitigation**: Add [reliability mechanisms](mechanisms.md) first
3. **Incremental Adoption**: Use [strangler fig pattern](system-patterns.md#migration-strategies)
4. **Team Training**: Ensure team understands chosen patterns

### For Enterprise Scale
1. **Architecture Review**: Map current state to meta-patterns
2. **Strategic Planning**: Define target architecture using system patterns
3. **Governance**: Establish pattern adoption guidelines
4. **Center of Excellence**: Create internal pattern expertise

## Pattern Documentation Structure

Each pattern page follows a consistent structure:

- **Problem Statement**: What specific issue does this solve?
- **Solution Architecture**: How does it work?
- **Implementation Guide**: Step-by-step implementation
- **Guarantees**: What does this pattern promise?
- **Trade-offs**: What are the costs and benefits?
- **Scale Variants**: How does it behave at different scales?
- **Failure Modes**: What can go wrong and how to handle it?
- **Examples**: Real-world implementations

## Related Resources

- **[Foundation](../foundation/universal-laws.md)**: Core principles and laws
- **[Production](../production/reality.md)**: Real-world considerations
- **[Examples](../examples/case-studies.md)**: Case studies and implementations
- **[Reference](../reference/glossary.md)**: Definitions and terminology

---

*The Atlas pattern framework is designed to be practical, proven, and production-ready. Every pattern has been validated in real-world systems at scale.*