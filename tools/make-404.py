"""Generate the dithered 404 background (static/img/404-bg-dither.png).

Same circuit-board style and palette as tools/make-header.py, but full-screen
(1920x1080) with a "broken connection": the main trace across the page is
snapped in the middle, with frayed ends and sparks jumping the gap.
Run from the site root:  python3 tools/make-404.py   (needs numpy + Pillow)
"""
import numpy as np, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
random.seed(404); np.random.seed(404)
OUT = sys.argv[1] if len(sys.argv) > 1 else "static/img/404-bg-dither.png"
S = 3; W, H = 1920 // S, 1080 // S
G = 8  # routing grid
img = Image.new("L", (W, H), 0); d = ImageDraw.Draw(img)
spark = Image.new("L", (W, H), 0); sd = ImageDraw.Draw(spark)   # extra-bright layer

MY = int(H * 0.60)            # main trace height
GAP0, GAP1 = int(W * 0.46), int(W * 0.54)

def route(x, y, steps):
    pts = [(x, y)]; dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
    for _ in range(steps):
        if random.random() < 0.25:
            dx, dy = random.choice([(dx, dy), (dx or random.choice([-1, 1]), dy or random.choice([-1, 1]))])
            if dx and dy and random.random() < 0.5: dx, dy = (dx, 0) if random.random() < .5 else (0, dy)
        n = random.randint(2, 7); x += dx * G * n; y += dy * G * n; pts.append((x, y))
    return pts

# Background traces – kept out of the top band (title) and the gap area
for i in range(230):
    x = random.randrange(0, W, G); y = random.randrange(0, H, G)
    pts = route(x, y, random.randint(3, 9))
    if any(abs(px - W / 2) < 70 and abs(py - MY) < 45 for px, py in pts): continue
    if any(py < H * 0.20 and abs(px - W / 2) < 190 for px, py in pts): continue
    b = random.randint(70, 170)
    d.line(pts, fill=b, width=random.choice([1, 1, 2]))
    for p in (pts[0], pts[-1]):
        r = random.choice([2, 3]); d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], outline=230, fill=b // 3)

# Chips (one carries a "404" silkscreen)
chips = [(60, int(H*0.70), 70, 40), (W-150, int(H*0.30), 64, 36), (120, int(H*0.30), 46, 30),
         (W-120, int(H*0.80), 52, 30), (int(W*0.30), int(H*0.82), 40, 26), (int(W*0.66), int(H*0.74), 58, 34)]
for cx, cy, w, h in chips:
    d.rectangle([cx, cy, cx+w, cy+h], fill=55, outline=210)
    for k in range(cx+4, cx+w-2, 5): d.line([k, cy-4, k, cy], fill=200); d.line([k, cy+h, k, cy+h+4], fill=200)
try:
    f = ImageFont.truetype("DejaVuSansMono-Bold.ttf", 15)
except OSError:
    f = ImageFont.load_default()
cx, cy, w, h = chips[0]
d.text((cx + w/2, cy + h/2), "404", font=f, fill=235, anchor="mm")

# Main bus: thick trace across the page, snapped in the middle
for x0, x1 in ((0, GAP0), (GAP1, W)):
    d.line([(x0, MY), (x1, MY)], fill=210, width=3)
    d.line([(x0, MY - 7), (x1, MY - 7)], fill=120, width=1)
    d.line([(x0, MY + 7), (x1, MY + 7)], fill=120, width=1)
# frayed copper at the break
for end, sgn in ((GAP0, 1), (GAP1, -1)):
    for k in range(5):
        L = random.randint(4, 12); ang = random.uniform(-0.9, 0.9)
        d.line([(end, MY), (end + sgn * L * np.cos(ang), MY + L * np.sin(ang))], fill=200, width=1)
    r = 4; sd.ellipse([end-r, MY-r, end+r, MY+r], fill=255)
# sparks jumping the gap: jagged arcs + scattered embers
for _ in range(3):
    pts = [(GAP0 + 3, MY)]
    for t in np.linspace(0.15, 0.85, 6):
        pts.append((GAP0 + (GAP1 - GAP0) * t, MY + random.randint(-9, 9)))
    pts.append((GAP1 - 3, MY))
    sd.line(pts, fill=255, width=1)
for _ in range(40):
    a = random.uniform(0, 2 * np.pi); rr = random.uniform(4, 34)
    px = W / 2 + rr * np.cos(a); py = MY + rr * np.sin(a) * 0.8
    s = random.choice([0, 1]); sd.rectangle([px, py, px + s, py + s], fill=255)

# Tone mapping + glow (as make-header.py)
a = np.asarray(img, dtype=float) / 255
glow = np.asarray(img.filter(ImageFilter.GaussianBlur(6)), dtype=float) / 255
sp = np.asarray(spark, dtype=float) / 255
spg = np.asarray(spark.filter(ImageFilter.GaussianBlur(10)), dtype=float) / 255
yy, xx = np.mgrid[0:H, 0:W]
grad = 0.08 + 0.12 * (yy / H)
title = np.exp(-(((yy - H * 0.13) / (H * 0.10)) ** 2)) * np.exp(-(((xx - W / 2) / (W * 0.24)) ** 2))
L = np.clip(grad + (a * 0.85 + glow * 1.1) * (1 - 0.75 * title) + sp * 1.0 + spg * 1.6, 0, 1)

def bayer(n):
    m = np.array([[0, 2], [3, 1]])
    while m.shape[0] < n: m = np.block([[4*m, 4*m+2], [4*m+3, 4*m+1]])
    return (m + 0.5) / m.size
B = np.tile(bayer(8), (H // 8 + 1, W // 8 + 1))[:H, :W]
pal = np.array([(8, 12, 24), (18, 36, 58), (24, 92, 110), (40, 170, 170), (240, 180, 70)], dtype=np.uint8)
lv = L * (len(pal) - 1); idx = np.floor(lv + (B - 0.5) * 0.999 + 0.5).astype(int).clip(0, len(pal) - 1)
out = Image.fromarray(pal[idx]).resize((W * S, H * S), Image.NEAREST)
out.save(OUT, optimize=True)
print(OUT, out.size)
