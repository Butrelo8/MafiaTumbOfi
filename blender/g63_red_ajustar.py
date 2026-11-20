"""Lays the cargo net and the alien's straps again over the roof load as it stands in a .blend (rack bars and k3_* objects in place): for a
scratch copy where a handle `techo_*` was moved, and for the owner's placement file after he places. The pipeline does the same inside
blender/g63_rack.py (its 3rd argument, the dump). The net (over every k3_* but the alien) and the straps (over the alien) are regenerated with
g63_carga.tender, from the bars and the world boxes of the k3_* objects; the old `carga_red` and `carga_red_alien` are replaced and keep their flags.

  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b <file.blend> --python-exit-code 1 --python blender/g63_red_ajustar.py \
    -- <out .blend (Windows)>
"""
import bpy, os, sys

SAL = sys.argv[sys.argv.index("--") + 1]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g63_carga as G

O = bpy.data.objects
bpy.context.view_layer.update()
k3 = {o.name.split(".")[0]: o for o in O if o.type == "MESH" and o.name.split(".")[0].startswith("k3_")}
alien = k3.pop("k3_alien")
cajas = {k: G.caja_vert(o) for k, o in k3.items()}
viejos = [O.get(n) for n in ("carga_red", "carga_red_alien")]
flags = [(v.hide_select, v.hide_render, v.hide_viewport) if v else (True, False, False) for v in viejos]
red, correas = G.tender(cajas, alien, G.geom_rack(), O["camion"])
for o, f in zip((red, correas), flags):
    o.hide_select, o.hide_render, o.hide_viewport = f
G.medir(k3, alien, red, correas, [O[f"rack_barra{k}"] for k in range(3)], "ajustada")
bpy.ops.wm.save_as_mainfile(filepath=SAL, copy=True)
print("RED guardado", SAL, flush=True)
