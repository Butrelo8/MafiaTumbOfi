# semillas_hoja.py <render dir> <out.png> <n seeds>
# One sheet for the owner: original | (a) painted | (b) geometry; rows = studio whole berry, studio macro (both at the
# scene's 4.1 cm scale, estudio.py), the in-scene close-up pp-fresa and the scene still pp1-b (props_placement.py), the
# scene rows as 100 % crops centred on the berry (found where the variants differ from the original).
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont

D, OUT, N = sys.argv[1], sys.argv[2], sys.argv[3]
V = [("strawberry", "original (friend's model)"), ("strawberry-a-pintada", "(a) painted: base colour + normal bump"),
     ("strawberry-b-semillas", f"(b) geometry: {N} seed meshes in the pits")]
F = lambda s, b=False: ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if b else ''}.ttf", s)
CW = 560


def centro(nombre):
    """Berry centre in a scene still: the pixels where (a) or (b) differ from the original."""
    a = [np.asarray(Image.open(f"{D}/{k}/{nombre}.png").convert("RGB")).astype(int) for k, _ in V]
    d = (np.abs(a[1] - a[0]).sum(2) > 12) | (np.abs(a[2] - a[0]).sum(2) > 12)
    ys, xs = np.nonzero(d)
    if not len(xs):
        raise SystemExit(f"{nombre}: variants identical to the original, the swap did not load")
    return int(np.median(xs)), int(np.median(ys)), int(d.sum())


filas = []
for v, rot in (("entera", "studio, whole berry (scaled to the scene's 4.1 cm)"), ("macro", "studio macro, 1.6 cm window")):
    filas.append((rot, [Image.open(f"{D}/est/{k}_{v}.png").convert("RGB").resize((CW, CW), Image.LANCZOS) for k, _ in V]))
for nombre, lado, rot in (("pp-fresa", CW, "in the cab: pp-fresa close-up, 100 % crop"),
                          ("pp1-b", 200, "in the scene: pp1-b (scene 1 camera), 100 % crop, then 2.8x nearest")):
    cx, cy, npx = centro(nombre)
    ims = []
    for k, _ in V:
        im = Image.open(f"{D}/{k}/{nombre}.png").convert("RGB")
        h = lado // 2
        c = im.crop((cx - h, cy - h, cx + h, cy + h))
        ims.append(c if lado == CW else c.resize((CW, CW), Image.NEAREST))
    filas.append((rot + f"  (berry at {cx},{cy} of {im.size[0]}x{im.size[1]}; {npx} px differ)", ims))

M, TOP, LAB = 20, 158, 34
W = M + 3 * (CW + M)
H = TOP + len(filas) * (LAB + CW + M)
hoja = Image.new("RGB", (W, H), (24, 24, 26))
d = ImageDraw.Draw(hoja)
d.text((M, 16), "MTO strawberry: yellow seeds on the friend's model. Pick (a) or (b)", fill=(240, 240, 240), font=F(30, True))
d.text((M, 56), "Reference: a real garden strawberry. Kept: seeds in the model's own pits, even spacing, sparser under the calyx, "
                "~1 mm achenes.", fill=(200, 200, 200), font=F(17))
d.text((M, 78), "Changed on purpose: pure yellow (the owner's ask) instead of the real yellow-green to brown.",
       fill=(200, 200, 200), font=F(17))
d.text((M, 100), f"{N} seeds, one list for both variants. The friend's shape and colour are unchanged: (a) touches only the seed "
                f"texels, (b) appends a seed mesh.", fill=(200, 200, 200), font=F(17))
for i, (_, t) in enumerate(V):
    d.text((M + i * (CW + M), 124), t, fill=(255, 214, 90) if i else (230, 230, 230), font=F(20, True))
y = TOP
for rot, ims in filas:
    d.text((M, y + 6), rot, fill=(180, 180, 185), font=F(18))
    y += LAB
    for i, im in enumerate(ims):
        hoja.paste(im, (M + i * (CW + M), y))
    y += CW + M
hoja.save(OUT)
print(OUT, hoja.size)
