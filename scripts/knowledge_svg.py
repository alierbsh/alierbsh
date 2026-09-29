"""'Computer Science Knowledge' listesini periyodik tablo gorunumlu bir SVG'ye cevirir.

Her konu bir element kutucugu: sol ustte sira numarasi, ortada iki harfli sembol
(La, De, Dm...), altta konunun adi. Bos kutucuklar kesikli cerceve + "?" ile
durur: tablo her zaman en az bir bos kutucuk birakir ve konu eklendikce satir
satir buyur. Siradaki bos kutucuk hafifce nabiz atar ("sonraki buraya").

Madde ya duz string ("Linear Algebra") ya da sembolu elle vermek icin
{"name": "Linear Algebra", "symbol": "La"}.

Terminal kartiyla (learning_svg.py) ayni palet; ayni animasyon kurali:
SVG'nin statik hali BITMIS hal, animasyon sadece giris.
"""

from __future__ import annotations

import math
from xml.sax.saxutils import escape

from learning_svg import BG, BORDER, TEXT, MUTED, NUM_COLORS

SANS = ('-apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, &quot;Noto Sans&quot;, '
        'Helvetica, Arial, sans-serif')

COLS = 5
TILE_W, TILE_H, GAP = 90, 106, 10
PAD_X = 30
GRID_TOP = 94
PAD_BOTTOM = 30
NAME_FONT = 11
NAME_MAX = 13          # bir satira sigan karakter (kutucuk adi)

EMPTY = "#30363d"
EMPTY_NUM = "#484f58"
NEXT = "#6e7681"

SKIP_WORDS = {"and", "with", "of", "the", "for", "in", "to", "a", "an"}

# zamanlama (saniye)
POP_START = 0.35
POP_GAP = 0.16


def normalize(items) -> list[dict]:
    out = []
    for it in items or []:
        if isinstance(it, dict):
            name = str(it.get("name", "")).strip()
            sym = str(it.get("symbol", "")).strip()
        else:
            name, sym = str(it).strip(), ""
        if name:
            out.append({"name": name, "symbol": sym})
    return out


def _symbols(items: list[dict]) -> list[str]:
    """Iki harfli, cakismayan semboller. Elle verilen sembol her zaman kazanir."""
    used = {it["symbol"] for it in items if it["symbol"]}
    out = []
    for it in items:
        if it["symbol"]:
            out.append(it["symbol"])
            continue
        words = [w for w in it["name"].replace("-", " ").split() if w[:1].isalpha()]
        main = [w for w in words if w.lower() not in SKIP_WORDS] or words
        first = main[0]
        cands = []
        if len(main) >= 2:
            cands.append(first[0].upper() + main[1][0].lower())
        cands += [first[0].upper() + ch.lower() for ch in first[1:] if ch.isalpha()]
        for w in main[1:]:
            cands += [first[0].upper() + ch.lower() for ch in w if ch.isalpha()]
        sym = next((c for c in cands if c not in used), first[:2].title())
        used.add(sym)
        out.append(sym)
    return out


def _wrap(name: str) -> list[str]:
    lines, cur = [], ""
    for w in name.split():
        if cur and len(cur) + 1 + len(w) > NAME_MAX:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines[:3]


def _slots(n: int) -> int:
    # en az iki satir, her zaman en az bir bos kutucuk
    return max(2 * COLS, math.ceil((n + 1) / COLS) * COLS)


def width(title: str, subtitle: str, items) -> int:
    return 2 * PAD_X + COLS * TILE_W + (COLS - 1) * GAP


def render(title: str, subtitle: str, items, min_width: int = 0) -> str:
    items = normalize(items)
    syms = _symbols(items)
    n = len(items)
    slots = _slots(n)
    rows = slots // COLS
    W = max(width(title, subtitle, items), min_width)
    H = GRID_TOP + rows * TILE_H + (rows - 1) * GAP + PAD_BOTTOM
    x0 = (W - (COLS * TILE_W + (COLS - 1) * GAP)) / 2
    done_at = POP_START + n * POP_GAP + 0.3

    alt = f"{title}: {subtitle} " + ", ".join(it["name"] for it in items)

    s: list[str] = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
      f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">')
    a(f'<title id="t">{escape(alt)}</title>')
    a('<defs>')
    a('<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">'
      '<feGaussianBlur stdDeviation="7"/></filter>')
    a('</defs>')
    a('<style>')
    a(f'text{{font-family:{SANS}}}')
    a('@keyframes in{from{opacity:0}to{opacity:1}}')
    a('@keyframes pop{0%{opacity:0;transform:scale(.6)}60%{opacity:1;transform:scale(1.06)}'
      '100%{opacity:1;transform:scale(1)}}')
    a('@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}')
    a('.tile{transform-box:fill-box;transform-origin:center;animation:pop .45s ease-out both}')
    a('.empty{animation:in .4s ease-out .1s both}')
    a(f'.next{{animation:in .4s ease-out .1s both,pulse 2s ease-in-out {done_at:.2f}s infinite}}')
    a('@media (prefers-reduced-motion:reduce){*{animation:none!important}}')
    a('</style>')

    a(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>')
    a(f'<text x="{W / 2}" y="46" font-size="21" font-weight="700" fill="{TEXT}" '
      f'text-anchor="middle">{escape(title)}</text>')
    if subtitle:
        a(f'<text x="{W / 2}" y="71" font-size="14" font-style="italic" fill="{MUTED}" '
          f'text-anchor="middle">{escape(subtitle)}</text>')

    for k in range(slots):
        r, c = divmod(k, COLS)
        x = x0 + c * (TILE_W + GAP)
        y = GRID_TOP + r * (TILE_H + GAP)
        cx = x + TILE_W / 2

        if k >= n:
            cls = "next" if k == n else "empty"
            stroke = NEXT if k == n else EMPTY
            a(f'<g class="{cls}">')
            a(f'<rect x="{x}" y="{y}" width="{TILE_W}" height="{TILE_H}" rx="8" fill="none" '
              f'stroke="{stroke}" stroke-dasharray="4 4"/>')
            a(f'<text x="{x + 9}" y="{y + 18}" font-size="11" fill="{EMPTY_NUM}">{k + 1}</text>')
            a(f'<text x="{cx}" y="{y + 60}" font-size="28" font-weight="700" fill="{stroke}" '
              f'text-anchor="middle">?</text>')
            a('</g>')
            continue

        it, sym = items[k], syms[k]
        col = NUM_COLORS[k % len(NUM_COLORS)]
        lines = _wrap(it["name"])
        sym_y = y + (58 if len(lines) <= 2 else 50)

        a(f'<g class="tile" style="animation-delay:{POP_START + k * POP_GAP:.2f}s">')
        a(f'<rect x="{x + 6}" y="{y + 10}" width="{TILE_W - 12}" height="{TILE_H - 12}" rx="10" '
          f'fill="{col}" opacity=".22" filter="url(#glow)"/>')
        a(f'<rect x="{x}" y="{y}" width="{TILE_W}" height="{TILE_H}" rx="8" fill="{BG}"/>')
        a(f'<rect x="{x}" y="{y}" width="{TILE_W}" height="{TILE_H}" rx="8" fill="{col}" '
          f'fill-opacity=".12" stroke="{col}" stroke-width="1.5"/>')
        a(f'<text x="{x + 9}" y="{y + 18}" font-size="11" font-weight="700" fill="{col}">{k + 1}</text>')
        a(f'<text x="{cx}" y="{sym_y}" font-size="34" font-weight="700" fill="{TEXT}" '
          f'text-anchor="middle">{escape(sym)}</text>')
        for j, ln in enumerate(lines):
            ly = y + TILE_H - 11 - (len(lines) - 1 - j) * 12.5
            fit = ''
            if len(ln) > NAME_MAX:
                fit = f' textLength="{TILE_W - 12}" lengthAdjust="spacingAndGlyphs"'
            a(f'<text x="{cx}" y="{ly}" font-size="{NAME_FONT}" fill="#c9d1d9" '
              f'text-anchor="middle"{fit}>{escape(ln)}</text>')
        a('</g>')

    a('</svg>')
    return "\n".join(s) + "\n"
