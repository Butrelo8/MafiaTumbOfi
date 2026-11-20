"""Round trip numbers: a cast GLB imported into Blender against the owner's pose dump (blender/props/reparto_pose_dueno.json).
Per rig: world distance of every pose bone head to the owner's (his world matrix x his bone matrix), with the scene at each frame in
FRAMES. DZ lowers the owner's side (the G63 cast shift is -0.28). Read only.

  ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b --python-exit-code 1 --python "$(wslpath -w scripts/g63/comparar_importado.py)" -- \
    <glb (Windows)> <dueno.json (Windows)> <DZ> [IMPORT_OPTS json] [out.json (Windows)]
IMPORT_OPTS: extra keyword arguments for bpy.ops.import_scene.gltf, e.g. '{"bone_heuristic":"TEMPERANCE"}'.
"""
import json
import sys

import bpy
from mathutils import Matrix, Vector

a = sys.argv[sys.argv.index("--") + 1:]
glb, dueno, dz = a[0], json.load(open(a[1], encoding="utf8")), float(a[2])
opts = json.loads(a[3]) if len(a) > 3 else {}
out = a[4] if len(a) > 4 else None
FRAMES = (0, 1, 2)

antes = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=glb, **opts)
rigs = {o.name.split(".")[0].replace("_v5_rig", ""): o for o in bpy.data.objects if o not in antes and o.type == "ARMATURE"}


def medir(rig, r, f):
    bpy.context.scene.frame_set(f)
    bpy.context.view_layer.update()
    M = Matrix(r["mundo"])
    d = []
    for b in rig.pose.bones:
        B = r["huesos"].get(b.name)
        if B is not None:
            d.append(((rig.matrix_world @ b.head - (M @ Matrix(B).translation + Vector((0, 0, dz)))).length, b.name))
    d.sort(reverse=True)
    head = next(x[0] for x in d if "HeadTop" in x[1])
    return {"bones": len(d), "max": round(d[0][0], 4), "max_bone": d[0][1], "median": round(d[len(d) // 2][0], 4), "headtop": round(head, 4)}


res = {}
for q, r in dueno["rigs"].items():
    rig = rigs.get(q)
    if rig is None:
        print("ROUND", q, "no armature in the import; found", sorted(rigs), flush=True)
        continue
    ad = rig.animation_data
    # Blender's importer makes one muted NLA track per glTF animation and activates only the first one: the other rigs stay in rest pose
    res[q] = {"importado": {f: medir(rig, r, f) for f in FRAMES}, "accion_activa": ad.action.name if ad and ad.action else None,
              "nla": [(t.name, t.mute) for t in ad.nla_tracks] if ad else []}
    print("ROUND", q, "as imported: active action", res[q]["accion_activa"], "nla", res[q]["nla"], "frame 0", res[q]["importado"][0], flush=True)
    if ad and not ad.action:
        ad.action = next(s.action for t in ad.nla_tracks for s in t.strips)
        res[q]["con_accion"] = {f: medir(rig, r, f) for f in FRAMES}
        print("ROUND", q, "action assigned by hand: frame 0", res[q]["con_accion"][0], "frame 2", res[q]["con_accion"][2], flush=True)
if out:
    json.dump(res, open(out, "w", encoding="utf8"), indent=1)
