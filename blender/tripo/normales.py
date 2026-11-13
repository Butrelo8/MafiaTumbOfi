# normales.py in.glb out.glb pos_<name>.npy [thr=0.12] [ymin=0.62] [zmax=0.02]
# Removes Tripo's bake lines from the normal map: texels in the back of the head (glTF y > ymin, z < zmax, from the
# posmap) whose normal differs from their 15-px median by more than thr are inpainted. Only the normal image's
# bytes change (rewritten as PNG); the mesh and the other images are untouched, as in patch.py.
import sys, io, numpy as np, cv2
sys.path.insert(0, '.'); import glbio
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
src, dst, posp = sys.argv[1], sys.argv[2], sys.argv[3]
thr, ymin, zmax = (float(a) for a in (sys.argv[4:] + ['0.12', '0.62', '0.02'])[:3])
j, b = glbio.load(src)
ni = j['textures'][j['materials'][0]['normalTexture']['index']]['source']
bvi = j['images'][ni]['bufferView']
nm = np.asarray(Image.open(io.BytesIO(glbio.view(j, b, bvi))).convert('RGB'))
N = nm.shape[0]
pos = cv2.resize(np.load(posp), (N, N), interpolation=cv2.INTER_NEAREST)
ok = ~np.isnan(pos[..., 0])
zona = ok & (np.nan_to_num(pos[..., 1]) > ymin) & (np.nan_to_num(pos[..., 2]) < zmax)
zona = cv2.erode(zona.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0  # keep off island borders
med = cv2.medianBlur(nm, 15)
dev = np.linalg.norm(nm.astype(np.float32) - med.astype(np.float32), axis=2) / 255
lineas = zona & (dev > thr)
lineas = cv2.dilate(lineas.astype(np.uint8), np.ones((3, 3), np.uint8)) & zona.astype(np.uint8)
out = cv2.inpaint(nm, lineas, 3, cv2.INPAINT_TELEA)
print(f'zone {int(zona.sum())} texels, lines {int(lineas.sum())} texels ({lineas.sum() / max(zona.sum(), 1):.2%})')
buf = io.BytesIO(); Image.fromarray(out).save(buf, 'PNG')
j['images'][ni]['mimeType'] = 'image/png'
views = [glbio.view(j, b, i) for i in range(len(j['bufferViews']))]
views[bvi] = buf.getvalue()
glbio.save(dst, j, views)
cv2.imwrite(dst + '.lineas.png', cv2.resize(np.where(lineas[..., None] > 0, (0, 0, 255), nm[..., ::-1] // 3).astype(np.uint8), (1024, 1024)))
