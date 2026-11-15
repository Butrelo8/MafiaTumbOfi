"""Bed B dressed with more props (caja5), owner 11-14: "Need to see if we keep adding more props, they can be irrelevant to the
genre but must look good." Twelve candidates, each built by script at real size, shown alone in studio light (caja5-estudio-*),
and three amounts of them on bed B (ligera, media, llena) in the close-up and the scene-2 camera. Sources: references.md › More
props on bed B.

Runs caja4.py's props, bed B and checks (which run caja3.py and utileria.py's scene), adds its options, then utileria.py's render
loop:

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/caja5.py)" \
    -- <escena.py path (Windows)> <out_dir (Windows)> [samples] <options> [WxH]

Options: caja5-estudio-<prop> (one per candidate; render them 1:1), caja5-<variant> (the close-up) and caja5-<variant>-esc2
(scene 2's hold, measured: CAJA5 MEDIDA lines), variant in ligera, media, llena. Through WSLENV: CAJA5_SONDA=1 prints the roll-bar probe; CAJA5_CPU=1 renders on the CPU.
"""
import bpy, bmesh, math, os, json
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

C4 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caja4.py")
_c4 = open(C4, encoding="utf8").read().rsplit("# ---------------------------------------------------------------- utileria.py's render loop", 1)[0]  # rsplit: caja4 quotes the marker
exec(compile(_c4, C4, "exec"), globals())

# ---------------------------------------------------------------- the roll bar (sport bar), measured
# Rays down over the bed with the load and the riders hidden (CAJA5_SONDA=1, tmp/caja5/sonda.log, 2026-11-14): no crossbar. Two
# tubes, ~8 cm hit width, run from the cab roof's rear edge (x ±0.36, y -1.10, top z 2.22) back, down and out to the bed sides
# (x ±0.76, y -2.30, z 1.64), where they meet the body's top ledge (x ±0.78, z 1.61), which runs back to the tailgate top
# (y -2.80, z 1.61). Cab roof z 2.24-2.25.
TUBO_A, TUBO_B = (0.36, -1.13, 2.19), (0.75, -2.27, 1.70)  # centre line of the right tube (x mirrored for the left), r ~0.03
LEDGE_Z = 1.61
TECHO_Z = 2.247


def tubo(t, lado):
    """Point on a sport-bar tube's centre line, t 0 (cab) .. 1 (bed side); lado -1 left, +1 right."""
    a, b = Vector(TUBO_A), Vector(TUBO_B)
    p = a.lerp(b, t)
    return Vector((CX + lado * p.x, p.y, p.z))


if os.environ.get("CAJA5_SONDA"):
    _ocultos = [c for o in bpy.data.objects if o.name.split(".")[0].startswith(("estuche_", "guitarra_")) or o in FIGURAS
                for c in [o] + list(o.children_recursive)]
    for o in _ocultos:
        o.hide_viewport = True
    _g["dg"] = bpy.context.evaluated_depsgraph_get()
    for y in [YF + 0.1 - 0.05 * i for i in range(40)]:
        hits = [(round(x - CX, 2), round(h.z, 2)) for x in [CX - 0.8 + 0.02 * i for i in range(81)] for h in [rayo((x, y, 3.2), (0, 0, -1))]
                if h and h.z > RIEL + 0.05]
        tramos, prev = [], None
        for x, z in hits:
            if prev is not None and x - prev < 0.025:
                tramos[-1] = (tramos[-1][0], x, max(tramos[-1][2], z))
            else:
                tramos.append((x, x, z))
            prev = x
        print(f"CAJA5 barra y {y:.3f} " + " ".join(f"[{a:+.2f}..{b:+.2f} z{z:.2f}]" for a, b, z in tramos))
    for o in _ocultos:
        o.hide_viewport = False
    _g["dg"] = bpy.context.evaluated_depsgraph_get()

# ---------------------------------------------------------------- materials: the DESIGN.md palette (black, warm white, gold) plus
# the donut's pink as the one accent (props-placement rule 7: gold/amber and one accent at night)
ORO5 = gastado3("k5_oro", (0.91, 0.71, 0.32), 0.22, (0.98, 0.85, 0.55), 0.15, metal=1.0)   # gold foil, #e7b551
NEGRO5 = gastado3("k5_negro", (0.015, 0.015, 0.016), 0.45, (0.09, 0.09, 0.09), 0.5)
ROSA5 = mat("k5_rosa", (0.95, 0.45, 0.6), 0.35)                                             # the donut's pink
CREMA = gastado3("k5_crema", (0.82, 0.77, 0.64), 0.3, (0.6, 0.55, 0.45), 0.5, coat=0.6)     # surfboard glass over cream foam
BOLSA = mat("k5_bolsa", (1.0, 1.0, 1.0), 0.05, alpha=0.07)                               # clear poly bag
FOCO = mat("k5_foco", (1.0, 0.78, 0.5), 0.2, emit=6.0, ecolor=(1.0, 0.72, 0.42))           # 2200 K festoon bulb
NEON = mat("k5_neon", (1.0, 0.75, 0.35), 0.2, emit=9.0, ecolor=(1.0, 0.72, 0.3))           # gold LED neon flex
CABLE5 = mat("k5_cable", (0.01, 0.01, 0.01), 0.5)


# ---------------------------------------------------------------- the twelve candidates (real sizes; references.md › More props)
def pinata_bolsa():
    """Star piñata (owner's earlier pick, removed for the drive), Ø 0.60 m point to point: a foil sphere and five foil cones in
    gold and black, pink tissue fringe at the tips, laid flat in a clear bag tied at one end, as a party store bags it."""
    c = Vector((0, 0, 0.15))
    esfera(0.15, c, ORO5, parent=F)
    for i in range(5):
        a = i * 2 * math.pi / 5
        d = Vector((math.cos(a), math.sin(a), 0))
        cono(0.065, 0.0, 0.18, c + d * 0.20, ORO5 if i % 2 == 0 else NEGRO5, rot=(0, math.pi / 2, a), parent=F)
        for k in (-1, 0, 1):
            plano(0.02, 0.07, c + d * 0.28 + Vector((0, 0, -0.07 + 0.003 * k)), ROSA5, rot=(0, 0, a + math.pi / 2 + 0.25 * k), parent=F)
    caja((0.64, 0.64, 0.30), (0, 0, 0.15), BOLSA, bevel=0.1, parent=F)  # the bag, a soft pillow shape
    cono(0.035, 0.012, 0.06, (-0.18, -0.34, 0.15), BOLSA, rot=(math.pi / 2, 0, 0), parent=F)  # the twisted neck, to the back
    cil(0.013, 0.012, (-0.18, -0.375, 0.15), ORO5, rot=(math.pi / 2, 0, 0), parent=F)          # its twist tie


def globos_bolsa():
    """Balloon transport bag, 0.86 × 0.58 × 0.32 m: six 11-inch balloons in one layer (gold foil, black and one pink latex) inflated at the
    shop and carried in a clear bag, as balloon shops send them by car; tied shut."""
    for x, y, m in ((-0.27, -0.13, ORO5), (0.0, -0.13, NEGRO5), (0.27, -0.13, ORO5), (-0.27, 0.13, NEGRO5), (0.0, 0.13, ROSA5),
                    (0.27, 0.13, ORO5)):
        esfera(0.13, (x, y, 0.155), m, scale=(1.0, 1.0, 0.95), parent=F)
    caja((0.86, 0.58, 0.32), (0, 0, 0.16), BOLSA, bevel=0.1, parent=F)
    cono(0.04, 0.014, 0.07, (0.30, -0.32, 0.16), BOLSA, rot=(math.pi / 2, 0, 0), parent=F)
    cil(0.015, 0.012, (0.30, -0.36, 0.16), ORO5, rot=(math.pi / 2, 0, 0), parent=F)


def picado5(a, b, n=7, caida=0.03):
    """A string of plastic papel picado (owner's earlier pick), panels 0.15 × 0.17 m in gold, pink and warm white, punched pattern
    as alpha, zip-tied taut at both ends so it flutters but cannot fly off."""
    a, b = Vector(a), Vector(b)
    cols = ((0.91, 0.71, 0.32), (0.95, 0.45, 0.6), (0.95, 0.92, 0.85))
    for i in range(n):
        t = (i + 0.5) / n
        p = a.lerp(b, t) - Vector((0, 0, caida * 4 * t * (1 - t)))
        nombre = f"k5_picado_{i % 3}"
        m = MATS.get(nombre)
        if not m:
            col = cols[i % 3]
            m = bpy.data.materials.new(nombre)
            m.use_nodes = True
            nt = m.node_tree
            bs = nt.nodes["Principled BSDF"]
            bs.inputs["Base Color"].default_value = (*col, 1)
            bs.inputs["Roughness"].default_value = 0.35
            bs.inputs["Emission Color"].default_value = (*col, 1)
            bs.inputs["Emission Strength"].default_value = 0.12
            vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 9.0
            gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.22
            nt.links.new(vo.outputs["Distance"], gt.inputs[0])
            nt.links.new(gt.outputs["Value"], bs.inputs["Alpha"])
            MATS[nombre] = m
        d = (b - a).normalized()
        plano(0.15, 0.17, p - Vector((0, 0, 0.09)), m, rot=(math.pi / 2 - 0.25, 0, math.atan2(d.y, d.x)), parent=F)  # leaning back in the wind
    for k in range(8):
        t0, t1 = k / 8, (k + 1) / 8
        p0 = a.lerp(b, t0) - Vector((0, 0, caida * 4 * t0 * (1 - t0)))
        p1 = a.lerp(b, t1) - Vector((0, 0, caida * 4 * t1 * (1 - t1)))
        dd = p1 - p0
        cil(0.002, dd.length, p0 + dd / 2, mat("u_hilo", (0.9, 0.9, 0.9), 0.5),
            rot=(0, math.atan2(math.hypot(dd.x, dd.y), dd.z), math.atan2(dd.y, dd.x)), verts=6, parent=F)
    for p in (a, b):
        caja((0.012, 0.03, 0.03), p, CABLE5, parent=F)  # zip ties


def luces5(puntos, paso=0.24, cuelga=0.05):
    """Festoon string lights (S14-style warm bulbs, 2200 K) on black cable, zip-tied along a path every ~0.3 m; between ties the
    cable sags and each bulb hangs on a short pigtail: the warm outline lights of props-placement rule 7."""
    puntos = [Vector(p) for p in puntos]
    largo = sum((puntos[i + 1] - puntos[i]).length for i in range(len(puntos) - 1))
    n = max(2, int(largo / 0.02))

    def en(s):
        for i in range(len(puntos) - 1):
            L = (puntos[i + 1] - puntos[i]).length
            if s <= L or i == len(puntos) - 2:
                return puntos[i].lerp(puntos[i + 1], min(1.0, s / L))
            s -= L

    sag = lambda s: 0.025 * math.sin(math.pi * ((s % 0.3) / 0.3))
    pts = [en(largo * k / n) - Vector((0, 0, sag(largo * k / n))) for k in range(n + 1)]
    for p0, p1 in zip(pts, pts[1:]):
        dd = p1 - p0
        cil(0.0035, dd.length, p0 + dd / 2, CABLE5, rot=(0, math.atan2(math.hypot(dd.x, dd.y), dd.z), math.atan2(dd.y, dd.x)), verts=6, parent=F)
    s = paso / 2
    while s < largo:
        p = en(s) - Vector((0, 0, sag(s)))
        cil(0.004, cuelga, p - Vector((0, 0, cuelga / 2)), CABLE5, verts=6, parent=F)
        cil(0.009, 0.02, p - Vector((0, 0, cuelga + 0.005)), CABLE5, verts=10, parent=F)
        esfera(0.019, p - Vector((0, 0, cuelga + 0.03)), FOCO, scale=(1, 1, 1.25), parent=F)
        s += paso


def bandera5():
    """The band flag (owner's earlier pick, caja3's bandera3: MT shield on black, 0.90 × 0.60 m) on a 1.5 m pole, for a bed's
    stake pocket, as flags ride on pickups (references: two pickups with a bed-mounted flag)."""
    bandera3()


def bocina5():
    """Battery party speaker, 0.36 × 0.34 × 0.72 m (caja3's tower), its woofer rings in gold and pink; it rides lying on its
    back on the load, rings up, under the net."""
    caja((0.36, 0.34, 0.72), (0, 0, 0.36), gastado3("k3_bocina", (0.025, 0.025, 0.028), 0.55, (0.12, 0.12, 0.13), 0.4), bevel=0.02, parent=F)
    for z, r, col in ((0.48, 0.13, (1.0, 0.7, 0.3)), (0.2, 0.12, (0.95, 0.45, 0.6))):
        cil(r, 0.01, (0, -0.172, z), GOMA, rot=(math.pi / 2, 0, 0), parent=F)
        toro(r + 0.01, 0.007, (0, -0.176, z), mat(f"k5_led_{z}", col, emit=0.8), rot=(math.pi / 2, 0, 0), parent=F)
    caja((0.22, 0.05, 0.04), (0, 0, 0.74), GOMA, bevel=0.015, parent=F)


def tabla():
    """7'0" funboard, 2.13 × 0.56 × 0.07 m, cream with a gold stringer and black fins, carried deck down and fins up on a soft
    pad, the way surfers on the Veracruz coast carry a board over a pickup's cab (references: lifeguard pickups with boards on
    the rack). Built as it rides: deck down, fins up, nose toward +y."""
    o = esfera(1, (0, 0, 0.035), CREMA, scale=(0.28, 1.065, 0.035), parent=F)
    caja((0.006, 2.0, 0.002), (0, 0, 0.0005), ORO5, parent=F)  # the stringer, on the deck (now underneath)
    caja((0.006, 1.9, 0.002), (0, 0, 0.0695), ORO5, parent=F)  # and through the bottom, which faces up
    for x, y, h in ((0, -0.95, 0.12), (-0.16, -0.82, 0.10), (0.16, -0.82, 0.10)):
        cono(0.06, 0.006, h, (x, y, 0.07 + h / 2), NEGRO5, verts=3, rot=(0, 0, math.pi / 2), parent=F)


def sombrerera5():
    """Hat box for a tejana (caja3's), Ø 0.50 m, black card, PURA MT on the lid: the singer's hat travels boxed."""
    sombrerera()


def cerveza():
    """Plastic crate of 12 amber bottles, 0.46 × 0.32 × 0.30 m, generic yellow, two bottles gone (caja3's rejilla)."""
    rejilla(2)


def sillas():
    """Two low beach chairs folded flat, 0.55 × 0.80 × 0.05 m each: black aluminium frame, gold and black striped fabric."""
    for k in range(2):
        z, dx = 0.025 + 0.052 * k, 0.015 * k
        for sx in (-1, 1):
            cil(0.011, 0.80, (dx + sx * 0.265, 0, z), NEGRO5, rot=(math.pi / 2, 0, 0), verts=10, parent=F)
        for sy in (-1, 1):
            cil(0.011, 0.55, (dx, sy * 0.39, z), NEGRO5, rot=(0, math.pi / 2, 0), verts=10, parent=F)
        for i in range(8):
            caja((0.505, 0.085, 0.004), (dx, -0.33 + i * 0.094, z + 0.01), ORO5 if i % 2 == 0 else NEGRO5, parent=F)


def bidon():
    """20 L steel jerry can, 0.345 × 0.165 × 0.47 m, black, the X pressed into both faces, three handles and the cap; it rides
    in a bolt-on holder (a steel tray and a strap), as cans ride on a jeep (reference: Willys MB)."""
    W, D, H = 0.345, 0.165, 0.47
    caja((W, D, H), (0, 0, H / 2), NEGRO5, bevel=0.012, parent=F)
    for sy in (-1, 1):
        for s in (-1, 1):
            caja((0.035, 0.008, 0.46), (0, sy * D / 2, H * 0.47), NEGRO5, rot=(0, s * 0.62, 0), parent=F)
    for x in (-0.09, 0.0, 0.09):
        caja((0.02, 0.03, 0.06), (x, 0, H + 0.03), NEGRO5, bevel=0.006, parent=F)
    caja((0.22, 0.03, 0.02), (0, 0, H + 0.065), NEGRO5, bevel=0.008, parent=F)
    cil(0.025, 0.04, (W * 0.36, 0, H + 0.02), ORO5, verts=16, parent=F)  # the cap
    caja((W + 0.03, D + 0.03, 0.01), (0, 0, -0.005), ACERO, parent=F)       # holder tray
    caja((W + 0.03, 0.006, 0.12), (0, D / 2 + 0.015, 0.05), ACERO, parent=F)
    caja((0.03, D + 0.04, 0.004), (0, 0, H * 0.75), CINTA_N, parent=F)


def neon5():
    """LED neon sign, MT in gold flex on a 0.62 × 0.30 m black acrylic back, battery powered, bolted between the sport-bar tubes
    facing back; built facing -y."""
    caja((0.62, 0.02, 0.30), (0, 0.01, 0.15), NEGRO5, bevel=0.01, parent=F)
    t = texto("MT", 0.24, (0, -0.004, 0.15), NEON, font="impact.ttf", rot=(math.pi / 2, 0, 0), parent=F)
    t.data.fill_mode = "NONE"
    t.data.bevel_depth = 0.0045
    for sx in (-1, 1):
        caja((0.06, 0.04, 0.03), (sx * 0.33, 0.03, 0.15), ACERO, parent=F)  # tube clamps


# ---------------------------------------------------------------- placement on bed B
NUEVOS = []  # objects added by caja5 in the current option (the ones rule 1 and rule 3 measure)


def encima(nombre, f, kg, cx, cy, rot=(0, 0, 0)):
    """Lay a prop on top of the load at (cx, cy): it rests on the highest point under its footprint (9 × 9 rays); joins CARGA,
    so the net goes over it and revisar_carga checks it."""
    o = unir(nombre, f, (cx, cy, PZ + 3.0), rot)
    bpy.context.view_layer.update()  # unir sets the location; matrix_world lags until an update
    lo, hi = caja_de(o)
    o.location += Vector((cx - (lo.x + hi.x) / 2, cy - (lo.y + hi.y) / 2, 0))
    bpy.context.view_layer.update()
    lo, hi = caja_de(o)
    z = max(alto_en(lo.x + (hi.x - lo.x) * i / 8, lo.y + (hi.y - lo.y) * j / 8) for i in range(9) for j in range(9))
    for q, *_ in CARGA:  # and over the boxes under its footprint: a bag on a road case rests on the ball corners
        lo2, hi2 = caja_de(q)
        if min(hi.x, hi2.x) - max(lo.x, lo2.x) > 0.01 and min(hi.y, hi2.y) - max(lo.y, lo2.y) > 0.01:
            z = max(z, hi2.z)
    poner(o, z0=z + 0.004)
    CARGA.append((o, nombre, kg))
    NUEVOS.append(o)
    return o


def montar(nombre, f, loc=(0, 0, 0), rot=(0, 0, 0)):
    """A prop fixed to the truck (sport bar, stake pocket, cab roof), not part of the load."""
    o = unir(nombre, f, loc, rot)
    bpy.context.view_layer.update()
    NUEVOS.append(o)
    MONTADOS.append(nombre)
    return o


MONTADOS = []
# Load items (under the net), placed in this order before the donut.
EN_CARGA = {
    "pinata": lambda: encima("pinata", pinata_bolsa, 1, XL + 0.33, YF - 0.34),                  # on the amp
    "bocina": lambda: encima("bocina", bocina5, 9, XR - 0.185, YF - 0.37, (-math.pi / 2, 0, 0)),  # on the cooler, rings up
    "sillas": lambda: encima("sillas", sillas, 5, XL + 0.30, -2.24),                            # on the case deck, under the donut
    "cerveza": lambda: encima("cerveza", cerveza, 9, XR - 0.16, -2.10, (0, 0, math.pi / 2)),     # on the cable crate and the snare
    "sombrerera": lambda: encima("sombrerera", sombrerera5, 1, XR - 0.26, -2.59),              # on the blankets
    "globos": lambda: encima("globos", globos_bolsa, 1, CX, YF - 0.40),                        # on the piñata and the speaker
}


def _picado():
    for t in (0.2, 0.4):  # near the cab: further back the strings would hang into the load
        montar("picado", lambda t=t: picado5(tubo(t, -1) + Vector((0.03, 0, 0.02)), tubo(t, 1) - Vector((0.03, 0, -0.02))))


def _luces():
    def f():
        for lado in (-1, 1):
            luces5([tubo(0.0, lado) - Vector((0, 0, 0.035)), tubo(1.0, lado) - Vector((0, 0, 0.035)),
                    Vector((CX + lado * 0.78, -2.32, LEDGE_Z - 0.01)), Vector((CX + lado * 0.78, -2.76, LEDGE_Z - 0.01))])
    montar("luces", f)


def _tabla():
    """The board: a rack bar clamped across the two tubes 0.15 along them, a foam pad on the cab roof, two cam straps."""
    pa, pb = tubo(0.15, -1), tubo(0.15, 1)
    ya, za = pa.y, pa.z + 0.045
    yb, zb = -0.40, TECHO_Z + 0.04

    def rack():
        cil(0.018, (pb - pa).length + 0.06, (CX, ya, pa.z + 0.025), NEGRO5, rot=(0, math.pi / 2, 0), verts=12, parent=F)
        caja((0.62, 0.10, 0.04), (CX, yb, TECHO_Z + 0.02), NEGRO5, bevel=0.015, parent=F)
    montar("rack", rack)
    inc = math.atan2(zb - za, yb - ya)
    o = montar("tabla", tabla, rot=(inc, 0, 0))  # nose up toward the cab roof
    cy = (ya + yb) / 2 - 0.05
    lo, hi = caja_de(o)
    o.location = Vector((CX, cy, (za + zb) / 2 + 0.035)) - Vector(((lo.x + hi.x) / 2 - o.location.x, (lo.y + hi.y) / 2 - o.location.y,
                                                                  (lo.z + hi.z) / 2 - o.location.z))
    bpy.context.view_layer.update()

    def correas():
        for y, z in ((ya, za), (yb, zb)):
            caja((0.64, 0.03, 0.003), (CX, y, z + 0.075), CINTA_N, rot=(inc, 0, 0), parent=F)
    montar("correas", correas)


MONTAJES = {
    "luces": _luces,
    "bandera": lambda: montar("bandera", lambda: bandera3(espejo=True), (CX - 0.77, -2.74, LEDGE_Z - 0.25), (0, 0, -math.pi / 2 - 0.35)),
    "picado": _picado,
    "tabla": _tabla,
    "bidon": lambda: montar("bidon", bidon, (CX + 0.69, -2.50, RIEL + 0.01), (0, 0, math.pi / 2)),
    "neon": lambda: montar("neon", neon5, (CX, YF - 0.10, 1.84)),
}
# Owner 11-14, after the studio sheet: keep #5 the speaker and #7 the beer crate, and add the inflatable alien; the other ten
# candidates stay on the sheet only.
NIVELES = {"elegida": ["bocina", "cerveza", "alien"]}
ALIEN_GLB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "utileria", "alien", "alien-trellis2-s33.glb")


def alien():
    """Inflatable alien, 1.50 m (owner 11-14, his photo): local TRELLIS.2 (seed 33) from a crop of the alien alone
    (tmp/caja5/recorte.py; the photo stays local), scaled to 1.5 m, feet at the origin, facing -y; its texture kept, the vinyl made
    glossy (roughness 0.12, a clear coat) the way blown PVC shines."""
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=ALIEN_GLB)
    objs = [o for o in bpy.data.objects if o not in antes and o.type == "MESH"]
    for o in [o for o in bpy.data.objects if o not in antes and o.type != "MESH"]:
        bpy.data.objects.remove(o)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.parent = None
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    pts = [Vector(c) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    k = 1.5 / (hi.z - lo.z)
    o.data.transform(__import__("mathutils").Matrix.Scale(k, 4) @ __import__("mathutils").Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))))
    for m in o.data.materials:
        if m and m.use_nodes:
            b = m.node_tree.nodes.get("Principled BSDF")
            if b:
                b.inputs["Roughness"].default_value = 0.12
                b.inputs["Coat Weight"].default_value = 0.6
                for l in list(b.inputs["Roughness"].links) + list(b.inputs["Metallic"].links):
                    m.node_tree.links.remove(l)
                b.inputs["Metallic"].default_value = 0.0
    print("CAJA5 alien", tuple(round(v, 3) for v in (hi - lo)), "-> 1.5 m, k", round(k, 4))
    GRUPO.append(o)


def vestir(nivel):
    """Bed B with the owner's picks: the speaker on the cooler and the beer crate on the cable crate under the net (the donut moves
    left, onto the case deck, clear of the crate), then the alien standing on the amp case at the cab wall, facing back, a strap
    round its waist to both sport-bar tubes: it rides upright like a passenger. Checked again with the alien in (CAJA4 CHECK)."""
    NUEVOS.clear(); MONTADOS.clear()
    lista = NIVELES[nivel]
    cama_b(lambda: [EN_CARGA[k]() for k in EN_CARGA if k in lista], f"B-{nivel}-sin-alien", (CX - 0.185, -2.44))
    if "alien" in lista:
        amp = next(o for o, n, _ in CARGA if n == "amp")
        lo, hi = caja_de(amp)
        a = encima("alien", alien, 2, (lo.x + hi.x) / 2, (lo.y + hi.y) / 2 - 0.02)
        alo, ahi = caja_de(a)
        z = alo.z + 0.58  # the waist
        cx, cy = (alo.x + ahi.x) / 2, (alo.y + ahi.y) / 2

        def correa():
            o = toro(0.15, 0.012, (cx, cy, z), CINTA_N, parent=F)
            o.scale = (1.0, 0.75, 0.6)
            for lado in (-1, 1):
                p = tubo(0.12, lado)
                q = Vector((cx + lado * 0.15, cy, z))
                d = p - q
                cil(0.012, d.length, q + d / 2, CINTA_N, rot=(0, math.atan2(math.hypot(d.x, d.y), d.z), math.atan2(d.y, d.x)), verts=8, parent=F)
        montar("correa_alien", correa)
        revisar_carga(f"B-{nivel}")
    bpy.context.view_layer.update()
    print(f"CAJA5 VARIANTE {nivel} nuevos {len(lista)} ({','.join(lista)})")


# ---------------------------------------------------------------- the trio's instruments, out of their cases (owner 11-15 05:41:
# "he doesn't see the band's instruments in the bed"). blender/assets/guitarra.blend (Blend Swap, no licence file) and tololoche.blend
# (no source recorded) stay out: licences unchecked (escenas-plan.md asset table). Our own primitives at the sizes of
# references.md › caja3 (tololoche 1.80 m, lower bout 0.66; bajo sexto 1.05 m, 0.44; requinto 0.98 m, 0.36 for its case, so the
# instrument ~0.90 m, 0.33). Built face up (+z), neck along +y, the origin under the lower bout's tail on the back; where each sits
# is blender/props/colocacion.json › instrumentos (the owner places them in the hand-off .blend).
INSTRUMENTOS = {  # id: (length, lower bout, upper bout, body length, depth, neck width, top colour, side colour, round hole)
    "tololoche": (1.80, 0.66, 0.50, 1.10, 0.25, 0.07, (0.40, 0.17, 0.05), (0.20, 0.07, 0.02), False),
    "bajo_sexto": (1.05, 0.44, 0.34, 0.52, 0.12, 0.065, (0.48, 0.24, 0.07), (0.02, 0.02, 0.02), True),  # a sunburst centre: (0.30, 0.10, 0.03) merged with the load in scene 2
    "requinto": (0.90, 0.33, 0.25, 0.42, 0.09, 0.05, (0.62, 0.42, 0.20), (0.10, 0.05, 0.02), True),
}


def instrumento(id):
    """One instrument as primitives under an empty `inst_<id>`: two bouts (flat cylinders), the top's hole (round, or a bass's two
    f-holes), bridge, neck with a dark fingerboard, headstock (a scroll on the bass, its endpin under the tail)."""
    L, inf, sup, cuerpo, prof, cuello, tapa, aro, redondo = INSTRUMENTOS[id]
    mt, ma, mo = mat(f"k5_{id}_tapa", tapa, 0.3), mat(f"k5_{id}_aro", aro, 0.35), mat("k5_ebano", (0.012, 0.009, 0.007), 0.4)
    e = bpy.data.objects.new("inst_" + id, None)
    sc.collection.objects.link(e)
    for r, y in ((inf / 2, inf / 2), (sup / 2, cuerpo - sup / 2)):
        cil(r, prof, (0, y, prof / 2), ma, verts=48, parent=e)
        cil(r - 0.006, 0.003, (0, y, prof + 0.0015), mt, verts=48, parent=e)  # the top, inset from the sides
    yb = inf * 0.45  # the bridge, on the lower bout
    caja((cuello * 1.8, 0.02, 0.012), (0, yb, prof + 0.009), mo, parent=e)
    if redondo:
        cil(sup * 0.24, 0.002, (0, cuerpo - sup * 0.62, prof + 0.0035), mo, verts=32, parent=e)
    else:
        for s in (-1, 1):
            caja((0.012, 0.16, 0.002), (s * inf * 0.22, inf * 0.62, prof + 0.0035), mo, rot=(0, 0, s * 0.12), parent=e)
    largo = L - cuerpo - (0.12 if redondo else 0.16)  # neck from the upper bout's top to the head
    caja((cuello, largo, 0.03), (0, cuerpo + largo / 2 - 0.02, prof - 0.005), ma, parent=e)
    caja((cuello, largo + cuerpo * 0.35, 0.006), (0, cuerpo + largo / 2 - cuerpo * 0.175 - 0.02, prof + 0.013), mo, parent=e)
    yc = cuerpo + largo - 0.02
    if redondo:
        caja((cuello * 1.6, 0.17, 0.018), (0, yc + 0.085, prof - 0.01), ma, rot=(-0.2, 0, 0), parent=e)
    else:
        caja((cuello, 0.12, 0.05), (0, yc + 0.06, prof - 0.005), ma, parent=e)
        cil(0.035, cuello * 0.9, (0, yc + 0.13, prof + 0.01), ma, rot=(0, math.pi / 2, 0), verts=24, parent=e)  # the scroll
        cil(0.008, 0.10, (0, -0.05, prof / 2), mo, rot=(math.pi / 2, 0, 0), verts=12, parent=e)  # the endpin
    c = COLOCA["instrumentos"][id]
    e.location, e.rotation_euler, e.scale = c["loc"], c["rot"], (c["escala"],) * 3  # children were built at the identity
    _fin(e, None, None)
    print("CAJA5 INSTRUMENTO", id, tuple(round(v, 3) for v in c["loc"]), "largo", L)
    return e


def instrumentos():
    return [instrumento(id) for id in INSTRUMENTOS]


# ---------------------------------------------------------------- scene-2 measures (props-placement reglas.md, rules 1-3)
HIST = {}


def medir(nombre, pos, mira, lens):
    """One ray per pixel at 1/5 of the still. Rule 1: of the tailgate stickers' pixels (c3_ decals behind the tailgate), the share
    covered by caja5 props (≤ 2 %). Rule 3: caja5 props that read (first hit on ≥ 0.1 % of the frame or self-lit), budget 4 in
    scene 2. Clutter: of the pixels where anything over the rails shows (load + caja5 props, hits above the rail), the share
    where two or more of those items stack along the ray (silhouette overlap)."""
    for ob in sc.objects:  # an earlier option's copies sit exactly where this one's are: hidden from render only, they'd eat the rays
        if ob.hide_render and not ob.hide_viewport:
            ob.hide_viewport = True
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    W, H = RW // 5, RH // 5
    R = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y").to_matrix()
    th = 18 / lens
    nuevos = {o.name for o in NUEVOS}
    carga_n = {o.name for o, *_ in CARGA}
    red = {o.name for o in RED}
    zona = cubierta = sil = encima_2 = 0
    vis = {}
    for j in range(H):
        for i in range(W):
            d = (R @ Vector(((2 * (i + 0.5) / W - 1) * th, (1 - 2 * (j + 0.5) / H) * th * H / W, -1))).normalized()
            o = Vector(pos)
            pila, primero = [], None
            for _ in range(16):
                hit, loc, nrm, idx, ob, _m = sc.ray_cast(dg, o, d)
                if not hit:
                    break
                if ob.hide_render:  # an earlier option's props stay in the scene, hidden from the render only
                    o = loc + d * 0.001
                    continue
                n = ob.name
                if primero is None:
                    primero = n
                if n in red:
                    o = loc + d * 0.001
                    continue
                if n in nuevos or n in carga_n:
                    if loc.z > RIEL + 0.005 and n not in pila:
                        pila.append(n)
                    o = loc + d * 0.001
                    continue
                m = ob.active_material
                if os.environ.get("CAJA5_PRUEBA"):
                    HIST[n] = HIST.get(n, 0) + 1
                if m and m.name.startswith("c3_"):  # a sticker that is not on the load: the tailgate's
                    zona += 1
                    cubierta += any(p in nuevos for p in pila) or (primero in nuevos)
                break
            if primero in nuevos:
                vis[primero] = vis.get(primero, 0) + 1
            if pila:
                sil += 1
                encima_2 += len(pila) >= 2
    clave = lambda n: {"rack": "tabla", "correas": "tabla", "correa_alien": "alien"}.get(n.split(".")[0][3:], n.split(".")[0][3:])
    vis_k = {}
    for n, c in vis.items():
        vis_k[clave(n)] = vis_k.get(clave(n), 0) + c
    leen = sorted(k for k, c in vis_k.items() if c >= 0.001 * W * H or k in ("luces", "neon", "bocina"))  # the self-lit ones read
    r1 = 100.0 * cubierta / zona if zona else float("nan")
    print(f"CAJA5 MEDIDA {nombre} zona {zona} px cubierta {r1:.2f} % -> r1 {'PASS' if zona and r1 <= 2 else 'FAIL'} | "
          f"leen {len(leen)} ({','.join(leen)}) presupuesto 4 -> r3 {'PASS' if len(leen) <= 4 else 'OVER'} | "
          f"sobre el borde {sil} px, encimados {100.0 * encima_2 / max(1, sil):.1f} %")
    with open(os.path.join(OUT, nombre + "-medidas.json"), "w") as fh:
        json.dump({"zona_px": zona, "cubierta_pct": r1, "leen": leen, "vis_px": vis_k, "sobre_borde_px": sil,
                   "encimados_pct": 100.0 * encima_2 / max(1, sil), "W": W, "H": H}, fh)


# ---------------------------------------------------------------- options
VISTA5 = lambda: ((CX - 0.9, -5.6, 3.7), (CX, -1.9, 1.75), 30)  # VISTA_CAJA3 pulled back and up: the alien stands 3 m tall


for _n in NIVELES:
    def _cerca(n=_n):
        vestir(n)
        relleno_caja(VISTA5()[0])
        return VISTA5()

    def _esc2(n=_n):
        _g["caja2_b"] = lambda: vestir(n)  # base_escena() dresses the bed with this
        toma_ = esc2_abre()
        medir(f"caja5-{n}-esc2", *toma_)
        return toma_
    opcion(f"caja5-{_n}")(_cerca)
    opcion(f"caja5-{_n}-esc2")(_esc2)

# ---------------------------------------------------------------- drinks in the cab (owner 11-14: "soda cans, water props to the
# middle in the van or give them to the characters"): made-up labels from blender/etiquetas.py, two placements to compare
ETIQ = os.path.join(REPO, "tmp", "utileria", "etiquetas")
ALU5 = mat("k5_alu", (0.75, 0.75, 0.77), 0.25, 1.0)
PET = mat("k5_pet", (0.85, 0.93, 0.98), 0.04, trans=0.95)


def mat_envuelta(nombre, png, rough=0.3, metal=0.0, dorso=None):
    """A label wrapped round a cylinder: u = the angle round the object's own z (Generated coordinates), v = its height.
    dorso: the colour of the label's inside face (a paper back, seen through a clear bottle)."""
    if nombre in MATS:
        return MATS[nombre]
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value, b.inputs["Metallic"].default_value = rough, metal
    tc, sep = nt.nodes.new("ShaderNodeTexCoord"), nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    dx, dy = nt.nodes.new("ShaderNodeMath"), nt.nodes.new("ShaderNodeMath")
    dx.operation = dy.operation = "SUBTRACT"
    dx.inputs[1].default_value = dy.inputs[1].default_value = 0.5
    nt.links.new(sep.outputs["X"], dx.inputs[0]); nt.links.new(sep.outputs["Y"], dy.inputs[0])
    at = nt.nodes.new("ShaderNodeMath"); at.operation = "ARCTAN2"
    nt.links.new(dy.outputs[0], at.inputs[0]); nt.links.new(dx.outputs[0], at.inputs[1])
    u = nt.nodes.new("ShaderNodeMath"); u.operation = "MULTIPLY_ADD"
    u.inputs[1].default_value, u.inputs[2].default_value = 1 / (2 * math.pi), 0.5
    nt.links.new(at.outputs[0], u.inputs[0])
    uv = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u.outputs[0], uv.inputs["X"]); nt.links.new(sep.outputs["Z"], uv.inputs["Y"])
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(os.path.join(ETIQ, png), check_existing=True)
    nt.links.new(uv.outputs[0], tx.inputs["Vector"])
    col = tx.outputs["Color"]
    if dorso:
        geo, mx = nt.nodes.new("ShaderNodeNewGeometry"), nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        nt.links.new(geo.outputs["Backfacing"], mx.inputs[0])
        nt.links.new(col, mx.inputs[6])
        mx.inputs[7].default_value = (*dorso, 1)
        col = mx.outputs[2]
    nt.links.new(col, b.inputs["Base Color"])
    MATS[nombre] = m
    return m


def bebida(tipo, nombre):
    """A 355 ml can (Ø 66 × 122 mm, the label on the wall, aluminium shoulders and lid) or a 600 ml water bottle (Ø 66 × 230 mm,
    clear PET, a wrap label, a black cap). Built under an empty at the base centre, so it can be posed or parented as one."""
    raiz = bpy.data.objects.new(nombre, None)
    sc.collection.objects.link(raiz)
    GRUPO.append(raiz)
    if tipo == "agua":
        cil(0.033, 0.158, (0, 0, 0.091), PET, verts=32, parent=raiz)
        cono(0.027, 0.033, 0.012, (0, 0, 0.006), PET, verts=32, parent=raiz)  # the base tapers to its feet, Ø 54 mm
        # an open tube: with end caps, the Generated mapping painted both caps with the label's gold band, two gold discs inside
        # the clear bottle that tinted the water amber (caja5-bebidas-consola, -mano, 11-14)
        et = cil(0.0335, 0.06, (0, 0, 0.095), mat_envuelta("k5_et_agua", "agua.png", 0.5, dorso=(0.8, 0.8, 0.78)), verts=48, parent=raiz)
        bm = bmesh.new()
        bm.from_mesh(et.data)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if abs(f.normal.z) > 0.9], context="FACES")
        bm.to_mesh(et.data)
        bm.free()
        cono(0.033, 0.014, 0.04, (0, 0, 0.19), PET, verts=32, parent=raiz)
        cil(0.015, 0.02, (0, 0, 0.22), NEGRO5, verts=24, parent=raiz)
    else:
        cil(0.033, 0.104, (0, 0, 0.061), mat_envuelta("k5_et_" + tipo, tipo + ".png", 0.25, 0.6), verts=48, parent=raiz)
        cono(0.026, 0.033, 0.009, (0, 0, 0.0045), ALU5, verts=48, parent=raiz)  # the standing ring, Ø 52 mm
        cono(0.033, 0.027, 0.01, (0, 0, 0.118), ALU5, verts=48, parent=raiz)
        caja((0.02, 0.012, 0.002), (0.008, 0, 0.123), ALU5, parent=raiz)  # the tab
    return raiz


MEDIDA_BEBIDA = {"agua": (0.0335, 0.23), "lata": (0.033, 0.122)}  # radius and height (the label tube is the widest part)
PIE = {"agua": 0.027, "lata": 0.026}  # the radius each one stands on (bottle feet, can standing ring)


def choques(raiz, R, H, fuera=()):
    """Does a drink cross anything? BVH overlap (triangle pairs) between the drink's parts and every other mesh near it (the
    G63's interior is low-poly: a big lid face can pass through a can with no vertex inside it), plus the count of those meshes'
    vertices inside the drink's cylinder (R, H, in the drink's own frame: it may stand tilted). `fuera`: objects not counted."""
    dg = bpy.context.evaluated_depsgraph_get()
    L = raiz.matrix_world.inverted()
    partes = [o for o in raiz.children_recursive if o.type == "MESH"]
    def malla(o, lo=None, hi=None):
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        vs = [ev.matrix_world @ v.co for v in me.vertices]
        ps = []
        for p in me.polygons:
            q = [vs[i] for i in p.vertices]
            if lo is None or all(min(c[k] for c in q) <= hi[k] and max(c[k] for c in q) >= lo[k] for k in range(3)):
                ps.append(list(p.vertices))
        ev.to_mesh_clear()
        return vs, ps
    vs, ps = [], []
    for o in partes:
        v, p = malla(o)
        ps += [[i + len(vs) for i in f] for f in p]
        vs += v
    yo = BVHTree.FromPolygons(vs, ps)
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))) - Vector((0.01, 0.01, 0.01))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs))) + Vector((0.01, 0.01, 0.01))
    pares, dentro, quien = 0, 0, set()
    for o in sc.objects:
        if o.type != "MESH" or o in partes or o in fuera or o.hide_render or o.hide_viewport:
            continue
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        if any(min(c[k] for c in bb) > hi[k] or max(c[k] for c in bb) < lo[k] for k in range(3)):
            continue
        v, p = malla(o, lo, hi)
        if not p:
            continue
        n = len(yo.overlap(BVHTree.FromPolygons(v, p)))
        dv = {i for f in p for i in f for q in [L @ v[i]] if 0.001 < q.z < H and math.hypot(q.x, q.y) < R}
        d = len(dv)
        if n or d:
            q = [v[i] for i in dv] or [v[i] for f in p for i in f]
            quien.add(f"{o.name} x {min(c.x for c in q) - CX:+.3f}..{max(c.x for c in q) - CX:+.3f}"
                      f" y {min(c.y for c in q):.3f}..{max(c.y for c in q):.3f} z {min(c.z for c in q):.3f}..{max(c.z for c in q):.3f}")
        pares += n
        dentro += d
    return pares, dentro, sorted(quien)


# The console (probed 11-14, tmp/caja7/cubierta.log, rays down from 1.6 m with the riders hidden): the armrest lid's top is a
# 10 cm wide crown (z 1.38 at y 0.45 falling to 1.34 at y 0.65) with flanks that drop 9 cm; the G63's mesh has no cupholder
# well. Ahead of the controller panel (y 0.80) the console steps down to a flat deck, z 1.236-1.241, x -0.03..+0.095 from the
# centre line, from y 0.81 to the centre stack (y ~1.04); the shifter stands on it at x +0.02..+0.06, y 0.88-0.945.
# The shifter boot's back lip (y 0.875-0.882, z 1.26-1.28), the controller step (y 0.80-0.81) and the centre stack's lower lip
# (y 1.031, z 1.33) are near-vertical faces the rays down miss; apoyo's BVH test found them (11-14). Behind the shifter every spot
# crossed the step or the boot (12-70 triangle pairs, upright or tilted); ahead of it the clear patch is x -0.03..+0.095 by
# y 0.945..1.031, room for one Ø 66 mm drink (centres x 0.003-0.062, y 0.978-0.998). So the console holds one drink.
CONSOLA = {  # variant: (drink, x from the centre line, y), the spot to start the support search from
    "lata": (("lata-tumba", 0.032, 0.988),),  # the can alone, ahead of the shifter
    "agua": (("agua", 0.032, 0.988),),        # the bottle alone, ahead of the shifter
}
# Kept (11-14 previews, 16 spp): the bottle. Its clear body and pale label read at luma 92 against the console's 14; the
# black can reads at 43 (its lower tenth at 0, merged with the console) and its silver lid reads as a second shift knob.
CONSOLA_VAR = os.environ.get("CAJA5_CONSOLA", "agua")


def entorno(lo, hi):
    """One BVH of every visible mesh's faces that reach into the box lo..hi (world), for the support search's overlap test."""
    dg = bpy.context.evaluated_depsgraph_get()
    vs, ps = [], []
    for o in sc.objects:
        if o.type != "MESH" or o.hide_render or o.hide_viewport or o.name.startswith("k5_"):
            continue
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        if any(min(c[k] for c in bb) > hi[k] or max(c[k] for c in bb) < lo[k] for k in range(3)):
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        v = [ev.matrix_world @ w.co for w in me.vertices]
        for f in me.polygons:
            q = [v[i] for i in f.vertices]
            if all(min(c[k] for c in q) <= hi[k] and max(c[k] for c in q) >= lo[k] for k in range(3)):
                ps.append([len(vs) + i for i in range(len(q))])
                vs += q
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(vs, ps)


def perfil(R, H, pie, M):
    """A drink's outline as a closed 24-sided mesh (feet ring at pie, full radius R from 12 mm up to H) under matrix M: a BVH."""
    anillos = [(pie, 0.0), (R, 0.012), (R, H)]
    vs = [M @ Vector((r * math.cos(2 * math.pi * k / 24), r * math.sin(2 * math.pi * k / 24), z)) for r, z in anillos for k in range(24)]
    ps = [[a * 24 + k, a * 24 + (k + 1) % 24, (a + 1) * 24 + (k + 1) % 24, (a + 1) * 24 + k] for a in range(2) for k in range(24)]
    ps += [list(range(24))[::-1], [48 + k for k in range(24)]]
    return BVHTree.FromPolygons(vs, ps)


def apoyo(x, y, R, busca=0.012, paso=0.001, libre=None):
    """Where a drink standing on radius R rests near (x, y): rays straight down from 1.6 m on a 5 mm grid over its base disc, a
    plane fitted to the hits; the drink stands square to it (the deck falls ~4° towards the dash: a level base would hang off
    the low side), tilt ≤ 6°. The base touches the highest hit + 0.5 mm, lifted in 0.5 mm steps while the contact gap stays
    ≤ 3 mm until `libre` says its outline crosses nothing. Keeps the clear spot with the shallowest hollow under the base (the
    deck's 2-5 mm relief, reported apart from the gap), then the nearest. Returns (x, y, z, hollow, normal, gap) or None."""
    import numpy as np
    disco = [(i * 0.005, j * 0.005) for i in range(-7, 8) for j in range(-7, 8) if math.hypot(i, j) * 0.005 <= R]
    n = int(round(busca / paso))
    mejor = None
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            cx, cy = x + i * paso, y + j * paso
            P = []
            for u, v in disco:
                h = rayo((cx + u, cy + v, 1.6), (0, 0, -1))
                P.append((u, v, h.z if h else -9.0))
            P = np.array(P)
            A = np.c_[P[:, 0], P[:, 1], np.ones(len(P))]
            (a, b, c), *_ = np.linalg.lstsq(A, P[:, 2], rcond=None)
            res = P[:, 2] - A @ np.array([a, b, c])
            hueco = float(res.max() - res.min())
            nrm = Vector((-a, -b, 1)).normalized()
            clave = (round(hueco, 4), math.hypot(i, j))
            if nrm.z < math.cos(math.radians(6)) or (mejor is not None and clave >= mejor[0]):
                continue
            for k in range(1, 7):
                if libre is None or libre(cx, cy, float(c + res.max()) + k * 0.0005, nrm):
                    mejor = (clave, cx, cy, float(c + res.max()) + k * 0.0005, hueco, nrm, k * 0.0005)
                    break
    return mejor[1:] if mejor else None


def bebidas_consola(var=CONSOLA_VAR):
    """(a) The console drink: standing on the lower deck ahead of the shifter, on a measured support (apoyo), checked for
    crossings (choques). Prints CAJA5 CONSOLA: the contact gap (the base over the highest support point; the gate, as CAJA5
    MANO's gap), the hollow under the base (the deck's relief, reported, not gated), pairs and vertices inside."""
    # Héctor's raised hand (ALZADA) used to stop this: the montaje scenes hold both drinks (mothership 05:43), and choques() below
    # tests the drink against his posed mesh too, so a crossing still prints FAIL
    for ob in sc.objects:  # an earlier option's drinks are hidden from render only: the rays must not land on them
        if ob.hide_render and not ob.hide_viewport:
            ob.hide_viewport = True
    for o in FIGURAS:
        o.hide_viewport = True
    _g["dg"] = bpy.context.evaluated_depsgraph_get()
    zona = entorno(Vector((CX - 0.10, 0.76, 1.15)), Vector((CX + 0.16, 1.12, 1.50)))  # the deck, shifter and centre stack
    hechos = []
    for tipo, x, y in CONSOLA[var]:
        R, H = MEDIDA_BEBIDA["agua" if tipo == "agua" else "lata"]
        pie = PIE["agua" if tipo == "agua" else "lata"]

        def libre(cx, cy, z, nrm, R=R, H=H, pie=pie):  # the drink's outline crosses no face of the cab there
            M = Matrix.Translation((cx, cy, z)) @ Vector((0, 0, 1)).rotation_difference(nrm).to_matrix().to_4x4()
            return not zona.overlap(perfil(R, H, pie, M))
        a = apoyo(CX + x, y, pie, libre=libre)
        if a is None:
            print(f"CAJA5 CONSOLA {var} {tipo} no flat support near ({x}, {y}) -> FAIL")
            continue
        r = bebida(tipo, "k5_bebida_" + tipo)
        r.location = (a[0], a[1], a[2])
        r.rotation_mode = "QUATERNION"
        r.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(a[4])
        hechos.append((tipo, r, R, H, a))
    for o in FIGURAS:
        o.hide_viewport = False
    bpy.context.view_layer.update()
    _g["dg"] = bpy.context.evaluated_depsgraph_get()
    for tipo, r, R, H, a in hechos:
        pares, dentro, quien = choques(r, R, H)
        gap, tilt = a[5], math.degrees(a[4].angle(Vector((0, 0, 1))))
        ok = gap <= 0.003 and not pares and not dentro and tilt <= 6
        print(f"CAJA5 CONSOLA {var} {tipo} at x {a[0] - CX:+.3f} y {a[1]:.3f} z {r.location.z:.4f} tilt {tilt:.1f}° contact gap"
              f" {gap * 1000:.1f} mm hollow {a[3] * 1000:.1f} mm pairs {pares} inside {dentro} {quien} -> {'PASS' if ok else 'FAIL'}")


CAMION_EXTRA.append(bebidas_consola)  # the montaje scenes carry the console bottle under the screen (mothership 05:43)
CAMION_EXTRA.append(instrumentos)     # and the trio's instruments on the load (owner 05:41)


MANO_POSE = os.environ.get("CAJA5_POSE", "ventana")
POSES = {  # Héctor's hand that holds the bottle, and where it goes from the shoulder (armature units; None: left on the thigh)
    "regazo": ("mano_p", None),                      # console side, as posed: the bottle sits below every scene camera
    "alzada": ("mano_p", (0.0, -0.22, -0.10)),       # console side over the lap: below the window sill
    "alta": ("mano_p", (0.0, -0.20, 0.04)),          # console side at the mouth: the bottle floats by his ear
    "ventana": ("mano_n", (0.0, -0.24, 0.0)),        # door side at the chest: seen through his window (scene 4B)
}
ALZADA = []


def alzar_mano(fig="hector", lado=1, objetivo=(0.0, -0.22, -0.10), polo=(1.0, 0.2, -1.0)):
    """Raise one hand off the thigh, as if holding a bottle in front of the belly: re-keys frame 0 with transicion's own Pose and
    two-bone IK (brazo). `objetivo` is the hand's end point from the shoulder, in armature units (the figure faces -Y). Every
    other bone gets sentar()'s frame-0 direction for Héctor (head from h_cabeza(0), the other hand on the thigh, as regazo)."""
    rig = bpy.data.objects[fig + "_rig"]
    j = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in rig.data.bones}
    P = T.Pose(rig, j)
    otro = -lado
    k_otro = "n" if otro < 0 else "p"
    rodilla = P.j[f"muslo_{k_otro}"][0] + Vector((0.02 * otro, -0.16, 0.06))
    k = "n" if lado < 0 else "p"
    dirs = {"columna": Vector((0, 0.10, 1)).normalized(), "cabeza": Vector((0.10, 0.0, 1)).normalized(),
            "muslo_n": Vector((-0.12, -1, -0.04)).normalized(), "muslo_p": Vector((0.12, -1, -0.04)).normalized(),
            "pierna_n": Vector((-0.05, -0.25, -1)).normalized(), "pierna_p": Vector((0.05, -0.25, -1)).normalized()}
    dirs.update(T.brazo(P, otro, rodilla, Vector((otro * 1.0, 0.5, -0.6))))
    dirs.update(T.brazo(P, lado, P.j[f"brazo_{k}"][0] + Vector(objetivo), Vector(polo)))
    P.poner(dirs, 0)
    sc.frame_set(0)
    bpy.context.view_layer.update()


AGARRE = os.environ.get("CAJA5_AGARRE")  # where the fist sits up the bottle (share of its height from the base); unset: searched
GIRO = os.environ.get("CAJA5_GIRO")      # the fist's yaw about the wrist, degrees; unset: searched
VISTA_MANO = Vector((0.95, -0.20, 0.12)).normalized()  # from the hand towards the close-up camera (outside his window); scene 4's
# camera sees the hand from (0.97, -0.18, 0.18), the same side
GIROS, BANDAS = (0, 20, 35, 50, 65), (0.5, 0.6)
PUNO = {}


def puno(fig="hector", hueso="mano_n"):
    """A wrist bone at the hand mesh's own wrist (the centroid of the vertices half-weighted to the hand), child of the hand bone,
    the hand's vertex group moved onto it: turning it turns the fist about the wrist. Turning the hand bone itself would swing
    the mesh round a pivot ~12 cm away. Once per run; returns the bone's name (also the hand's vertex group now)."""
    nombre = "puno_" + hueso[-1]
    if nombre in PUNO:
        return nombre
    rig, cuerpo = bpy.data.objects[fig + "_rig"], bpy.data.objects[fig]
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = cuerpo.evaluated_get(dg)
    me = ev.to_mesh()
    gi = cuerpo.vertex_groups[hueso].index

    def peso(v):
        return max((g.weight for g in v.groups if g.group == gi), default=0.0)
    anillo = [ev.matrix_world @ v.co for v in me.vertices if 0.2 <= peso(v) <= 0.8]
    mano = [ev.matrix_world @ v.co for v in me.vertices if peso(v) >= 0.5]
    ev.to_mesh_clear()
    muneca, centro = sum(anillo, Vector()) / len(anillo), sum(mano, Vector()) / len(mano)
    pb = rig.pose.bones[hueso]
    a_reposo = rig.data.bones[hueso].matrix_local @ pb.matrix.inverted() @ rig.matrix_world.inverted()
    bpy.context.view_layer.objects.active = rig
    rig.hide_viewport = False
    bpy.ops.object.mode_set(mode="EDIT")
    eb = rig.data.edit_bones.new(nombre)
    eb.head, eb.tail = a_reposo @ muneca, a_reposo @ centro
    eb.parent, eb.use_connect, eb.use_deform = rig.data.edit_bones[hueso], False, True
    bpy.ops.object.mode_set(mode="OBJECT")
    cuerpo.vertex_groups[hueso].name = nombre
    rig.pose.bones[nombre].rotation_mode = "QUATERNION"
    bpy.context.view_layer.update()
    PUNO[nombre] = muneca
    print(f"CAJA5 PUNO {fig} wrist {tuple(round(c, 3) for c in muneca)} hand centroid {tuple(round(c, 3) for c in centro)}")
    return nombre


def girar_puno(fig, nombre, grados):
    """Yaw the fist about the world vertical through its wrist (negative: the fingers turn from inboard towards the front)."""
    rig = bpy.data.objects[fig + "_rig"]
    pb = rig.pose.bones[nombre]
    pb.rotation_quaternion = Quaternion()
    bpy.context.view_layer.update()
    B = (rig.matrix_world @ pb.matrix).to_quaternion()
    pb.rotation_quaternion = B.inverted() @ Quaternion((0, 0, 1), math.radians(grados)) @ B
    bpy.context.view_layer.update()


def _cuerpo(fig, grupo):
    import numpy as np
    cuerpo = bpy.data.objects[fig]
    dg = bpy.context.evaluated_depsgraph_get()
    ev = cuerpo.evaluated_get(dg)
    me = ev.to_mesh()
    gi = cuerpo.vertex_groups[grupo].index
    V = np.array([tuple(ev.matrix_world @ v.co) for v in me.vertices])
    peso = np.array([max((g.weight for g in v.groups if g.group == gi), default=0.0) for v in me.vertices])
    ev.to_mesh_clear()
    return V, peso


def _sitio(V, peso, R, H, banda):
    """The bottle's base for a fist at `banda` of its height: no body vertex inside the upright cylinder, gap ≤ 3 mm to the hand,
    the axis farther from the camera than the fist's centroid, the smallest offset across the view. ((offset, gap), base).
    The hand, for the gap, is its group at any weight plus every vertex within 6 cm of its centroid: the thumb stands up on the
    palm side, partly outside the group, and the bottle can only pass behind the fist against it."""
    import numpy as np
    hc = V[peso >= 0.5].mean(axis=0)
    dist = np.linalg.norm(V - hc, axis=1)
    cerca = dist < H + 0.15
    V, es_mano, pes = V[cerca], ((peso >= 0.1) | (dist < 0.06))[cerca], peso[cerca]
    vh = np.array([VISTA_MANO.x, VISTA_MANO.y])
    vh /= np.linalg.norm(vh)
    bz = hc[2] - banda * H
    enz = (V[:, 2] >= bz) & (V[:, 2] <= bz + H)
    mejor = None
    for i in range(-16, 17):
        for j in range(-16, 17):
            bx, by = hc[0] + i * 0.005, hc[1] + j * 0.005
            w = np.array([bx - hc[0], by - hc[1]])
            if w @ vh > -0.01:
                continue
            rr = np.hypot(V[:, 0] - bx, V[:, 1] - by)
            if np.any(enz & (rr < R)):
                continue
            m = enz & es_mano
            if not m.any():
                continue
            k = int(np.argmin(rr[m]))
            gap = float(rr[m][k] - R)
            if gap > 0.003:
                continue
            lat = float(np.linalg.norm(w - (w @ vh) * vh))
            if mejor is None or (lat, gap) < mejor[0]:
                mejor = ((lat, gap), Vector((bx, by, bz)), float(pes[m][k]))  # the nearest vertex's weight to the hand
    return mejor


def _tapa(cam, base, H, R, fig):
    """cubre() without the bottle built: a ray to a point of the bottle's silhouette that hits the figure first is covered."""
    dg = bpy.context.evaluated_depsgraph_get()
    c = base + Vector((0, 0, H / 2))
    lado = (c - cam).cross(Vector((0, 0, 1))).normalized()
    filas = []
    for j in range(23):
        f = (j + 0.5) / 23
        n = [0, 0]
        for i in range(9):
            p = base + Vector((0, 0, f * H)) + lado * (((i + 0.5) / 9 * 2 - 1) * R * 0.9)
            d = p - cam
            o, dd, tapa = cam.copy(), d.normalized(), False
            for _ in range(12):  # through the window glass, as cubre()
                hit, loc, _n, idx, ob, _m = sc.ray_cast(dg, o, dd, distance=(p - o).length - 0.002)
                if not hit:
                    break
                if ob.type == "MESH" and idx < len(ob.data.polygons) and ob.material_slots and \
                        ob.material_slots[ob.data.polygons[idx].material_index].material.name.startswith(("vidrio", "mica")):
                    o = loc + dd * 0.001
                    continue
                tapa = ob.name.split(".")[0] == fig
                break
            n[0 if tapa else 1] += 1
        filas.append((f, n))

    def parte(a, b, k):
        t = [n for f, n in filas if a <= f < b]
        return sum(n[k] for n in t) / sum(sum(n) for n in t)
    return parte(0.35, 0.65, 0), parte(0.85, 1.01, 1), parte(0.0, 0.15, 1)


def bebida_en_mano(fig="hector", hueso=POSES[MANO_POSE][0], tipo="agua", banda=None, giro=None):
    """(b) A drink in a rider's fist (owner 11-14: Héctor's water bottle in his grip, not beside his hand). The hands are
    thumbs-up paddles with no finger bones, so the grip is what the camera reads: the bottle stands against the palm on the
    side away from the window camera (VISTA_MANO), the fist over its middle. As posed (ventana) the fingers point inboard, so
    the window camera looks along the hand from the wrist and the bottle could only sit at the fingertips (11-14 previews:
    the middle 11-25 % covered); the fist turns about its own wrist (puno) to show its back to the window. For each yaw in
    GIROS and fist height in BANDAS: the search centred on the hand's vertex-group centroid (the hand bone sits ~12 cm outboard
    of the mesh; centring on the bone, the 19:50 round, only reached spots beside the hand), no body vertex inside the bottle,
    gap ≤ 3 mm, then the coverage from the window camera (_tapa); keeps the smallest turn that passes cubre's threshold, else
    the best middle coverage. Parents the drink to the wrist bone. Prints CAJA5 GIRO per try and CAJA5 MANO."""
    asientos_traseros()
    if fig == "hector" and POSES[MANO_POSE][1] and not ALZADA:
        lado = -1 if hueso.endswith("_n") else 1
        alzar_mano(lado=lado, objetivo=POSES[MANO_POSE][1], polo=(lado * 1.0, 0.2, -1.0))
        ALZADA.append(1)
    bpy.context.view_layer.update()
    rig = bpy.data.objects[fig + "_rig"]
    R, H = MEDIDA_BEBIDA["agua" if tipo == "agua" else "lata"]
    grupo = puno(fig, hueso)
    giros = [float(giro if giro is not None else GIRO)] if (giro is not None or GIRO) else GIROS
    bandas = [float(banda if banda is not None else AGARRE)] if (banda is not None or AGARRE) else BANDAS
    pruebas = []
    for g in giros:
        girar_puno(fig, grupo, g)
        V, peso = _cuerpo(fig, grupo)
        hc = Vector(V[peso >= 0.5].mean(axis=0))
        for b in bandas:
            s = _sitio(V, peso, R, H, b)
            if s is None:
                print(f"CAJA5 GIRO {g:+.0f} banda {b}: no spot with 0 inside and gap <= 3 mm")
                continue
            medio, tapa, pie = _tapa(hc + VISTA_MANO * 1.0, s[1], H, R, fig)
            ok = medio >= 0.5 and tapa >= 0.5
            print(f"CAJA5 GIRO {g:+.0f} banda {b}: offset {s[0][0] * 1000:.0f} mm gap {s[0][1] * 1000:.1f} mm, middle covered"
                  f" {medio * 100:.0f} % cap visible {tapa * 100:.0f} % base visible {pie * 100:.0f} %{' ok' if ok else ''}")
            pruebas.append(((not ok, abs(g) if ok else -medio, abs(b - 0.5)), g, b, s))
    if pruebas:
        _k, g, banda, mejor = min(pruebas, key=lambda t: t[0])
    else:
        g, banda, mejor = giros[0], bandas[0], None
    girar_puno(fig, grupo, g)
    if mejor is None:
        print(f"CAJA5 MANO {fig} {hueso} {tipo}: no spot with 0 inside and gap <= 3 mm -> FAIL")
        V, peso = _cuerpo(fig, grupo)
        hc = V[peso >= 0.5].mean(axis=0)
        mejor = ((9.0, 9.0), Vector((hc[0], hc[1], hc[2] - banda * H)), 0.0)
    hueso = grupo
    base = mejor[1]
    raiz = bebida(tipo, "k5_bebida_mano")
    raiz.location = base
    bpy.context.view_layer.update()
    M = raiz.matrix_world.copy()
    raiz.parent, raiz.parent_type, raiz.parent_bone = rig, "BONE", hueso
    raiz.matrix_world = M
    bpy.context.view_layer.update()
    pares, dentro, quien = choques(raiz, R, H)
    lat, gap = mejor[0]
    ok = gap <= 0.003 and not pares and not dentro
    print(f"CAJA5 MANO {fig} {hueso} {tipo} pose {MANO_POSE} giro {g:+.0f} banda {banda} base {tuple(round(x, 3) for x in base)} gap {gap * 1000:.1f} mm"
          f" (to a vertex of hand weight {mejor[2]:.2f}) axis-to-fist {lat * 1000:.0f} mm pairs {pares} inside {dentro} {quien} -> {'PASS' if ok else 'FAIL'}")
    return base


def cubre(nombre, cam, base, H=0.23, R=0.033, fig="hector"):
    """What a camera sees of the hand-held bottle: rays from `cam` to a 9 × 23 grid on the bottle's silhouette (the plane through
    its axis, square to the view), stepping through glass. Per height band, the share whose first hit is the figure (the fist in
    front) vs the bottle. Prints CAJA5 AGARRE; my threshold (not the owner's): the middle band (35-65 % of the height) at least
    half covered, the cap band (85-100 %) and the base band (0-15 %) at least half visible: a fist round the middle."""
    for ob in sc.objects:
        if ob.hide_render and not ob.hide_viewport:
            ob.hide_viewport = True
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    cam = Vector(cam)
    c = base + Vector((0, 0, H / 2))
    lado = (c - cam).cross(Vector((0, 0, 1))).normalized()
    botella = {o.name for o in GRUPO if o.name.startswith("k5_bebida_mano") or (o.parent and o.parent.name.startswith("k5_bebida_mano"))}
    filas = []
    for j in range(23):
        f = (j + 0.5) / 23
        n = {"mano": 0, "botella": 0, "otro": 0}
        for i in range(9):
            p = base + Vector((0, 0, f * H)) + lado * (((i + 0.5) / 9 * 2 - 1) * R * 0.9)
            o, d = cam.copy(), (p - cam).normalized()
            que = "otro"
            for _ in range(12):
                hit, loc, nrm, idx, ob, _m = sc.ray_cast(dg, o, d)
                if not hit:
                    break
                if ob.name in botella:
                    que = "botella"
                    break
                if ob.name.split(".")[0] == fig:
                    que = "mano"
                    break
                if ob.type == "MESH" and idx < len(ob.data.polygons) and ob.material_slots and \
                        (ob.material_slots[ob.data.polygons[idx].material_index].material.name.startswith(("vidrio", "mica"))):
                    o = loc + d * 0.001
                    continue
                break
            n[que] += 1
        filas.append((f, n))
    def parte(a, b, k):
        t = [n for f, n in filas if a <= f < b]
        tot = sum(n["mano"] + n["botella"] for n in t)
        return sum(n[k] for n in t) / tot if tot else float("nan")
    medio, tapa, pie = parte(0.35, 0.65, "mano"), parte(0.85, 1.01, "botella"), parte(0.0, 0.15, "botella")
    otro = sum(n["otro"] for f, n in filas) / (23 * 9)
    ok = medio >= 0.5 and not tapa < 0.5 and not pie < 0.5  # a band the cab hides entirely (nan) is not a fail
    print(f"CAJA5 AGARRE {nombre} middle covered {medio * 100:.0f} % cap visible {tapa * 100:.0f} % base visible {pie * 100:.0f} %"
          f" (cab in front {otro * 100:.0f} %) -> {'PASS' if ok else 'FAIL'}")
    print("CAJA5 AGARRE " + nombre + " bands " + " ".join(f"{n['mano']}/{n['botella']}" for f, n in filas))


def medir1(nombre, pos, mira, lens, pasa_vidrio=False, paso=5):
    """Scene 1, rule 1: of the road band seen through the windshield (glass hits ahead of the cab's middle, below 1.87 m: the
    lower 70 % of the glass, props_placement.py's band), the share covered by the drinks (≤ 2 %). pasa_vidrio: rays go on
    through any other glass (a side window, told by the hit face's material), to count the drinks' visible pixels from outside
    the cab (scene 4). paso: one ray per paso × paso pixels (2 for a drink that is a few pixels wide)."""
    for ob in sc.objects:
        if ob.hide_render and not ob.hide_viewport:
            ob.hide_viewport = True
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    W, H = RW // paso, RH // paso
    R = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y").to_matrix()
    th = 18 / lens
    nuevos = {o.name for o in GRUPO if o.name.startswith("k5_bebida") or (o.parent and o.parent.name.startswith("k5_bebida"))}
    zona = cubierta = vis = 0
    for j in range(H):
        for i in range(W):
            d = (R @ Vector(((2 * (i + 0.5) / W - 1) * th, (1 - 2 * (j + 0.5) / H) * th * H / W, -1))).normalized()
            o, tapado = Vector(pos), False
            for _ in range(8):
                hit, loc, nrm, idx, ob, _m = sc.ray_cast(dg, o, d)
                if not hit:
                    break
                if ob.name in nuevos:
                    if not tapado:
                        vis += 1
                    tapado = True
                    o = loc + d * 0.001
                    continue
                m = ob.active_material
                if m and m.name.startswith("vidrio") and loc.y > 0.6 and loc.z < 1.87:
                    zona += 1
                    cubierta += tapado
                elif pasa_vidrio and ob.type == "MESH" and idx < len(ob.data.polygons) and \
                        (ob.material_slots[ob.data.polygons[idx].material_index].material.name.startswith(("vidrio", "mica"))):
                    o = loc + d * 0.001
                    continue
                break
    r1 = 100.0 * cubierta / zona if zona else float("nan")
    print(f"CAJA5 MEDIDA {nombre} camino {zona} px cubierto {r1:.2f} % -> r1 {'PASS' if zona and r1 <= 2 else 'FAIL'} | bebidas visibles {vis} px"
          f" (1 ray per {paso}x{paso} px)")


@opcion("caja5-bebidas-esc1")
def bebidas_esc1():
    """Scene 1's hold with the drink in the hand (owner 11-14: no console): between the rear headrests, 20 mm, the road
    through the windshield (transicion.CAMINO[0])."""
    cama_elegida()
    base_escena()
    bebida_en_mano()
    t1 = toma((T.CAMINO[0][1], T.CAMINO[0][2], T.CAMINO[0][3]), (T.CAMINO[0][1], T.CAMINO[0][2], v(T.CAMINO[0][3])))
    medir1("caja5-bebidas-esc1", *t1)
    return t1


@opcion("caja5-bebidas-esc4")
def bebidas_esc4():
    """Scene 4B's hold (passenger side, the lit cab) with the drink in the hand."""
    cama_elegida()
    t4 = esc4_cabina()
    p = bebida_en_mano()
    medir1("caja5-bebidas-esc4", *t4, pasa_vidrio=True, paso=2)
    cubre("caja5-bebidas-esc4", t4[0], p)
    return t4


CAM_CONSOLA = {  # (position, target, lens); "cabeceras" hides the drink's base behind the shifter (11-14 previews). Kept:
    # "alta", the bottle's rounded base shows on the left of the shifter knob; "lado" hides more of it (tmp/caja7/lado-base.png)
    "cabeceras": ((CX + 0.03, 0.28, 1.80), (CX + 0.03, 0.97, 1.30), 35),  # between the headrests, down over the lid onto the deck
    "alta": ((CX + 0.03, 0.58, 1.86), (CX + 0.02, 0.99, 1.27), 30),       # forward over the lid, steep enough to clear the shifter
    "lado": ((CX + 0.14, 0.50, 1.82), (CX + 0.02, 0.99, 1.27), 30),       # from the passenger side of the lid, past the shifter
}


def cerca_consola(var, cam="alta"):
    """(a) close: the console's lower deck from over the armrest, lit by scene 4B's own cab lamps (luz_costado "cabina") and a
    soft fill from behind the camera; the 11-14 still's 6 W lamp straight over the drinks made a hot spot on the can and left
    the cab black round it."""
    cama_elegida()
    base_escena()
    bebidas_consola(var)
    luz_costado("cabina", 1)
    luz("AREA", (CX + 0.05, 0.05, 1.95), 1.5, (1.0, 0.9, 0.8), mira=(CX + 0.03, 0.9, 1.3), size=0.8, parent=False)
    sin_camara()
    return CAM_CONSOLA[cam]


for _v in CONSOLA:
    opcion(f"caja5-bebidas-consola-{_v}")(lambda _v=_v: cerca_consola(_v))
for _c in CAM_CONSOLA:
    opcion(f"caja5-bebidas-consola-cam-{_c}")(lambda _c=_c: cerca_consola(CONSOLA_VAR, _c))


@opcion("caja5-bebidas-consola")
def bebidas_cerca_consola():
    """(a) close, the kept variant (CONSOLA_VAR)."""
    return cerca_consola(CONSOLA_VAR)


@opcion("caja5-bebidas-consola-esc1")
def bebidas_consola_esc1():
    """Scene 1's hold with the console drinks: do they enter the road band through the windshield (rule 1)?"""
    cama_elegida()
    base_escena()
    bebidas_consola()
    t1 = toma((T.CAMINO[0][1], T.CAMINO[0][2], T.CAMINO[0][3]), (T.CAMINO[0][1], T.CAMINO[0][2], v(T.CAMINO[0][3])))
    medir1("caja5-bebidas-consola-esc1", *t1)
    return t1


def cama_elegida():
    _g["caja2_b"] = lambda: vestir("elegida")  # base_escena() dresses bed B with the owner's picks, whatever ran before


def cerca_mano(cam, giro=None, nombre="caja5-bebidas-mano"):
    cama_elegida()
    base_escena()
    p = bebida_en_mano(giro=giro)
    c = p + Vector((0, 0, 0.11))
    luz("AREA", c + Vector((-0.25, 0.25, 0.45)), 5, (1.0, 0.85, 0.65), mira=c, size=0.4, parent=False)
    sin_camara()
    m = c + Vector((0, 0, 0.12))  # between the bottle and his face: both in frame, the door below kept to a strip
    pos = m + Vector(cam)
    print(f"CAJA5 CAMARA {nombre} x {pos.x - CX:+.2f} from the centre line (the door's outside face is at +0.78) ->"
          f" {'outside' if pos.x - CX > 0.80 else 'INSIDE'}")
    cubre(nombre, pos, p)
    return (pos, m, 32)


@opcion("caja5-bebidas-mano")
def bebidas_cerca_mano():
    """(b) close: Héctor's water bottle in his fist, from outside his window (scene 4B's side), closer."""
    return cerca_mano(VISTA_MANO * math.hypot(0.95, 0.20, 0.12))


for _gr in GIROS:  # the fist's turn about the wrist: the variants compared 11-14 (the fist height is searched for each)
    opcion(f"caja5-bebidas-mano-g{_gr}")(lambda _gr=_gr: cerca_mano(VISTA_MANO * math.hypot(0.95, 0.20, 0.12), _gr, f"caja5-bebidas-mano-g{_gr}"))


# Studio: each candidate alone in a closed grey box far above the set, key / fill / rim, 1:1 (render at 1080x1080).
ESTUDIO = Vector((CX, -40.0, 120.0))
SOLOS = [  # (option key, label, builder)
    ("pinata", "Piñata en bolsa", pinata_bolsa), ("globos", "Globos en bolsa", globos_bolsa),
    ("picado", "Papel picado", lambda: picado5((-0.6, 0, 0.9), (0.6, 0, 0.9))), ("bandera", "Bandera MT", bandera5),
    ("bocina", "Bocina de fiesta", bocina5), ("sombrerera", "Sombrerera", sombrerera5), ("cerveza", "Rejilla de cerveza", cerveza),
    ("luces", "Foquitos", lambda: luces5([(-0.6, 0, 0.9), (0.6, 0, 0.9)])), ("tabla", "Tabla de surf", tabla),
    ("sillas", "Sillas de playa", sillas), ("bidon", "Bidón", bidon), ("neon", "Letrero de neón", neon5),
    ("alien", "Alien inflable", alien),
]


def estudio(f):
    def op():
        antes = len(GRUPO)
        f()
        objs = [o for o in GRUPO[antes:] if o.type in ("MESH", "FONT", "CURVE")]
        for o in objs:
            if o.parent is None:
                o.location += ESTUDIO
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        c, s = (lo + hi) / 2, max((hi - lo).x, (hi - lo).y, (hi - lo).z, 0.25)
        caja((14, 14, 8), ESTUDIO + Vector((0, 0, 4.0 - 0.0005)), mat("k5_fondo", (0.045, 0.042, 0.04), 0.85), parent=False)
        if lo.z > ESTUDIO.z + 0.01:  # a stand for what was built in the air (the strings): two black posts
            for x in (lo.x, hi.x):
                cil(0.015, hi.z - ESTUDIO.z, Vector((x, c.y, (hi.z + ESTUDIO.z) / 2)), NEGRO5, verts=12, parent=False)
        d = Vector((-0.55, -1.0, 0.62)).normalized()
        cam = c + d * s * (2.6 if (hi - lo).z >= s else 2.0)  # a tall prop needs the room above and below
        luz("AREA", c + Vector((-1.6, -1.8, 2.2)) * max(1, s), 110 * max(1, s) ** 2, (1.0, 0.94, 0.86), mira=c, size=1.6 * max(1, s), parent=False)
        luz("AREA", c + Vector((2.0, -1.4, 0.8)) * max(1, s), 30 * max(1, s) ** 2, (0.9, 0.93, 1.0), mira=c, size=1.6 * max(1, s), parent=False)
        luz("AREA", c + Vector((0.6, 2.2, 2.0)) * max(1, s), 140 * max(1, s) ** 2, (1.0, 0.9, 0.8), mira=c, size=1.0 * max(1, s), parent=False)
        sin_camara()
        return (cam, c, 50)
    return op


for _k, _l, _f in SOLOS:
    opcion(f"caja5-estudio-{_k}")(estudio(_f))

if os.environ.get("CAJA5_PRUEBA"):  # measure one variant's scene-2 hold without rendering, with a histogram of what the rays stop on
    _t = OPC["caja5-" + os.environ["CAJA5_PRUEBA"] + "-esc2"]()
    print("CAJA5 PRUEBA camara", _t, "nuevos", [o.name for o in NUEVOS][:20])
    print("CAJA5 PRUEBA hist", sorted(HIST.items(), key=lambda kv: -kv[1])[:25])
    _g["SOLO"] = ["-"]

if os.environ.get("CAJA5_CPU"):  # the GPU is shared (grindsetdrone's TRELLIS): small studio frames can go on the CPU
    sc.cycles.device = "CPU"

# ---------------------------------------------------------------- utileria.py's render loop, over the options above
exec(compile(MARCA + _cola, U, "exec"), _g)
