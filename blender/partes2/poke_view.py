# poke_view.py -- <clip.blend open> <out prefix> <frame> <size m> obj:vert ...: Workbench close-ups of pokethrough.py's
# worst vertices at one frame. Each vertex gets a red 3 mm marker; the camera centres on the first one. Views: front,
# side (from +x or -x, whichever faces the point), and front again with the shirt and pants hidden (what is behind).
import bpy, sys, math
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
pre, f, size = a[0], int(a[1]), float(a[2]); marks = [x.split(":") for x in a[3:]]
mk = bpy.data.objects["Diego"].modifiers["Mask"]; mk.show_viewport = False      # vertex indices = pokethrough's
sc = bpy.context.scene; sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
pts = []
for o, i in marks:
    e = bpy.data.objects[o].evaluated_get(dg); pts.append(bpy.data.objects[o].matrix_world @ e.data.vertices[int(i)].co)
mk.show_viewport = mk.show_render = True
for p in pts: bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0015, location=p)
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"
sc.render.resolution_x = sc.render.resolution_y = 600; sc.view_settings.view_transform = "Standard"
sh.color_type = "OBJECT"
for o in sc.objects:
    if o.type == "MESH": o.color = {"Diego": (0.85, 0.65, 0.5, 1), "shirt": (0.3, 0.45, 0.8, 1), "pants": (0.25, 0.25, 0.3, 1)}.get(o.name, (0.6, 0.6, 0.6, 1))
    if o.name.startswith("Sphere"): o.color = (1, 0, 0, 1)
cam = bpy.data.objects.new("cam_p", bpy.data.cameras.new("cam_p")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = size; cam.data.clip_end = 20
c = pts[0]
side = Vector((1 if c.x > 0 else -1, 0, 0))
for name, d, hide in (("front", Vector((0, -1, 0)), False), ("side", side, False), ("front_nocloth", Vector((0, -1, 0)), True)):
    for n in ("shirt", "pants"): bpy.data.objects[n].hide_render = hide
    cam.location = c + d * 3; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = f"{pre}_f{f:04d}_{name}.png"; bpy.ops.render.render(write_still=True)
print("@@ view", f, [tuple(round(x, 4) for x in p) for p in pts])
