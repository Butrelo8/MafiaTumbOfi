# pen_diag2.py: are pen.py's inside hand vertices really inside? For each one (6-ray test), 26 rays: how many escape the
# trunk without any hit (an enclosed point has none), and the shortest distance to the LAST crossing along a ray (the
# outer skin, whatever inner shells lie between). Prints a histogram.
#   $B -b <blend> --python pen_diag2.py -- <frame> <side>
import bpy, sys, os, itertools
sys.path.append(os.path.dirname(__file__))
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from penlib import TRUNK, dominant, body_world, inside
a = sys.argv[sys.argv.index("--") + 1:]; f = int(a[0]); S = a[1]
sc = bpy.context.scene; body = bpy.data.objects["Body"]
dom = dominant(body); istrunk = np.isin(dom, list(TRUNK))
tp = [list(p.vertices) for p in body.data.polygons if all(istrunk[i] for i in p.vertices)]
idx = np.flatnonzero(np.char.startswith(dom, S + "Hand") | (dom == S + "ForeArm"))
DIR = [Vector(d).normalized() for d in itertools.product((-1, 0, 1), repeat=3) if any(d)]
sc.frame_set(f); P = body_world(body, bpy.context.evaluated_depsgraph_get())
tree = BVHTree.FromPolygons(P.tolist(), tp, all_triangles=False); d = inside(tree, P[idx]); sel = np.flatnonzero(d > 0)
esc, outer, hits = [], [], []
for k in sel:
    p = Vector(P[idx][k]); e = 0; best = 9.0; hs = []
    for dv in DIR:
        q, last, c = p + dv * 1e-5, None, 0
        while c < 60:
            h = tree.ray_cast(q, dv, 2.0)
            if h[0] is None: break
            c += 1; last = (h[0] - p).length; q = h[0] + dv * 1e-5
        if c == 0: e += 1
        else: best = min(best, last)
        hs.append(c)
    esc.append(e); outer.append(best); hits.append(np.median(hs))
esc = np.array(esc); outer = np.array(outer) * 1000
print("@@D2@@", dict(n_inside_6ray=len(sel), depth6_max=round(float(d.max()) * 1000, 2),
                     escaping_dirs_hist={int(x): int((esc == x).sum()) for x in np.unique(esc)},
                     truly_enclosed=int((esc == 0).sum()), outer_depth_mm_enclosed_max=round(float(outer[esc == 0].max()), 2) if (esc == 0).any() else 0,
                     median_crossings=float(np.median(hits))), flush=True)
