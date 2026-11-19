"""blender/vivo_bake.py's renders -> the page's world textures (P1 phase 1, 2026-11-18).

  uv run -q --with numpy --with pillow python -I scripts/vivo-bake-post.py tmp/p1/bake public/vivo

Each render spans y -16..192 (one 192 m period plus 16 m before it). The tile keeps y 0..192, and over its last 16 m it fades
into the 16 m before y 0, so where the tile repeats, y 192 meets y 0 with the same pixels (the wrap has no seam).
Orientation of every output: the first row (suelo, ancho) or the first column (cards) is y = 192; the last is y = 0.
Writes suelo.webp, ancho.webp, faros.webp, arboles_der.webp, arboles_izq.webp and prints the seam step before/after.
"""
import os, sys
import numpy as np
from PIL import Image

ENT, SAL = sys.argv[1], sys.argv[2]
Y0, Y1, P, F = -16.0, 192.0, 192.0, 16.0


def costura(a, eje):
    """a: rows (eje 0) or columns (eje 1) from y = 192 down to y = -16. Returns the 0..192 tile with the fade."""
    a = np.moveaxis(a.astype(np.float32), eje, 0)
    n = a.shape[0]
    k = round(n * P / (Y1 - Y0))  # rows for 0..192
    f = n - k                     # rows for -16..0 (= 176..192 one period on)
    t = a[:k].copy()
    w = np.linspace(1.0, 0.0, f, endpoint=False)[:, None, None]  # row 0 is y 192: all from y 0-; row f is y 176: none
    t[:f] = w * a[k:k + f] + (1 - w) * t[:f]
    paso = lambda x: float(np.abs(x[0] - x[-1]).mean())
    print(f"  costura: antes {paso(a[:k]):.2f}, despues {paso(t):.2f} (paso medio de una fila a la vecina {float(np.abs(np.diff(a[:k], axis=0)).mean()):.2f})")
    return np.moveaxis(t, 0, eje)


def guardar(a, nombre, tam, q):
    im = Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8))
    im = im.resize(tam, Image.LANCZOS)
    ruta = os.path.join(SAL, nombre)
    im.save(ruta, "WEBP", quality=q, method=6)
    print(f"{nombre} {im.size} {os.path.getsize(ruta) / 1024:.0f} KB")


leer = lambda n: np.asarray(Image.open(os.path.join(ENT, n)))
print("suelo")
guardar(costura(leer("suelo.png"), 0), "suelo.webp", (576, 4096), 82)
print("ancho")
guardar(costura(leer("ancho.png"), 0), "ancho.webp", (288, 512), 80)
guardar(leer("faros.png").astype(np.float32), "faros.webp", (192, 512), 85)
for lado in ("der", "izq"):
    a = leer(f"arboles_{lado}.png")
    if lado == "izq":
        a = a[:, ::-1]  # its camera looks -X: image right is +Y; flip so column 0 is y 192 like the right card
    print("arboles", lado)
    guardar(costura(a, 1), f"arboles_{lado}.webp", (2048, 312), 80)
