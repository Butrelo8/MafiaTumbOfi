"""Dash infotainment screen face (utileria radio round 2): one static frame of the release browser, as an image texture.
Cover + title + ‹ › + Escuchar, DESIGN.md type (Saira Condensed 800 slanted, Saira 400/600) and colours, square shapes.

  uv run -q --with pillow --with fonttools --with brotli python -I blender/pantalla_tablero.py [index=0]

Writes tmp/utileria/pantalla-ancha.png (3:1, the floating MBUX-style screen) and pantalla-comand.png (16:9, the screen in
the centre stack where the G63's COMAND unit sits). Fonts: the @fontsource woff2 files converted to TTF in tmp/fuentes.
"""
import json, os, sys
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "tmp", "utileria")
FD = os.path.join(REPO, "tmp", "fuentes")
INK, MUTED, GOLD, CAP, GOLD_DEEP, BG = "#f1eee9", "#c1bdb7", "#e7b551", "#110f0a", "#a8792f", "#000000"
LINE = "#32312c"  # --line (14 % white) flattened over --cap


def fuente(paquete, archivo, px):
    ttf = os.path.join(FD, archivo + ".ttf")
    if not os.path.exists(ttf):
        os.makedirs(FD, exist_ok=True)
        f = TTFont(os.path.join(REPO, "node_modules", "@fontsource", paquete, "files", archivo + ".woff2"))
        f.flavor = None
        f.save(ttf)
    return ImageFont.truetype(ttf, px)


def display(px):
    return fuente("saira-condensed", "saira-condensed-latin-800-normal", px)


def texto(px, peso=400):
    return fuente("saira", f"saira-latin-{peso}-normal", px)


def oblicua(img, xy, s, font, fill, skew=0.2):
    """Synthetic oblique like the browser's for Saira Condensed (no italic file): shear a text layer."""
    l, t, r, b = font.getbbox(s)
    w, h = r + int((b) * skew) + 8, b + 8
    capa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(capa).text((0, 0), s, font=font, fill=fill)
    capa = capa.transform(capa.size, Image.AFFINE, (1, skew, -skew * h, 0, 1, 0), Image.BICUBIC)
    img.alpha_composite(capa, (int(xy[0]), int(xy[1] - t)))


def tecla_flecha(d, x, y, s, derecha):
    """Square ghost key with a chevron drawn as a polygon (no glyph)."""
    d.rectangle((x, y, x + s, y + s), outline=LINE, width=max(2, s // 40))
    cx, cy, a, g = x + s / 2, y + s / 2, s * 0.16, s * 0.05
    k = 1 if derecha else -1
    d.line([(cx - k * a * 0.6, cy - a), (cx + k * a * 0.6, cy), (cx - k * a * 0.6, cy + a)], fill=INK, width=int(g), joint="curve")


def escuchar(d, x, y, w, h, px):
    """The Tecla, primary: filled gold square cap on a dark-gold lip (DESIGN.md › Components, Boton.astro)."""
    lip = max(4, h // 14)
    d.rectangle((x, y + lip, x + w, y + h + lip), fill=GOLD_DEEP)
    d.rectangle((x, y, x + w, y + h), fill=GOLD)
    f = texto(px, 600)
    l, t, r, b = f.getbbox("Escuchar")
    tx = x + h * 0.36
    d.text((tx, y + (h - (b - t)) / 2 - t), "Escuchar", font=f, fill=BG)
    # trailing play triangle
    cx, cy, a = x + w - h * 0.42, y + h / 2, h * 0.16
    d.polygon([(cx - a * 0.7, cy - a), (cx + a * 0.9, cy), (cx - a * 0.7, cy + a)], fill=BG)


def cara(W, H, rel, i, n):
    img = Image.new("RGBA", (W, H), CAP)
    d = ImageDraw.Draw(img)
    m = int(H * 0.1)
    c = H - 2 * m
    cover = Image.open(os.path.join(REPO, "public", rel["cover"].lstrip("/"))).convert("RGB").resize((c, c), Image.LANCZOS)
    img.paste(cover, (m, m))
    d.rectangle((m, m, m + c, m + c), outline=LINE, width=2)
    x0 = m * 2 + c
    tam = int(H * (0.2 if W / H > 2 else 0.15))
    f = display(tam)
    while f.getlength(rel["title"]) > (W - x0 - m) and tam > 20:
        tam -= 4
        f = display(tam)
    oblicua(img, (x0, m), rel["title"], f, INK)
    d.text((x0, m + tam * 1.0), rel.get("subtitle", ""), font=texto(int(H * 0.055)), fill=MUTED)
    s = int(H * 0.17)
    yb = m + c - s
    tecla_flecha(d, x0, yb, s, False)
    tecla_flecha(d, x0 + s + m * 0.4, yb, s, True)
    escuchar(d, x0 + 2 * s + m * 0.9, yb, int(s * 3.2), s, int(s * 0.34))
    # dot pager
    for k in range(n):
        r = H * 0.008
        cx, cy = x0 + k * r * 4 + r, m + c - s - H * 0.06
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD if k == i else LINE)
    return img.convert("RGB")


if __name__ == "__main__":
    i = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    rels = json.load(open(os.path.join(REPO, "research", "contenido", "catalog.json"), encoding="utf8"))["releases"]
    os.makedirs(OUT, exist_ok=True)
    cara(2400, 800, rels[i], i, len(rels)).save(os.path.join(OUT, "pantalla-ancha.png"))
    cara(1600, 900, rels[i], i, len(rels)).save(os.path.join(OUT, "pantalla-comand.png"))
    print("ok", rels[i]["title"])
