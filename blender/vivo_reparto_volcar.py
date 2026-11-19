"""Dumps the cast pose the owner placed (MTO-yappingdrone tmp/yap/colocar-reparto-v3.blend) for the live export: per v5 rig its world
matrix and every pose bone's evaluated matrix (armature space, constraints solved), plus Héctor's bottle trees, the Tripo console and
the truck's world matrix. Read only: nothing is saved to the .blend (autosave off).

  GPU=0 ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b "<colocar-reparto-v3.blend (Windows)>" \
    --python-expr "import bpy; bpy.context.preferences.filepaths.use_auto_save_temporary_files=False" \
    --python-exit-code 1 --python "$(wslpath -w blender/vivo_reparto_volcar.py)" -- <out .json (Windows)>

vivo_secciones_exportar.py reads it with VIVO_POSE=<json> (poner_pose()). All matrices are 4x4 row lists, Blender axes.
"""
import bpy, json, sys

out = sys.argv[sys.argv.index("--") + 1]
O = bpy.data.objects
sc = bpy.context.scene
sc.frame_set(sc.frame_current)
bpy.context.view_layer.update()


def m(x):
    return [[round(float(v), 6) for v in fila] for fila in x]


d = {"archivo": bpy.data.filepath, "frame": sc.frame_current, "camion": m(O["camion"].matrix_world), "rigs": {}, "objetos": {}}
for q in ("manager", "hector", "alejandro", "diego"):
    r = O[q + "_v5_rig"]
    d["rigs"][q] = {"mundo": m(r.matrix_world), "padre": r.parent.name if r.parent else None,
                    "huesos": {b.name: m(b.matrix) for b in r.pose.bones},
                    "cabeza": [round(v, 4) for v in r.matrix_world @ next(b for b in r.pose.bones if "HeadTop" in b.name).head]}
    print("VOLCAR", q, "cabeza", d["rigs"][q]["cabeza"], "padre", d["rigs"][q]["padre"], flush=True)
# Héctor's bottle trees (the rendered copy and its siblings), the console, the members' skins: world matrix + render visibility
for o in O:
    base = o.name.split(".")[0]
    if base.startswith(("k5_bebida", "tripo_consola", "tripo_asiento", "hector_botella")) or base.endswith("_v5"):
        d["objetos"][o.name] = {"mundo": m(o.matrix_world), "oculto": o.hide_render, "visible": o.visible_get(),
                                "padre": o.parent.name if o.parent else None, "tipo": o.type}
json.dump(d, open(out, "w", encoding="utf8"), indent=0)
print("VOLCAR listo", out, len(d["objetos"]), "objetos", flush=True)
