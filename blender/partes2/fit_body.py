# fit_body.py <kind> <garment.glb> <start.json> <body.glb> <body.json> <head.glb> <head.json> <out.npz> [under.glb:under.npz]: a garment onto
# the NEW body (the fused-Diego fit, fit.py, is only the start: the new body's torso and legs sit a few cm off the fused
# clothes). kind: shirt | pants | shoes | hair.
#  1. ICP (scale; hair, shirt and pants also per-axis scale) of the garment onto the body surface pushed out by EASE along its normals,
#     using only body points the started garment already covers (within 3 cm) inside the kind's height band.
#     Hair fits the head part's scalp (the visible head), the rest fit body.glb.
#  2. (Nothing is dropped any more, DEEP = 1 m: the TRELLIS garments are open shells; an early version dropped what
#     sat inside the body as caps and cut real panels out.) The optional under-garment (pants under the shirt) is a
#     second collider: the shirt must also clear its outer side.
#  3. Push-out: any vertex closer than GAP to the body (or inside) moves out along the body normal; the displacement is
#     smoothed over the garment's edges so the cloth does not dent, then re-clamped.
# Signed distance = (p - q) . n to the nearest of ~600k body surface samples (q, n): ~1 mm spacing.
# Writes the final per-vertex positions in GLB vertex order, a keep mask, T, and prints the numbers.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, trimesh
from scipy.spatial import cKDTree
from fitlib import load_glb, apply, umeyama

kind, gglb, start, bglb, bjson, hglb, hjson, out = sys.argv[1:9]
EASE = {"shirt": 0.006, "pants": 0.005, "shoes": 0.003, "hair": 0.004}[kind]
GAP = 0.002
DEEP = 1.0   # no drop: the TRELLIS garments are open shells (neck, sleeves, hem, waist, cuffs open); what sits inside is real panel


def placed(glb, js):
    V, F, _ = load_glb(glb); return apply(np.array(json.load(open(js))["T"]), V), F


def samples(V, F, n=600000):
    """Surface samples of the largest component only, normals made consistent (TRELLIS leaves hundreds of small inner
    pieces whose normals flip the sign of the distance)."""
    m = trimesh.Trimesh(V, F, process=True)
    m = max(m.split(only_watertight=False), key=lambda c: len(c.faces)); m.fix_normals()
    pts, fi = trimesh.sample.sample_surface(m, n)
    return pts, m.face_normals[fi]


BV, BF = placed(bglb, bjson)
if kind == "hair":
    HV, HF = placed(hglb, hjson); S, N = samples(HV, HF)
    band = (S[:, 2] > 0.83) | ((S[:, 1] > 0.02) & (S[:, 2] > 0.66))
    band &= ~((np.abs(S[:, 0]) > 0.15) & (S[:, 2] < 0.80))                       # ears stay out
else:
    S, N = samples(BV, BF)
    lo, hi = {"shirt": (0.27, 0.60), "pants": (0.04, 0.32), "shoes": (-1, 0.10)}[kind]
    band = (S[:, 2] > lo) & (S[:, 2] < hi)
G0, GF, _ = load_glb(gglb); T = np.array(json.load(open(start))["T"]); G = apply(T, G0)
near = cKDTree(G).query(S, distance_upper_bound=0.03)[0] < 0.03
tgt = (S + EASE * N)[band & near]
print(kind, "target points", len(tgt))
for it in range(40):                                   # 1. ICP, garment -> body + ease
    P = apply(T, G0); d, j = cKDTree(P).query(tgt); k = d <= np.quantile(d, 0.85)
    Tn = umeyama(G0[j[k]], tgt[k])
    if kind in ("hair", "shirt", "pants"):           # per-axis scale in the body frame (TRELLIS guesses a front-view garment's depth)
        A = apply(Tn, G0[j[k]]); B = tgt[k]; ca, cb = A.mean(0), B.mean(0)
        sx = ((A - ca) * (B - cb)).sum(0) / ((A - ca) ** 2).sum(0)
        Sx = np.eye(4); Sx[:3, :3] = np.diag(sx); Sx[:3, 3] = cb - sx * ca; Tn = Sx @ Tn
    if np.abs(Tn - T).max() < 1e-7: T = Tn; break
    T = Tn
P = apply(T, G0); d, _ = cKDTree(P).query(tgt)
print(kind, "ICP to body+ease: p50 %.1f p90 %.1f mm, scale %.3f" % (np.median(d) * 1000, np.quantile(d, 0.9) * 1000, np.cbrt(np.linalg.det(T[:3, :3]))))
tree = cKDTree(S)
if len(sys.argv) > 9:  # layering: a garment worn under this one (pants under the shirt) also pushes it out
    ug, unpz = sys.argv[9].split(":"); U = np.load(unpz); UV, UF, _ = load_glb(ug); UV = U["P"]
    UF = UF[U["keep"][UF].all(1)]; um = trimesh.Trimesh(UV, UF, process=False)
    S2, f2 = trimesh.sample.sample_surface(um, 300000); N2 = um.face_normals[f2]
    N2 *= np.sign(((S2 - S[tree.query(S2)[1]]) * N2).sum(1) + 1e-12)[:, None]   # face away from the body
    S2 = S2 + 0.001 * N2; tree2 = cKDTree(S2)                                       # the under-layer's outer side
    print(kind, "layered over", os.path.basename(ug))
else:
    tree2 = None


def sdist(P):
    _, i = tree.query(P); d, n = ((P - S[i]) * N[i]).sum(1), N[i]
    if tree2 is not None:
        d2, j = tree2.query(P); s2 = ((P - S2[j]) * N2[j]).sum(1)
        use = (d2 < 0.03) & (s2 < d)                 # only where the under-layer is near and the tighter constraint
        d, n = np.where(use, s2, d), np.where(use[:, None], N2[j], n)
    return d, n


if kind == "hair":     # rigid, bone-parented: no deformation, no holes; grow it about the head centre until it clears
    HV2 = HV[HV[:, 2] > 0.70]; c = HV2.mean(0)
    for s_in in np.arange(1.0, 1.4, 0.005):
        Ps = c + s_in * (P - c); sd, n = sdist(Ps)
        if (sd < GAP).mean() < 0.002: break
    sd, n = sdist(Ps); hard = sd < GAP; Ps[hard] += (GAP - sd[hard])[:, None] * n[hard]
    print("@@ hair rest: grown x%.3f about the head centre, %d verts clamped to %.0f mm, kept all %d" % (s_in, hard.sum(), GAP * 1000, len(Ps)))
    np.savez(out, P=Ps, keep=np.ones(len(Ps), bool), T=T); raise SystemExit
sd, _ = sdist(P); keep = sd > -DEEP                    # 2. caps and inner shells
print(kind, "dropped %d of %d vertices deeper than %.0f mm" % ((~keep).sum(), len(P), DEEP * 1000))
E = np.unique(np.sort(np.r_[GF[:, [0, 1]], GF[:, [1, 2]], GF[:, [2, 0]]], 1), axis=0)
deg = np.bincount(E.ravel(), minlength=len(P)).astype(float)
for rnd in range(4):                                   # 3. push-out with a smoothed displacement
    sd, n = sdist(P); need = np.where(keep & (sd < GAP), GAP - sd, 0.0)
    if not need.any(): break
    D0 = need[:, None] * n; D = D0.copy()
    for _ in range(15):                                # harmonic extension: pushed vertices fixed, the rest averaged
        acc = np.zeros_like(D); np.add.at(acc, E[:, 0], D[E[:, 1]]); np.add.at(acc, E[:, 1], D[E[:, 0]])
        D = np.where(need[:, None] > 0, D0, acc / np.maximum(deg, 1)[:, None])
    P = P + D * keep[:, None]
    print(kind, "push-out round %d: %d vertices under %.0f mm, max %.1f mm" % (rnd, (need > 0).sum(), GAP * 1000, need.max() * 1000))
if kind == "pants": keep &= P[:, 2] < 0.29             # the waistband above the shirt hem (0.275) only makes a shelf at the back
sd, n = sdist(P)       # what the smoothed push-out leaves stays as is and is reported (a hard clamp crumpled the shirt)
print("@@", kind, "rest: kept %d verts, min clearance %.2f mm, under 1 mm: %d, inside: %d" % (
    keep.sum(), sd[keep].min() * 1000, (sd[keep] < 0.001).sum(), (sd[keep] < 0).sum()))
np.savez(out, P=P, keep=keep, T=T)
