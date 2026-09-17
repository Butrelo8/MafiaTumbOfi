"""Santuario M⚡T — construcción de la escena.

Fase 1: greybox y rig de cámara. Sin materiales: solo volúmenes, recorrido,
encuadres y enfoque. Los materiales entran en la fase 2.

Ejecutar dentro de Blender:
    exec(open(r"E:\\Cursor Projects\\MTO\\blender\\altar.py").read())
    build()
"""

import bpy
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

# Estación -> (frame, offset, aim, foco, focal mm, altura extra m, f-stop)
# Seis canales: Follow Path es aditivo sobre la posición del objeto, así que
# "altura extra" sube la cámara por encima del recorrido — la grúa de la
# retirada. El recorrido no es monotónico: la retirada vuelve sobre sus pasos.
ESTACIONES = (
    # Los offsets salen de medir la curva, no de estimarlos: ver
    # docs/plans/…-implementation-plan.md, tarea 1.5.
    ("nave",       1,  0.000, "AIM_altar",     "AIM_altar",         28.0, 0.00, 4.0),
    ("sonido",     21, 0.825, "PROXY_vinilo",  "PROXY_vinilo",      70.0, 1.95, 3.2),
    ("hornacinas", 41, 0.885, "AIM_retablo",   "PROXY_hornacina_c", 34.0, 0.10, 3.5),
    ("reliquia",   61, 0.970, "PROXY_micro",   "PROXY_micro",       65.0, 0.15, 2.8),
    ("retirada",   81, 0.325, "PROXY_placa",   "PROXY_placa",       26.0, 1.30, 5.6),
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

    # Hornacinas: en greybox son marcos salientes. El boolean real entra en fase 2.
    for x, sufijo in zip(HORNACINA_X, ("i", "c", "d")):
        _caja(col, "HORNACINA_marco_" + sufijo,
              (x, RETABLO_Y - 0.25, HORNACINA_Z),
              (HORNACINA_ANCHO + 0.14, 0.1, HORNACINA_ALTO + 0.14))
        _caja(col, "PROXY_hornacina_" + sufijo,
              (x, RETABLO_Y - 0.32, HORNACINA_Z),
              (HORNACINA_ANCHO, 0.05, HORNACINA_ALTO))

    # Cruz de neón
    _caja(col, "CRUZ_vertical",
          (0, RETABLO_Y - 0.3, CRUZ_Z), (0.12, 0.08, 1.6))
    _caja(col, "CRUZ_horizontal",
          (0, RETABLO_Y - 0.3, CRUZ_Z + 0.35), (0.9, 0.08, 0.12))


def _reliquias(col):
    mesa_z = ALTAR_ALTO + 0.08

    for i in range(VELADORAS):
        x = -1.05 + i * (1.6 / (VELADORAS - 1))
        _cilindro(col, "VELADORA_%d" % i,
                  (x, ALTAR_Y - 0.32, mesa_z + 0.11), 0.055, 0.22, 16)

    # Vinilos acostados sobre la mesa del altar: la estación del sonido
    # los mira en picado, no de frente.
    _cilindro(col, "PROXY_vinilo", (1.05, ALTAR_Y + 0.05, mesa_z + 0.012),
              0.175, 0.024, 32)
    disco = _cilindro(col, "VINILO_ladeado", (1.58, ALTAR_Y - 0.22, mesa_z + 0.012),
                      0.175, 0.022, 32)
    disco.rotation_euler = (0, 0, 0.4)
    pila = _cilindro(col, "VINILO_pila", (0.62, ALTAR_Y + 0.3, mesa_z + 0.05),
                     0.168, 0.09, 32)
    pila.rotation_euler = (0.03, 0.02, 0)

    micro = _cilindro(col, "PROXY_micro",
                      (-0.95, ALTAR_Y + 0.08, mesa_z + 0.09), 0.048, 0.18, 20)
    micro.rotation_euler = (0.42, 0, 0.3)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.062, segments=16, ring_count=10,
        location=(-0.95, ALTAR_Y + 0.02, mesa_z + 0.2))
    rejilla = bpy.context.object
    rejilla.name = "MICRO_rejilla"
    _reubicar(col, rejilla)

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
