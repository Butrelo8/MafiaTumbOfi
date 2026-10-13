"""La troca del atrio (ticket 07, paso E2 del alcance): pickup doble cabina negra estilo Lobo, sin emblemas.

Medidas de una F-150 SuperCrew con caja de 5.5 ft: largo 5.89 m, ancho 2.03 m sin espejos, alto 1.96 m, distancia entre
ejes 3.68 m, llanta 275/55R20 (0.80 m). Referencia de look y pose: tmp/07/tablero/atrio_C2_lobo_elegida.png.
El cuerpo sale de su perfil lateral extruido a lo ancho; arcos de rueda y caja recortados con boolean. Frente = +Y
local, ancho en X, base en z 0. Sólo para la maqueta y la profundidad: no se exporta a la web.

    tr = {}; exec(open(r"E:\\Cursor Projects\\MTO\\blender\\troca.py").read(), tr); tr["troca"](m, (x, y, 0), giro)
"""
import math

import bmesh
import bpy

LARGO, ANCHO, ALTO = 5.89, 2.03, 1.96
EJE_DEL, EJE_TRAS = 1.62, -2.06          # y de los ejes (3.68 m entre ellos; voladizo trasero más largo)
R_LLANTA, ANCHO_LLANTA, R_RIN = 0.40, 0.28, 0.255
Y0, Y1 = -2.99, 2.90                       # defensa trasera y delantera
COFRE, CINTURA = 1.28, 1.30                # alto del cofre en el parabrisas y línea de cintura
Y_PARABRISAS, Y_TECHO0, Y_TECHO1, Y_CABINA = 1.05, 0.30, -0.95, -1.12  # base del parabrisas, techo, medallón


def _mat(nombre, color, rugoso=0.4, metal=0.0, emision=0.0):
    m = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    m.diffuse_color = (*color, 1)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rugoso
    b.inputs["Metallic"].default_value = metal
    if emision:
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = emision
    return m


def _perfil(nombre, puntos, x0, x1, mat):
    """Polígono en el plano YZ extruido de x0 a x1."""
    me = bpy.data.meshes.new(nombre)
    bm = bmesh.new()
    vs = [bm.verts.new((x0, y, z)) for y, z in puntos]
    cara = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[cara])
    for v in (e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)):
        v.co.x = x1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nombre, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def _caja(nombre, x0, x1, y0, y1, z0, z1, mat):
    return _perfil(nombre, [(y0, z0), (y1, z0), (y1, z1), (y0, z1)], x0, x1, mat)


def _cil_x(nombre, x0, x1, y, z, r, mat, v=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=x1 - x0, location=((x0 + x1) / 2, y, z),
                                        rotation=(0, math.pi / 2, 0))
    o = bpy.context.object
    o.name = nombre
    o.data.materials.append(mat)
    return o


def _restar(obj, cortador):
    b = obj.modifiers.new(cortador.name, "BOOLEAN")
    b.operation, b.object = "DIFFERENCE", cortador
    cortador.hide_render = cortador.hide_viewport = True


def troca(m, ubicacion, giro=0.0):
    pintura = _mat("troca_pintura", (0.012, 0.012, 0.014), rugoso=0.15)
    cromo = _mat("troca_cromo", (0.8, 0.8, 0.82), rugoso=0.1, metal=1.0)
    vidrio = _mat("troca_vidrio", (0.02, 0.025, 0.03), rugoso=0.05)
    hule = _mat("troca_hule", (0.02, 0.02, 0.02), rugoso=0.8)
    calavera = _mat("troca_calavera", (0.8, 0.02, 0.02), emision=3.0)
    faro = _mat("troca_faro", (0.9, 0.9, 0.85), emision=1.0)
    w = ANCHO / 2
    piezas = []
    # carrocería: estribo a 0.45, defensa al frente, cofre que baja 5 cm hacia la parrilla, cintura recta a la caja
    cuerpo = _perfil("troca_cuerpo", [(Y0 + 0.05, 0.45), (Y1 - 0.08, 0.45), (Y1, 0.62), (Y1, 1.22),
                                      (Y1 - 0.25, COFRE - 0.03), (Y_PARABRISAS, COFRE), (Y_CABINA, CINTURA),
                                      (Y0, CINTURA), (Y0, 0.62)], -w, w, pintura)
    for k, y in enumerate((EJE_DEL, EJE_TRAS)):  # arcos de rueda
        _restar(cuerpo, _cil_x(f"troca_arco_{k}", -w - 0.1, w + 0.1, y, R_LLANTA + 0.02, R_LLANTA + 0.07, hule))
    # la junta entre cabina y caja: sin ella, de lado se leía como sedán
    _restar(cuerpo, _caja("troca_caja_junta", -w - 0.1, w + 0.1, Y_CABINA - 0.07, Y_CABINA - 0.04, 0.5, 1.5, hule))
    _restar(cuerpo, _caja("troca_caja_hueco", -w + 0.09, w - 0.09, Y0 + 0.07, Y_CABINA - 0.08, 0.85, 1.5, hule))
    piezas.append(cuerpo)
    # cabina (más angosta: el vidrio se mete) con parabrisas inclinado y medallón casi vertical
    cab = _perfil("troca_cabina", [(Y_PARABRISAS, CINTURA - 0.01), (Y_TECHO0, ALTO), (Y_TECHO1, ALTO),
                                   (Y_CABINA, CINTURA - 0.01)], -w + 0.1, w - 0.1, pintura)
    piezas.append(cab)
    piezas.append(_perfil("troca_parabrisas", [(Y_PARABRISAS - 0.02, CINTURA + 0.02), (Y_TECHO0 + 0.04, ALTO - 0.04),
                                               (Y_TECHO0 + 0.01, ALTO - 0.04), (Y_PARABRISAS - 0.05, CINTURA + 0.02)],
                          -w + 0.16, w - 0.16, vidrio))
    piezas.append(_caja("troca_medallon", -w + 0.25, w - 0.25, Y_CABINA - 0.005, Y_CABINA + 0.01, CINTURA + 0.08,
                        ALTO - 0.08, vidrio))
    for lado in (-1, 1):  # ventanas laterales: delantera y trasera, con el poste B entre ellas
        x0, x1 = (w - 0.105, w - 0.095) if lado > 0 else (-w + 0.095, -w + 0.105)
        for nombre, (ya, yb) in (("del", (-0.05, Y_PARABRISAS - 0.25)), ("tras", (Y_TECHO1 + 0.05, -0.15))):
            piezas.append(_perfil(f"troca_ventana_{nombre}_{lado}", [(ya, CINTURA + 0.06), (yb, CINTURA + 0.06),
                                                                      (yb - 0.12, ALTO - 0.1), (ya, ALTO - 0.1)],
                                  x0, x1, vidrio))
        xa, xb = sorted((lado * (w - 0.03), lado * (w + 0.2)))
        piezas.append(_caja(f"troca_espejo_{lado}", xa, xb, 0.75, 0.9, 1.35, 1.58, pintura))
    # frente: parrilla de barras cromadas, faros, defensa cromada
    piezas.append(_caja("troca_parrilla", -0.62, 0.62, Y1 - 0.02, Y1 + 0.02, 0.72, 1.18, cromo))
    for k in range(4):
        piezas.append(_caja(f"troca_parrilla_barra_{k}", -0.6, 0.6, Y1 + 0.02, Y1 + 0.04, 0.78 + k * 0.11,
                            0.82 + k * 0.11, cromo))
    for lado in (-1, 1):
        piezas.append(_caja(f"troca_faro_{lado}", lado * 0.66 - 0.17, lado * 0.66 + 0.17, Y1 - 0.03, Y1 + 0.01,
                            0.95, 1.15, faro))
    piezas.append(_caja("troca_defensa_del", -w, w, Y1 - 0.05, Y1 + 0.12, 0.42, 0.68, cromo))
    # atrás: compuerta con su manija, calaveras verticales en las esquinas, defensa cromada con escalón
    piezas.append(_caja("troca_compuerta_manija", -0.12, 0.12, Y0 - 0.015, Y0 + 0.01, 1.16, 1.22, cromo))
    for lado in (-1, 1):
        x0, x1 = (w - 0.13, w - 0.01) if lado > 0 else (-w + 0.01, -w + 0.13)
        piezas.append(_caja(f"troca_calavera_{lado}", x0, x1, Y0 - 0.02, Y0 + 0.02, 0.88, 1.27, calavera))
    piezas.append(_caja("troca_defensa_tras", -w, w, Y0 - 0.16, Y0 + 0.05, 0.42, 0.66, cromo))
    # llantas y rines cromados, un poco afuera del costado
    for k, y in enumerate((EJE_DEL, EJE_TRAS)):
        for lado in (-1, 1):
            xa = lado * (w - 0.05)
            piezas.append(_cil_x(f"troca_llanta_{k}_{lado}", *sorted((xa, xa + lado * ANCHO_LLANTA)), y, R_LLANTA,
                                 R_LLANTA, hule))
            xr = xa + lado * ANCHO_LLANTA
            piezas.append(_cil_x(f"troca_rin_{k}_{lado}", *sorted((xr - lado * 0.02, xr + lado * 0.01)), y, R_LLANTA,
                                 R_RIN, cromo))
    # estribos cromados entre las ruedas
    for lado in (-1, 1):
        x0, x1 = (w - 0.02, w + 0.1) if lado > 0 else (-w - 0.1, -w + 0.02)
        piezas.append(_caja(f"troca_estribo_{lado}", x0, x1, EJE_TRAS + 0.55, EJE_DEL - 0.55, 0.36, 0.41, cromo))
    piv = bpy.data.objects.new("PROP_troca", None)
    bpy.context.collection.objects.link(piv)
    for o in piezas:
        o.parent = piv
    for o in bpy.data.objects:  # los cortadores también van con la troca
        if o.name.startswith(("troca_arco_", "troca_caja_")):
            o.parent = piv
    piv.location = ubicacion
    piv.rotation_euler = (0, 0, giro)
    return piv
