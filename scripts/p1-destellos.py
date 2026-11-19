"""Glare sprites on a still, as the live build would draw them (P1: head/tail lamps, bulbs, underglow): every bright blob gets a
soft radial glow and a thin horizontal streak, added in linear light. A mock for the owner's pick, not a lens simulation.

  uv run -q --with numpy --with opencv-python-headless --with pillow python -I scripts/p1-destellos.py <in.png> <out.png> [suave|fuerte]

Blobs: pixels whose brightest channel is >= 250 (8-bit), grouped by connected components of 3..3000 px (bigger ones are lit
surfaces, the alien or a screen, not lamps). Per blob: glow sigma 3 + 1.2 sqrt(area) px (<= 40) at 0.22 (fuerte 0.45) of the
blob's colour; blobs of >= 30 px also get a streak 20 + 5 sqrt(area) px long (<= 160), 1.2 px tall, at 0.12 (0.30). A first
pass (>= 245, every blob streaked, glow 0.30) laid streaks across the whole of stop 2, and streaks from the 10..30 px
Marquesina bulbs crossed the stop-5 copy: lamps, not bulbs, streak.
Prints the blob count and the share of pixels the pass changed by more than 2 levels.
"""
import sys
import cv2
import numpy as np
from PIL import Image

ent, sal = sys.argv[1], sys.argv[2]
fuerte = len(sys.argv) > 3 and sys.argv[3] == "fuerte"
im = np.asarray(Image.open(ent).convert("RGB")).astype(np.float32) / 255
lin = np.where(im <= 0.04045, im / 12.92, ((im + 0.055) / 1.055) ** 2.4)
H, W = im.shape[:2]
mascara = (im.max(-1) >= 250 / 255).astype(np.uint8)
n, etiquetas, stats, centros = cv2.connectedComponentsWithStats(mascara, 8)
brillo = np.zeros_like(lin)
k_glow, k_raya = (0.45, 0.30) if fuerte else (0.22, 0.12)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
manchas = 0
for i in range(1, n):
    area = stats[i, cv2.CC_STAT_AREA]
    if not 3 <= area <= 3000:
        continue
    manchas += 1
    cx, cy = centros[i]
    color = lin[etiquetas == i].mean(0)
    color = color / max(color.max(), 1e-6)
    s = min(40.0, 3 + 1.2 * np.sqrt(area))
    L = min(160.0, 20 + 5 * np.sqrt(area)) if area >= 30 else 0.0
    x0, x1, y0, y1 = int(max(0, cx - 3 * max(s, L))), int(min(W, cx + 3 * max(s, L))), int(max(0, cy - 3 * s)), int(min(H, cy + 3 * s))
    dx, dy = xx[y0:y1, x0:x1] - cx, yy[y0:y1, x0:x1] - cy
    g = k_glow * np.exp(-(dx ** 2 + dy ** 2) / (2 * s * s))
    if L:
        g = g + k_raya * np.exp(-(dx ** 2) / (2 * L * L) - (dy ** 2) / (2 * 1.2 ** 2))
    brillo[y0:y1, x0:x1] += g[..., None] * color
out = np.clip(lin + brillo, 0, 1)
srgb = np.where(out <= 0.0031308, out * 12.92, 1.055 * out ** (1 / 2.4) - 0.055)
o8 = (np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8)
Image.fromarray(o8).save(sal)
cambio = (np.abs(o8.astype(int) - (im * 255 + 0.5).astype(int)).max(-1) > 2).mean()
print(f"{sal}: {manchas} destellos, {100 * cambio:.1f} % de pixeles cambiados")
