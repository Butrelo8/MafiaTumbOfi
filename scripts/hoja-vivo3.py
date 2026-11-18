"""Before / after / Cycles sheet for /vivo-secciones (one row per stop).
  uv run -q --with pillow python -I scripts/hoja-vivo3.py <before run dir> <after run dir> <cycles dir> <out.jpg>
"""
import sys
from PIL import Image, ImageDraw
cols = [("antes (run2)", sys.argv[1] + "/vivo-{}.png"), ("ahora (run6)", sys.argv[2] + "/vivo-{}.png"), ("Cycles", sys.argv[3] + "/montaje-esc{}.png")]
W, H, M = 640, 360, 6
h = Image.new("RGB", (3 * W + 4 * M, 6 * (H + M) + M + 22), (12, 12, 12)); d = ImageDraw.Draw(h)
for k, (t, _) in enumerate(cols): d.text((M + k * (W + M), 5), t, fill=(220, 220, 220))
for i in range(6):
    y = 22 + M + i * (H + M)
    for k, (_, f) in enumerate(cols): h.paste(Image.open(f.format(i + 1)).convert("RGB").resize((W, H)), (M + k * (W + M), y))
    d.text((M + 6, y + 6), f"stop {i + 1}", fill=(255, 210, 90))
h.save(sys.argv[4], quality=85); print(sys.argv[4], h.size)
