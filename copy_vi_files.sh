#!/bin/bash

# Script per copiare tutti i file HTML dalla cartella html/ alla cartella vi/html/
# e modificare il lang da "en" a "vi"

SOURCE_DIR="html"
TARGET_DIR="vi/html"

# Lista dei file HTML da copiare (escludo nav.html che ho già creato manualmente)
FILES=(
    "adventure.html"
    "anniversary.html"
    "arms-race.html"
    "beginners.html"
    "building.html"
    "calculator.html"
    "classicadv.html"
    "events.html"
    "exclusive-gear.html"
    "footer.html"
    "gear.html"
    "generaladv.html"
    "guild-race.html"
    "guildboss.html"
    "heroes.html"
    "horde.html"
    "index.html"
    "kingdom.html"
    "league.html"
    "lord-gear.html"
    "nature.html"
    "pets.html"
    "privacy.html"
    "quick-tips.html"
    "relic.html"
    "research.html"
    "seasononeadv.html"
    "shop.html"
    "thanks.html"
    "tips.html"
    "villagers.html"
)

echo "Copiando file HTML da $SOURCE_DIR a $TARGET_DIR..."

for file in "${FILES[@]}"; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        # Copia il file e modifica il lang da "en" a "vi"
        sed 's/lang="en"/lang="vi"/' "$SOURCE_DIR/$file" > "$TARGET_DIR/$file"
        echo "✓ Copiato e modificato: $file"
    else
        echo "✗ File non trovato: $SOURCE_DIR/$file"
    fi
done

echo ""
echo "Copia completata! Totale file processati: ${#FILES[@]}"
