# fix_diag3.py: at one frame, rotate the upper arm so the hand tail moves 10 / 20 mm along each world axis; depth of the
# hand inside the trunk for each, and which trunk bones the inside vertices sit against.
#   $B -b <fixed blend> --python fix_diag3.py -- <frame> <side>
import bpy, sys, os
sys.path.append(os.path.dirname(__file__))
import numpy as np
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree
from penlib import TRUNK, dominant, body_world, inside
a = sys.argv[sys.argv.index("--") + 1:]; f = int(a[0]); S = a[1]
sc = bpy.context.scene; mx = bpy.data.objects["mx"]; body = bpy.data.objects["Body"]; ad = mx.animation_data; PB = mx.pose.bones
dom = dominant(body); istrunk = np.isin(dom, list(TRUNK))
tp = [list(p.vertices) for p in body.data.polygons if all(istrunk[i] for i in p.vertices)]
idx = np.flatnonzero(np.char.startswith(dom, S + "Hand") | (dom == S + "ForeArm"))
bn = f'pose.bones["mixamorig:{S}Arm"].rotation_quaternion'
fcs = sorted([c for c in ad.action.layers[0].strips[0].channelbags[0].fcurves if c.data_path == bn], key=lambda c: c.array_index)
def setq(q):
    for c in fcs:
        for k in c.keyframe_points:
            if int(k.co[0]) == f: k.co[1] = q[c.array_index]
        c.update()
def meas():
    sc.frame_set(f); P = body_world(body, bpy.context.evaluated_depsgraph_get())
    tree = BVHTree.FromPolygons(P.tolist(), tp, all_triangles=False); d = inside(tree, P[idx]); return round(float(d.max()) * 1000, 2), int((d > 0).sum())
setq((1, 0, 0, 0)); sc.frame_set(f)
s = mx.matrix_world @ PB[f"mixamorig:{S}Arm"].head; t = mx.matrix_world @ PB[f"mixamorig:{S}Hand"].tail; r = t - s
M = (mx.matrix_world @ PB[f"mixamorig:{S}Arm"].matrix).to_3x3(); M.normalize()
print("@@BASE@@", meas(), "tail", [round(x, 3) for x in t], "arm dir", [round(x, 2) for x in r.normalized()], flush=True)
for mm in (10, 20):
    for ax in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        dv = Vector(ax) * mm / 1000; w = r.cross(dv) / r.length_squared   # w x r = dv (perpendicular part)
        vl = M.transposed() @ w; setq(Quaternion(vl.normalized(), vl.length)[:]) if vl.length > 1e-9 else setq((1, 0, 0, 0))
        sc.frame_set(f); t2 = mx.matrix_world @ PB[f"mixamorig:{S}Hand"].tail
        print("@@MOVE@@", mm, ax, "moved", [round(x * 1000, 1) for x in (t2 - t)], "->", meas(), flush=True)
setq((1, 0, 0, 0))
