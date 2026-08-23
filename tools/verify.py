#!/usr/bin/env python3
"""
Safety net for the move to generated pages.

Renders every page from src/ and compares it against the file currently on
disk, ignoring formatting and looking only at things a reader or a search
engine would notice:

    * the visible text of the page body
    * every link target and image source
    * the heading outline
    * title, meta description, canonical, and the set of hreflang links

Anything that differs is printed. The refactor is only safe if every reported
difference is one we deliberately introduced.

    python3 tools/verify.py            summary
    python3 tools/verify.py -v         list every differing page
    python3 tools/verify.py --show P   full detail for one page (e.g. ko/html/league.html)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build as B  # noqa: E402

ROOT = B.ROOT

# Tags whose text is not shown to the reader.
INVISIBLE = {"script", "style", "template"}


class Extract(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text: list[str] = []
        self.links: list[str] = []
        self.images: list[str] = []
        self.headings: list[str] = []
        self.meta: dict[str, str] = {}
        self.hreflang: dict[str, str] = {}
        self._skip = 0
        self._heading: str | None = None
        self._in_body = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in INVISIBLE:
            self._skip += 1
        if tag == "body":
            self._in_body = True
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "img" and a.get("src"):
            self.images.append(a["src"])
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._heading = ""
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key in ("description", "og:title", "og:description", "og:url", "og:locale"):
                self.meta[key] = a.get("content", "")
        if tag == "link":
            rel = (a.get("rel") or "").lower() if isinstance(a.get("rel"), str) else ""
            if "canonical" in rel:
                self.meta["canonical"] = a.get("href", "")
            if "alternate" in rel and a.get("hreflang"):
                self.hreflang[a["hreflang"]] = a.get("href", "")

    def handle_endtag(self, tag):
        if tag in INVISIBLE and self._skip:
            self._skip -= 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._heading is not None:
            h = re.sub(r"\s+", " ", self._heading).strip()
            if h:
                self.headings.append(h)
            self._heading = None

    def handle_data(self, data):
        if self._skip:
            return
        if self._heading is not None:
            self._heading += data
        if self._in_body:
            self.text.append(data)

    # -- results ----------------------------------------------------------
    def title(self) -> str:
        return self.meta.get("og:title", "")

    def body_text(self) -> str:
        return re.sub(r"\s+", " ", "".join(self.text)).strip()


def parse(html: str) -> Extract:
    p = Extract()
    p.feed(html)
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    if m:
        p.meta["title"] = re.sub(r"\s+", " ", m.group(1)).strip()
    return p


def compare(old_html: str, new_html: str) -> list[str]:
    a, b = parse(old_html), parse(new_html)
    out: list[str] = []

    if a.body_text() != b.body_text():
        ta, tb = a.body_text(), b.body_text()
        # locate the first divergence to make the report actionable
        i = 0
        while i < min(len(ta), len(tb)) and ta[i] == tb[i]:
            i += 1
        out.append(
            f"BODY TEXT differs at char {i}: "
            f"...{ta[max(0,i-45):i+45]!r} -> ...{tb[max(0,i-45):i+45]!r}"
        )

    if a.links != b.links:
        lost = [x for x in a.links if x not in b.links]
        added = [x for x in b.links if x not in a.links]
        if lost:
            out.append(f"LINKS removed: {lost[:6]}")
        if added:
            out.append(f"LINKS added: {added[:6]}")
        if not lost and not added:
            out.append("LINKS reordered")

    if a.images != b.images:
        lost = [x for x in a.images if x not in b.images]
        added = [x for x in b.images if x not in a.images]
        if lost:
            out.append(f"IMAGES removed: {lost[:6]}")
        if added:
            out.append(f"IMAGES added: {added[:6]}")

    if a.headings != b.headings:
        out.append(f"HEADINGS differ: {len(a.headings)} -> {len(b.headings)}")

    for key in ("title", "description", "canonical"):
        if a.meta.get(key) != b.meta.get(key):
            out.append(f"{key.upper()}: {a.meta.get(key)!r} -> {b.meta.get(key)!r}")

    if set(a.hreflang) != set(b.hreflang):
        miss = sorted(set(b.hreflang) - set(a.hreflang))
        gone = sorted(set(a.hreflang) - set(b.hreflang))
        if miss:
            out.append(f"HREFLANG added: {miss}")
        if gone:
            out.append(f"HREFLANG removed: {gone}")

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--show", metavar="PATH", help="full detail for one page")
    args = ap.parse_args()

    clean, differing, missing = 0, [], []

    for slug, entry in sorted(B.PAGES.items()):
        for lang in B.LANGS:
            rel = B.rel_path(lang, slug)
            path = os.path.join(ROOT, rel)
            if not os.path.exists(path):
                missing.append(rel)
                continue
            with open(path, encoding="utf-8") as fh:
                old = fh.read()
            new = B.render_page(lang, slug, entry)

            if args.show and args.show != rel:
                continue

            diffs = compare(old, new)
            if diffs:
                differing.append((rel, diffs))
            else:
                clean += 1

            if args.show == rel:
                print(f"=== {rel} ===")
                print("\n".join(f"  {d}" for d in diffs) or "  identical in content")
                return 0

    if args.show:
        print(f"no such page: {args.show}")
        return 1

    print(f"content-identical : {clean}")
    print(f"with differences  : {len(differing)}")
    if missing:
        print(f"missing on disk   : {len(missing)}")

    # Group differences by kind so the report stays readable.
    kinds: dict[str, list[str]] = {}
    for rel, diffs in differing:
        for d in diffs:
            kinds.setdefault(d.split(":")[0].split(" at ")[0], []).append(rel)
    if kinds:
        print("\nby kind:")
        for kind, pages in sorted(kinds.items(), key=lambda kv: -len(kv[1])):
            print(f"  {len(pages):4}  {kind}")

    if args.verbose:
        print()
        for rel, diffs in differing:
            print(f"--- {rel}")
            for d in diffs:
                print(f"      {d}")

    return 1 if differing else 0


if __name__ == "__main__":
    sys.exit(main())
