# blender -b --factory-startup --python vistas.py -- <in.glb> <out_prefix> [lit|flat|nonormal] [size]
import bpy, sys, math, json
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
src, out = argv[0], argv[1]
mode = argv[2] if len(argv) > 2 else "lit"
size = int(argv[3]) if len(argv) > 3 else 900

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]

info = {"missing_images": [], "materials": {}}
for img in bpy.data.images:
    if img.source == "FILE" and not img.has_data and not img.packed_file:
        info["missing_images"].append(img.name)
for m in bpy.data.materials:
    if not m.use_nodes:
        continue
    links = [f"{l.from_node.bl_idname}:{l.from_socket.name}->{l.to_node.bl_idname}:{l.to_socket.name}" for l in m.node_tree.links]
    imgs = {n.image.name: [n.image.colorspace_settings.name, list(n.image.size)] for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image}
    info["materials"][m.name] = {"links": links, "images": imgs, "blend": getattr(m, "surface_render_method", "")}
info["tris"] = sum(len(o.data.loop_triangles) or (o.data.calc_loop_triangles() or len(o.data.loop_triangles)) for o in meshes)
print("INFO " + json.dumps(info))

for m in bpy.data.materials:
    nt = m.node_tree
    if not nt:
        continue
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    outn = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if mode == "flat" and bsdf:
        col = bsdf.inputs["Base Color"].links[0].from_socket if bsdf.inputs["Base Color"].links else None
        em = nt.nodes.new("ShaderNodeEmission")
        if col:
            nt.links.new(col, em.inputs["Color"])
        nt.links.new(em.outputs[0], outn.inputs["Surface"])
    if mode in ("metal", "rough") and bsdf:
        inp = bsdf.inputs["Metallic" if mode == "metal" else "Roughness"]
        sock = inp.links[0].from_socket if inp.links else None
        em = nt.nodes.new("ShaderNodeEmission")
        if sock: nt.links.new(sock, em.inputs["Color"])
        else: em.inputs["Color"].default_value = (inp.default_value,) * 3 + (1,)
        nt.links.new(em.outputs[0], outn.inputs["Surface"])
    if mode == "nonormal" and bsdf:
        for l in list(bsdf.inputs["Normal"].links):
            nt.links.remove(l)

# bounds
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
ctr = (lo + hi) / 2
h = hi.z - lo.z
print("BOUNDS", tuple(lo), tuple(hi))

sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.cycles.use_denoising = True
try:
    p = bpy.context.preferences.addons["cycles"].preferences
    p.compute_device_type = "OPTIX"
    p.get_devices()
    for d in p.devices:
        d.use = True
    sc.cycles.device = "GPU"
except Exception as e:
    print("GPU fail", e)
sc.render.resolution_x = int(size * 0.75)
sc.render.resolution_y = size
sc.render.film_transparent = False
sc.view_settings.view_transform = "Standard" if mode in ("flat", "metal", "rough") else "AgX"

w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.55, 0.56, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = {"lit": 0.6, "flat": 1.0}.get(mode, 0.0)
if mode in ("lit", "nonormal"):
    for name, rot, e in [("key", (50, 0, -35), 3.0), ("fill", (60, 0, 140), 1.0)]:
        L = bpy.data.lights.new(name, "SUN"); L.energy = e; L.angle = math.radians(8)
        o = bpy.data.objects.new(name, L); o.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(o)

cam = bpy.data.cameras.new("cam"); cam.type = "ORTHO"; cam.ortho_scale = h * 1.1
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
dist = 5 * h
views = [("front", (0, -1)), ("right", (1, 0)), ("back", (0, 1)), ("left", (-1, 0))]
for name, (dx, dy) in views:
    co.location = ctr + Vector((dx * dist, dy * dist, 0))
    co.rotation_euler = (Vector((0, 0, 0)) - Vector((dx, dy, 0))).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = f"{out}_{name}.png"
    bpy.ops.render.render(write_still=True)
