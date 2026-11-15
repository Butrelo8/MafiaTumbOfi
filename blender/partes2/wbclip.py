# wbclip.py -- <frames dir> [f0-f1]: colddrone's clip_wb.py settings (visual-lab render.py "side": ortho 1.4, 480 x 640,
# from the figure's right, studio light, texture colour, cavity, grid floor, camera following mixamorig:Hips) for the
# parts Diego, whose visible meshes are several objects (skin with its Mask, shirt, pants, shoes, hair, lids) where
# clip_wb.py renders only "Body". Same numbers, so its crawl compares with today's clips.
import bpy, sys, math, bmesh
a = sys.argv[sys.argv.index("--") + 1:]; out = a[0]
sc = bpy.context.scene; mx = bpy.data.objects["mx"]
if len(a) > 1: sc.frame_start, sc.frame_end = map(int, a[1].split("-"))
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name == "proxy"
sc.render.fps = 30
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam
floor = bpy.data.objects.new("Floor", bpy.data.meshes.new("Floor")); sc.collection.objects.link(floor)
b = bmesh.new(); bmesh.ops.create_grid(b, x_segments=20, y_segments=20, size=5); b.to_mesh(floor.data); b.free()
sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"
sc.display.shading.show_cavity = True; sc.view_settings.view_transform = "Standard"; sc.render.image_settings.file_format = "PNG"
sc.render.resolution_x, sc.render.resolution_y = 480, 640
cam.data.type = "ORTHO"; cam.data.ortho_scale = 1.4; cam.rotation_euler = (math.radians(90), 0, math.radians(90))
for f in range(sc.frame_start, sc.frame_end + 1):
    sc.frame_set(f); t = mx.matrix_world @ mx.pose.bones["mixamorig:Hips"].head
    cam.location = (4.0, t.y, 0.5); cam.keyframe_insert("location", frame=f)
sc.render.filepath = out.rstrip("\\/") + "/"
bpy.ops.render.render(animation=True)
