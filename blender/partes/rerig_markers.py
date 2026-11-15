# rerig_markers.py <front.png> <out.png>: Mixamo marker spots on export_rerig.py's front view (positions measured
# from the silhouette in docs/diego-rerig-handoff.md) and the current rig_fit joints (rig_trellis_p3), for comparison.
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
src = Image.open(sys.argv[1]).convert("RGB"); im = np.asarray(src).astype(int)
fg = np.abs(im - im[5, 5]).sum(2) > 30
K = 1280 / 1.1; px = lambda X, z: (512 + X * K, 640 - (z - 0.5) * K)
# symmetry check: arm thickness at mirrored columns (screen left arm = character's right)
for x in (760, 800, 826, 850):
    a = np.flatnonzero(fg[560:900, x]); b = np.flatnonzero(fg[560:900, 1024 - x])
    print("mirror", x, a[-1] - a[0], b[-1] - b[0])
M = {"chin": (0, 0.613), "groin": (0, 0.238), "elbow L": (0.205, 0.452), "elbow R": (-0.205, 0.452),
     "wrist L": (0.27, 0.41), "wrist R": (-0.27, 0.41), "knee L": (0.06, 0.16), "knee R": (-0.06, 0.16)}
R = {"elbow": (0.255, 0.44), "wrist": (0.334, 0.403), "knee": (0.06, 0.18), "hip": (0.06, 0.26), "ankle": (0.06, 0.10)}
d = ImageDraw.Draw(src); f = ImageFont.load_default(size=22)
for n, (X, z) in M.items():
    c = (255, 190, 40) if n.split()[0] in ("elbow", "knee") else (40, 220, 90)
    x, y = px(X, z); d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=c, outline=(0, 0, 0), width=2)
    d.text((x + 12 if X >= 0 else x - 12, y - 30), n, fill=c, font=f, anchor="la" if X >= 0 else "ra")
    print(f"marker {n:8s} X {X:+.3f} z {z:.3f}  px ({x:.0f}, {y:.0f})")
for n, (X, z) in R.items():
    for s in (1, -1):
        x, y = px(s * X, z); d.line((x - 8, y - 8, x + 8, y + 8), fill=(255, 60, 60), width=3); d.line((x - 8, y + 8, x + 8, y - 8), fill=(255, 60, 60), width=3)
d.text((16, 16), "green: marker on a visible feature   amber: estimate (elbow = shoulder-wrist midpoint,", fill=(240, 240, 240), font=f)
d.text((16, 44), "knee = hip-ankle midpoint; no visible joint)   red x: current rig_fit joints", fill=(240, 240, 240), font=f)
d.text((16, 72), "front view: Diego's LEFT is on screen RIGHT; red x above groin = hip joint, not an error", fill=(240, 240, 240), font=f)
src.save(sys.argv[2])
