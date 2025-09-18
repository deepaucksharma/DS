#!/usr/bin/env python3
"""
Simple script to display current metrics from CENTRAL_METRICS.json
"""

import json
from pathlib import Path

def show_metrics():
    """Display current project metrics"""
    metrics_file = Path(__file__).parent.parent / "data" / "CENTRAL_METRICS.json"

    if not metrics_file.exists():
        print("❌ Central metrics file not found")
        print("   Run: python scripts/unified_status_tracker.py --update-central")
        return

    with open(metrics_file, 'r') as f:
        metrics = json.load(f)

    print("=" * 60)
    print("ATLAS PROJECT METRICS".center(60))
    print("=" * 60)
    print(f"Last Updated: {metrics['metadata']['last_updated']}")
    print()

    # Progress
    current = metrics['current_status']['diagrams_created']
    target = metrics['targets']['total_diagrams']
    progress = metrics['progress_percentages']['overall']

    print(f"📊 PROGRESS: {current}/{target} diagrams ({progress:.1f}%)")

    # Progress bar
    bar_width = 40
    filled = int(bar_width * progress / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"   [{bar}]")
    print()

    # Systems
    sys_docs = metrics['current_status']['systems_documented']
    print(f"🏢 SYSTEMS: {sys_docs['complete']} complete, {sys_docs['partial']} partial, {sys_docs['not_started']} not started")
    print()

    # Compliance
    compliance = metrics['current_status']['compliance']
    print(f"✅ COMPLIANCE: {compliance['average_score']:.1f}% average")
    print(f"   Fully compliant: {compliance['fully_compliant']}")
    print(f"   Needs updates: {compliance['needs_updates']}")
    print()

    # Timeline
    timeline = metrics['timeline']
    print(f"📅 TIMELINE:")
    print(f"   Current week: {timeline['current_week']}/36")
    print(f"   Velocity: {timeline['current_velocity']} diagrams/week")
    print(f"   Required: {timeline['required_velocity']:.1f} diagrams/week")
    print()

    print("=" * 60)
    print("Run 'python scripts/unified_status_tracker.py --dashboard' for details")

if __name__ == "__main__":
    show_metrics()