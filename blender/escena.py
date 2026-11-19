"""Truck on an endless highway: one scene for the live page (GLB export) and the Cycles loop.

Values (stops, presets, world sizes) come from src/lib/escena.json, shared with the page.
Run headless from WSL (Blender on Windows):
  /mnt/e/Blender/blender.exe -b --factory-startup --python "$(wslpath -w blender/escena.py)" -- glb
  ... -- still <preset> <stop> <w> <h> <out.png> [samples]
  ... -- loop  <preset> <stop> <w> <h> <out_dir> [samples] [first] [last]
  ... -- hoja  <out_dir> [samples]     frame 0 of every stop, night, both formats (the sheet to approve before a batch)
  ... -- lote  <out_dir> [samples]     the batch: every stop's loop, night, both formats, scene built once
  ... -- transicion <out_dir> <w> <h> [samples] [first] [last] [step]   the cab -> outside move (blender/transicion.py)
The world moves -Y (Blender) by `recorrido_loop` metres per loop; everything periodic divides it, so frame N == frame 0.
"""
import bpy, json, math, os, sys
from mathutils import Vector, Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import luces_g63
import parrilla_g63

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(REPO, "src", "lib", "escena.json"), encoding="utf8"))
ASSETS = os.path.join(REPO, "blender", "assets", "camion")
MUNDO = CFG["mundo"]
FPS, LOOP_S, RECORRIDO, TRAMO = MUNDO["loop_fps"], MUNDO["loop_s"], MUNDO["recorrido_loop"], MUNDO["tramo"]
NFR = FPS * LOOP_S
# Light power conversions from the preset's page units to Cycles watts (calibrated by measuring renders).
W_FARO, W_POSTE = 40.0, 2200.0


def b(v):  # three.js (Y up, -Z forward) -> Blender (Z up, +Y forward)
    return Vector((v[0], -v[2], v[1]))


def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def mat(name, color, rough, metal=0.0, coat=0.0, emit=None, estr=0.0):
    m = bpy.data.materials.new(name)
    p = m.node_tree.nodes.get("Principled BSDF") if m.node_tree else None
    if p is None:
        m.use_nodes = True
        p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = 0.04
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = estr
    return m


def caja(name, size, loc, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def cil(name, r, h, loc, m, rot=(0, 0, 0), verts=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    return o


def plano(name, w, l, y0, z, m, tile):
    """Plane x in [-w/2, w/2], y in [y0, y0 + l]; UV in metres / tile so textures repeat every `tile` m."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, y0 + l / 2, z))
    o = bpy.context.object
    o.name = name
    o.scale = (w, l, 1)
    bpy.ops.object.transform_apply(scale=True)
    uv = o.data.uv_layers.active.data
    for loop in o.data.loops:
        co = o.data.vertices[loop.vertex_index].co
        uv[loop.index].uv = ((co.x + w / 2) / tile if tile != w else (co.x + w / 2) / w, (co.y + o.location.y) / tile)
    o.data.materials.append(m)
    return o


def tex_mat(name, stem, tile_dim=1.0, oscurecer=1.0, tinte=(1, 1, 1)):
    """Principled with ambientCG Color/Normal/Roughness images (exportable to glTF)."""
    m = bpy.data.materials.new(name)
    if not m.node_tree:
        m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    d = os.path.join(ASSETS, stem)
    def img(kind, non_color):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(os.path.join(d, f"{stem}_1K-JPG_{kind}.jpg"))
        if non_color:
            n.image.colorspace_settings.name = "Non-Color"
        return n
    c = img("Color", False)
    if oscurecer != 1.0 or tinte != (1, 1, 1):
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(c.outputs["Color"], mix.inputs[6])
        mix.inputs[7].default_value = (tinte[0] * oscurecer, tinte[1] * oscurecer, tinte[2] * oscurecer, 1)
        nt.links.new(mix.outputs[2], p.inputs["Base Color"])
    else:
        nt.links.new(c.outputs["Color"], p.inputs["Base Color"])
    r = img("Roughness", True)
    nt.links.new(r.outputs["Color"], p.inputs["Roughness"])
    nm = nt.nodes.new("ShaderNodeNormalMap")
    n = img("NormalGL", True)
    nt.links.new(n.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], p.inputs["Normal"])
    return m


# ---------------------------------------------------------------- truck

G63 = os.path.join(ASSETS, "g63-6x6", "modelo", "scene.gltf")  # Brabus G63 6x6, CC-BY (see g63-6x6/modelo/license.txt)
# The model's materials (flat colours, no textures) -> ours. Unlisted ones keep the model's own material.
REPINTAR = {"Body_Col": "pintura", "Second_Body_Col": "pintura_satin", "extra_details_carcoal": "plastico",
            "Color_001": "rin", "Color_006": "cromo", "Color_009": "plastico", "tire": "goma", "Material__438": "plastico",
            "Material__445": "cromo", "Material__452": "cromo", "Material__507": "cromo", "Material__526": "vidrio",
            "Material__470": "mica", "Material__544": "calaveras", "Material__463": "piel_roja", "Material__464": "piel_vino",
            "Material__469": "amortiguador", "Color_A16": "piel_vino"}


def islas(me):
    """Connected pieces of a mesh: a list of polygon-index lists."""
    por_vert = [[] for _ in me.vertices]
    for p in me.polygons:
        for v in p.vertices:
            por_vert[v].append(p.index)
    visto, out = bytearray(len(me.polygons)), []
    for p0 in range(len(me.polygons)):
        if visto[p0]:
            continue
        visto[p0] = 1
        pila, isla = [p0], []
        while pila:
            i = pila.pop()
            isla.append(i)
            for v in me.polygons[i].vertices:
                for j in por_vert[v]:
                    if not visto[j]:
                        visto[j] = 1
                        pila.append(j)
        out.append(isla)
    return out


# ---------------------------------------------------------------- cab interior (audit 2026-11-18, defects 1, 7, 9)
# The model paints the whole cab with Second_Body_Col, the body's satin: roof, seat backs, dash and console read as painted
# plastic. Each of its loose parts inside the cab gets a material by zone (refs r01-r04: black nappa, carbon on the centre stack,
# brushed aluminium on the wheel's spokes, a charcoal headliner); parts outside the cab keep the satin paint. The model has no
# UVs: a box projection in metres is written into a UV map for those faces, so the same textures reach Cycles and the live GLB.
CABINA_TEX = os.path.join(REPO, "blender", "texturas", "cabina")  # blender/texturas_escena.py makes them
CABINA_TECHO = os.environ.get("CABINA_TECHO", "alcantara")  # "alcantara_clara": the reference's light grey headliner
CABINA_MATS = {  # material: (texture set, tile m, metallic, coat)
    "cab_piel": ("piel", 0.35, 0.0, 0.0), "cab_techo": (CABINA_TECHO, 0.40, 0.0, 0.0),
    "cab_carbono": ("carbono", 0.12, 0.0, 1.0), "cab_aluminio": ("aluminio", 0.30, 1.0, 0.0),
    "cab_alfombra": ("alcantara", 0.25, 0.0, 0.0)}  # the charcoal suede scan reads as the floor's carpet
VOLANTE = (-0.382, 0.93, 1.56)  # wheel centre from the lane's centre line (transicion's hands at ten and two: x -0.39, y 0.95, z 1.6)


def cab_mat(nombre):
    tex, tile, metal, coat = CABINA_MATS[nombre]
    return mat_tex(nombre, CABINA_TEX, tex, metal, coat)


def mat_tex(nombre, carpeta, tex, metal=0.0, coat=0.0, normal=True):
    """Principled from blender/texturas/<group>/<tex>_{color,rough,nor}.jpg on the mesh's UVs."""
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = 0.03

    def img(kind, dato):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(os.path.join(carpeta, f"{tex}_{kind}.jpg"), check_existing=True)
        if dato:
            n.image.colorspace_settings.name = "Non-Color"
        return n
    nt.links.new(img("color", False).outputs["Color"], p.inputs["Base Color"])
    nt.links.new(img("rough", True).outputs["Color"], p.inputs["Roughness"])
    if normal:
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = 0.6
        nt.links.new(img("nor", True).outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], p.inputs["Normal"])
    return m


def pintura_negra():
    """Body paint (defect 15: it read flat grey under the sodium light): a darker base under a glossy clear coat (coat 1.0,
    rough 0.03) whose normal carries a faint orange peel (noise, ~3 mm cells), so the coat breaks the lamps' reflections up
    the way real paint does. Was mat("pintura", (0.012, 0.012, 0.014), 0.3, metal=0.2, coat=1.0)."""
    m = mat("pintura", (0.006, 0.006, 0.007), 0.35, metal=0.2, coat=1.0)
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Coat Roughness"].default_value = 0.03
    tc = nt.nodes.new("ShaderNodeTexCoord")
    ru = nt.nodes.new("ShaderNodeTexNoise")
    ru.inputs["Scale"].default_value = 300.0
    ru.inputs["Detail"].default_value = 2.0
    nt.links.new(tc.outputs["Object"], ru.inputs["Vector"])
    bu = nt.nodes.new("ShaderNodeBump")
    bu.inputs["Strength"].default_value = 0.04
    bu.inputs["Distance"].default_value = 0.0003
    nt.links.new(ru.outputs["Fac"], bu.inputs["Height"])
    nt.links.new(bu.outputs["Normal"], p.inputs["Coat Normal"])
    return m


def zona_cabina(c, d):
    """Material for one loose part of Second_Body_Col, from its box centre c and size d (world m), or None (stays body paint)."""
    dx, cx = c.x - MUNDO["carril_x"], MUNDO["carril_x"]
    if abs(dx) > 0.81 or not (-1.13 < c.y < 1.42 and 0.85 < c.z < 2.26) or (c.z > 1.9 and c.y > 1.0):
        return None  # outside the cab (body sides, the roof visor and its lamp pockets ahead of the windshield top)
    if c.z > 1.98:
        return "cab_techo"
    if c.z < 1.15 and d.z < 0.1 and max(d.x, d.y) > 0.3:
        return "cab_alfombra"  # the floor pans
    v = Vector((cx + VOLANTE[0], VOLANTE[1], VOLANTE[2]))
    if (c - v).length < 0.21:
        return "cab_piel" if max(d) > 0.18 else "cab_aluminio"  # the rim's halves, else the spokes and the hub trim
    if c.y > 0.85 and abs(dx) < 0.22 and c.z < 1.62:
        return "cab_carbono"  # the centre stack (the dash top above it stays leather)
    return "cab_piel"


def cabina(o):
    """Split o (Second_Body_Col, already in world space) into the cab zones; writes a box-projected UV map in metres / tile."""
    me = o.data
    base = me.materials[0]
    idx = {}
    vs = me.vertices
    cuenta = {}
    for isla in islas(me):
        pts = [vs[v].co for p in isla for v in me.polygons[p].vertices]
        lo = Vector([min(q[i] for q in pts) for i in range(3)])
        hi = Vector([max(q[i] for q in pts) for i in range(3)])
        z = zona_cabina((lo + hi) / 2, hi - lo)
        if z is None:
            continue
        if z not in idx:
            me.materials.append(bpy.data.materials.get(z) or cab_mat(z))
            idx[z] = len(me.materials) - 1
        for p in isla:
            me.polygons[p].material_index = idx[z]
        cuenta[z] = cuenta.get(z, 0) + len(isla)
    uv = (me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")).data
    tiles = {i: CABINA_MATS[z][1] for z, i in idx.items()}
    for p in me.polygons:
        t = tiles.get(p.material_index)
        if t is None:
            continue
        n = p.normal
        ax = max(range(3), key=lambda k: abs(n[k]))
        u_, v_ = [(1, 2), (0, 2), (0, 1)][ax]
        for li in p.loop_indices:
            co = vs[me.loops[li].vertex_index].co
            uv[li].uv = (co[u_] / t, co[v_] / t)
    print("CABINA zonas", cuenta, "pintura_satin queda en", base.name)


def voltear_costados_caja(meshes):
    """The bed's upper side panels (plastico, |x - CX| 0.80-0.90, over the wheels) face into the bed; the r1 stickers ride on the
    right one's outside (owner 2026-11-18: "holes or white patches" on the right side of the bed). Turn them outward."""
    cx, n = MUNDO["carril_x"], 0
    for o in meshes:
        me = o.data
        voltear = [p for p in me.polygons
                   if 0.80 <= abs(p.center.x - cx) <= 0.90 and -2.9 < p.center.y < -1.1 and 1.15 < p.center.z < 1.5
                   and p.normal.x * math.copysign(1, p.center.x - cx) < -0.5]
        for p in voltear:
            p.flip()
        n += len(voltear)
    print("CAJA costados volteados", n)


def separar_ruedas(meshes):
    """The model merges its parts by material. Pull out every piece that lies inside a tyre's cylinder: one object per wheel."""
    import bmesh
    llantas = [o for o in meshes if o.data.materials[0].name == "goma"]
    vs = [v.co for o in llantas for v in o.data.vertices]
    radio = (max(v.z for v in vs) - min(v.z for v in vs)) / 2
    ys = sorted(v.y for v in vs)
    cortes = [(ys[i] + ys[i + 1]) / 2 for i in range(len(ys) - 1) if ys[i + 1] - ys[i] > 0.05]  # gaps between the axles
    cx = MUNDO["carril_x"]
    centros = []
    for lado in (-1, 1):
        for k in range(len(cortes) + 1):
            g = [v for v in vs if (v.x - cx) * lado > 0 and (k == 0 or v.y > cortes[k - 1]) and (k == len(cortes) or v.y < cortes[k])]
            centros.append(Vector(((min(v.x for v in g) + max(v.x for v in g)) / 2, (min(v.y for v in g) + max(v.y for v in g)) / 2, radio)))
    partes = [[] for _ in centros]
    for o in meshes:
        me = o.data
        if not me.polygons or min(v.co.z for v in me.vertices) > 2 * radio:
            continue
        de = {}
        for isla in islas(me):
            idx = {v for i in isla for v in me.polygons[i].vertices}
            for k, c in enumerate(centros):
                if all(abs(me.vertices[v].co.x - c.x) < 0.3 and (me.vertices[v].co.y - c.y) ** 2 + (me.vertices[v].co.z - c.z) ** 2 < (radio * 1.03) ** 2 for v in idx):
                    for i in isla:
                        de[i] = k
                    break
        if not de:
            continue
        for k in set(de.values()):
            bm = bmesh.new()
            bm.from_mesh(me)
            bm.faces.ensure_lookup_table()
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if de.get(f.index) != k], context="FACES")
            m2 = bpy.data.meshes.new(f"rueda{k}_{o.name}")
            bm.to_mesh(m2)
            bm.free()
            for m in me.materials:
                m2.materials.append(m)
            partes[k].append(m2)
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index in de], context="FACES")
        bm.to_mesh(me)
        bm.free()
    ruedas = []
    for k, (c, ms) in enumerate(zip(centros, partes)):
        obs = []
        for m2 in ms:
            m2.transform(Matrix.Translation(-c))
            ob = bpy.data.objects.new(f"rueda{k}", m2)
            ob.location = c
            bpy.context.scene.collection.objects.link(ob)
            obs.append(ob)
        bpy.ops.object.select_all(action="DESELECT")
        for ob in obs:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = obs[0]
        bpy.ops.object.join()
        ruedas.append(obs[0])
    return ruedas, radio


def camion():
    bpy.ops.import_scene.gltf(filepath=G63)
    imported = list(bpy.context.selected_objects)
    meshes = [o for o in imported if o.type == "MESH" and o.data.polygons]
    for o in meshes:  # bake the importer's hierarchy into the mesh data
        mw = o.matrix_world.copy()
        o.parent = None
        o.data.transform(mw)
        o.matrix_world = Matrix.Identity(4)
    for o in imported:
        if o not in meshes:
            bpy.data.objects.remove(o)
    pts = [v.co for o in meshes for v in o.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    f = MUNDO["largo_camion"] / (hi.y - lo.y)
    c = (lo + hi) / 2
    # the model's nose points -Y: turn it to +Y, scale to the real length, stand it on the road in its lane
    M = Matrix.Translation((MUNDO["carril_x"], 0, 0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Scale(f, 4) @ Matrix.Translation((-c.x, -c.y, -lo.z))
    pre = CFG["presets"]["noche"]
    mats = {
        "pintura": pintura_negra(),
        "pintura_satin": mat("pintura_satin", (0.014, 0.014, 0.016), 0.45, metal=0.2, coat=0.3),
        "plastico": mat("plastico", (0.02, 0.02, 0.021), 0.6),
        "rin": mat("rin", (0.03, 0.03, 0.032), 0.25, metal=1.0),
        "cromo": mat("cromo", (0.92, 0.92, 0.93), 0.12, metal=1.0),
        "goma": mat("goma", (0.018, 0.018, 0.018), 0.85),
        "piel_roja": mat("piel_roja", lin("#7a0f12"), 0.45),
        "piel_vino": mat("piel_vino", lin("#3d0709"), 0.5),
        "amortiguador": mat("amortiguador", lin("#b8860b"), 0.4, metal=0.6),
        "calaveras": mat("calaveras", (0.6, 0.02, 0.01), 0.3, emit=lin(pre["calaveras"]["color"]), estr=4.0),
        "faros": mat("faros", (1, 0.95, 0.85), 0.2, emit=(1.0, 0.9, 0.72), estr=6.0),
    }
    for nombre, tinte, rough in (("vidrio", (0.75, 0.8, 0.82), 0.0), ("mica", (1, 1, 1), 0.05)):
        m = mat(nombre, tinte, rough)  # lightly tinted glass: the cast has to be seen through it
        m.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 1.0
        mats[nombre] = m
    for o in meshes:
        o.data.transform(M)
        viejo = o.data.materials[0].name.split(".")[0]
        if viejo == "Light_Col":  # one material for every lamp, split by where it sits (owner 2026-11-18: every G63 lamp lit, at its
            # real position; until then all but the headlights were chrome, and the chrome over the tail clusters hid their red)
            G = luces_g63._mats()
            lamparas = [mats["faros"],   # nose: headlight projectors, the LED strip under each, the bumper lamps (ruta.py's flash keys it)
                        mats["calaveras"],  # tail clusters: 6 mm behind the calaveras lens, which hides them (its red carries)
                        mats["plastico"],  # roof: the pockets' back; props_placement.barra_luces puts the lit lamp in front
                        G["g63_ambar"]]  # what is left: the mirror turn signals
            o.data.materials[0] = lamparas[0]
            for m_ in lamparas[1:]:
                o.data.materials.append(m_)
            L2 = MUNDO["largo_camion"] / 2
            for p in o.data.polygons:
                c_ = p.center
                p.material_index = (0 if c_.y > L2 - 0.5 and c_.z < 1.5 else 1 if c_.y < -L2 + 0.5 else 2 if c_.z > 2.0 else 3)
        elif viejo in REPINTAR:
            o.data.materials[0] = mats[REPINTAR[viejo]]
            if viejo == "Second_Body_Col":
                cabina(o)
    voltear_costados_caja(meshes)
    ruedas, radio = separar_ruedas(meshes)
    camion_e = bpy.data.objects.new("camion", None)
    bpy.context.scene.collection.objects.link(camion_e)
    for o in [*meshes, *ruedas]:
        o.parent = camion_e
    luces_g63.malla(camion_e, MUNDO["carril_x"])  # every lamp's lens at its real position (blender/luces_g63.py)
    parrilla_g63.parrilla(camion_e, MUNDO["carril_x"])  # the AMG 6x6 grille over the model's Brabus one (blender/parrilla_g63.py)
    body = max(meshes, key=lambda o: len(o.data.polygons))
    print("RADIO", radio, "RUEDAS", [(round(r.location.x, 2), round(r.location.y, 2)) for r in ruedas])
    return camion_e, body, ruedas, radio


# ---------------------------------------------------------------- road, props, hills

MUNDO_TEX = os.path.join(REPO, "blender", "texturas", "mundo")  # blender/texturas_escena.py makes them
W_ALTO, W_FONDO, W_CHAPA = 0.31, 0.083, 0.003  # W-beam guardrail: 310 mm tall, two ridges 83 mm deep, 3 mm sheet (AASHTO M180)
W_X = lambda z, x_atras=5.03, zc=0.62: x_atras - W_FONDO * 0.5 * (1 - math.cos(4 * math.pi * ((z - zc) / W_ALTO + 0.5)))


def riel_w(nombre, x_atras, zc, m, n=32):
    """Defect 22 (the rail was a plain 6 cm box): the W-beam's cross-section in x-z, two ridges toward the road (-x), a 3 mm
    sheet, extruded the tramo's length; UVs in metres (u along the road / 2 m, v down the profile / 0.5 m) for the zinc scan."""
    import bmesh
    zs = [zc - W_ALTO / 2 + W_ALTO * k / n for k in range(n + 1)]
    perfil = [(W_X(z, x_atras, zc), z) for z in zs] + [(W_X(z, x_atras, zc) + W_CHAPA, z) for z in reversed(zs)]
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    a = [bm.verts.new((x, 0.0, z)) for x, z in perfil]
    b = [bm.verts.new((x, float(TRAMO), z)) for x, z in perfil]
    largo = [0.0]
    for (x0, z0), (x1, z1) in zip(perfil, perfil[1:] + perfil[:1]):
        largo.append(largo[-1] + math.hypot(x1 - x0, z1 - z0))
    k = len(perfil)
    for i in range(k):
        j = (i + 1) % k
        f = bm.faces.new((a[i], a[j], b[j], b[i]))
        for lp, (u, v) in zip(f.loops, ((0, largo[i]), (0, largo[i + 1]), (TRAMO, largo[i + 1]), (TRAMO, largo[i]))):
            lp[uv].uv = (u / 2.0, v / 0.5)
        f.smooth = True
    bm.faces.new(a[::-1]); bm.faces.new(b)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me); bm.free()
    me.materials.append(m)
    o = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(o)
    return o


def tramo_props():
    """One `tramo` of roadside props at y in [0, TRAMO). Exported once, recycled on the page."""
    col = bpy.data.collections.new("tramo")
    bpy.context.scene.collection.children.link(col)
    galv = mat("galvanizado", (0.55, 0.56, 0.58), 0.38, metal=1.0)
    blanco = mat("poste_blanco", (0.7, 0.7, 0.68), 0.6)
    lampara = mat("lampara", (1, 0.8, 0.5), 0.3, emit=lin(CFG["presets"]["noche"]["postes"]["color"]), estr=6.0)
    refl = mat("reflejante", (0.5, 0.03, 0.02), 0.3, emit=lin(CFG["presets"]["noche"]["fantasmas"]["color"]), estr=0.8)
    objs = []
    # light pole, right shoulder
    objs.append(cil("poste", 0.11, 9.0, (6.4, 8, 4.5), galv, verts=64))  # 64 sides: ≥ 1 tri per px at scene 2's 184 px
    for p in objs[-1].data.polygons:
        p.use_smooth = p.loop_total == 4  # round sides, flat caps
    objs.append(cil("brazo", 0.06, 2.6, (5.15, 8, 8.95), galv, rot=(0, math.pi / 2, 0)))
    objs.append(caja("lampara", (0.75, 0.32, 0.14), (3.95, 8, 8.9), lampara))
    # guardrail, right side: a continuous beam and a post every 4 m
    objs.append(riel_w("riel", 5.03, 0.62, mat_tex("galvanizado_riel", MUNDO_TEX, "galvanizado", metal=1.0, normal=False)))
    for i in range(TRAMO // 4):
        objs.append(caja(f"poste_riel_{i}", (0.14, 0.14, 0.8), (5.1, i * 4 + 2, 0.4), galv))
    # delineators ("fantasmas"), left shoulder every 16 m, with a red reflector
    for i in range(TRAMO // 16):
        objs.append(caja(f"fantasma_{i}", (0.12, 0.12, 1.05), (-4.7, i * 16 + 6, 0.52), blanco))
        objs.append(caja(f"reflejante_{i}", (0.13, 0.03, 0.18), (-4.7, i * 16 + 6 - 0.06, 0.88), refl))
    for i in range(TRAMO // 16):  # reflectors on the guardrail, on the upper ridge's crest
        objs.append(caja(f"reflejante_riel_{i}", (0.012, 0.12, 0.05), (W_X(0.62 + 0.0775) - 0.0055, i * 16 + 2, 0.62 + 0.0775), refl))
    for o in objs:
        for c in o.users_collection:
            c.objects.unlink(o)
        col.objects.link(o)
    luz = bpy.data.lights.new("luz_poste", "SPOT")
    luz.spot_size = math.radians(120)
    luz.spot_blend = 0.6
    luz.color = lin(CFG["presets"]["noche"]["postes"]["color"])
    lo = bpy.data.objects.new("luz_poste", luz)
    lo.location = (3.95, 8, 8.75)
    col.objects.link(lo)
    return col, objs, lo


def cerros():
    """A ring of low hills far away: silhouette against the sky. Static (at infinity parallax is nil)."""
    import bmesh
    bm = bmesh.new()
    n, rings = 180, 4
    radios = [700, 820, 950, 1100]
    verts = []
    for j, rr in enumerate(radios):
        fila = []
        for i in range(n):
            a = 2 * math.pi * i / n
            h = 0 if j in (0, rings - 1) else (38 + 26 * math.sin(3 * a + 1.3) + 18 * math.sin(7 * a + 0.4) + 9 * math.sin(17 * a + 2.1)) * (1.0 if j == 1 else 0.75)
            fila.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, max(h, 0) - 2)))
        verts.append(fila)
    for j in range(rings - 1):
        for i in range(n):
            bm.faces.new((verts[j][i], verts[j][(i + 1) % n], verts[j + 1][(i + 1) % n], verts[j + 1][i]))
    uv = bm.loops.layers.uv.new("UVMap")  # defect 21 (a flat grey band): the scrub scan, planar in x-y, one tile every 60 m
    for f in bm.faces:
        for lp in f.loops:
            lp[uv].uv = (lp.vert.co.x / 60.0, lp.vert.co.y / 60.0)
    me = bpy.data.meshes.new("cerros")
    bm.to_mesh(me)
    o = bpy.data.objects.new("cerros", me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat_tex("cerro", MUNDO_TEX, "cerro"))  # was mat("cerro", (0.012, 0.011, 0.01), 0.95)
    return o


# ---------------------------------------------------------------- build

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    cam_e, body, ruedas, radio = camion()
    col, props, luz_poste = tramo_props()
    hills = cerros()
    return dict(camion=cam_e, body=body, ruedas=ruedas, radio=radio, tramo=col, props=props, luz_poste=luz_poste, cerros=hills)


def exportar_glb(s):
    out = os.path.join(REPO, "public", "escena", "escena.glb")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for o in [s["camion"], s["body"], *s["ruedas"], *s["props"], s["cerros"]]:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_apply=True,
                              export_yup=True, export_lights=False, export_cameras=False,
                              export_draco_mesh_compression_enable=False)
    print("GLB", out, os.path.getsize(out))


def mundo_render(s, preset):
    """Road, ground, instances of the tramo, lights, world; animated over one loop."""
    sc = bpy.context.scene
    P = CFG["presets"][preset]
    largo_total = 760 + 192 * max(0, int(os.environ.get("RUTA_PERIODOS", "4")) - 4)  # ruta.py's long run: the road ahead, in loop periods
    mundo = bpy.data.objects.new("mundo", None)
    sc.collection.objects.link(mundo)
    losa = MUNDO["losa"]
    if "cycles" not in P:  # presets with a `cycles` block get blender/mundo.py's world at the end instead
        road = plano("carretera", 8.0, largo_total, -120, 0.015, tex_mat("asfalto_carril", "Road007"), 8.0)
        ground = plano("terreno", 3000, largo_total + 1400, -820, 0.0, tex_mat("terreno", "Asphalt031", oscurecer=0.22, tinte=(1.0, 0.86, 0.72)), 4.0)
        road.parent = mundo; ground.parent = mundo
    # instances of the tramo every TRAMO m, enough to cover the view during the whole loop
    for k in range(-2, (largo_total - 120) // TRAMO):
        inst = bpy.data.objects.new(f"tramo_{k}", None)
        inst.instance_type = "COLLECTION"
        inst.instance_collection = s["tramo"]
        inst.location = (0, k * TRAMO, 0)
        inst.parent = mundo
        sc.collection.objects.link(inst)
    sc.view_layers[0].layer_collection.children["tramo"].exclude = True
    # lights from the preset
    s["luz_poste"].data.energy = W_POSTE * P["postes"]["intensidad"]
    if not P["postes"]["encendidos"]:
        for m in ("lampara",):
            bpy.data.materials[m].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.0
    sol = bpy.data.lights.new("luna", "SUN")
    sol.energy = P["luna"]["intensidad"]
    sol.color = lin(P["luna"]["color"])
    sol.angle = math.radians(1.5)
    so = bpy.data.objects.new("luna", sol)
    so.rotation_euler = (-b(P["luna"]["dir"])).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(so)
    for (fx, _fy, fz), lado in zip(luces_g63.FAROS, (-1, 1)):  # on the headlight centres (were CX +-0.78, z 1.15: off the lamps)
        sp = bpy.data.lights.new(f"faro_{lado}", "SPOT")
        sp.energy = W_FARO * P["faros"]["intensidad"]
        sp.color = lin(P["faros"]["color"])
        sp.spot_size = math.radians(55)
        sp.spot_blend = 0.5
        sp.shadow_soft_size = 0.08
        o = bpy.data.objects.new(f"faro_{lado}", sp)
        o.location = (fx, MUNDO["largo_camion"] / 2 + 0.05, fz)
        o.rotation_euler = Vector((0, 1, -0.06)).to_track_quat("-Z", "Y").to_euler()
        o.parent = s["camion"]
        sc.collection.objects.link(o)
    # no tail point light: the calaveras lenses carry the red. A red point behind each cluster washed them pink (top-20 % chroma
    # 87 -> 71, ~/cc-out/mto-asset-fixes/luces/cola/), and the old mid-tail one showed as a glare dot on the tailgate
    luces_g63.luces_interior(s["camion"], MUNDO["carril_x"])  # reading lamps, dome, dash glow
    # world HDRI
    w = bpy.data.worlds.new("cielo")
    sc.world = w
    if not w.node_tree:
        w.use_nodes = True
    nt = w.node_tree
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(ASSETS, f"{P['hdri']}_2k.hdr"))
    bg = nt.nodes.get("Background") or nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = P["cielo_intensidad"]
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_WORLD")
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    if "cycles" in P:  # Night B (owner's pick 2026-11-14): road, verges, plants, pole line, fog, sky
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import mundo as mundo_b
        s["mundo_b"] = mundo_b.construir(mundo, P["cycles"], P, RECORRIDO, s["props"][:3] + [s["luz_poste"]])
    # animation: world moves -Y by RECORRIDO over NFR frames; wheels turn a whole number of times
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 0, NFR - 1
    def lineal(ob, path, idx, v0, v1):
        ob.keyframe_insert(path, index=idx, frame=0)
        fc = ob.animation_data.action
        setattr_path(ob, path, idx, v1)
        ob.keyframe_insert(path, index=idx, frame=NFR)
        setattr_path(ob, path, idx, v0)
    def setattr_path(ob, path, idx, v):
        getattr(ob, path)[idx] = v
    mundo.location.y = 0
    lineal(mundo, "location", 1, 0.0, -float(RECORRIDO))
    vueltas = round(RECORRIDO / (2 * math.pi * s["radio"]))
    print("VUELTAS", vueltas, "radio", s["radio"])
    for r in s["ruedas"]:
        r.rotation_euler.x = 0
        lineal(r, "rotation_euler", 0, 0.0, -2 * math.pi * vueltas)
    for ob in [mundo, *s["ruedas"]]:
        for fc in iter_fcurves(ob):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
            fc.extrapolation = "LINEAR"


def iter_fcurves(ob):
    act = ob.animation_data.action
    try:
        return list(act.fcurves)
    except AttributeError:  # Blender 5 layered actions
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    out.extend(bag.fcurves)
        return out


def camara(parada, w, h):
    sc = bpy.context.scene
    st = next(p for p in CFG["paradas"] if p["id"] == parada)
    cd = bpy.data.cameras.new("cam")
    cd.sensor_fit = "VERTICAL"
    asp = w / h
    vfov = math.radians(st["fov"])
    if asp < 1:  # same rule as the page: hold the horizontal angle of a square frame
        vfov = 2 * math.atan(math.tan(vfov / 2) / asp)
    cd.angle_y = vfov
    cd.clip_end = 3000
    co = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(co)
    co.location = b(st["pos"])
    co.rotation_euler = (b(st["mira"]) - b(st["pos"])).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100


def motor(samples, preset):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == "OPTIX"
    sc.cycles.device = "GPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = math.log2(CFG["presets"][preset]["exposicion"])
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.5  # 180 degrees
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "8"


FORMATOS = ((720, 1280), (1600, 900))  # vertical first: it is the phone's entry


def tanda(s, modo, out, samples):
    """hoja: frame 0 of every stop in both formats, for approval. lote: the whole loop of every stop, built once.
    Output: <out>/<nn>-<stop>-noche-<WxH>/f_0000.png ... (hoja: <out>/<nn>-<stop>-noche-<WxH>.png)."""
    sc = bpy.context.scene
    mundo_render(s, "noche")
    motor(samples, "noche")
    for w, h in FORMATOS:
        for i, st in enumerate(CFG["paradas"]):
            camara(st["id"], w, h)
            nombre = f"{i + 1:02d}-{st['id']}-noche-{w}x{h}"
            if modo == "hoja":
                sc.frame_set(0)
                sc.render.filepath = os.path.join(out, nombre + ".png")
                bpy.ops.render.render(write_still=True)
            else:
                sc.frame_start, sc.frame_end = 0, NFR - 1
                sc.render.filepath = os.path.join(out, nombre, "f_####")
                bpy.ops.render.render(animation=True)
            print("TOMA", nombre)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["glb"]
    s = build()
    if argv[0] == "glb":
        exportar_glb(s)
        return
    if argv[0] in ("hoja", "lote"):
        tanda(s, argv[0], argv[1], int(argv[2]) if len(argv) > 2 else (16 if argv[0] == "hoja" else 64))
        return
    if argv[0] == "transicion":  # the inside -> outside move; frames to <out_dir>/f_####.png
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import transicion
        mundo_render(s, "noche")
        motor(int(argv[4]) if len(argv) > 4 else 16, "noche")
        transicion.preparar(s, int(argv[2]), int(argv[3]), islas)
        sc = bpy.context.scene
        sc.frame_start = int(argv[5]) if len(argv) > 5 else 0
        sc.frame_end = int(argv[6]) if len(argv) > 6 else transicion.NFR - 1
        sc.frame_step = int(argv[7]) if len(argv) > 7 else 1
        sc.render.filepath = os.path.join(argv[1], "f_####")
        bpy.ops.render.render(animation=True)
        return
    preset, parada, w, h, out = argv[1], argv[2], int(argv[3]), int(argv[4]), argv[5]
    samples = int(argv[6]) if len(argv) > 6 else 64
    mundo_render(s, preset)
    camara(parada, w, h)
    motor(samples, preset)
    sc = bpy.context.scene
    if argv[0] == "still":
        sc.frame_set(0)
        sc.render.filepath = out
        bpy.ops.render.render(write_still=True)
    else:
        sc.frame_start = int(argv[7]) if len(argv) > 7 else 0
        sc.frame_end = int(argv[8]) if len(argv) > 8 else NFR - 1
        sc.render.filepath = os.path.join(out, "f_####")
        bpy.ops.render.render(animation=True)


main()
