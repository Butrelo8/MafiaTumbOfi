"""Maquetas de producción del ticket 07 (paso E1 del alcance): vestidor (camarín), cripta y atrio.

Decisiones en .wayfinder/santuario/tickets/07-guion-espacios.md; los encuadres salen de las previas elegidas
(tmp/07/tablero/). Como transicion.py: sólo geometría, cámara y la profundidad; el look lo pone Klein. Cada espacio
vive en su propio sitio del mundo (la sacristía está en x 40), para que las transiciones E6–E8 los puedan juntar.
No toca nave ni sacristía: usa los ayudantes de transicion.py y los assets de assets.py sin cambiarlos.

Sin UI, sólo CPU (la GPU la tiene otro rol): gris en workbench, profundidad en Cycles por CPU.
    blender.exe -b --factory-startup --python espacios07.py -- <carpeta> [vestidor cripta atrio] [escritorio movil]
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

RAIZ = r"E:\Cursor Projects\MTO\blender"
T = {}
exec(open(os.path.join(RAIZ, "transicion.py"), encoding="utf-8").read(), T)
_caja, _cil, _boveda, _barra = T["_caja"], T["_cil"], T["_boveda"], T["_barra"]

X_VESTIDOR, X_CRIPTA, X_ATRIO = 80, 120, 160
# Cámaras (posición, punto al que mira, lente, shift_y) por espacio y formato, relativas al origen del espacio.
# Escritorio: las de las previas elegidas. Móvil: el sujeto arriba y el hueco abajo (ticket 03), lente y shift del 06.
CAMARAS = {
    "vestidor": {"escritorio": ((-2.0, -2.4, 1.55), (1.2, 2.2, 1.5), 35, 0.0),
                 "movil": ((-1.2, -2.6, 1.55), (1.5, 2.4, 1.75), 28, -0.25)},
    "cripta": {"escritorio": ((-1.3, -1.0, 1.3), (1.0, 3.5, 1.2), 35, 0.0),
               "movil": ((-0.6, -1.3, 1.3), (0.9, 3.3, 1.35), 28, -0.25)},
    "atrio": {"escritorio": ((-5.5, -3.5, 1.4), (0.0, 9.0, 3.0), 35, 0.0),
              "movil": ((-2.0, -4.5, 1.4), (2.8, 9.0, 3.2), 28, -0.25)},
}
FORMATOS = {"escritorio": (1280, 720), "movil": (720, 1280)}
SOPORTE = os.environ.get("SOPORTE", "atril")  # de la guitarra del vestidor: atril | gancho (se elige en E3)
# Rango de la profundidad (cerca, lejos) en m: con el 0.3–40 de la nave los cuartos chicos salen gris parejo.
PROFUNDIDAD = {"vestidor": (0.3, 10.0), "cripta": (0.3, 14.0), "atrio": (0.5, 40.0)}


def _mat(nombre, color, emision=0.0):
    m = T["_mat"](nombre, color, emision)
    m.diffuse_color = (*color, 1)  # lo que pinta workbench con color_type MATERIAL
    return m


def _assets():
    ns = {}
    exec(open(os.path.join(RAIZ, "assets.py"), encoding="utf-8").read(), ns)
    return ns


def _mover(objs, dx):
    for o in objs:
        if o.parent is None:
            o.location.x += dx


def _nuevos(antes):
    return [o for o in bpy.data.objects if o.name not in antes]


# ---------------- vestidor (camarín) ----------------

def vestidor(m):
    """El vestidor de la imagen convertido en el de la banda: ropero abierto con la ropa de escenario, texana,
    espejo de marco dorado, tocador con veladoras y la guitarra recargada."""
    antes = {o.name for o in bpy.data.objects}
    g, n, mad, oro, cera = m["gris"], m["negro"], m["madera"], m["oro"], m["cera"]
    _caja("v_piso", -3.2, 3.4, -3.0, 3.1, -0.1, 0, g)
    _caja("v_techo", -3.2, 3.4, -3.0, 3.1, 3.6, 3.7, g)
    _caja("v_fondo", -3.2, 3.4, 2.95, 3.1, 0, 3.6, g)
    _caja("v_der", 3.2, 3.4, -3.0, 3.1, 0, 3.6, g)
    _caja("v_izq", -3.2, -3.0, -3.0, 3.1, 0, 3.6, n)  # en sombra: el hueco de E
    # ropero contra el muro derecho, abierto hacia el cuarto (-X)
    _caja("ropero_fondo", 3.1, 3.2, 0.0, 2.4, 0, 2.6, mad)
    _caja("ropero_lado_a", 2.55, 3.2, -0.04, 0.0, 0, 2.6, mad)
    _caja("ropero_lado_b", 2.55, 3.2, 2.4, 2.44, 0, 2.6, mad)
    _caja("ropero_techo", 2.5, 3.2, -0.08, 2.48, 2.6, 2.7, mad)
    _caja("ropero_base", 2.55, 3.2, 0.0, 2.4, 0, 0.12, mad)
    _caja("ropero_repisa", 2.6, 3.1, 0.0, 2.4, 2.38, 2.42, mad)
    _barra("ropero_barra", (2.85, 0.05, 2.25), (2.85, 2.35, 2.25), 0.012, oro)
    # puerta abierta 55°, bisagra en la esquina de enfrente: el oclusor de camarín → cripta (E7)
    puerta = _caja("puerta_ropero", 0.0, 0.04, -1.15, 0.0, 0.12, 2.6, mad)
    piv = bpy.data.objects.new("puerta_ropero_bisagra", None)
    bpy.context.collection.objects.link(piv)
    piv.location = (2.53, -0.04, 0)
    puerta.location.x -= 0.02
    puerta.location.y += 0.04
    puerta.parent = piv
    piv.rotation_euler = (0, 0, math.radians(-55))
    # ropa colgada: hombros + cuerpo, en ganchos; tonos de la previa (negras, blanca, roja bordada, crema)
    tonos = ((0.05, 0.05, 0.05), (0.06, 0.06, 0.07), (0.85, 0.85, 0.82), (0.45, 0.06, 0.08), (0.75, 0.70, 0.58))
    for i, c in enumerate(tonos):
        y = 0.35 + i * 0.42
        tela = _mat(f"tela_{i}", c)
        _caja(f"ropa_{i}_hombros", 2.66, 3.04, y - 0.05, y + 0.05, 2.0, 2.2, tela)
        _caja(f"ropa_{i}", 2.68, 3.02, y - 0.045, y + 0.045, 1.2 - 0.1 * (i % 2), 2.02, tela)
        _cil(f"gancho_{i}", 2.85, y, 2.2, 2.25, 0.012, oro)
    # texana en la repisa alta: ala + copa con la punta pellizcada
    crema = _mat("texana", (0.82, 0.78, 0.66))
    _cil("texana_ala", 2.85, 2.05, 2.7, 2.72, 0.24, crema)
    _cil("texana_copa", 2.85, 2.05, 2.72, 2.86, 0.105, crema, conico=0.085)
    # espejo grande en el fondo (marco del asset), arbotantes, tocador
    A = _assets()
    try:
        marco = A["_traer"](os.path.join("marco-1", "fancy_picture_frame_01_2k.blend"), ("fancy_picture_frame_01",))[0]
        A["_plantar"](marco, (0.9, 2.94, 0.95), alto=2.15, nombre_ancla="espejo_marco")
        marco.data.materials.clear()
        marco.data.materials.append(oro)
    except Exception as e:  # sin el asset, el marco de cajas de la previa
        print("SIN MARCO", e)
        _caja("espejo_marco", 0.2, 1.6, 2.88, 2.94, 0.95, 3.1, oro)
    _caja("espejo", 0.33, 1.47, 2.90, 2.93, 1.1, 2.95, m["espejo"])
    for k, x in enumerate((0.0, 1.8)):
        _cil(f"arbotante_{k}", x, 2.85, 2.15, 2.4, 0.025, oro)
        _cil(f"arbotante_{k}_vela", x, 2.85, 2.4, 2.52, 0.012, cera)
    _caja("tocador", 0.1, 1.7, 2.3, 2.92, 0, 0.85, mad)
    _caja("tocador_tapa", 0.06, 1.74, 2.26, 2.94, 0.85, 0.89, mad)
    for z in (0.2, 0.48):
        _caja(f"tocador_cajon_{z}", 0.18, 1.62, 2.27, 2.3, z, z + 0.24, n)
    for k, x in enumerate((0.55, 0.9, 1.25)):
        _cil(f"veladora_v{k}", x, 2.62, 0.89, 1.0, 0.035, m["roja"])
    # la reliquia: la guitarra de Diego. Recargada en el tocador quedaba en una postura imposible (el usuario, E3):
    # va en un atril de piso entre el tocador y el rincón, o colgada de un gancho entre el espejo y el ropero.
    # El asset mira a -Y con giro 0.
    if SOPORTE == "atril":
        P, giro, incl = (2.15, 2.55, 0.10), math.radians(-35), math.radians(-15)
        h = 0.74  # altura del yugo: el cuello a esa altura con la guitarra inclinada 15° hacia atrás
        cuello_y = h * math.tan(-incl)
        T["_grupo"]("atril", P[:2] + (0,), giro, [
            _barra("atril_pata_izq", (-0.2, -0.2, 0.01), (-0.06, 0.02, 0.11), 0.01, n),
            _barra("atril_pata_der", (0.2, -0.2, 0.01), (0.06, 0.02, 0.11), 0.01, n),
            _barra("atril_cuna", (-0.16, -0.05, 0.1), (0.16, -0.05, 0.1), 0.012, n),
            _barra("atril_poste", (0, cuello_y + 0.12, 0.0), (0, cuello_y + 0.05, h), 0.012, n),
            _barra("atril_yugo", (-0.05, cuello_y + 0.05, h), (0.05, cuello_y + 0.05, h), 0.01, n)])
    else:  # gancho en el muro del fondo, la guitarra colgada del clavijero, de frente al cuarto
        P, giro, incl = (2.33, 2.86, 0.97), 0.0, 0.0
        _barra("gancho_guitarra", (2.33, 2.95, 1.96), (2.33, 2.85, 1.96), 0.01, n)
    for pieza, mat in zip(A["guitarra"](bpy.context.collection, P, largo=0.98, giro=giro, inclinacion=incl,
                                        nombre="PROP_guitarra"), (m["madera_clara"], oro)):
        pieza.data.materials.clear()
        pieza.data.materials.append(mat)  # madera clara: delante del tocador oscuro Klein la fundía (ticket 12)
    _mover(_nuevos(antes), X_VESTIDOR)


# ---------------- cripta ----------------

def telefono(m, x, y, z):
    """Teléfono de disco de escritorio (tipo años treinta, el de la previa): base de tronco de pirámide, disco al
    frente, horquilla y auricular encima, cordón en espiral. Medidas reales: base 23 × 21 × 9 cm, auricular 22 cm."""
    oro, negro = m["oro"], m["negro"]
    piezas = []
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.155, radius2=0.105, depth=0.09, location=(0, 0, 0.045),
                                    rotation=(0, 0, math.pi / 4))
    base = bpy.context.object
    base.name = "tel_base"
    base.scale = (1.0, 0.92, 1.0)
    base.data.materials.append(oro)
    piezas.append(base)
    # disco inclinado en la cara de enfrente (-Y), con su anillo de agujeros
    bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.012, location=(0, -0.085, 0.05),
                                        rotation=(math.radians(62), 0, 0))
    disco = bpy.context.object
    disco.name = "tel_disco"
    disco.data.materials.append(oro)
    piezas.append(disco)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.042, minor_radius=0.006, location=(0, -0.091, 0.053),
                                     rotation=(math.radians(62), 0, 0))
    anillo = bpy.context.object
    anillo.name = "tel_disco_anillo"
    anillo.data.materials.append(negro)
    piezas.append(anillo)
    for k, sx in enumerate((-0.07, 0.07)):  # horquilla: dos postes con su cuna
        piezas.append(_cil(f"tel_horquilla_{k}", sx, 0.01, 0.085, 0.135, 0.009, oro))
    # auricular: dos copas unidas por el mango, apoyado en la horquilla
    piezas.append(_barra("tel_mango", (-0.095, 0.01, 0.15), (0.095, 0.01, 0.15), 0.014, oro))
    for k, sx in enumerate((-0.105, 0.105)):
        bpy.ops.mesh.primitive_cone_add(radius1=0.038, radius2=0.02, depth=0.045, location=(sx, 0.01, 0.13))
        copa = bpy.context.object
        copa.name = f"tel_copa_{k}"
        copa.data.materials.append(oro)
        piezas.append(copa)
    # cordón en espiral del costado de la base a la copa izquierda, cayendo sobre el altar
    cv = bpy.data.curves.new("tel_cordon", "CURVE")
    cv.dimensions, cv.bevel_depth, cv.bevel_resolution = "3D", 0.004, 2
    sp = cv.splines.new("POLY")
    pts = []
    for i in range(160):
        t = i / 159
        cx = -0.13 - 0.12 * math.sin(math.pi * t)
        cy = -0.02 + 0.14 * t
        cz = 0.012 + 0.09 * (1 - t) * (1 - t) + 0.008 * math.sin(40 * math.pi * t)
        pts.append((cx + 0.008 * math.cos(40 * math.pi * t), cy, cz))
    sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts):
        p.co = (*c, 1)
    cordon = bpy.data.objects.new("tel_cordon", cv)
    bpy.context.collection.objects.link(cordon)
    cordon.data.materials.append(negro)
    piezas.append(cordon)
    return T["_grupo"]("PROP_telefono", (x, y, z), math.radians(-12), piezas)


def cripta(m):
    """Bóveda baja de tezontle con nichos de entierro; el altar al centro-derecha con el teléfono de oro bajo la
    reja de la clave. El haz de luna no es geometría: lo pinta Klein (en la profundidad sería un objeto falso)."""
    antes = {o.name for o in bpy.data.objects}
    g, n = m["gris"], m["negro"]
    _boveda(0, -2, 9, 1.6, 2.2, g)
    _caja("c_muro_izq", -2.4, -2.2, -2, 9, 0, 1.6, g)
    _caja("c_muro_der", 2.2, 2.4, -2, 9, 0, 1.6, g)
    _caja("c_piso", -2.4, 2.4, -2, 9, -0.1, 0, g)
    _caja("c_fondo", -2.4, 2.4, 8.8, 9.0, 0, 3.9, n)
    for y in range(0, 9, 2):  # nichos de entierro en arco, a los dos lados
        for k, x in enumerate((-2.0, 2.0)):
            _caja(f"nicho_{y}_{k}", x - 0.15, x + 0.15, y - 0.6, y + 0.6, 0.3, 1.5, n)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=0.3, location=(x, y, 1.5), rotation=(0, math.pi / 2, 0))
            arco = bpy.context.object
            arco.name = f"nicho_{y}_{k}_arco"
            arco.data.materials.append(n)
    for y in range(-1, 10, 2):  # arcos fajones
        bpy.ops.mesh.primitive_torus_add(major_radius=2.1, minor_radius=0.11, location=(0, y, 1.6), rotation=(math.pi / 2, 0, 0))
        faja = bpy.context.object
        faja.name = f"fajon_{y}"
        faja.data.materials.append(g)
    # altar de piedra: cuerpo y losa que vuela 5 cm
    _caja("altar", 0.3, 1.5, 2.85, 3.55, 0, 0.95, g)
    _caja("altar_losa", 0.25, 1.55, 2.8, 3.6, 0.95, 1.0, g)
    telefono(m, 0.9, 3.15, 1.0)
    for k, x in enumerate((0.4, 1.4)):
        _cil(f"veladora_c{k}", x, 3.05, 1.0, 1.11, 0.035, m["roja"])
    # la reja de la clave, sobre el altar: marco y barrotes, siguiendo la curva de la bóveda en x 0.9
    zc = 1.6 + math.sqrt(2.2 ** 2 - 0.9 ** 2)
    _caja("reja_clave_marco", 0.6, 1.2, 2.9, 3.5, zc - 0.03, zc + 0.03, m["hierro"])
    for k in range(6):
        _barra(f"reja_clave_{k}", (0.62 + k * 0.11, 2.9, zc - 0.05), (0.62 + k * 0.11, 3.5, zc - 0.05), 0.008, m["hierro"])
    _mover(_nuevos(antes), X_CRIPTA)


# ---------------- atrio ----------------

def atrio(m):
    """La fachada desde la calle: portal abierto con la luz de las velas, torre, barda y reja abiertas, banqueta y la
    troca negra. El poste del sodio va a la derecha del portal: a la izquierda alumbraba la esquina del monograma."""
    antes = {o.name for o in bpy.data.objects}
    g, n, luz = m["gris"], m["negro"], m["portal"]
    _caja("a_calle", -15, 15, -13, 17, -0.1, 0, n)
    _caja("a_banqueta", -1, 13, 7.0, 8.4, 0, 0.16, g)
    _caja("a_atrio_piso", -9, 12, 9.75, 13.5, 0, 0.05, g)
    # fachada con el vano del portal (2.6 × 5.2, medio punto) y el interior encendido 1 m adentro
    # fachada de una pieza con el vano recortado (boolean): caja + medio punto, y el interior encendido detrás
    fachada = _caja("fachada", -5.5, 8.5, 13.5, 14.5, 0, 12, g)
    vano = [_caja("vano_caja", 0.2, 2.8, 13.3, 14.7, -0.1, 5.2, n)]
    bpy.ops.mesh.primitive_cylinder_add(radius=1.3, depth=1.4, location=(1.5, 14.0, 5.2), rotation=(math.pi / 2, 0, 0))
    vano.append(bpy.context.object)
    for k, c in enumerate(vano):
        b = fachada.modifiers.new(f"vano_{k}", "BOOLEAN")
        b.operation, b.object = "DIFFERENCE", c
        c.hide_render = c.hide_viewport = True
    _caja("portal_interior", -1.0, 4.0, 16.5, 16.6, 0, 7.0, luz)
    _caja("portal_piso", -1.0, 4.0, 14.5, 16.5, 0, 0.05, g)
    for k, (x, signo) in enumerate(((0.2, 1), (2.8, -1))):  # hojas de madera abiertas 60° hacia dentro
        hoja = _caja(f"portal_hoja_{k}", min(0, signo * 1.3), max(0, signo * 1.3), 0, 0.08, 0, 4.4, m["madera"])
        piv = bpy.data.objects.new(f"portal_hoja_{k}_bisagra", None)
        bpy.context.collection.objects.link(piv)
        piv.location = (x, 14.5, 0)
        hoja.parent = piv
        piv.rotation_euler = (0, 0, math.radians(60 * signo))
    _caja("torre", 5.5, 8.5, 13.0, 16.0, 0, 20, g)
    _caja("torre_campanario", 6.2, 7.8, 12.95, 13.0, 14.5, 17.5, n)
    # barda atrial con la reja abierta en el claro del portal
    _caja("barda_izq", -10, 0, 9.25, 9.75, 0, 1.4, g)
    _caja("barda_der", 4.0, 12, 9.25, 9.75, 0, 1.4, g)
    for k in range(20):
        x = 0.1 + k * 0.2
        _cil(f"reja_{k}", x, 9.5, 0, 3.0, 0.015, m["hierro"])
    _caja("reja_travesano", 0, 4.0, 9.48, 9.52, 2.6, 2.66, m["hierro"])
    # poste del sodio entre el portal y la troca
    _cil("poste", 4.6, 8.0, 0.16, 5.2, 0.06, m["hierro"])
    _barra("poste_brazo", (4.6, 8.0, 5.1), (4.1, 8.0, 5.1), 0.03, m["hierro"])
    _cil("lampara_sodio", 4.05, 8.0, 4.9, 5.05, 0.18, m["cera"], conico=0.06)
    ruta = os.path.join(RAIZ, "troca.py")
    if os.path.exists(ruta):  # E2
        tr = {}
        exec(open(ruta, encoding="utf-8").read(), tr)
        tr["troca"](m, (3.4, 5.95, 0), giro=math.radians(-90))  # pegada a la banqueta (y 7.0)
    _mover(_nuevos(antes), X_ATRIO)


# ---------------- escena y render ----------------

ESPACIOS = {"vestidor": (vestidor, X_VESTIDOR), "cripta": (cripta, X_CRIPTA), "atrio": (atrio, X_ATRIO)}


def build(espacios=("vestidor", "cripta", "atrio")):
    for col in (bpy.data.objects, bpy.data.meshes, bpy.data.curves, bpy.data.lights, bpy.data.cameras,
                bpy.data.materials):
        for d in list(col):
            col.remove(d)
    m = {"gris": _mat("gris", (0.35, 0.35, 0.35)), "negro": _mat("negro", (0.02, 0.02, 0.02)),
         "madera": _mat("madera", (0.12, 0.07, 0.04)), "oro": _mat("oro", (0.5, 0.38, 0.15)),
         "cera": _mat("cera", (0.9, 0.8, 0.6), 0.5), "roja": _mat("veladora", (0.6, 0.05, 0.05), 0.5),
         "hierro": _mat("hierro", (0.03, 0.03, 0.03)), "espejo": _mat("espejo", (0.55, 0.58, 0.6)),
         "portal": _mat("portal", (1.0, 0.75, 0.45), 2.0), "madera_clara": _mat("madera_clara", (0.75, 0.58, 0.38))}
    for e in espacios:
        ESPACIOS[e][0](m)
    cd = bpy.data.cameras.new("cam")
    cd.sensor_width, cd.clip_start = 36, 0.05
    cam = bpy.data.objects.new("cam", cd)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


def encuadrar(cam, espacio, formato):
    pos, mira, lente, shift = CAMARAS[espacio][formato]
    x0 = ESPACIOS[espacio][1]
    p, q = Vector(pos) + Vector((x0, 0, 0)), Vector(mira) + Vector((x0, 0, 0))
    cam.location = p
    cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens, cam.data.shift_y = lente, shift
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = FORMATOS[formato]
    sc.render.resolution_percentage = 100


def render(carpeta, espacios, formatos, cam):
    sc = bpy.context.scene
    os.makedirs(carpeta, exist_ok=True)
    for e in espacios:
        zmat = T["_profundidad"](*PROFUNDIDAD[e])
        for f in formatos:
            encuadrar(cam, e, f)
            # gris: workbench, color de material (la GPU la ocupa otro rol; workbench apenas la toca)
            sc.render.engine = "BLENDER_WORKBENCH"
            sc.display.shading.light = "STUDIO"
            sc.display.shading.color_type = "MATERIAL"
            sc.display.shading.show_shadows = True
            sc.display.shading.show_cavity = True
            sc.view_layers[0].material_override = None
            sc.view_settings.view_transform = "Standard"
            sc.render.filepath = os.path.join(carpeta, f"{e}_{f}_gris.png")
            bpy.ops.render.render(write_still=True)
            # profundidad: Cycles por CPU, sólo emisión
            sc.render.engine = "CYCLES"
            sc.cycles.device = "CPU"
            sc.cycles.samples = 16
            sc.view_layers[0].material_override = zmat
            sc.render.filepath = os.path.join(carpeta, f"{e}_{f}_z.png")
            bpy.ops.render.render(write_still=True)
            print("SALIDA", e, f)
    sc.view_layers[0].material_override = None


def pases_reproy(carpeta, espacio, cam, esc=(1696, 944), vert=(720, 1280)):
    """Para la vertical por reproyección (E4, método de G3: tmp/props-06/reproyectar.py, que corre en `carpeta`):
    z_esc.png / z_vert.png en 16 bits con la codificación fija de _profundidad (0.3–40 m) y camaras.json con la matriz
    y el view_frame de cada cámara. Escritorio al tamaño de la placa de Klein."""
    sc = bpy.context.scene
    os.makedirs(carpeta, exist_ok=True)
    sc.render.engine, sc.cycles.device, sc.cycles.samples = "CYCLES", "CPU", 16
    sc.view_layers[0].material_override = T["_profundidad"]()
    sc.view_settings.view_transform = "Standard"
    s = sc.render.image_settings
    s.file_format, s.color_mode, s.color_depth = "PNG", "BW", "16"
    camaras = {}
    for formato, tag, (w, h) in (("escritorio", "esc", esc), ("movil", "vert", vert)):
        encuadrar(cam, espacio, formato)
        sc.render.resolution_x, sc.render.resolution_y = w, h
        sc.render.filepath = os.path.join(carpeta, f"z_{tag}.png")
        bpy.ops.render.render(write_still=True)
        bpy.context.view_layer.update()
        camaras[tag] = {"w": w, "h": h, "mundo": [list(r) for r in cam.matrix_world],
                        "marco": [list(v) for v in cam.data.view_frame(scene=sc)]}
    json.dump(camaras, open(os.path.join(carpeta, "camaras.json"), "w"), indent=1)
    s.color_mode, s.color_depth = "RGB", "8"
    sc.view_layers[0].material_override = None
    print("SALIDA reproy", espacio)


if __name__ == "__main__" and "--" in sys.argv:
    args = sys.argv[sys.argv.index("--") + 1:]
    if args[0] == "reproy":  # -- reproy <carpeta> <espacio> [ancho alto de la placa de escritorio]
        esc = (int(args[3]), int(args[4])) if len(args) > 4 else (1696, 944)
        pases_reproy(args[1], args[2], build([args[2]]), esc)
        sys.exit(0)
    carpeta = args[0]
    esp = [a for a in args[1:] if a in ESPACIOS] or list(ESPACIOS)
    fmt = [a for a in args[1:] if a in FORMATOS] or list(FORMATOS)
    render(carpeta, esp, fmt, build(esp))
