# lids_fit.py <head.glb> <head.json> <out.json>: upper-lid shape keys laid on each eye's own surface, for lids_build.py.
# The eye = the head's white vertices (bright, low saturation) plus the dark pupil vertices inside their box, front of
# the face. TRELLIS's eye is a near-flat disc, so a sphere fit is unstable (tried: centres 70-85 deg below the whites);
# instead the lid is an NI x NJ grid (24 x 12) over the eye's front outline (x columns, rows down from the eye's top edge), each point
# OFF (4 mm) in front of the eye surface (front-most of the 12 nearest eye vertices, depth box-smoothed; the outline is the white's only, its top
# being the painted lid line). Keys: open = rows within 1 mm of the top edge,
# half = down to mid-eye, closed = down to the bottom edge + 1 mm. Every key lies on the eye surface, so a blink
# through the half key does not cut into the eye (the research's linear shape-key pitfall).
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.spatial import cKDTree
from fitlib import load_glb, apply
NI, NJ, OFF = 24, 12, 0.004    # 16 x 8 at 2-3 mm let faces sag behind the bulging eye (white showed through in blocks)
V, F, C = load_glb(sys.argv[1]); V = apply(np.array(json.load(open(sys.argv[2]))["T"]), V)
lum = C.mean(1); sat = C.max(1) - C.min(1)
box = (V[:, 2] > 0.72) & (V[:, 2] < 0.84) & (V[:, 1] < -0.10) & (np.abs(V[:, 0]) > 0.02) & (np.abs(V[:, 0]) < 0.14)
res = {}
for side, sd in (("R", -1), ("L", 1)):
    Wt = box & (lum > 170) & (sat < 30) & (sd * V[:, 0] > 0)
    lo, hi = V[Wt].min(0), V[Wt].max(0)
    Wp = V[Wt]; xs = np.linspace(*np.percentile(Wp[:, 0], [3, 97]), NI)
    top, bot = [], []                                  # the WHITE's outline: its top is the painted lid line
    for x in xs:
        S = Wp[np.abs(Wp[:, 0] - x) < 0.002]; top.append(np.percentile(S[:, 2], 98)); bot.append(np.percentile(S[:, 2], 2))
    top, bot = np.array(top), np.array(bot)
    E = Wt | (box & (lum < 90) & (sd * V[:, 0] > 0) & np.all((V >= lo) & (V <= hi), 1) & (V[:, 2] < top.max()))  # + pupil
    P = V[box & (sd * V[:, 0] > 0)]; tree = cKDTree(P[:, [0, 2]])   # depth from EVERY head vertex there: the sculpted
    # lid relief stands ~1 cm proud of the white, and a lid sampled on the white alone slid behind it
    def surf(z_hi, z_lo):
        G = np.zeros((NI, NJ, 3))
        for i, x in enumerate(xs):
            for j, t in enumerate(np.linspace(0, 1, NJ)):
                z = z_hi[i] + t * (z_lo[i] - z_hi[i]); d, k = tree.query([x, z], 12)
                G[i, j] = (x, P[k, 1].min(), z)           # front-most of 12 (a mean mixes TRELLIS's back shell in)
        for _ in range(20):                                       # 3 x 3 box smoothing of the depth only, 20 passes (6 left column ripples)
            Y = np.pad(G[:, :, 1], 1, mode="edge")
            G[:, :, 1] = sum(Y[1 + di:1 + di + NI, 1 + dj:1 + dj + NJ] for di in (-1, 0, 1) for dj in (-1, 0, 1)) / 9
        G[:, :, 1] -= OFF
        return G.tolist()
    keys = {"open": surf(top + 0.0005, top - 0.0005), "half": surf(top + 0.0005, (top + bot) / 2), "closed": surf(top + 0.0005, bot - 0.001)}
    res[side] = {"keys": keys, "skin": [253, 163, 135], "eye_h_mm": float((top - bot).max() * 1000)}
    print("eye %s: %d eye verts, width %.1f mm, height up to %.1f mm, top edge z %.3f-%.3f" % (
        side, E.sum(), np.ptp(xs) * 1000, (top - bot).max() * 1000, top.min(), top.max()))
json.dump(res, open(sys.argv[3], "w"))
