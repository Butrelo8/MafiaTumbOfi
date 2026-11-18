"""Side-by-side sheet for /vivo-secciones: one row per stop, live frame (scripts/medir-vivo.mjs, ?f=0&sinpantalla, 960x540)
left, the Cycles montaje still right.
  uv run -q --with pillow python -I scripts/hoja-vivo.py <dir with vivo-N.png> <montaje dir> <out.jpg>
"""
import sys
from PIL import Image, ImageDraw

vivo, montaje, out = sys.argv[1:4]
W, H, M = 960, 540, 8
hoja = Image.new("RGB", (2 * W + 3 * M, 6 * (H + M) + M + 24), (12, 12, 12))
d = ImageDraw.Draw(hoja)
d.text((M, 6), "live three.js (?f=0, screen flat)", fill=(220, 220, 220))
d.text((2 * M + W, 6), "Cycles montaje still", fill=(220, 220, 220))
for i in range(6):
    y = 24 + M + i * (H + M)
    for k, f in enumerate((f"{vivo}/vivo-{i + 1}.png", f"{montaje}/montaje-esc{i + 1}.png")):
        im = Image.open(f).convert("RGB").resize((W, H))
        hoja.paste(im, (M + k * (W + M), y))
    d.text((M + 6, y + 6), f"stop {i + 1}", fill=(255, 210, 90))
hoja.save(out, quality=86)
print(out, hoja.size)
