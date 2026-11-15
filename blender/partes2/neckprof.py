# neckprof.py <glb> <fit.json> [z0 z1]: horizontal slices (3 mm) of the placed mesh near the neck: centre, mean radius
# and x/y widths of the central blob (|x| < 0.12), to put the head/body cut where the two necks have the same radius.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from fitlib import load_glb, apply
P = apply(np.array(json.load(open(sys.argv[2]))["T"]), load_glb(sys.argv[1])[0])
z0, z1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (0.50, 0.70)
for z in np.arange(z0, z1, 0.006):
    S = P[(np.abs(P[:, 2] - z) < 0.0015) & (np.abs(P[:, 0]) < 0.12)]
    if len(S) < 10: continue
    c = S.mean(0); r = np.linalg.norm((S - c)[:, :2], axis=1)
    print("z %.3f centre %s r_med %.1f wx %.1f wy %.1f n %d" % (z, c[:2].round(4), np.median(r) * 1000, np.ptp(S[:, 0]) * 1000, np.ptp(S[:, 1]) * 1000, len(S)))
