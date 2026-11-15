# markers_draw.py <front.png> <markers.json> <out.png>: Mixamo marker guide over export_mx.py's front view
# (1024 x 1280, ortho 1.1 m tall, centred at z 0.5). Diego faces the camera, so his left is on the screen's right.
import sys, json
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert("RGB"); mk = json.load(open(sys.argv[2])); d = ImageDraw.Draw(im)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
px = lambda x, z: (512 + x / 1.1 * 1280, 640 - (z - 0.5) / 1.1 * 1280)
for k, (x, z) in mk.items():
    if k.startswith("ankle"): continue
    u, v = px(x, z); d.ellipse((u - 9, v - 9, u + 9, v + 9), outline=(0, 230, 0), width=4)
    d.text((u + 12, v - 12), "%s (%d, %d)" % (k, u, v), fill=(255, 255, 0), font=f, stroke_width=2, stroke_fill=(0, 0, 0))
im.save(sys.argv[3]); print({k: tuple(int(t) for t in px(*v)) for k, v in mk.items()})
