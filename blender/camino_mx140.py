"""The road as the Xalapa-Veracruz highway (México 140, La Estanzuela / Miradores) in the owner's Street View refs
(~/cc-out/mto-pantalla/refs/road/, 2026-11-16; reference only, never a texture, never in the repo).

Runs inside montaje.py's namespace, exec'd at the end of pantalla_3d.py when MONTAJE_CAMINO is set (pass it with WSLENV).
It rebuilds mundo.py's road in place, in the render only (the page's GLB is not touched):

  x (m, the truck drives +Y; its lane is 0..3.5)
  +7.6 .. +6.4  dirt and gravel          +6.4 .. +3.85  worn asphalt shoulder, dirt creeping in at the outer edge
  +3.55 white edge | 0 dashed white | -3.55 yellow edge   (mundo.py's own lines: our carriageway, 2 lanes of 3.5 m)
  -3.85 .. -4.65 shoulder | -4.65 .. -5.25 concrete New Jersey barrier | -5.25 .. -6.05 shoulder
  -6.05 yellow edge | -9.55 dashed white | -13.05 white edge   (the oncoming carriageway, 2 lanes of 3.5 m)
  -13.35 .. -15.3 worn asphalt shoulder, then dirt to -16.6

Plus wooden poles (right) and concrete poles (left) with sagging wires, dry straw clumps among the tropical green, a bright
overcast sky (procedural, no HDRI) and the night lamps off. The truck, the screens and the 'ancha' lamp are not touched.
Assets: Poly Haven CC0 already in mundo.ASSETS_MUNDO (asphalt_02, gravelly_sand, sparse_grass, the plant models); nothing new.
Not built (optional in the brief): gas-station canopy, pedestrian bridge, oncoming traffic.
"""
import json
import math
import os
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix

import mundo as M

PER = float(json.load(open(os.path.join(REPO, "src", "lib", "escena.json"), encoding="utf8"))["mundo"]["recorrido_loop"])  # escena.RECORRIDO
Y0, Y1 = -2 * PER, 4 * PER
MUNDO_ROOT = bpy.data.objects["mundo"]
X_BARRERA = (-5.25, -4.65)
X_OP = dict(amarilla=-6.05, centro=-9.55, blanca=-13.05)
X_DER_FIN, X_IZQ_FIN = 6.4, -15.3          # worn asphalt ends; dirt strips follow (1.2 m), then the ground
CIELO = dict(horizonte=(0.80, 0.81, 0.80), cenit=(0.50, 0.54, 0.60), fuerza=1.0, exposicion=0.0)
SOL = dict(energia=2.5, angulo=22.0, color=(1.0, 0.97, 0.92))
NIEBLA = dict(densidad=0.0010, color=(0.80, 0.81, 0.80))


def _nodo(nt, tipo, **kw):
    n = nt.nodes.new(tipo)
    for k, v in kw.items():
        setattr(n, k, v)
    return n


def _mezcla(nt, a, b, fac, blend="MIX"):
    """Mix node (RGBA); a, b: socket or colour tuple; fac: socket or float. Returns the result socket."""
    m = _nodo(nt, "ShaderNodeMix", data_type="RGBA", blend_type=blend)
    for idx, v in ((6, a), (7, b)):
        if isinstance(v, tuple):
            m.inputs[idx].default_value = (*v, 1)
        else:
            nt.links.new(v, m.inputs[idx])
    if isinstance(fac, float):
        m.inputs["Factor"].default_value = fac
    else:
        nt.links.new(fac, m.inputs["Factor"])
    return m.outputs[2]


def _rango(nt, sock, lo, hi, a=0.0, b=1.0):
    r = _nodo(nt, "ShaderNodeMapRange")
    r.inputs["From Min"].default_value, r.inputs["From Max"].default_value = lo, hi
    r.inputs["To Min"].default_value, r.inputs["To Max"].default_value = a, b
    nt.links.new(sock, r.inputs["Value"])
    return r.outputs["Result"]


def _ruido(nt, co, escala, detalle=6):
    n = _nodo(nt, "ShaderNodeTexNoise")
    n.inputs["Scale"].default_value, n.inputs["Detail"].default_value = escala, detalle
    nt.links.new(co, n.inputs["Vector"])
    return n.outputs["Fac"]


def _tierra_borde(x_ini, x_fin, tierra=(0.30, 0.26, 0.20)):
    """extra for mat_textura: the surface turns to dirt from x_ini (none) to x_fin (all), the edge broken up by noise."""
    def f(nt, co, color, rough):
        x = _nodo(nt, "ShaderNodeSeparateXYZ"); nt.links.new(co, x.inputs["Vector"])
        ruido = _ruido(nt, co, 0.8)
        desv = _nodo(nt, "ShaderNodeMath", operation="MULTIPLY_ADD")
        nt.links.new(ruido, desv.inputs[0]); desv.inputs[1].default_value = 1.6; desv.inputs[2].default_value = -0.8
        s = _nodo(nt, "ShaderNodeMath", operation="ADD")
        nt.links.new(x.outputs["X"], s.inputs[0]); nt.links.new(desv.outputs[0], s.inputs[1])
        return _mezcla(nt, color, tierra, _rango(nt, s.outputs[0], x_ini, x_fin)), rough
    return f


def _suciedad(periodo):
    """The oncoming carriageway: mundo.desgaste's patches, cracks and macro variation (its wheel paths sit on our lane)."""
    return M.desgaste(periodo)


def _quitar(prefijos=(), exactos=()):
    n = 0
    for o in list(bpy.data.objects):
        base = o.name.split(".")[0]
        if base in exactos or any(base.startswith(p) for p in prefijos):
            bpy.data.objects.remove(o)
            n += 1
    return n


def _ocultar(objs):
    for o in objs:
        o.hide_viewport = True


# ---------------------------------------------------------------- surfaces
def superficies():
    tinte = 0.80
    asf = bpy.data.materials["w_asfalto"]
    asf.node_tree.nodes["tinte"].inputs[7].default_value = (tinte, tinte, tinte + 0.02, 1)   # day: the night tint is too dark
    hombro = lambda nombre, ini, fin: M.mat_textura(nombre, "asphalt_02", 3.0, (0.95, 0.93, 0.90), extra=_tierra_borde(ini, fin))
    grava = M.mat_textura("w_grava_dia", "gravelly_sand", 1.5, (0.62, 0.68, 0.72))
    op = M.mat_textura("w_asfalto_op", "asphalt_02", 3.0, (tinte, tinte, tinte + 0.02), extra=_suciedad(PER))
    _quitar(exactos={"w_acot_der", "w_acot_izq", "w_grava_der", "w_grava_izq"})
    return [
        M._plano("w_carretera_op", -13.35, -5.75, Y0, Y1, 0.016, op, MUNDO_ROOT),
        M._plano("w_acot_izq", -4.65, -3.85, Y0, Y1, 0.015, hombro("w_acot_izq_dia", -4.60, -4.65), MUNDO_ROOT),
        M._plano("w_acot_der", 3.85, X_DER_FIN, Y0, Y1, 0.015, hombro("w_acot_der_dia", 4.6, X_DER_FIN), MUNDO_ROOT),
        M._plano("w_acot_op_in", -5.75, -5.25, Y0, Y1, 0.015, hombro("w_acot_op_in_dia", -5.30, -5.25), MUNDO_ROOT),
        M._plano("w_acot_op_ext", X_IZQ_FIN, -13.35, Y0, Y1, 0.015, hombro("w_acot_op_ext_dia", -14.0, X_IZQ_FIN), MUNDO_ROOT),
        M._plano("w_grava_der", X_DER_FIN, 7.6, Y0, Y1, 0.012, grava, MUNDO_ROOT),
        M._plano("w_grava_izq", -16.6, X_IZQ_FIN, Y0, Y1, 0.012, grava, MUNDO_ROOT),
    ]


def rayas():
    """The oncoming carriageway's lines, same paints and dash fit as mundo.marcas (13 per period, 4.92 / 9.85 m)."""
    blanca, amarilla = bpy.data.materials["w_pintura_blanca"], bpy.data.materials["w_pintura_amarilla"]
    paso = PER / 13
    n = int(round((Y1 - Y0) / paso))

    def tira(nombre, rects, m):
        bm = bmesh.new()
        for a0, a1, b0, b1 in rects:
            bm.faces.new([bm.verts.new((a0, b0, 0)), bm.verts.new((a1, b0, 0)), bm.verts.new((a1, b1, 0)), bm.verts.new((a0, b1, 0))])
        me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(nombre, me); o.location = (0, 0, 0.019); o.data.materials.append(m)
        bpy.context.scene.collection.objects.link(o); o.parent = MUNDO_ROOT
        return o
    xa, xc, xb = X_OP["amarilla"], X_OP["centro"], X_OP["blanca"]
    out = [tira("w_op_amarilla", [(xa - 0.075, xa + 0.075, Y0, Y1)], amarilla),
           tira("w_op_blanca", [(xb - 0.075, xb + 0.075, Y0, Y1)], blanca),
           tira("w_op_carril", [(xc - 0.075, xc + 0.075, Y0 + k * paso, Y0 + k * paso + paso / 3) for k in range(n)], blanca)]
    _quitar(prefijos=("w_boton",))                                     # no cat's eyes in the refs
    return out


# ---------------------------------------------------------------- New Jersey barrier
def barrera():
    """Concrete NJ barrier, 6 m panels with a 2 cm joint, 0.80 m tall, between the two carriageways."""
    xc = sum(X_BARRERA) / 2
    perfil = [(-0.30, 0), (0.30, 0), (0.30, 0.075), (0.17, 0.33), (0.10, 0.80), (-0.10, 0.80), (-0.17, 0.33), (-0.30, 0.075)]
    bm = bmesh.new()
    largo = 6.0
    for y in np.arange(Y0, Y1, largo):
        anillos = [[bm.verts.new((xc + px, y + dy, pz)) for px, pz in perfil] for dy in (0.01, largo - 0.01)]
        k = len(perfil)
        for i in range(k):
            bm.faces.new([anillos[0][i], anillos[0][(i + 1) % k], anillos[1][(i + 1) % k], anillos[1][i]])
        bm.faces.new(anillos[0][::-1]); bm.faces.new(anillos[1])
    me = bpy.data.meshes.new("w_barrera"); bm.to_mesh(me); bm.free()
    m = bpy.data.materials.new("w_concreto_barrera"); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    co = _nodo(nt, "ShaderNodeTexCoord").outputs["Object"]
    z = _nodo(nt, "ShaderNodeSeparateXYZ"); nt.links.new(co, z.inputs["Vector"])
    base = _mezcla(nt, (0.46, 0.45, 0.42), (0.30, 0.30, 0.28), _rango(nt, _ruido(nt, co, 5.0, 8), 0.4, 0.65))      # weathered grey
    base = _mezcla(nt, base, (0.34, 0.27, 0.18), _rango(nt, z.outputs["Z"], 0.30, 0.0), "MULTIPLY")               # road dirt at the foot
    base = _mezcla(nt, base, (0.55, 0.60, 0.42), _rango(nt, _ruido(nt, co, 1.3, 4), 0.62, 0.8, 0.0, 0.5), "MULTIPLY")  # algae streaks
    nt.links.new(base, p.inputs["Base Color"]); p.inputs["Roughness"].default_value = 0.92
    me.materials.append(m)
    o = bpy.data.objects.new("w_barrera", me)
    bpy.context.scene.collection.objects.link(o); o.parent = MUNDO_ROOT
    return [o]


# ---------------------------------------------------------------- poles and wires
def postes(nombre, x, alto, mat, paso, fase, flecha, madera):
    bm = bmesh.new()
    ys = [float(y) for y in np.arange(Y0 + fase % paso, Y1 + 1, paso)]
    rnd = random.Random(int(abs(x) * 10))
    for y in ys:
        incl = rnd.uniform(-0.03, 0.03)
        r1, r2 = (0.15, 0.09) if madera else (0.19, 0.11)
        g = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=r1, radius2=r2, depth=alto,
                                  matrix=Matrix.Translation((x, y, alto / 2)) @ Matrix.Rotation(incl, 4, "Y"))
        bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation((x, y, alto - 0.55)) @ Matrix.Diagonal((2.2, 0.10, 0.10, 1)))
        for dx in (-1.0, 1.0):  # insulators
            bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.05, radius2=0.03, depth=0.16,
                                  matrix=Matrix.Translation((x + dx, y, alto - 0.42)))
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    po = bpy.data.objects.new(nombre, me); bpy.context.scene.collection.objects.link(po); po.parent = MUNDO_ROOT
    cu = bpy.data.curves.new(nombre + "_cables", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.011
    for dx, dz in ((-1.0, -0.42), (0.0, -0.9), (1.0, -0.42), (0.0, -0.42)):
        for ya, yb in zip(ys[:-1], ys[1:]):
            sp = cu.splines.new("POLY"); sp.points.add(11)
            for i in range(12):
                t = i / 11
                sp.points[i].co = (x + dx, ya + (yb - ya) * t, alto + dz - flecha * 4 * t * (1 - t), 1)
    co = bpy.data.objects.new(nombre + "_cables", cu)
    co.data.materials.append(M.mat_color("w_cable_dia", (0.012, 0.012, 0.012), 0.4))
    bpy.context.scene.collection.objects.link(co); co.parent = MUNDO_ROOT
    return [po, co]


def tendidos():
    _quitar(exactos={"w_postes", "w_cables"})
    madera = M.mat_color("w_madera_poste", (0.20, 0.14, 0.09), 0.9)
    conc = M.mat_color("w_concreto_poste", (0.45, 0.44, 0.41), 0.9)
    return (postes("w_postes_der", 9.5, 9.5, madera, 48.0, 11.0, 0.8, True)
            + postes("w_postes_izq", -17.5, 10.5, conc, 64.0, 29.0, 1.0, False))


# ---------------------------------------------------------------- plants: tropical green + dry straw
def _col_seca():
    """A copy of the grass collection with every material's colour pushed to straw (keeps the texture's light/dark)."""
    src = bpy.data.collections["w_pasto"]
    col = M._col_oculta("w_pasto_seco")
    for o in src.objects:
        c = o.copy(); c.data = o.data.copy()
        c.data.materials.clear()
        for m in o.data.materials:
            m2 = m.copy()
            nt = m2.node_tree; p = nt.nodes["Principled BSDF"]
            lig = p.inputs["Base Color"].links
            if lig:
                fuente = lig[0].from_socket
                nt.links.new(_mezcla(nt, fuente, (0.62, 0.48, 0.22), 0.85, "COLOR"), p.inputs["Base Color"])
            else:
                p.inputs["Base Color"].default_value = (0.45, 0.34, 0.15, 1)
            c.data.materials.append(m2)
        col.objects.link(c)
    return col


def plantas():
    _quitar(exactos={f"w_{n}{l:+d}" for n in ("corte", "pasto", "arbusto", "pasto_lejos", "copa") for l in (1, -1)})   # mundo.plantas' scatters
    seco = _col_seca()
    pasto, arbusto, copa = (bpy.data.collections[n] for n in ("w_pasto", "w_arbusto", "w_copa"))
    copas = M._col_oculta("w_copa_cerca")
    cc = M.copa_lejana(); cc.name = "w_copa_cerca"; copas.objects.link(cc)
    mc = bpy.data.materials["w_copa_verde"]; nt = mc.node_tree
    azar = _nodo(nt, "ShaderNodeObjectInfo").outputs["Random"]
    nt.links.new(_mezcla(nt, (0.07, 0.13, 0.04), (0.16, 0.20, 0.06), azar), nt.nodes["Principled BSDF"].inputs["Base Color"])
    out, copias = [], range(-2, 4)
    for lado, x_in, s in ((1, 7.6, 10), (-1, 16.6, 20)):
        for nombre, col, a, b, dens, esc, sd in (
                ("corte", seco, 0.0, 2.5, 1.6, (0.5, 0.9), s + 8),
                ("pasto", pasto, 2.5, 9, 2.0, (1.4, 2.6), s),
                ("seco", seco, 1.0, 12, 2.2, (1.3, 2.5), s + 4),
                ("arbusto", arbusto, 1.5, 34, 0.07, (1.2, 2.6), s + 1),
                ("pasto_lejos", pasto, 9, 34, 0.5, (2.2, 3.6), s + 2),
                ("seco_lejos", seco, 12, 34, 0.35, (2.0, 3.4), s + 5),
                ("copa_cerca", copas, 12, 55, 0.003, (1.8, 3.2), s + 6),
                ("copa", copa, 22, 260, 0.006, (3.0, 6.5), s + 3)):
            out.append(M.dispersar(f"w_{nombre}{lado:+d}", col, lado * (x_in + a), lado * (x_in + b), dens, esc, sd, MUNDO_ROOT, PER, copias))
    return out


# ---------------------------------------------------------------- day: sky, sun, haze, ground, lamps off
def dia():
    sc = bpy.context.scene
    w = sc.world; nt = w.node_tree
    for n in list(nt.nodes):
        if n.type not in ("OUTPUT_WORLD", "BACKGROUND"):
            nt.nodes.remove(n)
    bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
    d = _nodo(nt, "ShaderNodeVectorMath", operation="NORMALIZE")
    nt.links.new(_nodo(nt, "ShaderNodeTexCoord").outputs["Object"], d.inputs[0])
    sep = _nodo(nt, "ShaderNodeSeparateXYZ"); nt.links.new(d.outputs[0], sep.inputs["Vector"])
    t = _rango(nt, sep.outputs["Z"], 0.0, 0.75)                       # 0 at the horizon, 1 high up
    nubes = _rango(nt, _ruido(nt, d.outputs[0], 2.2, 8), 0.35, 0.7, 0.82, 1.08)  # overcast: patches a little greyer / whiter
    cielo = _mezcla(nt, CIELO["horizonte"], CIELO["cenit"], t)
    cielo = _mezcla(nt, cielo, (1, 1, 1), nubes, "MULTIPLY")
    suelo = _rango(nt, sep.outputs["Z"], 0.0, -0.05)                    # below the horizon: haze, the ground hides it anyway
    nt.links.new(_mezcla(nt, cielo, CIELO["horizonte"], suelo), bg.inputs["Color"])
    bg.inputs["Strength"].default_value = CIELO["fuerza"]
    sc.view_settings.exposure = CIELO["exposicion"]
    luna = bpy.data.objects["luna"].data                               # the moon becomes a weak, soft, warm-white sun behind cloud
    luna.energy, luna.angle, luna.color = SOL["energia"], math.radians(SOL["angulo"]), SOL["color"]
    fog = next(n for n in bpy.data.objects["w_niebla"].data.materials[0].node_tree.nodes if n.type == "PRINCIPLED_VOLUME")
    fog.inputs["Density"].default_value = NIEBLA["densidad"]
    fog.inputs["Color"].default_value = (*NIEBLA["color"], 1)
    for l in bpy.data.lights:
        if l.name.startswith("luz_poste"):
            l.energy = 0.0                                              # the road lamps are off in daylight
    bpy.data.materials["lampara"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.0
    if "cerro" in bpy.data.materials:                                   # the far hills: hazy green, not a night silhouette
        bpy.data.materials["cerro"].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.20, 0.27, 0.18, 1)
    # ground: dry straw and tropical green in 25 m patches
    suelo_m = bpy.data.objects["w_terreno"].data.materials[0]
    nt = suelo_m.node_tree
    co = next(n for n in nt.nodes if n.type == "TEX_COORD").outputs["Object"]
    nt.nodes["tinte"].inputs[7].default_value = (1, 1, 1, 1)
    nt.links.new(_mezcla(nt, (1.7, 1.4, 0.85), (0.9, 1.15, 0.55), _rango(nt, _ruido(nt, co, 1 / 22, 4), 0.50, 0.66)), nt.nodes["tinte"].inputs[7])
    # the far lamps' road-side guardrail and the night delineators give way to the barrier and the open shoulder
    n = _quitar(prefijos=("fantasma_", "poste_riel_", "reflejante_riel_"), exactos={"riel"})
    n += _quitar(prefijos=tuple(f"reflejante_{i}" for i in range(0, 10)))
    print("CAMINO tramo: quitados", n, "objetos (guardarriel derecho, delineadores)", flush=True)


nuevo = superficies() + rayas() + barrera() + tendidos() + plantas()
dia()
_ocultar([o for o in nuevo if not o.name.startswith(("w_carretera_op", "w_acot", "w_grava"))])
print("CAMINO MX140: carriles 2+2, barrera NJ x", X_BARRERA, "oncoming yellow", X_OP["amarilla"], "objetos nuevos", len(nuevo), flush=True)
