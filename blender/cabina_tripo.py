"""The owner's Tripo front seats and centre console in the cab (defects 2, 3; owner 2026-11-18 17:53 and 18:00), behind
CABINA_TRIPO=1 until the owner approves the sheet (~/cc-out/mto-asset-fixes/tripo3/). transicion.preparar() calls poner()
instead of sin_cabeceras(): the new seats bring their own headrests.

The G63 cab is triangle soup merged by material (Second_Body_Col, plastico, ...), so the old parts go by volume: every face whose
centre lies in a seat or console box, or that a new part encloses (borrar_viejos), outside the roof, the wheel and column, the
carpet and the centre stack. Boxes
measured on medir1/montaje.blend (tripo/volcar_cabina.py + ~/cc-out/mto-asset-fixes/tripo3/seg.py): driver seat x 1.081-1.585,
y 0.193-1.051, z 0.982-1.824 (headrest already gone); passenger x 1.855-2.360, y 0.093-0.951 (10 cm further back); console
x 1.575-1.865, y 0.298-0.979, z 0.981-1.466.

Seats (blender/assets/asiento/asiento-tripo3*.glb; no screen piece in the mesh: one shell, 47.9 k tris): turned to face +Y,
scaled 0.95 (cushion top 1.19, backrest 1.72, headrest top 1.93 over the 0.98 floor) and squeezed in x to the old seat's 0.50 m
(the Tripo seat is 0.59 m at that scale; the slot between door card and console is ~0.52). Backrest's rear on the old one's.
The switch column and the red tab are on the Tripo seat's +x side (outboard): the driver's stays, the passenger's is mirrored.
Console (consola-tripo3.glb, 49.4 k tris, ~17 deg off-axis in its file): turned to its narrowest width, armrest (the tall end)
to the rear, length fitted to the old console (y 0.28-0.98), base on the floor; CABINA_TRIPO_CONSOLA_Z stretches it in z
(1.0 = uniform: its top is 0.23 m lower than the G63's armrest).
Env: CABINA_TRIPO_ASIENTO = seat file suffix ("-deslucido" default: tripo/deslucir.py; "" raw).
"""
import bpy, math, os
import numpy as np
from mathutils import Vector, Matrix

AQUI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(AQUI, "assets", "asiento")
CX = 1.72
PISO = 0.98
BAJA, ATRAS = float(os.environ.get("CABINA_TRIPO_BAJA", "0.08")), float(os.environ.get("CABINA_TRIPO_ATRAS", "0.09"))
# the seats sit BAJA lower (rails under the floor) and ATRAS further back than the G63's: at 0/0 the cast's thighs sank 84-89 mm
# into the cushion, the manager's shoulder 79 mm into the inboard bolster, Héctor's head 61 mm into the headrest (probar_cabina_tripo)
ASIENTOS = {"izq": ((1.081, 0.193), (1.585, 0.0)), "der": ((1.855, 0.093), (2.360, 0.0))}  # (x0, backrest rear y), (x1, -)
CAJAS = {"asiento_izq": ((CX - 0.64, 0.05, 0.97), (CX - 0.135, 1.06, 1.88)),  # top: the old backrest (1.824; headrests gone),
         "asiento_der": ((CX + 0.135, 0.05, 0.97), (CX + 0.64, 1.06, 1.88)),   # not the headliner (2.12 took 315 of its faces)
         "consola": ((1.575, 0.25, 0.95), (1.865, 0.98, 1.47)),
         # the old headrests and backrest tops over the 1.88 cap (owner 2026-11-19 18:29, Banda/Diego: "the old cab around Diego
         # reads as shredded facets": 270 cab_piel + 350 plastico faces at z 1.88-2.03); the door side kept 3 cm in, and the
         # headliner material (CABECERA_NO) stays even here
         "cabecera_izq": ((CX - 0.61, 0.05, 1.88), (CX - 0.135, 0.60, 2.03)),
         "cabecera_der": ((CX + 0.135, 0.05, 1.88), (CX + 0.61, 0.60, 2.03))}
CABECERA_NO = "cab_techo"
CONSOLA_Y = (0.28, 0.98)
FUERA_OBJ = ("Material2", "rueda1", "rueda4", "w_copa", "prop_bottle")
PISO_MAT = "cab_alfombra"  # the floor: the seats sink BAJA into it, so it goes only where a new part wholly encloses it
HOLGURA = (0.02, 0.0, 0.0)  # the old seats' inboard sides lie on the boxes' x edge (1.585 = CX - 0.135): 2 cm to spare in x only
# (in y the centre stack starts 2-3 cm past the console box)


def dentro(arbol, p):
    """True when p lies inside the closed mesh of `arbol` (a BVHTree): ray parity on three axes, majority."""
    votos = 0
    for d in ((0, 0, 1), (1, 0, 0), (0, 1, 0)):
        d, q, n = Vector(d), Vector(p), 0
        for _ in range(40):
            hit = arbol.ray_cast(q + d * 1e-5, d)
            if hit[0] is None:
                break
            n, q = n + 1, hit[0]
        votos += n % 2
    return votos >= 2


def zona_vieja(c, mat=""):
    """The old seat or console box whose space holds point c (+ HOLGURA), None outside or over the driver's wheel and column."""
    for z, (a, b) in CAJAS.items():
        if z.startswith("cabecera") and mat == CABECERA_NO:
            continue
        if np.all(c >= np.array(a) - HOLGURA) and np.all(c <= np.array(b) + HOLGURA):
            if z == "asiento_izq" and c[1] > 0.62 and c[2] > 1.32:
                return None  # the wheel and column over the driver's cushion (the passenger side has none)
            return z
    return None


def borrar_viejos(camion_e, nuevos=()):
    """Deletes the old seats and console from the G63's material soup (owner 2026-11-19 16:56: their bits floated above and
    beside the Tripo seats and clipped the console). A face goes when its centre lies in a seat or console box (+ HOLGURA),
    or when a new part (`nuevos`, already placed) wholly encloses it, or crosses its surface with the face's centre inside the
    part's box (not the floor). Kept: the wheel and column over the driver's cushion,
    and the floor (PISO_MAT) unless enclosed. Until 2026-11-19 a face went only when wholly inside a box, the wheel exemption
    covered the passenger side too and the carbon trim stayed: the big soup triangles on the boxes' edges survived."""
    import bmesh
    from mathutils.bvhtree import BVHTree
    arboles = []
    for o in nuevos:
        me = o.data
        v = [o.matrix_world @ x.co for x in me.vertices]
        arboles.append((np.min(v, 0), np.max(v, 0), BVHTree.FromPolygons(v, [p.vertices for p in me.polygons])))
    n = {}
    for o in [camion_e] + list(camion_e.children_recursive):
        if o.type != "MESH" or not o.data.polygons or not o.name.startswith("Material") or o.name in FUERA_OBJ:
            continue  # only the G63's own meshes (named after their glTF materials): the cast and props are truck children too
        me = o.data
        W = np.array(o.matrix_world)
        v = np.empty(len(me.vertices) * 3)
        me.vertices.foreach_get("co", v)
        v = v.reshape(-1, 3) @ W[:3, :3].T + W[:3, 3]
        mats = [m.name.split(".")[0] if m else "" for m in me.materials] or [""]
        cruzan = set()  # faces through a new part's surface (the old shifter stub, the tunnel sides along the console's base)
        if arboles and len(me.polygons):
            mio = BVHTree.FromPolygons(v.tolist(), [p.vertices for p in me.polygons])
            for _, _, t in arboles:
                cruzan.update(i for i, _ in mio.overlap(t))
        fuera = []
        for p in me.polygons:
            q = v[list(p.vertices)]
            c = q.mean(0)
            mat = mats[min(p.material_index, len(mats) - 1)]
            zona = None
            if mat != PISO_MAT:
                zona = zona_vieja(c, mat)
            if zona is None:
                for lo, hi, t in arboles:
                    if np.all(q >= lo) and np.all(q <= hi) and all(dentro(t, x) for x in q):
                        zona = "encerrada"
                        break
                    if mat != PISO_MAT and p.index in cruzan and np.all(c >= lo - 0.01) and np.all(c <= hi + 0.01):
                        zona = "cruza"
                        break
            if zona:
                fuera.append(p.index)
                k = f"{zona}:{mat}"
                n[k] = n.get(k, 0) + 1
        if fuera:
            bm = bmesh.new()
            bm.from_mesh(me)
            bm.faces.ensure_lookup_table()
            bmesh.ops.delete(bm, geom=[bm.faces[i] for i in fuera], context="FACES")
            bm.to_mesh(me)
            bm.free()
    print("CABINA_TRIPO borradas", n, flush=True)


def importar(nombre_glb, nombre):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ASSETS, nombre_glb))
    nuevos = [o for o in bpy.data.objects if o not in antes]
    o = next(x for x in nuevos if x.type == "MESH")
    bpy.context.view_layer.update()
    M = o.matrix_world.copy()
    o.parent = None
    o.data.transform(M)  # bake the importer's Y-up turn into the mesh
    o.matrix_world = Matrix.Identity(4)
    for x in nuevos:
        if x is not o:
            bpy.data.objects.remove(x)
    o.name = o.data.name = nombre
    for m in o.data.materials:
        m.name = nombre
    return o


def caja(me):
    v = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", v)
    v = v.reshape(-1, 3)
    return v, v.min(0), v.max(0)


def asiento(lado, glb):
    o = importar(glb, "tripo_asiento_" + lado)
    me = o.data
    me.transform(Matrix.Rotation(math.pi, 4, "Z"))  # its front was -Y after import; the cab faces +Y
    _, lo, hi = caja(me)
    (x0, y_atras), (x1, _) = ASIENTOS[lado]
    s = 0.95
    sx = (x1 - x0) / ((hi[0] - lo[0]) * s)
    espejo = -1 if lado == "der" else 1  # switch column outboard on both
    me.transform(Matrix.Diagonal((espejo * sx * s, s, s, 1)))
    if espejo < 0:
        me.flip_normals()
    _, lo, hi = caja(me)
    me.transform(Matrix.Translation(((x0 + x1) / 2 - (lo[0] + hi[0]) / 2, y_atras - ATRAS - lo[1], PISO - BAJA - lo[2])))
    _, lo, hi = caja(me)
    print(f"CABINA_TRIPO asiento {lado} escala {s} x {sx * s:.3f} caja ({lo[0]:.3f},{lo[1]:.3f},{lo[2]:.3f})..({hi[0]:.3f},{hi[1]:.3f},{hi[2]:.3f})", flush=True)
    return o


def consola(kz):
    o = importar(os.environ.get("CABINA_TRIPO_CONSOLA", "consola-tripo3.glb"), "tripo_consola")  # file in ASSETS
    me = o.data
    v, _, _ = caja(me)
    giro = min(np.radians(np.arange(-90, 90.01, 0.5)), key=lambda t: np.ptp(v[:, 0] * math.cos(t) - v[:, 1] * math.sin(t)))
    me.transform(Matrix.Rotation(giro, 4, "Z"))
    v, lo, hi = caja(me)
    L = hi[1] - lo[1]
    alto_frente = v[v[:, 1] > hi[1] - 0.25 * L, 2].max()
    alto_atras = v[v[:, 1] < lo[1] + 0.25 * L, 2].max()
    if alto_frente > alto_atras:  # the armrest is the tall end: it goes to the rear
        me.transform(Matrix.Rotation(math.pi, 4, "Z"))
        giro += math.pi
    s = (CONSOLA_Y[1] - CONSOLA_Y[0]) / L
    me.transform(Matrix.Diagonal((s, s, s * kz, 1)))
    _, lo, hi = caja(me)
    me.transform(Matrix.Translation((CX - (lo[0] + hi[0]) / 2, CONSOLA_Y[0] - lo[1], PISO - lo[2])))
    _, lo, hi = caja(me)
    print(f"CABINA_TRIPO consola giro {math.degrees(giro):.1f} deg escala {s:.3f} z x{kz} caja ({lo[0]:.3f},{lo[1]:.3f},{lo[2]:.3f})..({hi[0]:.3f},{hi[1]:.3f},{hi[2]:.3f})", flush=True)
    return o


def poner(camion_e):
    glb = "asiento-tripo3" + os.environ.get("CABINA_TRIPO_ASIENTO", "-deslucido") + ".glb"
    nuevos = [asiento("izq", glb), asiento("der", glb), consola(float(os.environ.get("CABINA_TRIPO_CONSOLA_Z", "1.0")))]
    borrar_viejos(camion_e, nuevos)
    sc = bpy.context.scene
    for o in nuevos:
        if o.name not in sc.collection.objects and not o.users_collection:
            sc.collection.objects.link(o)
        o.parent = camion_e
        o.matrix_parent_inverse = camion_e.matrix_world.inverted()
    bpy.context.view_layer.update()
    return nuevos
