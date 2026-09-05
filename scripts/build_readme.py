#!/usr/bin/env python3
"""README.md uretici.

    templates/header.md  (GIF blogu - elle korunur, script asla degistirmez)
  + data/projects.json   (tek degisen dosya)
  = README.md

README.md ELLE DUZENLENMEZ. Degisiklik icin data/projects.json'u guncelle,
sonra bu scripti calistir:  python3 scripts/build_readme.py
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HEADER = ROOT / "templates" / "header.md"
DATA = ROOT / "data" / "projects.json"
OUTPUT = ROOT / "README.md"

DEFAULT_INTRO = "Here are a few things that might be useful:"


def bio_lines(data: dict) -> list[str]:
    """Tanitim blogu: ortalanmis basliklar. level 2 = en iri, 4 = govde boyu."""
    bio = data.get("bio")
    if isinstance(bio, str):
        bio = [{"text": bio, "level": 3}] if bio.strip() else []
    if not isinstance(bio, list):
        return []

    align = str(data.get("bio_align", "center")).strip() or "center"

    out = []
    for line in bio:
        text = str(line.get("text", "")).strip()
        if not text:
            continue
        level = min(max(int(line.get("level", 3)), 1), 6)

        # GitHub README'de CSS silindigi icin renk ancak LaTeX ile veriliyor.
        # Matematik blogu icinde bulundugu basligin punto'sunu miras aliyor.
        color = str(line.get("color", "")).strip()
        body = f"$\\color{{{color}}}\\textsf{{{text}}}$" if color else text

        out.append(f'<h{level} align="{align}">{body}</h{level}>')
    return out


def build() -> str:
    header = HEADER.read_text(encoding="utf-8").rstrip("\n")
    data = json.loads(DATA.read_text(encoding="utf-8"))

    projects = [p for p in data.get("projects", []) if not p.get("hidden")]

    parts = [header]

    bio = bio_lines(data)
    if bio:
        parts.append("")
        parts += bio

    if projects:
        intro = str(data.get("intro", DEFAULT_INTRO)).strip()
        parts += ["", f"**{intro}**", ""]

        for p in projects:
            name = str(p.get("name", "")).strip()
            if not name:
                raise ValueError(f"Projenin 'name' alani bos: {p!r}")

            url = str(p.get("url", "")).strip()
            desc = str(p.get("description", "")).strip()
            emoji = str(p.get("emoji", "")).strip()

            label = f"[{name}]({url})" if url else name
            line = f"- {emoji} **{label}**" if emoji else f"- **{label}**"
            if desc:
                line += f" — **{desc}**"
            parts.append(line)

    return "\n".join(parts).rstrip("\n") + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="README.md uret")
    ap.add_argument("--check", action="store_true",
                    help="Yazma; README guncel degilse 1 don (CI icin)")
    args = ap.parse_args()

    new = build()
    old = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else None

    if args.check:
        if new != old:
            print("README.md guncel degil. 'python3 scripts/build_readme.py' calistir.")
            return 1
        print("README.md guncel.")
        return 0

    if new == old:
        print("Degisiklik yok.")
        return 0

    OUTPUT.write_text(new, encoding="utf-8")
    print(f"README.md yazildi ({len(new.splitlines())} satir).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
