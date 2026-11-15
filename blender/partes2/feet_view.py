# feet_view.py -- <out prefix> [fbx]: Workbench close-ups of the feet and pant hems at rest (front, side, 3/4; 36 cm
# frame centred at z 0.12), texture colour, on the open blend or on a Mixamo FBX imported into an empty scene.
import bpy, sys, math
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
pre = a[0]; fbx = a[1] if len(a) > 1 else None
if fbx:
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=fbx)
sc = bpy.context.scene
for o in sc.objects:
    if o.type == "ARMATURE": o.data.pose_position = "REST"
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "TEXTURE"
sc.render.resolution_x = sc.render.resolution_y = 500; sc.view_settings.view_transform = "Standard"
sc.world = sc.world or bpy.data.worlds.new("w")
cam = bpy.data.objects.new("cam_f", bpy.data.cameras.new("cam_f")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = 0.36; cam.data.clip_end = 20
c = Vector((0, 0, 0.12))
for name, az in (("front", 0), ("q", 35), ("side", 90)):
    d = Vector((math.sin(math.radians(az)), -math.cos(math.radians(az)), 0))
    cam.location = c + d * 5; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = f"{pre}_{name}.png"; bpy.ops.render.render(write_still=True)
print("@@ feet", pre)
