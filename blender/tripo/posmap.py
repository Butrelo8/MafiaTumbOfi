# posmap.py in.glb out.npy [size]  -> (size,size,3) float32 glTF-space position per texel (NaN outside islands)
# Rasterizes each UV triangle filled with its centroid position (fine for region masks, not for exact texels).
import sys, numpy as np, cv2
sys.path.insert(0, '.'); import glbio
src, dst = sys.argv[1], sys.argv[2]
S = int(sys.argv[3]) if len(sys.argv) > 3 else 2048
j, b = glbio.load(src)
prim = j['meshes'][0]['primitives'][0]
def acc(i, comps, dt):
    a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(b, dt, a['count'] * comps, off).reshape(a['count'], comps)
P = acc(prim['attributes']['POSITION'], 3, np.float32)
UV = acc(prim['attributes']['TEXCOORD_0'], 2, np.float32)
I = acc(prim['indices'], 1, np.uint32).reshape(-1, 3)
cen = P[I].mean(1)
px = np.round(UV[I] * S - 0.5).astype(np.int32)  # glTF UV: v down = image row, no flip
out = np.full((S, S, 3), np.nan, np.float32)
# draw in 3 passes into float images via an id map
ids = np.zeros((S, S), np.int32)
for k, tri in enumerate(px):
    cv2.fillConvexPoly(ids, tri, k + 1)
m = ids > 0
out[m] = cen[ids[m] - 1]
np.save(dst, out)
print(dst, 'coverage', round(m.mean(), 3), 'bounds', P.min(0), P.max(0))
