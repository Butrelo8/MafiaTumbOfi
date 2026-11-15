# dump.py: rest mesh of Body (verts, tris, per-corner UV) + ORG bone rest/pose matrices over the idle -> npz/json.
#   $B -b idle_v2.blend --python dump.py -- <out dir (Windows)>
import bpy, sys, json, numpy as np, math
out = sys.argv[sys.argv.index("--") + 1]
ob = bpy.data.objects["Body"]; me = ob.data; rig = bpy.data.objects["rig"]
me.calc_loop_triangles()
V = np.array([v.co for v in me.vertices], np.float32)
T = np.array([t.vertices[:] for t in me.loop_triangles], np.int32)
TL = np.array([t.loops[:] for t in me.loop_triangles], np.int32)
UV = np.zeros((len(me.loops), 2), np.float32); me.uv_layers.active.data.foreach_get("uv", UV.ravel())
LV = np.array([l.vertex_index for l in me.loops], np.int32)
np.savez_compressed(out + r"\mesh.npz", V=V, T=T, TL=TL, UV=UV, LV=LV, mw=np.array(ob.matrix_world))
names = [b.name for b in rig.data.bones if b.name.startswith("ORG-")]
res = {"rest": {n: [list(r) for r in rig.data.bones[n].matrix_local] for n in names}, "pose": {}}
for f in range(1, 121):
    bpy.context.scene.frame_set(f)
    res["pose"][f] = {n: [list(r) for r in (rig.matrix_world @ rig.pose.bones[n].matrix)] for n in names}
json.dump(res, open(out + r"\bones.json", "w"))
print("@@DUMP@@", V.shape, T.shape, len(names), list(rig.matrix_world.to_translation()), [round(math.degrees(a),1) for a in rig.matrix_world.to_euler()])
