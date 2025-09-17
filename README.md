# Distributed Systems Atlas
## Production-First Architecture Documentation

A comprehensive documentation framework for distributed systems, featuring 900+ production-quality diagrams based on real architectures from Netflix, Uber, Stripe, and 100+ other companies operating at massive scale.

---

## 📁 Repository Structure

```
DS/
├── site/                    # MkDocs documentation site
│   ├── docs/               # Documentation content
│   │   ├── diagrams/       # Production diagram templates
│   │   ├── patterns/       # System and micro patterns
│   │   ├── guarantees/     # Consistency guarantees
│   │   ├── mechanisms/     # Core mechanisms
│   │   └── reference/      # API and glossary
│   ├── scripts/            # Build and validation scripts
│   └── mkdocs.yml         # Site configuration
│
├── readonly-spec/          # Comprehensive specifications
│   ├── 00-MASTER-SPECIFICATION-V4-FINAL.md
│   ├── 17-DIAGRAM-TRACKING.md
│   ├── 18-PRODUCTION-DATA-SOURCES.md
│   └── ...                # 20+ specification documents
│
├── reference/              # Core framework documents
│   ├── 00-overview.md     # Production-first philosophy
│   ├── 03-primitives.md   # 20 production-tested primitives
│   ├── 06-decision-engine.md
│   └── 07-production-reality.md
│
└── CLAUDE.md              # AI assistant instructions
```

---

## 🎯 Core Philosophy

### The 3 AM Test
> "Every diagram must help someone fix a production issue at 3 AM."

### Production-First Approach
- **Real Systems**: Netflix, Uber, Stripe architectures as they run today
- **Real Metrics**: Actual performance numbers from engineering blogs
- **Real Incidents**: AWS S3 2017, GitHub 2018, Cloudflare 2020
- **Real Costs**: $ amounts from production deployments

---

## 🚀 Quick Start

### 1. View Documentation Site

```bash
cd site
make serve   # Starts local server at http://127.0.0.1:8000
```

### 2. Build Static Site

```bash
cd site
make build   # Generates static site in site/site/
```

### 3. Run Tests

```bash
cd site
make test    # Validates diagrams and links
```

---

## 📊 Content Overview

### Guarantees (18 types)
- Linearizability, Sequential, Eventual Consistency
- Exactly Once, At Least Once, At Most Once
- Durability levels, Availability targets

### Mechanisms (20 primitives)
- Consensus (Raft, Paxos)
- Replication (Sync, Async, Quorum)
- Partitioning (Hash, Range, Geographic)
- Caching, Load Balancing, Rate Limiting

### Patterns (21 total)
- **Micro-patterns** (15): Outbox, Saga, CQRS, Event Sourcing
- **System patterns** (6): Lambda, Kappa, Microservices

### Case Studies (120+ systems)
- **Streaming**: Netflix, YouTube, Twitch
- **Mobility**: Uber, Lyft, DoorDash
- **Payments**: Stripe, PayPal, Square
- **Social**: Discord, Twitter, Instagram

---

## 📈 Production Metrics (2024)

### Scale Examples
- **Netflix**: 260M users, 200Tbps bandwidth
- **Uber**: 25M trips/day, 100M requests/sec
- **Stripe**: $1T annual volume, 99.999% uptime
- **Discord**: 15M concurrent users, 4B messages/day
- **Kafka@LinkedIn**: 7T events/day

### Infrastructure Costs
- **MySQL shard**: $500/month (20K writes/sec)
- **Redis cache node**: $200/month (1M ops/sec)
- **Kafka broker**: $1000/month (100K messages/sec)

---

## 📚 Key Documents

### Specifications
- [Master Specification](readonly-spec/00-MASTER-SPECIFICATION-V4-FINAL.md) - Production-first philosophy
- [Diagram Tracking](readonly-spec/17-DIAGRAM-TRACKING.md) - Progress on 1,233 diagrams
- [Production Data Sources](readonly-spec/18-PRODUCTION-DATA-SOURCES.md) - Verified metrics

### Reference
- [Overview](reference/00-overview.md) - Framework introduction
- [Primitives](reference/03-primitives.md) - Building blocks
- [Production Reality](reference/07-production-reality.md) - What actually breaks

### Templates
- [Diagram Templates](site/docs/diagrams/DIAGRAM_TEMPLATES.md) - Ready-to-use Mermaid templates

---

## 🛠️ Technology Stack

- **Site Generator**: MkDocs with Material theme
- **Diagrams**: Mermaid (embedded in markdown)
- **Validation**: Python scripts for quality checks
- **Deployment**: GitHub Pages

---

## 📋 Diagram Requirements

Every diagram must include:
- ✅ Real production data (not theoretical)
- ✅ Source attribution (engineering blog/talk)
- ✅ Specific instance types (r5.24xlarge)
- ✅ Actual costs ($/month)
- ✅ Latency metrics (p50, p99)
- ✅ Failure modes and recovery
- ✅ Scale limits from production

---

## 🤝 Contributing

See [Contribution Guidelines](readonly-spec/14-GOVERNANCE-CONTRIBUTION.md)

### Diagram Creation Workflow
1. Check [Diagram Tracking](readonly-spec/17-DIAGRAM-TRACKING.md) for unassigned diagrams
2. Use [Production Data Sources](readonly-spec/18-PRODUCTION-DATA-SOURCES.md) for metrics
3. Follow [Diagram Templates](site/docs/diagrams/DIAGRAM_TEMPLATES.md)
4. Submit PR with validation checks passed

---

## 📖 Learning Path

### For System Architects
1. Start with [Patterns](site/docs/patterns/)
2. Study [Case Studies](site/docs/case-studies/)
3. Review [Production Reality](reference/07-production-reality.md)

### For SREs/DevOps
1. Focus on [Mechanisms](site/docs/mechanisms/)
2. Study incident timelines in case studies
3. Review failure modes and recovery procedures

### For Developers
1. Start with [Guarantees](site/docs/guarantees/)
2. Understand [Primitives](reference/03-primitives.md)
3. Apply patterns from [Micro-patterns](site/docs/patterns/micro-patterns.md)

---

## 📝 License

This project is for educational purposes. All referenced architectures and metrics are from public sources (engineering blogs, conference talks).

---

## 🔗 Resources

### Engineering Blogs
- [Netflix Tech Blog](https://netflixtechblog.com/)
- [Uber Engineering](https://eng.uber.com/)
- [Stripe Engineering](https://stripe.com/blog/engineering)
- [Discord Engineering](https://discord.com/blog/engineering)

### Conferences
- AWS re:Invent
- QCon
- KubeCon
- Kafka Summit

---

*Built with production-first philosophy: If it doesn't help at 3 AM, it doesn't belong here.*