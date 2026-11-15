# fix_probe.py: numbers for fitting the hand fixes and props on a Mixamo clip blend (armature "mx", mesh "Body"):
# body height, hand mesh extents, per frame the hand tails in world and in the Spine2 frame, the hand-to-head distance.
#   $B -b <blend> --python fix_probe.py -- <out.json (Windows)>
import bpy, sys, json
import numpy as np
from mathutils import Vector
out = sys.argv[sys.argv.index("--") + 1:][0]
sc = bpy.context.scene; mx = bpy.data.objects["mx"]; body = bpy.data.objects["Body"]; PB = mx.pose.bones
f0, f1 = map(int, mx.animation_data.action.frame_range)
W = lambda n, t="head": mx.matrix_world @ getattr(PB["mixamorig:" + n], t)
names = {g.index: g.name.split(":")[-1] for g in body.vertex_groups}
dom = np.array([max(((g.weight, names[g.group]) for g in v.groups), default=(0, ""))[1] for v in body.data.vertices])
co = np.array([v.co[:] for v in body.data.vertices]) @ np.array(body.matrix_world.to_3x3()).T + np.array(body.matrix_world.translation)
info = dict(range=[f0, f1], height=float(co[:, 2].max() - co[:, 2].min()))
for S in ("Left", "Right"):
    h = co[np.char.startswith(dom, S + "Hand")]; info[S + "Hand_rest_extent_mm"] = (1000 * (h.max(0) - h.min(0))).round(1).tolist()
fr = []
for f in range(f0, f1 + 1):
    sc.frame_set(f); M = (mx.matrix_world @ PB["mixamorig:Spine2"].matrix).inverted()
    r = dict(f=f, hips=W("Hips")[:], head=W("Head")[:])
    for S in ("Left", "Right"):
        t = W(S + "Hand", "tail"); r[S] = t[:]; r[S + "_sp"] = (M @ t)[:]; r[S + "_head"] = (t - W("Head")).length
    fr.append(r)
info["frames"] = fr
json.dump(info, open(out, "w"))
print("@@PROBE@@", out, info["height"], flush=True)
