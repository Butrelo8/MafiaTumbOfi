"""Sticker art for the design pass (mothership brief 03:40, owner: "so they stand out as real stickies"). Each sticker is its own
piece of illustration and lettering with its own shape and finish; references.md › Stickers, design pass. Two directions:

  A "puesto de merch": four separate pieces, bold-pop colour (the bed props' pink/lime/turquoise), newish.
  B "troca": black and gold (DESIGN.md --gold/--ink/--cap), sun-faded, torn, stacked in one corner like a tailgate collection.

Per sticker it writes tmp/utileria/calcas3/<id>.png (RGBA, the die-cut is the alpha, white border included) and <id>-n.png
(tangent-space normal map: the raised edge from the alpha), plus calcas3.json (size in m, finish, glyph slot). The glyph slot is
left empty in the art (clear space = half the glyph each side, §2); utileria.py puts the glyph on its own upright quad.

  uv run -q --with numpy --with pillow python -I blender/calcas_arte.py
"""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "tmp", "utileria", "calcas3")
FONT = "/mnt/c/Windows/Fonts/SairaCondensed-{}.ttf"  # DESIGN.md display face (Saira Condensed, caps, slanted)
PX = 4  # px per mm
INK, WHITE = (20, 18, 16, 255), (246, 244, 238, 255)
ROSA, LIMA, TURQ, LIMON, NARANJA = (255, 58, 140, 255), (140, 230, 25, 255), (25, 190, 215, 255), (255, 210, 30, 255), (242, 90, 25, 255)
GOLD, CREMA, CAP = (231, 181, 81, 255), (241, 238, 233, 255), (17, 15, 10, 255)  # DESIGN.md --gold, --ink, --cap
GLIFO_MM = 34  # glyph edge; its slot is 2× (clear space half the glyph on every side)


def f(w, px):
    return ImageFont.truetype(FONT.format(w), px)


def lienzo(w_mm, h_mm):
    return Image.new("RGBA", (w_mm * PX, h_mm * PX), (0, 0, 0, 0))


def mascara(size, dibujo):
    m = Image.new("L", size, 0)
    dibujo(ImageDraw.Draw(m))
    return m


def pegar(img, m, color, borde=0, extr=0):
    """Fill a mask in colour with an ink outline (borde px) and a solid ink extrusion stepping down-right (bold-pop)."""
    if extr:
        img.paste(INK, (extr, extr), m)
    if borde:
        img.paste(INK, (0, 0), m.filter(ImageFilter.MaxFilter(borde * 2 + 1)))
    img.paste(color, (0, 0), m)


def letras(img, texto, cx, cy, alto, color, peso="Black", incl=0.18, borde=0, ancho=None):
    """Caps in Saira Condensed, slanted like the logo (DESIGN.md › Type), fitted to `ancho` px if given."""
    fn = f(peso, alto)
    l, t, r, b = fn.getbbox(texto)
    if ancho and r - l > ancho:
        fn = f(peso, int(alto * ancho / (r - l)))
        l, t, r, b = fn.getbbox(texto)
    w, h = r - l + int(alto * incl) + 8, b - t + 8
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((4 - l + int(alto * incl), 4 - t), texto, font=fn, fill=255)
    m = m.transform(m.size, Image.AFFINE, (1, incl, -incl * h, 0, 1, 0), Image.BICUBIC)
    full = Image.new("L", img.size, 0)
    full.paste(m, (int(cx - w / 2), int(cy - h / 2)))
    pegar(img, full, color, borde)


def fresa(img, cx, cy, r, borde, extr, cuerpo=ROSA, hoja=LIMA, semilla=LIMON):
    """PUTIFRESA strawberry with sunglasses (escenas-plan §2 subjects)."""
    s = img.size
    def cuerpo_m(d):
        d.ellipse((cx - r, cy - r * 0.85, cx + r, cy + r * 0.55), fill=255)
        d.polygon([(cx - r * 0.97, cy - r * 0.1), (cx + r * 0.97, cy - r * 0.1), (cx + r * 0.25, cy + r * 1.15), (cx - r * 0.25, cy + r * 1.15)], fill=255)
        d.ellipse((cx - r * 0.3, cy + r * 0.85, cx + r * 0.3, cy + r * 1.3), fill=255)
    pegar(img, mascara(s, cuerpo_m), cuerpo, borde, extr)
    d = ImageDraw.Draw(img)
    for i in range(14):
        a, k = i * 2.4, 0.3 + 0.6 * ((i * 0.37) % 1)
        x, y = cx + math.cos(a) * r * k * 0.8, cy + r * 0.2 + math.sin(a) * r * k * 0.7
        d.ellipse((x - r * 0.04, y - r * 0.06, x + r * 0.04, y + r * 0.06), fill=semilla)
    hojas = lambda dd: [dd.polygon([(cx, cy - r * 0.75), (cx + math.cos(a) * r * 0.75, cy - r * 0.8 + math.sin(a) * r * 0.35),
                                    (cx + math.cos(a + 0.5) * r * 0.3, cy - r * 0.85)], fill=255) for a in np.linspace(math.pi * 0.9, math.pi * 2.1, 5)]
    pegar(img, mascara(s, hojas), hoja, max(2, borde // 2))
    for sx in (-1, 1):  # sunglasses
        x0 = cx + sx * r * 0.08 if sx > 0 else cx - r * 0.66
        d.rounded_rectangle((x0, cy - r * 0.35, x0 + r * 0.58, cy - r * 0.02), r * 0.12, fill=INK)
        d.line((x0 + r * 0.12, cy - r * 0.27, x0 + r * 0.28, cy - r * 0.27), fill=(255, 255, 255, 220), width=max(2, int(r * 0.05)))
    d.line((cx - r * 0.1, cy - r * 0.27, cx + r * 0.1, cy - r * 0.27), fill=INK, width=max(3, int(r * 0.06)))
    d.arc((cx - r * 0.3, cy - r * 0.1, cx + r * 0.3, cy + r * 0.35), 20, 160, fill=INK, width=max(3, int(r * 0.07)))


def sombrero(img, cx, cy, r, borde, extr, ala=LIMON, banda=ROSA):
    s = img.size
    pegar(img, mascara(s, lambda d: (d.ellipse((cx - r, cy - r * 0.18, cx + r, cy + r * 0.32), fill=255),
                                      d.polygon([(cx - r * 0.42, cy + r * 0.05), (cx - r * 0.3, cy - r * 0.62), (cx, cy - r * 0.72),
                                                 (cx + r * 0.3, cy - r * 0.62), (cx + r * 0.42, cy + r * 0.05)], fill=255))), ala, borde, extr)
    d = ImageDraw.Draw(img)
    d.polygon([(cx - r * 0.4, cy - r * 0.08), (cx - r * 0.36, cy - r * 0.26), (cx + r * 0.36, cy - r * 0.26), (cx + r * 0.4, cy - r * 0.08)], fill=banda)
    for i in range(7):  # zigzag stitch on the band
        x = cx - r * 0.33 + i * r * 0.11
        d.line((x, cy - r * 0.22, x + r * 0.055, cy - r * 0.12, x + r * 0.11, cy - r * 0.22), fill=INK, width=max(2, borde // 3))
    d.arc((cx - r * 0.85, cy - r * 0.1, cx + r * 0.85, cy + r * 0.25), 15, 165, fill=INK, width=max(2, borde // 2))


def casete(img, cx, cy, w, borde, extr, cuerpo=TURQ, etiqueta=CREMA):
    h = w * 0.62
    s = img.size
    pegar(img, mascara(s, lambda d: d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), w * 0.06, fill=255)), cuerpo, borde, extr)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((cx - w * 0.4, cy - h * 0.38, cx + w * 0.4, cy + h * 0.12), w * 0.03, fill=etiqueta, outline=INK, width=max(2, borde // 2))
    for sx in (-1, 1):
        x = cx + sx * w * 0.2
        d.ellipse((x - w * 0.09, cy - h * 0.2, x + w * 0.09, cy + h * 0.04 + w * 0.0), fill=INK)
        d.ellipse((x - w * 0.04, cy - h * 0.13, x + w * 0.04, cy - h * 0.03), fill=etiqueta)
    d.polygon([(cx - w * 0.3, cy + h / 2), (cx - w * 0.22, cy + h * 0.25), (cx + w * 0.22, cy + h * 0.25), (cx + w * 0.3, cy + h / 2)], outline=INK, width=max(2, borde // 2))


def troquel(img, borde_mm, linea=(200, 197, 190, 255)):
    """Die-cut: the art's silhouette grown by a white vinyl border, rounded, with the faint cut line at the rim. Returns
    (image, pad px): the canvas grows by the border so the cut is never clipped flat at its edge."""
    pad = (borde_mm + 16) * PX  # beyond the closing's reach (border + 12 mm), or the cut is clipped flat
    big = Image.new("RGBA", (img.size[0] + 2 * pad, img.size[1] + 2 * pad), (0, 0, 0, 0))
    big.paste(img, (pad, pad))
    img, (W, H) = big, big.size
    a = img.split()[3].point(lambda v: 255 if v > 20 else 0)
    # one silhouette: grow by border + 12 mm on an 8× smaller mask, shrink back 12 mm (a closing that bridges the pieces),
    # holes filled, then a wide blur + threshold rounds the blocky steps into a smooth cut
    k8, c8 = borde_mm * PX // 8, 12 * PX // 8
    s = a.resize((W // 8, H // 8), Image.BOX).point(lambda v: 255 if v else 0)
    s = s.filter(ImageFilter.MaxFilter(2 * (k8 + c8) + 1)).filter(ImageFilter.MinFilter(2 * c8 + 1))
    ImageDraw.floodfill(s, (0, 0), 128)
    s = s.point(lambda v: 0 if v == 128 else 255)
    m = s.resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(PX * 5)).point(lambda v: 255 if v > 128 else 0)
    base = Image.new("RGBA", img.size, (0, 0, 0, 0))
    base.paste(linea, (0, 0), m)
    base.paste(WHITE, (0, 0), m.filter(ImageFilter.MinFilter(5)))
    base.alpha_composite(img)
    return base, pad


def gastar(img, sol=0.0, rasgado=0, rayones=0, semilla=1, evitar=None):
    """Wear: sun fade (ink pulled to a dusty grey and lifted), torn bites out of the rim, scuffs that show the white vinyl.
    `evitar` = (x0, y0, x1, y1) px kept clean: the glyph slot never wears (§2)."""
    rnd = random.Random(semilla)
    a = np.asarray(img).astype(np.float32)
    if sol:
        g = a[..., :3].mean(axis=2, keepdims=True)
        a[..., :3] = a[..., :3] * (1 - sol) + (g * 0.5 + np.array([158, 153, 145]) * 0.5) * sol
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    W, H = img.size
    alpha = img.split()[3]
    d = ImageDraw.Draw(img)
    fuera = lambda x, y: evitar and evitar[0] - 20 <= x <= evitar[2] + 20 and evitar[1] - 20 <= y <= evitar[3] + 20
    for _ in range(rayones):
        x, y = rnd.uniform(0.05, 0.95) * W, rnd.uniform(0.1, 0.9) * H
        if fuera(x, y):
            continue
        L, ang = rnd.uniform(0.04, 0.16) * W, rnd.uniform(-0.5, 0.5)
        d.line((x, y, x + L * math.cos(ang), y + L * math.sin(ang)), fill=(236, 232, 224, 200), width=rnd.choice((2, 3, 4)))
    img.putalpha(alpha)
    if rasgado:  # bites along the bottom-left rim (the curl corner side), never near the glyph
        m = ImageDraw.Draw(alpha)
        ys = np.where(np.asarray(alpha).max(axis=1) > 0)[0]
        for _ in range(rasgado):
            x = rnd.uniform(0.05, 0.45) * W
            col = np.where(np.asarray(alpha)[:, int(x)] > 0)[0]
            if not len(col) or fuera(x, col.max()):
                continue
            y, r = col.max(), rnd.uniform(5, 16)  # an irregular chip out of the rim, not a tooth
            m.polygon([(x + math.cos(t) * r * rnd.uniform(0.5, 1.1), y + math.sin(t) * r * rnd.uniform(0.5, 1.1) * 0.7)
                       for t in np.linspace(0, 2 * math.pi, 9)[:-1]], fill=0)
        img.putalpha(alpha)
    return img


def normal(img, mm=1.2, fuerza=6.0):
    """Raised edge: height = blurred alpha (vinyl thickness ramping over ~mm), normal from its gradient (Blender tangent space)."""
    h = np.asarray(img.split()[3].filter(ImageFilter.GaussianBlur(mm * PX))).astype(np.float32) / 255
    gy, gx = np.gradient(h)
    n = np.dstack((-gx * fuerza * PX, gy * fuerza * PX, np.ones_like(h)))
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8), "RGB")


def ranura(img, cx, cy):
    """Empty glyph slot: a clean field 2× the glyph (its clear space), returned as UV (0..1, V up) for utileria.py."""
    W, H = img.size
    return {"u": cx / W, "v": 1 - cy / H, "mm": GLIFO_MM}


# ---------------------------------------------------------------- the stickers
def a_instagram():
    """A1 die-cut gloss vinyl, fat white border: the strawberry over SÍGUENOS / EN INSTAGRAM, glyph slot on the right."""
    img = lienzo(240, 190)
    W, H = img.size
    fresa(img, W * 0.3, H * 0.43, W * 0.18, 12, 14)
    letras(img, "SÍGUENOS", W * 0.5, H * 0.79, int(H * 0.2), ROSA, borde=10, ancho=W * 0.82)
    letras(img, "EN INSTAGRAM", W * 0.47, H * 0.93, int(H * 0.08), INK, peso="Bold", incl=0.12, ancho=W * 0.55)
    g = (W * 0.76, H * 0.36)
    ImageDraw.Draw(img).ellipse((g[0] - GLIFO_MM * PX, g[1] - GLIFO_MM * PX, g[0] + GLIFO_MM * PX, g[1] + GLIFO_MM * PX), fill=WHITE)
    img, pad = troquel(img, 7)
    return img, ranura(img, g[0] + pad, g[1] + pad), "brillo"


def a_spotify():
    """A2 holographic round badge: cassette on a sun disc, ESCÚCHANOS ring, official Spotify icon at the bottom (vintage-emblem)."""
    img = lienzo(180, 180)
    W = img.size[0]
    d = ImageDraw.Draw(img)
    d.ellipse((0, 0, W - 1, W - 1), fill=(225, 225, 230, 255))  # holo silver field: the thin-film shader colours it
    d.ellipse((W * 0.06, W * 0.06, W * 0.94, W * 0.94), outline=INK, width=10)
    d.ellipse((W * 0.2, W * 0.12, W * 0.8, W * 0.72), fill=NARANJA)  # sun disc
    casete(img, W * 0.5, W * 0.42, W * 0.5, 9, 12)
    letras(img, "ESCÚCHANOS", W * 0.5, W * 0.18, int(W * 0.11), INK, ancho=W * 0.62)
    g = (W * 0.5, W * 0.8)
    d.ellipse((g[0] - GLIFO_MM * PX * 0.75, g[1] - GLIFO_MM * PX * 0.75, g[0] + GLIFO_MM * PX * 0.75, g[1] + GLIFO_MM * PX * 0.75), fill=(225, 225, 230, 255))
    return img, dict(ranura(img, *g), mm=GLIFO_MM * 0.7), "holo"


def a_youtube():
    """A3 classic oval bumper sticker on matte paper, sun-faded: MÍRANOS / EN YOUTUBE beside the MT monogram."""
    img = lienzo(320, 140)
    W, H = img.size
    d = ImageDraw.Draw(img)
    d.ellipse((0, 0, W - 1, H - 1), fill=WHITE)
    d.ellipse((14, 14, W - 15, H - 15), fill=TURQ)
    d.ellipse((30, 30, W - 31, H - 31), outline=INK, width=8)
    letras(img, "MT", W * 0.19, H * 0.5, int(H * 0.36), LIMON, borde=8)
    letras(img, "MÍRANOS", W * 0.5, H * 0.42, int(H * 0.3), WHITE, borde=8, ancho=W * 0.36)
    letras(img, "EN YOUTUBE", W * 0.5, H * 0.66, int(H * 0.13), INK, peso="Bold", ancho=W * 0.3)
    g = (W * 0.8, H * 0.5)
    d.ellipse((g[0] - GLIFO_MM * PX * 0.9, g[1] - GLIFO_MM * PX * 0.9, g[0] + GLIFO_MM * PX * 0.9, g[1] + GLIFO_MM * PX * 0.9), fill=WHITE)
    G = (g[0] - GLIFO_MM * PX, g[1] - GLIFO_MM * PX, g[0] + GLIFO_MM * PX, g[1] + GLIFO_MM * PX)
    img = gastar(img, sol=0.35, rasgado=6, rayones=14, semilla=3, evitar=G)
    return img, dict(ranura(img, *g), mm=GLIFO_MM * 0.85), "mate"


def a_tiktok():
    """A4 letter-cut gold chrome vinyl, the troca tailgate lettering: sombrero + ANDAMOS EN TIKTOK, no background."""
    img = lienzo(340, 120)
    W, H = img.size
    sombrero(img, W * 0.15, H * 0.58, H * 0.38, 0, 0, ala=GOLD, banda=GOLD)
    letras(img, "ANDAMOS", W * 0.5, H * 0.4, int(H * 0.52), GOLD, ancho=W * 0.5)
    letras(img, "EN TIKTOK", W * 0.5, H * 0.82, int(H * 0.2), GOLD, peso="Bold", ancho=W * 0.32)
    g = (W * 0.86, H * 0.5)
    return img, dict(ranura(img, *g), mm=GLIFO_MM * 0.9), "cromo"


def b_instagram():
    """B1 gloss bumper strip, black and gold, the oldest: heavily sun-faded, scuffed, torn at the left end."""
    img = lienzo(330, 105)
    W, H = img.size
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W - 1, H - 1), fill=WHITE)
    d.rectangle((10, 10, W - 11, H - 11), fill=CAP)
    d.rectangle((22, 22, W - 23, H - 23), outline=GOLD, width=5)
    letras(img, "SÍGUENOS EN INSTAGRAM", W * 0.42, H * 0.5, int(H * 0.42), GOLD, ancho=W * 0.66)
    g = (W * 0.87, H * 0.5)
    G = (g[0] - GLIFO_MM * PX, g[1] - GLIFO_MM * PX, g[0] + GLIFO_MM * PX, g[1] + GLIFO_MM * PX)
    d.rectangle((G[0] + 30, 22, W - 23, H - 23), fill=CAP)
    img = gastar(img, sol=0.45, rasgado=9, rayones=22, semilla=5, evitar=G)
    return img, dict(ranura(img, *g), mm=GLIFO_MM * 0.8), "brillo"


def b_spotify():
    """B2 holographic oval, ESCÚCHANOS over the gold sun disc, Spotify icon on the right."""
    img = lienzo(230, 150)
    W, H = img.size
    d = ImageDraw.Draw(img)
    d.ellipse((0, 0, W - 1, H - 1), fill=(225, 225, 230, 255))
    d.ellipse((12, 12, W - 13, H - 13), outline=CAP, width=9)
    d.ellipse((W * 0.12, H * 0.16, W * 0.5, H * 0.74), fill=GOLD)
    casete(img, W * 0.31, H * 0.45, W * 0.3, 7, 9, cuerpo=CAP, etiqueta=GOLD)
    letras(img, "ESCÚCHANOS", W * 0.47, H * 0.85, int(H * 0.14), CAP, ancho=W * 0.6)
    g = (W * 0.73, H * 0.45)
    return img, dict(ranura(img, *g), mm=GLIFO_MM * 0.8), "holo"


def b_youtube():
    """B3 die-cut gloss vinyl, white border: the strawberry in gold and cream over MÍRANOS; overlaps B1's torn end."""
    img = lienzo(200, 200)
    W, H = img.size
    fresa(img, W * 0.38, H * 0.38, W * 0.24, 12, 14, cuerpo=GOLD, hoja=CREMA, semilla=CAP)
    letras(img, "MÍRANOS", W * 0.45, H * 0.8, int(H * 0.2), CAP, ancho=W * 0.8)
    letras(img, "EN YOUTUBE", W * 0.42, H * 0.93, int(H * 0.08), CAP, peso="Bold", ancho=W * 0.45)
    g = (W * 0.8, H * 0.6)
    ImageDraw.Draw(img).ellipse((g[0] - GLIFO_MM * PX * 0.8, g[1] - GLIFO_MM * PX * 0.8, g[0] + GLIFO_MM * PX * 0.8, g[1] + GLIFO_MM * PX * 0.8), fill=WHITE)
    img, pad = troquel(img, 6)
    g = (g[0] + pad, g[1] + pad)
    img = gastar(img, sol=0.15, rayones=6, semilla=7, evitar=(g[0] - 140, g[1] - 140, g[0] + 140, g[1] + 140))
    return img, dict(ranura(img, *g), mm=GLIFO_MM * 0.75), "brillo"


def b_tiktok():
    """B4 round matte paper badge, the newest: gold sombrero on black, ANDAMOS ring, slot at the bottom."""
    img = lienzo(150, 150)
    W = img.size[0]
    d = ImageDraw.Draw(img)
    d.ellipse((0, 0, W - 1, W - 1), fill=CREMA)
    d.ellipse((W * 0.05, W * 0.05, W * 0.95, W * 0.95), fill=CAP)
    sombrero(img, W * 0.5, W * 0.42, W * 0.3, 6, 0, ala=GOLD, banda=CREMA)
    letras(img, "ANDAMOS", W * 0.5, W * 0.17, int(W * 0.12), GOLD, ancho=W * 0.55)
    g = (W * 0.5, W * 0.76)
    d.ellipse((g[0] - GLIFO_MM * PX * 0.6, g[1] - GLIFO_MM * PX * 0.6, g[0] + GLIFO_MM * PX * 0.6, g[1] + GLIFO_MM * PX * 0.6), fill=CREMA)
    return img, dict(ranura(img, *g), mm=GLIFO_MM * 0.6), "mate"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    for fn in (a_instagram, a_spotify, a_youtube, a_tiktok, b_instagram, b_spotify, b_youtube, b_tiktok):
        nombre = fn.__name__.replace("_", "-")
        img, glifo, acabado = fn()
        img.save(os.path.join(OUT, nombre + ".png"))
        normal(img).save(os.path.join(OUT, nombre + "-n.png"))
        meta[nombre] = {"w": img.size[0] / PX / 1000, "h": img.size[1] / PX / 1000, "acabado": acabado, "glifo": glifo}
        print(nombre, img.size, acabado)
    json.dump(meta, open(os.path.join(OUT, "calcas3.json"), "w"), indent=1)
    hoja = Image.new("RGBA", (2 * 1400, 4 * 820), (40, 40, 44, 255))  # contact sheet of the art (overview only)
    for i, n in enumerate(meta):
        im = Image.open(os.path.join(OUT, n + ".png"))
        im.thumbnail((1300, 760))
        hoja.alpha_composite(im, ((i // 4) * 1400 + 50, (i % 4) * 820 + 30))
    hoja.convert("RGB").resize((1400, 1640)).save(os.path.join(OUT, "hoja-arte.jpg"), quality=85)
