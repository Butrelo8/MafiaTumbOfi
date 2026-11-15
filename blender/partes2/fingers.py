# fingers.py <hand.glb> [length_m]: how separate the fingers are. Horizontal slices (fingers up = +Z) at 55-95 % of the
# hand's height; along x, vertices within 0.5 % of the height of the slice split into runs wherever x jumps by more
# than 1.5 % of the height. Prints the run count (fingers crossed) and the gaps between runs, scaled to length_m
# (the placed hand's wrist-to-tip length; default 0.155 m, Diego's mitten).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from fitlib import load_glb
V = load_glb(sys.argv[1])[0]; L = float(sys.argv[2]) if len(sys.argv) > 2 else 0.155
z0, h = V[:, 2].min(), np.ptp(V[:, 2]); s = L / h
for f in (0.55, 0.65, 0.75, 0.85, 0.95):
    S = np.sort(V[np.abs(V[:, 2] - (z0 + f * h)) < 0.005 * h, 0])
    d = np.diff(S); cut = np.flatnonzero(d > 0.015 * h)
    gaps = d[cut] * s * 1000
    print("height %d%%: %d runs, gaps mm %s" % (f * 100, len(cut) + 1, np.round(gaps, 1).tolist()))
