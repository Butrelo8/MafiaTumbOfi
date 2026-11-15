# place_nudge.py: the smallest correction on top of the owner's hand placement (place_ik.py blend). It pulls MANO_ctrl
# back toward the shoulder until it is `slack` mm inside the arm's reach (an IK target past reach locks the elbow straight),
# keeps the prop where he put it in the world, then slides the prop `back` mm along its own -z (away from the lips). Prints
# the elbow bend and the hand's move. Bake with sip_bake.py afterwards.
#   $B -b <placed blend> --python place_nudge.py -- <Side> <frame> <prop> <slack mm> <back mm> <out.blend (Windows)>
import bpy, sys, math
from mathutils import Matrix
a = sys.argv[sys.argv.index("--") + 1:]; S, F, prop = a[0], int(a[1]), a[2]; slack, back = float(a[3]) / 1000, float(a[4]) / 1000; out = a[5]
sc = bpy.context.scene; mx = bpy.data.objects["mx"]; PB = mx.pose.bones; W = mx.matrix_world
c = bpy.data.objects["MANO_ctrl"]; p = bpy.data.objects[prop]
sc.frame_set(F); bpy.context.view_layer.update(); keep = p.matrix_world.copy()
sh, el, wr = (W @ PB[f"mixamorig:{S}{b}"].head for b in ("Arm", "ForeArm", "Hand")); reach = (el - sh).length + (wr - el).length
h0 = wr.copy(); v = c.matrix_world.translation - sh
if v.length > reach - slack: c.matrix_world = Matrix.Translation(sh + v.normalized() * (reach - slack) - c.matrix_world.translation) @ c.matrix_world
bpy.context.view_layer.update()
p.matrix_world = keep @ Matrix.Translation((0, 0, -back)); bpy.context.view_layer.update()
sh, el, wr = (W @ PB[f"mixamorig:{S}{b}"].head for b in ("Arm", "ForeArm", "Hand"))
bpy.ops.wm.save_as_mainfile(filepath=out)
print("@@NUDGE@@", dict(elbow_bend_deg=round(math.degrees((el - sh).angle(wr - el)), 1), hand_moved_mm=round((wr - h0).length * 1000, 1),
                        ctrl_to_shoulder_mm=round(v.length * 1000, 1), reach_mm=round(reach * 1000, 1)), flush=True)
