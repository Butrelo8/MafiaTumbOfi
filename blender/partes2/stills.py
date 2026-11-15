# stills.py -- <out dir> <frames f,f,...> [fbx] [hand side]: Workbench stills (studio light, texture colour, 500 px) on an
# open blend, or on a Mixamo FBX imported into an empty scene (today's Diego: the clip FBX downloaded With Skin is his
# own mesh and Mixamo skin). Per frame: front and three-quarter, framed on the visible meshes' posed bounds; with a
# hand side (Left|Right), also a close-up following mixamorig:<side>Hand (14 cm frame, from outside the body, a little in front) and
# the face (mixamorig:Head, 42 cm frame, front and three-quarter).
import bpy, sys, os, math
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index("--") + 1:]
out, frames = a[0], [int(x) for x in a[1].split(",")]; fbx = a[2] if len(a) > 2 and a[2] != "-" else None
hand = a[3] if len(a) > 3 else None
if fbx:
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=fbx)
sc = bpy.context.scene; os.makedirs(out, exist_ok=True)
arm = next(o for o in sc.objects if o.type == "ARMATURE")
if fbx and arm.animation_data and arm.animation_data.action:
    act = arm.animation_data.action; sc.frame_start, sc.frame_end = (int(x) for x in act.frame_range)
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "TEXTURE"
sc.render.resolution_x = sc.render.resolution_y = 500; sc.world = sc.world or bpy.data.worlds.new("w")
sc.view_settings.view_transform = "Standard"
cam = bpy.data.objects.new("cam_s", bpy.data.cameras.new("cam_s")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.clip_end = 20
vis = [o for o in sc.objects if o.type == "MESH" and not o.hide_render and o.name != "proxy"]


def shoot(path, c, d, size):
    cam.location = c + d * 5; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler(); cam.data.ortho_scale = size
    sc.render.filepath = path; bpy.ops.render.render(write_still=True)


for f in frames:
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
    lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
    for o in vis:
        for c in o.evaluated_get(dg).bound_box:
            w = o.matrix_world @ Vector(c); lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    ctr = (lo + hi) / 2
    for name, az in (("front", 0), ("q", 35)):
        shoot(os.path.join(out, f"f{f:04d}_{name}.png"), ctr, Vector((math.sin(math.radians(az)), -math.cos(math.radians(az)), 0)), max(hi - lo) * 1.1)
    if hand:
        M = arm.matrix_world @ arm.pose.bones[f"mixamorig:{hand}Hand"].matrix
        c = M @ Vector((0, 0.06 / arm.matrix_world.to_scale()[0], 0))
        hips = arm.matrix_world @ arm.pose.bones["mixamorig:Hips"].head; side = c - hips; side.z = 0   # from outside the body
        side = (side.normalized() + Vector((0, -0.6, 0))).normalized()
        shoot(os.path.join(out, f"f{f:04d}_hand.png"), c, side, 0.14)
        H = arm.matrix_world @ arm.pose.bones["mixamorig:Head"].matrix          # face: 25 cm frame, front and 3/4
        c = H @ Vector((0, 0.15 / arm.matrix_world.to_scale()[0], 0)); fwd = (H.to_3x3() @ Vector((0, 0, 1))).normalized()
        for name, az in (("face", 0), ("face_q", 35)):
            d = Matrix.Rotation(math.radians(az), 3, "Z") @ fwd; shoot(os.path.join(out, f"f{f:04d}_{name}.png"), c, d, 0.42)
print("@@ stills", len(frames), "frames", "fbx" if fbx else "blend", out)
