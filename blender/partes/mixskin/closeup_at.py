# closeup_at.py: one lit close-up per (frame, bone) of a Mixamo-rig blend, aimed at the bone's tail (hand tip) from the
# figure's front three-quarter and from its side, clip_stills.py's light; for the hand-through-body / prop frames pen.py finds.
#   $B -b <blend> --python closeup_at.py -- <out dir (Windows)> <frame:bone,...> [ortho m, default 0.3]
import bpy, sys, math, os
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]; out = a[0]; jobs = [x.split(":") for x in a[1].split(",")]; S = float(a[2]) if len(a) > 2 else 0.3
sc = bpy.context.scene; mx = bpy.data.objects["mx"]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = not (o.name == "Body" or o.name.startswith("prop_"))
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sun = bpy.data.objects.new("S", bpy.data.lights.new("S", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.6, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
sc.view_settings.view_transform = "Standard"; sc.render.use_compositing = False
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.clip_end = 100; cam.data.ortho_scale = S
sc.render.resolution_x = sc.render.resolution_y = 512; sc.render.resolution_percentage = 100
hb = mx.data.bones["mixamorig:Hips"]; hp = mx.pose.bones["mixamorig:Hips"]
for f, bn in jobs:
    sc.frame_set(int(f))
    R = mx.matrix_world.to_3x3() @ hp.matrix.to_3x3() @ hb.matrix_local.to_3x3().inverted() @ mx.matrix_world.to_3x3().inverted()
    fwd = R @ Vector((0, -1, 0)); fwd.z = 0; fwd.normalize(); left = Vector((-fwd.y, fwd.x, 0))
    t = mx.matrix_world @ mx.pose.bones["mixamorig:" + bn].tail
    for tag, d in (("q", (-fwd - left * 0.6).normalized()), ("s", (-left if bn.startswith("Left") else left))):
        d = Vector(d) + Vector((0, 0, -0.15)); d.normalize()
        cam.location = t - d * 3; cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out, f"pen_f{int(f):04d}_{bn}_{tag}.png"); bpy.ops.render.render(write_still=True)
print("@@CLOSEUP@@", out, jobs, flush=True)
