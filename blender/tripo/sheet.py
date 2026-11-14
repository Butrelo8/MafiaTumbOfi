# sheet.py out.png ref.png|- "label=prefix" ...   (prefix -> r/<prefix>_{front,right,back,left}.png)
import sys
from PIL import Image, ImageDraw, ImageFont
out, ref, rows = sys.argv[1], sys.argv[2], sys.argv[3:]
views = ["front", "right", "back", "left"]
H = 500
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
except OSError:
    font = ImageFont.load_default()
tiles = []
for r in rows:
    label, pre = r.split("=", 1)
    ims = [Image.open(f"r/{pre}_{v}.png").convert("RGB") for v in views]
    ims = [im.resize((int(im.width * H / im.height), H)) for im in ims]
    tiles.append((label, ims))
refw = 0
if ref != "-":
    rim = Image.open(ref).convert("RGB")
    rim = rim.resize((int(rim.width * H / rim.height), H)); refw = rim.width
W = refw + sum(im.width for im in tiles[0][1])
sheet = Image.new("RGB", (W, H * len(tiles)), (40, 40, 40))
d = ImageDraw.Draw(sheet)
for i, (label, ims) in enumerate(tiles):
    x = 0
    if ref != "-":
        sheet.paste(rim, (0, i * H)); x = refw
    for im in ims:
        sheet.paste(im, (x, i * H)); x += im.width
    d.text((refw + 10, i * H + 8), label, fill=(255, 255, 0), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
sheet.save(out)
print(out, sheet.size)
