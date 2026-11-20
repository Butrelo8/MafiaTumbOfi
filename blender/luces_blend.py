"""Makes the owner's lamp file: the truck alone (no road, cast, props off the truck), from a vivo-montado.blend, with every luz_*
lamp in one collection `luces` so he can hide or delete them (docs/luces-dueno.md); blender/luces_leer.py reads his save back.

  GPU=0 ~/.claude/scripts/blender-run /mnt/e/Blender/blender.exe -b <vivo-montado.blend (Windows)> --python-exit-code 1 \
    --python "$(wslpath -w blender/luces_blend.py)" -- <out .blend (Windows)>
"""
import bpy, sys

out = sys.argv[sys.argv.index("--") + 1]
O = bpy.data.objects
cam = O["camion"]
quedan = {cam, *[o for o in cam.children_recursive if not o.name.startswith(("manager", "hector", "alejandro", "diego"))]}
for o in [o for o in O if o not in quedan]:
    bpy.data.objects.remove(o)
for o in [o for o in O if o.hide_render]:  # the other options' dressing: render-hidden in this one
    bpy.data.objects.remove(o)
col = bpy.data.collections.new("luces")
bpy.context.scene.collection.children.link(col)
luces = sorted((o for o in O if o.name.startswith("luz_") and o.type == "MESH"), key=lambda o: o.name)
for o in luces:
    for c in list(o.users_collection):
        c.objects.unlink(o)
    col.objects.link(o)
bpy.data.orphans_purge(do_recursive=True)
bpy.context.preferences.filepaths.use_auto_save_temporary_files = False
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
print("LUCES archivo", out, len(O), "objetos,", len(luces), "luces", flush=True)
