#!/usr/bin/env python3
"""
Script to restructure a static website repository for GitHub Pages.

This script creates two directories, `html` and `images`, then moves
all `.html` files into `html/` and image files (`.jpeg`, `.jpg`,
`.png`, `.gif`, etc.) into `images/`. It also updates HTML files so
that they still work after being moved:

  * The script tag that loads `nav-loader.js` is rewritten to use an
    absolute path (`/nav-loader.js`). This ensures that pages in
    `html/` can still load the script from the repository root.

  * All image references that were previously relative (e.g.
    `<img src="league-symbol.jpeg">`) are rewritten to reference the
    `images` folder (e.g. `<img src="/images/league-symbol.jpeg">`).
    The same transformation is applied to any JavaScript objects or
    dictionaries that map names to image filenames.

To use this script:

1. Place it at the root of your cloned repository.
2. Run it with Python 3: `python restructure_site.py`.
3. Commit and push the changes back to GitHub.

Note: The script is idempotent – running it multiple times should not
cause additional changes once the structure has been reorganized.
"""

import os
import re
import shutil
from pathlib import Path


def process_html(content: str) -> str:
    """Apply fixes to an HTML file's content.

    - Rewrites the nav-loader script tag to an absolute path.
    - Prefixes image sources with `/images/` when they are local.
    - Updates JavaScript dictionaries that map to image files.

    Args:
        content: The original HTML content.
    Returns:
        Modified HTML content.
    """
    # Ensure the nav-loader script tag uses an absolute path
    content = re.sub(
        r'<script\s+src=("|\')nav-loader\.js(\1)',
        r'<script src="/nav-loader.js"',
        content,
        flags=re.IGNORECASE,
    )

    # Update image sources in HTML tags (img, source, etc.)
    def replace_src(match: re.Match) -> str:
        filename = match.group(1)
        return f'src="/images/{filename}"'

    content = re.sub(
        r'src=("|\')(?!/|https?:|data:)([^\'" ]+\.(?:png|jpg|jpeg|gif))(\1)',
        lambda m: f'src="/images/{m.group(2)}"',
        content,
        flags=re.IGNORECASE,
    )

    # Update dictionary/object values that refer to image files
    def replace_dict_val(match: re.Match) -> str:
        filename = match.group(1)
        quote = match.group(0)[0]  # preserve original quote style
        return f'{quote}/images/{filename}{quote}'

    # Patterns like 'League':'league-symbol.jpeg'
    content = re.sub(
        r':\s*("|\')([^/"\']+\.(?:png|jpg|jpeg|gif))(\1)',
        lambda m: f': {m.group(1)}/images/{m.group(2)}{m.group(1)}',
        content,
        flags=re.IGNORECASE,
    )

    return content


def main() -> None:
    repo_root = Path(os.getcwd())
    html_dir = repo_root / "html"
    images_dir = repo_root / "images"

    # Create output directories if they don't exist
    html_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)

    # Collect a list of files to process; avoid descending into target dirs
    for root, dirs, files in os.walk(repo_root):
        # Skip the output directories themselves
        rel_root = Path(root).relative_to(repo_root)
        if rel_root == Path("html") or rel_root == Path("images"):
            # Do not recurse into html or images once created
            dirs[:] = []
            continue

        for filename in files:
            # Skip the script itself
            if filename == Path(__file__).name:
                continue

            file_path = Path(root) / filename
            ext = file_path.suffix.lower()

            # Skip if file already relocated
            if file_path.is_symlink():
                continue

            if ext == ".html":
                # Read, process, and write to html directory
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                processed = process_html(content)
                dest_path = html_dir / filename
                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write(processed)
                # Remove original file to avoid duplicates (optional)
                file_path.unlink()
            elif ext in {".jpeg", ".jpg", ".png", ".gif"}:
                # Move image to images directory if not already there
                dest_path = images_dir / filename
                # If destination exists, remove original; otherwise move
                if dest_path.exists():
                    file_path.unlink()
                else:
                    shutil.move(str(file_path), str(dest_path))
            else:
                # Leave other file types untouched in the root
                pass

    print("Restructuring complete. HTML files and images have been relocated.")


if __name__ == "__main__":
    main()
