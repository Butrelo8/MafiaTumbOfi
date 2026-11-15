# dump_t.py: the aligned TRELLIS mesh (Body_T in a parts blend) and its base colour, for landmarks.py.
#   $B -b diego_trellis_partes.blend --python dump_t.py -- <out dir (Windows)>
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index("--") + 1:]; out = a[0]
ob = bpy.data.objects[a[1] if len(a) > 1 else "Body_T"]; me = ob.data   # Body in a TRELLIS-refit rig blend
V = np.array([ob.matrix_world @ v.co for v in me.vertices], np.float32)
UV = np.zeros((len(me.loops), 2), np.float32); me.uv_layers.active.data.foreach_get("uv", UV.ravel())
LV = np.array([l.vertex_index for l in me.loops], np.int32)
np.savez_compressed(out + r"\mesh.npz", V=V, UV=UV, LV=LV)
im = next(n.image for n in ob.active_material.node_tree.nodes if n.type == "TEX_IMAGE" and "metal" not in n.image.name.lower()
          and n.image.colorspace_settings.name.lower().startswith("srgb"))
im.filepath_raw = out + r"\basecolor.png"; im.file_format = "PNG"; im.save()
print("@@DUMPT@@", V.shape, im.name, tuple(im.size), V.min(0).round(3), V.max(0).round(3), flush=True)
