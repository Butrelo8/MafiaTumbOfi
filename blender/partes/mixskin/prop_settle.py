# prop_settle.py: per-frame small corrections of an in-hand prop's keys (prop_rest.py), after the owner's placement:
#   clearance: where prop vertices are inside the body (penlib.inside_outer, outer depth), slide the prop along its own
#     axis away from the hit (-z for hits on the upper half, the lip end; +z otherwise) by the depth + 1.5 mm;
#   grip: where the hand's closest gap to the prop is outside 0.5-2.5 mm, move the prop toward / away from the closest
#     hand vertex to 1.5 mm.
# Offsets are world vectors turned into the parent's space, max-filtered (+-4 frames) and Gaussian-smoothed (sigma 2),
# added to the prop's location keys, and iterated.
#   $B -b <blend> --python prop_settle.py -- <prop> <hand set, e.g. RightHand> <out.blend (Windows)> <report.json (Windows)> [iters 3]
import bpy, sys, os, json
sys.path.append(os.path.dirname(__file__))
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from penlib import dominant, body_world, prop_world, inside_outer, near_box
a = sys.argv[sys.argv.index("--") + 1:]; p = bpy.data.objects[a[0]]; HS = a[1]; out, rep = a[2], a[3]; iters = int(a[4]) if len(a) > 4 else 3
sc = bpy.context.scene; body = bpy.data.objects["Body"]; me = body.data; mx = bpy.data.objects["mx"]
dom = dominant(body); hidx = np.flatnonzero(np.char.startswith(dom, HS)); polys = [list(q.vertices) for q in me.polygons]
fc = {i: next(f for f in p.animation_data.action.layers[0].strips[0].channelbags[0].fcurves if f.data_path == "location" and f.array_index == i) for i in range(3)}
frames = [int(k.co[0]) for k in fc[0].keyframe_points]; n = len(frames)
zt = max(v[2] for v in p.bound_box)
def smooth(V, mx_filter):
    if mx_filter:  # keep each push for +-4 frames (by magnitude) before smoothing, so the peak survives
        m = np.linalg.norm(V, axis=1); W_ = V.copy()
        for k in range(n):
            j = max(range(max(0, k - 4), min(n, k + 5)), key=lambda j: m[j]); W_[k] = V[j]
        V = W_
    g = np.exp(-0.5 * (np.arange(-6, 7) / 2.0) ** 2); g /= g.sum()
    return np.column_stack([np.convolve(np.pad(V[:, i], 6, mode="edge"), g, mode="valid") for i in range(3)])
log = []
for it in range(iters + 1):
    C, G = np.zeros((n, 3)), np.zeros((n, 3)); dep, gap = np.zeros(n), np.zeros(n)
    for k, f in enumerate(frames):
        sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); P = body_world(body, dg)
        full = BVHTree.FromPolygons(P.tolist(), polys, all_triangles=False); V, F = prop_world(p, dg); tr = BVHTree.FromPolygons(V.tolist(), F)
        Mw = p.matrix_world; Pinv = p.parent.matrix_world.to_3x3().inverted()
        d, D, _ = inside_outer(full, V); dep[k] = D.max() if len(D) else 0
        if dep[k] > 0:
            loc = np.array([(Mw.inverted() @ Vector(v))[2] for v in V[D > 0]]); up = loc.mean() > zt / 2
            ax = np.array((Mw.to_3x3() @ Vector((0, 0, -1 if up else 1))).normalized()); C[k] = np.array(Pinv @ Vector(ax * (dep[k] + 1.5e-3)))
        H = P[hidx[near_box(P[hidx], V, 0.1)]]
        best = min(((tr.find_nearest(Vector(h), 0.1), h) for h in H), key=lambda t: t[0][3] if t[0][3] is not None else 1) if len(H) else None
        if best and best[0][3] is not None:
            (q, nrm, _, dist), h = best; s = (Vector(h) - q).dot(nrm); gap[k] = s
            if not 0.5e-3 <= s <= 2.5e-3: G[k] = np.array(Pinv @ Vector(np.array(nrm) * (s - 1.5e-3)))
    log.append(dict(iter=it, inside_max_mm=round(float(dep.max()) * 1000, 2), frames_inside=int((dep > 0).sum()),
                    grip_mm=[round(float(gap.min()) * 1000, 2), round(float(gap.max()) * 1000, 2)], grip_over_3=int((gap > 3e-3).sum())))
    print("@@ITER@@", log[-1], flush=True)
    if it == iters or (log[-1]["frames_inside"] == 0 and ((gap >= 0.5e-3) & (gap <= 2.5e-3)).all()): break
    O = smooth(C, True) + smooth(G, False)
    for i in range(3):
        kp = fc[i].keyframe_points
        for k in range(n): kp[k].co[1] += float(O[k, i])
        fc[i].update()
json.dump(dict(iters=log), open(rep, "w"), indent=1)
sc.frame_set(305); bpy.ops.wm.save_as_mainfile(filepath=out)
print("@@SETTLE@@", json.dumps(log[-1]), flush=True)
