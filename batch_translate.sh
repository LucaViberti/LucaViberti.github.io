#!/bin/bash
# Script per copiare e tradurre in batch i file HTML rimanenti

SOURCE_DIR="/workspaces/LucaViberti.github.io/html"
TARGET_DIR="/workspaces/LucaViberti.github.io/de/html"

# Lista dei file già tradotti (da saltare)
SKIP_FILES="nav.html footer.html heroes.html beginners.html thanks.html quick-tips.html privacy.html"

# Funzione per tradurre contenuti base
translate_file() {
    local source="$1"
    local target="$2"
    
    echo "Traduco: $(basename "$source")"
    
    # Copia il file e applica traduzioni
    sed -e 's/lang="en"/lang="de"/g' \
        -e 's/TopHeroes Guide/TopHeroes Leitfaden/g' \
        -e 's/Strategies, Heroes, Adventure & Events/Strategien, Helden, Adventure & Events/g' \
        -e 's/<title>TopHeroes Guide - /<title>TopHeroes Leitfaden - /g' \
        -e 's/Home/Startseite/g' \
        -e 's/>Heroes</>Helden</g' \
        -e 's/>League</>Liga</g' \
        -e 's/>Nature</>Natur</g' \
        -e 's/>Horde</>Horde</g' \
        -e 's/>Overview</>Übersicht</g' \
        -e 's/>Gear</>Ausrüstung</g' \
        -e 's/>Pets</>Haustiere</g' \
        -e 's/>Building</>Gebäude</g' \
        -e 's/>Villagers</>Dorfbewohner</g' \
        -e 's/>Research</>Forschung</g' \
        -e 's/>Adventure</>Adventure</g' \
        -e 's/>Classic</>Klassik</g' \
        -e 's/>Events</>Events</g' \
        -e 's/>Guild Race</>Gildenrennen</g' \
        -e 's/>Arms Race</>Rüstungswettlauf</g' \
        -e 's/>Guild Boss</>Gildenboss</g' \
        -e 's/Beginners Guide/Anfänger-Leitfaden/g' \
        -e 's/Quick Tips/Schnelle Tipps/g' \
        -e 's/Cost Tables/Kostentabellen/g' \
        -e 's/Support Us/Unterstützen Sie uns/g' \
        -e 's/Policy&Privacy/Richtlinien & Datenschutz/g' \
        -e 's/Donate with Stripe/Mit Stripe spenden/g' \
        -e 's/All rights reserved/Alle Rechte vorbehalten/g' \
        -e 's|href="/html/|href="/de/html/|g' \
        -e 's|href="/index.html"|href="/de/index.html"|g' \
        -e 's|fetch("/html/footer.html")|fetch("/de/html/footer.html")|g' \
        "$source" > "$target"
}

# Processa tutti i file HTML
for file in "$SOURCE_DIR"/*.html; do
    filename=$(basename "$file")
    
    # Salta file già tradotti
    if echo "$SKIP_FILES" | grep -q "$filename"; then
        echo "Saltato: $filename (già tradotto manualmente)"
        continue
    fi
    
    # Salta restructure_site.py e .gitkeep
    if [[ "$filename" == "restructure_site.py" ]] || [[ "$filename" == ".gitkeep" ]]; then
        continue
    fi
    
    # Traduci il file
    translate_file "$file" "$TARGET_DIR/$filename"
done

echo ""
echo "✅ Traduzione batch completata!"
echo "Nota: Alcuni contenuti potrebbero necessitare di traduzioni manuali più dettagliate."
