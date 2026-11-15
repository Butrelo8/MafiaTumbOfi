# pen_diag.py: checks pen.py's normal test at given frames. For the hand vertices it calls inside: the bone region of the
# nearest trunk face, and a ray-parity vote (6 axis rays against the trunk faces; inside = odd hits on >= 4 of 6).
#   $B -b <blend> --python pen_diag.py -- <frames,...> [hand: Left|Right]
import bpy, sys, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]; frames = [int(x) for x in a[0].split(",")]; side = a[1] if len(a) > 1 else "Left"
sc = bpy.context.scene; body = bpy.data.objects["Body"]; me = body.data; nv = len(me.vertices)
names = {g.index: g.name for g in body.vertex_groups}
dom = np.array([max([(g.weight, names[g.group]) for g in v.groups if names[g.group].startswith("mixamorig")] or [(0, ":")])[1].split(":")[1] for v in me.vertices])
TR = {"Hips", "Spine", "Spine1", "Spine2", "Neck", "Head", "LeftUpLeg", "RightUpLeg", "LeftLeg", "RightLeg", "LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase"}
ist = np.isin(dom, list(TR)); polys = [list(p.vertices) for p in me.polygons]; tp = [p for p in polys if all(ist[i] for i in p)]
hand = np.flatnonzero(np.char.startswith(dom, side + "Hand"))
D = [Vector(d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]
out = {}
for f in frames:
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); ev = body.evaluated_get(dg); m = ev.to_mesh()
    P = np.empty(nv * 3, np.float32); m.vertices.foreach_get("co", P); ev.to_mesh_clear()
    P = P.reshape(-1, 3) @ np.array(body.matrix_world.to_3x3()).T + np.array(body.matrix_world.translation)
    tree = BVHTree.FromPolygons(P.tolist(), tp, all_triangles=False)
    norm_in, par_in, both, regions, depth = 0, 0, 0, {}, []
    for i in hand[::4]:
        p = Vector(P[i]); loc, n, fi, dist = tree.find_nearest(p, 0.06)
        ni = loc is not None and (p - loc).dot(n) < 0
        odd = 0
        for d in D:
            c, q = 0, p + d * 1e-5
            while True:
                hit = tree.ray_cast(q, d, 2.0)
                if hit[0] is None: break
                c += 1; q = hit[0] + d * 1e-5
            odd += c % 2
        pi = odd >= 4
        norm_in += ni; par_in += pi; both += ni and pi
        if ni and pi:
            r = dom[tp[fi][0]]; regions[r] = regions.get(r, 0) + 1; depth.append(dist)
    out[f] = dict(sampled=len(hand[::4]), normal_in=norm_in, parity_in=par_in, both=both, regions=regions,
                  both_depth_mm_p50_max=[round(float(np.median(depth)) * 1000, 1), round(float(max(depth)) * 1000, 1)] if depth else None)
print("@@DIAG@@" + json.dumps(out), flush=True)
