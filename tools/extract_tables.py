#!/usr/bin/env python3
"""
One-time migration of the Cost Tables page into data.

tips.html is ~285 KB of hand-written table markup, copied into all seven
languages. 55% of it is the same ten inline style strings repeated on 3,883
cells, and the numbers themselves - which are language independent - were
maintained separately in each copy. They had already fallen out of sync: the
Korean page is missing four whole sections (Troop Skin, Rune, Pet, Villager),
597 rows of data.

This reads the English page as the structure and the numbers, reads the other
languages to learn how each piece of text was translated, and writes:

    src/data/tips.yml          sections, tables and cells (one copy, shared)
    src/i18n/terms/<lang>.yml  English term -> translation

After this the page is generated for every language from the same numbers, so
a cost can only ever be wrong in all languages at once, never in one.

Run from the repository root:  python3 tools/extract_tables.py
"""

from __future__ import annotations

import os
import re
import sys
from collections import OrderedDict

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")

with open(os.path.join(SRC, "site.yml"), encoding="utf-8") as fh:
    SITE = yaml.safe_load(fh)
LANGS = list(SITE["languages"])
DEFAULT = SITE["default_language"]

# The ten inline style strings, expressed as reusable class tokens.
STYLE_TOKENS = {
    "text-align:center": "tc",
    "vertical-align:bottom": "vb",
    "vertical-align:center": "vc",
    "font-weight:bold": "fb",
    "white-space:normal": "wn",
}

# Most cells look the same; only store a class when it differs from these.
DEFAULT_CLASS = {
    "thead-th": "th-top fb tc vb",
    "tbody-th": "th-left fb vb",
    "tbody-td": "tc vb",
}


def read(rel: str) -> str:
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def classes_of(attrs: str) -> str:
    """Normalise a cell's class= and style= into a single class string."""
    out: list[str] = []
    m = re.search(r'class="([^"]*)"', attrs)
    if m:
        out.extend(m.group(1).split())
    m = re.search(r'style="([^"]*)"', attrs)
    if m:
        for decl in m.group(1).split(";"):
            decl = re.sub(r"\s+", "", decl)
            if not decl:
                continue
            token = STYLE_TOKENS.get(decl)
            if token:
                if token not in out:
                    out.append(token)
            else:
                # Unknown declaration - keep it verbatim so nothing is lost.
                out.append(f"style:{decl}")
    return " ".join(out)


CELL_RE = re.compile(r"<(t[dh])([^>]*)>(.*?)</\1>", re.S)
ROW_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)


def parse_rows(chunk: str, kind: str) -> list[list[dict]]:
    rows = []
    for rm in ROW_RE.finditer(chunk):
        cells = []
        for cm in CELL_RE.finditer(rm.group(1)):
            tag, attrs, inner = cm.group(1), cm.group(2), cm.group(3)
            cell = {
                "tag": tag,
                "text": inner.strip(),
                "cls": classes_of(attrs),
            }
            for attr in ("colspan", "rowspan"):
                m = re.search(rf'{attr}="(\d+)"', attrs)
                if m:
                    cell[attr] = int(m.group(1))
            cells.append(cell)
        rows.append(cells)
    return rows


TABLE_RE = re.compile(
    r'<table class="th-table" id="([^"]+)">\s*'
    r"(?:<thead>(.*?)</thead>)?\s*"
    r"(?:<tbody>(.*?)</tbody>)?\s*</table>",
    re.S,
)


def parse_page(html: str) -> "OrderedDict[str, dict]":
    """section id -> {title, switcher/tabs, tables: {id: {...}}}"""
    sections: "OrderedDict[str, dict]" = OrderedDict()
    for sm in re.finditer(
        r'<section id="([^"]+)" class="th-section">(.*?)</section>', html, re.S
    ):
        sid, body = sm.group(1), sm.group(2)
        sec: dict = {"id": sid}

        m = re.search(r"<h2>(.*?)</h2>", body, re.S)
        sec["title"] = m.group(1).strip() if m else sid

        # optional server-generation <select>
        sw = re.search(
            r'<div class="th-switcher">\s*<label for="([^"]+)">(.*?)</label>'
            r'\s*<select id="[^"]+">(.*?)</select>',
            body,
            re.S,
        )
        if sw:
            options = [
                {
                    "value": om.group(1),
                    "label": om.group(3).strip(),
                    **({"selected": True} if om.group(2) else {}),
                }
                for om in re.finditer(
                    r'<option value="([^"]*)"( selected)?>(.*?)</option>', sw.group(3), re.S
                )
            ]
            sec["switcher"] = {
                "id": sw.group(1),
                "label": sw.group(2).strip(),
                "options": options,
            }

        # optional tab strip
        tabs = re.search(r'<div class="th-tabs" role="tablist">(.*?)</div>', body, re.S)
        if tabs:
            sec["tabs"] = [
                {
                    "target": tm.group(2),
                    "label": tm.group(3).strip(),
                    **({"active": True} if "th-active" in tm.group(1) else {}),
                }
                for tm in re.finditer(
                    r'<button class="th-tab([^"]*)" data-target="([^"]+)">(.*?)</button>',
                    tabs.group(1),
                    re.S,
                )
            ]

        # wrappers tell us the id and initial visibility of each table
        wraps = {}
        for wm in re.finditer(r'<div id="(wrap-[^"]+)" class="th-wrap([^"]*)"', body):
            wraps[wm.group(1)] = "th-visible" in wm.group(2)

        # caption shown in the table header bar
        captions = dict(
            re.findall(
                r'aria-controls="([^"]+)-body"[^>]*>\+</button>\s*<strong>(.*?)</strong>',
                body,
                re.S,
            )
        )

        tables: "OrderedDict[str, dict]" = OrderedDict()
        for tm in TABLE_RE.finditer(body):
            tid = tm.group(1)
            wrap = f"wrap-{tid}" if f"wrap-{tid}" in wraps else None
            if wrap is None:
                # castle tables use a shorter wrapper id (wrap-castle-base)
                for w in wraps:
                    if tid.endswith(w[len("wrap-"):]):
                        wrap = w
                        break
            tables[tid] = {
                "id": tid,
                "wrap": wrap,
                "visible": wraps.get(wrap, False),
                "caption": captions.get(tid, "").strip(),
                "thead": parse_rows(tm.group(2) or "", "thead"),
                "tbody": parse_rows(tm.group(3) or "", "tbody"),
            }
        sec["tables"] = tables
        sections[sid] = sec
    return sections


# ---------------------------------------------------------------------------
# glossary
# ---------------------------------------------------------------------------

NUMERIC = re.compile(r"^[\d.,\s]*[a-z]?$", re.I)
ENTITY_ONLY = re.compile(r"^(?:&#\d+;|\s)*$")


def translatable(text: str) -> bool:
    """A cell holds a term worth translating if it isn't a number or a symbol."""
    t = text.strip()
    if not t or t == "-":
        return False
    if NUMERIC.match(t) or ENTITY_ONLY.match(t):
        return False
    return True


def collect_terms(en: dict, other: dict) -> dict[str, str]:
    """Align two parses cell by cell and record how each term was translated."""
    pairs: dict[str, str] = {}

    def note(a: str, b: str) -> None:
        a, b = a.strip(), b.strip()
        if a and b and translatable(a):
            pairs.setdefault(a, b)

    for sid, sec in en.items():
        osec = other.get(sid)
        if not osec:
            continue
        note(sec["title"], osec.get("title", ""))
        if "switcher" in sec and "switcher" in osec:
            note(sec["switcher"]["label"], osec["switcher"]["label"])
            for a, b in zip(sec["switcher"]["options"], osec["switcher"]["options"]):
                note(a["label"], b["label"])
        if "tabs" in sec and "tabs" in osec:
            for a, b in zip(sec["tabs"], osec["tabs"]):
                note(a["label"], b["label"])
        for tid, tbl in sec["tables"].items():
            otbl = osec["tables"].get(tid)
            if not otbl:
                continue
            note(tbl["caption"], otbl["caption"])
            for part in ("thead", "tbody"):
                for arow, brow in zip(tbl[part], otbl[part]):
                    for acell, bcell in zip(arow, brow):
                        note(acell["text"], bcell["text"])
    return pairs


# ---------------------------------------------------------------------------
# compaction
# ---------------------------------------------------------------------------


def compact_cell(cell: dict, part: str) -> object:
    """Plain string when the cell is an ordinary one; dict only when it isn't."""
    key = f"{part}-{cell['tag']}"
    out: dict = {}
    if cell["cls"] != DEFAULT_CLASS.get(key, ""):
        out["cls"] = cell["cls"]
    if cell["tag"] == "th" and part == "tbody" and "cls" not in out:
        pass
    for attr in ("colspan", "rowspan"):
        if attr in cell:
            out[attr[0]] = cell[attr]
    expected_tag = "th" if (part == "thead" or not out and cell["tag"] == "th") else "td"
    if cell["tag"] != ("th" if part == "thead" else "td"):
        out["th"] = True
    if not out:
        return cell["text"]
    out["t"] = cell["text"]
    return out


def compact(sections: "OrderedDict[str, dict]") -> list:
    out = []
    for sid, sec in sections.items():
        s: dict = {"id": sid, "title": sec["title"]}
        if "switcher" in sec:
            s["switcher"] = sec["switcher"]
        if "tabs" in sec:
            s["tabs"] = sec["tabs"]
        s["tables"] = []
        for tid, tbl in sec["tables"].items():
            s["tables"].append(
                {
                    "id": tid,
                    "wrap": tbl["wrap"],
                    "visible": tbl["visible"],
                    "caption": tbl["caption"],
                    "thead": [[compact_cell(c, "thead") for c in r] for r in tbl["thead"]],
                    "tbody": [[compact_cell(c, "tbody") for c in r] for r in tbl["tbody"]],
                }
            )
        out.append(s)
    return out


def main() -> int:
    en_html = read("src/content/en/tips.html")
    en = parse_page(en_html)

    n_tables = sum(len(s["tables"]) for s in en.values())
    n_rows = sum(
        len(t["thead"]) + len(t["tbody"]) for s in en.values() for t in s["tables"].values()
    )
    print(f"English: {len(en)} sections, {n_tables} tables, {n_rows} rows")

    # glossary per language
    os.makedirs(os.path.join(SRC, "i18n", "terms"), exist_ok=True)
    for lang in LANGS:
        if lang == DEFAULT:
            continue
        path = f"src/content/{lang}/tips.html"
        if not os.path.exists(os.path.join(ROOT, path)):
            continue
        terms = collect_terms(en, parse_page(read(path)))
        same = sum(1 for k, v in terms.items() if k == v)
        out = OrderedDict(sorted(terms.items()))
        with open(os.path.join(SRC, "i18n", "terms", f"{lang}.yml"), "w", encoding="utf-8") as fh:
            fh.write(
                f"# Cost-table terms for '{lang}': English term -> translation.\n"
                f"# Entries where the two sides are identical are terms this language\n"
                f"# keeps in English (proper nouns, rarity names, and so on).\n"
            )
            fh.write(yaml.safe_dump(dict(out), allow_unicode=True, sort_keys=True, width=200))
        print(f"  {lang}: {len(terms)} terms ({same} kept in English)")

    data = compact(en)
    os.makedirs(os.path.join(SRC, "data"), exist_ok=True)
    with open(os.path.join(SRC, "data", "tips.yml"), "w", encoding="utf-8") as fh:
        fh.write(
            "# Cost tables, generated by tools/extract_tables.py.\n"
            "# The numbers live here once and are shared by every language; the text\n"
            "# is translated through src/i18n/terms/<lang>.yml.\n"
            "#\n"
            "# A cell is written as a plain string when it is an ordinary cell, and as\n"
            "# a mapping only when it needs something extra:\n"
            "#     t   the text\n"
            "#     th  true if it is a header cell\n"
            "#     cls class list, when it differs from the default for its position\n"
            "#     c/r colspan / rowspan\n"
        )
        fh.write(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=200))

    size = os.path.getsize(os.path.join(SRC, "data", "tips.yml"))
    print(f"wrote src/data/tips.yml ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
