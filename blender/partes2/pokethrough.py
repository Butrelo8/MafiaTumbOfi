# pokethrough.py -- <clip.blend open> <out.json> [step]: poke-through on every step-th frame (default every frame) of a
# parts-Diego clip, depths in mm (figure 1.0 m tall, colddrone's frame).
# The body volume is the rigged Mixamo proxy ("proxy", 3 mm voxel remesh of the skin, one watertight piece, same
# weights): the skin itself is 3439 UV-seam pieces with a double body wall and four overlapping shells per hand, so
# an odd-hit vote on it is meaningless (the first version tested 1303 of 206161 skin vertices).
#   cloth->body : a shirt/pants vertex behind the nearest proxy face (within 3 cm) AND enclosed by the proxy
#                 (penlib's 6-ray vote, read-only from colddrone, as pen.py). Depth = distance to the proxy surface.
#                 "visible" = the skin vertex nearest that face (at rest) is not masked; "raw" = any face.
#   hands->trunk: a skin hand vertex (dominant *Hand*) behind the nearest proxy trunk face (torso, head, legs: pen.py's
#                 set) and enclosed by the proxy.
#   hands->cloth: a skin hand vertex behind the trunk cloth (shirt/pants faces dominated by trunk bones, no sleeves):
#                 c = its nearest such point (within 3 cm), the face normal turned away from the proxy trunk point
#                 nearest c; through when v lies behind that face along the normal
#                 (not beside a hem edge). Depth = |v - c|.
#                 NOT VALIDATED: guitar f122 still reads ~30 mm at the edge of the search radius, unexplained.
#   Every kind is also measured at rest (the baseline); "control" = a point 5 mm inside the hip at rest (must read ~5).
# Writes per frame maxima, the worst frames and the worst vertex per kind; prints @@POKE@@ with the clip maxima.
import bpy, sys, json, os
PEN = "E:/Cursor Projects/MTO-colddrone/blender/partes/mixskin"   # penlib.py, read-only (colddrone, untracked, 11-14)
sys.path.insert(0, PEN); import penlib
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]; step = int(a[1]) if len(a) > 1 else 1
sc = bpy.context.scene; arm = bpy.data.objects["mx"]; skin = bpy.data.objects["Diego"]; prox = bpy.data.objects["proxy"]
skin.modifiers["Mask"].show_viewport = False; prox.hide_viewport = False
cloth = [bpy.data.objects[n] for n in ("shirt", "pants")]


def dominant(o):
    names = {g.index: g.name for g in o.vertex_groups}; d = []
    for v in o.data.vertices:
        gs = [(g.weight, names[g.group]) for g in v.groups if names[g.group].startswith("mixamorig")]
        d.append(max(gs)[1].split(":")[1] if gs else "")
    return np.array(d)


TRUNK = {"Hips", "Spine", "Spine1", "Spine2", "Neck", "Head", "LeftUpLeg", "RightUpLeg", "LeftLeg", "RightLeg", "LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase"}
sdom = dominant(skin); hand = np.flatnonzero(np.char.find(sdom, "Hand") >= 0)
hid_i = skin.vertex_groups["hidden"].index
hidden = np.array([any(g.group == hid_i and g.weight > 0.5 for g in v.groups) for v in skin.data.vertices])
pdom = dominant(prox); PP = [list(p.vertices) for p in prox.data.polygons]
cdom = {o.name: dominant(o) for o in cloth}             # hands->cloth uses the trunk cloth only (no sleeves)
P_trunk = [p for p in PP if all(pdom[i] in TRUNK for i in p)]


def world(o, dg):
    e = o.evaluated_get(dg); m = e.to_mesh(); k = len(m.vertices)
    P = np.empty(k * 3); m.vertices.foreach_get("co", P); e.to_mesh_clear()
    M = np.array(o.matrix_world); return P.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]


def cloth_tree(dg):
    V, F = [], []
    for o in cloth:
        P = world(o, dg); off = len(V); V.extend(map(Vector, P))
        F.extend([[off + i for i in p.vertices] for p in o.data.polygons if all(cdom[o.name][i] in TRUNK for i in p.vertices)])
    return V, F


arm.data.pose_position = "REST"; sc.frame_set(sc.frame_start); dg = bpy.context.evaluated_depsgraph_get()
B0 = world(skin, dg); kd = KDTree(len(B0))
for i, p in enumerate(B0): kd.insert(p, i)
kd.balance()
X0 = world(prox, dg)
P_vis = np.array([not hidden[kd.find(Vector(X0[p].mean(0)))[1]] for p in PP])   # proxy face over visible skin


def measure(dg, extra=None):
    """Worst depth (m) and vertex of each kind on the current evaluated frame."""
    X = list(map(Vector, world(prox, dg))); tP = BVHTree.FromPolygons(X, PP); tT = BVHTree.FromPolygons(X, P_trunk)
    r = {k: (0.0, None) for k in ("cloth_body_visible", "cloth_body_raw", "hands_trunk", "hands_cloth")}
    for o in cloth:
        for vi, p in enumerate(map(Vector, world(o, dg))):
            loc, n, fi, d = tP.find_nearest(p, 0.03)
            if loc is None or (p - loc).dot(n) >= 0 or d <= 0.0003: continue
            if d <= r["cloth_body_raw"][0] and not (P_vis[fi] and d > r["cloth_body_visible"][0]): continue
            if not penlib.enclosed(tP, p): continue
            if d > r["cloth_body_raw"][0]: r["cloth_body_raw"] = (d, f"{o.name}:{vi}")
            if P_vis[fi] and d > r["cloth_body_visible"][0]: r["cloth_body_visible"] = (d, f"{o.name}:{vi}")
    CV, CF = cloth_tree(dg); tC = BVHTree.FromPolygons(CV, CF)
    S = world(skin, dg); pts = [(f"Diego:{i}", Vector(S[i])) for i in hand] + (extra or [])
    for name, v in pts:
        loc, n, fi, d = tT.find_nearest(v, 0.03)
        if loc is not None and (v - loc).dot(n) < 0 and d > r["hands_trunk"][0] and penlib.enclosed(tP, v):
            r["hands_trunk"] = (d, name)
        c, nc, _, dc = tC.find_nearest(v, 0.03)
        if c is None or dc <= r["hands_cloth"][0]: continue
        b = tT.find_nearest(c)[0]
        if nc.dot(c - b) < 0: nc = -nc                  # cloth normal pointing away from the body
        if (v - c).dot(nc) < -0.9 * dc: r["hands_cloth"] = (dc, name)   # behind the face, not beside its edge
    return {k: (round(d * 1000, 2), w) for k, (d, w) in r.items()}


# rest baseline and the positive control: a point 5 mm inside the front of the hip (0.27 m up, under the pants), which
# must read ~5 on hands_trunk and > 0 on hands_cloth.
X = list(map(Vector, world(prox, dg))); tT = BVHTree.FromPolygons(X, P_trunk)
loc, n, _, _ = tT.find_nearest(Vector((0.08, -0.2, 0.27)))
rest = measure(dg, [("control_5mm", loc - n * 0.005)])
arm.data.pose_position = "POSE"
rows = []
for f in range(sc.frame_start, sc.frame_end + 1, step):
    sc.frame_set(f); m = measure(bpy.context.evaluated_depsgraph_get())
    rows.append({"f": f, **{k: v[0] for k, v in m.items()}, "where": {k: v[1] for k, v in m.items()}})
    print("@@ f", f, {k: v[0] for k, v in m.items()}, flush=True)
keys = ["cloth_body_visible", "cloth_body_raw", "hands_trunk", "hands_cloth"]
summ = {k: {"max": max(r[k] for r in rows), "frame": max(rows, key=lambda r: r[k])["f"],
            "where": max(rows, key=lambda r: r[k])["where"][k], "frames_over_1mm": int(sum(r[k] > 1 for r in rows))} for k in keys}
summ["rest"] = rest; summ["penlib_mtime"] = os.path.getmtime(os.path.join(PEN, "penlib.py")); summ["frames"] = len(rows)
json.dump({"summary": summ, "rows": rows}, open(out, "w"), indent=1)
print("@@POKE@@", json.dumps(summ))
