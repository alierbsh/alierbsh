#!/usr/bin/env python3
"""README.md uretici.

    templates/header.md  (GIF blogu - elle korunur, script asla degistirmez)
  + data/projects.json   (tek degisen dosya: bio, projeler, "learning" listesi)
  = README.md  +  assets/currently-learning.svg  ("learning" listesinden cizilir)

README.md ve SVG ELLE DUZENLENMEZ. Degisiklik icin data/projects.json'u guncelle,
sonra bu scripti calistir:  python3 scripts/build_readme.py
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from learning_svg import render as render_learning_svg, width as learning_svg_width

ROOT = pathlib.Path(__file__).resolve().parent.parent
HEADER = ROOT / "templates" / "header.md"
DATA = ROOT / "data" / "projects.json"
OUTPUT = ROOT / "README.md"
LEARNING_SVG = ROOT / "assets" / "currently-learning.svg"

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

        # RENK KULLANMA. GitHub README'de CSS/style siliniyor; renk vermenin tek
        # yolu LaTeX ($\\color{...}) ama GitHub mobil uygulamasi matematigi
        # render etmiyor ve ham kaynagi ("$\\color{#008F11}...$") gosteriyor.
        # Denendi, mobilde bozuldu, geri alindi. Duz metin birak.
        out.append(f'<h{level} align="{align}">{text}</h{level}>')
    return out


def learning_items(data: dict) -> list[str]:
    return [str(x).strip() for x in data.get("learning", []) if str(x).strip()]


def learning_lines(items: list[str]) -> list[str]:
    """'Currently learning' blogu: terminal gorunumlu SVG. Liste bossa hic basilmaz."""
    if not items:
        return []
    rel = LEARNING_SVG.relative_to(ROOT).as_posix()
    # alt metin: resim yuklenmezse / ekran okuyucuda liste yine okunur
    alt = "Currently learning: " + ", ".join(items)
    alt = alt.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
    return ["", '<div align="center">',
            f'<img src="{rel}" width="{learning_svg_width(items)}" alt="{alt}" />',
            "</div>"]


def build() -> dict[pathlib.Path, str | None]:
    """Uretilecek dosyalar: {yol: icerik}. icerik None ise dosya silinir."""
    header = HEADER.read_text(encoding="utf-8").rstrip("\n")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    learning = learning_items(data)

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

    parts += learning_lines(learning)

    readme = "\n".join(parts).rstrip("\n") + "\n"
    svg = render_learning_svg(learning) if learning else None
    return {OUTPUT: readme, LEARNING_SVG: svg}


def current(path: pathlib.Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.exists() else None


def main() -> int:
    ap = argparse.ArgumentParser(description="README.md uret")
    ap.add_argument("--check", action="store_true",
                    help="Yazma; README guncel degilse 1 don (CI icin)")
    args = ap.parse_args()

    outputs = build()
    stale = [p for p, new in outputs.items() if current(p) != new]

    if args.check:
        if stale:
            names = ", ".join(p.relative_to(ROOT).as_posix() for p in stale)
            print(f"Guncel degil: {names}. 'python3 scripts/build_readme.py' calistir.")
            return 1
        print("README.md guncel.")
        return 0

    if not stale:
        print("Degisiklik yok.")
        return 0

    for path in stale:
        new = outputs[path]
        rel = path.relative_to(ROOT).as_posix()
        if new is None:
            path.unlink()
            print(f"{rel} silindi.")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(new, encoding="utf-8")
            print(f"{rel} yazildi ({len(new.splitlines())} satir).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
