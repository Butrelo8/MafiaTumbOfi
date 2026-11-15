# semillas_glb.py in.glb semillas.npz out_a.glb out_b.glb [sign]  (one seed list for both variants)
# (a) painted: yellow ellipses in the base colour + a dome bump in the normal map, both by 3D distance to each seed (so a dot
#     spanning a UV seam stays whole); only texels inside a seed change, written as PNG (no JPEG re-encode of the rest).
# (b) geometry: one extra mesh of small yellow ellipsoids, each sunk part-way into its pit, slight random tilt. The friend's
#     mesh and textures stay byte-identical.
import sys, io, json, numpy as np, cv2
from scipy.spatial import cKDTree
from PIL import Image
sys.path.insert(0, '.'); import glbio

src, npz, out_a, out_b = sys.argv[1:5]
A_L, A_W = 0.014, 0.009          # seed half-length (down the berry) and half-width, model units (1 = 4.1 cm in the scene)
YEL_C = np.array([245, 206, 46]) / 255.0   # sRGB, centre
YEL_E = np.array([214, 158, 22]) / 255.0   # sRGB, rim
BUMP_H = 0.002  # dome height; +1 sign = raised (checked under a top light, estudio.py rasante)
SIGN = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
s = np.load(npz)
SP, SN, SA = s['p'], s['n'], s['ax']
SB = np.cross(SN, SA)
j, b = glbio.load(src)
prim = j['meshes'][0]['primitives'][0]


def acc(i, comps, dt):
    a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(b, dt, a['count'] * comps, off).reshape(a['count'], comps)


views = [glbio.view(j, b, i) for i in range(len(j['bufferViews']))]

# ------------------------------------------------------------------ (a)
P = acc(prim['attributes']['POSITION'], 3, np.float32).astype(np.float64)
UV = acc(prim['attributes']['TEXCOORD_0'], 2, np.float32).astype(np.float64)
I = acc(prim['indices'], 1, np.uint32).reshape(-1, 3).astype(np.int64)
col = np.asarray(Image.open(io.BytesIO(views[j['images'][0]['bufferView']])).convert('RGB')).copy()
nrm = np.asarray(Image.open(io.BytesIO(views[j['images'][2]['bufferView']])).convert('RGB')).copy()
S = col.shape[0]
ids = np.zeros((S, S), np.int32)
SH = 4
tri_px = np.round(UV[I] * S * (1 << SH) - 0.5 * (1 << SH)).astype(np.int32)  # texel centres at (i+0.5)/S
for k in range(len(I)):
    cv2.fillConvexPoly(ids, tri_px[k], k + 1, lineType=cv2.LINE_8, shift=SH)
yy, xx = np.nonzero(ids)
t = ids[yy, xx] - 1
u = (xx + 0.5) / S; v = (yy + 0.5) / S
a0, a1, a2 = UV[I[t, 0]], UV[I[t, 1]], UV[I[t, 2]]
d1, d2 = a1 - a0, a2 - a0
den = d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]
den = np.where(np.abs(den) < 1e-14, 1e-14, den)
qx, qy = u - a0[:, 0], v - a0[:, 1]
w1 = (qx * d2[:, 1] - qy * d2[:, 0]) / den
w2 = (d1[:, 0] * qy - d1[:, 1] * qx) / den
w0 = 1 - w1 - w2
p0, p1, p2 = P[I[t, 0]], P[I[t, 1]], P[I[t, 2]]
pos = w0[:, None] * p0 + w1[:, None] * p1 + w2[:, None] * p2
dist, si = cKDTree(SP).query(pos, k=1, distance_upper_bound=A_L * 1.5)
near = np.isfinite(dist)
yy, xx, t, pos, si = yy[near], xx[near], t[near], pos[near], si[near]
d1, d2, den, p0, p1, p2 = d1[near], d2[near], den[near], p0[near], p1[near], p2[near]
rel = pos - SP[si]
dt_ = (rel * SA[si]).sum(1); db_ = (rel * SB[si]).sum(1); dn_ = (rel * SN[si]).sum(1)
r = np.sqrt((dt_ / A_L) ** 2 + (db_ / A_W) ** 2)
c0 = col[yy, xx].astype(np.float64) / 255
red = c0[:, 1] < 0.8 * c0[:, 0]  # not the green calyx (pit texels are darker orange-red, keep them)
inside = (r < 1.0) & red & (np.abs(dn_) < 0.004)  # pit floor only: on steep pit walls the ellipse smears
# texel size in model units here: for AA width
e1, e2 = p1 - p0, p2 - p0
dPdu = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) / den[:, None]
dPdv = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) / den[:, None]
texel = np.linalg.norm(dPdu, axis=1) / S
aa = np.clip((1 - r) * A_W / np.maximum(texel, 1e-9) + 0.5, 0, 1) * inside      # ~1-texel soft edge
yel = YEL_E + (YEL_C - YEL_E) * np.clip(1 - r, 0, 1)[:, None] ** 0.6
new = c0 * (1 - aa[:, None]) + yel * aa[:, None]
painted = aa > 0
col_a = col.copy()
col_a[yy[painted], xx[painted]] = np.round(new[painted] * 255).astype(np.uint8)
# bump: h = H (1 - r^2)^2, grad in 3D; n' = normalize(n_ts - (g.T, g.B, 0)), T = dP/du, B = dP/d(-v) (glTF normal maps: +Y up)
with np.errstate(invalid="ignore", divide="ignore"):
    fn = np.cross(e1, e2); fn /= np.linalg.norm(fn, axis=1, keepdims=True)
    T = dPdu - (dPdu * fn).sum(1, keepdims=True) * fn; T /= np.linalg.norm(T, axis=1, keepdims=True)
    B = -dPdv - (-dPdv * fn).sum(1, keepdims=True) * fn; B /= np.linalg.norm(B, axis=1, keepdims=True)
bump = inside & np.isfinite(T).all(1) & np.isfinite(B).all(1)  # degenerate UV or 3D triangles give no frame
k = -4 * BUMP_H * (1 - r ** 2)
g = k[:, None] * ((dt_ / A_L ** 2)[:, None] * SA[si] + (db_ / A_W ** 2)[:, None] * SB[si])
nts = nrm[yy, xx].astype(np.float64) / 255 * 2 - 1
nts[:, 0] -= (g * T).sum(1) * SIGN
nts[:, 1] -= (g * B).sum(1) * SIGN
nts /= np.linalg.norm(nts, axis=1, keepdims=True)
nrm_a = nrm.copy()
nrm_a[yy[bump], xx[bump]] = np.round((nts[bump] * 0.5 + 0.5) * 255).astype(np.uint8)
# gutters: uncovered texels within 4 px take the value of their nearest covered texel, only where that one changed
cov = (ids > 0).astype(np.uint8)
dist_g, lab = cv2.distanceTransformWithLabels(1 - cov, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
cy, cx = np.nonzero(cov)  # label i -> i-th zero pixel of (1-cov) in scan order = i-th covered texel
src_y = np.zeros(lab.max() + 1, np.int64); src_x = np.zeros(lab.max() + 1, np.int64)
src_y[1:len(cy) + 1] = cy; src_x[1:len(cx) + 1] = cx
gy, gx = np.nonzero((cov == 0) & (dist_g <= 4))
ly, lx = src_y[lab[gy, gx]], src_x[lab[gy, gx]]
for img_new, img_old in ((col_a, col), (nrm_a, nrm)):
    ch = np.any(img_new[ly, lx] != img_old[ly, lx], axis=1)
    img_new[gy[ch], gx[ch]] = img_new[ly[ch], lx[ch]]
chg_c = np.any(col_a != col, axis=2); chg_n = np.any(nrm_a != nrm, axis=2)
print('texel(model units) median', np.median(texel).round(6), 'seed length in texels', round(2 * A_L / np.median(texel), 1))
print('changed texels: colour', int(chg_c.sum()), f'({chg_c.mean() * 100:.2f} %)', 'normal', int(chg_n.sum()),
      'seeds with paint', len(np.unique(si[painted])), 'of', len(SP))


def png(a):
    bio = io.BytesIO(); Image.fromarray(a).save(bio, 'PNG', compress_level=6); return bio.getvalue()


ja = json.loads(json.dumps(j)); va = list(views)
va[ja['images'][0]['bufferView']] = png(col_a); ja['images'][0]['mimeType'] = 'image/png'
ja['images'][0]['name'] = 'strawberry_basecolor_semillas.png'
va[ja['images'][2]['bufferView']] = png(nrm_a)
glbio.save(out_a, ja, va)
cv2.imwrite(out_a.replace('.glb', '_mask.png'), (chg_c * 255).astype(np.uint8))

# ------------------------------------------------------------------ (b)
rng = np.random.default_rng(7)
nu, nvv = 10, 7
th = np.linspace(0, np.pi, nvv)[1:-1]; ph = np.linspace(0, 2 * np.pi, nu, endpoint=False)
unit = [np.array([0, 0, -1.0])] + [np.array([np.sin(a) * np.cos(c), np.sin(a) * np.sin(c), -np.cos(a)]) for a in th for c in ph] + [np.array([0, 0, 1.0])]
unit = np.array(unit)  # x = along, y = across, z = normal
tris = [(0, 1 + (i + 1) % nu, 1 + i) for i in range(nu)]
for r_ in range(len(th) - 1):
    for i in range(nu):
        a_, b_ = 1 + r_ * nu + i, 1 + r_ * nu + (i + 1) % nu
        tris += [(a_, b_, b_ + nu), (a_, b_ + nu, a_ + nu)]
top = len(unit) - 1; last = 1 + (len(th) - 1) * nu
tris += [(last + i, last + (i + 1) % nu, top) for i in range(nu)]
tris = np.array(tris)
HALF = np.array([A_L * 0.85, A_W * 0.8, 0.0045])
SINK = 0.0015  # centre above the pit floor: ~1/3 of the seed below the floor, its top just over the pit rim
VP, VN, VI = [], [], []


def rot(axis, ang):
    axis = axis / np.linalg.norm(axis); K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K


for i in range(len(SP)):
    R = np.stack([SA[i], SB[i], SN[i]], 1)  # columns: along, across, normal
    tilt = rot(R @ np.array([np.cos(q := rng.uniform(0, 2 * np.pi)), np.sin(q), 0]), np.radians(rng.uniform(0, 12)))
    spin = rot(SN[i], np.radians(rng.uniform(-20, 20)))
    M = tilt @ spin @ R
    VI.append(tris + len(VP) * len(unit))
    VP.append(SP[i] + SN[i] * SINK + (unit * HALF) @ M.T)
    nn = (unit / HALF) @ M.T; VN.append(nn / np.linalg.norm(nn, axis=1, keepdims=True))
VP = np.concatenate(VP).astype(np.float32); VN = np.concatenate(VN).astype(np.float32)
VI = np.concatenate(VI).astype(np.uint32).ravel()
jb = json.loads(json.dumps(j)); vb = list(views)
base = len(vb)
for data in (VP.tobytes(), VN.tobytes(), VI.tobytes()):
    jb['bufferViews'].append({'buffer': 0, 'byteOffset': 0, 'byteLength': len(data)}); vb.append(data)
na = len(jb['accessors'])
jb['accessors'] += [
    {'bufferView': base, 'componentType': 5126, 'count': len(VP), 'type': 'VEC3', 'min': VP.min(0).tolist(), 'max': VP.max(0).tolist()},
    {'bufferView': base + 1, 'componentType': 5126, 'count': len(VN), 'type': 'VEC3'},
    {'bufferView': base + 2, 'componentType': 5125, 'count': len(VI), 'type': 'SCALAR'}]
lin = lambda c: np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
jb['materials'].append({'name': 'semilla_amarilla', 'pbrMetallicRoughness': {
    'baseColorFactor': [*lin((YEL_C + YEL_E) / 2).round(4).tolist(), 1.0], 'metallicFactor': 0.0, 'roughnessFactor': 0.4}})
jb['meshes'].append({'name': 'semillas', 'primitives': [{'mode': 4, 'material': len(jb['materials']) - 1, 'indices': na + 2,
                                                          'attributes': {'POSITION': na, 'NORMAL': na + 1}}]})
jb['nodes'].append({'name': 'semillas', 'mesh': len(jb['meshes']) - 1})
jb['scenes'][0]['nodes'].append(len(jb['nodes']) - 1)
glbio.save(out_b, jb, vb)
print('(b) seeds', len(SP), 'verts', len(VP), 'tris', len(VI) // 3)
