# flat_tex.py <mesh.npz> <basecolor in> <png out> [k]: flat vinyl colours for the parts. The palette is k-means of the
# texels the mesh actually uses (one per vertex UV), so the face keeps its eyes, brows, mouth and hair as flat areas;
# every texel then takes its nearest palette colour and a mode filter removes specks (visual-lab's flatten.py, applied
# to the repainted Tripo texture instead of a TRELLIS bake).
import sys, numpy as np
from PIL import Image, ImageFilter
Image.MAX_IMAGE_PIXELS = None
d = np.load(sys.argv[1]); UV = d["UV"]; k = int(sys.argv[4]) if len(sys.argv) > 4 else 8
im = np.asarray(Image.open(sys.argv[2]).convert("RGB")).astype(np.float32); H, W = im.shape[:2]
px = im[np.clip(((1 - UV[:, 1]) * H).astype(int), 0, H - 1), np.clip((UV[:, 0] * W).astype(int), 0, W - 1)]
rng = np.random.default_rng(0); px = px[rng.choice(len(px), min(len(px), 200000), replace=False)]
c = px[rng.choice(len(px), k, replace=False)]
for _ in range(30):
    lab = ((px[:, None] - c[None]) ** 2).sum(2).argmin(1)
    c = np.array([px[lab == i].mean(0) if (lab == i).any() else c[i] for i in range(k)])
MERGE = float(sys.argv[5]) if len(sys.argv) > 5 else 25.0     # one vinyl per colour: merge clusters closer than this (RGB)
while True:
    n = np.bincount(((px[:, None] - c[None]) ** 2).sum(2).argmin(1), minlength=len(c))
    dd = np.sqrt(((c[:, None] - c[None]) ** 2).sum(2)) + np.eye(len(c)) * 1e9; i, j = np.unravel_index(dd.argmin(), dd.shape)
    if dd[i, j] >= MERGE: break
    c[i] = (c[i] * n[i] + c[j] * n[j]) / max(n[i] + n[j], 1); c = np.delete(c, j, 0)
k = len(c)
share = np.bincount(((px[:, None] - c[None]) ** 2).sum(2).argmin(1), minlength=k) / len(px)
flat = im.reshape(-1, 3); lab = np.empty(len(flat), np.uint8)
for i in range(0, len(flat), 1 << 20):
    lab[i:i + (1 << 20)] = ((flat[i:i + (1 << 20), None] - c[None]) ** 2).sum(2).argmin(1)
lab = np.asarray(Image.fromarray(lab.reshape(H, W)).filter(ImageFilter.ModeFilter(5)))
Image.fromarray(c[lab].astype(np.uint8)).save(sys.argv[3])
for i in np.argsort(-share): print("palette", c[i].astype(int).tolist(), "share %.1f%%" % (share[i] * 100))
