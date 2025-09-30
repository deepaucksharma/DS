#!/usr/bin/env python3
"""
Analyze mismatches between mkdocs.yml navigation and actual files
"""
import os
import yaml
from pathlib import Path

def extract_nav_files(nav_item, prefix=""):
    """Recursively extract all .md file paths from navigation"""
    files = []

    if isinstance(nav_item, dict):
        for key, value in nav_item.items():
            if isinstance(value, str) and value.endswith('.md'):
                files.append(value)
            elif isinstance(value, list):
                files.extend(extract_nav_files(value, prefix))
            elif isinstance(value, dict):
                files.extend(extract_nav_files(value, prefix))
    elif isinstance(nav_item, list):
        for item in nav_item:
            files.extend(extract_nav_files(item, prefix))
    elif isinstance(nav_item, str) and nav_item.endswith('.md'):
        files.append(nav_item)

    return files

def get_all_md_files(docs_dir):
    """Get all .md files in docs directory"""
    md_files = []
    docs_path = Path(docs_dir)

    for md_file in docs_path.rglob("*.md"):
        # Get relative path from docs directory
        rel_path = md_file.relative_to(docs_path)
        md_files.append(str(rel_path))

    return sorted(md_files)

def main():
    site_dir = Path("/home/deepak/DS/site")
    mkdocs_yml = site_dir / "mkdocs.yml"
    docs_dir = site_dir / "docs"

    # Load mkdocs.yml - use unsafe loader to handle Python tags
    with open(mkdocs_yml, 'r') as f:
        config = yaml.unsafe_load(f)

    # Extract all files from navigation
    nav_files = sorted(set(extract_nav_files(config.get('nav', []))))

    # Get all actual markdown files
    actual_files = get_all_md_files(docs_dir)

    # Find mismatches
    nav_set = set(nav_files)
    actual_set = set(actual_files)

    missing_from_nav = actual_set - nav_set
    missing_files = nav_set - actual_set

    print("="*80)
    print("NAVIGATION vs FILES MISMATCH ANALYSIS")
    print("="*80)
    print()

    print(f"Total files in navigation: {len(nav_files)}")
    print(f"Total actual .md files: {len(actual_files)}")
    print()

    if missing_files:
        print("="*80)
        print(f"FILES MISSING (referenced in nav but don't exist): {len(missing_files)}")
        print("="*80)
        for file in sorted(missing_files):
            full_path = docs_dir / file
            print(f"  ❌ {file}")
        print()
    else:
        print("✅ No missing files (all navigation entries point to existing files)")
        print()

    if missing_from_nav:
        print("="*80)
        print(f"FILES NOT IN NAVIGATION (exist but not referenced): {len(missing_from_nav)}")
        print("="*80)
        for file in sorted(missing_from_nav):
            full_path = docs_dir / file
            print(f"  📄 {file}")
        print()
    else:
        print("✅ No orphaned files (all files are referenced in navigation)")
        print()

    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Navigation entries pointing to missing files: {len(missing_files)}")
    print(f"Files not referenced in navigation: {len(missing_from_nav)}")
    print()

    if not missing_files and not missing_from_nav:
        print("✅ Perfect match! Navigation and files are in sync.")
    else:
        print("⚠️  Mismatches found. Please review the lists above.")

if __name__ == "__main__":
    main()