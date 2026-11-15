# where_dmm.py: where along the forearm the stretch sits (t = 0 elbow, 1 wrist), top-200 dmm vertices of the forearm
# region at given frames. Says if the forearm's stretch is the elbow bend or the wrist twist.
#   $B -b <blend> --python where_dmm.py -- <frames,...>
import bpy, sys, json
import numpy as np
fr = [int(x) for x in sys.argv[sys.argv.index("--") + 1].split(",")]
sc = bpy.context.scene; rig = bpy.data.objects["rig"]; body = bpy.data.objects["Body"]; me = body.data; nv = len(me.vertices)
rest = np.empty(nv * 3, np.float32); me.vertices.foreach_get("co", rest); rest = rest.reshape(-1, 3)
E = np.empty(len(me.edges) * 2, np.int32); me.edges.foreach_get("vertices", E); E = E.reshape(-1, 2)
L0 = np.linalg.norm(rest[E[:, 0]] - rest[E[:, 1]], axis=1)
names = {g.index: g.name for g in body.vertex_groups}
out = {}
for S in (".L", ".R"):
    a = np.array(rig.data.bones["DEF-forearm" + S].head_local); b = np.array(rig.data.bones["DEF-hand" + S].head_local)
    t = ((rest - a) @ (b - a)) / ((b - a) @ (b - a))
    near = np.linalg.norm(np.cross(rest - a, (b - a) / np.linalg.norm(b - a)), axis=1) < 0.06
    sel = near & (t > -0.3) & (t < 1.3)
    for f in fr:
        sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); ev = body.evaluated_get(dg).to_mesh()
        P = np.empty(nv * 3, np.float32); ev.vertices.foreach_get("co", P); P = P.reshape(-1, 3); body.evaluated_get(dg).to_mesh_clear()
        d = np.abs(np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1) - L0) * 1000
        dm = np.zeros(nv); np.maximum.at(dm, E[:, 0], d); np.maximum.at(dm, E[:, 1], d)
        idx = np.flatnonzero(sel); top = idx[np.argsort(dm[idx])[-200:]]
        out[f"{S}_f{f}"] = dict(max=round(float(dm[idx].max()), 1), t_top_median=round(float(np.median(t[top])), 2),
                                hist_t=np.histogram(t[top], bins=[-0.3, 0, 0.25, 0.5, 0.75, 1.0, 1.3])[0].tolist())
print("@@WHERE@@" + json.dumps(out), flush=True)
