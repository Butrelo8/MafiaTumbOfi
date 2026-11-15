# covers.py: joint covers for a parts blend (split.py output), built by construction about the pivot the clip uses:
#   ball  sphere about the joint's pivot (ball-jointed doll / figma ball shoulder): closed under any rotation about it
#   drum  cylinder about the hinge axis (action-figure hinge knee / elbow): closed under rotation about that axis
#   ext   the child's ring (convex hull in the cut plane) pushed into the parent as a tapered peg (vinyl peg-in-socket,
#         telescoping sleeve): the parent's rim stays inside the peg while the child swings
#   extp  the same with the parent's ring pushed into the child (trousers tucked under the shirt hem)
#   none  no cover
# Pivot and hinge axis come from the clip: least-squares fixed point of the parent-relative child motion over the idle
# (frames 1-120:3), the point nearest the ring centroid for a hinge. Size: every child ring point at every frame and
# every parent ring point sit inside the cover, plus a 1.5 mm margin.
# Caps (the faces closing each cut loop) and covers get a flat material in the garment colour read from the rim's
# texels (majority class dark / skin / white, like landmarks.py), so a cut through clothing never shows skin.
#   $B -b <parts.blend> --python covers.py -- <split.json> <out.blend> <out.json>
# env COVERS='{"knee":"drum","shoulder.L":"ball"}' (joint family or full name; default table DEF below)
#     SHOULDER_PIVOT=bone|ring: arm sockets at the bone head (split.py) or moved to the armhole ring centroid
#     FRAMES=a-b:s  frames the swept covers are built over (default 1-120:3 plus 22, 70, 110)
#     EXT_DEPTH=<m> peg depth (default 0.025), PEG_TAPER=<f> far-end scale (default 0.9)
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index("--") + 1:]
info = json.load(open(a[0])); out_blend, out_json = a[1], a[2]
DEF = {"collar": "ball", "hem": "extp", "shoulder": "ball", "elbow": "ext", "wrist": "ball", "hip": "ball",
       "knee": "drum", "cuff": "extp"}
DEF.update(json.loads(os.environ.get("COVERS", "{}")))
SHP = os.environ.get("SHOULDER_PIVOT", "bone"); DEPTH = float(os.environ.get("EXT_DEPTH", 0.025))
TAPER = float(os.environ.get("PEG_TAPER", 0.9)); MARGIN = 0.0015
# the collar plane cuts the neck, the chain and the shirt collar: neck skin on the head side, shirt on the torso side (by hand)
FORCE = {"collar": ("skin", "dark")}
sc = bpy.context.scene; rig = bpy.data.objects["rig"]
parts = {o.name[5:]: o for o in bpy.data.objects if o.name.startswith("part_")}
FR = sorted(set(range(1, 121, 3)) | {22, 70, 110})
if os.environ.get("FRAMES"):
    _r, _s = os.environ["FRAMES"].split(":"); _a, _b = map(int, _r.split("-")); FR = list(range(_a, _b + 1, int(_s)))
rig.data.pose_position = "REST"; sc.frame_set(1); bpy.context.view_layer.update()
for n, o in parts.items():
    assert np.abs(np.array(o.matrix_world) - np.eye(4)).max() < 1e-5, n   # split.py: rest world = mesh coordinates
def V(o): return np.array([v.co for v in o.data.vertices])
def cap_faces(o, c, tol=4e-3):   # faces lying in the cut plane (split.py's triangle_fill caps; holes_fill ones within tol)
    me = o.data; P = V(o); s = (P - c["co"]) @ c["no"]; d = np.linalg.norm(P - c["co"], axis=1)
    near = (np.abs(s) < tol) & (d < 0.14); out = []
    for p in me.polygons:
        if all(near[i] for i in p.vertices) and abs(Vector(p.normal).dot(Vector(c["no"]))) > 0.95: out.append(p.index)
    return out
def ring(o, c, comps=False):   # vertices of part o's cap faces on cut c (rest world = local); comps: per connected loop
    P = V(o); me = o.data; idx = sorted({i for fi in cap_faces(o, c, 2e-6) for i in me.polygons[fi].vertices})
    if not comps: return P[idx]
    par = {i: i for i in idx}
    def f_(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for fi in cap_faces(o, c, 2e-6):
        vs = me.polygons[fi].vertices
        for v_ in vs[1:]: par[f_(v_)] = f_(vs[0])
    g = {}
    for i in idx: g.setdefault(f_(i), []).append(i)
    return sorted((P[m] for m in g.values()), key=len, reverse=True)
cuts = {}
for cn, c in info["cuts"].items():
    c = dict(c, co=np.array(c["co"]), no=np.array(c["no"]) / np.linalg.norm(c["no"])); cuts[cn] = c
res = {"shoulder_pivot": SHP, "joints": {}}

# ---- optional: arm sockets moved to the armhole ring centroid -----------------------------------------------------------
if SHP == "ring":
    for S in "LR":
        e = bpy.data.objects[f"sock_upper_arm.{S}"]; c = cuts[f"shoulder.{S}"]
        ctr = ring(parts[f"upper_arm.{S}"], c).mean(0); old = e.matrix_basis.copy()
        new = old.copy(); new.translation = Vector(ctr); e.matrix_basis = new
        for ch in e.children: ch.matrix_parent_inverse = new.inverted()
        res[f"shoulder_pivot_move_mm.{S}"] = round((Vector(ctr) - old.translation).length * 1000, 1)
    bpy.context.view_layer.update()

# ---- relative motion per joint: X_f maps child rest-world points into the parent's rest frame --------------------------
rig.data.pose_position = "POSE"; X = {cn: [] for cn in cuts}
for f in FR:
    sc.frame_set(f)
    M = {n: np.array(o.matrix_world) for n, o in parts.items()}
    for cn, c in cuts.items(): X[cn].append(np.linalg.inv(M[c["parent"]]) @ M[c["child"]])
rig.data.pose_position = "REST"; sc.frame_set(1); bpy.context.view_layer.update()

def pivot(Xs, ctr):   # min-norm least squares of (R-I)(ctr+d) + t = 0 over frames
    A = np.vstack([x[:3, :3] - np.eye(3) for x in Xs]); b = -np.concatenate([(x[:3, :3] - np.eye(3)) @ ctr + x[:3, 3] for x in Xs])
    d = np.linalg.lstsq(A, b, rcond=1e-6)[0]; p = ctr + d
    r = max(np.linalg.norm(x[:3, :3] @ p + x[:3, 3] - p) for x in Xs); return p, r
def axis_angle(R):
    ang = math.acos(max(-1, min(1, (np.trace(R) - 1) / 2)))
    ax = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]); n = np.linalg.norm(ax)
    return (ax / n if n > 1e-9 else np.array([1.0, 0, 0])), math.degrees(ang)
def hull2(P2):   # monotone chain convex hull, counter-clockwise
    P = sorted(map(tuple, P2)); cr = lambda o, a_, b_: (a_[0] - o[0]) * (b_[1] - o[1]) - (a_[1] - o[1]) * (b_[0] - o[0])
    lo, hi = [], []
    for p in P:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(hi) >= 2 and cr(hi[-2], hi[-1], p) <= 0: hi.pop()
        hi.append(p)
    return np.array(lo[:-1] + hi[:-1])
def basis(n):
    u = np.cross(n, [0, 0, 1.0] if abs(n[2]) < 0.9 else [1.0, 0, 0]); u /= np.linalg.norm(u); return u, np.cross(n, u)

def mk_obj(name, bm, host, mat):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob)
    ob.parent = parts[host]; ob.matrix_parent_inverse = Matrix(); ob["attached"] = host
    for p in me.polygons: p.use_smooth = True
    return ob
def sphere(p, r):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=r, matrix=Matrix.Translation(Vector(p))); return bm
def drum(p, ax, r, lo, hi):
    u, v = basis(ax); bm = bmesh.new(); n = 48
    rings = [[bm.verts.new(Vector(p + ax * h + r * (math.cos(t) * u + math.sin(t) * v))) for t in np.linspace(0, 2 * math.pi, n, endpoint=False)] for h in (lo, hi)]
    for i in range(n): bm.faces.new((rings[0][i], rings[0][(i + 1) % n], rings[1][(i + 1) % n], rings[1][i]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm
def peg(c, pts, sgn, depth, taper):   # convex hull of pts in the cut plane, shrunk 1 mm, pushed sgn*no by depth, tapered
    n = c["no"]; u, v = basis(n); o = pts.mean(0); o = o - n * ((o - c["co"]) @ n)
    H = hull2(np.c_[(pts - o) @ u, (pts - o) @ v]); rr = np.linalg.norm(H, axis=1, keepdims=True); H = H * (rr - 0.001) / rr
    bm = bmesh.new(); L = []
    for k, sc_ in ((0.0, 1.0), (1.0, taper)):
        L.append([bm.verts.new(Vector(o + sgn * n * depth * k + sc_ * (h[0] * u + h[1] * v))) for h in H])
    m = len(H)
    for i in range(m): bm.faces.new((L[0][i], L[0][(i + 1) % m], L[1][(i + 1) % m], L[1][i]))
    bm.faces.new(L[0]); bm.faces.new(L[1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm

# ---- garment colour per joint, from the rim texels -------------------------------------------------------------------
img = next(n.image for o in parts.values() for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes
           if n.type == "TEX_IMAGE" and n.image and n.image.colorspace_settings.name.lower().startswith("srgb") and "metal" not in n.image.name.lower())
W, Hh = img.size; PX = np.empty(W * Hh * 4, np.float32); img.pixels.foreach_get(PX); PX = PX.reshape(Hh, W, 4)[:, :, :3]
mr = next((l.from_node.image for o in parts.values() for m in o.data.materials if m and m.use_nodes for l in m.node_tree.links
           if l.from_node.type == "TEX_IMAGE" and l.to_node.type == "SEPARATE_COLOR"), None)   # glTF metal-rough: G rough, B metal
MR = np.empty(W * Hh * 4, np.float32) if mr else None
if mr: assert tuple(mr.size) == (W, Hh); mr.pixels.foreach_get(MR); MR = MR.reshape(Hh, W, 4)[:, :, :3]
def cls(rgb):
    lum = rgb.mean(1); sat = rgb.max(1) - rgb.min(1); return np.where(lum < 0.22, 0, np.where((sat < 0.08) & (lum > 0.55), 2, 1))
CLS = ("dark", "skin", "white"); mats = {}
def flat_mat(name, rgb, rough=0.42, metal=0.0):
    if name in mats: return mats[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; bsdf = m.node_tree.nodes["Principled BSDF"]
    lin = [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in rgb]   # texels are sRGB
    bsdf.inputs["Base Color"].default_value = (*lin, 1); bsdf.inputs["Roughness"].default_value = rough; bsdf.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*lin, 1); mats[name] = m; return m
def rim_colour(o, caps, every=False):   # texels of the non-cap faces that touch a cap vertex (every: all non-cap faces)
    me = o.data; cv = {i for fi in caps for i in me.polygons[fi].vertices}; capset = set(caps); uvl = me.uv_layers.active.data
    uv = [uvl[li].uv[:] for p in me.polygons if p.index not in capset for li, vi in zip(p.loop_indices, p.vertices) if every or vi in cv]
    if not uv: return None, None
    uv = np.array(uv); px = PX[np.clip((uv[:, 1] * Hh).astype(int), 0, Hh - 1), np.clip((uv[:, 0] * W).astype(int), 0, W - 1)]
    yx = (np.clip((uv[:, 1] * Hh).astype(int), 0, Hh - 1), np.clip((uv[:, 0] * W).astype(int), 0, W - 1))
    k = cls(px); return k, np.c_[px, MR[yx] if MR is not None else np.tile([0, 0.42, 0], (len(px), 1))]

for cn, c in cuts.items():
    fam = cn.split(".")[0]; kind = DEF.get(cn, DEF.get(fam, "none"))
    pc, pp = parts[c["child"]], parts[c["parent"]]; rc, rp = ring(pc, c), ring(pp, c)
    ctr = rc.mean(0); Xs = X[cn]
    pts_c = np.array([(x[:3, :3] @ rc.T).T + x[:3, 3] for x in Xs]).reshape(-1, 3)   # child ring, every frame, parent frame
    p, resid = pivot(Xs, ctr)
    angs = [axis_angle(x[:3, :3]) for x in Xs]; amax = max(a_[1] for a_ in angs)
    ax = max(angs, key=lambda a_: a_[1])[0]
    swing = max(math.degrees(math.acos(min(1, abs(float(a_[0] @ ax))))) for a_ in angs if a_[1] > 2) if amax > 2 else 0.0
    # colour per side: majority class of that side's rim texels (cloth wins a near tie), its median texel as a flat colour
    side = {}; J = dict(kind=kind)
    for nm, o in (("child", pc), ("parent", pp)):
        k, px = rim_colour(o, cap_faces(o, c)); frac = np.bincount(k, minlength=3) / len(k)
        cl = CLS.index(FORCE[fam][nm == "parent"]) if fam in FORCE else int(np.argmax(frac * np.array([1, 0.5, 1])))
        k2, px2 = rim_colour(o, cap_faces(o, c), True)   # the class picked at the rim, its colour from the whole part:
        med = np.median(px2[k2 == cl] if (k2 == cl).any() else px[k == cl], axis=0); rgb = med[:3].tolist()   # rim texels carry baked shade
        mat = flat_mat(f"flat_{CLS[cl]}_{o.name[5:]}", [round(x, 3) for x in rgb], float(med[4]), float(med[5])); side[nm] = mat
        if mat.name not in o.data.materials: o.data.materials.append(mat)
        mi = list(o.data.materials).index(mat); caps = cap_faces(o, c)
        for fi in caps: o.data.polygons[fi].material_index = mi
        comp = ring(o, c, True)
        J[nm] = dict(colour=CLS[cl], rough_metal=[round(float(med[4]), 3), round(float(med[5]), 3)], rim_class_frac=dict(zip(CLS, frac.round(3).tolist())), rgb=[round(x * 255) for x in rgb],
                     caps=len(caps), loops=[(len(q), round(float(np.linalg.norm(q - q.mean(0), axis=1).max()) * 1000, 1)) for q in comp[:4]])
    host = c["child"] if fam == "collar" else c["parent"]; mat = side["child" if host == c["child"] else "parent"]
    J.update(host=host, pivot=p.round(4).tolist(), pivot_from_ring_centroid_mm=round(float(np.linalg.norm(p - ctr)) * 1000, 1),
             pivot_residual_mm=round(resid * 1000, 2), rot_max_deg=round(amax, 1), off_hinge_deg=round(swing, 1))
    if kind == "ball":
        R = max(np.linalg.norm(pts_c - p, axis=1).max(), np.linalg.norm(rp - p, axis=1).max()) + MARGIN + resid
        mk_obj("cover_" + cn, sphere(p, R), host, mat); J["radius_mm"] = round(R * 1000, 1)
    elif kind == "drum":
        allp = np.r_[pts_c, rp]; q = allp - p; h = q @ ax; rad = np.linalg.norm(q - np.outer(h, ax), axis=1)
        R = rad.max() + MARGIN + resid; lo, hi = h.min() - MARGIN, h.max() + MARGIN
        mk_obj("cover_" + cn, drum(p, ax, R, lo, hi), host, mat)
        J.update(radius_mm=round(R * 1000, 1), length_mm=round((hi - lo) * 1000, 1), axis=ax.round(3).tolist())
    elif kind == "ext":
        mk_obj("cover_" + cn, peg(c, rc, -1, DEPTH, TAPER), c["child"], side["child"]); J["depth_mm"] = DEPTH * 1000
    elif kind == "extp":
        mk_obj("cover_" + cn, peg(c, rp, +1, DEPTH, TAPER), c["parent"], side["parent"]); J["depth_mm"] = DEPTH * 1000
    elif kind in ("hull", "band"):
        # hull: the wedge the gap opens over this clip, hull of the parent's rim and the child's ring at every frame.
        # band: the same with both rings pushed BAND_DEPTH into their own parts, a short round cuff that bridges two
        # sections turned against each other (the wrist's constant 80 deg roll), so the step becomes a smooth band
        dd = float(os.environ.get("BAND_DEPTH", 0.006)) if kind == "band" else 0.0
        pc2 = np.array([(x[:3, :3] @ (rc + c["no"] * dd).T).T + x[:3, 3] for x in Xs]).reshape(-1, 3)
        bm = bmesh.new()
        for q in np.r_[rp - c["no"] * dd, pc2, rp, pts_c]: bm.verts.new(Vector(q))
        bmesh.ops.convex_hull(bm, input=bm.verts[:]); bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); mk_obj("cover_" + cn, bm, c["parent"], side["parent"])
    Rm = [x[:3, :3] for x in Xs]; U_, _, Vt = np.linalg.svd(sum(Rm)); Rbar = U_ @ Vt   # chordal mean rotation
    J["rot_spread_deg"] = round(max(axis_angle(Rbar.T @ r_)[1] for r_ in Rm), 1)
    J = json.loads(json.dumps(J, default=float)); res["joints"][cn] = J; print("@@COVER@@", cn, J, flush=True)
rig.data.pose_position = "POSE"
bpy.ops.wm.save_as_mainfile(filepath=out_blend, copy=True)
json.dump(res, open(out_json, "w"), indent=1)
print("@@COVERS@@ saved", out_blend, flush=True)
