# clip_wb.py: render.py's Workbench "side" clip (visual-lab wham-video-mocap/render.py: ortho 1.4, 480x640, from the
# figure's right, studio light, texture colour, cavity, grid floor) for a blend on Mixamo's armature "mx", following
# mixamorig:Hips instead of Rigify's torso. Only Body and prop_* meshes render.
#   $B -b <blend> --python clip_wb.py -- <frames dir (Windows)> [f0-f1]
import bpy, sys, math, bmesh
a = sys.argv[sys.argv.index("--") + 1:]; out = a[0]
sc = bpy.context.scene; mx = bpy.data.objects["mx"]
if len(a) > 1: sc.frame_start, sc.frame_end = map(int, a[1].split("-"))
for o in sc.objects:
    if o.type == "MESH": o.hide_render = not (o.name == "Body" or o.name.startswith("prop_"))
sc.render.fps = 30
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam
floor = bpy.data.objects.new("Floor", bpy.data.meshes.new("Floor")); sc.collection.objects.link(floor)
b = bmesh.new(); bmesh.ops.create_grid(b, x_segments=20, y_segments=20, size=5); b.to_mesh(floor.data); b.free()
sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"
sc.display.shading.show_cavity = True; sc.view_settings.view_transform = "Standard"; sc.render.image_settings.file_format = "PNG"
cam.data.type = "ORTHO"; cam.data.ortho_scale = 1.4; cam.rotation_euler = (math.radians(90), 0, math.radians(90))
for f in range(sc.frame_start, sc.frame_end + 1):
    sc.frame_set(f); t = mx.matrix_world @ mx.pose.bones["mixamorig:Hips"].head
    cam.location = (4.0, t.y, 0.5); cam.keyframe_insert("location", frame=f)
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 480, 640, 100
sc.render.filepath = out + "\\####"; bpy.ops.render.render(animation=True)
print("RENDERED", sc.frame_start, sc.frame_end)
