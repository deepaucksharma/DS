#!/usr/bin/env python3
"""
Migration script for updating JSON data files to reflect new navigation structure v5.0
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def load_migration_mapping(data_dir):
    """Load the path migration mapping"""
    mapping_file = data_dir / "path_migration_mapping.json"
    if not mapping_file.exists():
        raise FileNotFoundError(f"Migration mapping not found: {mapping_file}")

    with open(mapping_file, 'r') as f:
        return json.load(f)

def migrate_category(old_category, mapping):
    """Migrate old category to new category structure"""
    category_map = mapping["category_mapping"]["old_to_new"]
    return category_map.get(old_category, old_category)

def migrate_file_path(file_path, mapping):
    """Migrate file path if needed based on transformations"""
    if not file_path:
        return file_path

    transformations = mapping["path_transformations"]

    for old_prefix, new_prefix in transformations.items():
        if file_path.startswith(old_prefix):
            return file_path.replace(old_prefix, new_prefix, 1)

    return file_path

def update_unified_diagram_status(data_dir, mapping):
    """Update the unified_diagram_status.json file"""
    status_file = data_dir / "unified_diagram_status.json"

    if not status_file.exists():
        print(f"Warning: {status_file} not found")
        return

    print(f"Loading {status_file}...")
    with open(status_file, 'r') as f:
        data = json.load(f)

    # Update metadata
    data["metadata"]["last_updated"] = datetime.now().isoformat()
    data["metadata"]["navigation_version"] = "v5.0"
    data["metadata"]["migration_applied"] = True

    # Track migration statistics
    migration_stats = {
        "total_entries": len(data["diagrams"]),
        "categories_migrated": 0,
        "paths_migrated": 0,
        "unchanged": 0
    }

    # Migrate each diagram entry
    for diagram_key, diagram_info in data["diagrams"].items():
        old_category = diagram_info.get("category", "unknown")
        old_path = diagram_info.get("file_path", "")

        # Migrate category
        new_category = migrate_category(old_category, mapping)
        if new_category != old_category:
            diagram_info["category"] = new_category
            diagram_info["legacy_category"] = old_category
            migration_stats["categories_migrated"] += 1

        # Migrate file path
        new_path = migrate_file_path(old_path, mapping)
        if new_path != old_path:
            diagram_info["file_path"] = new_path
            diagram_info["legacy_file_path"] = old_path
            migration_stats["paths_migrated"] += 1

        if new_category == old_category and new_path == old_path:
            migration_stats["unchanged"] += 1

    # Add migration metadata
    data["migration_info"] = {
        "migration_date": datetime.now().isoformat(),
        "navigation_version": "v5.0",
        "statistics": migration_stats,
        "mapping_version": mapping["metadata"]["version"]
    }

    # Create backup
    backup_file = status_file.with_suffix('.json.backup')
    print(f"Creating backup: {backup_file}")
    with open(backup_file, 'w') as f:
        json.dump(data, f, indent=2)

    # Write updated file
    print(f"Writing updated {status_file}...")
    with open(status_file, 'w') as f:
        json.dump(data, f, indent=2)

    print("Migration Statistics:")
    for key, value in migration_stats.items():
        print(f"  {key}: {value}")

    return migration_stats

def validate_migration(data_dir, mapping):
    """Validate the migration results"""
    status_file = data_dir / "unified_diagram_status.json"

    with open(status_file, 'r') as f:
        data = json.load(f)

    validation_results = {
        "valid_categories": 0,
        "invalid_categories": 0,
        "valid_paths": 0,
        "issues": []
    }

    allowed_categories = mapping["validation_rules"]["category_validation"]["allowed_top_level"]
    allowed_with_subcats = []

    # Build full list of allowed categories including subcategories
    for top_level in allowed_categories:
        allowed_with_subcats.append(top_level)
        if top_level in mapping["validation_rules"]["category_validation"]["required_subcategories"]:
            subcats = mapping["validation_rules"]["category_validation"]["required_subcategories"][top_level]
            for subcat in subcats:
                allowed_with_subcats.append(f"{top_level}/{subcat}")

    for diagram_key, diagram_info in data["diagrams"].items():
        category = diagram_info.get("category", "")

        # Validate category
        if category in allowed_with_subcats:
            validation_results["valid_categories"] += 1
        else:
            validation_results["invalid_categories"] += 1
            validation_results["issues"].append(f"Invalid category '{category}' in {diagram_key}")

    print("Validation Results:")
    print(f"  Valid categories: {validation_results['valid_categories']}")
    print(f"  Invalid categories: {validation_results['invalid_categories']}")

    if validation_results["issues"]:
        print("Issues found:")
        for issue in validation_results["issues"][:10]:  # Show first 10 issues
            print(f"  - {issue}")
        if len(validation_results["issues"]) > 10:
            print(f"  ... and {len(validation_results['issues']) - 10} more")

    return validation_results

def main():
    """Main migration function"""
    # Get script directory and data directory
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        sys.exit(1)

    try:
        # Load migration mapping
        print("Loading migration mapping...")
        mapping = load_migration_mapping(data_dir)

        # Perform migration
        print("Starting migration...")
        migration_stats = update_unified_diagram_status(data_dir, mapping)

        # Validate results
        print("Validating migration...")
        validation_results = validate_migration(data_dir, mapping)

        print("Migration completed successfully!")

        return 0

    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()