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

    print("🔍 Checking internal links...\n")

    for md_file in sorted(docs_dir.rglob('*.md')):
        rel_path = md_file.relative_to(docs_dir)
        content = md_file.read_text()
        all_links = extract_links(content)
        internal_links = [l for l in all_links if not l.startswith(('http://', 'https://'))]

        if internal_links:
            total_files += 1
            total_links += len(internal_links)
            broken_links = validate_file(md_file, docs_dir)

            if broken_links:
                print(f"❌ {rel_path}")
                for link in broken_links:
                    print(f"   → {link}")
                files_with_broken_links.append(str(rel_path))
            else:
                print(f"✅ {rel_path} ({len(internal_links)} links)")

    # Summary
    print("\n" + "="*50)
    print("📊 Link Check Summary:")
    print(f"   Files checked: {total_files}")
    print(f"   Total internal links: {total_links}")

    if files_with_broken_links:
        print(f"   Files with broken links: {len(files_with_broken_links)}")
        return 1
    else:
        print("   ✅ All links valid!")
        return 0

if __name__ == "__main__":
    sys.exit(main())