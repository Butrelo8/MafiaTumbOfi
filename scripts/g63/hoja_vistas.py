"""Sheet of vivo-tomas.mjs shots: per view the 1440 shot and the 390 (phone) shot side by side.
  uv run -q --with pillow python -I scripts/g63/hoja_vistas.py <tomas dir> <out.jpg> view1 view2 ...
Overview only: not evidence for motion or for a look claim (those come from the numbers)."""
import sys
from PIL import Image, ImageDraw

d, out, *vistas = sys.argv[1:]
H, COLS, GAP = 300, 2, 12
filas = []
for v in vistas:
    a = Image.open(f"{d}/1440-{v}.png").convert("RGB")
    b = Image.open(f"{d}/390-{v}.png").convert("RGB")
    a = a.resize((round(a.width * H / a.height), H))
    b = b.resize((round(b.width * H / b.height), H))
    cell = Image.new("RGB", (a.width + b.width + GAP, H + 18), (24, 24, 24))
    cell.paste(a, (0, 18)); cell.paste(b, (a.width + GAP, 18))
    ImageDraw.Draw(cell).text((4, 3), v, fill=(235, 235, 235))
    filas.append(cell)
w = max(c.width for c in filas)
n = (len(filas) + COLS - 1) // COLS
hoja = Image.new("RGB", (COLS * w + (COLS + 1) * GAP, n * (H + 18 + GAP) + GAP), (0, 0, 0))
for i, c in enumerate(filas):
    hoja.paste(c, (GAP + (i % COLS) * (w + GAP), GAP + (i // COLS) * (H + 18 + GAP)))
hoja.save(out, quality=88)
print(out, hoja.size)
