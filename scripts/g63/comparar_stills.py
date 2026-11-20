"""Pixel difference of two stills of the same size: max / mean absolute difference per channel (0-255) and the share of pixels that differ.
  uv run -q --with numpy --with pillow python -I scripts/g63/comparar_stills.py a.png b.png [diff.png]
"""
import sys
import numpy as np
from PIL import Image

a, b = (np.asarray(Image.open(p).convert("RGB"), dtype=np.int16) for p in sys.argv[1:3])
d = np.abs(a - b)
print(f"{a.shape[1]}x{a.shape[0]}  max {d.max()}  media {d.mean():.5f}  pixeles distintos {(d.max(axis=2) > 0).mean() * 100:.4f} %")
if len(sys.argv) > 3:
    Image.fromarray(np.clip(d * 8, 0, 255).astype(np.uint8)).save(sys.argv[3])
