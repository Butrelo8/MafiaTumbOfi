# grid.py <out.jpg> <frame> <tiles> <label=dir>...: one row per labelled closeups.py folder, one column per tile name
# (e.g. shoulder.L_q,shoulder.L_s,knee.L_q); tiles scaled to 384 px, label on the left, tile names on top.
import sys, glob
from PIL import Image, ImageDraw, ImageFont
out, fr, tiles = sys.argv[1], sys.argv[2], sys.argv[3].split(","); rows = [r.split("=", 1) for r in sys.argv[4:]]
fp = (glob.glob("/usr/share/fonts/**/DejaVuSans.ttf", recursive=True) or [None])[0]
font = ImageFont.truetype(fp, 20) if fp else ImageFont.load_default()
S, L, T = 384, 170, 32
img = Image.new("RGB", (L + S * len(tiles), T + S * len(rows)), (24, 24, 24)); dr = ImageDraw.Draw(img)
for j, t in enumerate(tiles): dr.text((L + j * S + 6, 6), t, fill=(230, 230, 230), font=font)
for i, (lab, d) in enumerate(rows):
    dr.text((8, T + i * S + 8), lab, fill=(240, 200, 90), font=font)
    for j, t in enumerate(tiles):
        img.paste(Image.open(f"{d}/{t}_f{fr}.png").convert("RGB").resize((S, S), Image.LANCZOS), (L + j * S, T + i * S))
img.save(out, quality=90); print(out, img.size)
