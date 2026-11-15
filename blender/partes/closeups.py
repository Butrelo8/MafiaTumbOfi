# closeups.py: lit close-ups of the joints of a parts blend at one frame, with cameras that depend only on the cut
# (its centroid carried by the child part), so a before and an after blend share every framing. Also one full-body
# front still with a fixed frame (the figures are 1 m tall, feet at z 0). EEVEE, tex_probe.py's one sun + grey world.
#   $B -b <parts.blend> --python closeups.py -- <split.json> <out dir (Windows)> <frame> [joints, default shoulder.L,knee.L,elbow.L,wrist.L]
# Writes <out>/<joint>_<view>_f<frame>.png (512 px; views q = front three-quarter, s = side) and full_front_f<frame>.png.
import bpy, sys, json, math, os
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
info = json.load(open(a[0])); out = a[1]; frame = int(a[2])
joints = (a[3] if len(a) > 3 else "shoulder.L,knee.L,elbow.L,wrist.L").split(",")
sc = bpy.context.scene; sc.frame_set(frame)
for o in sc.objects:
    if o.type == "MESH": o.hide_render = not o.name.startswith(("part_", "cover_"))
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sun = bpy.data.objects.new("S", bpy.data.lights.new("S", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.6, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
sc.view_settings.view_transform = "Standard"; sc.render.film_transparent = False; sc.render.use_compositing = False
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.clip_end = 100
def shoot(target, d, scale, px, path):
    d = Vector(d).normalized(); cam.location = Vector(target) - d * 3; cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = scale; sc.render.resolution_x = sc.render.resolution_y = px; sc.render.resolution_percentage = 100
    sc.render.filepath = path; bpy.ops.render.render(write_still=True)
shoot((0, 0, 0.5), (0, 1, 0), 1.04, 1024, os.path.join(out, f"full_front_f{frame}.png"))
for jn in joints:
    c = info["cuts"][jn]; ch = bpy.data.objects["part_" + c["child"]]
    t = ch.matrix_world @ Vector(c["co"]); k = 1 if jn.endswith(".L") else -1
    bn = {"elbow": "ORG-forearm", "wrist": "ORG-hand"}.get(jn.split(".")[0])   # these cuts snap to different rings per
    if bn: rg = bpy.data.objects["rig"]; t = rg.matrix_world @ rg.pose.bones[bn + jn[-2:]].head   # blend: aim at the bone
    for v, d in (("q", (-0.55 * k, 1, -0.25)), ("s", (-k, 0.15, -0.2))):
        shoot(t, d, 0.24, 512, os.path.join(out, f"{jn}_{v}_f{frame}.png"))
print("@@CLOSEUPS@@", out, frame, flush=True)
