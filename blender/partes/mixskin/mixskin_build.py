# mixskin_build.py: column (c) of the binding test. Mixamo's own rig + skin weights (diego_mixamo.fbx) driven by the same
# posed Rigify bones as column (b), so (b) and (c) differ only in the binding. Each mixamorig bone is baked per frame from
# its DEF- counterpart as a rest-relative world delta: W_mx(f) = W_def(f) @ W_def_rest^-1 @ W_mx_rest. The Mixamo mesh
# becomes "Body" (heat body -> "Body_heat", hidden), takes the heat body's materials, and DEF-* groups copied as labels
# only (its modifier points at the Mixamo armature, so they have no influence), so deform.py / rerig_stills.py /
# render.py run unchanged.
#   $B -b <rig_trellis_mx/dance_trellis.blend> --python mixskin_build.py -- <diego_mixamo.fbx> <out.blend> [f0-f1]
import bpy, sys, json
import numpy as np
from mathutils import Matrix
a = sys.argv[sys.argv.index("--") + 1:]
fbx, out = a[0], a[1]; f0, f1 = map(int, (a[2] if len(a) > 2 else "1-299").split("-"))
sc = bpy.context.scene; rig = bpy.data.objects["rig"]; heat = bpy.data.objects["Body"]
before = set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=fbx)
new = [o for o in bpy.data.objects if o not in before]
mx = next(o for o in new if o.type == "ARMATURE"); mesh = next(o for o in new if o.type == "MESH" and o.name.startswith("Diego"))
for o in new:
    if o not in (mx, mesh): bpy.data.objects.remove(o)
if mx.animation_data: mx.animation_data_clear()
mx.name = "mx"; heat.name = "Body_heat"; heat.hide_render = True; mesh.name = "Body"
# vertex correspondence and materials
V = np.array([(mesh.matrix_world @ v.co)[:] for v in mesh.data.vertices]); H = np.array([(heat.matrix_world @ v.co)[:] for v in heat.data.vertices])
same = len(V) == len(H) and float(np.abs(V - H).max()) < 1e-4
if not same:
    from mathutils import kdtree
    kd = kdtree.KDTree(len(H))
    for i, p in enumerate(H): kd.insert(p, i)
    kd.balance(); idx = np.array([kd.find(p)[1] for p in V]); dist = np.linalg.norm(H[idx] - V, axis=1)
else: idx = np.arange(len(V)); dist = np.zeros(len(V))
mesh.data.materials.clear()
for m in heat.data.materials: mesh.data.materials.append(m)
for p in mesh.data.polygons: p.material_index = 0
hn = {g.index: g.name for g in heat.vertex_groups}; lab = {}
for g in heat.vertex_groups:
    if g.name.startswith("DEF-"): lab[g.name] = mesh.vertex_groups.new(name=g.name)
hv = heat.data.vertices
for i, j in enumerate(idx):
    for g in hv[int(j)].groups:
        n = hn[g.group]
        if n in lab and g.weight > 1e-4: lab[n].add([i], g.weight, "REPLACE")
# bone map
MAP = {"Hips": "DEF-spine", "Spine": "DEF-spine.001", "Spine1": "DEF-spine.002", "Spine2": "DEF-spine.003",
       "Neck": "DEF-spine.004", "Head": "DEF-spine.006"}
for s, S in (("Left", ".L"), ("Right", ".R")):
    MAP.update({s + "Shoulder": "DEF-shoulder" + S, s + "Arm": "DEF-upper_arm" + S, s + "ForeArm": "DEF-forearm" + S,
                s + "Hand": "DEF-hand" + S, s + "UpLeg": "DEF-thigh" + S, s + "Leg": "DEF-shin" + S,
                s + "Foot": "DEF-foot" + S, s + "ToeBase": "DEF-toe" + S})
bpy.context.view_layer.objects.active = mx; bpy.ops.object.mode_set(mode="EDIT")
for eb in mx.data.edit_bones: eb.use_connect = False   # connected bones ignore location: the delta needs it
bpy.ops.object.mode_set(mode="OBJECT")
MB, MP, RB = mx.data.bones, mx.pose.bones, rig.data.bones
pre = MB[0].name.split(":")[0] + ":"
miss = [d for d in MAP.values() if d not in RB]; assert not miss, miss
Wr, Wm = rig.matrix_world, mx.matrix_world
order = [b for b in MB]  # bones list is parent-before-child
mx.data.pose_position = "POSE"; rig.data.pose_position = "POSE"
for pb in MP: pb.rotation_mode = "QUATERNION"
ok_resid = []
for f in range(f0, f1 + 1):
    sc.frame_set(f)
    tgt = {}
    for b in order:
        k = b.name[len(pre):]
        if k in MAP:
            d = MAP[k]; tgt[b.name] = Wm.inverted() @ Wr @ rig.pose.bones[d].matrix @ RB[d].matrix_local.inverted() @ Wr.inverted() @ Wm @ b.matrix_local
        elif b.parent: tgt[b.name] = tgt[b.parent.name] @ b.parent.matrix_local.inverted() @ b.matrix_local
        else: tgt[b.name] = b.matrix_local
    for b in order:
        pb = MP[b.name]
        if b.parent: basis = (b.parent.matrix_local.inverted() @ b.matrix_local).inverted() @ tgt[b.parent.name].inverted() @ tgt[b.name]
        else: basis = b.matrix_local.inverted() @ tgt[b.name]
        pb.matrix_basis = basis
        for p in ("location", "rotation_quaternion", "scale"): pb.keyframe_insert(p, frame=f)
    if f in (f0, 153, 240, f1):
        bpy.context.view_layer.update()
        ok_resid.append(max((MP[n].matrix.translation - tgt[n].translation).length for n in tgt))
sc.frame_set(f0)
res = dict(verts=len(V), same_order=bool(same), corr_mm_p99=round(float(np.percentile(dist, 99)) * 1000, 3),
           bones_mapped=len(MAP), head_resid_mm=[round(r * 1000, 3) for r in ok_resid],
           connected=[b.name for b in MB if b.use_connect][:5], mods=[(m.type, m.object.name) for m in mesh.modifiers if m.type == "ARMATURE"])
bpy.ops.wm.save_as_mainfile(filepath=out)
print("@@MIXSKIN@@" + json.dumps(res), flush=True)
