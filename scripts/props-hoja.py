"""Side-by-side page for the owner's pick: per scene, A | B | close-up, with the rule numbers under each still.

  uv run -q --with pillow python -I scripts/props-hoja.py

Reads docs/design/props-placement/stills/ppN-{a,b,cerca}.jpg and stills/medidas.tsv (scripts/props-medir.py); writes 960 px
thumbnails to mini/, one A|B|close-up strip per scene to lado-a-lado/ and the page index.html.
"""
import html
from pathlib import Path

from PIL import Image

D = Path("docs/design/props-placement")
ST, MINI, LADO = D / "stills", D / "mini", D / "lado-a-lado"
MINI.mkdir(exist_ok=True)
LADO.mkdir(exist_ok=True)
ESCENAS = [
    ("1", "Escena 1 · Cabina (MÚSICA)", "Cámara CAMINO[0], 20 mm, entre las cabezas de atrás. A: flecos de lado a lado (tapan el espejo), papel picado en el techo, banderín al centro, fresa larga. B: flecos partidos que dejan libre el espejo, sin papel picado, banderín en la esquina del copiloto, fresa corta."),
    ("2", "Escena 2 · Caja (REDES)", "Cámara VISTA_ESC2, 28 mm. Montón del piso: caja3 A (la elección #34 sigue abierta; los props nuevos van sólo en el arco, los rieles y la cabina). A: marquesina a toda luz, focos en rieles y arco, banderines, piñata y dos racimos de globos como estaban. B: la marquesina es el único pico y más tenue que las calcas, focos sólo en el arco, un racimo de globos bajo en la esquina, sin bandera."),
    ("4", "Escena 4 · Costado (LA BANDA)", "Cámara a 6.2 m del lado del copiloto, 24 mm, luz de relleno (la opción de luz sigue abierta; los props con luz propia se leen con cualquiera). A: barra LED blanca, trompetas, parrilla con llanta, moños en los dos espejos, marquesina y focos a toda luz, luz bajo la carrocería. B: el techo lleva sólo la barra en ámbar, la caja un solo pico, nada sobre las ventanas."),
    ("6", "Escena 6 · Placa (CONTRATACIÓN)", "Cámara al frente, baja, 32 mm. A: barra LED blanca, trompetas, franja en el parabrisas, moños, luz bajo la carrocería, flecos completos. B: la placa sigue siendo lo más brillante tras los faros, así que la barra va en ámbar; sin trompetas; flecos partidos."),
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
for e, titulo, nota in ESCENAS:
    tomas = [(f"pp{e}-{s}", et) for s, et in (("a", "A · picks + props nuevos"), ("b", "B · recolocado por las reglas"), ("cerca", "Detalle (B)"))]
    figs, ims = [], []
    for nombre, et in tomas:
        src = ST / f"{nombre}.jpg"
        if not src.exists():
            continue
        im = Image.open(src).convert("RGB")
        ims.append(im)
        im.resize((960, round(960 * im.height / im.width)), Image.LANCZOS).save(MINI / f"{nombre}.jpg", quality=70)
        m = M.get(nombre, {})
        num = ""
        if m:
            num = (f"<dl><dt>Regla 1 · zona tapada</dt><dd>{m['zona_cubierta_%']} % · {m['r1']}</dd>"
                   f"<dt>Reglas 2-3 · props que se leen</dt><dd>{html.escape(m['props_que_leen'])} · {m['r3']}</dd>"
                   f"<dt>Regla 4 · luz total: zona vs prop con luz</dt><dd>{m['zona_luz']} vs {m['prop_luz']} · {m['r4']}</dd></dl>")
        figs.append(f'<figure><a href="stills/{nombre}.jpg"><img src="mini/{nombre}.jpg" alt="{html.escape(titulo)}, {html.escape(et)}" '
                    f'width="960" height="540" loading="lazy"></a><figcaption><strong>{html.escape(et)}</strong>{num}</figcaption></figure>')
    if ims:
        h = 540
        tira = Image.new("RGB", (sum(round(h * i.width / i.height) for i in ims) + 8 * (len(ims) - 1), h), (10, 10, 10))
        x = 0
        for i in ims:
            w = round(h * i.width / i.height)
            tira.paste(i.resize((w, h), Image.LANCZOS), (x, 0))
            x += w + 8
        tira.save(LADO / f"escena{e}.jpg", quality=80)
    secciones.append(f'<section id="e{e}"><h2>{html.escape(titulo)}</h2><p>{html.escape(nota)}</p><div class="fila">{"".join(figs)}</div></section>')

pagina = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Utilería y acomodo</title>
<style>
:root {{ --bg:#000; --fg:#eeeae0; --tenue:#b9b2a3; --oro:#e7b551; --linea:#2c2923; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.5 system-ui, sans-serif; }}
main {{ max-width:1500px; margin:0 auto; padding:24px 16px 64px; }}
h1 {{ font-size:1.6rem; margin:0 0 8px; }} h2 {{ font-size:1.25rem; margin:40px 0 4px; color:var(--oro); }}
p {{ color:var(--tenue); max-width:70ch; }}
a {{ color:var(--oro); }} a:focus-visible {{ outline:3px solid var(--oro); outline-offset:3px; }}
.fila {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:12px; }}
figure {{ margin:0; border:1px solid var(--linea); }}
img {{ display:block; width:100%; height:auto; }}
figcaption {{ padding:8px 10px; font-size:.9rem; }}
dl {{ margin:6px 0 0; display:grid; grid-template-columns:auto 1fr; gap:2px 10px; color:var(--tenue); }}
dt {{ font-weight:600; color:var(--fg); }} dd {{ margin:0; }}
</style></head><body><main>
<h1>Utilería nueva y acomodo: A contra B por escena</h1>
<p>Fotos reales, reglas y la lista de 14 props: <a href="referencias.md">referencias.md</a>, <a href="reglas.md">reglas.md</a>,
<a href="props.md">props.md</a>. Cada imagen abre el still completo (1920×1080, 64 muestras, de noche). Los números salen de una sonda
por rayos desde la cámara de cada escena (<code>scripts/props-medir.py</code>); el look se juzga en los stills.</p>
{''.join(secciones)}
<section id="preguntas"><h2>Preguntas para el dueño</h2><ol>
<li>Por escena, ¿A, B o una mezcla? (Respuesta: una letra por escena, por ejemplo 1B 2B 4B 6B.)</li>
<li>¿Entra la marquesina PURA MT en el arco de la caja? Funciona con la caja3 A y la B (#34 sigue abierta: las calcas quedan 0 % tapadas con las dos).</li>
<li>Barra LED del techo: (a) apagada en la escena 6, (b) ámbar tenue como luz de día, que empata con la placa, o (c) fuera.</li>
<li>Color de la luz bajo la carrocería: (a) ámbar/oro, el de la marca, como en los stills, o (b) morado, como el Renotaxi de la referencia 17.</li>
<li>Objetos religiosos (rosario en el espejo, Virgen en el tablero), comunes en cabinas mexicanas: (a) no, se queda la fresa, o (b) sí, uno, y ¿cuál?</li>
<li>Cuernos sobre el cofre: (a) no, o (b) sí. Ojo: en las búsquedas salen ligados a trocas de cártel.</li>
</ol>
<p>Fuera de estos stills: la escena 3 (un moño en el espejo del conductor, que sirve para las dos lecturas de #33) y la 5 (sólo se ve el cofre) no llevan stills nuevos; tampoco hay versión 9:16. El detalle de la escena 1 se hizo con flecos de 3 cm y la fresa a 7 cm; el still B final los lleva a 2.5 y 4.5 cm.</p></section>
</main></body></html>
"""
(D / "index.html").write_text(pagina, encoding="utf8")
print("index.html", len(secciones), "escenas")
