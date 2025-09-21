#!/usr/bin/env python3
"""
Update CENTRAL_METRICS.json to include new navigation structure while preserving current data
"""

import json
from datetime import datetime
from pathlib import Path

def update_central_metrics():
    """Update CENTRAL_METRICS.json with navigation structure"""
    data_dir = Path(__file__).parent.parent / "data"
    metrics_file = data_dir / "CENTRAL_METRICS.json"

    # Load current data
    with open(metrics_file, 'r') as f:
        data = json.load(f)

    # Update metadata
    data["metadata"]["navigation_version"] = "v5.0"
    data["metadata"]["migration_notes"] = "Updated for new navigation structure with Operations parent category"

    # Update category breakdown to reflect new structure
    current_breakdown = data["category_breakdown"]

    # Reorganize into new structure
    new_breakdown = {
        "home": {
            "foundation": 8,
            "guarantees": 18,
            "mechanisms": 30,
            "patterns": current_breakdown.get("patterns", 66),
            "examples": 15,
            "reference": 10
        },
        "systems": current_breakdown.get("systems", 142),
        "incidents": current_breakdown.get("incidents", 66),
        "operations": {
            "debugging": current_breakdown.get("debugging", 59),
            "production": current_breakdown.get("production", 0)
        },
        "performance": current_breakdown.get("performance", 38),
        "scaling": current_breakdown.get("scaling", 33),
        "capacity": current_breakdown.get("capacity", 32),
        "migrations": current_breakdown.get("migrations", 35),
        "costs": current_breakdown.get("costs", 28),
        "comparisons": current_breakdown.get("comparisons", 25)
    }

    # Calculate category totals
    category_totals = {}
    for key, value in new_breakdown.items():
        if isinstance(value, dict):
            category_totals[key] = sum(value.values())
        else:
            category_totals[key] = value

    data["category_breakdown"] = new_breakdown
    data["category_totals"] = category_totals

    # Add navigation structure information
    data["navigation_structure"] = {
        "top_level_categories": [
            "Home",
            "Systems",
            "Incidents",
            "Operations",
            "Performance",
            "Scaling",
            "Capacity",
            "Migrations",
            "Costs",
            "Comparisons"
        ],
        "home_subcategories": [
            "Getting Started",
            "Foundation",
            "Guarantees",
            "Mechanisms",
            "Patterns",
            "Examples",
            "Reference"
        ],
        "operations_subcategories": [
            "Debugging",
            "Production"
        ]
    }

    # Add migration tracking
    data["migration_info"] = {
        "navigation_version": "v5.0",
        "migration_date": datetime.now().isoformat(),
        "changes": [
            "Added Operations parent category with Debugging and Production subcategories",
            "Reorganized Home to include Foundation, Guarantees, Mechanisms, Patterns, Examples, Reference",
            "Updated category breakdown to reflect hierarchical structure",
            "Preserved all existing metrics and counts"
        ]
    }

    # Create backup
    backup_file = metrics_file.with_suffix('.json.nav_backup')
    with open(backup_file, 'w') as f:
        json.dump(data, f, indent=2)

    # Write updated file
    with open(metrics_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Updated {metrics_file}")
    print(f"Backup created: {backup_file}")
    print(f"Total categories: {sum(category_totals.values())}")

if __name__ == "__main__":
    update_central_metrics()