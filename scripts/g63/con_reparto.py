import bpy, sys, os
from mathutils import Vector, Matrix
# car + cast at the old placement (+ optional shift) with the cab cameras: -- <reparto.glb> <out_prefix> <dy> <dz> <cam...>
exec(open(r"E:\tmp\mto-g63-nuevo\scripts\still_lib.py").read())
a = sys.argv[sys.argv.index("--") + 1:]
glb, pre, dy, dz, cams = a[0], a[1], float(a[2]), float(a[3]), a[4:]
antes = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=glb)
nuevos = [o for o in bpy.data.objects if o not in antes]
for o in nuevos:
    if o.name.endswith("_v5_rig"):
        o.location += Vector((0, dy, dz))
    if o.name == "camion" and o not in antes:
        o.name = "camion_reparto"
for o in bpy.data.objects:  # hide the roof load for the cab views if asked
    if os.environ.get("SIN_TECHO") and (o.name.startswith(("carga_", "k3_", "rack_"))):
        o.hide_render = True
for c in cams:
    n, p, m, l = c.split(":")
    render(f"{pre}-{n}.png", p, m, l)
