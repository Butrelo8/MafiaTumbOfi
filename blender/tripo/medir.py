# medir.py : before (B0_) vs after (A_) numbers per figure
import sys, io, json, numpy as np
sys.path.insert(0, '.'); import glbio
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
views = ["front", "right", "back", "left"]
print("figure     metal_px_p99.9 before->after  metal_px_max before->after  rough_tex_median before->after  metal_tex>0.5 before->after  missing_images")
for n in ["manager", "hector", "diego", "alejandro"]:
    def px(pre):
        a = np.concatenate([np.asarray(Image.open(f"r/{pre}{n}_metal_{v}.png").convert("L")).ravel() / 255 for v in views])
        return np.percentile(a, 99.9), a.max()
    def tex(path):
        j, b = glbio.load(path)
        i = j['textures'][j['materials'][0]['pbrMetallicRoughness']['metallicRoughnessTexture']['index']]['source']
        a = np.asarray(Image.open(io.BytesIO(glbio.view(j, b, j['images'][i]['bufferView']))).convert('RGB')) / 255
        return np.median(a[..., 1]), (a[..., 2] > 0.5).mean()
    b9, bm = px("B0_"); a9, am = px("A_")
    br, bf = tex(f"{n}.glb"); ar, af = tex(f"fin/{n}.glb")
    miss = json.loads(open(f"r/A_{n}_lit.info").read().split("INFO ", 1)[1])["missing_images"]
    print(f"{n:10} {b9:.2f} -> {a9:.2f}                 {bm:.2f} -> {am:.2f}                {br:.3f} -> {ar:.3f}                 {bf:.4f} -> {af:.4f}             {miss}")
