# pen.py: where the hands (and forearms) go through the body or a stand-in prop, per frame, on a Mixamo-skinned blend
# (mesh "Body" with mixamorig:* groups; props prop_*). A vertex is inside a target when its nearest point on the target's
# surface has the vertex on the back side of that face (normal test) within 6 cm AND 6 axis rays agree it is enclosed
# (odd hit count on >= 4 of 6; TRELLIS's inner shells fooled the normal test alone: 32 false hits at 60 mm on dance f115,
# pen_diag.py); depth = the distance to the nearest surface.
# Body target = faces whose vertices are all dominated by torso, head or leg bones (arms excluded). Prints @@PEN@@ json.
#   $B -b <blend> --python pen.py -- <out.json (Windows)> [step]
import bpy, sys, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]; step = int(a[1]) if len(a) > 1 else 2
sc = bpy.context.scene; body = bpy.data.objects["Body"]; me = body.data; nv = len(me.vertices)
names = {g.index: g.name for g in body.vertex_groups}
dom = []
for v in me.vertices:
    gs = [(g.weight, names[g.group]) for g in v.groups if names[g.group].startswith("mixamorig")]
    dom.append(max(gs)[1].split(":")[1] if gs else "")
dom = np.array(dom)
TRUNK = {"Hips", "Spine", "Spine1", "Spine2", "Neck", "Head", "LeftUpLeg", "RightUpLeg", "LeftLeg", "RightLeg", "LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase"}
istrunk = np.isin(dom, list(TRUNK))
polys = [list(p.vertices) for p in me.polygons]
tpolys = [p for p in polys if all(istrunk[i] for i in p)]
SETS = {}
for S in ("Left", "Right"):
    SETS[S + "Hand"] = np.flatnonzero(np.char.startswith(dom, S + "Hand"))
    SETS[S + "ForeArm"] = np.flatnonzero(dom == S + "ForeArm")
props = [o for o in sc.objects if o.type == "MESH" and o.name.startswith("prop_")]
arm = next(o for o in sc.objects if o.type == "ARMATURE" and o.name == "mx")
act = arm.animation_data.action if arm.animation_data and arm.animation_data.action else None
f0, f1 = (map(int, act.frame_range) if act else (sc.frame_start, sc.frame_end))
DIRS = [Vector(d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]
def enclosed(tree, p):
    odd = 0
    for d in DIRS:
        c, q = 0, p + d * 1e-5
        while c < 50:
            hit = tree.ray_cast(q, d, 2.0)
            if hit[0] is None: break
            c += 1; q = hit[0] + d * 1e-5
        odd += c % 2
    return odd >= 4
def inside(tree, P):
    d = np.zeros(len(P))
    for k, p in enumerate(P):
        p = Vector(p); loc, n, i, dist = tree.find_nearest(p, 0.06)
        if loc is not None and (p - loc).dot(n) < 0 and enclosed(tree, p): d[k] = dist
    return d
res = {}
for f in range(f0, f1 + 1, step):
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); ev = body.evaluated_get(dg); m = ev.to_mesh()
    P = np.empty(nv * 3, np.float32); m.vertices.foreach_get("co", P); ev.to_mesh_clear()
    P = P.reshape(-1, 3) @ np.array(body.matrix_world.to_3x3()).T + np.array(body.matrix_world.translation)
    tree = BVHTree.FromPolygons(P.tolist(), tpolys, all_triangles=False)
    tg = {"body": tree}
    for o in props:
        oe = o.evaluated_get(dg); mm = oe.to_mesh(); W = o.matrix_world
        tg[o.name] = BVHTree.FromPolygons([(W @ v.co)[:] for v in mm.vertices], [list(p.vertices) for p in mm.polygons]); oe.to_mesh_clear()
    for s, idx in SETS.items():
        for t, tr in tg.items():
            if "ForeArm" in s and t != "body": continue
            d = inside(tr, P[idx]); r = res.setdefault(f"{s}>{t}", {"frames_over_3mm": [], "max_mm": 0.0, "max_frame": None})
            mx_ = float(d.max()) * 1000
            if mx_ > 3: r["frames_over_3mm"].append(f)
            if mx_ > r["max_mm"]: r["max_mm"], r["max_frame"] = round(mx_, 1), f
def runs(fs):
    o = []
    for x in fs:
        if o and x - o[-1][1] <= step: o[-1][1] = x
        else: o.append([x, x])
    return o
for k, r in res.items(): r["n_over_3mm"] = len(r["frames_over_3mm"]); r["runs"] = runs(r.pop("frames_over_3mm"))
summary = dict(range=[f0, f1], step=step, trunk_faces=len(tpolys), sets={k: len(v) for k, v in SETS.items()}, pen=res)
json.dump(summary, open(out, "w"), indent=1)
print("@@PEN@@" + json.dumps(summary), flush=True)
