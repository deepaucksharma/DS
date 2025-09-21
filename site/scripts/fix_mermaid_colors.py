#!/usr/bin/env python3
"""
Fix Mermaid diagram syntax errors caused by color codes in subgraph labels.
Removes the color codes from subgraph labels to prevent syntax errors.
"""

import re
import glob
import os

def fix_mermaid_colors(file_path):
    """Fix color codes in Mermaid subgraph labels."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Pattern to match subgraph with color codes
    # Matches: subgraph Name[Label - #HEXCODE]
    pattern = r'subgraph\s+(\w+)\[(.*?)\s*-\s*#[A-Fa-f0-9]{6}\]'

    # Replace with just the label in quotes
    def replacement(match):
        identifier = match.group(1)
        label = match.group(2).strip()
        return f'subgraph {identifier}["{label}"]'

    content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    # Find all markdown files in docs directory
    base_path = '/home/deepak/DS/site/docs'
    patterns = [
        'scaling/*.md',
        'systems/**/*.md',
        'performance/*.md',
        'capacity/*.md',
        'costs/*.md',
        'migrations/*.md',
        'incidents/*.md',
        'debugging/*.md',
        'comparisons/*.md',
        'patterns/*.md'
    ]

    fixed_files = []

    for pattern in patterns:
        path_pattern = os.path.join(base_path, pattern)
        files = glob.glob(path_pattern)

        for file_path in files:
            if fix_mermaid_colors(file_path):
                fixed_files.append(file_path)
                print(f"Fixed: {file_path}")

    print(f"\nTotal files fixed: {len(fixed_files)}")

    if fixed_files:
        print("\nFixed files:")
        for f in sorted(fixed_files):
            print(f"  - {f}")

if __name__ == "__main__":
    main()