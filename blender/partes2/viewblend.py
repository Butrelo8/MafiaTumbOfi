# viewblend.py -- <out prefix> <res> <views> [object names]: view.py's views on objects already in a blend
# (default: every mesh). FRAME=x,y,z,size env fixes the framing, as in view.py.
import bpy, sys, os, math
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
pre, res, views = a[0], int(a[1]), a[2]; names = a[3:]
sc = bpy.context.scene
objs = [o for o in sc.objects if o.type == "MESH" and (not names or o.name in names)]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o not in objs
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "TEXTURE"
sc.render.resolution_x = sc.render.resolution_y = res; sc.view_settings.view_transform = "Standard"
sc.world = sc.world or bpy.data.worlds.new("w")
lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
for o in objs:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c); lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
ctr = (lo + hi) / 2; size = max(hi - lo) * 1.08
if os.environ.get("FRAME"):
    *c3, size = map(float, os.environ["FRAME"].split(",")); ctr = Vector(c3)
cam = bpy.data.objects.new("cam_v", bpy.data.cameras.new("cam_v")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"
AZ = {"front": 0, "q": 35, "side": 90, "back": 180, "qb": -145}
for v in views.split(";"):
    c, s, el = ctr, size, 0.0
    if v.startswith("zoom:"):
        x, y, z, s, az, *e = map(float, v[5:].split(",")); c = Vector((x, y, z)); el = e[0] if e else 0.0
        name = "zoom_%g_%g_%g_%g" % (x, y, z, az)
    elif v == "top": az, el, name = 0, 89.9, v
    elif v == "under": az, el, name = 0, -60, v
    else: az, name = AZ[v], v
    az, el = math.radians(az), math.radians(el)
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cam.location = c + d * 5; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = s; cam.data.clip_end = 20
    sc.render.filepath = f"{pre}_{name}.png"; bpy.ops.render.render(write_still=True); print("@@", sc.render.filepath)
