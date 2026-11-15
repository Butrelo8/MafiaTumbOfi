# fix_diag2.py: body_fix.py's solve (penlib.arm_push, outer-skin depth) on one frame only, unsmoothed, 6 rounds: depth, |w|, mean push normal, hand motion.
#   $B -b <fixed blend> --python fix_diag2.py -- <frame> [side]
import bpy, sys, os
sys.path.append(os.path.dirname(__file__))
import numpy as np
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree
from penlib import TRUNK, dominant, body_world, inside_outer, arm_push
a = sys.argv[sys.argv.index("--") + 1:]; f = int(a[0]); S = a[1] if len(a) > 1 else "Right"
sc = bpy.context.scene; mx = bpy.data.objects["mx"]; body = bpy.data.objects["Body"]; ad = mx.animation_data; PB = mx.pose.bones
dom = dominant(body); istrunk = np.isin(dom, list(TRUNK))
tp = [list(p.vertices) for p in body.data.polygons if all(istrunk[i] for i in p.vertices)]
idx = np.flatnonzero(np.char.startswith(dom, S + "Hand") | (dom == S + "ForeArm"))
bn = f'pose.bones["mixamorig:{S}Arm"].rotation_quaternion'
fcs = [c for c in ad.action.layers[0].strips[0].channelbags[0].fcurves if c.data_path == bn]
def setq(q):
    for c in fcs:
        for k in c.keyframe_points:
            if int(k.co[0]) == f: k.co[1] = q[c.array_index]
        c.update()
def getq():
    return Quaternion([next(k.co[1] for k in c.keyframe_points if int(k.co[0]) == f) for c in sorted(fcs, key=lambda c: c.array_index)])
setq((1, 0, 0, 0))
for rnd in range(6):
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); P = body_world(body, dg)
    tree = BVHTree.FromPolygons(P.tolist(), tp, all_triangles=False); _, d, N = inside_outer(tree, P[idx]); sel = d > 0
    tail = mx.matrix_world @ PB[f"mixamorig:{S}Hand"].tail
    if not sel.any(): print("@@R@@", rnd, "clear", list(tail)); break
    s = np.array(mx.matrix_world @ PB[f"mixamorig:{S}Arm"].head); A = np.cross(P[idx][sel] - s, N[sel]); b = d[sel] + 0.0015
    w, push, across = arm_push(tree, P[idx][sel], N[sel], s, np.array(tail), 0.0015)
    pred = np.cross(w, P[idx][sel] - s); M = (mx.matrix_world @ PB[f"mixamorig:{S}Arm"].matrix).to_3x3(); M.normalize()
    vl = M.transposed() @ Vector(w)
    print("@@R@@", dict(rnd=rnd, n_in=int(sel.sum()), max_mm=round(d.max() * 1000, 2), w_deg=round(float(np.degrees(np.linalg.norm(w))), 2),
                         nmean=np.round(N[sel].mean(0), 2).tolist(), push_mm=np.round(push * 1000, 1).tolist(), across=round(across, 2),
                         tail=[round(x, 4) for x in tail]), flush=True)
    setq((getq() @ Quaternion(vl.normalized(), vl.length))[:])
