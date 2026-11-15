# shoes_box.py <shoes.glb> <shoes.json> <target.npz> <out.npz> [zscale]: the shoes placed per side by a per-axis box fit onto
# the fused Diego's shoe region (target.npz label "shoes", the owner's reference), replacing fit_body.py for shoes.
# Why: TRELLIS guessed the shoes' depth from a front-view part image (28 cm long against an 18.5 cm foot), and
# fit_body.py's uniform-scale ICP onto the bare foot could not shorten them, so the heel hung 8.6 cm behind the leg; its
# push-out against the bare toes crumpled the toe box. No push-out here: the foot is masked under the shoe.
# Extents are the 1st-99th percentiles (label noise); z sits on the region's floor, x and y are centred. zscale, when
# given, replaces the fitted height scale (the region's label stops at z 0.10, so its height may be short).
# Writes P (GLB vertex order), keep (all), T (the start) as dress.py reads; prints each side's scale and box.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from fitlib import load_glb, apply

glb, start, tnpz, out = sys.argv[1:5]; zs = float(sys.argv[5]) if len(sys.argv) > 5 else None
G0, _, _ = load_glb(glb); T = np.array(json.load(open(start))["T"]); P = apply(T, G0)
t = np.load(tnpz); R = t["V"][t["lab"] == "shoes"]
for sg in (-1, 1):
    m = np.sign(P[:, 0]) == sg; S = P[m]; Q = R[np.sign(R[:, 0]) == sg]
    ls, hs = np.percentile(S, 1, 0), np.percentile(S, 99, 0); lt, ht = np.percentile(Q, 1, 0), np.percentile(Q, 99, 0)
    k = (ht - lt) / (hs - ls); k[2] = zs or k[2]; cs, ct = (ls + hs) / 2, (lt + ht) / 2
    N = ct + (S - cs) * k; N[:, 2] += lt[2] - (ct[2] + (ls[2] - cs[2]) * k[2])   # floor on the region's floor
    P[m] = N
    print("@@ shoe x%+d: scale x %.3f y %.3f z %.3f; box y %.3f..%.3f (was %.3f..%.3f) z %.3f..%.3f" % (
        sg, *k, N[:, 1].min(), N[:, 1].max(), S[:, 1].min(), S[:, 1].max(), N[:, 2].min(), N[:, 2].max()))
np.savez(out, P=P, keep=np.ones(len(P), bool), T=T)
