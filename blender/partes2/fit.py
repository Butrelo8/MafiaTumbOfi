# fit.py <part> <part.glb> <target.npz> <out.json> [body.glb body.json]: one part's placement in the upload frame.
#   body : start from the arm span and the soles, ICP (with scale) onto the fused Diego's bare skin above the waist
#          (face, neck, arms, hands; the bald body has no hair and the fused legs are trousers).
#   head : onto the placed body's head (body vertices above the chin line), start from the head's width and top.
#   hair / shirt / pants / shoes : onto the fused Diego's region of that colour and height, start from the region's box.
# Prints the scale, the trimmed residual (mm, target -> part) and writes {"T": 4x4, ...}.
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python -I drops the script dir
import numpy as np
from fitlib import load_glb, apply, bbox_init, icp

part, glb, tnpz, out = sys.argv[1:5]
t = np.load(tnpz); TV, lab = t["V"], t["lab"]
V, F, C = load_glb(glb)
z = TV[:, 2]
if part == "body":
    tgt = TV[(lab == "skin") & (z > 0.30)]
    T0 = bbox_init(V, TV, scale_axis=0, anchor=("c", "c", "min"))
elif part == "head":
    BV, _, _ = load_glb(sys.argv[5]); TB = np.array(json.load(open(sys.argv[6]))["T"])
    B = apply(TB, BV); tgt = B[B[:, 2] > 0.62]                       # chin at ~0.61 (rerig marker table)
    top = V[V[:, 2] > V[:, 2].max() - 0.6 * (V[:, 2].max() - V[:, 2].min())]
    T0 = bbox_init(top, tgt, scale_axis=0, anchor=("c", "c", "max"))
else:
    sel = {"hair": lab == "hair",
           "shirt": (lab == "shirt") & (np.abs(TV[:, 0]) < 0.30),
           "pants": (lab == "pants") & (z > 0.06),
           "shoes": lab == "shoes"}[part]
    tgt = TV[sel]
    T0 = bbox_init(V, tgt, scale_axis=None, anchor=("c", "c", "min"))
T, d = icp(V, tgt, T0)
s = float(np.cbrt(np.linalg.det(T[:3, :3])))
P = apply(T, V)
res = {"part": part, "glb": glb, "T": T.tolist(), "scale": s, "n_target": int(len(tgt)),
       "resid_mm": {"p50": float(np.median(d) * 1000), "p90": float(np.quantile(d, 0.9) * 1000), "max": float(d.max() * 1000)},
       "bounds": [P.min(0).round(4).tolist(), P.max(0).round(4).tolist()]}
json.dump(res, open(out, "w"), indent=1)
print(part, "scale %.4f" % s, "resid p50/p90/max mm %.1f / %.1f / %.1f" % tuple(res["resid_mm"].values()), "bounds", res["bounds"])
