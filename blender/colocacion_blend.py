"""Placement hand-off (owner rule 2026-11-15: drones stop at placement). Builds montaje's scene 1 and scene 2 the way the build does,
then saves three locked .blend files where only one item's empties can be selected, with a LEEME in Spanish:

  colocar-pantalla.blend      the console screen (scene 1's camera)
  colocar-calcas.blend        the seven r1 stickers (scene 2's camera; frame 1 = scene 4B's, for the bed side)
  colocar-instrumentos.blend  the trio's instruments in the bed (scene 2's camera)

The owner moves them (G/R/S) and saves (Ctrl+S); blender/colocacion_leer.py reads the empties back into blender/props/colocacion.json.

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/colocacion_blend.py)" \
    -- "$(wslpath -w blender/escena.py)" <out_dir (Windows)> 1 - 960x540
"""
import bpy, math, os
from mathutils import Matrix

AQUI = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(AQUI, "montaje.py")
LAZO = "# ---------------------------------------------------------------- utileria.py's render loop"
exec(compile(open(M, encoding="utf8").read().rsplit(LAZO, 1)[0], M, "exec"), globals())

LEEME = """COLOCACIÓN: {que}

Solo {que} se puede seleccionar; todo lo demás está bloqueado.

1. Haz clic en la cruz de un objeto, o en su nombre en el Outliner (arriba a la derecha).
2. G mueve, R gira, S cambia el tamaño. Puedes teclear un número después (por ejemplo G, X, 0.05, Enter).
   Clic derecho o Esc cancela el movimiento.
3. Ctrl+S guarda en este mismo archivo. Cuando termines, avísale a Claude.

Numpad 0 vuelve a la vista de la cámara. {extra}
Cada objeto es una pieza tal cual se va a ver; el siguiente paso reconstruye la escena con tu colocación y la revisa.
"""
EXTRA = {
    "pantalla": "La pantalla va en el tablero central, arriba de la botella de la consola. Si la quieres en otro lado "
                "(por ejemplo flotando sobre el tablero), muévela ahí y lo anotamos.",
    "calcas": "Las calcas se deslizan sobre su cara (el portón o el costado derecho) y R las gira en ese plano. "
              "Al reconstruir, cada calca se vuelve a pegar a la lámina con su esquina levantada. "
              "Flecha derecha: la vista del costado (escena 4B); flecha izquierda: la del portón (escena 2). "
              "Si quieres pasar una calca del portón al costado, dilo y la cambiamos de cara.",
    "instrumentos": "El tololoche, el bajo sexto y el requinto están fuera de sus estuches, sobre la carga. "
                    "Acomódalos donde se verían bien desde la cámara de la escena 2; si alguno debe ir de pie, gíralo con R.",
}


def soltar(e):
    """Unparent, keeping the world transform: the read-back reads world values."""
    mw = e.matrix_world.copy()
    e.parent = None
    e.matrix_world = mw


def camara(nombre, toma_):
    pos, mira, lens = toma_
    cd = bpy.data.cameras.new(nombre)
    cd.lens, cd.clip_start, cd.clip_end, cd.sensor_fit = lens, 0.01, 3000, "HORIZONTAL"
    c = bpy.data.objects.new(nombre, cd)
    sc.collection.objects.link(c)
    c.location = Vector(pos)
    c.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    return c


def guardar(que, sueltos, camaras, ruta):
    for o in bpy.data.objects:
        o.hide_select = o not in sueltos
        o.select_set(False)
    for o in sueltos:
        o.select_set(True)
    sc.camera = camaras[0]
    sc.timeline_markers.clear()
    for i, c in enumerate(camaras):
        sc.timeline_markers.new(c.name, frame=i).camera = c
    sc.frame_set(0)
    t = bpy.data.texts.get("LEEME") or bpy.data.texts.new("LEEME")
    t.clear()
    t.write(LEEME.format(que={"pantalla": "la pantalla", "calcas": "las siete calcas", "instrumentos": "los tres instrumentos"}[que], extra=EXTRA[que]))
    for scr in bpy.data.screens:  # an area's type can't be switched without a window (-b), so the Scripting tab's editor shows it
        for a in scr.areas:
            if a.type == "VIEW_3D":
                a.spaces[0].region_3d.view_perspective = "CAMERA"
                a.spaces[0].shading.type, a.spaces[0].shading.color_type = "SOLID", "TEXTURE"
            elif a.type == "TEXT_EDITOR":
                a.spaces[0].text = t
    for c in [c for c in camaras if "leeme_" + c.name not in bpy.data.objects]:  # a line along the bottom of each camera view
        hw = 18 / c.data.lens
        cu = bpy.data.curves.new("leeme_" + c.name, "FONT")
        cu.body = "LEEME: pestaña Scripting, arriba.  G mover · R girar · S tamaño · Ctrl+S guardar"
        cu.size, cu.align_x = hw * 0.045, "CENTER"
        tx = bpy.data.objects.new("leeme_" + c.name, cu)
        sc.collection.objects.link(tx)
        tx.parent, tx.location, tx.hide_render, tx.hide_select = c, (0, -hw * 9 / 16 * 0.88, -1.0), True, True
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=ruta, copy=True)
    print("COLOCACION guardado", ruta, [o.name for o in sueltos], flush=True)


def limpiar():
    """Remove the objects the last option built (its GRUPO and their children)."""
    nombres = {c.name for o in GRUPO for c in [o] + list(o.children_recursive)}  # names first: a parent's removal drops nothing else
    for n in nombres:
        if n in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[n])
    GRUPO.clear()


# ---- scene 1: the screen
GRUPO.clear()
t1 = OPC["montaje-esc1"]()
pant = bpy.data.objects["pantalla_consola"]
soltar(pant)
pant.empty_display_type, pant.empty_display_size = "PLAIN_AXES", 0.12
guardar("pantalla", [pant], [camara("cam_esc1", t1)], os.path.join(OUT, "colocar-pantalla.blend"))
limpiar()

# ---- scene 2: the stickers and the instruments
t2 = OPC["montaje-esc2"]()
c2 = camara("cam_esc2", t2)
c4 = camara("cam_esc4", ((CX + 6.2, -0.3, 2.6), (CX, -0.3, 1.45), 24))  # esc4()'s wide hold (utileria.py), the passenger side
marcas = []
for o in [o for o in GRUPO if o.get("c3", "").startswith("r1-")]:
    c = COLOCA["calcas_r1"][o["c3"]]
    O, nrm, eul = cara3(c["cara"])
    e = bpy.data.objects.new("calca_" + o["c3"], None)
    sc.collection.objects.link(e)
    e.empty_display_type, e.empty_display_size = "PLAIN_AXES", max(o["w"], o["h"]) / 2
    e.location = o.matrix_world.translation  # the grid's own origin: calca3's base-plane point
    e.rotation_euler = (eul[0], c["rot"], eul[2])
    e.scale = (c["escala"],) * 3
    e["calca"], e["cara"], e["orden"], e["cx"] = o["c3"], c["cara"], c["orden"], CX
    e.lock_location = (c["cara"] != "porton", c["cara"] == "porton", False)  # slides on its face
    e.lock_rotation = (True, False, True)                                    # spins in the face's plane
    bpy.context.view_layer.update()
    mw = o.matrix_world.copy()
    o.parent = e
    o.matrix_parent_inverse = e.matrix_world.inverted()
    o.matrix_world = mw
    marcas.append(e)
guardar("calcas", marcas, [c2, c4], os.path.join(OUT, "colocar-calcas.blend"))
inst = [bpy.data.objects["inst_" + id] for id in INSTRUMENTOS]
for e in inst:
    soltar(e)
    e.empty_display_type, e.empty_display_size = "PLAIN_AXES", 0.3
guardar("instrumentos", inst, [c2], os.path.join(OUT, "colocar-instrumentos.blend"))
