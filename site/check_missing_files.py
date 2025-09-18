#!/usr/bin/env python3
import os
import re

# Read the mkdocs.yml file
with open('mkdocs.yml', 'r') as f:
    content = f.read()

# Extract nav section
nav_match = re.search(r'^nav:(.*?)^[a-z]', content, re.MULTILINE | re.DOTALL)
if not nav_match:
    print("Could not find nav section")
    exit(1)

nav_content = nav_match.group(1)

# Find all .md file references
md_files = re.findall(r':\s*([a-z][a-z0-9/-]+\.md)', nav_content)

# Check which files are missing
missing_files = []
for md_file in md_files:
    full_path = os.path.join('docs', md_file)
    if not os.path.exists(full_path):
        missing_files.append(md_file)

# Print results
if missing_files:
    print(f"Found {len(missing_files)} missing files:\n")
    for f in missing_files:
        print(f"  - {f}")
else:
    print("All navigation files exist!")