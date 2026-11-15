# strip.py <out.png> <height> <img> ...: images side by side at one height (a variants strip, not evidence).
import sys
from PIL import Image
out, h = sys.argv[1], int(sys.argv[2])
L = [Image.open(p).convert("RGB") for p in sys.argv[3:]]
L = [i.resize((int(i.width * h / i.height), h), Image.LANCZOS) for i in L]
c = Image.new("RGB", (sum(i.width for i in L), h)); x = 0
for i in L: c.paste(i, (x, 0)); x += i.width
c.save(out)
print(out, [i.size for i in L])
