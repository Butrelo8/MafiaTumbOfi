# sip_bake.py: the owner's hand pose from a place_ik.py placement blend, baked into body_fix.py's correction layer (the
# active "fix" action, COMBINE: final local = clip @ fix) as the sip key. At the key frame it reads the evaluated local
# rotation of <Side>Arm, ForeArm, Hand and the mitten chain HandIndex1-3 (IK, Copy Rotation and his finger keys included),
# drops the controls, and multiplies each bone's fix keys by slerp(identity, delta, w), where delta takes the frame's
# current pose to his and w eases 0 -> 1 -> 0 (smoothstep) over the window. The bottle and his prop transform stay.
# Self-check: the hand and the prop at the key frame against his pose (mm). Report: the delta angles, the elbow angle
# range and the largest frame-to-frame jump of the hand head, inside the window and in the clip before the bake.
#   $B -b <placed blend> --python sip_bake.py -- <Side> <frame> <in0-in1> <out0-out1> <out.blend (Windows)> <report.json (Windows)>
import bpy, sys, json, math
import numpy as np
from mathutils import Quaternion
a = sys.argv[sys.argv.index("--") + 1:]; S, F = a[0], int(a[1]); i0, i1 = map(int, a[2].split("-")); o0, o1 = map(int, a[3].split("-"))
out, rep = a[4], a[5]
sc = bpy.context.scene; mx = bpy.data.objects["mx"]; PB = mx.pose.bones; W = mx.matrix_world; ad = mx.animation_data
NAMES = [f"mixamorig:{S}{b}" for b in ("Arm", "ForeArm", "Hand", "HandIndex1", "HandIndex2", "HandIndex3")]
props = [o for o in sc.objects if o.name.startswith("prop_") and o.parent and o.parent.name.endswith("_hand")]
sc.frame_set(F); bpy.context.view_layer.update()
T = {n: mx.convert_space(pose_bone=PB[n], matrix=PB[n].matrix, from_space="POSE", to_space="LOCAL").to_quaternion() for n in NAMES}
goal = {"hand": (W @ PB[NAMES[2]].matrix).copy(), **{o.name: o.matrix_world.copy() for o in props}}
for n in NAMES:
    for c in list(PB[n].constraints): PB[n].constraints.remove(c)
for nm in ("MANO_ctrl", "CODO_ctrl"):
    if nm in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[nm])
cb = ad.action.layers[0].strips[0].channelbags[0]
# his finger keys (if any) sit in the fix action as single keys: drop them, the eased delta replaces them
for n in NAMES[3:]:
    for f_ in [f_ for f_ in cb.fcurves if f_.data_path == f'pose.bones["{n}"].rotation_quaternion']: cb.fcurves.remove(f_)
def hand_track(names_frames):
    H, E = [], []
    for f in names_frames:
        sc.frame_set(f); s_, e_, w_ = (np.array(W @ PB[f"mixamorig:{S}{b}"].head) for b in ("Arm", "ForeArm", "Hand"))
        H.append(w_); u, v = e_ - s_, w_ - e_; E.append(math.degrees(math.acos(np.clip(u.dot(v) / np.linalg.norm(u) / np.linalg.norm(v), -1, 1))))
    return np.array(H), np.array(E)
win = list(range(i0 - 5, o1 + 6))
H0, E0 = hand_track(win)
sc.frame_set(F); bpy.context.view_layer.update()
D = {n: PB[n].rotation_quaternion.inverted() @ T[n] for n in NAMES}  # current (clip @ fix) -> his
frames = sorted({int(k.co[0]) for f_ in cb.fcurves for k in f_.keyframe_points}); n = len(frames)
def ss(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
wt = [ss((f - i0) / (i1 - i0)) * (1 - ss((f - o0) / (o1 - o0))) for f in frames]
for nm in NAMES:
    dp = f'pose.bones["{nm}"].rotation_quaternion'; PB[nm].rotation_mode = "QUATERNION"
    fl = sorted([f_ for f_ in cb.fcurves if f_.data_path == dp], key=lambda f_: f_.array_index)
    if not fl:
        fl = [cb.fcurves.new(dp, index=i, group_name=nm) for i in range(4)]
        for i, f_ in enumerate(fl):
            f_.keyframe_points.add(n); f_.keyframe_points.foreach_set("co", np.column_stack([frames, np.full(n, 1.0 if i == 0 else 0.0)]).ravel().tolist())
            f_.keyframe_points.foreach_set("interpolation", [1] * n)
    Q = [Quaternion([f_.evaluate(f) for f_ in fl]) for f in frames]
    new = [(q @ Quaternion().slerp(D[nm], w)).normalized() for q, w in zip(Q, wt)]
    for i, f_ in enumerate(fl):
        f_.keyframe_points.foreach_set("co", np.column_stack([frames, [q[i] for q in new]]).ravel().tolist()); f_.update()
sc.frame_set(F); bpy.context.view_layer.update()
err = {"hand_mm": round(((W @ PB[NAMES[2]].matrix).translation - goal["hand"].translation).length * 1000, 2),
       **{o.name + "_mm": round((o.matrix_world.translation - goal[o.name].translation).length * 1000, 2) for o in props}}
H1, E1 = hand_track(win)
jump = lambda H: round(float(np.linalg.norm(np.diff(H, axis=0), axis=1).max()) * 1000, 1)
R = dict(frame=F, ease_in=[i0, i1], ease_out=[o0, o1], delta_deg={nm.split(":")[1]: round(math.degrees(D[nm].angle), 1) for nm in NAMES},
         selfcheck=err, window=[win[0], win[-1]], elbow_deg_before=[round(E0.min(), 1), round(E0.max(), 1)], elbow_deg_after=[round(E1.min(), 1), round(E1.max(), 1)],
         hand_jump_mm_per_frame_before=jump(H0), hand_jump_mm_per_frame_after=jump(H1), hand_moved_mm_at_key=round(float(np.linalg.norm(H1[win.index(F)] - H0[win.index(F)])) * 1000, 1))
json.dump(R, open(rep, "w"), indent=1)
sc.frame_set(F); bpy.ops.wm.save_as_mainfile(filepath=out)
print("@@SIPBAKE@@", json.dumps(R), flush=True)
