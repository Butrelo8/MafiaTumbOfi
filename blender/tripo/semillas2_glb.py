# semillas2_glb.py in.glb semillas.npz out.glb size sink colour [min_gap]
# Pass 2 of the 3D seeds: the same seed list as semillas_glb.py (b), but the ellipsoids are `size` times pass 1's, placed with its centre `sink`
# (model units) ABOVE the pit floor along the normal (centre height: 0 = half buried, bigger = more proud), in `colour` (amarilla = pass 1's yellow, oro = gold, satin). Seeds closer than
# `min_gap` to an already kept one are dropped (greedy, in list order), so bigger seeds do not fuse. Only a seed mesh, its
# material and its node are appended: every original bufferView stays byte-identical (semillas_verif.py checks).
import sys, json, numpy as np
sys.path.insert(0, '.'); import glbio

src, npz, out, size, sink, colour = sys.argv[1:7]
size, sink = float(size), float(sink)
min_gap = float(sys.argv[7]) if len(sys.argv) > 7 else 0.0
A_L, A_W = 0.014, 0.009
COL = {'amarilla': ((245, 206, 46), (214, 158, 22), 0.0, 0.4),     # pass 1: sRGB centre, rim, metallic, roughness
       'oro': ((236, 178, 38), (196, 128, 14), 0.55, 0.32)}
(c_c, c_e, metal, rough) = COL[colour]
s = np.load(npz)
SP, SN, SA = s['p'], s['n'], s['ax']
SB = np.cross(SN, SA)
keep = []
for i in range(len(SP)):
    if not keep or np.linalg.norm(SP[keep] - SP[i], axis=1).min() >= min_gap:
        keep.append(i)
SP, SN, SA, SB = SP[keep], SN[keep], SA[keep], SB[keep]
j, b = glbio.load(src)
views = [glbio.view(j, b, i) for i in range(len(j['bufferViews']))]
rng = np.random.default_rng(7)
nu, nvv = 10, 7
th = np.linspace(0, np.pi, nvv)[1:-1]; ph = np.linspace(0, 2 * np.pi, nu, endpoint=False)
unit = [np.array([0, 0, -1.0])] + [np.array([np.sin(a) * np.cos(c), np.sin(a) * np.sin(c), -np.cos(a)]) for a in th for c in ph] + [np.array([0, 0, 1.0])]
unit = np.array(unit)
tris = [(0, 1 + (i + 1) % nu, 1 + i) for i in range(nu)]
for r_ in range(len(th) - 1):
    for i in range(nu):
        a_, b_ = 1 + r_ * nu + i, 1 + r_ * nu + (i + 1) % nu
        tris += [(a_, b_, b_ + nu), (a_, b_ + nu, a_ + nu)]
top = len(unit) - 1; last = 1 + (len(th) - 1) * nu
tris += [(last + i, last + (i + 1) % nu, top) for i in range(nu)]
tris = np.array(tris)
HALF = np.array([A_L * 0.85, A_W * 0.8, 0.0045]) * size


def rot(axis, ang):
    axis = axis / np.linalg.norm(axis); K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K


VP, VN, VI = [], [], []
for i in range(len(SP)):
    R = np.stack([SA[i], SB[i], SN[i]], 1)
    # tilt/spin drawn exactly as pass 1 (same rng stream over the full list would differ after thinning: draw per kept seed)
    tilt = rot(R @ np.array([np.cos(q := rng.uniform(0, 2 * np.pi)), np.sin(q), 0]), np.radians(rng.uniform(0, 12)))
    spin = rot(SN[i], np.radians(rng.uniform(-20, 20)))
    M = tilt @ spin @ R
    VI.append(tris + len(VP) * len(unit))
    VP.append(SP[i] + SN[i] * sink + (unit * HALF) @ M.T)
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
mid = (np.array(c_c) + np.array(c_e)) / 2 / 255
jb['materials'].append({'name': 'semilla_' + colour, 'pbrMetallicRoughness': {
    'baseColorFactor': [*lin(mid).round(4).tolist(), 1.0], 'metallicFactor': metal, 'roughnessFactor': rough}})
jb['meshes'].append({'name': 'semillas', 'primitives': [{'mode': 4, 'material': len(jb['materials']) - 1, 'indices': na + 2,
                                                          'attributes': {'POSITION': na, 'NORMAL': na + 1}}]})
jb['nodes'].append({'name': 'semillas', 'mesh': len(jb['meshes']) - 1})
jb['scenes'][0]['nodes'].append(len(jb['nodes']) - 1)
glbio.save(out, jb, vb)
print(out, 'seeds', len(SP), 'of', len(s['p']), 'size', size, 'sink', sink, colour, 'verts', len(VP), 'tris', len(VI) // 3)
