"""Roof rack for the new G63, the load and the tie-down, on blender/g63_nuevo.py's output (g63-listo.blend).

Reference (docs/design/references.md): the owner's refs 8.png / 9.png / 10.png, the "G-Wagen Basic Carrier Bars, Three Crossbars" for the
W463A (g-wagenaccessories.com): three silver aluminium aero bars across the roof, black plastic feet (a rounded block, a lock cylinder
on the outer face, a clamp plate on the gutter rail), spaced front / middle / back. Matched: the bar profile, the foot shape, the
silver-and-black, three bars. Changed on purpose: no Mercedes star on the feet (owner), the bars are a little thicker so they
read from the Caja camera 7 m away, and the load is the band's: two flight cases, two guitar cases, a bag, a backpack (blender/g63_carga.py), the
donut and the alien, the load under a net and the alien strapped apart above it.

  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b <g63-listo.blend> --python-exit-code 1 --python blender/g63_rack.py \
    -- <out .blend (Windows)> <props glb (Windows): the live escena.glb that holds the donut and the alien> \
       <volcado .json (Windows): vivo_reparto_volcar.py's dump of the owner's placement file>

The load goes where he left it (`props`: the world matrix of each k3_* object, as moved by his techo_* handles) and the net and the alien's
straps are laid over it (g63_carga.tender). blender/g63_red_ajustar.py does the same on an existing .blend (scratch checks).
"""
import bpy, bmesh, math, os, sys, json
from mathutils import Matrix, Vector

_ARGS = sys.argv[sys.argv.index("--") + 1:]
SAL, PROPS, VOLCADO = _ARGS[0], _ARGS[1], _ARGS[2]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g63_carga as G
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


# ---------------------------------------------------------------- the load
def traer_props(glb):
    """The donut and the alien from the live scene's props glb (the objects the owner's file carries), plus the new roof load from
    blender/g63_carga.py: two flight cases, two guitar cases, a bag and a backpack, each with its stickers. Every object sits at the
    origin, box-centred, so a dump matrix places it as his techo_* handle left it."""
    antes = set(O)
    bpy.ops.import_scene.gltf(filepath=glb)
    nuevos = [o for o in O if o not in antes]
    quiero = {}
    for o in nuevos:
        base = o.name.split(".")[0]
        if o.type == "MESH" and base in ("k3_alien", "k3_dona"):
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
    for nombre, o in G.traer().items():
        G.calcas(o, nombre[3:])
        quiero[nombre] = o
    return quiero


def colocar_volcado(props, js):
    """The load as the owner placed it: each k3_* object takes the world matrix of his dump (the dump's truck mapped onto this one).
    Returns the load's boxes (world AABBs) for the net, like colocar_carga."""
    p = json.load(open(js, encoding="utf8"))
    cam = O["camion"]
    T = cam.matrix_world @ Matrix(p["camion"]).inverted()
    cajas = {}
    for nombre, o in props.items():
        o.matrix_world = T @ Matrix(p["props"][nombre]["mundo"])
        o.parent = cam
        o.matrix_parent_inverse = cam.matrix_world.inverted()
        bpy.context.view_layer.update()
        cajas[nombre] = caja_vert(o)
    return cajas


if __name__ == "__main__":
    T = techo()
    print("G63 TECHO", json.dumps(T), flush=True)
    ys, z_barra, piezas = rack(T)
    print("G63 RACK barras y", [round(y, 3) for y in ys], "z", round(z_barra, 3), "piezas", len(piezas), flush=True)
    props = traer_props(PROPS)
    cajas = colocar_volcado(props, VOLCADO)
    for k, (a, b) in cajas.items():
        print("G63 RACK caja", k, [round(v, 3) for v in a], [round(v, 3) for v in b], flush=True)
    # the net goes over everything but the alien; the alien has its own straps (g63_carga.tender)
    netted = {k: o for k, o in props.items() if k != "k3_alien"}
    red, correas = G.tender({k: cajas[k] for k in netted}, props["k3_alien"], G.geom_rack(), O["camion"])
    print("G63 RACK red tris", sum(len(p.vertices) - 2 for p in red.data.polygons), "correas tris", sum(len(p.vertices) - 2 for p in correas.data.polygons), flush=True)
    G.medir(netted, props["k3_alien"], red, correas, [O[f"rack_barra{k}"] for k in range(3)], "rack")
    bpy.ops.wm.save_as_mainfile(filepath=SAL, copy=True)
    print("G63 RACK guardado", SAL, flush=True)
