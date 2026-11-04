# Micrófono colgado en la nave — escritorio (2026-10-10)

Spec: `docs/specs/2026-10-10-micro-colgado-design.md`. Resultado: `r7_micro.mp4` (239 KB; v5 287 KB), costura 0.48
(v5 0.54), micro L p99 25.1 ≤ guitarra 26.3 en todo el loop. Lado a lado: `sbs_v5_vs_micro.mp4`.

Cadena (desde la placa aprobada `../placa-13/capillas/placa.png`):
1. Maqueta: `micro()` en `blender/transicion.py`; render gris + alfa a 1712×944 (`esc_gris.png`, `esc_alfa.png`), pegado
   (`placa_pegada.png`).
2. Klein semilla 1 (`mto_micro_esc_s1.json`) → `componer.py` (máscara = lo que Klein cambió cerca de lo pegado) →
   `placa_micro_s1.png`. Klein dibujó el micro 1.4× más ancho y lo dejó tan brillante como la cruz (L 99).
3. Rosa con tallo en espiral: con sólo prompt Klein fundía cable y tallo (y lo bajaba por la rejilla). Lo que funcionó:
   `guia_espiral.py` dibuja una espiral café alrededor del cable real (x 988), tramos de atrás bajo el cable → Klein
   (`mto_micro_guia_s2.json`) → `sobre_rosa.py` (sólo franja del cable y arriba de la rosa) → `placa_micro.png`.
4. `micro_viva.py`: micro dentro de `mascara_micro_ajustada.png` sobre cada cuadro de `../cine-look/escritorio_real_s2b_nr.mkv`
   (v5), luz igualada en anillo, tope de luma 0.85 × guitarra medido en la viva (el LOOK y la halación levantan más el oro),
   brasa: multiplica el brillo cálido de Klein, parpadeo que cierra en 120 cuadros.
5. `HUMO=mascara_humo_micro.png ../cine-look/montar_r7.sh` (humo por detrás: cruza el micro en ~7500 px).
6. MoGe de `placa_micro.png` (`disp_micro.png`: micro 0.97, bocina 0.56, retablo 0) →
   `FOCO_D=0.97 FOCO_MASK=foco_micro.png dof.py … 0.575 0.48 12.5` → `halacion.sh`.

Gotchas:
- Máscara: la "mancha" de diferencias trae trozos del retablo redibujado → quedaban enfocados junto a la rejilla. La
  ajustada (diferencia > 28, huecos rellenados, recortes a mano a la izquierda de la rejilla y bajo ella) es la que va a
  composición, foco y humo. El dorado delante del retablo dorado: GrabCut no separa por color.
- La deriva por flujo DIS no sirve contra una silueta plana pegada (27–40 px falsos); se midió caja contra caja.
- Atenuar contra la guitarra en la placa sin NR no basta: con NR la guitarra queda más oscura. Medir en la viva.
- ComfyUI se colgó dos veces en "Model Initializing" con la 2.ª/3.ª semilla en cola; `start-comfy.ps1` lo reinicia.

## Correcciones posteriores (2026-10-10, ~03:00)
Detalle en `docs/handoffs/2026-10-10-micro-colgado.md` § "Cambios tras NOTAS". Resumen: `TOPE=1.2` (el usuario: más
brillante; oro 42 contra guitarra 27), atenuación sólo del oro por posición (y < 330), rosa entera en las máscaras
(relleno, color y envolvente convexa), espiral cortada en y 232, rosa colgada cabeza abajo (`mto_micro_rosa_s1.json`),
cable negro separado con `guia_espiral.py`. Abierto: a la rosa aún le faltan trozos en el loop (sospechoso: los
recortes a mano de `ajustar_mascara.py` hechos para la rosa vieja). → Resuelto abajo.

## Rosa de Blender (2026-10-10, noche) — cierra "le faltan trozos"
Reconstruir: `./reconstruir.sh` (~5 min, cadena entera desde `atenuar.py`). Antes/después: `rosa_loop_antes_despues.jpg`.

Causa medida: no eran los recortes. La mitad de abajo de la rosa de Klein estaba pintada casi negra (L 2–6 en la placa)
contra un fondo más claro (L 10 → 6 tras el LOOK): se leía como hueco. Además la máscara (diferencia > 28 + envolvente
de la pieza de color más grande) dejaba fuera los pétalos oscuros de abajo a la derecha, que salían de v5 desenfocados.

Cadena nueva de la rosa (el usuario eligió "rosa en Blender" y luego roja, no marfil):
1. `rosa3d/rosa_colgada.py` (Blender headless): asset `rosa-roja.glb` (CC-BY, Lassi Kaukonen, ya en los créditos) sin
   tallo ni hojas, cabeza abajo, cerrada hacia la boca (abierta parecía hongo), cabeza de 13 cm (Klein dibuja el micro
   ~1.3× el real), cámara a 1.8 m a su altura, filo frío grande arriba-izquierda + relleno débil + brasa abajo. RGBA.
   `blender.exe -b --factory-startup --python rosa_colgada.py -- <png> 5 120 80 0.15`.
2. `rosa3d/pegar_rosa.py`: la pega en la placa colgada del tallo de Klein (x 1000, sépalos y 245), color de Klein
   (tono y croma por franja de L: lo oscuro más cálido, lo claro más magenta), grano y suavidad de la placa. Sola se
   veía de fieltro.
3. Klein `mto_rosa3d_roja_s1.json` sobre esa placa ("retouch only the hanging rose… keep its exact shape"): rosa
   fotográfica, capas de pétalo marcadas, abajo carmesí oscuro y no negro. También se probó marfil (`_marfil_s1`).
4. `rosa3d/pegar_klein.py`: Klein corre el cuadro (+3.0, −1.3) px y agranda la rosa ~10 px: se alinea por correlación de
   fase y la máscara es la rosa de Klein (diferencia contra la aprobada, cerca del alfa de Blender, sin oro y, fuera del
   alfa, sólo lo claramente rojo o verde: el pináculo café del retablo bajo el sépalo izquierdo quedaba enfocado) ∪ alfa → `placa_micro_rosa.png`, `mascara_rosa.png`. Va después de `atenuar.py`.
5. `ajustar_mascara.py` toma la rosa de `mascara_rosa.png` (adiós a color, envolvente y diferencia > 12).
6. `micro_viva.py` con `ROSA=mascara_rosa.png`: la rosa llega a y ≈ 351 y el tope "por posición" (y < 330) la
   oscurecía; sus pétalos rojos claros además pasaban por brasa y parpadeaban.
7. `rosa3d/disp_rosa.py`: `disp_micro.png` (MoGe) traía la silueta de la rosa vieja: donde ya no hay rosa decía "cerca"
   y el DOF dejaba nítido un pináculo junto a los sépalos. Se rellena desde el fondo → `disp_micro_rosa.png`.

Gotchas: el inpaint del mapa de profundidad debe tapar también el sujeto, o rellena con "cerca". Klein no tiene fuerza
de edición: redibuja según la instrucción; recortar a ciegas a su alfa de origen corta lo que agranda.

## Loop alargado (2026-10-10, noche; idea del usuario: "el mismo video pero literal alargado", ritmo más relajado)
Sin generar nada: el loop montado (`r7_micro_m.mkv`, 120 cuadros) + su cuadro 0 al final → FILM ×k en ComfyUI
(`E:\ComfyUI\workflows\runs\mto_r7m_film_png_x{2,3}.json` = `preset_60fps` con un SaveImage colgado de la salida IMAGE del
subgrafo) → `largo/alargar.sh <carpeta_png> <k> <salida>` (quita el cuadro repetido, 24 fps, foco, halación con `GOP=N`).
Resultados: `largo/r7_micro_10s.mp4` (344 KB), `largo/r7_micro_15s.mp4` (419 KB), contra 242 KB del de 5 s; costura 0.42
(5 s: 0.38), sin saltos. Lado a lado 15 s: `largo/sbs_5_10_15.mp4` (5 s ×3 | 10 s | 15 s).
Gotchas: el SaveVideo de ComfyUI comprime a ~0.8 Mbps (salto de calidad a media toma) → guardar PNG. x264 mete un
cuadro clave a los 250 y en lo oscuro se ve el salto: `halacion.sh` acepta `GOP` (por omisión 250, igual que antes).
**Descartado (el usuario):** "muy lento, el humo y la flama se ven chopeadas". Medido: en ×3 FILM pone sus dos cuadros
intermedios casi juntos (pasos 0.38 / 0.08 / 0.37: avanza a tirones); en ×2 la cadencia es pareja pero en humo y fuego
FILM funde en vez de mover. Interpolar no sirve para fluidos.

## Humo en el periodo completo (2026-10-10, el usuario: "mejor el derecho")
`montar_r7.sh` hacía del humo un loop propio de 60 cuadros fundido de punta a punta (ticket 13, r3): cada cuadro es
mezcla de dos momentos y se repite cada 2.5 s. `largo/montar_largo.sh` (copia parametrizada: N, X, H3) pasa humo y
llamas por el mismo loop de N cuadros con fundido de X al cerrar. Con N=120 sobre el loop actual: `largo/r7_micro_humo120.mp4`,
lado a lado `largo/sbs_humo60_vs_120.mp4`. Costura igual (0.38). Va en todas las versiones nuevas.

## Loop de 10 s con movimiento real (2026-10-10, noche)
Largo: múltiplo de 120 (velas y polvo vienen horneados en loops de 120 con el NR de DLSS, que no se rehace aquí) →
240 cuadros (10 s) + 20 de fundido de cierre = 260 de H3 (260 = 17·15+5). En esta prueba velas y polvo siguen ciclando
cada 5 s. Prompt calmado: `largo/prompt_calmo.txt` (sin "slow motion": lo de FILM ya era "muy lento").
- **Nativa:** `preset_posevideo_ff` a 928×512 (H3 pide lados múltiplos de 32: 944×520 falla con "shape … invalid"),
  260 cuadros, canny `ctl260.mp4`, 20 pasos: 608 s, cabe en 12 GB. RTX ×2 → `montar_largo.sh N=240 X=20` →
  `largo/r7_micro_10s_nativo.mp4` (383 KB). Humo 0.30/cuadro (antes 0.53). El usuario: ese es el ritmo, pero "chopped":
  medido, cadencia irregular (humo: 11 cuadros casi repetidos, 40 saltos > 2× el vecino; la de 141 a 1280×704: 0 y 1).
- **Encadenada (idea del usuario):** tramo 1 (141, 1280×704) → tramo 2 desde su cuadro 130, fundido de 11 cuadros
  (`largo/unir.sh`) → RTX ×1.5 → `largo/r7_micro_10s_encadenado.mp4` (381 KB). Junta sin salto medible, cadencia pareja,
  pero el prompt calmado apenas frenó el humo a 141 cuadros (1.18 contra 1.21). Lado a lado: `largo/sbs_nativo_vs_encadenado.mp4`.
- **Elegida (el usuario): nativa a 40 pasos + suavizado temporal** → `largo/r7_micro_10s_nativo_40p_suave.mp4` (383 KB,
  costura 0.40). El usuario pidió el ritmo de la nativa "pero fluida": a 40 pasos y con `tmix` 1-2-1 los tirones del humo
  bajan de 98 a 11 en el loop final. Reconstruir: `largo/reconstruir_10s.sh`. Lado a lado 20/40 pasos: `largo/sbs_suave_20p_vs_40p.mp4`.
- Pendiente: velas y polvo siguen en loops de 120 (ciclan cada 5 s); hacerlos de 240 pide rehacer velas.py/polvo.py con
  N=240 y el paso de NR. La vertical y las transiciones siguen en 5 s.
- Intermedios borrados (2026-10-10, el usuario): pruebas de FILM, nativa de 20 pasos, encadenada y .mkv sin pérdida; quedan lo elegido, los lado a lado y lo que usa `largo/reconstruir_10s.sh`.
