# landmarks.py <mesh.npz> <basecolor> : per-vertex texel class (skin / dark / white) from the base colour, then the
# garment boundaries along each limb: collar, sleeve hem, shirt hem, trouser cuff. Prints z / distance profiles.
import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
d = np.load(sys.argv[1]); V, UV, LV = d["V"], d["UV"], d["LV"]
im = np.asarray(Image.open(sys.argv[2]).convert("RGB")).astype(np.float32) / 255; H, W = im.shape[:2]
uvv = np.zeros((len(V), 2), np.float32); uvv[LV] = UV            # one corner's UV per vertex
px = im[np.clip(((1 - uvv[:, 1]) * H).astype(int), 0, H - 1), np.clip((uvv[:, 0] * W).astype(int), 0, W - 1)]
lum = px.mean(1); sat = px.max(1) - px.min(1)
cls = np.where(lum < 0.22, 0, np.where((sat < 0.08) & (lum > 0.55), 2, 1))   # 0 dark, 1 skin/colour, 2 white
np.save(sys.argv[1].replace("mesh.npz", "vcls.npy"), cls)
print("classes dark/skin/white", np.bincount(cls, minlength=3))
x, y, z = V.T
def prof(mask, coord, lo, hi, step, label):
    print("--", label)
    for a in np.arange(lo, hi, step):
        m = mask & (coord >= a) & (coord < a + step)
        if m.sum() < 20: continue
        b = np.bincount(cls[m], minlength=3) / m.sum()
        print(f"  {a:.3f} n={m.sum():5d} dark {b[0]:.2f} skin {b[1]:.2f} white {b[2]:.2f}")
prof(np.abs(x) < 0.04, z, 0.50, 0.66, 0.01, "neck/collar, |x|<4cm, by z")
prof((x > 0.10) & (z > 0.30), x, 0.10, 0.42, 0.01, "left arm, by x")
prof((np.abs(x) < 0.13) & (np.abs(x) > 0.0), z, 0.18, 0.42, 0.01, "torso/hips |x|<13cm, by z")
prof((x > 0.02) & (x < 0.12), z, 0.0, 0.20, 0.01, "left leg, by z")
# crotch: lowest z with mesh on the centre line below the hips
cm = (np.abs(x) < 0.004) & (z < 0.3)
print("crotch z (lowest centre-line vertex below 0.3):", z[cm].min().round(4) if cm.any() else None)
for zz in (0.25, 0.28, 0.30, 0.32, 0.34):
    m = np.abs(z - zz) < 0.003
    print(f"  slab z={zz}: x range {x[m].min():.3f}..{x[m].max():.3f}  y range {y[m].min():.3f}..{y[m].max():.3f}")
print("bbox", V.min(0).round(3), V.max(0).round(3))
