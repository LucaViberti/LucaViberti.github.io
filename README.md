# TopHeroes Guide

Static HTML/CSS/JavaScript guides published with GitHub Pages at
`www.guidetopheroes.com`. The **English pages are the editorial source**;
all other versions are translations of the same guides and game data.

## Local development

From the repository root, run:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

No application dependencies or build are required for local development.
GitHub Pages also uses `_config.yml` and `jekyll-sitemap` when publishing.

## Structure and editing

- `index.html`: official English home; `html/`: English guides and nav/footer fragments.
- `de/`, `ja/`, `ko/`, `vi/`, `zh/`, `tc/`: translated homes and matching `html/` pages.
- `images/`: shared assets; never add language prefixes to image URLs.
- `nav-loader.js`, `lang-switcher.js`, `navigation.css`: common navigation behavior.
- `html/tips.html`: official cost tables; retain identical values in all translations.
- `sitemap-index.xml`: one sitemap per language, including traditional Chinese (`tc`).

Edit the English guide first, then update every translation without changing its
meaning, lineup, images, numbers or table structure. Preserve stable element IDs
used by tabs, links and language switching. Each `html/index.html` redirects to
its language's primary home, so there is only one home to maintain per language.

Keep canonical URLs, all seven `hreflang` alternatives, `x-default`, JSON-LD and
the language sitemap consistent when adding or removing a guide. Navigation and
footer fragments are not standalone indexed pages. Spring of the Steed and the
old Rush calculator have been removed from every language.

## Checks

Requires Python 3 and Node.js:

```sh
python3 -m unittest discover -s tests -v
```

These checks cover links/assets, fragments, language sets, HTML structure,
metadata, sitemap coverage, JavaScript syntax, translated images/table data and
maintenance helpers. `tests/english-content.json` protects the original English
editorial text; update it only alongside an intentional English content change.
Also check navigation, language switching, table tabs and FAQ panels in desktop
and mobile browsers when changing their behavior. External advertising,
donations and form submissions require separate service verification.

With Playwright and Chromium installed, `python3 tests/browser_smoke.py` loads
every page and checks those interactions. It blocks external services and does
not submit forms or make payments.

## Maintenance helpers

`python3 copy_to_ja.py` (also available through `setup_ja.sh`, `copy_files.py`,
and `copy_all_html.py`) creates **only missing** Japanese drafts and never
overwrites existing translations. New drafts still need translation and review.
The helpers resolve paths from their own location and work from any directory.

`python3 fix_japanese_pages.py` repairs Japanese language metadata.
`convert_tc_to_traditional.py` converts visible Chinese text while preserving
URLs, attributes and JavaScript; its optional dependency is
`opencc-python-reimplemented==0.1.7`. The historical restructuring script refuses
to run on this already organized, multilingual repository.
