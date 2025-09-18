#!/usr/bin/env python3
"""
Simple Mermaid diagram validator for markdown files.
Checks syntax and basic structure without complex processing.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

def extract_mermaid_blocks(content: str) -> List[Tuple[int, str]]:
    """Extract all mermaid code blocks from markdown content."""
    pattern = r'```mermaid\n(.*?)\n```'
    blocks = []

    for match in re.finditer(pattern, content, re.DOTALL):
        line_num = content[:match.start()].count('\n') + 1
        blocks.append((line_num, match.group(1)))

    return blocks

def validate_mermaid_syntax(diagram: str) -> List[str]:
    """Basic validation of Mermaid diagram syntax."""
    errors = []

    # Check for diagram type declaration
    diagram_types = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
                     'stateDiagram', 'erDiagram', 'journey', 'gantt', 'pie', 'timeline']

    # Skip init lines when checking for diagram type
    lines = diagram.strip().split('\n')
    non_init_lines = [line for line in lines if not line.startswith('%%')]
    first_line = non_init_lines[0] if non_init_lines else ''
    has_valid_type = any(dtype in first_line for dtype in diagram_types)

    if not has_valid_type:
        errors.append("Missing or invalid diagram type declaration")

    # Check for basic syntax issues
    if diagram.count('[') != diagram.count(']'):
        errors.append("Mismatched square brackets")

    if diagram.count('{') != diagram.count('}'):
        errors.append("Mismatched curly braces")

    if diagram.count('(') != diagram.count(')'):
        errors.append("Mismatched parentheses")

    # Check for unclosed strings
    if diagram.count('"') % 2 != 0:
        errors.append("Unclosed quotes")

    # Check for new Tailwind colors
    new_colors = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6']
    old_colors = ['#0066CC', '#00AA00', '#FF8800', '#CC0000']

    # Warning for old colors (not error)
    for old_color in old_colors:
        if old_color in diagram:
            errors.append(f"Warning: Using old color {old_color}, consider updating to new Tailwind palette")

    # Check for interactive features (warnings, not errors)
    if 'classDef' in diagram and not any(color in diagram for color in new_colors):
        errors.append("Warning: classDef found but not using new Tailwind colors")

    # Check for 4-plane architecture
    if 'graph' in first_line or 'flowchart' in first_line:
        planes = ['Edge', 'Service', 'State', 'Control']
        has_planes = sum(1 for plane in planes if plane in diagram)
        if has_planes > 0 and has_planes < 4:
            errors.append(f"Warning: Only {has_planes} of 4 planes detected, consider adding all planes")

    return errors

def validate_file(file_path: Path) -> Tuple[int, List[str]]:
    """Validate all Mermaid diagrams in a markdown file."""
    content = file_path.read_text()
    blocks = extract_mermaid_blocks(content)

    all_errors = []
    for line_num, diagram in blocks:
        errors = validate_mermaid_syntax(diagram)
        if errors:
            for error in errors:
                all_errors.append(f"Line {line_num}: {error}")

    return len(blocks), all_errors

def main():
    """Main validation function."""
    docs_dir = Path('docs')
    if not docs_dir.exists():
        print("❌ No docs directory found")
        return 1

    total_files = 0
    total_diagrams = 0
    files_with_errors = []

    print("🔍 Validating Mermaid diagrams...\n")

    for md_file in sorted(docs_dir.rglob('*.md')):
        rel_path = md_file.relative_to(docs_dir)
        diagram_count, errors = validate_file(md_file)

        if diagram_count > 0:
            total_files += 1
            total_diagrams += diagram_count

            if errors:
                print(f"❌ {rel_path} ({diagram_count} diagrams)")
                for error in errors:
                    print(f"   {error}")
                files_with_errors.append(str(rel_path))
            else:
                print(f"✅ {rel_path} ({diagram_count} diagrams)")

    # Summary
    print("\n" + "="*50)
    print("📊 Validation Summary:")
    print(f"   Files scanned: {total_files}")
    print(f"   Total diagrams: {total_diagrams}")

    if files_with_errors:
        print(f"   Files with errors: {len(files_with_errors)}")
        return 1
    else:
        print("   ✅ All diagrams valid!")
        return 0

if __name__ == "__main__":
    sys.exit(main())