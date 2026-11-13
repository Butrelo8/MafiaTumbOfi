# patch.py in.glb out.glb rough_median|none metal:zero|jewel|keep [maxarea]
import sys, io, numpy as np, cv2
sys.path.insert(0, '.'); import glbio
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
src, dst, rough, metal = sys.argv[1:5]
maxarea = int(sys.argv[5]) if len(sys.argv) > 5 else 6000
j, b = glbio.load(src)
mat = j['materials'][0]['pbrMetallicRoughness']
rmi = j['textures'][mat['metallicRoughnessTexture']['index']]['source']
bvi = j['images'][rmi]['bufferView']
a = np.asarray(Image.open(io.BytesIO(glbio.view(j, b, bvi))).convert('RGB')).astype(np.float32) / 255
g, B = a[..., 1], a[..., 2]
if rough != 'none':
    t = float(rough); med = np.median(g)
    g = np.clip(t + (g - med) * (1 - t) / (1 - med) if t > med else g, 0, 1)  # affine: keeps 1.0 at 1.0, moves median to t
if metal == 'zero':
    B = B * 0
elif metal == 'jewel':
    m = (B > float(sys.argv[6]) if len(sys.argv) > 6 else B > 0.6).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    keep = np.zeros(n, bool); keep[1:] = st[1:, cv2.CC_STAT_AREA] < maxarea
    mask = cv2.dilate(keep[lab].astype(np.uint8), np.ones((5, 5), np.uint8))
    B = np.where(mask > 0, B, 0)
out = np.stack([a[..., 0], g, B], -1)
buf = io.BytesIO(); Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(buf, 'JPEG', quality=95, subsampling=0)
views = [glbio.view(j, b, i) for i in range(len(j['bufferViews']))]
views[bvi] = buf.getvalue()
glbio.save(dst, j, views)
print(dst, 'rough median', round(float(np.median(a[...,1])),3), '->', round(float(np.median(g)),3), 'metal>0.5 frac', round(float((a[...,2]>0.5).mean()),4), '->', round(float((B>0.5).mean()),4))
