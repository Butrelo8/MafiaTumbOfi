# clip_stills.py: contact-sheet stills of a Mixamo-rig clip blend (armature "mx", mesh "Body", props prop_*): front and
# front three-quarter (from the figure's left), camera aimed by the figure's own facing (Hips rotation applied to the
# rest forward -Y) and following the hips, crops.py's light and world, ortho 1.3 m, 640 px.
#   $B -b <blend> --python clip_stills.py -- <out dir (Windows)> <n frames | f,f,...>
import bpy, sys, math, os
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]; sc = bpy.context.scene; mx = bpy.data.objects["mx"]
if "," in a[1]: frames = [int(x) for x in a[1].split(",")]
else:
    act = mx.animation_data.action if mx.animation_data and mx.animation_data.action else None
    f0, f1 = (map(int, act.frame_range) if act else (sc.frame_start, sc.frame_end)); n = int(a[1])
    frames = [round(f0 + (f1 - f0) * i / (n - 1)) for i in range(n)]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = not (o.name == "Body" or o.name.startswith("prop_"))
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sun = bpy.data.objects.new("S", bpy.data.lights.new("S", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.6, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
sc.view_settings.view_transform = "Standard"; sc.render.film_transparent = False; sc.render.use_compositing = False
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.clip_end = 100; cam.data.ortho_scale = 1.3
sc.render.resolution_x = sc.render.resolution_y = 640; sc.render.resolution_percentage = 100
hb = mx.data.bones["mixamorig:Hips"]; pb = mx.pose.bones["mixamorig:Hips"]
for f in frames:
    sc.frame_set(f)
    R = (mx.matrix_world.to_3x3() @ pb.matrix.to_3x3() @ hb.matrix_local.to_3x3().inverted() @ mx.matrix_world.to_3x3().inverted())
    fwd = R @ Vector((0, -1, 0)); fwd.z = 0; fwd.normalize(); left = Vector((-fwd.y, fwd.x, 0))  # figure's left
    hip = mx.matrix_world @ pb.head
    for tag, d in (("front", -fwd), ("q", (-fwd - left * 0.6).normalized())):
        cam.location = Vector((hip.x, hip.y, 0.5)) - d * 3; cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out, f"{tag}_f{f:04d}.png"); bpy.ops.render.render(write_still=True)
print("@@CLIPSTILLS@@", out, frames, flush=True)
