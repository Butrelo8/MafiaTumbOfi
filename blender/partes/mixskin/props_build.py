# props_build.py: build the props props_fit.py fitted, into a fixed clip blend. All dense (<= ~1 cm edges) so pen_fix.py's
# prop -> body test has vertices to test. Names: prop_seat, prop_wheel, prop_guitar_body, prop_guitar_neck, prop_bottle.
#   seat: bevel-free box, floor to the fitted top;
#   wheel: rim torus + hub + two lower spokes, static in the world, spun per frame by the fists' angle (props_fit spin);
#   guitar: transicion.py's toy guitar proportions (two lobes, neck, headstock) as flat solids, parented to the fitted bone;
#   bottle: lathe profile (body, shoulder, neck, lip), Child Of on mixamorig:RightHand with an identity inverse.
#   $B -b <fixed blend> --python props_build.py -- <params.json (Windows)> <out.blend (Windows)>
import bpy, bmesh, sys, json, math
from mathutils import Matrix, Vector, Quaternion
a = sys.argv[sys.argv.index("--") + 1:]; P = json.load(open(a[0])); out = a[1]
sc = bpy.context.scene; mx = bpy.data.objects["mx"]
for o in [o for o in sc.objects if o.name.startswith("prop_")]: bpy.data.objects.remove(o)
def mat(name, rgb, rough=0.5, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; m.diffuse_color = (*rgb, 1)
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal; return m
def obj(name, bm, m):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o)
    for mm in (m if isinstance(m, list) else [m]): me.materials.append(mm)
    return o
def densify(bm, edge=0.01):
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for _ in range(8):
        long = [e for e in bm.edges if e.calc_length() > edge]
        if not long: break
        bmesh.ops.subdivide_edges(bm, edges=long, cuts=1, use_grid_fill=False)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
def box(bm, lo, hi):
    r = bmesh.ops.create_cube(bm, size=1.0); vs = r["verts"]; c = [(l + h) / 2 for l, h in zip(lo, hi)]; s = [h - l for l, h in zip(lo, hi)]
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ Matrix.Diagonal((*s, 1)), verts=vs); return vs
def cyl(bm, cx, cy, rad, z0, z1, seg=48, axis_m=Matrix()):
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=rad, radius2=rad, depth=z1 - z0)
    bmesh.ops.transform(bm, matrix=axis_m @ Matrix.Translation((cx, cy, (z0 + z1) / 2)), verts=r["verts"]); return r["verts"]
info = {}
if "seat" in P:
    s = P["seat"]; bm = bmesh.new(); box(bm, (-s["size"][0] / 2, -s["size"][1] / 2, 0), (s["size"][0] / 2, s["size"][1] / 2, s["top"])); densify(bm, 0.012)
    o = obj("prop_seat", bm, mat("prop_wood", (0.20, 0.12, 0.07), 0.7))
    o.matrix_world = Matrix.Translation((*s["center"], 0)) @ Matrix.Rotation(s["yaw"], 4, "Z"); info["seat"] = len(o.data.vertices)
if "wheel" in P:
    w = P["wheel"]; R, r = w["R"], w["tube"]
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=128, minor_segments=24)
    t = bpy.context.active_object; bm = bmesh.new(); bm.from_mesh(t.data); bpy.data.objects.remove(t)
    cyl(bm, 0, 0, 0.03, -0.012, 0.012, 32)                                             # hub
    for ang in (-60, -120):                                                            # spokes to 4 and 8 o'clock
        th = math.radians(ang); L = R - 0.02
        vs = box(bm, (0.02, -0.007, -0.005), (0.02 + L - 0.01, 0.007, 0.005))
        bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=Matrix.Rotation(th, 3, "Z"))
    densify(bm, 0.01)
    o = obj("prop_wheel", bm, mat("prop_wheel_grey", (0.32, 0.32, 0.34), 0.45)); o.rotation_mode = "QUATERNION"
    Rm = Matrix(w["rot"]); o.location = w["center"]; f0 = P["frames"][0]
    for k, ang in enumerate(w["spin"]):
        o.rotation_quaternion = (Rm @ Matrix.Rotation(ang, 3, "Z")).to_quaternion(); o.keyframe_insert("rotation_quaternion", frame=f0 + k)
    info["wheel"] = len(o.data.vertices)
if "guitar" in P:
    g = P["guitar"]; G = g["dims"]; t = g["thick"]
    bm = bmesh.new(); cyl(bm, 0, 0, G["r1"], -t / 2, t / 2, 64); cyl(bm, G["x2"], 0, G["r2"], -t / 2, t / 2, 64)
    densify(bm, 0.012); body = obj("prop_guitar_body", bm, mat("prop_guitar_tapa", (0.55, 0.22, 0.06), 0.35))
    bm = bmesh.new(); box(bm, (G["n0"] - 0.03, -G["nw"] / 2, G["nz"] - G["nd"] / 2), (G["n1"], G["nw"] / 2, G["nz"] + G["nd"] / 2))
    box(bm, (G["h0"], -0.03, G["nz"] - 0.01), (G["h1"], 0.03, G["nz"] + 0.01)); densify(bm, 0.008)
    neck = obj("prop_guitar_neck", bm, mat("prop_guitar_diapason", (0.012, 0.008, 0.006), 0.5))
    bm = bmesh.new(); cyl(bm, 0.08, 0, 0.04, t / 2 - 0.0005, t / 2 + 0.0002, 32)
    hole = obj("prop_guitar_hole", bm, mat("prop_guitar_hole", (0.01, 0.01, 0.01), 0.8))
    sc.frame_set(P["frames"][0]); pb = mx.pose.bones["mixamorig:" + g["bone"]]; Mb = mx.matrix_world @ pb.matrix
    L = Matrix.Translation(g["origin"]) @ Matrix(g["rot"]).to_4x4()
    for o in (body, neck, hole):
        o.parent = mx; o.parent_type = "BONE"; o.parent_bone = "mixamorig:" + g["bone"]; o.matrix_world = Mb @ L
    if "track" in g:  # the neck aims at the fretting fist: Damped Track +X on an empty riding mixamorig:LeftHand (guitar_track.py)
        for o in (neck, hole): mw = o.matrix_world.copy(); o.parent = body; o.parent_type = "OBJECT"; o.matrix_world = mw
        sc.frame_set(g["track"]["frame"]); bpy.context.view_layer.update()
        e = bpy.data.objects.new("guitar_aim", None); sc.collection.objects.link(e)
        e.parent = mx; e.parent_type = "BONE"; e.parent_bone = "mixamorig:LeftHand"
        e.matrix_world = mx.matrix_world @ pb.matrix @ L @ Matrix.Translation((g["track"]["x"], 0, 0))
        c = body.constraints.new("DAMPED_TRACK"); c.target = e; c.track_axis = "TRACK_X"
    info["guitar"] = [len(body.data.vertices), len(neck.data.vertices)]
if "bottle" in P:
    b = P["bottle"]; B = b["dims"]; L = b["length"]; lb = L - B["ls"] - B["ln"]
    prof = [(0, 0.0), (B["rb"] - 0.003, 0.0), (B["rb"], 0.003)]
    prof += [(B["rb"], z) for z in [0.003 + k * (lb - 0.003) / 12 for k in range(1, 13)]]
    prof += [(B["rb"] + (B["rn"] - B["rb"]) * k / 7, lb + B["ls"] * k / 7) for k in range(1, 8)]
    prof += [(B["rn"], lb + B["ls"] + B["ln"] * k / 8) for k in range(1, 8)] + [(B["rn"], L - 0.002), (B["rn"] - 0.002, L), (0, L)]
    bm = bmesh.new(); seg = 40; rings = []
    for rad, z in prof:
        if rad < 1e-6: rings.append([bm.verts.new((0, 0, z))]); continue
        rings.append([bm.verts.new((rad * math.cos(2 * math.pi * i / seg), rad * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)])
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(seg):
            if len(r0) == 1: bm.faces.new((r0[0], r1[i], r1[(i + 1) % seg]))
            elif len(r1) == 1: bm.faces.new((r0[i], r0[(i + 1) % seg], r1[0]))
            else: bm.faces.new((r0[i], r0[(i + 1) % seg], r1[(i + 1) % seg], r1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); densify(bm, 0.008)
    o = obj("prop_bottle", bm, mat("prop_amber", (0.35, 0.13, 0.02), 0.15))
    c = o.constraints.new("CHILD_OF"); c.target = mx; c.subtarget = "mixamorig:RightHand"; c.set_inverse_pending = False
    c.inverse_matrix = Matrix.Identity(4)
    o.matrix_basis = Matrix.Translation(b["base"]) @ Matrix(b["rot"]).to_4x4(); info["bottle"] = len(o.data.vertices)
sc.frame_set(P["frames"][0]); bpy.ops.wm.save_as_mainfile(filepath=out)
print("@@PROPSBUILD@@", json.dumps(info), flush=True)
