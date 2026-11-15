# target.py <fused glb> <out.npz>: today's fused Diego as the assembly target, in the Mixamo upload frame
# (export_rerig.py: GLB Y-up -> Blender Z-up, scale 1/height... checked against diego_rerig.fbx bounds x ±0.3993, y ±0.1879),
# with a per-vertex colour sampled from its texture and a region label from colour + height.
import sys
import numpy as np, trimesh
src, out = sys.argv[1:3]
m = trimesh.load(src, force="mesh", process=False)
V = np.asarray(m.vertices, float); V = np.c_[V[:, 0], -V[:, 2], V[:, 1]]          # GLB (x, y, z) -> Blender (x, -z, y)
h = V[:, 2].max() - V[:, 2].min(); V /= h
lo, hi = V.min(0), V.max(0); V -= [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]]
print("height before", round(h, 4), "bounds", V.min(0).round(4), V.max(0).round(4))
C = np.asarray(m.visual.to_color().vertex_colors)[:, :3].astype(float)
lum = C.mean(1); z = V[:, 2]
sk = (C[:, 0] - C[:, 2] > 25) & (lum > 90)
dark = lum < 70; white = (lum > 150) & ~sk
lab = np.full(len(V), "other", "<U6")
lab[sk] = "skin"
lab[dark & (z > 0.60)] = "hair"; lab[dark & (z <= 0.60) & (z > 0.275)] = "shirt"; lab[dark & (z <= 0.275)] = "pants"
lab[white & (z < 0.10)] = "shoes"
for L in np.unique(lab):
    s = lab == L; print(L, s.sum(), "z", V[s, 2].min().round(3), V[s, 2].max().round(3), "x", V[s, 0].min().round(3), V[s, 0].max().round(3))
np.savez(out, V=V, F=np.asarray(m.faces), C=C, lab=lab)
