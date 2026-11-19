"""The G63 grille's black diamond mesh as one tiling colour texture (2 x 2 cells).
  uv run -q --with numpy --with pillow python -I parrilla_malla.py  -> parrilla_malla.png here (128 px, a few KB)
Reference: the AMG 6x6 grille (~/cc-out/mto-asset-fixes/luces/refs/Mercedes-Benz_G63_AMG_6__6__W463__front.JPG): a black
diamond wire mesh, the holes darker than the wires."""
import os
import numpy as np
from PIL import Image

N = 128
y, x = np.mgrid[0:N, 0:N] / N * 2  # two cells per tile in each direction
f = lambda t: np.minimum(t % 1, 1 - t % 1)  # distance to the nearest line t = integer
d = np.minimum(f(x + y), f(x - y))  # to the nearest diagonal wire
alambre = np.clip((0.16 - d) / 0.05, 0, 1)  # 1 on the wires, 0 in the diamond holes
v = 0.004 + 0.016 * alambre  # linear: holes near black, wires black-grey (0.012 / 0.06 read mid-grey under the headlights)
rgb = (np.stack([v, v, v * 1.05], -1) ** (1 / 2.2) * 255).astype(np.uint8)  # stored as sRGB
Image.fromarray(rgb, "RGB").save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "parrilla_malla.png"))
