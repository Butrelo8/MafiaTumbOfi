# joints.py: per joint of a parts blend, across the idle, the seam gap and the interpenetration (mm), plus how far each
# rigid part sits from the skinned mesh (a part on the wrong bone shows as a large distance), plus kiln's floating().
#   $B -b <parts.blend> --python joints.py -- <split.json> <out.json> [first-last:step]
# gap: the child's cut-loop vertices, posed, to the parent part's surface (0 at rest).
# pen: child vertices within 8 cm of the joint that end up inside the parent's capped volume, deepest (0 at rest).
# seam: two-sided and cover-aware (covers.py objects cover_* count as part of the part they hang on). Each child ring
# vertex is paired with the parent ring vertex it sat on at rest; a pair is closed when either one is inside or on the
# other side's part or covers; seam = the largest open distance over the pairs (a ball on the parent buries the child's
# ring, a peg on the child holds the parent's rim). Without covers it reads at or under gap. rigid_dev: largest
# |M^T M - I| of each part's world matrix over the clip (0: the parts move rigidly, so their mesh cannot stretch).
import bpy, sys, json, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]
info = json.load(open(a[0])); out = a[1]; rng = a[2] if len(a) > 2 else "1-120:3"
lo, rest = rng.split("-"); hi, st = rest.split(":"); frames = sorted(set(range(int(lo), int(hi) + 1, int(st))) | {22, 70, 110})
sc = bpy.context.scene; rig = bpy.data.objects["rig"]
parts = {o.name[5:]: o for o in bpy.data.objects if o.name.startswith("part_")}
def local(o):
    me = o.data; V = np.array([v.co for v in me.vertices])
    return V, BVHTree.FromPolygons([v.co for v in me.vertices], [p.vertices[:] for p in me.polygons])
L = {n: local(o) for n, o in parts.items()}
J = {}
for cn, c in info["cuts"].items():
    co, no = np.array(c["co"]), np.array(c["no"]); V, _ = L[c["child"]]
    s = (V - co) @ no; d = np.linalg.norm(V - co, axis=1)
    ring = np.where((np.abs(s) < 2e-6) & (d < 0.12))[0]
    near = np.where((np.abs(s) > 1e-5) & (d < 0.08))[0]
    if len(near) > 3000: near = near[np.linspace(0, len(near) - 1, 3000).astype(int)]
    Vp = L[c["parent"]][0]; sp = (Vp - co) @ no; pring = np.where((np.abs(sp) < 2e-6) & (np.linalg.norm(Vp - co, axis=1) < 0.12))[0]
    D2 = ((V[ring][:, None, :] - Vp[pring][None, :, :]) ** 2).sum(2)
    J[cn] = dict(child=c["child"], parent=c["parent"], ring=ring, near=near, gap=[], pen=[], seam=[],
                 pring=pring, c2p=D2.argmin(1), p2c=D2.argmin(0))
COV = {}
for o in bpy.data.objects:
    if o.name.startswith("cover_"): COV.setdefault(o["attached"], []).append(local(o)[1])
CT = {n: [L[n][1]] + COV.get(n, []) for n in parts}
rigid = {n: 0.0 for n in parts}
dist = {n: [] for n in parts}
body = bpy.data.objects["Body"]
DIRS = [Vector((0.577, 0.577, 0.577)), Vector((-0.3, 0.8, -0.52)).normalized(), Vector((0.71, -0.2, -0.67)).normalized()]
def inside(T, p):   # ray parity in 3 directions, majority (the parts are closed by their caps)
    votes = 0
    for d in DIRS:
        n, o = 0, p.copy()
        for _ in range(64):
            hit = T.ray_cast(o, d)
            if hit[0] is None: break
            n += 1; o = hit[0] + d * 1e-6
        votes += n % 2
    return votes >= 2
def measure(j, T, Vc, Tp):
    def to_p(idx): return (np.c_[Vc[idx], np.ones(len(idx))] @ T.T)[:, :3]
    g = pen = 0.0
    for p in to_p(j["ring"]):          # a cut-loop vertex is either out in the open (gap) or buried (interpenetration)
        p = Vector(p); dd = Tp.find_nearest(p)[3]
        if dd < 2e-5: continue
        if inside(Tp, p): pen = max(pen, dd)
        else: g = max(g, dd)
    for p in to_p(j["near"]):
        p = Vector(p); dd = Tp.find_nearest(p)[3]
        if dd > pen and inside(Tp, p): pen = dd
    return g * 1000, pen * 1000
def open_d(Ts, p):   # 0 if p is on or inside any of the closed meshes Ts, else the distance to the nearest
    p = Vector(p); d = min(T.find_nearest(p)[3] for T in Ts)
    return 0.0 if d < 2e-5 or any(inside(T, p) for T in Ts) else d
def seam(j, M):
    xf = lambda T, P: (np.c_[P, np.ones(len(P))] @ T.T)[:, :3]
    Tcp = np.linalg.inv(M[j["parent"]]) @ M[j["child"]]
    gc = np.array([open_d(CT[j["parent"]], p) for p in xf(Tcp, L[j["child"]][0][j["ring"]])])
    gp = np.array([open_d(CT[j["child"]], p) for p in xf(np.linalg.inv(Tcp), L[j["parent"]][0][j["pring"]])])
    return max(np.minimum(gc, gp[j["c2p"]]).max(), np.minimum(gp, gc[j["p2c"]]).max()) * 1000
rig.data.pose_position = "REST"; sc.frame_set(1)       # the metric's own check: rest must read 0 / 0
Mr = {n: np.array(o.matrix_world) for n, o in parts.items()}
for cn, j in J.items():
    Mc, Mp = np.array(parts[j["child"]].matrix_world), np.array(parts[j["parent"]].matrix_world)
    j["rest"] = measure(j, np.linalg.inv(Mp) @ Mc, L[j["child"]][0], L[j["parent"]][1]) + (seam(j, Mr),)
rig.data.pose_position = "POSE"
for f in frames:
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
    M = {n: np.array(o.matrix_world) for n, o in parts.items()}
    for n in parts: rigid[n] = max(rigid[n], float(np.abs(M[n][:3, :3].T @ M[n][:3, :3] - np.eye(3)).max()))
    for cn, j in J.items():
        g, pen = measure(j, np.linalg.inv(M[j["parent"]]) @ M[j["child"]], L[j["child"]][0], L[j["parent"]][1])
        j["gap"].append(g); j["pen"].append(pen); j["seam"].append(seam(j, M))
    if f in (22, 70, 110):
        ev = body.evaluated_get(dg); me = ev.to_mesh()
        tb = BVHTree.FromPolygons([body.matrix_world @ v.co for v in me.vertices], [p.vertices[:] for p in me.polygons]); ev.to_mesh_clear()
        for n, o in parts.items():
            V, _ = L[n]; idx = np.linspace(0, len(V) - 1, min(len(V), 600)).astype(int)
            P = (np.c_[V[idx], np.ones(len(idx))] @ M[n].T)[:, :3]
            dist[n].append(float(np.median([tb.find_nearest(Vector(p))[3] for p in P]) * 1000))
res = {"frames": [frames[0], frames[-1], len(frames)], "joints": {}, "part_to_skinned_median_mm": {n: round(max(v), 1) for n, v in dist.items()}}
for cn, j in J.items():
    i = int(np.argmax(j["gap"])); k = int(np.argmax(j["pen"]))
    res["joints"][cn] = {"child": j["child"], "parent": j["parent"], "ring_verts": int(len(j["ring"])),
                         "rest_gap_pen_mm": [round(x, 2) for x in j["rest"]],
                         "gap_max_mm": round(j["gap"][i], 1), "gap_frame": frames[i], "gap_f70_mm": round(j["gap"][frames.index(70)], 1),
                         "pen_f70_mm": round(j["pen"][frames.index(70)], 1),
                         "pen_max_mm": round(j["pen"][k], 1), "pen_frame": frames[k],
                         "seam_max_mm": round(max(j["seam"]), 1), "seam_frame": frames[int(np.argmax(j["seam"]))]}
    print("@@JOINT@@", cn, res["joints"][cn], flush=True)
res["rigid_dev_max"] = {n: float("%.2g" % v) for n, v in rigid.items()}; res["covers"] = sorted(o.name for o in bpy.data.objects if o.name.startswith("cover_"))
print("@@RIGID@@", max(rigid.values()), flush=True)
# kiln's attachment check (overlap first, then the gap of parts that overlap nothing) at f70
k = {}; exec(open(r"\\wsl.localhost\Ubuntu\home\black\projects\visual-lab\blender\scripts\kiln_parts.py").read(), k)
sc.frame_set(70); res["kiln_floating_f70"] = k["floating"](list(parts.values()))
print("@@KILN@@", res["kiln_floating_f70"], flush=True)
print("@@DIST@@", res["part_to_skinned_median_mm"], flush=True)
json.dump(res, open(out, "w"), indent=1)
