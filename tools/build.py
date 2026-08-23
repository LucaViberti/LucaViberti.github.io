#!/usr/bin/env python3
"""
Generate the whole site from src/.

    python3 tools/build.py            rebuild everything
    python3 tools/build.py --check    rebuild into memory and report what would
                                      change, without touching any file

Output is written in place (index.html, html/*.html, <lang>/...), exactly where
GitHub Pages already serves it from, so the generated HTML stays committed and
every rebuild shows up as a reviewable diff.

Everything a page needs comes from four places:

    src/site.yml          domain, languages, shared SEO defaults
    src/pages.yml         what each page is (template, stylesheet, extras)
    src/i18n/<lang>.yml   translated title / description / breadcrumb
    src/content/<lang>/   the body of the page

The ~100 lines of <head> boilerplate that used to be copy-pasted into all 217
files - canonical, eight hreflang links, Open Graph, Twitter cards, JSON-LD -
are derived here instead, which is what stops them drifting apart again.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import date

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")


def load_yaml(path: str):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


SITE = load_yaml(os.path.join(SRC, "site.yml"))
PAGES = load_yaml(os.path.join(SRC, "pages.yml"))
FACTIONS = load_yaml(os.path.join(SRC, "factions.yml"))
LANGS: dict = SITE["languages"]
DEFAULT = SITE["default_language"]
BASE = SITE["base_url"].rstrip("/")

I18N = {
    lang: load_yaml(os.path.join(SRC, "i18n", f"{lang}.yml")) or {}
    for lang in LANGS
}


# ---------------------------------------------------------------------------
# paths and urls
# ---------------------------------------------------------------------------


def rel_path(lang: str, slug: str) -> str:
    """Path of a generated page, relative to the repository root."""
    d = LANGS[lang]["dir"]
    if slug == "index":
        return "index.html" if not d else f"{d}/index.html"
    return f"html/{slug}.html" if not d else f"{d}/html/{slug}.html"


def url_for(lang: str, slug: str) -> str:
    return f"{BASE}/{rel_path(lang, slug)}"


def footer_url(lang: str) -> str:
    d = LANGS[lang]["dir"]
    return "/html/footer.html" if not d else f"/{d}/html/footer.html"


def strings_for(lang: str, slug: str) -> dict:
    """Translated strings, falling back to English for anything missing."""
    base = dict(I18N.get(DEFAULT, {}).get(slug, {}))
    base.update({k: v for k, v in (I18N.get(lang, {}).get(slug, {}) or {}).items() if v})
    return base


# ---------------------------------------------------------------------------
# structured data
# ---------------------------------------------------------------------------


def jsonld_webpage(lang: str, slug: str, t: dict, canonical: str) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "@id": f"{canonical}#webpage",
            "name": t["title"],
            "url": canonical,
            "inLanguage": LANGS[lang]["html_lang"],
            "description": t["description"],
            "image": SITE["og_image"],
            "isPartOf": {
                "@type": "WebSite",
                "name": SITE["site_name"],
                "url": BASE,
            },
        },
        ensure_ascii=False,
    )


def jsonld_breadcrumbs(lang: str, slug: str, t: dict, canonical: str) -> str | None:
    if not t.get("breadcrumb"):
        return None
    home = t.get("breadcrumb_home") or "Home"
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": home,
                    "item": url_for(lang, "index"),
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": t["breadcrumb"],
                    "item": canonical,
                },
            ],
        },
        ensure_ascii=False,
    )


# ---------------------------------------------------------------------------
# data-driven page bodies
# ---------------------------------------------------------------------------

# Utility classes replacing the ten inline style strings that used to be
# repeated on all 3,883 cells (55% of the old page's bytes).
CELL_DEFAULT_CLASS = {
    "thead-th": "th-top fb tc vb",
    "tbody-th": "th-left fb vb",
    "tbody-td": "tc vb",
}

_TABLE_DATA: dict | None = None
_TERMS: dict[str, dict] = {}


def table_data() -> list:
    global _TABLE_DATA
    if _TABLE_DATA is None:
        path = os.path.join(SRC, "data", "tips.yml")
        _TABLE_DATA = load_yaml(path) if os.path.exists(path) else []
    return _TABLE_DATA


def terms_for(lang: str) -> dict:
    if lang not in _TERMS:
        path = os.path.join(SRC, "i18n", "terms", f"{lang}.yml")
        _TERMS[lang] = (load_yaml(path) or {}) if os.path.exists(path) else {}
    return _TERMS[lang]


def normalise_cell(cell, part: str) -> dict:
    """Turn a stored cell into the tag, attributes and text the template needs."""
    if isinstance(cell, str):
        text, extra = cell, {}
    else:
        text, extra = cell.get("t", ""), cell

    is_header = part == "thead" or bool(extra.get("th"))
    tag = "th" if is_header else "td"
    key = f"{part}-{tag}"
    cls = extra.get("cls", CELL_DEFAULT_CLASS.get(key, ""))

    attrs = ""
    # A class token of the form "style:x:y" is an inline declaration we could
    # not express as a utility class; put it back as a style attribute.
    tokens = [c for c in cls.split() if not c.startswith("style:")]
    inline = [c[len("style:"):] for c in cls.split() if c.startswith("style:")]
    if tokens:
        attrs += f' class="{" ".join(tokens)}"'
    if inline:
        attrs += f' style="{";".join(inline)}"'
    if extra.get("c"):
        attrs += f' colspan="{extra["c"]}"'
    if extra.get("r"):
        attrs += f' rowspan="{extra["r"]}"'
    return {"tag": tag, "attrs": attrs, "html": text}


def render_tables_body(lang: str, t: dict) -> str:
    """Render the Cost Tables page body for one language."""
    glossary = terms_for(lang)

    def term(text: str) -> str:
        return glossary.get(text, text)

    sections = []
    for section in table_data():
        s = dict(section)
        s["tables"] = [
            {
                **table,
                "thead": [
                    [normalise_cell(c, "thead") for c in row] for row in table["thead"]
                ],
                "tbody": [
                    [normalise_cell(c, "tbody") for c in row] for row in table["tbody"]
                ],
            }
            for table in section["tables"]
        ]
        sections.append(s)

    return env.get_template("tips.html.j2").render(sections=sections, t=t, term=term)


def faction_icon_pairs(lang: str) -> list[tuple[str, str]]:
    """(display name, image) for every spelling this language uses."""
    images = FACTIONS["images"]
    aliases = FACTIONS["aliases"].get(lang, {})
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for faction, names in aliases.items():
        for name in names:
            if name in seen:
                continue
            seen.add(name)
            pairs.append((name, images[faction]))
    return pairs


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

env = Environment(
    loader=FileSystemLoader(os.path.join(SRC, "templates")),
    undefined=StrictUndefined,
    keep_trailing_newline=True,
)
# Pages are served as UTF-8, so write Japanese/Korean/Chinese text literally in
# generated JavaScript instead of \uXXXX escapes - it stays readable in a diff.
env.policies["json.dumps_kwargs"] = {"ensure_ascii": False, "sort_keys": False}


def render_page(lang: str, slug: str, entry: dict) -> str:
    t = strings_for(lang, slug)
    if not t.get("title"):
        raise SystemExit(f"missing title for {lang}/{slug} in src/i18n/{lang}.yml")

    canonical_slug = entry.get("canonical_to", slug)
    canonical = url_for(lang, canonical_slug)

    alternates = [
        {"hreflang": LANGS[l]["hreflang"], "url": url_for(l, canonical_slug)}
        for l in SITE["hreflang_order"]
    ]
    alternate_locales = [
        LANGS[l]["locale"] for l in SITE["hreflang_order"] if l != lang
    ]

    if entry.get("body_from") == "tables":
        content = render_tables_body(lang, t).rstrip("\n")
    else:
        content_path = os.path.join(SRC, "content", lang, f"{slug}.html")
        if not os.path.exists(content_path):
            content_path = os.path.join(SRC, "content", DEFAULT, f"{slug}.html")
        with open(content_path, encoding="utf-8") as fh:
            content = fh.read().rstrip("\n")

    # Templates run with StrictUndefined so a typo fails the build rather than
    # silently rendering nothing; fill in the optional flags explicitly.
    page = {
        "kind": "page",
        "style": None,
        "main_attrs": None,
        "has_adsense": False,
        "has_breadcrumbs": False,
        "itemscope_html": False,
        "stripe_donation": False,
        "faction_icons": False,
        "table_ui": False,
    }
    page.update(entry)
    page["html_extra_attrs"] = (
        ' itemscope itemtype="https://schema.org/WebPage"'
        if entry.get("itemscope_html")
        else ""
    )
    ma = entry.get("main_attrs")
    page["main_attrs_str"] = f" {ma}" if ma else ""

    template = env.get_template(
        "standalone.html.j2" if entry.get("kind") == "standalone" else "page.html.j2"
    )
    return template.render(
        site=SITE,
        lang=LANGS[lang],
        lang_code=lang,
        page=page,
        t=t,
        content=content,
        canonical=canonical,
        x_default=url_for(DEFAULT, canonical_slug),
        alternates=alternates,
        alternate_locales=alternate_locales,
        jsonld_webpage=jsonld_webpage(lang, slug, t, canonical),
        jsonld_breadcrumbs=jsonld_breadcrumbs(lang, slug, t, canonical),
        footer_url=footer_url(lang),
        faction_icons=faction_icon_pairs(lang),
    )


# ---------------------------------------------------------------------------
# redirects
# ---------------------------------------------------------------------------


def render_redirect(lang: str, target_slug: str) -> str:
    target = url_for(lang, target_slug)
    return f"""<!doctype html>
<html lang="{LANGS[lang]['html_lang']}">
<head>
  <meta charset="utf-8" />
  <title>{strings_for(lang, target_slug)['title']}</title>
  <link rel="canonical" href="{target}" />
  <meta name="robots" content="noindex, follow" />
  <meta http-equiv="refresh" content="0; url={target}" />
</head>
<body>
  <p>This page has moved to <a href="{target}">{target}</a>.</p>
  <script>location.replace({json.dumps(target)});</script>
</body>
</html>
"""


def build_redirects() -> dict[str, str]:
    out: dict[str, str] = {}
    for rule in SITE.get("redirects", []):
        for lang in LANGS:
            d = LANGS[lang]["dir"]
            rel = rule["from"] if not d else f"{d}/{rule['from']}"
            out[rel] = render_redirect(lang, rule["to"])
    return out


# ---------------------------------------------------------------------------
# sitemaps
# ---------------------------------------------------------------------------

# Pages that must not be advertised to search engines.
SITEMAP_EXCLUDE = {"thanks", "privacy"}


def build_sitemaps(today: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for lang in LANGS:
        urls = []
        for slug, entry in sorted(PAGES.items()):
            if slug in SITEMAP_EXCLUDE or entry.get("canonical_to"):
                continue
            loc = url_for(lang, slug)
            alts = "\n".join(
                f'    <xhtml:link rel="alternate" hreflang="{LANGS[l]["hreflang"]}"'
                f' href="{url_for(l, slug)}" />'
                for l in SITE["hreflang_order"]
            )
            urls.append(
                f"  <url>\n    <loc>{loc}</loc>\n{alts}\n"
                f'    <xhtml:link rel="alternate" hreflang="x-default"'
                f' href="{url_for(DEFAULT, slug)}" />\n'
                f"    <lastmod>{today}</lastmod>\n  </url>"
            )
        out[f"sitemap-{lang}.xml"] = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(urls)
            + "\n</urlset>\n"
        )

    entries = "\n".join(
        f"  <sitemap>\n    <loc>{BASE}/sitemap-{lang}.xml</loc>\n"
        f"    <lastmod>{today}</lastmod>\n  </sitemap>"
        for lang in LANGS
    )
    out["sitemap-index.xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + entries
        + "\n</sitemapindex>\n"
    )
    return out


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--check",
        action="store_true",
        help="report what would change without writing anything",
    )
    args = ap.parse_args()

    produced: dict[str, str] = {}

    # pages
    for slug, entry in sorted(PAGES.items()):
        for lang in LANGS:
            produced[rel_path(lang, slug)] = render_page(lang, slug, entry)

    # language partials loaded at runtime by nav-loader.js / the footer fetch
    for lang in LANGS:
        d = LANGS[lang]["dir"]
        prefix = "html" if not d else f"{d}/html"
        for name in ("nav", "footer"):
            src = os.path.join(SRC, "partials", lang, f"{name}.html")
            if os.path.exists(src):
                with open(src, encoding="utf-8") as fh:
                    produced[f"{prefix}/{name}.html"] = fh.read()

    # stylesheets
    styles_dir = os.path.join(SRC, "styles")
    for fn in sorted(os.listdir(styles_dir)):
        if fn.endswith(".css"):
            with open(os.path.join(styles_dir, fn), encoding="utf-8") as fh:
                produced[f"assets/css/{fn}"] = fh.read()

    # shared scripts
    js_dir = os.path.join(SRC, "js")
    if os.path.isdir(js_dir):
        for fn in sorted(os.listdir(js_dir)):
            if fn.endswith(".js"):
                with open(os.path.join(js_dir, fn), encoding="utf-8") as fh:
                    produced[f"assets/js/{fn}"] = fh.read()

    # legacy URL redirects
    produced.update(build_redirects())

    # sitemaps
    produced.update(build_sitemaps(date.today().isoformat()))

    # ---- compare / write ---------------------------------------------------
    changed, created = [], []
    for rel, text in sorted(produced.items()):
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            created.append(rel)
        else:
            with open(path, encoding="utf-8") as fh:
                if fh.read() != text:
                    changed.append(rel)

    if args.check:
        print(f"would create {len(created)} file(s), change {len(changed)}")
        for rel in created[:20]:
            print("   +", rel)
        for rel in changed[:20]:
            print("   ~", rel)
        extra = len(created) + len(changed) - 40
        if extra > 0:
            print(f"   ... and {extra} more")
        return 0

    for rel, text in produced.items():
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    # assets/ is generated in full, so anything left there that this run did not
    # produce is a leftover from a renamed or deleted source file.
    stale = 0
    for sub in ("assets/css", "assets/js"):
        directory = os.path.join(ROOT, sub)
        if not os.path.isdir(directory):
            continue
        for fn in os.listdir(directory):
            if f"{sub}/{fn}" not in produced:
                os.remove(os.path.join(directory, fn))
                stale += 1

    print(f"generated {len(produced)} files "
          f"({len(PAGES)} pages x {len(LANGS)} languages, plus assets and sitemaps)")
    if created:
        print(f"  new: {len(created)}")
    if changed:
        print(f"  updated: {len(changed)}")
    if stale:
        print(f"  removed stale assets: {stale}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
