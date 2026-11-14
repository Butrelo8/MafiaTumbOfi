"""Side-by-side page for the owner: the picked arrangement (B) per scene with its rule numbers, then each new piece (light
bar, MT emblem, strawberry) as the kept version next to the variants it beat.

  uv run -q --with pillow python -I scripts/props-hoja.py

Reads docs/design/props-placement/stills/*.jpg and stills/medidas.tsv (scripts/props-medir.py); writes 960 px thumbnails to
mini/, one strip per section to lado-a-lado/ and the page index.html.
"""
import html
from pathlib import Path

from PIL import Image

D = Path("docs/design/props-placement")
ST, MINI, LADO = D / "stills", D / "mini", D / "lado-a-lado"
MINI.mkdir(exist_ok=True)
LADO.mkdir(exist_ok=True)

SECCIONES = [
    ("escenas", "Las cuatro escenas con lo elegido (B)",
     "B en todas las escenas, sin marquesina, sin cuernos; en el camión las lámparas reales del alerón y el MT dorado en el cofre. "
     "La luz bajo la carrocería sigue ámbar. Montón de la caja: caja3 A (#34 sigue abierta). Escena 4 con la luz de relleno (sigue abierta).",
     [("pp1-b", "Escena 1 · Cabina (MÚSICA)"), ("pp2-b", "Escena 2 · Caja (REDES)"), ("pp4-b", "Escena 4 · Costado (LA BANDA)"),
      ("pp6-b", "Escena 6 · Placa (CONTRATACIÓN)")]),
    ("barra", "Barra de luces: la pieza real",
     "El G 63 AMG 6×6 de fábrica lleva una lámpara LED en cada esquina del alerón del techo: mica clara sobre caja negra con cinco "
     "copas redondas (fotos 12b y 12c en referencias.md). El modelo del camión ya tiene esas dos cavidades, apagadas; aquí se llenan "
     "y se encienden en blanco, con su haz hacia el camino. Al lado, la otra lectura: la barra de dos pisos del Brabus XLP 800 6×6 "
     "(foto 12), que es una pieza del G nuevo (W465), no de este camión.",
     [("pp-barra", "Se queda · lámparas de fábrica del 6×6"), ("pv-barra-xlp", "Variante · dos pisos estilo Brabus XLP 800"),
      ("pv-6-xlp", "Variante XLP en la escena 6 (para la regla 4)")]),
    ("emblema", "Emblema MT dorado en el cofre",
     "Letra gótica Grenze Gotisch ExtraBold (licencia OFL, libre), extruida y biselada, en el oro de la marca (DESIGN.md, "
     "oklch 78 % 0.15 85) como metal pulido. En vez de los cuernos.",
     [("pp-emblema", "Se queda · de pie, atornillado al frente del cofre"), ("pv-emblema-plano", "Variante · plano sobre el cofre")]),
    ("fresa", "La fresa del espejo",
     "Un solo archivo intercambiable: blender/props/fresa.glb (Z arriba, metros, origen en la argolla). Si llega un modelo de un "
     "amigo, se reemplaza ese archivo y el script lo escala a 4.1 cm.",
     [("pp-fresa", "Se queda · fruta (semillas en hoyuelos, cáliz, barniz)"), ("pv-fresa-resina", "Variante · resina con oro"),
      ("pv-fresa-peluche", "Variante · peluche de fieltro"), ("fresa-estudio", "Las tres en estudio")]),
]


def medidas():
    p = ST / "medidas.tsv"
    if not p.exists():
        return {}
    filas = p.read_text(encoding="utf8").strip().split("\n")
    cab = filas[0].split("\t")
    return {f.split("\t")[0]: dict(zip(cab, f.split("\t"))) for f in filas[1:]}


M = medidas()
secciones = []
for sid, titulo, nota, tomas in SECCIONES:
    figs, ims = [], []
    for nombre, et in tomas:
        src = ST / f"{nombre}.jpg"
        if not src.exists():
            continue
        im = Image.open(src).convert("RGB")
        ims.append(im)
        w, h = 960, round(960 * im.height / im.width)
        im.resize((w, h), Image.LANCZOS).save(MINI / f"{nombre}.jpg", quality=70)
        m = M.get(nombre, {})
        num = ""
        if m and m["r1"] != "detalle":
            num = (f"<dl><dt>Regla 1 · zona tapada</dt><dd>{m['zona_cubierta_%']} % · {m['r1']}</dd>"
                   f"<dt>Reglas 2-3 · props que se leen</dt><dd>{html.escape(m['props_que_leen'])} · {m['r3']}</dd>"
                   f"<dt>Regla 4 · luz total: zona vs prop con luz</dt><dd>{m['zona_luz']} vs {m['prop_luz']} · {m['r4']}</dd></dl>")
        figs.append(f'<figure><a href="stills/{nombre}.jpg"><img src="mini/{nombre}.jpg" alt="{html.escape(et)}" '
                    f'width="{w}" height="{h}" loading="lazy"></a><figcaption><strong>{html.escape(et)}</strong>{num}</figcaption></figure>')
    if ims:
        h = 540
        tira = Image.new("RGB", (sum(round(h * i.width / i.height) for i in ims) + 8 * (len(ims) - 1), h), (10, 10, 10))
        x = 0
        for i in ims:
            w = round(h * i.width / i.height)
            tira.paste(i.resize((w, h), Image.LANCZOS), (x, 0))
            x += w + 8
        tira.save(LADO / f"{sid}.jpg", quality=80)
    secciones.append(f'<section id="{sid}"><h2>{html.escape(titulo)}</h2><p>{html.escape(nota)}</p><div class="fila">{"".join(figs)}</div></section>')

pagina = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Utilería: lo elegido</title>
<style>
:root {{ --bg:#000; --fg:#eeeae0; --tenue:#b9b2a3; --oro:#e7b551; --linea:#2c2923; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.5 system-ui, sans-serif; }}
main {{ max-width:1500px; margin:0 auto; padding:24px 16px 64px; }}
h1 {{ font-size:1.6rem; margin:0 0 8px; }} h2 {{ font-size:1.25rem; margin:40px 0 4px; color:var(--oro); }}
p {{ color:var(--tenue); max-width:75ch; }}
a {{ color:var(--oro); }} a:focus-visible {{ outline:3px solid var(--oro); outline-offset:3px; }}
.fila {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:12px; }}
figure {{ margin:0; border:1px solid var(--linea); }}
img {{ display:block; width:100%; height:auto; }}
figcaption {{ padding:8px 10px; font-size:.9rem; }}
dl {{ margin:6px 0 0; display:grid; grid-template-columns:auto 1fr; gap:2px 10px; color:var(--tenue); }}
dt {{ font-weight:600; color:var(--fg); }} dd {{ margin:0; }}
</style></head><body><main>
<h1>Utilería: lo que eligió el dueño (13 nov, 20:04)</h1>
<p>B en todas las escenas, sin marquesina, sin cuernos, la barra de luces real, la fresa nueva y el MT dorado en el cofre. Cada
imagen abre el still completo (1920×1080, 64 muestras, de noche). Los números salen de una sonda por rayos desde la cámara de cada
escena (<code>scripts/props-medir.py</code>); el look se juzga en los stills. Reglas: <a href="reglas.md">reglas.md</a>; props:
<a href="props.md">props.md</a>; fotos: <a href="referencias.md">referencias.md</a>.</p>
{''.join(secciones)}
<section id="preguntas"><h2>Preguntas abiertas</h2><ol>
<li>Emblema: (a) de pie, del tamaño actual (letras de unos 14 cm): en la escena 6 ocupa 0.088 % del cuadro, bajo la línea de 0.1 % de la regla 2, así que ahí se ve como un brillo dorado y se lee en los detalles; (b) más grande, para que se lea en la escena 6 (letras de unos 18 cm, casi la mitad del ancho del cofre al frente); o (c) plano sobre el cofre (no se ve desde la cámara baja de la escena 6).</li>
<li>Letra del emblema: (a) se queda Grenze Gotisch (su M mayúscula parece una m minúscula: se puede leer «mt») o (b) una gótica de mayúsculas más claras, como Pirata One (OFL, la de DESIGN.md).</li>
<li>Fresa: (a) fruta, (b) resina con oro o (c) peluche; o se espera el modelo del amigo (se cambia un archivo).</li>
</ol>
<p>Ya resuelta (13 nov): la barra de luces son las lámparas de fábrica del 6×6, no la de dos pisos estilo Brabus.</p>
<p>Siguen abiertas, sin decidir aquí: #33 (escena 3, espejo o puerta trasera), #34 (acomodo de la caja) y la luz de la escena 4.</p></section>
</main></body></html>
"""
(D / "index.html").write_text(pagina, encoding="utf8")
print("index.html", len(secciones), "secciones")
