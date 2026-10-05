"""Maqueta gris de la transición nave → sacristía (prueba 1) y su pase de profundidad.

Sólo geometría, cámara y una luz que la deje leer: el look lo pone la IA (Klein / MiniMax) con la
profundidad de aquí. Plan en docs/handoffs/2026-10-04-hero-y-transiciones.md.

Un solo travelling a la derecha. La nave y la sacristía están en sitios distintos del mundo (x 0 y x 40):
el corte cae mientras la cámara está tapada por un pilar (nave) y luego por un jambaje (sacristía), así que
el salto no se ve. Frames: A (loop nave) 1-260, T (transición) 301-360, B (loop sacristía) 401-660.
Los loops miden PERIODO cuadros y se renderizan N_LOOP: el sobrante repite el inicio para fundir la costura.

    ns = {}; exec(open(r"E:\\Cursor Projects\\MTO\\blender\\transicion.py").read(), ns)
    ns["build"](); ns["render"](r"E:\\Cursor Projects\\MTO\\tmp\\transicion-1")
"""
import math
import os

import bmesh
import bpy
from mathutils import Vector

LENTE = 35
ALTO_OJO = 1.6
ALTO_SAC = 1.35    # más baja: la tornamesa queda un poco bajo el centro
PILAR_X = 3.5        # pilar oclusor de la nave, centro
SAC_X0 = 42.3        # cámara de la sacristía en el instante del corte (tapada por el jambaje)
SAC_FIN = 44.5       # x final de la sacristía: tornamesa en el tercio derecho
N_T = 60             # 2.5 s a 24 fps
OCLUSORES = ("pilar_0_1", "jambaje")
A, T, B = 1, 301, 401
PERIODO = 120         # 5 s (ticket 04: a 1280×704, 10 s no cabe en 12 GB): la cámara vuelve a su inicio
N_LOOP = 141          # MiniMax pide 17n+5; los 20 de más funden la costura del humo
# Móvil (ticket 06): cámara vertical propia, misma trayectoria. Con la de escritorio en 9:16 el contrabajo, el Cristo y
# la lámpara quedan fuera; aquí arrancan más a la derecha y el shift sube el sujeto (hueco abajo, ticket 03).
MOVIL = {"lente": 28, "shift_y": -0.25, "nave_x": 0.8, "sac_fin": 45.4}  # 45.4: el neón en u ≤ 0.84, dentro de 19.5:9
_movil = False


def _mat(nombre, color, emision=0.0):
    m = bpy.data.materials.new(nombre)
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    if emision:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = emision
    return m


def _caja(nombre, x0, x1, y0, y1, z0, z1, mat):
    bpy.ops.mesh.primitive_cube_add(location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object
    o.name = nombre
    o.scale = ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2)
    o.data.materials.append(mat)
    return o


def _cil(nombre, x, y, z0, z1, r, mat, conico=None):
    if conico is None:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, location=(x, y, (z0 + z1) / 2))
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=conico, depth=z1 - z0, location=(x, y, (z0 + z1) / 2))
    o = bpy.context.object
    o.name = nombre
    o.data.materials.append(mat)
    return o


def _luz(nombre, tipo, loc, energia, color, size=0.1):
    d = bpy.data.lights.new(nombre, tipo)
    d.energy, d.color = energia, color
    if tipo == "AREA":
        d.size = size
    else:
        d.shadow_soft_size = size
    o = bpy.data.objects.new(nombre, d)
    o.location = loc
    bpy.context.collection.objects.link(o)
    return o


def _boveda(x, y0, y1, z, r, mat):
    """Medio cilindro sobre z, eje Y: la bóveda de cañón de la nave."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=y1 - y0, location=(x, (y0 + y1) / 2, z),
                                        rotation=(math.pi / 2, 0, 0), end_fill_type="NOTHING")
    o = bpy.context.object
    o.name = "boveda"
    # Sin transform_apply (no surte efecto vía MCP): con rotación X de 90°, la "y" local es la altura.
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -1e-4], context="VERTS")
    bm.to_mesh(o.data)
    bm.free()
    o.data.materials.append(mat)


def _banca(nombre, x0, x1, y, mat):
    """Banca de iglesia vista desde atrás (ticket 13: las cajas macizas se leían como cajas). Mira al altar (+Y):
    respaldo delgado del lado de la cámara con un remate de 12 cm a 0.9 m (ahí se paran requinto y veladoras),
    asiento a 0.45 m y hueco debajo, costados con perfil: descansabrazos bajo y alto junto al respaldo.
    """
    _caja(f"{nombre}_remate", x0, x1, y, y + 0.12, 0.86, 0.9, mat)
    _caja(f"{nombre}_respaldo", x0, x1, y, y + 0.04, 0.46, 0.86, mat)
    _caja(f"{nombre}_asiento", x0, x1, y + 0.04, y + 0.5, 0.42, 0.46, mat)
    for x in (x0, x1 - 0.05):
        _caja(f"{nombre}_costado_{x}", x, x + 0.05, y, y + 0.5, 0, 0.62, mat)
        _caja(f"{nombre}_brazo_{x}", x, x + 0.05, y, y + 0.14, 0.62, 0.94, mat)


def nave(gris, negro, oro, neon, cera):
    _caja("suelo_nave", -7, 7, -2, 31, -0.1, 0, gris)
    for s in (-1, 1):
        _caja(f"muro_nave_{s}", s * 7, s * 7.2, -2, 31, 0, 8, gris)
    _boveda(0, -2, 31, 8, 7, gris)
    _caja("muro_fondo", -7, 7, 30, 30.2, 0, 15, gris)
    _caja("muro_entrada", -7, 7, -2.2, -2, 0, 15, gris)
    for k in range(5):
        y = 3.2 + 5 * k
        for s in (-1, 1):
            # El primero de la derecha es el oclusor: negro, 1.4 m de ancho a 0.7 m de la cámara.
            _caja(f"pilar_{k}_{s}", s * PILAR_X - 0.7, s * PILAR_X + 0.7, y - 0.5, y + 0.5, 0, 8,
                  negro if (k, s) == (0, 1) else gris)
    for i in range(12):
        y = 6 + 1.2 * i
        for x0, x1 in ((-2.6, -0.5), (0.5, 2.6)):
            _banca(f"banca_{i}_{x0}", x0, x1, y, gris)
    _caja("mesa_altar", -1.5, 1.5, 26, 27, 0, 1.1, gris)
    _caja("retablo", -3, 3, 29.4, 29.8, 0, 8, oro)
    for x in (-1.8, 0, 1.8):
        _caja(f"hornacina_{x}", x - 0.5, x + 0.5, 29.2, 29.4, 2.2 if x else 1.6, 4.2 if x else 3.6, gris)
    _caja("cruz_v", -0.06, 0.06, 29.1, 29.2, 4.6, 7.0, neon)
    _caja("cruz_h", -0.6, 0.6, 29.1, 29.2, 6.0, 6.12, neon)
    for x in (-1.2, -0.8, 0.8, 1.2):
        _cil(f"cirio_{x}", x, 26.5, 1.1, 1.6, 0.04, cera)
        _luz(f"llama_{x}", "POINT", (x, 26.5, 1.7), 240, (1.0, 0.55, 0.2))
    _luz("neon_cruz", "POINT", (0, 28.5, 6), 720, (1.0, 0.08, 0.1), 0.5)
    _luz("haz", "SPOT", (5, 10, 13), 3600, (1.0, 0.75, 0.5), 0.3).rotation_euler = (math.radians(35), math.radians(20), 0)


def _instrumento(nombre, base, alto, cuerpo, fondo, rot, mat):
    """Silueta de guitarra: dos discos (abajo y arriba del cuerpo), mástil y clavijero.

    Local: arriba = +Z, la tapa mira a la cámara (-Y). `cuerpo` = fracción del alto que ocupa la caja;
    `rot` = (atrás, de lado, giro) en grados, aplicado en un empty en la base.
    """
    piv = bpy.data.objects.new(nombre, None)
    bpy.context.collection.objects.link(piv)
    c = cuerpo * alto
    partes = [
        ("abajo", 0.30 * c, 0.33 * c),   # radio, altura del centro
        ("arriba", 0.23 * c, 0.75 * c),
    ]
    for parte, r, z in partes:
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=fondo, location=(0, 0, z),
                                            rotation=(math.pi / 2, 0, 0))
        o = bpy.context.object
        o.name = f"{nombre}_{parte}"
        o.data.materials.append(mat)
        o.parent = piv
    for parte, ancho, z0, z1 in (("mastil", 0.045 * alto, c, 0.92 * alto), ("clavijero", 0.075 * alto, 0.92 * alto, alto)):
        o = _caja(f"{nombre}_{parte}", -ancho / 2, ancho / 2, -fondo / 4, fondo / 4, z0, z1, mat)
        o.parent = piv
    piv.location = base
    piv.rotation_euler = [math.radians(g) for g in rot]


def _assets():
    """blender/assets.py, cargado a mano como en altar.py: este script corre con exec()."""
    ns = {}
    exec(open(r"E:\Cursor Projects\MTO\blender\assets.py", encoding="utf-8").read(), ns)
    return ns


def instrumentos(mat, negro, cera):
    """Las reliquias de la nave (ticket 02): a la derecha de la primera banca; el titular vive a la izquierda.
    Veladoras de ofrenda a sus pies: la luz que los lee tiene fuente.

    El tololoche es el asset de contrabajo (ticket 12): con dos discos se leía como "una guitarra gigante".
    """
    bajo = _assets()["tololoche"](bpy.context.collection, (1.35, 5.69, 0), alto=1.85,  # y medida: apoya en la banca sin cruzarla
                                  giro=math.radians(-15), inclinacion=math.radians(-10))
    bajo.data.materials.append(mat)
    # Bocina de pie en el asiento y el requinto delante, recargado en su frente (ticket 12): 9° es el último ángulo
    # sin cruzarla, medido con BVH. Parado solo en la orilla de la banca "desafiaba la gravedad".
    # Ticket 06: en el asiento, detrás del respaldo, Klein le dibujaba la base sobre el remate y "flotaba". Ahora sub +
    # bocina en el piso, frente a la banca (como monta su equipo una banda). El sub es hondo (75 cm, uno de 18"): el
    # requinto se para sobre él, delante de la bocina; en el piso, el borde del cuadro de escritorio le cortaba el cuerpo.
    _caja("sub", 0.40, 0.90, 5.2, 5.95, 0, 0.6, negro)
    _caja("bocina", 0.45, 0.85, 5.55, 5.93, 0.6, 1.35, negro)
    # Madera clara en la maqueta: delante de la bocina negra, en gris, Klein lo fundía con el woofer (Klein copia los tonos).
    clara = _mat("madera_clara", (0.75, 0.58, 0.38))
    _instrumento("requinto", (0.62, 5.41, 0.588), 0.9, 0.52, 0.1, (-9, 0, -8), clara)  # BVH: toca sub y bocina
    # El humo necesita fuente (ticket 12: salía "de la guitarra"): sahumador de copal en la bocina, a la derecha del
    # clavijero. Brasa = luz naranja baja dentro del cuenco. Las veladoras nuevas (bocina y segunda banca) sólo dan hilos.
    _cil("sahumador_pie", 0.74, 5.8, 1.35, 1.4, 0.035, mat, conico=0.025)
    _cil("sahumador", 0.74, 5.8, 1.4, 1.49, 0.045, mat, conico=0.075)
    _luz("brasa", "POINT", (0.74, 5.8, 1.47), 6, (1.0, 0.35, 0.1), 0.03)
    for i, (x, y, z) in enumerate(((0.35, 5.05, 0), (1.05, 5.0, 0), (1.7, 5.45, 0),
                                   (0.53, 5.74, 1.35), (0.6, 7.24, 0.9), (1.6, 7.24, 0.9))):  # 7.24: sobre el remate
        _cil(f"veladora_{i}", x, y, z, z + 0.12, 0.035, cera)
        _luz(f"veladora_{i}", "POINT", (x, y, z + 0.2), 25, (1.0, 0.55, 0.2), 0.02)


def _barra(nombre, p0, p1, r, mat):
    """Cilindro de p0 a p1 (para brazos y cuerpos tumbados)."""
    a, b = Vector(p0), Vector(p1)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r, depth=(b - a).length, location=(a + b) / 2)
    o = bpy.context.object
    o.name = nombre
    o.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    o.data.materials.append(mat)
    return o


def _grupo(nombre, ubicacion, giro, piezas):
    """Empty en `ubicacion` con giro en Z; las piezas se crearon en coordenadas locales (empty en el origen)."""
    piv = bpy.data.objects.new(nombre, None)
    bpy.context.collection.objects.link(piv)
    for o in piezas:
        o.parent = piv
    piv.location = ubicacion
    piv.rotation_euler = (0, 0, giro)
    return piv


def capillas(madera, negro, oro, gris, cera):
    """Utilería de las capillas y los pilares (ticket 13). Desde el pasillo sólo se ven los arcos entre pilares
    (medido con rayos: hacia el muro del fondo de la nave lateral sólo hay una rendija de ~30 px), así que todo va
    justo dentro de los arcos 1 (y 8.7–12.7) y 2 (y 13.7–17.7). Referencia: catedral de Xalapa (neogótica,
    santos estofados del XVIII–XIX, relicario de Santa Teodora).
    """
    rojo = _mat("vaso_rojo", (0.8, 0.06, 0.03), emision=1.5)
    # Cristo negro crucificado, arco 1 derecho, girado hacia la cámara.
    p = [_caja("cristo_peana", -0.3, 0.3, -0.3, 0.3, 0, 0.5, madera),
         _caja("cristo_cruz", -0.06, 0.06, -0.04, 0.04, 0.5, 3.3, madera),
         _caja("cristo_travesano", -0.75, 0.75, -0.04, 0.04, 2.78, 2.9, madera),
         _barra("cristo_torso", (0, -0.1, 2.25), (0, -0.1, 2.8), 0.13, negro),
         _barra("cristo_brazo_i", (-0.12, -0.1, 2.75), (-0.68, -0.1, 2.88), 0.04, negro),
         _barra("cristo_brazo_d", (0.12, -0.1, 2.75), (0.68, -0.1, 2.88), 0.04, negro),
         _barra("cristo_piernas", (0, -0.1, 1.5), (0, -0.1, 2.25), 0.08, negro)]
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0.05, -0.12, 2.92))
    bpy.context.object.name = "cristo_cabeza"; bpy.context.object.data.materials.append(negro)
    p.append(bpy.context.object)
    _grupo("cristo", (3.3, 12.0, 0), -math.atan2(3.3, 10.0), p)  # mira hacia la cámara (0, 2); en y 11 lo tapaba el pilar 1
    # Urna de cristal con santo tendido, arco 1 izquierdo, a lo largo de la nave. Sin vidrio: lo pone Klein.
    x0, x1, y0, y1, z0, z1 = -0.3, 0.3, -0.8, 0.8, 0.9, 1.45
    p = [_caja("urna_peana", -0.35, 0.35, -1.05, 1.05, 0, 0.9, madera)]
    for i, (a, b) in enumerate((((x0, y0), (x0, y1)), ((x1, y0), (x1, y1)), ((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)))):
        for z in (z0, z1):
            p.append(_caja(f"urna_canto_{i}_{z}", min(a[0], b[0]) - 0.02, max(a[0], b[0]) + 0.02,
                           min(a[1], b[1]) - 0.02, max(a[1], b[1]) + 0.02, z, z + 0.04, oro))
    for i, (x, y) in enumerate(((x0, y0), (x0, y1), (x1, y0), (x1, y1))):
        p.append(_caja(f"urna_poste_{i}", x - 0.02, x + 0.02, y - 0.02, y + 0.02, z0, z1, oro))
    p.append(_barra("urna_santo", (0, -0.55, 1.05), (0, 0.45, 1.05), 0.12, gris))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0, 0.58, 1.08))
    bpy.context.object.name = "urna_cabeza"; bpy.context.object.data.materials.append(gris)
    p.append(bpy.context.object)
    _grupo("urna", (-3.6, 11.3, 0), 0, p)
    for i, y in enumerate((10.35, 12.25)):  # en las puntas de la peana
        _cil(f"urna_cirio_{i}", -3.6, y, 0.9, 1.25, 0.03, cera)
        _luz(f"urna_cirio_{i}", "POINT", (-3.6, y, 1.33), 25, (1.0, 0.55, 0.2), 0.02)
    # Candelero de veladoras en vaso rojo, al fondo del arco 2 izquierdo (más cerca lo tapa el pilar 2): gradas que suben hacia atrás.
    for g in range(3):
        _caja(f"candelero_{g}", -3.65, -3.2 - 0.15 * g, 16.4, 17.6, 0, 0.7 + 0.15 * g, negro)
        for j in range(6):
            _cil(f"veladora_roja_{g}_{j}", -3.27 - 0.15 * g, 16.52 + 0.19 * j, 0.7 + 0.15 * g,
                 0.78 + 0.15 * g, 0.03, rojo)
    _luz("candelero", "POINT", (-3.3, 17.0, 1.3), 60, (1.0, 0.3, 0.12), 0.3)
    # Vía Crucis en la cara interior de los pilares, a 2 m. El del pilar 3 derecho cae en la zona del humo: no va.
    for k, s in ((1, 1), (1, -1), (2, 1), (2, -1), (3, -1)):
        y, x = 3.2 + 5 * k, s * 2.8
        _caja(f"via_{k}_{s}", x - s * 0.04, x, y - 0.17, y + 0.17, 1.95, 2.4, oro)
        _caja(f"via_cruz_{k}_{s}", x - s * 0.04, x, y - 0.012, y + 0.012, 2.4, 2.56, oro)
        _caja(f"via_brazo_{k}_{s}", x - s * 0.04, x, y - 0.05, y + 0.05, 2.49, 2.51, oro)
    # Ventanal: lanceta en el muro sobre la arquería, arco del fondo izquierdo (pilares 3–4), y rayo de luna que
    # baja hasta el pasillo. Fuera de las capillas no hay muro sobre los arcos en la maqueta: se pone este tramo.
    _caja("claristorio", -2.9, -2.8, 18.7, 22.7, 4.4, 8, gris)
    _caja("ventanal", -2.8, -2.78, 20.1, 21.3, 4.8, 6.8, _mat("luna_vidrio", (0.6, 0.7, 0.9), emision=3.0))
    luna = _luz("luna", "SPOT", (-2.7, 20.7, 5.8), 4000, (0.75, 0.82, 1.0), 0.4)
    luna.rotation_euler = (Vector((0.4, 13.0, 0)) - luna.location).to_track_quat("-Z", "Y").to_euler()  # al pasillo
    luna.data.spot_size = math.radians(18)


def sacristia(gris, negro, madera, neon, cera):
    x0 = 40
    _caja("suelo_sac", x0, x0 + 8, -1, 4.0, -0.1, 0, gris)
    _caja("techo_sac", x0, x0 + 8, -1, 4.0, 4.5, 4.6, gris)
    _caja("muro_sac_izq", x0 - 0.2, x0, -1, 4.0, 0, 4.5, gris)
    _caja("muro_sac_der", 47.2, 47.4, -1, 4.0, 0, 4.5, gris)
    _caja("muro_sac_fondo", x0, x0 + 8, 3.8, 4.0, 0, 4.5, gris)
    _caja("muro_sac_atras", x0, x0 + 8, -1.2, -1, 0, 4.5, gris)
    _caja("jambaje", x0, 43, 0.7, 1.0, 0, 4.5, negro)  # el oclusor de entrada
    _caja("armario", 42.2, 43.6, 3.1, 3.8, 0, 2.4, madera)
    _caja("cajonera", 44.4, 46.4, 3.1, 3.8, 0, 1.0, madera)
    _caja("cuadro", 44.9, 45.9, 3.75, 3.8, 1.6, 2.9, madera)
    _caja("tornamesa", 44.88, 45.34, 3.27, 3.63, 1.0, 1.1, negro)
    _cil("plato", 45.06, 3.45, 1.1, 1.12, 0.15, gris)
    _cil("vinilo", 45.06, 3.45, 1.12, 1.125, 0.148, negro)
    _caja("brazo", 45.26, 45.28, 3.3, 3.57, 1.12, 1.14, gris)
    _cil("lampara_pie", 46.0, 3.5, 1.0, 1.45, 0.03, madera)
    _cil("pantalla", 46.0, 3.5, 1.4, 1.65, 0.22, cera, conico=0.1)
    _luz("lampara", "POINT", (45.85, 3.4, 1.35), 150, (1.0, 0.62, 0.3), 0.03)  # fuera del pie, bajo la pantalla
    _caja("neon_sac", 46.25, 46.3, 3.7, 3.75, 0.4, 3.6, neon)
    _luz("neon_sac", "AREA", (46.25, 3.5, 2), 8, (1.0, 0.08, 0.1), 0.5).rotation_euler = (0, math.radians(90), 0)  # roza hacia -X


def _pose(f):
    """Posición de cámara del frame f. Los loops vuelven a su inicio; la transición sigue un smoothstep.

    La deriva de los loops arranca desde quieta (1 − cos), igual que acaba la transición: si arrancara en
    movimiento, al llegar a un espacio la cámara frena y vuelve a arrancar de golpe.
    """
    def deriva(t, ax, ay):
        return ax * (1 - math.cos(2 * math.pi * t)), ay * (1 - math.cos(4 * math.pi * t))

    x0, fin = (MOVIL["nave_x"], MOVIL["sac_fin"]) if _movil else (0, SAC_FIN)
    if A <= f < A + N_LOOP:
        dx, dy = deriva((f - A) / PERIODO, 0.03, 0.025)
        return x0 + dx, 2 + dy
    if B <= f < B + N_LOOP:
        dx, dy = deriva((f - B) / PERIODO, 0.025, 0.02)
        return fin + dx, dy
    t = (f - T) / (N_T - 1)
    s = x0 + (fin - SAC_X0 + PILAR_X - x0) * t * t * (3 - 2 * t)  # recorrido total, velocidad continua en el corte
    return (s, 2) if s <= PILAR_X else (SAC_X0 + s - PILAR_X, 0)


def build(movil=False):
    global _movil
    _movil = movil
    # No read_factory_settings: apagaría el add-on MCP.
    for col in (bpy.data.objects, bpy.data.meshes, bpy.data.lights, bpy.data.cameras, bpy.data.materials):
        for d in list(col):
            col.remove(d)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.fps = 24
    sc.view_settings.view_transform = "AgX"
    w = bpy.data.worlds.new("noche")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.04, 0.04, 0.045, 1)  # luz de maqueta: que se lea la geometría
    sc.world = w
    gris = _mat("gris", (0.35, 0.35, 0.35))
    negro = _mat("negro", (0.01, 0.01, 0.01))
    oro = _mat("oro", (0.5, 0.38, 0.15))
    madera = _mat("madera", (0.12, 0.07, 0.04))
    neon = _mat("neon", (1.0, 0.05, 0.08), emision=2.6)
    cera = _mat("cera", (0.9, 0.8, 0.6), emision=0.5)
    nave(gris, negro, oro, neon, cera)
    instrumentos(gris, negro, cera)
    capillas(madera, negro, oro, gris, cera)
    sacristia(gris, negro, madera, neon, cera)

    cd = bpy.data.cameras.new("cam")
    cd.lens, cd.sensor_width, cd.clip_start = LENTE, 36, 0.05
    if movil:
        cd.lens, cd.shift_y = MOVIL["lente"], MOVIL["shift_y"]
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.rotation_euler = (math.pi / 2, 0, 0)  # nivelada, mirando +Y
    for f in [*range(A, A + N_LOOP), *range(T, T + N_T), *range(B, B + N_LOOP)]:
        x, y = _pose(f)
        cam.location = (x, y, ALTO_OJO if x < 20 else ALTO_SAC)
        cam.keyframe_insert("location", frame=f)


def _profundidad(cerca=0.3, lejos=40.0):
    """Material que emite 1 - log(z/cerca)/log(lejos/cerca): cerca = blanco, como lo espera el ControlNet."""
    m = bpy.data.materials.new("profundidad")
    nt = m.node_tree
    nt.nodes.clear()
    z = nt.nodes.new("ShaderNodeCameraData").outputs["View Z Depth"]
    for op, v in (("DIVIDE", cerca), ("LOGARITHM", math.e), ("DIVIDE", math.log(lejos / cerca))):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        nt.links.new(z, n.inputs[0])
        n.inputs[1].default_value = v
        z = n.outputs[0]
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation, inv.use_clamp = "SUBTRACT", True
    inv.inputs[0].default_value = 1
    nt.links.new(z, inv.inputs[1])
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(inv.outputs[0], em.inputs["Color"])
    nt.links.new(em.outputs[0], nt.nodes.new("ShaderNodeOutputMaterial").inputs["Surface"])
    return m


def render(carpeta, ancho=864, alto=480, tramos="ATB", pases=("gris", "z")):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = ancho, alto
    sc.render.image_settings.file_format = "PNG"
    rangos = {"A": (A, A + N_LOOP - 1), "T": (T, T + N_T - 1), "B": (B, B + N_LOOP - 1)}
    zmat = _profundidad()
    for pase in pases:
        sc.view_layers[0].material_override = zmat if pase == "z" else None
        sc.view_settings.view_transform = "Standard" if pase == "z" else "AgX"
        for luz in (o for o in sc.objects if o.type == "LIGHT"):
            luz.hide_render = pase == "z"
        # mascara: sólo los oclusores, fondo transparente; su alfa pinta de negro lo que tapan en el video final
        for o in sc.objects:
            if o.type == "MESH":
                o.hide_render = pase == "mascara" and o.name not in OCLUSORES
        sc.render.film_transparent = pase == "mascara"
        sc.render.image_settings.color_mode = "RGBA" if pase == "mascara" else "RGB"
        for tramo in tramos:
            sc.frame_start, sc.frame_end = rangos[tramo]
            sc.render.filepath = os.path.join(carpeta, pase, tramo, "f_")
            bpy.ops.render.render(animation=True)
    sc.view_layers[0].material_override = None
