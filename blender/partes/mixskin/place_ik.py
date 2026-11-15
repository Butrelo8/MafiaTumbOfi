# place_ik.py: lets the owner pose a hand in a placement .blend (place_build.py). At the key frame it adds the empty
# MANO_ctrl at the hand (IK on <Side>ForeArm, chain 2, plus Copy Rotation on <Side>Hand) and the pole empty CODO_ctrl
# off the elbow. The pole angle is scanned so the arm does not move until he does (self-check: max bone-head error, mm).
# The mitten's finger chain (<Side>HandIndex1-3) stays selectable in Pose Mode, with rotation only. The armature object and
# every other bone are locked. sip_bake.py later turns his pose into fix-layer keys.
#   $B -b <placement blend> --python place_ik.py -- <Side Right|Left> <frame> <still.png (Windows)>
import bpy, sys, math
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; S, f, still = a[0], int(a[1]), a[2]
sc = bpy.context.scene; mx = bpy.data.objects["mx"]; PB = mx.pose.bones; W = mx.matrix_world
arm, fore, hand = (PB[f"mixamorig:{S}{b}"] for b in ("Arm", "ForeArm", "Hand"))
sc.frame_set(f); bpy.context.view_layer.update()
ref = {p.name: (W @ p.matrix).copy() for p in (arm, fore, hand)}
sh, el, wr = (W @ arm.head), (W @ fore.head), (W @ hand.head)
def empty(name, M, shape, size):
    e = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
    if e.name not in sc.collection.objects: sc.collection.objects.link(e)
    e.empty_display_type = shape; e.empty_display_size = size; e.matrix_world = M; e.show_in_front = True; return e
ctrl = empty("MANO_ctrl", ref[hand.name], "CUBE", 0.035)
axis = (wr - sh).normalized(); out = (el - sh) - axis * (el - sh).dot(axis); out.normalize()
pole = empty("CODO_ctrl", Matrix.Translation(el + out * 0.25), "SPHERE", 0.03)
for p_ in (fore, hand):
    for c in list(p_.constraints): p_.constraints.remove(c)
ik = fore.constraints.new("IK"); ik.target = ctrl; ik.pole_target = pole; ik.chain_count = 2
cr = hand.constraints.new("COPY_ROTATION"); cr.target = ctrl
def err(deg):  # metres: how far the bone heads and the elbow's roll axis move from the clip's pose
    ik.pole_angle = math.radians(deg); bpy.context.view_layer.update()
    return max(((W @ p.matrix).translation - ref[p.name].translation).length for p in (arm, fore, hand)) + \
        ((W @ fore.matrix).col[0].xyz - ref[fore.name].col[0].xyz).length * 0.01
best = min((err(d), d) for d in range(-180, 180, 2))
best = min([best] + [(err(best[1] + x / 10), best[1] + x / 10) for x in range(-20, 21)])
e_mm = err(best[1]) * 1000
for o in sc.objects: o.hide_select = o.name not in ("MANO_ctrl", "CODO_ctrl", "prop_bottle", "mx")
mx.lock_location = mx.lock_rotation = (True, True, True); mx.lock_scale = (True, True, True)
fingers = [f"mixamorig:{S}HandIndex{i}" for i in (1, 2, 3)]
for b in mx.data.bones: b.hide_select = b.name not in fingers
for n in fingers: PB[n].lock_location = (True, True, True); PB[n].lock_scale = (True, True, True)
for o in sc.objects: o.select_set(o is ctrl)
bpy.context.view_layer.objects.active = ctrl; sc.frame_set(f)
sc.render.filepath = still; bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_mainfile()
print("@@PLACEIK@@", dict(pole_angle_deg=round(best[1], 1), selfcheck_mm=round(e_mm, 2), fingers=fingers), flush=True)
