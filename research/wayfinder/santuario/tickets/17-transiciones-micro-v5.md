# 17 — Transiciones con el micro y la v5
Type: prototype · Status: open · Blocks: 09 · Blocked by: — · Assignee: claude

## Question
El loop de la nave ya tiene el micro colgado (15) y la v5 (placa real + foco de lente, 14); las transiciones vecinas
(nave → sacristía de ida y vuelta, y la llegada desde el hero del 08) no tienen ninguno de los dos, así que el micro
aparecería de golpe en el corte. La spec del micro lo pone como condición dura antes de cualquier deploy. ¿Cómo se
llevan las dos cosas a una toma con cámara en movimiento?
- **Micro y rosa** en una toma que se mueve: `micro()` en la maqueta y H3 + ControlNet como en el 01, o el sujeto
  compuesto aparte (render de Blender por cuadro, como la rosa del 15), porque H3/Klein lo deforman.
- **Foco de lente** por cuadro: MoGe por cuadro o profundidad desde Blender; ¿tiembla el foco entre cuadros?
- Orden con el obturador de 180° del 14 (FILM ×8 antes del LOOK) y empalme con el loop de 10 s (mezcla de 0.15 s del 11).

## Avance (2026-10-11)
Lo que hay hoy:
- **Vertical:** ida/vuelta de 60 cuadros (`tmp/movil-06/h3.sh` + `montar.sh`: dos mitades de H3 a 704×1280 con
  profundidad de Blender, corte tras el pilar en el cuadro 28) y su versión a 24p con obturador (`tmp/cine-look/web/`).
- **Escritorio:** la última transición es la de `tmp/transicion-4` (864×480, 2026-10-04, placas de antes del 13). Hay que
  rehacerla entera de todos modos (1280×704 del 04, placa r6/v5, obturador del 14).
- La maqueta (`build()`) ya trae la pila (sub y bocina en el piso, 06 v4) y las placas vigentes no: una H3 nueva con la
  profundidad de hoy no coincide con la placa de arranque en los instrumentos.

Medido (cámara con smoothstep, 60 cuadros): el micro **sale del cuadro por la izquierda** en el cuadro 11 en vertical
(0.46 s) y en el 17 en escritorio (0.71 s), mucho antes del pilar. En ese tramo el ángulo de vista cambia ~13° (vertical)
y ~31° (escritorio); micro y rosa son casi de revolución alrededor del cable.

Caminos para el micro:
1. **Capa 2D seguida con la cámara de Blender** sobre la transición (el sujeto aprobado de cada formato, corrido y
   escalado por la proyección del micro cuadro a cuadro, con su máscara y la brasa). Sin H3; el giro de 13–31° no se ve
   en un objeto de revolución, pero sí la falta de paralaje interno.
2. **Micro en la maqueta y H3 lo dibuja** desde la placa con micro: riesgo de que lo deforme (lo que llevó a la rosa de
   Blender), y pide resolver antes lo de la pila en la profundidad.
Para el foco de lente por cuadro: profundidad de Blender (exacta y sin parpadeo; la pila queda detrás del micro, donde
igual se desenfoca) o MoGe por cuadro (sigue lo que dibujó H3, puede parpadear).

### Prueba vertical: micro como capa seguida + foco con la profundidad de Blender (2026-10-11)
Elegido por el usuario: capa 2D seguida con la cámara y profundidad de Blender. `tmp/micro/trans/` (`armar_ida.sh`):
- Pista del micro en Blender (`pista_micro.py`): la cámara vertical va de lado a altura fija y el micro queda a 1.8 m en
  todo el tramo (z constante, v constante): la capa sólo se corre en u, sin escala. Sale del cuadro en el cuadro 11.
- La capa es el sujeto del loop vertical aprobado (cuadro 0 de `micro/movil/nave_micro240.mkv` dentro de
  `mascara_trasplante.png`), con **desenfoque de movimiento de 180° exacto** (caja horizontal de medio desplazamiento por
  cuadro: para una capa que sólo se traslada es lo mismo que el obturador).
- Foco por cuadro con `movil-06/z/T` (anterior a la pila, coincide con las placas): plano en el micro (z 0.634), sólo en
  la mitad de la nave (el corte cae en el negro del pilar); coc 27.6 calibrado para que el retablo se desenfoque igual
  que en el loop. LOOK y halación después, como los loops.
- `ida_micro.mp4` 452 KB (la vigente 485), `vuelta_micro.mp4` 437 KB. Empalme loop → ida en el cuadro 0: 6.43 (antes,
  loop v5 → ida vigente: 9.33). Vista previa loop → ida → sacristía, vigente | nueva: `preview_viejo_vs_micro.mp4`.
- Falta: el obturador de FILM ×8 del 14 en el fondo (va antes del LOOK) y la placa real (v5) por cuadro; escritorio
  entero (rehacer desde la H3).
- Visto por el usuario: bien. **Obturador del 14 añadido** (2026-10-11): FILM ×8 del fondo sin micro (`gen.sh
  runs/mto_r7m_film_png_x2 … 16.value=8`, 473 subcuadros; el copiado de `gen.sh` falla con un prefijo con subcarpeta: los
  PNG se toman de `E:\ComfyUI\ComfyUI\output\mto\ida_micro_film8`) → `obturador.py` (promedio centrado de medio intervalo
  en luz lineal, cuadros 0–1 y 58–59 sin barrido) → micro, foco, LOOK y halación. `ida_micro.mp4` 452 → **397 KB**,
  `vuelta_micro.mp4` 380 KB. La vista previa ahora compara contra la ida vigente con obturador (`cine-look/web/ida.mp4`).

### Escritorio desde cero (2026-10-11)
`tmp/micro/trans_esc/`. La última transición de escritorio era de 864×480 y no hay placa de sacristía de escritorio
moderna. Pases de Blender con la maqueta **de antes de la pila** (`git show cccf32c:blender/transicion.py`; coincide con
la placa r6, sin dobles al superponer): T a 1280×704 (gris, z, máscara) y los grises en reposo a 1712×944 (`pases.py`).
Sacristía con Klein de 2 imágenes (maqueta + la sacristía vertical aprobada como referencia, `klein_sac.sh`), 3 semillas:
`hoja_sac.jpg` (maqueta | s11 / s22 | s33). s11 y s33 respetan la maqueta (s33 con dos cuadros); s22 mueve la lámpara.
**Pendiente: que el usuario elija.**
- **Elegida por el usuario: s11.** H3 de las dos mitades a 1280×704 con la profundidad de antes de la pila (`h3_esc.sh`,
  ~150 s cada una), corte en 34 (negro del pilar 32–36, medido con la máscara). `armar_ida_esc.sh`: máscara de oclusores →
  FILM ×8 + obturador **a 1280×704** (a 1080p FILM guardaría ~12 GB de cuadros) → RTX ×1.5 → 1920×1080 → micro seguido
  (sale del cuadro en ~0.7 s) + foco por cuadro (coc 13.0, calibrado contra el loop de escritorio) → LOOK → halación.
  `ida_micro.mp4` **774 KB**, `vuelta_micro.mp4` 770 KB; empalme loop → ida 7.65. Vista previa loop → ida → sacristía
  quieta: `preview_esc.mp4`. Peso: con el loop de 354 KB el gesto pasa de 1 MB (el tope del 05 es para móvil; en
  escritorio no hay tope escrito). Visto por el usuario: bien. Falta la placa real (v5) por cuadro, un loop de la
  sacristía de escritorio (s11) y bajar el peso.

### Peso: la cascada de códecs del 05 (2026-10-11)
`tmp/micro/trans_esc/cod/`. El 05 ya decidió AV1 → HEVC → H.264 (un `<source>` por códec); aquí se calibra con la ida.
`halacion.sh` acepta `VC` (p. ej. `VC="-c:v ffv1"`) para sacar un maestro sin pérdida y codificar desde él, no desde el
H.264; sin `VC` sale byte a byte igual que antes. `ladder.sh <maestro> <prefijo>`: tamaño y SSIM contra el maestro, `-g 60`.

| Códec | Escritorio | Vertical |
|---|---|---|
| H.264 crf 23 (vigente) | 755 KB | 387 KB |
| H.264 crf 26 | 517 KB | 263 KB |
| HEVC crf 26 (`hvc1`) | 358 KB | 210 KB |
| HEVC crf 28 | 279 KB | 160 KB |
| AV1 crf 40 (SVT, preset 4) | **172 KB** | **107 KB** |
| AV1 crf 45, 10 bits | 123 KB | 77 KB |

El SSIM queda en 0.962–0.968 en todos (el piso lo pone el ruido fino, no distingue). Al 100 %
(`hoja_codecs.png`: micro, piedra oscura, muro de la sacristía; maestro | H.264 23 | HEVC 26 | AV1 40 | AV1 45) AV1 40 y
HEVC 26 no se distinguen del maestro; AV1 45 suaviza la piedra. Para ver en movimiento con el mismo cuadro:
`index.html` (teclas 1–4) desde `trans_esc/cod/`.

### Detalle: la ida se veía blanda (2026-10-11)
El usuario, viendo los códecs: "se ve muy blurosa, y no hablo del blur intencionado". No era el códec (el maestro sin
pérdida igual). Medido por etapa (`hoja_etapas`, Laplaciano por cuadro): H3 a 1280×704 pierde detalle al moverse (123 →
57 → 31 en los cuadros 0, 10, 20) y RTX ×1.5 no lo devuelve; la halación + Pro-Mist "fuerte" lava el muro iluminado de la
sacristía; además H3 arrancaba de la placa r6, no de la v5. El usuario pidió probar las cuatro salidas:
- **H3 a 1920×1056** (`W=1920 H=1056 NAVE=../../cine-look/placa_real_s2b_nr.png TAG=_1056 ./h3_esc.sh`; 39 cuadros × 2 MP
  caben en 12 GB, 390 + 372 s a 20 pasos) desde la placa v5 → `armar_hd.sh hd_h3` (sin RTX, FILM ×8 a 1920×1056).
  Detalle real en piedra, retablo y Cristo; empalme loop → ida **7.65 → 5.17** (arranca de la misma placa que el loop).
  AV1 crf 40: 197 KB.
- **Detalle de la placa real** (`detalle.py`, `DET=1 armar_hd.sh hd_det`): la cámara sólo se corre en x dentro de cada
  mitad, así que la placa se reproyecta exacta con la Z de Blender (x + f·Δx/Z) y entra como razón P/G(P) donde la Z
  coincide y la luz baja se parece (con desfase, no ganancia: H3 baja el negro ~0.015). **H3 no sigue el tiempo del
  control**: en la sacristía de 1280 va 27 px donde la cámara pide 108 (cuadro 7) y casi lineal; se busca, por cuadro, la Δx
  de cámara que reproduce a H3 (1D a 1/4 y continua). Con H3 a 1080p aporta poco más (H3 ya se acerca a la placa); el
  flujo residual pasa de 8 px hacia el cuadro 15 y ahí no entra (lo tapa el obturador). AV1 189 KB.
- **Difusión más ligera** (`halacion.sh … 0.5 0.2` en vez de 0.8 / 0.45): devuelve la textura dentro del charco de la
  lámpara. Ojo: los loops se aprobaron con la fuerte; para el empalme, va en todo o sólo durante el movimiento.
- **SeedVR2 ×1.5 en vez de RTX** (`seedvr_esc.sh`, 181 s): mucho más filo pero sobreafilado (talla "grabada"), vira a
  amarillo y satura (rompe el grado del loop) y en reposo cambia ~40 % más por cuadro (4.5–5 contra 3.5, alternando): detalle
  inventado que titila, como FlashVSR en el 04. AV1 301 KB.
Para ver con el mismo cuadro: `detalle_web/index.html` (teclas 1–5: vigente, H3 1080p, + placa, + difusión ligera, SeedVR2;
todos H.264 crf 16).
- **Elegido por el usuario:** base **H3 a 1080p + detalle de la placa** (`hd_det`) y difusión **ligera sólo al moverse**:
  `mezcla_difusion.py` mezcla por cuadro el maestro fuerte (0.8 / 0.45, empalma con los loops) y el ligero (0.5 / 0.2) con
  la velocidad del smoothstep, 6t(1−t)/1.5. Cascada del 05: ida **AV1 189 KB** (vuelta 194), HEVC 375, H.264 794
  (`hd_det/ida_final_*.mp4`); antes 774 KB en H.264. Tecla 6 de `detalle_web/`. Falta la vertical con el mismo método y
  todo esto se rehace sobre las placas con la pila (06).

## G7: las transiciones sobre la nave con la gente (2026-10-13)
Todo en `tmp/g7/{esc,vert}/` (ignorado). Mismo método que lo aprobado arriba, con la placa real G4, la maqueta actual y
el micro de G6 (tallo nuevo, luz C).
- **Pases** (`pases.py`): `blender/transicion.py` actual (pila, gente, espiral pegada) **sin el micro**: la maqueta del 17
  no lo tenía y el micro va como capa 2D seguida (camino 1, elegido por el usuario); con él en la profundidad, H3
  dibujaría un segundo micro bajo la capa. Pistas del micro (`pista_micro.py`) iguales a las del 17 (u idéntica).
- **Sólo cambia la mitad de la nave.** La profundidad y la máscara son idénticas a las del 17 desde el cuadro 334
  (escritorio) y 328 (vertical); el corte toma la sacristía de 335/329 en adelante, así que T3r (y su detalle de
  escritorio) se reutilizan tal cual. H3 sólo para T1: escritorio 1920×1056 ~414 s, vertical 704×1280; semilla 7;
  prompts en `prompts/g7-transiciones/` (la nave de G6: gente, velo, rosas, copal en la bocina).
- Escritorio: H3 inventa un altar lateral con velas a la derecha antes del pilar (cuadros 20–28); el copal sale ya con
  llamas en la placa G4. El usuario siguió con s7. Cadenas: `tmp/g7/esc/armar.sh`, `tmp/g7/vert/armar.sh`.
- **Copal en el arranque de escritorio.** La primera pasada salió de `nave_g4_esc.png`: el cuadro 0 traía llamas abiertas
  en el cuenco y no el copal del loop congelado. Rehecha desde `tmp/g6/copal/nave_g6_esc_real_copal.png` (también para
  `detalle.py`) con el prompt del humo saliendo del cuenco (`h3g7c_T1_s7`, 391 s; salidas en `ida_c/`, `cod/c/`).
  Empalme loop → ida en el cuadro 0: diferencia media 7.1, igual que el 17 contra su loop (7.0); vertical 4.3.
- **Aprobado por el usuario y congelado** (`entrega/`): escritorio AV1 211 KB / HEVC 411 / H.264 860, vuelta AV1 215;
  vertical H.264 374 / AV1 105 / HEVC 207, vuelta H.264 364. Vertical con el método del 17 (sin el detalle de 1080p):
  sigue pendiente pasarla al método de escritorio, como dice arriba.
