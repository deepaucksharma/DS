# Overview

## What is a Distributed System?

A distributed system is a collection of independent computers that appears to its users as a single coherent system. The key characteristics are:

- **Multiple nodes** working together
- **Network communication** between components  
- **Shared state** or coordinated behavior
- **Partial failures** are normal
- **No global clock** or shared memory

## Why This Framework?

Most distributed systems education focuses on individual algorithms or technologies. This framework takes a different approach:

!!! success "Systematic Approach"
    - **Complete taxonomy** of all distributed systems concepts
    - **Mathematical foundation** with formal proofs
    - **Production-validated** patterns and solutions  
    - **Quantitative models** for performance and cost
    - **Decision algorithms** for automated design

## The Building Blocks

### Universal Laws (15)
Mathematical laws that govern all distributed systems. Examples:
- **CAP Theorem**: You can't have Consistency, Availability, and Partition tolerance simultaneously
- **Little's Law**: Concurrent users = arrival rate × response time  
- **Amdahl's Law**: Maximum speedup is limited by serial fraction

### Capabilities (30)
Fundamental guarantees systems provide:
- **Consistency**: LinearizableWrite, EventualConsistency, BoundedStaleness
- **Performance**: SubMillisecondRead, PredictableTail, ElasticScale
- **Availability**: HighAvailability, FaultTolerance, GracefulDegradation

### Primitives (20)
Building blocks that provide capabilities:
- **P1 Partitioning**: Split data across nodes for scale
- **P2 Replication**: Copy data for availability  
- **P5 Consensus**: Agree on single value across nodes

### Patterns (15)
Proven combinations of primitives:
- **Outbox**: Atomic DB update + event publishing
- **Saga**: Distributed transaction with compensations
- **CQRS**: Separate read and write models

## How to Use This Framework

### 1. Requirements Analysis
Start by identifying your:
- **Consistency needs** (financial vs social vs analytics)
- **Scale requirements** (reads/writes per second)  
- **Availability targets** (99.9% vs 99.99%)
- **Latency budgets** (milliseconds vs seconds)
- **Cost constraints** (budget limits)

### 2. Capability Mapping
Map requirements to specific capabilities:
```python
# Example: E-commerce checkout
required_capabilities = [
    'LinearizableWrite',    # For inventory updates
    'DurableWrite',         # For order persistence  
    'HighAvailability',     # For customer experience
    'SubSecondRead'         # For responsive UI
]
```

### 3. Primitive Selection  
Choose primitives that provide required capabilities:
```python
# Capabilities → Primitives mapping
primitives_needed = [
    'P1_Partitioning',      # For scale
    'P2_Replication',       # For availability
    'P5_Consensus',         # For consistency
    'P11_Caching'           # For performance
]
```

### 4. Pattern Composition
Combine primitives into proven patterns:
```python
# Pattern detection
if has_primitives(['P3_DurableLog', 'P7_Idempotency', 'P19_CDC']):
    recommended_pattern = 'Outbox'
```

### 5. Validation
Verify the design meets requirements:
```python
# Automated validation
calculated_throughput = min(bottlenecks) * 0.7
calculated_availability = 1 - (1 - node_availability) ** replication_factor

assert calculated_throughput >= required_throughput
assert calculated_availability >= required_availability
```

## Learning Path

### Beginner Path
1. **Foundation** → Universal Laws (understand the constraints)
2. **Foundation** → Capabilities (learn what systems can provide)  
3. **Patterns** → Micro-Patterns (see proven solutions)
4. **Examples** → Case Studies (real-world applications)

### Intermediate Path  
1. **Foundation** → Primitives (understand building blocks)
2. **Patterns** → System Patterns (complete architectures)
3. **Production** → Reality Check (what actually breaks)
4. **Examples** → Implementation Guides (how to build)

### Advanced Path
1. **Patterns** → Decision Engine (algorithmic design)
2. **Production** → Proof Obligations (formal verification)
3. **Reference** → API Reference (implementation details)
4. **Examples** → Common Pitfalls (what to avoid)

## Key Principles

### Design for Failure
- Assume every component will fail
- Plan for network partitions
- Design graceful degradation
- Test failure scenarios regularly

### Measure Everything  
- Latency percentiles (not just averages)
- Error rates by component
- Resource utilization trends
- Business impact metrics

### Start Simple
- Begin with proven patterns
- Add complexity only when needed
- Prefer boring technology
- Optimize based on measurements

### Learn from Production
- Monitor continuously
- Conduct blameless postmortems  
- Practice chaos engineering
- Document lessons learned

## Next Steps

Ready to dive deeper? Here are your next steps:

1. **New to distributed systems?** → [Quick Start](quick-start.md)
2. **Want to understand the theory?** → [Foundation → Universal Laws](../foundation/universal-laws.md)
3. **Need to design a system?** → [Patterns → Decision Engine](../patterns/decision-engine.md)
4. **Building something specific?** → [Examples → Implementation Guides](../examples/implementation.md)

Remember: distributed systems are inherently complex. This framework helps you navigate that complexity systematically.