# mouth_mark.py: find the mouth as a Body vertex. Renders a front ortho close-up of the head at a frame (clip_stills.py's
# light) with a 10 px grid; given a pixel, casts the camera ray into the evaluated mesh and prints the nearest vertex index.
#   $B -b <blend> --python mouth_mark.py -- <out.png (Windows)> <frame> [px,py]
import bpy, sys, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]; out, f = a[0], int(a[1])
sc = bpy.context.scene; mx = bpy.data.objects["mx"]; body = bpy.data.objects["Body"]; sc.frame_set(f)
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name != "Body"
hb = mx.data.bones["mixamorig:Hips"]; pb = mx.pose.bones["mixamorig:Hips"]
R = mx.matrix_world.to_3x3() @ pb.matrix.to_3x3() @ hb.matrix_local.to_3x3().inverted() @ mx.matrix_world.to_3x3().inverted()
fwd = R @ Vector((0, -1, 0)); fwd.z = 0; fwd.normalize()
head = mx.matrix_world @ mx.pose.bones["mixamorig:Head"].head; c = head + Vector((0, 0, 0.12))
S, RES = 0.36, 720
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = S; d = -fwd
cam.location = c - d * 3; cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
sc.render.resolution_x = sc.render.resolution_y = RES; sc.render.resolution_percentage = 100
if len(a) > 2:
    px, py = map(float, a[2].split(",")); M = cam.matrix_world.to_3x3()
    o = cam.location + M @ Vector(((px / RES - 0.5) * S, (0.5 - py / RES) * S, 0))
    dg = bpy.context.evaluated_depsgraph_get(); ev = body.evaluated_get(dg); m = ev.to_mesh()
    V = [body.matrix_world @ v.co for v in m.vertices]; tree = BVHTree.FromPolygons(V, [list(p.vertices) for p in m.polygons])
    loc, nrm, fi, dist = tree.ray_cast(o, d); vi = min(m.polygons[fi].vertices, key=lambda i: (V[i] - loc).length)
    print("@@MOUTH@@", dict(vertex=vi, loc=[round(x, 4) for x in loc], normal=[round(x, 3) for x in nrm]), flush=True); sys.exit(0)
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
sun = bpy.data.objects.new("S", bpy.data.lights.new("S", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.6, 1)
sc.view_settings.view_transform = "Standard"; sc.render.use_compositing = False
sc.render.filepath = out; bpy.ops.render.render(write_still=True)
print("@@MOUTHPNG@@", out, flush=True)
