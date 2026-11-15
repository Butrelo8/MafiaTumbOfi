# lids_build.py -- <rig or clip blend open> <lids.json> <out.blend> [blink frames f0,f1]: the two upper-lid meshes from
# lids_fit.py (basis = open, keys half and closed), smooth with a level-2 subdivision, skin coloured (look.py's colour
# if set, else lids.json's), bone-parented to mixamorig:Head. With blink frames,
# a blink is keyed on both lids: open at f0, half at f0+2, closed at f0+4..f0+5, half at f0+7, open at f0+9 (~0.3 s).
import bpy, sys, json
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
L = json.load(open(a[0])); out = a[1]; blink = int(a[2]) if len(a) > 2 else None
arm = bpy.data.objects["mx"]; sc = bpy.context.scene
skin = list(sc.get("skin_srgb", L["R"]["skin"]))       # look.py's skin colour when the blend has had it
mat = bpy.data.materials.new("lid"); s = [(c / 255) ** 2.2 for c in skin]; mat.diffuse_color = (*s, 1)   # sRGB -> linear
mat.use_nodes = True; mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*s, 1)
for side in ("R", "L"):
    K = L[side]["keys"]; G = K["open"]; ni, nj = len(G), len(G[0])
    verts = [G[i][j] for i in range(ni) for j in range(nj)]
    faces = [(i * nj + j, (i + 1) * nj + j, (i + 1) * nj + j + 1, i * nj + j + 1) for i in range(ni - 1) for j in range(nj - 1)]
    me = bpy.data.meshes.new("lid_" + side); me.from_pydata(verts, [], faces); me.materials.append(mat)
    me.shade_smooth()                                    # flat 24-column facets read as column banding in the blink
    o = bpy.data.objects.new("lid_" + side, me); sc.collection.objects.link(o)
    sd = o.modifiers.new("subd", "SUBSURF"); sd.levels = sd.render_levels = 2
    o.shape_key_add(name="open")
    for k in ("half", "closed"):
        sk = o.shape_key_add(name=k)
        for idx, p in enumerate(K[k][i][j] for i in range(ni) for j in range(nj)): sk.data[idx].co = Vector(p)
    M = o.matrix_world.copy(); o.parent = arm; o.parent_type = "BONE"; o.parent_bone = "mixamorig:Head"
    bpy.context.view_layer.update(); o.matrix_world = M
    if blink is not None:
        h, c = o.data.shape_keys.key_blocks["half"], o.data.shape_keys.key_blocks["closed"]
        for f, hv, cv in ((blink, 0, 0), (blink + 2, 1, 0), (blink + 4, 0, 1), (blink + 5, 0, 1), (blink + 7, 1, 0), (blink + 9, 0, 0)):
            h.value, c.value = hv, cv; h.keyframe_insert("value", frame=f); c.keyframe_insert("value", frame=f)
    print("@@ lid", side, len(verts), "verts, keys open/half/closed, parent Head", "blink at %s" % blink if blink else "")
bpy.ops.wm.save_as_mainfile(filepath=out)
