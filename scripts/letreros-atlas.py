"""Gantry titles per stop (P1 phase 1, 2026-11-18): one atlas row per stop, white Saira 600 on transparent, the face of ickdrone's
signs (tmp/fuentes/saira-latin-600-normal.ttf, OFL). The live page puts the stop's row on the title panels of portico_b and
arco_c; blender/vivo_p1_stills.py uses the same rows in the Cycles stills.

  uv run -q --with pillow python -I scripts/letreros-atlas.py <font.ttf> public/vivo/letreros.png

Row k (0..5, top first) = stop k+1. Each row is 1024 x 170 px for a 3.2 x 0.53 m plane (320 px/m); the cap height is 0.34 m
(ickdrone used 0.45 m, but then the accent of MÚSICA left the row), shrunk only when the word is wider than 3.0 m. The
baseline sits 12 px above the row bottom, so accents fit above the caps.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

TITULOS = ["MÚSICA", "REDES", "VIDEOS", "LA BANDA", "DÓNDE ANDAMOS", "CONTRATACIÓN"]
W, H, PXM = 1024, 170, 320
fuente, salida = sys.argv[1], sys.argv[2]
img = Image.new("RGBA", (W, 1024), (255, 255, 255, 0))  # 6 rows of 170 px, 4 px spare at the bottom
d = ImageDraw.Draw(img)
for k, t in enumerate(TITULOS):
    # size the em so the cap height (from the font's own "H") is 0.34 m, then fit the width to 3.0 m
    em = 200
    f = ImageFont.truetype(fuente, em)
    cap = f.getbbox("H")[3] - f.getbbox("H")[1]
    em = round(em * 0.34 * PXM / cap)
    f = ImageFont.truetype(fuente, em)
    ancho = f.getlength(t)
    if ancho > 3.0 * PXM:
        em = int(em * 3.0 * PXM / ancho)
        f = ImageFont.truetype(fuente, em)
    x0, y0, x1, y1 = d.textbbox((0, 0), t, font=f, anchor="ls")
    capk = f.getbbox("H")[3] - f.getbbox("H")[1]
    base = k * H + H - 12
    d.text((W / 2, base), t, font=f, fill=(255, 255, 255, 255), anchor="ms")
    print(f"{k + 1} {t}: em {em} px, cap {capk / PXM:.2f} m, ancho {(x1 - x0) / PXM:.2f} m")
img.save(salida, optimize=True)
print(salida, img.size)
