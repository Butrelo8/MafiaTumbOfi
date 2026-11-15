# penlib.py: shared pieces of pen_fix.py and body_fix.py (pen.py's inside test, kept as is):
# a vertex is inside a surface when the nearest face has it on its back side (within 6 cm) AND >= 4 of 6 axis rays
# cross the surface an odd number of times (the vote keeps TRELLIS's inner shells from reading as 60 mm hits).
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

TRUNK = {"Hips", "Spine", "Spine1", "Spine2", "Neck", "Head", "LeftUpLeg", "RightUpLeg", "LeftLeg", "RightLeg",
         "LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase"}
DIRS = [Vector(d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]


def dominant(body):
    """Per vertex, the mixamorig bone with the largest weight (no prefix), '' when none."""
    names = {g.index: g.name for g in body.vertex_groups}
    out = []
    for v in body.data.vertices:
        gs = [(g.weight, names[g.group]) for g in v.groups if names[g.group].startswith("mixamorig")]
        out.append(max(gs)[1].split(":")[1] if gs else "")
    return np.array(out)


def body_world(body, dg):
    ev = body.evaluated_get(dg); m = ev.to_mesh(); n = len(m.vertices)
    P = np.empty(n * 3, np.float32); m.vertices.foreach_get("co", P); ev.to_mesh_clear()
    return P.reshape(-1, 3) @ np.array(body.matrix_world.to_3x3()).T + np.array(body.matrix_world.translation)


def prop_world(o, dg):
    oe = o.evaluated_get(dg); mm = oe.to_mesh(); W = o.matrix_world
    V = np.array([(W @ v.co)[:] for v in mm.vertices]); F = [list(p.vertices) for p in mm.polygons]; oe.to_mesh_clear()
    return V, F


def enclosed(tree, p):
    odd = 0
    for d in DIRS:
        c, q = 0, p + d * 1e-5
        while c < 50:
            hit = tree.ray_cast(q, d, 2.0)
            if hit[0] is None: break
            c += 1; q = hit[0] + d * 1e-5
        odd += c % 2
    return odd >= 4


def inside(tree, P, normals=False):
    """Depth (m) of each point of P inside tree's surface, 0 outside; with normals, also the outward normal at the nearest point."""
    d = np.zeros(len(P)); N = np.zeros((len(P), 3))
    for k, p in enumerate(P):
        p = Vector(p); loc, n, i, dist = tree.find_nearest(p, 0.06)
        if loc is not None and (p - loc).dot(n) < 0 and enclosed(tree, p): d[k] = dist; N[k] = n[:]
    return (d, N) if normals else d


DIR26 = [Vector(d).normalized() for d in __import__("itertools").product((-1, 0, 1), repeat=3) if any(d)]


def outer(tree, p):
    """For a point the 6-ray test calls inside: the shortest of 26 rays to its LAST crossing (the outer skin, past any
    inner shell) as (depth along that face's normal, outward normal). The nearest-face distance of inside() saturates
    near the TRELLIS shell spacing (~6 mm: a hand 14 mm deep still reads 5.8 mm), so the fix solves on this one."""
    p = Vector(p); best = None
    for dv in DIR26:
        q, last, c = p + dv * 1e-5, None, 0
        while c < 60:
            h = tree.ray_cast(q, dv, 2.0)
            if h[0] is None: break
            c += 1; last = h; q = h[0] + dv * 1e-5
        if last is None: continue
        n = last[1] if last[1].dot(dv) > 0 else -last[1]; dep = (last[0] - p).dot(n)
        if best is None or dep < best[0]: best = (dep, n)
    return best if best else (0.0, Vector((0, 0, 1)))


def inside_outer(tree, P):
    """inside() with the outer-skin depth and normal (outer()) for the inside points."""
    d = inside(tree, P); D = np.zeros(len(P)); N = np.zeros((len(P), 3))
    for k in np.flatnonzero(d > 0):
        dep, n = outer(tree, P[k]); D[k] = max(dep, d[k]); N[k] = n[:]
    return d, D, N


def exit_along(tree, p, n):
    """Distance from p along n to the last surface crossing (how far p must move along n to be outside), 0 if no hit."""
    from mathutils import Vector as V_
    q, last, c, p = V_(p) + V_(n) * 1e-5, None, 0, V_(p)
    while c < 60:
        h = tree.ray_cast(q, V_(n), 2.0)
        if h[0] is None: break
        c += 1; last = (h[0] - p).length; q = h[0] + V_(n) * 1e-5
    return last or 0.0


def arm_push(tree, P, N, s, tail, margin):
    """One push per hand: along the mean outer-skin normal of its inside vertices, by the largest exit distance along it
    plus margin, made by a shoulder rotation w (no twist: only the part of the push across the arm). Returns w, the push."""
    n = N.mean(0); n /= np.linalg.norm(n)
    lam = max(exit_along(tree, p, n) for p in P) + margin; t = lam * n
    r = tail - s; rn = r / np.linalg.norm(r); tp = t - rn * t.dot(rn)
    return np.cross(r, tp) / r.dot(r), t, float(np.linalg.norm(tp) / np.linalg.norm(t))


def near_box(P, V, margin):
    lo, hi = V.min(0) - margin, V.max(0) + margin
    return np.flatnonzero(np.all((P >= lo) & (P <= hi), axis=1))
