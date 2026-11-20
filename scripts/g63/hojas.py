"""Sheets: the done-check stills (new G63) and before / after against d7f18f1c. Labelled, 1440 shots at half size."""
import sys
from PIL import Image, ImageDraw
nuevo, viejo, salida = sys.argv[1:4]
W, H = 720, 450
def hoja(celdas, cols, ruta):
    filas = (len(celdas) + cols - 1) // cols
    h = Image.new("RGB", (cols * W, filas * (H + 24)), (16, 16, 16)); d = ImageDraw.Draw(h)
    for i, (dir_, vista, etiqueta) in enumerate(celdas):
        x, y = (i % cols) * W, (i // cols) * (H + 24)
        h.paste(Image.open(f"{dir_}/1440-{vista}.png").convert("RGB").resize((W, H)), (x, y + 24))
        d.text((x + 8, y + 5), etiqueta, fill=(240, 240, 240))
    h.save(ruta, quality=84); print(ruta, h.size)
hoja([(nuevo, "frente34", "exterior 3/4 frente"), (nuevo, "tras34", "exterior 3/4 atras"),
      (nuevo, "techo_carga", "techo: rack + carga + red"), (nuevo, "parada1", "interior, camara Cabina"),
      (nuevo, "parada2", "camara Caja (la carga del techo)"), (nuevo, "banda-manager", "toma de la banda: manager")], 2, f"{salida}/hoja-g63-nuevo.jpg")
hoja([(viejo, v, f"antes d7f18f1c  {v}") if k == 0 else (nuevo, v, f"despues (G63 nuevo)  {v}") for v in ("parada1", "parada2", "frente34", "tras34") for k in (0, 1)], 2, f"{salida}/hoja-antes-despues.jpg")
