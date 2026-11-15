# semillas.py in.glb out_dir [n_max] [d_min]  -> out_dir/semillas.npz (seed centre, normal, long axis per seed) + stats
# Seeds go in the model's own pits: vertices welded by position, Laplacian-smoothed copy, h = (P - smooth) . n;
# a pit is a local minimum of h under a depth threshold; pits on red texels only, thinned by a 3D minimum distance that
# grows toward the calyx (fewer near the green top, as on a real berry). Pits: one seed each; gaps wider than d_min get fill seeds.
import sys, numpy as np, scipy.sparse as sp
from scipy.spatial import cKDTree
from PIL import Image
sys.path.insert(0, '.'); import glbio, io

src, out = sys.argv[1], sys.argv[2]
N_MAX = int(sys.argv[3]) if len(sys.argv) > 3 else 400
D_MIN = float(sys.argv[4]) if len(sys.argv) > 4 else 0.03
j, b = glbio.load(src)
prim = j['meshes'][0]['primitives'][0]


def acc(i, comps, dt):
    a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(b, dt, a['count'] * comps, off).reshape(a['count'], comps)


P = acc(prim['attributes']['POSITION'], 3, np.float32).astype(np.float64)
UV = acc(prim['attributes']['TEXCOORD_0'], 2, np.float32)
I = acc(prim['indices'], 1, np.uint32).reshape(-1, 3)
col = np.asarray(Image.open(io.BytesIO(glbio.view(j, b, j['images'][0]['bufferView'])))).astype(np.float32) / 255
S = col.shape[0]

# weld by position (glTF splits verts at UV seams)
key = np.round(P / 1e-5).astype(np.int64)
_, w, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
inv = inv.ravel()
Pw = P[w]; Iw = inv[I]; nv = len(Pw)
fn = np.cross(Pw[Iw[:, 1]] - Pw[Iw[:, 0]], Pw[Iw[:, 2]] - Pw[Iw[:, 0]])
area = np.linalg.norm(fn, axis=1) / 2
vn = np.zeros_like(Pw)
for k in range(3):
    np.add.at(vn, Iw[:, k], fn)
vn /= np.linalg.norm(vn, axis=1, keepdims=True) + 1e-12
e = np.concatenate([Iw[:, [0, 1]], Iw[:, [1, 2]], Iw[:, [2, 0]]])
A = sp.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), (nv, nv)).tocsr()
A = ((A + A.T) > 0).astype(np.float64)
L = sp.diags(1 / np.asarray(A.sum(1)).ravel()) @ A
Q = Pw.copy()
for _ in range(150):
    Q = 0.5 * Q + 0.5 * (L @ Q)
h = ((Pw - Q) * vn).sum(1)

# colour per welded vertex (any of its split copies' UV)
uvw = UV[w]
px = np.clip((uvw * S).astype(int), 0, S - 1)
c = col[px[:, 1], px[:, 0]]
rojo = (c[:, 0] > 0.6) & (c[:, 1] < 0.3)
verde = (c[:, 1] > 0.45)
gi = np.where(verde)[0]
dv, _ = cKDTree(Pw[gi]).query(Pw, k=1)
from scipy.sparse.csgraph import connected_components
ytop = np.percentile(Pw[verde, 1], 5)
ybot = Pw[:, 1].min()
tt = np.clip((Pw[:, 1] - ybot) / (ytop - ybot), 0, 1)  # 0 tip, 1 shoulder
sparse_top = 1 + 0.8 * np.clip((tt - 0.6) / 0.4, 0, 1)  # spacing grows toward the calyx

# one seed per pit: pit = connected patch of h < PIT; its seed = the patch vertex nearest the depth-weighted centroid
PIT = -0.0025
m = (h < PIT) & ~verde & (dv > 0.02)
idx = np.where(m)[0]
nc, lab = connected_components(A[idx][:, idx], directed=False)
pits = []
for k in range(nc):
    vs = idx[lab == k]
    if len(vs) < 6:
        continue
    ext = np.linalg.norm(Pw[vs].max(0) - Pw[vs].min(0))
    if ext > 0.05:  # merged pits: local minima of h within 0.015
        tk = cKDTree(Pw[vs]); done = np.zeros(len(vs), bool)
        for i in np.argsort(h[vs]):
            if done[i]:
                continue
            pits.append(vs[i]); done[tk.query_ball_point(Pw[vs[i]], 0.015)] = True
        continue
    wgt = PIT - h[vs]
    cen = (Pw[vs] * wgt[:, None]).sum(0) / wgt.sum()
    pits.append(vs[np.argmin(np.linalg.norm(Pw[vs] - cen, axis=1))])
cand = np.array(pits)
keep, pts = [], np.empty((0, 3))
for v in cand[np.argsort(h[cand])]:  # deepest first; two seeds never closer than 0.02
    if len(pts) and np.min(np.linalg.norm(pts - Pw[v], axis=1)) < 0.02 * sparse_top[v]:
        continue
    keep.append(v); pts = np.vstack([pts, Pw[v]])
n_pit = len(keep)
# fill the gaps wider than D_MIN on red skin (even spacing), random order, fixed seed
rng = np.random.default_rng(3)
for v in rng.permutation(np.where(rojo & (dv > 0.03))[0]):
    if len(keep) >= N_MAX:
        break
    if np.min(np.linalg.norm(pts - Pw[v], axis=1)) < D_MIN * sparse_top[v]:
        continue
    keep.append(v); pts = np.vstack([pts, Pw[v]])
keep = np.array(keep)
n = vn[keep]
down = np.array([0, -1, 0.0])
ax = down - (n @ down)[:, None] * n
ax /= np.linalg.norm(ax, axis=1, keepdims=True) + 1e-12
np.savez(f'{out}/semillas.npz', p=Pw[keep], n=n, ax=ax, h=h[keep], pit=np.arange(len(keep)) < n_pit)
print('verts', nv, 'pit patches', nc, 'pit seeds', n_pit, 'fill seeds', len(keep) - n_pit, 'total', len(keep))
print('pit depth (pit seeds)', np.percentile(-h[keep[:n_pit]], [5, 50, 95]).round(4))
nn_d, _ = cKDTree(Pw[keep]).query(Pw[keep], k=2)
print('nn spacing', np.percentile(nn_d[:, 1], [5, 50, 95]).round(4))
