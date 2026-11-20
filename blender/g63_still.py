"""Workbench still of a placement file (geometry, not look): the Cabina camera or an ad-hoc one, for comparing two files frame by frame.
Empties (the controls) do not render, so a file with controls and one without give the same picture when nothing moved.

  blender-run blender.exe -b <file.blend> --python-exit-code 1 --python blender/g63_still.py -- <out.png (Windows)> [cam=<nombre>] [w=960] [h=540] \
      [desde=x,y,z hasta=x,y,z lente=mm] [ocultar=<prefijo>,...] [resaltar=<prefijo>,...] [soloreparto=1]
"""
import bpy, sys
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
out, kv = a[0], dict(t.split("=", 1) for t in a[1:])
O = bpy.data.objects
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = int(kv.get("w", 960)), int(kv.get("h", 540)), 100
sc.display.shading.light, sc.display.shading.color_type = "STUDIO", "MATERIAL"
sc.display.shading.show_cavity = False
sc.render.film_transparent = False
sc.render.image_settings.file_format = "PNG"
for m in sc.timeline_markers:  # the markers switch the scene camera on every frame change and at render time
    m.camera = None
sc.frame_set(0)
if "desde" in kv:
    cd = bpy.data.cameras.new("cam_prueba")
    cd.lens, cd.clip_start, cd.clip_end = float(kv.get("lente", 24)), 0.01, 3000
    c = bpy.data.objects.new("cam_prueba", cd)
    sc.collection.objects.link(c)
    p, m = (Vector(float(v) for v in kv[k].split(",")) for k in ("desde", "hasta"))
    c.location = p
    c.rotation_euler = (m - p).to_track_quat("-Z", "Y").to_euler()
    sc.camera = c
else:
    sc.camera = O[kv.get("cam", "cam_cabina")]
if kv.get("soloreparto"):  # only the four skins (<nombre>_v5) and Héctor's bottle: for close-ups of hands inside the cab
    for o in O:
        if o.type == "MESH" and not (o.name.split(".")[0].endswith("_v5") or o.name.startswith("k5_bebida") or (o.parent and o.parent.name.startswith("k5_bebida"))):
            o.hide_render = True
for pref in filter(None, kv.get("resaltar", "").split(",")):  # flat colour for the named objects (Workbench shows the material's viewport colour)
    for o in O:
        if o.name.startswith(pref) and o.type == "MESH":
            for sl in o.material_slots:
                sl.material.diffuse_color = (1.0, 0.25, 0.0, 1.0)
for pref in filter(None, kv.get("ocultar", "").split(",")):
    for o in O:
        if o.name.startswith(pref):
            o.hide_render = True
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("STILL", out, sc.camera.name, tuple(round(v, 3) for v in sc.camera.matrix_world.translation), flush=True)
