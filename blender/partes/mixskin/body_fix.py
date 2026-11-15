# body_fix.py: the body-contact correction layer on a Mixamo clip blend (armature "mx", mesh "Body").
# The clip's action goes to an NLA track ("clip"); a correction action ("fix") sits on top as the active action with
# blend COMBINE, keyed on every frame of the clip on mixamorig:LeftArm / RightArm rotation_quaternion only (so the
# timing and every other bone stay the clip's). Per frame and side, the hand and forearm vertices inside the body
# (penlib.inside, depth and normal of the outer skin: penlib.outer) give constraints  w . ((p - shoulder) x n) >= depth + margin  on a small world rotation w about the
# shoulder; one push per hand along the mean outer normal, by the largest exit distance (penlib.arm_push), w is carried to the bone's local frame, max-filtered over +-4 frames (so smoothing
# never shaves a peak) and Gaussian-smoothed (sigma 2). Repeated until no vertex is inside (only the frames the layer
# touches are re-measured). The old prop_* stand-ins are deleted: the props are refitted after this (props_fit.py).
#   $B -b <clip blend> --python body_fix.py -- <out.blend (Windows)> <report.json (Windows)> [iters 4] [margin mm 1.5]
import bpy, sys, os, json, math
sys.path.append(os.path.dirname(__file__))
import numpy as np
from mathutils import Vector, Quaternion, Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras import anim_utils
from penlib import TRUNK, dominant, body_world, inside_outer, arm_push
a = sys.argv[sys.argv.index("--") + 1:]
out, rep = a[0], a[1]; iters = int(a[2]) if len(a) > 2 else 4; margin = (float(a[3]) if len(a) > 3 else 1.5) / 1000
sc = bpy.context.scene; mx = bpy.data.objects["mx"]; body = bpy.data.objects["Body"]
for o in [o for o in sc.objects if o.name.startswith("prop_")]: bpy.data.objects.remove(o)
ad = mx.animation_data; clip = ad.action; f0, f1 = map(int, clip.frame_range); sc.frame_start, sc.frame_end = f0, f1
frames = list(range(f0, f1 + 1)); n = len(frames)
cslot = ad.action_slot
tr = ad.nla_tracks.new(); tr.name = "clip"; st = tr.strips.new("clip", f0, clip)
if cslot is not None and hasattr(st, "action_slot"): st.action_slot = cslot
ad.action = None
fix = bpy.data.actions.new("fix"); slot = fix.slots.new("OBJECT", "mx"); ad.action = fix; ad.action_slot = slot
ad.action_blend_type = "COMBINE"; ad.action_influence = 1.0
cb = anim_utils.action_ensure_channelbag_for_slot(fix, slot)
SIDES = ("Left", "Right"); FC = {}
for S in SIDES:
    bn = f"mixamorig:{S}Arm"; mx.pose.bones[bn].rotation_mode = "QUATERNION"
    FC[S] = [cb.fcurves.new(f'pose.bones["{bn}"].rotation_quaternion', index=i, group_name=bn) for i in range(4)]
Q = {S: np.tile([1.0, 0, 0, 0], (n, 1)) for S in SIDES}
def write(S):
    for i, fc in enumerate(FC[S]):
        fc.keyframe_points.clear(); fc.keyframe_points.add(n)
        fc.keyframe_points.foreach_set("co", np.column_stack([frames, Q[S][:, i]]).ravel().tolist())
        fc.keyframe_points.foreach_set("interpolation", [1] * n)   # LINEAR
        fc.update()
for S in SIDES: write(S)
PB = mx.pose.bones
def armrot(S):
    M = (mx.matrix_world @ PB[f"mixamorig:{S}Arm"].matrix).to_3x3(); M.normalize(); return M
# self-check: which side of the basis COMBINE puts the strip's quaternion on (local post-multiply is expected)
fc_ = frames[n // 2]; sc.frame_set(fc_); S = "Left"
s0 = mx.matrix_world @ PB["mixamorig:LeftArm"].head; t0 = mx.matrix_world @ PB["mixamorig:LeftHand"].tail
w = Vector((0.0, 0.0, 0.05)); R = armrot(S); vl = R.transposed() @ w
Q[S][n // 2] = Quaternion(vl.normalized(), vl.length)[:]; write(S); sc.frame_set(fc_)
t1 = mx.matrix_world @ PB["mixamorig:LeftHand"].tail; pred = w.cross(t0 - s0)
selfcheck = dict(moved_mm=round((t1 - t0).length * 1000, 2), predicted_mm=round(pred.length * 1000, 2), err_mm=round(((t1 - t0) - pred).length * 1000, 3))
print("@@SELFCHECK@@", selfcheck, flush=True)
assert selfcheck["err_mm"] < 0.1 * selfcheck["predicted_mm"], "COMBINE does not post-multiply the local rotation"
Q[S][n // 2] = (1, 0, 0, 0); write(S)
dom = dominant(body); istrunk = np.isin(dom, list(TRUNK))
tpolys = [list(p.vertices) for p in body.data.polygons if all(istrunk[i] for i in p.vertices)]
SET = {S: np.flatnonzero(np.char.startswith(dom, S + "Hand") | (dom == S + "ForeArm")) for S in SIDES}
def smooth(V):
    mag = np.linalg.norm(V, axis=1); W = np.zeros_like(V)
    for k in range(n):
        lo, hi = max(0, k - 4), min(n, k + 5); W[k] = V[lo + int(mag[lo:hi].argmax())]
    g = np.exp(-0.5 * (np.arange(-6, 7) / 2.0) ** 2); g /= g.sum()
    return np.column_stack([np.convolve(np.pad(W[:, i], 6, mode="edge"), g, mode="valid") for i in range(3)])
log = []; todo = set(range(n))
for it in range(iters):
    inc = {S: np.zeros((n, 3)) for S in SIDES}; worst = {S: (0.0, None) for S in SIDES}; hit = set(); minacross = {S: 1.0 for S in SIDES}
    for k in sorted(todo):
        sc.frame_set(frames[k]); dg = bpy.context.evaluated_depsgraph_get(); P = body_world(body, dg)
        tree = BVHTree.FromPolygons(P.tolist(), tpolys, all_triangles=False)
        for S in SIDES:
            _, d, N = inside_outer(tree, P[SET[S]]); sel = d > 0
            if not sel.any(): continue
            hit.add(k)
            if d.max() > worst[S][0]: worst[S] = (float(d.max()), frames[k])
            s = np.array(mx.matrix_world @ PB[f"mixamorig:{S}Arm"].head)
            tail = np.array(mx.matrix_world @ PB[f"mixamorig:{S}Hand"].tail)
            wv, push, across = arm_push(tree, P[SET[S]][sel], N[sel], s, tail, margin); minacross[S] = min(minacross[S], across)
            inc[S][k] = np.array(armrot(S).transposed() @ Vector(wv))
    log.append({"iter": it, "frames_measured": len(todo), "frames_inside": len(hit),
                "worst_mm": {S: [round(worst[S][0] * 1000, 2), worst[S][1]] for S in SIDES},
                "min_push_across_arm": {S: round(minacross[S], 2) for S in SIDES}})
    print("@@ITER@@", log[-1], flush=True)
    if not hit: break
    for S in SIDES:
        V = smooth(inc[S])
        for k in range(n):
            if np.linalg.norm(V[k]) < 1e-9: continue
            q = Quaternion(Q[S][k]) @ Quaternion(Vector(V[k]).normalized(), float(np.linalg.norm(V[k]))); Q[S][k] = q[:]
        write(S)
    todo = {k for k in range(n) for S in SIDES if abs(Q[S][k][0]) < 1 - 1e-12}
ang = {S: round(float(np.degrees(2 * np.arccos(np.clip(np.abs(Q[S][:, 0]), 0, 1))).max()), 2) for S in SIDES}
json.dump(dict(selfcheck=selfcheck, iters=log, max_angle_deg=ang, margin_mm=margin * 1000,
               keyed_frames=[f0, f1]), open(rep, "w"), indent=1)
sc.frame_set(f0); bpy.ops.wm.save_as_mainfile(filepath=out)
print("@@BODYFIX@@", json.dumps(dict(max_angle_deg=ang, last=log[-1])), flush=True)
