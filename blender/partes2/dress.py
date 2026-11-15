# dress.py -- <fit dir> <assets dir> <out.blend> name=glb ...: the open blend (the skin, "Diego") plus each clothing
# part <glb>.glb as an object called <name> (shirt, pants, shoes, hair). Each part takes its fitted vertex positions
# from <fit dir>/<glb>_body.npz (fit_body.py: P in GLB vertex order, keep mask) when it exists, else the rigid
# <fit dir>/<glb>.json "T"; vertices outside keep are deleted (caps and inner shells).
import bpy, bmesh, sys, os, json
import numpy as np
from mathutils import Matrix
a = sys.argv[sys.argv.index("--") + 1:]
fit, assets, out = a[:3]
for item in a[3:]:
    name, glb = item.split("=")
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(assets, glb + ".glb"))
    new = [o for o in bpy.data.objects if o not in before]
    m = [o for o in new if o.type == "MESH"][0]
    for o in new:
        if o is not m: bpy.data.objects.remove(o, do_unlink=True)
    m.data.transform(m.matrix_world); m.matrix_world = Matrix.Identity(4)
    npz = os.path.join(fit, glb + "_body.npz")
    if os.path.exists(npz):
        Z = np.load(npz); P, keep = Z["P"], Z["keep"]
        if len(P) != len(m.data.vertices): raise SystemExit(f"{glb}: {len(P)} fitted vs {len(m.data.vertices)} imported vertices")
        m.data.vertices.foreach_set("co", P.ravel()); m.data.update()
        bm = bmesh.new(); bm.from_mesh(m.data); bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.verts[i] for i in np.flatnonzero(~keep)], context="VERTS"); bm.to_mesh(m.data); bm.free()
    else:
        m.data.transform(Matrix(json.load(open(os.path.join(fit, glb + ".json")))["T"]))
    m.name = m.data.name = name
    print("@@", name, glb, "fitted" if os.path.exists(npz) else "rigid", len(m.data.vertices), "verts")
bpy.ops.wm.save_as_mainfile(filepath=out)
