# crops.py <diego.png> <out dir>: square crops of the head and the screen-left hand, Lanczos to 1024², as Klein inputs.
import sys
from PIL import Image
src, out = sys.argv[1:3]
im = Image.open(src).convert("RGB")
for name, box in {"head": (225, 60, 685, 520), "hand": (40, 560, 260, 780)}.items():
    im.crop(box).resize((1024, 1024), Image.LANCZOS).save(f"{out}/diego_{name}_crop.png")
