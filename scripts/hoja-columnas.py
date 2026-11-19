"""Sheet of N columns x M rows of same-size stills, with a label over each column and an optional label per row.

  uv run -q --with pillow python -I scripts/hoja-columnas.py <out.jpg> <ancho_celda> "col label=dir_or_pattern" ... \
      [--filas "1 Cabina,2 Caja,..."] [--nota "line under the title"]

Each column argument is `label=pattern`, where the pattern has `{n}` for the row number (1-based), e.g.
"live=E:/tmp/x/vivo-{n}.png". Missing files leave a dark cell.
"""
import os, sys
from PIL import Image, ImageDraw

args = sys.argv[1:]
out, ancho = args[0], int(args[1])
filas, nota, cols = None, "", []
i = 2
while i < len(args):
    if args[i] == "--filas":
        filas = args[i + 1].split(","); i += 2
    elif args[i] == "--nota":
        nota = args[i + 1]; i += 2
    else:
        cols.append(args[i].split("=", 1)); i += 1
n = len(filas) if filas else 6
M, T = 8, 24 + (18 if nota else 0)
celdas = [[cols[c][1].format(n=r + 1) for c in range(len(cols))] for r in range(n)]
alto = None
for fila in celdas:
    for p in fila:
        if os.path.exists(p):
            w, h = Image.open(p).size
            alto = round(ancho * h / w)
            break
    if alto:
        break
hoja = Image.new("RGB", (len(cols) * (ancho + M) + M, n * (alto + M + (16 if filas else 0)) + M + T), (12, 12, 12))
d = ImageDraw.Draw(hoja)
if nota:
    d.text((M, 4), nota, fill=(200, 200, 200))
for c, (et, _) in enumerate(cols):
    d.text((M + c * (ancho + M), T - 18), et, fill=(230, 230, 230))
y = T
for r, fila in enumerate(celdas):
    if filas:
        d.text((M, y), filas[r], fill=(230, 200, 120)); y += 16
    for c, p in enumerate(fila):
        if os.path.exists(p):
            hoja.paste(Image.open(p).convert("RGB").resize((ancho, alto), Image.LANCZOS), (M + c * (ancho + M), y))
    y += alto + M
hoja.save(out, quality=88)
print(out, hoja.size)
