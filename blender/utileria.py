"""Prop look options for scene-plan phase 1 (docs/design/escenas-plan.md §2): 2-3 options per new prop, stills only,
rendered in the night scene with the G63. Every option traces to a row of docs/design/references.md (section "Scene props").

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/utileria.py)" \
    -- <escena.py path (Windows)> <out_dir (Windows)> [samples=32] [only=radio-a,placa-b] [WxH=1280x720]

The scene comes from escena.py + transicion.py next to <escena.py> (assets resolve beside that copy: point it at the main
checkout, whose blender/assets/ holds the G63, HDRI and figures). Options are hidden except while their still renders.
"""
import bpy, math, os, sys, time
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
ESCENA, OUT = argv[0], argv[1]
SAMPLES = int(argv[2]) if len(argv) > 2 else 32
SOLO = argv[3].split(",") if len(argv) > 3 and argv[3] not in ("", "all") else None
RW, RH = (int(x) for x in (argv[4] if len(argv) > 4 else "1280x720").split("x"))
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTES = "C:\\Windows\\Fonts\\"  # stills only: the shipped lettering needs free fonts (noted in references.md)

t0 = time.time()
src = open(ESCENA, encoding="utf8").read()
g = {"__file__": ESCENA, "__name__": "escena_utileria"}
exec(compile(src.rstrip()[: -len("main()")], ESCENA, "exec"), g)
sys.path.insert(0, os.path.dirname(ESCENA))
import transicion as T

s = g["build"]()
g["mundo_render"](s, "noche")
g["motor"](SAMPLES, "noche")
T.preparar(s, RW, RH, g["islas"])
sc = bpy.context.scene
sc.frame_set(0)
sc.render.use_motion_blur = False  # stills of props: the road blur is not what is being judged
CX, CAM = T.CX, s["camion"]
dg = bpy.context.evaluated_depsgraph_get()
print("ESCENA", round(time.time() - t0, 1), "s")
print("OBJETOS", sorted({o.name.split(".")[0] for o in bpy.data.objects if not o.name.startswith(("Object", "Mesh"))})[:80])


def rayo(o, d):
    hit, loc, *_ = sc.ray_cast(dg, Vector(o), Vector(d))
    return loc if hit else None


ys = [(o.matrix_world @ Vector(c)).y for o in CAM.children_recursive if o.type == "MESH" for c in o.bound_box]
FRENTE, COLA = max(ys), min(ys)
FIGURAS = [o for o in bpy.data.objects if o.name.split("_")[0].split(".")[0] in ("hector", "diego", "alejandro", "manager")]
for o in FIGURAS:  # the rays must hit the truck, not the figures sitting in front of the dash
    o.hide_viewport = True
dg = bpy.context.evaluated_depsgraph_get()
TABLERO = rayo((CX, 0.75, 1.40), (0, 1, 0))          # centre stack face, ahead of the armrest
GUANTERA = rayo((CX + 0.42, 0.5, 1.28), (0, 1, 0))   # passenger dash face
for z in (1.25, 1.32, 1.40, 1.48, 1.56):
    print("PERFIL", z, rayo((CX, 0.75, z), (0, 1, 0)))
for o in FIGURAS:
    o.hide_viewport = False
dg = bpy.context.evaluated_depsgraph_get()
PORTON = rayo((CX, COLA - 1.0, 1.15), (0, 1, 0))      # tailgate
DEFENSA = rayo((CX, FRENTE + 1.0, 0.72), (0, -1, 0))  # front bumper
for n, p in (("TABLERO", TABLERO), ("GUANTERA", GUANTERA), ("PORTON", PORTON), ("DEFENSA", DEFENSA)):
    print("RAYO", n, p)
TABLERO = TABLERO or Vector((CX, 1.05, 1.38))
GUANTERA = GUANTERA or Vector((CX + 0.42, 1.05, 1.30))
PORTON = PORTON or Vector((CX, COLA, 1.15))
DEFENSA = DEFENSA or Vector((CX, FRENTE, 0.72))

# ---------------------------------------------------------------- helpers

MATS = {}


def mat(name, color, rough=0.5, metal=0.0, emit=0.0, ecolor=None, alpha=1.0, trans=0.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Transmission Weight"].default_value = trans
    b.inputs["Alpha"].default_value = alpha
    if emit:
        b.inputs["Emission Color"].default_value = (*(ecolor or color), 1)
        b.inputs["Emission Strength"].default_value = emit
    MATS[name] = m
    return m


def img_mat(name, path, emit=0.0, led=0, rough=0.4):
    """Image material; led=N draws it as an N-column LED panel (pixelated UV + round dot mask, emissive)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt, b = m.node_tree, m.node_tree.nodes["Principled BSDF"]
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(path, check_existing=True)
    tx.extension = "CLIP"
    b.inputs["Roughness"].default_value = rough
    if not led:
        nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
        if emit:
            nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"])
            b.inputs["Emission Strength"].default_value = emit
        return m
    uv = nt.nodes.new("ShaderNodeTexCoord")
    esc = nt.nodes.new("ShaderNodeVectorMath"); esc.operation = "MULTIPLY"
    esc.inputs[1].default_value = (led, led * 0.5, 1)  # caller sets aspect via plane UVs: rows = led/2 per unit
    nt.links.new(uv.outputs["UV"], esc.inputs[0])
    fl = nt.nodes.new("ShaderNodeVectorMath"); fl.operation = "FLOOR"
    nt.links.new(esc.outputs[0], fl.inputs[0])
    ce = nt.nodes.new("ShaderNodeVectorMath"); ce.operation = "ADD"; ce.inputs[1].default_value = (0.5, 0.5, 0)
    nt.links.new(fl.outputs[0], ce.inputs[0])
    di = nt.nodes.new("ShaderNodeVectorMath"); di.operation = "DIVIDE"; di.inputs[1].default_value = (led, led * 0.5, 1)
    nt.links.new(ce.outputs[0], di.inputs[0])
    nt.links.new(di.outputs[0], tx.inputs["Vector"])
    fr = nt.nodes.new("ShaderNodeVectorMath"); fr.operation = "FRACTION"
    nt.links.new(esc.outputs[0], fr.inputs[0])
    su = nt.nodes.new("ShaderNodeVectorMath"); su.operation = "SUBTRACT"; su.inputs[1].default_value = (0.5, 0.5, 0)
    nt.links.new(fr.outputs[0], su.inputs[0])
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
    nt.links.new(su.outputs[0], ln.inputs[0])
    lt = nt.nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = 0.36
    nt.links.new(ln.outputs["Value"], lt.inputs[0])
    mu = nt.nodes.new("ShaderNodeMixRGB"); mu.blend_type = "MULTIPLY"; mu.inputs[0].default_value = 1
    nt.links.new(tx.outputs["Color"], mu.inputs[1])
    nt.links.new(lt.outputs[0], mu.inputs[2])
    b.inputs["Base Color"].default_value = (0.01, 0.01, 0.01, 1)
    nt.links.new(mu.outputs[0], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = emit or 3.0
    return m


GRUPO = []  # objects of the option being built


def _fin(o, m, parent):
    if m:
        o.data.materials.append(m)
    if parent is not False:
        o.parent = parent or CAM
        o.matrix_parent_inverse = (parent or CAM).matrix_world.inverted()
    GRUPO.append(o)
    return o


def caja(size, loc, m, rot=(0, 0, 0), bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    if bevel:
        bpy.ops.object.transform_apply(scale=True)
        md = o.modifiers.new("bv", "BEVEL"); md.width = bevel; md.segments = 3
    return _fin(o, m, parent)


def cil(r, h, loc, m, rot=(0, 0, 0), verts=32, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=verts)
    return _fin(bpy.context.object, m, parent)


def esfera(r, loc, m, scale=(1, 1, 1), parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=32, ring_count=16)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.shade_smooth()
    return _fin(o, m, parent)


def toro(R, r, loc, m, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot, major_segments=48, minor_segments=16)
    bpy.ops.object.shade_smooth()
    return _fin(bpy.context.object, m, parent)


def cono(r1, r2, h, loc, m, rot=(0, 0, 0), verts=32, parent=None):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=h, location=loc, rotation=rot, vertices=verts)
    bpy.ops.object.shade_smooth()
    return _fin(bpy.context.object, m, parent)


def plano(w, h, loc, m, rot=(math.pi / 2, 0, 0), parent=None):
    """A w x h quad; default rotation stands it up facing -Y (towards a camera behind it)."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = (w, h, 1)
    return _fin(o, m, parent)


def texto(body, size, loc, m, font="bahnschrift.ttf", rot=(math.pi / 2, 0, 0), extr=0.0, align="CENTER", parent=None, ancho=1.0):
    cu = bpy.data.curves.new("txt", "FONT")
    cu.body = body
    cu.font = bpy.data.fonts.load(FUENTES + font, check_existing=True)
    cu.size, cu.extrude, cu.align_x, cu.align_y = size, extr, align, "CENTER"
    o = bpy.data.objects.new("txt", cu)
    sc.collection.objects.link(o)
    o.location, o.rotation_euler, o.scale = loc, rot, (ancho, 1, 1)
    return _fin(o, m, parent)


def luz(tipo, loc, energia, color, mira=None, size=0.1, parent=None):
    ld = bpy.data.lights.new("luz", tipo)
    ld.energy, ld.color = energia, color
    if tipo == "AREA":
        ld.size = size
    if tipo == "SPOT":
        ld.spot_size, ld.spot_blend = 0.9, 0.4
    o = bpy.data.objects.new("luz", ld)
    sc.collection.objects.link(o)
    o.location = loc
    if mira is not None:
        o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return _fin(o, None, parent)


NEGRO = mat("u_negro", (0.012, 0.012, 0.013), 0.35)
NEGRO_MATE = mat("u_negro_mate", (0.02, 0.02, 0.02), 0.8)
CROMO = mat("u_cromo", (0.8, 0.8, 0.82), 0.12, 1.0)
ORO = mat("u_oro", (0.91, 0.71, 0.32), 0.25, 1.0)          # DESIGN.md --gold #e7b551
CAP = mat("u_cap", (0.0056, 0.0048, 0.0031), 0.4)            # DESIGN.md --cap #110f0a
AMBAR = mat("u_ambar", (1.0, 0.55, 0.12), 0.3, emit=6.0)
VERDE_VFD = mat("u_vfd", (0.35, 1.0, 0.75), 0.3, emit=5.0)
BLANCO = mat("u_blanco", (0.9, 0.9, 0.88), 0.4)
BLANCO_REFL = mat("u_blanco_refl", (0.95, 0.95, 0.95), 0.25, emit=0.35)  # retroreflective sheeting under headlights
VERDE_SCT = mat("u_verde_sct", (0.0, 0.18, 0.08), 0.4, emit=0.12, ecolor=(0.0, 0.3, 0.12))
ACERO = mat("u_acero", (0.55, 0.56, 0.58), 0.45, 1.0)
CONCRETO = mat("u_concreto", (0.35, 0.34, 0.32), 0.85)
COVER = os.path.join(REPO, "public", "music", "la-bubu.jpg")
BANDA = os.path.join(REPO, "public", "band", "band-1.jpg")

# ---------------------------------------------------------------- options
# each builder places its objects (collected in GRUPO) and returns (pos, look-at, lens) for its still
OPC = {}


def opcion(nombre):
    def deco(f):
        OPC[nombre] = f
        return f
    return deco


def frente_tablero(dz=0.0):
    """Origin on the centre-stack face, nudged out of the plastic."""
    return Vector((CX, TABLERO.y - 0.012, TABLERO.z + dz))


def tecla(x, z, y):
    # the Tecla scene twin (docs/design/botones): gold square cap over a dark lip, pressed = translation
    caja((0.05, 0.02, 0.04), (x, y - 0.006, z - 0.004), CAP, bevel=0.002)
    caja((0.05, 0.02, 0.04), (x, y - 0.012, z), ORO, bevel=0.003)
    texto("ESCUCHAR", 0.0065, (x, y - 0.0225, z), NEGRO, font="bahnschrift.ttf")


VISTA_RADIO = lambda: ((CX + 0.08, TABLERO.y - 0.50, TABLERO.z + 0.16), (CX, TABLERO.y, TABLERO.z - 0.01), 32)


@opcion("radio-a")
def radio_a():
    """A: 1980s single-DIN cassette head unit, amber segment display, two chrome knobs, cassette in the door window."""
    o = frente_tablero()
    caja((0.18, 0.04, 0.05), o + Vector((0, 0.01, 0)), NEGRO, bevel=0.002)
    plano(0.07, 0.016, o + Vector((0.03, -0.011, 0.012)), AMBAR)
    texto("LA BUBU  98.5", 0.009, o + Vector((0.03, -0.012, 0.012)), mat("u_ambar_txt", (0.05, 0.02, 0), emit=0.0))
    caja((0.09, 0.006, 0.022), o + Vector((-0.02, -0.011, -0.01)), mat("u_ranura", (0.05, 0.05, 0.05), 0.2, trans=0.0))
    plano(0.07, 0.016, o + Vector((-0.02, -0.0145, -0.01)), img_mat("u_cover_a", COVER, emit=0.6))
    for dx in (-0.075, 0.075):
        cil(0.011, 0.016, o + Vector((dx, -0.018, 0)), CROMO, rot=(math.pi / 2, 0, 0))
    tecla(CX + 0.0, TABLERO.z - 0.055, TABLERO.y - 0.02)
    return VISTA_RADIO()


@opcion("radio-b")
def radio_b():
    """B: vintage AM/FM dash radio, warm horizontal tuning scale with a needle, push buttons; cassette deck under it."""
    o = frente_tablero(0.01)
    caja((0.20, 0.04, 0.055), o + Vector((0, 0.01, 0)), CROMO, bevel=0.004)
    plano(0.12, 0.022, o + Vector((0, -0.011, 0.008)), mat("u_escala", (1.0, 0.78, 0.45), 0.4, emit=3.0))
    for i in range(9):
        plano(0.0012, 0.008 if i % 2 else 0.012, o + Vector((-0.05 + i * 0.0125, -0.0115, 0.008)), NEGRO)
    plano(0.0015, 0.02, o + Vector((0.012, -0.012, 0.008)), mat("u_aguja", (0.9, 0.1, 0.05), emit=2.0))
    for i in range(5):
        caja((0.014, 0.012, 0.009), o + Vector((-0.04 + i * 0.02, -0.014, -0.016)), CROMO, bevel=0.001)
    for dx in (-0.085, 0.085):
        cil(0.013, 0.02, o + Vector((dx, -0.02, 0.0)), NEGRO, rot=(math.pi / 2, 0, 0))
    d = o + Vector((0, -0.01, -0.06))
    caja((0.15, 0.06, 0.035), d, NEGRO, bevel=0.002)
    plano(0.07, 0.018, d + Vector((0, -0.031, 0)), img_mat("u_cover_b", COVER, emit=0.6))
    tecla(CX + 0.095, d.z, d.y - 0.02)
    return VISTA_RADIO()


@opcion("radio-c")
def radio_c():
    """C: aftermarket single-DIN with one big dial (the dial the visitor turns), green VFD, cassette pull-out in gold."""
    o = frente_tablero()
    caja((0.18, 0.04, 0.05), o + Vector((0, 0.01, 0)), NEGRO_MATE, bevel=0.002)
    cil(0.022, 0.02, o + Vector((-0.055, -0.02, 0)), CROMO, rot=(math.pi / 2, 0, 0))
    toro(0.022, 0.0016, o + Vector((-0.055, -0.012, 0)), mat("u_aro", (1.0, 0.6, 0.2), emit=4.0), rot=(math.pi / 2, 0, 0))
    plano(0.085, 0.018, o + Vector((0.035, -0.011, 0.01)), VERDE_VFD)
    texto("02 LA BUBU", 0.0095, o + Vector((0.035, -0.0118, 0.01)), mat("u_vfd_txt", (0.0, 0.03, 0.02)))
    caja((0.09, 0.03, 0.012), o + Vector((0.035, -0.024, -0.014)), ORO, bevel=0.0015)
    plano(0.05, 0.009, o + Vector((0.035, -0.0395, -0.014)), img_mat("u_cover_c", COVER, emit=0.5))
    tecla(CX + 0.14, TABLERO.z, TABLERO.y - 0.01)
    return VISTA_RADIO()


VISTA_GUANTERA = lambda: ((CX + 0.02, GUANTERA.y - 0.55, GUANTERA.z + 0.14), (GUANTERA.x, GUANTERA.y - 0.12, GUANTERA.z - 0.14), 24)


def guantera_abierta():
    p = Vector((GUANTERA.x, GUANTERA.y - 0.012, GUANTERA.z - 0.06))
    caja((0.38, 0.012, 0.16), p + Vector((0, -0.07, -0.075)), NEGRO_MATE, rot=(math.radians(70), 0, 0))
    caja((0.36, 0.14, 0.13), p + Vector((0, 0.06, 0.0)), mat("u_hueco", (0.004, 0.004, 0.004), 0.9))
    luz("POINT", p + Vector((0, 0.0, 0.05)), 3.0, (1.0, 0.8, 0.55))
    luz("AREA", p + Vector((-0.1, -0.35, 0.25)), 6.0, (1.0, 0.85, 0.65), mira=p + Vector((0, -0.1, -0.12)), size=0.2)
    return p


def hoyo_tapa(p):  # where the junk lands: on the dropped lid
    return p + Vector((0, -0.10, -0.12))


@opcion("guantera-a")
def guantera_a():
    """A: the plan's set: rubber duck, a deck of cards fanned out, a toy sombrero."""
    p = hoyo_tapa(guantera_abierta())
    am = mat("u_patito", (1.0, 0.75, 0.02), 0.35)
    esfera(0.035, p + Vector((-0.10, 0, 0.03)), am, scale=(1.0, 1.3, 0.8))
    esfera(0.022, p + Vector((-0.10, -0.035, 0.065)), am)
    cono(0.009, 0.0, 0.02, p + Vector((-0.10, -0.06, 0.063)), mat("u_pico", (1.0, 0.35, 0.02), 0.4), rot=(math.pi / 2, 0, 0))
    for i in range(5):
        caja((0.045, 0.065, 0.002), p + Vector((0.02 + i * 0.012, 0, 0.008 + i * 0.002)), BLANCO, rot=(0, 0, 0.25 * i - 0.5))
    paja = mat("u_paja", (0.75, 0.55, 0.25), 0.8)
    cil(0.07, 0.006, p + Vector((0.12, 0.02, 0.01)), paja)
    cono(0.03, 0.022, 0.04, p + Vector((0.12, 0.02, 0.033)), paja)
    toro(0.05, 0.004, p + Vector((0.12, 0.02, 0.014)), mat("u_cinta", (0.7, 0.05, 0.05), 0.5))
    return VISTA_GUANTERA()


@opcion("guantera-b")
def guantera_b():
    """B: lotería cards spilling, a tiny charro sombrero in black and gold, a pine air freshener."""
    p = hoyo_tapa(guantera_abierta())
    for i in range(7):
        caja((0.05, 0.075, 0.0015), p + Vector((-0.11 + i * 0.03, (i % 2) * 0.02, 0.006 + i * 0.0015)),
             img_mat(f"u_loteria_{i}", COVER if i % 2 else BANDA, emit=0.2), rot=(0, 0, 0.4 * (i - 3)))
    cil(0.075, 0.005, p + Vector((0.11, 0.02, 0.03)), NEGRO, rot=(0.3, 0, 0))
    cono(0.032, 0.02, 0.05, p + Vector((0.11, 0.025, 0.06)), NEGRO, rot=(0.3, 0, 0))
    toro(0.07, 0.003, p + Vector((0.11, 0.02, 0.03)), ORO, rot=(0.3, 0, 0))
    caja((0.04, 0.003, 0.07), p + Vector((-0.02, -0.04, 0.05)), mat("u_pino", (0.05, 0.45, 0.12), 0.6), rot=(0.2, 0, 0.3))
    return VISTA_GUANTERA()


@opcion("guantera-c")
def guantera_c():
    """C: band junk: a cassette with no case, guitar picks, a crumpled set list, sunglasses."""
    p = hoyo_tapa(guantera_abierta())
    caja((0.1, 0.064, 0.012), p + Vector((-0.08, 0, 0.008)), mat("u_casete", (0.05, 0.05, 0.06), 0.2), rot=(0, 0, 0.3))
    plano(0.07, 0.03, p + Vector((-0.08, 0, 0.0145)), img_mat("u_cover_g", COVER, emit=0.4), rot=(0, 0, 0.3))
    for i in range(4):
        cil(0.012, 0.002, p + Vector((0.0 + i * 0.025, -0.03 + (i % 2) * 0.03, 0.004)), ORO if i % 2 else mat("u_pua", (0.8, 0.1, 0.1), 0.3), verts=3)
    esfera(0.04, p + Vector((0.1, 0.03, 0.02)), BLANCO, scale=(1.2, 1.0, 0.5))
    for dx in (-0.025, 0.025):
        cil(0.02, 0.004, p + Vector((0.06 + dx, -0.04, 0.02)), mat("u_lente", (0.02, 0.02, 0.02), 0.05), rot=(1.2, 0, 0))
    return VISTA_GUANTERA()


VISTA_CALCAS = lambda: ((CX + 0.6, PORTON.y - 2.4, 1.45), (CX, PORTON.y, 1.15), 35)


def relleno(pos, mira, energia=60):
    """Camera-side fill (a following car's headlights / the screen truck's spill): plan storyboard note 4."""
    luz("AREA", pos, energia, (1.0, 0.92, 0.8), mira=mira, size=1.2, parent=False)


def calca(body, sub, loc, rot_y, fondo, tinta, borde, w=0.26, h=0.15, forma="rect", font="impact.ttf"):
    """One own-art sticker on the tailgate: our lettering + a clear area (outlined) for the platform's unaltered glyph,
    kept upright (no rotation), outside the peel corner."""
    rot = (math.pi / 2, rot_y, 0)
    if forma == "rect":
        plano(w + 0.02, h + 0.02, loc + Vector((0, -0.001, 0)), borde, rot=rot)
        plano(w, h, loc + Vector((0, -0.002, 0)), fondo, rot=rot)
    else:
        cil(h / 2 + 0.01, 0.001, loc + Vector((0, -0.001, 0)), borde, rot=(math.pi / 2, 0, 0))
        cil(h / 2, 0.001, loc + Vector((0, -0.0025, 0)), fondo, rot=(math.pi / 2, 0, 0))
    texto(body, h * 0.30, loc + Vector((0, -0.004, h * 0.12)), tinta, font=font, rot=rot)
    texto(sub, h * 0.16, loc + Vector((0, -0.004, -h * 0.20)), tinta, font=font, rot=rot)
    # upright clear area for the official glyph (the glyph itself is pasted from the platform's own files at build)
    gx = loc + Vector((w * 0.36 if forma == "rect" else 0, -0.005, -h * 0.02 if forma == "rect" else h * 0.42))
    plano(0.034, 0.034, gx, mat("u_glifo", (0.5, 0.5, 0.5), 0.5), rot=(math.pi / 2, 0, 0))


@opcion("calcas-a")
def calcas_a():
    relleno((CX + 1.2, PORTON.y - 4.0, 1.3), (CX, PORTON.y, 1.15), 120)
    """A: die-cut vinyl with a fat white border (classic tailgate stickers), our jokes as art: PUTIFRESA strawberry, MT."""
    z = PORTON.z
    y = PORTON.y - 0.004
    bl = mat("u_vinil_blanco", (0.95, 0.95, 0.93), 0.3)
    calca("SÍGUENOS", "EN INSTAGRAM", Vector((CX - 0.45, y, z + 0.08)), 0.12, mat("u_rosa", (0.9, 0.12, 0.35), 0.3), bl, bl)
    calca("ESCÚCHANOS", "EN SPOTIFY", Vector((CX + 0.05, y, z + 0.15)), -0.08, NEGRO, ORO, bl)
    calca("MÍRANOS", "EN YOUTUBE", Vector((CX + 0.5, y, z + 0.02)), 0.2, mat("u_rojo", (0.75, 0.04, 0.03), 0.3), bl, bl)
    calca("ANDAMOS", "EN TIKTOK", Vector((CX - 0.05, y, z - 0.12)), -0.15, mat("u_amarillo", (1.0, 0.78, 0.05), 0.3), NEGRO, bl)
    esfera(0.035, Vector((CX - 0.62, y - 0.01, z + 0.16)), mat("u_fresa", (0.85, 0.05, 0.08), 0.3), scale=(1, 0.2, 1.15))
    return VISTA_CALCAS()


@opcion("calcas-b")
def calcas_b():
    relleno((CX + 1.2, PORTON.y - 4.0, 1.3), (CX, PORTON.y, 1.15), 120)
    """B: bumper-sticker strips, text-led, black and gold (DESIGN.md palette), stacked like a tour of truck stops."""
    z, y = PORTON.z, PORTON.y - 0.004
    for i, (a, b2) in enumerate((("SÍGUENOS", "EN INSTAGRAM"), ("ESCÚCHANOS", "EN SPOTIFY"), ("MÍRANOS", "EN YOUTUBE"), ("ANDAMOS", "EN TIKTOK"))):
        calca(a, b2, Vector((CX + (-0.3 if i % 2 else 0.3), y, z + 0.22 - i * 0.14)), (-0.04, 0.03, 0.05, -0.02)[i],
              CAP if i % 2 else ORO, ORO if i % 2 else NEGRO, mat("u_borde_oro", (0.5, 0.38, 0.15), 0.4), w=0.42, h=0.11, font="bahnschrift.ttf")
    return VISTA_CALCAS()


@opcion("calcas-c")
def calcas_c():
    relleno((CX + 1.2, PORTON.y - 4.0, 1.3), (CX, PORTON.y, 1.15), 120)
    """C: round badge stickers (bottle-cap / lotería-like), slapped at angles across the tailgate and rear bumper."""
    z, y = PORTON.z, PORTON.y - 0.004
    bl = mat("u_vinil_blanco", (0.95, 0.95, 0.93), 0.3)
    for i, (a, b2, col, x, dz) in enumerate((("SÍGUENOS", "INSTAGRAM", (0.9, 0.12, 0.35), -0.5, 0.1), ("ESCÚCHANOS", "SPOTIFY", (0.1, 0.55, 0.25), -0.15, -0.05),
                                             ("MÍRANOS", "YOUTUBE", (0.75, 0.04, 0.03), 0.2, 0.12), ("ANDAMOS", "TIKTOK", (0.05, 0.05, 0.06), 0.55, -0.02))):
        calca(a, b2, Vector((CX + x, y, z + dz)), 0.0, mat(f"u_badge_{i}", col, 0.3), bl if i != 3 else ORO, bl, h=0.2, forma="redonda")
    return VISTA_CALCAS()


# pantalla móvil: rides in the left lane beside the band (as storyboard 3-pantalla)
PM_X, PM_Y = CX - 4.0, 1.0
VISTA_PANTALLA = lambda: ((CX + 0.4, -8.0, 2.7), (PM_X + 0.6, PM_Y + 0.5, 2.0), 26)


def ruedas(xs, ys, r=0.5, ancho=0.32, padre=None):
    for y in ys:
        for x in xs:
            cil(r, ancho, (x, y, r), NEGRO_MATE, rot=(0, math.pi / 2, 0), parent=False)
            cil(r * 0.55, ancho + 0.01, (x, y, r), ACERO, rot=(0, math.pi / 2, 0), parent=False)


def cabina_camion(x, y, ancho=2.3, color=(0.06, 0.06, 0.07)):
    m = mat(f"u_cab_{color}", color, 0.3, 0.3)
    caja((ancho, 2.0, 1.6), (x, y, 1.6), m, bevel=0.08, parent=False)
    caja((ancho, 1.4, 0.9), (x, y - 0.3, 2.85), m, bevel=0.1, parent=False)
    plano(ancho - 0.3, 0.7, (x, y + 0.41, 2.9), mat("u_parabrisas", (0.02, 0.02, 0.03), 0.05), rot=(math.radians(80), 0, 0), parent=False)
    for dx in (-0.8, 0.8):
        plano(0.3, 0.12, (x + dx, y + 1.01, 1.3), mat("u_faro", (1, 0.95, 0.85), emit=30), rot=(-math.pi / 2, 0, math.pi), parent=False)
        luz("SPOT", (x + dx, y + 1.1, 1.3), 300, (1, 0.93, 0.8), mira=(x + dx, y + 20, 0.0), parent=False)
    caja((ancho - 0.4, 0.05, 0.5), (x, y + 1.0, 0.85), NEGRO, parent=False)


def panel_led(w, h, loc, rot, img, cols):
    return plano(w, h, loc, img_mat(f"u_led_{len(GRUPO)}", img, emit=3.5, led=cols), rot=rot, parent=False)


def pantalla_vacia(w, h, loc, rot):
    """The rear screen in its empty state (escenas-plan §5): no invented dates."""
    plano(w, h, loc, mat("u_led_negro", (0.01, 0.01, 0.01), 0.3), rot=rot, parent=False)
    off = Vector((0, -0.01, 0)) if rot[2] == 0 else Vector((0.01, 0, 0))
    texto("PRÓXIMAS FECHAS", h * 0.16, Vector(loc) + off + Vector((0, 0, h * 0.18)), mat("u_led_oro", (1.0, 0.7, 0.25), emit=6), font="consolab.ttf", rot=rot, parent=False)
    texto("MUY PRONTO", h * 0.12, Vector(loc) + off + Vector((0, 0, -h * 0.12)), mat("u_led_blanco", (1, 1, 1), emit=4), font="consolab.ttf", rot=rot, parent=False)


@opcion("pantalla-a")
def pantalla_a():
    """A: rigid box truck (camión publicitario): LED panels on both sides and the back, black body, gold trim line."""
    x, y = PM_X, PM_Y
    cabina_camion(x, y + 3.6)
    caja((2.5, 6.0, 3.0), (x, y - 0.4, 2.15), mat("u_caja_pm", (0.03, 0.03, 0.035), 0.4), parent=False)
    panel_led(5.4, 2.5, (x + 1.26, y - 0.4, 2.2), (math.pi / 2, 0, math.pi / 2), BANDA, 96)
    caja((0.02, 5.6, 0.04), (x + 1.27, y - 0.4, 0.92), ORO, parent=False)
    pantalla_vacia(2.2, 2.4, (x, y - 3.42, 2.2), (math.pi / 2, 0, 0))
    ruedas((x - 1.0, x + 1.0), (y - 2.6, y - 1.6, y + 3.6))
    return VISTA_PANTALLA()


@opcion("pantalla-b")
def pantalla_b():
    """B: a pickup towing an LED screen trailer (remolque con pantalla): lower, the screen stands on a mast."""
    x, y = PM_X, PM_Y
    cabina_camion(x, y + 4.0, ancho=2.0, color=(0.55, 0.55, 0.56))
    caja((2.0, 2.2, 0.8), (x, y + 1.9, 1.1), mat("u_batea", (0.5, 0.5, 0.51), 0.35, 0.4), parent=False)
    caja((1.8, 3.0, 0.5), (x, y - 1.2, 0.85), NEGRO, parent=False)
    caja((0.15, 0.15, 1.2), (x, y - 1.2, 1.6), ACERO, parent=False)
    caja((0.3, 3.6, 2.2), (x, y - 1.2, 3.2), NEGRO, parent=False)
    panel_led(3.4, 2.0, (x + 0.16, y - 1.2, 3.2), (math.pi / 2, 0, math.pi / 2), BANDA, 72)
    ruedas((x - 0.9, x + 0.9), (y - 1.2, y + 3.9))
    return VISTA_PANTALLA()


@opcion("pantalla-c")
def pantalla_c():
    """C: box truck with the side screen framed like a marquee: a row of warm bulbs around it, the rear screen the same."""
    x, y = PM_X, PM_Y
    cabina_camion(x, y + 3.6, color=(0.02, 0.02, 0.02))
    caja((2.5, 6.0, 3.0), (x, y - 0.4, 2.15), CAP, parent=False)
    panel_led(5.0, 2.2, (x + 1.26, y - 0.4, 2.2), (math.pi / 2, 0, math.pi / 2), BANDA, 80)
    foco = mat("u_foco", (1.0, 0.75, 0.4), 0.3, emit=12)
    for i in range(26):
        yy = y - 0.4 - 2.6 + i * 0.208
        for zz in (0.98, 3.42):
            esfera(0.04, (x + 1.28, yy, zz), foco, parent=False)
    for i in range(12):
        for yy in (y - 3.0, y + 2.2):
            esfera(0.04, (x + 1.28, yy, 0.98 + i * 0.22), foco, parent=False)
    pantalla_vacia(2.0, 2.2, (x, y - 3.42, 2.2), (math.pi / 2, 0, 0))
    ruedas((x - 1.0, x + 1.0), (y - 2.6, y - 1.6, y + 3.6))
    return VISTA_PANTALLA()


# sign gantry: across the road ahead of the truck; the camera rides high behind the bed, as at the end of the v3 move
PORTICO_Y = 16.0
VISTA_PORTICO = lambda: ((CX - 0.6, -7.5, 3.4), (CX + 0.2, PORTICO_Y, 5.4), 36)


def letrero(titulo, sub, x, z, w, h):
    """SCT-style green guide sign: white retroreflective border and lettering (stills: Bahnschrift, a DIN 1451 cut)."""
    plano(w, h, (x, PORTICO_Y - 0.06, z), BLANCO_REFL, parent=False)
    plano(w - 0.16, h - 0.16, (x, PORTICO_Y - 0.07, z), VERDE_SCT, parent=False)
    texto(titulo, h * 0.36, (x, PORTICO_Y - 0.08, z + h * 0.08), BLANCO_REFL, parent=False)
    if sub:
        texto(sub, h * 0.15, (x, PORTICO_Y - 0.08, z - h * 0.28), BLANCO_REFL, parent=False)


@opcion("portico-a")
def portico_a():
    """A: steel truss gantry spanning the road, one big green sign over the band's lane (title + arrow line)."""
    for x in (-7.0, 9.0):
        cil(0.18, 6.4, (x, PORTICO_Y, 3.2), ACERO, verts=16, parent=False)
    for dz in (6.0, 7.2):
        caja((16.4, 0.12, 0.12), (1.0, PORTICO_Y + 0.25, dz), ACERO, parent=False)
    for i in range(14):
        caja((0.06, 0.06, 1.6), (-6.5 + i * 1.15, PORTICO_Y + 0.25, 6.6), ACERO, rot=(0, 0.75 if i % 2 else -0.75, 0), parent=False)
    letrero("REDES", "SÍGUENOS  ↑", CX, 6.1, 4.2, 2.0)
    return VISTA_PORTICO()


@opcion("portico-b")
def portico_b():
    """B: cantilever (bandera) sign: one pole on the right shoulder, the sign hanging over the lane."""
    cil(0.25, 7.2, (CX + 5.5, PORTICO_Y, 3.6), ACERO, verts=16, parent=False)
    caja((5.6, 0.25, 0.25), (CX + 2.8, PORTICO_Y + 0.2, 6.9), ACERO, parent=False)
    letrero("REDES", "SALIDA  2 km", CX + 1.2, 6.0, 3.6, 1.8)
    return VISTA_PORTICO()


@opcion("portico-c")
def portico_c():
    """C: the sign bolted to the side of a concrete puente peatonal (footbridge) with its railing and stair towers."""
    for x in (-8.0, 10.5):
        caja((1.2, 2.2, 6.0), (x, PORTICO_Y, 3.0), CONCRETO, parent=False)
    caja((19.7, 2.0, 0.6), (1.25, PORTICO_Y + 0.4, 5.8), CONCRETO, parent=False)
    for i in range(40):
        caja((0.04, 0.04, 1.1), (-8.0 + i * 0.47, PORTICO_Y - 0.55, 6.65), ACERO, parent=False)
    caja((19.7, 0.06, 0.06), (1.25, PORTICO_Y - 0.55, 7.2), ACERO, parent=False)
    letrero("REDES", "", CX, 4.7, 3.6, 1.4)
    plano(19.7, 0.4, (1.25, PORTICO_Y - 0.61, 5.6), mat("u_anuncio", (0.6, 0.6, 0.55), 0.6), parent=False)
    return VISTA_PORTICO()


VISTA_PLACA = lambda: ((CX + 0.35, DEFENSA.y + 2.4, 0.95), (CX, DEFENSA.y, 0.72), 45)
FILL_PLACA = lambda: relleno((CX + 0.8, DEFENSA.y + 3.0, 1.6), (CX, DEFENSA.y, 0.72), 40)


def placa_base(fondo, borde):
    p = Vector((CX, DEFENSA.y + 0.015, 0.72))
    plano(0.31, 0.16, p, borde, rot=(math.pi / 2, 0, math.pi))
    plano(0.30, 0.15, p + Vector((0, 0.002, 0)), fondo, rot=(math.pi / 2, 0, math.pi))
    return p + Vector((0, 0.004, 0))


ROT_P = (math.pi / 2, 0, math.pi)


@opcion("placa-a")
def placa_a():
    FILL_PLACA()
    """A: state-format plate (white field, state name on top, dark characters); the characters spell the band, not a real plate."""
    p = placa_base(mat("u_placa_blanca", (0.92, 0.92, 0.9), 0.35), mat("u_placa_marco", (0.6, 0.6, 0.6), 0.3, 1.0))
    texto("VERACRUZ", 0.022, p + Vector((0, 0, 0.05)), mat("u_vino", (0.45, 0.05, 0.1), 0.4), rot=ROT_P)
    texto("MT·420·VER", 0.055, p + Vector((0, 0, -0.005)), NEGRO, rot=ROT_P, ancho=0.85)
    texto("CONTRATACIONES", 0.014, p + Vector((0, 0, -0.055)), NEGRO, rot=ROT_P)
    return VISTA_PLACA()


@opcion("placa-b")
def placa_b():
    FILL_PLACA()
    """B: black-and-gold fantasy plate (placa de fantasía) with the band's monogram, like a custom show plate."""
    p = placa_base(CAP, ORO)
    texto("MAFIA", 0.05, p + Vector((0, 0, 0.018)), ORO, font="impact.ttf", rot=ROT_P)
    texto("TUMBADA", 0.03, p + Vector((0, 0, -0.035)), ORO, font="impact.ttf", rot=ROT_P, ancho=1.3)
    return VISTA_PLACA()


@opcion("placa-c")
def placa_c():
    FILL_PLACA()
    """C: a plain plate in a chrome frame whose lettering carries the call to action: CONTRÁTANOS · WHATSAPP."""
    p = placa_base(mat("u_placa_blanca", (0.92, 0.92, 0.9), 0.35), CROMO)
    plano(0.33, 0.025, p + Vector((0, 0.001, -0.088)), CROMO, rot=ROT_P)
    texto("CONTRÁTANOS · WHATSAPP", 0.013, p + Vector((0, 0.003, -0.088)), NEGRO, rot=ROT_P)
    texto("MT 420", 0.07, p + Vector((0, 0, 0.0)), NEGRO, rot=ROT_P, ancho=0.9)
    return VISTA_PLACA()


# bed props: seen from the end of the v3 move (high behind the bed, 28 mm)
c1 = T.CAMINO[-1]
VISTA_CAJA = lambda: ((CX - 0.5, -5.4, 2.9), (CX, -2.4, 1.15), 30)
Z0 = T.CAJA_Z


@opcion("caja-a")
def caja_a():
    """A: fiesta: inflatable donut with sprinkles, a classic red cooler with white lid, a 7-point star piñata."""
    dona = toro(0.30, 0.12, (CX + 0.45, -2.5, Z0 + 0.42), mat("u_dona", (0.95, 0.45, 0.6), 0.15), rot=(0.9, 0.3, 0))
    for i in range(10):
        a = i * 0.63
        caja((0.04, 0.012, 0.012), (CX + 0.45 + 0.3 * math.cos(a), -2.5 + 0.15 * math.sin(a), Z0 + 0.5 + 0.2 * math.sin(a)),
             mat(f"u_chispa_{i % 3}", ((1, 1, 1), (0.2, 0.6, 1.0), (1.0, 0.85, 0.1))[i % 3], 0.3), rot=(0, 0, a))
    caja((0.6, 0.4, 0.34), (CX - 0.55, -2.5, Z0 + 0.17), mat("u_hielera", (0.75, 0.05, 0.04), 0.3), bevel=0.03)
    caja((0.62, 0.42, 0.07), (CX - 0.55, -2.5, Z0 + 0.37), BLANCO, bevel=0.02)
    centro = (CX + 0.0, -2.2, Z0 + 0.75)
    esfera(0.2, centro, mat("u_pinata", (1.0, 0.2, 0.55), 0.6))
    for i in range(7):
        a = i * 2 * math.pi / 7
        d = Vector((math.cos(a), 0, math.sin(a)))
        cono(0.07, 0.0, 0.4, Vector(centro) + d * 0.32, mat(f"u_pico_{i % 3}", ((1, 0.8, 0.1), (0.1, 0.7, 0.9), (0.95, 0.35, 0.1))[i % 3], 0.6),
             rot=(0, math.atan2(d.x, d.z), 0))
    return VISTA_CAJA()


@opcion("caja-b")
def caja_b():
    """B: on tour: the instrument cases (tololoche case standing tall, an amp), road cases with stencilled MT, a cooler."""
    caja((0.45, 0.35, 1.25), (CX - 0.55, -2.3, Z0 + 0.62), NEGRO, bevel=0.05)
    caja((0.7, 0.45, 0.4), (CX + 0.4, -2.5, Z0 + 0.2), mat("u_road", (0.03, 0.03, 0.03), 0.5), bevel=0.01)
    for dx in (-0.35, 0.35):
        for dy in (-0.225, 0.225):
            caja((0.04, 0.04, 0.4), (CX + 0.4 + dx, -2.5 + dy, Z0 + 0.2), ACERO)
    texto("MT · GIRA", 0.09, (CX + 0.4, -2.5 + 0.0, Z0 + 0.41), ORO, rot=(0, 0, 0))
    caja((0.5, 0.3, 0.45), (CX + 0.1, -1.95, Z0 + 0.225), mat("u_amp", (0.04, 0.04, 0.04), 0.7), bevel=0.01)
    plano(0.42, 0.3, (CX + 0.1, -2.101, Z0 + 0.25), mat("u_rejilla", (0.15, 0.13, 0.1), 0.9))
    caja((0.5, 0.35, 0.32), (CX - 0.05, -2.75, Z0 + 0.16), mat("u_hielera_azul", (0.05, 0.2, 0.6), 0.3), bevel=0.03)
    caja((0.52, 0.37, 0.06), (CX - 0.05, -2.75, Z0 + 0.34), BLANCO, bevel=0.02)
    return VISTA_CAJA()


@opcion("caja-c")
def caja_c():
    """C: rancho party: a stack of plastic crates of beer, sombreros on top, a string of warm bulbs strung over the bed."""
    rojo = mat("u_rejas", (0.65, 0.05, 0.04), 0.5)
    for i, (dx, dz) in enumerate(((-0.5, 0), (-0.5, 0.3), (0.05, 0), (-0.22, 0.6))):
        caja((0.45, 0.32, 0.3), (CX + dx, -2.5, Z0 + 0.15 + dz), rojo, bevel=0.01)
        for j in range(6):
            cil(0.03, 0.22, (CX + dx - 0.15 + (j % 3) * 0.15, -2.55 + (j // 3) * 0.1, Z0 + 0.32 + dz), mat("u_vidrio_ambar", (0.4, 0.15, 0.02), 0.1, trans=0.6))
    paja = mat("u_paja", (0.75, 0.55, 0.25), 0.8)
    for x, z in ((CX - 0.22, Z0 + 0.92), (CX + 0.55, Z0 + 0.1)):
        cil(0.25, 0.015, (x, -2.5, z), paja)
        cono(0.1, 0.08, 0.14, (x, -2.5, z + 0.075), paja)
    foco = mat("u_foco", (1.0, 0.75, 0.4), 0.3, emit=12)
    for i in range(14):
        t = i / 13
        esfera(0.025, (CX - 0.85 + 1.7 * t, -1.3 - 1.6 * t, 1.9 - 0.25 * math.sin(math.pi * t)), foco)
    return VISTA_CAJA()


# ================================================================ round 2 (owner's picks 2026-11-13 02:51; handoff-fase1-ronda2.md)
PANTALLAS = os.path.join(REPO, "tmp", "utileria")  # faces from blender/pantalla_tablero.py (run it first)
CRISTAL = mat("u_bisel", (0.008, 0.008, 0.009), 0.18)


def cara_pantalla(w, h, loc, inclina, archivo):
    """Bezel + emissive screen face, top leaning back by `inclina` rad (towards +Y), facing the cabin."""
    rot = (math.pi / 2 - inclina, 0, 0)
    n = Vector((0, -math.cos(inclina), math.sin(inclina)))
    caja((w + 0.016, h + 0.016, 0.012), Vector(loc) - n * 0.004, CRISTAL, rot=rot, bevel=0.003)  # local XY = the face
    plano(w, h, Vector(loc) + n * 0.0025, img_mat("u_" + archivo, os.path.join(PANTALLAS, archivo + ".png"), emit=2.2, rough=0.15), rot=rot)


def techo_tablero(y):
    """Top of the dash on the centre line at depth y (ray down from inside the cab)."""
    p = rayo((CX, y, 1.78), (0, 0, -1))
    print("TECHO", y, p)
    return p.z if p else 1.62


@opcion("radio2-a")
def radio2_a():
    """(a) Floating wide screen on top of the dash, MBUX style (G-Class 2025 / Ram 14.5" rows); no cassette, no Tecla."""
    y = TABLERO.y + 0.06
    z = techo_tablero(y) + 0.095
    w = 0.36
    caja((0.05, 0.03, 0.06), (CX, y + 0.03, z - 0.07), CRISTAL, bevel=0.004)  # stem into the dash top
    cara_pantalla(w, w / 3, (CX, y, z), 0.12, "pantalla-ancha")
    return ((CX + 0.10, y - 0.62, z + 0.02), (CX, y, z - 0.10), 30)


@opcion("radio2-b")
def radio2_b():
    """(b) The screen built into the centre stack where the G63's small COMAND unit sits, between the vents. The Tecla is
    left out: beside this screen it lands on the right vent (round-2 first still), so it does not sit naturally."""
    z = 1.52
    p = rayo((CX, 0.75, z), (0, 1, 0)) or Vector((CX, 1.1, z))
    w = 0.17
    cara_pantalla(w, w * 9 / 16, (CX, p.y - 0.012, z), math.atan(0.40), "pantalla-comand")  # stack leans ~22° (PERFIL rays)
    return ((CX + 0.08, p.y - 0.52, z + 0.10), (CX, p.y, z - 0.04), 32)


# ---- plate: stylised after NOM-001-SCT-2-2016 (300×150 mm, r 14 mm corners, 3 mm rim, 4 slots 20×6 mm at 50 mm from the
# sides and 10 mm from top/bottom, embossed characters 2 mm, legends ≤ 18 mm) and the Veracruz layout (unotv 2025: state
# name top, characters centre, state name bottom beside a yellow figure). Mothership 02:53: no seals, no QR.
def rect_redondo(w, h, r, loc, m, grosor=0.0015, segs=6):
    import bmesh
    me = bpy.data.meshes.new("placa")
    bm = bmesh.new()
    vs = []
    for cx, cz, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(segs + 1):
            a = math.radians(a0 + 90 * k / segs)
            vs.append(bm.verts.new((cx + r * math.cos(a), 0, cz + r * math.sin(a))))
    f = bm.faces.new(vs)
    bmesh.ops.solidify(bm, geom=[f], thickness=grosor)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("placa", me)
    sc.collection.objects.link(o)
    o.location = loc
    return _fin(o, m, None)


def placa2(centro, abajo, ancho_c=0.85):
    FILL_PLACA()
    y = DEFENSA.y + 0.016
    p = Vector((CX, y, 0.72))
    rect_redondo(0.300, 0.150, 0.014, p, mat("u_placa_alu", (0.75, 0.75, 0.74), 0.35, 1.0))
    rect_redondo(0.294, 0.144, 0.011, p + Vector((0, 0.0012, 0)), mat("u_placa_blanca", (0.92, 0.92, 0.9), 0.35))
    f = p + Vector((0, 0.0026, 0))
    for sx in (-1, 1):
        for sz in (-1, 1):
            plano(0.020, 0.006, f + Vector((sx * (0.150 - 0.060), 0.0004, sz * (0.075 - 0.013))), NEGRO_MATE, rot=ROT_P)
    texto("VERACRUZ", 0.016, f + Vector((0, 0, 0.046)), NEGRO, rot=ROT_P)
    texto(centro, 0.056, f + Vector((0, 0, 0.0)), NEGRO, rot=ROT_P, extr=0.001, ancho=ancho_c)  # embossed 2 mm
    texto(abajo, 0.013, f + Vector((0.012, 0, -0.050)), NEGRO, rot=ROT_P)
    amarillo = mat("u_amarillo_placa", (1.0, 0.72, 0.02), 0.4)
    bx = 0.012 + 0.0039 * len(abajo) + 0.014  # world +x reads as the plate's left (ROT_P turns it to face +Y)
    plano(0.018, 0.010, f + Vector((bx, 0.0003, -0.050)), amarillo, rot=ROT_P)  # the yellow figure, as a plain bar
    return VISTA_PLACA()


@opcion("placa2-a")
def placa2_a():
    """A1: the round-1 characters (MT·420·VER) and CONTRATACIONES at the bottom beside the yellow figure."""
    return placa2("MT·420·VER", "CONTRATACIONES")


@opcion("placa2-b")
def placa2_b():
    """A2: the band name in place of the number; the bottom repeats the state name, as the official layout does."""
    return placa2("TUMBADA", "VERACRUZ", ancho_c=0.9)


# ---- bed props A, fuller: donut, cooler, piñata kept; a pyramid peaking at the piñata. Two cameras: VISTA_CAJA and the
# scene-2 framing (T.CAMINO[-1], v3 f191), where readability is judged.
VISTA_ESC2 = lambda: (c1[1], c1[2], c1[3])
Y0, YC = -2.15, -1.38  # bed centre; roll bar (from the caja-c bulb string anchor)
ROSA, LIMA, TURQ = (1.0, 0.2, 0.55), (0.55, 0.9, 0.1), (0.1, 0.75, 0.85)


def pinata(c, r=0.2):
    esfera(r, c, mat("u_pinata", ROSA, 0.6))
    for i in range(7):
        a = i * 2 * math.pi / 7
        d = Vector((math.cos(a), 0, math.sin(a)))
        cono(r * 0.35, 0.0, r * 2, Vector(c) + d * r * 1.6, mat(f"u_pico_{i % 3}", ((1, 0.8, 0.1), TURQ, (0.95, 0.35, 0.1))[i % 3], 0.6),
             rot=(0, math.atan2(d.x, d.z), 0))


def dona(c, rot, color=(0.95, 0.45, 0.6), nombre="u_dona", R=0.30, r=0.12):
    toro(R, r, c, mat(nombre, color, 0.15), rot=rot)


def hielera(c):
    caja((0.6, 0.4, 0.34), Vector(c) + Vector((0, 0, 0.17)), mat("u_hielera", (0.75, 0.05, 0.04), 0.3), bevel=0.03)
    caja((0.62, 0.42, 0.07), Vector(c) + Vector((0, 0, 0.37)), BLANCO, bevel=0.02)


def pelota(c, r=0.17):
    """Beach ball: six coloured gores read as bands from above (a sphere with a band material would need UVs)."""
    for i, col in enumerate(((1, 1, 1), (0.9, 0.1, 0.1), (1, 0.8, 0.1), (0.1, 0.4, 0.9))):
        o = esfera(r * (1 + 0.012 * i), c, mat(f"u_pelota_{i}", col, 0.25), scale=(1, 0.3, 1) if i else (1, 1, 1))
        o.rotation_euler = (0, 0, i * math.pi / 4)


def globos(base, n, alto=0.75):
    hilo = mat("u_hilo", (0.9, 0.9, 0.9), 0.5)
    for i in range(n):
        a = i * 2.4
        top = Vector(base) + Vector((0.12 * math.cos(a), 0.12 * math.sin(a), alto + 0.08 * (i % 3)))
        esfera(0.11, top, mat(f"u_globo_{i % 4}", ((1, 0.8, 0.1), ROSA, TURQ, (0.95, 0.95, 0.95))[i % 4], 0.12), scale=(1, 1, 1.18))
        d = top - Vector(base)
        cil(0.002, d.length, Vector(base) + d / 2, hilo, rot=(0, math.atan2(math.hypot(d.x, d.y), d.z), math.atan2(d.y, d.x) + math.pi / 2), verts=6)


def bocina(c):
    caja((0.22, 0.18, 0.34), Vector(c) + Vector((0, 0, 0.17)), mat("u_bocina", (0.03, 0.03, 0.035), 0.5), bevel=0.02)
    for dz, r in ((0.22, 0.065), (0.08, 0.035)):
        cil(r, 0.01, Vector(c) + Vector((0, -0.092, dz)), mat("u_cono", (0.08, 0.08, 0.08), 0.7), rot=(math.pi / 2, 0, 0))
    toro(0.07, 0.006, Vector(c) + Vector((0, -0.095, 0.22)), mat("u_aro_led", TURQ, emit=4.0), rot=(math.pi / 2, 0, 0))


def maracas(c):
    for k, col in enumerate(((0.95, 0.35, 0.1), (0.1, 0.6, 0.3))):
        p = Vector(c) + Vector((k * 0.08, 0, 0.03))
        esfera(0.045, p, mat(f"u_maraca_{k}", col, 0.4), scale=(1.2, 1, 1))
        cil(0.01, 0.14, p + Vector((0.1, 0, 0)), mat("u_mango", (0.6, 0.4, 0.2), 0.6), rot=(0, math.pi / 2, 0.3 * k))


def sombrero(c, rot=(0, 0, 0)):
    paja = mat("u_paja", (0.75, 0.55, 0.25), 0.8)
    cil(0.25, 0.015, c, paja, rot=rot)
    cono(0.1, 0.08, 0.14, Vector(c) + Vector((0, 0, 0.075)), paja, rot=rot)


@opcion("caja2-a")
def caja2_a():
    """A1 stacked pyramid: cooler + speaker as the base, the donut standing behind, the piñata on top as the peak;
    beach ball, lime ring, maracas and sombrero at the base corners; two balloon bunches tied to the roll bar ends."""
    hielera((CX - 0.1, Y0, Z0))
    bocina((CX + 0.42, Y0 - 0.05, Z0))
    dona((CX - 0.05, Y0 + 0.3, Z0 + 0.42), (math.radians(80), 0, 0))
    pinata((CX - 0.08, Y0 + 0.05, Z0 + 0.92), 0.18)
    pelota((CX + 0.48, Y0 - 0.5, Z0 + 0.17))
    dona((CX - 0.45, Y0 - 0.3, Z0 + 0.08), (0.15, 0, 0), LIMA, "u_dona_lima", 0.2, 0.08)  # inside the tailgate (y ≥ -2.75)
    maracas((CX + 0.25, Y0 - 0.48, Z0 + 0.01))
    sombrero((CX - 0.1, Y0 - 0.02, Z0 + 0.45), rot=(0.15, -0.2, 0))
    for x in (CX - 0.7, CX + 0.7):
        globos((x, YC, 1.65), 4)
    return VISTA_CAJA()


@opcion("caja2-a-esc2")
def caja2_a_esc2():
    caja2_a()
    return VISTA_ESC2()


@opcion("caja2-b")
def caja2_b():
    """A2 hanging peak: the piñata hangs from the middle of the roll bar on a rope, balloons rise from the bar beside it,
    a low pile below (donut flat on the cooler, beach ball, lime ring, speaker, sombrero, maracas)."""
    hielera((CX - 0.35, Y0 - 0.1, Z0))
    dona((CX - 0.35, Y0 - 0.1, Z0 + 0.52), (0.1, 0.05, 0))
    bocina((CX + 0.45, Y0 + 0.35, Z0))
    pelota((CX + 0.02, Y0 - 0.45, Z0 + 0.17))
    dona((CX + 0.45, Y0 - 0.3, Z0 + 0.08), (0.2, 0, 0.4), LIMA, "u_dona_lima", 0.2, 0.08)
    sombrero((CX - 0.55, Y0 + 0.4, Z0 + 0.02))
    maracas((CX - 0.1, Y0 + 0.4, Z0 + 0.01))
    pinata((CX, YC - 0.35, Z0 + 1.05), 0.2)
    cil(0.004, 0.62, (CX, YC - 0.18, Z0 + 1.45), mat("u_hilo", (0.9, 0.9, 0.9), 0.5), rot=(0.55, 0, 0), verts=6)
    for x in (CX - 0.45, CX + 0.45):
        globos((x, YC, 1.85), 5, alto=0.8)
    return VISTA_CAJA()


@opcion("caja2-b-esc2")
def caja2_b_esc2():
    caja2_b()
    return VISTA_ESC2()


# ---- glovebox C: the door cut out of the G63 mesh. Destructive for the dash: these options must stay last in the file.
CORTE = {}
CORTE_BOX = ((1.95, 2.35), (1.15, 1.30), (1.15, 1.38))
GIRO = math.radians(70)


def cortar_guantera():
    import bmesh
    from mathutils import Matrix
    if CORTE:
        for o in CORTE["objs"]:
            o.hide_render = False
            GRUPO.append(o)
        return CORTE
    (x0, x1), (y0, y1), (z0, z1) = CORTE_BOX
    dentro = lambda v: x0 <= v.x <= x1 and y0 <= v.y <= y1 and z0 <= v.z <= z1
    puertas, todos = [], []
    for o in [o for o in CAM.children_recursive if o.type == "MESH"]:
        mw = o.matrix_world
        idx = [f.index for f in o.data.polygons if dentro(mw @ f.center)]
        if not idx:
            continue
        o.data = o.data.copy()  # single user
        sel = set(idx)
        puerta = o.copy()
        puerta.data = o.data.copy()
        sc.collection.objects.link(puerta)
        for ob, quitar in ((o, lambda i: i in sel), (puerta, lambda i: i not in sel)):
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            bm.faces.ensure_lookup_table()
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if quitar(f.index)], context="FACES")
            bm.to_mesh(ob.data)
            bm.free()
        puertas.append(puerta)
        todos += [mw @ v.co for v in puerta.data.vertices]
        print("CORTE", o.name, len(idx), "caras")
    if not todos:
        raise RuntimeError("CORTE: no faces in the glovebox box")
    lo = Vector((min(v.x for v in todos), min(v.y for v in todos), min(v.z for v in todos)))
    hi = Vector((max(v.x for v in todos), max(v.y for v in todos), max(v.z for v in todos)))
    print("CORTE bbox", lo, hi)
    piv = Vector(((lo.x + hi.x) / 2, min(v.y for v in todos if v.z < lo.z + 0.01), lo.z))
    giro = Matrix.Translation(piv) @ Matrix.Rotation(GIRO, 4, "X") @ Matrix.Translation(-piv)
    bpy.context.view_layer.update()
    for pt in puertas:
        mw = pt.matrix_world.copy()
        pt.parent = None
        pt.matrix_world = giro @ mw
    w, h = hi.x - lo.x, hi.z - lo.z
    # inner liner of the door (the cut skin has no inside), turned with it
    # the cut faces run 0.2 m deep (round-2 first still), so the liner hangs off the hinge line, not off the deepest face
    liner = caja((w - 0.01, 0.008, h - 0.01), (piv.x, piv.y + 0.03, lo.z + h / 2), mat("u_guantera_int", (0.03, 0.028, 0.026), 0.8), parent=False)
    bpy.context.view_layer.update()
    liner.matrix_world = giro @ liner.matrix_world
    # the dark inner box, open towards the cabin, its rim on the cut edges
    hueco = mat("u_hueco", (0.006, 0.006, 0.006), 0.9)
    yb, prof, t = lo.y, 0.20, 0.006
    cx, cz = (lo.x + hi.x) / 2, (lo.z + hi.z) / 2
    caja((w, t, h), (cx, yb + prof, cz), hueco, parent=False)
    caja((w, prof, t), (cx, yb + prof / 2, hi.z), hueco, parent=False)
    caja((w, prof, t), (cx, yb + prof / 2, lo.z), hueco, parent=False)
    for sx in (lo.x, hi.x):
        caja((t, prof, h), (sx, yb + prof / 2, cz), hueco, parent=False)
    luz("POINT", (cx, yb + 0.1, hi.z - 0.03), 2.0, (1.0, 0.8, 0.55), parent=False)
    luz("AREA", (cx - 0.1, yb - 0.45, hi.z + 0.2), 6.0, (1.0, 0.85, 0.65), mira=(cx, yb - 0.1, lo.z), size=0.2, parent=False)
    n = giro.to_3x3() @ Vector((0, 1, 0))  # the door's inside, now facing up
    centro = giro @ Vector((piv.x, piv.y + 0.034, lo.z + h / 2))
    CORTE.update(objs=puertas + list(GRUPO), centro=centro, n=n, lo=lo, hi=hi)
    for pt in puertas:
        GRUPO.append(pt)
    return CORTE


@opcion("guantera2-borde")
def guantera2_borde():
    """Close still of the cut edges, before the junk goes in."""
    c = cortar_guantera()
    lo, hi = c["lo"], c["hi"]
    return ((CX + 0.15, lo.y - 0.40, hi.z + 0.08), ((lo.x + hi.x) / 2, lo.y, (lo.z + hi.z) / 2), 30)


@opcion("guantera2-c")
def guantera2_c():
    """C on the cut door: a loose cassette, picks, a crumpled set list, sunglasses."""
    from mathutils import Matrix
    c = cortar_guantera()
    antes = len(GRUPO)
    guantera_c_basura(Vector((0, 0, 0)))
    M = Matrix.Translation(c["centro"] + c["n"] * 0.004) @ Vector((0, 0, 1)).rotation_difference(c["n"]).to_matrix().to_4x4()
    bpy.context.view_layer.update()
    for o in GRUPO[antes:]:
        o.matrix_world = M @ o.matrix_world
    return VISTA_GUANTERA()


def guantera_c_basura(p):
    caja((0.1, 0.064, 0.012), p + Vector((-0.08, 0, 0.008)), mat("u_casete", (0.05, 0.05, 0.06), 0.2), rot=(0, 0, 0.3))
    plano(0.07, 0.03, p + Vector((-0.08, 0, 0.0145)), img_mat("u_cover_g2", COVER, emit=0.4), rot=(0, 0, 0.3))
    for i in range(4):
        cil(0.012, 0.002, p + Vector((0.0 + i * 0.025, -0.03 + (i % 2) * 0.03, 0.004)), ORO if i % 2 else mat("u_pua", (0.8, 0.1, 0.1), 0.3), verts=3)
    esfera(0.04, p + Vector((0.1, 0.03, 0.02)), BLANCO, scale=(1.2, 1.0, 0.5))
    for dx in (-0.025, 0.025):
        cil(0.02, 0.004, p + Vector((0.06 + dx, -0.04, 0.02)), mat("u_lente", (0.02, 0.02, 0.02), 0.05), rot=(1.2, 0, 0))


# ---------------------------------------------------------------- render
os.makedirs(OUT, exist_ok=True)
for nombre, f in OPC.items():
    if SOLO and nombre not in SOLO:
        continue
    t1 = time.time()
    GRUPO.clear()
    pos, mira, lens = f()
    ocultos = {"guantera": ("hector",), "caja": ("alejandro", "diego")}.get(nombre.split("-")[0].rstrip("2"), ())
    for o in FIGURAS:  # Héctor sits over the glovebox; v3 seats Alexandro and Diego in the bed (plan: rear seats)
        if o.name.split("_")[0].split(".")[0] in ocultos:
            o.hide_render = True
    cd = bpy.data.cameras.new("cam_" + nombre)
    cd.clip_start, cd.clip_end, cd.lens, cd.sensor_fit = 0.01, 3000, lens, "HORIZONTAL"
    co = bpy.data.objects.new("cam_" + nombre, cd)
    sc.collection.objects.link(co)
    co.location = Vector(pos)
    co.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = RW, RH, 100
    sc.render.filepath = os.path.join(OUT, nombre + ".png")
    bpy.ops.render.render(write_still=True)
    for o in GRUPO:
        o.hide_render = True
    for o in FIGURAS:
        o.hide_render = False
    print("TOMA", nombre, round(time.time() - t1, 1), "s")
