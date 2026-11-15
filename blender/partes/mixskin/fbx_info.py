# fbx_info.py: what a Mixamo FBX holds (meshes, verts, vertex groups, bones, action range, bounds).
#   $B -b --factory-startup --python fbx_info.py -- <fbx>
import bpy, sys
import numpy as np
f = sys.argv[sys.argv.index("--") + 1]
bpy.ops.import_scene.fbx(filepath=f)
for o in bpy.data.objects:
    print("@@OBJ", o.name, o.type, tuple(round(x, 4) for x in o.scale), tuple(round(x, 3) for x in o.rotation_euler), o.parent.name if o.parent else None)
    if o.type == "MESH":
        dg = bpy.context.evaluated_depsgraph_get()
        V = np.array([(o.matrix_world @ v.co)[:] for v in o.data.vertices])
        print("@@MESH", len(o.data.vertices), "groups", len(o.vertex_groups), "min", V.min(0).round(4), "max", V.max(0).round(4))
        print("@@GROUPS", [g.name for g in o.vertex_groups])
        mx = [len(v.groups) for v in o.data.vertices]; print("@@INFL max", max(mx), "mean", round(sum(mx) / len(mx), 2))
    if o.type == "ARMATURE":
        print("@@BONES", len(o.data.bones), [b.name for b in o.data.bones][:70])
        if o.animation_data and o.animation_data.action:
            a = o.animation_data.action; print("@@ACT", a.name, tuple(a.frame_range))
print("@@SCENE fps", bpy.context.scene.render.fps, "range", bpy.context.scene.frame_start, bpy.context.scene.frame_end)
