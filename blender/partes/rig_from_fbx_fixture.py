# rig_from_fbx_fixture.py: identity-test input for rig_from_fbx.py. From the current rig blend (rig_full output: Body with
# Rigify DEF weights), build an external-style FBX whose joints are the current rig's own DEF heads:
#   $B -b <diego_trellis_rig_full$S.blend> --python rig_from_fbx_fixture.py -- <out.fbx (Windows)> mixamo|cc A|T
# mixamo: bones mixamorig:Hips ... LeftArm/LeftForeArm/LeftHand, LeftUpLeg/LeftLeg/LeftFoot; cc: CC_Base_* with twist
# bones (the .001 DEF segments become *Twist01 groups). T: arms rotated to horizontal and applied as rest (Mixamo's
# T-pose download), then the whole figure scaled 1.7x and moved, so the bridge must undo pose, unit and offset.
import bpy, sys, re
from mathutils import Matrix, Vector
out, conv, pose = sys.argv[sys.argv.index("--") + 1:][:3]
rig, body = bpy.data.objects["rig"], bpy.data.objects["Body"]
for o in list(bpy.data.objects):
    if o not in (rig, body): bpy.data.objects.remove(o, do_unlink=True)
H = {b.name: rig.matrix_world @ b.head_local for b in rig.data.bones if b.name.startswith("DEF-")}
T = {b.name: rig.matrix_world @ b.tail_local for b in rig.data.bones if b.name.startswith("DEF-")}
if conv == "mixamo":
    P = "mixamorig:"; S = {"L": "Left", "R": "Right"}
    chain = [("Hips", "DEF-spine", None), ("Spine", "DEF-spine.001", "Hips"), ("Spine1", "DEF-spine.002", "Spine"),
             ("Spine2", "DEF-spine.003", "Spine1"), ("Neck", "DEF-spine.004", "Spine2"), ("Head", "DEF-spine.006", "Neck")]
    limbs = [("{S}Shoulder", "DEF-shoulder.{s}", "Spine2"), ("{S}Arm", "DEF-upper_arm.{s}", "{S}Shoulder"),
             ("{S}ForeArm", "DEF-forearm.{s}", "{S}Arm"), ("{S}Hand", "DEF-hand.{s}", "{S}ForeArm"),
             ("{S}UpLeg", "DEF-thigh.{s}", "Hips"), ("{S}Leg", "DEF-shin.{s}", "{S}UpLeg"),
             ("{S}Foot", "DEF-foot.{s}", "{S}Leg"), ("{S}ToeBase", "DEF-toe.{s}", "{S}Foot")]
    G = {"DEF-spine": "Hips", "DEF-pelvis": "Hips", "DEF-spine.001": "Spine", "DEF-spine.002": "Spine1",
         "DEF-spine.003": "Spine2", "DEF-breast": "Spine2", "DEF-spine.004": "Neck", "DEF-spine.005": "Neck",
         "DEF-spine.006": "Head", "DEF-shoulder": "{S}Shoulder", "DEF-upper_arm": "{S}Arm", "DEF-upper_arm#": "{S}Arm",
         "DEF-forearm": "{S}ForeArm", "DEF-forearm#": "{S}ForeArm", "DEF-hand": "{S}Hand", "DEF-thigh": "{S}UpLeg",
         "DEF-thigh#": "{S}UpLeg", "DEF-shin": "{S}Leg", "DEF-shin#": "{S}Leg", "DEF-foot": "{S}Foot", "DEF-toe": "{S}ToeBase"}
    arm_bone = "{S}Arm"
else:
    P = "CC_Base_"; S = {"L": "L_", "R": "R_"}
    chain = [("Pelvis", "DEF-spine", None), ("Waist", "DEF-spine.001", "Pelvis"), ("Spine01", "DEF-spine.002", "Waist"),
             ("Spine02", "DEF-spine.003", "Spine01"), ("NeckTwist01", "DEF-spine.004", "Spine02"),
             ("NeckTwist02", "DEF-spine.005", "NeckTwist01"), ("Head", "DEF-spine.006", "NeckTwist02")]
    limbs = [("{S}Clavicle", "DEF-shoulder.{s}", "Spine02"), ("{S}Upperarm", "DEF-upper_arm.{s}", "{S}Clavicle"),
             ("{S}UpperarmTwist01", "DEF-upper_arm.{s}.001", "{S}Upperarm"), ("{S}Forearm", "DEF-forearm.{s}", "{S}Upperarm"),
             ("{S}ForearmTwist01", "DEF-forearm.{s}.001", "{S}Forearm"), ("{S}Hand", "DEF-hand.{s}", "{S}Forearm"),
             ("{S}Thigh", "DEF-thigh.{s}", "Pelvis"), ("{S}ThighTwist01", "DEF-thigh.{s}.001", "{S}Thigh"),
             ("{S}Calf", "DEF-shin.{s}", "{S}Thigh"), ("{S}CalfTwist01", "DEF-shin.{s}.001", "{S}Calf"),
             ("{S}Foot", "DEF-foot.{s}", "{S}Calf"), ("{S}ToeBase", "DEF-toe.{s}", "{S}Foot")]
    G = {"DEF-spine": "Pelvis", "DEF-pelvis": "Pelvis", "DEF-spine.001": "Waist", "DEF-spine.002": "Spine01",
         "DEF-spine.003": "Spine02", "DEF-breast": "Spine02", "DEF-spine.004": "NeckTwist01", "DEF-spine.005": "NeckTwist02",
         "DEF-spine.006": "Head", "DEF-shoulder": "{S}Clavicle", "DEF-upper_arm": "{S}Upperarm",
         "DEF-upper_arm#": "{S}UpperarmTwist01", "DEF-forearm": "{S}Forearm", "DEF-forearm#": "{S}ForearmTwist01",
         "DEF-hand": "{S}Hand", "DEF-thigh": "{S}Thigh", "DEF-thigh#": "{S}ThighTwist01", "DEF-shin": "{S}Calf",
         "DEF-shin#": "{S}CalfTwist01", "DEF-foot": "{S}Foot", "DEF-toe": "{S}ToeBase"}
    arm_bone = "{S}Upperarm"
bones = [(P + n, d, P + p if p else None) for n, d, p in chain]
for sd in "LR":
    for n, d, p in limbs:
        bones.append((P + n.format(S=S[sd]), d.format(s=sd), P + p.format(S=S[sd])))
am = bpy.data.objects.new("Armature", bpy.data.armatures.new("Armature")); bpy.context.scene.collection.objects.link(am)
bpy.context.view_layer.objects.active = am; bpy.ops.object.mode_set(mode="EDIT")
for n, d, p in bones:
    e = am.data.edit_bones.new(n); e.head, e.tail = H[d], T[d]
for n, d, p in bones:
    if p: am.data.edit_bones[n].parent = am.data.edit_bones[p]
bpy.ops.object.mode_set(mode="OBJECT")


def target(g):  # DEF group -> fixture bone name: DEF-upper_arm.L.001 -> key "DEF-upper_arm#", side L
    m = re.match(r"^(DEF-[a-z_]+(?:\.\d{3})?)(?:\.([LR]))?(\.001)?$", g)
    if not m: return None
    t = G.get(m[1] + ("#" if m[3] else ""))
    return P + t.format(S=S[m[2]]) if t and m[2] else (P + t if t else None)


acc = {}
names = {g.index: g.name for g in body.vertex_groups}
for v in body.data.vertices:
    for g in v.groups:
        t = target(names[g.group])
        if t: acc.setdefault(t, {}); acc[t][v.index] = acc[t].get(v.index, 0) + g.weight
for m in list(body.modifiers): body.modifiers.remove(m)
body.vertex_groups.clear(); body.parent = None
for t, d in acc.items():
    vg = body.vertex_groups.new(name=t)
    for i, w in d.items(): vg.add([i], w, "REPLACE")
body.parent = am; mod = body.modifiers.new("Armature", "ARMATURE"); mod.object = am
if pose == "T":
    bpy.context.view_layer.objects.active = am; bpy.ops.object.mode_set(mode="POSE")
    for sd, k in (("L", 1), ("R", -1)):
        pb = am.pose.bones[P + arm_bone.format(S=S[sd])]
        d = (pb.tail - pb.head).normalized(); goal = Vector((k, 0, 0))
        q = d.rotation_difference(goal)  # world-space swing to horizontal, about the bone head
        M = pb.bone.matrix_local; pb.matrix = Matrix.Translation(pb.head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-pb.head) @ M
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.objects.active = body; bpy.ops.object.modifier_apply(modifier="Armature")
    bpy.context.view_layer.objects.active = am; bpy.ops.object.mode_set(mode="POSE"); bpy.ops.pose.armature_apply(selected=False)
    bpy.ops.object.mode_set(mode="OBJECT"); mod = body.modifiers.new("Armature", "ARMATURE"); mod.object = am
    am.scale = (1.7, 1.7, 1.7); am.location = (0.3, 0.2, 0.05)
    bpy.ops.object.select_all(action="DESELECT"); am.select_set(True); body.select_set(True)
    bpy.context.view_layer.objects.active = am; bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.select_all(action="DESELECT"); am.select_set(True); body.select_set(True)
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False,
                         apply_scale_options="FBX_SCALE_ALL", bake_anim=False, path_mode="COPY", embed_textures=False)
print("@@FIXTURE@@", conv, pose, len(bones), "bones", len(acc), "groups", sorted(acc)[:6])
