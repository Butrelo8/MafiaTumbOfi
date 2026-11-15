"""Made-up drink labels for the cab and the riders' hands (owner 11-14: "soda cans, water props"), no real brands, in the DESIGN.md
palette: black #000, warm white #f1eee9, gold #e7b551. Writes tmp/utileria/etiquetas/{lata-tumba,lata-oro,agua}.png, wrapped
round the can or bottle by caja5.py (u = angle, v = height). Run before rendering:

  uv run -q --with pillow python -I blender/etiquetas.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

R = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(R, "..", "tmp", "utileria", "etiquetas")
os.makedirs(OUT, exist_ok=True)
NEGRO, BLANCO, ORO = (0, 0, 0), (241, 238, 233), (231, 181, 81)
F = "/mnt/c/Windows/Fonts/bahnschrift.ttf"
W, H = 1400, 820  # a 66 mm can: 207 mm round by 122 mm tall


def lata(nombre, fondo, banda, letra, texto, sub):
    im = Image.new("RGB", (W, H), fondo)
    d = ImageDraw.Draw(im)
    d.rectangle((0, int(H * 0.62), W, int(H * 0.70)), fill=banda)
    f, fs = ImageFont.truetype(F, 150), ImageFont.truetype(F, 54)
    for x0 in (0, W // 2):  # twice round, so it reads from any side
        d.text((x0 + W // 4, int(H * 0.40)), texto, font=f, fill=letra, anchor="mm")
        d.text((x0 + W // 4, int(H * 0.80)), sub, font=fs, fill=banda, anchor="mm")
    im.save(os.path.join(OUT, nombre + ".png"))


lata("lata-tumba", NEGRO, ORO, BLANCO, "TUMBA", "COLA · 355 ml")
lata("lata-oro", ORO, NEGRO, NEGRO, "ORO", "SODA DE TORONJA")
im = Image.new("RGB", (W, 360), BLANCO)  # the water bottle's wrap label, 66 mm round by 60 mm tall
d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 40), fill=ORO); d.rectangle((0, 320, W, 360), fill=ORO)
for x0 in (0, W // 2):
    d.text((x0 + W // 4, 150), "AGUA DE LA COSTA", font=ImageFont.truetype(F, 74), fill=NEGRO, anchor="mm")
    d.text((x0 + W // 4, 250), "NATURAL · 600 ml", font=ImageFont.truetype(F, 46), fill=ORO, anchor="mm")
im.save(os.path.join(OUT, "agua.png"))
print("etiquetas ->", os.path.abspath(OUT))
