# mouth_gap.py: per frame, the distance from a prop's lip (the top centre of its bounding box along local +z, the
# bottle's mouth) to the mouth vertex of Body (mouth_mark.py), over a frame range: min, the frame, and the range.
#   $B -b <blend> --python mouth_gap.py -- <prop> <mouth vertex> <f0-f1> <out.json (Windows)>
import bpy, sys, json
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]; p = bpy.data.objects[a[0]]; mv = int(a[1]); f0, f1 = map(int, a[2].split("-"))
sc = bpy.context.scene; body = bpy.data.objects["Body"]
zt = max(v[2] for v in p.bound_box); lip = Vector((0, 0, zt)); d = {}
for f in range(f0, f1 + 1):
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); ev = body.evaluated_get(dg); m = ev.to_mesh()
    d[f] = round(((p.matrix_world @ lip) - body.matrix_world @ m.vertices[mv].co).length * 1000, 1); ev.to_mesh_clear()
k = min(d, key=d.get); R = dict(prop=p.name, range=[f0, f1], min_mm=d[k], min_frame=k, max_mm=max(d.values()), per_frame_mm=d)
json.dump(R, open(a[3], "w")); print("@@MOUTHGAP@@", json.dumps({x: y for x, y in R.items() if x != "per_frame_mm"}), flush=True)
