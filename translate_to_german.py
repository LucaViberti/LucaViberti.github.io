#!/usr/bin/env python3
"""
Script per tradurre automaticamente i file HTML dall'inglese al tedesco.
Mantiene la struttura HTML intatta e traduce solo i contenuti testuali.
"""

import os
import re
from pathlib import Path

# Dizionario di traduzioni comuni (inglese -> tedesco)
translations = {
    # Navigazione e UI
    "Home": "Startseite",
    "Heroes": "Helden",
    "Overview": "Übersicht",
    "League": "Liga",
    "Nature": "Natur",
    "Horde": "Horde",
    "Gear": "Ausrüstung",
    "Exclusive Gear": "Exklusive Ausrüstung",
    "Pets": "Haustiere",
    "Building": "Gebäude",
    "Villagers": "Dorfbewohner",
    "Lord Gear": "Lord-Ausrüstung",
    "Relics Hall": "Reliktenhalle",
    "Research": "Forschung",
    "Adventure": "Adventure",
    "Classic": "Klassik",
    "Season 1": "Season 1",
    "Events": "Events",
    "Guild Race": "Gildenrennen",
    "Arms Race": "Rüstungswettlauf",
    "Guild Boss": "Gildenboss",
    "Beginners Guide": "Anfänger-Leitfaden",
    "SHOP": "SHOP",
    "Cost Tables": "Kostentabellen",
    "Quick Tips": "Schnelle Tipps",
    "Support Us": "Unterstützen Sie uns",
    "Donate with Stripe": "Mit Stripe spenden",
    "Policy&Privacy": "Richtlinien & Datenschutz",
    
    # Contenuti comuni
    "TopHeroes Guide": "TopHeroes Leitfaden",
    "Privacy Policy": "Datenschutzrichtlinie",
    "Contact us": "Kontaktieren Sie uns",
    "Your email": "Ihre E-Mail",
    "Message": "Nachricht",
    "Send": "Senden",
    "Thank you": "Vielen Dank",
    "Support us on Ko-fi": "Unterstützen Sie uns auf Ko-fi",
    
    # Frasi comuni
    "There are three factions in the game": "Es gibt drei Fraktionen im Spiel",
    "All rights reserved": "Alle Rechte vorbehalten",
    "If you'd like to support our guides": "Wenn Sie unsere Leitfäden unterstützen möchten",
    "consider leaving a small tip": "ziehen Sie bitte in Betracht, ein kleines Trinkgeld zu hinterlassen",
    
    # Meta tags
    'lang="en"': 'lang="de"',
    "Strategies, Heroes, Adventure & Events": "Strategien, Helden, Adventure & Events",
}

def translate_html_content(content, filename):
    """Traduce il contenuto HTML dall'inglese al tedesco"""
    
    # Sostituisci tutte le occorrenze nel dizionario
    for english, german in translations.items():
        content = content.replace(english, german)
    
    # Aggiorna i percorsi per puntare alla versione tedesca
    content = re.sub(r'href="/html/', 'href="/de/html/', content)
    content = re.sub(r'href="/index.html"', 'href="/de/index.html"', content)
    content = re.sub(r'fetch\("/html/footer.html"\)', 'fetch("/de/html/footer.html")', content)
    content = re.sub(r'src="/nav-loader.js"', 'src="/nav-loader.js"', content)  # Keep as is
    
    # Traduzioni specifiche per alcuni pattern comuni
    content = re.sub(
        r'Short, practical guides to progress faster in <strong>TopHeroes</strong>',
        'Kurze, praktische Anleitungen für schnelleren Fortschritt in <strong>TopHeroes</strong>',
        content
    )
    
    return content

def main():
    """Funzione principale per la traduzione dei file"""
    
    # Percorsi
    source_dir = Path("/workspaces/LucaViberti.github.io/html")
    target_dir = Path("/workspaces/LucaViberti.github.io/de/html")
    
    # Crea la directory di destinazione se non esiste
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Lista dei file già tradotti (da saltare)
    already_translated = {"nav.html", "footer.html", "heroes.html"}
    
    # Processa ogni file HTML
    html_files = list(source_dir.glob("*.html"))
    
    print(f"Trovati {len(html_files)} file HTML da processare")
    
    for html_file in html_files:
        if html_file.name in already_translated:
            print(f"⏭️  Saltato {html_file.name} (già tradotto)")
            continue
            
        print(f"📝 Processando {html_file.name}...")
        
        try:
            # Leggi il file originale
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Traduci il contenuto
            translated_content = translate_html_content(content, html_file.name)
            
            # Scrivi il file tradotto
            target_file = target_dir / html_file.name
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            print(f"✅ Completato {html_file.name}")
            
        except Exception as e:
            print(f"❌ Errore processando {html_file.name}: {e}")
    
    print("\n✨ Traduzione completata!")

if __name__ == "__main__":
    main()
