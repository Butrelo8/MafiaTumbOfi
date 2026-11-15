# blender -b --factory-startup --python estudio.py -- <in.glb> <out_prefix> [size] [samples] [rasante]
# The charm normalised as props_placement._fresa_mallas does (4.1 cm tall, top centre at the origin, rotated 0.5 rad about Z),
# rendered in a studio: `entera` (whole berry) and `macro` (1.6 cm window on the lower front body). `rasante` = one hard light
# from above (50°, in front), for reading the bump's direction (a raised seed is bright on top, dark underneath).
import bpy, sys, math, os
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
src, out = argv[0], argv[1]
size = int(argv[2]) if len(argv) > 2 else 1000
spp = int(argv[3]) if len(argv) > 3 else 128
rasante = len(argv) > 4 and argv[4] == "rasante"
ALTO = float(os.environ.get("PP_FRESA_ALTO", 0.041))  # whole mesh height; pass 2 sets 0.0647 so the BODY is 4.1 cm
K = ALTO / 0.041  # framing scales with the berry

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
pts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
k = ALTO / (hi.z - lo.z)
M = Matrix.Rotation(0.5, 4, "Z") @ Matrix.Scale(k, 4) @ Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, hi.z)))
for o in meshes:
    o.matrix_world = M @ o.matrix_world

sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = spp
sc.cycles.use_denoising = True
p = bpy.context.preferences.addons["cycles"].preferences
p.compute_device_type = "OPTIX"; p.get_devices()
for d in p.devices:
    d.use = True
sc.cycles.device = "GPU"
sc.render.resolution_x = sc.render.resolution_y = size
sc.view_settings.view_transform = "AgX"
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.18, 0.18, 0.19, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.0 if rasante else 0.25


def luz(nombre, tipo, loc, energia, tam):
    L = bpy.data.lights.new(nombre, tipo); L.energy = energia
    if tipo == "AREA":
        L.size = tam
    else:
        L.angle = math.radians(tam)
    o = bpy.data.objects.new(nombre, L); sc.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector((0, 0, -0.02)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


if rasante:
    luz("arriba", "SUN", (0, -1, 1.2), 4.0, 2)  # above and in front: straight down, the calyx shades the body
else:
    luz("key", "AREA", (-0.12, -0.15, 0.1), 1.5, 0.08)
    luz("fill", "AREA", (0.15, -0.1, -0.02), 0.4, 0.12)
    luz("rim", "AREA", (0.05, 0.15, 0.08), 0.8, 0.06)

cam = bpy.data.cameras.new("cam"); cam.lens = 100; cam.clip_start = 0.001
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
cuerpo = Vector((0, 0, -0.03 * K))  # mid body (top of the stem at 0, tip at -0.041)
for nombre, ventana, mira in (("entera", 0.05 * K, Vector((0, 0, -0.0215 * K))), ("macro", 0.016 * K, cuerpo)):
    if rasante and nombre == "entera":
        continue
    dist = ventana / cam.sensor_width * cam.lens
    co.location = mira + Vector((0, -dist, 0))
    co.rotation_euler = Vector((0, 1, 0)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = f"{out}_{nombre}.png"
    bpy.ops.render.render(write_still=True)
