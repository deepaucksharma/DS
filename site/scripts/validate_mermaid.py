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
                     'stateDiagram', 'erDiagram', 'journey', 'gantt', 'pie']

    first_line = diagram.strip().split('\n')[0] if diagram.strip() else ''
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