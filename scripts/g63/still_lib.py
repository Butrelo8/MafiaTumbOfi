import bpy, os, math
from mathutils import Vector
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = int(os.environ.get("STILL_W", 1400)), int(os.environ.get("STILL_H", 900))
w = bpy.data.worlds.new("w") if not sc.world else sc.world
sc.world = w; w.use_nodes = True
noche = os.environ.get("STILL_LUZ", "dia") == "noche"
bg = w.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (0.02, 0.025, 0.04, 1) if noche else (0.35, 0.37, 0.42, 1); bg.inputs["Strength"].default_value = 1.0
for n, loc, e in (("key", (6, -3, 7), 2200), ("fill", (-3, 6, 4), 900), ("top", (1.72, 0.5, 6), 700)):
    d = bpy.data.lights.new(n, "AREA"); d.energy = e * (0.35 if noche else 1); d.size = 5
    o = bpy.data.objects.new(n, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((1.72, 0.5, 1.2)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
for m in bpy.data.materials:
    if m.name.startswith("web_vidrio"):
        m.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.15
        try: m.surface_render_method = "BLENDED"
        except Exception: pass
_cd = bpy.data.cameras.new("c"); _cam = bpy.data.objects.new("c", _cd); sc.collection.objects.link(_cam); sc.camera = _cam
_cd.sensor_fit, _cd.sensor_width, _cd.clip_start, _cd.clip_end = "HORIZONTAL", 36, 0.05, 200
def render(ruta, p, m, l):
    pos, mira = Vector(map(float, p.split(","))), Vector(map(float, m.split(",")))
    _cam.location = pos; _cd.lens = float(l)
    _cam.rotation_euler = (mira - pos).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = ruta; bpy.ops.render.render(write_still=True); print("STILL", ruta, flush=True)
