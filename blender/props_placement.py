"""Props and placement (mothership queue 2026-11-13-mto-props-placement): new props (docs/design/props-placement/props.md) in
two arrangements per scene with a bed or cab view, A = the scene's picks + the new props where they first fit, B = re-placed by
the rules in docs/design/props-placement/reglas.md, plus one close-up per scene. Every still also writes a probe: one ray per
pixel at 1/5 size from the still's camera, new props hidden and shown, so rules 1-4 are numbers (stills/medidas-<still>.json).

Runs caja3.py (which runs utileria.py's scene and helpers) without its render loop, adds the options, then utileria.py's loop:

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/props_placement.py)" \
    -- <escena.py path (Windows)> <out_dir (Windows)> [samples] [pp1-b,pp-barra,...] [WxH]

No option list (or `all`) renders the owner's picks (FINALES: B in scenes 1, 2, 4, 6 and close-ups of the light bar, the
MT emblem and the strawberry). pp<N>-a and the pv-* variants stay callable by name.

The bed keeps the open pick #34 open: the floor pile is caja3 A (pass PP_CAMA=b for caja3 B); new bed props sit only on the
roll bar, the rails and the cab. Alexandro and Diego ride in the rear seats (base_escena); only the bed's seat cases and the
guitars left on them are hidden.
"""
import bpy, json, math, os
import numpy as np
from mathutils import Vector

C3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caja3.py")
_src = open(C3, encoding="utf8").read()
_cola = "# ---------------------------------------------------------------- utileria.py's render loop"
exec(compile(_src.split(_cola)[0], C3, "exec"), globals())
CAMA = os.environ.get("PP_CAMA", "a")


def vaciar_caja():
    """caja3's version also hides Alexandro and Diego; here they already sit in the rear seats, so hide only the seat cases and
    the guitars left on them."""
    for o in bpy.data.objects:
        if o.name.split(".")[0].startswith(("estuche_", "guitarra_")):
            for c in [o] + list(o.children_recursive):
                c.hide_render = True


# ---------------------------------------------------------------- probes: roof, windows, mirrors, rails (figures hidden)
def golpe(o, d):
    hit, loc, n, i, ob, _ = sc.ray_cast(dg, Vector(o), Vector(d))
    if not hit:
        return None
    ev = ob.evaluated_get(dg)
    try:
        m = ev.material_slots[ev.data.polygons[i].material_index].material
    except (IndexError, AttributeError):
        m = None
    return loc, ob.name, (m.name if m else "")


_SONDA_OCULTOS = [o for o in bpy.data.objects if (o in FIGURAS or o.name.split(".")[0].startswith(("estuche_", "guitarra_")))
                  and not o.hide_viewport]  # only these come back: Night B's fog and plants stay hidden from the rays
for o in _SONDA_OCULTOS:
    o.hide_viewport = True
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()

TECHO_Z = max((h[0].z for y in np.arange(-0.6, 1.0, 0.1) for dx in (-0.3, 0, 0.3)
               for h in [golpe((CX + dx, y, 5), (0, 0, -1))] if h), default=2.25)
_t = [y for y in np.arange(-1.6, 2.6, 0.02) for h in [golpe((CX, y, 5), (0, 0, -1))] if h and h[0].z > TECHO_Z - 0.06]
YT, YR = (max(_t), min(_t)) if _t else (1.0, -0.9)          # roof front / back edge
_w = [x for x in np.arange(0, 1.3, 0.01) for h in [golpe((CX + x, (YT + YR) / 2, 5), (0, 0, -1))] if h and h[0].z > TECHO_Z - 0.1]
WT = max(_w) if _w else 0.9                                 # roof half width
TECHO_IN = golpe((CX, 0.0, 1.6), (0, 0, 1))                 # cab ceiling from inside
CIELO_Z = TECHO_IN[0].z if TECHO_IN else TECHO_Z - 0.12
# windshield from inside: the glass hits along z; the first non-glass hit in front of it near the top centre is the mirror
VID = [(z, h[0], h[1]) for z in np.arange(1.3, 2.35, 0.01) for h in [golpe((CX + 0.25, 0.2, z), (0, 1, 0))] if h and h[2].startswith("vidrio")]
PB_ABAJO, PB_ARRIBA = (VID[0][1], VID[-1][1]) if VID else (Vector((CX, 1.3, 1.45)), Vector((CX, 0.95, 2.05)))
PB_OBJS = {v[2] for v in VID}
ESPEJO, _zs = None, []
for z in np.arange(2.12, 1.75, -0.005):  # the mirror hangs from the windshield top: the run of solid hits in front of the glass
    h = golpe((CX, 0.3, z), (0, 1, 0))
    if h and not h[2].startswith("vidrio") and 0.7 < h[0].y < PB_ARRIBA.y + 0.05:
        if _zs and _zs[-1][0] - z > 0.011:
            break
        _zs.append((z, h))
    elif _zs:
        break
if _zs:
    _m = _zs[len(_zs) // 2][1]
    ESPEJO = (_m[0], _m[1], _m[2], _zs[0][0], _zs[-1][0])  # centre hit, object, material, top z, bottom z
# rear window, from the bed looking forward
VT = [(z, h[0]) for z in np.arange(1.3, 2.35, 0.01) for h in [golpe((CX + 0.2, -1.3, z), (0, 1, 0))] if h and h[2].startswith("vidrio")]
VT_ABAJO, VT_ARRIBA = (VT[0][1], VT[-1][1]) if VT else (Vector((CX, -0.95, 1.55)), Vector((CX, -0.95, 1.95)))
# outside mirrors: hits beyond the body side
RETROS = {}
for lado in (-1, 1):
    pts = [h[0] for y in np.arange(0.3, 1.8, 0.04) for z in np.arange(1.3, 2.1, 0.04)
           for h in [golpe((CX + lado * 2.2, y, z), (-lado, 0, 0))] if h and 1.02 < abs(h[0].x - CX) < 1.5]
    if pts:
        RETROS[lado] = sum(pts, Vector()) / len(pts), max(abs(p.x - CX) for p in pts)
# bed rails
for x in (0.5, 0.55, 0.58, 0.6, 0.62, 0.66, 0.7):  # the bed wall's top, sampled across its thickness
    print("PP riel", x, [round(h[0].z, 3) for y in (-2.5, -2.1, -1.7) for h in [golpe((CX + x, y, 3.0), (0, 0, -1))] if h])
RIEL_Z = float(os.environ.get("PP_RIEL_Z", 0)) or 1.235  # bed wall top at x ±0.62-0.66 (the "PP riel" samples)


def _corrida(vals, cerca):
    """The contiguous run of sampled values (step <= 0.006) that contains the one nearest `cerca`."""
    if not vals:
        return []
    vals = sorted(vals)
    i = min(range(len(vals)), key=lambda k: abs(vals[k] - cerca))
    a = b = i
    while a > 0 and vals[a] - vals[a - 1] < 0.006:
        a -= 1
    while b < len(vals) - 1 and vals[b + 1] - vals[b] < 0.006:
        b += 1
    return vals[a:b + 1]


# the factory G 63 AMG 6x6 roof spoiler's two lamp pockets (the model has them, unlit): the run of non-paint hits on the
# visor face around x ±0.6, z 7 cm under the roof (sonda: x ±0.51-0.69, z 2.157-2.193, lamp faces at y 1.11-1.143)
BOLSAS = {}
for lado in (-1, 1):
    _f = lambda dx, z: golpe((CX + lado * dx, YT + 2.0, z), (0, -1, 0))
    xs = _corrida([dx for dx in np.arange(0.35, 0.9, 0.005) for h in [_f(dx, TECHO_Z - 0.072)] if h and h[0].y > 0 and h[2] != "pintura_satin"], 0.6)
    if not xs:
        continue
    xm = (xs[0] + xs[-1]) / 2
    zs = _corrida([z for z in np.arange(TECHO_Z - 0.16, TECHO_Z, 0.002) for h in [_f(xm, z)] if h and h[0].y > 0 and h[2] != "pintura_satin"],
                  TECHO_Z - 0.072)
    ys = [h[0].y for dx in np.arange(xs[0], xs[-1] + 1e-4, 0.01) for z in np.arange(zs[0], zs[-1] + 1e-4, 0.004) for h in [_f(dx, z)] if h]
    BOLSAS[lado] = (CX + lado * xs[0], CX + lado * xs[-1], zs[0], zs[-1], max(ys))
# the hood along the centre line: front edge and top (for the MT emblem)
CAPO = [(y, h[0].z) for y in np.arange(FRENTE + 0.2, FRENTE - 1.8, -0.01) for h in [golpe((CX, y, 4.0), (0, 0, -1))] if h and 1.2 < h[0].z < 1.75]
for n_, v_ in (("TECHO_Z", TECHO_Z), ("YT", YT), ("YR", YR), ("WT", WT), ("CIELO_Z", CIELO_Z), ("PB", (PB_ABAJO, PB_ARRIBA)),
               ("ESPEJO", ESPEJO), ("VT", (VT_ABAJO, VT_ARRIBA)), ("RETROS", RETROS), ("RIEL_Z", RIEL_Z), ("ARCO_Z", ARCO_Z),
               ("PORTON", PORTON), ("FRENTE", FRENTE), ("COLA", COLA),
               ("BOLSAS", BOLSAS), ("CAPO", CAPO[:3] + CAPO[-3:])):
    print("PP", n_, v_)
for o in _SONDA_OCULTOS:
    o.hide_viewport = False
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
ESP =Vector((CX, ESPEJO[0].y, (ESPEJO[3] + ESPEJO[4]) / 2)) if ESPEJO else Vector((CX, PB_ARRIBA.y - 0.12, PB_ARRIBA.z - 0.1))

# ---------------------------------------------------------------- new props: each one's objects are tagged with its id
PROP = {}      # id -> [objects]
LUMINOSO = set()


class prop:
    def __init__(self, pid, emisivo=False):
        self.pid, self.emisivo = pid, emisivo

    def __enter__(self):
        self.antes = len(GRUPO)

    def __exit__(self, *a):
        PROP.setdefault(self.pid, []).extend(o for o in GRUPO[self.antes:] if o.type != "LIGHT")
        if self.emisivo:
            LUMINOSO.add(self.pid)


ORO_L = lambda e: mat(f"pp_oro_luz_{e}", (1.0, 0.72, 0.3), 0.3, emit=e)
BOMBILLA = lambda e: mat(f"pp_bombilla_{e}", (1.0, 0.55, 0.2), 0.2, emit=e)  # warm: at 8 they clipped to white
SATIN = mat("pp_satin", (0.92, 0.92, 0.9), 0.35)
TERCIOPELO = mat("pp_terciopelo", (0.05, 0.008, 0.012), 0.9)
FLECO = mat("pp_fleco", (0.85, 0.62, 0.25), 0.45, 0.6)
PLASTICO_B = mat("pp_plastico_blanco", (0.85, 0.85, 0.83), 0.4)
LLANTA = mat("pp_llanta", (0.015, 0.015, 0.015), 0.85)


def entre(a, b, r, m, verts=8):
    a, b = Vector(a), Vector(b)
    d = b - a
    return cil(r, d.length, (a + b) / 2, m, rot=(0, math.atan2(math.hypot(d.x, d.y), d.z), math.atan2(d.y, d.x) + math.pi / 2), verts=verts, parent=False)


def barra_luces(variante="fabrica"):
    """P1, the real part: the factory G 63 AMG 6x6 roof spoiler carries one LED lamp in each outer pocket (refs [12b], [12c]:
    a clear lens over a black housing with five round reflector cups). The truck model has the pockets, unlit; this fills
    them. variante 'xlp' adds the Brabus XLP 800 6x6 upper tier (ref [12], a W465 part): 27 round reflectors in a gloss black
    tray along the visor top, and six cups per pocket like its lower modules. White LED (~6000 K); each lamp also throws a
    spot ahead, so the light lands on the hood and the road the way a lit lamp's does."""
    blanco = (1.0, 0.96, 0.92)
    emisor = mat("pp_led_emisor", blanco, 0.2, emit=60.0)      # a tiny, very bright die: lights its cup like a real LED
    copa = mat("pp_led_copa", (0.9, 0.9, 0.9), 0.12, metal=1.0)
    caja_n = mat("pp_led_caja", (0.012, 0.012, 0.013), 0.25)
    mica = mat("pp_led_mica", (1.0, 1.0, 1.0), 0.04, trans=1.0)

    def copas(xs, y, z, r):
        for x in xs:
            bpy.ops.mesh.primitive_cone_add(radius1=r * 0.35, radius2=r, depth=r * 0.7, location=(x, y - r * 0.35, z),
                                            rotation=(-math.pi / 2, 0, 0), vertices=24, end_fill_type="NOTHING")
            bpy.ops.object.shade_smooth()
            _fin(bpy.context.object, copa, False)
            esfera(r * 0.28, (x, y - r * 0.55, z), emisor, parent=False)

    def lampara(x0, x1, z0, z1, yf, n, foco=True):
        w, h = x1 - x0, z1 - z0
        paso = w / n
        r = min(paso, h) * 0.44
        caja((w, 0.024, h), ((x0 + x1) / 2, yf - 0.001 - r * 0.7 - 0.012, (z0 + z1) / 2), caja_n, parent=False)  # behind the cups
        copas([x0 + (i + 0.5) * paso for i in range(n)], yf - 0.001, (z0 + z1) / 2, r)
        caja((w, 0.003, h), ((x0 + x1) / 2, yf + 0.0015, (z0 + z1) / 2), mica, parent=False)
        if foco:  # the beam: aimed ahead and a little down, 14 m out
            o = luz("SPOT", ((x0 + x1) / 2, yf + 0.02, (z0 + z1) / 2), 25, blanco, mira=((x0 + x1) / 2, yf + 14, 0.0), parent=False)
            o.data.spot_size, o.data.spot_blend, o.data.shadow_soft_size = math.radians(55), 0.6, 0.03

    with prop("P1", emisivo=True):
        for lado, (xa, xb, z0, z1, ymax) in BOLSAS.items():
            lampara(min(xa, xb), max(xa, xb), z0, z1, ymax + 0.012, 6 if variante == "xlp" else 5)  # clear of the model's own lamp
        if variante == "xlp":
            w, y, z = WT * 1.8, YT - 0.03, TECHO_Z + 0.035
            caja((w + 0.06, 0.12, 0.085), (CX, y - 0.07, z), mat("pp_xlp_negro", (0.01, 0.01, 0.011), 0.12), bevel=0.012, parent=False)
            lampara(CX - w / 2, CX + w / 2, z - 0.032, z + 0.032, y + 0.022, 27, foco=False)
            for dx in (-w / 3, 0, w / 3):
                o = luz("SPOT", (CX + dx, y + 0.05, z), 25, blanco, mira=(CX + dx, y + 20, 0.0), parent=False)
                o.data.spot_size, o.data.spot_blend = math.radians(50), 0.5


def franja(donde, texto_="MAFIA TUMBADA"):
    """P2, ref [8]: a name strip across the top of the glass. donde: 'parabrisas' (outside, read from ahead) or 'trasera'."""
    from mathutils import Matrix
    if donde == "parabrisas":   # read from ahead: the reader's right is world -X
        a, b, der = PB_ABAJO, PB_ARRIBA, Vector((-1, 0, 0))
    else:                       # read from behind
        a, b, der = VT_ABAJO, VT_ARRIBA, Vector((1, 0, 0))
    d = (b - a).normalized()
    n = der.cross(d)            # faces the reader
    rot = Matrix((der, d, n)).transposed().to_euler()
    alto = 0.13
    c = b - d * (alto / 2 + 0.015) + n * 0.008
    with prop("P2"):
        plano(1.25, alto, c, mat("pp_franja", (0.03, 0.03, 0.035), 0.3, alpha=0.85), rot=rot, parent=False)
        texto(texto_, 0.085, c + n * 0.003, mat("pp_franja_letra", (0.85, 0.8, 0.7), 0.4, emit=0.25),
              font="impact.ttf", rot=rot, parent=False, ancho=1.25)


def flecos(partida, largo=0.06):
    """P3, ref [15]: fringe valance inside the windshield top: a velvet band with PURA MT and gold fringe. partida=True leaves
    the mirror clear (rule 1), False runs it full width."""
    b = PB_ARRIBA
    y, z = b.y - 0.05, b.z - 0.05
    tramos = [(-0.62, -0.13), (0.13, 0.62)] if partida else [(-0.62, 0.62)]
    with prop("P3"):
        for x0, x1 in tramos:
            caja((x1 - x0, 0.012, 0.07), (CX + (x0 + x1) / 2, y, z), TERCIOPELO, parent=False)
            n = int((x1 - x0) / 0.022)
            for i in range(n):
                x = CX + x0 + (i + 0.5) * (x1 - x0) / n
                cil(0.003, largo, (x, y, z - 0.035 - largo / 2), FLECO, verts=4, parent=False)
        xs = (-0.37, 0.37) if partida else (0.0,)
        for xt in xs:
            texto("PURA MT", 0.04, (CX + xt, y - 0.008, z + 0.002), ORO_L(1.5), font="impact.ttf", parent=False)  # faces the cab


def banderin_tablero(x):
    """P4, ref [9]: a pennant on a desk stand and an air-freshener bottle, low on the dash at x."""
    o_, h = Vector((x, 0.6, 2.2)), None
    for _ in range(4):  # step through the windshield glass to the dash top
        h = golpe(o_, (0, 0.45, -1))
        if not h or not h[2].startswith("vidrio"):
            break
        o_ = h[0] + Vector((0, 0.45, -1)).normalized() * 0.003
    base = h[0] if h else Vector((x, 0.95, 1.45))
    print("PP banderin", x, h)
    with prop("P4"):
        cil(0.03, 0.012, base + Vector((0, 0, 0.006)), NEGRO, parent=False)
        cil(0.0025, 0.16, base + Vector((0, 0, 0.09)), CROMO, verts=6, parent=False)
        me = bpy.data.meshes.new("pp_banderin")
        me.from_pydata([(0, 0, 0), (0.13, 0, -0.035), (0, 0, -0.07)], [], [(0, 1, 2)])
        o = bpy.data.objects.new("pp_banderin", me)
        sc.collection.objects.link(o)
        o.location = base + Vector((0, 0, 0.165))
        o.rotation_euler = (0, 0, math.radians(200))
        _fin(o, ORO, False)
        cil(0.022, 0.07, base + Vector((0.09, 0.02, 0.035)), mat("pp_frasco", (0.05, 0.02, 0.02), 0.1, trans=0.5), parent=False)
        cil(0.012, 0.025, base + Vector((0.09, 0.02, 0.083)), CROMO, parent=False)


FRESA_GLB = os.environ.get("PP_FRESA") or os.path.join(REPO, "blender", "props", "strawberry-s2-oro.glb")  # the owner's pick (11-14): the friend's berry with gold 3D seeds
FRESA_ALTO = float(os.environ.get("PP_FRESA_ALTO", 0.0647))  # whole mesh height: the friend's berry is ringless with a long stem, so 0.0647 makes its BODY 4.1 cm (a ring-top-to-tip model wants 0.041)
_FRESA = {}


def _fresa_mallas(archivo):
    """The charm's meshes from its one asset file (blender/fresa_charm.py's contract: Z up, metres, origin at the hang point),
    baked to world space and normalised: FRESA_ALTO tall, top centre at the origin, so a friend's model drops in at any scale."""
    if archivo not in _FRESA:
        antes = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=archivo)
        nuevos = [o for o in bpy.data.objects if o not in antes]
        mallas = []
        for o in nuevos:
            if o.type == "MESH":
                me = o.data.copy()
                me.transform(o.matrix_world)
                mallas.append(me)
        for o in nuevos:
            bpy.data.objects.remove(o)
        pts = [v.co for me in mallas for v in me.vertices]
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        k = FRESA_ALTO / (hi.z - lo.z)
        from mathutils import Matrix
        m = Matrix.Scale(k, 4) @ Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, hi.z)))
        for me in mallas:
            me.transform(m)
        _FRESA[archivo] = mallas
    return _FRESA[archivo]


def fresa(largo, archivo=None):
    """P5, ref [9]: the strawberry charm under the mirror (the PUTIFRESA joke), on a cord `largo` long. The charm is one
    swappable file (FRESA_GLB, or PP_FRESA=<path>)."""
    top = Vector((ESP.x, ESP.y, ESPEJO[4] if ESPEJO else ESP.z - 0.04))
    with prop("P5"):
        cil(0.0006, largo, top - Vector((0, 0, largo / 2)), mat("pp_cordon", (0.6, 0.02, 0.03), 0.6), verts=6, parent=False)
        for me in _fresa_mallas(archivo or FRESA_GLB):
            o = bpy.data.objects.new("pp_fresa", me)
            sc.collection.objects.link(o)
            o.location = top - Vector((0, 0, largo))
            o.rotation_euler = (0, 0, 0.5)
            _fin(o, None, False)


def trompetas():
    """P6, ref [6]: two white horn speakers on a roof bar, facing forward and out."""
    with prop("P6"):
        y = (YT + YR) / 2 + 0.1
        caja((0.9, 0.05, 0.05), (CX, y, TECHO_Z + 0.06), NEGRO, parent=False)
        for lado in (-1, 1):
            p = Vector((CX + lado * 0.32, y + 0.12, TECHO_Z + 0.2))
            cono(0.03, 0.13, 0.32, p, PLASTICO_B, rot=(-math.pi / 2, 0, lado * -0.45), parent=False)
            entre(p - Vector((0, 0.1, 0.0)), (CX + lado * 0.32, y, TECHO_Z + 0.08), 0.015, NEGRO)


def monos(lados):
    """P7, ref [13]: white satin rosettes with two tails on the outside mirrors."""
    with prop("P7"):
        for lado in lados:
            if lado not in RETROS:
                continue
            c, ancho = RETROS[lado]
            p = Vector((CX + lado * (ancho + 0.03), c.y - 0.02, c.z - 0.02))
            for k in range(4):
                toro(0.06, 0.014, p + Vector((0, 0, 0)), SATIN, rot=(0, math.pi / 2, k * math.pi / 4), parent=False)
            for dy in (-0.03, 0.03):
                plano(0.05, 0.40, p + Vector((lado * 0.005, dy - 0.04, -0.22)), SATIN, rot=(math.pi / 2 - 0.25, 0, math.pi / 2), parent=False)


def picado_techo():
    """P8, ref [16]: papel picado strung across the cab ceiling (caja3's string)."""
    with prop("P8"):  # two strings along the ceiling sides, front to back, panels at a third of caja3's size (8 × 10 cm)
        for lado in (-1, 1):
            antes = len(GRUPO)
            papel_picado((CX + lado * 0.5, 0.85, CIELO_Z - 0.02), (CX + lado * 0.5, -0.55, CIELO_Z - 0.02), n=8, caida=0.03)
            for o in GRUPO[antes:]:
                if o.type == "MESH" and abs(o.scale.x - 0.24) < 1e-4:
                    o.scale = (0.08, 0.10, 1)
                    o.location.z += 0.10


def bombillas(tramos, e, paso=0.11):
    """P9, refs [1], [19]-[22]: warm bulbs on a wire along the given polylines (outline lights)."""
    m, alambre = BOMBILLA(e), mat("pp_alambre", (0.02, 0.02, 0.02), 0.5)
    with prop("P9", emisivo=True):
        for pts in tramos:
            for a, b in zip(pts, pts[1:]):
                a, b = Vector(a), Vector(b)
                entre(a, b, 0.003, alambre, verts=4)
                n = max(1, int((b - a).length / paso))
                for i in range(n):
                    esfera(0.02, a.lerp(b, (i + 0.5) / n), m, parent=False)


def contorno_caja(arco=True, rieles=True):
    xi, xd = CX - 0.64, CX + 0.64  # on the wall tops
    y0, y1 = PORTON.y + 0.05, YC
    t = []
    if rieles:
        t += [[(xi, y1, RIEL_Z + 0.02), (xi, y0, RIEL_Z + 0.02), (xd, y0, RIEL_Z + 0.02), (xd, y1, RIEL_Z + 0.02)]]
    if arco:
        t += [[(xi + 0.04, YC - 0.06, RIEL_Z + 0.05), (xi + 0.04, YC - 0.06, ARCO_Z + 0.02), (xd - 0.04, YC - 0.06, ARCO_Z + 0.02),
               (xd - 0.04, YC - 0.06, RIEL_Z + 0.05)]]
    return t


def marquesina(e, texto_="PURA MT"):
    """P10, refs [2], [3], [11], [22]: a lit marquee sign on top of the roll bar, facing back: gold letters on a black panel, a
    bulb border. e = emission of the letters (the bulbs run at e/2)."""
    w, h = 0.95, 0.30
    c = Vector((CX, YC - 0.02, ARCO_Z + 0.07 + h / 2))
    with prop("P10", emisivo=True):
        caja((w, 0.05, h), c, NEGRO, bevel=0.01, parent=False)
        for lado in (-1, 1):
            caja((0.03, 0.03, 0.09), (CX + lado * w * 0.35, YC - 0.02, ARCO_Z + 0.04), NEGRO, parent=False)
        texto(texto_, 0.17, c + Vector((0, -0.03, -0.01)), ORO_L(e), font="impact.ttf", extr=0.006, parent=False, ancho=1.1)
        mb = BOMBILLA(e / 2)
        for i in range(14):
            for z in (c.z - h / 2 + 0.025, c.z + h / 2 - 0.025):
                esfera(0.012, (CX - w / 2 + 0.04 + i * (w - 0.08) / 13, c.y - 0.03, z), mb, parent=False)


def bajo_luz(color=(1.0, 0.6, 0.18), w=300):
    """P11, ref [17]: underglow, two rectangular area lights under the body aimed at the road."""
    for y in (FRENTE - 1.4, (FRENTE + COLA) / 2 - 0.6):
        o = luz("AREA", (CX, y, 0.32), w, color, mira=(CX, y, 0.0), parent=False)
        o.data.shape, o.data.size, o.data.size_y = "RECTANGLE", 1.4, 2.0
        o.visible_camera = False


def parrilla_techo():
    """P12, refs [12], [7]: a roof rack with a strapped spare tyre and a road case."""
    with prop("P12"):
        y0, y1 = YR + 0.15, YT - 0.25
        for lado in (-1, 1):
            caja((0.04, y1 - y0, 0.04), (CX + lado * WT * 0.8, (y0 + y1) / 2, TECHO_Z + 0.08), ACERO, parent=False)
        for k in range(5):
            caja((WT * 1.6, 0.03, 0.03), (CX, y0 + k * (y1 - y0) / 4, TECHO_Z + 0.08), ACERO, parent=False)
        toro(0.29, 0.11, (CX - 0.25, (y0 + y1) / 2 + 0.3, TECHO_Z + 0.21), LLANTA, parent=False)
        caja((0.6, 0.45, 0.35), (CX + 0.35, (y0 + y1) / 2 - 0.3, TECHO_Z + 0.27), LAMINADO, bevel=0.02, parent=False)
        cincho((CX - 0.6, (y0 + y1) / 2 - 0.3, TECHO_Z + 0.45), (CX + 0.8, (y0 + y1) / 2 - 0.3, TECHO_Z + 0.45), CINTA_N)


def banderines():
    """P13, ref [18]: two band pennants on short poles at the bed's rear corners (never a national flag)."""
    with prop("P13"):
        for lado in (-1, 1):
            base = Vector((CX + lado * 0.6, PORTON.y + 0.08, RIEL_Z))
            cil(0.008, 0.7, base + Vector((0, 0, 0.35)), NEGRO, verts=6, parent=False)
            me = bpy.data.meshes.new("pp_pennant")
            me.from_pydata([(0, 0, 0), (0, -0.32, -0.08), (0, 0, -0.16)], [], [(0, 1, 2)])
            o = bpy.data.objects.new("pp_pennant", me)
            sc.collection.objects.link(o)
            o.location = base + Vector((0, 0, 0.7))
            _fin(o, ORO, False)


FUENTE_MT = os.path.join(REPO, "blender", "fuentes", "GrenzeGotisch-800.ttf")  # OFL, converted from @fontsource woff2
ORO_MARCA = mat("pp_oro_marca", (0.768, 0.426, 0.021), 0.22, metal=1.0)  # DESIGN.md --gold oklch(78% 0.15 85), linear sRGB
# pass 2 (owner never saw the options): the emblem in two blackletters at the same CAP height, so the size labels hold for both.
# (file, M cap height in em, "MT" advance in em, lowest point of the M below the baseline in em), measured with fontTools; Grenze at size 0.235 has a 14.6 cm cap.
FUENTES_MT = {"grenze": (FUENTE_MT, 0.622, 1.408, -0.011),
              "pirata": (os.path.join(REPO, "blender", "fuentes", "PirataOne-400.ttf"), 0.771, 1.005, -0.032)}
CAP_MT = {"parado": 0.146, "grande": 0.146 * 18 / 14, "plano": 0.199, "elegido": 0.215}  # m cap height: ~14 cm standing (pass 1), ~18 cm, flat (0.32 em of Grenze), the owner's pick (Pirata One, ~21.5 cm, scene 6 >= 0.1 %)


def emblema(modo="parado", fuente=None):
    """P15, the owner's pick in place of the cattle horns: a gold MT on the hood in the band's blackletter (Grenze Gotisch
    ExtraBold, or Pirata One), extruded and bevelled, brand gold as polished metal. modo 'parado': stands bolted on a black
    plinth at the hood's front edge, read from ahead (scene 6's camera sits below the hood, so a flat badge would be edge-on);
    'grande': the same at ~18 cm letters; 'plano': a large flat badge on the hood, read from ahead."""
    ruta, cap_em, ancho_em, pie_em = FUENTES_MT[fuente or VAR["fuente"]]
    cap = CAP_MT[modo]
    tam = cap / cap_em
    k = cap / CAP_MT["parado"]
    yb, zb = CAPO[0] if CAPO else (FRENTE - 0.2, 1.5)
    tapa = [(y, z) for y, z in CAPO if y > yb - 0.6]
    ztop = max(z for y, z in tapa) if tapa else zb
    with prop("P15"):
        cu = bpy.data.curves.new("pp_emblema", "FONT")
        cu.body, cu.font = "MT", bpy.data.fonts.load(ruta, check_existing=True)
        cu.align_x, cu.align_y = "CENTER", "BOTTOM_BASELINE"
        cu.bevel_resolution = 2
        o = bpy.data.objects.new("pp_emblema", cu)
        sc.collection.objects.link(o)
        if modo != "plano":
            y = yb - 0.12
            z = max((zz for yy, zz in CAPO if abs(yy - y) < 0.02), default=ztop)
            # cap 14.6 cm (size 0.235 in Grenze): 0.15 covered 0.039 % of scene 6's frame and 0.22 0.09 %, under rule 2's 0.1 % line
            cu.size, cu.extrude, cu.bevel_depth = tam, 0.009 * k, 0.002 * k
            o.location, o.rotation_euler = (CX, y, z + 0.0215), (math.pi / 2, 0, math.pi)  # baseline seated on the plinth
            w = ancho_em * tam * 0.97
            caja((w, 0.06 * k, 0.02), (CX, y, z + 0.01), NEGRO, bevel=0.005, parent=False)
            for dx in (-1, 1):
                cil(0.007 * k, 0.006, (CX + dx * (w / 2 - 0.035 * k), y + 0.015 * k, z + 0.021), CROMO, verts=6, parent=False)
        else:
            y = yb - 0.45
            zh = max((z for yy, z in CAPO if abs(yy - y) < 0.02), default=ztop)
            cu.size, cu.extrude, cu.bevel_depth = tam, 0.002, 0.001
            o.location, o.rotation_euler = (CX, y, zh + 0.003 - pie_em * tam), (0, 0, math.pi)
        _fin(o, ORO_MARCA, False)


# ---------------------------------------------------------------- the bed (#34 stays open) and its bar-level re-place in B
_techo_caja3 = techo_caja


def cama(barra="caja3"):
    """The floor pile is caja3 A (or B with PP_CAMA=b). barra: 'caja3' keeps its bar items (piñata, two balloon bunches, the
    flag); 'reglas' keeps the piñata under the bar and one balloon bunch low at the rear left corner, and drops the flag (one
    peak: the marquee)."""
    global techo_caja
    if barra == "reglas":
        def techo_caja(x0, x1, y):
            pinata((CX, y - 0.35, ARCO_Z - 0.45), 0.2)
            cil(0.004, 0.5, (CX, y - 0.18, ARCO_Z - 0.12), mat("u_hilo", (0.9, 0.9, 0.9), 0.5), rot=(0.55, 0, 0), verts=6, parent=False)
            globos((CX - 0.55, PORTON.y + 0.15, RIEL_Z), 4, alto=0.45)
    else:
        techo_caja = _techo_caja3
    antes = len(GRUPO)
    (caja3_b if CAMA == "b" else caja3_a)()
    techo_caja = _techo_caja3
    if barra == "reglas":
        for o in GRUPO[antes:]:
            if o.name.startswith("k3_bandera"):
                o.hide_render = True


# ---------------------------------------------------------------- probe: rules 1-4 as numbers
ZONAS = {}  # still -> function(obj_name, mat_name, v) -> zone name or None (v: 0 top .. 1 bottom)


def zona_1(ob, m, p):
    """The mirror is a box around the probed mirror point (its mesh is shared with the whole interior); the road is every
    pixel that sees the windshield glass."""
    if ESPEJO and abs(p.x - ESP.x) < 0.16 and abs(p.y - ESP.y) < 0.08 and ESPEJO[4] - 0.01 < p.z < ESPEJO[3] + 0.01:
        return "espejo"
    if ob in PB_OBJS and p.z < PB_ABAJO.z + 0.7 * (PB_ARRIBA.z - PB_ABAJO.z):  # the road band, not the sky over it
        return "camino"
    return None


ZONA = {
    "1": zona_1,
    "2": lambda ob, m, p: "calcas" if m.startswith("c3_") else None,
    "4": lambda ob, m, p: "ventanas" if m.startswith("vidrio") else None,
    "6": lambda ob, m, p: "placa" if m.startswith("u_placa") else ("faros" if m == "faros" else None),
}
SONDA_DIV = 5


def sondear(nombre, escena, pos, mira, lens):
    W, H = RW // SONDA_DIV, RH // SONDA_DIV
    q = (Vector(mira) - Vector(pos)).to_track_quat("-Z", "Y")
    tx = math.tan(math.atan(18 / lens))
    ty = tx * H / W
    dirs = [q @ Vector(((2 * (i + 0.5) / W - 1) * tx, (1 - 2 * (j + 0.5) / H) * ty, -1)) for j in range(H) for i in range(W)]
    duenio = {o.name: pid for pid, objs in PROP.items() for o in objs}
    previo = {o.name: o.hide_viewport for o in bpy.data.objects}
    for o in bpy.data.objects:
        o.hide_viewport = o.hide_render
    leyenda, pases = {"otro": 0}, []
    for mostrar in (False, True):
        for objs in PROP.values():
            for o in objs:
                o.hide_viewport = (not mostrar) or o.hide_render
        bpy.context.view_layer.update()
        global dg
        dg = bpy.context.evaluated_depsgraph_get()
        ids = np.zeros(W * H, np.uint16)
        for k, d in enumerate(dirs):
            h = golpe(pos, d)
            if not h:
                continue
            ob, m = h[1], h[2]
            if m.startswith("vidrio") and mostrar:  # a prop seen through the glass covers that zone too (P15 from the cab)
                h2 = h
                for _ in range(3):
                    h2 = golpe(h2[0] + Vector(d).normalized() * 0.003, d)
                    if not h2 or not h2[2].startswith("vidrio"):
                        break
                if h2 and h2[1] in duenio:
                    ob = h2[1]
            pid = duenio.get(ob)
            et = ("prop:" + pid) if pid else (("zona:" + z) if (z := ZONA[escena](ob, m, h[0])) else "otro")
            ids[k] = leyenda.setdefault(et, len(leyenda))
        pases.append(ids)
    for o in bpy.data.objects:
        o.hide_viewport = previo.get(o.name, False)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    inv = {v: k for k, v in leyenda.items()}
    sin, con = pases
    med = {"still": nombre, "escena": escena, "W": W, "H": H, "zonas": {}, "props": {}}
    for et, i in leyenda.items():
        if et.startswith("zona:"):
            z = sin == i
            tapado = z & np.array([inv[x].startswith("prop:") for x in con])
            med["zonas"][et[5:]] = {"px": int(z.sum()), "tapado": int(tapado.sum()),
                                    "pct": round(100 * tapado.sum() / max(z.sum(), 1), 2)}
        if et.startswith("prop:"):
            med["props"][et[5:]] = {"px": int((con == i).sum()), "pct_cuadro": round(100 * (con == i).sum() / (W * H), 3),
                                    "luminoso": et[5:] in LUMINOSO}
    os.makedirs(OUT, exist_ok=True)
    np.save(os.path.join(OUT, f"{nombre}-id.npy"), con.reshape(H, W))
    med["leyenda"] = leyenda
    with open(os.path.join(OUT, f"medidas-{nombre}.json"), "w", encoding="utf8") as f:
        json.dump(med, f, ensure_ascii=False, indent=1)
    print("SONDA", json.dumps({k: med[k] for k in ("still", "zonas", "props")}, ensure_ascii=False))


def toma_pp(nombre, escena, f):
    """Register an option that builds, probes from its own camera, and returns the camera to utileria's loop."""
    @opcion(nombre)
    def _op():
        PROP.clear()
        LUMINOSO.clear()
        pos, mira, lens = f()
        sondear(nombre, escena, pos, mira, lens)
        return pos, mira, lens


# ---------------------------------------------------------------- scenes
CAM1 = (T.CAMINO[0][1], T.CAMINO[0][2], T.CAMINO[0][3])


VAR = {"barra": "fabrica", "emblema": "elegido", "fuente": "pirata", "fresa": None}  # the picks; the pv-* options swap one at a time


def camion():
    """What rides on the truck in every scene (owner, 11-13): the real roof lamps and the gold MT on the hood; the roll-bar bulbs
    (P9, as pp2-b: the arch only, 2.5; owner 11-15 05:41 "bring the roll-bar bulbs back", montaje had left them out); then the props
    phase's additions (utileria.CAMION_EXTRA: the console screen, the r1 stickers, and caja5's console drink when caja5 is loaded)."""
    barra_luces(VAR["barra"]); emblema(VAR["emblema"]); bombillas(contorno_caja(rieles=False), 2.5)
    for f in CAMION_EXTRA:
        f()


def esc1(arreglo="b"):
    base_escena(cama=False)
    if arreglo == "a":   # where each first fits: full-width valance, ceiling papel picado, pennant mid-dash, long charm
        flecos(partida=False); picado_techo(); banderin_tablero(CX - 0.1); fresa(0.16)
    else:                # rules 1, 3, 6: the mirror and the road clear, three props, the pennant in the passenger corner
        flecos(partida=True, largo=0.025); banderin_tablero(CX + 0.14); fresa(0.045, VAR["fresa"]); emblema(VAR["emblema"])  # rule 1: a 6 cm fringe covered 3 % of the road
    return CAM1


def esc2(arreglo="b"):
    base_escena(cama=False)
    calcas3_mix()
    luces3(VISTA_ESC2()[0])
    if arreglo == "a":   # the caja3 bar as it is; the new props added on top: marquee full on, bulbs everywhere, pennants
        cama("caja3"); marquesina(10.0); bombillas(contorno_caja(), 4.0); franja("trasera"); banderines()
    else:                # owner: no marquee. Rules 4, 5: the bulbs trace the roll bar only, the piñata under it is the peak
        cama("reglas"); bombillas(contorno_caja(rieles=False), 2.5)
    relleno_caja(VISTA_ESC2()[0])
    return VISTA_ESC2()


def esc4(arreglo="b"):
    base_escena(cama=False)
    luz_costado("relleno", 1)  # scene-4 light pick open: the fill (A), recommended; self-lit props read under either
    if arreglo == "a":
        cama("caja3"); barra_luces(); trompetas(); parrilla_techo(); monos((1, -1)); marquesina(10.0)
        bombillas(contorno_caja(), 4.0); bajo_luz()
    else:                # rule 5: the roof carries only its own lamps, no marquee; rule 1: nothing above the windows
        cama("reglas"); camion(); monos((1,)); bombillas(contorno_caja(arco=False), 2.5); bajo_luz()  # camion() has the arch's
    return ((CX + 6.2, -0.3, 2.6), (CX, -0.3, 1.45), 24)


def esc6(arreglo="b"):
    base_escena(cama=False)
    placa3()
    if arreglo == "a":
        barra_luces(); trompetas(); franja("parabrisas"); monos((1, -1)); bajo_luz(); flecos(partida=False)
    else:                # rule 4: the plate stays brightest after the headlights; rule 3: three reads
        camion(); franja("parabrisas"); monos((1, -1)); bajo_luz(w=150); flecos(partida=True)
    return ((CX + 1.4, FRENTE + 6.5, 0.95), (CX + 0.1, FRENTE - 1.5, 1.2), 32)


for _e, _f in (("1", esc1), ("2", esc2), ("4", esc4), ("6", esc6)):
    for _a in ("a", "b"):
        toma_pp(f"pp{_e}-{_a}", _e, lambda f=_f, a=_a: f(a))


def _bolsa():
    xa, xb, z0, z1, y = BOLSAS.get(1, (CX + 0.51, CX + 0.69, 2.157, 2.193, 1.14))
    return Vector(((xa + xb) / 2, y, (z0 + z1) / 2))


def _emblema_pos():
    yb, zb = CAPO[0] if CAPO else (FRENTE - 0.2, 1.5)
    y = yb - (0.45 if VAR["emblema"] == "plano" else 0.12)
    return Vector((CX, y, max((z for yy, z in CAPO if abs(yy - y) < 0.02), default=zb)))


def _fresa_pos():
    return Vector((ESP.x, ESP.y, (ESPEJO[4] if ESPEJO else ESP.z - 0.04) - 0.045 - 0.02))


# close-ups of the three new pieces, in the B scenes
CERCA = {
    "barra": ("6", esc6, lambda: (_bolsa() + Vector((0.55, 1.15, 0.28)), _bolsa() + Vector((-0.38, 0, -0.03)), 40)),
    "emblema": ("6", esc6, lambda: (_emblema_pos() + Vector((0.6, 1.25, 0.32)), _emblema_pos() + Vector((0, 0, 0.09)), 50)),
    "fresa": ("1", esc1, lambda: (_fresa_pos() + Vector((-0.12, -0.36, 0.02)), _fresa_pos(), 50)),
}
for _n, (_e, _f, _c) in CERCA.items():
    toma_pp(f"pp-{_n}", _e, lambda f=_f, c=_c: (f("b"), c())[1])


def variante(clave, valor, toma):
    """pv-<toma>-<valor>: the same still with one pick swapped (for the side-by-side), then the pick restored."""
    e, f, cam = toma

    def _op():
        viejo = VAR[clave]
        VAR[clave] = valor
        try:
            f("b")
            return cam()
        finally:
            VAR[clave] = viejo
    return e, _op


_FRESAS = os.path.join(REPO, "tmp", "fresa")
VARIANTES = {
    "pv-barra-xlp": variante("barra", "xlp", CERCA["barra"]),
    "pv-6-xlp": variante("barra", "xlp", ("6", esc6, lambda: ((CX + 1.4, FRENTE + 6.5, 0.95), (CX + 0.1, FRENTE - 1.5, 1.2), 32))),
    "pv-emblema-plano": variante("emblema", "plano", ("6", esc6, lambda: (_emblema_pos() + Vector((0.55, 1.4, 0.75)), _emblema_pos(), 40))),
    "pv-fresa-resina": variante("fresa", os.path.join(_FRESAS, "fresa-resina.glb"), CERCA["fresa"]),
    "pv-fresa-peluche": variante("fresa", os.path.join(_FRESAS, "fresa-peluche.glb"), CERCA["fresa"]),
}
for _n, (_e, _op) in VARIANTES.items():
    toma_pp(_n, _e, _op)


def _em_pos(modo):
    yb, zb = CAPO[0] if CAPO else (FRENTE - 0.2, 1.5)
    y = yb - (0.45 if modo == "plano" else 0.12)
    return Vector((CX, y, max((z for yy, z in CAPO if abs(yy - y) < 0.02), default=zb)))


def _em(modo, fuente, cerca):
    """em-<modo>-<fuente>: scene 6's truck with one emblem option, from one 3/4 camera that sees all three sizes (cerca) or from
    scene 6's own low camera (not cerca)."""
    def _op():
        viejo = (VAR["emblema"], VAR["fuente"])
        VAR["emblema"], VAR["fuente"] = modo, fuente
        try:
            cam6 = esc6("b")
            if not cerca:
                return cam6
            a = _em_pos("parado")
            return (a + Vector((0.55, 1.35, 0.55)), a + Vector((0, -0.14, 0.05)), 55)
        finally:
            VAR["emblema"], VAR["fuente"] = viejo
    return _op


for _m in ("parado", "grande", "plano", "elegido"):
    for _f in ("grenze", "pirata"):
        toma_pp(f"em-{_m}-{_f}", "6", _em(_m, _f, True))
        toma_pp(f"em6-{_m}-{_f}", "6", _em(_m, _f, False))

# no option list (or `all`) renders the picks, never utileria's older options (the glovebox cut among them)
FINALES = ["pp1-b", "pp2-b", "pp4-b", "pp6-b", "pp-barra", "pp-emblema", "pp-fresa"]
if _g["SOLO"] is None:
    _g["SOLO"] = FINALES

# ---------------------------------------------------------------- utileria.py's render loop over the options above
exec(compile(MARCA + _cola, U, "exec"), _g)  # _cola: utileria.py's tail, as caja3.py split it
