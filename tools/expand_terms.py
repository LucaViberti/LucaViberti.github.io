#!/usr/bin/env python3
"""
Translate the patterned cost-table terms.

Most of the glossary is ordinary vocabulary, but a few hundred entries are the
same phrase with a number in it - "Level 34", "3 same + 15 rare", "2 Universal
Shard". Translating those by hand is busywork and easy to get inconsistent, so
they are generated from a rule per language instead.

    python3 tools/expand_terms.py           update every language
    python3 tools/expand_terms.py de vi     update only these
"""

from __future__ import annotations

import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMS = os.path.join(ROOT, "src", "i18n", "terms")

# For each language, a list of (pattern, replacement). \1, \2 are the numbers.
# A language missing from this table keeps these terms in English, which is the
# established convention for Japanese, Traditional and Simplified Chinese.
RULES: dict[str, list[tuple[str, str]]] = {
    "de": [
        (r"^Level (\d+)$", r"Stufe \1"),
        (r"^Lv\.? ?(\d+)$", r"Stufe \1"),
        (r"^Hero Lv\.? ?(\d+)$", r"Heldenstufe \1"),
        (r"^Brilliance Level (\d+)$", r"Brillanzstufe \1"),
        (r"^(\d+) Universal Shard$", r"\1 universeller Splitter"),
        (r"^(\d+) same \+ (\d+) rare$", r"\1 gleiche + \2 seltene"),
        (r"^(\d+) same$", r"\1 gleiche"),
        (r"^(\d+) rare$", r"\1 seltene"),
        (r"^(\d+) Legendary$", r"\1 legendäre"),
        (r"^(\d+) Mythic$", r"\1 mythische"),
        (r"^\$ Estimated$", "$ geschätzt"),
    ],
    "vi": [
        (r"^Level (\d+)$", r"Cấp \1"),
        (r"^Lv\.? ?(\d+)$", r"Cấp \1"),
        (r"^Hero Lv\.? ?(\d+)$", r"Cấp anh hùng \1"),
        (r"^Brilliance Level (\d+)$", r"Cấp Rực rỡ \1"),
        (r"^(\d+) Universal Shard$", r"\1 Mảnh vạn năng"),
        (r"^(\d+) same \+ (\d+) rare$", r"\1 cùng loại + \2 hiếm"),
        (r"^(\d+) same$", r"\1 cùng loại"),
        (r"^(\d+) rare$", r"\1 hiếm"),
        (r"^(\d+) Legendary$", r"\1 Huyền thoại"),
        (r"^(\d+) Mythic$", r"\1 Thần thoại"),
        (r"^\$ Estimated$", "$ ước tính"),
    ],
    "ko": [
        (r"^Level (\d+)$", r"레벨 \1"),
        (r"^Lv\.? ?(\d+)$", r"레벨 \1"),
        (r"^Hero Lv\.? ?(\d+)$", r"영웅 레벨 \1"),
        (r"^Brilliance Level (\d+)$", r"광휘 레벨 \1"),
        (r"^(\d+) Universal Shard$", r"범용 조각 \1개"),
        (r"^(\d+) same \+ (\d+) rare$", r"동일 \1개 + 희귀 \2개"),
        (r"^(\d+) same$", r"동일 \1개"),
        (r"^(\d+) rare$", r"희귀 \1개"),
        (r"^(\d+) Legendary$", r"전설 \1개"),
        (r"^(\d+) Mythic$", r"신화 \1개"),
        (r"^\$ Estimated$", "$ 예상"),
    ],
}


def terms_in_use() -> set[str]:
    """Every piece of text the tables render, so patterned terms a glossary has
    never seen get an entry too rather than only the ones already listed."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build as B  # noqa: PLC0415

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
    wanted = sys.argv[1:] or sorted(RULES)
    used = terms_in_use()
    for lang in wanted:
        rules = RULES.get(lang)
        if not rules:
            print(f"{lang}: no rules defined, skipped")
            continue
        path = os.path.join(TERMS, f"{lang}.yml")
        with open(path, encoding="utf-8") as fh:
            glossary = yaml.safe_load(fh) or {}

        changed = 0
        for term in sorted(used):
            # Leave anything already translated alone.
            if glossary.get(term, term) != term:
                continue
            for pattern, replacement in rules:
                if re.match(pattern, term):
                    glossary[term] = re.sub(pattern, replacement, term)
                    changed += 1
                    break

        with open(path, "w", encoding="utf-8") as fh:
            fh.write(
                f"# Cost-table terms for '{lang}': English term -> translation.\n"
                "# A term with no entry here falls back to English, so the table is\n"
                "# never missing a row - only ever untranslated.\n"
            )
            fh.write(yaml.safe_dump(glossary, allow_unicode=True, sort_keys=True, width=200))

        still = sum(1 for k, v in glossary.items() if k == v)
        print(f"{lang}: translated {changed} patterned term(s), {still} left in English")
    return 0


if __name__ == "__main__":
    sys.exit(main())
