# clip_probe.py: a Mixamo clip's frame range and the paths of the hands, hips, head and feet (world, Diego's 1 m frame),
# to place stand-in props from data. $B -b --factory-startup --python clip_probe.py -- <clip.fbx>
import bpy, sys, json
f = sys.argv[sys.argv.index("--") + 1]
bpy.ops.import_scene.fbx(filepath=f)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE"); act = arm.animation_data.action
f0, f1 = map(int, act.frame_range); sc = bpy.context.scene
W = lambda n, t="head": arm.matrix_world @ getattr(arm.pose.bones["mixamorig:" + n], t)
tr = {}
for fr in range(f0, f1 + 1, max(1, (f1 - f0) // 12)):
    sc.frame_set(fr)
    tr[fr] = {k: [round(x, 3) for x in W(n, t)] for k, n, t in (("hips", "Hips", "head"), ("head", "Head", "head"),
              ("handL", "LeftHand", "tail"), ("handR", "RightHand", "tail"), ("footL", "LeftFoot", "head"), ("footR", "RightFoot", "head"),
              ("kneeL", "LeftLeg", "head"))}
print("@@PROBE@@" + json.dumps(dict(range=[f0, f1], fps=sc.render.fps, path=tr)), flush=True)
