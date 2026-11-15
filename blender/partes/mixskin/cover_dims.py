# cover_dims.py: each cover's largest rest extent in mm (the "elbow ball" size), from a parts blend.
import bpy, json
from mathutils import Vector
r = {}
for o in bpy.data.objects:
    if o.name.startswith("cover_") and o.type == "MESH":
        P = [o.matrix_world @ v.co for v in o.data.vertices]
        if P: r[o.name[6:]] = round(max(max(p[i] for p in P) - min(p[i] for p in P) for i in range(3)) * 1000)
print("@@COVERDIMS@@" + json.dumps(dict(sorted(r.items()))))
