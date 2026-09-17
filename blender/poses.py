"""Detectar qué props se movieron a mano, sin depender de la memoria.

El flujo, cuando alguien coloca cosas en el visor y hay que congelarlas:

    exec(open(r"E:\\Cursor Projects\\MTO\\blender\\poses.py").read(), p)
    p["volcar"](r"E:\\Cursor Projects\\MTO\\tmp\\poses-visor.json")   # ANTES de reconstruir
    # ...build() + aplicar()...
    p["comparar"](r"E:\\Cursor Projects\\MTO\\tmp\\poses-visor.json")

`comparar()` devuelve sólo los objetos cuya pose difiere de la que produce el
script. El volcado tiene que hacerse antes de `build()`: reconstruir borra la
escena y con ella lo que se movió a mano.

La pose se mide por el centro de la caja envolvente, no por `location`: el
origen de una malla importada no cae siempre en el mismo sitio.
"""

import json

import bpy
from mathutils import Vector

TOLERANCIA = 1e-4


def _pose(ob):
    caja = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    centro = sum(caja, Vector()) / 8.0
    euler = (ob.rotation_euler if ob.rotation_mode == "XYZ"
             else ob.rotation_quaternion.to_euler("XYZ"))
    return {"centro": [round(v, 5) for v in centro],
            "euler": [round(v, 5) for v in euler],
            "escala": [round(v, 5) for v in ob.scale]}


def volcar(ruta):
    """Guarda la pose de cada malla de la escena."""
    bpy.context.view_layer.update()
    poses = {o.name: _pose(o) for o in bpy.data.objects if o.type == "MESH"}
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(poses, f, indent=1)
    return len(poses)


def comparar(ruta):
    """Devuelve lo que difiere entre el volcado y la escena actual.

    Sirve en los dos sentidos: volcar el visor y reconstruir, o volcar recién
    reconstruido y dejar que alguien mueva cosas. El segundo es más barato,
    porque no hace falta reconstruir para comparar.
    """
    bpy.context.view_layer.update()
    with open(ruta, encoding="utf-8") as f:
        antes = json.load(f)
    ahora = {o.name: _pose(o) for o in bpy.data.objects if o.type == "MESH"}

    movidos = []
    for nombre, pose in antes.items():
        actual = ahora.get(nombre)
        if actual is None:
            continue
        # actual - referencia: positivo = se movió hacia ahí.
        deltas = {campo: [round(b - a, 5) for a, b in zip(pose[campo], actual[campo])]
                  for campo in ("centro", "euler", "escala")}
        if any(abs(v) > TOLERANCIA for d in deltas.values() for v in d):
            movidos.append({"nombre": nombre, "referencia": pose, "actual": actual,
                            "delta": deltas})
    return {"movidos": movidos,
            "solo_en_volcado": sorted(set(antes) - set(ahora)),
            "solo_en_escena": sorted(set(ahora) - set(antes))}
