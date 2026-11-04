# Look de cine en el santuario (2026-10-09) — prototipo, sin decidir

Base: investigación de visual-lab `cross-tool/lab/orbit-movie-look/NOTES.md` (obturador sintético, 1.85, gradación).

Qué aplica aquí y qué no:
- **Loops (cámara quieta):** el obturador no cambia nada. Polvo ≤ 1.5 px/cuadro, velas sólo brillo, humo lento.
  Se quedan a 24p.
- **Transiciones (travelling de 2.5 s):** sí. FILM ×8 de `movil-06/web/ida.mp4` (163 s en GPU) → 24p con obturador
  de 180° (4 de 8 subcuadros, ventana centrada). A la máxima velocidad (cuadro 20) la piedra del piso y el contrabajo
  se barren en horizontal; el barrido del pilar se suaviza (12.2 → 10.2). **Pesa 20 % menos**: 497 → 396 KB.
  48p/360° = 472 KB (48p nítido 480 KB: a 48 fps los cambios por cuadro son menores, así que no duplica el peso).
  Pendiente: el primer/último cuadro difieren 1.7/2.2 del original (el empalme con el loop medía 0.87/1.5): en
  producción, dejar sin barrido los 2 cuadros de cada punta (la cámara sale y llega de quieta).
- **Gradación:** el LOOK 2383 se queda. Se suma halación roja en velas y neón + difusión tipo Pro-Mist
  (`halacion.sh`, encima del LOOK): +0.7 % de peso en escritorio, +3 % en vertical.
- **Grano:** ya está en DESIGN.md como overlay SVG en HTML (no horneado: no pesa ni da el "pop" de cuadro intra).
  Sólo falta que se mueva (animación por pasos), en el 09/10.
- **Formato 1.85/2.39:** no aplica; el fondo es a sangre 16:9 y vertical, el layout (03) depende de eso.

Archivos: `sbs_ida_actual_vs_24p180.mp4`, `sbs_r7_actual_vs_halacion.mp4`, `cmp_ida_shutter.jpg`,
`cmp_r7_hal.jpg`, `ida_24p180.mp4`, `ida_48p360.mp4`, `r7_hal.mp4`, `nave_hal.mp4`, `halacion.sh`.

## Textura de rodaje real en la placa (2026-10-09, pedido del usuario: "como cámara de cine + lente profesional")

Lo que delataba la placa al 100 %: todo nítido de 2 m a 15 m (un T2 en una iglesia oscura no puede), superficies
limpias y nuevas, textura de 1.6 MP escalada a 1080p.
- **Placa real (Klein 4 MP sobre la placa vigente):** prompt "frame grab de un largometraje, ARRI Alexa 35 + Cooke S4/i,
  mismo todo, sólo superficies reales y gastadas" (`E:\ComfyUI\workflows\runs\mto_placa_real_s{1,2}.json`),
  ~58 s. Da madera con veta y rayones, bocina raspada, piedra porosa, retablo con pátina. Efectos secundarios:
  sube la luz (luma 40 → 51–60) y corre el cuadro 3–4 px. `placa_real.py` lo devuelve: correlación de fase (corrimiento
  3.4, −0.5) + igualación de histograma por canal a la placa vieja (luma 39.5), y pega las capas vivas
  (velas + polvo) como placa_nueva + (cuadro − placa_vieja). Semilla 2 elegida (menos cambio: 14.4 contra 20.7).
  Pendiente: juntas claras del tezontle (el original también las tiene en la zona del haz; el prompt puede pedirlas oscuras).
- **Profundidad de campo de lente real:** MoGe-2 (ya instalado, nodo core, 2 s) da la disparidad de la placa; `dof.py`
  desenfoca en disco y en luz lineal sólo lo que está detrás del foco (las velas lejanas se vuelven bokeh). Foco en la
  guitarra/bocina, desenfoque de 9 px de diámetro en el fondo a 1920 (≈ 32 mm T2.8 en Super 35 a ~2.5 m). Enfocar el
  contrabajo dejaba blanda la guitarra (va una fila atrás). Lo que queda más cerca que el foco sigue nítido (sin
  desenfoque de primer plano).
- **Peso:** el fondo desenfocado comprime mucho mejor: r7 510 KB → 287 KB (actual + foco) / 296 KB (placa real + foco).
  Costura del loop intacta (0.66 → 0.40).

Archivos: `sbs_textura_4.mp4` (1 actual, 2 placa real, 3 actual + foco, 4 real + foco), `cmp_real_100g.jpg`,
`cmp_actual_vs_real_foco.jpg`, `placa_real.py`, `dof.py`, `montar_r7.sh` (copia con IN/OUT), `disp_r7.png`.

### v5: correcciones de Fable (2026-10-09; el usuario delegó la elección a Fable)
Fable eligió **placa real + foco T2.8 (9 px)** y pidió 3 arreglos. Hechos (`r7_v5.mp4`, 287 KB; `sbs_actual_vs_v5.mp4`):
- **Retablo caliente / guitarra naranja:** la causa era otra: la loop aprobada usa la placa con **DLSS NR**, que oscurece
  el retablo; la placa real partía de la placa sin NR. Ahora `placa_real.py` toma tono y luz de `escritorio_nrplaca.mkv`
  (cuadro 0): histograma + exposición local (σ 40) + color Lab a/b de la aprobada + luminancia fina (σ 8), y con
  `PROF=disp_r7.png` la placa real sólo entra de cerca (lo lejano va desenfocado y el dorado de Klein se leía pálido).
  Retablo 81/68/57 → igual al aprobado con foco.
- **Humo desenfocado:** MoGe veía el muro detrás del humo. `FOCO_MASK=mascara_humo.png` en `dof.py` lo lleva al plano de foco.
- **Motas blancas y juntas claras:** prompt nuevo (`mto_placa_real_s2b.json`: juntas oscuras, raspones oscuros, "no white
  specks", misma exposición). Klein respetó la luz (luma 39.4 contra 39.6). La placa es fija: no hay parpadeo de textura.
- Honesto: con luz y color fijados a la aprobada, lo que aporta Klein es micro-textura (vetas, raspones, poros) cerca; el
  salto de "lente real" lo da el foco. Costura 0.4 (antes 0.66).

### v5 en la vertical (2026-10-09, noche)
Misma cadena que r7 sobre la nave vertical (704×1280). `nave_v5.mp4` 197 KB contra 259 KB de la aprobada con halación
(`nave_actual_hal.mp4`, −24 %); costura 0.56 (antes 0.59; r7_v5 0.54 con la misma medida). Ver en el teléfono:
`web/v5.html` (toca para alternar actual/v5); `sbs_nave_actual_vs_v5.mp4`, `cmp_nave_v5_100.jpg`, `cmp_nave_v5_full.jpg`.
```
PY="uv run -q --with numpy --with opencv-python-headless python -I"; cd tmp/cine-look
$PY alinear_flujo.py ../movil-06/viva/placa.png klein_nave_s2b.png klein_nave_s2b_al.png
PROF=disp_nave.png PROF_LO=0.105 PROF_HI=0.235 $PY placa_real.py klein_nave_s2b_al.png ../movil-06/viva/placa.png \
  ../movil-06/viva/placa_polvo.mkv placa_real_nave.png nave_real.mkv ../dlss5-fondo/placa_polvo_nrplaca.mkv
IN=nave_real.mkv OUT=nave_real_m.mkv ./montar_nave.sh
FOCO_MASK=../movil-06/viva/mascara_humo.png $PY dof.py nave_real_m.mkv disp_nave.png nave_dof.mkv 0.50 0.34 19
./halacion.sh nave_dof.mkv nave_v5.mp4
```
- **Klein redibuja la vertical:** con el mismo prompt (`mto_placa_nave_real_s{2,3}b.json`) el bajo, la guitarra y el
  retablo se mueven 25–47 px en el tercio medio (flujo DIS; escritorio: 3.5 px). No es corrimiento, es geometría nueva:
  la correlación de fase no basta. `alinear_flujo.py` remapea el Klein 4 MP con flujo suavizado (σ 6); bordes de
  guitarra, retablo y bajo coinciden y lo distinto es micro-textura redibujada, que `placa_real.py` sólo toma por debajo
  de 8 px. Semilla 1 cayó en `Fault failed: 2`; no hizo falta reintentar.
- **PROF relativo al foco:** la guitarra está en disparidad 0.34 (escritorio 0.80: la cámara vertical está más lejos y
  el piso llena el frente). Con el rango fijo 0.25–0.55 la guitarra sólo recibía 30 % de placa real; `PROF_LO/PROF_HI`
  (nuevo, por omisión los de escritorio) con el mismo rango relativo al foco: 0.105–0.235. El retablo sale de la
  aprobada (diferencia 0.4).
- **Foco y desenfoque:** foco `0.50 0.34` (guitarra sobre la bocina; el contrabajo, más cerca, queda nítido). El
  argumento de `dof.py` es diámetro a 1920 y se escala por ancho: los ~7 px reales de la vertical son `19`
  (radio máx 3.5; con `7` saldrían 2.6 px de diámetro, casi nada).
- MoGe de la vertical: el mismo grafo API de r7 (sacado de los metadatos de `placa_r7_moge_depth_00001_.png`) →
  `disp_nave.png`. ComfyUI escucha en `172.20.96.1:8188`, no en 127.0.0.1.
