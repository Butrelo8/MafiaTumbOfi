"""road2's roadside at night, exec'd by camino_mx140.py in its namespace (MONTAJE_CAMINO=noche). No Geometry Nodes, no textures.

A seeded Python instancer over one period, copied along Y0..Y1 (see edificios()): kits are shared meshes, each instance its own object with its own
colour and lit/dark in Object Color (RGB = colour, A = lit), a mirrored or not, a setback jitter and gaps between them.
  right  (x +11..+17)  a lit shop (one or two storeys), a barda wall as filler, ONE generic gas-station canopy: the only new real light
  left   (x -24..-34)  dark silhouettes with a few lit windows; one oncoming car beyond the barrier (one pair of headlights)
Signs and windows are their own objects with visible_volume_scatter off, so they do not light the fog. Generic signs, no brands.
Kit frame: x = 0 is the front face, +x goes back from the road, y along the road, z up.
"""
import random

from mathutils import Matrix, Vector

SEMILLA = 140
LUGAR_DOSEL = (15.5, 62.0)   # x, y of the canopy's centre: the brightest patch, ahead and to the right of the screen truck at scene 5
PAREDES = [(0.55, 0.50, 0.40), (0.50, 0.52, 0.56), (0.60, 0.36, 0.28), (0.36, 0.50, 0.45), (0.62, 0.60, 0.55), (0.52, 0.42, 0.20)]
LETREROS = [(1.0, 0.25, 0.15), (0.2, 0.7, 1.0), (1.0, 0.85, 0.2), (0.3, 1.0, 0.5), (1.0, 1.0, 1.0)]
VENTANAS = [(1.0, 0.78, 0.45), (0.85, 0.92, 1.0), (1.0, 0.9, 0.7)]


def _caja_kit(bm, x0, x1, y0, y1, z0, z1):
    bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)) @ Matrix.Diagonal((x1 - x0, y1 - y0, z1 - z0, 1)))


def _malla(nombre, cajas, m):
    bm = bmesh.new()
    for c in cajas:
        _caja_kit(bm, *c)
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free(); me.materials.append(m)
    return me


def _mat_ed(nombre, emite, base=None):
    """Object Color -> base colour (walls) or emission colour; Object Alpha x `emite` -> emission strength."""
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    p.inputs["Roughness"].default_value = 0.85
    if emite:
        p.inputs["Base Color"].default_value = (*(base or (0.02, 0.02, 0.02)), 1)
        nt.links.new(oi.outputs["Color"], p.inputs["Emission Color"])
        k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = emite
        nt.links.new(oi.outputs["Alpha"], k.inputs[0]); nt.links.new(k.outputs[0], p.inputs["Emission Strength"])
    else:
        nt.links.new(oi.outputs["Color"], p.inputs["Base Color"])
    return m


def _obj(nombre, me, loc, rot_z=0.0, esc=(1, 1, 1), color=None, vol=True):
    o = bpy.data.objects.new(nombre, me)
    o.location, o.rotation_euler.z, o.scale = loc, rot_z, esc
    if color:
        o.color = color
    o.visible_volume_scatter = vol
    bpy.context.scene.collection.objects.link(o); o.parent = MUNDO_ROOT
    return o


def _luz_area(nombre, loc, w, h, energia, color):
    ld = bpy.data.lights.new(nombre, "AREA")
    ld.shape, ld.size, ld.size_y, ld.energy, ld.color = "RECTANGLE", w, h, energia, color
    o = bpy.data.objects.new(nombre, ld); o.location = loc          # an area light faces -Z: straight down
    bpy.context.scene.collection.objects.link(o); o.parent = MUNDO_ROOT
    return o


def _dosel(x, y):
    """One generic gas-station canopy: roof on four columns, a lit ceiling, two pumps, a lit price pylon, an area light."""
    cons = _mat_ed("e_dosel", 0.0)
    blanco = bpy.data.materials.new("e_dosel_blanco"); blanco.use_nodes = True
    blanco.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.55, 0.57, 0.58, 1)
    luz_m = _mat_ed("e_dosel_luz", 5.0)
    pared = [(-4.5, 4.5, -8.0, 8.0, 5.0, 5.5)] + [(cx - 0.22, cx + 0.22, cy - 0.22, cy + 0.22, 0, 5.0) for cx in (-3.2, 3.2) for cy in (-6.5, 6.5)]
    pumps = [(-0.3, 0.3, py - 0.25, py + 0.25, 0, 1.3) for py in (-3.0, 3.0)]
    losa = [(-8.0, 8.0, -14.0, 14.0, 0.0, 0.03)]
    me_blanco = _malla("e_dosel_cuerpo", pared + pumps, blanco)
    me_losa = _malla("e_dosel_losa", losa, bpy.data.materials.new("e_dosel_losa")); me_losa.materials[0].use_nodes = True
    me_losa.materials[0].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.30, 0.30, 0.30, 1)
    me_techo = _malla("e_dosel_techo", [(-4.0, 4.0, -7.5, 7.5, 4.94, 4.98)], luz_m)      # the lit ceiling panel
    me_faja = _malla("e_dosel_faja", [(-4.55, -4.5, -8.0, 8.0, 5.05, 5.45)], luz_m)       # the lit band on the road-facing edge
    me_pilon = _malla("e_dosel_pilon", [(-0.1, 0.1, -0.1, 0.1, 0, 6.5), (-0.15, 0.15, -1.3, 1.3, 4.4, 6.5)], cons)
    me_pilon_l = _malla("e_dosel_pilon_luz", [(-0.2, -0.16, -1.2, 1.2, 4.5, 6.4)], luz_m)
    out = [_obj("e_dosel_cuerpo", me_blanco, (x, y, 0)), _obj("e_dosel_losa", me_losa, (x, y, 0)),
           _obj("e_dosel_techo", me_techo, (x, y, 0), color=(0.9, 0.97, 1.0, 1.0), vol=False),
           _obj("e_dosel_faja", me_faja, (x, y, 0), color=(0.2, 0.7, 1.0, 1.0), vol=False),
           _obj("e_pilon", me_pilon, (x - 5.0, y + 14.0, 0), color=(0.12, 0.12, 0.12, 1)),
           _obj("e_pilon_luz", me_pilon_l, (x - 5.0, y + 14.0, 0), color=(1.0, 0.8, 0.3, 1.0), vol=False)]
    out.append(_luz_area("e_dosel_luz", (x, y, 4.9), 8.0, 15.0, 1400.0, (0.92, 0.97, 1.0)))
    return out


def _tienda(rnd):
    cons = _mat_ed("e_pared", 0.0)
    letrero_m, ventana_m = _mat_ed("e_letrero", 3.0), _mat_ed("e_ventana", 1.3)
    ancho = 5.0
    pared = lambda alto: _malla(f"e_pared_{alto}", [(0, 7, -ancho, ancho, 0, alto), (-1.4, 0, -ancho, ancho, 3.0, 3.12), (-0.1, 7.1, -ancho - 0.1, ancho + 0.1, alto, alto + 0.35)], cons)
    kits = dict(pared1=pared(3.8), pared2=pared(7.0),
                letrero=_malla("e_letrero", [(-0.16, -0.02, -3.6, 3.6, 3.22, 3.72)], letrero_m),
                vitrina=_malla("e_vitrina", [(-0.05, 0.0, -4.0, -0.7, 0.45, 2.7), (-0.05, 0.0, 0.7, 4.0, 0.45, 2.7)], ventana_m),
                altas=_malla("e_altas", [(-0.05, 0.0, y0, y0 + 1.6, 4.6, 6.0) for y0 in (-4.0, -1.2, 1.6)], ventana_m))
    return kits


def _barda(rnd):
    return _malla("e_barda", [(0, 0.3, -0.5, 0.5, 0, 2.3), (-0.1, 0.4, -0.5, 0.5, 2.3, 2.45)], _mat_ed("e_barda", 0.0))


def _silueta():
    oscuro = bpy.data.materials.new("e_silueta"); oscuro.use_nodes = True
    oscuro.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.012, 0.012, 0.014, 1)
    oscuro.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    return _malla("e_silueta", [(0, 9, -5.0, 5.0, 0, 5.0)], oscuro), _malla("e_silueta_v", [(-0.05, 0.0, y0, y0 + 0.9, 1.4, 2.3) for y0 in (-3.6, -0.5, 2.6)], _mat_ed("e_silueta_ventana", 1.3))


def _auto_opuesto(y):
    """One oncoming car beyond the barrier (the nearer oncoming lane's centre, x -7.8), facing -Y, one pair of headlights."""
    x = -7.8
    cuerpo = bpy.data.materials.new("e_auto"); cuerpo.use_nodes = True
    cuerpo.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.03, 0.03, 0.035, 1)
    me = _malla("e_auto", [(-0.9, 0.9, -2.2, 2.2, 0.25, 1.35)], cuerpo)
    out = [_obj("e_auto", me, (x, y, 0))]
    faro_m = _mat_ed("e_faro", 400.0)
    me_f = _malla("e_faro", [(-0.12, 0.12, -0.04, 0.04, 0.55, 0.75)], faro_m)
    for dx in (-0.65, 0.65):
        out.append(_obj("e_faro", me_f, (x + dx, y - 2.2, 0), color=(1.0, 0.95, 0.85, 1.0), vol=False))
        ld = bpy.data.lights.new("e_faro_luz", "SPOT")
        ld.energy, ld.color, ld.spot_size, ld.spot_blend, ld.shadow_soft_size = 700.0, (1.0, 0.93, 0.8), math.radians(50), 0.5, 0.08
        o = bpy.data.objects.new("e_faro_luz", ld)
        o.location = (x + dx, y - 2.3, 0.65)
        o.rotation_euler = Vector((0, -1, -0.07)).to_track_quat("-Z", "Y").to_euler()   # aimed down the road, towards the camera
        bpy.context.scene.collection.objects.link(o); o.parent = MUNDO_ROOT
        out.append(o)
    return out


def edificios():
    """Periodic (movimiento-plan §5.1): one period y in [0, PER) of the roadside, copied at k·PER for k in -2..N_PER-1 like the
    plants (mundo.dispersar), so a 240-frame loop clip wraps clean (the world slides PER per loop). No item crosses the period's
    end. The canopy and the oncoming car stay one-offs: scene 5's composition, hundreds of metres behind the band loop."""
    rnd = random.Random(SEMILLA)
    k = _tienda(rnd)
    barda = _barda(rnd)
    sil, sil_v = _silueta()
    per = []  # (name, mesh, x, yc, rot_z, scale, colour, volume) in one period
    # ---- right: shops, barda as filler, gaps; clear of the canopy (its period-local y)
    y = rnd.uniform(0, 10)
    i = 0
    while True:
        tipo = rnd.choices(("tienda", "barda", "nada"), (0.5, 0.35, 0.15))[0]
        largo = rnd.uniform(10, 14) if tipo == "tienda" else rnd.uniform(10, 28) if tipo == "barda" else rnd.uniform(8, 25)
        if y + largo > PER:
            break
        yc = y + largo / 2
        if tipo != "nada" and abs(yc - LUGAR_DOSEL[1]) > 24:
            esp = rnd.choice((-1, 1))
            if tipo == "tienda":
                x = 11.0 + rnd.uniform(0, 6)
                esc = (rnd.uniform(0.85, 1.15), largo / 10.0 * esp, 1)
                alto = rnd.choice(("pared1", "pared1", "pared2"))
                per.append((f"e_tienda_{i}", k[alto], x, yc, 0.0, esc, (*rnd.choice(PAREDES), 1), True))
                lit = lambda p: 1.0 if rnd.random() < p else 0.0
                per.append((f"e_letrero_{i}", k["letrero"], x, yc, 0.0, esc, (*rnd.choice(LETREROS), lit(0.75)), False))
                per.append((f"e_vitrina_{i}", k["vitrina"], x, yc, 0.0, esc, (*rnd.choice(VENTANAS), lit(0.65)), False))
                if alto == "pared2":
                    per.append((f"e_altas_{i}", k["altas"], x, yc, 0.0, esc, (*rnd.choice(VENTANAS), lit(0.4)), False))
            else:
                x = 8.5 + rnd.uniform(0, 2.5)
                per.append((f"e_barda_{i}", barda, x, yc, 0.0, (1, largo, 1), (*rnd.choice(PAREDES), 1), True))
        y += largo + rnd.uniform(2, 16) * (rnd.random() < 0.7) + (rnd.uniform(15, 60) if rnd.random() < 0.15 else 0.0)
        i += 1
    # ---- left: dark silhouettes, a few lit windows
    y, i = rnd.uniform(0, 20), 0
    while True:
        largo = rnd.uniform(12, 26)
        if y + largo > PER:
            break
        x = -(24.0 + rnd.uniform(0, 10))
        esc = (1, largo / 10.0, rnd.uniform(0.7, 1.5))
        per.append((f"e_sil_{i}", sil, x, y + largo / 2, math.pi, esc, None, True))
        if rnd.random() < 0.55:
            per.append((f"e_sil_v_{i}", sil_v, x, y + largo / 2, math.pi, (1, esc[1], 1), (1.0, 0.8, 0.45, 1.0), False))
        y += largo + rnd.uniform(6, 40)
        i += 1
    out = [_obj(f"{n}_p{c + 2}", me, (x, yc + c * PER, 0), rz, esc, col, vol=v)
           for c in range(-2, N_PER) for n, me, x, yc, rz, esc, col, v in per]
    out += _dosel(*LUGAR_DOSEL)
    out += _auto_opuesto(70.0)
    print("CAMINO edificios:", len(out), "objetos,", len(per), "por periodo de", PER, "m; dosel en", LUGAR_DOSEL, flush=True)
    return out
