"""Loop seam check for a 60-frame layer: mean |diff| between consecutive frames vs the wrap (last -> first).
  uv run -q --with numpy --with pillow python -I effectcraft/costura.py <dir with f_0000.png..>
A seamless loop has the wrap inside the spread of the consecutive steps."""
import sys, glob, numpy as np
from PIL import Image
fs = sorted(glob.glob(sys.argv[1] + "/f_*.png"))
im = [np.asarray(Image.open(f).convert("RGBA")).astype(np.float32) / 255 for f in fs]
d = [np.abs(im[i + 1] - im[i]).mean() for i in range(len(im) - 1)]
w = np.abs(im[0] - im[-1]).mean()
print("%s: %d frames, steps mean %.5f min %.5f max %.5f | wrap %.5f (%.2fx mean)" % (sys.argv[1], len(fs), np.mean(d), min(d), max(d), w, w / np.mean(d)))
