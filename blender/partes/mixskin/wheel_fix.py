# wheel_fix.py: the mothership's option C for driving: the wheel stays where props_fit.py put it (static, least nudge);
# the fists are moved onto its rim through body_fix.py's correction layer (the "fix" action, COMBINE), IK-like:
# per frame and side, the fist vertex closest to the rim (analytic torus) should move along the rim's normal there until
# its gap is 1.5 mm (out if inside, in if it floats). The part of that move across the arm is a shoulder rotation without
# twist (mixamorig:*Arm); the part along the shoulder-to-hand line is an elbow bend (mixamorig:*ForeArm, about the arm
# plane's normal), which a shoulder rotation cannot give. Increments Gaussian-smoothed (sigma 2, two-sided: the target is a
# band, not a floor) and repeated. The clip's own keys stay untouched. "moved" = the fist centroid's displacement.
#   $B -b <driving _fix blend> --python wheel_fix.py -- <fit.json (Windows)> <out.blend (Windows)> <report.json (Windows)> [iters 8]
import bpy, sys, os, json
sys.path.append(os.path.dirname(__file__))
import numpy as np
from mathutils import Vector, Quaternion
from penlib import dominant, body_world
a = sys.argv[sys.argv.index("--") + 1:]; W = json.load(open(a[0]))["wheel"]; out, rep = a[1], a[2]; iters = int(a[3]) if len(a) > 3 else 8
c, Rm, Rr, r = np.array(W["center"]), np.array(W["rot"]), W["R"], W["tube"]; TARGET = 1.5e-3
sc = bpy.context.scene; mx = bpy.data.objects["mx"]; body = bpy.data.objects["Body"]; ad = mx.animation_data; PB = mx.pose.bones
cb = ad.action.layers[0].strips[0].channelbags[0]; SIDES = ("Left", "Right"); BONES = ("Arm", "ForeArm")
frames = [int(k.co[0]) for k in next(f for f in cb.fcurves).keyframe_points]; n = len(frames)
FC, Q = {}, {}
for S in SIDES:
    for b in BONES:
        dp = f'pose.bones["mixamorig:{S}{b}"].rotation_quaternion'; PB[f"mixamorig:{S}{b}"].rotation_mode = "QUATERNION"
        fl = sorted([f for f in cb.fcurves if f.data_path == dp], key=lambda f: f.array_index)
        if not fl:
            fl = [cb.fcurves.new(dp, index=i, group_name=f"mixamorig:{S}{b}") for i in range(4)]
            for i, f in enumerate(fl):
                f.keyframe_points.add(n); f.keyframe_points.foreach_set("co", np.column_stack([frames, np.full(n, 1.0 if i == 0 else 0.0)]).ravel().tolist())
                f.keyframe_points.foreach_set("interpolation", [1] * n); f.update()
        FC[S, b] = fl; Q[S, b] = np.array([[f.keyframe_points[k].co[1] for f in fl] for k in range(n)])
def write(key):
    for i, f in enumerate(FC[key]):
        f.keyframe_points.foreach_set("co", np.column_stack([frames, Q[key][:, i]]).ravel().tolist()); f.update()
dom = dominant(body); IDX = {S: np.flatnonzero(np.char.startswith(dom, S + "Hand")) for S in SIDES}
def gaps(P):
    q = (P - c) @ Rm; rho = np.hypot(q[:, 0], q[:, 1]); s = np.sqrt((rho - Rr) ** 2 + q[:, 2] ** 2) - r
    k = int(s.argmin()); qk = q[k]; foot = np.array([qk[0] / rho[k] * Rr, qk[1] / rho[k] * Rr, 0.0])
    return float(s[k]), Rm @ ((qk - foot) / np.linalg.norm(qk - foot)), P[k]
def smooth(V):
    g = np.exp(-0.5 * (np.arange(-6, 7) / 2.0) ** 2); g /= g.sum()
    return np.column_stack([np.convolve(np.pad(V[:, i], 6, mode="edge"), g, mode="valid") for i in range(3)])
def wpos(bone, attr="head"): return np.array(mx.matrix_world @ getattr(PB[f"mixamorig:{bone}"], attr))
def rotm(bone):
    M = (mx.matrix_world @ PB[f"mixamorig:{bone}"].matrix).to_3x3(); M.normalize(); return M
log = []; G0 = None; C0 = {S: np.zeros((n, 3)) for S in SIDES}
for it in range(iters + 1):
    inc = {key: np.zeros((n, 3)) for key in Q}; G = {S: np.zeros(n) for S in SIDES}; moved = {S: np.zeros(n) for S in SIDES}
    for k, f in enumerate(frames):
        sc.frame_set(f); P = body_world(body, bpy.context.evaluated_depsgraph_get())
        for S in SIDES:
            H = P[IDX[S]]; s, nrm, p = gaps(H); G[S][k] = s; cen = H.mean(0)
            if G0 is None: C0[S][k] = cen
            moved[S][k] = np.linalg.norm(cen - C0[S][k])
            t = (TARGET - s) * nrm; sh, el = wpos(S + "Arm"), wpos(S + "ForeArm"); rv = p - sh; rn = rv / np.linalg.norm(rv)
            tr = t.dot(rn); tp = t - rn * tr
            inc[S, "Arm"][k] = np.array(rotm(S + "Arm").transposed() @ Vector(np.cross(rv, tp) / rv.dot(rv)))
            ax = np.cross(el - sh, p - el); ax /= np.linalg.norm(ax); rate = np.cross(ax, p - el).dot(rn)
            if abs(rate) > 0.02: inc[S, "ForeArm"][k] = np.array(rotm(S + "ForeArm").transposed() @ Vector(ax * (tr / rate)))
    if G0 is None: G0 = {S: G[S].copy() for S in SIDES}
    log.append({"iter": it, **{f"gap{S[0]}_mm": [round(G[S].min() * 1000, 2), round(G[S].max() * 1000, 2)] for S in SIDES},
                **{f"fist{S[0]}_moved_mm_max": round(float(moved[S].max()) * 1000, 1) for S in SIDES}})
    print("@@ITER@@", log[-1], flush=True)
    if it == iters or all(((G[S] >= 0.5e-3) & (G[S] <= 2.5e-3)).all() for S in SIDES): break
    for key in Q:
        V = smooth(inc[key])
        for k in range(n):
            L = float(np.linalg.norm(V[k]))
            if L > 1e-9: Q[key][k] = (Quaternion(Q[key][k]) @ Quaternion(Vector(V[k]) / L, L))[:]
        write(key)
json.dump(dict(iters=log, gap_before_mm={S: np.round(G0[S] * 1000, 2).tolist() for S in SIDES}, gap_after_mm={S: np.round(G[S] * 1000, 2).tolist() for S in SIDES},
               fist_moved_mm={S: np.round(moved[S] * 1000, 2).tolist() for S in SIDES}), open(rep, "w"))
sc.frame_set(frames[0]); bpy.ops.wm.save_as_mainfile(filepath=out)
print("@@WHEELFIX@@", json.dumps(log[-1]), flush=True)
