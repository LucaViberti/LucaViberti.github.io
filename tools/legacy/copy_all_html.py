#!/usr/bin/env python3
import shutil
import os
from pathlib import Path

# Percorsi
source_dir = Path("/workspaces/LucaViberti.github.io/html")
dest_dir = Path("/workspaces/LucaViberti.github.io/ja/html")

# Crea la directory di destinazione se non esiste
dest_dir.mkdir(parents=True, exist_ok=True)

# Copia tutti i file HTML
copied_count = 0
for html_file in source_dir.glob("*.html"):
    dest_file = dest_dir / html_file.name
    shutil.copy2(html_file, dest_file)
    print(f"Copiato: {html_file.name}")
    copied_count += 1

# Copia anche index.html dalla root a ja/index.html se non esiste già
root_index = Path("/workspaces/LucaViberti.github.io/index.html")
ja_index = Path("/workspaces/LucaViberti.github.io/ja/index.html")
if root_index.exists() and not ja_index.exists():
    shutil.copy2(root_index, ja_index)
    print(f"Copiato: index.html nella cartella ja/")

print(f"\nTotale file HTML copiati in ja/html/: {copied_count}")
