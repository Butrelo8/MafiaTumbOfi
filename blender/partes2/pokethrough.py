# pokethrough.py -- <clip.blend open> <out.json> [step]: poke-through on every step-th frame (default every frame) of a
# parts-Diego clip, depths in mm. The skin is measured before its Mask (every vertex), on its largest connected piece
# only (TRELLIS leaves ~500 small inner pieces whose faces would read as false hits).
#   cloth->body : a shirt/pants vertex behind the nearest skin face (within 3 cm) AND enclosed by the skin (penlib's
#                 6-ray vote, read-only from colddrone, as pen.py does).
#                 "visible" = that face has no hidden (masked) vertex; "raw" = any face.
#   body->cloth : a visible skin vertex whose ray back into the body (-normal) crosses shirt/pants within 1.5 cm
#                 (the cloth is between it and the body). Every kind is also reported at rest (the baseline).
#   hands->trunk: a hand vertex (dominant LeftHand*/RightHand*) behind the nearest trunk face (torso, head, legs).
# Writes per frame maxima and the worst frames; prints @@POKE@@ with the clip maxima.
import bpy, bmesh, sys, json, os
PEN = "E:/Cursor Projects/MTO-colddrone/blender/partes/mixskin"   # penlib.py, read-only (colddrone, untracked, 11-14)
sys.path.insert(0, PEN); import penlib
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]; step = int(a[1]) if len(a) > 1 else 1
sc = bpy.context.scene; arm = bpy.data.objects["mx"]; skin = bpy.data.objects["Diego"]
skin.modifiers["Mask"].show_viewport = False
me = skin.data; nv = len(me.vertices)
names = {g.index: g.name for g in skin.vertex_groups}; hid_i = skin.vertex_groups["hidden"].index
hidden = np.zeros(nv, bool); dom = []
for v in me.vertices:
    gs = [(g.weight, names[g.group]) for g in v.groups if names[g.group].startswith("mixamorig")]
    dom.append(max(gs)[1].split(":")[1] if gs else "")
    hidden[v.index] = any(g.group == hid_i and g.weight > 0.5 for g in v.groups)
dom = np.array(dom)
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()        # largest connected piece of the skin
seen = np.zeros(nv, bool); best = []
for v0 in bm.verts:
    if seen[v0.index]: continue
    stack, comp = [v0], []; seen[v0.index] = True
    while stack:
        v = stack.pop(); comp.append(v.index)
        for e in v.link_edges:
            w = e.other_vert(v)
            if not seen[w.index]: seen[w.index] = True; stack.append(w)
    if len(comp) > len(best): best = comp
main = np.zeros(nv, bool); main[best] = True; bm.free()
polys = [list(p.vertices) for p in me.polygons]
P_main = [p for p in polys if main[p[0]]]
P_hid = np.array([any(hidden[i] for i in p) for p in P_main])
TRUNK = {"Hips", "Spine", "Spine1", "Spine2", "Neck", "Head", "LeftUpLeg", "RightUpLeg", "LeftLeg", "RightLeg"}
P_trunk = [p for p in P_main if all(dom[i] in TRUNK for i in p)]
hand = np.flatnonzero(main & (np.char.find(dom, "Hand") >= 0))
vis = np.flatnonzero(main & ~hidden)
cloth = [bpy.data.objects[n] for n in ("shirt", "pants")]


def world(o, dg):
    e = o.evaluated_get(dg); m = e.to_mesh(); k = len(m.vertices)
    P = np.empty(k * 3); m.vertices.foreach_get("co", P); e.to_mesh_clear()
    M = np.array(o.matrix_world); return P.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]


def cloth_tree(dg):
    V, F = [], []
    for o in cloth:
        P = world(o, dg); off = len(V); V.extend(map(Vector, P)); F.extend([[off + i for i in p.vertices] for p in o.data.polygons])
    return V, F


# rest pose first: the baseline of every kind
arm.data.pose_position = "REST"; sc.frame_set(sc.frame_start); dg = bpy.context.evaluated_depsgraph_get()
B = list(map(Vector, world(skin, dg))); tB = BVHTree.FromPolygons(B, P_main)
CV, CF = cloth_tree(dg); tC = BVHTree.FromPolygons(CV, CF)


def body_out(B, BN, tC):
    """A visible skin vertex is through the cloth when a ray from it back into the body (-normal) crosses cloth within
    1.5 cm: the cloth is then between it and the body. Depth = that distance."""
    worst = 0.0
    for i in vis:
        hit = tC.ray_cast(B[i] - BN[i] * 1e-5, -BN[i], 0.015)
        if hit[0] is not None and hit[3] > worst: worst = hit[3]
    return worst


def normals(o, dg):
    e = o.evaluated_get(dg); m = e.to_mesh(); k = len(m.vertices)
    N = np.empty(k * 3); m.vertices.foreach_get("normal", N); e.to_mesh_clear()
    return [Vector(n).normalized() for n in N.reshape(-1, 3) @ np.array(o.matrix_world.to_3x3()).T]


def cloth_in(B, tB, dg):
    """Cloth vertices behind the nearest skin face AND enclosed by the skin (penlib's 6-ray vote, as pen.py)."""
    cv_ = cr_ = 0.0
    for o in cloth:
        for p in map(Vector, world(o, dg)):
            loc, n, fi, d = tB.find_nearest(p, 0.03)
            if loc is not None and (p - loc).dot(n) < 0 and d > max(cr_, 0.0005) and penlib.enclosed(tB, p):
                cr_ = d
            if loc is not None and (p - loc).dot(n) < 0 and not P_hid[fi] and d > max(cv_, 0.0005) and penlib.enclosed(tB, p):
                cv_ = d
    return cv_, cr_


rest_cv, rest_cr = cloth_in(B, tB, dg)
rest_bo = body_out(B, normals(skin, dg), tC); arm.data.pose_position = "POSE"
rows = []
for f in range(sc.frame_start, sc.frame_end + 1, step):
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
    B = list(map(Vector, world(skin, dg))); tB = BVHTree.FromPolygons(B, P_main); tT = BVHTree.FromPolygons(B, P_trunk)
    cv_, cr_ = cloth_in(B, tB, dg)
    CV, CF = cloth_tree(dg); tC = BVHTree.FromPolygons(CV, CF); bo = body_out(B, normals(skin, dg), tC)
    hd = 0.0
    for i in hand:
        loc, n, fi, d = tT.find_nearest(B[i], 0.03)
        if loc is not None and (B[i] - loc).dot(n) < 0: hd = max(hd, d)
    rows.append({"f": f, "cloth_body_visible": float(cv_) * 1000, "cloth_body_raw": float(cr_) * 1000, "body_cloth": float(bo) * 1000, "hands_trunk": float(hd) * 1000})
keys = ["cloth_body_visible", "cloth_body_raw", "body_cloth", "hands_trunk"]
summ = {k: {"max": max(r[k] for r in rows), "frame": max(rows, key=lambda r: r[k])["f"],
            "frames_over_1mm": int(sum(r[k] > 1 for r in rows))} for k in keys}
summ["rest"] = {"cloth_body_visible": float(rest_cv) * 1000, "cloth_body_raw": float(rest_cr) * 1000, "body_cloth": float(rest_bo) * 1000}
summ["penlib_mtime"] = os.path.getmtime(os.path.join(PEN, "penlib.py")); summ["frames"] = len(rows)
json.dump({"summary": summ, "rows": rows}, open(out, "w"), indent=1)
print("@@POKE@@", json.dumps(summ))
