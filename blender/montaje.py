"""Integration build (branch cc/highkeydrone; owner 2026-11-15 04:18: one integration branch, the lanes branch off it and merge
back, docs/lanes.md). One chain for the six selected scenes, built from what each lane already made, edited in none of them:

  escena.py + mundo.py (Night B world) -> utileria.py (scene holds, props) -> caja3.py -> caja4.py -> caja5.py (bed B 'elegida',
  drinks), then props_placement.py's body in its own namespace (the truck-level picks: roof lamps, Pirata One MT emblem, strawberry
  B, fringe, pennant, rosettes, underglow, name strip, plate), then the cast slot and the interim Diego, then utileria's render loop.

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/montaje.py)" \
    -- <escena.py (Windows)> <out_dir (Windows)> [samples] [montaje-esc1,...|all] [WxH] [wb]

`wb` renders raw Workbench stills (material colours, glass hidden because Workbench draws it opaque, road and markings flat);
without it, Cycles like the other chain scripts. Before the scenes it saves <out_dir>/montaje.blend: the truck, the world, the
cast slot and the interim Diego (each scene's dressing is built per option, as in every chain script). Never hand-edit it.

Scene -> hold -> picks (sources: docs/design/escenas-plan.md §1, props-placement/props.md pass 2, caja5.py, the owner's
decisions of 2026-11-15 in the mothership queue):
  1 Cabina  CAMINO[0] 20 mm (caja5-bebidas-esc1)   pp1-b cab picks: split fringe, pennant on the dash, strawberry B, MT
  2 Caja    esc2-abre 28 mm (caja5-elegida-esc2)   stickers calcas3 mix (utileria); bed caja5 'elegida'
  3 Pantalla esc3-hombro 24 mm (owner pick 3B)      the screen truck overtaking on the left
  4 Costado esc4-cabina 24 mm (owner pick 4B)       pp4-b truck picks: one rosette, underglow; water in Héctor's hand
  5 Gira    esc5-abre 30 mm                         the screen truck ahead in the lane
  6 Placa   pp6-b 32 mm                             plate, name strip, two rosettes, underglow 150 W, split fringe
Every scene: bed caja5 'elegida' (owner: "the latest", not final), camion() (roof lamps + MT), Héctor's water bottle (caja5),
Diego holding his drink (colddrone). Dropped on purpose: uncdrone's bed B 'reglas' (piñata under the bar, balloons) and the
bulbs along the bed and roll bar, which belong to the older bed; the props lane decides whether bulbs come back on caja5.

Cast slot (apedrone's Tripo cast drops in here): collection `reparto` with one child collection per seat, each holding an empty
`asiento_<who>` at the seated hip point, facing forward, with custom properties alto_m (Diego, Alexandro 1.74; Héctor, the
manager 1.67), rol and asiento; the stand-ins sit in the same collection, so a drop-in replaces the contents. Diego is the
interim colddrone clip (sitting_drinking with the owner's hand pose and the sip bake), live rig, scaled to 1.74 m.

Placing a rigged clip: parent its top-level objects to one empty and move the empty. Setting matrix_world on the armature and on
its children one by one moves bone-parented children twice (they read the bone's pose before the depsgraph updates): that was
the raw sheet's "live rig mis-evaluates" (hallazgos.md #6), measured 2026-11-15 in an empty file, docs/lanes.md › Findings.
"""
import bpy, math, os, sys, time
import numpy as np
from mathutils import Vector, Matrix
sys.dont_write_bytecode = True

AQUI = os.path.dirname(os.path.abspath(__file__))
LAZO = "# ---------------------------------------------------------------- utileria.py's render loop"
WB = len(sys.argv) > sys.argv.index("--") + 6 and sys.argv[sys.argv.index("--") + 6] == "wb"
DIEGO_CLIP = os.environ.get("MONTAJE_DIEGO") or r"\\wsl.localhost\Ubuntu\home\black\cc-out\mto-integracion\assets\diego_clip_sitting_drinking_sip.blend"
# copied 2026-11-15 from MTO-colddrone/blender/assets/reparto/ (untracked there; docs/diego-clip-fixes.md › Sitting_drinking: done)

# ---------------------------------------------------------------- 1. caja5's chain, without its render loop
C5 = os.path.join(AQUI, "caja5.py")
exec(compile(open(C5, encoding="utf8").read().rsplit(LAZO, 1)[0], C5, "exec"), globals())

# ---------------------------------------------------------------- 2. props_placement's body in its own namespace: it reuses
# names with other meanings (YT is the roof's front edge there, the tailgate in caja4; TECHO_Z, dg, vaciar_caja), so its
# functions keep their own while GRUPO, MATS and OPC stay shared. From after its caja3 exec to before its option registry.
PP = os.path.join(AQUI, "props_placement.py")
_pp = open(PP, encoding="utf8").read()
_ini, _fin_pp = _pp.index('CAMA = os.environ.get("PP_CAMA"'), _pp.index('for _e, _f in (("1", esc1)')
P = dict(globals())
P["np"] = np
exec(compile("\n" * _pp[:_ini].count("\n") + _pp[_ini:_fin_pp], PP, "exec"), P)


# ---------------------------------------------------------------- 3. cast slot and the interim Diego
ASIENTOS = {  # who -> (seat, role, height m); the figure names the chain uses
    "manager": ("delantero izquierdo", "conductor (El Manco)", 1.67),
    "hector": ("delantero derecho", "copiloto", 1.67),
    "alejandro": ("trasero izquierdo", "Alexandro", 1.74),
    "diego": ("trasero derecho", "Diego", 1.74),
}
DIEGO_OBJS = []


def mover_a(col, objs):
    for o in objs:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)


def techo_sobre(p):
    """Cab ceiling above a point: the first hit going up from just above it, figures hidden."""
    for o in FIGURAS + DIEGO_OBJS:
        o.hide_viewport = True
    _g["dg"] = bpy.context.evaluated_depsgraph_get()
    h = rayo(p + Vector((0, 0, 0.05)), (0, 0, 1))
    for o in FIGURAS + DIEGO_OBJS:
        o.hide_viewport = False
    _g["dg"] = bpy.context.evaluated_depsgraph_get()
    return h.z if h else float("nan")


def diego_interino(cadera, giro):
    """colddrone's sitting_drinking clip, live: its top-level objects under one empty that puts the posed Hips (frame 0 of this
    scene = the clip's first key) on the seat's hip point, facing forward, scaled so the rest pose is 1.74 m."""
    with bpy.data.libraries.load(DIEGO_CLIP, link=False) as (s, d):
        d.objects = [n for n in s.objects]
    nuevos = [o for o in d.objects if o is not None and o.type in ("MESH", "ARMATURE", "EMPTY") and o.name.split(".")[0] != "prop_seat"]
    for o in nuevos:
        sc.collection.objects.link(o)
    mx = next(o for o in nuevos if o.type == "ARMATURE")
    piel = max((o for o in nuevos if o.type == "MESH" and any(m.type == "ARMATURE" for m in o.modifiers)), key=lambda o: len(o.data.vertices))

    def alto_z():
        e = piel.evaluated_get(bpy.context.evaluated_depsgraph_get())
        me = e.to_mesh()
        zs = [(e.matrix_world @ v.co).z for v in me.vertices]
        e.to_mesh_clear()
        return min(zs), max(zs)
    mx.data.pose_position = "REST"
    bpy.context.view_layer.update()
    lo, hi = alto_z()
    mx.data.pose_position = "POSE"
    sc.frame_set(0)
    k = 1.74 / (hi - lo)
    hips = mx.matrix_world @ mx.pose.bones["mixamorig:Hips"].head
    raiz = bpy.data.objects.new("diego_raiz", None)
    sc.collection.objects.link(raiz)
    raiz.matrix_world = Matrix.Translation(cadera) @ giro @ Matrix.Scale(k, 4) @ Matrix.Translation(-hips)
    for o in nuevos:
        if o.parent is None:
            o.parent = raiz
            o.matrix_parent_inverse = Matrix.Identity(4)
    sc.frame_set(0)
    lo2, hi2 = alto_z()
    print(f"MONTAJE diego clip reposo {hi - lo:.3f} m -> escala {k:.3f}; sentado z {lo2:.3f}..{hi2:.3f}", flush=True)
    return [raiz] + nuevos, hi2


def montar_reparto():
    asientos_traseros()
    raiz = bpy.data.collections.new("reparto")
    sc.collection.children.link(raiz)
    for quien, (asiento, rol, alto) in ASIENTOS.items():
        col = bpy.data.collections.new("reparto_" + quien)
        raiz.children.link(col)
        rig = bpy.data.objects[quien + "_rig"]
        cad = rig.matrix_world @ rig.pose.bones["cadera"].head
        giro = rig.matrix_world.to_3x3().normalized().to_4x4()
        e = bpy.data.objects.new("asiento_" + quien, None)
        e.empty_display_type, e.empty_display_size = "SINGLE_ARROW", 0.3
        e.matrix_world = Matrix.Translation(cad) @ giro  # the stand-in rig's turn: its local -Y (a Tripo glb's front) faces forward
        e["alto_m"], e["rol"], e["asiento"] = alto, rol, asiento
        e["nota"] = "Hips here; local -Y faces forward. Drop-in: scale to alto_m, hips on this point; replace the stand-ins."
        col.objects.link(e)
        mover_a(col, [rig] + list(rig.children_recursive))
        techo = techo_sobre(cad)
        cabeza = None
        if quien == "diego":
            objs, cabeza = diego_interino(cad, giro)
            DIEGO_OBJS.extend(objs)
            mover_a(col, objs)
        estimada = cad.z + 0.52 * alto - 0.09  # seated: vertex ~0.52 of stature above the seat, hip joint ~0.09 above it
        fr = giro @ Vector((0, -1, 0))
        print(f"MONTAJE asiento {quien} {asiento} alto {alto} cadera ({cad.x:.3f}, {cad.y:.3f}, {cad.z:.3f}) frente ({fr.x:+.2f}, {fr.y:+.2f}) techo {techo:.3f} "
              f"cabeza {'medida' if cabeza else 'estimada'} {cabeza or estimada:.3f} libre {techo - (cabeza or estimada):+.3f}", flush=True)
    viejo_diego()


def viejo_diego():
    """The old glb Diego stays in the file (the chain's code finds him by name) but out of the render; utileria's loop shows every
    figure again after each still, so this runs before each one."""
    for o in [bpy.data.objects["diego_rig"]] + list(bpy.data.objects["diego_rig"].children_recursive):
        o.hide_render = True


def carril():
    """Which lane the truck drives in, as numbers: travel direction (the world's motion and the cab's seat order), the truck's
    x span and the lane lines from mundo.py."""
    import mundo
    xs = [(o.matrix_world @ Vector(c)).x for o in bpy.data.objects if o.name.startswith("rueda") for c in o.bound_box]
    espejos = (P["RETROS"][-1][0].x, P["RETROS"][1][0].x) if P["RETROS"] else (float("nan"),) * 2
    m = bpy.data.objects["mundo"]
    sc.frame_set(0); y0 = m.matrix_world.translation.y
    sc.frame_set(10); y1 = m.matrix_world.translation.y
    sc.frame_set(0)
    ym = bpy.data.objects["manager_rig"].matrix_world @ bpy.data.objects["manager_rig"].pose.bones["cadera"].head
    yd = bpy.data.objects["diego_rig"].matrix_world @ bpy.data.objects["diego_rig"].pose.bones["cadera"].head
    print(f"MONTAJE carril mundo y f0 {y0:.2f} f10 {y1:.2f} (se mueve {'-Y: el camión avanza +Y' if y1 < y0 else '+Y'}); "
          f"asiento delantero y {ym.y:.2f} > trasero y {yd.y:.2f}; frente y {FRENTE:.2f}", flush=True)
    print(f"MONTAJE carril llantas x {min(xs):.2f}..{max(xs):.2f}, espejos x {espejos[0]:.2f}..{espejos[1]:.2f} (centro CX {CX}); raya central x 0; borde derecho blanco x "
          f"+{mundo.X_LINEA}; borde izquierdo amarillo x -{mundo.X_LINEA}; mirando +Y la derecha es +X -> carril "
          f"{'DERECHO' if min(xs) > 0 else 'IZQUIERDO' if max(xs) < 0 else 'SOBRE LA RAYA'}", flush=True)


t_m = time.time()
montar_reparto()
carril()
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "montaje.blend"), copy=True)
print("MONTAJE guardado", os.path.join(OUT, "montaje.blend"), round(time.time() - t_m, 1), "s", flush=True)


# ---------------------------------------------------------------- 4. the six scenes
def cama():
    cama_elegida()  # base_escena() dresses bed B with caja5's 'elegida'


def m_esc1():
    cama(); base_escena(); bebida_en_mano(); P["camion"]()
    P["flecos"](partida=True, largo=0.025); P["banderin_tablero"](CX + 0.14); P["fresa"](0.045, P["VAR"]["fresa"])
    c = P["CAM1"]
    return toma(c, (c[0], c[1], v(c[2])))


def m_esc2():
    cama(); t = esc2_abre(); bebida_en_mano(); P["camion"]()
    return t


def m_esc3():
    cama(); t = esc3_hombro(); bebida_en_mano(); P["camion"]()
    return t


def m_esc4():
    cama(); t = esc4_cabina(); bebida_en_mano(); P["camion"](); P["monos"]((1,)); P["bajo_luz"]()
    return t


def m_esc5():
    cama(); t = esc5_abre(); bebida_en_mano(); P["camion"]()
    return t


def m_esc6():
    cama(); base_escena(); bebida_en_mano(); placa3(); P["camion"](); P["franja"]("parabrisas"); P["monos"]((1, -1))
    P["bajo_luz"](w=150); P["flecos"](partida=True)
    return ((CX + 1.4, FRENTE + 6.5, 0.95), (CX + 0.1, FRENTE - 1.5, 1.2), 32)


CRISTALES_WB = ("vidrio", "mica")  # material names; VIDRIO is caja3's glass material
SUELO = {"w_carretera": (0.06, 0.06, 0.065), "w_acot_der": (0.11, 0.11, 0.11), "w_acot_izq": (0.11, 0.11, 0.11),
         "w_grava_der": (0.16, 0.15, 0.13), "w_grava_izq": (0.16, 0.15, 0.13), "w_terreno": (0.05, 0.08, 0.04),
         "w_borde_der": (0.9, 0.9, 0.9), "w_carril": (0.9, 0.9, 0.9), "w_borde_izq": (0.95, 0.7, 0.05)}


def pase_wb():
    """Workbench raw pass (crudo.py's): material colours from the Principled base colour, glass hidden (Workbench draws it
    opaque: noted, not fixed), the fog box hidden, the road, verges and markings flat so the lane reads."""
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light, sh.color_type = "STUDIO", "TEXTURE"
    sc.display.render_aa = "8"
    sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure = "Standard", "None", 0.0
    for m in bpy.data.materials:
        p = m.node_tree.nodes.get("Principled BSDF") if m.node_tree else None
        if p is not None and not p.inputs["Base Color"].links:
            m.diffuse_color = p.inputs["Base Color"].default_value[:]
    for o in bpy.data.objects:
        if o.type == "MESH" and o.data.materials and o.data.materials[0] and o.data.materials[0].name.split(".")[0] in CRISTALES_WB:
            o.hide_render = True
        n = o.name.split(".")[0]
        if n in SUELO and o.type == "MESH":
            plano_ = bpy.data.materials.get("wb_" + n) or bpy.data.materials.new("wb_" + n)
            plano_.diffuse_color = (*SUELO[n], 1.0)
            o.data.materials.clear()
            o.data.materials.append(plano_)
    if "w_niebla" in bpy.data.objects:
        bpy.data.objects["w_niebla"].hide_render = True


ESCENAS = [("montaje-esc1", m_esc1), ("montaje-esc2", m_esc2), ("montaje-esc3", m_esc3), ("montaje-esc4", m_esc4),
           ("montaje-esc5", m_esc5), ("montaje-esc6", m_esc6)]
for _n, _f in ESCENAS:
    def _op(f=_f):
        r = f()
        viejo_diego()
        if WB:
            pase_wb()
        return r
    opcion(_n)(_op)
if _g["SOLO"] is None:
    _g["SOLO"] = [n for n, _ in ESCENAS]

# ---------------------------------------------------------------- utileria.py's render loop, over the options above
exec(compile(MARCA + _cola, U, "exec"), _g)
print("MONTAJE total", round(time.time() - t0, 1), "s", flush=True)
