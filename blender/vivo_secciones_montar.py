"""Live sections spike, step 1 (spec: mothership queue 2026-11-18-mto-live-sections-spike.md): montaje.py's whole chain with the
road3 world and the screen truck, as the montaje-esc1..6 stills were built, but instead of utileria's render loop it runs each
option's builder once, records its camera (pos, look-at, lens; sensor 36 mm horizontal, as the loop sets it) and the objects it
added, then saves the file for step 2 (blender/vivo_secciones_exportar.py). Edits no other lane's file.

  CABINA_TRIPO=1 MONTAJE_PANTALLA=a MONTAJE_PANTALLA_LUZ=ancha MONTAJE_CAMINO=road3 CURVA_PRUEBA=recta \
  WSLENV=CABINA_TRIPO:MONTAJE_PANTALLA:MONTAJE_PANTALLA_LUZ:MONTAJE_CAMINO:CURVA_PRUEBA \
  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/vivo_secciones_montar.py)" \
    -- "$(wslpath -w blender/escena.py)" <out_dir (Windows)> 1 all 960x540

Writes <out_dir>/vivo-montado.blend and <out_dir>/vivo-montado.json (cameras, per-option objects, object inventory).
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
_MONTAJE = os.path.join(AQUI, "montaje.py")
_src = open(_MONTAJE, encoding="utf8").read()
_LAZO = "# ---------------------------------------------------------------- utileria.py's render loop, over the options above"
assert _src.count(_LAZO) == 1, "montaje.py's render-loop marker moved"

_COLA = '''
import json
_VS = {"camaras": {}, "grupos": {}, "objetos": {}}
for _n, _ in ESCENAS:
    GRUPO.clear()
    sc.frame_set(0)
    _p, _m, _l = OPC[_n]()
    _VS["camaras"][_n] = {"pos": [float(x) for x in _p], "mira": [float(x) for x in _m], "lens": float(_l)}
    _VS["grupos"][_n] = [o.name for o in GRUPO]
    for o in GRUPO:
        o.hide_render = True
    for o in FIGURAS:
        o.hide_render = False
    print("VIVO opcion", _n, _VS["camaras"][_n], len(GRUPO), "objetos", flush=True)
sc.frame_set(0)
_dg = bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    d = {"tipo": o.type, "padre": o.parent.name if o.parent else None, "oculto": o.hide_render,
         "cols": [c.name for c in o.users_collection]}
    if o.type == "MESH":
        ys = [(o.matrix_world @ Vector(c)).y for c in o.bound_box]
        d["y"] = [min(ys), max(ys)]
        d["tris"] = sum(len(p.vertices) - 2 for p in o.data.polygons)
        d["mats"] = [m.name for m in o.data.materials if m]
    elif o.type == "LIGHT":
        d["luz"] = [o.data.type, float(o.data.energy), list(o.matrix_world.translation)]
    _VS["objetos"][o.name] = d
_out = os.path.join(OUT, "vivo-montado")
json.dump(_VS, open(_out + ".json", "w", encoding="utf8"), indent=0)
bpy.ops.wm.save_as_mainfile(filepath=_out + ".blend", copy=True)
print("VIVO guardado", _out, flush=True)
'''
exec(compile(_src.split(_LAZO)[0] + _COLA, _MONTAJE, "exec"), globals())
