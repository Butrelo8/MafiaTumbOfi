# clip_build.py: a Mixamo clip (diego_* on Mixamo's own rig and skin) as a blend: mesh "Body" with the heat body's
# materials (same shading as the binding test), armature "mx", and stand-in props placed from the clip's own joint paths.
#   $B -b --factory-startup --python clip_build.py -- <clip.fbx> <material source blend> <out.blend> <kind>
# kind: sit (box seat under the seated hips) | drive (box seat + torus wheel through both hands) | guitar (block guitar:
#       body box in front of the belly at the strumming hand, neck box to the fretting hand, carried by the Spine bone)
# Props are named prop_*; the seat is placed at the lowest seated buttock vertex.
import bpy, sys, json, math
import numpy as np
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index("--") + 1:]
fbx, msrc, out, kind = a
bpy.ops.import_scene.fbx(filepath=fbx)
for o in list(bpy.data.objects):
    if o.type in ("CAMERA", "LIGHT") or o.name.startswith("Cube"): bpy.data.objects.remove(o)
mx = next(o for o in bpy.data.objects if o.type == "ARMATURE"); body = next(o for o in bpy.data.objects if o.type == "MESH")
mx.name = "mx"; body.name = "Body"
with bpy.data.libraries.load(msrc) as (src, dst): dst.objects = ["Body"]
hb = dst.objects[0]; body.data.materials.clear()
for m in hb.data.materials: body.data.materials.append(m)
for p in body.data.polygons: p.material_index = 0
bpy.data.objects.remove(hb)
sc = bpy.context.scene; act = mx.animation_data.action; f0, f1 = map(int, act.frame_range)
sc.frame_start, sc.frame_end, sc.render.fps = f0, f1, 30
PB = mx.pose.bones; W = lambda n, t="head": mx.matrix_world @ getattr(PB["mixamorig:" + n], t)
def mesh_world(f):
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); ev = body.evaluated_get(dg); m = ev.to_mesh()
    P = np.array([(body.matrix_world @ v.co)[:] for v in m.vertices]); ev.to_mesh_clear(); return P
def box(name, center, size, rot=Matrix()):
    me = bpy.data.meshes.new(name); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o)
    import bmesh; bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    o.matrix_world = Matrix.Translation(center) @ rot.to_4x4() @ Matrix.Diagonal((*size, 1)); return o
mat = bpy.data.materials.new("prop_grey"); mat.diffuse_color = (0.35, 0.33, 0.30, 1); mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.35, 0.33, 0.30, 1)
info = {"range": [f0, f1], "kind": kind}
if kind in ("sit", "drive"):
    zs = []
    for f in range(f0, f1 + 1, 4): sc.frame_set(f); zs.append((W("Hips").z, f))
    zmin = min(z for z, _ in zs); seated = [f for z, f in zs if z < zmin + 0.01]; fs = seated[len(seated) // 2]
    sc.frame_set(fs); hips = W("Hips"); feet = (W("LeftFoot") + W("RightFoot")) / 2
    fwd = Vector((feet.x - hips.x, feet.y - hips.y, 0)).normalized()
    P = mesh_world(fs); gn = {g.index: g.name.split(":")[-1] for g in body.vertex_groups}
    seatg = [max(((g.weight, gn[g.group]) for g in v.groups), default=(0, ""))[1] in ("Hips", "LeftUpLeg", "RightUpLeg") for v in body.data.vertices]
    top = float(P[np.array(seatg), 2].min())  # lowest vertex the Hips / UpLeg bones dominate: buttocks and thigh undersides
    rot = Matrix(((fwd.y, fwd.x, 0), (-fwd.x, fwd.y, 0), (0, 0, 1))).transposed()  # local X across, local Y along fwd
    c = Vector((hips.x, hips.y, top / 2)) + fwd * 0.02
    s = box("prop_seat", c, (0.26, 0.22, top), Matrix.Rotation(math.atan2(fwd.y, fwd.x) - math.pi / 2, 3, "Z"))
    s.data.materials.append(mat); info.update(seat_top=round(top, 4), seated_frame=fs, seated_frames=[seated[0], seated[-1]], fwd=list(fwd))
if kind == "drive":
    HL, HR = [], []
    for f in range(f0, f1 + 1, 3): sc.frame_set(f); HL.append(W("LeftHand", "tail")); HR.append(W("RightHand", "tail"))
    hl = sum(HL, Vector()) / len(HL); hr = sum(HR, Vector()) / len(HR); c = (hl + hr) / 2; r = (hl - hr).length / 2
    across = (hl - hr).normalized(); chest = W("Spine2"); back = Vector((chest.x - c.x, chest.y - c.y, 0)).normalized()
    axis = (back * math.cos(math.radians(25)) + Vector((0, 0, 1)) * math.sin(math.radians(25)))   # wheel tilted 25 deg
    axis = (axis - across * axis.dot(across)).normalized()
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.012, major_segments=64, minor_segments=12)
    t = bpy.context.active_object; t.name = "prop_wheel"
    z = axis; x = across; y = z.cross(x); t.matrix_world = Matrix.Translation(c) @ Matrix((x, y, z)).transposed().to_4x4()
    t.data.materials.append(mat); info.update(wheel_center=[round(v, 4) for v in c], wheel_r=round(r, 4), wheel_axis=[round(v, 3) for v in axis])
if kind == "guitar":
    sc.frame_set(f0); hr = W("RightHand", "tail"); hl = W("LeftHand", "tail"); sp = W("Spine1"); hips = W("Hips")
    P = mesh_world(f0); belly = P[(np.abs(P[:, 2] - hr.z) < 0.03) & (np.abs(P[:, 0] - hr.x) < 0.05)]
    front_y = float(belly[:, 1].min())   # the belly's front surface at the strumming hand's height
    bc = Vector((hr.x + 0.03, front_y - 0.035, hr.z - 0.01))      # body centre: behind the strumming hand, off the belly
    neck_end = hl; d = (neck_end - bc); L = d.length; dn = d.normalized()
    zrot = Matrix.Rotation(math.atan2(dn.y, dn.x), 3, "Z") @ Matrix.Rotation(math.asin(max(-1, min(1, dn.z))), 3, "Y").inverted()
    gb = box("prop_guitar_body", bc, (0.16, 0.05, 0.13), Matrix.Rotation(math.atan2(dn.y, dn.x), 3, "Z"))
    gn = box("prop_guitar_neck", bc + d * 0.55, (L * 0.9, 0.022, 0.028), zrot)
    for o in (gb, gn):
        o.data.materials.append(mat); mw = o.matrix_world.copy(); o.parent = mx; o.parent_type = "BONE"; o.parent_bone = "mixamorig:Spine"
        o.matrix_world = mw
    info.update(guitar_body=[round(v, 4) for v in bc], neck_len=round(L, 4), belly_front_y=round(front_y, 4))
sc.frame_set(f0)
bpy.ops.wm.save_as_mainfile(filepath=out)
print("@@CLIPBUILD@@" + json.dumps(info), flush=True)
