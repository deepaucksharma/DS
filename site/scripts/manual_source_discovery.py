#!/usr/bin/env python3
"""
Manual Source Discovery Workflow
Adapted from readonly-spec/13-SOURCE-DISCOVERY-AUTOMATION.md
For manual execution with minimal automation overhead
"""

import yaml
import json
from datetime import datetime, timedelta
from typing import Dict, List
import re

# High-value sources curated from spec
HIGH_VALUE_SOURCES = {
    "cloudflare": {
        "url": "https://blog.cloudflare.com",
        "focus": ["workers", "durable-objects", "d1", "r2", "edge computing"],
        "scale_indicators": ["billion requests", "edge locations"]
    },
    "discord": {
        "url": "https://discord.com/blog",
        "focus": ["elixir", "rust", "cassandra", "voice processing", "real-time"],
        "scale_indicators": ["140 million users", "voice channels"]
    },
    "notion": {
        "url": "https://www.notion.so/blog/topic/eng",
        "focus": ["block-based architecture", "real-time collaboration"],
        "scale_indicators": ["30 million users", "real-time sync"]
    },
    "shopify": {
        "url": "https://shopify.engineering",
        "focus": ["flash sales", "global commerce", "platform scaling"],
        "scale_indicators": ["merchants", "Black Friday"]
    },
    "github": {
        "url": "https://github.blog/category/engineering/",
        "focus": ["copilot", "actions", "security", "git-at-scale"],
        "scale_indicators": ["100 million developers", "CI/CD"]
    },
    "anthropic": {
        "url": "https://www.anthropic.com/research",
        "focus": ["claude", "constitutional AI", "safety research"],
        "scale_indicators": ["large language models", "AI infrastructure"]
    },
    "netflix": {
        "url": "https://netflixtechblog.com",
        "focus": ["chaos engineering", "microservices", "CDN", "streaming"],
        "scale_indicators": ["230 million subscribers", "encoding"]
    },
    "stripe": {
        "url": "https://stripe.com/blog",
        "focus": ["payments", "financial infrastructure", "reliability"],
        "scale_indicators": ["payment processing", "millions of businesses"]
    },
    "uber": {
        "url": "https://www.uber.com/blog/engineering/",
        "focus": ["real-time matching", "geospatial systems", "marketplace"],
        "scale_indicators": ["25M trips/day", "global marketplace"]
    }
}

# Production-focused keywords for filtering
SCALE_PATTERNS = [
    r'\b\d+\s*million\b',
    r'\b\d+\s*billion\b',
    r'\b\d+[km]\s*rps\b',
    r'\bpetabyte\b',
    r'\bterabyte\b',
    r'\bat scale\b',
    r'\bglobal scale\b',
    r'\b99\.9+%\s*uptime\b'
]

ARCHITECTURE_KEYWORDS = [
    'architecture', 'infrastructure', 'distributed',
    'real-time', 'performance', 'scalability',
    'microservices', 'event-driven', 'consensus',
    'replication', 'partitioning', 'consistency'
]

class ManualSourceDiscovery:
    """Manual source discovery workflow for weekly execution"""

    def __init__(self):
        self.candidates = []
        self.review_date = datetime.now()

    def generate_weekly_checklist(self) -> str:
        """Generate weekly manual review checklist"""
        checklist = [
            "# Weekly Source Discovery Checklist",
            f"## Week of {self.review_date.strftime('%Y-%m-%d')}",
            "",
            "### High-Priority Sources to Check:",
            ""
        ]

        for source, config in HIGH_VALUE_SOURCES.items():
            checklist.append(f"#### {source.title()}")
            checklist.append(f"- [ ] Visit: {config['url']}")
            checklist.append(f"- [ ] Look for: {', '.join(config['focus'][:3])}")
            checklist.append(f"- [ ] Scale indicators: {', '.join(config['scale_indicators'][:2])}")
            checklist.append("")

        checklist.extend([
            "### Evaluation Criteria:",
            "- [ ] Scale: 10M+ users OR 100K+ RPS OR 1TB+ data",
            "- [ ] Architecture depth: System diagrams or detailed descriptions",
            "- [ ] Production focus: Real metrics, incidents, or lessons learned",
            "- [ ] Diagram potential: 10-15 diagrams possible from content",
            "",
            "### Found Candidates:",
            "```yaml",
            "candidates:",
            "  - title: ",
            "    url: ",
            "    source: ",
            "    scale_metrics: ",
            "    architecture_value: ",
            "    priority: high|medium|low",
            "```"
        ])

        return "\n".join(checklist)

    def evaluate_candidate(self, title: str, url: str, summary: str) -> Dict:
        """Evaluate a candidate for case study potential"""
        text = f"{title} {summary}".lower()

        # Check scale indicators
        has_scale = any(re.search(pattern, text) for pattern in SCALE_PATTERNS)

        # Check architecture relevance
        arch_score = sum(1 for keyword in ARCHITECTURE_KEYWORDS if keyword in text)
        has_architecture = arch_score >= 3

        # Determine priority
        if has_scale and has_architecture:
            priority = "high"
        elif has_scale or arch_score >= 2:
            priority = "medium"
        else:
            priority = "low"

        return {
            "title": title,
            "url": url,
            "has_scale": has_scale,
            "architecture_score": arch_score,
            "priority": priority,
            "evaluation_date": datetime.now().isoformat()
        }

    def create_case_study_template(self, org: str, title: str) -> str:
        """Create case study YAML template for approved candidates"""
        template = f"""# Case Study: {org.upper()} - {title}
# Generated: {datetime.now().strftime('%Y-%m-%d')}

id: CS-{org.upper()}
name: {org}
title: {title}
category: # e.g., streaming, payments, real-time
created: {datetime.now().isoformat()}
confidence: B  # A/B/C based on source quality

scale:
  users: # e.g., 238M subscribers
  throughput: # e.g., 25M trips/day
  data_volume: # e.g., 10PB stored
  availability: # e.g., 99.99%

sources:
  - url:
    type: blog|paper|talk
    date:
    confidence: A|B|C

architecture:
  patterns:
    - # e.g., CQRS
    - # e.g., Event Sourcing
  mechanisms:
    - # e.g., Consistent Hashing
    - # e.g., Gossip Protocol
  guarantees:
    - # e.g., Eventual Consistency
    - # e.g., At-least-once delivery

diagrams:
  planned:
    - type: system_overview
      title: "{org} Global Architecture"
      complexity: high
    - type: data_flow
      title: "{org} Data Pipeline"
      complexity: medium
    - type: failure_scenario
      title: "{org} Failure Recovery"
      complexity: high
    - type: scaling_approach
      title: "{org} Scaling Strategy"
      complexity: medium
  total_count: 12  # Target 10-15 per case study

implementation_notes: |
  # Key insights from source materials
  -
  -

production_metrics: |
  # Real metrics from production
  -
  -

status: draft  # draft|approved|in_progress|completed
priority: high  # high|medium|low based on value
"""
        return template

    def generate_progress_report(self, completed_studies: int, total_diagrams: int) -> str:
        """Generate progress report toward 900-1500 diagram goal"""
        target_min = 900
        target_max = 1500
        target_mid = 1200

        progress_pct = (total_diagrams / target_mid) * 100
        avg_per_study = total_diagrams / max(completed_studies, 1)

        report = f"""# Atlas Progress Report
## {datetime.now().strftime('%Y-%m-%d')}

### Current Status
- **Case Studies Completed**: {completed_studies}
- **Total Diagrams Created**: {total_diagrams}
- **Average per Case Study**: {avg_per_study:.1f}
- **Progress to Target**: {progress_pct:.1f}% (target: {target_min}-{target_max})

### Velocity
- **Weekly Target**: 20-30 diagrams (2-3 case studies)
- **Monthly Target**: 80-120 diagrams (6-8 case studies)
- **Quarterly Target**: 250-350 diagrams (20-25 case studies)

### Next Milestones
- [ ] 300 diagrams - Foundation Complete
- [ ] 600 diagrams - Core Patterns Done
- [ ] 900 diagrams - Minimum Target Achieved
- [ ] 1200 diagrams - Optimal Coverage
- [ ] 1500 diagrams - Stretch Goal

### Quality Metrics
- All diagrams follow 5-plane architecture
- All include SLO labels and metrics
- All validated against schema
- All under 500KB size limit
"""
        return report

def main():
    """Main execution for manual workflow"""
    discovery = ManualSourceDiscovery()

    # Generate weekly checklist
    checklist = discovery.generate_weekly_checklist()
    with open("weekly-checklist.md", "w") as f:
        f.write(checklist)
    print("✓ Generated weekly-checklist.md")

    # Example candidate evaluation
    example = discovery.evaluate_candidate(
        "How Discord Stores Billions of Messages",
        "https://discord.com/blog/how-discord-stores-billions-of-messages",
        "Deep dive into Discord's message storage architecture using Cassandra, ScyllaDB, and custom data services handling billions of messages daily"
    )
    print(f"✓ Example evaluation: {example['priority']} priority")

    # Generate case study template
    template = discovery.create_case_study_template("discord", "Message Storage at Scale")
    with open("case-study-template.yaml", "w") as f:
        f.write(template)
    print("✓ Generated case-study-template.yaml")

    # Generate progress report
    report = discovery.generate_progress_report(5, 60)
    with open("progress-report.md", "w") as f:
        f.write(report)
    print("✓ Generated progress-report.md")

if __name__ == "__main__":
    main()