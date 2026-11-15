# sheet.py <dir> <out.png> [frames, default 22,70,110]: the comparison sheet. One row per frame; columns front x4 then side x4, in the order
# skinned v2 | Tripo parts (texture) | Tripo parts (flat vinyl) | TRELLIS.2 parts. Every tile is the same crop of a
# 1024 px still rendered with one framing (render_parts.py), scaled to 0.75.
import sys, glob
from PIL import Image, ImageDraw, ImageFont
d, out = sys.argv[1], sys.argv[2]
who = [("skinned", "Tripo v2 con piel"), ("tex", "Tripo piezas · textura"), ("flat", "Tripo piezas · vinilo plano"),
       ("trellis", "TRELLIS.2 piezas")]
X0, CW, S = 277, 480, 0.75   # the figure spans x 297-734 in all 24 stills
tw, th = int(CW * S), int(1024 * S); top, left = 70, 70  #; tw, th = int(CW * S), int(1024 * S); top, left = 70, 70
fp = (glob.glob("/usr/share/fonts/**/DejaVuSans.ttf", recursive=True) or [None])[0]
font = ImageFont.truetype(fp, 22) if fp else ImageFont.load_default(); big = ImageFont.truetype(fp, 28) if fp else font
FR = [int(x) for x in (sys.argv[3] if len(sys.argv) > 3 else "22,70,110").split(",")]
W = left + 8 * tw + 20; H = top + len(FR) * th
img = Image.new("RGB", (W, H), (24, 24, 24)); dr = ImageDraw.Draw(img)
for vi, (v, vl) in enumerate((("front", "frente"), ("side", "lado"))):
    x = left + vi * (4 * tw + 20); dr.text((x + 4, 4), vl, fill=(240, 200, 90), font=big)
    for wi, (w, wl) in enumerate(who): dr.text((x + wi * tw + 6, 40), wl, fill=(230, 230, 230), font=font)
for fi, f in enumerate(FR):
    y = top + fi * th; dr.text((8, y + 8), f"f{f}", fill=(240, 200, 90), font=big)
    for vi, v in enumerate(("front", "side")):
        for wi, (w, _) in enumerate(who):
            t = Image.open(f"{d}/{w}_{v}_f{f}.png").convert("RGB").crop((X0, 0, X0 + CW, 1024)).resize((tw, th), Image.LANCZOS)
            img.paste(t, (left + vi * (4 * tw + 20) + wi * tw, y))
img.save(out); print(out, img.size)
