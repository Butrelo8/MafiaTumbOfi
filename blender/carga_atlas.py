"""Roof load, step 2 (2026-11-20): the owner's seven r1 stickers (blender/props/calcas-r1, the newest set: 2026-11-15, commit 8d625ae) packed into one
atlas, so every decal on the roof costs one material and one draw call.

  uv run -q --with pillow python -I blender/carga_atlas.py <out dir> [px = 1024]

Writes <out>/calcas_atlas.png (RGBA, the same px/mm for every sticker, 6 px gutters; the stickers already carry a transparent margin) and
<out>/calcas_atlas.json: {id: {"uv": [u0, v0, u1, v1] (glTF/Blender v up), "w": m, "h": m}}, w and h being the sticker's size in metres
(calcas3.json). Shelf packing, tallest first; the px/mm is the largest that fits the square.
"""
import json
import os
import sys
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
SAL = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
CARPETA = os.path.join(AQUI, "props", "calcas-r1")
J = json.load(open(os.path.join(CARPETA, "calcas3.json"), encoding="utf8"))
IDS = list(J)
GUT = 6


def empaquetar(px_mm):
    """Shelf pack at px_mm; returns {id: (x, y, w, h)} or None if it does not fit."""
    tam = {i: (round(J[i]["w"] * 1000 * px_mm), round(J[i]["h"] * 1000 * px_mm)) for i in IDS}
    pos, x, y, fila = {}, 0, 0, 0
    for i in sorted(IDS, key=lambda k: -tam[k][1]):
        w, h = tam[i]
        if x + w + GUT > N:
            x, y, fila = 0, y + fila + GUT, 0
        if w + GUT > N or y + h + GUT > N:
            return None
        pos[i] = (x, y, w, h)
        x += w + GUT
        fila = max(fila, h)
    return pos


bajo, alto = 0.2, 4.0
for _ in range(30):
    medio = (bajo + alto) / 2
    if empaquetar(medio):
        bajo = medio
    else:
        alto = medio
pos = empaquetar(bajo)
atlas = Image.new("RGBA", (N, N), (0, 0, 0, 0))
out = {}
for i, (x, y, w, h) in pos.items():
    im = Image.open(os.path.join(CARPETA, i + ".png")).convert("RGBA").resize((w, h), Image.LANCZOS)
    atlas.paste(im, (x, y))
    out[i] = {"uv": [x / N, 1 - (y + h) / N, (x + w) / N, 1 - y / N], "w": J[i]["w"], "h": J[i]["h"], "px": [w, h]}
os.makedirs(SAL, exist_ok=True)
atlas.save(os.path.join(SAL, "calcas_atlas.png"))
json.dump(out, open(os.path.join(SAL, "calcas_atlas.json"), "w"), indent=1)
print("ATLAS", N, "px/mm", round(bajo, 3), "fill", round(sum(w * h for _, _, w, h in pos.values()) / N / N, 3), {i: v["px"] for i, v in out.items()})
