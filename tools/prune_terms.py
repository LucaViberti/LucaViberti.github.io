#!/usr/bin/env python3
"""
Drop glossary entries for terms the tables no longer contain.

Glossaries were seeded from the pages as they were, so they picked up entries
for text that has since been corrected - the mojibake medal emoji left five
dead keys in every language. Removing them keeps the files an accurate picture
of what still needs translating.

Run from the repository root:  python3 tools/prune_terms.py
"""

from __future__ import annotations

import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build as B  # noqa: E402

TERMS = os.path.join(B.SRC, "i18n", "terms")


def terms_in_use() -> set[str]:
    used: set[str] = set()

    def note(value) -> None:
        if isinstance(value, str) and value.strip():
            used.add(value.strip())

    for section in B.table_data():
        note(section.get("title"))
        switcher = section.get("switcher")
        if switcher:
            note(switcher.get("label"))
            for option in switcher.get("options", []):
                note(option.get("label"))
        for tab in section.get("tabs") or []:
            note(tab.get("label"))
        for table in section.get("tables", []):
            note(table.get("caption"))
            for part in ("thead", "tbody"):
                for row in table.get(part, []):
                    for cell in row:
                        note(cell if isinstance(cell, str) else cell.get("t"))
    return used


def main() -> int:
    used = terms_in_use()
    for fn in sorted(os.listdir(TERMS)):
        if not fn.endswith(".yml"):
            continue
        lang = fn[:-4]
        path = os.path.join(TERMS, fn)
        with open(path, encoding="utf-8") as fh:
            glossary = yaml.safe_load(fh) or {}
        dead = [k for k in glossary if k not in used]
        if not dead:
            print(f"{lang}: nothing to prune ({len(glossary)} entries)")
            continue
        for k in dead:
            del glossary[k]
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(
                f"# Cost-table terms for '{lang}': English term -> translation.\n"
                "# A term with no entry here falls back to English, so the table is\n"
                "# never missing a row - only ever untranslated.\n"
            )
            fh.write(yaml.safe_dump(glossary, allow_unicode=True, sort_keys=True, width=200))
        print(f"{lang}: pruned {len(dead)} dead entr(ies), {len(glossary)} left")
    return 0


if __name__ == "__main__":
    sys.exit(main())
