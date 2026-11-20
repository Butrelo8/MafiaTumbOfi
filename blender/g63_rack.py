"""Roof rack for the new G63, the load and the tie-down, on blender/g63_nuevo.py's output (g63-listo.blend).

Reference (docs/design/references.md): the owner's refs 8.png / 9.png / 10.png, the "G-Wagen Basic Carrier Bars, Three Crossbars" for the
W463A (g-wagenaccessories.com): three silver aluminium aero bars across the roof, black plastic feet (a rounded block, a lock cylinder
on the outer face, a clamp plate on the gutter rail), spaced front / middle / back. Matched: the bar profile, the foot shape, the
silver-and-black, three bars. Changed on purpose: no Mercedes star on the feet (owner), the bars are a little thicker so they
read from the Caja camera 7 m away, and the load is the band's: instrument cases, the donut, the alien, tied with a net.

  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b <g63-listo.blend> --python-exit-code 1 --python blender/g63_rack.py \
    -- <out .blend (Windows)> <props glb (Windows): the live escena.glb that holds the k3_* props> [variante: red|correas|cable|todas]
"""
import bpy, bmesh, math, os, sys, json
from mathutils import Matrix, Vector

SAL = sys.argv[sys.argv.index("--") + 1]
PROPS = sys.argv[sys.argv.index("--") + 2]
VARIANTE = sys.argv[sys.argv.index("--") + 3] if len(sys.argv) > sys.argv.index("--") + 3 else "red"
O = bpy.data.objects
sc = bpy.context.scene

BARRA_ANCHO, BARRA_ALTO = 0.058, 0.034   # aero profile, along the car x across the roof
PIE = (0.150, 0.100, 0.085)              # foot block: along the bar, along the car, height


def mat(nombre, col, met, rug, emi=None, est=0.0):
    m = bpy.data.materials.get(nombre)
    if m:
        return m
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Metallic"].default_value = met
    p.inputs["Roughness"].default_value = rug
    return m


M_ALU = mat("web_barra_aluminio", (0.62, 0.62, 0.64), 1.0, 0.28)
M_PIE = mat("web_pie_plastico", (0.012, 0.012, 0.013), 0.0, 0.6)
M_CIL = mat("web_pie_cilindro", (0.7, 0.7, 0.72), 1.0, 0.2)
M_RED = mat("web_red_cuerda", (0.05, 0.05, 0.05), 0.0, 0.8)   # black nylon, lifted so the net still reads on the dark paint at night
M_CORREA = mat("web_correa", (0.55, 0.12, 0.02), 0.0, 0.7)


def objeto(nombre, bm, m, padre=None):
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(m)
    o = bpy.data.objects.new(nombre, me)
    sc.collection.objects.link(o)
    if padre:
        o.parent = padre
    return o


def caja_vert(o):
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    return Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))), Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))


# ---------------------------------------------------------------- the roof, measured
def techo():
    """Roof height map by rays straight down over the body: returns z (flat top), x half-width of the flat, y range of the flat."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    cam = O["camion"]
    cx = 1.72

    def h(x, y):
        ok, loc, n, i, o, M = sc.ray_cast(dg, Vector((x, y, 3.2)), Vector((0, 0, -1)))
        return loc.z if ok and (o.parent == cam) else None
    zs = [h(cx, y / 100) for y in range(-100, 100, 5)]
    zmax = max(z for z in zs if z)
    # flat top: where the height is within 4 cm of the max, scanning y at the centre line and x at mid roof
    ys = [y / 100 for y in range(-250, 250, 2) if (h(cx, y / 100) or 0) > zmax - 0.04]
    y0, y1 = min(ys), max(ys)
    ym = (y0 + y1) / 2
    xs = [cx + d / 100 for d in range(-110, 111, 1) if (h(cx + d / 100, ym) or 0) > zmax - 0.05]
    return {"z": zmax, "x0": min(xs), "x1": max(xs), "y0": y0, "y1": y1, "ym": ym, "perfil": [round(h(cx + d / 100, ym) or 0, 3) for d in range(-110, 111, 10)]}


# ---------------------------------------------------------------- bars and feet
def barra(nombre, y, z, x0, x1):
    """Aero bar: a flattened oval (16 sides) extruded from x0 to x1, closed ends."""
    bm = bmesh.new()
    n = 16
    anillos = []
    for x in (x0, x1):
        anillos.append([bm.verts.new((x, y + math.cos(2 * math.pi * k / n) * BARRA_ANCHO / 2, z + math.sin(2 * math.pi * k / n) * BARRA_ALTO / 2)) for k in range(n)])
    for k in range(n):
        bm.faces.new((anillos[0][k], anillos[0][(k + 1) % n], anillos[1][(k + 1) % n], anillos[1][k]))
    bm.faces.new(anillos[0][::-1])
    bm.faces.new(anillos[1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return objeto(nombre, bm, M_ALU)


def pie(nombre, lado, y, z_roof, x_borde, z_barra):
    """Foot at the roof edge: black rounded block holding the bar's end, a lock cylinder on the outer face, a clamp plate down the
    gutter rail. lado = -1 (low x) or +1. x_borde: outer edge of the flat roof; the block sits just inside it."""
    sx, sy, sz = PIE
    cx = x_borde - lado * sx / 2 + lado * 0.012
    cz = z_barra - 0.012
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= sx; v.co.y *= sy; v.co.z *= sz
        # taper: the outer side of the block is lower and the top rounds off toward the car's front/back
        if v.co.z > 0:
            v.co.y *= 0.84
        if v.co.x * lado > 0:
            v.co.z *= 0.86
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.014, segments=2, affect="EDGES")
    for v in bm.verts:
        v.co += Vector((cx, y, cz))
    # clamp plate: thin plate on the outside of the block reaching down over the gutter rail
    pl = bmesh.ops.create_cube(bm, size=1.0)["verts"]
    for v in pl:
        v.co.x = cx + lado * (sx / 2 + 0.006) + v.co.x * 0.012
        v.co.y = y + v.co.y * (sy * 0.78)
        v.co.z = cz - sz / 2 - 0.02 + v.co.z * 0.075
    o = objeto(nombre, bm, M_PIE)
    # lock cylinder
    bm2 = bmesh.new()
    bmesh.ops.create_cone(bm2, cap_ends=True, segments=12, radius1=0.012, radius2=0.012, depth=0.014)
    for v in bm2.verts:  # cone axis is z: lay it along x
        v.co = Vector((v.co.z, v.co.y, v.co.x))
        v.co += Vector((cx + lado * (sx / 2 + 0.002), y - 0.01, cz + 0.01))
    cil = objeto(nombre + "_cil", bm2, M_CIL)
    return o, cil


def rack(T):
    cam = O["camion"]
    z_barra = T["z"] + 0.075
    # bars span the flat roof plus 3 cm each side; feet at its edge
    x0, x1 = T["x0"] - 0.0, T["x1"] + 0.0
    largo = T["y1"] - T["y0"]
    ys = [T["y0"] + largo * f for f in (0.16, 0.50, 0.84)]
    piezas = []
    for k, y in enumerate(ys):
        piezas.append(barra(f"rack_barra{k}", y, z_barra, x0 - 0.05, x1 + 0.05))
        for lado, xb in ((-1, x0), (1, x1)):
            p, c = pie(f"rack_pie{k}{'i' if lado < 0 else 'd'}", lado, y, T["z"], xb, z_barra)
            piezas += [p, c]
    for p in piezas:
        p.parent = cam
    return ys, z_barra, piezas


# ---------------------------------------------------------------- the load: the live scene's own props
def traer_props(glb):
    antes = set(O)
    bpy.ops.import_scene.gltf(filepath=glb)
    nuevos = [o for o in O if o not in antes]
    quiero = {}
    for o in nuevos:
        base = o.name.split(".")[0]
        if o.type == "MESH" and base in ("k3_bajo", "k3_docerola", "k3_requinto", "k3_tarola", "k3_teclado", "k3_alien", "k3_dona"):
            quiero.setdefault(base, o)
    for o in quiero.values():  # keep the mesh in world coordinates of the old truck, then re-origin at its box centre
        mw = o.matrix_world.copy()
        o.parent = None
        o.data.transform(mw)
        o.matrix_world = Matrix.Identity(4)
    for o in nuevos:
        if o not in quiero.values():
            O.remove(o, do_unlink=True)
    for o in quiero.values():
        a, b = caja_vert(o)
        c = (a + b) / 2
        o.data.transform(Matrix.Translation(-c))
        o.location = (0, 0, 0)
        o.rotation_mode = "XYZ"  # the glTF importer leaves quaternions: rotation_euler would be ignored
    return quiero


def colocar_carga(T, ys, z_barra, props):
    """Best-guess load plan on the rack: the three cases lie lengthwise side by side on the middle and rear bars, the keyboard case flat
    across the stack, the snare behind, the donut laid on the front bar and the alien lying face up along the stack, head forward.
    Returns the load's boxes (world AABBs) for the tie-down."""
    cam = O["camion"]
    cx = 1.72
    zb = z_barra + BARRA_ALTO / 2           # top of the bars
    y_c = (ys[1] + ys[2]) / 2                # the cases rest on the middle and rear bars
    cajas = {}

    def poner(nombre, loc, rot=(0, 0, 0)):
        o = props[nombre]
        o.location = loc
        o.rotation_euler = rot
        o.parent = cam
        o.matrix_parent_inverse = Matrix.Identity(4)
        bpy.context.view_layer.update()
        cajas[nombre] = caja_vert(o)
        return o
    dim = {k: (lambda a, b: b - a)(*caja_vert(o)) for k, o in props.items()}
    print("G63 RACK dimensiones", {k: [round(v, 3) for v in d] for k, d in dim.items()}, flush=True)
    dz = lambda k: dim[k].z / 2
    # cases: bajo sexto left, docerola middle, requinto right (the owner's order in the old bed is not recorded: guess)
    poner("k3_bajo", (cx - 0.46, y_c, zb + dz("k3_bajo")))
    poner("k3_docerola", (cx + 0.00, y_c, zb + dz("k3_docerola")))
    poner("k3_requinto", (cx + 0.44, y_c, zb + dz("k3_requinto")))
    tope = max(cajas[k][1].z for k in cajas)
    # keyboard case: stood on its side in the model (0.145 x 1.023 x 0.378): lay it flat, across the stack's right half
    poner("k3_teclado", (cx + 0.22, y_c, tope + 0.378 / 2 * 0 + 0.145 / 2 + 0.0), (0, math.pi / 2, 0))
    # donut: flat on the front bar, in front of the cases
    don = dim["k3_dona"]
    poner("k3_dona", (cx, ys[0] + 0.02, zb + dz("k3_dona")))
    # snare behind the cases, on the rear bar
    poner("k3_tarola", (cx - 0.36, ys[2] + 0.10, zb + dz("k3_tarola")))
    # alien: lying on its back (z -> y), head forward, on top of the keyboard and the cases
    tope2 = max(cajas[k][1].z for k in ("k3_bajo", "k3_docerola", "k3_requinto", "k3_teclado"))
    poner("k3_alien", (cx - 0.20, y_c + 0.05, tope2 + dim["k3_alien"].y / 2), (-math.pi / 2, 0, 0))
    return cajas


def hexcuerda(bm, pts, r, lados=6):
    """Tube along a polyline (hexagonal section)."""
    anillos = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        n = t.cross(ref).normalized()
        b = t.cross(n).normalized()
        anillos.append([bm.verts.new(p + n * math.cos(2 * math.pi * k / lados) * r + b * math.sin(2 * math.pi * k / lados) * r) for k in range(lados)])
    for i in range(len(anillos) - 1):
        for k in range(lados):
            bm.faces.new((anillos[i][k], anillos[i][(k + 1) % lados], anillos[i + 1][(k + 1) % lados], anillos[i + 1][k]))


def suavizar(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def altura(cajas, x, y, base, margen=0.12):
    """Drape height at (x, y): the highest load box's top, eased down over `margen` outside its footprint."""
    z = base
    for a, b in cajas.values():
        dx = max(a.x - x, 0, x - b.x)
        dy = max(a.y - y, 0, y - b.y)
        d = math.hypot(dx, dy)
        z = max(z, base + (b.z + 0.012 - base) * suavizar(1 - d / margen))
    return z


def red(cajas, T, ys, z_barra, variante):
    """Tie-down over the load. red: a square cargo net (rope 7 mm, 0.22 m cells); cable: a diagonal wire lattice (5 mm, 0.34 m);
    correas: four ratchet straps across and one along (flat ribbon 4 cm)."""
    cam = O["camion"]
    base = z_barra + BARRA_ALTO / 2 + 0.008
    x0, x1 = T["x0"] - 0.02, T["x1"] + 0.02
    y0, y1 = ys[0] - 0.02, ys[2] + 0.02
    bm = bmesh.new()
    if variante in ("red", "cable"):
        paso = 0.22 if variante == "red" else 0.34
        r = 0.007 if variante == "red" else 0.005
        n = max(2, round((x1 - x0) / paso)); m = max(2, round((y1 - y0) / paso))
        paso_x, paso_y = (x1 - x0) / n, (y1 - y0) / m
        dirs = []
        if variante == "red":
            dirs = [("x", x0 + paso_x * i) for i in range(n + 1)] + [("y", y0 + paso_y * j) for j in range(m + 1)]
        for kind, v in dirs:
            L = int((y1 - y0 if kind == "x" else x1 - x0) / 0.06)
            pts = [Vector((v, y0 + (y1 - y0) * k / L, 0)) if kind == "x" else Vector((x0 + (x1 - x0) * k / L, v, 0)) for k in range(L + 1)]
            for p in pts:
                p.z = altura(cajas, p.x, p.y, base)
            hexcuerda(bm, pts, r)
        if variante == "cable":  # diagonal lattice clipped to the rack rectangle
            for sgn in (1, -1):
                for k in range(-4, 9):
                    c0 = Vector((x0, y0 + k * 0.34 if sgn > 0 else y1 - k * 0.34, 0))
                    pts = []
                    for s in range(0, 61):
                        p = c0 + Vector((s * 0.03, sgn * s * 0.03, 0))
                        if x0 - 1e-6 <= p.x <= x1 + 1e-6 and y0 - 1e-6 <= p.y <= y1 + 1e-6:
                            p.z = altura(cajas, p.x, p.y, base)
                            pts.append(p)
                    if len(pts) > 2:
                        hexcuerda(bm, pts, r)
    else:  # correas
        for yy in (ys[0] + 0.10, (ys[0] + ys[1]) / 2 + 0.05, ys[1] + 0.10, ys[2] - 0.05):
            pts = [Vector((x0 + (x1 - x0) * k / 40, yy, 0)) for k in range(41)]
            for p in pts:
                p.z = altura(cajas, p.x, p.y, base) + 0.004
            hexcuerda(bm, pts, 0.016, lados=4)
        pts = [Vector((1.72 + 0.05, y0 + (y1 - y0) * k / 50, 0)) for k in range(51)]
        for p in pts:
            p.z = altura(cajas, p.x, p.y, base) + 0.012
        hexcuerda(bm, pts, 0.016, lados=4)
    o = objeto(f"carga_{variante}", bm, M_CORREA if variante == "correas" else M_RED)
    o.parent = cam
    return o


if __name__ == "__main__":
    T = techo()
    print("G63 TECHO", json.dumps(T), flush=True)
    ys, z_barra, piezas = rack(T)
    print("G63 RACK barras y", [round(y, 3) for y in ys], "z", round(z_barra, 3), "piezas", len(piezas), flush=True)
    props = traer_props(PROPS)
    cajas = colocar_carga(T, ys, z_barra, props)
    for k, (a, b) in cajas.items():
        print("G63 RACK caja", k, [round(v, 3) for v in a], [round(v, 3) for v in b], flush=True)
    for v in (("red", "correas", "cable") if VARIANTE == "todas" else (VARIANTE,)):
        o = red(cajas, T, ys, z_barra, v)
        print("G63 RACK red", v, "tris", sum(len(p.vertices) - 2 for p in o.data.polygons), flush=True)
        if VARIANTE == "todas":
            o.hide_render = o.hide_viewport = (v != "red")  # the variants sheet toggles them
    bpy.ops.wm.save_as_mainfile(filepath=SAL, copy=True)
    print("G63 RACK guardado", SAL, flush=True)
