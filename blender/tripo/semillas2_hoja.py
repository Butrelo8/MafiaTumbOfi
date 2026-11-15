# semillas2_hoja.py <est dir> <escena dir> <medidas-semillas.tsv> <out.jpg>
# The owner's sheet for pass 2 of the 3D seeds. Columns = pass 1's seeds on the rescaled berry, then the variants (size, colour,
# sink). Rows = studio whole berry, studio macro, the cab close-up (100 % crop), scene 1's camera (100 % crop, 3x nearest) and
# the same crop with the unseeded berry beside it for the difference. Numbers come from semillas2_medir.py.
import sys, csv, numpy as np
from PIL import Image, ImageDraw, ImageFont

EST, ESC, TSV, OUT = sys.argv[1:5]
V = [("strawberry-b-semillas", "pase 1", "336 semillas, amarillas, x1"),
     ("strawberry-s2-amarilla", "A", "278, amarillas, x2"),
     ("strawberry-s2-oro", "B", "278, oro satinado, x2, 1/3 enterradas"),
     ("strawberry-s2-oro-hundida", "E", "como B, enterradas a la mitad"),
     ("strawberry-s2-oro-alta", "F", "como B, apoyadas sobre el hoyuelo"),
     ("strawberry-s3-oro", "C", "161, oro satinado, x3"),
     ("strawberry-s4-oro", "D", "97, oro satinado, x4")]
MED = {(r["still"], r["variant"]): r for r in csv.DictReader(open(TSV), delimiter="\t")}
F = lambda s, b=False: ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if b else ''}.ttf", s)
CW = 330
M, TOP, LAB = 16, 150, 28


def caja(still, v):
    x, y, w = MED[(still, v)]["box"].replace("+", ",").split(",")
    return int(x), int(y), int(w)


ctrl = lambda s: np.asarray(Image.open(f"{ESC}/strawberry/{s}.png").convert("RGB"))
filas = []
for k, rot in (("entera", "estudio: la fresa entera (cuerpo de 4.1 cm)"), ("macro", "estudio: macro, ventana de 2.5 cm")):
    filas.append((rot, [Image.open(f"{EST}/{v}_{k}.png").convert("RGB").resize((CW, CW), Image.LANCZOS) for v, *_ in V]))
x, y, w = caja("pp-fresa", V[0][0])
filas.append(("en la cabina: toma de cerca, recorte al 100 %",
              [Image.open(f"{ESC}/{v}/pp-fresa.png").convert("RGB").crop((x + 90, y + 40, x + w - 90, y + w - 140)).resize((CW, CW * 380 // 380), Image.LANCZOS) for v, *_ in V]))
x, y, w = caja("pp1-b", V[0][0])
filas.append(("escena 1: la cámara real, recorte de 110 px al 100 %, ampliado 3x sin suavizar",
              [Image.open(f"{ESC}/{v}/pp1-b.png").convert("RGB").crop((x + 45, y + 45, x + 155, y + 155)).resize((CW, CW), Image.NEAREST) for v, *_ in V]))
W = M + len(V) * (CW + M)
H = TOP + len(filas) * (LAB + CW + M) + 80
hoja = Image.new("RGB", (W, H), (24, 24, 26))
d = ImageDraw.Draw(hoja)
d.text((M, 14), "Fresa del espejo: semillas 3D, pasada 2", fill=(240, 240, 240), font=F(28, True))
d.text((M, 52), "Referencia: fresa de jardín con aquenios en hoyuelos. Se queda: la malla y las texturas del amigo, idénticas byte a byte.",
       fill=(200, 200, 200), font=F(15))
d.text((M, 72), "Cambia a propósito: la fresa se escala para que el CUERPO mida 4.1 cm (antes 2.6); las semillas son más grandes que las reales,",
       fill=(200, 200, 200), font=F(15))
d.text((M, 92), "doradas y a distinta altura sobre el hoyuelo, y se quitan las que se encimarían. La luz de la cabina sigue lavando la mitad de abajo.",
       fill=(200, 200, 200), font=F(15))
for i, (v, n, t) in enumerate(V):
    d.text((M + i * (CW + M), 114), n, fill=(255, 214, 90), font=F(20, True))
    d.text((M + i * (CW + M), 138 - 4), t, fill=(200, 200, 200), font=F(13))
yy = TOP
for rot, ims in filas:
    d.text((M, yy + 4), rot, fill=(180, 180, 185), font=F(15))
    yy += LAB
    for i, im in enumerate(ims):
        hoja.paste(im, (M + i * (CW + M), yy))
    yy += CW + M
d.text((M, yy), "Lectura medida en la toma de la escena 1 (cuadro de 200 px, ver informe): semillas separadas de >= 3 px / legibles (dE >= 15 contra su vecino)",
       fill=(200, 200, 200), font=F(15))
t = "   ".join(f"{n}: {MED[('pp1-b', v)]['blobs']} / {MED[('pp1-b', v)]['readable']}" for v, n, _ in V)
d.text((M, yy + 24), t, fill=(255, 214, 90), font=F(17, True))
hoja.save(OUT, quality=88)
print(OUT, hoja.size)
