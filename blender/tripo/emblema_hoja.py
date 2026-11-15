# emblema_hoja.py <render dir (em-*, em6-* stills + medidas)> <out.jpg>
# One sheet for the owner: the MT hood emblem, 3 sizes (columns) x 2 blackletters (rows).
#   rows 1-2: one 3/4 camera above the hood that sees all three sizes (em-<size>-<font>)
#   rows 3-4: scene 6's own low camera (em6-<size>-<font>), a 360x225 crop around the emblem at 100 % then 2.5x nearest,
#             with the emblem's share of the frame (the probe's number; rule 2 asks >= 0.1 %)
import sys, json, numpy as np
from PIL import Image, ImageDraw, ImageFont

D, OUT = sys.argv[1], sys.argv[2]
TAM = [("parado", "(a) 14 cm de pie (la actual)"), ("grande", "(b) 18 cm de pie"), ("plano", "(c) plano sobre el cofre")]
FUE = [("grenze", "Grenze Gotisch ExtraBold"), ("pirata", "Pirata One")]
F = lambda s, b=False: ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if b else ''}.ttf", s)
CW, CH = 800, 450
M, TOP, LAB = 20, 150, 30


def recorte(nombre):
    """Crop around P15 in a scene-6 still (from the probe's 1/5-size id map), 360x225 at 100 %, shown 800x500 nearest."""
    j = json.load(open(f"{D}/medidas-{nombre}.json"))
    ids = np.load(f"{D}/{nombre}-id.npy")
    k = j["leyenda"]["prop:P15"]
    ys, xs = np.nonzero(ids == k)
    pct = j["props"]["P15"]["pct_cuadro"]
    im = Image.open(f"{D}/{nombre}.png").convert("RGB")
    cx, cy = int((xs.min() + xs.max() + 1) / 2 * 5), int((ys.min() + ys.max() + 1) / 2 * 5)
    w, h = 360, 225
    c = im.crop((cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2)).resize((CW, int(CW * h / w)), Image.NEAREST)
    return c, pct, (int(xs.max() - xs.min() + 1) * 5, int(ys.max() - ys.min() + 1) * 5)


filas = []
for fk, ft in FUE:
    filas.append((f"{ft}: cámara 3/4 sobre el cofre", [Image.open(f"{D}/em-{tk}-{fk}.png").convert("RGB").resize((CW, CH), Image.LANCZOS) for tk, _ in TAM], None))
for fk, ft in FUE:
    cs = [recorte(f"em6-{tk}-{fk}") for tk, _ in TAM]
    filas.append((f"{ft}: cámara baja de la escena 6 (recorte al 100 %, ampliado 2.2x)", [c[0] for c in cs],
                  [f"{c[1]} % del cuadro, {c[2][0]} x {c[2][1]} px" for c in cs]))
H = TOP + sum(LAB + max(i.size[1] for i in f[1]) + M + (22 if f[2] else 0) for f in filas)
W = M + 3 * (CW + M)
hoja = Image.new("RGB", (W, H), (24, 24, 26))
d = ImageDraw.Draw(hoja)
d.text((M, 14), "MT del cofre: tamaño y letra", fill=(240, 240, 240), font=F(30, True))
d.text((M, 54), "Referencia: el emblema de pie de la ronda 1 (Grenze, letras de unos 14 cm). Cambia: tamaño (18 cm, plano) y letra (Pirata One).",
       fill=(200, 200, 200), font=F(16))
d.text((M, 76), "Misma altura de mayúscula en las dos letras (14.6 / 18.8 / 19.9 cm). Cada cámara es la misma para las seis tomas.",
       fill=(200, 200, 200), font=F(16))
d.text((M, 98), "Ojo: la M de Grenze se parece a una «m» minúscula (se puede leer «mt»); la de Pirata One es una mayúscula clara.",
       fill=(255, 214, 90), font=F(16))
for i, (_, t) in enumerate(TAM):
    d.text((M + i * (CW + M), 124), t, fill=(255, 214, 90), font=F(20, True))
y = TOP
for rot, ims, pies in filas:
    d.text((M, y + 4), rot, fill=(180, 180, 185), font=F(17))
    y += LAB
    for i, im in enumerate(ims):
        hoja.paste(im, (M + i * (CW + M), y))
        if pies:
            d.text((M + i * (CW + M), y + im.size[1] + 3), pies[i], fill=(200, 200, 200), font=F(16))
    y += max(i.size[1] for i in ims) + M + (22 if pies else 0)
hoja.save(OUT, quality=88)
print(OUT, hoja.size)
