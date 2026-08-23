#!/usr/bin/env python3
"""
Collapse the per-language stylesheet drift onto a single sheet per page.

Every page used to inline its own <style> block, copied into each language.
Over time those copies diverged: some translations had CSS comments machine
translated, some lost whole rule blocks (Traditional Chinese lost all the
donation-button styling), and a few gained polish English never got.

Taking the English sheet verbatim would silently drop that polish, so instead
this merges: English is the base, and any declaration that exists only in a
translation is appended in a clearly marked block. Nothing is lost, and after
this every language renders from the same stylesheet.

Run after tools/extract.py, from the repository root.
"""

from __future__ import annotations

import os
import re
import sys
from collections import OrderedDict

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLES = os.path.join(ROOT, "src", "styles")
PAGES = os.path.join(ROOT, "src", "pages.yml")

# Stylesheets used by several pages get an auto-generated name from whichever
# page sorted first, which reads misleadingly ("shared-horde.css" was the sheet
# for League and Nature). Name the known groups after what they actually are.
SHARED_NAMES = [
    ({"league", "nature", "horde"}, "faction"),
    (
        {
            "adventure",
            "arms-race",
            "events",
            "exclusive-gear",
            "guildboss",
            "kingdom",
            "relic",
        },
        "simple-page",
    ),
]


def read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def declarations(css: str) -> "OrderedDict[tuple, str]":
    """Map (normalised-selector, property) -> value, last declaration winning."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out: OrderedDict[tuple, str] = OrderedDict()
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css, re.S):
        raw = re.sub(r"\s+", " ", m.group(1)).strip()
        if raw.startswith("@"):
            continue  # at-rules (media queries) are compared as whole blocks
        key = tuple(sorted(s.strip() for s in raw.split(",") if s.strip()))
        for decl in m.group(2).split(";"):
            if ":" not in decl:
                continue
            prop, val = decl.split(":", 1)
            out[(key, prop.strip().lower())] = re.sub(r"\s+", " ", val).strip()
    return out


def selector_text(css: str, key: tuple) -> str:
    """Recover the selector as written, for readable output."""
    for m in re.finditer(r"([^{}]+)\{", css):
        raw = re.sub(r"\s+", " ", m.group(1)).strip()
        if raw.startswith("@"):
            continue
        if tuple(sorted(s.strip() for s in raw.split(",") if s.strip())) == key:
            return raw
    return ", ".join(key)


def main() -> int:
    registry = yaml.safe_load(read(PAGES))
    merged_pages = 0
    added_rules = 0
    dropped: set[str] = set()

    for slug, entry in registry.items():
        overrides = entry.pop("style_overrides", None)
        if not overrides:
            continue

        base_name = entry["style"]
        base_path = os.path.join(STYLES, f"{base_name}.css")
        base_css = read(base_path)
        base_decls = declarations(base_css)

        # Collect declarations present in a translation but absent from English.
        extra: "OrderedDict[tuple, list]" = OrderedDict()
        for lang, name in sorted(overrides.items()):
            path = os.path.join(STYLES, f"{name}.css")
            if not os.path.exists(path):
                continue
            other_css = read(path)
            for key, val in declarations(other_css).items():
                if key in base_decls:
                    continue
                sel = selector_text(other_css, key[0])
                extra.setdefault((key, sel), []).append((key[1], val, lang))
            dropped.add(name)

        if extra:
            by_selector: "OrderedDict[str, list]" = OrderedDict()
            langs: set[str] = set()
            for (key, sel), items in extra.items():
                for prop, val, lang in items:
                    by_selector.setdefault(sel, [])
                    if (prop, val) not in by_selector[sel]:
                        by_selector[sel].append((prop, val))
                    langs.add(lang)

            block = [
                "",
                "/* --------------------------------------------------------------",
                "   Merged in from the {} stylesheet(s) during the move to shared".format(
                    "/".join(sorted(langs))
                ),
                "   stylesheets: these declarations existed only in a translated copy",
                "   of this page, so keeping them preserves that styling for every",
                "   language instead of silently dropping it.",
                "   -------------------------------------------------------------- */",
            ]
            for sel, decls in by_selector.items():
                block.append(f"{sel} {{")
                for prop, val in decls:
                    block.append(f"  {prop}: {val};")
                    added_rules += 1
                block.append("}")
            base_css = base_css.rstrip("\n") + "\n" + "\n".join(block) + "\n"
            with open(base_path, "w", encoding="utf-8") as fh:
                fh.write(base_css)

        merged_pages += 1

    # ---- collapse sheets that are equivalent apart from formatting ---------
    # e.g. the three faction pages had byte-different sheets that differed only
    # by a space after a comma in one 'transition' value.
    signatures: dict[tuple, str] = {}
    collapsed = 0
    for slug, entry in registry.items():
        name = entry.get("style")
        if not name:
            continue
        path = os.path.join(STYLES, f"{name}.css")
        if not os.path.exists(path):
            continue
        css = read(path)
        sig = tuple(sorted((k, re.sub(r"\s+", "", v)) for k, v in declarations(css).items()))
        canonical = signatures.get(sig)
        if canonical is None:
            signatures[sig] = name
        elif canonical != name:
            entry["style"] = canonical
            dropped.add(name)
            collapsed += 1

    # ---- give shared sheets a name that says what they are -----------------
    for pages, nice in SHARED_NAMES:
        users = {s for s, e in registry.items() if e.get("style") and s in pages}
        current = {registry[s]["style"] for s in users}
        if len(current) != 1:
            continue
        old = current.pop()
        if old == nice:
            continue
        src_path = os.path.join(STYLES, f"{old}.css")
        if not os.path.exists(src_path):
            continue
        os.rename(src_path, os.path.join(STYLES, f"{nice}.css"))
        for s, e in registry.items():
            if e.get("style") == old:
                e["style"] = nice
        dropped.discard(old)

    # Remove stylesheets no longer referenced by any page.
    still_used = {e["style"] for e in registry.values() if e.get("style")}
    removed = 0
    for name in sorted(dropped):
        if name in still_used:
            continue
        path = os.path.join(STYLES, f"{name}.css")
        if os.path.exists(path):
            os.remove(path)
            removed += 1

    header = (
        "# Generated by tools/extract.py, then unified by tools/unify_styles.py.\n"
        "# One stylesheet per page, shared by every language.\n"
    )
    with open(PAGES, "w", encoding="utf-8") as fh:
        fh.write(header + yaml.safe_dump(registry, allow_unicode=True, sort_keys=False, width=100))

    remaining = len([f for f in os.listdir(STYLES) if f.endswith(".css")])
    print(f"pages unified      : {merged_pages}")
    print(f"declarations merged: {added_rules}")
    print(f"stylesheets removed: {removed}")
    print(f"stylesheets left   : {remaining}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
