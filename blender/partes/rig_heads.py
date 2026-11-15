# rig_heads.py: dump the rest heads and tails of every DEF bone of "rig" to JSON (rig_from_fbx identity test).
#   $B -b <rig.blend> --python rig_heads.py -- <out.json (Windows)>
import bpy, sys, json
rig = bpy.data.objects["rig"]
json.dump({b.name: [list(rig.matrix_world @ b.head_local), list(rig.matrix_world @ b.tail_local)]
           for b in rig.data.bones if b.name.startswith("DEF-")}, open(sys.argv[sys.argv.index("--") + 1], "w"))
