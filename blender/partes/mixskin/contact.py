# contact.py: a clip's contact sheet from clip_stills.py output: one column per frame, rows front / three-quarter.
#   contact.py <out.jpg> <stills dir> <title> [tile px]
import sys, os, re
from PIL import Image, ImageDraw, ImageFont
out, d, title = sys.argv[1:4]; px = int(sys.argv[4]) if len(sys.argv) > 4 else 300
fr = sorted({int(re.search(r"_f(\d+)", f).group(1)) for f in os.listdir(d) if f.endswith(".png")})
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
except OSError: font = ImageFont.load_default()
T, L = 58, 110; im = Image.new("RGB", (L + px * len(fr), T + 2 * px), (24, 24, 24)); g = ImageDraw.Draw(im)
g.text((8, 6), title, fill=(240, 240, 240), font=font)
for j, f in enumerate(fr):
    g.text((L + j * px + 8, 32), f"f{f}", fill=(240, 200, 120), font=font)
    for i, v in enumerate(("front", "q")):
        im.paste(Image.open(f"{d}/{v}_f{f:04d}.png").convert("RGB").resize((px, px), Image.LANCZOS), (L + j * px, T + i * px))
for i, v in enumerate(("front", "3/4")): g.text((8, T + i * px + 8), v, fill=(240, 200, 120), font=font)
im.save(out, quality=88); print(out, im.size)
