#!/usr/bin/env python3
import shutil
import os
from pathlib import Path

source_dir = Path('/workspaces/LucaViberti.github.io/html')
dest_dir = Path('/workspaces/LucaViberti.github.io/ja/html')

# Copy all files from html/ to ja/html/
files_copied = 0
for file_path in source_dir.iterdir():
    if file_path.is_file():
        dest_file = dest_dir / file_path.name
        shutil.copy2(file_path, dest_file)
        files_copied += 1
        print(f"Copiato: {file_path.name}")

# Copy index.html
index_source = Path('/workspaces/LucaViberti.github.io/index.html')
index_dest = Path('/workspaces/LucaViberti.github.io/ja/index.html')
shutil.copy2(index_source, index_dest)
print(f"\nCopiato: index.html -> ja/index.html")

print(f"\n✓ Totale file copiati in ja/html/: {files_copied}")
