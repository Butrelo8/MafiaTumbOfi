"""Plate face after the current Veracruz private-car plate (owner's reference, mothership 03:30): white field, VERACRUZ heading,
olive geometric corner pattern, faint crest watermark, QR top right, the state slogan logo, TRANSPORTE PRIVADO AUTOMOVIL, round
seals, a 30 and a red T badge. Ours in place of the official parts: the characters, the MT monogram in the national-seal spot
(Ley sobre el Escudo, la Bandera y el Himno Nacionales), a simplified crest lookalike, a QR that opens the band's WhatsApp.

  uv run -q --with pillow --with qrcode python -I blender/placa_veracruz.py [CHARS=MT-420-VER]

Writes tmp/utileria/placa-veracruz.png (1200×600 = 300×150 mm at 4 px/mm, rounded corners transparent).
"""
import os, sys
import qrcode
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the site's counted WhatsApp route (main: wa.js, /wa/<number>); number from socials.ts, pending the band's confirmation
WA = "https://mafiatumbada.com/wa/5212283538827"
BAH = "/mnt/c/Windows/Fonts/bahnschrift.ttf"  # DIN-like stand-in for the plate face; variable: wdth 75-100, wght 300-700
OLIVA, OLIVA_C, GRIS, MARCA, ROJO, TINTA = "#a8955a", "#d8cb9a", "#9a9a98", "#ececea", "#d0202a", "#141414"
W, H, MM = 1200, 600, 4


def bah(px, wght=600, wdth=100):
    f = ImageFont.truetype(BAH, px)
    f.set_variation_by_axes([wght, wdth])
    return f


def centrado(d, x, y, s, f, fill):
    l, t, r, b = f.getbbox(s)
    d.text((x - (r - l) / 2 - l, y - (b - t) / 2 - t), s, font=f, fill=fill)


def greca(d, x0, y0, sx, sy, n=6, c=34):
    """Stepped fret cells filling a triangle from the corner (sx, sy = ±1 point the triangle inwards)."""
    for i in range(n):
        for j in range(n - i):
            x, y = x0 + sx * i * c, y0 + sy * j * c
            box = (min(x, x + sx * c), min(y, y + sy * c), max(x, x + sx * c), max(y, y + sy * c))
            col = OLIVA if (i + j) % 2 == 0 else OLIVA_C
            d.rectangle(box, outline=col, width=5)
            k = c * 0.3
            d.rectangle((box[0] + k, box[1] + k, box[2] - k, box[3] - k), fill=col)


def sello(d, cx, cy, r, texto=None, GRIS=GRIS):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GRIS, width=4)
    d.ellipse((cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78), outline=GRIS, width=2)
    if texto:
        centrado(d, cx, cy, texto, bah(int(r * 0.85), 700, 75), GRIS)
    else:  # crest lookalike: a crenellated tower over waves, not the state arms
        t = r * 0.42
        d.rectangle((cx - t, cy - t * 0.6, cx + t, cy + t * 0.5), outline=GRIS, width=3)
        for k in range(-2, 3, 2):
            d.rectangle((cx + k * t / 2.4 - t / 6, cy - t * 0.95, cx + k * t / 2.4 + t / 6, cy - t * 0.6), fill=GRIS)
        d.line([(cx - t, cy + t * 0.8), (cx - t / 3, cy + t * 0.6), (cx + t / 3, cy + t * 0.8), (cx + t, cy + t * 0.6)], fill=GRIS, width=3)


def cara(chars):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius=14 * MM, fill="white", outline="#c9c9c6", width=3 * MM)
    greca(d, 3 * MM, 3 * MM, 1, 1, n=5)
    greca(d, W - 3 * MM, 3 * MM, -1, 1, n=4)
    # faint crest watermark behind the characters (lookalike outline)
    cx, cy = W / 2, H * 0.53
    for r, w in ((190, 6), (150, 3)):
        d.ellipse((cx - r, cy - r * 1.1, cx + r, cy + r * 1.1), outline=MARCA, width=w)
    sello(d, cx, cy, 120, GRIS=MARCA)
    # NOM-001 slots: 20 × 6 mm, 50 mm from the sides, 10 mm from top and bottom
    for x in (50 * MM, W - 70 * MM):
        for y in (10 * MM, H - 16 * MM):
            d.rounded_rectangle((x, y, x + 20 * MM, y + 6 * MM), radius=3 * MM, outline="#d4d4d2", width=3)
    centrado(d, W / 2, 62, "VERACRUZ", bah(92, 700, 100), TINTA)
    centrado(d, 60, 205, "T", bah(56, 700, 100), ROJO)
    # small two-line block under the left pattern (ours: the band, not the state government)
    sello(d, 128, 142, 20, "MT")
    for k, s in enumerate(("MAFIA", "TUMBADA")):
        d.text((156, 126 + k * 18), s, font=bah(17, 600, 85), fill=GRIS)
    q = qrcode.QRCode(border=1, box_size=4)
    q.add_data(WA)
    q.make(fit=True)
    qi = q.make_image(fill_color=TINTA, back_color="white").convert("RGBA")  # 4 px a module, no resample
    img.alpha_composite(qi, (W - 3 * MM - 4 * 34 - 128, 30))  # clear of the fret, so it scans
    # the characters: condensed, the plate's weight
    px = 280
    f = bah(px, 600, 75)
    while f.getlength(chars) > W - 150:
        px -= 6
        f = bah(px, 600, 75)
    centrado(d, W / 2, H * 0.52, chars, f, TINTA)
    # bottom: slogan logo, 30, seals, service line
    greca_ic = (W / 2 - 150, 452)
    for i in range(2):
        for j in range(2):
            x, y = greca_ic[0] + i * 18, greca_ic[1] + j * 18
            d.rectangle((x, y, x + 16, y + 16), outline=OLIVA if (i + j) % 2 == 0 else OLIVA_C, width=3)
            d.rectangle((x + 5, y + 5, x + 11, y + 11), fill=OLIVA)
    d.text((W / 2 - 104, 444), "VERACRUZ", font=bah(42, 700, 100), fill="#5b4a6b")
    d.text((W / 2 - 100, 490), "ME LLENA DE ORGULLO", font=bah(17, 600, 90), fill="#5b4a6b")
    centrado(d, W / 2, 548, "TRANSPORTE PRIVADO AUTOMOVIL", bah(30, 700, 100), TINTA)
    centrado(d, W - 230, 482, "30", bah(46, 700, 100), TINTA)
    sello(d, 96, 500, 40, "MT")   # the national-seal spot: our monogram (Ley sobre el Escudo…)
    sello(d, W - 96, 500, 40)     # state crest lookalike
    return img


if __name__ == "__main__":
    out = os.path.join(REPO, "tmp", "utileria")
    os.makedirs(out, exist_ok=True)
    cara(sys.argv[1] if len(sys.argv) > 1 else "MT-420-VER").save(os.path.join(out, "placa-veracruz.png"))
    print("ok")
