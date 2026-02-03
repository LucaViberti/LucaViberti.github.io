#!/usr/bin/env python3
"""Fix all paths in HTML files inside html/ folder."""

import os
import re
from pathlib import Path

def fix_html_file(file_path):
    """Fix paths in a single HTML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix nav-loader.js path (relative to absolute)
    content = re.sub(
        r'<script\s+src=["\'](?!/)nav-loader\.js["\']',
        '<script src="/nav-loader.js"',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix footer.html path (relative to absolute)
    content = re.sub(
        r'fetch\(["\'](?!/)footer\.html["\']',
        'fetch("/html/footer.html"',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix nav.html path (relative to absolute) - if any page loads it directly
    content = re.sub(
        r'fetch\(["\'](?!/)nav\.html["\']',
        'fetch("/html/nav.html"',
        content,
        flags=re.IGNORECASE
    )
    
    # Only write if changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    html_dir = Path('/workspaces/LucaViberti.github.io/html')
    
    if not html_dir.exists():
        print(f"Directory {html_dir} does not exist!")
        return
    
    fixed_count = 0
    for html_file in html_dir.glob('*.html'):
        # Skip nav.html and footer.html as they are includes, not pages
        if html_file.name in ['nav.html', 'footer.html']:
            continue
            
        if fix_html_file(html_file):
            print(f"Fixed: {html_file.name}")
            fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
