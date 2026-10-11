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
