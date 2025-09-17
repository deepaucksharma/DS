# Atlas Distributed Systems Documentation Site

## 🎯 Mission
Generate **900 production-quality diagrams** documenting distributed systems patterns, guarantees, and real-world architectures.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Serve documentation locally
mkdocs serve
# Visit: http://127.0.0.1:8000

# 3. Start creating diagrams
python scripts/manual_source_discovery.py  # Weekly checklist
python scripts/progress_tracker.py         # Track progress
```

## 📁 Project Structure

```
site/
├── EXECUTION_MASTER.md      # 📍 START HERE - Complete execution guide
├── README.md               # This file
├── mkdocs.yml             # MkDocs configuration
├── requirements.txt       # Python dependencies
│
├── execution/             # Execution documentation
│   ├── EXECUTION.md       # Quick workflow
│   ├── MANUAL_WORKFLOW.md # Manual process details
│   └── DIAGRAM_STRATEGY.md # Comprehensive strategy
│
├── docs/                  # Documentation content
│   ├── index.md          # Home page
│   ├── patterns/         # Pattern Implementation diagrams
│   │   ├── cqrs/         # CQRS pattern variations
│   │   ├── event-sourcing/ # Event sourcing implementations
│   │   └── sagas/        # Saga pattern examples
│   ├── systems/          # Architecture Deep-Dives (30 companies)
│   │   ├── netflix/      # 8 Netflix diagrams
│   │   ├── uber/         # 8 Uber diagrams
│   │   └── [28 more]/    # 8 diagrams each
│   ├── incidents/        # Incident Anatomies (100)
│   ├── performance/      # Performance Profiles (80)
│   ├── costs/           # Cost Breakdowns (60)
│   ├── scaling/         # Scale Journeys (80)
│   ├── migrations/      # Migration Playbooks (60)
│   ├── debugging/       # Debugging Guides (100)
│   ├── capacity/        # Capacity Models (60)
│   ├── comparisons/     # Technology Comparisons (40)
│   ├── foundation/      # Guarantees, mechanisms, primitives
│   ├── examples/        # Case studies, implementations
│   └── production/      # Best practices, incidents
│
├── scripts/              # Automation scripts
│   ├── manual_source_discovery.py  # Find high-value content
│   ├── progress_tracker.py        # Track diagram progress
│   ├── validate_mermaid.py       # Validate diagrams
│   └── check_links.py            # Check for broken links
│
├── data/                 # Tracking data
│   ├── diagram-tracking.md        # Detailed status
│   ├── production-data-sources.md # Verified metrics
│   └── progress.json             # Progress history
│
└── .github/workflows/    # GitHub Actions
    ├── weekly-discovery.yml      # Weekly source discovery
    └── progress-tracking.yml     # Progress monitoring
```

## 📊 Current Progress

| Category | Target | Created | Status |
|----------|--------|---------|--------|
| **Architecture Deep-Dives** | 240 | 0 | ⬜ Pending |
| **Pattern Implementations** | 80 | 0 | ⬜ Pending |
| **Incident Anatomies** | 100 | 0 | ⬜ Pending |
| **Debugging Guides** | 100 | 0 | ⬜ Pending |
| **Scale Journeys** | 80 | 0 | ⬜ Pending |
| **Performance Profiles** | 80 | 0 | ⬜ Pending |
| **Cost Breakdowns** | 60 | 0 | ⬜ Pending |
| **Migration Playbooks** | 60 | 0 | ⬜ Pending |
| **Capacity Models** | 60 | 0 | ⬜ Pending |
| **Technology Comparisons** | 40 | 0 | ⬜ Pending |
| **TOTAL** | **900** | **0** | **0%** |

## 🎨 Diagram Standards

Every diagram MUST follow the **Four-Plane Architecture**:

- **Edge Plane** (#0066CC): CDN, WAF, Load Balancer
- **Service Plane** (#00AA00): API, Business Logic
- **State Plane** (#FF8800): Database, Cache
- **Control Plane** (#CC0000): Monitoring, Config

## 🏢 The 30 Must-Document Systems

### Tier 1: The Giants (8 diagrams each)
1. **Netflix** - Microservices, Chaos Engineering
2. **Uber** - Real-time matching, Geo-distributed
3. **Amazon** - Everything (DynamoDB, S3, Lambda)
4. **Google** - Spanner, BigTable, Borg
5. **Meta/Facebook** - TAO, Social Graph
6. **Microsoft** - Azure, Cosmos DB, Teams
7. **LinkedIn** - Kafka creators, Professional network
8. **Twitter/X** - Timeline generation, Real-time
9. **Stripe** - Payment processing, Financial consistency
10. **Spotify** - Music streaming, Discovery algorithms

### Tier 2: The Innovators (8 diagrams each)
11. **Airbnb** - Search, Pricing, Booking systems
12. **Discord** - Real-time chat/voice at scale
13. **Cloudflare** - Edge computing, DDoS protection
14. **GitHub** - Git at scale, Actions CI/CD
15. **Shopify** - E-commerce platform, Black Friday
16. **DoorDash** - Logistics, Real-time tracking
17. **Slack** - Enterprise messaging, Search
18. **Pinterest** - Visual discovery, Image serving
19. **Twitch** - Live streaming, Chat scale
20. **Coinbase** - Crypto exchange, Matching engine

### Tier 3: The Specialists (8 diagrams each)
21. **Reddit** - Comment trees, Voting system
22. **Datadog** - Metrics ingestion, Time series
23. **Robinhood** - Stock trading, Market data
24. **Zoom** - Video conferencing, WebRTC
25. **TikTok** - Recommendation algorithm, CDN
26. **Square** - Payment processing, Hardware
27. **Snap** - Ephemeral messaging, Stories
28. **Dropbox** - File sync, Storage optimization
29. **Instacart** - Grocery logistics, Inventory
30. **OpenAI** - LLM serving, ChatGPT scale

**Total Architecture Deep-Dives: 240 diagrams**

## 📝 9-12 Month Phased Approach

| Phase | Timeline | Target | Team Effort |
|-------|----------|--------|-------------|
| **Phase 1: Emergency Response** | Months 1-2 | 150 diagrams (incidents, debugging) | 60-80 hours/week |
| **Phase 2: Core Concepts** | Months 3-4 | 200 diagrams (guarantees, mechanisms) | 60-80 hours/week |
| **Phase 3: Pattern Library** | Months 5-6 | 150 diagrams (pattern implementations) | 60-80 hours/week |
| **Phase 4: Case Studies** | Months 7-9 | 240 diagrams (30 systems × 8) | 80-100 hours/week |
| **Phase 5: Polish & Gaps** | Months 10-12 | 160 diagrams (performance, costs, etc.) | 40-60 hours/week |

**Total**: 3-4 engineers at 50% allocation → 900 diagrams in 9-12 months

## 🛠️ Key Commands

```bash
# Build documentation
mkdocs build

# Validate Mermaid diagrams
python scripts/validate_mermaid.py

# Check progress
python scripts/progress_tracker.py

# Generate weekly checklist
python scripts/manual_source_discovery.py

# Check for broken links
python scripts/check_links.py
```

## 📚 Reference Documents

- **Start Here**: `EXECUTION_MASTER.md`
- **Strategy**: `execution/DIAGRAM_STRATEGY.md`
- **Tracking**: `data/diagram-tracking.md`

## 🏆 Success Criteria

- ✅ 900 production diagrams
- ✅ All follow 4-plane architecture
- ✅ Include real production metrics
- ✅ Help debug issues at 3 AM
- ✅ Complete in 12 weeks
- ✅ Document all 30 major systems

## ✅ Quality Gates

### The 3 AM Test
Every diagram must:
- Show exact error messages to look for
- Indicate which logs to check
- Specify metrics that indicate the issue
- Include runbook link or inline instructions
- Show recovery procedures

### The Production Reality Test
Every diagram must include:
- **Real company/system names** (not "Service A")
- **Actual metrics** (not "high performance")
- **Specific technologies** with versions
- **Failure scenarios** and recovery procedures
- **Cost information** where applicable
- **4-plane color scheme** (no exceptions)

## 📞 Support

- **Documentation**: See `/readonly-spec/` for specifications (read-only)
- **Theory**: See `/reference/` for distributed systems concepts (read-only)
- **Execution**: All active work happens in `/site/`

---

**Remember**: Every diagram must answer: *"How does this help me fix production at 3 AM?"*

**The Prime Directive**: If it doesn't help during an incident, during debugging, during capacity planning, or during architecture decisions - it doesn't belong here.