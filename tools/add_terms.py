#!/usr/bin/env python3
"""
Merge translations into a cost-table glossary.

    python3 tools/add_terms.py <lang> <file.yml>

<file.yml> holds "English term: translation" pairs. Existing entries are
overwritten, entries not mentioned are left alone, and the result is written
back sorted so the glossary stays easy to scan.
"""

from __future__ import annotations

import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.strip())
        return 2
    lang, source = sys.argv[1], sys.argv[2]

    target = os.path.join(ROOT, "src", "i18n", "terms", f"{lang}.yml")
    with open(target, encoding="utf-8") as fh:
        current = yaml.safe_load(fh) or {}
    with open(source, encoding="utf-8") as fh:
        additions = yaml.safe_load(fh) or {}

    added = sum(1 for k in additions if k not in current)
    changed = sum(1 for k, v in additions.items() if k in current and current[k] != v)
    current.update(additions)

    with open(target, "w", encoding="utf-8") as fh:
        fh.write(
            f"# Cost-table terms for '{lang}': English term -> translation.\n"
            "# A term with no entry here falls back to English, so the table is\n"
            "# never missing a row - only ever untranslated.\n"
        )
        fh.write(yaml.safe_dump(current, allow_unicode=True, sort_keys=True, width=200))

    still_english = sum(1 for k, v in current.items() if k == v)
    print(f"{lang}: +{added} new, {changed} updated")
    print(f"     {len(current)} entries, {still_english} still identical to English")
    return 0


if __name__ == "__main__":
    sys.exit(main())
