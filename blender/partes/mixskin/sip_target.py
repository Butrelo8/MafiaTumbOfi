# sip_target.py: the smallest move of the drinking fist, constant in Head space over the sip hold, after which a straight
# fist-to-lips segment clears the head by `clear` (the bottle neck's radius plus margin) and the fist itself stays `gap`
# off the head. Searched on dump.py's .npz on a 1 cm grid; checked on every hold frame. For sip_fix.py.
#   uv run -q --with numpy --with scipy python -I sip_target.py <dump.npz> <side Right|Left> <hold f0-f1> <out.json> [clear mm 16] [gap mm 10]
import sys, json, numpy as np
from scipy.spatial import cKDTree
npz, S, hold, out = sys.argv[1:5]; CLR = float(sys.argv[5]) / 1000 if len(sys.argv) > 5 else 0.016
GAP = float(sys.argv[6]) / 1000 if len(sys.argv) > 6 else 0.010
D = np.load(npz); fr = D["frames"]; h0, h1 = map(int, hold.split("-")); K = np.flatnonzero((fr >= h0) & (fr <= h1))[::6]
head = D["trunk_dom"] == "Head"; Mh = D["M_Head"]; ts = np.linspace(0, 1, 40)
def ok(k, dw):  # world move dw at hold frame k: (best segment clearance, fist-to-head distance)
    H = D[S + "Hand"][k][::6] + dw; m = D["mouth"][k]; tr = cKDTree(D["trunk"][k][head])
    v = m - H; L = np.linalg.norm(v, axis=1); P = H[:, None] + v[:, None] * ts[None, :, None]
    keep = (L[:, None] * (1 - ts[None])) > 0.015; d = np.where(keep, tr.query(P.reshape(-1, 3))[0].reshape(P.shape[:2]), np.inf).min(1)
    return float(d.max()), float(tr.query(H)[0].min())
g = np.arange(-0.16, 0.161, 0.01); cand = np.array([(x, y, z) for x in g for y in g for z in g]); cand = cand[np.argsort(np.linalg.norm(cand, axis=1))]
km = K[len(K) // 2]; R = Mh[km][:3, :3]
for dl in cand:  # dl in Head space
    if all(ok(k, Mh[k][:3, :3] @ dl)[0] >= CLR and ok(k, Mh[k][:3, :3] @ dl)[1] >= GAP for k in K): break
else: sys.exit("no move within 16 cm clears")
rep = {int(fr[k]): [round(x * 1000, 1) for x in ok(k, Mh[k][:3, :3] @ dl)] for k in K}
json.dump(dict(side=S, hold=[h0, h1], delta_head=dl.tolist(), move_mm=round(float(np.linalg.norm(dl)) * 1000, 1), clear_mm=CLR * 1000,
               per_frame_clear_gap_mm=rep), open(out, "w"), indent=1)
print("@@SIPTARGET@@", np.linalg.norm(dl) * 1000, "mm head-space", dl.round(3), "world at mid", (R @ dl).round(3), rep)
