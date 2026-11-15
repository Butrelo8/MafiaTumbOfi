# seam_view.py -- <skin blend open> <fit dir> <out prefix>: Workbench close-ups of the three seams of the assembled skin
# at rest (wrists from above and from the front, 9 cm frame; neck from the front and the back, 16 cm frame), one flat
# colour so only the shape reads. Used to compare assemble.py variants on the same cameras.
import bpy, sys, os, json, math
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
fit, pre = a[0], a[1]; H = json.load(open(os.path.join(fit, "hand.json")))
sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"
sh.color_type = "SINGLE"; sh.single_color = (0.8, 0.62, 0.52); sc.render.resolution_x = sc.render.resolution_y = 500
sc.view_settings.view_transform = "Standard"
cam = bpy.data.objects.new("cam_s", bpy.data.cameras.new("cam_s")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.clip_end = 20
skin = next(o for o in sc.objects if o.name == "Diego")
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o is not skin
neck = Vector((0, 0, 0.598))
views = [(f"wrist{s[0].upper()}_{n}", Vector(H[s]["wrist"]), d, 0.09) for s in ("right", "left")
         for n, d in (("top", Vector((0, 0, 1))), ("front", Vector((0, -1, 0))))]
views += [("neck_front", neck, Vector((0, -1, 0)), 0.16), ("neck_back", neck, Vector((0, 1, 0)), 0.16)]
for name, c, d, size in views:
    cam.location = c + d * 3; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler(); cam.data.ortho_scale = size
    sc.render.filepath = f"{pre}_{name}.png"; bpy.ops.render.render(write_still=True)
print("@@ seams", pre)
