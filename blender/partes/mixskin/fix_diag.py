# fix_diag.py: at one frame of a body_fix.py blend, the inside hand / forearm vertices with the fix layer on and off:
# count, max depth, where they sit (dominant bone of the nearest trunk face) and how far the hand moved.
#   $B -b <fixed blend> --python fix_diag.py -- <frame> [side Right]
import bpy, sys, os
sys.path.append(os.path.dirname(__file__))
import numpy as np
from mathutils.bvhtree import BVHTree
from penlib import TRUNK, dominant, body_world, inside
a = sys.argv[sys.argv.index("--") + 1:]; f = int(a[0]); S = a[1] if len(a) > 1 else "Right"
sc = bpy.context.scene; mx = bpy.data.objects["mx"]; body = bpy.data.objects["Body"]; ad = mx.animation_data
dom = dominant(body); istrunk = np.isin(dom, list(TRUNK)); polys = [list(p.vertices) for p in body.data.polygons]
tp = [p for p in polys if all(istrunk[i] for i in p)]; tdom = [dom[p[0]] for p in tp]
idx = np.flatnonzero(np.char.startswith(dom, S + "Hand") | (dom == S + "ForeArm"))
fc = [c for c in ad.action.layers[0].strips[0].channelbags[0].fcurves]
print("@@FC@@", [(c.data_path[-40:], c.array_index, round(min(k.co[1] for k in c.keyframe_points), 4), round(max(k.co[1] for k in c.keyframe_points), 4)) for c in fc])
for on in (1.0, 0.0):
    ad.action_influence = on; sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); P = body_world(body, dg)
    tree = BVHTree.FromPolygons(P.tolist(), tp, all_triangles=False)
    d = inside(tree, P[idx]); sel = np.flatnonzero(d > 0)
    where = {}
    for k in sel:
        loc, n, i, dist = tree.find_nearest(P[idx][k].tolist(), 0.06); where[tdom[i]] = where.get(tdom[i], 0) + 1
    print("@@DIAG@@", dict(influence=on, n_inside=len(sel), max_mm=round(float(d.max()) * 1000, 2), where=where,
                           vdom={str(x): int((dom[idx][sel] == x).sum()) for x in set(dom[idx][sel])},
                           tail=[round(x, 4) for x in (mx.matrix_world @ mx.pose.bones[f"mixamorig:{S}Hand"].tail)]), flush=True)
