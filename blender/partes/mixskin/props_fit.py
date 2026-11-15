# props_fit.py: fit the props to a fixed clip (dump.py's .npz), not the clip to the props. Analytic signed distances
# (torus, box, flat two-lobe guitar body, axisymmetric bottle) against the fist and body vertices of every frame;
# Powell on penalties: grips want the closest fist vertex 0.5-2.5 mm off the prop's surface (never inside) and the prop as
# deep in the fist's curl as that allows; everything else wants >= 0.5 mm. The wheel is the exception: no rigid wheel
# follows these fists (+-7 mm), so it is fitted for the least nudge and wheel_fix.py moves the fists onto it. Writes the params for props_build.py.
#   uv run -q --with numpy --with scipy python -I props_fit.py <dump.npz> <kind sit|drive|guitar> <out.json> [variant k=v,...]
import sys, json
import numpy as np
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation as Rot
npz, kind, out = sys.argv[1:4]
VAR = dict(x.split("=") for x in sys.argv[4].split(",")) if len(sys.argv) > 4 and sys.argv[4] else {}
D = np.load(npz); fr = D["frames"]; n = len(fr); MM = 1000.0
LO, HI = 0.5e-3, 2.5e-3
def band(s):  # grip penalty, metres -> mm^2
    return (np.maximum(0, LO - s) * MM * 10) ** 2 + (np.maximum(0, s - HI) * MM) ** 2
def clear(s):
    return (np.maximum(0, LO - s) * MM * 10) ** 2
def frame_of(M, P):  # world points (n, k, 3) into each frame's bone space
    Mi = np.linalg.inv(M); return np.einsum("fij,fkj->fki", Mi[:, :3, :3], P) + Mi[:, None, :3, 3]
res = {"kind": kind, "variant": VAR, "frames": [int(fr[0]), int(fr[-1])]}

# ------------------------------------------------------------------------------------------------ seat
def fit_seat():
    hz = D["M_Hips"][:, 2, 3]; seated = np.flatnonzero(hz < hz.min() + 0.01)
    dom = D["trunk_dom"]; T = D["trunk"]; ms = int(seated[len(seated) // 2])
    Mh = D["M_Hips"][ms]
    # facing: from the hips to the mean of both feet, seated median frame
    feet = T[ms][np.isin(dom, ["LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase"])].mean(0); hips = Mh[:3, 3]
    fwd = feet[:2] - hips[:2]; fwd /= np.linalg.norm(fwd); acr = np.array([fwd[1], -fwd[0]])
    seatv = np.isin(dom, ["Hips", "LeftUpLeg", "RightUpLeg"])
    def uv(P): return np.stack([(P[..., :2] - hips[:2]) @ acr, (P[..., :2] - hips[:2]) @ fwd], -1)
    Pm = T[ms][seatv]; low = Pm[:, 2] < Pm[:, 2].min() + 0.02; U = uv(Pm[low])
    u0, u1 = U[:, 0].min() - 0.015, U[:, 0].max() + 0.015; v0 = U[:, 1].min() - float(VAR.get("back", 0.02)); v1 = U[:, 1].max()
    # the front edge stops 8 mm short of any calf / foot vertex below the seat's height (any seated frame)
    legs = np.isin(dom, ["LeftLeg", "RightLeg", "LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase"])
    for it in range(3):  # top from the seat-bearing vertices (buttocks, thigh undersides) over the footprint, every seated frame
        Ts = T[seated][:, seatv]; Ua = uv(Ts); inb = (Ua[..., 0] > u0) & (Ua[..., 0] < u1) & (Ua[..., 1] > v0) & (Ua[..., 1] < v1)
        z = np.where(inb, Ts[..., 2], np.inf); top = float(z.min()) - 0.8e-3
        Lg = T[:, legs]; UL = uv(Lg); under = (Lg[..., 2] < top) & (UL[..., 0] > u0) & (UL[..., 0] < u1) & (UL[..., 1] > v0)
        if under.any(): v1 = min(v1, float(UL[..., 1][under].min()) - 0.008)
    # every frame, every trunk vertex: inside the box?
    Ua = uv(T); inside = (Ua[..., 0] > u0) & (Ua[..., 0] < u1) & (Ua[..., 1] > v0) & (Ua[..., 1] < v1) & (T[..., 2] < top)
    depth = np.where(inside, np.minimum.reduce([top - T[..., 2], Ua[..., 0] - u0, u1 - Ua[..., 0], Ua[..., 1] - v0, v1 - Ua[..., 1]]), 0)
    gap = np.where((Ua[..., 0] > u0) & (Ua[..., 0] < u1) & (Ua[..., 1] > v0) & (Ua[..., 1] < v1), T[..., 2] - top, np.inf).min(1)
    c = hips[:2] + acr * (u0 + u1) / 2 + fwd * (v0 + v1) / 2
    res["seat"] = dict(center=[float(c[0]), float(c[1])], size=[float(u1 - u0), float(v1 - v0)], top=top,
                       yaw=float(np.arctan2(fwd[1], fwd[0]) - np.pi / 2), seated=[int(fr[seated[0]]), int(fr[seated[-1]])],
                       fit_max_depth_mm=round(float(depth.max()) * MM, 2),
                       fit_gap_mm_seated=[round(float(gap[seated].min()) * MM, 2), round(float(gap[seated].max()) * MM, 2)])

# ------------------------------------------------------------------------------------------------ wheel
def torus_sdf(P, c, R_, r, R):
    q = (P - c) @ R  # local, axis = z
    return np.sqrt((np.hypot(q[..., 0], q[..., 1]) - R_) ** 2 + q[..., 2] ** 2) - r
def fit_wheel():
    r = float(VAR.get("tube", 11)) / MM; tilt0 = np.radians(float(VAR.get("tilt", 25)))
    HL, HR = D["LeftHand"], D["RightHand"]; gl, gr = HL.mean(1), HR.mean(1)
    c0 = (gl + gr).mean(0) / 2; acr = (gl - gr).mean(0); acr /= np.linalg.norm(acr)
    chest = D["M_Spine2"][:, :3, 3].mean(0); back = chest - c0; back[2] = 0; back /= np.linalg.norm(back)
    ax0 = back * np.cos(tilt0) + np.array([0, 0, 1.0]) * np.sin(tilt0); ax0 -= acr * ax0.dot(acr); ax0 /= np.linalg.norm(ax0)
    R0 = np.column_stack([acr, np.cross(ax0, acr), ax0]); rv0 = Rot.from_matrix(R0).as_rotvec()
    Rr0 = np.linalg.norm(gl - gr, axis=1).mean() / 2 - 0.045  # rim inside the circle through both fists, at their palms
    keep = lambda H: H[:, np.abs(torus_sdf(H, c0, Rr0, r, R0)).min(0) < 0.035]
    HLa, HRa = keep(HL), keep(HR); HL, HR = HLa[::2], HRa[::2]; gla, gra = gl, gr; gl, gr = gl[::2], gr[::2]
    Tb = D["trunk"]; qt = (Tb - c0) @ R0; Tb = Tb[:, (np.hypot(qt[..., 0], qt[..., 1]) < Rr0 + 0.08).any(0) & (np.abs(qt[..., 2]) < 0.10).any(0)][::2]
    def body_sdf(c, Rr, R):  # trunk vs rim and vs the disc the hub and spokes fill
        q = (Tb - c) @ R; rho = np.hypot(q[..., 0], q[..., 1])
        return np.minimum(np.sqrt((rho - Rr) ** 2 + q[..., 2] ** 2) - r, np.maximum(rho - Rr, np.abs(q[..., 2]) - 0.012))
    def unpack(x): return c0 + x[:3], Rr0 + x[3], Rot.from_rotvec(rv0 + x[4:7]).as_matrix()
    def circ_dist(G, c, Rr, R):
        q = (G - c) @ R; return np.sqrt((np.hypot(q[:, 0], q[:, 1]) - Rr) ** 2 + q[:, 2] ** 2)
    def cost(x, report=False):
        c, Rr, R = unpack(x); sl = torus_sdf(HL, c, Rr, r, R).min(1); sr = torus_sdf(HR, c, Rr, r, R).min(1)
        # a mitten cannot wrap the rim: the rim meets each palm from inside the circle, both fists alike and on its plane
        ql, qr = (gl - c) @ R, (gr - c) @ R; radl = np.hypot(ql[:, 0], ql[:, 1]) - Rr; radr = np.hypot(qr[:, 0], qr[:, 1]) - Rr
        deep = (ql[:, 2] ** 2).mean() + (qr[:, 2] ** 2).mean() + (radl.mean() - radr.mean()) ** 2
        # keep the tilt near the asked one (the rim plane is otherwise free to swing around the hands)
        ax = R[:, 2]; tilt = np.arcsin(np.clip(ax[2], -1, 1))
        # static wheel, the fists get nudged onto it by wheel_fix.py (mothership's option C): least total nudge to a 1.5 mm gap
        sb = body_sdf(c, Rr, R).min(1)
        J = ((((sl - 1.5e-3) * MM) ** 2).sum() + (((sr - 1.5e-3) * MM) ** 2).sum() + deep * MM * MM * 0.05 + (np.degrees(tilt - tilt0)) ** 2
             + clear(sb - 1.5e-3).sum())
        if report: return dict(gapL_mm=[round(sl.min() * MM, 2), round(sl.max() * MM, 2)], gapR_mm=[round(sr.min() * MM, 2), round(sr.max() * MM, 2)],
                               tilt_deg=round(float(np.degrees(tilt)), 1), body_mm=round(float(sb.min()) * MM, 2), fist_radial_mm=[round(radl.mean() * MM, 1), round(radr.mean() * MM, 1)],
                               fist_axial_mm=[round(ql[:, 2].mean() * MM, 1), round(qr[:, 2].mean() * MM, 1)])
        return J
    x = np.zeros(7)
    for _ in range(2): x = minimize(cost, x, method="Powell", options=dict(maxiter=20000, xtol=1e-6, ftol=1e-9)).x
    HL, HR, gl, gr = HLa, HRa, gla, gra
    c, Rr, R = unpack(x)
    # steering: angle of the left-to-right fist vector in the wheel plane, relative to the first frame
    v = (gl - gr) @ R; ang = np.unwrap(np.arctan2(v[:, 1], v[:, 0])); ang -= ang[0]
    res["wheel"] = dict(center=c.tolist(), R=float(Rr), tube=r, rot=R.tolist(), spin=ang.tolist(), fit=cost(x, True),
                        gapL_mm=np.round(torus_sdf(HL, c, Rr, r, R).min(1) * MM, 2).tolist(), gapR_mm=np.round(torus_sdf(HR, c, Rr, r, R).min(1) * MM, 2).tolist())

# ------------------------------------------------------------------------------------------------ guitar
G = dict(r1=0.13, r2=0.10, x2=0.15, n0=0.21, n1=0.55, nw=0.045, nd=0.025, nz=0.02, h0=0.55, h1=0.62)
def cyl_sdf(q, cx, rad, hz):
    d0 = np.hypot(q[..., 0] - cx, q[..., 1]) - rad; d1 = np.abs(q[..., 2]) - hz
    return np.hypot(np.maximum(d0, 0), np.maximum(d1, 0)) + np.minimum(np.maximum(d0, d1), 0)
def box_sdf(q, lo, hi):
    c = (lo + hi) / 2; h = (hi - lo) / 2; d = np.abs(q - c) - h
    return np.linalg.norm(np.maximum(d, 0), axis=-1) + np.minimum(d.max(-1), 0)
def guitar_parts(q, t):
    body = np.minimum(cyl_sdf(q, 0, G["r1"], t / 2), cyl_sdf(q, G["x2"], G["r2"], t / 2))
    neck = box_sdf(q, np.array([G["n0"] - 0.03, -G["nw"] / 2, G["nz"] - G["nd"] / 2]), np.array([G["n1"], G["nw"] / 2, G["nz"] + G["nd"] / 2]))
    head = box_sdf(q, np.array([G["h0"], -0.03, G["nz"] - 0.01]), np.array([G["h1"], 0.03, G["nz"] + 0.01]))
    return body, np.minimum(neck, head)
def fit_guitar():
    t = float(VAR.get("thick", 60)) / MM
    best = None
    for b in ("Spine", "Spine1", "Spine2"):
        L = frame_of(D["M_" + b], D["LeftHand"].mean(1)[:, None])[:, 0]; L0 = L - L.mean(0)
        _, s, vt = np.linalg.svd(L0, full_matrices=False); perp = np.sqrt((s[1:] ** 2).sum() / n)
        if best is None or perp < best[1]: best = (b, perp, vt[0])
    bone = VAR.get("bone", best[0]); M = D["M_" + bone]
    loc = lambda k: frame_of(M, D[k])
    HL, HR = loc("LeftHand"), loc("RightHand"); gl, gr = HL.mean(1), HR.mean(1)
    T = loc("trunk"); A = np.concatenate([loc(k) for k in ("LeftForeArm", "RightForeArm", "LeftArm", "RightArm")], 1)
    # initial pose: neck from the strumming fist towards the fretting fist, face away from the belly
    xg = (gl - gr).mean(0); xg /= np.linalg.norm(xg)
    belly = T.mean(0).mean(0); out_ = gr.mean(0) - belly; out_ -= xg * out_.dot(xg); out_ /= np.linalg.norm(out_)
    R0 = np.column_stack([xg, np.cross(out_, xg), out_]); rv0 = Rot.from_matrix(R0).as_rotvec()
    o0 = gr.mean(0) - xg * 0.06 - out_ * (t / 2 + 0.025)
    near = lambda P, m: P[:, np.linalg.norm(P - gr.mean(0), axis=-1).min(0) < m]
    T, A = near(T, 0.40), near(A, 0.40)
    def close(P, m=0.10):  # only vertices within m of the starting guitar on some frame (the full sets slowed Powell to 25+ min)
        q = (P - o0) @ R0; return P[:, np.minimum(*guitar_parts(q, t)).min(0) < m]
    T, A = close(T), close(A)
    full = (HL, HR, T, A, gl); HL, HR, T, A, gl = HL[::3, ::2], HR[::3, ::2], T[::3, ::2], A[::3, ::2], gl[::3]  # fit on a subset
    def unpack(x): return o0 + x[:3], Rot.from_rotvec(rv0 + x[3:6]).as_matrix()
    def cost(x, report=False):
        o, R = unpack(x); q = lambda P: (P - o) @ R
        bL, nL = guitar_parts(q(HL), t); bR, nR = guitar_parts(q(HR), t)
        sn = nL.min(1); sr = np.minimum(bR, nR).min(1); sl_body = bL.min(1)
        bt, nt = guitar_parts(q(T), t); st = np.minimum(bt, nt).min(1); ba, na = guitar_parts(q(A), t); sa = np.minimum(ba, na).min(1)
        ql = q(gl); dn = np.hypot(ql[:, 1], ql[:, 2] - G["nz"])  # fretting fist centre to the neck's axis
        J = (band(sn).sum() + clear(sr).sum() + ((np.maximum(0, sr.min() - HI)) * MM) ** 2 * 20 + clear(sl_body).sum()
             + clear(st).sum() + clear(sa).sum() + (dn ** 2).mean() * MM * MM * 0.2
             + ((np.maximum(0, ql[:, 0] - (G["n1"] - 0.04)) * MM) ** 2).sum() + ((np.maximum(0, G["n0"] + 0.03 - ql[:, 0]) * MM) ** 2).sum())
        if report: return dict(neck_gap_mm=[round(sn.min() * MM, 2), round(sn.max() * MM, 2)], strum_gap_mm=[round(sr.min() * MM, 2), round(sr.max() * MM, 2)],
                               body_mm=round(st.min() * MM, 2), arms_mm=round(sa.min() * MM, 2), neck_x=[round(ql[:, 0].min(), 3), round(ql[:, 0].max(), 3)])
        return J
    x = np.zeros(6)
    for _ in range(2): x = minimize(cost, x, method="Powell", options=dict(maxiter=30000, xtol=1e-5, ftol=1e-6)).x
    HL, HR, T, A, gl = full; o, R = unpack(x)
    res["guitar"] = dict(bone=bone, pca_perp_mm={"chosen": round(best[1] * MM, 1)}, thick=t, dims=G, origin=o.tolist(), rot=R.tolist(), fit=cost(x, True))

# ------------------------------------------------------------------------------------------------ bottle
B = dict(rb=0.024, lb=0.10, ls=0.035, rn=0.011, ln=0.045)
def bottle_sdf(q, L):  # q in bottle space: axis +z from the base (z 0) to the lip (z L)
    s = q[..., 2]; rho = np.hypot(q[..., 0], q[..., 1]); lb = L - B["ls"] - B["ln"]
    r = np.where(s < lb, B["rb"], np.where(s < lb + B["ls"], B["rb"] + (B["rn"] - B["rb"]) * (s - lb) / B["ls"], B["rn"]))
    return np.maximum(rho - r, np.maximum(-s, s - L))
def fit_bottle():
    sip = int(VAR["sip"]) if "sip" in VAR else None
    M = D["M_RightHand"]; loc = lambda P: frame_of(M, P)
    H = loc(D["RightHand"]); gc = H.mean(1).mean(0)
    mouth = loc(D["mouth"][:, None])[:, 0]
    if sip is None: sip = int(np.argmin(np.linalg.norm(mouth - gc, axis=1)))
    else: sip = int(np.flatnonzero(fr == sip)[0])
    T = loc(D["trunk"]); A = np.concatenate([loc(D[k]) for k in ("LeftHand", "LeftForeArm", "RightForeArm", "LeftArm", "RightArm")], 1)
    T = T[:, np.linalg.norm(T - gc, axis=-1).min(0) < 0.35]; A = A[:, np.linalg.norm(A - gc, axis=-1).min(0) < 0.35]
    u0 = mouth[sip] - gc; L0 = float(VAR.get("len", 0.19))
    u0 /= np.linalg.norm(u0); base0 = mouth[sip] - u0 * L0
    def unpack(x):
        u = Rot.from_rotvec(x[3:6]).apply(u0); return base0 + x[:3], u
    def frame(base, u):
        a = np.cross(u, [1, 0, 0]); a = a if np.linalg.norm(a) > 0.1 else np.cross(u, [0, 1, 0]); a /= np.linalg.norm(a)
        return np.column_stack([a, np.cross(u, a), u])
    R0 = frame(base0, u0); keep = lambda P: P[:, bottle_sdf((P - base0) @ R0, L0).min(0) < 0.10]
    T, A = keep(T), keep(A)  # only vertices within 10 cm of the starting bottle on some frame
    full = (H, T, A); H, T, A = H[::5, ::2], T[:, ::2], A[:, ::2]
    def cost(x, report=False):
        base, u = unpack(x); R = frame(base, u); q = lambda P: (P - base) @ R
        sh = bottle_sdf(q(H), L0).min(1); st = bottle_sdf(q(T), L0).min(1); sa = bottle_sdf(q(A), L0).min(1)
        tip = base + u * L0; dm = np.linalg.norm(tip - mouth[sip])
        ax = np.linalg.norm(np.cross(gc - base, u))  # grip centre to the bottle's axis
        J = (band(sh).sum() + clear(st).sum() + clear(sa).sum() + (np.maximum(0, dm - HI) * MM) ** 2 * 10 + ax ** 2 * MM * MM * 0.2)
        if report: return dict(grip_gap_mm=[round(sh.min() * MM, 2), round(sh.max() * MM, 2)], body_mm=round(st.min() * MM, 2),
                               body_mm_at_sip=round(float(st[sip]) * MM, 2), arms_mm=round(sa.min() * MM, 2), tip_mouth_mm=round(dm * MM, 2),
                               axis_to_grip_mm=round(ax * MM, 1))
        return J
    x = np.zeros(6)
    for _ in range(2): x = minimize(cost, x, method="Powell", options=dict(maxiter=30000, xtol=1e-5, ftol=1e-6)).x
    H, T, A = full; base, u = unpack(x)
    res["bottle"] = dict(bone="RightHand", sip=int(fr[sip]), length=L0, dims=B, base=base.tolist(), rot=frame(base, u).tolist(), fit=cost(x, True))

if kind in ("sit", "drive"): fit_seat()
if kind == "drive": fit_wheel()
if kind == "guitar": fit_guitar()
if kind == "sit" and VAR.get("bottle", "1") == "1": fit_bottle()
json.dump(res, open(out, "w"), indent=1, default=float)
print(json.dumps({k: (v.get("fit") if isinstance(v, dict) and "fit" in v else v) for k, v in res.items() if k != "frames"}, default=str)[:3000])
