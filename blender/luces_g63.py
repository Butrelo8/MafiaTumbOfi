"""Every lamp of the real Mercedes-AMG G63 6x6 (2013, W463), at its real position (owner 2026-11-18 19:11-19:20: "the actual
light position of the G 63 6x6"; the two roof LED clusters side by side on the visor first). Reference: the front photo
~/cc-out/mto-asset-fixes/parrilla/ref-frente-g63-6x6.png for the front lamps' x and proportions; heights and depths from the
model's own body (blender/tripo/volcar_cabina.py dump of montaje.blend, ~/cc-out/mto-asset-fixes/luces/g63/), not from the
model's Light_Col chrome, which only roughly follows the real lamps.

One mesh, `luces_g63`, holds every lamp lens (one material per colour: live cost = one draw call per material), parented
to the truck. Cycles also gets real lights where they light something (the cab interior here; headlights and tail in
escena.mundo_render); the lenses alone
glow (emission + the page's bloom live). Coordinates are the truck's local frame at rest (escena.py: x = lane, CX the
centre line, +y the nose, z up from the road), which is world space at build time.
"""
import math
import bpy
import bmesh
from mathutils import Matrix, Vector

# --- lens materials: name -> (base, emission colour, strength). Linear RGB.
MATS = {
    "g63_led": ((0.9, 0.92, 0.95), (0.82, 0.9, 1.0), 25.0),       # headlight rings: 6000 K LED
    "g63_ambar": ((0.8, 0.35, 0.02), (1.0, 0.42, 0.02), 6.0),     # fender-top and mirror turn signals, as side markers
    "g63_cabina": ((0.9, 0.85, 0.75), (1.0, 0.72, 0.42), 4.0),    # inside: reading-lamp lenses, dash glow
    # the aftermarket W463 ambient kit (owner's ref: gwagenparts.com ambient-light-kit, photos in /mnt/e/tmp/mto-asset-fixes/
    # ref/ambiente/): door-card strips and a passenger dash-trim line; its footwell pools are Cycles lights (PIES)
    "g63_ambiente": ((0.9, 0.1, 0.08), (1.0, 0.05, 0.03), 8.0),  # 3 barely read next to the 300 W face lamps (emblema/amb/)
}
PIES = ((0.15, 0.25, 1.0), 5.0)  # footwell light colour and watts (the kit's photos: red strips, blue footwells)


def _mats():
    out = {}
    for n, (base, em, s) in MATS.items():
        m = bpy.data.materials.get(n) or bpy.data.materials.new(n)
        m.use_nodes = True
        p = m.node_tree.nodes["Principled BSDF"]
        p.inputs["Base Color"].default_value = (*base, 1)
        p.inputs["Roughness"].default_value = 0.25
        p.inputs["Emission Color"].default_value = (*em, 1)
        p.inputs["Emission Strength"].default_value = s
        out[n] = m
    return out


def _caja(bm, idx, centro, tam, normal=(0, 1, 0)):
    """A thin lens box: tam = (width, height, depth) in the lens's own frame (depth along its normal)."""
    q = Vector(normal).normalized().to_track_quat("Z", "Y")
    M = Matrix.Translation(centro) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((*tam, 1))
    r = bmesh.ops.create_cube(bm, size=1.0, matrix=M)
    for f in {f for v in r["verts"] for f in v.link_faces}:
        f.material_index = idx


def _disco(bm, idx, centro, r_ext, r_int, normal, prof=0.004, n=24):
    """A flat ring (r_int > 0) or disc facing `normal`: the headlight LED ring."""
    q = Vector(normal).normalized().to_track_quat("Z", "Y").to_matrix()
    c = Vector(centro)
    ext = [c + q @ Vector((r_ext * math.cos(2 * math.pi * i / n), r_ext * math.sin(2 * math.pi * i / n), 0)) for i in range(n)]
    if r_int > 0:
        intr = [c + q @ Vector((r_int * math.cos(2 * math.pi * i / n), r_int * math.sin(2 * math.pi * i / n), 0)) for i in range(n)]
        ve, vi = [bm.verts.new(p) for p in ext], [bm.verts.new(p) for p in intr]
        for i in range(n):
            bm.faces.new((ve[i], ve[(i + 1) % n], vi[(i + 1) % n], vi[i])).material_index = idx
    else:
        bm.faces.new([bm.verts.new(p) for p in ext]).material_index = idx


def _luz(nombre, tipo, loc, w, color, parent, mira=None, tam=0.05, cono=None):
    ld = bpy.data.lights.new(nombre, tipo)
    ld.energy, ld.color = w, color
    if tipo == "AREA":
        ld.size = tam
    else:
        ld.shadow_soft_size = tam
    if tipo == "SPOT":
        ld.spot_size, ld.spot_blend = math.radians(cono or 60), 0.6
    o = bpy.data.objects.new(nombre, ld)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    if mira is not None:
        o.rotation_euler = (Vector(mira) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    o.parent = parent
    o.visible_camera = False  # the lens mesh is what the camera sees
    return o


# --- the cab interior (dump: tripo3/cabina.npz). Left-hand drive: the driver sits at x < CX.
def lentes_interior(bm, I, cx):
    k = I["g63_cabina"]
    for x in (cx - 0.07, cx + 0.07):  # overhead control panel, two reading lamps (model's lenses at y 0.80, z 2.12-2.17)
        _caja(bm, k, (x, 0.792, 2.135), (0.045, 0.03, 0.004), normal=(0, -0.6, -0.8))
    for x in (cx - 0.40, cx + 0.40):  # rear reading lamps in the headliner over each rear seat (headliner z 2.24 there)
        _caja(bm, k, (x, -0.40, 2.232), (0.07, 0.04, 0.004), normal=(0, 0, -1))
    _caja(bm, k, (cx, -0.25, 2.178), (0.16, 0.06, 0.004), normal=(0, 0, -1))  # centre dome lamp (cab_techo z 2.183)
    a = I["g63_ambiente"]
    for x, n in ((cx - 0.685, 1), (cx + 0.695, -1)):  # ambient strips along the door cards (caja5 cards x -0.690 / +0.700)
        _caja(bm, a, (x, 0.55, 1.40), (0.70, 0.006, 0.004), normal=(n, 0, 0))   # front door, y 0.20-0.90
        _caja(bm, a, (x, -0.45, 1.20), (0.60, 0.006, 0.004), normal=(n, 0, 0))  # rear door, y -0.75..-0.15
    _caja(bm, a, (cx + 0.43, 1.133, 1.51), (0.42, 0.006, 0.004), normal=(0, -1, 0))  # passenger dash trim (face y 1.134, z 1.51)
    for c, n in (((1.235, 1.183, 1.598), (0.46, -0.89, 0.04)), ((1.432, 1.183, 1.598), (-0.46, -0.89, 0.05))):
        _disco(bm, k, Vector(c) - 0.006 * Vector(n), 0.05, 0.0, n)  # instrument cluster: 6 mm behind each gauge glass (mica)
    _caja(bm, k, (cx, 1.128, 1.6235), (0.19, 0.085, 0.003), normal=(0, -0.97, 0.22))  # COMAND screen on the centre stack (7 mm in)


def luces_interior(parent, cx, w=1.0):
    """Cycles lights for the cab. w scales them all (stop 4 measures faces with it)."""
    c = (1.0, 0.72, 0.42)
    out = []
    for x in (cx - 0.07, cx + 0.07):
        out.append(_luz("g63_lectura_del", "SPOT", (x, 0.78, 2.12), 4 * w, c, parent, mira=(x + (x - cx) * 3, 0.25, 1.3), tam=0.03, cono=70))
    for x in (cx - 0.40, cx + 0.40):
        out.append(_luz("g63_lectura_tras", "SPOT", (x, -0.40, 2.225), 4 * w, c, parent, mira=(x, -0.5, 1.3), tam=0.03, cono=80))
    out.append(_luz("g63_domo", "AREA", (cx, -0.25, 2.172), 6 * w, c, parent, tam=0.12))  # an area light faces -Z: down
    out.append(_luz("g63_tablero", "AREA", (cx - 0.40, 1.15, 1.60), 0.6 * w, (0.85, 0.9, 1.0), parent, mira=(cx - 0.40, 0.3, 1.7), tam=0.2))
    # the kit's four footwell lights, facing down: under the driver's knee panel, under the glovebox, under each front seat
    for p in ((cx - 0.35, 1.00, 1.42), (cx + 0.35, 1.12, 1.36), (cx - 0.35, 0.15, 1.20), (cx + 0.35, 0.15, 1.20)):
        out.append(_luz("g63_pies", "AREA", p, PIES[1] * w, PIES[0], parent, tam=0.08))
    return out


# --- outside. Front: the photo's ratios checked against the model (headlights at CX +-0.62, the LED strip 0.14 m under each
# headlight centre; Light_Col's strip sits 1-12 mm behind the housing's plastic, so TIRAS puts it on the face). The roof clusters are props_placement.barra_luces (P1: five LED cups and a 25 W
# spot per pocket, x CX +-0.51-0.69, z 2.157-2.193, front y 1.143): not repeated here. Rear: Wikimedia Commons "Mercedes-Benz
# G 63 AMG 6x6 (W463) rear.JPG": the tail clusters are the bed's bottom corners (the model's calaveras, z 0.92-1.04).
FAROS = [(1.105, 2.706, 1.176), (2.351, 2.706, 1.176)]  # headlight glass (mica) centres, front face y 2.704, r ~0.09
# The LED strip under each headlight: six dots (the photo shows discrete LEDs) at z 1.045 on the housing's curved face.
# (x, face y) ray-cast from the front on the stop-6 dump (/mnt/e/tmp/mto-asset-fixes/tira/sonda_tira2.py).
TIRAS = [[(1.01, 2.712), (1.05, 2.733), (1.09, 2.747), (1.13, 2.759), (1.17, 2.768), (1.21, 2.776)],
         [(2.43, 2.718), (2.39, 2.737), (2.35, 2.751), (2.31, 2.761), (2.27, 2.770), (2.23, 2.778)]]


def lentes_exterior(bm, I):
    led, ambar = I["g63_led"], I["g63_ambar"]
    for c in FAROS:  # the LED ring round each headlight (photo: a bright circle at the rim)
        _disco(bm, led, Vector(c) + Vector((0, -0.006, 0)), 0.090, 0.079, (0, 1, 0), n=40)  # on the bezel (revisar: -3.4 mm still floated 3)
    for tira in TIRAS:
        for i, (x, y) in enumerate(tira):  # face normal from the neighbours' slope; the dot's back 1 mm into the face
            a, b = tira[max(i - 1, 0)], tira[min(i + 1, len(tira) - 1)]
            n = Vector((-(b[1] - a[1]) / (b[0] - a[0]), 1, 0)).normalized()
            _caja(bm, led, Vector((x, y, 1.045)) + 0.001 * n, (0.022, 0.014, 0.004), normal=n)
    for x in (0.995, 2.445):  # fender-top turn-signal pods (W463: on each front wing's top, ahead; the model has none)
        _caja(bm, ambar, (x, 2.42, 1.386), (0.06, 0.03, 0.045), normal=(0, 1, 0))  # on the wing (z 1.392 floated 5-6 mm)
    # amber side marker on each front wing's flank just ahead of the door (owner's ref ref/ambar-laterales.png; flank face
    # x 0.889 / 2.563 at y 1.00, z 1.28, ray-cast: emblema/sonda_ambar.py), back 1 mm into the face
    for x, n in ((0.888, -1), (2.564, 1)):
        _caja(bm, ambar, (x, 1.00, 1.28), (0.045, 0.022, 0.004), normal=(n, 0, 0))


def malla(parent, cx=1.72, interior=True):
    """The lens mesh: one object, one material per colour (live: one draw call each). Returns it."""
    I = _mats()
    me = bpy.data.meshes.new("luces_g63")
    for m in I.values():
        me.materials.append(m)
    idx = {n: i for i, n in enumerate(I)}
    bm = bmesh.new()
    lentes_exterior(bm, idx)
    if interior:
        lentes_interior(bm, idx, cx)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("luces_g63", me)
    bpy.context.scene.collection.objects.link(o)
    o.parent = parent
    return o
