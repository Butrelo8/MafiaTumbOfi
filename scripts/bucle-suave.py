"""Eases and lengthens the band loop's moves 2 and 3 (owner 2026-11-16 16:25: "make 2 and 3 smooth like 1, ease out the shots";
16:46: "it's the duration of the shots ... the other 2 are really fast").

The authored loop points in src/lib/ruta.json (bucles[0].camara) define the approved curve: their `t` placed them on the first,
240-frame loop (U_FIN), through ruta.ts's monotone Hermite from the run's pose at `hasta` to its pose at `desde`. That curve is only C1: its acceleration
jumps at every knot. This script takes points on it (every authored pose, plus one about every 4 frames between them), and
chooses when the camera reaches each one, so that a clamped C2 cubic spline through them (no acceleration jump anywhere, the
run's own velocity and acceleration at both handovers) has the lowest peak of combined acceleration (position m/f^2 and camera-axis turn
deg/f^2), stays within TOL of the approved path, splits the time after move 1 evenly between moves 2 and 3 (the hood pose, the
split, at its middle) and keeps the slow push between the front heads at the share of move 3 it had (26 of 62 frames). It prints each move's bar
(buggyship 16:33: peak acceleration x T^2 / D no higher than move 1's) as an acceleration, to compare with the result.
`largo` (a multiple of 240, so vibra, the world and the cast loop) sets how long the moves last: 480 gives each about 8 s. It writes bucles[0].suave ([t, pos, mira, mm] rows that ruta.ts and blender/ruta.py
sample) and each authored point's `reloj` (the loop frame at which the eased loop reaches it).

  uv run -q --with numpy --with scipy python -I scripts/bucle-suave.py src/lib/ruta.json
"""
import json, math, sys
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree

RUTA_P = sys.argv[1]
R = json.load(open(RUTA_P, encoding="utf8"))
B = R["bucles"][0]
L1 = B["hasta"] - B["desde"]
U_FIN = 240  # the authored points' `t` are on the first loop, 240 frames long
HOOD = (5, L1 + (B["largo"] - L1) / 2)  # authored point index pinned at that loop frame
EMPUJE = (7, 8, 26 * (B["largo"] - HOOD[1]) / (U_FIN - 178))  # the slow push from point 7 to 8 keeps its share of move 3 (26 of 62 f)
cam = R["camara"]
val = lambda p: np.array([*p["pos"], *p["mira"], p["mm"]], float)
TOL, TOL_MIRA = 0.02, 0.05  # m off the approved path (camera, look target)
A_REF, W_REF = 0.01, 0.5  # m/f^2 and deg/f^2 that weigh the same in the cost


def mono(ps_t, ps_v, i, e0, e1):  # ruta.ts tangentes(): monotone, one-sided ends unless e0/e1
    n = len(ps_t)
    if i == 0:
        return e0
    if i == n - 1:
        return e1
    d0 = (ps_v[i] - ps_v[i - 1]) / (ps_t[i] - ps_t[i - 1]); d1 = (ps_v[i + 1] - ps_v[i]) / (ps_t[i + 1] - ps_t[i])
    h0, h1 = ps_t[i] - ps_t[i - 1], ps_t[i + 1] - ps_t[i]
    out = []
    for a, b in zip(d0, d1):
        if a * b <= 0:
            out.append(0.0)
            continue
        m = (a * h1 + b * h0) / (h0 + h1)
        out.append(math.copysign(min(abs(m), 3 * abs(a), 3 * abs(b)), m))
    return np.array(out)


def herm(T, Y, M, t):
    k = np.clip(np.searchsorted(T, t, side="right") - 1, 0, len(T) - 2)
    h = (T[k + 1] - T[k])[:, None]; s = ((t - T[k]) / (T[k + 1] - T[k]))[:, None]
    s2, s3 = s * s, s * s * s
    return (2*s3-3*s2+1)*Y[k] + (s3-2*s2+s)*h*M[k] + (-2*s3+3*s2)*Y[k+1] + (s3-s2)*h*M[k+1]


def c2(T, Y, e0, e1):  # clamped cubic spline: the tangent at each knot (Thomas algorithm, as ruta.ts tangentesC2)
    n = len(T); h = np.diff(T); d = np.diff(Y, axis=0) / h[:, None]
    a = np.zeros(n); b = np.ones(n); c = np.zeros(n); r = np.zeros_like(Y); r[0], r[-1] = e0, e1
    a[1:-1], b[1:-1], c[1:-1] = h[1:], 2 * (h[:-1] + h[1:]), h[:-1]
    r[1:-1] = 3 * (h[1:, None] * d[:-1] + h[:-1, None] * d[1:])
    for i in range(1, n):
        w = a[i] / b[i - 1]; b[i] -= w * c[i - 1]; r[i] -= w * r[i - 1]
    m = np.zeros_like(Y); m[-1] = r[-1] / b[-1]
    for i in range(n - 2, -1, -1):
        m[i] = (r[i] - c[i] * m[i + 1]) / b[i]
    return m


# the run's tangents at the loop's ends, and the approved curve
idx = {p["fr"]: i for i, p in enumerate(cam)}
run_t = np.array([p["fr"] for p in cam], float); run_v = np.array([val(p) for p in cam])
E0, E1 = mono(run_t, run_v, idx[B["hasta"]], None, None), mono(run_t, run_v, idx[B["desde"]], None, None)
U = np.array([L1] + [p["t"] for p in B["camara"]] + [U_FIN], float)
YA = np.array([run_v[idx[B["hasta"]]]] + [val(p) for p in B["camara"]] + [run_v[idx[B["desde"]]]])
MA = np.array([mono(U, YA, i, E0, E1) for i in range(len(U))])
UD = np.arange(L1, U_FIN + 1e-9, 0.25); APROB = herm(U, YA, MA, UD)

# the bar (buggyship, 16:33): each move's peak acceleration x T^2 / D no higher than move 1's, measured on the run's desde..hasta
# (interior frames, per-frame differences); BAR2 and BAR3 are that peak for move 2 and for move 3 at this loop's length
_sec = lambda i: (run_v[i + 1] - run_v[i]) / (run_t[i + 1] - run_t[i])
_MR = np.array([mono(run_t, run_v, i, _sec(0), _sec(len(run_t) - 2)) for i in range(len(run_t))])
_p1 = herm(run_t, run_v, _MR, np.arange(B["desde"], B["hasta"] + 1e-9, 1.0))[:, :3]
NORM1 = np.linalg.norm(np.diff(_p1, 2, axis=0), axis=1)[1:-1].max() * L1 ** 2 / np.linalg.norm(np.diff(_p1, axis=0), axis=1).sum()
_largo = lambda u0, u1: np.linalg.norm(np.diff(APROB[(UD >= u0) & (UD <= u1), :3], axis=0), axis=1).sum()
BAR2 = NORM1 * _largo(L1, 178) / (HOOD[1] - L1) ** 2
BAR3 = NORM1 * _largo(178, U_FIN) / (B["largo"] - HOOD[1]) ** 2

# knots on the approved curve: the authored ones plus about one every 4 frames of its own timing
UK, AUT = [], []
for i in range(len(U) - 1):
    AUT.append(len(UK)); k = max(1, round((U[i + 1] - U[i]) / (1 if i in (0, len(U) - 2) else 4)))
    UK += list(np.linspace(U[i], U[i + 1], k + 1)[:-1])
AUT.append(len(UK)); UK.append(U[-1]); UK = np.array(UK)
YK = herm(U, YA, MA, UK); YK[AUT] = YA  # exact at the authored poses
n = len(UK)
fijos = [(0, float(L1)), (AUT[HOOD[0]], HOOD[1]), (n - 1, float(B["largo"]))]


def tiempos(x):  # every knot's time: gaps from a softmax inside each fixed stretch
    T = np.zeros(n); j = 0
    for (i0, t0), (i1, t1) in zip(fijos[:-1], fijos[1:]):
        xi = x[j:j + i1 - i0]; g = np.exp(xi - xi.max()); g = (t1 - t0) * g / g.sum(); j += i1 - i0
        T[i0] = t0; T[i0 + 1:i1 + 1] = t0 + np.cumsum(g)
    return T


def acc0(T, Y, M, fin):  # second derivative of a Hermite at its first knot (fin False) or its last (fin True)
    if fin:
        h = T[-1] - T[-2]; return (6 * Y[-2] + 2 * h * M[-2] - 6 * Y[-1] + 4 * h * M[-1]) / h ** 2
    h = T[1] - T[0]; return (-6 * Y[0] - 4 * h * M[0] + 6 * Y[1] - 2 * h * M[1]) / h ** 2


# the run's acceleration where the loop leaves it (end of its hasta segment) and where it rejoins it (start of the desde segment)
_ih, _id = idx[B["hasta"]], idx[B["desde"]]
_tr = lambda i: np.array([mono(run_t, run_v, k, None, None) for k in (i, i + 1)])
AC0 = acc0(run_t[_ih - 1:_ih + 1], run_v[_ih - 1:_ih + 1], _tr(_ih - 1), True)
AC1 = acc0(run_t[_id:_id + 2], run_v[_id:_id + 2], _tr(_id), False)


def nudos(T):  # the knots, with the 2nd and 2nd-to-last moved so the spline's acceleration at both ends is the run's (C2 handovers)
    Y = YK.copy()
    def ends(Y):
        M = c2(T, Y, E0, E1); return acc0(T, Y, M, False), acc0(T, Y, M, True)
    a0, a1 = ends(Y); J = np.zeros((2, 2, Y.shape[1]))
    for k, i in enumerate((1, n - 2)):
        Yd = Y.copy(); Yd[i] += 1; b0, b1 = ends(Yd); J[0, k], J[1, k] = b0 - a0, b1 - a1
    for j in range(Y.shape[1]):
        x = np.linalg.solve(J[:, :, j], [AC0[j] - a0[j], AC1[j] - a1[j]]); Y[1, j] += x[0]; Y[n - 2, j] += x[1]
    return Y


def medir(T, paso=0.5):  # accelerations along the eased loop, with the run continued past both ends at its own acceleration
    ts = np.arange(L1 - 2, B["largo"] + 2 + 1e-9, paso); Y = nudos(T)
    v = herm(T, Y, c2(T, Y, E0, E1), np.clip(ts, L1, B["largo"]))
    dt0, dt1 = (ts[ts < L1] - L1)[:, None], (ts[ts > B["largo"]] - B["largo"])[:, None]
    v[ts < L1] = Y[0] + dt0 * E0 + dt0 ** 2 / 2 * AC0
    v[ts > B["largo"]] = Y[-1] + dt1 * E1 + dt1 ** 2 / 2 * AC1
    p = v[:, :3]; z = p - v[:, 3:6]; z /= np.linalg.norm(z, axis=1)[:, None]
    acc = np.linalg.norm(np.diff(p, 2, axis=0), axis=1) / paso ** 2
    cr = np.cross(z[:-1], z[1:]); sn = np.linalg.norm(cr, axis=1)
    w = (np.arcsin(np.clip(sn, 0, 1)) / np.maximum(sn, 1e-12))[:, None] * cr * (180 / math.pi / paso)
    return v[(ts >= L1) & (ts <= B["largo"])], acc, np.linalg.norm(np.diff(w, axis=0), axis=1) / paso


ARBOL = cKDTree(APROB[:, :3])


def desvio(v):  # each sample's distance to the approved curve (camera), and its look target's to the matching approved one
    d, j = ARBOL.query(v[:, :3])
    return d, np.linalg.norm(v[:, 3:6] - APROB[j, 3:6], axis=1)


def f(x):
    T = tiempos(x)
    if np.diff(T).min() < 0.1:  # knots about to merge: the spline blows up; keep the search away
        return 1e6 * (1 + 0.1 - np.diff(T).min())
    v, a, wa = medir(T); dp, dm = desvio(v)
    e = np.sqrt((a / A_REF) ** 2 + (wa / W_REF) ** 2)
    g = np.diff(T)
    return (np.mean(e ** 8) ** 0.125 + 50 * np.sum(np.maximum(0, 1.0 - g) ** 2)
            + 0.05 * (EMPUJE[2] - (T[AUT[EMPUJE[1]]] - T[AUT[EMPUJE[0]]])) ** 2
            + 2e4 * (np.sum(np.maximum(0, dp - TOL) ** 2) + np.sum(np.maximum(0, dm - TOL_MIRA) ** 2)))


x0 = np.concatenate([np.log(np.diff(UK[i0:i1 + 1])) for (i0, _), (i1, _) in zip(fijos[:-1], fijos[1:])])
r = minimize(f, x0, method="L-BFGS-B", options={"maxiter": 3000, "maxfun": 200000})
r = minimize(f, r.x, method="Powell", options={"maxiter": 20000, "maxfev": 400000, "xtol": 1e-4, "ftol": 1e-8})
T = tiempos(r.x)
v, a, wa = medir(T); dp, dm = desvio(v)
print("bucle-suave: move 1 a*T^2/D %.1f -> bars move 2 %.5f, move 3 %.5f m/f2" % (NORM1, BAR2, BAR3))
print("bucle-suave: %d knots · cost %.3f · peak acc %.4f m/f2, turn acc %.3f deg/f2 · off path %.3f m (look %.3f m) · push %.1f f"
      % (n, f(r.x), a.max(), wa.max(), dp.max(), dm.max(), T[AUT[EMPUJE[1]]] - T[AUT[EMPUJE[0]]]))
B["suave"] = [[float(t)] + [float(x) for x in y] for t, y in zip(T, nudos(T))]
for i, p in enumerate(B["camara"]):
    p["reloj"] = float(T[AUT[i + 1]])
open(RUTA_P, "w", encoding="utf8").write(json.dumps(R, ensure_ascii=False, indent=1))
