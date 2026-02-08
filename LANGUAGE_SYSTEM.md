# Language Switcher System (Sistema di Cambio Lingua)

## Overview / Panoramica

Il sito TopHeroes Guide supporta un **sistema di cambio lingua bilingue (Inglese/Tedesco)** con:
- ✅ Cambio lingua fluido e intuitivo
- ✅ Memoria della preferenza in localStorage
- ✅ Link intelligenti tra versioni linguistiche
- ✅ Footer e selector visibili in entrambe le lingue

---

## File Structure / Struttura dei File

```
/workspaces/LucaViberti.github.io/
├── index.html                  # Homepage inglese (EN)
├── de/index.html              # Homepage tedesca (DE)
├── lang-switcher.js           # Script centrale di gestione lingua
├── html/
│   ├── *.html                 # Tutti i file EN
│   └── footer.html            # Footer EN + language selector
└── de/html/
    ├── *.html                 # Tutti i file DE
    └── footer.html            # Footer DE + language selector
```

---

## How It Works / Come Funziona

### 1. **Language Selector Button / Bottone Cambio Lingua**

Disponibile in:
- **Footer**: Link "🇬🇧 English | 🇩🇪 Deutsch" (in entrambe le versioni)
- **Homepage**: Banner blu all'inizio della pagina principale

**Comportamento:**
- Click su "English" → Naviga a version EN della pagina corrente
- Click su "Deutsch" → Naviga a version DE della pagina corrente
- Salva la preferenza in `localStorage` con chiave `topheroes-lang`

### 2. **Automatic Path Conversion / Conversione Automatica Percorsi**

```javascript
// Esempi di conversione:
/index.html              → /de/index.html
/de/index.html           → /index.html
/html/heroes.html        → /de/html/heroes.html
/de/html/heroes.html     → /html/heroes.html
```

### 3. **LocalStorage Persistence / Memorizzazione Preferenza**

```javascript
// Salva: localStorage.setItem('topheroes-lang', 'de')
// Legge: localStorage.getItem('topheroes-lang')  → 'de' o 'en'
```

La preferenza viene utilizzata per:
- ✅ Redirect automatico dalla homepage (opzionale)
- ✅ Esperienze future (quando l'utente torna sul sito)

---

## Using the Language Switcher / Come Usare

### In HTML Files / Nei File HTML

**1. Nel Footer (automatico):**
```html
<!-- Nel footer.html (EN e DE) aggiunto automaticamente -->
<div class="lang-selector" id="footer-lang-selector"></div>
<script src="/lang-switcher.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function() {
    LangSwitcher.init('footer-lang-selector');
  });
</script>
```

**2. Bottone Personalizzato:**
```html
<button onclick="LangSwitcher.switchLanguage('de')">
  🇩🇪 Zur deutschen Version
</button>
```

**3. Link Intelligente:**
```html
<a href="#" onclick="LangSwitcher.switchLanguage('en'); return false;">
  English
</a>
```

---

## JavaScript API / API JavaScript

### `LangSwitcher.switchLanguage(lang)`
Cambia lingua e naviga alla versione corrente nell'altra lingua.

```javascript
LangSwitcher.switchLanguage('de');  // → Naviga a version DE
LangSwitcher.switchLanguage('en');  // → Naviga a version EN
```

### `LangSwitcher.getCurrentLang()`
Ritorna la lingua corrente (`'en'` o `'de'`) dal pathname.

```javascript
const currentLang = LangSwitcher.getCurrentLang();  // 'en' o 'de'
```

### `LangSwitcher.getPreferredLang()`
Legge la lingua preferita da localStorage.

```javascript
const preferred = LangSwitcher.getPreferredLang();  // 'en' di default
```

### `LangSwitcher.setPreferredLang(lang)`
Salva la lingua preferita in localStorage.

```javascript
LangSwitcher.setPreferredLang('de');
```

### `LangSwitcher.switchPath(lang)`
Ritorna il percorso equivalente nell'altra lingua (senza navigare).

```javascript
const dePath = LangSwitcher.switchPath('de');  // '/de/html/heroes.html'
```

### `LangSwitcher.init(elementId)`
Inizializza il language selector in un elemento DOM.

```javascript
LangSwitcher.init('footer-lang-selector');  // Popola il div con il selector
```

### `LangSwitcher.autoRedirectIfNeeded()`
Facoltativo: Redirige automaticamente dalla homepage vers la lingua preferita.

```javascript
// Attualmente commentato, attivabile decommentando nel lang-switcher.js
LangSwitcher.autoRedirectIfNeeded();
```

---

## URL Mapping / Schema degli URL

| Pagina | English | Deutsch |
|--------|---------|---------|
| Homepage | `/index.html` | `/de/index.html` |
| Heroes | `/html/heroes.html` | `/de/html/heroes.html` |
| Adventure | `/html/generaladv.html` | `/de/html/generaladv.html` |
| Cost Tables | `/html/tips.html` | `/de/html/tips.html` |
| Tutti gli altri | `/html/*.html` | `/de/html/*.html` |

---

## Visual UI / Interfaccia Visiva

### Footer Language Selector / Selector nel Footer
```
────────────────────────────────────────────────────
Language:    🇬🇧 English | 🇩🇪 Deutsch
────────────────────────────────────────────────────
```

Stile:
- **Current language**: Testo **grassetto** e blu (#0066cc)
- **Inactive language**: Testo grigio (#666)
- **Separatore**: "|" leggero (#ccc)

### Homepage Banner / Banner sulla Homepage
```
┌────────────────────────────────────────────────────┐
│ Language: 🇬🇧 English | 🇩🇪 Deutsch              │
└────────────────────────────────────────────────────┘
```

Background: Azzurro chiaro (#f0f8ff)
Border: Blu leggero (#b3d9ff)
Padding: 14px

---

## Maintenance / Manutenzione

### Quando Aggiungere Nuove Pagine / Adding New Pages

1. **Crea la versione EN**: `/html/new-page.html`
2. **Crea la versione DE**: `/de/html/new-page.html`
3. **Aggiungi link nel nav**: (verrà caricato automaticamente)
4. **Non devi modificare `lang-switcher.js`** - funziona per qualsiasi URL!

### Disabilitazione Redirect Automatico / Disabling Auto-Redirect

Nel file `lang-switcher.js`, cerca questa sezione e commenta:

```javascript
// Commenta questa linea per disabilitare il redirect automatico
// LangSwitcher.autoRedirectIfNeeded();
```

---

## Browser Support / Supporto Browser

- ✅ Chrome, Firefox, Safari, Edge (tutti moderni)
- ✅ localStorage supportato (IE 8+)
- ✅ Fallback a `/index.html` se localStorage non disponibile

---

## Notes / Note

- Il selector di lingua è **sempre visibile** nel footer
- La lingua corrente è **evidenziata in blu** e grassetto
- Il link per "Lingua corrente" rimane (non fa nulla) per UX consistency
- localStorage viene usato solo per preferenza futura (non essenziale al funzionamento)
- **Nessuna dipendenza esterna** - puro JavaScript vanilla

---

## Future Improvements / Possibili Miglioramenti Futuri

- [ ] Aggiungere più lingue (FR, ES, IT)
- [ ] Cookie alternativo per GDPR compliance
- [ ] Bandiere selezionabili con dropdown
- [ ] Detrazione automatica della lingua del browser (navigator.language)
- [ ] Analytics per tracciare quale lingua viene usata più spesso
