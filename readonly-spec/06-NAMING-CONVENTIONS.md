# Naming Conventions and ID System v2.0.0
## Production-First Specification for Diagram and Page Identification

### Overview

This document establishes the naming conventions and identification system for 900-1500 production diagrams and focused documentation in the Framework. Every element must follow these conventions to ensure consistency, searchability, and real-world applicability.

---

## Entity ID System

### Primary Entity IDs

| Entity Type | ID Pattern | Examples | Count |
|-------------|------------|----------|-------|
| Guarantee | G-{3-4 chars} | G-LIN, G-SEQ, G-CAU, G-EVE | 18 |
| Mechanism | M-P{1-2 digits} or M-{name} | M-P1, M-P12, M-OUTBOX | 22 |
| Pattern | P-{lowercase-slug} | P-CQRS, P-EVENT-SOURCING | 12 |
| Composition | C-{type}-{name} | C-VALID-MATRIX, C-RECIPE-SYNC | 10 |
| Evolution | E-S{0-5} | E-S0, E-S1, E-S5 | 6 |
| Law | L-{abbreviated} | L-CAP, L-LITTLE, L-AMDAHL | 12 |
| Case Study | CS-{COMPANY} | CS-NETFLIX, CS-UBER, CS-DISCORD | 25+ |
| Rosetta | R-{mapping} | R-CLOUD, R-ACADEMIA, R-OSS | 3 |
| Matrix | MX-{type} | MX-GUARANTEE-MECHANISM | 6 |
| Chooser | CH-{function} | CH-STRESSOR, CH-DECISION | 2 |

### Secondary Component IDs

| Component | ID Pattern | Examples |
|-----------|------------|----------|
| Plane | PL-{name} | PL-EDGE, PL-SERVICE, PL-STATE |
| Node | N-{entity}-{seq} | N-G-LIN-001, N-P-CQRS-042 |
| Edge | E-{from}-{to}-{seq} | E-N001-N002-001 |
| Subgraph | SG-{name}-{seq} | SG-CONSENSUS-001 |
| Table | T-{entity}-{type} | T-G-LIN-CONFIG |
| Section | S-{page}-{name} | S-HOME-NAV |

---

## Diagram Naming Convention

### Full Diagram Name Pattern

```
{entity_id}__{diagram_type}__{version}.{extension}
```

### Components Breakdown

| Component | Description | Rules | Examples |
|-----------|------------|-------|----------|
| entity_id | Entity identifier | Lowercase, hyphens | g-lin, p-cqrs, m-p3 |
| diagram_type | Diagram type code | Uppercase, 2-3 chars | FL, SQ, ST, MR |
| version | Semantic version | vX.Y.Z format | v1.0.0, v2.3.1 |
| extension | File format | mmd, svg, png | .svg, .mmd |

### Complete Examples

```
g-lin__FL__v1.0.0.svg          # Linearizability flow diagram v1.0.0
p-cqrs__SQ__v2.1.0.mmd          # CQRS sequence diagram source v2.1.0
m-p3__ST__v1.3.2.png           # P3 Log state machine v1.3.2
cs-uber__MR__v1.0.0.svg        # Uber multi-region diagram
e-s2__MG__v3.0.0.svg           # Evolution stage 2 migration
```

### Tiled Diagram Naming

When diagrams are split into tiles:

```
{base_name}__{tile_position}.{extension}
```

Examples:
```
p-streaming__FL__v1.0.0__NW.svg    # Northwest quadrant
p-streaming__FL__v1.0.0__NE.svg    # Northeast quadrant
p-streaming__FL__v1.0.0__SW.svg    # Southwest quadrant
p-streaming__FL__v1.0.0__SE.svg    # Southeast quadrant
p-streaming__FL__v1.0.0__index.html # Tile navigation page
```

---

## Case Study Naming Convention (Extended)

### Case Study ID Patterns

```
CS-{ORGANIZATION}
```

| Organization Type | ID Pattern | Examples |
|-------------------|------------|----------|
| Single Word | CS-{WORD} | CS-UBER, CS-NETFLIX, CS-STRIPE |
| Multi Word | CS-{WORD1}{WORD2} | CS-LINKEDIN, CS-DOORDASH |
| Abbreviated | CS-{ABBREV} | CS-AWS, CS-GCP, CS-META |
| Product Specific | CS-{ORG}-{PRODUCT} | CS-CLOUDFLARE-WORKERS, CS-AWS-DYNAMO |

### Case Study Diagram Types

| Diagram Code | Type | Description | Required |
|--------------|------|-------------|----------|
| L0 | Global Flow | Five-plane overview with guarantees | Yes |
| L1-EDGE | Edge Plane Zoom | Routing, admission, rate limiting | Yes |
| L1-SERVICE | Service Plane Zoom | Business logic, orchestration | Yes |
| L1-STREAM | Stream Plane Zoom | Events, async workflows | Yes |
| L1-STATE | State Plane Zoom | Persistence, consistency | Yes |
| CO | Consistency | Boundaries and models | Yes |
| MR | Multi-Region | Geographic distribution | Yes |
| BP | Backpressure | Flow control ladder | Yes |
| FM | Failure Modes | Top 5 failure scenarios | Yes |
| SL | SLA/Latency | Capacity and latency budgets | Yes |
| DR | Drills | Required chaos exercises | No |
| FM-{SCENARIO} | Failure Variant | Specific failure deep-dive | No |
| SCALE-{TIER} | Scale Variant | Startup vs hyperscale | No |
| MR-{VARIANT} | Region Variant | Alternative strategies | No |
| MIG | Migration | Evolution from previous | No |

### Case Study File Examples

```
cs-discord__L0__v1.0.0.svg           # Discord global flow (700M users, 40B messages/day)
cs-discord__L1-EDGE__v1.0.0.svg      # Discord edge plane (Cloudflare, 165 PoPs)
cs-discord__CO__v1.0.0.svg           # Discord consistency (eventual, channel ordering)
cs-discord__MR__v1.0.0.svg           # Discord multi-region (13 regions, 450ms p99)
cs-discord__BP__v1.0.0.svg           # Discord backpressure (rate limits, queues)
cs-discord__FM__v1.0.0.svg           # Discord failure modes (API outages, voice failures)
cs-discord__FM-CELEBRITY__v1.0.0.svg # Discord celebrity storm (10K+ joins/sec)
cs-discord__SCALE-700M__v1.0.0.svg   # Discord at 700M users (current scale)
```

### Case Study Data Organization

```
/site/docs/case-studies/
├── {category}/
│   ├── {organization}.md             # Production architecture analysis
│   ├── {organization}-metrics.md     # Scale metrics and SLAs
│   └── {organization}-evolution.md   # Architecture evolution timeline
├── index.md                          # Master index with comparison table
└── framework.md                      # Analysis methodology
```

### Case Study Categories

| Category | Directory | Example Organizations |
|----------|-----------|----------------------|
| Social & Feeds | social | Meta (Instagram/Facebook), Twitter/X, LinkedIn, Reddit |
| Messaging | messaging | Discord (700M users), Slack (20M DAU), WhatsApp (2B users) |
| Media Streaming | media | Netflix (260M subs), YouTube (2B users), Twitch, TikTok |
| Mobility & Logistics | mobility | Uber (130M monthly users), DoorDash, Lyft, Instacart |
| Commerce | commerce | Shopify (2M merchants), Amazon, Stripe (millions TPS) |
| FinTech | fintech | Stripe (99.99% uptime), Coinbase, Klarna, Adyen |
| Cloud Platforms | cloud | Cloudflare (20% web traffic), Fastly, Vercel, Railway |
| Data Platforms | data | Snowflake (exabyte scale), Databricks, ClickHouse |
| DevTools & CI/CD | devtools | GitHub (100M repos), Vercel, Railway, PlanetScale |
| Gaming & Real-time | gaming | Discord (voice/video), Riot Games, Epic Games |

### Confidence Level Naming

| Level | Code | Meaning | File Suffix |
|-------|------|---------|-------------|
| Definitive | A | Explicit architecture from official sources | _verified |
| Strong | B | Strong evidence with minor inference | _inferred |
| Partial | C | Partial info with significant inference | _estimated |

### Source Type Codes

| Code | Type | Example |
|------|------|----------|
| BLOG | Engineering Blog | discord.com/blog/engineering |
| TALK | Conference Talk | QCon, KubeCon presentation |
| PAPER | Academic/White Paper | USENIX, ACM publication |
| DOC | Official Documentation | Public architecture docs |
| VIDEO | Video Presentation | YouTube, InfoQ video |
| BOOK | Published Book | O'Reilly, Manning chapter |

### Case Study Version Strategy

```yaml
# Versioning for case studies follows architecture changes
versioning:
  major: "Fundamental architecture change"
  minor: "Significant component update"
  patch: "Metric updates, minor corrections"

examples:
  - "1.0.0": "Initial Discord architecture (2020, Elixir monolith)"
  - "2.0.0": "Post-outage microservices redesign (2021, Rust services)"
  - "2.1.0": "Added Go services and Scylla (2022, 500M users)"
  - "2.1.1": "Updated to current scale metrics (2024, 700M users)"
  - "3.0.0": "Voice/video infrastructure overhaul (2024, WebRTC)"
```

---

## File Path Structure

### Directory Organization

```
/assets/diagrams/{category}/{entity}/{diagram_name}
```

### Path Examples

```
/assets/diagrams/guarantees/g-lin/g-lin__FL__v1.0.0.svg
/assets/diagrams/patterns/p-cqrs/p-cqrs__SQ__v2.0.0.svg
/assets/diagrams/mechanisms/m-p3/m-p3__ST__v1.0.0.svg
/assets/diagrams/cases/mobility/cs-uber/cs-uber__MR__v1.0.0.svg
/assets/diagrams/cases/messaging/cs-discord/cs-discord__L0__v1.0.0.svg
/assets/diagrams/cases/media/cs-netflix/cs-netflix__L0__v1.0.0.svg
/assets/diagrams/cases/fintech/cs-stripe/cs-stripe__CO__v1.0.0.svg
```

### Source and Rendered Separation

```
/assets/diagrams/
├── mmd/                    # Mermaid source files
│   └── {category}/{entity}/{diagram}.mmd
├── svg/                    # Rendered SVG files
│   └── {category}/{entity}/{diagram}.svg
└── png/                    # PNG exports
    └── {category}/{entity}/{diagram}.png
```

---

## Page URL Structure

### URL Pattern

```
/{section}/{entity-slug}/[{subsection}/]
```

### URL Mapping Table

| Page Type | URL Pattern | Example URLs |
|-----------|------------|--------------|
| Home | / | / |
| Section Index | /{section}/ | /guarantees/, /patterns/ |
| Entity Page | /{section}/{entity}/ | /guarantees/linearizable/ |
| Subsection | /{section}/{entity}/{detail}/ | /patterns/cqrs/multi-region/ |
| Tool Page | /tools/{tool}/ | /tools/chooser/ |
| Matrix Page | /matrices/{type}/ | /matrices/guarantee-mechanism/ |

### Canonical URLs

```
https://atlas.example.com/guarantees/linearizable/
https://atlas.example.com/patterns/event-sourcing/
https://atlas.example.com/mechanisms/p3-durable-log/
https://atlas.example.com/case-studies/instagram/
```

---

## Table Naming Convention

### Table ID Pattern

```
T-{entity}-{table_type}
```

### Table Types

| Code | Type | Purpose | Example ID |
|------|------|---------|------------|
| SUM | Summary | Overview metrics | T-G-LIN-SUM |
| CFG | Configuration | Parameters | T-G-LIN-CFG |
| FLR | Failure Modes | Failure analysis | T-G-LIN-FLR |
| CLD | Cloud Mapping | Service mappings | T-G-LIN-CLD |
| IMP | Implementation | Code/libraries | T-G-LIN-IMP |
| PRF | Performance | Benchmarks | T-G-LIN-PRF |
| TST | Testing | Test suites | T-G-LIN-TST |
| CMP | Comparison | Side-by-side | T-G-LIN-CMP |

---

## Version Management

### Semantic Versioning Rules

| Version Component | When to Increment | Examples |
|-------------------|-------------------|----------|
| Major (X.0.0) | Breaking changes, contract changes | 1.0.0 → 2.0.0 |
| Minor (0.X.0) | New features, significant updates | 1.0.0 → 1.1.0 |
| Patch (0.0.X) | Bug fixes, label updates | 1.0.0 → 1.0.1 |

### Version History Tracking

```yaml
version_history:
  - version: "1.0.0"
    date: "2024-01-01"
    changes: "Initial diagram"
    author: "system"
  - version: "1.1.0"
    date: "2024-01-15"
    changes: "Added backpressure overlay"
    author: "team"
  - version: "2.0.0"
    date: "2024-02-01"
    changes: "Redesigned with new guarantees"
    breaking: true
```

---

## Cross-Reference Naming

### Internal Links Pattern

```
#{entity_id}-{diagram_type}
#g-lin-fl                    # Link to linearizability flow
#p-cqrs-sq                   # Link to CQRS sequence
#m-p3-st                     # Link to P3 state machine
```

### External Reference Pattern

```
{page_url}#{anchor}
/guarantees/linearizable/#g-lin-fl
/patterns/cqrs/#p-cqrs-implementation
```

### API Reference Pattern

```
/api/diagram/{entity_id}/{diagram_type}/{version}
/api/diagram/g-lin/fl/v1.0.0
/api/page/{section}/{entity}
/api/page/guarantees/linearizable
```

---

## MkDocs File Organization

### Direct Markdown with Embedded Mermaid

```
/site/docs/{category}/{entity}.md
```

Examples:
```
/site/docs/guarantees/linearizability.md         # Direct Mermaid in markdown
/site/docs/patterns/cqrs.md                      # Production CQRS examples
/site/docs/mechanisms/consensus.md               # Raft/Paxos implementations
```

### Asset Organization

```
/site/docs/assets/
├── diagrams/                      # Exported SVGs for sharing
├── images/                        # Screenshots and photos
└── data/                          # Production metrics CSV/JSON
```

---

## Search Index Naming

### MkDocs Search Integration

Built-in search powered by:
- **MkDocs Search Plugin**: Automatic indexing of all markdown content
- **Mermaid Integration**: Diagram titles and descriptions indexed
- **Tag Support**: Via frontmatter in markdown files

Example markdown frontmatter:
```yaml
---
title: "Netflix Microservices Architecture"
tags: [netflix, microservices, streaming, chaos-engineering]
category: case-study
scale: hyperscale
---
```

---

## Tag Naming Convention

### Tag Categories

| Category | Pattern | Examples |
|----------|---------|----------|
| Guarantee | guarantee:{name} | guarantee:linearizable |
| Plane | plane:{name} | plane:service |
| Pattern | pattern:{name} | pattern:cqrs |
| Consistency | consistency:{level} | consistency:strong |
| Availability | availability:{level} | availability:five-nines |
| Scale | scale:{tier} | scale:hyperscale |
| Industry | industry:{sector} | industry:fintech |
| Cloud | cloud:{provider} | cloud:aws |

### Compound Tags

```
consistency:strong+availability:high
pattern:cqrs+plane:service+scale:large
guarantee:exactly-once+mechanism:outbox
```

---

## Metadata Naming

### Diagram Metadata

```yaml
metadata:
  id: "g-lin-fl"
  entity_id: "g-lin"
  diagram_type: "FL"
  version: "1.0.0"
  created: "2024-01-01T00:00:00Z"
  modified: "2024-01-15T12:00:00Z"
  author: "system"
  reviewers: ["reviewer1", "reviewer2"]
  tags: ["guarantee", "linearizable", "flow"]
  dependencies: ["m-p5", "m-p7"]
  provides: ["strong-consistency"]
  requires: ["consensus", "quorum"]
```

### Page Metadata

```yaml
page:
  id: "guarantees-linearizable"
  url: "/guarantees/linearizable/"
  title: "Linearizability Guarantee"
  entity_id: "g-lin"
  diagrams: ["fl", "sq", "st", "co", "er", "mr", "pr"]
  tables: ["sum", "cfg", "flr", "cld", "imp"]
  related: ["g-seq", "g-cau", "m-p5"]
  seo_title: "Linearizability - Strongest Consistency Guarantee"
  seo_description: "Complete specification of linearizability with 7 diagrams and implementation guide"
```

---

## Validation Rules

### ID Validation Regex

```javascript
// Entity ID
/^[A-Z]-[A-Z0-9-]{1,20}$/

// Diagram name
/^[a-z-]+__[A-Z]{2,3}__v\d+\.\d+\.\d+\.(mmd|svg|png)$/

// Version
/^v\d+\.\d+\.\d+$/

// URL path
/^\/[a-z-]+\/[a-z-]+\/?$/

// Tag
/^[a-z]+:[a-z-]+$/
```

### Forbidden Characters

| Context | Forbidden | Use Instead |
|---------|-----------|-------------|
| IDs | Spaces, special chars | Hyphens, underscores |
| URLs | Spaces, uppercase | Lowercase, hyphens |
| Files | Spaces, unicode | ASCII, underscores |
| Tags | Spaces, caps | Lowercase, colons |

---

## Examples Summary

### Complete Entity Example: Linearizability

```yaml
entity:
  id: "G-LIN"
  slug: "linearizable"
  url: "/guarantees/linearizable/"

diagrams:
  - file: "g-lin__FL__v1.0.0.svg"
    id: "g-lin-fl"
    anchor: "#g-lin-fl"
  - file: "g-lin__SQ__v1.0.0.svg"
    id: "g-lin-sq"
    anchor: "#g-lin-sq"

tables:
  - id: "T-G-LIN-SUM"
    anchor: "#summary"
  - id: "T-G-LIN-CFG"
    anchor: "#configuration"

data:
  source: "/data/yaml/guarantees/g-lin.yaml"
  compiled: "/data/json/g-lin__compiled.json"

search_entry:
  id: "g-lin::main"
  tags: ["guarantee:linearizable", "consistency:strong"]
```

---

## Change Management

### Renaming Process

1. **Never delete old names** - Maintain redirects
2. **Version bump** - Major version for ID changes
3. **Update all references** - Use automated tooling
4. **Redirect chains** - Maximum 2 redirects
5. **Deprecation notice** - 6 month warning

### Redirect Rules

```nginx
# Old to new redirects
rewrite ^/guarantees/linear/$ /guarantees/linearizable/ permanent;
rewrite ^/patterns/command-query/$ /patterns/cqrs/ permanent;
rewrite ^/diagrams/(.*).jpg$ /diagrams/$1.svg permanent;
```

---

## Automation Requirements

### Naming Validation Script

```python
def validate_diagram_name(filename):
    pattern = r'^[a-z-]+__[A-Z]{2,3}__v\d+\.\d+\.\d+\.(mmd|svg|png)$'
    return re.match(pattern, filename) is not None

def validate_entity_id(entity_id):
    patterns = {
        'guarantee': r'^G-[A-Z]{3,4}$',
        'mechanism': r'^M-(P\d{1,2}|[A-Z-]+)$',
        'pattern': r'^P-[a-z-]+$'
    }
    # Check against all patterns
```

### Production Documentation Workflow

**Direct Approach:**
1. **Research**: Gather production data from blogs, papers, talks
2. **Document**: Write markdown with embedded Mermaid diagrams
3. **Validate**: Review with practitioners who've operated the systems
4. **Export**: Use MkDocs to generate static site

**Tools:**
- **MkDocs**: Static site generation
- **Mermaid**: Embedded diagrams in markdown
- **GitHub Actions**: Automated deployment
- **Material Theme**: Production-ready documentation theme

---

*Version: 2.0.0 | Document 06 of 16 | Last Updated: 2025-01-18*