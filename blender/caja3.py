"""Bed props, design pass (caja3): 12 props a corridos tumbados band would carry, each with its material (soft funda, tolex
hard case, ATA road case, worn plastic, our vinyl decals), a model sheet, and two arrangements of the picked bed B (the piñata
hangs from the roll bar over a low pile): A tidy, B lived-in. Sources: docs/design/references.md › Bed props, design pass.

Runs utileria.py's scene and helpers, adds its options, then utileria.py's own render loop (so utileria.py is not edited):

  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/caja3.py)" \
    -- <escena.py path (Windows)> <out_dir (Windows)> [samples] caja3-hoja,caja3-a,caja3-a-esc2,caja3-b,caja3-b-esc2 [WxH]

Decals reuse the sticker art from blender/calcas_arte.py (tmp/utileria/calcas3/, run that first), only the band pieces
without a platform glyph, so the §2 brand rules don't apply on the props.
"""
import bpy, math, os
from mathutils import Vector

U = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utileria.py")
MARCA = "# ---------------------------------------------------------------- render"
_cab, _cola = open(U, encoding="utf8").read().split(MARCA)
_g = {"__file__": U, "__name__": "utileria_caja3"}
exec(compile(_cab, U, "exec"), _g)
globals().update({k: v for k, v in _g.items() if not k.startswith("__")})

# ---------------------------------------------------------------- probes: bed walls and roll bar
CEN = Vector((CX, -2.1, Z0 + 0.25))
for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)):
    print("CAJA3 pared", d, rayo(CEN, d))
ARCO_Z = max((h.z for x in (CX - 0.6, CX - 0.3, CX, CX + 0.3, CX + 0.6) for h in [rayo((x, YC, 3.5), (0, 0, -1))] if h and h.z > 1.3),
             default=1.85)
print("CAJA3 arco z", ARCO_Z)

# ---------------------------------------------------------------- materials (kiln-prop: one per physical material; worn
# edges from a Bevel-node mask, edges="bevel", the way blender/skills/kiln-prop paints boxes)


def gastado3(nombre, color, rough, borde=None, rough_borde=None, bump=0.0, escala=300.0, tela=0.0, metal=0.0, coat=0.0):
    if nombre in MATS:
        return MATS[nombre]
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    L = nt.links.new
    # broad grime: the base colour varies 0.8-1.0 over ~30 cm
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.8, 1.0
    L(nz.outputs["Fac"], mr.inputs["Value"])
    base = nt.nodes.new("ShaderNodeMixRGB"); base.blend_type = "MULTIPLY"; base.inputs[0].default_value = 1
    base.inputs[1].default_value = (*color, 1)
    L(mr.outputs["Result"], base.inputs[2])
    col, rgh = base.outputs["Color"], None
    if borde is not None:
        bv = nt.nodes.new("ShaderNodeBevel"); bv.samples = 8; bv.inputs["Radius"].default_value = 0.008
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        dot = nt.nodes.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"
        L(bv.outputs["Normal"], dot.inputs[0]); L(geo.outputs["Normal"], dot.inputs[1])
        filo = nt.nodes.new("ShaderNodeMapRange")
        filo.inputs["From Min"].default_value, filo.inputs["From Max"].default_value = 0.90, 0.995
        filo.inputs["To Min"].default_value, filo.inputs["To Max"].default_value = 1.0, 0.0
        L(dot.outputs["Value"], filo.inputs["Value"])
        nz2 = nt.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 30.0; nz2.inputs["Detail"].default_value = 6
        rot = nt.nodes.new("ShaderNodeMapRange")
        rot.inputs["From Min"].default_value, rot.inputs["From Max"].default_value = 0.42, 0.58
        L(nz2.outputs["Fac"], rot.inputs["Value"])
        mk = nt.nodes.new("ShaderNodeMath"); mk.operation = "MULTIPLY"; mk.use_clamp = True
        L(filo.outputs["Result"], mk.inputs[0]); L(rot.outputs["Result"], mk.inputs[1])
        mx = nt.nodes.new("ShaderNodeMixRGB"); mx.inputs[2].default_value = (*borde, 1)
        L(mk.outputs["Value"], mx.inputs[0]); L(col, mx.inputs[1])
        col = mx.outputs["Color"]
        rr = nt.nodes.new("ShaderNodeMapRange")
        rr.inputs["To Min"].default_value, rr.inputs["To Max"].default_value = rough, rough_borde if rough_borde is not None else rough
        L(mk.outputs["Value"], rr.inputs["Value"])
        rgh = rr.outputs["Result"]
    L(col, b.inputs["Base Color"])
    if rgh:
        L(rgh, b.inputs["Roughness"])
    else:
        b.inputs["Roughness"].default_value = rough
    if bump or tela:
        if tela:  # quilted nylon: stitched bands every ~8 cm
            tx = nt.nodes.new("ShaderNodeTexWave"); tx.wave_type = "BANDS"; tx.inputs["Scale"].default_value = 12.0 * tela
            tco = nt.nodes.new("ShaderNodeTexCoord")
            L(tco.outputs["Object"], tx.inputs["Vector"])
            h = tx.outputs["Fac"]
        else:
            tx = nt.nodes.new("ShaderNodeTexNoise"); tx.inputs["Scale"].default_value = escala; tx.inputs["Detail"].default_value = 4
            h = tx.outputs["Fac"]
        bu = nt.nodes.new("ShaderNodeBump"); bu.inputs["Strength"].default_value = bump or 0.35
        L(h, bu.inputs["Height"])
        L(bu.outputs["Normal"], b.inputs["Normal"])
    MATS[nombre] = m
    return m


FUNDA = gastado3("k3_funda", (0.018, 0.018, 0.02), 0.85, (0.07, 0.07, 0.07), 0.7, bump=0.25, tela=1.0)  # padded nylon
FUNDA_CAFE = gastado3("k3_funda_cafe", (0.09, 0.05, 0.025), 0.8, (0.2, 0.13, 0.07), 0.7, bump=0.25, tela=1.3)
TOLEX = gastado3("k3_tolex", (0.012, 0.011, 0.01), 0.45, (0.12, 0.11, 0.1), 0.6, bump=0.3, escala=400, coat=0.2)  # hard case
LAMINADO = gastado3("k3_laminado", (0.015, 0.015, 0.016), 0.6, (0.16, 0.16, 0.17), 0.45, bump=0.12, escala=250)  # ATA laminate
ALU = gastado3("k3_alu", (0.6, 0.6, 0.62), 0.35, (0.8, 0.8, 0.82), 0.2, metal=1.0)
HIELERA = gastado3("k3_hielera", (0.62, 0.05, 0.04), 0.35, (0.75, 0.55, 0.5), 0.6)  # worn plastic: stress-whitened edges
TAPA = gastado3("k3_tapa", (0.85, 0.85, 0.82), 0.4, (0.55, 0.53, 0.48), 0.7)
REJA = gastado3("k3_reja", (0.85, 0.6, 0.05), 0.45, (0.95, 0.85, 0.55), 0.6)  # beer crate, generic yellow, no brand
CARTON = gastado3("k3_carton", (0.02, 0.018, 0.016), 0.55, (0.5, 0.42, 0.25), 0.8)  # hat box: black, scuffed to kraft at the rims
FIELTRO = gastado3("k3_fieltro", (0.75, 0.66, 0.5), 0.9)  # straw-coloured tejana
LONA = gastado3("k3_lona", (0.12, 0.13, 0.07), 0.9, (0.2, 0.2, 0.14), 0.9, bump=0.2, escala=600)  # duffel canvas
CINTA = gastado3("k3_cinta", (0.95, 0.35, 0.02), 0.7, bump=0.15, escala=900)  # ratchet strap webbing
CINTA_N = gastado3("k3_cinta_n", (0.02, 0.02, 0.02), 0.7, bump=0.15, escala=900)
VIDRIO = mat("k3_vidrio", (0.35, 0.15, 0.02), 0.1, trans=0.6)
GOMA = mat("k3_goma", (0.01, 0.01, 0.01), 0.75)
STENCIL = mat("k3_stencil", (0.85, 0.84, 0.8), 0.8)
CALCAS3 = os.path.join(PANTALLAS, "calcas3")


def calca_en(id, loc, rot, escala=1.0):
    """One of our band stickers (no platform glyph) on a flat face, 0.6 mm off it (kiln-utility-box decals)."""
    w, h = META3[id]["w"] * escala, META3[id]["h"] * escala
    return plano(w, h, loc, mat3(id, META3[id]["acabado"]), rot=rot, parent=False)


def unir(nombre, construir, loc, rot=(0, 0, 0)):
    """Build a prop around the origin, then make it one object placed at loc/rot (so it can be posed, and wobbled later)."""
    antes = len(GRUPO)
    construir()
    objs = GRUPO[antes:]
    del GRUPO[antes:]
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.parent = None
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.convert(target="MESH")  # applies the bevels and turns text into mesh
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = "k3_" + nombre
    o.location, o.rotation_euler = loc, rot
    GRUPO.append(o)
    return o


# ---------------------------------------------------------------- the props (real sizes, references.md › Bed props)
F = False


def funda(L, inf, sup, prof, cuerpo, m=FUNDA):
    """Soft padded gig bag in the instrument's outline, standing on its end at the origin (z up, front −y)."""
    zi, zs = cuerpo * 0.36 * L, cuerpo * 0.80 * L
    esfera(1, (0, 0, zi), m, scale=(inf / 2, prof / 2, cuerpo * 0.36 * L), parent=F)
    esfera(1, (0, 0, zs), m, scale=(sup / 2, prof / 2 * 0.95, cuerpo * 0.26 * L), parent=F)
    cuello = L - cuerpo * L
    caja((sup * 0.34, prof * 0.62, cuello), (0, 0, cuerpo * L + cuello / 2 - 0.04), m, bevel=0.03, parent=F)
    esfera(1, (0, 0, L - 0.07), m, scale=(sup * 0.24, prof * 0.34, 0.09), parent=F)
    caja((inf * 0.55, 0.05, cuerpo * L * 0.3), (0, -prof / 2 - 0.005, zi - 0.05), m, bevel=0.02, parent=F)  # front pocket


def tololoche():
    """3/4 double bass in a padded funda: 1.80 m, lower bout 0.66 m, 0.32 m deep (the only fundas found are soft)."""
    funda(1.80, 0.66, 0.50, 0.32, 0.58)


def bajo_sexto():
    """Bajo sexto (12 strings) funda: 1.05 m, lower bout 0.44 m, 0.14 m deep, brown nylon."""
    funda(1.05, 0.44, 0.34, 0.14, 0.50, FUNDA_CAFE)


def estuche_requinto(calcas=("b-escudo", "a-estrella")):
    """Requinto hard case, rectangular, black tolex: 0.98 × 0.36 × 0.12 m, aluminium valance, two latches; stickers on the lid."""
    caja((0.98, 0.36, 0.12), (0, 0, 0.06), TOLEX, bevel=0.025, parent=F)
    caja((0.985, 0.365, 0.012), (0, 0, 0.075), ALU, bevel=0.003, parent=F)
    for x in (-0.25, 0.25):
        caja((0.04, 0.012, 0.03), (x, -0.185, 0.075), ALU, bevel=0.003, parent=F)
    caja((0.12, 0.02, 0.025), (0, -0.19, 0.06), GOMA, bevel=0.008, parent=F)  # handle
    for i, id in enumerate(calcas):
        calca_en(id, (-0.18 + i * 0.36, 0.0, 0.1206), (0, 0, 0.12 - 0.3 * i), 0.8)


def road_case(calcas=("a-mafia", "b-ver", "a-loteria")):
    """ATA road case, 0.76 × 0.46 × 0.50 m: black laminate on ply, aluminium extrusions on every edge, steel ball corners,
    recessed butterfly latches, spring handles; stencilled band name and stickers."""
    W, D, H = 0.76, 0.46, 0.50
    caja((W, D, H), (0, 0, H / 2), LAMINADO, bevel=0.004, parent=F)
    e = 0.022
    for sx in (-1, 1):
        for sy in (-1, 1):
            caja((e, e, H), (sx * W / 2, sy * D / 2, H / 2), ALU, parent=F)
        for sz in (0, 1):
            caja((e, D, e), (sx * W / 2, 0, sz * H), ALU, parent=F)
    for sy in (-1, 1):
        for sz in (0, 1):
            caja((W, e, e), (0, sy * D / 2, sz * H), ALU, parent=F)
    caja((W + 0.01, D + 0.01, 0.018), (0, 0, H * 0.72), ALU, parent=F)  # the lid seam
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (0, 1):
                esfera(0.024, (sx * W / 2, sy * D / 2, sz * H), ALU, parent=F)
    for x in (-0.22, 0.22):
        caja((0.06, 0.01, 0.06), (x, -D / 2 - 0.004, H * 0.72), ALU, bevel=0.004, parent=F)  # butterfly latch dish
    for sx in (-1, 1):
        caja((0.012, 0.12, 0.05), (sx * (W / 2 + 0.004), 0, H * 0.45), GOMA, bevel=0.004, parent=F)
    texto("MAFIA TUMBADA", 0.075, (0, -D / 2 - 0.0008, H * 0.42), STENCIL, font="impact.ttf", parent=F)
    texto("XALAPA, VER.  ·  BACKLINE 03", 0.028, (0, -D / 2 - 0.0008, H * 0.26), STENCIL, font="consola.ttf", parent=F)
    for i, id in enumerate(calcas):
        if i == 0:
            calca_en(id, (0.05, 0.02, H + 0.0006), (0, 0, -0.08), 0.85)
        else:
            calca_en(id, (-0.28 + (i - 1) * 0.56, -D / 2 - 0.0012, H * 0.12 + 0.06 * (i == 2)), (math.pi / 2, 0.1 - 0.25 * (i - 1), 0), 0.6)


def hielera3(calca="a-putifresa"):
    """Coleman-style 48 qt cooler, 0.64 × 0.37 × 0.42 m: red body, white lid, worn plastic, the band strawberry on its side."""
    caja((0.64, 0.37, 0.36), (0, 0, 0.18), HIELERA, bevel=0.03, parent=F)
    caja((0.66, 0.39, 0.06), (0, 0, 0.39), TAPA, bevel=0.02, parent=F)
    for s in (-1, 1):
        caja((0.03, 0.12, 0.03), (s * 0.335, 0, 0.3), TAPA, bevel=0.008, parent=F)
    calca_en(calca, (0, -0.1856, 0.19), (math.pi / 2, 0, 0), 0.82)


def bocina3():
    """Party tower speaker, 0.36 × 0.34 × 0.72 m: two woofers with LED rings and a top handle."""
    caja((0.36, 0.34, 0.72), (0, 0, 0.36), gastado3("k3_bocina", (0.025, 0.025, 0.028), 0.55, (0.12, 0.12, 0.13), 0.4), bevel=0.02, parent=F)
    for z, r, col in ((0.48, 0.13, ROSA), (0.2, 0.12, TURQ)):
        cil(r, 0.01, (0, -0.172, z), GOMA, rot=(math.pi / 2, 0, 0), parent=F)
        toro(r + 0.01, 0.007, (0, -0.176, z), mat(f"k3_led_{z}", col, emit=5.0), rot=(math.pi / 2, 0, 0), parent=F)
    caja((0.22, 0.05, 0.04), (0, 0, 0.74), GOMA, bevel=0.015, parent=F)


def sombrerera(calca="b-pura"):
    """Hat box for a tejana: round, 0.50 m across, 0.22 m tall, black card scuffed to kraft at the rims; PURA MT on the lid."""
    cil(0.25, 0.20, (0, 0, 0.10), CARTON, verts=48, parent=F)
    cil(0.255, 0.05, (0, 0, 0.205), CARTON, verts=48, parent=F)
    calca_en(calca, (0, 0, 0.2306), (0, 0, 0.1), 0.85)


def tejana():
    """Straw tejana: brim 0.42 × 0.36 m curled at the sides, a pinched crown 0.13 m tall."""
    o = cil(0.2, 0.012, (0, 0, 0.006), FIELTRO, verts=48, parent=F)
    o.scale = (1, 0.85, 1)
    toro(0.17, 0.045, (0, 0, 0.02), FIELTRO, parent=F).scale = (1, 0.82, 0.35)  # the rolled brim edge
    cono(0.10, 0.085, 0.13, (0, 0, 0.07), FIELTRO, verts=32, parent=F)
    cil(0.101, 0.025, (0, 0, 0.022), mat("k3_toquilla", (0.02, 0.02, 0.02), 0.5), parent=F)


def rejilla(faltan=0):
    """Plastic crate of 12 amber bottles, 0.46 × 0.32 × 0.30 m, generic (no brand); `faltan` bottles taken."""
    W, D, H, t = 0.46, 0.32, 0.30, 0.012
    caja((W, D, t), (0, 0, t / 2), REJA, parent=F)
    for sx in (-1, 1):
        caja((t, D, H), (sx * (W - t) / 2, 0, H / 2), REJA, bevel=0.003, parent=F)
    for sy in (-1, 1):
        caja((W, t, H * 0.55), (0, sy * (D - t) / 2, H * 0.275), REJA, bevel=0.003, parent=F)
        caja((W, t, 0.04), (0, sy * (D - t) / 2, H - 0.02), REJA, bevel=0.003, parent=F)
    k = 0
    for i in range(4):
        for j in range(3):
            k += 1
            if k <= faltan:
                continue
            x, y = -0.165 + i * 0.11, -0.1 + j * 0.1
            cil(0.032, 0.17, (x, y, 0.1), VIDRIO, verts=16, parent=F)
            cono(0.032, 0.013, 0.06, (x, y, 0.215), VIDRIO, verts=16, parent=F)
            cil(0.014, 0.025, (x, y, 0.255), mat("k3_corcho", (0.8, 0.7, 0.1), 0.3, 1.0), verts=12, parent=F)


def bandera3(espejo=False):
    """Band flag on an aluminium pole: 0.90 × 0.60 m cloth with a wind ripple, black field, the MT shield in the middle.
    espejo: the cameras see the back of the cloth (it flies back over the bar), so print the art mirrored to read MT, not TM."""
    cil(0.012, 1.5, (0, 0, 0.75), ALU, verts=12, parent=F)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=30, y_subdivisions=20, size=1, location=(0, 0, 0))
    o = bpy.context.object
    o.scale = (0.9, 0.6, 1)
    bpy.ops.object.transform_apply(scale=True)
    for v in o.data.vertices:
        u = v.co.x + 0.45
        v.co = Vector((u, 0.05 * u * math.sin(u * 9.0 + v.co.y * 3), v.co.y))
    o.location = (0.012, 0, 1.18)
    m = bpy.data.materials.new("k3_bandera")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.8
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(os.path.join(CALCAS3, "b-escudo.png"), check_existing=True)
    tx.extension = "CLIP"
    mp = nt.nodes.new("ShaderNodeMapping")
    sx, sy = 0.9 / 0.4, 0.6 / 0.46
    mp.inputs["Scale"].default_value = (-sx if espejo else sx, sy, 1)
    mp.inputs["Location"].default_value = ((sx + 1) / 2 if espejo else -(sx - 1) / 2, -(sy - 1) / 2, 0)
    uv = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(uv.outputs["UV"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], tx.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMixRGB")
    mx.inputs[1].default_value = (0.008, 0.008, 0.008, 1)
    nt.links.new(tx.outputs["Alpha"], mx.inputs[0])
    nt.links.new(tx.outputs["Color"], mx.inputs[2])
    nt.links.new(mx.outputs["Color"], b.inputs["Base Color"])
    _fin(o, m, F)


def papel_picado(a, b, n=9, caida=0.12):
    """String of plastic papel picado between two points: n panels 0.24 × 0.30 m, punched pattern as alpha, the string sagging."""
    a, b = Vector(a), Vector(b)
    for i in range(n):
        t = (i + 0.5) / n
        p = a.lerp(b, t) - Vector((0, 0, caida * 4 * t * (1 - t)))
        col = (ROSA, TURQ, (1, 0.8, 0.1), LIMA, (0.95, 0.35, 0.1))[i % 5]
        m = MATS.get(f"k3_picado_{i % 5}")
        if not m:
            m = bpy.data.materials.new(f"k3_picado_{i % 5}")
            m.use_nodes = True
            nt = m.node_tree
            bs = nt.nodes["Principled BSDF"]
            bs.inputs["Base Color"].default_value = (*col, 1)
            bs.inputs["Roughness"].default_value = 0.35
            bs.inputs["Emission Color"].default_value = (*col, 1)
            bs.inputs["Emission Strength"].default_value = 0.15
            vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 7.0
            gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.22
            nt.links.new(vo.outputs["Distance"], gt.inputs[0])
            nt.links.new(gt.outputs["Value"], bs.inputs["Alpha"])
            MATS[m.name] = m
        d = (b - a).normalized()
        plano(0.24, 0.30, p - Vector((0, 0, 0.15)), m, rot=(math.pi / 2, 0, math.atan2(d.y, d.x) + 0.12 * math.sin(i * 1.7)), parent=F)
    L = (b - a).length
    for k in range(8):  # the sagging string as short segments
        t0, t1 = k / 8, (k + 1) / 8
        p0 = a.lerp(b, t0) - Vector((0, 0, caida * 4 * t0 * (1 - t0)))
        p1 = a.lerp(b, t1) - Vector((0, 0, caida * 4 * t1 * (1 - t1)))
        dd = p1 - p0
        cil(0.002, dd.length, p0 + dd / 2, mat("u_hilo", (0.9, 0.9, 0.9), 0.5),
            rot=(0, math.atan2(math.hypot(dd.x, dd.y), dd.z), math.atan2(dd.y, dd.x)), verts=6, parent=F)


def maleta():
    """Duffel bag, 0.62 m long, olive canvas, slumped; two handles."""
    esfera(1, (0, 0, 0.12), LONA, scale=(0.31, 0.16, 0.13), parent=F)
    for s in (-1, 1):
        toro(0.06, 0.008, (s * 0.08, 0, 0.24), CINTA_N, rot=(0, 0, 0), parent=F).scale = (1, 0.4, 1)


def cable():
    """Coiled XLR cable, 0.26 m across, black, a loose tail."""
    for i in range(6):
        toro(0.12 + 0.004 * (i % 3), 0.0055, (0.004 * i, 0.003 * i, 0.006 + 0.008 * i), GOMA, rot=(0.05 * (i % 2), 0.04, 0), parent=F)
    cil(0.0055, 0.25, (0.2, -0.05, 0.006), GOMA, rot=(0, math.pi / 2, 0.6), verts=8, parent=F)


def cincho(a, b, m=CINTA, ancho=0.035):
    """A ratchet strap run from a to b (flat webbing), with a buckle in the middle."""
    a, b = Vector(a), Vector(b)
    d = b - a
    o = caja((d.length, ancho, 0.003), a + d / 2, m, parent=False)
    o.rotation_euler = d.to_track_quat("X", "Z").to_euler()
    caja((0.07, ancho + 0.01, 0.025), a + d / 2 + Vector((0, 0, 0.012)), ALU, rot=o.rotation_euler, bevel=0.004, parent=False)


# ---------------------------------------------------------------- scene housekeeping
def vaciar_caja():
    """The bed is dressed here: hide the two members who sit in it in v3 (plan: they ride in the rear seats), their guitars and the
    three seat cases transicion.py puts there."""
    for o in bpy.data.objects:
        n = o.name.split(".")[0]
        if n.startswith(("estuche_", "guitarra_")) or n.split("_")[0] in ("alejandro", "diego"):
            for c in [o] + list(o.children_recursive):  # the guitars are built of child meshes
                c.hide_render = True


def techo_caja(x0, x1, y):
    """Piñata hanging from the middle of the roll bar (bed B), balloons at the bar's ends."""
    pinata((CX, y - 0.35, ARCO_Z - 0.45), 0.2)
    cil(0.004, 0.5, (CX, y - 0.18, ARCO_Z - 0.12), mat("u_hilo", (0.9, 0.9, 0.9), 0.5), rot=(0.55, 0, 0), verts=6, parent=False)
    for x in (x0, x1):
        globos((x, y, ARCO_Z), 5, alto=0.8)


def relleno_caja(pos):
    """A warm fill from the camera's side so the materials read (tail lamps and the bed light alone leave them black)."""
    S = Vector((CX, -2.1, Z0 + 0.35))
    P = Vector(pos)
    luz("AREA", P + (S - P).normalized() * 0.8 + Vector((0.6, 0, 0.6)), 45 * ((S - P).length / 3.0) ** 2, (1.0, 0.86, 0.7),
        mira=S, size=1.2, parent=False)
    for o in GRUPO:
        if o.type == "LIGHT":
            o.visible_camera = False


# ---------------------------------------------------------------- model sheet: the 12 on the road behind the truck
HOJA_Y = -30.0
PROPS = [  # back row (tall) then front row
    ("1 Tololoche", tololoche), ("2 Bajo sexto", bajo_sexto), ("3 Bandera", bandera3), ("4 Bocina", bocina3),
    ("5 Road case", road_case), ("6 Requinto", estuche_requinto),
    ("7 Hielera", hielera3), ("8 Sombrerera", sombrerera), ("9 Tejana", tejana), ("10 Cerveza", rejilla), ("11 Maleta", maleta),
    ("12 Cable", cable),
]


@opcion("caja3-hoja")
def caja3_hoja():
    """All 12 props, front-on, in three rows of four, with a number and a name under each."""
    for k, (nombre, f) in enumerate(PROPS):
        fila, col = divmod(k, 6)
        x, y = CX - 2.9 + col * 1.16, HOJA_Y + 1.9 * (1 - fila)
        unir(nombre.split(maxsplit=1)[1].lower().replace(" ", "_"), f, (x, y, 0.0), (0, 0, 0))
        texto(nombre, 0.15, (x, y - 0.6, 0.12), mat("k3_rotulo", (0.95, 0.93, 0.88), 0.5, emit=1.2), rot=(math.radians(50), 0, 0), parent=False)
    S = Vector((CX, HOJA_Y + 1.0, 0.6))
    luz("AREA", S + Vector((0, -1.5, 4.0)), 900, (1.0, 0.95, 0.88), mira=S, size=5.0, parent=False)
    luz("AREA", S + Vector((-3.0, -4.0, 1.5)), 400, (1.0, 0.9, 0.8), mira=S, size=3.0, parent=False)
    for o in GRUPO:
        if o.type == "LIGHT":
            o.visible_camera = False
    return ((CX, HOJA_Y - 4.6, 4.3), (CX, HOJA_Y + 1.05, 0.4), 28)


# ---------------------------------------------------------------- arrangements of bed B
VISTA_CAJA3 = lambda: ((CX - 0.7, -4.7, 3.3), (CX, -1.95, 1.25), 32)  # higher than VISTA_CAJA: it sees into the bed


def caja3_a():
    """A, tidy: the two fundas standing square against the cab, a black strap across them; the road case with the requinto on
    it; the crate with the hat box and the tejana; the cooler with the donut on it (as bed B); the speaker; the flag zip-tied to
    the right post; papel picado taut along the bar."""
    vaciar_caja()
    unir("tololoche", tololoche, (CX - 0.25, -1.3, Z0))
    unir("bajo_sexto", bajo_sexto, (CX + 0.3, -1.22, Z0))
    cincho((CX - 0.55, -1.12, Z0 + 0.8), (CX + 0.55, -1.12, Z0 + 0.8), CINTA_N)
    unir("road_case", road_case, (CX + 0.17, -1.8, Z0))
    unir("requinto", estuche_requinto, (CX + 0.17, -1.8, Z0 + 0.5), (0, 0, math.pi / 2))
    unir("cerveza", rejilla, (CX - 0.3, -1.85, Z0))
    unir("sombrerera", sombrerera, (CX - 0.3, -1.85, Z0 + 0.3))
    unir("tejana", tejana, (CX - 0.3, -1.85, Z0 + 0.53), (0, 0, 0.3))
    unir("hielera", hielera3, (CX - 0.23, -2.45, Z0))
    dona((CX - 0.23, -2.45, Z0 + 0.54), (0.05, 0, 0))
    unir("bocina", bocina3, (CX + 0.35, -2.45, Z0))
    unir("bandera", lambda: bandera3(True), (CX + 0.55, YC, ARCO_Z - 0.6), (0, 0, math.radians(-140)))  # flies back over the bar, above the cab line
    papel_picado((CX - 0.55, YC, ARCO_Z), (CX + 0.55, YC, ARCO_Z), n=7, caida=0.06)
    techo_caja(CX - 0.45, CX + 0.45, YC)


def caja3_b():
    """B, lived-in: the fundas leaning crossed against the cab, an orange ratchet strap over the pile, the requinto thrown on the
    road case with a coiled cable on it, a duffel on the crate (two bottles gone), the hat box rolled on its side on the cooler,
    the tejana on the speaker, the donut squeezed upright between them, papel picado sagging off one end."""
    vaciar_caja()
    unir("tololoche", tololoche, (CX - 0.32, -1.32, Z0 + 0.02), (-0.12, 0.28, 0.2))
    unir("bajo_sexto", bajo_sexto, (CX + 0.32, -1.3, Z0 + 0.02), (-0.18, -0.3, -0.25))
    unir("road_case", road_case, (CX + 0.17, -1.9, Z0), (0, 0, -0.12))
    unir("requinto", estuche_requinto, (CX + 0.12, -1.95, Z0 + 0.5), (0, 0, math.pi / 2 + 0.1))
    unir("cable", cable, (CX + 0.28, -1.78, Z0 + 0.62))
    unir("cerveza", lambda: rejilla(2), (CX - 0.3, -1.85, Z0), (0, 0, 0.3))
    unir("maleta", maleta, (CX - 0.32, -1.88, Z0 + 0.3), (0, 0, 0.5))
    unir("hielera", hielera3, (CX - 0.25, -2.42, Z0), (0, 0, 0.15))
    unir("sombrerera", sombrerera, (CX - 0.25, -2.45, Z0 + 0.42 + 0.25), (math.pi / 2, 0, 0.25))
    unir("bocina", bocina3, (CX + 0.36, -2.45, Z0), (0, 0, -0.3))
    unir("tejana", tejana, (CX + 0.36, -2.45, Z0 + 0.76), (0.2, 0.1, 0.8))
    dona((CX + 0.05, -2.5, Z0 + 0.3), (1.3, 0.2, 0.15))
    cincho((CX - 0.55, -2.0, Z0 + 0.62), (CX + 0.55, -1.85, Z0 + 0.64))
    unir("bandera", lambda: bandera3(True), (CX + 0.55, YC, ARCO_Z - 0.6), (0.08, 0.1, math.radians(-150)))
    papel_picado((CX - 0.55, YC, ARCO_Z), (CX + 0.15, YC - 0.05, ARCO_Z - 0.3), n=5, caida=0.18)
    techo_caja(CX - 0.45, CX + 0.45, YC)


for _n, _f in (("a", caja3_a), ("b", caja3_b)):
    for _suf, _vista in (("", VISTA_CAJA3), ("-esc2", VISTA_ESC2)):
        def _op(f=_f, vista=_vista):
            f()
            relleno_caja(vista()[0])
            return vista()
        opcion(f"caja3-{_n}{_suf}")(_op)

# ---------------------------------------------------------------- utileria.py's render loop, over the options above
exec(compile(MARCA + _cola, U, "exec"), _g)
