# guitar_track.py: the fretting-fist point for props_build.py's guitar Damped Track. No rigid guitar follows the fretting
# fist (props_fit's neck gap spans ~20 mm), so the neck aims at an empty on mixamorig:LeftHand. This picks the reference
# frame (the fist's neck gap closest to 1.5 mm in the rigid fit) and the fist's position along the neck there; adds
# "track": {"frame", "x"} to the params json.
#   uv run -q --with numpy --with scipy python -I guitar_track.py <dump.npz> <fit_guitar.json>
import sys, json, numpy as np
npz, pj = sys.argv[1:3]; D = np.load(npz); P = json.load(open(pj)); g = P["guitar"]; G = g["dims"]; t = g["thick"]
M = D["M_" + g["bone"]]; Mi = np.linalg.inv(M); o = np.array(g["origin"]); R = np.array(g["rot"])
q = ((np.einsum("fij,fkj->fki", Mi[:, :3, :3], D["LeftHand"]) + Mi[:, None, :3, 3]) - o) @ R
def box(q, lo, hi):
    c = (lo + hi) / 2; h = (hi - lo) / 2; d = np.abs(q - c) - h
    return np.linalg.norm(np.maximum(d, 0), axis=-1) + np.minimum(d.max(-1), 0)
neck = box(q, np.array([G["n0"] - 0.03, -G["nw"] / 2, G["nz"] - G["nd"] / 2]), np.array([G["n1"], G["nw"] / 2, G["nz"] + G["nd"] / 2])).min(1)
k = int(np.argmin(np.abs(neck - 1.5e-3))); x = float(q[k].mean(0)[0])
P["guitar"]["track"] = dict(frame=int(D["frames"][k]), x=x, gap_mm_at_ref=round(float(neck[k]) * 1000, 2))
P["guitar"]["rigid_neck_gap_mm"] = np.round(neck * 1000, 2).tolist()
json.dump(P, open(pj, "w"), indent=1); print(P["guitar"]["track"], "rigid neck gap", neck.min() * 1000, neck.max() * 1000)
