"""The roof load of the new G63 (2026-11-20 07:30 brief): two flight cases, two guitar cases, one of each bag, the donut and the alien.
Shared by blender/colocacion_g63_carga.py (the owner's placement file), blender/g63_rack.py (the live scene) and blender/g63_red_ajustar.py.
Needs no arguments: import it from a script that already has the rack bars (`rack_barra0-2`) in the scene.

  traer()            the four prepared pieces (blender/assets/carga-nueva/*.glb, from carga_preparar.py), one `k3_<name>` object each, at the
                     origin, centred on its box, scaled to the size in CARGA, with its decals joined in as a second material
  calcas(o, nombre)  the stickers of blender/props/carga_calcas.json glued on `o` (atlas: carga_atlas.py)
  layout(...)        the plan on the rack: world matrix of each piece
  tender(...)        the net over every piece but the alien (carga_red) and the alien's own straps (carga_red_alien)
  medir(...)         the checks of the brief: rope inside items, alien above the net, straps touching the alien, item/item and item/bar overlaps
"""
import bpy, bmesh, math, json, os
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

AQUI = os.path.dirname(os.path.abspath(__file__))
ACTIVOS = os.path.join(AQUI, "assets", "carga-nueva")
O = bpy.data.objects
sc = bpy.context.scene

# the prepared files (one per piece) and what goes on the roof: (name, piece, scale of the downloaded model)
PIEZAS = {"maleta": "maleta-12k.glb", "guitarra": "guitarra-5k.glb", "bolsa": "bolsa-5k.glb", "mochila": "mochila-9k.glb"}
CARGA = (("maleta_a", "maleta", 0.88), ("maleta_b", "maleta", 0.88), ("guitarra_a", "guitarra", 0.94), ("guitarra_b", "guitarra", 0.94),
         ("bolsa", "bolsa", 1.0), ("mochila", "mochila", 0.70))
CX = 1.72                               # the car's centre line
BARRA_ALTO = 0.034                      # g63_rack.BARRA_ALTO
HILO = 0.007                            # net rope radius
CINTA = (0.040, 0.004)                  # strap: width, thickness


def caja_vert(o):
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    return Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))), Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))


def activar(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o


# ---------------------------------------------------------------- pieces
def traer():
    """-> {"k3_maleta_a": obj, ...}, each at the origin, unrotated, parentless, box-centred."""
    crudos = {}
    for pieza, glb in PIEZAS.items():
        antes = set(O)
        bpy.ops.import_scene.gltf(filepath=os.path.join(ACTIVOS, glb))
        nuevos = [o for o in O if o not in antes]
        malla = next(o for o in nuevos if o.type == "MESH")
        for o in nuevos:
            if o is not malla:
                O.remove(o, do_unlink=True)
        malla.parent = None
        malla.matrix_world = Matrix.Identity(4)
        crudos[pieza] = malla
    salida = {}
    usados = set()
    pendientes = []
    for nombre, pieza, esc in CARGA:       # every copy is taken before any scaling: Mesh.transform on a copy of a scaled mesh scales twice
        if pieza not in usados:
            o = crudos[pieza]
            usados.add(pieza)
        else:
            o = crudos[pieza].copy()
            o.data = crudos[pieza].data.copy()   # single-user: Mesh.transform compounds once per user
            sc.collection.objects.link(o)
        pendientes.append((nombre, o, esc))
    for nombre, o, esc in pendientes:
        o.data.transform(Matrix.Scale(esc, 4))
        o.name = o.data.name = "k3_" + nombre
        if pieza == "guitarra":   # the downloaded gig bag is white: the stickers' white die-cut border would vanish on it, so each one gets a colour
            m = o.data.materials[0].copy()
            m.name = "guitarra_" + nombre[-1]
            m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = {"a": (0.030, 0.030, 0.035, 1), "b": (0.20, 0.025, 0.035, 1)}[nombre[-1]]
            o.data.materials[0] = m
        o.rotation_mode = "XYZ"
        o.location = (0, 0, 0)
        salida[o.name] = o
    return salida


# ---------------------------------------------------------------- stickers
def material_calcas():
    m = bpy.data.materials.get("calcas_atlas")
    if m:
        return m
    m = bpy.data.materials.new("calcas_atlas")
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(os.path.join(ACTIVOS, "tex", "calcas_atlas.png"))
    t.image.alpha_mode = "STRAIGHT"
    nt.links.new(t.outputs["Color"], p.inputs["Base Color"])
    nt.links.new(t.outputs["Alpha"], p.inputs["Alpha"])
    p.inputs["Roughness"].default_value = 0.35
    p.inputs["Specular IOR Level"].default_value = 0.6
    m.surface_render_method = "DITHERED"  # the page cuts it at alpha 0.5 (vivo-optimizar.mjs, MASK by name)
    return m


EJES = {  # face -> (normal, right, up) in the piece's local axes, as seen by someone looking at that face
    "+z": ((0, 0, 1), (1, 0, 0), (0, 1, 0)), "-z": ((0, 0, -1), (1, 0, 0), (0, -1, 0)),
    "-y": ((0, -1, 0), (1, 0, 0), (0, 0, 1)), "+y": ((0, 1, 0), (-1, 0, 0), (0, 0, 1)),
    "+x": ((1, 0, 0), (0, 1, 0), (0, 0, 1)), "-x": ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
}


def calcas(o, nombre, spec=None, atlas=None):
    """Glues each sticker of `nombre` (carga_calcas.json: [{id, cara, u, v, giro, esc}]) onto `o` (at the origin, unrotated): a grid the size of
    the sticker (carga_atlas.json), every vertex projected onto the surface along the face normal and lifted 1.2 mm, UVs on the atlas. The
    quads join `o`'s mesh as a material slot, so the sticker travels with the piece. Returns the number of stickers."""
    spec = spec or json.load(open(os.path.join(AQUI, "props", "carga_calcas.json"), encoding="utf8"))
    atlas = atlas or json.load(open(os.path.join(ACTIVOS, "tex", "calcas_atlas.json"), encoding="utf8"))
    lista = spec.get(nombre, [])
    if not lista:
        return 0
    bpy.context.view_layer.update()
    bvh = BVHTree.FromObject(o, bpy.context.evaluated_depsgraph_get())
    lo, hi = caja_vert(o)
    c = (lo + hi) / 2
    ext = hi - lo
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    for s in lista:
        n, r, u = (Vector(v) for v in EJES[s["cara"]])
        a = atlas[s["id"]]
        w, h = a["w"] * s.get("esc", 1.0), a["h"] * s.get("esc", 1.0)
        g = math.radians(s.get("giro", 0))
        r2, u2 = r * math.cos(g) + u * math.sin(g), u * math.cos(g) - r * math.sin(g)
        # face centre on the bounding box, then slid by (u, v)
        cara = c + Vector(n[i] * ext[i] / 2 for i in range(3))
        centro = cara + r * s.get("u", 0) + u * s.get("v", 0)
        nx, ny = max(2, round(w / 0.035)), max(2, round(h / 0.035))
        verts = []
        for j in range(ny + 1):
            fila = []
            for i in range(nx + 1):
                p = centro + r2 * ((i / nx - 0.5) * w) + u2 * ((j / ny - 0.5) * h)
                hit, nor, _, _ = bvh.ray_cast(p + n * 0.10, -n, 0.30)
                q = (hit + nor * 0.0012) if hit else p
                fila.append(bm.verts.new(q))
            verts.append(fila)
        u0, v0, u1, v1 = a["uv"]
        for j in range(ny):
            for i in range(nx):
                f = bm.faces.new((verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]))
                for l, (ii, jj) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                    l[uv].uv = (u0 + (u1 - u0) * ii / nx, v0 + (v1 - v0) * jj / ny)
                f.material_index = 0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("calcas_tmp")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material_calcas())
    d = bpy.data.objects.new("calcas_tmp", me)
    sc.collection.objects.link(d)
    if not o.data.materials or o.data.materials[-1] != me.materials[0]:
        o.data.materials.append(me.materials[0])
    bpy.ops.object.select_all(action="DESELECT")
    d.select_set(True)
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.join()
    return len(lista)


# ---------------------------------------------------------------- the plan on the rack
def geom_rack():
    """Bars' y, the top of the bars and their x ends, read from rack_barra0-2 (present in the car and in the owner's file)."""
    bpy.context.view_layer.update()
    b = [caja_vert(O[f"rack_barra{k}"]) for k in range(3)]
    return {"ys": [(lo.y + hi.y) / 2 for lo, hi in b], "zb": b[0][1].z, "x0": b[0][0].x, "x1": b[0][1].x, "zt": b[0][1].z - 0.092}


def dim_local(o):
    vs = [v.co for v in o.data.vertices]
    return Vector((max(v.x for v in vs) - min(v.x for v in vs), max(v.y for v in vs) - min(v.y for v in vs), max(v.z for v in vs) - min(v.z for v in vs)))


def caja_en(o, M):
    vs = [M @ v.co for v in o.data.vertices]
    return Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))), Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))


def Mw(loc, rot=(0, 0, 0)):
    from mathutils import Euler
    return Matrix.Translation(Vector(loc)) @ Euler(rot, "XYZ").to_matrix().to_4x4()


def layout(props, rg, dona_caja, alien, variante=1):
    """World matrix of each new piece and of the alien. The flight cases lie lengthwise on the middle and front bars (each rests on two), side by
    side across the roof; a guitar case lies on the outer half of each; the alien lies on the pile, above the net's top, head forward (+y).
    variante picks where the bags stand: 1 the roof ahead of the pile, 2 the roof behind it, 3 on the flight cases beside the guitar cases.
    dona_caja: the donut's world box (his placement stays). Returns ({name: Matrix}, {name: world box})."""
    Z90 = (0, 0, math.pi / 2)
    d = {k: dim_local(o) for k, o in props.items()}
    ya = (rg["ys"][1] + rg["ys"][2]) / 2 - 0.04   # a little behind the middle of the two bars it rests on, to leave room ahead for the bags
    M, B = {}, {}

    def poner(n, loc, rot=(0, 0, 0)):
        M[n] = Mw(loc, rot)
        B[n] = caja_en(props[n] if n in props else alien, M[n])
    for n, lado in (("k3_maleta_a", -1), ("k3_maleta_b", 1)):
        w = d[n].y
        poner(n, (CX + lado * (w / 2 + 0.01), ya, rg["zb"] + d[n].z / 2 + 0.001), Z90)
    for n, ref, lado in (("k3_guitarra_a", "k3_maleta_a", -1), ("k3_guitarra_b", "k3_maleta_b", 1)):
        c = (B[ref][0] + B[ref][1]) / 2
        w, wr = d[n].y, B[ref][1].x - B[ref][0].x
        poner(n, (c.x + lado * (wr / 2 - w / 2 - 0.03), ya, B[ref][1].z + d[n].z / 2 + 0.003), Z90)
    ext_y = (min(B[k][0].y for k in B), max(B[k][1].y for k in B))
    zr = rg["zt"] + 0.002
    yf = rg["ys"][2] + 0.029 + 0.012    # ahead of the front bar (its half width 29 mm) on the roof panel
    if variante == 1:    # both bags side by side on the roof panel ahead of the pile
        for n, dx in (("k3_bolsa", -0.30), ("k3_mochila", 0.30)):
            poner(n, (CX + dx, yf + d[n].y / 2, zr + d[n].z / 2))
    elif variante == 2:  # the small bag behind the pile (between it and the donut), the backpack ahead
        poner("k3_bolsa", (CX - 0.30, ext_y[0] - 0.015 - d["k3_bolsa"].y / 2, zr + d["k3_bolsa"].z / 2))
        poner("k3_mochila", (CX + 0.30, yf + d["k3_mochila"].y / 2, zr + d["k3_mochila"].z / 2))
    else:                # both standing on the pile, on the flight cases' free inner half
        for n, ref, lado in (("k3_bolsa", "k3_maleta_a", 1), ("k3_mochila", "k3_maleta_b", -1)):
            c = (B[ref][0] + B[ref][1]) / 2
            poner(n, (c.x + lado * 0.16, ya, B[ref][1].z + d[n].z / 2 + 0.003))
    # alien: lengthwise on the pile, its underside 3 cm over the highest thing under its footprint (net rope + clearance)
    da = dim_local(alien)
    yaa = ya
    cajas_bajo = [B[k] for k in B]
    for _ in range(2):
        poner("k3_alien", (CX, yaa, 0), (-math.pi / 2, 0, 0))
        a = B["k3_alien"]
        tope = max((b[1].z for b in cajas_bajo if k_overlap(a, b) and b is not a), default=rg["zb"])
        tope = max(tope, dona_caja[1].z if k_overlap(a, dona_caja) else 0)
        zc = tope + 0.03 + da.y / 2
        poner("k3_alien", (CX, yaa, zc), (-math.pi / 2, 0, 0))
    return M, B


def k_overlap(a, b, m=0.0):
    return a[0].x < b[1].x - m and a[1].x > b[0].x + m and a[0].y < b[1].y - m and a[1].y > b[0].y + m


# ---------------------------------------------------------------- net and straps
def suavizar(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def altura(cajas, x, y, base, margen):
    z = base
    for a, b in cajas:   # measured from the box grown by 1 cm: the rope (7 mm) never runs through a wall
        d = math.hypot(max(a.x - 0.01 - x, 0, x - b.x - 0.01), max(a.y - 0.01 - y, 0, y - b.y - 0.01))
        z = max(z, base + (b.z + 0.012 - base) * suavizar(1 - d / margen))
    return z


def tubo(bm, pts, r, lados=6):
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


def cinta(bm, pts, ancho, grueso):
    """Flat ribbon along pts that run in the x-z plane: `ancho` along y, `grueso` along the local normal."""
    L = Vector((0, 1, 0))
    anillos = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        n = t.cross(L).normalized()
        anillos.append([bm.verts.new(p + L * sy * ancho / 2 + n * sn * grueso / 2) for sy, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    for i in range(len(anillos) - 1):
        for k in range(4):
            bm.faces.new((anillos[i][k], anillos[i][(k + 1) % 4], anillos[i + 1][(k + 1) % 4], anillos[i + 1][k]))
    bm.faces.new(anillos[0][::-1])
    bm.faces.new(anillos[-1])


def malla(nombre, bm, color, padre):
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    m = bpy.data.materials.get(color[0]) or bpy.data.materials.new(color[0])
    if not m.use_nodes:
        m.use_nodes = True
        p = m.node_tree.nodes["Principled BSDF"]
        p.inputs["Base Color"].default_value = (*color[1], 1)
        p.inputs["Roughness"].default_value = color[2]
    me.materials.append(m)
    o = bpy.data.objects.new(nombre, me)
    sc.collection.objects.link(o)
    o.parent = padre
    o.matrix_parent_inverse = padre.matrix_world.inverted() if padre else Matrix.Identity(4)
    return o


def tender(cajas, alien_obj, rg, padre, paso=0.22):
    """cajas: {name: (lo, hi)} world boxes of every netted piece (everything but the alien). Replaces carga_red (rope 7 mm, 22 cm cells over the
    union of the pieces' footprints + 2 cm, hugging each piece's sides) and carga_red_alien (two 4 cm straps across the alien, over the pile,
    anchored on the middle and front bars just outside the pile). Returns (net, straps)."""
    for n in ("carga_red", "carga_red_alien"):
        v = O.get(n)
        if v:
            me = v.data
            O.remove(v, do_unlink=True)
            bpy.data.meshes.remove(me)
    bx = list(cajas.values())
    x0 = min(a.x for a, b in bx) - 0.02; x1 = max(b.x for a, b in bx) + 0.02
    y0 = min(a.y for a, b in bx) - 0.02; y1 = max(b.y for a, b in bx) + 0.02
    base = rg["zb"] + 0.008
    n, m = max(2, round((x1 - x0) / paso)), max(2, round((y1 - y0) / paso))
    bm = bmesh.new()
    lineas = [("x", x0 + (x1 - x0) * i / n) for i in range(n + 1)] + [("y", y0 + (y1 - y0) * j / m) for j in range(m + 1)]
    for tipo, v in lineas:
        L = int(((y1 - y0) if tipo == "x" else (x1 - x0)) / 0.04)
        pts = [Vector((v, y0 + (y1 - y0) * k / L, 0)) if tipo == "x" else Vector((x0 + (x1 - x0) * k / L, v, 0)) for k in range(L + 1)]
        for p in pts:
            p.z = altura(bx, p.x, p.y, base, 0.035)
        tubo(bm, pts, HILO)
    red = malla("carga_red", bm, ("web_red_cuerda", (0.05, 0.05, 0.05), 0.8), padre)
    # straps
    bm = bmesh.new()
    bvh = BVHTree.FromPolygons([alien_obj.matrix_world @ v.co for v in alien_obj.data.vertices], [p.vertices[:] for p in alien_obj.data.polygons])
    xa, xb = x0 - 0.03, x1 + 0.03
    for y in (rg["ys"][1], rg["ys"][2]):
        xs = [xa + k * 0.01 for k in range(int((xb - xa) / 0.01) + 1)]
        zp, za = [], []
        for x in xs:
            z = rg["zb"] + CINTA[1]
            for a, b in bx:   # the pile's outline, 4.5 cm out at the sides, 3 cm clear over the net
                if a.x - 0.045 <= x <= b.x + 0.045 and a.y - 0.02 <= y <= b.y + 0.02:
                    z = max(z, b.z + 0.03)
            zp.append(z)
            h = 0.0
            for dy in (-CINTA[0] / 2, -CINTA[0] / 4, 0.0, CINTA[0] / 4, CINTA[0] / 2):   # across the ribbon: it rests on the highest of them
                hit, _, _, _ = bvh.ray_cast(Vector((x, y + dy, 4.0)), Vector((0, 0, -1)))
                if hit:
                    h = max(h, hit.z + 0.010)
            za.append(h)
        # the alien's height spreads 3 cm to each side, so the ribbon never cuts through its flank on the way down
        pts = [Vector((x, y, max(zp[k], max(za[max(0, k - 3):k + 4])))) for k, x in enumerate(xs)]
        cinta(bm, pts, *CINTA)
    correas = malla("carga_red_alien", bm, ("web_correa", (0.55, 0.12, 0.02), 0.7), padre)
    return red, correas


# ---------------------------------------------------------------- the checks of the brief
def bvh_mundo(o):
    return BVHTree.FromPolygons([o.matrix_world @ v.co for v in o.data.vertices], [p.vertices[:] for p in o.data.polygons])


def medir(items, alien, red, correas, barras, titulo=""):
    """Prints and returns the numbers: rope vertices inside any netted piece, alien above the net, straps to the alien, overlaps."""
    bpy.context.view_layer.update()
    r = {}
    vs = [red.matrix_world @ v.co for v in red.data.vertices]
    dentro = {}
    for k, o in items.items():
        t = bvh_mundo(o)
        lo, hi = caja_vert(o)
        c = 0
        for v in vs:
            # inside the piece's box (5 mm in), or closer to its surface than the rope's own radius: the rope would be through it
            if lo.x + 0.005 < v.x < hi.x - 0.005 and lo.y + 0.005 < v.y < hi.y - 0.005 and lo.z + 0.005 < v.z < hi.z - 0.005:
                c += 1
            elif lo.x - 0.02 < v.x < hi.x + 0.02 and lo.y - 0.02 < v.y < hi.y + 0.02 and lo.z - 0.02 < v.z < hi.z + 0.02:
                if t.find_nearest(v)[3] < HILO * 0.7:
                    c += 1
        dentro[k] = c
    r["cuerda_dentro"] = dentro
    # net vs pieces: nearest rope point clear of the surface (>= 1 mm); counts rope vertices closer than the rope radius
    tr = BVHTree.FromPolygons(vs, [p.vertices[:] for p in red.data.polygons])
    # alien above the net: no net above any alien vertex (ray up), and the smallest gap to the net below
    va = [alien.matrix_world @ v.co for v in alien.data.vertices]
    arriba = sum(1 for v in va[::3] if tr.ray_cast(v, Vector((0, 0, 1)))[0] is not None)
    huecos = [v.z - h.z for v in va[::3] for h in [tr.ray_cast(v, Vector((0, 0, -1)))[0]] if h is not None]
    r["alien_red_encima"] = arriba
    r["alien_hueco_min_m"] = round(min(huecos), 4) if huecos else None
    ta = bvh_mundo(alien)
    vc = [correas.matrix_world @ v.co for v in correas.data.vertices]
    ds = [ta.find_nearest(v)[3] for v in vc]
    r["correa_a_alien_min_m"] = round(min(ds), 4)
    r["correa_a_alien_tocan"] = sum(1 for d in ds if d < 0.012)
    r["correa_dentro_alien"] = sum(1 for d in ds if d < 0.002)
    sol = {k: bvh_mundo(o) for k, o in {**items, "k3_alien": alien}.items()}
    barr = {b.name: bvh_mundo(b) for b in barras}
    cruces = {}
    ks = list(sol)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            c = len(sol[ks[i]].overlap(sol[ks[j]]))
            if c:
                cruces[f"{ks[i]}~{ks[j]}"] = c
        for b, tb in barr.items():
            c = len(sol[ks[i]].overlap(tb))
            if c:
                cruces[f"{ks[i]}~{b}"] = c
    r["cruces"] = cruces
    print("CARGA medir", titulo, json.dumps(r), flush=True)
    return r
