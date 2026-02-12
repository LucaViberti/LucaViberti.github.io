#!/usr/bin/env python3
"""
Script per copiare tutti i file da html/ a ja/html/
Esegue la copia usando shutil e conta i file
"""
import os
import shutil
from pathlib import Path

def copy_all_files():
    source_dir = Path("html")
    dest_dir = Path("ja/html")
    
    # Assicura che la directory di destinazione esista
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    files_copied = 0
    errors = []
    
    # Copia tutti i file da html/ a ja/html/
    for item in source_dir.iterdir():
        if item.is_file():
            try:
                dest_file = dest_dir / item.name
                shutil.copy2(item, dest_file)
                print(f"✓ Copiato: {item.name}")
                files_copied += 1
            except Exception as e:
                errors.append(f"✗ Errore copiando {item.name}: {e}")
                print(errors[-1])
    
    # Copia index.html
    try:
        shutil.copy2("index.html", "ja/index.html")
        print(f"\n✓ Copiato: index.html -> ja/index.html")
    except Exception as e:
        errors.append(f"✗ Errore copiando index.html: {e}")
        print(errors[-1])
    
    print(f"\n{'='*50}")
    print(f"✓ Totale file copiati in ja/html/: {files_copied}")
    if errors:
        print(f"✗ Errori: {len(errors)}")
    return files_copied

if __name__ == "__main__":
    os.chdir("/workspaces/LucaViberti.github.io")
    count = copy_all_files()
    print(f"\n✓ Operazione completata! {count} file copiati.")
