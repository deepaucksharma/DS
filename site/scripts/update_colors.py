#!/usr/bin/env python3
"""
Update all Mermaid diagram colors to new Tailwind-inspired palette.
Replaces old harsh colors with more aesthetic, accessible colors.
"""

import os
import re
from pathlib import Path
from typing import Dict, Tuple

# Color mapping: old -> new (primary and stroke colors)
COLOR_MAPPINGS = {
    # Edge Plane (Blue)
    '#0066CC': '#3B82F6',  # Primary blue
    '#004499': '#2563EB',  # Stroke blue

    # Service Plane (Green -> Emerald)
    '#00AA00': '#10B981',  # Primary emerald
    '#007700': '#059669',  # Stroke emerald

    # State Plane (Orange -> Amber)
    '#FF8800': '#F59E0B',  # Primary amber
    '#CC6600': '#D97706',  # Stroke amber

    # Control Plane (Red -> Violet)
    '#CC0000': '#8B5CF6',  # Primary violet
    '#990000': '#7C3AED',  # Stroke violet

    # Stream Plane (deprecated - but update if found)
    '#AA00AA': '#8B5CF6',  # Convert to control/violet
    '#770077': '#7C3AED',  # Stroke violet
}

# Case-insensitive version for flexibility
COLOR_MAPPINGS_CI = {k.lower(): v for k, v in COLOR_MAPPINGS.items()}


def update_colors_in_file(filepath: Path) -> Tuple[int, bool]:
    """
    Update colors in a single file.
    Returns (number of replacements, whether file was modified)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return 0, False

    original_content = content
    replacements = 0

    # Replace colors (case-insensitive)
    for old_color, new_color in COLOR_MAPPINGS.items():
        # Count replacements before making them
        pattern = re.compile(re.escape(old_color), re.IGNORECASE)
        matches = pattern.findall(content)
        replacements += len(matches)

        # Perform replacement
        content = pattern.sub(new_color, content)

    # Check if file was modified
    if content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return replacements, True
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return replacements, False

    return 0, False


def main():
    """Main execution function"""
    print("=" * 60)
    print("🎨 Mermaid Diagram Color Update Script")
    print("=" * 60)
    print("\nUpdating to Tailwind-inspired color palette...")
    print("\nColor Mappings:")
    print("-" * 40)
    print("Plane        | Old Color | New Color")
    print("-" * 40)
    print(f"Edge        | #0066CC   | #3B82F6")
    print(f"Service     | #00AA00   | #10B981")
    print(f"State       | #FF8800   | #F59E0B")
    print(f"Control     | #CC0000   | #8B5CF6")
    print("-" * 40)

    # Find all markdown files
    docs_dir = Path('docs')
    if not docs_dir.exists():
        print(f"Error: docs directory not found. Run from site/ directory.")
        return

    md_files = list(docs_dir.glob('**/*.md'))
    print(f"\nFound {len(md_files)} markdown files to process")

    # Process files
    total_replacements = 0
    modified_files = []

    for i, filepath in enumerate(md_files, 1):
        # Show progress
        if i % 10 == 0:
            print(f"Processing file {i}/{len(md_files)}...", end='\r')

        replacements, modified = update_colors_in_file(filepath)

        if modified:
            modified_files.append((filepath, replacements))
            total_replacements += replacements

    # Print results
    print("\n" + "=" * 60)
    print("✅ Color Update Complete!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  - Files scanned: {len(md_files)}")
    print(f"  - Files modified: {len(modified_files)}")
    print(f"  - Total color replacements: {total_replacements}")

    if modified_files:
        print(f"\n📝 Top 10 Modified Files (by replacement count):")
        modified_files.sort(key=lambda x: x[1], reverse=True)
        for filepath, count in modified_files[:10]:
            rel_path = filepath.relative_to(docs_dir)
            print(f"  - {rel_path}: {count} replacements")

    print("\n💡 Next Steps:")
    print("  1. Run 'mkdocs serve' to test the changes")
    print("  2. Navigate to a few diagrams to verify colors")
    print("  3. Test dark mode switching")
    print("  4. Commit changes if everything looks good")

    # Create a summary file
    summary_path = Path('color_update_summary.txt')
    with open(summary_path, 'w') as f:
        f.write("Color Update Summary\n")
        f.write("=" * 40 + "\n")
        f.write(f"Total files modified: {len(modified_files)}\n")
        f.write(f"Total replacements: {total_replacements}\n\n")
        f.write("Modified files:\n")
        for filepath, count in modified_files:
            rel_path = filepath.relative_to(docs_dir)
            f.write(f"  {rel_path}: {count} replacements\n")

    print(f"\n📄 Detailed summary saved to: {summary_path}")


if __name__ == "__main__":
    main()