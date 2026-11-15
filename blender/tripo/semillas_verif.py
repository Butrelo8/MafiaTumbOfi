# semillas_verif.py original.glb a.glb b.glb  -> proves the friend's model stays: (a) only seed texels change, the mesh and
# rm map are byte-identical; (b) every original bufferView is byte-identical (only a seed mesh is appended).
import sys, io, numpy as np
from PIL import Image
sys.path.insert(0, '.'); import glbio

(j0, b0), (ja, ba), (jb, bb) = (glbio.load(p) for p in sys.argv[1:4])
img = lambda j, b, i: np.asarray(Image.open(io.BytesIO(glbio.view(j, b, j['images'][i]['bufferView']))).convert('RGB'))
c0, ca, n0, na = img(j0, b0, 0), img(ja, ba, 0), img(j0, b0, 2), img(ja, ba, 2)
mc, mn = np.any(c0 != ca, 2), np.any(n0 != na, 2)
tex = {j0['images'][0]['bufferView'], j0['images'][2]['bufferView']}
same_a = all(glbio.view(j0, b0, i) == glbio.view(ja, ba, i) for i in range(len(j0['bufferViews'])) if i not in tex)
same_b = all(glbio.view(j0, b0, i) == glbio.view(jb, bb, i) for i in range(len(j0['bufferViews'])))
print(f'(a) colour texels changed {mc.sum()} ({mc.mean() * 100:.2f} %), normal texels changed {mn.sum()}, '
      f'normal changed where colour did not {(mn & ~mc).sum()}; mesh + rm identical: {same_a}')
print(f'(b) original bufferViews identical: {same_b}; meshes {len(jb["meshes"])}, seed verts {jb["accessors"][-3]["count"]}')
