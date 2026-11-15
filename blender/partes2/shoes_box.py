# shoes_box.py <shoes.glb> <shoes.json> <target.npz> <pants_body.npz> <out.npz> [zscale]: the shoes placed per side by a
# per-axis box fit onto
# the fused Diego's shoe region (target.npz label "shoes", the owner's reference), replacing fit_body.py for shoes.
# Why: TRELLIS guessed the shoes' depth from a front-view part image (28 cm long against an 18.5 cm foot), and
# fit_body.py's uniform-scale ICP onto the bare foot could not shorten them, so the heel hung 8.6 cm behind the leg; its
# push-out against the bare toes crumpled the toe box. No push-out here: the foot is masked under the shoe.
# Extents are the 1st-99th percentiles (label noise); z sits on the region's floor, x and y are centred. zscale, when
# given, replaces the fitted height scale. Leave it out: the fitted top (~0.09) is the source's own shoe height
# (diego.png measures ~0.083 of the figure), and the cuff rests on it as in the source; keeping TRELLIS's height (1.0)
# put the cuff inside the shoe.
# Line-up (owner, 00:39: cuffs and shoes still off): the box sits where the fused Diego's shoes were, but the new body's
# legs stand elsewhere (the leg met the shoe at 57 % of its length from the toe, the reference at 74 %). So each shoe
# then slides in x and y until the pant leg's centre at the shoe top (fitted pants, z top..top+15 mm) sits at the
# same fractions of the shoe box as the reference leg (pants/skin labels at z 0.115) sits in the reference shoe.
# Writes P (GLB vertex order), keep (all), T (the start) as dress.py reads; prints each side's scale and box.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from fitlib import load_glb, apply

glb, start, tnpz, pnpz, out = sys.argv[1:6]; zs = float(sys.argv[6]) if len(sys.argv) > 6 else None
Pa = np.load(pnpz); PA = Pa["P"][Pa["keep"]]
G0, _, _ = load_glb(glb); T = np.array(json.load(open(start))["T"]); P = apply(T, G0)
t = np.load(tnpz); R = t["V"][t["lab"] == "shoes"]; LEG = t["V"][np.isin(t["lab"], ["pants", "skin"])]
for sg in (-1, 1):
    m = np.sign(P[:, 0]) == sg; S = P[m]; Q = R[np.sign(R[:, 0]) == sg]
    ls, hs = np.percentile(S, 1, 0), np.percentile(S, 99, 0); lt, ht = np.percentile(Q, 1, 0), np.percentile(Q, 99, 0)
    k = (ht - lt) / (hs - ls); k[2] = zs or k[2]; cs, ct = (ls + hs) / 2, (lt + ht) / 2
    N = ct + (S - cs) * k; N[:, 2] += lt[2] - (ct[2] + (ls[2] - cs[2]) * k[2])   # floor on the region's floor
    leg = LEG[(np.sign(LEG[:, 0]) == sg) & (np.abs(LEG[:, 2] - 0.115) < 0.005)][:, :2].mean(0)
    f = (leg - lt[:2]) / (ht[:2] - lt[:2])                                   # the reference leg in its shoe box
    top = N[:, 2].max(); pl = PA[(np.sign(PA[:, 0]) == sg) & (PA[:, 2] > top) & (PA[:, 2] < top + 0.015)][:, :2].mean(0)
    lo, hi = np.percentile(N, 1, 0)[:2], np.percentile(N, 99, 0)[:2]
    d = pl - (lo + f * (hi - lo)); N[:, :2] += d
    print("@@ shoe x%+d: leg at %.2f / %.2f of the box (reference), slid x %+.1f y %+.1f mm" % (sg, f[0], f[1], d[0] * 1000, d[1] * 1000))
    P[m] = N
    print("@@ shoe x%+d: scale x %.3f y %.3f z %.3f; box y %.3f..%.3f (was %.3f..%.3f) z %.3f..%.3f" % (
        sg, *k, N[:, 1].min(), N[:, 1].max(), S[:, 1].min(), S[:, 1].max(), N[:, 2].min(), N[:, 2].max()))
np.savez(out, P=P, keep=np.ones(len(P), bool), T=T)
