# rerig_bones.py <front.png> <heads.json> <out.png> [label]: a rig's rest DEF bones (rig_heads.py dump) drawn on
# export_rerig.py's orthographic front view (1024 x 1280, 1.1 m frame centred on z 0.5), joints as dots.
import sys, json
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert("RGB"); H = json.load(open(sys.argv[2])); d = ImageDraw.Draw(im)
K = 1280 / 1.1; px = lambda p: (512 + p[0] * K, 640 - (p[2] - 0.5) * K)
LIMB = ("DEF-upper_arm", "DEF-forearm", "DEF-hand", "DEF-thigh", "DEF-shin", "DEF-foot", "DEF-spine", "DEF-shoulder")
for n, (h, t) in H.items():
    if not n.startswith(LIMB): continue
    d.line((*px(h), *px(t)), fill=(255, 210, 40), width=5)
for n, (h, t) in H.items():
    if n.startswith(LIMB) and not n.endswith(".001"):
        x, y = px(h); d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(255, 60, 60), outline=(0, 0, 0), width=2)
if len(sys.argv) > 4: d.text((16, 16), sys.argv[4], fill=(255, 255, 255), font=ImageFont.load_default(size=36))
im.save(sys.argv[3])
