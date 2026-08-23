#!/usr/bin/env python3
"""
One-time migration: turn the hand-written site into structured sources.

Reads every existing page and splits it into the three things that actually
differ from page to page:

    src/content/<lang>/<slug>.html   the body content (prose, cards, tables)
    src/i18n/<lang>.yml              title / description / breadcrumb strings
    src/styles/<name>.css            the inline <style> blocks, de-duplicated

plus a page registry (src/pages.yml) describing what each page is.

Everything else in the old files - the ~100 lines of <head> boilerplate, the
navbar/footer plumbing, the hreflang block - is boilerplate that build.py
regenerates, so it is deliberately NOT saved here.

Run from the repository root:  python3 tools/extract.py
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import defaultdict

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")

with open(os.path.join(SRC, "site.yml"), encoding="utf-8") as fh:
    SITE = yaml.safe_load(fh)

LANGS: dict = SITE["languages"]

# Pages that are complete standalone documents: no navbar, no footer, own shell.
STANDALONE = {"calculator", "thanks"}
# Fragments loaded at runtime by JS rather than served as pages.
PARTIALS = {"nav", "footer"}

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def page_path(lang: str, slug: str) -> str:
    """On-disk path of an existing page, relative to the repo root."""
    d = LANGS[lang]["dir"]
    if slug == "index":
        return os.path.join(d, "index.html") if d else "index.html"
    return os.path.join(d, "html", f"{slug}.html") if d else os.path.join("html", f"{slug}.html")


def read(rel: str) -> str | None:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def write(rel: str, text: str) -> None:
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def first(pattern: str, text: str, flags=re.S) -> str | None:
    m = re.search(pattern, text, flags)
    return m.group(1) if m else None


def dedent_block(text: str) -> str:
    """Strip the common leading indentation so fragments are readable on disk."""
    lines = [ln for ln in text.split("\n")]
    widths = [len(ln) - len(ln.lstrip()) for ln in lines if ln.strip()]
    if not widths:
        return text.strip("\n")
    cut = min(widths)
    out = [ln[cut:] if ln.strip() else "" for ln in lines]
    return "\n".join(out).strip("\n")


# ---------------------------------------------------------------------------
# head extraction
# ---------------------------------------------------------------------------


def extract_head(html: str) -> dict:
    head = first(r"<head>(.*?)</head>", html) or ""

    title = first(r"<title>(.*?)</title>", head)
    desc = first(r'<meta\s+name="description"\s+content="(.*?)"\s*/?>', head)

    # The breadcrumb JSON-LD carries the human name of the page and of "Home",
    # both of which are translated strings we need to keep.
    crumb_home = crumb_page = None
    raw = first(r'<script type="application/ld\+json" id="seo-breadcrumbs">(.*?)</script>', head)
    if raw:
        try:
            data = json.loads(raw.strip())
            items = data.get("itemListElement", [])
            if len(items) >= 1:
                crumb_home = items[0].get("name")
            if len(items) >= 2:
                crumb_page = items[1].get("name")
        except json.JSONDecodeError:
            pass

    styles = re.findall(r"<style>(.*?)</style>", head, re.S)

    return {
        "title": title,
        "description": desc,
        "breadcrumb_home": crumb_home,
        "breadcrumb_page": crumb_page,
        "style": "\n".join(s.strip("\n") for s in styles) if styles else None,
        "has_adsense": "adsbygoogle.js" in head,
        "has_breadcrumbs": raw is not None,
        "itemscope_html": bool(re.search(r"<html[^>]*itemscope", html)),
        "html_tag": first(r"(<html[^>]*>)", html),
    }


# ---------------------------------------------------------------------------
# body extraction
# ---------------------------------------------------------------------------

NAV_SCRIPT = re.compile(r'<script src="/nav-loader\.js" defer></script>')
FOOTER_DIV = re.compile(r'<div id="footer"></div>')
FOOTER_FETCH = re.compile(
    r'<script>\s*fetch\((["\'])/[^"\']*/?footer\.html\1\).*?</script>', re.S
)


def extract_body(html: str, slug: str) -> dict:
    body = first(r"<body[^>]*>(.*)</body>", html)
    if body is None:
        raise ValueError("no <body> found")

    body_attrs = first(r"<body([^>]*)>", html) or ""

    if slug in STANDALONE:
        return {
            "content": dedent_block(body),
            "body_attrs": body_attrs.strip(),
            "main_attrs": None,
            "pre_main": None,
            "extra_scripts": [],
        }

    # --- region between the navbar plumbing and the footer plumbing ---------
    m = NAV_SCRIPT.search(body)
    start = m.end() if m else 0

    m = FOOTER_DIV.search(body, start)
    if m:
        end = m.start()
        after = body[m.end():]
    else:
        end = len(body)
        after = ""

    region = body[start:end]

    # Trailing page-specific scripts live after the footer fetch snippet.
    # There are only three kinds site-wide, and all three are boilerplate that
    # build.py regenerates, so we record *which* ones a page needs rather than
    # copying the code. (The faction-icon script is language dependent - it
    # matches translated heading text - which is exactly why copying it around
    # by hand had gone wrong.)
    after = FOOTER_FETCH.sub("", after, count=1)
    trailing = "\n".join(re.findall(r"(<script>.*?</script>)", after, re.S))
    extra_scripts = {
        "faction_icons": bool(re.search(r"const icons\s*=", trailing)),
        "table_ui": bool(re.search(r"th-collapse|castle-switch", trailing)),
    }
    leftover = re.sub(r"<script>.*?</script>", "", trailing, flags=re.S).strip()
    if leftover:
        extra_scripts["unrecognised"] = leftover

    # --- split the region into "before <main>" and the <main> itself --------
    mm = re.search(r"<main([^>]*)>", region)
    if not mm:
        # No <main> at all (shouldn't happen on content pages) - keep as-is.
        return {
            "content": dedent_block(region),
            "body_attrs": body_attrs.strip(),
            "main_attrs": None,
            "pre_main": None,
            "extra_scripts": extra_scripts,
        }

    pre_main = region[: mm.start()]
    main_attrs = mm.group(1).strip()
    inner = region[mm.end():]

    # Several pages never close <main>. Drop the tag if present; build.py
    # always emits a properly balanced one.
    close = inner.rfind("</main>")
    if close != -1:
        inner = inner[:close]

    # Everything left before <main> is either an HTML comment left over from
    # editing (some still in Italian, some machine-translated into Korean) or
    # the Stripe donation block on the home page. Comments are dropped; the
    # Stripe block becomes a template partial with one translatable label.
    stripe_aria = None
    m = re.search(r'<section class="stripe-donation"[^>]*aria-label="([^"]*)"', pre_main)
    if m:
        stripe_aria = m.group(1)
        pre_main = re.sub(
            r'<section class="stripe-donation".*?</section>', "", pre_main, flags=re.S
        )

    pre_main = re.sub(r"<!--.*?-->", "", pre_main, flags=re.S).strip()

    return {
        "content": dedent_block(inner),
        "body_attrs": body_attrs.strip(),
        "main_attrs": main_attrs or None,
        "pre_main": dedent_block(pre_main) if pre_main else None,
        "stripe_donation": stripe_aria,
        "extra_scripts": extra_scripts,
    }


# ---------------------------------------------------------------------------
# faction icon data
# ---------------------------------------------------------------------------

FACTIONS = ("league", "nature", "horde")


def extract_factions() -> dict:
    """
    Collect, per language, every spelling of each faction name that appears in
    the site's own text.

    The faction-icon script works by matching link/heading text against a map
    of names. Because that map was maintained by hand in every page of every
    language it had drifted badly: Korean pages used three different spellings
    of "League" ("League", "리그", "연맹") so the icons only ever appeared on
    some of them. Gathering every alias that the content actually uses makes
    the lookup succeed regardless of which wording a given page chose.
    """
    aliases: dict[str, dict[str, set]] = {
        lang: {f: set() for f in FACTIONS} for lang in LANGS
    }

    for lang in LANGS:
        d = LANGS[lang]["dir"]
        base = os.path.join(d, "html") if d else "html"

        # 1. navigation links
        nav = read(os.path.join(base, "nav.html"))
        if nav:
            for f in FACTIONS:
                for m in re.finditer(rf'href="[^"]*{f}\.html"[^>]*>([^<]+)<', nav):
                    aliases[lang][f].add(m.group(1).strip())

        # 2. link and heading text on every page, plus any hand-written map
        for fn in sorted(os.listdir(os.path.join(ROOT, base))):
            if not fn.endswith(".html") or os.path.splitext(fn)[0] in PARTIALS:
                continue
            html = read(os.path.join(base, fn)) or ""
            for f in FACTIONS:
                for m in re.finditer(rf'href="[^"]*{f}\.html"[^>]*>([^<]+)</a>', html):
                    txt = m.group(1).strip()
                    if txt and "<" not in txt and len(txt) < 40:
                        aliases[lang][f].add(txt)
            m = re.search(r"const icons\s*=\s*\{(.*?)\}", html, re.S)
            if m:
                for key, val in re.findall(r"'([^']+)'\s*:\s*'([^']+)'", m.group(1)):
                    for f in FACTIONS:
                        if f"{f}-symbol" in val:
                            aliases[lang][f].add(key.strip())

    # English names are understood in every language (the site keeps proper
    # nouns in English by convention), so make sure they are always present.
    english = {f: sorted(aliases["en"][f]) for f in FACTIONS}
    for lang in LANGS:
        for f in FACTIONS:
            aliases[lang][f].update(english[f])

    return {
        "images": {f: f"/images/{f}-symbol.jpeg" for f in FACTIONS},
        "aliases": {
            lang: {f: sorted(aliases[lang][f]) for f in FACTIONS} for lang in LANGS
        },
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def guard_already_migrated() -> None:
    """
    Refuse to run once the site is generated.

    This is a one-way migration: it reads the hand-written pages and produces
    src/. After the first build those pages no longer carry inline <style>
    blocks or a hand-written <head>, so re-running would quietly produce an
    empty src/ and destroy the real sources.
    """
    sample = read(os.path.join("html", "league.html")) or ""
    if "<style>" not in sample and 'href="/assets/css/' in sample:
        print(
            "refusing to run: the site is already generated from src/.\n"
            "\n"
            "tools/extract.py is the one-time migration that created src/ from\n"
            "the old hand-written pages. src/ is the source of truth now - edit\n"
            "it and run tools/build.py.",
            file=sys.stderr,
        )
        raise SystemExit(2)


def main() -> int:
    guard_already_migrated()
    slugs = sorted(
        os.path.splitext(f)[0]
        for f in os.listdir(os.path.join(ROOT, "html"))
        if f.endswith(".html")
    )
    slugs = [s for s in slugs if s not in PARTIALS]
    # The root index lives outside html/, add it explicitly.
    if "index" not in slugs:
        slugs.append("index")
    slugs = sorted(set(slugs))

    registry: dict[str, dict] = {}
    i18n: dict[str, dict] = {lang: {} for lang in LANGS}
    styles_by_hash: dict[str, str] = {}
    style_usage: dict[tuple[str, str], str] = {}
    warnings: list[str] = []

    for slug in slugs:
        kind = "standalone" if slug in STANDALONE else "page"
        per_lang_extra: dict[str, str] = {}
        entry: dict = {"kind": kind}

        for lang in LANGS:
            rel = page_path(lang, slug)
            html = read(rel)
            if html is None:
                warnings.append(f"MISSING  {rel}")
                continue

            try:
                head = extract_head(html)
                body = extract_body(html, slug)
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"PARSE-FAIL {rel}: {exc}")
                continue

            # ---- content fragment ----------------------------------------
            write(f"src/content/{lang}/{slug}.html", body["content"] + "\n")

            # ---- translated strings --------------------------------------
            strings = {"title": head["title"], "description": head["description"]}
            if head["breadcrumb_page"]:
                strings["breadcrumb"] = head["breadcrumb_page"]
            if head["breadcrumb_home"]:
                strings["breadcrumb_home"] = head["breadcrumb_home"]
            if body.get("stripe_donation"):
                strings["support_aria"] = body["stripe_donation"]
            i18n[lang][slug] = strings

            # ---- style block ---------------------------------------------
            if head["style"]:
                h = hashlib.md5(head["style"].encode()).hexdigest()[:10]
                styles_by_hash[h] = head["style"]
                style_usage[(slug, lang)] = h

            # ---- structural attributes (language independent) ------------
            for key in ("main_attrs", "pre_main", "body_attrs"):
                val = body[key]
                prev = entry.get(key, "__unset__")
                if prev == "__unset__":
                    entry[key] = val
                elif prev != val and lang != SITE["default_language"]:
                    # English wins; note the divergence.
                    warnings.append(
                        f"DIVERGENT {key} on {slug} ({lang}) - using English version"
                    )

            entry["has_adsense"] = head["has_adsense"]
            entry["has_breadcrumbs"] = head["has_breadcrumbs"]
            entry["itemscope_html"] = head["itemscope_html"]
            if body.get("stripe_donation"):
                entry["stripe_donation"] = True

            if body["extra_scripts"]:
                per_lang_extra[lang] = body["extra_scripts"]

        # A page needs a given script if ANY language carried it. Doing it this
        # way repairs pages where the script had simply been forgotten in some
        # translations (adventure was missing it in tc/zh, pets in de/ko).
        if per_lang_extra:
            wants_icons = any(v.get("faction_icons") for v in per_lang_extra.values())
            wants_tables = any(v.get("table_ui") for v in per_lang_extra.values())
            if wants_icons:
                entry["faction_icons"] = True
                partial = [l for l, v in per_lang_extra.items() if not v.get("faction_icons")]
                if partial:
                    warnings.append(
                        f"REPAIRED  {slug}: faction-icon script was missing in {sorted(partial)}"
                    )
            if wants_tables:
                entry["table_ui"] = True
            for lang, v in per_lang_extra.items():
                if "unrecognised" in v:
                    warnings.append(f"UNKNOWN-SCRIPT {slug} ({lang}) - needs manual review")

        registry[slug] = entry

    # ---- partials (nav / footer), per language ----------------------------
    for name in sorted(PARTIALS):
        for lang in LANGS:
            d = LANGS[lang]["dir"]
            rel = os.path.join(d, "html", f"{name}.html") if d else os.path.join("html", f"{name}.html")
            txt = read(rel)
            if txt is None:
                warnings.append(f"MISSING  {rel}")
                continue
            write(f"src/partials/{lang}/{name}.html", txt.rstrip("\n") + "\n")

    # ---- styles ------------------------------------------------------------
    # Name each distinct style block after the page(s) that use it.
    hash_pages = defaultdict(set)
    for (slug, lang), h in style_usage.items():
        hash_pages[h].add(slug)

    names: dict[str, str] = {}
    for h, pages in sorted(hash_pages.items(), key=lambda kv: (-len(kv[1]), sorted(kv[1])[0])):
        base = sorted(pages)[0] if len(pages) == 1 else f"shared-{sorted(pages)[0]}"
        name = base
        n = 2
        while name in names.values():
            name = f"{base}-{n}"
            n += 1
        names[h] = name
        write(f"src/styles/{name}.css", styles_by_hash[h].strip("\n") + "\n")

    # Record, per page, which stylesheet each language currently uses.
    for slug, entry in registry.items():
        used = {lang: names[h] for (s, lang), h in style_usage.items() if s == slug}
        if not used:
            continue
        base = used.get(SITE["default_language"]) or next(iter(used.values()))
        entry["style"] = base
        divergent = {lang: nm for lang, nm in used.items() if nm != base}
        if divergent:
            entry["style_overrides"] = divergent

    # ---- faction icon data -------------------------------------------------
    factions = extract_factions()
    write(
        "src/factions.yml",
        "# Faction icon data, generated by tools/extract.py.\n"
        "# 'aliases' lists every spelling of a faction name that appears in that\n"
        "# language's own text; the icon script matches against all of them.\n"
        + yaml.safe_dump(factions, allow_unicode=True, sort_keys=False, width=100),
    )

    # ---- write registry + i18n --------------------------------------------
    ordered = {slug: registry[slug] for slug in sorted(registry)}
    write(
        "src/pages.yml",
        "# Generated by tools/extract.py - page registry.\n"
        "# 'style_overrides' records languages whose CSS drifted from English;\n"
        "# they are unified in a later step.\n"
        + yaml.safe_dump(ordered, allow_unicode=True, sort_keys=False, width=100),
    )

    for lang, data in i18n.items():
        ordered_i18n = {slug: data[slug] for slug in sorted(data)}
        write(
            f"src/i18n/{lang}.yml",
            f"# Translated page strings for '{lang}'. Generated by tools/extract.py.\n"
            + yaml.safe_dump(ordered_i18n, allow_unicode=True, sort_keys=False, width=100),
        )

    # ---- report ------------------------------------------------------------
    print(f"pages      : {len(registry)}")
    print(f"languages  : {len(LANGS)}")
    print(f"fragments  : {sum(1 for _ in os.walk(os.path.join(SRC, 'content')) for _ in _[2])}")
    print(f"stylesheets: {len(names)} distinct (from {len(style_usage)} inline blocks)")
    print(f"warnings   : {len(warnings)}")
    for w in warnings[:40]:
        print("   ", w)
    if len(warnings) > 40:
        print(f"    ... and {len(warnings) - 40} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
