# assemble.py -- <fit dir> <assets dir> <head name> <hand name> <out.blend> [cut_z]: the skin Mixamo rigs, from parts.
# Every joint (neck, both wrists) is joined the same way, about a joint axis a through a centre c0:
#   - the body keeps a column that runs IN past the cut, clamped to its ring - 1 mm and tapered 4 mm further in,
#     so it stays hidden inside the part;
#   - the part loses everything below the cut, its lowest BAND is pulled, angle by angle, onto the body's ring at the
#     cut + 0.5 mm (only where the part is within REACH of that ring: a chin or a skull base stays where it is); the
#     part is bisected on the cut plane first, so its rim is a clean line that lands on the ring.
#   neck : a = +Z through the body's neck centre, cut at CUT (just under the chin); head = <head>.glb by <head>.json.
#   wrist: a = the forearm axis through the wrist ring (hand.json); hand = <hand>.glb, mirrored for the left, placed by
#          hand.json (hand_fit.py), then slid along a until its palm base (first ring as wide as the forearm's) sits
#          3 mm past the ring; its stub is cut away.
# Joined into one mesh "Diego" (not welded; the seams are overlaps), decimated to the face budget, saved to out.blend.
# Prints @@ lines: vertex/face counts per part and the ring radii at each joint before the snap.
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Matrix, Vector
a = sys.argv[sys.argv.index("--") + 1:]
fit, assets, head_name, hand_name, out = a[:5]
CUT = float(a[5]) if len(a) > 5 else 0.598
NECK = dict(cut=0.0, IN=0.022, BAND=0.010, REACH=0.012, NEAR=2.0)
WRIST = dict(cut=0.003, IN=0.014, BAND=0.010, REACH=0.010, slide=True, NEAR=0.25)
BUDGET = {"body": 140000, "head": 100000, "hand": 30000}
bpy.ops.wm.read_factory_settings(use_empty=True)


def load(name, T=None):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(assets, name + ".glb"))
    ms = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    for o in bpy.data.objects:
        if o not in before and o.type != "MESH": bpy.data.objects.remove(o, do_unlink=True)
    o = ms[0]; o.name = name
    o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4)   # GLB frame, as fitlib.load_glb
    if T is not None: o.data.transform(Matrix(T))
    return o


def coords(o):
    P = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", P); return P.reshape(-1, 3)


def set_coords(o, P):
    o.data.vertices.foreach_set("co", P.ravel()); o.data.update()


def delete(o, mask):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in np.flatnonzero(mask)], context="VERTS")
    bm.to_mesh(o.data); bm.free()


def decimate(o, faces):
    n = len(o.data.polygons)
    if n > faces:
        m = o.modifiers.new("dec", "DECIMATE"); m.ratio = faces / n
        bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier="dec")
    print("@@", o.name, len(o.data.vertices), "verts", len(o.data.polygons), "faces")


def basis(a):
    e1 = np.cross(a, [0, 1, 0] if abs(a[1]) < 0.9 else [1, 0, 0]); e1 /= np.linalg.norm(e1); return e1, np.cross(a, e1)


def joint(body, part, c0, a, J, name):
    """Join one part onto the body at one joint (see the header). Returns nothing; edits both meshes."""
    e1, e2 = basis(a); loc = lambda P: ((P - c0) @ a, np.arctan2((P - c0) @ e2, (P - c0) @ e1),
                                        np.hypot((P - c0) @ e1, (P - c0) @ e2))
    B = coords(body); sB, thB, rB = loc(B)
    slab = (np.abs(sB - J["cut"]) < 0.003) & (rB < 0.07)
    bins = np.linspace(-math.pi, math.pi, 13); mid = (bins[:-1] + bins[1:]) / 2
    rb = np.array([np.median(rB[m]) if (m := slab & (thB >= bins[k]) & (thB < bins[k + 1])).sum() else np.nan for k in range(12)])
    ok = ~np.isnan(rb); rb = np.interp(mid, mid[ok], rb[ok], period=2 * math.pi)       # an empty bin takes its neighbours
    rb_of = lambda th: np.interp(th, mid, rb, period=2 * math.pi)
    nb = np.linalg.norm(B - c0, axis=1) < J["NEAR"];   # NEAR: how far from c0 a joint may edit the body
    col = nb & (sB > J["cut"] - 0.002) & (sB <= J["cut"] + J["IN"]) & (rB <= rb_of(thB) + 0.003)
    # the column stays inside the part's rim (ring + 0.5 mm): clamp it to the ring - 1 mm, tapering 4 mm further in
    rmax = rb_of(thB[col]) - 0.001 - 0.004 * np.clip((sB[col] - J["cut"]) / J["IN"], 0, 1)
    sc_ = np.minimum(1, rmax / np.maximum(rB[col], 1e-9)); Q = B[col] - c0
    B[col] = c0 + np.outer(sB[col], a) + (Q - np.outer(sB[col], a)) * sc_[:, None]; set_coords(body, B)
    delete(body, nb & (sB > J["cut"] - 0.002) & ~col)
    P = coords(part); s, th, r = loc(P)
    if J.get("slide"):            # slide the part along a so its first ring as wide as the body's (palm base) sits at the cut
        for sc in np.arange(-0.03, 0.06, 0.001):
            m = np.abs(s - sc) < 0.001
            if m.sum() > 10 and np.median(r[m]) >= 0.95 * np.median(rb): break
        P += (J["cut"] - sc) * a; s = s + (J["cut"] - sc)
        print("@@ %s: part slid %.1f mm along the joint axis" % (name, (J["cut"] - sc) * 1000))
    set_coords(part, P)
    bm = bmesh.new(); bm.from_mesh(part.data)        # a clean rim exactly on the cut plane, not a sawtooth of deleted verts
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6,
                           plane_co=Vector(c0 + a * J["cut"]), plane_no=Vector(a), clear_inner=True)
    bm.to_mesh(part.data); bm.free(); part.data.update()
    P = coords(part); s, th, r = loc(P); s = np.maximum(s, J["cut"]); keep = s >= J["cut"]
    r0 = r[s < J["cut"] + 0.002]
    band = keep & (s < J["cut"] + J["BAND"]) & (r < rb_of(th) + J["REACH"])
    w = (1 - (s[band] - J["cut"]) / J["BAND"]) * np.clip(1 - (r[band] - rb_of(th[band])) / J["REACH"], 0, 1)  # fades to 0 at REACH: no step, no flaps
    rn = r[band] + (rb_of(th[band]) + 0.0005 - r[band]) * w
    P[band] = c0 + np.outer(s[band], a) + np.outer(rn * np.cos(th[band]), e1) + np.outer(rn * np.sin(th[band]), e2)
    set_coords(part, P)
    print("@@ %s ring: body r %.1f-%.1f (median %.1f) mm, part rim r before median %.1f mm, %d verts snapped" % (
        name, rb.min() * 1000, rb.max() * 1000, np.median(rb) * 1000, np.median(r0) * 1000, band.sum()))


def drop_inner_wall(o):
    """TRELLIS gave the body two complete walls (welded by position: 39k and 24k vertices, both full height). Both were
    cut at the joints, and the inner one's sawtooth showed as teeth at the wrists and a band at the neck. Keep the
    outer one: the larger median distance from the torso axis at z 0.35-0.55."""
    P = coords(o); _, wid = np.unique(np.round(P / 1e-5).astype(np.int64), axis=0, return_inverse=True); wid = wid.ravel()
    E = np.empty(len(o.data.edges) * 2, np.int64); o.data.edges.foreach_get("vertices", E); E = wid[E.reshape(-1, 2)]
    par = np.arange(wid.max() + 1)
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for p, q in E:
        rp, rq = find(p), find(q)
        if rp != rq: par[rp] = rq
    comp = np.array([find(x) for x in range(len(par))])[wid]; u, cnt = np.unique(comp, return_counts=True)
    two = u[np.argsort(-cnt)[:2]]; H = P[:, 2].max() - P[:, 2].min()
    if any(np.ptp(P[comp == c, 2]) < 0.8 * H for c in two): print("@@ body: no double wall"); return
    band = (P[:, 2] > 0.35) & (P[:, 2] < 0.55); ax = P[band, :2].mean(0)
    rad = [np.median(np.linalg.norm(P[(comp == c) & band, :2] - ax, axis=1)) for c in two]
    inner = two[int(np.argmin(rad))]; delete(o, comp == inner)
    print("@@ body: dropped the inner wall, %d verts (median radius %.1f vs %.1f mm)" % ((comp == inner).sum(), min(rad) * 1000, max(rad) * 1000))


J = lambda n: json.load(open(os.path.join(fit, n + ".json")))
body = load("body", J("body")["T"]); head = load(head_name, J(head_name)["T"]); HJ = J("hand")
drop_inner_wall(body)
B = coords(body); slab = B[(np.abs(B[:, 2] - CUT) < 0.002) & (np.abs(B[:, 0]) < 0.12) & (np.abs(B[:, 1]) < 0.12)]
c0 = np.r_[slab[:, :2].mean(0), CUT]
NECK["cut"] = 0.0; joint(body, head, c0, np.array([0, 0, 1.0]), NECK, "neck")
hands = []
for side in ("right", "left"):
    h = HJ[side]; o = load(hand_name); o.name = "hand_" + side; P = coords(o)
    if h["mirror_x"]:
        P[:, 0] *= -1; o.data.flip_normals()
    T = np.array(h["T"]); set_coords(o, P @ T[:3, :3].T + T[:3, 3]); hands.append(o)
    joint(body, o, np.array(h["wrist"]), np.array(h["axis"]), WRIST, "wrist " + side)
decimate(body, BUDGET["body"]); decimate(head, BUDGET["head"])
for o in hands: decimate(o, BUDGET["hand"])
for o in bpy.data.objects: o.select_set(o.type == "MESH")
bpy.context.view_layer.objects.active = body; bpy.ops.object.join()
body.name = body.data.name = "Diego"
print("@@ Diego", len(body.data.vertices), "verts", len(body.data.polygons), "faces", "dims", tuple(round(x, 4) for x in body.dimensions))
bpy.ops.wm.save_as_mainfile(filepath=out)
