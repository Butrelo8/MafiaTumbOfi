# pen_fix.py: the strict version of pen.py for the clip fixes (pen.py stays as it was for the dance). Per frame:
#   hand / forearm -> body (trunk, head and legs; arms excluded, as pen.py);
#   hand / forearm / upper arm / trunk -> each prop_* (only the vertices within 6 cm of the prop's box);
#   each prop_*'s vertices -> the whole body (all faces, so the head, hands and arms count);
#   grips (hand:prop pairs): the smallest hand-to-prop surface gap, negative = the deepest vertex inside.
# Inside = penlib.inside (pen.py's normal test + 6-ray vote). Two depths: pen.py's (distance to the nearest face) and, for
# targets on the TRELLIS body, the outer-skin depth (penlib.outer; the nearest-face one saturates near 6 mm on its shells). Props must be dense (a bare box has only 8 vertices).
#   $B -b <blend> --python pen_fix.py -- <out.json (Windows)> [step] [grips: LeftHand:prop_wheel,...] [f0-f1]
import bpy, sys, os, json
sys.path.append(os.path.dirname(__file__))
import numpy as np
from mathutils.bvhtree import BVHTree
from penlib import TRUNK, dominant, body_world, prop_world, inside, inside_outer, near_box
a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]; step = int(a[1]) if len(a) > 1 else 1
grips = [g.split(":") for g in a[2].split(",")] if len(a) > 2 and a[2] else []
sc = bpy.context.scene; body = bpy.data.objects["Body"]; me = body.data
dom = dominant(body); istrunk = np.isin(dom, list(TRUNK))
polys = [list(p.vertices) for p in me.polygons]
tpolys = [p for p in polys if all(istrunk[i] for i in p)]
SETS = {"Trunk": np.flatnonzero(istrunk)}
for S in ("Left", "Right"):
    SETS[S + "Hand"] = np.flatnonzero(np.char.startswith(dom, S + "Hand"))
    SETS[S + "ForeArm"] = np.flatnonzero(dom == S + "ForeArm")
    SETS[S + "Arm"] = np.flatnonzero(dom == S + "Arm")
props = [o for o in sc.objects if o.type == "MESH" and o.name.startswith("prop_")]
mx = bpy.data.objects["mx"]; ad = mx.animation_data
f0, f1 = map(int, a[3].split("-")) if len(a) > 3 else (map(int, ad.action.frame_range) if ad and ad.action else (sc.frame_start, sc.frame_end))
frames = list(range(f0, f1 + 1, step))
res = {}
def put(key, f, d, D=None):
    r = res.setdefault(key, {"depth_mm": [], "outer_mm": [], "n_in": []}); r["depth_mm"].append(round(float(d.max()) * 1000 if len(d) else 0.0, 2))
    r["outer_mm"].append(round(float(D.max()) * 1000 if D is not None and len(D) else r["depth_mm"][-1], 2)); r["n_in"].append(int((d > 0).sum()))
for f in frames:
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); P = body_world(body, dg)
    trunk = BVHTree.FromPolygons(P.tolist(), tpolys, all_triangles=False)
    full = BVHTree.FromPolygons(P.tolist(), polys, all_triangles=False)
    for s in ("LeftHand", "RightHand", "LeftForeArm", "RightForeArm"): d, D, _ = inside_outer(trunk, P[SETS[s]]); put(f"{s}>body", f, d, D)
    for o in props:
        V, F = prop_world(o, dg); tr = BVHTree.FromPolygons(V.tolist(), F)
        for s, idx in SETS.items():
            near = idx[near_box(P[idx], V, 0.06)]; put(f"{s}>{o.name}", f, inside(tr, P[near]))
        d, D, _ = inside_outer(full, V); put(f"{o.name}>body", f, d, D)
        for s, pn in grips:
            if pn != o.name: continue
            idx = SETS[s]; near = idx[near_box(P[idx], V, 0.1)]
            gap = min((tr.find_nearest(p, 0.1)[3] or 0.1) for p in P[near].tolist()) if len(near) else 0.1
            dmax = res[f"{s}>{o.name}"]["depth_mm"][-1]
            res.setdefault(f"grip {s}>{o.name}", {"gap_mm": []})["gap_mm"].append(round(-dmax if dmax > 0 else gap * 1000, 2))
summary = {"range": [f0, f1], "step": step, "frames": frames, "sets": {k: len(v) for k, v in SETS.items()}, "pen": {}}
for k, r in res.items():
    if "gap_mm" in r:
        g = np.array(r["gap_mm"]); summary["pen"][k] = dict(gap_min=float(g.min()), gap_max=float(g.max()), frame_gap_max=frames[int(g.argmax())],
                                                         n_gap_over_3=int((g > 3).sum()), gap_mm=r["gap_mm"])
        continue
    d = np.array(r["depth_mm"]); D = np.array(r["outer_mm"]); n = np.array(r["n_in"])
    summary["pen"][k] = dict(max_mm=float(d.max()), max_frame=frames[int(d.argmax())], max_outer_mm=float(D.max()), max_outer_frame=frames[int(D.argmax())],
                             n_frames_over_1mm=int((np.maximum(d, D) > 1).sum()), n_frames_any_inside=int((n > 0).sum()), depth_mm=r["depth_mm"], outer_mm=r["outer_mm"])
json.dump(summary, open(out, "w"))
print("@@PENFIX@@" + json.dumps({k: {x: y for x, y in v.items() if not x.endswith("_mm") or x.startswith("max")} for k, v in summary["pen"].items() if v.get("max_mm", 1) > 0 or "gap_min" in v}), flush=True)
