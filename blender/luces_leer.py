"""Reads which lamps the owner turned off in his .blend (docs/luces-dueno.md) into blender/props/luces.json, which the live
exporter honours (vivo_secciones_exportar.py hides every lamp listed in "fuera"). A lamp is off when its luz_* object is gone
(deleted), hidden (eye), disabled in viewports (monitor) or in renders (camera). Same pattern as vivo_reparto_volcar.py: read only.

  GPU=0 ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b "<his .blend (Windows)>" \
    --python-exit-code 1 --python "$(wslpath -w blender/luces_leer.py)"
"""
import bpy, json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from luces_g63 import LUCES

RUTA = os.path.join(AQUI, "props", "luces.json")
capa = bpy.context.view_layer.objects
vistas = {o.name.split(".")[0] for o in bpy.data.objects
          if o.name.startswith("luz_") and o.name in capa and not (o.hide_render or o.hide_viewport or o.hide_get())}
fuera = [n for n in LUCES if n not in vistas]
d = {"archivo": bpy.data.filepath, "fuera": fuera, "todas": list(LUCES)}
json.dump(d, open(RUTA, "w", encoding="utf8"), indent=1)
print("LUCES fuera", len(fuera), fuera, "->", RUTA, flush=True)
