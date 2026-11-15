# hand_fit.py <hand.glb> <body.glb> <body.json> <out.json>: the spread-finger hand onto both wrists by landmarks
# (no ICP: a spread hand fitted onto a mitten slides). Hand landmarks, in the GLB's own frame (fingers up = +Z; TRELLIS gave a right hand: thumb +X, palm on the
# image side -Y): wrist-stub centre W (bottom 3 % of the height), middle fingertip M (top vertex),
# thumb tip Th (most lateral point of the lower hand). Body landmarks per side: the wrist ring (the ring before the first one whose max radius
# passes 1.4x the forearm's), the forearm axis a over the last 5 cm, and the body's mitten length along a.
# Placement: fingers along a, thumb forward (-Y), the back of the hand (+Y in the GLB) up, palm down, length = mitten length,
# stub centre WRIST_IN m into the forearm. The left hand is the right one mirrored in X. The stub is widened radially to
# the forearm ring's radius + 1 mm (blend to none at the palm), so the forearm end is hidden inside it.
# Writes per side: the 4x4 (applied after the mirror and the stub widening), the landmarks and the radii.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from fitlib import load_glb, apply

WRIST_IN = 0.010
hglb, bglb, bjson, out = sys.argv[1:5]
H, HF, HC = load_glb(hglb)
B = apply(np.array(json.load(open(bjson))["T"]), load_glb(bglb)[0])


def ring(P, c, u, half=0.002):
    S = P[np.abs((P - c) @ u) < half]; D = (S - c) - np.outer((S - c) @ u, u); r = np.linalg.norm(D, axis=1)
    S, r = S[r < 0.06], r[r < 0.06]
    return S.mean(0), r


def arm_path(sd):
    A = B[(sd * B[:, 0] > 0.14) & (B[:, 2] > 0.30) & (B[:, 2] < 0.60)]
    path = []
    for x in np.arange(0.16, 0.34, 0.004):
        S = A[np.abs(sd * A[:, 0] - x) < 0.002]
        if len(S) > 10: path.append((x, S.mean(0), np.ptp(S[:, 2])))
    return A, path


def body_side(sd):
    A, path = arm_path(sd)
    X = np.array([p[0] for p in path]); C = np.array([p[1] for p in path])
    rmax = np.zeros(len(path))
    for k in range(1, len(path) - 1):                                         # rings across the local path direction
        u = C[k + 1] - C[k - 1]; u /= np.linalg.norm(u); rmax[k] = ring(A, C[k], u)[1].max()
    ref = np.median(rmax[(X > 0.19) & (X < 0.24)])
    k = int(np.flatnonzero((X > 0.24) & (rmax > 1.4 * ref))[0])               # first ring where the hand widens
    e = C[np.argmin(np.abs(X - (X[k - 1] - 0.05)))]
    a = C[k - 1] - e; a /= np.linalg.norm(a)
    c, r = ring(A, C[k - 1], a)
    tip = ((A - c) @ a).max()
    return {"wrist": c, "axis": a, "r_forearm": float(np.median(r)), "mitten_len": float(tip), "hand_x": float(path[k][0])}


def frame(f, t):
    f = f / np.linalg.norm(f); t = t - f * (t @ f); t /= np.linalg.norm(t)
    return np.c_[f, t, np.cross(f, t)]


res = {}
for sd, name in ((-1, "right"), (1, "left")):
    P = H * np.array([-1.0 if sd > 0 else 1.0, 1, 1])                          # left = mirrored right
    h = np.ptp(P[:, 2]); bot = P[P[:, 2] < P[:, 2].min() + 0.03 * h]
    W = bot.mean(0); M = P[np.argmax(P[:, 2])]
    low = P[(P[:, 2] > P[:, 2].min() + 0.25 * h) & (P[:, 2] < P[:, 2].min() + 0.60 * h)]
    Th = low[np.argmax(np.abs(low[:, 0] - W[0]))]           # thumb tip: the most lateral point of the lower hand
    f_s = M - W; L_h = np.linalg.norm(f_s)
    Fs = frame(f_s, Th - W)
    # stub widening, in the hand's own frame: radial distance from the f axis, scaled near the wrist
    u = Fs[:, 0]; t = (P - W) @ u; radial = (P - W) - np.outer(t, u)
    bs = body_side(sd); s = bs["mitten_len"] / L_h
    r_stub = np.median(np.linalg.norm(radial[(t > 0.02 * L_h) & (t < 0.10 * L_h)], axis=1)) * s
    k_w = (bs["r_forearm"] + 0.001) / r_stub
    blend = np.clip(1 - (t / L_h - 0.12) / 0.10, 0, 1) if k_w > 1 else np.zeros_like(t)   # full to 12 %, none past 22 %
    P = W + np.outer(t, u) + radial * (1 + (k_w - 1) * blend)[:, None] if k_w > 1 else P
    Ft = frame(bs["axis"], np.array([0, -1.0, 0]))
    R = Ft @ Fs.T
    if np.linalg.det(R) < 0: raise SystemExit("hand frames disagree in handedness on " + name)
    T = np.eye(4); T[:3, :3] = s * R; T[:3, 3] = bs["wrist"] - bs["axis"] * WRIST_IN - s * R @ W
    res[name] = {"T": T.tolist(), "mirror_x": sd > 0, "widen": {"axis_W": W.tolist(), "u": u.tolist(), "k": float(k_w),
                 "L": float(L_h)}, "scale": float(s), "wrist": bs["wrist"].tolist(), "axis": bs["axis"].tolist(),
                 "r_forearm_mm": bs["r_forearm"] * 1000, "r_stub_mm": float(r_stub * 1000), "mitten_len_mm": bs["mitten_len"] * 1000,
                 "hand_starts_x": bs["hand_x"]}
    print(name, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in res[name].items() if k not in ("T", "widen")})
json.dump(res, open(out, "w"), indent=1)
