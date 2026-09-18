"""Santuario M⚡T — construcción de la escena.

Fase 1: greybox y rig de cámara. Sin materiales: solo volúmenes, recorrido,
encuadres y enfoque. Los materiales entran en la fase 2.

Ejecutar dentro de Blender:
    exec(open(r"E:\\Cursor Projects\\MTO\\blender\\altar.py").read())
    build()
"""

import bpy
import math
import random
from mathutils import Vector

# ---------------------------------------------------------------- parámetros
# Unidades en metros. La nave se extiende sobre +Y; el altar está al fondo.

NAVE_ANCHO = 6.6
NAVE_LARGO = 20.0
NAVE_ALTO = 9.5
COLUMNAS = 6          # por lado; generan el paralaje del viaje
COLUMNA_LADO = 0.5

ALTAR_Y = 7.0
ALTAR_ANCHO = 3.2
ALTAR_FONDO = 1.1
ALTAR_ALTO = 1.05

RETABLO_Y = 8.6
HORNACINA_X = (-1.25, 0.0, 1.25)
HORNACINA_Z = 2.05
HORNACINA_ANCHO = 0.72
HORNACINA_ALTO = 1.15

CRUZ_Z = 4.4
VELADORAS = 8

# Ventanas: la tormenta de fuera. Dos tipos, como el resto de la nave: el
# ventanal de cuatro luces junto al altar y lancetas lisas a lo largo de la
# nave, entre columna y columna para no partir ninguna.
VENTANAL_Y = 6.4
VENTANAL_ALTO = 4.2
VENTANAL_Z = 4.1   # mas alto se sale de cuadro en la estacion altar
LANCETA_Y = (-6.4, -3.2, 0.0, 3.2)
LANCETA_ALTO = 1.5
LANCETA_Z = 2.7

# Estación -> (frame, offset, aim, foco, focal mm, altura extra m, f-stop)
# Seis canales: Follow Path es aditivo sobre la posición del objeto, así que
# "altura extra" sube la cámara por encima del recorrido — la grúa de la
# retirada. El recorrido no es monotónico: la retirada vuelve sobre sus pasos.
ESTACIONES = (
    # Los offsets salen de medir la curva, no de estimarlos: ver
    # docs/plans/…-implementation-plan.md, tarea 1.5.
    ("nave",       1,   0.000, "AIM_altar",     "AIM_altar",         28.0, 0.00, 4.0),
    # altar: elegida mirando, 2026-09-17. El offset 0.35 deja la camara a 10.2 m
    # del altar y desviada 0.85 a la derecha; mas alla los muros se levantan a
    # gris. Mismo encuadre sirve en 16:9 y en 9:16, verificado renderizando los
    # dos. Es la estacion mas brillante de las seis: manda sobre el velo.
    ("altar",      31,  0.350, "AIM_altar",     "AIM_altar",         24.0, 0.00, 4.0),
    ("sonido",     61,  0.825, "PROXY_vinilo",  "PROXY_vinilo",      70.0, 1.95, 3.2),
    # 28 mm, no 34: a 34 el retablo no entraba entero.
    ("hornacinas", 91,  0.885, "AIM_retablo",   "PROXY_hornacina_c", 28.0, 0.10, 3.5),
    ("reliquia",   121, 0.962, "PROXY_micro",   "PROXY_micro",       58.0, 0.30, 3.2),
    ("retirada",   151, 0.325, "AIM_altar",     "PROXY_placa",       26.0, 1.05, 5.6),
)

# Puntos del recorrido de cámara: (x, y, z)
RECORRIDO = (
    (0.00, -9.00, 1.75),
    (0.40, -5.00, 1.72),
    (1.30, -1.20, 1.66),
    (2.05,  2.40, 1.60),
    (1.70,  4.90, 1.48),
    (-1.20, 5.20, 1.55),
    (-0.85, 6.30, 1.15),
)

# Colocación de los instrumentos, tomada moviéndolos en el visor y leyendo su
# transformación: a mano se decide mejor dónde queda bien, pero el valor tiene
# que vivir aquí o se pierde en la siguiente reconstrucción.
TOLOLOCHE_POSE = (
    (-1.4365, 4.9190, 0.4095),        # centro de su caja, no su origen
    (-1.2155, -0.0489, -0.0395),      # euler en radianes
    0.9748,                           # escala (alto final 1.85 m)
)
REQUINTO_POS = (1.2357, 6.0578, 0.3026)   # recargado contra el frente del altar
REQUINTO_GIRO = -0.0136
REQUINTO_INCLINACION = -0.1792

COLECCION = "SANTUARIO"


# ------------------------------------------------------------------ utilidades

def _limpiar():
    """Vacía la escena. El .blend es un artefacto de build, no un documento."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for bloque in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras):
        for datablock in list(bloque):
            if datablock.users == 0:
                bloque.remove(datablock)
    # Los append de assets dejan datablocks huérfanos que se acumulan entre
    # reconstrucciones; sin purgarlos, el .blend crece en cada build.
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True,
                                   do_recursive=True)
    existente = bpy.data.collections.get(COLECCION)
    if existente:
        bpy.data.collections.remove(existente)
    col = bpy.data.collections.new(COLECCION)
    bpy.context.scene.collection.children.link(col)
    return col


def _caja(col, nombre, centro, dims):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=centro)
    ob = bpy.context.object
    ob.name = nombre
    ob.scale = Vector(dims)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    _reubicar(col, ob)
    return ob


def _cilindro(col, nombre, centro, radio, alto, vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radio, depth=alto, vertices=vertices, location=centro
    )
    ob = bpy.context.object
    ob.name = nombre
    _reubicar(col, ob)
    return ob


def _empty(col, nombre, centro):
    bpy.ops.object.empty_add(type="PLAIN_AXES", radius=0.25, location=centro)
    ob = bpy.context.object
    ob.name = nombre
    _reubicar(col, ob)
    return ob


def _casco_convexo(puntos):
    """Casco convexo 2D por monotone chain. En Blender no hay numpy."""
    def cruz(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def media(secuencia):
        pila = []
        for punto in secuencia:
            while len(pila) >= 2 and cruz(pila[-2], pila[-1], punto) <= 0:
                pila.pop()
            pila.append(punto)
        return pila[:-1]

    puntos = sorted(set(puntos))
    return media(puntos) + media(reversed(puntos))


# Una púa 351 es el casco convexo de un cuerpo redondo y una punta pequeña.
# Los dos círculos van en un cuadrado normalizado que luego se escala al ancho
# y alto reales, así que salen elipses: es lo que hace que la púa sea más ancha
# que alta, como las de verdad.
PUA_CIRCULOS = ((0.20, 0.30), (-0.44, 0.06))


def _pua(col, nombre, centro, ancho=0.028, alto=0.031, grosor=0.0009):
    """Púa de primitivas, para cuando el asset no está."""
    puntos = []
    for centro_y, radio in PUA_CIRCULOS:
        for i in range(48):
            angulo = i * 2.0 * math.pi / 48
            puntos.append((round(math.cos(angulo) * radio * (0.5 / 0.30), 6),
                           round(centro_y + math.sin(angulo) * radio, 6)))
    contorno = _casco_convexo(puntos)

    malla = bpy.data.meshes.new(nombre)
    malla.from_pydata([(x * ancho, y * alto, 0.0) for x, y in contorno], [],
                      [list(range(len(contorno)))])
    malla.update()
    ob = bpy.data.objects.new(nombre, malla)
    ob.location = centro
    bpy.context.scene.collection.objects.link(ob)
    # Grosor por modificador: aplicarlo no aporta nada y una púa de 0.9 mm
    # modelada a mano son cuarenta caras más por nada.
    solido = ob.modifiers.new("grosor", "SOLIDIFY")
    solido.thickness = grosor
    solido.offset = 0.0
    _reubicar(col, ob)
    return ob


def _reubicar(col, ob):
    for otra in list(ob.users_collection):
        otra.objects.unlink(ob)
    col.objects.link(ob)


# -------------------------------------------------------------------- escena

def _arquitectura(col):
    _caja(col, "NAVE_piso", (0, 0, -0.05), (NAVE_ANCHO, NAVE_LARGO, 0.1))
    _caja(col, "NAVE_muro_izq",
          (-NAVE_ANCHO / 2, 0, NAVE_ALTO / 2), (0.3, NAVE_LARGO, NAVE_ALTO))
    _caja(col, "NAVE_muro_der",
          (NAVE_ANCHO / 2, 0, NAVE_ALTO / 2), (0.3, NAVE_LARGO, NAVE_ALTO))
    _caja(col, "RETABLO_muro",
          (0, RETABLO_Y, NAVE_ALTO / 2), (NAVE_ANCHO, 0.4, NAVE_ALTO))
    _caja(col, "NAVE_techo",
          (0, 0, NAVE_ALTO), (NAVE_ANCHO, NAVE_LARGO, 0.3))

    # Columnas: lo que hace que el viaje se sienta como viaje.
    paso = (NAVE_LARGO - 4.0) / (COLUMNAS - 1)
    for i in range(COLUMNAS):
        y = -NAVE_LARGO / 2 + 2.0 + i * paso
        for signo, lado in ((-1, "izq"), (1, "der")):
            _caja(col, "COLUMNA_%s_%d" % (lado, i),
                  (signo * (NAVE_ANCHO / 2 - COLUMNA_LADO / 2 - 0.1), y,
                   NAVE_ALTO / 2),
                  (COLUMNA_LADO, COLUMNA_LADO, NAVE_ALTO))

    # Escalones: elevan el altar y frenan la vista antes de llegar.
    for i in range(2):
        _caja(col, "ESCALON_%d" % i,
              (0, ALTAR_Y - 1.5 - i * 0.45, 0.09 + (1 - i) * 0.18),
              (5.2, 0.9, 0.18))

    _caja(col, "ALTAR_bloque",
          (0, ALTAR_Y, ALTAR_ALTO / 2), (ALTAR_ANCHO, ALTAR_FONDO, ALTAR_ALTO))
    _caja(col, "ALTAR_mesa",
          (0, ALTAR_Y, ALTAR_ALTO + 0.04),
          (ALTAR_ANCHO + 0.25, ALTAR_FONDO + 0.2, 0.08))

    _hornacinas(col)
    _ventanas(col)

    # Cruz de neón
    _caja(col, "CRUZ_vertical",
          (0, RETABLO_Y - 0.3, CRUZ_Z), (0.12, 0.08, 1.6))
    _caja(col, "CRUZ_horizontal",
          (0, RETABLO_Y - 0.3, CRUZ_Z + 0.35), (0.9, 0.08, 0.12))


def _ventanas(col):
    """Ventanas góticas en los dos muros, con el hueco recortado a su forma.

    El cristal es un plano emisivo: de día no hay día en esta escena, así que
    lo que entra por la ventana es la tormenta. Su fuerza de emisión la manda
    `look.py`, y subirla es el relámpago.

    Sin el asset no pasa nada: la nave se queda ciega, como estaba.
    """
    assets = _cargar_assets()
    if assets is None or not assets.disponible(assets.VENTANAS):
        return []

    puestas = []
    for signo, lado in ((-1, "izq"), (1, "der")):
        muro = bpy.data.objects["NAVE_muro_%s" % lado]
        x = signo * NAVE_ANCHO / 2
        trabajos = [(assets.VENTANA_ROSETON, "ventanal", VENTANAL_Y,
                     VENTANAL_ALTO, VENTANAL_Z)]
        for indice, y in enumerate(LANCETA_Y):
            trabajos.append((assets.VENTANA_LANCETA, "lanceta_%d" % indice, y,
                             LANCETA_ALTO, LANCETA_Z))

        for pieza, etiqueta, y, alto, z in trabajos:
            nombre = "VENTANA_traceria_%s_%s" % (lado, etiqueta)
            _traceria, _cristal, cortador = assets.ventana(
                col, pieza, nombre, (x, y, z), alto, -signo)
            modificador = muro.modifiers.new("corte_" + etiqueta, "BOOLEAN")
            modificador.operation = "DIFFERENCE"
            modificador.object = cortador
            bpy.context.view_layer.objects.active = muro
            bpy.ops.object.modifier_apply(modifier=modificador.name)
            bpy.data.objects.remove(cortador, do_unlink=True)
            puestas.append(nombre)
    return puestas


def _hornacinas(col):
    """Huecos reales restados del retablo, con su marco de oro alrededor."""
    muro = bpy.data.objects["RETABLO_muro"]
    for x, sufijo in zip(HORNACINA_X, ("i", "c", "d")):
        hueco = _caja(col, "CORTE_" + sufijo,
                      (x, RETABLO_Y - 0.12, HORNACINA_Z),
                      (HORNACINA_ANCHO, 0.42, HORNACINA_ALTO))
        modificador = muro.modifiers.new("corte_" + sufijo, "BOOLEAN")
        modificador.operation = "DIFFERENCE"
        modificador.object = hueco
        bpy.context.view_layer.objects.active = muro
        bpy.ops.object.modifier_apply(modifier=modificador.name)
        bpy.data.objects.remove(hueco, do_unlink=True)

        # Fondo del nicho: el retrato irá encima, en HTML.
        _caja(col, "PROXY_hornacina_" + sufijo,
              (x, RETABLO_Y + 0.08, HORNACINA_Z),
              (HORNACINA_ANCHO, 0.04, HORNACINA_ALTO))
        # Marco de oro rodeando el hueco, cuatro listones.
        grosor = 0.07
        for dx, dz, ancho, alto in (
            (0, (HORNACINA_ALTO + grosor) / 2, HORNACINA_ANCHO + grosor * 2, grosor),
            (0, -(HORNACINA_ALTO + grosor) / 2, HORNACINA_ANCHO + grosor * 2, grosor),
            ((HORNACINA_ANCHO + grosor) / 2, 0, grosor, HORNACINA_ALTO + grosor * 2),
            (-(HORNACINA_ANCHO + grosor) / 2, 0, grosor, HORNACINA_ALTO + grosor * 2),
        ):
            _caja(col, "HORNACINA_marco_%s_%d_%d" % (sufijo, int(dx * 100), int(dz * 100)),
                  (x + dx, RETABLO_Y - 0.22, HORNACINA_Z + dz), (ancho, 0.12, alto))


def _cubana_greybox(col, mesa_z):
    """Cadena cubana de toros, para cuando el asset no está."""
    inicio_x, inicio_y = 0.02, ALTAR_Y + 0.34
    paso = 0.019                      # menor que el diámetro: los eslabones se solapan
    for i in range(26):
        avance = inicio_x + paso * i - 0.26
        lateral = inicio_y + 0.05 * math.sin(i * 0.42)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.0145, minor_radius=0.0042,
            major_segments=14, minor_segments=6,
            location=(avance, lateral, mesa_z + 0.008))
        eslabon = bpy.context.object
        eslabon.name = "PROP_cubana_%d" % i
        # alternar el plano de cada eslabón es lo que hace que se lea como cadena
        eslabon.rotation_euler = (math.radians(90) if i % 2 else 0.0,
                                  0.0,
                                  math.atan2(0.05 * 0.42 * math.cos(i * 0.42), paso))
        eslabon.scale = (1.0, 1.35, 1.0)
        bpy.ops.object.shade_smooth()
        _reubicar(col, eslabon)


def _lentes_greybox(col, mesa_z):
    """Lentes de primitivas, para cuando el asset no está."""
    for signo in (-1, 1):
        cristal = _caja(col, "PROP_lentes_cristal_%d" % signo,
                        (1.42 + signo * 0.032, ALTAR_Y + 0.42, mesa_z + 0.012),
                        (0.055, 0.032, 0.018))
        cristal.rotation_euler = (0.15, 0, 0.3)
    _caja(col, "PROP_lentes_patilla", (1.50, ALTAR_Y + 0.5, mesa_z + 0.014),
          (0.11, 0.008, 0.01)).rotation_euler = (0, 0, 0.9)


def _cenicero_greybox(col, mesa_z):
    """Cenicero de primitivas con dos cigarros, para cuando el asset no está."""
    _cilindro(col, "PROP_cenicero", (-0.45, ALTAR_Y - 0.1, mesa_z + 0.015),
              0.085, 0.03, 24)
    _cilindro(col, "PROP_cenicero_hueco", (-0.45, ALTAR_Y - 0.1, mesa_z + 0.032),
              0.062, 0.012, 24)
    for i, (dx, dy, giro) in enumerate(((0.06, 0.02, 0.9), (-0.05, -0.04, -0.4))):
        cigarro = _cilindro(col, "PROP_cigarro_%d" % i,
                            (-0.45 + dx, ALTAR_Y - 0.1 + dy, mesa_z + 0.042),
                            0.0055, 0.09, 12)
        cigarro.rotation_euler = (1.45, 0, giro)
        brasa = _cilindro(col, "PROP_brasa_%d" % i,
                          (-0.45 + dx + 0.042 * math.sin(giro),
                           ALTAR_Y - 0.1 + dy + 0.042 * math.cos(giro),
                           mesa_z + 0.042), 0.0056, 0.008, 12)
        brasa.rotation_euler = (1.45, 0, giro)


def _botella_greybox(col, bx, by, mesa_z):
    """Botella de primitivas, para cuando el asset no está."""
    cuerpo_bot = _caja(col, "PROP_botella", (bx, by, mesa_z + 0.095),
                       (0.086, 0.086, 0.19))
    bisel = cuerpo_bot.modifiers.new("bisel", "BEVEL")
    bisel.width = 0.012
    bisel.segments = 3
    hombro = _caja(col, "PROP_botella_hombro", (bx, by, mesa_z + 0.205),
                   (0.062, 0.062, 0.04))
    bisel_h = hombro.modifiers.new("bisel", "BEVEL")
    bisel_h.width = 0.016
    bisel_h.segments = 3
    _cilindro(col, "PROP_botella_cuello", (bx, by, mesa_z + 0.245), 0.019, 0.05, 16)
    _cilindro(col, "PROP_botella_cinta", (bx, by, mesa_z + 0.262), 0.022, 0.022, 16)
    tapon = _cilindro(col, "PROP_botella_tapon", (bx, by, mesa_z + 0.292),
                      0.028, 0.042, 20)
    tapon.scale = (1.0, 1.0, 0.85)
    bisel_t = tapon.modifiers.new("bisel", "BEVEL")
    bisel_t.width = 0.014
    bisel_t.segments = 4
    lazo = _caja(col, "PROP_botella_lazo", (bx + 0.05, by - 0.02, mesa_z + 0.245),
                 (0.07, 0.004, 0.028))
    lazo.rotation_euler = (0, 0.35, 0.4)
    # Tequila dentro: sin líquido, el vidrio se lee como un bloque vacío.
    _caja(col, "PROP_botella_liquido", (bx, by, mesa_z + 0.072),
          (0.074, 0.074, 0.14))


def _props(col, mesa_z):
    """Lo que hace que el altar parezca usado y no un render de catálogo."""
    # Cenicero cerca del micro (estación de la reliquia). El asset ya viene
    # desbordado de colillas, así que con él no se ponen cigarros sueltos.
    assets_cen = _cargar_assets()
    if assets_cen is not None and assets_cen.disponible(assets_cen.CENICERO):
        assets_cen.cenicero(col, (-0.45, ALTAR_Y - 0.1, mesa_z), alto=0.10,
                            giro=0.7)
    else:
        _cenicero_greybox(col, mesa_z)

    # Botella cuadrada de hombros marcados: se reconoce por la silueta, sin
    # logo ni etiqueta, que a este tamaño no se leerían.
    bx, by = 1.2205, ALTAR_Y + 0.30
    assets_bot = _cargar_assets()
    if assets_bot is not None and assets_bot.disponible(assets_bot.BOTELLA):
        assets_bot.botella(col, (bx, by, mesa_z), alto=0.26, giro=0.5)
    else:
        _botella_greybox(col, bx, by, mesa_z)

    # Billetes: sueltos y desordenados, como propina de una noche. Ordenados en
    # abanico se leían como "el dinero es el tema", que no es la idea.
    azar = random.Random(7)
    for i in range(4):
        billete = _caja(col, "PROP_billete_%d" % i,
                        (1.58 + azar.uniform(-0.16, 0.16),
                         ALTAR_Y + 0.24 + azar.uniform(-0.12, 0.12),
                         mesa_z + 0.003 + i * 0.0015),
                        (0.15, 0.068, 0.0015))
        billete.rotation_euler = (azar.uniform(-0.05, 0.05),
                                  azar.uniform(-0.05, 0.05),
                                  azar.uniform(0, 3.14))

    assets_gorra = _cargar_assets()
    if assets_gorra is not None and assets_gorra.disponible(assets_gorra.GORRA):
        assets_gorra.gorra(col, (GORRA_POS[0], ALTAR_Y + GORRA_POS[1], mesa_z),
                           ancho=0.155, giro=GORRA_POS[2], inclinacion=0.05)
    else:
        _gorra_mesa(col, mesa_z)

    # Requinto recostado contra el altar, visible en los planos generales.
    assets_guitarra = _cargar_assets()
    if assets_guitarra is not None and assets_guitarra.disponible(assets_guitarra.GUITARRA):
        # Colocación tomada del visor: recargada contra el frente del altar.
        assets_guitarra.guitarra(col, REQUINTO_POS, largo=0.98,
                                 giro=REQUINTO_GIRO, inclinacion=REQUINTO_INCLINACION)
    else:
        cuerpo = _cilindro(col, "PROP_requinto_cuerpo", (1.9, ALTAR_Y - 0.85, 0.42),
                           0.17, 0.09, 24)
        cuerpo.rotation_euler = (1.25, 0, -0.25)
        mastil = _caja(col, "PROP_requinto_mastil", (2.06, ALTAR_Y - 1.32, 0.95),
                       (0.07, 0.05, 0.78))
        mastil.rotation_euler = (0.32, 0, -0.25)

    # Vaso y cerillos, cerca del cenicero.
    _cilindro(col, "PROP_vaso", (-0.18, ALTAR_Y + 0.22, mesa_z + 0.05),
              0.036, 0.1, 20)
    _caja(col, "PROP_cerillos", (-0.535, ALTAR_Y + 0.26, mesa_z + 0.012),
          (0.055, 0.035, 0.024))

    # Tapete bajo los discos: unifica la toma cenital y separa el negro del
    # vinilo del de la piedra.
    tapete = _caja(col, "PROP_tapete", (1.15, ALTAR_Y + 0.02, mesa_z + 0.001),
                   (0.92, 0.58, 0.004))
    tapete.rotation_euler = (0, 0, 0.12)

    # Polaroids de la banda entre los discos: dicen quién toca sin una palabra.
    azar_foto = random.Random(11)
    for i in range(3):
        foto = _caja(col, "PROP_polaroid_%d" % i,
                     (0.72 + i * 0.1 + azar_foto.uniform(-0.05, 0.05),
                      ALTAR_Y - 0.34799 + azar_foto.uniform(-0.06, 0.06),
                      mesa_z + 0.004 + i * 0.002),
                     (0.13, 0.108, 0.002))
        foto.rotation_euler = (0, 0, azar_foto.uniform(-0.35, 0.35))
        _caja(col, "PROP_polaroid_img_%d" % i,
              (foto.location.x, foto.location.y + 0.008,
               foto.location.z + 0.0015), (0.108, 0.082, 0.001)).rotation_euler = (
                  0, 0, foto.rotation_euler.z)

    # Frasco tallado de agua bendita.
    _cilindro(col, "PROP_frasco", (0.30, ALTAR_Y - 0.02, mesa_z + 0.085),
              0.042, 0.17, 16)
    _cilindro(col, "PROP_frasco_tapon", (0.30, ALTAR_Y - 0.02, mesa_z + 0.185),
              0.022, 0.035, 12)

    # Estuche de micrófono abierto y marcador grueso: la estación de
    # contratación dice "aquí se firma", con objetos de su mundo y no de
    # una película de época.
    caja_trato = _caja(col, "PROP_caja_trato", (-0.72, ALTAR_Y + 0.18, mesa_z + 0.04),
                       (0.17, 0.115, 0.075))
    caja_trato.rotation_euler = (0, 0, -0.35)
    tapa = _caja(col, "PROP_caja_tapa", (-0.7049, ALTAR_Y + 0.2178, mesa_z + 0.1303),
                 (0.17, 0.11, 0.012))
    tapa.rotation_euler = (-1.15, 0, -0.35)
    _caja(col, "PROP_caja_forro", (-0.72, ALTAR_Y + 0.18, mesa_z + 0.079),
          (0.15, 0.095, 0.004)).rotation_euler = (0, 0, -0.35)
    marcador = _cilindro(col, "PROP_marcador", (-0.63, ALTAR_Y + 0.0071, mesa_z + 0.012),
                         0.011, 0.14, 12)
    marcador.rotation_euler = (1.57, 0, 0.62)
    tapa_m = _cilindro(col, "PROP_marcador_tapa", (-0.71, ALTAR_Y - 0.01, mesa_z + 0.012),
                       0.0125, 0.045, 12)
    tapa_m.rotation_euler = (1.57, 0, 0.62)

    # Anillos caídos junto al micrófono.
    azar_anillo = random.Random(13)
    for i in range(3):
        anillo = _cilindro(col, "PROP_anillo_%d" % i,
                           (-1.08 + azar_anillo.uniform(-0.09, 0.09),
                            ALTAR_Y - 0.18 + azar_anillo.uniform(-0.07, 0.07),
                            mesa_z + 0.006), 0.0115, 0.012, 14)
        anillo.rotation_euler = (1.57, 0, azar_anillo.uniform(0, 3.14))

    # Púas dispersas. El asset es de terceros; sin él se cae al greybox, que
    # es la misma silueta hecha a mano.
    assets_pua = _cargar_assets()
    hay_asset = assets_pua is not None and assets_pua.disponible(assets_pua.PUA)
    for i in range(5):
        sitio = (0.15 + azar_anillo.uniform(-0.5, 0.5),
                 ALTAR_Y + azar_anillo.uniform(-0.3, 0.3), mesa_z + 0.003)
        giro = azar_anillo.uniform(0, 3.14)
        if hay_asset:
            assets_pua.pua(col, "PROP_pua_%d" % i, sitio, ancho=0.028, giro=giro)
        else:
            _pua(col, "PROP_pua_%d" % i, sitio).rotation_euler = (0, 0, giro)

    # Lentes sobre la mesa, del lado de los discos.
    assets_len = _cargar_assets()
    if assets_len is not None and assets_len.disponible(assets_len.LENTES):
        assets_len.lentes(col, (0.97208, ALTAR_Y + 0.36958, mesa_z), ancho=0.14,
                          giro=0.2406)
    else:
        _lentes_greybox(col, mesa_z)

    # Botella alta de cerámica al fondo de la mesa. La X viene de moverla en el
    # visor: 9 cm hacia el centro, para que no se salga del canto de la mesa.
    _cilindro(col, "PROP_ceramica", (-1.662, ALTAR_Y + 0.3, mesa_z + 0.16),
              0.05, 0.32, 20)
    _cilindro(col, "PROP_ceramica_cuello", (-1.662, ALTAR_Y + 0.3, mesa_z + 0.36),
              0.018, 0.09, 12)

    # Cera escurrida al pie de las veladoras. Las cinco gotas se repartieron
    # a mano en el visor; ninguna sigue donde la puso el bucle.
    CERA = (((-0.95, -0.2933), 1.8421), ((-0.5666, -0.4363), 0.0),
            ((0.2824, -0.0715), 0.0), ((0.3721, -0.3079), 0.0),
            ((0.64721, -0.17206), 0.0))
    for i, ((x, dy), giro) in enumerate(CERA):
        gota = _cilindro(col, "PROP_cera_%d" % i,
                         (x, ALTAR_Y + dy, mesa_z + 0.004), 0.048, 0.008, 16)
        gota.scale = (1.0, 0.65, 1.0)
        gota.rotation_euler = (0, 0, giro)


def _tololoche(col):
    """Tololoche contra una columna, el bajo del género.

    Es el mismo asset de la guitarra escalado a 1.85 m: a ocho metros y en
    penumbra, la silueta de un contrabajo y la de una guitarra grande no se
    distinguen. Si aparece un tololoche de verdad, se cambia esta llamada.
    """
    assets_tololoche = _cargar_assets()
    if assets_tololoche is not None and assets_tololoche.disponible(assets_tololoche.TOLOLOCHE):
        # Pose tomada del visor: recargado contra el escalón izquierdo.
        assets_tololoche.tololoche(col, pose=TOLOLOCHE_POSE)
        return
    if assets_tololoche is not None and assets_tololoche.disponible(assets_tololoche.GUITARRA):
        assets_tololoche.guitarra(col, (-2.05, 3.05, 0.02), largo=1.85,
                                  giro=0.30, inclinacion=0.0,
                                  nombre="PROP_tololoche")
        return
    cuerpo = _cilindro(col, "PROP_tololoche_cuerpo", (-2.35, 1.4, 0.72), 0.34, 0.22, 24)
    cuerpo.rotation_euler = (1.35, 0, 0.18)
    cuerpo.scale = (1.0, 1.35, 1.0)
    mastil = _caja(col, "PROP_tololoche_mastil", (-2.52, 0.62, 1.62), (0.09, 0.07, 1.1))
    mastil.rotation_euler = (0.28, 0, 0.18)
    clavijero = _caja(col, "PROP_tololoche_clavijero", (-2.60, 0.28, 2.18),
                      (0.11, 0.09, 0.26))
    clavijero.rotation_euler = (0.28, 0, 0.18)


def _guirnalda(col):
    """Focos colgados al fondo: bokeh cálido que rompe la solemnidad."""
    azar = random.Random(41)
    for i in range(11):
        x = -2.3 + i * 0.46
        caida = 0.35 * math.sin(i / 10.0 * math.pi)
        _cilindro(col, "FOCO_%d" % i, (x, RETABLO_Y - 1.5, 6.4 - caida),
                  0.035, 0.07, 10)


def _exvotos(col):
    """Milagritos de latón al pie de los nichos: devoción, no decorado."""
    azar = random.Random(23)
    repisa_z = HORNACINA_Z - HORNACINA_ALTO / 2 - 0.05
    for x in HORNACINA_X:
        _caja(col, "EXVOTO_repisa_%d" % int(x * 100),
              (x, RETABLO_Y - 0.28, repisa_z), (HORNACINA_ANCHO + 0.2, 0.16, 0.04))
        for i in range(4):
            pieza = _caja(col, "EXVOTO_%d_%d" % (int(x * 100), i),
                          (x - 0.28 + i * 0.19 + azar.uniform(-0.02, 0.02),
                           RETABLO_Y - 0.31,
                           repisa_z + 0.045),
                          (0.045, 0.012, 0.055))
            pieza.rotation_euler = (azar.uniform(-0.12, 0.12), 0,
                                    azar.uniform(-0.25, 0.25))


def _rayo(col, nombre, centro, alto=0.06, grosor=0.012):
    """El rayo del monograma M⚡T, como dije. Malla propia: es la identidad de
    la banda, no un símbolo prestado."""
    escala = alto / 2.0
    perfil = [
        (0.26, 1.0), (-0.42, 0.06), (-0.02, 0.06), (-0.26, -1.0),
        (0.42, -0.04), (0.04, -0.04),
    ]
    vertices = [(x * escala, 0.0, y * escala) for x, y in perfil]
    malla = bpy.data.meshes.new(nombre)
    malla.from_pydata(vertices, [], [list(range(len(vertices)))])
    malla.update()
    ob = bpy.data.objects.new(nombre, malla)
    col.objects.link(ob)
    ob.location = centro
    engrosar = ob.modifiers.new("grosor", "SOLIDIFY")
    engrosar.thickness = grosor
    return ob


# Marca ficticia de la gorra. Lenguaje de casa de lujo —monograma entrelazado,
# serif, oro— sin parecerse a ninguna marca real: imitar una de cerca sería el
# mismo problema legal que copiarla.
MARCA = "SANTO VICIO"
MARCA_MONOGRAMA = "SV"
GORRA_POS = (-1.4038, -0.3088, 0.4088)   # x, desplazamiento en y, giro


def _texto(col, nombre, cuerpo, centro, alto, extrusion=0.002, negrita=True):
    """Texto extruido como malla. Sirve para el monograma de la marca."""
    bpy.ops.object.text_add(location=centro)
    ob = bpy.context.object
    ob.name = nombre
    ob.data.body = cuerpo
    ob.data.size = alto
    ob.data.extrude = extrusion
    ob.data.align_x = "CENTER"
    ob.data.align_y = "CENTER"
    for ruta in (r"C:\Windows\Fonts\georgiab.ttf" if negrita else r"C:\Windows\Fonts\georgia.ttf",
                 r"C:\Windows\Fonts\timesbd.ttf", r"C:\Windows\Fonts\times.ttf"):
        try:
            ob.data.font = bpy.data.fonts.load(ruta, check_existing=True)
            break
        except RuntimeError:
            continue
    bpy.ops.object.convert(target="MESH")
    ob = bpy.context.object
    ob.name = nombre
    _reubicar(col, ob)
    return ob


def _gorra_mesa(col, mesa_z):
    """Gorra de seis gajos con visera curva y parche de marca.

    La primera versión era una cúpula con un disco debajo; ésta se construye
    con la copa cortada en gajos por costuras, visera con curvatura real
    (intersección de una esfera achatada) y botón superior.
    """
    gx, gy, giro = GORRA_POS[0], ALTAR_Y + GORRA_POS[1], GORRA_POS[2]
    frente_x, frente_y = math.sin(giro), -math.cos(giro)
    radio = 0.10

    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radio, segments=48, ring_count=24, location=(gx, gy, mesa_z + 0.026))
    copa = bpy.context.object
    copa.name = "PROP_gorra_copa"
    copa.scale = (1.0, 1.02, 0.82)
    copa.rotation_euler = (0, 0, giro)
    bpy.ops.object.shade_smooth()
    _reubicar(col, copa)

    # Costuras de los seis gajos: tres aros verticales girados entre sí.
    for i in range(3):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=radio * 0.995, minor_radius=0.0016,
            major_segments=48, minor_segments=6,
            location=(gx, gy, mesa_z + 0.026))
        costura = bpy.context.object
        costura.name = "PROP_gorra_costura_%d" % i
        costura.rotation_euler = (math.radians(90), 0, giro + i * math.radians(60))
        costura.scale = (1.0, 0.82, 1.0)
        bpy.ops.object.shade_smooth()
        _reubicar(col, costura)

    # Botón superior.
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.008, segments=16, ring_count=8,
        location=(gx, gy, mesa_z + 0.026 + radio * 0.82))
    boton = bpy.context.object
    boton.name = "PROP_gorra_boton"
    bpy.ops.object.shade_smooth()
    _reubicar(col, boton)

    # Visera: esfera achatada recortada, para que tenga curvatura real en vez
    # de ser un disco plano.
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.15, segments=40, ring_count=20,
        location=(gx, gy, mesa_z + 0.028))
    visera = bpy.context.object
    visera.name = "PROP_gorra_visera"
    visera.scale = (0.80, 1.20, 0.075)
    # Se gira la esfera ANTES de cortar: si sólo se gira la caja de recorte,
    # la intersección sale desviada y la visera envuelve por los lados.
    visera.rotation_euler = (0, 0, giro)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.shade_smooth()
    _reubicar(col, visera)

    recorte = _caja(col, "CORTE_visera",
                    (gx + frente_x * 0.115, gy + frente_y * 0.115, mesa_z + 0.028),
                    (0.20, 0.155, 0.08))
    recorte.rotation_euler = (0, 0, giro)
    corte = visera.modifiers.new("corte", "BOOLEAN")
    corte.operation = "INTERSECT"
    corte.object = recorte
    bpy.context.view_layer.objects.active = visera
    bpy.ops.object.modifier_apply(modifier=corte.name)
    bpy.data.objects.remove(recorte, do_unlink=True)
    # La geometría ya salió orientada del booleano; volver a girarla en Z la
    # desviaba. Sólo se inclina alrededor del eje transversal de la gorra.
    visera.rotation_euler = (0.22 * math.cos(giro), 0.22 * math.sin(giro), 0)

    # Parche frontal con el monograma de la marca.
    parche = _caja(col, "PROP_gorra_parche",
                   (gx + frente_x * 0.094, gy + frente_y * 0.094, mesa_z + 0.072),
                   (0.056, 0.006, 0.042))
    parche.rotation_euler = (0.1, 0, giro)


def _parche_gorra(col, mesa_z):
    """Monograma de la marca ficticia bordado en el parche."""
    gx, gy, giro = GORRA_POS[0], ALTAR_Y + GORRA_POS[1], GORRA_POS[2]
    frente_x, frente_y = math.sin(giro), -math.cos(giro)

    mono = _texto(col, "PROP_gorra_monograma", MARCA_MONOGRAMA,
                  (gx + frente_x * 0.101, gy + frente_y * 0.101, mesa_z + 0.078),
                  alto=0.028, extrusion=0.002)
    mono.rotation_euler = (math.radians(90) + 0.1, 0, giro)

    nombre = _texto(col, "PROP_gorra_marca", MARCA,
                    (gx + frente_x * 0.101, gy + frente_y * 0.101, mesa_z + 0.060),
                    alto=0.0068, extrusion=0.001)
    nombre.rotation_euler = (math.radians(90) + 0.1, 0, giro)


def _devocion(col, mesa_z):
    """Escapulario y rosario colgando de los nichos, cadena con el rayo en la
    mesa. Lo que cuelga de un altar real no es decoración: es promesa."""
    azar = random.Random(53)

    # Escapulario sobre el marco del nicho central.
    x_centro = HORNACINA_X[1]
    borde = HORNACINA_Z + HORNACINA_ALTO / 2 + 0.03
    # La placa frontal es un plano con grosor, no un cubo: un cubo mapea la
    # estampa por cara y sale recortada. El alto sigue la proporción real de
    # la imagen (480x790) para que la figura no se deforme.
    ancho_placa = 0.095
    alto_placa = ancho_placa * 790 / 480
    bpy.ops.mesh.primitive_plane_add(
        size=1.0, location=(x_centro + 0.30, RETABLO_Y - 0.315, borde - 0.30))
    frente = bpy.context.object
    frente.name = "PROP_escapulario_frente"
    frente.rotation_euler = (math.radians(90), 0, 0.05)
    frente.scale = (ancho_placa, alto_placa, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    grosor = frente.modifiers.new("grosor", "SOLIDIFY")
    grosor.thickness = 0.006
    _reubicar(col, frente)

    espalda = _caja(col, "PROP_escapulario_espalda",
                    (x_centro + 0.30, RETABLO_Y - 0.30, borde - 0.37),
                    (ancho_placa, 0.007, alto_placa))
    espalda.rotation_euler = (0.08, 0, 0.05)
    for lado in (-1, 1):
        cordon = _cilindro(col, "PROP_escapulario_cordon_%d" % lado,
                           (x_centro + 0.30 + lado * 0.062, RETABLO_Y - 0.305,
                            borde - 0.07), 0.005, 0.30, 8)
        cordon.rotation_euler = (0, lado * 0.06, 0)

    # Rosario de madera colgando del marco del nicho izquierdo.
    x_izq = HORNACINA_X[0] - HORNACINA_ANCHO / 2 + 0.06
    for i in range(18):
        angulo = i / 18.0 * math.pi * 2
        _cilindro(col, "PROP_rosario_nicho_%d" % i,
                  (x_izq + 0.075 * math.cos(angulo), RETABLO_Y - 0.31,
                   HORNACINA_Z + 0.22 + 0.15 * math.sin(angulo)),
                  0.011, 0.012, 8)
    _caja(col, "PROP_rosario_cruz_v",
          (x_izq, RETABLO_Y - 0.31, HORNACINA_Z - 0.01), (0.016, 0.01, 0.075))
    _caja(col, "PROP_rosario_cruz_h",
          (x_izq, RETABLO_Y - 0.31, HORNACINA_Z + 0.018), (0.052, 0.01, 0.016))

    # Cadena cubana con el dije del rayo, sobre la mesa. Con el asset de cadena
    # los eslabones sobran: se quedaría una cadena encima de la otra.
    assets_cub = _cargar_assets()
    if assets_cub is None or not assets_cub.disponible(assets_cub.CADENA):
        _cubana_greybox(col, mesa_z)
        dije_pos = (0.02 + 0.028 * 22 - 0.30, ALTAR_Y + 0.36, mesa_z + 0.014)
    else:
        # Dentro del rollo de la cadena, que es donde cae un dije al soltarlo.
        dije_pos = (0.05, ALTAR_Y + 0.22, mesa_z + 0.014)
    dije = _rayo(col, "PROP_dije_rayo", dije_pos, alto=0.075, grosor=0.008)
    dije.rotation_euler = (1.57, 0.35, 0)

    # Vicios de la mesa: montón de cigarros de papel junto al micrófono, un
    # cigarro apoyado en el borde del cenicero y su colilla al lado.
    assets_vicio = _cargar_assets()
    if assets_vicio is not None and assets_vicio.disponible(assets_vicio.PRERROLLOS):
        # Aquí y no en el escalón: medido proyectando a cámara, en el escalón
        # salían a 8 px en los planos generales y fuera de cuadro en el resto.
        # Junto al micro ocupan 118 px en el plano de la reliquia.
        assets_vicio.prerrollos(col, (0.5371, ALTAR_Y - 0.4426, mesa_z),
                                ancho=0.11, giro=0.3)
    if assets_vicio is not None and assets_vicio.disponible(assets_vicio.CIGARROS):
        assets_vicio.cigarro_suelto(col, "PROP_cigarro_borde",
                                    (-0.34, 6.86, mesa_z + 0.075), giro=0.9)
        assets_vicio.cigarro_suelto(col, "PROP_cigarro_colilla",
                                    (-0.62, 6.66, mesa_z), giro=-0.5,
                                    colilla=True)

    # Cinturón piteado con hebilla: identidad del género sin marca de nadie.
    # CINTURON_DY se colocó a mano en el visor; la hebilla y las puntadas
    # cuelgan de él para que el conjunto se mueva de una pieza.
    CINTURON_DY = -0.52472
    correa = _caja(col, "PROP_cinturon", (1.15, ALTAR_Y + CINTURON_DY, mesa_z + 0.008),
                   (0.62, 0.075, 0.012))
    correa.rotation_euler = (0, 0, -0.12)
    for i in range(22):
        avance = -0.28 + i * 0.026
        for borde_y in (-0.028, 0.028):
            puntada = _caja(col, "PROP_pitiado_%d_%d" % (i, int(borde_y * 1000)),
                            (1.15 + avance * math.cos(-0.12),
                             ALTAR_Y + CINTURON_DY + borde_y
                             + avance * math.sin(-0.12),
                             mesa_z + 0.0145), (0.012, 0.004, 0.002))
            puntada.rotation_euler = (0, 0, -0.12)

    hebilla = _caja(col, "PROP_hebilla",
                    (0.78, ALTAR_Y + CINTURON_DY + 0.04, mesa_z + 0.014),
                    (0.125, 0.092, 0.012))
    hebilla.rotation_euler = (0, 0, -0.12)
    bisel_hebilla = hebilla.modifiers.new("bisel", "BEVEL")
    bisel_hebilla.width = 0.006
    bisel_hebilla.segments = 3
    mono_hebilla = _texto(col, "PROP_hebilla_monograma", MARCA_MONOGRAMA,
                          (0.78, ALTAR_Y + CINTURON_DY + 0.04, mesa_z + 0.021),
                          alto=0.052,
                          extrusion=0.003)
    mono_hebilla.rotation_euler = (0, 0, -0.12)


def _alfombra(col):
    """Alfombra del pasillo central, como en cualquier parroquia: guía la vista
    al altar y rompe la losa lisa."""
    _caja(col, "ALFOMBRA_pasillo", (0, -1.4, 0.006), (1.7, 13.6, 0.012))
    for signo in (-1, 1):
        _caja(col, "ALFOMBRA_franja_%d" % signo,
              (signo * 0.76, -1.4, 0.0125), (0.09, 13.6, 0.013))


def _desechos(col):
    """Confeti y colillas en el piso. El suelo limpio delataba el render."""
    azar = random.Random(31)
    for i in range(70):
        # concentrados en el pasillo central y hacia la cámara, que es donde
        # el desenfoque los convierte en destellos dorados
        x = azar.gauss(0, 1.15)
        y = azar.uniform(-8.5, 5.5)
        # sobre la alfombra, no debajo
        z = 0.016 if abs(x) < 0.85 and -8.2 < y < 5.4 else 0.003
        pieza = _caja(col, "CONFETI_%d" % i, (x, y, z),
                      (azar.uniform(0.015, 0.03), azar.uniform(0.012, 0.025), 0.0008))
        pieza.rotation_euler = (azar.uniform(-0.3, 0.3), azar.uniform(-0.3, 0.3),
                                azar.uniform(0, 3.14))
    for i in range(14):
        cx, cy = azar.gauss(0, 1.3), azar.uniform(-8.0, 5.0)
        cz = 0.021 if abs(cx) < 0.85 and -8.2 < cy < 5.4 else 0.008
        colilla = _cilindro(col, "COLILLA_%d" % i, (cx, cy, cz), 0.0055, 0.042, 8)
        colilla.rotation_euler = (1.57, 0, azar.uniform(0, 3.14))


def _mobiliario(col):
    """Bancas y candelabros: dan escala a la nave y pueblan los planos generales."""
    for lado, signo in (("izq", -1), ("der", 1)):
        for i in range(5):
            # La última banca izquierda no se pone: ese claro lo ocupa el
            # tololoche, y forzarlo en el hueco entre banca y escalón lo dejaba
            # siempre atravesando una de las dos.
            if (lado, i) == ("izq", 4):
                continue
            y = -5.5 + i * 2.1
            x = signo * 1.95
            _caja(col, "BANCA_%s_%d" % (lado, i), (x, y, 0.45), (1.5, 0.42, 0.1))
            _caja(col, "BANCA_respaldo_%s_%d" % (lado, i),
                  (x, y - signo * 0.0 - 0.2, 0.72), (1.5, 0.08, 0.45))
            for dx in (-0.6, 0.6):
                _caja(col, "BANCA_pata_%s_%d_%d" % (lado, i, int(dx * 10)),
                      (x + dx, y, 0.22), (0.1, 0.34, 0.45))

    # Candelabros de pie flanqueando los escalones del altar. Si el asset no
    # está, se cae a los cilindros de siempre.
    assets_cand = _cargar_assets()
    hay_candelabro = (assets_cand is not None
                      and assets_cand.disponible(assets_cand.CANDELABRO))
    for signo in (-1, 1):
        x = signo * 1.9
        if hay_candelabro:
            # Los brazos abren hacia el centro de la nave: el asset los saca en
            # su eje X, así que el de la izquierda va girado media vuelta.
            # Sobre el escalón alto y pegados a los lados: es la única
            # colocación que no toca nada. Comprobado con cajas envolventes;
            # más al centro choca con el tololoche.
            assets_cand.candelabro(col, "CANDELABRO_%d" % signo,
                                   (signo * 2.3, ALTAR_Y - 1.4, 0.36),
                                   alto=0.95,
                                   giro=0.0 if signo < 0 else math.pi)
            continue
        _cilindro(col, "CANDELABRO_pie_%d" % signo, (x, ALTAR_Y - 1.9, 0.55),
                  0.07, 1.1, 12)
        _cilindro(col, "CANDELABRO_base_%d" % signo, (x, ALTAR_Y - 1.9, 0.04),
                  0.24, 0.08, 16)
        _cilindro(col, "CANDELABRO_plato_%d" % signo, (x, ALTAR_Y - 1.9, 1.12),
                  0.16, 0.04, 16)
        _cilindro(col, "VELADORA_pie_%d" % signo, (x, ALTAR_Y - 1.9, 1.28),
                  0.06, 0.28, 16)


def _cargar_assets():
    """blender/assets.py, cargado a mano: este script se ejecuta con exec() y
    no hay paquete del que importar."""
    import os
    ruta = os.path.join(os.path.dirname(__file__) if "__file__" in dir() else "",
                        "assets.py")
    if not os.path.exists(ruta):
        ruta = r"E:\Cursor Projects\MTO\blender\assets.py"
    if not os.path.exists(ruta):
        return None
    espacio = {}
    exec(open(ruta).read(), espacio)
    class Modulo:
        pass
    modulo = Modulo()
    for clave, valor in espacio.items():
        setattr(modulo, clave, valor)
    return modulo


def _reliquias(col):
    mesa_z = ALTAR_ALTO + 0.08

    assets_velas = _cargar_assets()
    hay_trio = (assets_velas is not None
                and assets_velas.disponible(assets_velas.VELAS))
    if hay_trio:
        # Donde la cámara se acerca, velas de verdad; en el resto, cilindros,
        # que a esa distancia rinden igual y cuestan mucho menos.
        assets_velas.trio_velas(col, "TRIO_velas_izq",
                                (-0.62, ALTAR_Y - 0.42, mesa_z), alto=0.20, giro=0.25)
        assets_velas.trio_velas(col, "TRIO_velas_der",
                                (0.46, ALTAR_Y - 0.30, mesa_z), alto=0.23, giro=-0.4)
        # (x, y respecto del altar), colocadas a mano en el visor: las dos
        # primeras se adelantaron hacia la cámara, las otras dos siguen en fila.
        posiciones = ((-0.92, -0.2188), (0.622, -0.1099), (1.16, -0.32),
                      (1.36096, -0.32))
    else:
        posiciones = tuple((-1.05 + i * (1.6 / (VELADORAS - 1)), -0.32)
                           for i in range(VELADORAS))
    for i, (x, dy) in enumerate(posiciones):
        _cilindro(col, "VELADORA_%d" % i,
                  (x, ALTAR_Y + dy, mesa_z + 0.11), 0.055, 0.22, 16)

    # Vinilos acostados sobre la mesa del altar: la estación del sonido
    # los mira en picado, no de frente.
    _cilindro(col, "PROXY_vinilo", (1.05, ALTAR_Y + 0.05, mesa_z + 0.012),
              0.175, 0.024, 32)
    disco = _cilindro(col, "VINILO_ladeado",
                      (1.62938, ALTAR_Y - 0.26732, mesa_z + 0.012),
                      0.175, 0.022, 32)
    disco.rotation_euler = (0, 0, 0.4)
    pila = _cilindro(col, "VINILO_pila", (0.62, ALTAR_Y + 0.3, mesa_z + 0.05),
                     0.168, 0.09, 32)
    pila.rotation_euler = (0.03, 0.02, 0)

    # Etiquetas: sin ellas los discos son manchas negras sin lectura.
    for nombre, (x, y, z) in (
        ("ETIQUETA_principal", (1.05, ALTAR_Y + 0.05, mesa_z + 0.025)),
        ("ETIQUETA_ladeado", (1.62938, ALTAR_Y - 0.26732, mesa_z + 0.024)),
        ("ETIQUETA_pila", (0.62, ALTAR_Y + 0.3, mesa_z + 0.101)),
    ):
        _cilindro(col, nombre, (x, y, z), 0.058, 0.002, 24)

    # El micrófono es un asset externo (CC-0). Si no está, se cae al proxy de
    # siempre: la escena tiene que poder construirse sin los .blend de terceros,
    # que no se versionan.
    assets = _cargar_assets()
    if assets is not None and assets.disponible(assets.MICROFONO):
        assets.microfono(col, (-1.28, ALTAR_Y + 0.02, mesa_z), alto=0.26, giro=0.6)
    else:
        micro = _cilindro(col, "PROXY_micro",
                          (-0.95, ALTAR_Y + 0.08, mesa_z + 0.09), 0.048, 0.18, 20)
        micro.rotation_euler = (0.42, 0, 0.3)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.062, segments=16, ring_count=10,
            location=(-0.95, ALTAR_Y + 0.02, mesa_z + 0.2))
        rejilla = bpy.context.object
        rejilla.name = "MICRO_rejilla"
        _reubicar(col, rejilla)

    # Cadena enrollada sobre la mesa. El proxy era un toro aplastado; con el
    # asset se ven los eslabones y el broche.
    assets_cad = _cargar_assets()
    if assets_cad is not None and assets_cad.disponible(assets_cad.CADENA):
        assets_cad.cadena(col, (0.05, ALTAR_Y + 0.22, mesa_z), ancho=0.20,
                          giro=0.4)
    else:
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.22, minor_radius=0.018,
            major_segments=28, minor_segments=8,
            location=(0.05, ALTAR_Y + 0.22, mesa_z + 0.02))
        cadena = bpy.context.object
        cadena.name = "PROXY_cadena"
        cadena.scale = (1.0, 0.55, 0.35)
        _reubicar(col, cadena)

    _caja(col, "PROXY_placa",
          (0, ALTAR_Y - ALTAR_FONDO / 2 - 0.04, 0.58), (1.5, 0.06, 0.62))

    _props(col, mesa_z)
    _devocion(col, mesa_z)
    if bpy.data.objects.get("PROP_gorra_copa") is not None:
        _parche_gorra(col, mesa_z)
    _mobiliario(col)
    _exvotos(col)
    _tololoche(col)
    _guirnalda(col)
    _alfombra(col)
    _desechos(col)


def _rig(col):
    curva = bpy.data.curves.new("RECORRIDO", type="CURVE")
    curva.dimensions = "3D"
    spline = curva.splines.new("NURBS")
    spline.points.add(len(RECORRIDO) - 1)
    for punto, (x, y, z) in zip(spline.points, RECORRIDO):
        punto.co = (x, y, z, 1.0)
    spline.use_endpoint_u = True
    spline.order_u = 4
    # bpy.data.curves.new deja use_path en False; sin esto el Follow Path
    # no tiene camino y la cámara se queda en el origen.
    curva.use_path = True
    curva.path_duration = 100
    camino = bpy.data.objects.new("RECORRIDO", curva)
    col.objects.link(camino)

    aim_altar = _empty(col, "AIM_altar", (0, ALTAR_Y, ALTAR_ALTO + 0.55))
    _empty(col, "AIM_retablo", (0, RETABLO_Y - 0.4, HORNACINA_Z))

    aim = _empty(col, "AIM", aim_altar.location)
    foco = _empty(col, "FOCO", aim_altar.location)

    camara_data = bpy.data.cameras.new("CAM_santuario")
    camara_data.lens = 38.0
    camara_data.dof.use_dof = True
    camara_data.dof.focus_object = foco
    camara_data.dof.aperture_fstop = 2.0
    camara = bpy.data.objects.new("CAM_santuario", camara_data)
    col.objects.link(camara)
    bpy.context.scene.camera = camara

    seguir = camara.constraints.new("FOLLOW_PATH")
    seguir.target = camino
    seguir.use_fixed_location = True
    seguir.use_curve_follow = False

    mirar = camara.constraints.new("TRACK_TO")
    mirar.target = aim
    mirar.track_axis = "TRACK_NEGATIVE_Z"
    mirar.up_axis = "UP_Y"

    return camara, seguir, aim, foco


def _animar(seguir, aim, foco):
    """Cada estación fija tres canales: recorrido, encuadre y enfoque."""
    escena = bpy.context.scene
    escena.frame_start = ESTACIONES[0][1]
    escena.frame_end = ESTACIONES[-1][1]

    camara = bpy.context.scene.camera
    for nombre, frame, offset, aim_obj, foco_obj, focal, alto, fstop in ESTACIONES:
        seguir.offset_factor = offset
        seguir.keyframe_insert("offset_factor", frame=frame)

        aim.location = bpy.data.objects[aim_obj].matrix_world.translation
        aim.keyframe_insert("location", frame=frame)

        foco.location = bpy.data.objects[foco_obj].matrix_world.translation
        foco.keyframe_insert("location", frame=frame)

        camara.data.lens = focal
        camara.data.keyframe_insert("lens", frame=frame)

        camara.data.dof.aperture_fstop = fstop
        camara.data.dof.keyframe_insert("aperture_fstop", frame=frame)

        camara.location.z = alto
        camara.keyframe_insert("location", index=2, frame=frame)

        marcador = escena.timeline_markers.new(nombre, frame=frame)
        marcador.select = False


def _luz_greybox(col):
    """Luz plana y provisional: en fase 1 solo se juzgan volúmenes y encuadre."""
    bpy.ops.object.light_add(type="AREA", location=(1.5, 1.0, 5.2))
    key = bpy.context.object
    key.name = "GREYBOX_key"
    key.data.energy = 900.0
    key.data.size = 4.0
    key.rotation_euler = (0.5, 0.25, 0.0)
    _reubicar(col, key)

    bpy.ops.object.light_add(type="AREA", location=(0.0, 6.4, 2.6))
    fill = bpy.context.object
    fill.name = "GREYBOX_fill"
    fill.data.energy = 220.0
    fill.data.size = 3.0
    fill.rotation_euler = (1.35, 0, 3.14159)
    _reubicar(col, fill)

    mundo = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = mundo
    mundo.use_nodes = True
    fondo = mundo.node_tree.nodes["Background"]
    fondo.inputs[0].default_value = (0.02, 0.02, 0.024, 1.0)
    fondo.inputs[1].default_value = 0.35


def build():
    col = _limpiar()
    _arquitectura(col)
    _reliquias(col)
    camara, seguir, aim, foco = _rig(col)
    _animar(seguir, aim, foco)
    _luz_greybox(col)

    escena = bpy.context.scene
    escena.render.engine = "BLENDER_EEVEE"
    escena.render.film_transparent = False
    bpy.context.view_layer.update()
    return {
        "objetos": len(col.objects),
        "estaciones": [e[0] for e in ESTACIONES],
        "frames": [e[1] for e in ESTACIONES],
    }


def render_stills(out_dir, ancho=480, alto=270):
    """Stills de puerta: uno por estación, baratos y feos a propósito."""
    import os
    escena = bpy.context.scene
    escena.render.resolution_x = ancho
    escena.render.resolution_y = alto
    escena.render.resolution_percentage = 100
    escena.render.image_settings.file_format = "PNG"
    escena.render.use_motion_blur = False
    os.makedirs(out_dir, exist_ok=True)
    escritos = []
    for indice, (nombre, frame, *_resto) in enumerate(ESTACIONES):
        escena.frame_set(frame)
        escena.render.filepath = os.path.join(out_dir, "%d-%s.png" % (indice, nombre))
        bpy.ops.render.render(write_still=True)
        escritos.append(escena.render.filepath)
    return escritos


# Sólo estos pueden ser primer plano. La arquitectura queda fuera: su origen
# está en el centro de una malla enorme, así que la distancia al origen no dice
# nada sobre si tapa o no a la cámara.
PREFIJOS_FRENTE = (
    "COLUMNA_", "BANCA_", "CANDELABRO_", "PROP_", "VELADORA_", "LLAMA_",
    "VINILO_", "ETIQUETA_", "MICRO_", "PROXY_micro", "PROXY_cadena",
)


def render_capa_frontal(out_dir, ancho=800, alto=450, margen=0.78):
    """Capa con alfa de lo que queda DELANTE del sujeto enfocado.

    Se compone por encima del texto HTML, así la tipografía queda dentro de la
    escena en vez de flotar sobre ella: una columna pasa frente al título.
    Sólo se renderiza en las estaciones; durante los tramos se oculta.

    `margen` define el umbral: es primer plano lo que esté más cerca que la
    distancia cámara->objeto enfocado multiplicada por este factor.
    """
    import os
    escena = bpy.context.scene
    camara = escena.camera
    escena.render.resolution_x = ancho
    escena.render.resolution_y = alto
    escena.render.image_settings.file_format = "PNG"
    escena.render.image_settings.color_mode = "RGBA"
    escena.render.film_transparent = True
    os.makedirs(out_dir, exist_ok=True)

    # La niebla del mundo llenaría el alfa entero: se desconecta mientras dura.
    mundo = escena.world
    enlaces_volumen = []
    if mundo and mundo.use_nodes:
        salida_mundo = mundo.node_tree.nodes.get("World Output")
        if salida_mundo:
            for enlace in list(mundo.node_tree.links):
                if enlace.to_socket == salida_mundo.inputs["Volume"]:
                    enlaces_volumen.append((enlace.from_socket, enlace.to_socket))
                    mundo.node_tree.links.remove(enlace)

    mallas = [o for o in bpy.data.objects if o.type == "MESH"]
    ocultos_previos = {o.name: o.hide_render for o in mallas}
    escritos = []
    try:
        for indice, (nombre, frame, _o, _a, foco_obj, *_r) in enumerate(ESTACIONES):
            escena.frame_set(frame)
            bpy.context.view_layer.update()
            grafo = bpy.context.evaluated_depsgraph_get()
            origen = camara.evaluated_get(grafo).matrix_world.translation
            sujeto = bpy.data.objects[foco_obj].matrix_world.translation
            umbral = (sujeto - origen).length * margen

            frontales = 0
            for ob in mallas:
                candidato = ob.name.startswith(PREFIJOS_FRENTE)
                distancia = (ob.matrix_world.translation - origen).length
                ob.hide_render = not (candidato and distancia < umbral)
                frontales += not ob.hide_render

            escena.render.filepath = os.path.join(
                out_dir, "%d-%s-frente.png" % (indice, nombre))
            bpy.ops.render.render(write_still=True)
            escritos.append((nombre, frontales, round(umbral, 2)))
    finally:
        for ob in mallas:
            ob.hide_render = ocultos_previos.get(ob.name, False)
        for desde, hacia in enlaces_volumen:
            mundo.node_tree.links.new(desde, hacia)
        escena.render.film_transparent = False
        escena.render.image_settings.color_mode = "RGB"
    return escritos
