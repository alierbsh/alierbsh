"""'Computer Science Knowledge' listesini kod editoru penceresi gorunumlu bir
SVG'ye cevirir. Liste bir Python class'i gibi durur:

    class ComputerScienceKnowledge:          <- baslik (title)
        \"\"\"I've really been racking ...\"\"\"   <- alt baslik (subtitle)

        topics = [
            "Linear Algebra",                <- maddeler (items)
            ...
        ]

Terminal kartiyla (learning_svg.py) ayni renk paleti ve pencere dili; ayni
animasyon kurali: SVG'nin statik hali BITMIS hal, animasyon sadece giris.
"""

from __future__ import annotations

import math
import re
from xml.sax.saxutils import escape

from learning_svg import BG, BAR, BORDER, TEXT, MUTED, FONT_STACK

FONT = 13
CW = 7.8               # tek karakter genisligi; her kod satiri bu genislige sabitlenir
LH = 22
TITLE_H = 40           # trafik isiklari + sekme
STATUS_H = 24
PAD_TOP = 16
NUM_RIGHT = 36         # satir numaralarinin sag kenari
CODE_X = 54            # kodun basladigi x
PAD_RIGHT = 28

GUTTER = "#6e7681"
ACTIVE_BG = "#6e76811f"
TAB_ACCENT = "#f78166"

# GitHub Dark syntax renkleri
KW = "#ff7b72"         # class
CLS = "#d2a8ff"        # class adi
STR = "#a5d6ff"        # string / docstring
VAR = "#ffa657"        # topics
OP = "#ff7b72"         # =
BRK = "#f2cc60"        # [ ]  (bracket pair renklendirme)

INDENT = 4

# zamanlama (saniye)
LINE_START = 0.35
LINE_GAP = 0.09


def _words(title: str) -> list[str]:
    return [w for w in re.split(r"[^0-9A-Za-z]+", title) if w]


def class_name(title: str) -> str:
    return "".join(w[:1].upper() + w[1:] for w in _words(title)) or "Knowledge"


def file_name(title: str) -> str:
    return "_".join(w.lower() for w in _words(title)) + ".py" if _words(title) else "knowledge.py"


def _lines(title: str, subtitle: str, items: list[str]):
    """Her satir: (girinti, [(metin, renk, kalin_mi), ...])"""
    lines = [(0, [("class ", KW, False), (class_name(title), CLS, True), (":", TEXT, False)])]
    if subtitle:
        lines.append((INDENT, [(f'"""{subtitle}"""', STR, False)]))
    lines.append((0, []))
    lines.append((INDENT, [("topics", VAR, False), (" = ", OP, False), ("[", BRK, True)]))
    for item in items:
        lines.append((2 * INDENT, [(f'"{item}"', STR, False), (",", TEXT, False)]))
    lines.append((INDENT, [("]", BRK, True)]))
    return lines


def _line_len(line) -> int:
    indent, toks = line
    return indent + sum(len(t) for t, _, _ in toks)


def width(title: str, subtitle: str, items: list[str]) -> int:
    longest = max(_line_len(l) for l in _lines(title, subtitle, items))
    return math.ceil(CODE_X + longest * CW + PAD_RIGHT)


def render(title: str, subtitle: str, items: list[str], min_width: int = 0) -> str:
    lines = _lines(title, subtitle, items)
    W = max(width(title, subtitle, items), min_width)
    n = len(lines)
    H = TITLE_H + PAD_TOP + n * LH + 12 + STATUS_H

    active = n - 2                      # son madde: bir sonraki buraya eklenecek
    active_len = _line_len(lines[active])
    end_at = LINE_START + n * LINE_GAP + 0.1

    alt = f"{title}: {subtitle} " + ", ".join(items)

    s: list[str] = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
      f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">')
    a(f'<title id="t">{escape(alt)}</title>')
    a('<style>')
    a(f'text{{font-family:{FONT_STACK};font-size:{FONT}px}}')
    a('.ui{font-size:11.5px}')
    a('@keyframes in{from{opacity:0}to{opacity:1}}')
    a('@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}')
    a('.ln{animation:in .25s ease-out both}')
    a('.hl{animation:in .2s linear %.2fs both}' % end_at)
    a('.cur{animation:in .01s linear %.2fs both,blink 1.1s step-end %.2fs infinite}'
      % (end_at, end_at + 0.4))
    a('@media (prefers-reduced-motion:reduce){*{animation:none!important}}')
    a('</style>')

    # pencere
    a(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>')
    a(f'<path d="M0.5 {TITLE_H} V10.5 a10 10 0 0 1 10 -10 H{W - 10.5} a10 10 0 0 1 10 10 V{TITLE_H} Z" '
      f'fill="{BAR}"/>')
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        a(f'<circle cx="{20 + i * 20}" cy="{TITLE_H / 2}" r="6" fill="{c}"/>')

    # sekme: editor zeminine bagli, ustunde turuncu vurgu
    fname = file_name(title)
    tab_x, tab_y = 86, 8
    tab_w = math.ceil(28 + len(fname) * 6.9 + 30)
    a(f'<path d="M{tab_x} {TITLE_H} V{tab_y + 6} a6 6 0 0 1 6 -6 H{tab_x + tab_w - 6} '
      f'a6 6 0 0 1 6 6 V{TITLE_H} Z" fill="{BG}"/>')
    a(f'<path d="M{tab_x + 1} {tab_y + 3} a6 6 0 0 1 5 -3 H{tab_x + tab_w - 6} a6 6 0 0 1 5 3" '
      f'fill="none" stroke="{TAB_ACCENT}" stroke-width="2"/>')
    a(f'<line x1="0.5" y1="{TITLE_H}" x2="{tab_x}" y2="{TITLE_H}" stroke="{BORDER}"/>')
    a(f'<line x1="{tab_x + tab_w}" y1="{TITLE_H}" x2="{W - 0.5}" y2="{TITLE_H}" stroke="{BORDER}"/>')
    a(f'<line x1="{tab_x}" y1="{tab_y + 6}" x2="{tab_x}" y2="{TITLE_H}" stroke="{BORDER}"/>')
    a(f'<line x1="{tab_x + tab_w}" y1="{tab_y + 6}" x2="{tab_x + tab_w}" y2="{TITLE_H}" stroke="{BORDER}"/>')
    icy = tab_y + (TITLE_H - tab_y) / 2
    a(f'<circle cx="{tab_x + 14}" cy="{icy - 2}" r="4" fill="#3572a5"/>')
    a(f'<circle cx="{tab_x + 18}" cy="{icy + 2}" r="4" fill="#ffd43b"/>')
    a(f'<text class="ui" x="{tab_x + 30}" y="{icy + 4}" fill="{TEXT}">{escape(fname)}</text>')
    a(f'<text class="ui" x="{tab_x + tab_w - 14}" y="{icy + 4}" fill="{MUTED}" '
      f'text-anchor="middle">&#215;</text>')

    # aktif satir vurgusu
    top = TITLE_H + PAD_TOP
    ay = top + active * LH
    a(f'<rect class="hl" x="1" y="{ay}" width="{W - 2}" height="{LH}" fill="{ACTIVE_BG}"/>')

    # kod satirlari
    for i, line in enumerate(lines):
        indent, toks = line
        base = top + i * LH + LH / 2 + FONT * 0.36
        num_c = TEXT if i == active else GUTTER
        a(f'<g class="ln" style="animation-delay:{LINE_START + i * LINE_GAP:.2f}s">')
        a(f'<text x="{NUM_RIGHT}" y="{base:.1f}" fill="{num_c}" text-anchor="end">{i + 1}</text>')
        if toks:
            chars = sum(len(t) for t, _, _ in toks)
            bold = ' font-weight="700"'
            spans = "".join(
                f'<tspan fill="{c}"{bold if b else ""}>{escape(t)}</tspan>' for t, c, b in toks)
            a(f'<text x="{CODE_X + indent * CW:.1f}" y="{base:.1f}" textLength="{chars * CW:.1f}" '
              f'lengthAdjust="spacing" xml:space="preserve">{spans}</text>')
        a('</g>')

    # imlec: son maddenin sonunda, yeni madde bekliyor
    cy = top + active * LH + 3
    a(f'<rect class="cur" x="{CODE_X + active_len * CW + 1:.1f}" y="{cy}" width="2" '
      f'height="{LH - 6}" fill="{TEXT}"/>')

    # durum cubugu
    sy = H - STATUS_H
    a(f'<path d="M0.5 {sy} H{W - 0.5} V{H - 10.5} a10 10 0 0 1 -10 10 H10.5 a10 10 0 0 1 -10 -10 Z" '
      f'fill="{BAR}"/>')
    a(f'<line x1="0.5" y1="{sy}" x2="{W - 0.5}" y2="{sy}" stroke="{BORDER}"/>')
    a(f'<circle cx="18" cy="{sy + STATUS_H / 2}" r="3.5" fill="#3fb950"/>')
    a(f'<text class="ui" x="28" y="{sy + STATUS_H / 2 + 4}" fill="{MUTED}">main</text>')
    a(f'<text class="ui" x="{W - 16}" y="{sy + STATUS_H / 2 + 4}" fill="{MUTED}" text-anchor="end" '
      f'xml:space="preserve">Ln {active + 1}, Col {active_len + 1}   Python   UTF-8</text>')

    a('</svg>')
    return "\n".join(s) + "\n"
