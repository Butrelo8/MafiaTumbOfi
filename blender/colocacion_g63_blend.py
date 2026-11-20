"""Placement hand-off for the new G63 (owner rule 2026-11-15: drones stop at placement). Builds one locked .blend with the new car, its rack
and load, the dressing and the four cast members at a best-guess placement (the old placement shifted down 0.28 m, blender/props/
g63_paradas.json `cast`), where only the four `posicion_<nombre>` empties can be selected. A LEEME in Spanish sits in the Scripting
tab and under each camera; the cameras are the Cabina stop and the four stop-4 shots (the same names the old file used).

  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b <vivo-g63.blend> --python-exit-code 1 --python blender/colocacion_g63_blend.py \
    -- <out .blend (Windows)> <public/vivo/reparto.glb (Windows)> <public/vivo/escena.glb (Windows): Héctor's bottle comes from it>

After he saves: blender/vivo_reparto_volcar.py on his file (rigs `<nombre>_v5_rig`, pose bones, the bottle trees) -> VIVO_POSE for the
old exporter -> scripts/vivo-g63.sh (header). Nothing here is the final cast.
"""
import bpy, json, os, sys
from mathutils import Matrix, Vector

SAL, REPARTO, ESCENA = sys.argv[sys.argv.index("--") + 1:][:3]
AQUI = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(AQUI, "props", "g63_paradas.json"), encoding="utf8"))
O = bpy.data.objects
sc = bpy.context.scene
NOMBRES = ("manager", "hector", "alejandro", "diego")

LEEME = """COLOCACIÓN DEL REPARTO EN EL G63 NUEVO

Solo las cuatro cruces «posicion_manager / hector / alejandro / diego» se pueden seleccionar; todo lo demás está bloqueado.
Cada cruz mueve a su personaje entero (con su botella, en el caso de Héctor).

1. Haz clic en una cruz, o en su nombre en el Outliner (arriba a la derecha).
2. G mueve, R gira (Z para girar sobre el piso), S no lo toques (cambia el tamaño). Puedes teclear un número después
   (por ejemplo G, Z, -0.05, Enter). Clic derecho o Esc cancela.
3. Las cámaras están marcadas en la línea de tiempo (abajo): la primera es «Cabina» (parada 1) y las otras cuatro son las tomas
   de la banda. Numpad 0 vuelve a la vista de la cámara. Revisa que nadie atraviese el techo, el asiento ni la puerta.
4. Ctrl+S guarda en este mismo archivo. Avísale a Claude o a la nave nodriza: «leer reparto de <ruta de tu archivo>».

Punto de partida (mi mejor suposición): la colocación vieja bajada 0.28 m para que las cabezas (con gorra) queden bajo el techo.
"""


def contar(objs):
    return sum(len(o.data.polygons) for o in objs if o.type == "MESH")


# ---------------------------------------------------------------- the cast, as the live page has it
antes = set(O)
bpy.ops.import_scene.gltf(filepath=REPARTO)
nuevos = [o for o in O if o not in antes]
rigs = {n: next(o for o in nuevos if o.name.split(".")[0] == f"{n}_v5_rig") for n in NOMBRES}
raiz_glb = next((o for o in nuevos if o.type == "EMPTY" and o.name.split(".")[0] == "camion"), None)
bpy.context.view_layer.update()
pos = {}
for n, r in rigs.items():
    e = bpy.data.objects.new(f"posicion_{n}", None)
    sc.collection.objects.link(e)
    e.empty_display_type, e.empty_display_size = "PLAIN_AXES", 0.35
    e.location = (r.matrix_world.translation.x, r.matrix_world.translation.y, 0.0)
    bpy.context.view_layer.update()
    mw = r.matrix_world.copy()
    r.parent = e
    r.matrix_parent_inverse = e.matrix_world.inverted()
    r.matrix_world = mw
    pos[n] = e
    for c in r.children:  # the skin meshes keep following the rig
        pass
# the glb's own `camion` empty carried the rigs: it stays as an empty root (the car's `camion` is the real one)
if raiz_glb:
    raiz_glb.name = "reparto_raiz"
    raiz_glb.hide_select = True

# ---------------------------------------------------------------- Héctor's bottle from the live scene
antes = set(O)
bpy.ops.import_scene.gltf(filepath=ESCENA)
todo = [o for o in O if o not in antes]
botella = [o for o in todo if o.name.startswith("k5_bebida_mano")]
mantener = set()
for b in botella:
    mantener.update([b, *b.children_recursive])
for o in todo:
    if o not in mantener:
        O.remove(o, do_unlink=True)
bpy.context.view_layer.update()
for b in [o for o in mantener if o.parent is None or o.parent not in mantener]:
    mw = b.matrix_world.copy()
    b.parent = pos["hector"]
    b.matrix_parent_inverse = pos["hector"].matrix_world.inverted()
    b.matrix_world = mw
print("COLOCACION botella", sorted(o.name for o in mantener)[:6], flush=True)

# ---------------------------------------------------------------- cameras: Cabina and the four stop-4 shots
def camara(nombre, toma_):
    cd = bpy.data.cameras.new(nombre)
    cd.lens, cd.clip_start, cd.clip_end, cd.sensor_fit = toma_["lens"], 0.01, 3000, "HORIZONTAL"
    c = bpy.data.objects.new(nombre, cd)
    sc.collection.objects.link(c)
    c.location = Vector(toma_["pos"])
    c.rotation_euler = (Vector(toma_["mira"]) - Vector(toma_["pos"])).to_track_quat("-Z", "Y").to_euler()
    return c


camaras = [camara("cam_cabina", P["camaras"][0])]
for n, t in zip(NOMBRES, P["banda"]):  # banda order in vivo.json: manager, Héctor, Alejandro, Diego
    camaras.append(camara(f"cam_{n}_asiento", t))

# ---------------------------------------------------------------- lock everything but the four crosses, LEEME, save
sueltos = list(pos.values())
for o in O:
    o.hide_select = o not in sueltos
    o.select_set(False)
for o in sueltos:
    o.select_set(True)
sc.camera = camaras[0]
sc.timeline_markers.clear()
for i, c in enumerate(camaras):
    sc.timeline_markers.new(c.name, frame=i).camera = c
sc.frame_set(0)
sc.frame_start, sc.frame_end = 0, len(camaras) - 1
t = bpy.data.texts.get("LEEME") or bpy.data.texts.new("LEEME")
t.clear()
t.write(LEEME)
for scr in bpy.data.screens:
    for a in scr.areas:
        if a.type == "VIEW_3D":
            a.spaces[0].region_3d.view_perspective = "CAMERA"
            a.spaces[0].shading.type, a.spaces[0].shading.color_type = "SOLID", "TEXTURE"
        elif a.type == "TEXT_EDITOR":
            a.spaces[0].text = t
for c in camaras:  # a line along the bottom of each camera view
    hw = 18 / c.data.lens
    cu = bpy.data.curves.new("leeme_" + c.name, "FONT")
    cu.body = "LEEME: pestaña Scripting, arriba.  G mover · R girar · Ctrl+S guardar"
    cu.size, cu.align_x = hw * 0.045, "CENTER"
    tx = bpy.data.objects.new("leeme_" + c.name, cu)
    sc.collection.objects.link(tx)
    tx.parent, tx.location, tx.hide_render, tx.hide_select = c, (0, -hw * 9 / 16 * 0.88, -1.0), True, True
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=SAL, copy=True)
print("COLOCACION guardado", SAL, [o.name for o in sueltos], flush=True)
