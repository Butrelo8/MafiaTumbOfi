# cover_normals.py: shade each joint cover as a continuation of the parts it bridges (the faint lighter line where the
# flat-shaded hull wedge met the curved trouser under Workbench cavity, eagle 11-14). TRELLIS.2's trouser and shirt
# albedo is (0, 0, 0), the same as the covers' flat colour, so that line is shading, not texels: each cover corner takes
# the smooth normal at the nearest point of its parent or child part (cap faces excluded, vertex normals interpolated
# inside that triangle) as a custom split normal. Sampled at a mid-clip frame, since the joints sit 24-57 deg from rest.
#   $B -b <covers.blend> --python cover_normals.py -- <split.json> <out.blend (Windows)> [frame, default 60] [skip, default none]
import bpy, sys, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]
cuts = json.load(open(a[0]))["cuts"]; out = a[1]; FR = int(a[2]) if len(a) > 2 else 60
SKIP = (a[3] if len(a) > 3 else "").split(",")
sc = bpy.context.scene; sc.frame_set(FR); bpy.context.view_layer.update()
parts = {o.name[5:]: o for o in bpy.data.objects if o.name.startswith("part_")}
src = {}
def source(o):   # world-space BVH of o's non-cap triangles at this frame (rigid parts: matrix_world @ mesh)
    if o.name in src: return src[o.name]
    me = o.data; me.calc_loop_triangles(); M = o.matrix_world; R = M.to_3x3()
    V = [M @ v.co for v in me.vertices]; N = [(R @ v.normal).normalized() for v in me.vertices]
    tris = [tuple(t.vertices) for t in me.loop_triangles
            if not o.material_slots[me.polygons[t.polygon_index].material_index].material.name.startswith("flat_")]
    src[o.name] = (BVHTree.FromPolygons(V, tris), tris, V, N); return src[o.name]
def normal_at(bvhs, p):
    best = None
    for b in bvhs:
        loc, _, i, d = b[0].find_nearest(p)
        if loc is not None and (best is None or d < best[0]): best = (d, b, i, loc)
    _, (bv, tris, V, N), i, loc = best
    A, B, C = (V[k] for k in tris[i]); v0, v1, v2 = B - A, C - A, loc - A
    d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01 or 1e-12; w1 = (d11 * d20 - d01 * d21) / den; w2 = (d00 * d21 - d01 * d20) / den
    return (N[tris[i][0]] * (1 - w1 - w2) + N[tris[i][1]] * w1 + N[tris[i][2]] * w2).normalized(), best[0]
info = {}
for cv in [o for o in bpy.data.objects if o.name.startswith("cover_")]:
    cn = cv.name[6:]
    if cn.split(".")[0] in SKIP: continue
    bvhs = [source(parts[cuts[cn]["parent"]]), source(parts[cuts[cn]["child"]])]
    me = cv.data; M = cv.matrix_world; Ri = M.to_3x3().inverted()
    for p in me.polygons: p.use_smooth = True
    vn, dist = [], []
    for v in me.vertices:
        n, d = normal_at(bvhs, M @ v.co); vn.append((Ri @ n).normalized()); dist.append(d)
    me.normals_split_custom_set_from_vertices(vn)
    info[cn] = dict(verts=len(vn), dist_mm_max=round(max(dist) * 1000, 1))
    print("@@NORMALS@@", cn, info[cn], flush=True)
bpy.ops.wm.save_as_mainfile(filepath=out)
print("@@COVERNORMALS@@", FR, len(info), out, flush=True)
