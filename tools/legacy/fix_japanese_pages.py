#!/usr/bin/env python3
"""
Script per correggere i file HTML giapponesi con:
1. Cambio di lang da "en" a "ja"
2. Aggiunta del link hreflang per 'ja'
3. Correzione del percorso nel canonical se necessario
"""

import os
import re
from pathlib import Path

def fix_html_lang(content: str) -> str:
    """Cambia lang="en" a lang="ja" nel tag <html>"""
    content = re.sub(r'<html\s+lang="en">', '<html lang="ja">', content, flags=re.IGNORECASE)
    return content

def add_ja_hreflang(content: str, filename: str) -> str:
    """Aggiunge il link hreflang per 'ja' se non presente"""
    
    # Estrai il percorso della pagina
    if filename == 'index.html':
        page_path = '/html/index.html'
    else:
        page_path = f'/html/{filename}'
    
    ja_href = f'https://www.guidetopheroes.com/ja{page_path}'
    
    # Controlla se hreflang="ja" esiste già
    if 'hreflang="ja"' in content or "hreflang='ja'" in content:
        return content
    
    # Trova dove inserire il link (dopo gli altri hreflang)
    # Cerca il pattern dei link hreflang
    hreflang_pattern = r'<link\s+rel="alternate"\s+hreflang="zh"\s+href="[^"]+"\s*/?\s*>'
    match = re.search(hreflang_pattern, content, re.IGNORECASE)
    
    if match:
        # Inserisci il link ja dopo il link zh
        insert_pos = match.end()
        ja_link = f'\n  <link rel="alternate" hreflang="ja" href="{ja_href}" />'
        content = content[:insert_pos] + ja_link + content[insert_pos:]
    else:
        # Fallback: cerca il tag x-default e inserisci prima di quello
        xdefault_pattern = r'<link\s+rel="alternate"\s+hreflang="x-default"'
        match = re.search(xdefault_pattern, content, re.IGNORECASE)
        if match:
            insert_pos = match.start()
            ja_link = f'  <link rel="alternate" hreflang="ja" href="{ja_href}" />\n  '
            content = content[:insert_pos] + ja_link + content[insert_pos:]
    
    return content

def fix_japanese_pages():
    """Processa tutti i file HTML nella directory ja/html/"""
    
    ja_html_dir = Path("/workspaces/LucaViberti.github.io/ja/html")
    
    if not ja_html_dir.exists():
        print(f"✗ Directory {ja_html_dir} non esiste")
        return False
    
    html_files = list(ja_html_dir.glob("*.html"))
    
    if not html_files:
        print(f"✗ Nessun file HTML trovato in {ja_html_dir}")
        return False
    
    fixed_count = 0
    errors = []
    
    for html_file in sorted(html_files):
        try:
            # Leggi il file
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Applica le correzioni
            content = fix_html_lang(content)
            content = add_ja_hreflang(content, html_file.name)
            
            # Se sono state fatte modifiche, scrivi il file
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Corretto: {html_file.name}")
                fixed_count += 1
            else:
                print(f"- Nessuna modifica: {html_file.name}")
        
        except Exception as e:
            error_msg = f"✗ Errore processando {html_file.name}: {e}"
            errors.append(error_msg)
            print(error_msg)
    
    print(f"\n{'='*50}")
    print(f"✓ File corretti: {fixed_count}")
    if errors:
        print(f"✗ Errori: {len(errors)}")
    
    return fixed_count > 0

if __name__ == "__main__":
    os.chdir("/workspaces/LucaViberti.github.io")
    success = fix_japanese_pages()
    if success:
        print(f"\n✓ Operazione completata!")
    else:
        print(f"\n✗ Nessun file è stato processato")
