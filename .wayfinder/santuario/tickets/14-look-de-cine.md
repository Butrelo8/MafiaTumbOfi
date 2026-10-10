# 14 — Look de cine: obturador en las transiciones, halación en los loops
Type: prototype · Status: resolved · Blocks: 09 · Blocked by: — · Assignee: claude

## Question
¿Qué de la investigación de "parecer una toma de película" (visual-lab `cross-tool/lab/orbit-movie-look/NOTES.md`:
obturador sintético, fps, formato, gradación, grano) le sirve al santuario, y cuánto pesa?

## Prueba (2026-10-09)
Sobre los prototipos vigentes: escritorio `tmp/dlss5-fondo/r7_nrplaca.mp4`, vertical `tmp/movil-06/web/`.
- **Loops: el obturador no aplica.** Cámara quieta; el polvo se mueve ≤ 1.5 px por cuadro, las velas sólo cambian de
  brillo y el humo es lento. Se quedan a 24p.
- **Transiciones: sí.** FILM ×8 de `ida.mp4` (704×1280, 60 cuadros, 163 s en GPU) → 192 fps → 24p con obturador de
  180° (promedio de 4 de 8 subcuadros, ventana centrada). A la máxima velocidad (cuadro 20) la piedra del piso y el
  contrabajo se barren en horizontal; el barrido del pilar se suaviza (12.2 → 10.2). **Pesa 20 % menos**
  (497 → 396 KB; el barrido comprime mejor). 48p/360° pesaría 472 KB, pero cambia de cadencia en cada empalme con los
  loops de 24p. Los cuadros 0–1 y 58–59 quedan sin barrido (la cámara sale y llega de quieta): así el empalme con los
  loops queda igual que antes (ida → sacristía 3.19 → 3.29; nave → ida 4.23 → 4.31).
- **Gradación:** el LOOK 2383 se queda. Encima, **halación** (halo rojizo en llamas, brasas y neón) y **difusión** tipo
  Pro-Mist (`tmp/cine-look/halacion.sh`). La primera fuerza (0.5 / 0.3) apenas se veía al 100 %; la elegida sube la
  ganancia de las altas luces: +1.5 % de peso en escritorio, +3–6 % en los loops verticales.
- **Grano:** ya está en DESIGN.md como overlay SVG en HTML, no horneado (no pesa ni da el "pop" del cuadro intra). Que
  se mueva (animación por pasos) va en el 09/10.
- **Formato 1.85 / 2.39:** no aplica. El fondo va a sangre en 16:9 y vertical, y el layout del 03 depende de eso.

| Archivo vertical | Antes | Ahora |
|---|---|---|
| ida | 497 KB | 407 KB |
| vuelta | 504 KB | 383 KB |
| nave | 242 KB | 250 KB |
| sacristía | 155 KB | 163 KB |

Assets (`tmp/cine-look/`, ignorado): `web/` (página móvil con los cuatro archivos nuevos), `sbs_ida_actual_vs_24p180.mp4`,
`sbs_r7_actual_vs_halacion.mp4`, `cmp_r7_hal3_100.jpg` (actual / primera / elegida, al 100 %), `r7_hal2.mp4`
(escritorio), `halacion.sh`, `NOTAS.md`.

### v5: textura de rodaje y foco de lente real (2026-10-09)
El usuario pidió "texturas de vida real, como cámara de cine + lente profesional". Al 100 % la placa delataba: todo
nítido de 2 m a 15 m (un T2 en una iglesia de noche no puede), superficies limpias y nuevas, 1.6 MP escalados a 1080p.
- **Placa real:** Klein 4 MP sobre la placa vigente ("frame grab de un largometraje, ARRI Alexa 35 + Cooke S4/i, mismo
  todo, sólo superficies reales y gastadas, juntas oscuras, sin motas blancas"; `E:\ComfyUI\workflows\runs\mto_placa_real_s2b.json`,
  ~58 s). Sale con 3–4 px de corrimiento y el dorado pálido; `placa_real.py` la devuelve: corrimiento por correlación de
  fase, tono y luz de la placa **NR** aprobada (cuadro 0 de `dlss5-fondo/escritorio_nrplaca.mkv`: histograma, exposición
  local σ 40, color Lab a/b, luminancia fina σ 8) y sólo de cerca (`PROF=disp_r7.png`). Aporta micro-textura: vetas,
  raspones, poros en bancas, instrumentos y pilares.
- **Foco de lente real:** MoGe-2 (ya instalado, nodo core, 2 s) da la disparidad de la placa (`disp_r7.png`); `dof.py`
  desenfoca en disco y en luz lineal lo que está detrás del foco: foco en guitarra/bocina, 9 px de diámetro en el fondo a
  1920 (≈ 32 mm T2.8 en Super 35). Las velas lejanas salen como bokeh. `FOCO_MASK=mascara_humo.png` deja el humo del
  sahumador en el plano de foco (MoGe veía el muro detrás). Enfocar el contrabajo dejaba blanda la guitarra.
- **Elegida por Fable** (el usuario le delegó la elección): placa real + T2.8; T4 apenas se nota a tamaño web y T1.4
  borra la cruz y los santos. Sus 3 arreglos (retablo caliente, humo desenfocado, motas blancas) están en v5.
- **Peso:** 510 → 287 KB por 5 s a 1080p (el fondo desenfocado comprime mucho mejor). Costura 0.66 → 0.45.

Cadena (escritorio, r7): `placa_real.py` → `montar_r7.sh` (copia del montaje con IN/OUT, sin pérdida) →
`FOCO_MASK=… dof.py … 0.68 0.68 9` → `halacion.sh`. Assets en `tmp/cine-look/`: `r7_v5.mp4`, `sbs_actual_vs_v5.mp4`,
`sbs_textura_4.mp4`, `fable/` (los 6 cuadros que vio Fable), `cmp_v5_100.jpg`, `NOTAS.md`.

## Answer
Decidido por el usuario el 2026-10-09 con los lado a lado:
- **Transiciones a 24p con obturador de 180°**: FILM ×8 → promedio centrado de 4 de 8 subcuadros, las 2 puntas sin
  barrido; la vuelta es la ida invertida. En producción va **antes** del LOOK (hoy se probó sobre la ida ya gradada).
- **Halación + difusión, versión fuerte**, en todos los loops y transiciones, después del LOOK.
- Loops a 24p sin obturador; grano en HTML; sin recorte de formato.
- **Placa real + foco de lente T2.8** (v5) como base del santuario: aprobado por el usuario el 2026-10-09 ("we keeping
  that"). Falta llevarlo a la vertical y a las transiciones (éstas piden profundidad por cuadro).
- Siguiente (usuario): un sujeto/objeto en el centro del cuadro para que el bokeh tenga más protagonismo.
