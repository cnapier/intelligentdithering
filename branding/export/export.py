"""Intelligent Dithering export pack generator."""
import numpy as np, cairosvg, os, json, shutil
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from PIL import Image

ROOT = "/home/claude/logo/export"
shutil.rmtree(ROOT, ignore_errors=True)
for d in ("logo", "youtube", "beehiiv", "web", "social"):
    os.makedirs(f"{ROOT}/{d}", exist_ok=True)

TEAL = "#1A9BAA"; INK = "#0F1B24"; PAPER = "#F4F1EA"; WHITE = "#FFFFFF"
TAGLINE = "Overthinking technology so you don’t have to"

# ---------------- mark ----------------
HEAD_D = ("M 54 174 C 55 162 56 148 58 135 C 60 118 42 100 40 72 C 38 40 66 14 100 14 "
          "C 134 14 158 40 158 66 C 158 72 156 76 158 80 C 161 88 166 100 168 106 "
          "C 170 110 166 112 160 112 C 158 115 159 118 157 120 C 155 121 155 122 156 124 "
          "C 158 126 158 129 155 131 C 153 134 155 139 154 143 C 152 149 146 151 138 151 "
          "C 130 151 124 151 122 156 L 121 174 Z")
BBOX = (38.5, 14, 170, 174)          # x0, y0, x1, y1 of the head in mark units

def bayer(n):
    m = np.array([[0]])
    while m.shape[0] < n:
        m = np.block([[4*m, 4*m+2], [4*m+3, 4*m+1]])
    return (m + 0.5) / (n*n)
B = bayer(8)
clamp = lambda v: max(0.0, min(1.0, v))
ss = lambda t: (lambda t: t*t*(3-2*t))(clamp(t))
density = lambda x, y: 1.0 if x >= 112.5 else min(0.999, 0.25 + 0.75*ss((x-36)/70)**0.55)

def _cells(N=80):
    s = 200/N; out = []
    for j in range(N):
        for i in range(N):
            x, y = (i+0.5)*s, (j+0.5)*s
            v = density(x, y)
            if v >= 1: continue
            if v > 0.94 or v > B[j % 8, i % 8]:
                out.append(f'<rect x="{i*s:g}" y="{j*s:g}" width="{s:g}" height="{s:g}"/>')
    return "".join(out)
CELLS = _cells()
_uid = [0]

def mark(fg, x, y, h, dither=True):
    """Head mark, top-left of its bbox at (x,y), bbox height h. Returns SVG fragment."""
    k = h / (BBOX[3]-BBOX[1])
    tx, ty = x - BBOX[0]*k, y - BBOX[1]*k
    if not dither:
        return f'<path transform="translate({tx:.3f},{ty:.3f}) scale({k:.5f})" fill="{fg}" d="{HEAD_D}"/>'
    _uid[0] += 1; cid = f"h{_uid[0]}"
    return (f'<g transform="translate({tx:.3f},{ty:.3f}) scale({k:.5f})">'
            f'<clipPath id="{cid}"><path d="{HEAD_D}"/></clipPath>'
            f'<g clip-path="url(#{cid})" fill="{fg}"><rect x="112.5" y="0" width="100" height="200"/>'
            f'<g shape-rendering="crispEdges">{CELLS}</g></g></g>')

def mark_w(h): return h * (BBOX[2]-BBOX[0]) / (BBOX[3]-BBOX[1])

# ---------------- outlined text ----------------
FONTS = {"xbold": "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
         "medium": "/usr/share/fonts/opentype/inter/Inter-Medium.otf"}
_fc = {}
def _font(w):
    if w not in _fc:
        data = open(FONTS[w], "rb").read()
        _fc[w] = (hb.Font(hb.Face(data)), TTFont(FONTS[w]))
    return _fc[w]

def text(s, x, baseline, size, fill, weight="xbold", tracking=-0.023):
    """Outlined text as an SVG path. tracking in em. Returns (svg, width, cap_height)."""
    hfont, tt = _font(weight)
    upem = tt["head"].unitsPerEm; gs = tt.getGlyphSet()
    buf = hb.Buffer(); buf.add_str(s); buf.guess_segment_properties()
    hb.shape(hfont, buf, {"kern": True, "liga": True})
    order = tt.getGlyphOrder(); k = size/upem; pen_x = 0; parts = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        sp = SVGPathPen(gs)
        gs[name].draw(TransformPen(sp, (k, 0, 0, -k, x + (pen_x + pos.x_offset)*k, baseline)))
        d = sp.getCommands()
        if d: parts.append(d)
        pen_x += pos.x_advance + tracking*upem
    width = (pen_x - tracking*upem) * k
    cap = tt["OS/2"].sCapHeight * k
    return f'<path fill="{fill}" d="{" ".join(parts)}"/>', width, cap

def text_w(s, size, weight="xbold", tracking=-0.023): return text(s, 0, 0, size, "#000", weight, tracking)[1]

# ---------------- composition helpers ----------------
def svg_doc(w, h, body, bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{b}{body}</svg>'

def save(path, svg, png_w=None, png_path=None):
    full = f"{ROOT}/{path}"
    if path.endswith(".svg"):
        open(full, "w").write(svg)
        if png_w:
            cairosvg.svg2png(bytestring=svg.encode(), write_to=png_path and f"{ROOT}/{png_path}" or full[:-4]+".png", output_width=png_w)
    else:
        cairosvg.svg2png(bytestring=svg.encode(), write_to=full, output_width=png_w)

def square(size, bg, fg, frac=0.70, dither=True, dy=0.0):
    h = size*frac; w = mark_w(h)
    return svg_doc(size, size, mark(fg, (size-w)/2, (size-h)/2 + dy*size, h, dither), bg)

def stacked(bg, word_fg, pad=24):
    """Mark + two-line wordmark. Returns svg, w, h."""
    size = 80; lh = size*1.0
    w1 = text_w("Intelligent", size); w2 = text_w("Dithering", size)
    cap = text("I", 0, 0, size, "#000")[2]
    block_h = lh + cap              # top of line1 cap to baseline of line2
    mh = block_h * 1.32; mw = mark_w(mh); gap = size*0.42
    W = pad*2 + mw + gap + max(w1, w2); H = pad*2 + mh
    tx = pad + mw + gap; top = pad + (mh - block_h)/2
    t1 = text("Intelligent", tx, top+cap, size, word_fg)[0]
    t2 = text("Dithering", tx, top+cap+lh, size, TEAL)[0]
    body = mark(TEAL, pad, pad, mh) + t1 + t2
    return svg_doc(round(W), round(H), body, bg), W, H

def inline(bg, word_fg, pad=20):
    size = 64
    cap = text("I", 0, 0, size, "#000")[2]
    w1 = text_w("Intelligent ", size)
    mh = cap*1.75; mw = mark_w(mh); gap = size*0.32
    W = pad*2 + mw + gap + text_w("Intelligent Dithering", size); H = pad*2 + mh
    tx = pad + mw + gap; base = pad + mh/2 + cap/2
    t1 = text("Intelligent", tx, base, size, word_fg)[0]
    t2 = text("Dithering", tx + w1, base, size, TEAL)[0]
    return svg_doc(round(W), round(H), mark(TEAL, pad, pad, mh) + t1 + t2, bg), W, H

def inner(svgdoc):
    """Strip outer <svg> so a composed doc can be nested."""
    return svgdoc[svgdoc.index(">")+1:-6]

# ================= LOGO =================
for name, fg in (("teal", TEAL), ("white", WHITE), ("ink", INK)):
    s = square(1024, None, fg, frac=0.86)
    save(f"logo/mark-{name}-transparent.svg", s, 1024)
for name, bg in (("on-dark", INK), ("on-light", PAPER)):
    save(f"logo/mark-{name}.svg", square(1024, bg, TEAL, frac=0.70), 1024)
for name, bg, fg in (("on-light", PAPER, INK), ("on-dark", INK, PAPER),
                     ("transparent-dark-text", None, INK), ("transparent-light-text", None, PAPER)):
    s, W, H = stacked(bg, fg); save(f"logo/lockup-stacked-{name}.svg", s, round(W*3))
    s, W, H = inline(bg, fg);  save(f"logo/lockup-inline-{name}.svg", s, round(W*3))

# ================= YOUTUBE =================
save("youtube/avatar-800-dark.png", square(800, INK, TEAL, frac=0.62, dy=0.01), 800)
save("youtube/avatar-800-light.png", square(800, PAPER, TEAL, frac=0.62, dy=0.01), 800)
save("youtube/watermark-150.png", square(150, None, WHITE, frac=0.86), 150)

def banner(bg, word_fg):
    W, H = 2560, 1440
    ls, lw, lh = stacked(None, word_fg, pad=0)
    sc = 290/lh          # lockup 290px tall: fits inside the 1546x423 all-device safe area
    tag_size = 46
    tw = text_w(TAGLINE, tag_size, "medium", 0)
    x = (W - lw*sc)/2; y = (H - 290)/2 - 40
    body = (f'<g transform="translate({x:.1f},{y:.1f}) scale({sc:.4f})">{inner(ls)}</g>'
            + text(TAGLINE, (W-tw)/2, y + 290 + 78, tag_size, TEAL if bg == INK else "#5B6770", "medium", 0)[0])
    # subtle dither strip across the bottom of the full-width (TV) area
    return svg_doc(W, H, body, bg)
save("youtube/banner-2560x1440-dark.png", banner(INK, PAPER), 2560)
save("youtube/banner-2560x1440-light.png", banner(PAPER, INK), 2560)

# ================= BEEHIIV =================
save("beehiiv/publication-logo-1000-dark.png", square(1000, INK, TEAL, frac=0.66), 1000)
save("beehiiv/publication-logo-1000-light.png", square(1000, PAPER, TEAL, frac=0.66), 1000)
def header(bg, fg, W=1200, H=300):
    ls, lw, lh = inline(None, fg, pad=0); sc = 96/lh
    return svg_doc(W, H, f'<g transform="translate({(W-lw*sc)/2:.1f},{(H-96)/2:.1f}) scale({sc:.4f})">{inner(ls)}</g>', bg)
save("beehiiv/email-header-1200x300-light.png", header(PAPER, INK), 2400)
save("beehiiv/email-header-1200x300-dark.png", header(INK, PAPER), 2400)

# ================= SOCIAL / OG =================
def card(W, H, bg=INK, fg=PAPER, lock_h=None):
    ls, lw, lh = stacked(None, fg, pad=0)
    lock_h = lock_h or H*0.36; sc = lock_h/lh
    tag_size = W*0.03
    tw = text_w(TAGLINE, tag_size, "medium", 0)
    y = (H - lock_h - tag_size*2.4)/2
    body = (f'<g transform="translate({(W-lw*sc)/2:.1f},{y:.1f}) scale({sc:.4f})">{inner(ls)}</g>'
            + text(TAGLINE, (W-tw)/2, y + lock_h + tag_size*2.2, tag_size, TEAL, "medium", 0)[0])
    return svg_doc(W, H, body, bg)
og = card(1200, 630)
save("social/og-card-1200x630.png", og, 1200)
save("web/og-image.png", og, 1200)
save("social/square-post-1080.png", card(1080, 1080, lock_h=300), 1080)

# ================= WEB / FAVICONS =================
# Small sizes: solid silhouette (dither turns to mush below ~48px)
fav_svg = square(64, None, TEAL, frac=0.94, dither=False)
open(f"{ROOT}/web/favicon.svg", "w").write(fav_svg)
for sz in (16, 32, 48):
    save(f"web/favicon-{sz}.png", square(sz*8, None, TEAL, frac=0.94, dither=False), sz)
ims = [Image.open(f"{ROOT}/web/favicon-{sz}.png").convert("RGBA") for sz in (16, 32, 48)]
ims[2].save(f"{ROOT}/web/favicon.ico", sizes=[(16,16),(32,32),(48,48)], append_images=ims[:2])
save("web/apple-touch-icon.png", square(180, INK, TEAL, frac=0.66, dither=True), 180)
save("web/android-chrome-192.png", square(192, INK, TEAL, frac=0.62), 192)
save("web/android-chrome-512.png", square(512, INK, TEAL, frac=0.62), 512)
s, W, H = inline(None, INK, pad=0);  open(f"{ROOT}/web/logo-header.svg", "w").write(s)
s, W, H = inline(None, PAPER, pad=0); open(f"{ROOT}/web/logo-header-light-text.svg", "w").write(s)
json.dump({"name": "Intelligent Dithering", "short_name": "Int. Dithering",
           "icons": [{"src": "/android-chrome-192.png", "sizes": "192x192", "type": "image/png"},
                     {"src": "/android-chrome-512.png", "sizes": "512x512", "type": "image/png"}],
           "theme_color": INK, "background_color": INK, "display": "standalone"},
          open(f"{ROOT}/web/site.webmanifest", "w"), indent=2)
print("done")
