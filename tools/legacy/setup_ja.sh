#!/bin/bash
# Script per completare la configurazione della cartella giapponese

echo "🚀 Inizio copia file per la versione giapponese..."

# Copia tutti i file HTML dalla cartella html/ a ja/html/
echo "📋 Copiando file HTML..."
for file in html/*.html; do
    filename=$(basename "$file")
    if [ ! -f "ja/html/$filename" ]; then
        cp "$file" "ja/html/$filename"
        # Aggiorna i link nel file copiato
        sed -i 's|href="/html/|href="/ja/html/|g' "ja/html/$filename"
        sed -i 's|src="/html/|src="/ja/html/|g' "ja/html/$filename"
        sed -i 's|action="/html/|action="/ja/html/|g' "ja/html/$filename"
        sed -i 's|lang="en"|lang="ja"|g' "ja/html/$filename"
        echo "  ✅ $filename"
    else
        echo "  ⏭️  $filename (già esistente)"
    fi
done

echo ""
echo "✅ Copia completata!"
echo ""
echo "📊 Riepilogo file in ja/html/:"
ls -1 ja/html/*.html 2>/dev/null | wc -l
echo ""
echo "🎉 Operazione terminata con successo!"
echo ""
echo "⚠️  Ricorda di:"
echo "  1. Aggiornare gli index.html delle altre lingue (de, ko, vi, zh) per aggiungere hreflang='ja'"
echo "  2. Creare il file sitemap-ja.xml"
echo "  3. Tradurre i contenuti nelle pagine giapponesi"
