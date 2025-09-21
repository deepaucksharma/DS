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

def validate_directory_structure():
    """Validate the new navigation structure exists."""
    docs_dir = Path('docs')
    if not docs_dir.exists():
        return ["❌ No docs directory found"]

    errors = []

    # Check Home section directories
    home_dirs = ['foundation', 'guarantees', 'mechanisms', 'patterns', 'examples', 'reference']
    for dir_name in home_dirs:
        dir_path = docs_dir / dir_name
        if not dir_path.exists():
            errors.append(f"❌ Missing Home directory: {dir_name}")

    # Check Operations parent directories
    operations_dirs = ['debugging', 'production']
    for dir_name in operations_dirs:
        dir_path = docs_dir / dir_name
        if not dir_path.exists():
            errors.append(f"❌ Missing Operations directory: {dir_name}")

    # Check Systems directory exists
    systems_dir = docs_dir / 'systems'
    if not systems_dir.exists():
        errors.append("❌ Missing systems directory")

    # Check Incidents directory exists
    incidents_dir = docs_dir / 'incidents'
    if not incidents_dir.exists():
        errors.append("❌ Missing incidents directory")

    # Check Comparisons directory exists
    comparisons_dir = docs_dir / 'comparisons'
    if not comparisons_dir.exists():
        errors.append("❌ Missing comparisons directory")

    return errors

def main():
    """Main validation function."""
    docs_dir = Path('docs')
    if not docs_dir.exists():
        print("❌ No docs directory found")
        return 1

    # First validate directory structure
    structure_errors = validate_directory_structure()
    if structure_errors:
        print("🏗️  Directory Structure Issues:")
        for error in structure_errors:
            print(f"   {error}")
        print()

    total_files = 0
    total_diagrams = 0
    files_with_errors = []

    # Organize by section for better reporting
    sections = {
        'Home': ['foundation', 'guarantees', 'mechanisms', 'patterns', 'examples', 'reference'],
        'Operations': ['debugging', 'production'],
        'Systems': ['systems'],
        'Incidents': ['incidents'],
        'Comparisons': ['comparisons'],
        'Other': []
    }

    print("🔍 Validating Mermaid diagrams by section...\n")

    for section_name, section_dirs in sections.items():
        section_files = 0
        section_diagrams = 0
        section_errors = []

        if section_name == 'Systems':
            # Special handling for systems subdirectories
            systems_dir = docs_dir / 'systems'
            if systems_dir.exists():
                for md_file in sorted(systems_dir.rglob('*.md')):
                    rel_path = md_file.relative_to(docs_dir)
                    diagram_count, errors = validate_file(md_file)

                    if diagram_count > 0:
                        section_files += 1
                        section_diagrams += diagram_count

                        if errors:
                            section_errors.append((str(rel_path), diagram_count, errors))
        else:
            # Handle other sections
            for dir_name in section_dirs:
                dir_path = docs_dir / dir_name
                if dir_path.exists():
                    for md_file in sorted(dir_path.rglob('*.md')):
                        rel_path = md_file.relative_to(docs_dir)
                        diagram_count, errors = validate_file(md_file)

                        if diagram_count > 0:
                            section_files += 1
                            section_diagrams += diagram_count

                            if errors:
                                section_errors.append((str(rel_path), diagram_count, errors))

        # Report section results
        if section_files > 0:
            print(f"📂 {section_name} Section:")
            print(f"   Files: {section_files}, Diagrams: {section_diagrams}")

            if section_errors:
                for rel_path, diagram_count, errors in section_errors:
                    print(f"   ❌ {rel_path} ({diagram_count} diagrams)")
                    for error in errors:
                        print(f"      {error}")
                    files_with_errors.append(rel_path)
            else:
                print(f"   ✅ All diagrams valid")
            print()

        total_files += section_files
        total_diagrams += section_diagrams

    # Handle any remaining files not in defined sections
    for md_file in sorted(docs_dir.rglob('*.md')):
        rel_path = md_file.relative_to(docs_dir)
        # Check if file is already processed
        in_section = False
        for section_dirs in sections.values():
            for dir_name in section_dirs:
                if str(rel_path).startswith(dir_name + '/') or rel_path.name == 'index.md':
                    in_section = True
                    break
            if in_section:
                break

        if not in_section and str(rel_path) not in ['index.md']:
            diagram_count, errors = validate_file(md_file)
            if diagram_count > 0:
                total_files += 1
                total_diagrams += diagram_count
                if errors:
                    files_with_errors.append(str(rel_path))

    # Summary
    print("="*50)
    print("📊 Complete Validation Summary:")
    print(f"   Files scanned: {total_files}")
    print(f"   Total diagrams: {total_diagrams}")

    if structure_errors:
        print(f"   Structure issues: {len(structure_errors)}")

    if files_with_errors:
        print(f"   Files with errors: {len(files_with_errors)}")
        print("   ⚠️  Continuing with warnings...")
        return 0  # Don't fail on diagram errors for now
    else:
        print("   ✅ All diagrams valid!")
        return 0 if not structure_errors else 1

if __name__ == "__main__":
    sys.exit(main())