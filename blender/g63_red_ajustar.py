"""Lays the cargo net again over the roof load as it stands in a .blend (rack bars and k3_* objects in place): for a scratch copy where a
handle `techo_*` was moved, and for the owner's placement file after he places. The pipeline does the same inside blender/g63_rack.py
(its 4th argument, the dump). The net is regenerated with g63_rack's own `red`, from the bars (extent, heights) and the world boxes of the
k3_* objects; the old `carga_red` is replaced and keeps its flags.

  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b <file.blend> --python-exit-code 1 --python blender/g63_red_ajustar.py \
    -- <out .blend (Windows)>
"""
import bpy, os, sys

SAL = sys.argv[sys.argv.index("--") + 1]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = [sys.argv[0], "--", SAL, ""]  # g63_rack reads its arguments at import; none of them is used here
import g63_rack as R

O = bpy.data.objects
bpy.context.view_layer.update()
barras = [R.caja_vert(O[f"rack_barra{k}"]) for k in range(3)]
ys = [(a.y + b.y) / 2 for a, b in barras]
z_barra = (barras[0][0].z + barras[0][1].z) / 2
T = {"x0": barras[0][0].x + 0.05, "x1": barras[0][1].x - 0.05}  # the bars overhang the flat roof by 5 cm (g63_rack.rack)
cajas = {o.name.split(".")[0]: R.caja_vert(o) for o in O if o.type == "MESH" and o.name.split(".")[0].startswith("k3_")}


def cubre(titulo):
    """Net vertices inside each box of the load (> 0: the rope goes through the case, the net no longer sits on the load)."""
    red = O.get("carga_red")
    vs = [red.matrix_world @ v.co for v in red.data.vertices]
    dentro = {k: sum(1 for v in vs if a.x + 0.01 < v.x < b.x - 0.01 and a.y + 0.01 < v.y < b.y - 0.01 and a.z + 0.01 < v.z < b.z - 0.01)
              for k, (a, b) in sorted(cajas.items())}
    print(f"RED {titulo} vértices de la red dentro de cada caja:", dentro, "total", sum(dentro.values()), flush=True)


cubre("antes ")
viejo = O.get("carga_red")
flags = (viejo.hide_select, viejo.hide_render, viejo.hide_viewport) if viejo else (True, False, False)
if viejo:
    malla = viejo.data
    O.remove(viejo, do_unlink=True)
    bpy.data.meshes.remove(malla)
red = R.red(cajas, T, ys, z_barra, "red")
red.hide_select, red.hide_render, red.hide_viewport = flags
cubre("despues")
print("RED ajustada: cajas", {k: [round(v, 3) for v in (a + b) / 2] for k, (a, b) in cajas.items()}, "tris", sum(len(p.vertices) - 2 for p in red.data.polygons), flush=True)
bpy.ops.wm.save_as_mainfile(filepath=SAL, copy=True)
print("RED guardado", SAL, flush=True)
