# hair_fused.py <target.npz> <head.glb> <head.json> <out.npz>: the hair cut out of today's fused Diego (TRELLIS.2,
# already in the upload frame), because both part-image TRELLIS hairs came out ~2x deeper than the head (a front view
# of a thin shape gives TRELLIS no depth). Faces whose three vertices are hair-coloured (target.py's label), largest
# connected patch (brows and pupils are separate dark patches), grown by one ring so the fringe edge is clean.
# Then the same rigid clearance as fit_body.py's hair: grow about the head centre until < 0.2 % of the vertices sit
# under GAP from the head part's scalp, clamp those. Writes P (all fused vertices, GLB order) and keep.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree
from fitlib import load_glb, apply
GAP = 0.002
t = np.load(sys.argv[1]); V, F, lab = t["V"], t["F"], t["lab"]
hair = lab == "hair"; fh = hair[F].all(1)
for _ in range(1):
    ring = np.zeros(len(V), bool); ring[F[fh].ravel()] = True; fh = ring[F].any(1) & (V[F][:, :, 2].min(1) > 0.62)
_, wid = np.unique(np.round(V, 6), axis=0, return_inverse=True); wid = wid.ravel()   # weld UV-seam copies for connectivity
Fh = wid[F[fh]]; e = np.r_[Fh[:, [0, 1]], Fh[:, [1, 2]]]; nw = wid.max() + 1
g = coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(nw, nw))
nc, cl = connected_components(g, directed=False)
used = np.unique(Fh); big = np.bincount(cl[used]).argmax()
keepw = np.zeros(nw, bool); keepw[used[cl[used] == big]] = True
keep = keepw[wid] & np.isin(np.arange(len(V)), F[fh].ravel())
HV, HF, _ = load_glb(sys.argv[2]); HV = apply(np.array(json.load(open(sys.argv[3]))["T"]), HV)
m = trimesh.Trimesh(HV, HF, process=True); m = max(m.split(only_watertight=False), key=lambda c: len(c.faces)); m.fix_normals()
S, fi = trimesh.sample.sample_surface(m, 600000); N = m.face_normals[fi]; tree = cKDTree(S)
def sdist(P):
    _, i = tree.query(P); return ((P - S[i]) * N[i]).sum(1), N[i]
P = V.copy(); c = HV[HV[:, 2] > 0.70].mean(0)
for s_in in np.arange(1.0, 1.2, 0.002):
    Ps = c + s_in * (P[keep] - c); sd, n = sdist(Ps)
    if (sd < GAP).mean() < 0.002: break
hard = sd < GAP; Ps[hard] += (GAP - sd[hard])[:, None] * n[hard]; P[keep] = Ps
print("@@ hair from fused: %d verts, %d faces, grown x%.3f, %d clamped to %.0f mm; bounds %s %s" % (
    keep.sum(), fh.sum(), s_in, hard.sum(), GAP * 1000, Ps.min(0).round(3), Ps.max(0).round(3)))
np.savez(sys.argv[4], P=P, keep=keep)
