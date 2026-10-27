"""Generate the profile banner SVGs (light and dark) for github.com/madecero.

The site's fonts (Newsreader, Manrope) are pinned to one weight, subset to the
glyphs the banner uses, and embedded as base64 WOFF2 so the SVG renders the
same everywhere GitHub serves it.

Usage: python scripts/banner.py <path to Website/public/fonts>
Needs: fonttools, brotli
"""

import base64
import io
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONTS = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent.parent / "assets"

W, H = 1280, 400
EYEBROW = "DECEROAI SOLUTIONS  ·  WAUNAKEE, WISCONSIN"
NAME = "Michael DeCero"
LEAD = "I take AI from prototype to "
LEAD_EM = "production."
MARK = "de0"
STAGES = ["prototype", "semantic layer", "agents", "controls", "production"]

THEMES = {
    "dark": dict(bg="#0a0a0f", elevated="#111118", ink="#e4e4e7", ink2="#a1a1aa",
                 muted="#8b8b96", accent="#22d3ee", accent_soft="#06b6d4", amber="#fbbf24",
                 dot_opacity=0.08, glow=0.22, warm=0.10, mark_opacity=0.07),
    "light": dict(bg="#f7f4ee", elevated="#fffdf9", ink="#16140f", ink2="#3d3a33",
                  muted="#625d53", accent="#0e7490", accent_soft="#0891b2", amber="#d97706",
                  dot_opacity=0.10, glow=0.14, warm=0.10, mark_opacity=0.06),
}


def build_font(file, axes, text):
    font = instancer.instantiateVariableFont(TTFont(FONTS / file), axes)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    opts.name_IDs = []
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    measure = TTFont(io.BytesIO(buf.getvalue()))
    return base64.b64encode(buf.getvalue()).decode(), measure


def text_width(font, text, size, tracking=0.0):
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    upem = font["head"].unitsPerEm
    return sum(hmtx[cmap[ord(c)]][0] for c in text) * size / upem + tracking * (len(text) - 1)


display, _ = build_font("newsreader-latin-normal.woff2", {"wght": 500, "opsz": 72}, NAME)
serif, _ = build_font("newsreader-latin-normal.woff2", {"wght": 400, "opsz": 36}, LEAD)
italic, _ = build_font("newsreader-latin-italic.woff2", {"wght": 500, "opsz": 48}, LEAD_EM + MARK)
sans, sans_m = build_font("manrope-latin.woff2", {"wght": 600}, EYEBROW + "".join(STAGES))

# Pipeline geometry: five pills spread across the banner, measured from the real font.
PILL_SIZE, PILL_PAD, PILL_H, PIPE_Y = 15, 22, 40, 326
x0, x1 = 80, W - 80
widths = [text_width(sans_m, s, PILL_SIZE, 0.3) + 2 * PILL_PAD for s in STAGES]
gap = (x1 - x0 - sum(widths)) / (len(STAGES) - 1)
pills, x = [], x0
for label, w in zip(STAGES, widths):
    pills.append((label, x, w))
    x += w + gap
start_c = pills[0][1] + pills[0][2] / 2
end_c = pills[-1][1] + pills[-1][2] / 2
travel = end_c - start_c


def svg(t):
    pill_svg = []
    for i, (label, px, pw) in enumerate(pills):
        cls = "pill first" if i == 0 else "pill last" if i == len(pills) - 1 else "pill"
        pill_svg.append(
            f'<g class="{cls}"><rect x="{px:.1f}" y="{PIPE_Y - PILL_H / 2}" width="{pw:.1f}" '
            f'height="{PILL_H}" rx="{PILL_H / 2}"/>'
            f'<text x="{px + pw / 2:.1f}" y="{PIPE_Y + 5}" text-anchor="middle">{label}</text></g>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Michael DeCero. I take AI from prototype to production.">
<style>
@font-face{{font-family:"ND";src:url(data:font/woff2;base64,{display}) format("woff2")}}
@font-face{{font-family:"NS";src:url(data:font/woff2;base64,{serif}) format("woff2")}}
@font-face{{font-family:"NI";src:url(data:font/woff2;base64,{italic}) format("woff2")}}
@font-face{{font-family:"MS";src:url(data:font/woff2;base64,{sans}) format("woff2")}}
.eyebrow{{font:14px "MS",sans-serif;letter-spacing:3px;fill:{t['accent']}}}
.name{{font:84px "ND",Georgia,serif;fill:{t['ink']};letter-spacing:-1px}}
.lead{{font:36px "NS",Georgia,serif;fill:{t['ink2']}}}
.em{{font:36px "NI",Georgia,serif;font-style:italic;fill:{t['accent']}}}
.mark{{font:260px "NI",Georgia,serif;font-style:italic;fill:none;stroke:{t['ink']};stroke-width:1.2;opacity:{t['mark_opacity']}}}
.pill rect{{fill:{t['elevated']};stroke:{t['ink']};stroke-opacity:.16}}
.pill text{{font:{PILL_SIZE}px "MS",sans-serif;letter-spacing:.3px;fill:{t['ink2']}}}
.pill.first rect{{stroke:{t['amber']};stroke-opacity:.7}}
.pill.first text{{fill:{t['amber']}}}
.pill.last rect{{stroke:{t['accent']};stroke-opacity:.9;animation:arrive 6s ease-in-out infinite}}
.pill.last text{{fill:{t['accent']}}}
.flow{{stroke-dasharray:3 9;animation:flow 1.4s linear infinite}}
.packet{{animation:travel 6s cubic-bezier(.65,0,.35,1) infinite}}
@keyframes flow{{to{{stroke-dashoffset:-12}}}}
@keyframes travel{{0%{{transform:translateX(0);opacity:0}}6%{{opacity:1}}70%{{transform:translateX({travel:.1f}px);opacity:1}}82%,100%{{transform:translateX({travel:.1f}px);opacity:0}}}}
@keyframes arrive{{0%,64%{{fill:{t['elevated']};fill-opacity:1;filter:none}}74%{{fill:{t['accent']};fill-opacity:.18;filter:url(#glow)}}100%{{fill:{t['elevated']};fill-opacity:1;filter:none}}}}
@media (prefers-reduced-motion:reduce){{.flow,.packet,.pill.last rect{{animation:none}}.packet{{opacity:0}}}}
</style>
<defs>
<radialGradient id="cool" cx="{W - 140}" cy="30" r="560" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t['accent_soft']}" stop-opacity="{t['glow']}"/><stop offset="1" stop-color="{t['accent_soft']}" stop-opacity="0"/></radialGradient>
<radialGradient id="warm" cx="60" cy="{H + 40}" r="460" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t['amber']}" stop-opacity="{t['warm']}"/><stop offset="1" stop-color="{t['amber']}" stop-opacity="0"/></radialGradient>
<linearGradient id="wire" x1="{start_c:.1f}" x2="{end_c:.1f}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t['amber']}"/><stop offset="1" stop-color="{t['accent']}"/></linearGradient>
<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{t['ink']}" fill-opacity="{t['dot_opacity']}"/></pattern>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" fill="{t['bg']}"/>
<rect width="{W}" height="{H}" fill="url(#dots)"/>
<rect width="{W}" height="{H}" fill="url(#cool)"/>
<rect width="{W}" height="{H}" fill="url(#warm)"/>
<text class="mark" x="{W - 70}" y="250" text-anchor="end">{MARK}</text>
<text class="eyebrow" x="82" y="86">{EYEBROW.replace(chr(183), '&#183;')}</text>
<text class="name" x="76" y="172">{NAME}</text>
<text x="80" y="232"><tspan class="lead">{LEAD}</tspan><tspan class="em">{LEAD_EM}</tspan></text>
<line x1="{start_c:.1f}" y1="{PIPE_Y}" x2="{end_c:.1f}" y2="{PIPE_Y}" stroke="{t['ink']}" stroke-opacity=".14" stroke-width="2"/>
<line class="flow" x1="{start_c:.1f}" y1="{PIPE_Y}" x2="{end_c:.1f}" y2="{PIPE_Y}" stroke="url(#wire)" stroke-opacity=".75" stroke-width="2"/>
<g class="packet"><circle cx="{start_c:.1f}" cy="{PIPE_Y}" r="6" fill="{t['accent']}" filter="url(#glow)"/></g>
{''.join(pill_svg)}
</svg>
"""


OUT.mkdir(exist_ok=True)
for name, theme in THEMES.items():
    path = OUT / f"banner-{name}.svg"
    path.write_text(svg(theme))
    print(f"{path.name}: {path.stat().st_size // 1024} KB")
