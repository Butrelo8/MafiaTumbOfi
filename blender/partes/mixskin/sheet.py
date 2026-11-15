# sheet.py: labelled grid. sheet.py <out.jpg> <tile px> <col1_label=dir> ... -- <row tile names (no .png)> ...
# A tile missing in a column is left dark grey.
import sys
from PIL import Image, ImageDraw, ImageFont
a = sys.argv[1:]; out, px = a[0], int(a[1]); k = a.index("--"); cols = [c.split("=", 1) for c in a[2:k]]; rows = a[k + 1:]
L, T = 170, 34
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
except OSError: font = ImageFont.load_default()
im = Image.new("RGB", (L + px * len(cols), T + px * len(rows)), (24, 24, 24)); d = ImageDraw.Draw(im)
for j, (lab, _) in enumerate(cols): d.text((L + j * px + 8, 8), lab, fill=(240, 240, 240), font=font)
for i, r in enumerate(rows):
    d.text((8, T + i * px + 8), r.replace("_f", "\nf"), fill=(240, 200, 120), font=font)
    for j, (_, dr) in enumerate(cols):
        try: t = Image.open(f"{dr}/{r}.png").convert("RGB").resize((px, px), Image.LANCZOS); im.paste(t, (L + j * px, T + i * px))
        except FileNotFoundError: d.rectangle([L + j * px, T + i * px, L + (j + 1) * px - 1, T + (i + 1) * px - 1], fill=(60, 60, 60))
im.save(out, quality=88); print(out, im.size)
