# fbx_bones.py -- <rig.fbx>: what a Mixamo FBX holds: armature bones (finger chains per hand), meshes, groups, actions.
import bpy, sys
f = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.fbx(filepath=f)
for o in bpy.data.objects:
    if o.type == "ARMATURE":
        names = [b.name.split(":")[-1] for b in o.data.bones]
        print("@@ armature", o.name, len(names), "bones")
        for s in ("Left", "Right"):
            print("@@", s, "hand bones:", sorted(n for n in names if n.startswith(s + "Hand") and n != s + "Hand"))
    if o.type == "MESH":
        print("@@ mesh", o.name, len(o.data.vertices), "verts", len(o.vertex_groups), "groups")
for a in bpy.data.actions: print("@@ action", a.name, tuple(int(x) for x in a.frame_range))
