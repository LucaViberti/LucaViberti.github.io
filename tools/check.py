#!/usr/bin/env python3
"""
Integrity checks over the generated site.

These are the checks that would have caught the problems found while moving the
site to src/: portraits pointing at files that do not exist, pages missing from
a language, hreflang links that do not come back, and pages whose content is
much shorter in one language than in English.

    python3 tools/check.py          run everything, exit non-zero on failure
    python3 tools/check.py --warn   report but always exit 0
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build as B  # noqa: E402

ROOT = B.ROOT


def page_html(rel: str) -> str | None:
    """A page's markup with HTML comments removed.

    Commented-out blocks are not rendered, so links inside them are not broken
    links - beginners.html keeps a disabled donation block that would otherwise
    be reported in all seven languages.
    """
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)


def all_pages() -> list[tuple[str, str, str]]:
    out = []
    for slug in sorted(B.PAGES):
        for lang in B.LANGS:
            out.append((lang, slug, B.rel_path(lang, slug)))
    return out


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------


def check_assets(problems: list[str]) -> None:
    """Every image and stylesheet a page points at must exist on disk."""
    seen: set[str] = set()
    for _, _, rel in all_pages():
        html = page_html(rel)
        if html is None:
            continue
        refs = re.findall(r'(?:src|href)="(/[^"]+\.(?:jpe?g|png|svg|css|js|ico|webp))"', html)
        for ref in refs:
            if ref in seen:
                continue
            seen.add(ref)
            if not os.path.exists(os.path.join(ROOT, ref.lstrip("/"))):
                problems.append(f"missing file {ref} (referenced by {rel})")


def check_internal_links(problems: list[str]) -> None:
    """Relative links between pages must resolve to a file that exists."""
    for _, _, rel in all_pages():
        html = page_html(rel)
        if html is None:
            continue
        base = os.path.dirname(rel)
        for href in re.findall(r'href="([^"#?]+\.html)(?:[#?][^"]*)?"', html):
            if href.startswith(("http://", "https://", "//", "mailto:")):
                continue
            target = href.lstrip("/") if href.startswith("/") else os.path.normpath(
                os.path.join(base, href)
            )
            if not os.path.exists(os.path.join(ROOT, target)):
                problems.append(f"broken link {href} on {rel}")


def check_pages_present(problems: list[str]) -> None:
    for lang, slug, rel in all_pages():
        if not os.path.exists(os.path.join(ROOT, rel)):
            problems.append(f"page missing: {rel}")


def check_hreflang(problems: list[str]) -> None:
    """
    Every page must advertise all languages, and each alternate must point at a
    page that exists and links back. A one-way hreflang is ignored by search
    engines, which is how Traditional Chinese ended up invisible before.
    """
    expected = {B.LANGS[l]["hreflang"] for l in B.SITE["hreflang_order"]}
    for lang, slug, rel in all_pages():
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        found = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', html))
        missing = expected - set(found)
        if missing:
            problems.append(f"{rel}: missing hreflang {sorted(missing)}")
        if "x-default" not in found:
            problems.append(f"{rel}: missing hreflang x-default")
        if not re.search(r'<link rel="canonical"', html):
            problems.append(f"{rel}: no canonical")
        for tag, url in found.items():
            local = urlparse(url).path.lstrip("/")
            if local and not os.path.exists(os.path.join(ROOT, local)):
                problems.append(f"{rel}: hreflang {tag} points at missing {local}")


def check_lang_attribute(problems: list[str]) -> None:
    for lang, slug, rel in all_pages():
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            head = fh.read(400)
        m = re.search(r'<html lang="([^"]*)"', head)
        want = B.LANGS[lang]["html_lang"]
        if not m:
            problems.append(f"{rel}: no lang attribute")
        elif m.group(1) != want:
            problems.append(f"{rel}: lang is {m.group(1)!r}, expected {want!r}")


def check_translation_coverage(problems: list[str], warn: list[str]) -> None:
    """
    Flag pages that are much shorter than the same page in other languages.

    Comparing directly against English does not work: Japanese and Chinese
    write the same meaning in far fewer characters and without spaces, so every
    CJK page looks "short". Instead, work out how long each language's pages
    usually are relative to English, then flag the pages that fall well below
    that language's own norm. This is what would have surfaced the Korean cost
    tables - four sections missing - without anyone diffing files.
    """
    def visible_length(rel: str) -> int:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            return 0
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        body = re.search(r"<main.*?</main>", html, re.S)
        text = body.group(0) if body else html
        text = re.sub(r"<(script|style).*?</\1>", "", text, flags=re.S)
        return len(re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", text)))

    english = {slug: visible_length(B.rel_path(B.DEFAULT, slug)) for slug in B.PAGES}
    slugs = [s for s, n in english.items() if n >= 400]

    for lang in B.LANGS:
        if lang == B.DEFAULT:
            continue
        ratios = {}
        for slug in slugs:
            n = visible_length(B.rel_path(lang, slug))
            ratios[slug] = n / english[slug]
        if not ratios:
            continue
        ordered = sorted(ratios.values())
        median = ordered[len(ordered) // 2]
        for slug, ratio in sorted(ratios.items()):
            # Half of what this language normally produces means content is
            # missing, not just a more compact script.
            if ratio < median * 0.5:
                warn.append(
                    f"{B.rel_path(lang, slug)}: {ratio:.0%} the length of English, "
                    f"but {lang} pages are usually {median:.0%} - looks incomplete"
                )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--warn", action="store_true", help="never exit non-zero")
    args = ap.parse_args()

    problems: list[str] = []
    warn: list[str] = []

    check_pages_present(problems)
    check_assets(problems)
    check_internal_links(problems)
    check_hreflang(problems)
    check_lang_attribute(problems)
    check_translation_coverage(problems, warn)

    pages = len(B.PAGES) * len(B.LANGS)
    print(f"checked {pages} pages across {len(B.LANGS)} languages")

    if warn:
        print(f"\n{len(warn)} warning(s):")
        for w in warn:
            print("   ", w)

    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print("   ", p)
        return 0 if args.warn else 1

    print("no problems found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
