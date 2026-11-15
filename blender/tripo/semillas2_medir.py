# semillas2_medir.py <render dir> <control name> <variant,variant,...> [out.tsv]
# Do separate gold seeds read in the scene stills? Per variant and per still (pp1-b = scene 1 camera, pp-fresa = close-up),
# in a box centred on the berry (found as where the variants differ from the unseeded control):
#   seedpx   pixels that are seed-coloured (hue 15-58 deg (gold seeds look orange in the dim cab), sat > 0.45, val > 0.30) and where the variant differs from the control
#   blobs    separate seed-coloured connected components of >= MIN_AREA px (8-connected), median area, and how many have a ring of
#            berry between them and the next blob (they are separate, not one speckle)
#   readable blobs whose mean CIE76 dE against their own 2 px ring is >= 15 (a seed you can tell from the berry next to it)
#   dE>10    pixels that changed by dE76 > 10 against the control (revisar's own threshold)
# A seed "reads" at a camera when >= 25 readable blobs of >= 3 px each exist. 25 is about a fifth of the front-facing seeds.
import sys, csv, numpy as np, cv2
from PIL import Image

D, CTRL, VARS = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
OUT = sys.argv[4] if len(sys.argv) > 4 else None
MIN_AREA, READ_DE, READ_N = 3, 15.0, 25
BOX = {"pp1-b": 100, "pp-fresa": 280}  # half-size of the berry box in px


def lab(rgb):
    return cv2.cvtColor(rgb.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)


def carga(v, s):
    return np.asarray(Image.open(f"{D}/{v}/{s}.png").convert("RGB"))


rows = []
for s in ("pp1-b", "pp-fresa"):
    c0 = carga(CTRL, s)
    imgs = {v: carga(v, s) for v in VARS}
    d = np.zeros(c0.shape[:2], bool)
    for im in imgs.values():
        d |= np.abs(im.astype(int) - c0.astype(int)).sum(2) > 24
    ys, xs = np.nonzero(d)
    cx, cy = int(np.median(xs)), int(np.median(ys))
    h = BOX[s]
    sl = (slice(max(cy - h, 0), cy + h), slice(max(cx - h, 0), cx + h))
    L0 = lab(c0[sl])
    for v in [CTRL] + VARS:
        im = carga(v, s)[sl]
        L = lab(im)
        dE = np.sqrt(((L - L0) ** 2).sum(2))
        hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV_FULL).astype(float)  # H 0-255 -> degrees * 256/360
        hue = hsv[..., 0] * 360 / 256
        sem = (hue > 15) & (hue < 58) & (hsv[..., 1] / 255 > 0.45) & (hsv[..., 2] / 255 > 0.30)
        sem &= dE > 10  # seed-coloured AND changed against the control (so the control row is 0 by construction)
        n, lab_, st, cen = cv2.connectedComponentsWithStats(sem.astype(np.uint8), connectivity=8)
        areas = st[1:, cv2.CC_STAT_AREA]
        ok = [i + 1 for i, a in enumerate(areas) if a >= MIN_AREA]
        leer = bajo = 0
        for i in ok:
            m = (lab_ == i).astype(np.uint8)
            anillo = cv2.dilate(m, np.ones((5, 5), np.uint8)) - cv2.dilate(m, np.ones((1, 1), np.uint8))
            anillo = (anillo > 0) & ~sem
            if anillo.sum() and np.sqrt(((L[m > 0].mean(0) - L[anillo].mean(0)) ** 2).sum()) >= READ_DE:
                leer += 1
                bajo += cen[i][1] > h  # lower half of the box (the cab light washes it pink-white)
        rows.append(dict(still=s, variant=v, box=f"{sl[1].start},{sl[0].start}+{2 * h}", seedpx=int(sem.sum()), blobs=len(ok),
                         median_area=float(np.median(areas[[i - 1 for i in ok]])) if ok else 0.0, readable=leer, readable_lower_half=int(bajo),
                         changed_dE10=int((dE > 10).sum()), reads="YES" if leer >= READ_N else "no"))
w = csv.DictWriter(open(OUT, "w") if OUT else sys.stdout, rows[0].keys(), delimiter="\t")
w.writeheader(); w.writerows(rows)
if OUT:
    for r in rows:
        print("\t".join(str(x) for x in r.values()))
