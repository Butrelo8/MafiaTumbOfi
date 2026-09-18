"""Assets 3D externos.

Los `.blend` de terceros viven en `blender/assets/` y **no** se versionan: son
binarios pesados. Este módulo los trae a la escena, los limpia y los coloca, de
modo que lo versionado sigue siendo el código que los coloca, no el asset.

Licencias en `blender/assets/*-LICENSE.txt` y en `public/scene/CREDITOS.md`.
"""

import bmesh
import bpy
import math
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
CADENA = "cadena.blend"              # cubana enrollada, con broche
CADENA_POLIGONOS = 20000
PRERROLLOS = "prerolls.blend"        # cinco cigarros de papel, en montón
PRERROLLOS_POLIGONOS = 12000

# Cigarros sueltos de terceros: llegan ya a escala real y con sus texturas.
# Licencia SIN VERIFICAR, ver public/scene/CREDITOS.md. Se importan sólo las
# dos mallas y se les quita el material, así que de momento sólo entra la
# geometría.
CIGARROS = "cigarros.blend"
CIGARRO_ENTERO = "Cigarette_01_GEO"
CIGARRO_COLILLA = "Cigarette_02_GEO"

# Púa de celuloide. El .blend trae además el estudio del autor: un suelo de
# 21 m, dos paneles de luz y una cámara. Sólo entra `Plane`, que es la púa.
# Licencia SIN VERIFICAR, ver public/scene/CREDITOS.md.
PUA = "pick.blend"
PUA_PIEZA = "Plane"
PUA_POLIGONOS = 400

# Tracerías góticas, CC0: 29 mallas planas en el plano XY —X ancho, Y alto,
# Z grosor 0.02— sin cristal, sin derrame y sin marco. Llegan a escala de
# dibujo, no de metros, así que se escalan por altura y nunca por factor.
VENTANAS = "ventanas-goticas.blend"
VENTANA_ROSETON = "window_gothic_8"    # cuatro luces y óculo: el presbiterio
VENTANA_LANCETA = "window_gothic_2"    # lanceta lisa: la nave


def ventana(col, pieza, nombre, ubicacion, alto, hacia_dentro):
    """Tracería de pie contra un muro lateral, con su cristal detrás.

    Devuelve `(traceria, cristal, cortador)`. Los dos salen del contorno
    exterior de la propia tracería: el cristal encogido un 3% para que su canto
    quede detrás del marco, y el cortador engordado a lo ancho del muro. Así el
    hueco tiene **la forma exacta del arco** sin recortar nada a mano.

    La malla llega tumbada. Se levanta y se gira para que el grosor quede en X,
    que es la normal de los muros laterales; `hacia_dentro` es el signo que
    empuja la tracería hacia la nave.
    """
    traceria = _traer(VENTANAS, (pieza,))[0]
    traceria.name = nombre
    # El asset llega con scale 100 ya puesta y `dimensions` la incluye: hay que
    # multiplicar la escala, no sustituirla, o la ventana sale de 2 cm.
    escala = alto / traceria.dimensions.y
    traceria.scale = tuple(v * escala for v in traceria.scale)
    traceria.rotation_euler = (math.radians(90), 0, math.radians(90))
    traceria.location = (ubicacion[0] + hacia_dentro * 0.16,
                         ubicacion[1], ubicacion[2])
    bpy.ops.object.select_all(action="DESELECT")
    traceria.select_set(True)
    bpy.context.view_layer.objects.active = traceria
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    traceria.data.materials.clear()
    for otra in list(traceria.users_collection):
        otra.objects.unlink(traceria)
    col.objects.link(traceria)

    def _perfil(sufijo, grosor, encoger, franjas=160):
        """El contorno EXTERIOR de la tracería, relleno y engordado.

        Ni el casco convexo ni los bucles de borde sirven: el primero cambia la
        curva del arco por dos rectas y abre un hueco más alto que la ventana;
        los segundos no existen, porque la malla es un sólido biselado y no hay
        ninguna cara mirando de frente.

        Se mide por franjas de altura: a cada altura, el material más a la
        izquierda y el más a la derecha son el marco de fuera, así que subir por
        un lado y bajar por el otro dibuja el contorno. Vale para cualquier
        ventana de este pack porque todas son de una sola luz por altura.
        """
        puntos = [v.co for v in traceria.data.vertices]
        z0 = min(p.z for p in puntos)
        z1 = max(p.z for p in puntos)
        paso = (z1 - z0) / franjas
        izquierda, derecha = [], []
        for i in range(franjas + 1):
            z = z0 + paso * i
            dentro = [p.y for p in puntos if abs(p.z - z) <= paso]
            if not dentro:
                continue
            izquierda.append((min(dentro), z))
            derecha.append((max(dentro), z))

        contorno = izquierda + list(reversed(derecha))
        malla = bpy.data.meshes.new(nombre.replace("traceria", sufijo))
        bm = bmesh.new()
        vertices = [bm.verts.new((0.0, y, z)) for y, z in contorno]
        bm.faces.new(vertices)
        bm.normal_update()
        salida = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
        movidos = [g for g in salida["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=(grosor, 0, 0), verts=movidos)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(malla)
        bm.free()

        copia = bpy.data.objects.new(malla.name, malla)
        col.objects.link(copia)
        copia.matrix_world = traceria.matrix_world.copy()
        bpy.ops.object.select_all(action="DESELECT")
        copia.select_set(True)
        bpy.context.view_layer.objects.active = copia
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
        copia.scale = (1.0, encoger, encoger)
        # Centrado en el eje del muro: descentrarlo medio grosor deja la mitad
        # interior del muro sin cortar y la ventana no se ve desde la nave.
        copia.location = (ubicacion[0], copia.location.y, copia.location.z)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        return copia

    cristal = _perfil("vidrio", 0.06, 0.97)
    cortador = _perfil("corte", 1.2, 0.995)
    return traceria, cristal, cortador


# Fiel sentada en una banca. El .blend trae la escena del autor —dos soles, un
# suelo, una cámara, una icosfera— y una acción de caminar que en esta escena se
# reproduciría con el scroll: sólo entran la armadura y la malla, y sin acción.
# Rig de 72 huesos con IK en los pies, así que se sienta moviendo la cadera y
# los dos controles de pie: las rodillas las dobla el IK solo.
MUJER = "mujer.blend"
MUJER_PIEZAS = ("Armature", "Low Poly Characte.001")
MUJER_ALTO_ORIGEN = 5.88      # estatura en las unidades del asset
MUJER_POLIGONOS = 9000


def mujer(col, ubicacion, estatura=1.62, giro=0.0, pose=None):
    """Trae a la fiel, la escala a estatura humana y la sienta.

    `pose` es un diccionario `hueso -> (traslación, cuaternión)` en espacio de
    hueso, tal cual `matrix_basis`. Lo que no pase por aquí se pierde: si la
    pose se retoca en el visor, hay que volcarla a las constantes.
    """
    from mathutils import Matrix, Quaternion, Vector

    traidos = _traer(MUJER, MUJER_PIEZAS)
    armadura = next((o for o in traidos if o.type == "ARMATURE"), None)
    malla = next((o for o in traidos if o.type == "MESH"), None)
    if armadura is None or malla is None:
        return None

    for ob in traidos:
        ob.animation_data_clear()
        for otra in list(ob.users_collection):
            otra.objects.unlink(ob)
        col.objects.link(ob)

    # El Subsurf del autor multiplica la malla por cuatro al renderizar, y el
    # Collision no pinta nada en una escena sin física.
    for modificador in list(malla.modifiers):
        if modificador.type in {"SUBSURF", "MULTIRES", "COLLISION"}:
            malla.modifiers.remove(modificador)

    factor = estatura / MUJER_ALTO_ORIGEN
    armadura.scale = (factor, factor, factor)
    armadura.rotation_euler = (0, 0, giro)
    armadura.location = ubicacion

    bpy.context.view_layer.objects.active = armadura
    bpy.ops.object.mode_set(mode="POSE")
    for hueso, (traslacion, giro) in (pose or {}).items():
        pb = armadura.pose.bones.get(hueso)
        if pb is None:
            continue
        pb.rotation_mode = "QUATERNION"
        pb.location = Vector(traslacion)
        pb.rotation_quaternion = Quaternion(giro)
    bpy.ops.object.mode_set(mode="OBJECT")

    _decimar(malla, MUJER_POLIGONOS)
    malla.name = "FIEL_cuerpo"
    armadura.name = "FIEL_rig"
    return armadura


# Cinturón de cuero. El .blend trae la escena del autor —esfera de fondo, dos
# luces, una cámara— y su propia hebilla, que no se usa: la nuestra lleva el
# monograma. Sólo entra la correa, que además viene con un modificador Lattice
# cuyo objeto no está en el archivo.
CINTURON = "cinturon.blend"
CINTURON_CORREA = "BezierCircle"      # la correa de cuero
CINTURON_HEBILLA = "Cube"             # la hebilla del autor, en metal
CINTURON_POLIGONOS = 6000

# Rayo M⚡T, generado por el equipo. Malla única, sin materiales ni UV, ya en el
# plano XZ con el grosor en Y: la orientación del retablo.
LOGO = "logo-mt.blend"
LOGO_PIEZA = "mesh_node"
LOGO_POLIGONOS = 20000


def cinturon(col, nombre, ubicacion, ancho=0.30, giro=0.0, inclinacion=0.0):
    """Correa enrollada y su hebilla, apoyadas en la mesa.

    Devuelve `(correa, hebilla)` para darles materiales distintos: cuero y
    metal. Las dos piezas vienen de la misma escena del autor, así que su
    posición relativa ya es la buena; se cuelgan de un ancla común y se mueven
    juntas, como la guitarra.

    Apoyar restando el mínimo de la caja envolvente a la ubicación no vale: el
    origen del asset no está en cero y la correa se fue metro y pico bajo el
    suelo en el primer intento. De ahí el ancla.
    """
    piezas = []
    for pieza_nombre, sufijo in ((CINTURON_CORREA, ""), (CINTURON_HEBILLA, "_hebilla")):
        traidas = _traer(CINTURON, (pieza_nombre,))
        if not traidas:
            continue
        ob = traidas[0]
        ob.name = nombre + sufijo
        # El Lattice de la correa apunta a un objeto que no viene en el archivo.
        for modificador in list(ob.modifiers):
            if modificador.type == "LATTICE":
                ob.modifiers.remove(modificador)
        _sin_subdivision(ob)
        ob.data.materials.clear()
        for otra in list(ob.users_collection):
            otra.objects.unlink(ob)
        col.objects.link(ob)
        _decimar(ob, CINTURON_POLIGONOS)
        piezas.append(ob)
    if not piezas:
        return None, None

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

    ancho_actual = maximos[0] - minimos[0]
    factor = ancho / ancho_actual if ancho_actual else 1.0
    ancla.scale = (factor, factor, factor)
    ancla.rotation_mode = "XYZ"
    ancla.rotation_euler = (inclinacion, 0.0, giro)
    ancla.location = ubicacion
    bpy.context.view_layer.update()
    return piezas[0], (piezas[1] if len(piezas) > 1 else None)


def logo_mt(col, nombre, ubicacion, alto=1.5):
    """El rayo M⚡T sobre el retablo, en el sitio que ocupaba la cruz."""
    logo = _traer(LOGO, (LOGO_PIEZA,))[0]
    logo.name = nombre
    _sin_subdivision(logo)
    logo.data.materials.clear()
    for otra in list(logo.users_collection):
        otra.objects.unlink(logo)
    col.objects.link(logo)
    _decimar(logo, LOGO_POLIGONOS)
    # `ubicacion` es el CENTRO del rayo, no su base: es lo que era la cruz.
    minimos, maximos = _caja_mundo([logo])
    _plantar(logo, (ubicacion[0], ubicacion[1], ubicacion[2] - alto / 2), alto,
             nombre_ancla="CRUZ_logo_ancla")
    return logo


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


def _malla_unica(archivo, nombre, col, techo, cual=None):
    """Trae una malla de un .blend generado, la limpia y la decima.

    `cual` elige por nombre cuando el archivo trae más de una; sin él se unen
    todas, que es lo que hace falta en los assets de una sola pieza.
    """
    ruta = os.path.join(CARPETA, archivo)
    with bpy.data.libraries.load(ruta, link=False) as (origen, destino):
        destino.objects = [cual] if cual else list(origen.objects)
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


def prerrollos(col, ubicacion, ancho=0.14, giro=0.0):
    """Montón de cigarros de papel. Se escala por el ancho, como los lentes."""
    pieza = _malla_unica(PRERROLLOS, "PROP_prerrollos", col, PRERROLLOS_POLIGONOS)
    if pieza is None:
        return None
    minimos, maximos = _caja_mundo([pieza])
    ancho_actual = maximos[0] - minimos[0]
    alto_actual = maximos[2] - minimos[2]
    alto = alto_actual * (ancho / ancho_actual) if ancho_actual else alto_actual
    return _plantar(pieza, ubicacion, alto, giro=giro,
                    nombre_ancla="PROP_prerrollos_ancla")


def cigarro_suelto(col, nombre, ubicacion, giro=0.0, colilla=False):
    """Un cigarro (o una colilla aplastada) apoyado donde se le diga.

    El asset viene a escala real, así que no se reescala: sólo se apoya por su
    base y se gira. Se le quita el material del autor; el look de la escena le
    pone el suyo por el prefijo del nombre.
    """
    pieza = _malla_unica(CIGARROS, nombre, col, 2000,
                         cual=CIGARRO_COLILLA if colilla else CIGARRO_ENTERO)
    if pieza is None:
        return None
    minimos, maximos = _caja_mundo([pieza])
    return _plantar(pieza, ubicacion, maximos[2] - minimos[2], giro=giro,
                    nombre_ancla=nombre + "_ancla")


def cadena(col, ubicacion, ancho=0.20, giro=0.0):
    """Cadena cubana enrollada sobre la mesa. Como los lentes, se escala por el
    ancho: tumbada, el alto es el grosor de un eslabón."""
    pieza = _malla_unica(CADENA, "PROXY_cadena", col, CADENA_POLIGONOS)
    if pieza is None:
        return None
    minimos, maximos = _caja_mundo([pieza])
    ancho_actual = maximos[0] - minimos[0]
    alto_actual = maximos[2] - minimos[2]
    alto = alto_actual * (ancho / ancho_actual) if ancho_actual else alto_actual
    return _plantar(pieza, ubicacion, alto, giro=giro,
                    nombre_ancla="PROXY_cadena_ancla")


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


def pua(col, nombre, ubicacion, ancho=0.028, giro=0.0):
    """Púa tumbada sobre la mesa.

    Como los lentes, se escala por el ancho: tumbada, su alto es el grosor del
    celuloide y ajustar por ahí la dejaría del tamaño de un disco.
    """
    pieza = _malla_unica(PUA, nombre, col, PUA_POLIGONOS, cual=PUA_PIEZA)
    if pieza is None:
        return None
    minimos, maximos = _caja_mundo([pieza])
    ancho_actual = maximos[0] - minimos[0]
    alto_actual = maximos[2] - minimos[2]
    alto = alto_actual * (ancho / ancho_actual) if ancho_actual else alto_actual
    return _plantar(pieza, ubicacion, alto, giro=giro,
                    nombre_ancla=nombre + "_ancla")


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
