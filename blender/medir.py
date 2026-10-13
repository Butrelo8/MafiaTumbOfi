"""Medir en la escena en vez de mirar renders: dónde cae un objeto en el cuadro,
si la cámara lo ve y si dos objetos se cruzan.

Sirve con cualquiera de las dos escenas (altar.py o transicion.py), en el visor
(MCP) o en segundo plano:

    m = {}
    exec(open(r"E:\\Cursor Projects\\MTO\\blender\\medir.py").read(), m)
    m["en_cuadro"]("ALTAR_mesa", frame=1)       # caja en píxeles y cuánto queda dentro
    m["visible"]("ALTAR_mesa", frame=1)         # rayos desde la cámara: quién lo tapa
    m["solapan"]("BANCA_der_0", "BANCA_der_1")   # caras que se cruzan (BVH), no sólo cajas

Antes se reescribía a mano en cada sesión (147 llamadas en 14 sesiones). Con
cajas y rayos se supo, por ejemplo, que el candelabro sólo cabía en un sitio
(18 combinaciones) y que los prerrollos ocupaban 8 px en el escalón.
"""

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def _escena(frame):
    escena = bpy.context.scene
    if frame is not None:
        escena.frame_set(frame)
    bpy.context.view_layer.update()
    return escena


def _caja(ob):
    return [ob.matrix_world @ Vector(c) for c in ob.bound_box]


def en_cuadro(nombre, frame=None, camara=None):
    """La caja envolvente del objeto proyectada a la cámara, en píxeles del render.

    Origen arriba a la izquierda. `dentro` = fracción del rectángulo proyectado
    que cae en el cuadro; `delante` = todas las esquinas delante de la cámara.
    """
    escena = _escena(frame)
    cam = bpy.data.objects[camara] if camara else escena.camera
    ob = bpy.data.objects[nombre]
    pct = escena.render.resolution_percentage / 100
    ancho, alto = escena.render.resolution_x * pct, escena.render.resolution_y * pct
    puntos = [world_to_camera_view(escena, cam, p) for p in _caja(ob)]
    xs = [p.x * ancho for p in puntos]
    ys = [(1 - p.y) * alto for p in puntos]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    area = max(x1 - x0, 1e-6) * max(y1 - y0, 1e-6)
    cx = max(0.0, min(x1, ancho) - max(x0, 0.0))
    cy = max(0.0, min(y1, alto) - max(y0, 0.0))
    return {"px": [round(v, 1) for v in (x0, y0, x1, y1)],
            "ancho_px": round(x1 - x0, 1), "alto_px": round(y1 - y0, 1),
            "dentro": round(cx * cy / area, 3),
            "delante": all(p.z > 0 for p in puntos),
            "cuadro": [int(ancho), int(alto)]}


def visible(nombre, frame=None, camara=None):
    """Rayos desde la cámara al centro y a las 8 esquinas de la caja del objeto.

    Devuelve cuántos llegan al objeto (o a uno de sus hijos) y quién tapa el resto.
    Las esquinas de la caja pueden caer fuera de la malla: un rayo que no choca con
    nada cuenta como "al aire", no como tapado.
    """
    escena = _escena(frame)
    cam = bpy.data.objects[camara] if camara else escena.camera
    ob = bpy.data.objects[nombre]
    propios = {ob.name} | {h.name for h in ob.children_recursive}
    grafo = bpy.context.evaluated_depsgraph_get()
    origen = cam.matrix_world.translation
    caja = _caja(ob)
    puntos = [sum(caja, Vector()) / 8.0] + caja
    llegan, al_aire, tapan = 0, 0, {}
    for p in puntos:
        rayo = p - origen
        choca, _loc, _n, _i, otro, _m = escena.ray_cast(grafo, origen, rayo.normalized(), distance=rayo.length + 1e-3)
        if not choca:
            al_aire += 1
        elif otro.name in propios:
            llegan += 1
        else:
            tapan[otro.name] = tapan.get(otro.name, 0) + 1
    return {"llegan": llegan, "al_aire": al_aire, "rayos": len(puntos), "tapan": tapan}


def _arbol(ob, grafo):
    evaluado = ob.evaluated_get(grafo)
    malla = evaluado.to_mesh()
    try:
        vertices = [ob.matrix_world @ v.co for v in malla.vertices]
        caras = [tuple(c.vertices) for c in malla.polygons]
        return BVHTree.FromPolygons(vertices, caras)
    finally:
        evaluado.to_mesh_clear()


def solapan(a, b):
    """¿Se cruzan dos mallas? Cajas en el mundo y, si se tocan, caras con BVH."""
    _escena(None)
    oa, ob = bpy.data.objects[a], bpy.data.objects[b]
    ca, cb = _caja(oa), _caja(ob)
    cajas = all(min(p[i] for p in ca) <= max(p[i] for p in cb) and min(p[i] for p in cb) <= max(p[i] for p in ca)
                for i in range(3))
    if not cajas:
        return {"cajas": False, "caras": 0}
    grafo = bpy.context.evaluated_depsgraph_get()
    return {"cajas": True, "caras": len(_arbol(oa, grafo).overlap(_arbol(ob, grafo)))}
