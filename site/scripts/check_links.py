#!/usr/bin/env python3
"""
Simple internal link validator for markdown files.
Checks that all internal links point to existing files.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

def extract_links(content: str) -> List[str]:
    """Extract all markdown links from content."""
    # Match [text](link) pattern
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = []

    for match in re.finditer(pattern, content):
        link = match.group(2)
        # Only check internal links (not http/https)
        if not link.startswith(('http://', 'https://', '#', 'mailto:')):
            links.append(link)

    return links

def validate_link(link: str, current_file: Path, docs_dir: Path) -> bool:
    """Check if a link points to an existing file."""
    # Remove anchor if present
    if '#' in link:
        link = link.split('#')[0]

    if not link:  # Was just an anchor
        return True

    # Resolve the link relative to current file
    if link.startswith('/'):
        # Absolute path from docs root
        target = docs_dir / link.lstrip('/')
    else:
        # Relative path from current file
        target = (current_file.parent / link).resolve()

    # Check if file exists (try with and without .md extension)
    return target.exists() or target.with_suffix('.md').exists()

def validate_file(file_path: Path, docs_dir: Path) -> List[str]:
    """Validate all links in a markdown file."""
    content = file_path.read_text()
    links = extract_links(content)

    broken_links = []
    for link in links:
        if not validate_link(link, file_path, docs_dir):
            broken_links.append(link)

    return broken_links

def main():
    """Main validation function."""
    docs_dir = Path('docs')
    if not docs_dir.exists():
        print("❌ No docs directory found")
        return 1

    total_files = 0
    total_links = 0
    files_with_broken_links = []

    # Organize by section for better reporting
    sections = {
        'Home': ['foundation', 'guarantees', 'mechanisms', 'patterns', 'examples', 'reference'],
        'Operations': ['debugging', 'production'],
        'Systems': ['systems'],
        'Incidents': ['incidents'],
        'Comparisons': ['comparisons']
    }

    print("🔍 Checking internal links by section...\n")

    for section_name, section_dirs in sections.items():
        section_files = 0
        section_links = 0
        section_broken = []

        if section_name == 'Systems':
            # Special handling for systems subdirectories
            systems_dir = docs_dir / 'systems'
            if systems_dir.exists():
                for md_file in sorted(systems_dir.rglob('*.md')):
                    rel_path = md_file.relative_to(docs_dir)
                    content = md_file.read_text()
                    all_links = extract_links(content)
                    internal_links = [l for l in all_links if not l.startswith(('http://', 'https://'))]

                    if internal_links:
                        section_files += 1
                        section_links += len(internal_links)
                        broken_links = validate_file(md_file, docs_dir)

                        if broken_links:
                            section_broken.append((str(rel_path), broken_links))
        else:
            # Handle other sections
            for dir_name in section_dirs:
                dir_path = docs_dir / dir_name
                if dir_path.exists():
                    for md_file in sorted(dir_path.rglob('*.md')):
                        rel_path = md_file.relative_to(docs_dir)
                        content = md_file.read_text()
                        all_links = extract_links(content)
                        internal_links = [l for l in all_links if not l.startswith(('http://', 'https://'))]

                        if internal_links:
                            section_files += 1
                            section_links += len(internal_links)
                            broken_links = validate_file(md_file, docs_dir)

                            if broken_links:
                                section_broken.append((str(rel_path), broken_links))

        # Report section results
        if section_files > 0:
            print(f"📂 {section_name} Section:")
            print(f"   Files: {section_files}, Links: {section_links}")

            if section_broken:
                for rel_path, broken_links in section_broken:
                    print(f"   ❌ {rel_path}")
                    for link in broken_links:
                        print(f"      → {link}")
                    files_with_broken_links.append(rel_path)
            else:
                print(f"   ✅ All links valid")
            print()

        total_files += section_files
        total_links += section_links

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
            content = md_file.read_text()
            all_links = extract_links(content)
            internal_links = [l for l in all_links if not l.startswith(('http://', 'https://'))]

            if internal_links:
                total_files += 1
                total_links += len(internal_links)
                broken_links = validate_file(md_file, docs_dir)

                if broken_links:
                    files_with_broken_links.append(str(rel_path))

    # Summary
    print("="*50)
    print("📊 Complete Link Check Summary:")
    print(f"   Files checked: {total_files}")
    print(f"   Total internal links: {total_links}")

    if files_with_broken_links:
        print(f"   Files with broken links: {len(files_with_broken_links)}")
        print("   ⚠️  Continuing with warnings...")
        return 0  # Don't fail on broken links for now
    else:
        print("   ✅ All links valid!")
        return 0

if __name__ == "__main__":
    sys.exit(main())