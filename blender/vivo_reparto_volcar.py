"""Dumps the cast pose the owner placed (MTO-yappingdrone tmp/yap/colocar-reparto-v3.blend) for the live export: per v5 rig its world
matrix and every pose bone's evaluated matrix (armature space, constraints solved), plus Héctor's bottle trees, the Tripo console and
the truck's world matrix. Read only: nothing is saved to the .blend (autosave off).
Since the hands/props placement file (blender/colocacion_g63_manos.py) it also carries `manos` (per rig and side: the control empty's
world matrix, where the target asks for the wrist and where the evaluated wrist and elbow are) and `props` (the world matrix of every
roof load object k3_*, with its handle techo_*): g63_rack.py reads `props` (VIVO_PROPS), the exporter's poner_pose already takes every
evaluated bone of `rigs[..].huesos`, arms and hands included.

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
# hands: the IK controls (mano_<izq|der>_<nombre>), if the file has them, against the evaluated wrist and elbow
d["manos"] = {}
for q in ("manager", "hector", "alejandro", "diego"):
    r, d["manos"][q] = O[q + "_v5_rig"], {}
    for lado, hueso in (("izq", "Left"), ("der", "Right")):
        mano, brazo = r.pose.bones[f"mixamorig:{hueso}Hand"], r.pose.bones[f"mixamorig:{hueso}ForeArm"]
        c, codo = O.get(f"mano_{lado}_{q}"), O.get(f"codo_{lado}_{q}")
        d["manos"][q][lado] = {"control": c.name if c else None, "control_mundo": m(c.matrix_world) if c else None,
                               "codo_control": codo.name if codo else None,
                               "muneca": [round(v, 5) for v in r.matrix_world @ mano.head], "codo": [round(v, 5) for v in r.matrix_world @ brazo.head],
                               "agarre": float(c["agarre"]) if c and "agarre" in c else None}
# the roof load: every k3_* mesh (his rack) and, in the hands file, the handle that moves it
d["props"] = {}
for o in O:
    if o.type == "MESH" and o.name.split(".")[0].startswith("k3_"):
        asa = o.parent if o.parent and o.parent.name.startswith("techo_") else None
        d["props"][o.name.split(".")[0]] = {"objeto": o.name, "mundo": m(o.matrix_world), "asa": asa.name if asa else None,
                                            "asa_mundo": m(asa.matrix_world) if asa else None}
print("VOLCAR props", {k: [round(x["mundo"][i][3], 3) for i in range(3)] for k, x in d["props"].items()}, flush=True)
json.dump(d, open(out, "w", encoding="utf8"), indent=0)
print("VOLCAR listo", out, len(d["objetos"]), "objetos", flush=True)
