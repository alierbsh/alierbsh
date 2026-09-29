"""'Currently learning' listesini terminal penceresi gorunumlu bir SVG'ye cevirir.

GitHub README'de CSS/renk yok ama README'ye resim olarak giren SVG'nin icinde
her sey serbest. Bu yuzden liste burada ciziliyor, README sadece resmi gosteriyor.

Animasyon notlari:
- Her animasyonun "baslangic" hali CSS keyframe'lerde; SVG'nin kendi (statik)
  hali ise BITMIS hal. Animasyonu desteklemeyen bir goruntuleyici (or. bazi
  mobil render'lar) bos kutu degil, tam listeyi gosterir.
- prefers-reduced-motion acikken animasyon kapanir, yine bitmis hal gorunur.
- Pencere koyu arka planli; GitHub'in acik ve koyu temasinda ayni durur.
"""

from __future__ import annotations

import math
from xml.sax.saxutils import escape

MIN_W = 480            # SVG en az genisligi; uzun madde gelirse kendiliginden genisler
PAD_X = 24             # sol bosluk
TITLE_H = 34           # baslik cubugu yuksekligi
FONT = 14              # yazi boyu
LH = 25                # satir yuksekligi
CW = 8.4               # tek karakter genisligi (komut satiri bu genislige sabitlenir)

BG = "#0d1117"
BAR = "#161b22"
BORDER = "#30363d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
PROMPT = "#3fb950"
PATH = "#79c0ff"
NUM_COLORS = ["#7ee787", "#79c0ff", "#d2a8ff", "#ffa657", "#ff7b72", "#f2cc60", "#56d4dd"]

COMMAND = "cat currently-learning.txt"
WINDOW_TITLE = "alierbsh@github: ~"

FONT_STACK = ('ui-monospace, SFMono-Regular, &quot;SF Mono&quot;, Menlo, Consolas, '
              '&quot;Liberation Mono&quot;, &quot;DejaVu Sans Mono&quot;, monospace')

# zamanlama (saniye)
TYPE_START = 0.5
TYPE_STEP = 0.045
LINE_GAP = 0.13


def _prompt(y: float, extra: str = "") -> list[str]:
    return [
        f'<text x="{PAD_X}" y="{y}" fill="{PROMPT}" font-weight="700"{extra}>&#10140;</text>',
        f'<text x="{PAD_X + 2 * CW}" y="{y}" fill="{PATH}" font-weight="700"{extra}>~</text>',
    ]


def width(items: list[str]) -> int:
    longest = max([len(COMMAND)] + [len(x) for x in items]) + 4   # "01  " oneki
    return max(MIN_W, math.ceil(2 * PAD_X + longest * CW + 48))


def render(items: list[str], min_width: int = 0) -> str:
    """min_width: README'de alt alta duran kartlar ayni genislikte olsun diye."""
    n = len(items)
    W = max(width(items), min_width)
    type_end = TYPE_START + len(COMMAND) * TYPE_STEP
    out_start = type_end + 0.25
    final_at = out_start + n * LINE_GAP + 0.15

    body_top = TITLE_H + 30                      # ilk satirin taban cizgisi
    out_top = body_top + LH + 4                  # cikti satirlari biraz ayrik
    final_y = out_top + n * LH + 4
    H = final_y + 22

    cmd_x = PAD_X + 4 * CW
    cmd_w = len(COMMAND) * CW

    title = "Currently learning: " + ", ".join(items)

    s: list[str] = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
      f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">')
    a(f'<title id="t">{escape(title)}</title>')
    a('<style>')
    a(f'text{{font-family:{FONT_STACK};font-size:{FONT}px;white-space:pre}}')
    a('.bar{font-size:12px}')
    a('@keyframes in{from{opacity:0}to{opacity:1}}')
    a(f'@keyframes type{{from{{transform:translateX({cmd_x}px)}}'
      f'to{{transform:translateX({cmd_x + cmd_w}px)}}}}')
    a('@keyframes tcur{0%,99%{opacity:1}100%{opacity:0}}')
    a('@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}')
    a(f'.typer{{animation:type {len(COMMAND) * TYPE_STEP:.3f}s steps({len(COMMAND)},end) '
      f'{TYPE_START}s both}}')
    a('.tcur{opacity:0;animation:tcur %.3fs linear 0s both}' % type_end)
    a('.o{animation:in .22s ease-out both}')
    a('.cur{animation:in .01s linear %.2fs both,blink 1.1s step-end %.2fs infinite}'
      % (final_at, final_at + 0.4))
    a('@media (prefers-reduced-motion:reduce){*{animation:none!important}.tcur{opacity:0}}')
    a('</style>')

    # pencere + baslik cubugu
    a(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>')
    a(f'<path d="M0.5 {TITLE_H} V10.5 a10 10 0 0 1 10 -10 H{W - 10.5} a10 10 0 0 1 10 10 V{TITLE_H} Z" '
      f'fill="{BAR}"/>')
    a(f'<line x1="0.5" y1="{TITLE_H}" x2="{W - 0.5}" y2="{TITLE_H}" stroke="{BORDER}"/>')
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        a(f'<circle cx="{20 + i * 20}" cy="{TITLE_H / 2}" r="6" fill="{c}"/>')
    a(f'<text class="bar" x="{W / 2}" y="{TITLE_H / 2 + 4}" fill="{MUTED}" '
      f'text-anchor="middle">{escape(WINDOW_TITLE)}</text>')

    # 1) komut satiri: yazilma efekti = ustunden kayan bir ortu
    s += _prompt(body_top)
    a(f'<text x="{cmd_x}" y="{body_top}" fill="{TEXT}" textLength="{cmd_w}" '
      f'lengthAdjust="spacing">{escape(COMMAND)}</text>')
    # ortu sadece komutun ustunde gezer; pencere kenarina tasmasin diye kirpilir
    a(f'<clipPath id="cmdclip"><rect x="{cmd_x - 1}" y="{body_top - FONT - 4}" '
      f'width="{cmd_w + CW + 2}" height="{FONT + 12}"/></clipPath>')
    a('<g clip-path="url(#cmdclip)">')
    a(f'<g class="typer" transform="translate({cmd_x + cmd_w} 0)">')
    a(f'<rect x="0" y="{body_top - FONT - 2}" width="{cmd_w + 4}" height="{FONT + 8}" fill="{BG}"/>')
    a(f'<rect class="tcur" x="0" y="{body_top - FONT + 1}" width="{CW}" height="{FONT + 3}" fill="{TEXT}"/>')
    a('</g>')
    a('</g>')

    # 2) cikti satirlari: tek tek belirir
    for i, item in enumerate(items):
        y = out_top + i * LH
        color = NUM_COLORS[i % len(NUM_COLORS)]
        delay = out_start + i * LINE_GAP
        a(f'<g class="o" style="animation-delay:{delay:.2f}s">')
        a(f'<text x="{PAD_X}" y="{y}" fill="{color}" font-weight="700">{i + 1:02d}</text>')
        a(f'<text x="{PAD_X + 4 * CW}" y="{y}" fill="{TEXT}">{escape(item)}</text>')
        a('</g>')

    # 3) son satir: bos prompt + yanip sonen imlec
    a(f'<g class="o" style="animation-delay:{final_at:.2f}s">')
    s += _prompt(final_y)
    a('</g>')
    a(f'<rect class="cur" x="{PAD_X + 4 * CW}" y="{final_y - FONT + 1}" width="{CW}" '
      f'height="{FONT + 3}" fill="{TEXT}"/>')

    a('</svg>')
    return "\n".join(s) + "\n"
