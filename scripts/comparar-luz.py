"""Light match between a live frame and its Cycles still (same framing, different renderer): numbers for tuning the bake, the
cab light and the fog, where revisar's image mode (same-picture checks: align, halo) does not apply.

  uv run -q --with numpy --with pillow python -I scripts/comparar-luz.py <live.png> <cycles.png> [x0,y0,x1,y1 ...]

Per region (default: whole frame; boxes in pixels of the live frame): mean L* of each, the difference, and the mean dE76 between
the two images blurred to 32 x 18 cells (layout-level colour, not detail). A row `l3` gives the mean L* of the frame's
thirds (top, middle, bottom) for both.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter


def lab(im):
    a = np.asarray(im.convert("RGB")).astype(np.float64) / 255
    a = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    xyz = a @ np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]).T
    xyz /= np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


v, c = Image.open(sys.argv[1]).convert("RGB"), Image.open(sys.argv[2]).convert("RGB")
c = c.resize(v.size, Image.LANCZOS)
W, H = v.size
cajas = [tuple(int(t) for t in s.split(",")) for s in sys.argv[3:]] or [(0, 0, W, H)]
for x0, y0, x1, y1 in cajas:
    a, b = v.crop((x0, y0, x1, y1)), c.crop((x0, y0, x1, y1))
    la, lb = lab(a), lab(b)
    pa, pb = (lab(i.resize((32, 18), Image.BOX)) for i in (a, b))
    de = np.sqrt(((pa - pb) ** 2).sum(-1)).mean()
    print(f"caja {x0},{y0},{x1},{y1}  L* vivo {la[..., 0].mean():5.1f}  cycles {lb[..., 0].mean():5.1f}  dif {la[..., 0].mean() - lb[..., 0].mean():+5.1f}  dE76 32x18 {de:5.1f}"
          f"  a*b* vivo {la[..., 1].mean():+.1f},{la[..., 2].mean():+.1f} cycles {lb[..., 1].mean():+.1f},{lb[..., 2].mean():+.1f}")
L = lab(v)[..., 0], lab(c)[..., 0]
print("l3 vivo", [round(float(L[0][i * H // 3:(i + 1) * H // 3].mean()), 1) for i in range(3)],
      "cycles", [round(float(L[1][i * H // 3:(i + 1) * H // 3].mean()), 1) for i in range(3)])
