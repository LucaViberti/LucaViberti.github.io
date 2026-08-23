# Guida al sito

Questa guida spiega come funziona il sito adesso e come fare le modifiche più
comuni. Non serve saper programmare.

---

## Cos'è cambiato

Prima il sito era fatto di **217 pagine HTML scritte a mano** (31 pagine × 7
lingue). Ogni pagina conteneva la sua copia di tutto: intestazione, menu, stili,
tabelle, dati. Cambiare un costo voleva dire modificare 7 file; aggiungere un
eroe, 7 file; e se ci si dimenticava di uno, le lingue divergevano in silenzio.

Adesso le pagine vengono **generate** a partire da file sorgente. I dati esistono
una volta sola e valgono per tutte le lingue.

```
src/                      ← QUI si modifica
 ├── site.yml             dominio, elenco lingue
 ├── pages.yml            elenco delle pagine
 ├── data/                i dati veri e propri (costi, eroi)
 ├── i18n/                i testi tradotti, una cartella per lingua
 ├── content/             il testo discorsivo delle pagine
 ├── styles/              i fogli di stile
 └── templates/           la struttura delle pagine

        ↓  python3 tools/build.py

index.html, html/, de/, ja/, ko/, tc/, vi/, zh/, assets/, sitemap-*.xml
                          ← QUI viene generato, NON si modifica a mano
```

**Regola d'oro:** si modifica solo dentro `src/`, poi si lancia la build. I file
HTML in `html/`, `de/`, `ja/` ecc. sono prodotti automaticamente: se li modifichi
a mano, la modifica verrà cancellata alla build successiva.

---

## I tre comandi

Da terminale, nella cartella del progetto:

```bash
python3 tools/build.py     # rigenera tutto il sito
python3 tools/check.py     # controlla che non ci siano link o immagini rotte
python3 tools/verify.py    # confronta il generato con quello che c'era prima
```

Dopo aver modificato qualcosa in `src/`, lancia sempre `build.py` e poi
`check.py`. Se `check.py` dice `no problems found`, puoi committare.

Serve Python 3 con due librerie; si installano una volta sola:

```bash
pip install jinja2 pyyaml
```

---

## Come fare le cose

### Correggere un costo nelle tabelle

I dati delle tabelle costi stanno in **`src/data/tips.yml`**. Cerca il numero da
correggere, cambialo, lancia la build. Cambia in tutte e 7 le lingue insieme.

Le tabelle sono organizzate per sezione (`castle`, `hero`, `gear`, …) e ogni
riga è una lista di celle:

```yaml
- - Level 21
  - 2.04 m
  - ''
  - Research Cottage, Hospital
```

I numeri non si traducono. Le parole invece passano dal glossario (vedi sotto).

### Tradurre una parola che compare nelle tabelle

Il glossario sta in **`src/i18n/terms/<lingua>.yml`** ed è fatto così:

```yaml
Stone and Timber: Stein und Holz
```

A sinistra il termine inglese, a destra la traduzione. Se un termine non c'è nel
file, il sito mostra l'inglese: **niente sparisce mai**, al massimo resta da
tradurre.

> Stato attuale: il tedesco ha 40 termini tradotti su 500, il vietnamita 4 su 500.
> Sono i due file da completare per primi.

### Aggiungere un eroe

Due passaggi.

**1.** In **`src/data/heroes.yml`**, sotto la fazione giusta, aggiungi:

```yaml
    - id: nuovo-eroe
      name: Nuovo Eroe
      image: /images/nuovo-eroe.jpeg
      alt: Nuovo Eroe
      role: dps
      skills:
      - Prima Abilità
      - Seconda Abilità
```

Il campo `role` può essere: `dps`, `tank`, `support`, `healer`, `tank_dps`,
`support_dps`, `healer_support`. L'etichetta visibile viene tradotta in
automatico in ogni lingua.

**2.** In **`src/i18n/heroes/<lingua>.yml`** aggiungi le frasi:

```yaml
      nuovo-eroe:
        skills:
          Prima Abilità: Descrizione della prima abilità.
          Seconda Abilità: Descrizione della seconda.
        note: Commento su quando usarlo.
```

Se lo fai solo in inglese, le altre lingue mostrano l'inglese finché non le
compili. La scheda però appare subito ovunque, con l'immagine giusta.

Ricorda di mettere l'immagine in `images/`. Se manca, `check.py` te lo dice.

### Correggere o aggiungere una traduzione di testo discorsivo

Il testo lungo delle pagine sta in **`src/content/<lingua>/<pagina>.html`**.
Sono normali frammenti HTML: modifica la frase e rilancia la build.

Titoli e descrizioni per Google stanno invece in
**`src/i18n/<lingua>.yml`**.

### Aggiungere una pagina nuova

1. Crea il testo in `src/content/en/nuova-pagina.html`
2. Aggiungi titolo e descrizione in `src/i18n/en.yml`
3. Aggiungi la pagina a `src/pages.yml`:

```yaml
nuova-pagina:
  kind: page
  has_adsense: true
  style: simple-page
```

4. Aggiungi la voce nel menu, in `src/partials/<lingua>/nav.html`
5. Lancia la build

Canonical, hreflang, Open Graph, sitemap e collegamenti tra lingue vengono
generati da soli.

### Cambiare qualcosa che appare su tutte le pagine

- Menu e piè di pagina: `src/partials/<lingua>/`
- Struttura della pagina (tag `<head>`, script): `src/templates/page.html.j2`
- Dominio, elenco lingue: `src/site.yml`

---

## Cosa controlla `check.py`

- ogni immagine e foglio di stile citato esiste davvero
- nessun link interno porta a una pagina inesistente
- ogni pagina esiste in tutte e 7 le lingue
- ogni pagina dichiara correttamente tutte le lingue alternative (hreflang)
- l'attributo lingua è corretto
- segnala le pagine molto più corte del normale per quella lingua (di solito
  vuol dire che manca del contenuto)

Il controllo gira anche automaticamente su GitHub a ogni push
(`.github/workflows/site.yml`), e blocca il push se i file generati non
corrispondono ai sorgenti — cioè se qualcuno ha modificato `src/` senza
rilanciare la build.

---

## Problemi che questa struttura ha già risolto

Erano tutti presenti prima e invisibili senza confrontare i file a mano:

- il **cinese tradizionale non aveva la sitemap** e non era proprio elencato
  nell'indice delle sitemap: Google non lo stava indicizzando
- la pagina **tabelle costi in coreano** aveva 4 sezioni intere in meno
  (Troop Skin, Rune, Pet, Villager): 597 righe di dati mancanti
- la pagina **Horde in coreano** puntava a 3 immagini inesistenti, aveva
  3 abilità in meno e 3 eroi con il ruolo sbagliato
- le **icone delle fazioni** non comparivano quasi mai fuori dall'inglese,
  perché lo script cercava solo i nomi inglesi
- 12 pagine per lingua **non chiudevano il tag `<main>`**
- `calculator.html` era **in italiano** in tutte le lingue tranne il coreano
- `/html/index.html` era un **doppione della home** non collegato a nulla, che
  competeva con la home stessa su Google (ora rimanda alla home)
- `restructure_site.py` era dentro la cartella pubblicata ed era
  **scaricabile dal sito**

---

## Cosa resta da fare

1. **Completare i glossari delle tabelle** — `src/i18n/terms/de.yml` e
   `src/i18n/terms/vi.yml` sono quasi vuoti, e al coreano mancano i termini
   delle 4 sezioni recuperate.
2. **Etichette formazione in tedesco** — `Front` e `Back` sono rimaste in
   inglese (solo `Mitte` è tradotto). In `src/i18n/heroes/de.yml`.
3. **Tre abilità coreane** mai tradotte (Horde Defender, Enthusiast,
   War Messenger): ora mostrano l'inglese.

---

## Se qualcosa va storto

I file generati sono tutti ricostruibili: se il sito si rompe, `git checkout` sui
file HTML e rilancia `python3 tools/build.py`. L'unica cosa che conta davvero è
la cartella `src/`.

Gli script in `tools/legacy/` sono vecchi script usati una volta sola per la
migrazione: non servono più, sono tenuti solo per storia.
