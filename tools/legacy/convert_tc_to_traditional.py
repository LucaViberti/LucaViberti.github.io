#!/usr/bin/env python3
"""
Converte tutti i file HTML nella cartella tc da cinese semplificato a cinese tradizionale.
"""
import os
from opencc import OpenCC

# Crea il convertitore da semplificato a tradizionale (Taiwan standard)
cc = OpenCC('s2twp')  # Simplified to Traditional (Taiwan) with phrases

def convert_file(filepath):
    """Converte un singolo file da cinese semplificato a tradizionale."""
    print(f"Convertendo: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Converti il contenuto
    converted = cc.convert(content)
    
    # Scrivi il file convertito
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(converted)
    
    print(f"✓ Completato: {filepath}")

def main():
    """Converte tutti i file HTML nella cartella tc."""
    tc_dir = '/workspaces/LucaViberti.github.io/tc'
    
    # Converti index.html nella root di tc
    index_file = os.path.join(tc_dir, 'index.html')
    if os.path.exists(index_file):
        convert_file(index_file)
    
    # Converti tutti i file HTML nella sottocartella html
    html_dir = os.path.join(tc_dir, 'html')
    if os.path.exists(html_dir):
        for filename in os.listdir(html_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(html_dir, filename)
                convert_file(filepath)
    
    print("\n✅ Conversione completata!")

if __name__ == '__main__':
    main()
