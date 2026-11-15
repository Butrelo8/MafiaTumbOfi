# bind.py -- <dressed.blend in> <proxy_rig.fbx> <out.blend>: the parts Diego on Mixamo's rig.
#   skin (Diego)   <- the rigged proxy's mixamorig:* weights, Data Transfer (nearest face, interpolated), normalized
#   shirt, pants   <- the skin's weights the same way (the research's step 4: tight clothes take the body's weights)
#   hair           -> bone-parented to Head; shoes split by side and bone-parented to Left/RightFoot (step 5)
#   body mask      : "hidden" group = skin vertices a garment covers (a ray out along the normal hits it within 4 cm)
#                    plus everything below the shoe tops and the briefs zone (z 0.20-0.33, a gap at the crotch
#                    otherwise shows white); Mask modifier (inverted) on the skin, Armature first
#   Corrective Smooth after the Armature on the skin, shirt and pants.
# Prints the frame check (proxy vs skin bounds), group counts and the hidden share.
import bpy, bmesh, sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]
fbx, out = a[0], a[1]
sc = bpy.context.scene; skin = bpy.data.objects["Diego"]
before = set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=fbx)
new = [o for o in bpy.data.objects if o not in before]
arm = next(o for o in new if o.type == "ARMATURE"); prox = next(o for o in new if o.type == "MESH")
arm.name = "mx"; prox.name = "proxy"
bpy.context.view_layer.update()


def bounds(o):
    M = o.matrix_world; P = np.array([(M @ v.co)[:] for v in o.data.vertices]); return P.min(0), P.max(0)


print("@@ frame: skin", [x.round(4).tolist() for x in bounds(skin)], "proxy", [x.round(4).tolist() for x in bounds(prox)])


def transfer(src, dst):
    for g in list(dst.vertex_groups): dst.vertex_groups.remove(g)
    for g in src.vertex_groups: dst.vertex_groups.new(name=g.name)
    m = dst.modifiers.new("dt", "DATA_TRANSFER"); m.object = src; m.use_vert_data = True
    m.data_types_verts = {"VGROUP_WEIGHTS"}; m.vert_mapping = "POLYINTERP_NEAREST"
    m.layers_vgroup_select_src = "ALL"; m.layers_vgroup_select_dst = "NAME"
    for o in sc.objects: o.select_set(False)
    bpy.context.view_layer.objects.active = dst; dst.select_set(True)
    bpy.ops.object.modifier_apply(modifier="dt")
    bpy.ops.object.vertex_group_normalize_all(lock_active=False)
    am = dst.modifiers.new("Armature", "ARMATURE"); am.object = arm
    cs = dst.modifiers.new("CorrectiveSmooth", "CORRECTIVE_SMOOTH"); cs.rest_source = "ORCO"; cs.use_only_smooth = False
    print("@@", dst.name, "<-", src.name, len(dst.vertex_groups), "groups")


transfer(prox, skin)
for n in ("shirt", "pants"): transfer(skin, bpy.data.objects[n])
# body mask: covered by a garment, or below the shoe tops
dg = bpy.context.evaluated_depsgraph_get()
trees = []
for n in ("shirt", "pants", "shoes"):
    o = bpy.data.objects[n]; bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    trees.append(BVHTree.FromBMesh(bm)); bm.free()
shoes = bpy.data.objects["shoes"]; shoe_top = max((shoes.matrix_world @ v.co).z for v in shoes.data.vertices)
hid = []
for v in skin.data.vertices:
    p = skin.matrix_world @ v.co; n = (skin.matrix_world.to_3x3() @ v.normal).normalized()
    if p.z < shoe_top - 0.004 or 0.20 < p.z < 0.33 or any(t.ray_cast(p + n * 1e-4, n, 0.04)[0] is not None for t in trees): hid.append(v.index)
g = skin.vertex_groups.new(name="hidden"); g.add(hid, 1.0, "REPLACE")
mk = skin.modifiers.new("Mask", "MASK"); mk.vertex_group = "hidden"; mk.invert_vertex_group = True
with bpy.context.temp_override(object=skin): bpy.ops.object.modifier_move_to_index(modifier="Mask", index=0)
print("@@ hidden %d of %d skin vertices (%.0f %%), shoe top z %.3f" % (len(hid), len(skin.data.vertices), 100 * len(hid) / len(skin.data.vertices), shoe_top))
# rigid accessories
def bone_parent(o, bone):
    M = o.matrix_world.copy(); o.parent = arm; o.parent_type = "BONE"; o.parent_bone = bone
    bpy.context.view_layer.update(); o.matrix_world = M
bone_parent(bpy.data.objects["hair"], "mixamorig:Head")
bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = shoes; shoes.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); bm = bmesh.from_edit_mesh(shoes.data)
for v in bm.verts: v.select = (shoes.matrix_world @ v.co).x > 0     # world x: the object may carry a transform
for e in bm.edges: e.select = all(v.select for v in e.verts)          # faces keep a stale selection otherwise
for f in bm.faces: f.select = all(v.select for v in f.verts)
bmesh.update_edit_mesh(shoes.data); bpy.ops.mesh.separate(type="SELECTED"); bpy.ops.object.mode_set(mode="OBJECT")
left = next(o for o in sc.objects if o.name.startswith("shoes.")); left.name = "shoe_L"; shoes.name = "shoe_R"
bone_parent(left, "mixamorig:LeftFoot"); bone_parent(shoes, "mixamorig:RightFoot")
prox.hide_render = True; prox.hide_viewport = True
bpy.ops.wm.save_as_mainfile(filepath=out)
