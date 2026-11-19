"""Textures for the P1 stills mock (2026-11-18): the stop 1 dash screen, the stop 5 rear-screen copy variants, the stop 4 name
plate, and the gantry title rows cut from public/vivo/letreros.png. Spanish copy is a proposal: the owner approves the wording.

  uv run -q --with pillow python -I scripts/p1-texturas.py <repo> <out_dir>

Fonts: tmp/fuentes (Saira, Saira Condensed 800: OFL; the screen truck's lettering already uses Saira Condensed 800). Saira has no
arrow glyphs (↗ drew a box), so the copy carries none.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

REPO, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
F = lambda n, s: ImageFont.truetype(os.path.join(REPO, "tmp", "fuentes", n), s)
COND, S6, S4 = "saira-condensed-latin-800-normal.ttf", "saira-latin-600-normal.ttf", "saira-latin-400-normal.ttf"
ORO, BLANCO, NEGRO = (232, 178, 64), (245, 242, 235), (10, 10, 12)

# ---- stop 1: dash screen, 3:1 (utileria's radio2-a screen is 0.36 x 0.12 m). Latest single from catalog.json: PUTIFRESA.
w, h = 1200, 400
im = Image.new("RGB", (w, h), (8, 9, 12))
d = ImageDraw.Draw(im)
portada = Image.open(os.path.join(REPO, "public", "music", "putifresa.webp")).convert("RGB").resize((320, 320), Image.LANCZOS)
im.paste(portada, (40, 40))
d.text((400, 70), "PUTIFRESA", font=F(COND, 96), fill=BLANCO)
d.text((402, 180), "Single · Mafia Tumbada", font=F(S4, 40), fill=(170, 170, 175))
d.rounded_rectangle((400, 268, 640, 340), 6, fill=ORO)
d.text((520, 304), "ESCUCHAR", font=F(S6, 34), fill=NEGRO, anchor="mm")
for x, s in ((900, "‹"), (1060, "›")):
    d.rounded_rectangle((x - 60, 250, x + 60, 350), 8, outline=(200, 200, 205), width=4)
    d.text((x, 296), s, font=F(S6, 90), fill=BLANCO, anchor="mm")
d.text((980, 120), "1 / 9", font=F(S4, 40), fill=(150, 150, 155), anchor="mm")
im.save(os.path.join(OUT, "tablero.png"))

# ---- stop 5: rear screen (2.0 x 2.05 m), LED copy. Headline + a crawl line cut at both edges (it moves in the live build).
COPIAS = {
    "v1": ("¿DÓNDE\nANDAMOS?", "MIRA DÓNDE ANDAMOS · INSTAGRAM · @MAFIA_TUMBADA_OFICIAL · MIRA DÓNDE"),
    "v2": ("EN RUTA", "DÓNDE TOCAMOS HOY: EN NUESTRAS HISTORIAS DE INSTAGRAM · DÓNDE TOCAMOS"),
    "v3": ("AHÍ\nVAMOS", "SÍGUENOS LA PISTA EN INSTAGRAM · @MAFIA_TUMBADA_OFICIAL · SÍGUENOS LA"),
}
for k, (titulo, cinta) in COPIAS.items():
    w, h = 800, 820
    im = Image.new("RGB", (w, h), (4, 4, 5))
    d = ImageDraw.Draw(im)
    d.text((w / 2, 300), titulo, font=F(COND, 190 if "\n" in titulo else 230), fill=ORO, anchor="mm", align="center", spacing=4)
    d.rectangle((0, 590, w, 700), fill=(28, 8, 6))
    d.text((24, 645), cinta, font=F(COND, 64), fill=BLANCO, anchor="lm")  # starts on its first word, cut on the right
    d.text((w / 2, 760), "VER HISTORIAS", font=F(S6, 44), fill=(200, 200, 200), anchor="mm")
    im.save(os.path.join(OUT, f"trasera-{k}.png"))

# ---- stop 4: name plate that rises from the lowered window (members.ts: name, role, Instagram)
for clave, nombre, rol, ig in (("hector", "HÉCTOR BÁEZ", "Vocal principal", "@hector_baezzzmt_"),):
    w, h = 1024, 384
    im = Image.new("RGB", (w, h), NEGRO)
    d = ImageDraw.Draw(im)
    d.rectangle((8, 8, w - 9, h - 9), outline=ORO, width=8)
    d.text((w / 2, 130), nombre, font=F(COND, 120), fill=BLANCO, anchor="mm")
    d.text((w / 2, 225), rol, font=F(S4, 54), fill=(190, 190, 190), anchor="mm")
    d.text((w / 2, 305), ig, font=F(S6, 54), fill=ORO, anchor="mm")
    im.save(os.path.join(OUT, f"placa-{clave}.png"))

# ---- gantry title rows, one PNG per stop, from the live atlas (same pixels in the stills and the page)
atlas = Image.open(os.path.join(REPO, "public", "vivo", "letreros.png"))
for k in range(6):
    atlas.crop((0, k * 170, 1024, (k + 1) * 170)).save(os.path.join(OUT, f"titulo-{k + 1}.png"))
print("p1-texturas listo", sorted(os.listdir(OUT)))
