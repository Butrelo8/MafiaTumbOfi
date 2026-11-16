"""road3's signs, chevrons and the denser lamp row, built on the straight road (camino_curva.py bends them with everything else).
Exec'd by camino_mx140.py in its namespace (MONTAJE_CAMINO=road3), after camino_edificios.py (reuses its _malla, _mat_ed, _obj).

  gantry A    an overhead sign over our two lanes at y 44: a green panel, an up arrow and "La X we"
  guide B     a roadside two-post sign at (8.6, 33): "La X we" and "12 km"
  chevrons    yellow squares with a black "<" on the outside of the bend (x +6.9), every 14 m from y 70, facing the traffic
  lamps       extra instances of the existing road lamp (the same collection and datablock) between the 64 m ones, from y 104
Mexican SCT style (green guide sign, white letters, white border, yellow chevrons). Generic Blender font, no logos: the letters are
only what the owner asked for ("La X we"). Retroreflection is faked with a weak emission, and the faces do not scatter in the fog.
Everything is named e3_* (an `objeto` for the bend) and is hidden in the viewport with the rest of `nuevo`.
"""
import bmesh

VERDE = (0.0, 0.28, 0.12)
POSTE_GRIS = (0.30, 0.30, 0.30)
CHEVRON_X = 6.9


def _mat_fijo(nombre, base, emis=None, fuerza=0.0, rough=0.5):
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*base, 1); p.inputs["Roughness"].default_value = rough
    if emis:
        p.inputs["Emission Color"].default_value = (*emis, 1); p.inputs["Emission Strength"].default_value = fuerza
    return m


def _malla_poly(nombre, caras, m):
    """faces in the kit frame (x, y, z) -> mesh."""
    bm = bmesh.new()
    for f in caras:
        bm.faces.new([bm.verts.new(v) for v in f])
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free(); me.materials.append(m)
    return me


def _trazo(p0, p1, ancho, y=0.0):
    """a thick segment in the XZ plane as one quad"""
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    n = (dx * dx + dz * dz) ** 0.5
    nx, nz = -dz / n * ancho / 2, dx / n * ancho / 2
    return [(p0[0] + nx, y, p0[1] + nz), (p1[0] + nx, y, p1[1] + nz), (p1[0] - nx, y, p1[1] - nz), (p0[0] - nx, y, p0[1] - nz)]


def _texto(nombre, s, cap, loc, m, ancho_max=None):
    """Blender's built-in font, emboldened, facing -Y (toward the traffic), centred."""
    cu = bpy.data.curves.new(nombre, "FONT")
    cu.body, cu.align_x, cu.align_y = s, "CENTER", "CENTER"
    cu.size, cu.offset = cap / 0.72, 0.045 * cap
    cu.materials.append(m)
    o = bpy.data.objects.new(nombre, cu)
    o.location, o.rotation_euler = loc, (math.pi / 2, 0, 0)
    o.visible_volume_scatter = False
    bpy.context.scene.collection.objects.link(o); o.parent = MUNDO_ROOT
    if ancho_max:
        bpy.context.view_layer.update()
        if o.dimensions.x > ancho_max:
            o.scale = (ancho_max / o.dimensions.x,) * 3
    return o


def _panel(nombre, x, y, z0, w, h, lineas, flecha=False):
    """Green panel with a white frame, facing -Y; its back face at y + 0.06. lineas: [(text, cap m, z offset from the centre)]."""
    verde = _mat_fijo("e3_verde", VERDE, VERDE, 0.9)
    blanco = _mat_fijo("e3_blanco", (0.8, 0.8, 0.78), (0.95, 0.95, 0.9), 2.2)
    out = [_obj(nombre, _malla(nombre, [(-w / 2, w / 2, -0.03, 0.03, 0, h)], verde), (x, y, z0), vol=False)]
    b = 0.07
    marco = [(-w / 2, w / 2, -0.045, 0.0, 0, b), (-w / 2, w / 2, -0.045, 0.0, h - b, h), (-w / 2, -w / 2 + b, -0.045, 0.0, 0, h), (w / 2 - b, w / 2, -0.045, 0.0, 0, h)]
    out.append(_obj(nombre + "_marco", _malla(nombre + "_marco", marco, blanco), (x, y, z0), vol=False))
    zc = z0 + h / 2
    for s, cap, dz, dx in lineas:
        out.append(_texto(nombre + "_" + s.replace(" ", ""), s, cap, (x + dx, y - 0.06, zc + dz), blanco, ancho_max=w - 1.0))
    if flecha:   # an up arrow, left of the text
        ax = x - w / 2 + 0.9
        caras = [[(ax - 0.12, -0.05, zc - 0.7), (ax + 0.12, -0.05, zc - 0.7), (ax + 0.12, -0.05, zc + 0.15), (ax - 0.12, -0.05, zc + 0.15)],
                 [(ax - 0.5, -0.05, zc + 0.15), (ax + 0.5, -0.05, zc + 0.15), (ax, -0.05, zc + 0.75)]]
        out.append(_obj(nombre + "_flecha", _malla_poly(nombre + "_flecha", caras, blanco), (0, y, 0), vol=False))
    return out


def _pilar(nombre, x, y, z0, z1, gris, ancho=0.45):
    return _obj(nombre, _malla(nombre, [(-ancho / 2, ancho / 2, -ancho / 2, ancho / 2, z0, z1)], gris), (x, y, 0))


def portico(y=44.0):
    """The overhead sign: two columns (right shoulder x +7.6, left shoulder x -4.25), a beam, one panel over our two lanes."""
    gris = _mat_fijo("e3_gris", POSTE_GRIS, rough=0.7)
    xr, xl = 7.6, -4.25
    out = [_pilar("e3_portico_der", xr, y, 0, 7.9, gris), _pilar("e3_portico_izq", xl, y, 0, 7.9, gris),
           _obj("e3_viga", _malla("e3_viga", [(xl, xr, -0.2, 0.2, 7.3, 7.9)], gris), (0, y, 0))]
    w = 6.4
    out += _panel("e3_letrero_A", (xl + xr) / 2, y - 0.25, 5.2, w, 2.4, [("La X we", 0.95, 0.12, 0.5)], flecha=True)
    return out


def guia(x=8.6, y=33.0):
    """The roadside guide sign: a green panel on two posts, right shoulder."""
    gris = _mat_fijo("e3_gris_b", POSTE_GRIS, rough=0.7)
    w = 3.9
    out = [_pilar("e3_guia_p1", x - w / 2 + 0.5, y, 0, 3.6, gris, 0.16), _pilar("e3_guia_p2", x + w / 2 - 0.5, y, 0, 3.6, gris, 0.16)]
    out += _panel("e3_letrero_B", x, y - 0.12, 1.9, w, 1.9, [("La X we", 0.55, 0.38, 0.0), ("26 km", 0.42, -0.4, 0.0)])  # Xalapa: 26 km by road from Cerro Gordo (OSRM, 2026-11-16)
    return out


def tablero(x=8.6, y=270.0):
    """SCT distance board, right shoulder, for the westbound road from Cerro Gordo (19.438 N, 96.690 W) to Xalapa (owner 2026-11-16:
    only the signs to Xalapa say "La X we"; the rest name real places). Road distances from OSRM on OSM data: Dos Ríos 12.5 km,
    El Lencero 16.0 km, Xalapa 26.1 km (the city's first exit). At y 270 it passes during ruta.py's caja section; the stills do not see it."""
    gris = _mat_fijo("e3_gris_t", POSTE_GRIS, rough=0.7)
    w = 4.6
    out = [_pilar("e3_tablero_p1", x - w / 2 + 0.6, y, 0, 4.2, gris, 0.16), _pilar("e3_tablero_p2", x + w / 2 - 0.6, y, 0, 4.2, gris, 0.16)]
    out += _panel("e3_tablero", x, y - 0.12, 1.9, w, 2.3, [("Dos Ríos  12 km", 0.36, 0.62, 0.0), ("El Lencero  16 km", 0.36, 0.0, 0.0),
                                                       ("La X we  26 km", 0.36, -0.62, 0.0)])
    return out


def chevrones(y_ini=58.0, y_fin=250.0, paso=12.0):
    """Yellow squares (1.2 m, a bit over SCT size so they read at 100 m) with a black '<' on a post, outside of the bend, facing the traffic: they point into the (left) turn."""
    amarillo = _mat_fijo("e3_chevron", (0.85, 0.62, 0.02), (1.0, 0.72, 0.03), 4.0)
    negro = _mat_fijo("e3_chevron_negro", (0.01, 0.01, 0.01), rough=0.9)
    gris = _mat_fijo("e3_gris_c", POSTE_GRIS, rough=0.7)
    placa = _malla("e3_chevron_placa", [(-0.6, 0.6, -0.03, 0.0, 0, 1.2)], amarillo)
    sig = _malla_poly("e3_chevron_flecha", [_trazo((0.23, 1.04), (-0.23, 0.6), 0.16, -0.035),
                                            _trazo((-0.23, 0.6), (0.23, 0.16), 0.16, -0.035)], negro)
    poste = _malla("e3_chevron_poste", [(-0.05, 0.05, -0.05, 0.05, 0, 1.9)], gris)
    esc = (1.4, 1.0, 1.4)    # 1.7 m squares, 1.9 m up: oversized on purpose, they must read at 80-150 m in the fog
    out, y, i = [], y_ini, 0
    while y <= y_fin:
        if abs(((y - 8.0) % 64.0) - 0.0) > 3.0 and abs(((y - 8.0) % 64.0) - 64.0) > 3.0:   # not on a lamp pole
            out += [_obj(f"e3_chev_placa_{i}", placa, (CHEVRON_X, y, 1.9), esc=esc, vol=False), _obj(f"e3_chev_flecha_{i}", sig, (CHEVRON_X, y, 1.9), esc=esc, vol=False),
                    _obj(f"e3_chev_poste_{i}", poste, (CHEVRON_X, y, 0))]
        y += paso
        i += 1
    return out


def farolas_extra(y_desde=100.0):
    """More instances of the road lamp collection (pole, arm, lamp, spot light), 32 m after each existing one (they stand every 64 m at
    y = 8 + 64 k, before the bend): the row reads the arc at night."""
    col = bpy.data.collections["w_farola"]
    out = []
    for k in range(-6, 14):
        ye = 64.0 * k + 32.0
        if ye + 8.0 < y_desde or ye + 8.0 > 280.0:
            continue
        e = bpy.data.objects.new(f"w_farola_x{k}", None)
        e.instance_type, e.instance_collection = "COLLECTION", col
        e.location = (1.0, ye, 0)
        bpy.context.scene.collection.objects.link(e); e.parent = MUNDO_ROOT
        out.append(e)
    return out


def puente(y=128.0):
    """A plain pedestrian footbridge over both carriageways (ref 1): a concrete deck at 5.5 m, yellow rails, a stair tower at each end.
    Boxes only; at 128 m in the fog it reads as a silhouette across the road."""
    conc = _mat_fijo("e3_puente", (0.34, 0.34, 0.33), rough=0.9)
    rail = _mat_fijo("e3_puente_baranda", (0.55, 0.45, 0.06), rough=0.6)
    x0, x1 = -16.5, 10.5
    cuerpo = _malla("e3_puente_cuerpo", [(x0, x1, -1.3, 1.3, 5.5, 5.9), (x0 - 1.5, x0 + 1.5, -1.3, 1.3, 0, 5.9), (x1 - 1.5, x1 + 1.5, -1.3, 1.3, 0, 5.9),
                                          (-5.45, -4.45, -1.3, 1.3, 0, 5.5)], conc)
    barandas = _malla("e3_puente_barandas", [(x0, x1, a, a + 0.06, 5.9, 7.0) for a in (-1.3, 1.24)] + [(x0, x1, -1.3, 1.3, 6.9, 7.0)], rail)
    out = [_obj("e3_puente_cuerpo", cuerpo, (0, y, 0)), _obj("e3_puente_baranda", barandas, (0, y, 0))]
    return out


def destellos(y_desde=70.0, y_hasta=280.0):
    """A glowing ball on each far lamp head (the lamp heads are 0.4 m: 2 px at 100 m, lost in the fog): lamps stand at y = 8 + 32 j, head at
    x 4.95 (1 m out, farolas_fuera), z 8.85."""
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.9)
    me = bpy.data.meshes.new("e3_destello"); bm.to_mesh(me); bm.free()
    me.materials.append(_mat_fijo("e3_destello", (0.0, 0.0, 0.0), (1.0, 0.78, 0.45), 25.0))
    return [_obj(f"e3_destello_{j}", me, (4.95, 8.0 + 32.0 * j, 8.85), vol=False) for j in range(0, 20) if y_desde <= 8.0 + 32.0 * j <= y_hasta]


def letreros():
    out = portico() + guia() + tablero() + chevrones() + farolas_extra() + destellos() + puente()
    print("CAMINO letreros:", len(out), "objetos (portico y=44, guia (8.6, 33), chevrones desde y 70, farolas extra desde y 104)", flush=True)
    return out
