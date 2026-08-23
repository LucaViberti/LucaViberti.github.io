#!/usr/bin/env python3
"""
One-time migration of the three faction hero pages into data.

League, Nature and Horde are the same page three times, in seven languages: a
lineup block and then one card per hero, each with a portrait, a role, a skill
list and a note. Everything except the sentences is identical across languages -
hero names, skill names, portraits and roles - yet all 21 files were maintained
by hand, so they had drifted:

  * role labels are an enum with seven values, but German left four heroes on
    the English "Damage Dealer", Japanese uses two different words for the same
    role, Vietnamese uses three, and Korean has editorial asides in the field
    ("healer (starter)", "tank/DPS (best)")
  * ko/horde.html is missing three skills

Splitting them into structure (src/data/heroes.yml) and sentences
(src/i18n/heroes/<lang>.yml) makes the first class of problem impossible and
the second visible.

Run from the repository root:  python3 tools/extract_heroes.py
"""

from __future__ import annotations

import os
import re
import sys
from collections import Counter

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")

with open(os.path.join(SRC, "site.yml"), encoding="utf-8") as fh:
    SITE = yaml.safe_load(fh)
LANGS = list(SITE["languages"])
DEFAULT = SITE["default_language"]

FACTIONS = ("league", "nature", "horde")

# The seven role values English uses, in the order they should be offered.
ROLE_IDS = {
    "Damage Dealer": "dps",
    "Tank": "tank",
    "Support": "support",
    "Healer": "healer",
    "Tank / Damage Dealer": "tank_dps",
    "Support / Damage Dealer": "support_dps",
    "Healer / Support": "healer_support",
}

LINEUP_LABELS = {"Front": "front", "Middle": "middle", "Back": "back"}


def read(rel: str) -> str:
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def write(rel: str, text: str) -> None:
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# ---------------------------------------------------------------------------
# parsing
# ---------------------------------------------------------------------------

CARD_RE = re.compile(r'<div class="card">(.*?)</div>\s*(?=<div class="card">|</section>|$)', re.S)


def split_cards(html: str) -> tuple[str, str, list[str]]:
    """(prose before the first card, lineup card, hero cards)"""
    i = html.find('<div class="card">')
    prose = html[:i]
    rest = html[i:]

    # The lineup card is the one holding .lineup-wrapper; hero cards hold .role
    chunks = re.split(r'(?=<div class="card">)', rest)
    chunks = [c for c in chunks if c.strip()]
    lineup = ""
    heroes = []
    for c in chunks:
        if "lineup-wrapper" in c:
            lineup = c
        elif '<div class="role">' in c:
            heroes.append(c)
    return prose, lineup, heroes


def parse_lineups(chunk: str) -> dict:
    title = clean(re.search(r"<h3>(.*?)</h3>", chunk, re.S).group(1))
    cards = []
    # Split on the card boundary rather than using a lookahead: an end-anchored
    # lookahead silently dropped every lineup card but the first.
    pieces = re.split(r'<div class="lineup-card">', chunk)[1:]
    for piece in pieces:
        m = re.search(r"<h3>(.*?)</h3>", piece, re.S)
        if not m:
            continue
        card_title, body = clean(m.group(1)), piece
        rows = []
        for rm in re.finditer(
            r'<div class="lineup-row">\s*<div class="lineup-label">(.*?)</div>\s*'
            r'<div class="lineup-heroes">(.*?)</div>',
            body,
            re.S,
        ):
            label = clean(rm.group(1))
            imgs = [
                {"image": im.group(1), "alt": clean(im.group(2))}
                for im in re.finditer(r'<img src="([^"]+)" alt="([^"]*)"', rm.group(2))
            ]
            rows.append({"label": label, "heroes": imgs})
        # Korean's Horde page wraps its note in a <div> rather than a <p>;
        # matching only <p> silently dropped a Korean-only tip.
        note = re.search(r'<(?:p|div) class="lineup-note">(.*?)</(?:p|div)>', body, re.S)
        cards.append(
            {"title": card_title, "rows": rows, "note": clean(note.group(1)) if note else ""}
        )
    return {"title": title, "cards": cards}


def parse_hero(chunk: str) -> dict:
    name = clean(re.search(r"<h3>(.*?)</h3>", chunk, re.S).group(1))
    role = clean(re.search(r'<div class="role">(.*?)</div>', chunk, re.S).group(1))
    img = re.search(r'<img src="([^"]+)" alt="([^"]*)"', chunk)
    skills_label = re.search(r"<strong>(.*?)</strong>", chunk, re.S)
    # Japanese, Traditional and Simplified Chinese separate the skill name from
    # its description with a full-width colon rather than an ASCII one.
    skills = [
        {"name": clean(m.group(1)), "text": clean(m.group(2))}
        for m in re.finditer(r"<li><em>(.*?)</em>\s*[:：]\s*(.*?)</li>", chunk, re.S)
    ]
    # the note is the <p> after the skill list
    note = re.search(r"</ul>\s*<p>(.*?)</p>", chunk, re.S)
    return {
        "name": name,
        "role": role,
        "image": img.group(1) if img else "",
        "alt": clean(img.group(2)) if img else "",
        "skills_label": clean(skills_label.group(1)) if skills_label else "Skills",
        "skills": skills,
        "note": clean(note.group(1)) if note else "",
    }


def parse_faction(lang: str, faction: str) -> dict:
    html = read(f"src/content/{lang}/{faction}.html")
    prose, lineup_chunk, hero_chunks = split_cards(html)
    return {
        "prose": prose,
        "lineups": parse_lineups(lineup_chunk) if lineup_chunk else None,
        "heroes": [parse_hero(c) for c in hero_chunks],
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> int:
    parsed = {
        lang: {f: parse_faction(lang, f) for f in FACTIONS} for lang in LANGS
    }
    warnings: list[str] = []

    # ---- structure, taken from English -----------------------------------
    data: dict = {"roles": list(ROLE_IDS.values()), "factions": {}}
    for faction in FACTIONS:
        en = parsed[DEFAULT][faction]
        lineups = []
        for card in en["lineups"]["cards"]:
            lineups.append(
                {
                    "id": slug(card["title"]),
                    "rows": [
                        {
                            "label": LINEUP_LABELS.get(r["label"], slug(r["label"])),
                            "heroes": r["heroes"],
                        }
                        for r in card["rows"]
                    ],
                }
            )
        heroes = []
        for h in en["heroes"]:
            role_id = ROLE_IDS.get(h["role"])
            if role_id is None:
                warnings.append(f"unknown English role {h['role']!r} on {faction}/{h['name']}")
                role_id = slug(h["role"])
            heroes.append(
                {
                    "id": slug(h["name"]),
                    "name": h["name"],
                    "image": h["image"],
                    "alt": h["alt"],
                    "role": role_id,
                    "skills": [s["name"] for s in h["skills"]],
                }
            )
        data["factions"][faction] = {"lineups": lineups, "heroes": heroes}

    # ---- translations -----------------------------------------------------
    for lang in LANGS:
        out: dict = {"roles": {}, "lineup_labels": {}, "factions": {}}

        role_votes: dict[str, Counter] = {rid: Counter() for rid in ROLE_IDS.values()}
        label_votes: dict[str, Counter] = {lid: Counter() for lid in LINEUP_LABELS.values()}
        skills_label_votes: Counter = Counter()

        for faction in FACTIONS:
            en = parsed[DEFAULT][faction]
            cur = parsed[lang][faction]
            fout: dict = {"lineups": {}, "heroes": {}}

            if cur["lineups"]:
                fout["lineups_title"] = cur["lineups"]["title"]
                for en_card, card in zip(en["lineups"]["cards"], cur["lineups"]["cards"]):
                    fout["lineups"][slug(en_card["title"])] = {
                        "title": card["title"],
                        "note": card["note"],
                    }
                    for en_row, row in zip(en_card["rows"], card["rows"]):
                        lid = LINEUP_LABELS.get(en_row["label"])
                        if lid:
                            label_votes[lid][row["label"]] += 1

            for en_h, h in zip(en["heroes"], cur["heroes"]):
                rid = ROLE_IDS.get(en_h["role"])
                if rid:
                    role_votes[rid][h["role"]] += 1
                skills_label_votes[h["skills_label"]] += 1

                skills: dict[str, str] = {}
                renamed: dict[str, str] = {}
                if len(h["skills"]) < len(en_h["skills"]):
                    missing = [
                        s["name"] for s in en_h["skills"][len(h["skills"]):]
                    ]
                    warnings.append(
                        f"GAP {lang}/{faction}/{en_h['name']}: never translated "
                        f"{missing} - will fall back to English"
                    )
                elif len(h["skills"]) > len(en_h["skills"]):
                    warnings.append(
                        f"{lang}/{faction}/{en_h['name']}: {len(h['skills'])} skills "
                        f"vs {len(en_h['skills'])} in English"
                    )
                for en_s, s in zip(en_h["skills"], h["skills"]):
                    skills[en_s["name"]] = s["text"]
                    # Every language but Korean keeps skill names in English.
                    # Record Korean's translated names rather than overwriting
                    # them, so nothing visible changes.
                    if s["name"] != en_s["name"]:
                        renamed[en_s["name"]] = s["name"]
                hero_out: dict = {"skills": skills, "note": h["note"]}
                if renamed:
                    hero_out["skill_names"] = renamed
                # Korean translated 18 of the 28 hero names (Nature and Horde,
                # but not League). Record the name it displays rather than
                # forcing English on it, so the page reads as it did before.
                if h["name"] != en_h["name"]:
                    hero_out["name"] = h["name"]
                fout["heroes"][slug(en_h["name"])] = hero_out

            out["factions"][faction] = fout

        # Pick one wording per enum value. Where a language wrote it several
        # ways, prefer a genuinely translated variant over one that was left in
        # English, so collapsing to an enum can never drop a translation - German
        # wrote "Mitte" on two pages and "Middle" on four, and the majority vote
        # alone would have thrown the German word away.
        def choose(votes: Counter, english: str | None) -> str:
            translated = Counter({k: v for k, v in votes.items() if k != english})
            return (translated or votes).most_common(1)[0][0]

        english_roles = {v: k for k, v in ROLE_IDS.items()}
        for rid, votes in role_votes.items():
            if votes:
                best = choose(votes, english_roles.get(rid))
                out["roles"][rid] = best
                if len(votes) > 1:
                    others = {k: v for k, v in votes.items() if k != best}
                    warnings.append(
                        f"{lang}: role '{rid}' written {len(votes)} different ways, "
                        f"using {best!r}; also saw {others}"
                    )
        english_labels = {v: k for k, v in LINEUP_LABELS.items()}
        for lid, votes in label_votes.items():
            if votes:
                best = choose(votes, english_labels.get(lid))
                out["lineup_labels"][lid] = best
                if len(votes) > 1:
                    others = {k: v for k, v in votes.items() if k != best}
                    warnings.append(
                        f"{lang}: lineup label '{lid}' written {len(votes)} ways, "
                        f"using {best!r}; also saw {others}"
                    )
        # Same rule for the "Skills" heading: German wrote "Fähigkeiten" on the
        # Horde page and "Skills" on the other two, so a plain majority vote
        # would have replaced the German word with the English one.
        out["skills_label"] = choose(skills_label_votes, "Skills")

        write(
            f"src/i18n/heroes/{lang}.yml",
            f"# Hero page text for '{lang}'.\n"
            "# Structure (which heroes, which portraits, which skills) lives in\n"
            "# src/data/heroes.yml and is shared by every language.\n"
            + yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=200),
        )

    write(
        "src/data/heroes.yml",
        "# Hero rosters, generated by tools/extract_heroes.py.\n"
        "# Hero names, portraits and skill names stay in English by site convention,\n"
        "# so they live here once; the sentences are in src/i18n/heroes/<lang>.yml.\n"
        "# 'role' is one of the ids in 'roles' - the label for each is translated.\n"
        + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=200),
    )

    total = sum(len(data["factions"][f]["heroes"]) for f in FACTIONS)
    print(f"factions: {len(FACTIONS)}   heroes: {total}")
    print(f"warnings: {len(warnings)}")
    for w in warnings:
        print("   ", w)

    # Only rewrite the sources once the parse is clean: a structural mismatch
    # means the extraction lost something, and the fragments are the originals.
    structural = [w for w in warnings if "skills vs" in w or "unknown English role" in w]
    if structural:
        print("\nrefusing to rewrite src/content: structural mismatches above")
        return 1

    # ---- replace the structured part of each fragment with a marker --------
    for lang in LANGS:
        for faction in FACTIONS:
            prose = parsed[lang][faction]["prose"].rstrip()
            write(
                f"src/content/{lang}/{faction}.html",
                prose + "\n\n<!-- heroes -->\n</section>\n",
            )

    print("rewrote src/content fragments to a <!-- heroes --> marker")
    return 0


if __name__ == "__main__":
    sys.exit(main())
