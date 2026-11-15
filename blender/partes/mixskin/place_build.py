# place_build.py: a placement .blend for the owner to place one prop by hand (he places, the scripts check). From a props
# blend (props_build.py): the prop is re-parented to an empty "<prop>_hand" on the given bone, so his transform is the
# prop's matrix_basis in bone space (place_read.py reads it); every other object gets hide_select; a shot camera framed on
# the bone and the mouth at the key frame, the 3D views set to it; one EEVEE still of the current placement.
#   $B -b <props blend> --python place_build.py -- <prop> <bone> <frame> <out.blend (Windows)> <still.png (Windows)> [lens 50]
import bpy, sys, math
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; prop, bone, f, out, still = a[0], a[1], int(a[2]), a[3], a[4]; lens = float(a[5]) if len(a) > 5 else 50
sc = bpy.context.scene; mx = bpy.data.objects["mx"]; p = bpy.data.objects[prop]; pb = mx.pose.bones["mixamorig:" + bone]
sc.frame_set(f); bpy.context.view_layer.update(); mw = p.matrix_world.copy()
for c in list(p.constraints):  # the hand placement replaces them; an aim empty only they used goes too
    t = getattr(c, "target", None); p.constraints.remove(c)
    if t is not None and t.type == "EMPTY": bpy.data.objects.remove(t)
e = bpy.data.objects.new(prop + "_hand", None); sc.collection.objects.link(e); e.empty_display_size = 0.03
e.parent = mx; e.parent_type = "BONE"; e.parent_bone = pb.name; e.matrix_world = mx.matrix_world @ pb.matrix
bpy.context.view_layer.update(); p.parent = e; p.matrix_parent_inverse = Matrix.Identity(4); p.matrix_world = mw
for o in sc.objects: o.hide_select = o is not p
# camera: front three-quarter from the prop's side, aimed at the middle of the hand, the prop and the head
hb = mx.data.bones["mixamorig:Hips"]; hp = mx.pose.bones["mixamorig:Hips"]
R = mx.matrix_world.to_3x3() @ hp.matrix.to_3x3() @ hb.matrix_local.to_3x3().inverted() @ mx.matrix_world.to_3x3().inverted()
fwd = R @ Vector((0, -1, 0)); fwd.z = 0; fwd.normalize(); left = Vector((-fwd.y, fwd.x, 0)); side = -left if bone.startswith("Right") else left
pts = [mx.matrix_world @ mx.pose.bones["mixamorig:" + b].head for b in (bone, "HeadTop_End", "Spine1")] + [p.matrix_world @ Vector(c) for c in p.bound_box]
lo = Vector([min(v[i] for v in pts) for i in range(3)]); hi = Vector([max(v[i] for v in pts) for i in range(3)]); mid = (lo + hi) / 2
d = (-fwd - side * 0.7 + Vector((0, 0, -0.15))).normalized(); span = max((hi.z - lo.z) / 0.5625, (hi - lo).xy.length) * 1.3  # 16:9: fit the height
cam = bpy.data.objects.new("shot_cam", bpy.data.cameras.new("shot_cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = lens; cam.data.sensor_width = 36; cam.location = mid - d * (span * lens / 36); cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
cam.hide_select = True; sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
for s in (o for o in sc.objects if o.type == "MESH"): s.hide_render = not (s.name == "Body" or s.name.startswith("prop_"))
sun = bpy.data.objects.new("S", bpy.data.lights.new("S", "SUN")); sc.collection.objects.link(sun); sun.hide_select = True
sun.data.energy = 3.0; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.6, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
sc.view_settings.view_transform = "Standard"; sc.render.use_compositing = False
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [x.identifier for x in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
for scr in bpy.data.screens:
    for ar in scr.areas:
        if ar.type == "VIEW_3D":
            for sp in ar.spaces:
                if sp.type == "VIEW_3D": sp.region_3d.view_perspective = "CAMERA"; sp.shading.type = "MATERIAL"
for o in sc.objects: o.select_set(o is p)
bpy.context.view_layer.objects.active = p; sc.frame_set(f)
sc.render.filepath = still; bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=out)
print("@@PLACE@@", prop, "on", pb.name, "frame", f, "basis", [list(r) for r in p.matrix_basis], flush=True)
