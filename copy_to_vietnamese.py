#!/usr/bin/env python3
import os
import shutil

# Lista dei file HTML da copiare
html_files = [
    'adventure.html', 'anniversary.html', 'arms-race.html', 'beginners.html',
    'building.html', 'calculator.html', 'classicadv.html', 'events.html',
    'exclusive-gear.html', 'footer.html', 'gear.html', 'generaladv.html',
    'guild-race.html', 'guildboss.html', 'heroes.html', 'horde.html',
    'index.html', 'kingdom.html', 'league.html', 'lord-gear.html',
    'nature.html', 'nav.html', 'pets.html', 'privacy.html',
    'quick-tips.html', 'relic.html', 'research.html', 'seasononeadv.html',
    'shop.html', 'thanks.html', 'tips.html', 'villagers.html'
]

# Copia file dalla cartella html/ a vi/html/
for file in html_files:
    src = f'html/{file}'
    dst = f'vi/html/{file}'
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copiato: {src} -> {dst}")

# Copia index.html
shutil.copy2('index.html', 'vi/index.html')
print("Copiato: index.html -> vi/index.html")

print("\nTutti i file sono stati copiati nella cartella vietnamita!")
