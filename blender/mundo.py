"""The world around the truck in direction Night B (owner's pick 2026-11-14 19:13): a humid Gulf lowland under mist.

Ported from the world audit (~/cc-out/mto-world/plan.md, fixes.py variant B) into the repo's scene code: escena.py's
mundo_render() calls construir() for the Cycles render, so every scene script (utileria, caja3, props_placement,
storyboard, transicion) gets this world. The GLB export (build()) does not build it.

Reference: R1 (MEX 180 Veracruz: plants up to the asphalt, a pole line on the verge), R2 (far trees as one band of crowns),
R3 (patched, worn asphalt), F2 (Collateral 022: lamp halos in haze, a warm-grey sky floor), F3 (Sicario 032: detail only in
the light pools). Rows in docs/design/references.md › World, Night B.

Loop rule (escena.py): the world moves RECORRIDO m per loop and frame NFR == frame 0, so every piece repeats in RECORRIDO:
the plant scatters are one RECORRIDO tile copied along y, the road's procedural wear reads y wrapped on a circle of that
circumference, and the markings, studs and poles have periods that divide it.

Ray casts: utileria/props_placement place props and measure their rules with viewport ray casts. The pieces that were not
in the old world (fog box, plants, poles, markings) are hidden from the viewport (hide_viewport) so those numbers do not
move; Cycles still renders them. The road, shoulders and ground stay visible: they replace the old road and ground planes.

Assets: Poly Haven, CC0 (docs/licencias/mundo-polyhaven.md), kept outside the repo in ASSETS_MUNDO.
"""
import bpy, bmesh, math, os, random
import numpy as np
from mathutils import Vector, Matrix

ASSETS_MUNDO = r"\\wsl.localhost\Ubuntu\home\black\cc-out\mto-world\assets\polyhaven-2026-11-14"
X_LINEA = 3.55   # lane 0..3.5 m holds the truck (centre 1.72); the edge lines sit just outside
TENDIDO = dict(x=-9.0, fase=36.0, alto=11.0)  # CFE pole line (R1): x, y of the first pole mod PASO_POSTES, height
# fase 36 = the audit stills the owner picked from; at 0 a pole rose out of the bed in hold 4. Owner 00:32: placement good
PASO_POSTES = 64.0   # owner 00:32 "one fewer pole and one fewer light": 3 per 192 m loop instead of 4 (was 48 m)
PASO_FAROLAS = 64.0  # the road lamps leave the 48 m tramo for the Cycles render; the page keeps its 48 m tramo
ASFALTO = dict(tinte=0.62, rough_rodada=0.6)  # the glossy wheel paths (0.42) clipped scene 6's headlight pool 0.61 %, not the
# tint: 0.62 with matte paths clips 0.00 % and keeps the floor detail that the it4 tint 0.5 lost (docs/mundo-noche-b.md)


def _sc():
    return bpy.context.scene


def mat_color(nombre, color, rough=0.6):
    m = bpy.data.materials.new(nombre)
    if not m.node_tree:
        m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    return m


def _imagen(nt, ruta, non_color, coord, escala):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(ruta, check_existing=True)
    if non_color:
        n.image.colorspace_settings.name = "Non-Color"
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / escala,) * 3
    nt.links.new(coord, mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
    return n


def mat_textura(nombre, stem, escala, tinte, extra=None):
    """Poly Haven diff/rough/nor_gl at `escala` m per tile in object coordinates (each piece moves with `mundo`).
    Every escala used here divides RECORRIDO, so the image repeats with the loop."""
    m = bpy.data.materials.new(nombre)
    if not m.node_tree:
        m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    co = nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]
    d = os.path.join(ASSETS_MUNDO, stem)
    c = _imagen(nt, os.path.join(d, f"{stem}_diff_1k.jpg"), False, co, escala)
    r = _imagen(nt, os.path.join(d, f"{stem}_rough_1k.jpg"), True, co, escala)
    n = _imagen(nt, os.path.join(d, f"{stem}_nor_gl_1k.jpg"), True, co, escala)
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.name = "tinte"
    mix.inputs["Factor"].default_value = 1.0
    mix.inputs[7].default_value = (*tinte, 1)
    nt.links.new(c.outputs["Color"], mix.inputs[6])
    color, rough = mix.outputs[2], r.outputs["Color"]
    if extra:
        color, rough = extra(nt, co, color, rough)
    nt.links.new(color, p.inputs["Base Color"])
    nt.links.new(rough, p.inputs["Roughness"])
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(n.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], p.inputs["Normal"])
    return m


# ---------------------------------------------------------------- road: surface, wear, markings, shoulders

def _ciclico(nt, co, periodo):
    """(x, R cos 2πy/P, R sin 2πy/P) with R = P/2π: 3D noise read through it repeats every P m along y, same scale."""
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(co, sep.inputs["Vector"])
    th = nt.nodes.new("ShaderNodeMath"); th.operation = "MULTIPLY"; th.inputs[1].default_value = 2 * math.pi / periodo
    nt.links.new(sep.outputs["Y"], th.inputs[0])
    R = periodo / (2 * math.pi)
    out = []
    for op in ("COSINE", "SINE"):
        t = nt.nodes.new("ShaderNodeMath"); t.operation = op; nt.links.new(th.outputs[0], t.inputs[0])
        k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = R
        nt.links.new(t.outputs[0], k.inputs[0]); out.append(k.outputs[0])
    cb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(sep.outputs["X"], cb.inputs["X"]); nt.links.new(out[0], cb.inputs["Y"]); nt.links.new(out[1], cb.inputs["Z"])
    return sep, cb.outputs["Vector"]


def desgaste(periodo):
    """R3: wheel paths polished and darker, an oil band down each lane's centre, fresh-asphalt patches (7 m cells), cracks
    that come and go, and a 40 m macro variation that breaks the image tile. Road metres: x across, y along."""
    def _f(nt, co, color, rough):
        sep, cy = _ciclico(nt, co, periodo)
        def banda(centro, ancho):  # 1 inside |x - centro| < ancho/2, soft edges
            a = nt.nodes.new("ShaderNodeMath"); a.operation = "SUBTRACT"; a.inputs[1].default_value = centro
            nt.links.new(sep.outputs["X"], a.inputs[0])
            b = nt.nodes.new("ShaderNodeMath"); b.operation = "ABSOLUTE"; nt.links.new(a.outputs[0], b.inputs[0])
            c = nt.nodes.new("ShaderNodeMapRange"); c.inputs["From Min"].default_value = ancho / 2
            c.inputs["From Max"].default_value = ancho / 2 + 0.25
            c.inputs["To Min"].default_value = 1.0; c.inputs["To Max"].default_value = 0.0
            nt.links.new(b.outputs[0], c.inputs["Value"])
            return c.outputs["Result"]
        def maximo(a, b):
            s = nt.nodes.new("ShaderNodeMath"); s.operation = "MAXIMUM"; nt.links.new(a, s.inputs[0]); nt.links.new(b, s.inputs[1])
            return s.outputs[0]
        def rango(sock, lo, hi, invertir=False):
            r = nt.nodes.new("ShaderNodeMapRange"); r.inputs["From Min"].default_value = lo; r.inputs["From Max"].default_value = hi
            if invertir:
                r.inputs["To Min"].default_value = 1.0; r.inputs["To Max"].default_value = 0.0
            nt.links.new(sock, r.inputs["Value"])
            return r.outputs["Result"]
        rodada = None
        for lane in (1.75, -1.75):
            for k in (-0.85, 0.85):
                b = banda(lane + k, 0.55)
                rodada = b if rodada is None else maximo(rodada, b)
        aceite = maximo(banda(1.75, 0.5), banda(-1.75, 0.5))
        mac = nt.nodes.new("ShaderNodeTexNoise"); mac.inputs["Scale"].default_value = 1 / 40; mac.inputs["Detail"].default_value = 3
        nt.links.new(cy, mac.inputs["Vector"])
        vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 1 / 7.0
        nt.links.new(cy, vor.inputs["Vector"])
        parche = rango(vor.outputs["Color"], 0.86, 0.87)  # the cell's random colour as a per-cell value
        vg = nt.nodes.new("ShaderNodeTexVoronoi"); vg.feature = "DISTANCE_TO_EDGE"; vg.inputs["Scale"].default_value = 0.9
        nt.links.new(cy, vg.inputs["Vector"])
        mg = nt.nodes.new("ShaderNodeTexNoise"); mg.inputs["Scale"].default_value = 1 / 6
        nt.links.new(cy, mg.inputs["Vector"])
        grieta = nt.nodes.new("ShaderNodeMath"); grieta.operation = "MULTIPLY"
        nt.links.new(rango(vg.outputs["Distance"], 0.012, 0.03, True), grieta.inputs[0])
        nt.links.new(rango(mg.outputs["Fac"], 0.62, 0.68), grieta.inputs[1])
        def oscurece(c, mask, f):
            m = nt.nodes.new("ShaderNodeMix"); m.data_type = "RGBA"; m.blend_type = "MULTIPLY"
            nt.links.new(mask, m.inputs["Factor"]); nt.links.new(c, m.inputs[6]); m.inputs[7].default_value = (f, f, f, 1)
            return m.outputs[2]
        color = oscurece(color, rango(mac.outputs["Fac"], 0.35, 0.65), 0.8)
        color = oscurece(color, rodada, 0.78)
        color = oscurece(color, aceite, 0.7)
        color = oscurece(color, parche, 0.55)
        color = oscurece(color, grieta.outputs[0], 0.35)
        def baja(r, mask, v, nombre):
            m = nt.nodes.new("ShaderNodeMix"); m.data_type = "FLOAT"; m.name = nombre
            nt.links.new(mask, m.inputs["Factor"]); nt.links.new(r, m.inputs[2]); m.inputs[3].default_value = v
            return m.outputs[0]
        rough = baja(rough, rodada, ASFALTO["rough_rodada"], "rough_rodada")
        rough = baja(rough, parche, 0.5, "rough_parche")
        return color, rough
    return _f


def _plano(nombre, x0, x1, y0, y1, z, m, padre):
    me = bpy.data.meshes.new(nombre)
    me.from_pydata([(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], [], [(0, 1, 2, 3)])
    o = bpy.data.objects.new(nombre, me)
    o.location = (0, 0, z)
    o.data.materials.append(m)
    _sc().collection.objects.link(o)
    o.parent = padre
    return o


def _cajas(nombre, centros, tam, m, padre, z=0.0):
    bm = bmesh.new()
    for c in centros:
        bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation(c) @ Matrix.Diagonal((*tam, 1)))
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nombre, me); o.location = (0, 0, z); o.data.materials.append(m)
    _sc().collection.objects.link(o); o.parent = padre
    return o


def marcas(padre, y0, y1, periodo):
    """NOM-034-SCT2 as geometry (exports to glTF): M-3.1 right edge solid white, M-3.3 left edge solid yellow (median side of
    a divided autopista), M-2.3 lane line dashed 5 m / 10 m (table 5) fitted to the loop: 13 per period, 4.92 / 9.85 m.
    Studs (7.5.1, every 30 m) every period/6 = 32 m: white on the lane line and the right edge, amber on the left, a little
    emission standing in for retroreflection."""
    blanca = mat_color("w_pintura_blanca", (0.78, 0.78, 0.74), 0.5)
    amarilla = mat_color("w_pintura_amarilla", (0.8, 0.55, 0.06), 0.5)
    for m in (blanca, amarilla):  # worn paint: the asphalt shows through in patches
        nt = m.node_tree; p = nt.nodes["Principled BSDF"]
        co = nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]
        _, cy = _ciclico(nt, co, periodo)
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 6
        nt.links.new(cy, nz.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.3; mr.inputs["From Max"].default_value = 0.45
        nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
        mx.inputs[6].default_value = (0.06, 0.06, 0.06, 1); mx.inputs[7].default_value = p.inputs["Base Color"].default_value[:]
        nt.links.new(mr.outputs["Result"], mx.inputs["Factor"]); nt.links.new(mx.outputs[2], p.inputs["Base Color"])
    def tiras(nombre, rects, m):
        bm = bmesh.new()
        for a0, a1, b0, b1 in rects:
            bm.faces.new([bm.verts.new((a0, b0, 0)), bm.verts.new((a1, b0, 0)), bm.verts.new((a1, b1, 0)), bm.verts.new((a0, b1, 0))])
        me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(nombre, me); o.location = (0, 0, 0.019); o.data.materials.append(m)
        _sc().collection.objects.link(o); o.parent = padre
        return o
    paso = periodo / 13
    n = int(round((y1 - y0) / paso))
    out = [tiras("w_borde_der", [(X_LINEA - 0.075, X_LINEA + 0.075, y0, y1)], blanca),
           tiras("w_borde_izq", [(-X_LINEA - 0.075, -X_LINEA + 0.075, y0, y1)], amarilla),
           tiras("w_carril", [(-0.075, 0.075, y0 + k * paso, y0 + k * paso + paso / 3) for k in range(n)], blanca)]
    for nombre, x, color in (("w_boton_carril", 0.0, (1, 1, 0.95)), ("w_boton_der", X_LINEA, (1, 1, 0.95)),
                             ("w_boton_izq", -X_LINEA, (1, 0.62, 0.1))):
        m = mat_color(nombre, color, 0.3)
        p = m.node_tree.nodes["Principled BSDF"]
        p.inputs["Emission Color"].default_value = (*color, 1); p.inputs["Emission Strength"].default_value = 2.5
        ys = np.arange(y0 + paso * 0.66, y1, periodo / 6)
        out.append(_cajas(nombre, [(x, float(y), 0.012) for y in ys], (0.1, 0.1, 0.022), m, padre, 0.019))
    return out


def carretera(padre, y0, y1, periodo):
    """Plan fixes 3, 4, 7: worn asphalt (3 m tile), an older lighter shoulder to the guardrail, a gravel strip where the
    delineators stand. The old Road007 plane (markings painted in, white on both edges) is gone."""
    t = ASFALTO["tinte"]
    asf = mat_textura("w_asfalto", "asphalt_02", 3.0, (t, t, t + 0.02), extra=desgaste(periodo))
    hombro = mat_textura("w_acotamiento", "asphalt_02", 3.0, (0.75, 0.74, 0.72))  # older, lighter, no traffic wear
    grava = mat_textura("w_grava", "gravelly_sand", 1.5, (0.55, 0.52, 0.48))
    suelo = [_plano("w_carretera", -X_LINEA - 0.3, X_LINEA + 0.3, y0, y1, 0.016, asf, padre),
             _plano("w_acot_der", X_LINEA + 0.3, 4.95, y0, y1, 0.015, hombro, padre),
             _plano("w_acot_izq", -4.25, -X_LINEA - 0.3, y0, y1, 0.015, hombro, padre),
             _plano("w_grava_der", 4.95, 5.6, y0, y1, 0.012, grava, padre),
             _plano("w_grava_izq", -5.3, -4.25, y0, y1, 0.012, grava, padre)]
    return suelo, marcas(padre, y0, y1, periodo)


# ---------------------------------------------------------------- plants

def importar(stem, col):
    """Import a Poly Haven glTF; each variant (nodes at different offsets) becomes one object at the origin, in `col`."""
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ASSETS_MUNDO, stem, f"{stem}_1k.gltf"))
    nuevos = [o for o in bpy.data.objects if o not in antes]
    grupos = {}
    for o in nuevos:
        if o.type != "MESH":
            continue
        mw = o.matrix_world.copy()
        t = mw.translation.copy()
        o.parent = None
        o.data.transform(Matrix.Translation(-t) @ mw)
        o.matrix_world = Matrix.Identity(4)
        grupos.setdefault((round(t.x, 1), round(t.y, 1)), []).append(o)
    for o in nuevos:
        if o.type != "MESH":
            bpy.data.objects.remove(o)
    out = []
    for obs in grupos.values():
        bpy.ops.object.select_all(action="DESELECT")
        for o in obs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = obs[0]
        if len(obs) > 1:
            bpy.ops.object.join()
        o = bpy.context.view_layer.objects.active
        o.name = f"{stem}_{len(out)}"
        for k in list(o.users_collection):
            k.objects.unlink(o)
        col.objects.link(o)
        out.append(o)
    return out


def _col_oculta(nombre):
    sc = _sc()
    c = bpy.data.collections.new(nombre)
    sc.collection.children.link(c)
    sc.view_layers[0].layer_collection.children[nombre].exclude = True
    return c


def dispersar(nombre, col, x0, x1, densidad, esc, seed, padre, periodo, copias):
    """Geometry-nodes scatter on one strip y in [0, periodo) (local to `mundo`), copied at y = k·periodo for k in `copias`,
    so the layout repeats with the loop. Random pick, yaw, lean and scale; same seed, same layout."""
    me = bpy.data.meshes.new(nombre)
    me.from_pydata([(x0, 0, 0), (x1, 0, 0), (x1, periodo, 0), (x0, periodo, 0)], [], [(0, 1, 2, 3)])
    o = bpy.data.objects.new(nombre, me); _sc().collection.objects.link(o); o.parent = padre
    ng = bpy.data.node_groups.new(nombre, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; L = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    dist = N.new("GeometryNodeDistributePointsOnFaces")
    dist.inputs["Density"].default_value = densidad; dist.inputs["Seed"].default_value = seed
    ci = N.new("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = col
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    iop = N.new("GeometryNodeInstanceOnPoints"); iop.inputs["Pick Instance"].default_value = True
    def azar(tipo, lo, hi, sd):
        r = N.new("FunctionNodeRandomValue"); r.data_type = tipo
        t = {"INT": "INT", "FLOAT": "VALUE", "FLOAT_VECTOR": "VECTOR"}[tipo]
        [s for s in r.inputs if s.name == "Min" and s.type == t][0].default_value = lo
        [s for s in r.inputs if s.name == "Max" and s.type == t][0].default_value = hi
        r.inputs["Seed"].default_value = sd
        return [s for s in r.outputs if s.type == t][0]
    L.new(gi.outputs[0], dist.inputs["Mesh"])
    L.new(dist.outputs["Points"], iop.inputs["Points"])
    L.new(ci.outputs[0], iop.inputs["Instance"])
    L.new(azar("INT", 0, 99, seed + 1), iop.inputs["Instance Index"])
    L.new(azar("FLOAT_VECTOR", (0, 0, 0), (0.08, 0.08, 6.283), seed + 2), iop.inputs["Rotation"])
    L.new(azar("FLOAT", esc[0], esc[1], seed + 3), iop.inputs["Scale"])
    junta = N.new("GeometryNodeJoinGeometry")
    for k in copias:
        tr = N.new("GeometryNodeTransform"); tr.inputs["Translation"].default_value = (0, k * periodo, 0)
        L.new(iop.outputs[0], tr.inputs["Geometry"]); L.new(tr.outputs[0], junta.inputs[0])
    L.new(junta.outputs[0], go.inputs[0])
    mod = o.modifiers.new("scatter", "NODES"); mod.node_group = ng
    mod.show_viewport = False  # render only: every bpy.ops call while a hold builds would re-scatter (audit: 8 min a hold)
    return o


def copa_lejana():
    """Far tree mass (R2: the lowland's far trees are one band of crowns): 4-5 lumps, wider than tall, trunk hidden under
    them. Past ~40 m at night only the silhouette reads (F3)."""
    bm = bmesh.new()
    rnd = random.Random(7)
    for k in range(5):
        a = k * 2.4
        r = 0.55 + 0.35 * rnd.random()
        c = Vector((math.cos(a) * 0.7 * (k > 0), math.sin(a) * 0.7 * (k > 0), 1.25 + 0.35 * rnd.random()))
        g = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r, matrix=Matrix.Translation(c))
        for v in g["verts"]:
            d = v.co - c
            v.co = c + Vector((d.x * 1.25, d.y * 1.25, d.z * 0.8)) * (0.88 + 0.24 * rnd.random())
    bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.12, radius2=0.08, depth=1.2,
                          matrix=Matrix.Translation((0, 0, 0.6)))
    me = bpy.data.meshes.new("w_copa"); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat_color("w_copa_verde", (0.02, 0.035, 0.015), 0.85))
    return bpy.data.objects.new("w_copa", me)


def plantas(padre, periodo, copias):
    """Plan fixes 1, 2 (LoD rule, F3): hero plants within ~14 m and inside the light pools, crown silhouettes 22-260 m,
    nothing 260-700 m, the hills under fog beyond. First 3 m past the gravel mowed (SCT verge upkeep; keeps scene 4's
    camera, 6 m out, above the stalks), then guinea-grass height (the grass model ×2.2-4) to 14 m, sparser grass and
    shrubs (pachira, fern) to 40 m."""
    pasto, arbusto, copa = _col_oculta("w_pasto"), _col_oculta("w_arbusto"), _col_oculta("w_copa")
    for stem in ("grass_medium_02", "weed_plant_02"):
        importar(stem, pasto)
    for stem in ("shrub_02", "shrub_04", "pachira_aquatica_01", "fern_02"):
        importar(stem, arbusto)
    copa.objects.link(copa_lejana())
    out = []
    for lado, x_in in ((1, 5.6), (-1, 5.3)):
        s = 10 if lado > 0 else 20
        for nombre, col, a, b, dens, esc, sd in (
                ("corte", pasto, x_in, x_in + 3, 2.5, (0.8, 1.4), s + 8),
                ("pasto", pasto, x_in + 3, 14, 2.2, (2.2, 4.0), s),
                ("arbusto", arbusto, x_in + 1.5, 40, 0.06, (1.2, 2.6), s + 1),
                ("pasto_lejos", pasto, 14, 40, 0.5, (2.5, 4.0), s + 2),
                ("copa", copa, 22, 260, 0.006, (3.0, 6.5), s + 3)):
            out.append(dispersar(f"w_{nombre}{lado:+d}", col, lado * a, lado * b, dens, esc, sd, padre, periodo, copias))
    return out


# ---------------------------------------------------------------- power line, ground, fog, sky

def tendido(padre, y0, y1):
    """R1: CFE-style concrete poles every PASO_POSTES (divides the loop), a crossarm, three wires sagging 1.2 m per span.
    Position from TENDIDO (the owner places it: docs/mundo-noche-b.md › Placement)."""
    conc = mat_color("w_concreto", (0.32, 0.31, 0.29), 0.85)
    cable = mat_color("w_cable", (0.01, 0.01, 0.01), 0.4)
    X, H, fase = TENDIDO["x"], TENDIDO["alto"], TENDIDO["fase"] % PASO_POSTES
    ys = [float(y) for y in np.arange(y0 + fase, y1 + 1, PASO_POSTES)]
    bm = bmesh.new()
    for y in ys:
        cono = bmesh.ops.create_cone(bm, cap_ends=True, segments=64, radius1=0.2, radius2=0.11, depth=H,
                                     matrix=Matrix.Translation((X, y, H / 2)))  # 64 sides: revisar's detail gate wants ≥ 1 tri per px of the 232 px pole
        for f in {f for v in cono["verts"] for f in v.link_faces if len(f.verts) == 4}:
            f.smooth = True  # round sides, flat caps
        bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation((X, y, H - 0.5)) @ Matrix.Diagonal((2.4, 0.12, 0.12, 1)))
    me = bpy.data.meshes.new("w_postes"); bm.to_mesh(me); bm.free(); me.materials.append(conc)
    postes = bpy.data.objects.new("w_postes", me); _sc().collection.objects.link(postes); postes.parent = padre
    cu = bpy.data.curves.new("w_cables", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.012
    for dx in (-1.05, 0.0, 1.05):
        for ya, yb in zip(ys[:-1], ys[1:]):
            sp = cu.splines.new("POLY"); n = 12; sp.points.add(n - 1)
            for i in range(n):
                t = i / (n - 1)
                sp.points[i].co = (X + dx, ya + (yb - ya) * t, H - 0.38 - 1.2 * 4 * t * (1 - t), 1)
    cables = bpy.data.objects.new("w_cables", cu); cables.data.materials.append(cable)
    _sc().collection.objects.link(cables); cables.parent = padre
    return [postes, cables]


def farolas(farol, padre, y0, y1):
    """The tramo's lamp (pole, arm, lamp, its spot light) moved out of the 48 m tramo into its own collection, instanced
    every PASO_FAROLAS under `mundo`, at the same y within its period (8 m)."""
    col = _col_oculta("w_farola")
    for o in farol:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)
    out = []
    for y in np.arange(y0, y1, PASO_FAROLAS):
        e = bpy.data.objects.new(f"w_farola_{int(y)}", None)
        e.instance_type, e.instance_collection = "COLLECTION", col
        e.location = (0, float(y), 0)
        _sc().collection.objects.link(e); e.parent = padre
        out.append(e)
    return out


def niebla(cfg):
    """A fog box, not a world volume: the sky above 82 m stays clean. Cycles only (the page's FogExp2 is a different unit:
    blender-notas, "don't transfer volume values between engines")."""
    me = bpy.data.meshes.new("w_niebla")
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("w_niebla", me); _sc().collection.objects.link(o)
    o.location, o.scale = (0, 300, 40), (3000, 3000, 82)
    m = bpy.data.materials.new("w_niebla")
    if not m.node_tree:
        m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Density"].default_value = cfg["densidad"]
    pv.inputs["Color"].default_value = (*cfg["color"], 1)
    pv.inputs["Anisotropy"].default_value = cfg["anisotropia"]
    nt.links.new(pv.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Volume"])
    o.data.materials.append(m)
    o.visible_shadow = False
    _sc().cycles.volume_step_rate = 4.0
    return o


def cielo(world, ruta, fuerza, luna):
    """Plan fix 6: the world HDRI rotated about Z so its brightest point sits at the azimuth of the `luna` light."""
    img = bpy.data.images.load(ruta, check_existing=True)
    w, h = img.size
    px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px)
    lum = px.reshape(h, w, 4)[..., :3].sum(-1)
    j, i = np.unravel_index(int(lum.argmax()), lum.shape)
    az_hdri = ((i + 0.5) / w - 0.5) * 2 * math.pi     # Blender equirect: u = atan2(d.y, -d.x) / 2π + 0.5
    d = luna.matrix_world.to_quaternion() @ Vector((0, 0, 1))  # the light travels along -Z: the moon is at +Z
    giro = math.atan2(d.y, -d.x) - az_hdri
    nt = world.node_tree
    env = next(n for n in nt.nodes if n.type == "TEX_ENVIRONMENT")
    env.image = img
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, giro)
    nt.links.new(nt.nodes.new("ShaderNodeTexCoord").outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.nodes["Background"].inputs["Strength"].default_value = fuerza
    print("MUNDO cielo", os.path.basename(ruta), "giro", round(math.degrees(giro)))


def construir(mundo, ciclo, P, recorrido, farol):
    """Build the Night B world under `mundo` (the empty that moves -Y over the loop). `ciclo` = escena.json preset's
    `cycles` block; P = the preset; farol = the tramo's lamp objects (escena.tramo_props). Returns every new object."""
    sc = _sc()
    n = int(os.environ.get("RUTA_PERIODOS", "4"))  # ruta.py's long run needs more road ahead than one loop
    y0, y1 = -2 * recorrido, n * recorrido     # the view during the whole loop (mundo moves -recorrido), both directions
    copias = range(-2, n)
    suelo, pintura = carretera(mundo, y0, y1, recorrido)
    tierra = _plano("w_terreno", -1500, 1500, -5 * recorrido, (n + 3) * recorrido, 0.0,
                    mat_textura("w_suelo", "sparse_grass", 4.0, (0.22, 0.25, 0.18)), mundo)  # plan fix 9: green verge ground
    flora = plantas(mundo, recorrido, copias)
    linea = tendido(mundo, y0, y1) + farolas(farol, mundo, y0, y1)
    fog = niebla(ciclo["niebla"])
    cielo(sc.world, os.path.join(ASSETS_MUNDO, ciclo["hdri"] + "_2k.hdr"), ciclo["cielo_intensidad"], bpy.data.objects["luna"])
    bpy.data.objects["luna"].data.angle = math.radians(ciclo["luna_angulo"])  # overcast: a soft moon (plan fix 6)
    for o in pintura + flora + linea + [fog]:
        o.hide_viewport = True
    return suelo + [tierra] + pintura + flora + linea + [fog]
