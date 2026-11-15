# clip.py -- <rig.blend open> <clip.fbx> <out.blend>: one Mixamo clip (downloaded on this character,
# With Skin) onto the bound rig "mx": its action is taken from the clip FBX's armature (same bones, same rest), the
# imported objects are dropped, the scene range is the action's. Stills: stills.py.
import bpy, sys, os
a = sys.argv[sys.argv.index("--") + 1:]
fbx, out = a[0], a[1]
sc = bpy.context.scene; arm = bpy.data.objects["mx"]
before = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=fbx)
new = [o for o in bpy.data.objects if o not in before]
src = next(o for o in new if o.type == "ARMATURE"); act = src.animation_data.action
for o in new: bpy.data.objects.remove(o, do_unlink=True)
arm.animation_data_create(); arm.animation_data.action = act
if hasattr(act, "slots") and act.slots:                 # layered actions (Blender 4.4+): bind the clip's slot explicitly
    arm.animation_data.action_slot = act.slots[0]
f0, f1 = (int(x) for x in act.frame_range); sc.frame_start, sc.frame_end = f0, f1; sc.render.fps = 30
print("@@ clip", os.path.basename(fbx), "action", act.name, "frames", f0, f1)
bpy.ops.wm.save_as_mainfile(filepath=out)
