# crops.py: the binding test's tiles, the same for a parts blend and a skinned blend. Per frame: full front and front
# three-quarter (camera follows DEF-spine, rerig_stills.py framing) and left-side joint close-ups aimed at the rig's own
# bone heads (shoulder, elbow, wrist, hip, knee), closeups.py's light, world and q view. "rest" = every armature at rest.
#   $B -b <blend> --python crops.py -- <out dir (Windows)> <frames: rest,60,153,240> <parts|skin>
import bpy, sys, math, os
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
out, frames, mode = a[0], a[1].split(","), a[2]
sc = bpy.context.scene
for o in sc.objects:
    if o.type == "MESH": o.hide_render = not (o.name.startswith(("part_", "cover_")) if mode == "parts" else o.name == "Body")
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sun = bpy.data.objects.new("S", bpy.data.lights.new("S", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.6, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
sc.view_settings.view_transform = "Standard"; sc.render.film_transparent = False; sc.render.use_compositing = False
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.clip_end = 100
rig = bpy.data.objects["rig"]; arms = [o for o in sc.objects if o.type == "ARMATURE"]
JN = {"shoulder": "DEF-upper_arm.L", "elbow": "DEF-forearm.L", "wrist": "DEF-hand.L", "hip": "DEF-thigh.L", "knee": "DEF-shin.L"}
def shoot(target, d, scale, px, path):
    d = Vector(d).normalized(); cam.location = Vector(target) - d * 3; cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = scale; sc.render.resolution_x = sc.render.resolution_y = px; sc.render.resolution_percentage = 100
    sc.render.filepath = path; bpy.ops.render.render(write_still=True)
for fr in frames:
    rest = fr == "rest"
    for o in arms: o.data.pose_position = "REST" if rest else "POSE"
    sc.frame_set(1 if rest else int(fr)); bpy.context.view_layer.update()
    hd = lambda n: rig.matrix_world @ (rig.data.bones[n].head_local if rest else rig.pose.bones[n].head)
    hip = hd("DEF-spine")
    for tag, d in (("front", (0, 1, 0)), ("q", (-0.6, 1, 0))):
        d = Vector(d).normalized(); shoot(Vector((hip.x, hip.y, 0.55)), d, 1.3, 640, os.path.join(out, f"{tag}_f{fr}.png"))
    for j, n in JN.items():
        shoot(hd(n), (-0.55, 1, -0.25), 0.24, 384, os.path.join(out, f"{j}_f{fr}.png"))
print("@@CROPS@@", out, frames, flush=True)
