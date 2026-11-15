# cusheet.py: closeup_at.py's output as one sheet: a row per (frame, bone), columns three-quarter / side, an optional
# label per row (the contact and its number).
#   uv run -q --with pillow python -I cusheet.py <out.jpg> <closeup dir> <title> [frame:bone=label ...]
import sys, os, re
from PIL import Image, ImageDraw, ImageFont
out, d, title = sys.argv[1:4]; labels = dict(x.split("=", 1) for x in sys.argv[4:])
jobs = sorted({m.groups() for f in os.listdir(d) if (m := re.match(r"pen_f(\d+)_(\w+?)_[qs]\.png", f))})
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
except OSError: font = ImageFont.load_default()
px, L, T = 400, 230, 40; im = Image.new("RGB", (L + 2 * px, T + px * len(jobs)), (24, 24, 24)); g = ImageDraw.Draw(im)
g.text((8, 10), title, fill=(240, 240, 240), font=font)
for i, (f, b) in enumerate(jobs):
    lab = labels.get(f"{int(f)}:{b}", "")
    g.multiline_text((8, T + i * px + 8), f"f{int(f)} {b}\n{lab}".replace("; ", "\n"), fill=(240, 200, 120), font=font)
    for j, v in enumerate("qs"):
        im.paste(Image.open(f"{d}/pen_f{f}_{b}_{v}.png").convert("RGB").resize((px, px), Image.LANCZOS), (L + j * px, T + i * px))
im.save(out, quality=88); print(out, im.size)
