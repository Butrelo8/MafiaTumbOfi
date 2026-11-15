# split.py: Diego as a part-built toy. Weld, plane cuts at the joints (bounded to each joint), capped loops, every part
# rigidly parented to one bone of the existing rig (no skin weights). Method: the 11-09 StableGen+teardown proof
# (visual-lab comfyui/lab/stablegen-teardown-proof-2026-11-09: weld -> bisect_plane -> fill the cut loops), plus a
# leak test per cut and cap UVs copied from the rim so the cut face takes the rim's colour.
#   $B -b idle_v2.blend --python split.py -- <out.blend> <out.json> [glb to align on the Tripo Body]
# env: SHOULDER=armhole|hem (cut through the shoulder pivot, or at the sleeve hem); PIN=1|0 (1: arm parts hang from a
#      socket fixed on the torso and copy the arm bones' world rotation, i.e. no clavicle joint; 0: straight bone parents)
#      WELD=<m> (default 1e-6 Tripo, 1e-5 for a glb)
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector, Matrix

a = sys.argv[sys.argv.index("--") + 1:]
out_blend, out_json = a[0], a[1]; glb = a[2] if len(a) > 2 else None
SHOULDER = os.environ.get("SHOULDER", "armhole"); PIN = os.environ.get("PIN", "1") == "1"
rig = bpy.data.objects["rig"]; B = rig.data.bones
rig.data.pose_position = "REST"; bpy.context.view_layer.update()
H = lambda n: Vector(B[n].head_local); T = lambda n: Vector(B[n].tail_local); D = lambda n: (T(n) - H(n)).normalized()
body = bpy.data.objects["Body"]
for n in ("Body_proxy",):
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n])

# ---- source mesh in world space, rest pose -------------------------------------------------------------------------
if glb:
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=glb)
    new = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    for o in bpy.data.objects:
        if o not in before and o.type != "MESH": bpy.data.objects.remove(o)
    src = new[0]
    if len(new) > 1:
        with bpy.context.temp_override(active_object=src, selected_editable_objects=new): bpy.ops.object.join()
    src.parent = None; me = src.data; me.transform(src.matrix_world); src.matrix_world = Matrix()
    P = np.array([v.co for v in me.vertices]); Q = np.array([v.co for v in body.data.vertices])
    s = (Q[:, 2].max() - Q[:, 2].min()) / (P[:, 2].max() - P[:, 2].min())
    c_p = np.r_[(P[:, :2].min(0) + P[:, :2].max(0)) / 2, P[:, 2].min()]; c_q = np.r_[(Q[:, :2].min(0) + Q[:, :2].max(0)) / 2, Q[:, 2].min()]
    me.transform(Matrix.Translation(Vector(c_q)) @ Matrix.Scale(s, 4) @ Matrix.Translation(Vector(-c_p)))
    src.name = "Body_T"; WELD = float(os.environ.get("WELD", 1e-5))
    align = {"scale": s, "bbox_src": [P.min(0).tolist(), P.max(0).tolist()], "bbox_tripo": [Q.min(0).tolist(), Q.max(0).tolist()]}
else:
    src = body; WELD = float(os.environ.get("WELD", 1e-6)); align = None
mat_src = list(src.data.materials)
bm = bmesh.new(); bm.from_mesh(src.data)
if src is body: bm.transform(body.matrix_world)
nv0 = len(bm.verts); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=WELD)
uvl = bm.loops.layers.uv.active
info = {"src": src.name, "verts_in": nv0, "verts_welded": len(bm.verts), "faces": len(bm.faces), "weld": WELD,
        "shoulder": SHOULDER, "pin": PIN, "align": align, "cuts": {}, "parts": {}}

# ---- cuts: plane (co, no -> child side), bounded region, child/parent part ---------------------------------------------
G = json.loads(os.environ.get("GARMENT", "{}"))       # garment lines; defaults measured on the Tripo mesh (landmarks.py)
HEM, CUFF, CROTCH, HIPOUT = G.get("hem", 0.280), G.get("cuff", 0.068), G.get("crotch", 0.235), G.get("hipout", 0.270)
COLLAR = G.get("collar", [0.0, 0.0, 0.56]); COLLAR_NO = Vector(G.get("collar_no", [0.0, -0.36, 1.0])).normalized()
SLEEVE = G.get("sleeve", 0.048)                         # sleeve hem: metres along the upper arm from its head
cuts = [dict(name="collar", co=Vector(COLLAR), no=COLLAR_NO, c=Vector((0, 0.02, COLLAR[2])), r=0.09, box=lambda P: np.abs(P[:, 0]) < 0.07,
             child="head", parent="torso"),
        dict(name="hem", co=Vector((0, 0, HEM)), no=Vector((0, 0, 1)), c=Vector((0, 0.02, HEM)), r=0.2,
             box=lambda P: (np.abs(P[:, 0]) < 0.15) & (np.abs(P[:, 2] - HEM) < 0.03), child="torso", parent="pelvis")]
for S, k in (("L", 1), ("R", -1)):
    up, fo, ha = H(f"ORG-upper_arm.{S}"), H(f"ORG-forearm.{S}"), H(f"ORG-hand.{S}")
    sh_co = up if SHOULDER == "armhole" else up + D(f"ORG-upper_arm.{S}") * SLEEVE
    hp = H(f"ORG-thigh.{S}"); kn = H(f"ORG-shin.{S}")
    hip_no = Vector((k * (HIPOUT - CROTCH), 0, -0.105)).normalized()
    cuts += [
        dict(name=f"wrist.{S}", co=ha, no=D(f"ORG-forearm.{S}"), c=ha, r=0.08, box=lambda P, k=k: k * P[:, 0] > 0.2,
             child=f"hand.{S}", parent=f"forearm.{S}"),
        dict(name=f"elbow.{S}", co=fo, no=(D(f"ORG-upper_arm.{S}") + D(f"ORG-forearm.{S}")).normalized(), c=fo, r=0.08,
             box=lambda P, k=k: k * P[:, 0] > 0.15, child=f"forearm.{S}", parent=f"upper_arm.{S}"),
        dict(name=f"shoulder.{S}", co=sh_co, no=D(f"ORG-upper_arm.{S}"), c=sh_co, r=0.09, box=lambda P, k=k: k * P[:, 0] > 0.06,
             child=f"upper_arm.{S}", parent="torso"),
        dict(name=f"hip.{S}", co=Vector((0, 0, CROTCH)), no=hip_no, c=hp, r=0.15,
             box=lambda P, k=k: (k * P[:, 0] > -0.0005) & (P[:, 2] < HEM - 0.002), child=f"thigh.{S}", parent="pelvis"),
        dict(name=f"knee.{S}", co=kn, no=(D(f"ORG-thigh.{S}") + D(f"ORG-shin.{S}")).normalized(), c=kn, r=0.08,
             box=lambda P, k=k: k * P[:, 0] > 0.0, child=f"shin.{S}", parent=f"thigh.{S}"),
        dict(name=f"cuff.{S}", co=Vector((k * 0.065, 0, CUFF)), no=Vector((0, 0, -1)), c=Vector((k * 0.065, 0.02, CUFF)), r=0.09,
             box=lambda P, k=k: k * P[:, 0] > 0.0, child=f"shoe.{S}", parent=f"shin.{S}")]
bone = {"head": "ORG-spine.006", "torso": "ORG-spine.003", "pelvis": "ORG-spine"}
for S in "LR":
    bone.update({f"upper_arm.{S}": f"ORG-upper_arm.{S}", f"forearm.{S}": f"ORG-forearm.{S}", f"hand.{S}": f"ORG-hand.{S}",
                 f"thigh.{S}": f"ORG-thigh.{S}", f"shin.{S}": f"ORG-shin.{S}", f"shoe.{S}": f"ORG-foot.{S}"})

bm.verts.ensure_lookup_table()
def nearest_vert(p):
    V = np.array([v.co for v in bm.verts]); return int(np.argmin(((V - np.array(p)) ** 2).sum(1)))
mid = lambda n: (H(n) + T(n)) / 2
def seeds():
    V = np.array([v.co for v in bm.verts])
    sd = {"head": int(np.argmax(V[:, 2])), "torso": nearest_vert((0, -0.1, 0.42)), "pelvis": nearest_vert((0, -0.06, (HEM + CROTCH) / 2))}
    for S, k in (("L", 1), ("R", -1)):
        sd[f"upper_arm.{S}"] = nearest_vert(H(f"ORG-upper_arm.{S}") + D(f"ORG-upper_arm.{S}") * 0.09)
        sd[f"forearm.{S}"] = nearest_vert(mid(f"ORG-forearm.{S}")); sd[f"hand.{S}"] = nearest_vert(T(f"ORG-hand.{S}"))
        sd[f"thigh.{S}"] = nearest_vert(mid(f"ORG-thigh.{S}")); sd[f"shin.{S}"] = nearest_vert(mid(f"ORG-shin.{S}"))
        sd[f"shoe.{S}"] = nearest_vert((k * 0.065, -0.104, 0.012))
    return sd

def region(cut, P):   # P: N x 3 -> mask
    P = np.atleast_2d(np.asarray(P, float)); return (np.linalg.norm(P - np.array(cut["c"]), axis=1) < cut["r"]) & cut["box"](P)
def on_cut_np(cut, P):
    P = np.atleast_2d(np.asarray(P, float)); return (np.abs((P - np.array(cut["co"])) @ np.array(cut["no"])) < 2e-6) & region(cut, P)
def vco(b): return np.array([v.co for v in b.verts])

# ---- leak test on the vertex graph: edges crossing the plane inside the region are blocked ---------------------------
def reach(cut, a_seed, b_seed):
    V = np.array([v.co for v in bm.verts]); E = np.array([[e.verts[0].index, e.verts[1].index] for e in bm.edges])
    s = (V - np.array(cut["co"])) @ np.array(cut["no"])
    inr = region(cut, V)
    block = inr[E[:, 0]] & inr[E[:, 1]] & ((np.sign(s[E[:, 0]]) != np.sign(s[E[:, 1]])) | (np.abs(s[E]).min(1) < 1e-7))
    E = E[~block]; E2 = np.r_[E, E[:, ::-1]]; o = np.argsort(E2[:, 0]); E2 = E2[o]
    st = np.searchsorted(E2[:, 0], np.arange(len(V) + 1)); seen = np.zeros(len(V), bool); seen[a_seed] = True; fr = [a_seed]
    while fr:
        nx = []
        for u in fr:
            for w in E2[st[u]:st[u + 1], 1]:
                if not seen[w]: seen[w] = True; nx.append(w)
        fr = nx
    return bool(seen[b_seed]), int(seen.sum())

def ring_radius(cut, co):   # largest distance from co of the plane's crossings inside the region (the cut loop's size)
    V = vco(bm); s = (V - np.array(co)) @ np.array(cut["no"]); c2 = dict(cut, co=co, c=co); inr = region(c2, V)
    E = np.array([[e.verts[0].index, e.verts[1].index] for e in bm.edges]) if "E" not in ring_radius.__dict__ else ring_radius.E
    ring_radius.E = E
    x = inr[E[:, 0]] & inr[E[:, 1]] & (np.sign(s[E[:, 0]]) != np.sign(s[E[:, 1]]))
    if not x.any(): return 9.0
    R = V[E[x, 0]]; return float(np.linalg.norm(R - R.mean(0), axis=1).max())   # ring size about its own centre

sd = seeds()
for cut in cuts:
    shift = 0.0; leak = True; n = 0; rr = None
    if cut["name"].split(".")[0] in ("wrist", "elbow", "knee"):
        # snap to the narrowest closed loop within -20..+10 mm of the pivot (a pivot inside the palm cuts the palm)
        best = None; co0 = cut["co"]; c0 = cut["c"]
        for t in np.arange(-0.035, 0.0101, 0.0025):
            co = co0 + cut["no"] * float(t); trial = dict(cut, co=co, c=co)
            lk, nn = reach(trial, sd[cut["child"]], sd[cut["parent"]])
            if lk: continue
            r_ = ring_radius(cut, co)
            if best is None or r_ < best[0]: best = (r_, float(t), co, nn)
        if best:
            rr, t, cut["co"], n = best; cut["c"] = cut["co"]; shift = round(t * 1000, 1); leak = False
    else:
        for it in range(8):
            leak, n = reach(cut, sd[cut["child"]], sd[cut["parent"]])
            if not leak: break
            cut["co"] = cut["co"] + cut["no"] * 0.005; shift += 5
    info["cuts"][cut["name"]] = {"co": list(cut["co"]), "no": list(cut["no"]), "shift_mm": shift, "leak": leak,
                                 "ring_radius_mm": rr and round(rr * 1000, 1), "child_verts": n,
                                 "child": cut["child"], "parent": cut["parent"]}
    print("@@CUT@@", cut["name"], "shift", shift, "leak", leak, "ring", rr, "child verts", n, flush=True)

# ---- bisect inside each region, then flood faces from each seed without crossing a cut edge --------------------------
for cut in cuts:
    bm.verts.ensure_lookup_table(); idx = np.where(region(cut, vco(bm)))[0]
    fs = list({f for i in idx for f in bm.verts[i].link_faces})
    es = list({e for f in fs for e in f.edges}); vs = list({v for f in fs for v in f.verts})
    bmesh.ops.bisect_plane(bm, geom=fs + es + vs, dist=1e-6, plane_co=cut["co"], plane_no=cut["no"])
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
def on_cut(v, cut): return bool(on_cut_np(cut, [v.co])[0])
Vb = vco(bm); Eb = np.array([[e.verts[0].index, e.verts[1].index] for e in bm.edges]); cutedge = np.zeros(len(Eb), bool)
for cut in cuts:
    oc = on_cut_np(cut, Vb); cutedge |= oc[Eb[:, 0]] & oc[Eb[:, 1]]
sd = seeds(); owner = -np.ones(len(bm.faces), int); names = list(bone)
clash = {}
for pi, pn in enumerate(names):
    start = [f for f in bm.verts[sd[pn]].link_faces]; fr = [f.index for f in start]
    for i in fr: owner[i] = pi
    while fr:
        nx = []
        for fi in fr:
            for e in bm.faces[fi].edges:
                if cutedge[e.index]: continue
                for g in e.link_faces:
                    if owner[g.index] == -1: owner[g.index] = pi; nx.append(g.index)
                    elif owner[g.index] != pi: clash[(pn, names[owner[g.index]])] = clash.get((pn, names[owner[g.index]]), 0) + 1
        fr = nx
un = np.where(owner < 0)[0]
if len(un):   # shells no seed reaches (TRELLIS has separate hair/eye shells): each cut-bounded piece goes whole to the
    # part that owns most of the nearest owned faces of its vertices
    C = np.array([f.calc_center_median() for f in bm.faces]); own = np.where(owner >= 0)[0]
    from mathutils.kdtree import KDTree
    kd = KDTree(len(own))
    for j, i in enumerate(own): kd.insert(C[i], j)
    kd.balance()
    comp = -np.ones(len(bm.faces), int); nc = 0
    for s0 in un:
        if comp[s0] >= 0: continue
        comp[s0] = nc; fr = [s0]; mem = [s0]
        while fr:
            nx = []
            for fi in fr:
                for e in bm.faces[fi].edges:
                    if cutedge[e.index]: continue
                    for g in e.link_faces:
                        if owner[g.index] < 0 and comp[g.index] < 0: comp[g.index] = nc; nx.append(g.index); mem.append(g.index)
            fr = nx
        votes = np.bincount([owner[own[kd.find(C[i])[1]]] for i in mem[::max(1, len(mem) // 200)]], minlength=len(names))
        owner[mem] = int(votes.argmax()); nc += 1
    info["unreached_pieces"] = nc
info["unreached_faces"] = int(len(un)); info["clash"] = {f"{a}|{b}": n for (a, b), n in clash.items()}
print("@@FLOOD@@ unreached", len(un), "clash", info["clash"], flush=True)

# ---- one object per part, cut loops capped (UVs from the rim), parented rigidly ---------------------------------------
socks, srest = {}, {}
def rest_world(bn): return rig.matrix_world @ B[bn].matrix_local
def parent_to_bone(ob, bn):
    ob.parent = rig; ob.parent_type = "BONE"; ob.parent_bone = bn
    ob.matrix_parent_inverse = (rest_world(bn) @ Matrix.Translation((0, B[bn].length, 0))).inverted()
def ring_center(cut):
    oc = on_cut_np(cut, Vb); return Vector(Vb[oc].mean(0))
def sock(S, seg, parent, pivot=None):
    # an empty at the bone's rest frame (or at `pivot`), carried by the torso or the previous socket, copying the bone's
    # world rotation: the arm hangs from a socket fixed on the torso (no clavicle), the hand swivels about the wrist's centre
    bn = f"ORG-{seg}.{S}"; e = bpy.data.objects.new(f"sock_{seg}.{S}", None); bpy.context.scene.collection.objects.link(e)
    R = rest_world(bn).copy()
    if pivot is not None: R.translation = pivot
    if parent is None: parent_to_bone(e, "ORG-spine.003")
    else: e.parent = parent; e.matrix_parent_inverse = srest[parent.name].inverted()
    e.matrix_basis = R; srest[e.name] = R
    c = e.constraints.new("COPY_ROTATION"); c.target = rig; c.subtarget = bn
    return e
if PIN:
    for S in "LR":
        wc = ring_center(next(c for c in cuts if c["name"] == f"wrist.{S}")); info["wrist_pivot_" + S] = list(wc)
        u = sock(S, "upper_arm", None); f_ = sock(S, "forearm", u); h_ = sock(S, "hand", f_, wc)
        socks.update({f"upper_arm.{S}": u, f"forearm.{S}": f_, f"hand.{S}": h_})
for pi, pn in enumerate(names):
    pb = bm.copy(); pb.faces.ensure_lookup_table()
    bmesh.ops.delete(pb, geom=[pb.faces[i] for i in range(len(pb.faces)) if owner[i] != pi], context="FACES")
    pb.verts.ensure_lookup_table(); uvp = pb.loops.layers.uv.active
    caps = 0; mine = [c for c in cuts if pn in (c["child"], c["parent"])]
    for cut in mine:
        E = [e for e in pb.edges if e.is_boundary and on_cut(e.verts[0], cut) and on_cut(e.verts[1], cut)]
        if not E: continue
        want = -cut["no"] if pn == cut["child"] else cut["no"]
        r = bmesh.ops.triangle_fill(pb, use_beauty=True, use_dissolve=False, edges=E, normal=want)
        nf = [g for g in r["geom"] if isinstance(g, bmesh.types.BMFace)]
        flip = [g for g in nf if g.normal.dot(want) < 0]
        if flip: bmesh.ops.reverse_faces(pb, faces=flip)
        for g in nf:
            for l in g.loops:
                ring = [x for x in l.vert.link_loops if x.face not in nf]
                if ring: l[uvp].uv = ring[0][uvp].uv
        caps += len(nf)
    # loops left open on a cut plane (a TRELLIS shell cut open, its loop not closed on the plane): fill them as holes
    def near_cut(v): return any(abs((v.co - c["co"]).dot(c["no"])) < 0.004 and bool(region(c, [v.co])[0]) for c in mine)
    E = [e for e in pb.edges if e.is_boundary and near_cut(e.verts[0]) and near_cut(e.verts[1])]
    if E:
        nf = bmesh.ops.holes_fill(pb, edges=E, sides=0)["faces"]; caps += len(nf)
        for g in nf:
            for l in g.loops:
                ring = [x for x in l.vert.link_loops if x.face not in nf]
                if ring: l[uvp].uv = ring[0][uvp].uv
    open_e = sum(1 for e in pb.edges if e.is_boundary)
    m = bpy.data.meshes.new("part_" + pn); pb.to_mesh(m); pb.free()
    for mt in mat_src: m.materials.append(mt)
    ob = bpy.data.objects.new("part_" + pn, m); bpy.context.scene.collection.objects.link(ob)
    if pn in socks: ob.parent = socks[pn]; ob.matrix_parent_inverse = srest[socks[pn].name].inverted()
    else: parent_to_bone(ob, bone[pn])
    info["parts"][pn] = {"bone": bone[pn], "pinned": pn in socks, "faces": len(m.polygons), "cap_faces": caps, "open_edges_after": open_e}
    print("@@PART@@", pn, info["parts"][pn], flush=True)
bm.free()
body.hide_render = True
if src is not body: src.hide_render = True; src.hide_viewport = True
rig.data.pose_position = "POSE"
for o in bpy.data.objects: o.select_set(False)
bpy.ops.wm.save_as_mainfile(filepath=out_blend, copy=True)
json.dump(info, open(out_json, "w"), indent=1, default=str)
print("@@SPLIT@@ saved", out_blend, flush=True)
