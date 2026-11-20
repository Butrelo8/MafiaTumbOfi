"""Paints cabina_choques.py's flagged faces and renders them (Workbench, fast) from its cameras: magenta = flotan, yellow =
atraviesan, cyan = dentro, orange = asoman; the new parts pale green, the rest of the cab grey by material. Read only.

  GPU=0 ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b <vivo-montado.blend> --python-exit-code 1 \
    --python "$(wslpath -w blender/cabina_choques_ver.py)" -- <vivo.json> <choques.json> <out_dir> [sin_nuevas] [borrar] [diezmar=r [soldar] [despues|ambos] [mas=obj:w,...]]
"""
import bpy, json, os, sys
from mathutils import Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import cabina_choques as CC
import cabina_tripo as CT

a = sys.argv[sys.argv.index("--") + 1:]
JS, CH, OUT = a[0], a[1], a[2]
SIN = "sin_nuevas" in a[3:]
if os.environ.get("VIVO_POSE"):  # the console as the exporter ships it: the owner's matrix (vivo_secciones_exportar.poner_pose)
    from mathutils import Matrix
    bpy.data.objects["tripo_consola"].matrix_world = Matrix(json.load(open(os.environ["VIVO_POSE"], encoding="utf8"))["objetos"]["tripo_consola"]["mundo"])
    bpy.context.view_layer.update()
if "borrar" in a[3:]:
    CT.borrar_viejos(bpy.data.objects["camion"], [o for o in CC.nuevas() if o.name.startswith("tripo_")])
for x in a[3:]:
    if x.startswith("diezmar="):
        CC.diezmar(float(x.split("=")[1]), "soldar" in a[3:], CC.pesos(a[3:]), "ambos" if "ambos" in a[3:] else "despues" in a[3:])
        dg = bpy.context.evaluated_depsgraph_get()
        for o in [o for o in bpy.data.objects if o.type == "MESH" and "dec" in o.modifiers]:  # bake it: the face indices are the evaluated ones
            me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
            o.modifiers.clear()
            o.data = me
os.makedirs(OUT, exist_ok=True)
ch = json.load(open(CH, encoding="utf8"))
COL = {"flotan": (1, 0, 1, 1), "atraviesan": (1, 0.9, 0, 1), "dentro": (0, 0.9, 1, 1), "asoman": (1, 0.45, 0, 1)}
O = bpy.data.objects
for k, col in COL.items():
    m = bpy.data.materials.new("marca_" + k)
    m.diffuse_color = col
    por_obj = {}
    for nom, cara in ch["caras"].get(k, []):
        por_obj.setdefault(nom, []).append(cara)
    for nom, caras in por_obj.items():
        me = O[nom].data
        me.materials.append(m)
        i = len(me.materials) - 1
        for c in caras:
            if c < len(me.polygons):
                me.polygons[c].material_index = i
for m in bpy.data.materials:
    if not m.name.startswith("marca_"):
        m.diffuse_color = (0.25, 0.25, 0.27, 1) if not m.name.startswith(("tripo_asiento", "tripo_consola", "tripo_material_f4b")) else (0.55, 0.85, 0.55, 1)
for o in CC.nuevas(ocultas=True):
    o.hide_render = SIN
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"
sc.display.shading.color_type = "MATERIAL"
sc.display.shading.show_cavity = False
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 960, 600, 100
sc.render.film_transparent = False
cd = bpy.data.cameras.new("ver")
cam = bpy.data.objects.new("ver", cd)
sc.collection.objects.link(cam)
sc.camera = cam
cd.sensor_fit, cd.sensor_width = "HORIZONTAL", 36.0
dentro, fuera = CC.camaras(JS)
SOLO = os.environ.get("VER_VISTAS", "").split(",") if os.environ.get("VER_VISTAS") else None
SUF = os.environ.get("VER_SUFIJO", "")
for vista, (pos, mira, lens) in {**dentro, **fuera}.items():
    if SOLO and vista not in SOLO:
        continue
    cam.location = Vector(pos)
    cam.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    cd.lens, cd.clip_start = lens, 0.02
    sc.render.filepath = os.path.join(OUT, vista + ("-sin" if SIN else "") + SUF + ".png")
    bpy.ops.render.render(write_still=True)
    print("VER", sc.render.filepath, flush=True)
