"""Bed load, real-life pass (caja4): what a touring band carries in the G63 6x6 bed, packed and strapped the way a load is
packed for the road. Instruments travel in hard cases (owner 11-14), the donut stays. Two arrangements: A against the cab,
B laid flat under a net. Sources: docs/design/references.md › Bed load, real-life pass.

Runs caja3.py's props and helpers (which run utileria.py's scene), adds its options, then utileria.py's render loop:

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/caja4.py)" \
    -- <escena.py path (Windows)> <out_dir (Windows)> [samples] <options> [WxH]

Options: caja4-sonda (bed probe, prints CAJA4 lines), caja4-hoja, caja4-{a,b}, caja4-{a,b}-esc2, caja4-{a,b}-esc4,
caja4-{a,b}-esc5, esc3-hombro4, esc4-cabina4, esc4-fin4 (the scene stills with the owner's picks, bed per CAMA4 env, default b).
"""
import bpy, math, os
from mathutils import Vector

C3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caja3.py")
_c3 = open(C3, encoding="utf8").read().split("# ---------------------------------------------------------------- utileria.py's render loop")[0]
exec(compile(_c3, C3, "exec"), globals())


# ---------------------------------------------------------------- probe: the bed's real inside
_ENCAJA = [c for o in bpy.data.objects if o.name.split(".")[0].startswith(("estuche_", "guitarra_"))
           or o.name.split("_")[0].split(".")[0] in ("alejandro", "diego") for c in [o] + list(o.children_recursive)]
for o in _ENCAJA:  # the rays must hit the bed, not v3's seat cases and riders
    o.hide_viewport = True
dg = bpy.context.evaluated_depsgraph_get()


def _r(o, d):
    hit, loc, *_ = sc.ray_cast(dg, Vector(o), Vector(d))
    return loc if hit else None


PISO = _r((CX, -2.0, 2.6), (0, 0, -1))
print("CAJA4 piso", PISO, "Z0", Z0)
zf = PISO.z if PISO else Z0
for z in (zf + 0.05, zf + 0.25):
    print("CAJA4 frente", round(z, 3), _r((CX, -2.0, z), (0, 1, 0)), "porton", _r((CX, -2.0, z), (0, -1, 0)))
for y in [round(-1.2 - 0.1 * i, 2) for i in range(17)]:
    izq, der = _r((CX, y, zf + 0.08), (-1, 0, 0)), _r((CX, y, zf + 0.08), (1, 0, 0))
    izq2, der2 = _r((CX, y, zf + 0.30), (-1, 0, 0)), _r((CX, y, zf + 0.30), (1, 0, 0))
    print("CAJA4 pared y", y, [round(p.x - CX, 3) if p else None for p in (izq, der, izq2, der2)])
for x in (-0.62, -0.6, -0.58, 0.58, 0.6, 0.62):
    h = _r((CX + x, -2.0, 2.6), (0, 0, -1))
    print("CAJA4 riel x", x, h)
for y in (-2.6, -2.7, -2.75, -2.8):
    print("CAJA4 porton z y", y, _r((CX, y, 2.6), (0, 0, -1)))
print("CAJA4 arco", ARCO_Z, "YC", YC, "COLA", COLA)

for o in _ENCAJA:
    o.hide_viewport = False
dg = bpy.context.evaluated_depsgraph_get()

# ---------------------------------------------------------------- the bed, measured (CAJA4 lines above, 2026-11-14)
PZ = PISO.z if PISO else 0.933           # bed floor
XL, XR = CX - 0.515, CX + 0.525         # inner walls up to PZ + 0.20 (-0.52 / +0.531), 5 mm clear
YF, YT = -1.105, -2.86                  # cab wall (-1.094/-1.101) and tailgate inner face (-2.866/-2.873), 5 mm clear
RIEL = PZ + 0.28                         # rail top: 1.18-1.235 (0.25-0.30 m above the floor)
ANCLA_Z = PZ + 0.06                      # tie-down rings on the walls, 6 cm up
CARGA = []                              # (object, name, kg) of the arrangement being built
CINTAS = []                             # (y, [x range covered], top) of each strap
RED = []                                # the net, if any
# The bed's tie-downs: the model has none, so both arrangements get the same set, assumed: a ring at each corner (as pickup
# beds have) and one mid pair, all on the walls 6 cm up. Straps and the net hook only to these.
ANCLAS_Y = (YF - 0.06, -1.98, YT + 0.06)
# The rear axles (the 6x6 has two): wheels are the truck's meshes about 1 m tall that touch the road; printed as CAJA4 eje.
_ruedas = []
for o in CAM.children_recursive:
    if o.type == "MESH":
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        zs, ys = [p.z for p in pts], [p.y for p in pts]
        if min(zs) < 0.15 and 0.8 < max(zs) - min(zs) < 1.5 and max(ys) - min(ys) < 1.5:
            _ruedas.append(round((min(ys) + max(ys)) / 2, 2))
EJES = sorted({y for y in _ruedas})
print("CAJA4 eje", EJES)
_traseros = [y for y in EJES if y < -0.5]
BOGIE = sum(_traseros) / len(_traseros) if _traseros else None

DOMO_FUNDA = gastado3("k4_cobija", (0.02, 0.05, 0.16), 0.9, (0.06, 0.1, 0.25), 0.9, bump=0.3, tela=2.2)  # moving blanket, navy
POLI = gastado3("k4_poli", (0.02, 0.02, 0.022), 0.6, (0.14, 0.14, 0.15), 0.5, bump=0.1, escala=500)  # drum case polyethylene
REJA_N = gastado3("k4_reja", (0.025, 0.025, 0.027), 0.55, (0.15, 0.15, 0.16), 0.5)  # black milk crate
CUERDA = mat("k4_cuerda", (0.015, 0.015, 0.015), 0.6)


def poner(o, x0=None, x1=None, y0=None, y1=None, z0=None):
    """Snap a placed prop by its world box: x0/x1 = left/right face, y1 = front face (toward the cab), y0 = back face, z0 = foot."""
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    d = Vector((0, 0, 0))
    if x0 is not None: d.x = x0 - lo.x
    if x1 is not None: d.x = x1 - hi.x
    if y1 is not None: d.y = y1 - hi.y
    if y0 is not None: d.y = y0 - lo.y
    if z0 is not None: d.z = z0 - lo.z
    o.location = o.location + d
    bpy.context.view_layer.update()
    return o


def carga(nombre, f, kg, rot=(0, 0, 0), **donde):
    o = unir(nombre, f, (CX, -2.0, PZ), rot)
    poner(o, **donde)
    CARGA.append((o, nombre, kg))
    return o


def caja_de(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


# ---------------------------------------------------------------- props (real sizes; references.md › Bed load)
def estuche(L, W, H, calcas=(), m=None):
    """Rectangular hard case (guitar, bass, keyboard): tolex over ply, aluminium valance at the lid seam, two latches and a
    handle on the front long side (-y), rubber feet; built lying flat, L along x."""
    m = m or TOLEX
    caja((L, W, H), (0, 0, H / 2), m, bevel=min(0.025, H * 0.2), parent=F)
    caja((L + 0.005, W + 0.005, 0.012), (0, 0, H * 0.62), ALU, bevel=0.003, parent=F)
    for x in (-L * 0.26, L * 0.26):
        caja((0.04, 0.012, 0.03), (x, -W / 2 - 0.004, H * 0.62), ALU, bevel=0.003, parent=F)
    caja((0.13, 0.022, 0.026), (0, -W / 2 - 0.008, H * 0.5), GOMA, bevel=0.008, parent=F)
    for i, id in enumerate(calcas):
        calca_en(id, (-L * 0.2 + i * L * 0.36, 0.0, H + 0.0006), (0, 0, 0.12 - 0.3 * i), 0.8)


def amp_case(W=0.62, D=0.42, H=0.56, calcas=("a-mafia", "b-ver")):
    """Combo amp in an ATA road case: laminate on ply, aluminium extrusions on all 12 edges, ball corners, two butterfly latches,
    side handles, the band stencil; W along x, D along y, the lid seam at 72 %."""
    caja((W, D, H), (0, 0, H / 2), LAMINADO, bevel=0.004, parent=F)
    e = 0.02
    for sx in (-1, 1):
        for sy in (-1, 1):
            caja((e, e, H), (sx * W / 2, sy * D / 2, H / 2), ALU, parent=F)
        for sz in (0, 1):
            caja((e, D, e), (sx * W / 2, 0, sz * H), ALU, parent=F)
    for sy in (-1, 1):
        for sz in (0, 1):
            caja((W, e, e), (0, sy * D / 2, sz * H), ALU, parent=F)
    caja((W + 0.008, D + 0.008, 0.016), (0, 0, H * 0.72), ALU, parent=F)
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (0, 1):
                esfera(0.022, (sx * W / 2, sy * D / 2, sz * H), ALU, parent=F)
    for x in (-W * 0.3, W * 0.3):
        for sy in (-1, 1):
            caja((0.055, 0.01, 0.055), (x, sy * (D / 2 + 0.004), H * 0.72), ALU, bevel=0.004, parent=F)
    for sx in (-1, 1):
        caja((0.012, 0.12, 0.05), (sx * (W / 2 + 0.004), 0, H * 0.45), GOMA, bevel=0.004, parent=F)
    for sy in (-1, 1):  # the stencil on both long faces: the back one faces the tailgate camera
        r = (math.pi / 2, 0, 0 if sy < 0 else math.pi)
        texto("MAFIA TUMBADA", 0.06, (0, sy * (D / 2 + 0.0008), H * 0.42), STENCIL, font="impact.ttf", rot=r, parent=F)
        texto("BACKLINE 01  ·  AMP", 0.024, (0, sy * (D / 2 + 0.0008), H * 0.30), STENCIL, font="consola.ttf", rot=r, parent=F)
    for i, id in enumerate(calcas):
        calca_en(id, (-W * 0.2 + i * W * 0.4, 0.02, H + 0.0006), (0, 0, -0.08 + 0.2 * i), 0.7)


def caso_tambor(D, H, nombre):
    """Round drum case (rotomoulded polyethylene): a drum-sized can and its lid band, a strap with a buckle across the lid."""
    cil(D / 2, H * 0.82, (0, 0, H * 0.41), POLI, verts=48, parent=F)
    cil(D / 2 + 0.008, H * 0.22, (0, 0, H * 0.89), POLI, verts=48, parent=F)
    caja((D + 0.02, 0.035, 0.004), (0, 0, H + 0.002), CINTA_N, parent=F)
    for s in (-1, 1):
        caja((0.004, 0.035, H * 0.5), (s * (D / 2 + 0.012), 0, H * 0.75), CINTA_N, parent=F)
    caja((0.06, 0.045, 0.015), (D * 0.22, 0, H + 0.008), ALU, bevel=0.003, parent=F)
    texto(nombre, 0.035, (0, -D * 0.25, H + 0.001), STENCIL, font="impact.ttf", rot=(0, 0, 0), parent=F)


def caja_cables():
    """Black milk crate, 0.33 x 0.33 x 0.28 m, slotted walls, three coiled XLR / power cables inside, a tail over the rim."""
    W, H, t = 0.33, 0.28, 0.012
    caja((W, W, t), (0, 0, t / 2), REJA_N, parent=F)
    h = (W - t) / 2
    for z in (0.02, 0.10, 0.18, 0.265):  # four rails a side, the slots between them
        for sg in (-1, 1):
            caja((W, t, 0.03), (0, sg * h, z), REJA_N, parent=F)
            caja((t, W, 0.03), (sg * h, 0, z), REJA_N, parent=F)
    for u in (-h, -0.06, 0.06, h):  # posts
        for sg in (-1, 1):
            caja((0.02, t, H), (u, sg * h, H / 2), REJA_N, parent=F)
            caja((t, 0.02, H), (sg * h, u, H / 2), REJA_N, parent=F)
    for i in range(3):
        for j in range(5):
            toro(0.115 - 0.01 * i, 0.006, (0.004 * j, 0.003 * j, 0.03 + 0.07 * i + 0.011 * j), GOMA, rot=(0.06 * (j % 2), 0.05, 0), parent=F)
    cil(0.006, 0.2, (0.12, -0.15, 0.27), GOMA, rot=(0.9, 0, 0.3), verts=8, parent=F)


def cobija_rollo(L=1.0, d=0.22):
    """Moving blanket rolled tight, a black tie at each end (void fill between cases)."""
    cil(d / 2, L, (0, 0, d / 2), DOMO_FUNDA, rot=(0, math.pi / 2, 0), verts=32, parent=F)
    for x in (-L * 0.35, L * 0.35):
        toro(d / 2 + 0.004, 0.006, (x, 0, d / 2), CINTA_N, rot=(0, math.pi / 2, 0), parent=F)


def cobijas_dobladas(W=0.55, D=0.36, n=3):
    """A stack of folded moving blankets, each 4-5 cm thick, slightly off-square."""
    for i in range(n):
        caja((W - 0.02 * (i % 2), D - 0.015 * i, 0.045), (0.01 * (i % 2), 0.005 * i, 0.0225 + 0.046 * i), DOMO_FUNDA, bevel=0.02,
             rot=(0, 0, 0.03 * (i - 1)), parent=F)


def dona4():
    """The donut (kept, owner 11-14): the inflatable ring from bed B, R 0.30 m, tube 0.12 m."""
    toro(0.30, 0.12, (0, 0, 0.12), mat("u_dona", (0.95, 0.45, 0.6), 0.15), parent=F)


def argolla(x, y, lado):
    """Bed tie-down: a bolt-on cleat plate on the wall with a folding D-ring, 6 cm up."""
    xw = XL if lado < 0 else XR
    caja((0.008, 0.07, 0.05), (xw, y, ANCLA_Z), ACERO, bevel=0.002, parent=False)
    toro(0.022, 0.0045, (xw - lado * 0.016, y, ANCLA_Z - 0.008), ACERO, rot=(0, math.radians(90 - lado * 35), 0), parent=False)


# ---------------------------------------------------------------- straps and net, laid over the load by ray casts
def alto_en(x, y):
    """Top of the load at (x, y): the highest hit of a downward ray over the props of this arrangement, else the floor."""
    z = PZ
    for o, *_ in CARGA:
        mi = o.matrix_world.inverted()
        a = mi @ Vector((x, y, PZ + 1.5))
        b = mi @ Vector((x, y, PZ - 0.1))
        ok, loc, *_ = o.ray_cast(a, (b - a).normalized(), distance=(b - a).length)
        if ok:
            z = max(z, (o.matrix_world @ loc).z)
    return z


def envolvente(pts):
    """Upper convex hull of (x, z) points ordered by x: the line a tensioned strap takes over the load."""
    h = []
    for p in pts:
        while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) >= 0:
            h.pop()
        h.append(p)
    return h


def cinta(y, ya, m=CINTA, ancho=0.05):
    """A 2-inch ratchet strap across the bed at y: from the left wall's tie-down, taut over the load, to the right one. The
    ratchet sits on the right shoulder of the load."""
    assert ya in ANCLAS_Y, ya
    bpy.context.view_layer.update()
    xs = [XL + 0.03 + i * 0.02 for i in range(int((XR - XL - 0.06) / 0.02) + 1)]
    perfil = [(x, alto_en(x, y) + 0.004) for x in xs]
    pts = envolvente([(XL - 0.016, ANCLA_Z)] + [p for p in perfil if p[1] > PZ + 0.01] + [(XR + 0.016, ANCLA_Z)])
    bm_v, bm_f = [], []
    n = len(pts)
    for i, (x, z) in enumerate(pts):
        yy = ya if i in (0, n - 1) else y
        bm_v += [(x, yy - ancho / 2, z), (x, yy + ancho / 2, z)]
        if i:
            k = 2 * i
            bm_f.append((k - 2, k - 1, k + 1, k))
    me = bpy.data.meshes.new("k4_cinta")
    me.from_pydata(bm_v, [], bm_f)
    o = bpy.data.objects.new("k4_cinta", me)
    bpy.context.collection.objects.link(o)
    sol = o.modifiers.new("grosor", "SOLIDIFY"); sol.thickness = 0.003
    _fin(o, m, False)
    cima = [p for p in pts[1:-1]]
    if cima:
        x, z = cima[-1]
        caja((0.11, ancho + 0.012, 0.03), (x - 0.06, y, z + 0.012), ALU, bevel=0.004, parent=False)  # the ratchet
    CINTAS.append((y, (cima[0][0], cima[-1][0]) if cima else None, max(p[1] for p in pts)))
    return o


def red(paso=0.11):
    """Cargo net over the whole load: a 11 cm mesh of 6 mm elastic cord, laid taut over the top (a max filter and a blur of
    the height field) and pulled down to the rails at the edge, hooked to the four corner tie-downs."""
    import numpy as np
    bpy.context.view_layer.update()
    nx, ny = int((XR - XL) / 0.025) + 1, int((YF - YT) / 0.025) + 1
    xs, ys = np.linspace(XL + 0.01, XR - 0.01, nx), np.linspace(YT + 0.01, YF - 0.01, ny)
    H = np.array([[alto_en(x, y) for x in xs] for y in ys])
    M = H.copy()
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            M = np.maximum(M, np.roll(np.roll(H, dy, 0), dx, 1))
    k = np.exp(-np.arange(-4, 5) ** 2 / 8.0); k /= k.sum()
    B = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 1, np.pad(M, 4, mode="edge"))
    B = np.apply_along_axis(lambda c: np.convolve(c, k, "same"), 0, B)[4:-4, 4:-4]
    S = np.maximum(B, H) + 0.012
    gx, gy = int((XR - XL) / paso) + 1, int((YF - YT) / paso) + 1
    hz = lambda x, y: H[min(ny - 1, max(0, int(round((y - ys[0]) / (ys[1] - ys[0]))))), min(nx - 1, max(0, int(round((x - xs[0]) / (xs[1] - xs[0])))))]
    vs, fs = [], []
    for j in range(gy):
        for i in range(gx):
            x = XL + 0.01 + i * (XR - XL - 0.02) / (gx - 1)
            y = YT + 0.01 + j * (YF - YT - 0.02) / (gy - 1)
            z = S[min(ny - 1, int(round((y - ys[0]) / (ys[1] - ys[0])))), min(nx - 1, int(round((x - xs[0]) / (xs[1] - xs[0]))))]
            if i in (0, gx - 1) or j in (0, gy - 1):
                z = max(min(z, RIEL), hz(x, y) + 0.012)  # down to the rail, unless the load at the edge is higher: then on the load
            vs.append([x, y, max(z, PZ + 0.03)])
            if i and j:
                a = j * gx + i
                fs.append((a - gx - 1, a - gx, a, a - 1))
    # the cords are the quads' edges, 11 cm long: where the load's top rises between two knots, lift both knots until the cord
    # clears it by 9 mm (the cord's 3 mm radius + 6 mm); it crossed the amp 80 mm, the speaker 29 mm, the ring 33 mm (defect 12)
    aristas = [(a, a + 1) for a in range(gx * gy) if (a + 1) % gx] + [(a, a + gx) for a in range(gx * (gy - 1))]
    for _ in range(6):
        subio = False
        for a, b in aristas:
            (xa, ya, za), (xb, yb, zb) = vs[a], vs[b]
            falta = max(hz(xa + (xb - xa) * t, ya + (yb - ya) * t) + 0.009 - (za + (zb - za) * t) for t in np.linspace(0, 1, 12))
            if falta > 0.0005:
                vs[a][2] += falta; vs[b][2] += falta; subio = True
        if not subio:
            break
    me = bpy.data.meshes.new("k4_red")
    me.from_pydata(vs, [], fs)
    o = bpy.data.objects.new("k4_red", me)
    bpy.context.collection.objects.link(o)
    w = o.modifiers.new("cuerda", "WIREFRAME"); w.thickness = 0.006; w.use_replace = True
    _fin(o, CUERDA, False)
    for x, lado in ((XL, -1), (XR, 1)):
        for y in ANCLAS_Y:
            arriba = max(RIEL, min(vs, key=lambda v: (v[0] - x) ** 2 + (v[1] - y) ** 2)[2])  # up to the net's edge knot
            cil(0.004, arriba - ANCLA_Z, (x - lado * 0.02, y, (arriba + ANCLA_Z) / 2), ACERO, verts=6, parent=False)  # the hook cord
    RED.append(o)
    return o


# ---------------------------------------------------------------- checks: the real-life rules, measured on the boxes
def revisar_carga(nombre):
    """Prints one CAJA4 CHECK line per rule. dentro: every prop inside the walls and ahead of the tailgate (it closes).
    choque: no two props interpenetrate (> 1 cm on every axis). alto: a prop over the rails is under a strap or the net.
    frenado: nothing can slide forward: the gap ahead of each prop's front face, to the cab wall or the next prop, is <= 3 cm,
    or the prop rides on top and is strapped/netted. pesado: props of 15 kg or more touch the cab wall or a heavy prop does."""
    bpy.context.view_layer.update()
    cajas = [(n, kg) + caja_de(o) for o, n, kg in CARGA]
    malos = []
    for n, kg, lo, hi in cajas:
        if lo.x < XL - 0.003 or hi.x > XR + 0.003 or hi.y > YF + 0.003 or lo.y < YT - 0.003:
            if not (lo.z > RIEL - 0.02 and lo.x > CX - 0.61 and hi.x < CX + 0.62 and lo.y > YT - 0.003):  # above the rail lip
                malos.append(f"dentro:{n}")
    for i in range(len(cajas)):
        for j in range(i + 1, len(cajas)):
            a, b = cajas[i], cajas[j]
            solape = [min(a[3][k], b[3][k]) - max(a[2][k], b[2][k]) for k in range(3)]
            if min(solape) > 0.01 and "dona" not in (a[0], b[0]):
                malos.append(f"choque:{a[0]}/{b[0]}:{min(solape):.3f}")
    sujeto = {}
    for n, kg, lo, hi in cajas:
        por_cinta = any(lo.y - 0.03 <= y <= hi.y + 0.03 and r and r[0] <= hi.x and r[1] >= lo.x for y, r, _ in CINTAS)
        sujeto[n] = por_cinta or bool(RED)
        if hi.z > RIEL + 0.005 and not sujeto[n]:
            malos.append(f"alto:{n}:{hi.z - RIEL:.2f}")
    for n, kg, lo, hi in cajas:
        frente = YF
        for m, _, lo2, hi2 in cajas:
            if m != n and lo2.y > hi.y - 0.01 and min(hi.x, hi2.x) - max(lo.x, lo2.x) > 0.02 and min(hi.z, hi2.z) - max(lo.z, lo2.z) > 0.02:
                frente = min(frente, lo2.y)
        hueco = frente - hi.y
        arriba = lo.z > PZ + 0.02
        print(f"CAJA4 FRENADO {nombre} {n} hueco {hueco:.3f} {'arriba' if arriba else 'piso'} {'sujeto' if sujeto[n] else 'suelto'}")
        if hueco > 0.03 and not (arriba and sujeto[n]):
            malos.append(f"frenado:{n}:{hueco:.2f}")
    pesados = [(n, lo, hi) for n, kg, lo, hi in cajas if kg >= 15]
    for n, lo, hi in pesados:
        toca = hi.y >= YF - 0.01 or any(m != n and abs(lo2.y - hi.y) < 0.02 and hi2.y >= YF - 0.01
                                        for m, lo2, hi2 in pesados)
        if not toca:
            malos.append(f"pesado:{n}")
    kg_tot = sum(kg for _, kg, *_ in cajas)
    cg = sum(kg * (lo.y + hi.y) / 2 for _, kg, lo, hi in cajas) / kg_tot
    sobre = [n for n, kg, lo, hi in cajas if hi.z > RIEL + 0.005]
    print(f"CAJA4 CHECK {nombre} props {len(cajas)} kg {kg_tot} cg_y {cg:.2f} (rear bogie {BOGIE:.2f}, bed mid {(YF + YT) / 2:.2f}) "
          f"over the rails {len(sobre)} ({','.join(sobre)}) "
          f"tope {max(hi.z for *_, hi in cajas) - PZ:.2f} m -> {'PASS' if not malos else 'FAIL ' + ' '.join(malos)}")
    for n, kg, lo, hi in cajas:
        print(f"CAJA4 PROP {nombre} {n} kg {kg} x {lo.x - CX:+.3f}..{hi.x - CX:+.3f} y {lo.y:.3f}..{hi.y:.3f} z {lo.z - PZ:.3f}..{hi.z - PZ:.3f}")


# ---------------------------------------------------------------- the two arrangements
DE_CANTO = (-math.pi / 2, 0, math.pi / 2)  # a case on its long edge, lengthwise, handle up, end toward the tailgate
A_LO_LARGO = (0, 0, math.pi / 2)          # a case flat, lengthwise


def vaciar4():
    """Empty the bed of v3's seat cases and guitars (the guitars travel in their cases now); the riders sit in the cab."""
    asientos_traseros()
    for o in bpy.data.objects:
        if o.name.split(".")[0].startswith(("estuche_", "guitarra_")):
            for c in [o] + list(o.children_recursive):
                c.hide_render = True
    CARGA.clear(); CINTAS.clear(); RED.clear()
    for y in ANCLAS_Y:
        for lado in (-1, 1):
            argolla(XL if lado < 0 else XR, y, lado)


def atras(o):
    return caja_de(o)[0].y - 0.002  # the next item's front face, 2 mm behind this one


def der(o):
    return caja_de(o)[1].x + 0.004


def tope(o):
    return caja_de(o)[1].z


def dona_encima(cx, cy, rot=(0.0, 0.0, 0.0)):
    """The donut laid on the load: its tube rests on the highest point under its ring (sampled on the ring's centre line)."""
    z = max(alto_en(cx + 0.30 * math.cos(t * math.pi / 8), cy + 0.30 * math.sin(t * math.pi / 8)) for t in range(16))
    o = carga("dona", dona4, 1, rot, z0=z + 0.002)
    lo, hi = caja_de(o)
    o.location += Vector((cx - (lo.x + hi.x) / 2, cy - (lo.y + hi.y) / 2, 0))
    bpy.context.view_layer.update()
    return o


def cama_a():
    """A, against the cab, strapped: the four instrument cases on their edge in a file along the left wall, from the cab wall
    back (as guitar cases go in a van); the amp case (the heaviest) in the right front corner against the cab; the full cooler
    behind it; the cable crate and folded blankets behind that; the snare case and a rolled blanket behind the case file; the
    donut on top at the back. Three ratchet straps across, each between a pair of wall tie-downs."""
    vaciar4()
    b = carga("bajo", lambda: estuche(1.22, 0.38, 0.13), 7, DE_CANTO, x0=XL, y1=YF, z0=PZ)
    d = carga("docerola", lambda: estuche(1.08, 0.45, 0.15), 6, DE_CANTO, x0=der(b), y1=YF, z0=PZ)
    r = carga("requinto", lambda: estuche(0.98, 0.36, 0.12), 5, DE_CANTO, x0=der(d), y1=YF, z0=PZ)
    t = carga("teclado", lambda: estuche(1.02, 0.36, 0.15), 12, DE_CANTO, x0=der(r), y1=YF, z0=PZ)
    w = XR - der(t) - 0.045  # the ball corners stand 2.2 cm proud on each side
    a = carga("amp", lambda: amp_case(w, 0.40, 0.56), 30, x1=XR, y1=YF, z0=PZ)
    h = carga("hielera", hielera3, 25, (0, 0, -math.pi / 2), x1=XR - 0.03, y1=atras(a), z0=PZ)
    c = carga("cables", caja_cables, 9, x1=XR - 0.04, y1=atras(h), z0=PZ)
    carga("cobijas", lambda: cobijas_dobladas(0.40, min(0.36, atras(c) - YT - 0.01), 3), 6,
          x1=XR - 0.03, y1=atras(c), z0=PZ)
    ta = carga("tarola", lambda: caso_tambor(0.36, 0.18, "TAROLA"), 6, x0=XL + 0.01, y1=atras(b), z0=PZ)
    carga("cobija", lambda: cobija_rollo(0.70, 0.16), 3, A_LO_LARGO, x0=der(ta), y1=atras(t), z0=PZ)
    dona_encima(CX + 0.14, YT + 0.44)  # clear of the case ends, on the cooler lid and the crate
    for y, ya, m in ((-1.22, ANCLAS_Y[0], CINTA), (-1.45, ANCLAS_Y[1], CINTA), (-2.05, ANCLAS_Y[1], CINTA_N), (-2.45, ANCLAS_Y[2], CINTA_N)):
        cinta(y, ya, m)  # two straps over the amp, each pulled to the nearest ring pair
    revisar_carga("A")


def cama_b(extra=None, nombre="B", dona_xy=None):
    """B, flat stacks under a net: the full cooler and the amp case side by side against the cab; behind the amp the bass,
    12-string and requinto cases lie flat and lengthwise, three high; the keyboard case on its edge beside them; behind the
    cooler the cable crate, the snare case and the folded blankets; the donut on the case deck. One cargo net over everything,
    hooked to the same six rings. extra / dona_xy: caja5.py adds its props on top here, before the
    donut (which it may move) and the net."""
    vaciar4()
    h = carga("hielera", hielera3, 25, (0, 0, -math.pi / 2), x1=XR - 0.005, y1=YF, z0=PZ)
    w = caja_de(h)[0].x - XL - 0.05
    a = carga("amp", lambda: amp_case(w, 0.42, 0.56), 30, x0=XL, y1=YF, z0=PZ)
    b = carga("bajo", lambda: estuche(1.22, 0.38, 0.13), 7, A_LO_LARGO, x0=XL, y1=atras(a), z0=PZ)
    d = carga("docerola", lambda: estuche(1.08, 0.45, 0.15, ("a-putifresa", "b-pura")), 6, A_LO_LARGO, x0=XL, y1=atras(a), z0=tope(b))
    carga("requinto", lambda: estuche(0.98, 0.36, 0.12, ("b-escudo", "a-estrella")), 5, A_LO_LARGO, x0=XL + 0.01, y1=atras(a), z0=tope(d))
    t = carga("teclado", lambda: estuche(1.02, 0.36, 0.15), 12, DE_CANTO, x0=der(d), y1=atras(a), z0=PZ)
    c = carga("cables", caja_cables, 9, x1=XR - 0.02, y1=atras(h), z0=PZ)
    ta = carga("tarola", lambda: caso_tambor(0.36, 0.18, "TAROLA"), 6, x1=XR - 0.01, y1=atras(c), z0=PZ)
    carga("cobijas", lambda: cobijas_dobladas(XR - der(t) - 0.04, min(0.36, atras(ta) - YT - 0.01), 4), 9, x1=XR - 0.01, y1=atras(ta), z0=PZ)
    if extra:
        extra()
    dona_encima(*(dona_xy or (CX, -2.30)))
    red()
    revisar_carga(nombre)


CAMAS = {"a": cama_a, "b": cama_b}
CAMA4 = os.environ.get("CAMA4", "b")  # the recommendation; a Windows Blender needs WSLENV=CAMA4 to see an override


def con_cama(letra, escena):
    def op():
        _g["caja2_b"] = CAMAS[letra]  # base_escena() dresses the bed with this
        return escena()
    return op


for _l in ("a", "b"):
    def _cerca(l=_l):
        CAMAS[l]()
        relleno_caja(VISTA_CAJA3()[0])
        return VISTA_CAJA3()
    opcion(f"caja4-{_l}")(_cerca)
    opcion(f"caja4-{_l}-esc2")(con_cama(_l, esc2_abre))
    opcion(f"caja4-{_l}-esc4")(con_cama(_l, esc4_cabina))
# The scene stills that show the bed, re-dressed with bed CAMA4; 3 and 4 with the owner's picks (11-14: 3B from the rear door,
# 4B the lit cab, ESC4_LUZ in utileria.py)
for _n, _f in (("esc2-abre4", esc2_abre), ("esc2-fin4", esc2_fin), ("esc3-hombro4", esc3_hombro), ("esc3-fin4", esc3_fin),
               ("esc4-cabina4", esc4_cabina), ("esc4-fin4", esc4_fin), ("esc5-fin4", esc5_fin)):
    opcion(_n)(con_cama(CAMA4, _f))

# ---------------------------------------------------------------- utileria.py's render loop, over the options above
exec(compile(MARCA + _cola, U, "exec"), _g)
