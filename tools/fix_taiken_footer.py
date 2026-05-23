#!/usr/bin/env python3
"""
Fix duplicate footer elements in converted taiken files.
"""

import re
from pathlib import Path

TAIKEN_FILES = [
    'taiken3.html', 'taiken4.html', 'taiken5.html', 'taiken6.html',
    'taiken7.html', 'taiken9.html', 'taiken10.html', 'taiken11.html',
    'taiken12.html', 'taiken13.html', 'taiken14.html', 'taiken15.html',
    'taiken16.html', 'taiken17.html', 'taiken20.html', 'taiken21.html',
    'taiken22.html', 'taiken23.html', 'taiken24.html'
]

def fix_footer(filepath):
    """Remove duplicate footer elements and clean up blocks."""

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern 1: Remove duplicate footer inside the blocks
    # <div>\n<footer>...</footer>\n</div> inside taiken-article__blocks
    pattern = r'<div>\s*<footer class="taiken-article__foot">.*?</footer>\s*</div>'
    content = re.sub(pattern, '', content, flags=re.DOTALL)

    # Pattern 2: Clean up extra spaces/newlines
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[OK] {Path(filepath).name} - Footer fixed")

def main():
    repo_root = Path(__file__).parent.parent

    for filename in TAIKEN_FILES:
        filepath = repo_root / filename
        if filepath.exists():
            fix_footer(filepath)
        else:
            print(f"[SKIP] {filename} - Not found")

if __name__ == '__main__':
    main()
