"""The owner's G63 placement file with the new roof load (queue 2026-11-20-mto-roof-props-swap-rebuild).

Takes a COPY of his colocar-g63-manos.blend (hands and elbow controls, cast, cameras: untouched) and swaps the roof load: the five old instrument
cases and their handles go, the donut stays where he put it, the alien keeps its handle and is lifted onto the pile; the new pieces (two flight
cases with different stickers, two guitar cases, a bag and a backpack) come in with one `techo_<pieza>` handle each; the net over everything but
the alien and the alien's own straps are laid over his placement. Same controls as the manos file; only the handles, the crosses and the hand and
elbow controls stay selectable.

  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b <a copy of colocar-g63-manos.blend> --python-exit-code 1 \
    --python blender/colocacion_g63_carga.py -- <out .blend (Windows)> [variante=1|2|3]
"""
import bpy, math, os, sys
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g63_carga as G

A = sys.argv[sys.argv.index("--") + 1:]
SAL = A[0]
VAR = int(A[1].split("=")[1]) if len(A) > 1 else 1
O = bpy.data.objects
sc = bpy.context.scene
camion = O["camion"]
coleccion = bpy.data.collections["controles"]
bpy.context.view_layer.update()
SELECCIONABLES = {o.name for o in O if not o.hide_select}

# ---------------------------------------------------------------- what leaves
def por_base(base):
    """Objects named `base` or `base.001` ...: his file may carry the suffix."""
    return [o for o in O if o.name.split(".")[0] == base]


VIEJOS = ("bajo", "docerola", "requinto", "teclado", "tarola")
for n in VIEJOS:
    for nombre in (f"k3_{n}", f"techo_{n}"):
        for o in por_base(nombre):
            me = o.data if o.type == "MESH" else None
            O.remove(o, do_unlink=True)
            if me and not me.users:
                bpy.data.meshes.remove(me)
    SELECCIONABLES.discard(f"techo_{n}")
viejo = O.get("carga_red")
if viejo:
    me = viejo.data
    O.remove(viejo, do_unlink=True)
    bpy.data.meshes.remove(me)
dona, alien = por_base("k3_dona")[0], por_base("k3_alien")[0]
mw_dona = dona.matrix_world.copy()

# ---------------------------------------------------------------- what comes
props = G.traer()
for k, o in props.items():
    print("CARGA calcas", k, G.calcas(o, k[3:]), "dim", [round(v, 3) for v in G.dim_local(o)], flush=True)
rg = G.geom_rack()
print("CARGA rack", {k: ([round(x, 3) for x in v] if isinstance(v, list) else round(v, 3)) for k, v in rg.items()}, flush=True)
M, B = G.layout(props, rg, G.caja_vert(dona), alien, VAR)


def sin_escala(m):
    return Matrix.LocRotScale(m.to_translation(), m.to_quaternion(), None)


def vacio(nombre, mw):
    e = bpy.data.objects.new(nombre, None)
    coleccion.objects.link(e)
    e.empty_display_type, e.empty_display_size = "PLAIN_AXES", 0.18
    e.show_in_front, e.show_name = True, True
    bpy.context.view_layer.update()
    e.parent = camion
    e.matrix_parent_inverse = camion.matrix_world.inverted()
    e.matrix_world = mw
    return e


for nombre, o in props.items():
    sc.collection.objects.link(o) if o.name not in sc.collection.objects else None
    h = vacio("techo_" + nombre[3:], sin_escala(M[nombre]))
    o.parent = h
    o.matrix_parent_inverse = h.matrix_world.inverted()
    o.matrix_world = M[nombre]
    SELECCIONABLES.add(h.name)
h_alien = por_base("techo_alien")[0]
h_alien.matrix_world = sin_escala(M["k3_alien"])      # his handle carries the alien; it goes up onto the pile
bpy.context.view_layer.update()
print("CARGA alien", [round(x, 3) for x in alien.matrix_world.translation], "dona", [round(x, 3) for x in dona.matrix_world.translation],
      "dona movida", round((dona.matrix_world.translation - mw_dona.translation).length, 6), flush=True)

# ---------------------------------------------------------------- net and straps
netted = {k: o for k, o in {**props, "k3_dona": dona}.items()}
cajas = {k: G.caja_vert(o) for k, o in netted.items()}
red, correas = G.tender(cajas, alien, rg, camion)
red.hide_select = correas.hide_select = True
barras = [O[f"rack_barra{k}"] for k in range(3)]
G.medir(netted, alien, red, correas, barras, f"variante {VAR}")

import json
json.dump({k: [[round(float(v), 6) for v in f] for f in m] for k, m in M.items()}, open(SAL.replace(".blend", "-layout.json"), "w"), indent=0)

# ---------------------------------------------------------------- lock, save
bpy.context.view_layer.update()
for o in O:
    o.hide_select = o.name not in SELECCIONABLES
    o.select_set(False)
bpy.context.view_layer.objects.active = None
t = bpy.data.texts.get("LEEME")
if t:
    txt = t.as_string()
    txt = txt.replace("techo_bajo, techo_docerola, techo_requinto, techo_teclado, techo_tarola, techo_dona, techo_alien",
                      "techo_maleta_a, techo_maleta_b, techo_guitarra_a, techo_guitarra_b, techo_bolsa, techo_mochila, techo_dona, techo_alien")
    txt = txt.replace("La red NO sigue a las piezas mientras acomodas: se vuelve a tender sola al reconstruir.",
                      "La red (carga_red, sobre todo menos el alien) y las correas del alien (carga_red_alien) NO siguen a las piezas mientras acomodas: se vuelven a tender solas al reconstruir.")
    t.clear()
    t.write(txt)
bpy.ops.wm.save_as_mainfile(filepath=SAL, copy=True)
print("CARGA guardado", SAL, len(SELECCIONABLES), "seleccionables", flush=True)
