# rerig_stills.py: lit full-body stills of a skinned rig blend (rig_trellis.sh's <clip>_trellis.blend: Body on "rig"), with
# closeups.py's light, world and fixed full-body framing, so stills of different rigs line up tile for tile.
#   $B -b <clip_trellis.blend> --python rerig_stills.py -- <out dir (Windows)> <frame,frame,...>
# Writes <out>/front_f<frame>.png (front) and <out>/q_f<frame>.png (front three-quarter from the figure's left), 768 px.
import bpy, sys, math, os
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
out, frames = a[0], [int(f) for f in a[1].split(",")]
sc = bpy.context.scene
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name != "Body"
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sun = bpy.data.objects.new("S", bpy.data.lights.new("S", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.6, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
sc.view_settings.view_transform = "Standard"; sc.render.film_transparent = False; sc.render.use_compositing = False
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.clip_end = 100; cam.data.ortho_scale = 1.3
sc.render.resolution_x = sc.render.resolution_y = 768; sc.render.resolution_percentage = 100
for f in frames:
    sc.frame_set(f)
    rig = bpy.data.objects["rig"]; hip = rig.matrix_world @ rig.pose.bones["DEF-spine"].head  # follow the dance's root
    for tag, d in (("front", (0, 1, 0)), ("q", (-0.6, 1, 0))):
        d = Vector(d).normalized(); cam.location = Vector((hip.x, hip.y, 0.55)) - d * 3; cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out, f"{tag}_f{f}.png"); bpy.ops.render.render(write_still=True)
print("@@STILLS@@", out, frames)
