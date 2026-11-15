# sheet.py <out.jpg> <cols> <cell px> label=img ...: labelled grid (overview only, never evidence for motion).
import sys
from PIL import Image, ImageDraw, ImageFont
out, cols, px = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
items = [a.split("=", 1) for a in sys.argv[4:]]
rows = (len(items) + cols - 1) // cols; lab = 34
S = Image.new("RGB", (cols * px, rows * (px + lab)), (245, 245, 245)); d = ImageDraw.Draw(S)
try: f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
except OSError: f = ImageFont.load_default()
for k, (t, p) in enumerate(items):
    im = Image.open(p).convert("RGB"); im.thumbnail((px, px), Image.LANCZOS)
    x, y = (k % cols) * px, (k // cols) * (px + lab)
    S.paste(im, (x + (px - im.width) // 2, y + lab + (px - im.height) // 2)); d.text((x + 8, y + 5), t, fill=(20, 20, 20), font=f)
S.save(out, quality=90); print(out, S.size)
