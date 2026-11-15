# view.py -- <out prefix> <res> <views> <glb[@fit.json]> ...: Workbench (texture colour, studio light) renders of GLBs,
# each placed by its fit.json "T" when given (FRAME=x,y,z,size env fixes the framing). views: comma list of front,side,q (three-quarter),back,top, or
# zoom:<x>,<y>,<z>,<size>,<az> for an orthographic close-up centred on a point. One PNG per view.
import bpy, sys, json, math
from mathutils import Matrix, Vector
a = sys.argv[sys.argv.index("--") + 1:]
pre, res, views, items = a[0], int(a[1]), a[2], a[3:]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
objs = []
for it in items:
    glb, _, fj = it.partition("@")
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glb)
    new = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    T = Matrix(json.load(open(fj))["T"]) if fj else Matrix.Identity(4)
    for o in new:
        o.matrix_world = T @ o.matrix_world; objs.append(o)
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "TEXTURE"; sh.show_cavity = False
sc.render.resolution_x = sc.render.resolution_y = res
sc.render.film_transparent = False; sc.world = bpy.data.worlds.new("w") if not sc.world else sc.world
sc.view_settings.view_transform = "Standard"
lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
for o in objs:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c); lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
ctr = (lo + hi) / 2; size = max(hi - lo) * 1.08
import os
if os.environ.get("FRAME"):  # fixed framing "x,y,z,size" so separate renders line up
    *c3, size = map(float, os.environ["FRAME"].split(",")); ctr = Vector(c3)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"
AZ = {"front": 0, "q": 35, "side": 90, "back": 180}
for v in views.split(";"):
    c, s, el = ctr, size, 0.0
    if v.startswith("zoom:"):
        x, y, z, s, az = map(float, v[5:].split(",")); c = Vector((x, y, z)); name = "zoom_%g_%g_%g" % (x, y, z)
    elif v == "top":
        az, el, name = 0, 89.9, v
    else:
        az, name = AZ[v], v
    az, el = math.radians(az), math.radians(el)
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cam.location = c + d * 5; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = s; cam.data.clip_end = 20
    sc.render.filepath = f"{pre}_{name}.png"; bpy.ops.render.render(write_still=True)
    print("@@", sc.render.filepath)
