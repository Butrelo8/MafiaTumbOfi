# make_flat.py: the flat-vinyl copy of a parts blend. The base-colour image becomes the posterized texture (flat_tex.py),
# packed; the parts' Principled gets MTO's satin vinyl (reparto.py mat(): roughness 0.42, coat 0.2 at 0.15), which only
# a lit engine shows (Workbench draws the colour, not the finish).
#   $B -b <parts.blend> --python make_flat.py -- <flat png (Windows)> <out.blend (Windows)>
import bpy, sys
flat, out = sys.argv[sys.argv.index("--") + 1:][:2]
for im in bpy.data.images:
    if "basecolor" in im.name.lower():
        cs = im.colorspace_settings.name
        if im.packed_file: im.unpack(method="REMOVE")
        im.filepath = flat; im.reload(); im.colorspace_settings.name = cs; im.pack()
mats = {m for o in bpy.data.objects if o.name.startswith("part_") for m in o.data.materials if m}
for m in mats:
    p = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not p: continue
    for l in list(p.inputs["Roughness"].links): m.node_tree.links.remove(l)
    for l in list(p.inputs["Metallic"].links): m.node_tree.links.remove(l)
    for l in list(p.inputs["Normal"].links): m.node_tree.links.remove(l)
    p.inputs["Roughness"].default_value = 0.42; p.inputs["Metallic"].default_value = 0.0
    p.inputs["Coat Weight"].default_value = 0.2; p.inputs["Coat Roughness"].default_value = 0.15
bpy.ops.wm.save_as_mainfile(filepath=out, copy=True)
print("@@FLAT@@", out, [m.name for m in mats], flush=True)
