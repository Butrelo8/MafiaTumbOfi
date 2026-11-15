# rig_from_fbx.py: rig_fit.py (firedrone, blender/rig/rig_fit.py, copied 2026-11-14) with the limb joints and the neck
# taken from an externally rigged FBX (Mixamo `mixamorig*:` names or Reallusion CC/ActorCore `CC_Base_*` names) instead
# of rig_fit's ratios (elbow 45 % / wrist 75 % of shoulder->fingertip, knee = hip-ankle midpoint).
#   B=/mnt/e/Blender/blender.exe; $B -b --factory-startup --python "$(wslpath -w rig_from_fbx.py)" -- <glb_win> <fbx_win> <out.blend_win> [tris]
# Output: the same objects as rig_fit.py (Body, rig), so rig_trellis.sh's full / clip / deform stages run unchanged.
# The FBX may be in any pose (Mixamo T-pose, AccuRIG A-pose), unit or offset. Each joint is carried onto our A-pose
# mesh by a similarity transform (Umeyama: rotation, translation, uniform scale) fitted on the vertices one adjacent
# limb segment dominates (summed weight >= 0.95, else 0.8, else 0.5), matched between the FBX mesh and ours by UV (index
# order if UVs fail). Each joint is fitted on both adjacent segments and the more rigid fit (lower rms) is kept: in a
# T-pose the upper arm's vertices near the shoulder are skin-blended (rms 1.2 mm, elbow 1.8 mm off in the identity test)
# while the forearm moves rigidly. "disagree_mm" is the gap to the other segment's estimate (a quality check).
# Not taken from the FBX: spine split, breast, pelvis, foot/toe/heel (rig_fit's mesh landmarks, as before).
# Prints @@RIG@@{json} like rig_fit.py, plus "fbx" (convention, matching, scale, per-joint residual and disagreement).
import sys, json, math, os, re
import bpy, bmesh
from mathutils import Vector
import numpy as np

SK = r"\\wsl.localhost\Ubuntu\home\black\projects\scratch-blender-skills\vendor\blender-skills\skills\blender-character-rigging\scripts"
sys.path.insert(0, SK)
import rigify_build, bind_mesh  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
glb, fbx, out = args[0], args[1], args[2]
tris_goal = int(args[3]) if len(args) > 3 else 40000
res = {}
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob)


def import_glb_mesh():
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glb)
    meshes = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    m = bpy.context.view_layer.objects.active
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    for o in [o for o in bpy.data.objects if o not in before and o != m]:
        bpy.data.objects.remove(o)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return m


def vert_uv(me):
    uv = np.zeros((len(me.vertices), 2))
    lay = me.uv_layers.active.data
    for lp in me.loops:
        uv[lp.vertex_index] = lay[lp.index].uv
    return uv


# --- our full-resolution mesh, normalised exactly as rig_full.py does: correspondence target for the FBX joints ---
full = import_glb_mesh()
FV = np.array([v.co[:] for v in full.data.vertices]); lo, hi = FV.min(0), FV.max(0); s0 = 1.0 / (hi[2] - lo[2])
FV = (FV - [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]]) * s0
FUV = vert_uv(full.data)
bpy.data.objects.remove(full)

# --- the FBX: armature rest heads, its mesh's rest vertices, UVs and weights ---
before = set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=fbx)
new = [o for o in bpy.data.objects if o not in before]
arm = next(o for o in new if o.type == "ARMATURE")
fm = max((o for o in new if o.type == "MESH"), key=lambda o: len(o.data.vertices))
norm = lambda n: re.sub(r"^(mixamorig\d*_|cc_base_)", "", n.split(":")[-1], flags=re.I).lower()  # mixamorig:LeftArm -> leftarm
heads = {norm(b.name): arm.matrix_world @ b.head_local for b in arm.data.bones}
conv = "mixamo" if "leftupleg" in heads else "cc" if "l_thigh" in heads else None
assert conv, f"unknown bone names: {sorted(heads)[:20]}"
# joint = head of this bone; segments = (primary, secondary) vertex-group name prefixes the joint is rigid with
MAP = {"mixamo": {"shoulder": ("{S}arm", ("{S}arm", "{S}shoulder")), "elbow": ("{S}forearm", ("{S}arm", "{S}forearm")),
                  "wrist": ("{S}hand", ("{S}forearm", "{S}hand")), "hip": ("{S}upleg", ("{S}upleg", "hips")),
                  "knee": ("{S}leg", ("{S}upleg", "{S}leg")), "ankle": ("{S}foot", ("{S}leg", "{S}foot")),
                  "neck": ("neck", ("neck", "head"))},
       "cc": {"shoulder": ("{S}_upperarm", ("{S}_upperarm", "{S}_clavicle")), "elbow": ("{S}_forearm", ("{S}_upperarm", "{S}_forearm")),
              "wrist": ("{S}_hand", ("{S}_forearm", "{S}_hand")), "hip": ("{S}_thigh", ("{S}_thigh", "pelvis")),
              "knee": ("{S}_calf", ("{S}_thigh", "{S}_calf")), "ankle": ("{S}_foot", ("{S}_calf", "{S}_foot")),
              "neck": ("necktwist01", ("neck", "head"))}}[conv]
SIDE = {"mixamo": {"L": "left", "R": "right"}, "cc": {"L": "l", "R": "r"}}[conv]

me = fm.data
MV = np.array([fm.matrix_world @ v.co for v in me.vertices])
gname = {g.index: norm(g.name) for g in fm.vertex_groups}
W = {}  # group name -> weight array
for v in me.vertices:
    for g in v.groups:
        W.setdefault(gname[g.group], np.zeros(len(me.vertices)))[v.index] = g.weight
tot = sum(W.values())
# correspondence FBX vertex -> our vertex: UV key (rounded), unique on both sides; index order as the fallback
key = lambda uv: [tuple(k) for k in np.round(uv * 2e4).astype(np.int64)]
ours = {}
for i, k in enumerate(key(FUV)):
    ours[k] = -1 if k in ours else i
pairs = [(i, ours.get(k, -1)) for i, k in enumerate(key(vert_uv(me)))]
pairs = np.array([(i, j) for i, j in pairs if j >= 0])
match = "uv"
if len(pairs) < 0.5 * len(me.vertices) and len(me.vertices) == len(FV):
    pairs = np.stack([np.arange(len(FV))] * 2, 1); match = "index"
res_fbx = dict(convention=conv, match=match, matched=len(pairs), fbx_verts=len(me.vertices), joints={})


def seg_mask(prefix):
    w = sum((a for n, a in W.items() if n.startswith(prefix)), np.zeros(len(me.vertices)))
    return w / np.maximum(tot, 1e-9)


def umeyama(A, B):  # B ~ s R A + t
    ma, mb = A.mean(0), B.mean(0); a, b = A - ma, B - mb
    U, D, Vt = np.linalg.svd(b.T @ a / len(A)); S = np.eye(3); S[2, 2] = np.sign(np.linalg.det(U @ Vt))
    R = U @ S @ Vt; s = np.trace(np.diag(D) @ S) / (a ** 2).sum(1).mean(); t = mb - s * R @ ma
    return s, R, t, float(np.sqrt(((s * (R @ A.T).T + t - B) ** 2).sum(1).mean()))


def carry(p, prefix):
    m = seg_mask(prefix)[pairs[:, 0]]
    for th in (0.95, 0.8, 0.5):
        sel = pairs[m >= th]
        if len(sel) >= 30: break
    if len(sel) < 30: return None  # e.g. Mixamo's Neck: no vertex has half its weight there
    s, R, t, rms = umeyama(MV[sel[:, 0]], FV[sel[:, 1]])
    return s * R @ np.array(p) + t, s, rms, len(sel)


FJ = {}
for role, (bone, segs) in MAP.items():
    for sd in (("L", "R") if "{S}" in bone else ("",)):
        f = lambda x: x.format(S=SIDE[sd]) if sd else x
        b = f(bone); assert b in heads, f"bone {b} missing"
        fits = sorted((e for e in (carry(heads[b], f(sg)) for sg in segs) if e), key=lambda e: e[2])
        assert fits, f"joint {role + sd}: no segment of {segs} has 30 dominated vertices"
        p1, s1, r1, n1 = fits[0]  # the more rigid of the two segments (skin blending bends a segment near a posed joint)
        FJ[role + sd] = p1
        res_fbx["joints"][role + sd] = dict(at=np.round(p1, 4).tolist(), scale=round(s1, 4), rms_mm=round(r1 * 1000, 2), n=n1,
                                            disagree_mm=round(float(np.linalg.norm(p1 - fits[1][0])) * 1000, 2) if len(fits) > 1 else None)
for sd, k in (("L", 1), ("R", -1)):  # Left must land on +x (our frame: facing -Y, character's left = +x)
    assert k * FJ["shoulder" + sd][0] > 0 and k * FJ["hip" + sd][0] > 0, f"side {sd} mirrored: {FJ['shoulder' + sd]}"
res["fbx"] = res_fbx
print(f"@@FBX@@ {conv} match {match} {len(pairs)}/{len(me.vertices)}", flush=True)
for k, v in res_fbx["joints"].items():
    print(f"@@JOINT@@ {k:10s} scale {v['scale']:.3f} rms {v['rms_mm']:5.2f} mm n {v['n']:6d} disagree {v['disagree_mm']} mm", flush=True)
for o in new:
    bpy.data.objects.remove(o, do_unlink=True)

# --- from here: rig_fit.py, with the FBX joints replacing its arm, leg and neck landmarks ---
body = import_glb_mesh()
body.name = "Body"
tris = sum(len(p.vertices) - 2 for p in body.data.polygons)
res["tris_in"] = tris
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")  # MTO: weld glTF UV-seam duplicates so
bpy.ops.mesh.remove_doubles(threshold=1e-6); bpy.ops.object.mode_set(mode="OBJECT")  # bone heat sees one surface
dec = body.modifiers.new("dec", "DECIMATE"); dec.ratio = min(1.0, tris_goal / tris)
bpy.ops.object.modifier_apply(modifier="dec")
res["tris_out"] = sum(len(p.vertices) - 2 for p in body.data.polygons)
V = np.array([body.matrix_world @ v.co for v in body.data.vertices])
lo, hi = V.min(0), V.max(0)
s = 1.0 / (hi[2] - lo[2])
body.location = (-(lo[0] + hi[0]) / 2 * s, -(lo[1] + hi[1]) / 2 * s, -lo[2] * s); body.scale = (s, s, s)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
V = np.array([v.co[:] for v in body.data.vertices])
x, y, z = V[:, 0], V[:, 1], V[:, 2]
res["dims"] = [round(float(d), 3) for d in np.ptp(V, 0)]

# cross-sections every 1 %: half-width, centre-line mesh (rig_fit: crotch -> pelvis width for breast/pelvis bones)
prof = []
for i in range(100):
    m = (z >= i / 100) & (z < (i + 1) / 100)
    prof.append((i, float(np.abs(x[m]).max()) if m.any() else 0.0, bool((np.abs(x[m]) < 0.004).any()) if m.any() else False))
crotch = next(p[0] for p in prof[8:60] if p[2]) / 100
pelvis_hw = max(p[1] for p in prof if crotch <= p[0] / 100 < crotch + 0.06)
torso_hw = pelvis_hw
sh_m = (z < 0.10) & (x > 0)
toe_y, heel_y = float(y[sh_m].min()), float(y[sh_m].max())
J = {}
for sd, k in (("L", 1), ("R", -1)):
    A = V[(k * x > 0) & (z > crotch) & (z > FJ["wrist" + sd][2] - 0.15) & (k * x > k * FJ["wrist" + sd][0])]
    tip = A[np.argmax(k * A[:, 0])]  # fingertip, as rig_fit; the hand bone ends at 80 % from wrist to tip (rig_fit: 0.95 d)
    J[sd] = {r: FJ[r + sd] for r in ("shoulder", "elbow", "wrist", "hip", "knee", "ankle")}
    J[sd]["hand_tail"] = J[sd]["wrist"] + 0.8 * (tip - J[sd]["wrist"])
hip_z = float(np.mean([J[sd]["hip"][2] for sd in "LR"])); sh_z = float(np.mean([J[sd]["shoulder"][2] for sd in "LR"]))
neck_z = float(FJ["neck"][2]); leg_x = float(np.mean([abs(J[sd]["hip"][0]) for sd in "LR"]))
res["landmarks"] = dict(crotch=crotch, hip_z=round(hip_z, 3), sh_z=round(sh_z, 3), neck_z=round(neck_z, 3),
                        torso_hw=round(torso_hw, 3), leg_x=round(leg_x, 3), toe_y=round(toe_y, 3), heel_y=round(heel_y, 3),
                        joints={sd: {r: np.round(p, 3).tolist() for r, p in J[sd].items()} for sd in "LR"})

r = rigify_build.run(add="basic_human", fit="Body", generate=False)
meta = bpy.data.objects[r["metarig"]]
bpy.context.view_layer.objects.active = meta
bpy.ops.object.mode_set(mode="EDIT")
eb = meta.data.edit_bones
sp = [hip_z, hip_z + (sh_z - hip_z) * 0.35, hip_z + (sh_z - hip_z) * 0.7, sh_z, neck_z, neck_z + 0.02, neck_z + 0.05, 1.0]
for i, nm in enumerate(["spine", "spine.001", "spine.002", "spine.003", "spine.004", "spine.005", "spine.006"]):
    eb[nm].head = (0, 0, sp[i]); eb[nm].tail = (0, 0, sp[i + 1])


def bent(a, b, c, push):  # the middle joint keeps its place along the limb but its rest bend lies only in rig_fit's
    # direction (elbow back, knee forward), >= 6 mm: Mixamo's elbow sat 7 mm *below* the shoulder-wrist line (an A-pose
    # droop), which made the rest bend plane point down; deform.py then flagged 94 of 100 dance frames wrong-way
    # (frame 1 included, same mocap angle as the current rig) and Rigify's IK pole would aim down too.
    proj = a + (b - a) @ (c - a) / ((c - a) @ (c - a)) * (c - a); u = push / np.linalg.norm(push)
    u = u - (c - a) * (u @ (c - a)) / ((c - a) @ (c - a)); u /= np.linalg.norm(u)  # perpendicular to the limb
    return proj + u * max((b - proj) @ u, 0.006)


for sd, k in (("L", 1), ("R", -1)):
    j = J[sd]; sh = j["shoulder"]
    el = bent(sh, j["elbow"], j["wrist"], np.array([0, 0.006, 0])); wr = j["wrist"]; ht = j["hand_tail"]
    kn = bent(j["hip"], j["knee"], j["ankle"], np.array([0, -0.006, 0])); hp, an = j["hip"], j["ankle"]
    eb[f"shoulder.{sd}"].head = (k * 0.02, 0, sh[2] + 0.005); eb[f"shoulder.{sd}"].tail = tuple(sh * [0.9, 1, 1])
    eb[f"upper_arm.{sd}"].head = tuple(sh); eb[f"upper_arm.{sd}"].tail = tuple(el)
    eb[f"forearm.{sd}"].head = tuple(el); eb[f"forearm.{sd}"].tail = tuple(wr)
    eb[f"hand.{sd}"].head = tuple(wr); eb[f"hand.{sd}"].tail = tuple(ht)
    eb[f"breast.{sd}"].head = (k * torso_hw * 0.5, 0, sh[2] - 0.08); eb[f"breast.{sd}"].tail = (k * torso_hw * 0.5, -0.04, sh[2] - 0.08)
    eb[f"pelvis.{sd}"].head = (0, 0, hip_z); eb[f"pelvis.{sd}"].tail = (k * leg_x, -0.03, hip_z + 0.06)
    eb[f"thigh.{sd}"].head = tuple(hp); eb[f"thigh.{sd}"].tail = tuple(kn)
    eb[f"shin.{sd}"].head = eb[f"thigh.{sd}"].tail; eb[f"shin.{sd}"].tail = tuple(an)
    eb[f"foot.{sd}"].head = eb[f"shin.{sd}"].tail; eb[f"foot.{sd}"].tail = (an[0], toe_y * 0.55, 0.012)
    eb[f"toe.{sd}"].head = eb[f"foot.{sd}"].tail; eb[f"toe.{sd}"].tail = (an[0], toe_y, 0.012)
    eb[f"heel.02.{sd}"].head = (an[0] - k * 0.03, heel_y, 0); eb[f"heel.02.{sd}"].tail = (an[0] + k * 0.03, heel_y, 0)
bpy.ops.armature.select_all(action="SELECT")
bpy.ops.armature.calculate_roll(type="GLOBAL_POS_Z")
for sd in ("L", "R"):
    for nm in ("thigh", "shin", "foot", "toe"):
        eb[f"{nm}.{sd}"].roll = 0
bpy.ops.object.mode_set(mode="OBJECT")
g = rigify_build.run(metarig=meta.name, generate=True)
rig = bpy.data.objects[g["rig"]]; rig.name = "rig"
res["bind"] = bind_mesh.run(armature="rig", meshes=["Body"])
names = {gr.index: gr.name for gr in body.vertex_groups}
unw = maxinf = bleed = 0
for v in body.data.vertices:
    ws = [(names[gg.group], gg.weight) for gg in v.groups if gg.weight > 1e-4]
    unw += not ws; maxinf = max(maxinf, len(ws))
    if abs(v.co.x) > 0.02 and any(w > 0.1 and not n.startswith("DEF-pelvis") and ((n.endswith(".L") and v.co.x < 0) or (n.endswith(".R") and v.co.x > 0)) for n, w in ws):
        bleed += 1
res["weights"] = {"verts": len(body.data.vertices), "unweighted": unw, "max_influences": maxinf, "lr_bleed_verts": bleed}
pb = rig.pose.bones
L = lambda a, b: (rig.data.bones[a].head_local - rig.data.bones[b].head_local).length
res["leg_len_m"] = round(L("DEF-thigh.L", "DEF-shin.L") + L("DEF-shin.L", "DEF-foot.L"), 4)
for n in ("thigh_ik.L", "thigh_ik.R", "MCH-shin_ik.L", "MCH-shin_ik.R"):
    if n in pb:
        pb[n].ik_stretch = 0.0
bpy.ops.wm.save_as_mainfile(filepath=out)
print("@@RIG@@" + json.dumps(res, default=str), flush=True)
