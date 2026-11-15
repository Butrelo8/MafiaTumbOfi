# armprof.py <glb> <fit.json> <side -1|1> [x0 x1]: the placed arm's centre path from x-slices (4 mm, z 0.30-0.60),
# then rings perpendicular to the local path direction: centre, mean/max radius. The wrist is the narrowest ring
# before the hand widens. Prints one line per ring, then "@@ wrist" with centre, axis and radius.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from fitlib import load_glb, apply
V, F, C = load_glb(sys.argv[1]); P = apply(np.array(json.load(open(sys.argv[2]))["T"]), V)
sd = float(sys.argv[3]); x0, x1 = (float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else (0.16, 0.30)
A = P[(sd * P[:, 0] > x0 - 0.02) & (P[:, 2] > 0.30) & (P[:, 2] < 0.60)]
xs = np.arange(x0, x1 + 1e-9, 0.004); path = []
for x in xs:
    S = A[np.abs(sd * A[:, 0] - x) < 0.002]
    if len(S) > 10: path.append(S.mean(0))
path = np.array(path); rows = []
for k in range(1, len(path) - 1):
    u = path[k + 1] - path[k - 1]; u /= np.linalg.norm(u); c = path[k]
    S = A[np.abs((A - c) @ u) < 0.002]; D = (S - c) - np.outer((S - c) @ u, u); r = np.linalg.norm(D, axis=1)
    S = S[r < 0.06]; r = r[r < 0.06]
    if len(S) < 10: continue
    m = S.mean(0); rows.append((sd * c[0], m, u, r.mean(), r.max()))
    print("x %.3f centre %s r_mean %.1f r_max %.1f mm" % (sd * c[0], m.round(4), r.mean() * 1000, r.max() * 1000))
R = np.array([r[3] for r in rows]); X = np.array([r[0] for r in rows])
k = int(np.argmin(np.where((X > 0.22), R, 9)))
print("@@ wrist", json.dumps({"x": X[k], "centre": rows[k][1].tolist(), "axis": rows[k][2].tolist(), "r_mean": R[k], "r_max": rows[k][4]}))
