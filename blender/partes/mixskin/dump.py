# dump.py: per-frame world data of a (fixed) clip blend for props_fit.py, as one .npz:
# hand / forearm / upper-arm vertices per side, every 3rd trunk vertex (+ its dominant bone), the mouth vertex and its
# normal, and the world matrices of the bones the props can ride on.
#   $B -b <blend> --python dump.py -- <out.npz (Windows)> <mouth vertex>
import bpy, sys, os
sys.path.append(os.path.dirname(__file__))
import numpy as np
from penlib import TRUNK, dominant
a = sys.argv[sys.argv.index("--") + 1:]; out, mv = a[0], int(a[1])
sc = bpy.context.scene; mx = bpy.data.objects["mx"]; body = bpy.data.objects["Body"]
f0, f1 = map(int, mx.animation_data.action.frame_range); frames = np.arange(f0, f1 + 1)
dom = dominant(body); istrunk = np.isin(dom, list(TRUNK))
IDX = {"trunk": np.flatnonzero(istrunk)[::3]}
for S in ("Left", "Right"):
    IDX[S + "Hand"] = np.flatnonzero(np.char.startswith(dom, S + "Hand"))
    IDX[S + "ForeArm"] = np.flatnonzero(dom == S + "ForeArm"); IDX[S + "Arm"] = np.flatnonzero(dom == S + "Arm")
BONES = ["Hips", "Spine", "Spine1", "Spine2", "Neck", "Head", "LeftHand", "RightHand", "LeftArm", "RightArm"]
D = {k: [] for k in IDX}; Mb = {b: [] for b in BONES}; mouth, mouth_n = [], []
W3 = np.array(body.matrix_world.to_3x3()); Wt = np.array(body.matrix_world.translation)
for f in frames:
    sc.frame_set(int(f)); dg = bpy.context.evaluated_depsgraph_get(); ev = body.evaluated_get(dg); m = ev.to_mesh()
    P = np.empty(len(m.vertices) * 3, np.float32); m.vertices.foreach_get("co", P); P = P.reshape(-1, 3) @ W3.T + Wt
    mouth.append(P[mv]); mouth_n.append(np.array(m.vertices[mv].normal[:]) @ W3.T); ev.to_mesh_clear()
    for k, idx in IDX.items(): D[k].append(P[idx].astype(np.float32))
    for b in BONES: Mb[b].append(np.array(mx.matrix_world @ mx.pose.bones["mixamorig:" + b].matrix))
np.savez_compressed(out, frames=frames, mouth=np.array(mouth), mouth_n=np.array(mouth_n), trunk_dom=dom[IDX["trunk"]],
                    **{k: np.array(v) for k, v in D.items()}, **{"M_" + b: np.array(v) for b, v in Mb.items()})
print("@@DUMP@@", out, len(frames), {k: len(v) for k, v in IDX.items()}, flush=True)
