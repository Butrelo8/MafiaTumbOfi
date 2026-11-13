# repaint.py <name> in.glb out.glb ops...   ops: cap | eyes | hands
# Edits the base-colour texture only, in texture space, using pos_<name>.npy (UV -> 3D, glTF axes: y up, +z front).
import sys, io, numpy as np, cv2
sys.path.insert(0, '.'); import glbio
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
name, src, dst, ops = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
j, b = glbio.load(src)
bci = j['textures'][j['materials'][0]['pbrMetallicRoughness']['baseColorTexture']['index']]['source']
bvi = j['images'][bci]['bufferView']
img = np.asarray(Image.open(io.BytesIO(glbio.view(j, b, bvi))).convert('RGB')).astype(np.float32) / 255
N = img.shape[0]
pos = np.load(f'pos_{name}.npy')
pos = cv2.resize(pos, (N, N), interpolation=cv2.INTER_NEAREST)
ok = ~np.isnan(pos[..., 0]); x, y, z = (np.nan_to_num(pos[..., i]) for i in range(3))
hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)  # H 0..360, S 0..1, V 0..1
H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
skin = ok & (H > 8) & (H < 40) & (S > 0.25) & (V > 0.5)
total = np.zeros((N, N), bool)

def paint(mask, ref_mask, label):
    global total
    col = np.median(img[ref_mask], 0)
    m = cv2.dilate(mask.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    soft = cv2.GaussianBlur(m.astype(np.float32), (15, 15), 0)[..., None]
    img[:] = img * (1 - soft) + col * soft
    total |= m
    print(f'{name} {label}: {int(mask.sum())} texels -> rgb {np.round(col * 255).astype(int).tolist()}')

xmax = np.abs(x[ok]).max()
if 'cap' in ops:  # navy smear on the crown above the brim line (brim and its band sit at y < 0.9)
    blue = ok & (img[..., 2] - img[..., 0] > 0.025) & (y > 0.9)
    paint(blue, ok & (y > 0.9) & (V > 0.7) & (S < 0.1), 'cap crown navy -> cap white')
if 'eyes' in ops:  # whitish wash over the lids: half white, half skin (saturation between sclera and skin)
    band = ok & (z > 0.0) & (y > 0.72) & (y < 0.815) & (np.abs(x) < 0.17)
    wash = band & (S > 0.08) & (S < 0.3) & (V > 0.6)
    paint(wash, band & skin, 'eye wash -> skin')
if 'hands' in ops:  # grey fringe on the outer arms and hands, only next to skin
    arm = ok & (np.abs(x) > 0.55 * xmax)
    near_skin = cv2.dilate((skin & arm).astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    fringe = arm & near_skin & (S < 0.15) & (V > 0.45) & (V < 0.92)
    paint(fringe, skin & arm, 'hand/arm grey fringe -> skin')

buf = io.BytesIO(); Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(buf, 'JPEG', quality=95, subsampling=0)
views = [glbio.view(j, b, i) for i in range(len(j['bufferViews']))]
views[bvi] = buf.getvalue()
glbio.save(dst, j, views)
Image.fromarray((total * 255).astype(np.uint8)).resize((1024, 1024)).save(f'mask_{name}.png')
