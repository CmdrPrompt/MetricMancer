#!/usr/bin/env python3
"""
remove_multiple_blank_lines.py

Removes all multiple consecutive blank lines from a markdown file, leaving at most one blank line between sections.
Usage:
    python remove_multiple_blank_lines.py SoftwareSpecificationAndDesign.md
"""
import sys
import re

if len(sys.argv) != 2:
    print("Usage: python remove_multiple_blank_lines.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace 2+ consecutive blank lines with a single blank line
deduped = re.sub(r'\n{3,}', '\n\n', content)

with open(filename, 'w', encoding='utf-8') as f:
    f.write(deduped)

print(f"Removed multiple blank lines in {filename}")
