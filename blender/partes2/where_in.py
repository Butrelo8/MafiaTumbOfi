# where_in.py <garment npz> <body.glb> <body.json>: where the garment's kept vertices still sit under 1 mm from the
# body (or inside) at rest: a histogram by height and side, so creases (armpit, crotch) show up.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, trimesh
from scipy.spatial import cKDTree
from fitlib import load_glb, apply
Z = np.load(sys.argv[1]); P, keep = Z["P"], Z["keep"]
V, F, _ = load_glb(sys.argv[2]); V = apply(np.array(json.load(open(sys.argv[3]))["T"]), V)
m = trimesh.Trimesh(V, F, process=True); m = max(m.split(only_watertight=False), key=lambda c: len(c.faces)); m.fix_normals()
S, fi = trimesh.sample.sample_surface(m, 600000); N = m.face_normals[fi]
_, i = cKDTree(S).query(P); sd = ((P - S[i]) * N[i]).sum(1)
bad = keep & (sd < 0.001); Q = P[bad]
print("under 1 mm:", bad.sum())
for z0 in np.arange(0, 1, 0.05):
    k = (Q[:, 2] >= z0) & (Q[:, 2] < z0 + 0.05)
    if k.sum(): print("z %.2f-%.2f: %4d  |x| p10/p50/p90 %.3f %.3f %.3f  y p50 %.3f  depth max %.1f mm" % (z0, z0 + 0.05, k.sum(), *np.percentile(np.abs(Q[k, 0]), [10, 50, 90]), np.median(Q[k, 1]), -sd[bad][k].min() * 1000))
