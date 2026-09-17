"""Assets 3D externos.

Los `.blend` de terceros viven en `blender/assets/` y **no** se versionan: son
binarios pesados. Este módulo los trae a la escena, los limpia y los coloca, de
modo que lo versionado sigue siendo el código que los coloca, no el asset.

Licencias en `blender/assets/*-LICENSE.txt` y en `public/scene/CREDITOS.md`.
"""

import bmesh
import bpy
import os

CARPETA = r"E:\Cursor Projects\MTO\blender\assets"

# Micrófono de cinta sobre pie de mesa, generado por el equipo. Malla única,
# sin materiales ni UV. Llega de pie sobre un disco de escenario de 1.9 m que
# no sirve aquí y que hay que cortar: ver `microfono()`.
MICROFONO = "microfono-spot.blend"
MICRO_POLIGONOS = 12000
MICRO_CORTE_Z = 0.27          # altura relativa por debajo de la cual todo es disco

# Gorra snapback con relieves góticos, generada por el propio equipo. Viene sin
# materiales ni UV: sólo geometría, que es justo lo que interesa.
# Guitarra clásica. El .blend trae la escena entera del autor: soporte, foco,
# entorno y una calcomanía con el material `hohner`, que es una marca real y se
# queda fuera. Sólo se traen las piezas del instrumento.
GUITARRA = "guitarra.blend"
GUITARRA_MADERA = ("Deck", "Deck inside", "Vulture", "Nut",
                   "Fastening", "Fastening two")
GUITARRA_METAL = ("frets", "1", "2", "3", "4", "5", "6",
                  "Screw 1", "Screw 2", "Screw 3", "Screw 4")

# Generados por el equipo, sin materiales ni UV: sólo geometría.
VELAS = "velas.blend"          # trío de velas, malla única e indivisible
VELAS_POLIGONOS = 9000
TOLOLOCHE = "tololoche.blend"
TOLOLOCHE_POLIGONOS = 22000
CANDELABRO = "candelabro.blend"      # nueve brazos, generado por el equipo
CANDELABRO_POLIGONOS = 14000
BOTELLA = "botella.blend"            # tequila cuadrado con tapón de bola
BOTELLA_POLIGONOS = 9000
CENICERO = "cenicero.blend"          # cuenco desbordado de colillas
CENICERO_POLIGONOS = 16000
LENTES = "lentes.blend"              # montura dorada sin aro, patillas abiertas
LENTES_POLIGONOS = 10000

GORRA = "gorra.glb"
GORRA_POLIGONOS = 18000     # techo tras decimar; el original trae ~92k


def disponible(nombre):
    return os.path.exists(os.path.join(CARPETA, nombre))


def _traer(nombre_blend, piezas):
    """Append de objetos concretos; devuelve los objetos ya en la escena."""
    ruta = os.path.join(CARPETA, nombre_blend)
    with bpy.data.libraries.load(ruta, link=False) as (origen, destino):
        destino.objects = [n for n in origen.objects if n in piezas]
    traidos = [o for o in destino.objects if o is not None]
    for ob in traidos:
        bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    return traidos


def _sin_subdivision(ob):
    """Quita los modificadores de subdivisión que traen los assets.

    Un Subsurf a nivel 4 convierte 2.000 caras en 55.000 al renderizar, y
    entonces decimar la malla base no sirve de nada: el coste vuelve a
    aparecer en cada frame.
    """
    for modificador in list(ob.modifiers):
        if modificador.type in {"SUBSURF", "MULTIRES", "EDGE_SPLIT"}:
            ob.modifiers.remove(modificador)
    if ob.type == "MESH":
        for poligono in ob.data.polygons:
            poligono.use_smooth = True
    return ob


def _decimar(ob, techo):
    """Baja la malla a un techo de polígonos. Un instrumento en penumbra al
    fondo no gana nada con 300.000 caras y encarece cada frame."""
    if ob.type != "MESH" or len(ob.data.polygons) <= techo:
        return ob
    modificador = ob.modifiers.new("decimar", "DECIMATE")
    modificador.ratio = techo / len(ob.data.polygons)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=modificador.name)
    return ob


def _unir(objetos, nombre, col):
    """Convierte curvas a malla y une todo en un objeto."""
    bpy.ops.object.select_all(action="DESELECT")
    mallas = []
    for ob in objetos:
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        if ob.type == "CURVE":
            bpy.ops.object.convert(target="MESH")
        mallas.append(bpy.context.view_layer.objects.active)

    bpy.ops.object.select_all(action="DESELECT")
    for ob in mallas:
        ob.select_set(True)
    activo = mallas[0]
    bpy.context.view_layer.objects.active = activo
    if len(mallas) > 1:
        bpy.ops.object.join()
    unido = bpy.context.view_layer.objects.active
    unido.name = nombre
    unido.data.materials.clear()
    _sin_subdivision(unido)
    for otra in list(unido.users_collection):
        otra.objects.unlink(unido)
    col.objects.link(unido)
    return unido


def _caja_mundo(objetos):
    """Caja envolvente real en coordenadas de mundo.

    El origen de un objeto no tiene por qué estar en su centro ni en su base:
    medir con `location` y `dimensions` deja el asset flotando.
    """
    import mathutils
    bpy.context.view_layer.update()
    minimos = [1e9] * 3
    maximos = [-1e9] * 3
    for ob in objetos:
        for esquina in ob.bound_box:
            punto = ob.matrix_world @ mathutils.Vector(esquina)
            for eje in range(3):
                minimos[eje] = min(minimos[eje], punto[eje])
                maximos[eje] = max(maximos[eje], punto[eje])
    return minimos, maximos


def microfono(col, ubicacion, alto=0.26, giro=0.0):
    """Trae el micrófono, le quita el disco de escenario y lo planta en la mesa.

    El asset viene en una sola malla soldada: el disco no se puede separar por
    partes sueltas, así que se corta por geometría. Todo lo que queda por
    debajo de `MICRO_CORTE_Z` (relativo a la base) es disco; la peana del pie
    empieza justo encima. El fondo queda abierto, que no se ve: se apoya en la
    mesa.

    La pieza se llama `PROXY_micro` porque es el objeto al que apunta el foco
    de la estación de la reliquia: renombrarla obligaría a tocar el rig.
    """
    pieza = _malla_unica(MICROFONO, "PROXY_micro", col, MICRO_POLIGONOS)
    if pieza is None:
        return None

    malla = pieza.data
    base = min(v.co.z for v in malla.vertices)
    bm = bmesh.new()
    bm.from_mesh(malla)
    bmesh.ops.delete(
        bm,
        geom=[v for v in bm.verts if (v.co.z - base) < MICRO_CORTE_Z],
        context="VERTS",
    )
    bm.to_mesh(malla)
    bm.free()
    malla.update()
    bpy.context.view_layer.update()

    return _plantar(pieza, ubicacion, alto, giro=giro, nombre_ancla="MICRO_ancla")


def gorra(col, ubicacion, ancho=0.27, giro=0.0, inclinacion=0.0):
    """Importa la gorra .glb, la decima y la apoya por su base.

    El original trae ~92.000 polígonos para un objeto que en el render final
    ocupa unos pocos píxeles; se decima para no cargar la escena.
    """
    ruta = os.path.join(CARPETA, GORRA)
    previos = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=ruta)
    nuevos = [o for o in bpy.data.objects if o not in previos and o.type == "MESH"]
    if not nuevos:
        return None

    pieza = nuevos[0]
    if len(nuevos) > 1:
        bpy.ops.object.select_all(action="DESELECT")
        for ob in nuevos:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = pieza
        bpy.ops.object.join()
        pieza = bpy.context.view_layer.objects.active

    pieza.name = "PROP_gorra"
    pieza.data.materials.clear()
    _sin_subdivision(pieza)
    if len(pieza.data.polygons) > GORRA_POLIGONOS:
        decimar = pieza.modifiers.new("decimar", "DECIMATE")
        decimar.ratio = GORRA_POLIGONOS / len(pieza.data.polygons)
        bpy.context.view_layer.objects.active = pieza
        bpy.ops.object.modifier_apply(modifier=decimar.name)

    for otra in list(pieza.users_collection):
        otra.objects.unlink(pieza)
    col.objects.link(pieza)

    minimos, maximos = _caja_mundo([pieza])
    ancla = bpy.data.objects.new("GORRA_ancla", None)
    col.objects.link(ancla)
    ancla.location = ((minimos[0] + maximos[0]) / 2,
                      (minimos[1] + maximos[1]) / 2,
                      minimos[2])
    bpy.context.view_layer.update()
    matriz = pieza.matrix_world.copy()
    pieza.parent = ancla
    pieza.matrix_parent_inverse = ancla.matrix_world.inverted()
    pieza.matrix_world = matriz

    ancho_actual = maximos[0] - minimos[0]
    factor = ancho / ancho_actual if ancho_actual else 1.0
    ancla.scale = (factor, factor, factor)
    ancla.rotation_mode = "XYZ"
    ancla.rotation_euler = (inclinacion, 0.0, giro)
    ancla.location = ubicacion
    bpy.context.view_layer.update()
    return pieza


def guitarra(col, ubicacion, largo=0.98, giro=0.0, inclinacion=0.0,
             nombre="PROP_requinto"):
    """Trae la guitarra y la recuesta contra el altar.

    Devuelve (madera, metal) para poder darles materiales distintos. El eje
    largo del asset es Z, así que ya viene casi de pie.
    """
    madera = _unir(_traer(GUITARRA, GUITARRA_MADERA), nombre + "_cuerpo", col)
    metal = _unir(_traer(GUITARRA, GUITARRA_METAL), nombre + "_metal", col)
    _decimar(madera, 14000)
    _decimar(metal, 6000)
    piezas = (madera, metal)

    minimos, maximos = _caja_mundo(piezas)
    ancla = bpy.data.objects.new(nombre + "_ancla", None)
    col.objects.link(ancla)
    ancla.location = ((minimos[0] + maximos[0]) / 2,
                      (minimos[1] + maximos[1]) / 2,
                      minimos[2])
    bpy.context.view_layer.update()
    for ob in piezas:
        matriz = ob.matrix_world.copy()
        ob.parent = ancla
        ob.matrix_parent_inverse = ancla.matrix_world.inverted()
        ob.matrix_world = matriz

    largo_actual = maximos[2] - minimos[2]
    factor = largo / largo_actual if largo_actual else 1.0
    ancla.scale = (factor, factor, factor)
    ancla.rotation_mode = "XYZ"
    ancla.rotation_euler = (inclinacion, 0.0, giro)
    ancla.location = ubicacion
    bpy.context.view_layer.update()
    return madera, metal


def _malla_unica(archivo, nombre, col, techo):
    """Trae el único objeto de un .blend generado, lo limpia y lo decima."""
    ruta = os.path.join(CARPETA, archivo)
    with bpy.data.libraries.load(ruta, link=False) as (origen, destino):
        destino.objects = list(origen.objects)
    traidos = [o for o in destino.objects if o is not None and o.type == "MESH"]
    if not traidos:
        return None
    for ob in traidos:
        bpy.context.scene.collection.objects.link(ob)
    pieza = traidos[0]
    if len(traidos) > 1:
        bpy.ops.object.select_all(action="DESELECT")
        for ob in traidos:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = pieza
        bpy.ops.object.join()
        pieza = bpy.context.view_layer.objects.active
    pieza.name = nombre
    pieza.data.materials.clear()
    _sin_subdivision(pieza)
    _decimar(pieza, techo)
    for otra in list(pieza.users_collection):
        otra.objects.unlink(pieza)
    col.objects.link(pieza)
    return pieza


def _plantar(pieza, ubicacion, alto, giro=0.0, inclinacion=0.0, nombre_ancla=None):
    """Escala por altura y apoya por la base, vía un empty que hace de ancla."""
    minimos, maximos = _caja_mundo([pieza])
    ancla = bpy.data.objects.new(nombre_ancla or (pieza.name + "_ancla"), None)
    for coleccion in pieza.users_collection:
        coleccion.objects.link(ancla)
        break
    ancla.location = ((minimos[0] + maximos[0]) / 2,
                      (minimos[1] + maximos[1]) / 2,
                      minimos[2])
    bpy.context.view_layer.update()
    matriz = pieza.matrix_world.copy()
    pieza.parent = ancla
    pieza.matrix_parent_inverse = ancla.matrix_world.inverted()
    pieza.matrix_world = matriz

    alto_actual = maximos[2] - minimos[2]
    factor = alto / alto_actual if alto_actual else 1.0
    ancla.scale = (factor, factor, factor)
    ancla.rotation_mode = "XYZ"
    ancla.rotation_euler = (inclinacion, 0.0, giro)
    ancla.location = ubicacion
    bpy.context.view_layer.update()
    return pieza


def lentes(col, ubicacion, ancho=0.14, giro=0.0):
    """Lentes abiertos sobre la mesa.

    Se escalan por el ancho y no por el alto, que aquí es el grosor: unos
    lentes tumbados miden cuatro centímetros de alto y catorce de ancho, así
    que ajustar por altura los dejaría del tamaño de una mesa.
    """
    pieza = _malla_unica(LENTES, "PROP_lentes_montura", col, LENTES_POLIGONOS)
    if pieza is None:
        return None
    minimos, maximos = _caja_mundo([pieza])
    ancho_actual = maximos[0] - minimos[0]
    alto_actual = maximos[2] - minimos[2]
    alto = alto_actual * (ancho / ancho_actual) if ancho_actual else alto_actual
    return _plantar(pieza, ubicacion, alto, giro=giro,
                    nombre_ancla="PROP_lentes_ancla")


def cenicero(col, ubicacion, alto=0.10, giro=0.0):
    """Cenicero desbordado de colillas. Cuenco y colillas son la misma malla,
    así que comparten material: se le da el de ceniza, porque unas colillas de
    vidrio cantan más que un cenicero mate."""
    pieza = _malla_unica(CENICERO, "PROP_cenicero_lleno", col, CENICERO_POLIGONOS)
    if pieza is None:
        return None
    return _plantar(pieza, ubicacion, alto, giro=giro,
                    nombre_ancla="PROP_cenicero_ancla")


def botella(col, ubicacion, alto=0.26, giro=0.0):
    """Botella de tequila sobre la mesa. Malla única: el líquido, el tapón y el
    lazo son parte de la misma pieza, así que todo va con el mismo vidrio."""
    pieza = _malla_unica(BOTELLA, "PROP_botella", col, BOTELLA_POLIGONOS)
    if pieza is None:
        return None
    return _plantar(pieza, ubicacion, alto, giro=giro,
                    nombre_ancla="PROP_botella_ancla")


def candelabro(col, nombre, ubicacion, alto=1.35, giro=0.0):
    """Candelabro de nueve brazos, de pie. Los brazos salen en el eje X del
    asset, así que `giro` decide hacia dónde abren."""
    pieza = _malla_unica(CANDELABRO, nombre, col, CANDELABRO_POLIGONOS)
    if pieza is None:
        return None
    return _plantar(pieza, ubicacion, alto, giro=giro,
                    nombre_ancla=nombre + "_ancla")


def trio_velas(col, nombre, ubicacion, alto=0.26, giro=0.0):
    """Trío de velas. La malla es única: no se pueden separar en velas sueltas,
    así que se usa como grupo."""
    pieza = _malla_unica(VELAS, nombre, col, VELAS_POLIGONOS)
    if pieza is None:
        return None
    return _plantar(pieza, ubicacion, alto, giro=giro)


def tololoche(col, ubicacion=None, alto=1.85, giro=0.0, inclinacion=0.0,
              pose=None):
    """Tololoche. Con `pose` se fija la colocación exacta.

    `pose` es (traslación, euler en radianes, escala) tal como quedó tras
    colocarlo a mano en Blender. Se usa cuando la posición se decidió moviendo
    el objeto en el visor: los parámetros de ubicación/giro/inclinación no
    pueden describir una pose arbitraria, y traducirla a mano se presta a
    errores. La escala va referida a la geometría de este asset concreto; si el
    .blend cambia, hay que volver a tomarla.
    """
    pieza = _malla_unica(TOLOLOCHE, "PROP_tololoche_cuerpo", col, TOLOLOCHE_POLIGONOS)
    if pieza is None:
        return None
    if pose is not None:
        centro_objetivo, euler, escala = pose
        # Los assets generados llegan en modo quaternion: asignar
        # `rotation_euler` sin cambiar el modo no hace nada, y no avisa.
        pieza.rotation_mode = "XYZ"
        pieza.rotation_euler = euler
        pieza.scale = (escala, escala, escala)
        bpy.context.view_layer.update()
        # La pose se ancla por el centro de la caja, no por `location`: el
        # origen de la malla importada no tiene por qué caer donde cayó en la
        # sesión en que se colocó a mano, y entonces la misma rotación acaba en
        # otro sitio.
        minimos, maximos = _caja_mundo([pieza])
        centro_actual = [(minimos[i] + maximos[i]) / 2 for i in range(3)]
        for eje in range(3):
            pieza.location[eje] += centro_objetivo[eje] - centro_actual[eje]
        bpy.context.view_layer.update()
        return pieza
    return _plantar(pieza, ubicacion, alto, giro=giro, inclinacion=inclinacion,
                    nombre_ancla="PROP_tololoche_ancla")
