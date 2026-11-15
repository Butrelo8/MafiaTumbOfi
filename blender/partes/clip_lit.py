# clip_lit.py: the delivery-look twin of visual-lab's wham-video-mocap/render.py side view. Same camera (ortho 1.4 from
# the figure's right, following the torso, 480x640), same floor grid and frames, but EEVEE with closeups.py's one sun +
# grey world and the MTO satin finish on every part/cover material (roughness 0.42, metallic 0, coat 0.2 / 0.15; the
# base colour and its texture stay; TRELLIS's own roughness/metal maps are unlinked).
#   $B -b <parts.blend> --python clip_lit.py -- <frames dir (Windows)> [samples, default 64]
# Env RENDER_FRAMES=1,70: only those frames (WSLENV passes it to Windows Blender).
import bpy, sys, math, os
a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]; samples = int(a[1]) if len(a) > 1 else 64
sc = bpy.context.scene; rig = bpy.data.objects["rig"]
sc.render.fps = 30
for m in bpy.data.materials:
    if not m.use_nodes: continue
    for p in [n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"]:
        for s in ("Roughness", "Metallic"):
            for l in list(p.inputs[s].links): m.node_tree.links.remove(l)
        p.inputs["Roughness"].default_value = 0.42; p.inputs["Metallic"].default_value = 0.0
        p.inputs["Coat Weight"].default_value = 0.2; p.inputs["Coat Roughness"].default_value = 0.15
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam
floor = bpy.data.objects.new("Floor", bpy.data.meshes.new("Floor")); sc.collection.objects.link(floor)
import bmesh
b = bmesh.new(); bmesh.ops.create_grid(b, x_segments=20, y_segments=20, size=5); b.to_mesh(floor.data); b.free()
eng = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in eng else "BLENDER_EEVEE"
sc.eevee.taa_render_samples = samples
sun = bpy.data.objects.new("S", bpy.data.lights.new("S", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.6, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
sc.view_settings.view_transform = "Standard"; sc.render.use_compositing = False
sc.render.image_settings.file_format = "PNG"
cam.data.type = "ORTHO"; cam.data.ortho_scale = 1.4
cam.rotation_euler = (math.radians(90), 0, math.radians(90))
for f in range(sc.frame_start, sc.frame_end + 1):
    sc.frame_set(f)
    t = rig.matrix_world @ rig.pose.bones["torso"].head
    cam.location = (4.0, t.y, 0.5); cam.keyframe_insert("location", frame=f)
sc.render.resolution_x, sc.render.resolution_y = 480, 640; sc.render.resolution_percentage = 100
if os.environ.get("RENDER_FRAMES"):
    for f in map(int, os.environ["RENDER_FRAMES"].split(",")):
        sc.frame_set(f); sc.render.filepath = out + f"\\{f:04d}"; bpy.ops.render.render(write_still=True)
    sys.exit(0)
sc.render.filepath = out + "\\####"
bpy.ops.render.render(animation=True)
print("RENDERED", sc.frame_start, sc.frame_end)
