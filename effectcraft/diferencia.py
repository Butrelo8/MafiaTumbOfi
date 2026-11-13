"""Stack the f0 layers (fg over fig over bg) and diff against the plain render: prints mean/p99/max |diff| and the share
of pixels over 0.05; writes a sheet (bg, fig, fg / beauty, stack, diff x8).
  uv run -q --with numpy --with pillow python -I effectcraft/diferencia.py <hoja dir with bg fig fg beauty> <sheet.png>
"""
import sys, numpy as np
from PIL import Image
d = sys.argv[1]
L = lambda p: np.asarray(Image.open(f"{d}/{p}/f_0000.png").convert("RGBA")).astype(np.float32) / 255
bg, fig, fg, be = L("bg"), L("fig"), L("fg"), L("beauty")
def over(a, b):  # a over b, straight alpha
    aa = a[..., 3:]; return np.concatenate([a[..., :3] * aa + b[..., :3] * (1 - aa), np.ones_like(aa)], -1)
comp = over(fg, over(fig, bg))
diff = np.abs(comp[..., :3] - be[..., :3])
print("diff mean %.4f  p99 %.4f  max %.3f  px>0.05: %.2f%%" % (diff.mean(), np.percentile(diff, 99), diff.max(), 100 * (diff.max(-1) > 0.05).mean()))
gray = np.zeros_like(bg); gray[..., :3] = 0.35; gray[..., 3] = 1
tiles = [bg, over(fig, gray), over(fg, gray), be, comp, np.concatenate([np.clip(diff * 8, 0, 1), np.ones_like(diff[..., :1])], -1)]
row = lambda t: np.concatenate(t, 1)
img = np.concatenate([row(tiles[:3]), row(tiles[3:])], 0)
Image.fromarray((img[..., :3] * 255).astype(np.uint8)).resize((img.shape[1] // 3, img.shape[0] // 3)).save(sys.argv[2])
