# Site Structure Specification v2.0.0
## Production-First MkDocs Documentation Framework

### Streamlined MkDocs Navigation

```
ds-framework.dev/
├── home/                               # Landing page and overview
├── getting-started/
│   ├── overview/                       # Framework introduction
│   ├── quick-start/                    # Production deployment guide
│   └── concepts/                       # Core concepts and terminology
├── foundation/
│   ├── universal-laws/                 # CAP theorem, Little's law, etc.
│   ├── capabilities/                   # System capabilities taxonomy
│   └── primitives/                     # Building block patterns
├── guarantees/
│   ├── overview/                       # Consistency and availability guarantees
│   └── index/                          # Guarantee catalog
├── mechanisms/
│   ├── overview/                       # Implementation mechanisms
│   └── index/                          # Mechanism catalog
├── patterns/
│   ├── overview/                       # Architectural patterns
│   ├── production-architecture/        # Real-world reference architectures
│   ├── system-patterns/                # Large-scale system patterns
│   ├── micro-patterns/                 # Component-level patterns
│   ├── decision-engine/                # Pattern selection framework
│   ├── mechanisms/                     # Pattern-mechanism mapping
│   └── pattern-catalog/                # Comprehensive pattern index
├── case-studies/
│   ├── overview/                       # Production system analyses
│   ├── netflix/                        # Netflix microservices architecture
│   ├── uber/                           # Uber ride-hailing platform
│   ├── framework/                      # Analysis framework methodology
│   ├── data-collection/                # Metrics and measurement approach
│   └── comparisons/                    # Cross-company comparison matrices
├── examples/
│   ├── case-studies/                   # Detailed implementation examples
│   ├── implementation/                 # Code samples and configurations
│   └── pitfalls/                       # Common mistakes and anti-patterns
├── production/
│   ├── reality/                        # Production challenges and solutions
│   ├── best-practices/                 # Battle-tested recommendations
│   └── proof-obligations/              # Testing and validation requirements
└── reference/
    ├── api/                            # Framework API reference
    ├── glossary/                       # Terminology definitions
    └── reading/                        # Additional resources and papers
```

---

## Core Architectural Concepts

### 4-Plane Architecture (MANDATORY)
All diagrams MUST use these exact colors:

- **Edge Plane** (Blue #3B82F6): CDN, WAF, Load Balancers, API Gateways
- **Service Plane** (Emerald #10B981): Business Logic, Microservices, Application Logic
- **State Plane** (Amber #F59E0B): Databases, Caches, Storage, Message Queues
- **Control Plane** (Violet #8B5CF6): Monitoring, Config, Automation, Observability

**Note**: The architecture has been simplified from 5 planes to 4 planes. The former "Stream Plane" components are now part of the State Plane.

### Content Organization
- **Guarantees**: What the system promises (consistency, availability, etc.)
- **Mechanisms**: How guarantees are implemented (consensus, replication, etc.)
- **Patterns**: Complete architectural solutions combining mechanisms
- **Systems**: Real-world implementations (Netflix, Uber, etc.)

---

## Page Specifications

### 1. Home Page (/)

| Section | Content Type | Count | Description |
|---------|-------------|-------|-------------|
| Navigation Header | Table | 1 | Quick links to all major sections |
| Decision Matrix v2 | Interactive Table | 1 | Stressor → Pattern mapping |
| Mechanism Rules v2 | Matrix Diagram | 1 | Valid composition rules |
| Evolution Path v2 | Timeline Diagram | 1 | Stage progression triggers |
| Site Map | Hierarchical Diagram | 1 | Visual navigation tree |
| Search Box | Component | 1 | Full-text diagram search |
| Statistics | Table | 1 | Total diagrams, pages, updates |

### 2. Guarantee Pages (/guarantees/*)

Each guarantee page contains:

| Diagram Code | Type | Purpose | Node Count | Required Elements |
|--------------|------|---------|------------|-------------------|
| G-FL | Flow | Architecture placement | 80-100 | Plane heat, guarantee labels |
| G-SQ | Sequence | Test/proof sequence | 15-20 steps | Jepsen-style validation |
| G-ST | State Machine | Guarantee states | 8-12 states | Transitions, violations |
| G-CO | Consistency Graph | Causality relations | 20-30 nodes | Happens-before edges |
| G-ER | Data Model | Required metadata | 5-10 entities | Keys, TTLs, indices |
| G-MR | Multi-Region | Geo distribution | 5-8 regions | Sync modes, RPO/RTO |
| G-PR | Proof Harness | Verification map | 10-15 tests | Input/output specs |

Tables per guarantee page:

| Table | Rows | Columns | Content |
|-------|------|---------|---------|
| Summary | 1 | 8 | ID, Definition, SLO, Mechanisms, Patterns, Proofs, Cost, Links |
| Configuration | 10-15 | 5 | Parameter, Default, Range, Impact, Example |
| Failure Modes | 5-8 | 6 | Mode, Frequency, Detection, Mitigation, Recovery, Test |
| Cloud Mapping | 3 | 4 | AWS Service, GCP Service, Azure Service, OSS Alternative |
| Implementation | 5-10 | 4 | Language, Library, Config, Performance |

### 3. Mechanism Pages (/mechanisms/*)

Each mechanism page contains:

| Diagram Code | Type | Purpose | Node Count | Required Elements |
|--------------|------|---------|------------|-------------------|
| M-PL | Plane Placement | Where it lives | 4 planes | Requires/provides labels |
| M-FL | Internal Flow | Processing pipeline | 30-50 | Stages, queues, workers |
| M-SQ | Sequence | Hot/cold/failure paths | 20-30 msgs | Latency annotations |
| M-ST | State Machine | Internal states | 10-15 | Transitions, timeouts |
| M-RP | Requirements | Capability contracts | 20-30 | Valid/invalid edges |
| M-BP | Backpressure | Control overlay | 8-12 | Admission to shedding |
| M-SL | Latency Budget | Performance map | Per-edge | p50/p95/p99 labels |
| M-MR | Multi-Region | Distribution modes | 5-8 regions | Sync/async, fencing |
| M-FM | Failure Modes | Fault scenarios | 10-15 | Injection → recovery |
| M-CL | Cloud Binding | Service mapping | 3 clouds | Component → service |

### 4. Pattern Pages (/patterns/*)

Each pattern page contains:

| Diagram Code | Type | Purpose | Node Count | Required Elements |
|--------------|------|---------|------------|-------------------|
| P-L0 | Global Flow | Full architecture | 100-120 | All planes, mechanisms |
| P-L1 | Plane Views | Per-plane detail | 4×40 | Edge/Service/State/Control |
| P-SQ1 | Happy Path | Success sequence | 20-25 | End-to-end latencies |
| P-SQ2 | Failure Path | Degradation flow | 25-30 | Mitigation steps |
| P-BP | Backpressure | Control ladder | 10-12 | Full stack controls |
| P-MR1 | Multi-Region v1 | Region-pinned | 5-8 | Write locality |
| P-MR2 | Multi-Region v2 | Active-active | 5-8 | CRDT reconciliation |
| P-CO | Consistency | Boundary map | 15-20 | Linearizable zones |
| P-SL | Latency Map | Budget breakdown | Per-hop | Cumulative p99 |
| P-CP | Capacity | Resource planning | Tables | Partitions, connections |
| P-FM | Failures | Common outages | 15-20 | Top 5 scenarios |
| P-DR | Drills | Required tests | 10-15 | Chaos experiments |
| P-MG | Migration | Evolution path | 8-10 steps | Dual-write → cleanup |
| P-CL | Cloud Blueprint | Reference arch | 3 clouds | Service selection |
| P-EX | Exemplar | Case study | 30-40 | Real implementation |

---

## Content Requirements Per Section

### Guarantees Section (18 pages × 7 diagrams = 126 base diagrams)

**Pages:**
1. Linearizable
2. Sequential Consistency
3. Causal Consistency
4. Eventual Consistency
5. Bounded Staleness
6. Exactly Once
7. At Least Once
8. At Most Once
9. Read Your Writes
10. Monotonic Reads
11. Monotonic Writes
12. Write Follows Read
13. Five Nines Availability
14. Durability (N-way)
15. Partition Tolerance
16. Total Ordering
17. Idempotency
18. Isolation Levels (ACID)

**Per-page requirements:**
- 7 core diagrams (FL, SQ, ST, CO, ER, MR, PR)
- 5 tables (Summary, Config, Failures, Cloud, Implementation)
- 3 L2 detail diagrams for complex guarantees
- Cross-links to implementing mechanisms
- Cross-links to patterns that provide guarantee

### Mechanisms Section (22 pages × 10 diagrams = 220 base diagrams)

**Core Mechanisms (P1-P12):**
1. P1-Partition (hash, range, geo)
2. P2-Replicate (leader, multi-leader, leaderless)
3. P3-Durable Log (WAL, event log, audit)
4. P4-Broadcast (reliable, ordered, atomic)
5. P5-Consensus (Raft, Paxos, PBFT)
6. P6-Clock (logical, vector, hybrid)
7. P7-Quorum (majority, weighted, hierarchical)
8. P8-Chain (replication, causality)
9. P9-Converge (CRDT, OT, reconciliation)
10. P10-Orchestrate (workflow, saga, state machine)
11. P11-Shard Work Result (map-reduce, scatter-gather)
12. P12-Cache (write-through, write-back, aside)

**Micro Mechanisms:**
13. Outbox (transactional messaging)
14. Saga (distributed transactions)
15. Circuit Breaker (failure isolation)
16. Bulkhead (resource isolation)
17. Rate Limiter (admission control)
18. Retry (exponential backoff)
19. Timeout (cascading)
20. Hedge (speculative execution)
21. Load Balancer (L4/L7)
22. Service Mesh (sidecar proxy)

### Patterns Section (12 pages × 15 diagrams = 180 base diagrams)

**Primary Patterns:**
1. Request-Response (synchronous RPC)
2. Async Task (queue-worker)
3. Streaming (continuous processing)
4. Batch (periodic bulk)
5. CQRS (read/write separation)
6. Event Sourcing (append-only state)

**Overlay Patterns:**
7. Fan-Out (broadcast/multicast)
8. Search (indexing + query)
9. Graph (traversal + analytics)
10. ML Inference (model serving)
11. Ledger (immutable accounting)
12. Analytics (OLAP/warehouse)

---

## Production-First Diagram Distribution

| Section | Pages | Core Diagrams | Production Variants | Final |
|---------|-------|---------------|-------------------|-------|
| Foundation | 3 | 15 | 10 | 25 |
| Guarantees | 8 | 40 | 20 | 60 |
| Mechanisms | 12 | 120 | 80 | 200 |
| Patterns | 15 | 150 | 100 | 250 |
| Case Studies | 20 | 200 | 300 | 500 |
| Production | 3 | 30 | 50 | 80 |
| Reference | 3 | 15 | 10 | 25 |
| **TOTAL** | **64** | **570** | **570** | **1,140** |

**Focus:** Every diagram must address real production challenges with actual components, metrics, and failure modes.

---

## Navigation Structure

### Primary Navigation (Top Bar)
```
[Home] [Guarantees ▼] [Mechanisms ▼] [Patterns ▼] [Compositions] [Evolution] [Laws] [Cases] [Tools ▼]
```

### Breadcrumb Pattern
```
Home > Patterns > CQRS > Multi-Region Variant 2
```

### Cross-Reference Links
Every page includes:
- **Requires:** Links to prerequisite pages
- **Provides:** Links to capabilities offered
- **Related:** Similar or alternative approaches
- **Examples:** Case studies using this element
- **Tests:** Drill and proof pages

### Search Integration
- Full-text search across all diagrams
- Filter by: Type, Plane, Guarantee, Pattern
- Autocomplete with diagram previews
- Keyboard navigation (/)

---

## Responsive Design Breakpoints

| Breakpoint | Width | Layout | Diagram Display |
|------------|-------|--------|-----------------|
| Mobile | < 768px | Single column | Zoomable SVG |
| Tablet | 768-1024px | Two columns | Side-by-side |
| Desktop | 1024-1440px | Three columns | Grid view |
| Wide | > 1440px | Four columns | Dashboard |

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Initial Load | < 2s | Time to first diagram |
| Page Navigation | < 500ms | Client-side routing |
| Diagram Render | < 200ms | SVG display time |
| Search Results | < 100ms | Lunr.js query |
| Total Page Weight | < 2MB | Gzipped assets |
| Lighthouse Score | > 95 | Performance audit |

---

## Accessibility Requirements

- WCAG 2.1 AA compliance
- Keyboard navigation for all interactions
- Screen reader descriptions for diagrams
- High contrast mode support
- Reduced motion alternatives
- Focus indicators on all interactive elements

---

## Browser Support

| Browser | Minimum Version | Features |
|---------|----------------|----------|
| Chrome | 120+ | Full support |
| Firefox | 115+ | Full support |
| Safari | 16+ | Full support |
| Edge | 120+ | Full support |
| Mobile Safari | iOS 16+ | Touch zoom |
| Chrome Mobile | Android 12+ | Touch zoom |

---

*Version: 2.0.0 | Document 01 of 16 | Last Updated: 2025-01-18*