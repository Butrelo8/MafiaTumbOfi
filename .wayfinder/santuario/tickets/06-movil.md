# 06 — Versión móvil 9:16
Type: prototype · Status: open · Blocks: 09 · Blocked by: 03 · Assignee: —

## Question
¿Cada toma tiene su propia cámara vertical en Blender (render y generación aparte) o sale de recortar la
horizontal? Prueba con la transición nave → sacristía: un travelling lateral en vertical tapa con el pilar
mucho antes. ¿Cambia el movimiento en móvil?

## Prueba (2026-10-05)
**Recortar la horizontal está descartado** por el 04 (un 9:16 de 1280×704 deja 396 px reales de ancho). Queda: ¿misma
cámara en vertical o cámara propia? Medido en `blender/transicion.py` (proyección de cajas y rayos, `tmp/movil-06/`):
- **Misma cámara a 704×1280** (35 mm, el sensor de 36 pasa a lo alto → 31.6° de ancho): se salen el contrabajo
  (u 0.97–1.36), el Cristo, la urna, y en la sacristía la lámpara (1.11–1.43) y el neón (1.32). No sirve.
- **Cámara vertical propia, misma trayectoria** (`build(movil=True)`, `MOVIL`): 28 mm, `shift_y` −0.25 (sube el sujeto y
  deja el hueco abajo, ticket 03), nave x 0.8, sacristía x 45.2. Mismo travelling lateral, 2.5 s, smoothstep; el
  recorrido es casi igual (5.6 m contra 5.7). Hoja de candidatos gris: `hoja_nave.jpg`, `hoja_sac.jpg` (V0 misma cámara,
  V1 la elegida, V2 24 mm / −0.32: sujetos diminutos).
- **El pilar no tapa "mucho antes"**: cobertura por cuadro con rayos (24×24). Escritorio: entra 24–31, negro 32–36 (5),
  sale 37–43. Vertical V1: entra 20–25, negro 26–32 (**7**), sale 33–36. El barrido es más rápido (el pilar cruza un
  cuadro angosto) y el negro dura 2 cuadros más; el corte va al índice 29 en vez del 35.
- **Real:** Klein a 944×1712 (3 semillas; nave s33, la única con el requinto en la bocina; sacristía s22 relight), H3
  704×1280 en las dos mitades (153 s + 140 s), máscara de oclusores, LOOK. Uniones: placa → ida 4.58 (el 11 midió
  3.7–6.9 y lo cubre la mezcla de 0.15 s), ida → sacristía 2.01; el negro entra 11.2 → 4.6 (el 11: 11.6 → 7.1 → 1.8).
  Peso: ida 411 KB, vuelta 386 KB (H.264 crf 23, sin capas vivas: las placas van quietas).
- **19.5:9 recorta:** un teléfono de 390×844 con `cover` pierde ~8 % por lado de un cuadro 9:16. En la sacristía se va el
  neón (u 0.9) y medio sahumador en la nave. Zona segura u 0.08–0.92.

Assets (`tmp/movil-06/`, ignorado): `web/index.html` (`python3 -m http.server 8806` desde `web/`), `hoja_klein.jpg`,
`hoja_ida.jpg`, `shots.jpg` (390×844), `klein.sh`, `h3.sh`, `montar.sh`, `medir.py`.

### v2: comparación con la placa de escritorio y polvo en la luna (2026-10-05)
El usuario pidió comparar la placa vertical con la aprobada de escritorio (13 r6) antes de hacer el loop.
- **Lo que la v1 cambiaba** (s33, sin referencia): la cruz de neón dentro de un nicho rojo con muro de piedra visible atrás
  (en r6 flota sobre negro); Cristo claro y clavado al pilar (en r6, Cristo negro en cruz de pie dentro del arco); sin
  sahumador ni vaso rojo en la bocina (en su lugar dos velas blancas) y un brasero **con llama** sobre un pedestal a la
  derecha del contrabajo; el requinto fundido con el woofer; un solo haz de luna; velas de más en las cabeceras de las
  bancas; piso de losas mojado y brillante. La urna no sale (queda fuera de cuadro, esperado).
- **Klein con referencia** (`preset_edit_ref`: el nodo de 2 imágenes de `preset_edit`, maqueta + placa r6): corrige todo lo
  anterior objeto por objeto (`klein_ref.sh`).
- **Pero Klein ignora el `shift_y` de la lente:** superpuesta a la maqueta, toda placa vertical (v1 incluida) baja ~15 % y
  crece (recentra el horizonte). Arreglo exacto: maqueta **sin shift en un lienzo más alto** (704×1920, sensor 54 mm a lo
  alto = mismo píxel) y recorte de los 2/3 de abajo: igual al encuadre con shift (diferencia media 0.02). Así coinciden
  maqueta y placa (s11, s33; la s22 vuelve a bajar el contrabajo). Elegida **nave s33** (`klein_alto.sh`) y **sacristía s33**
  (`klein_sac_alto.sh`, foto + relight). Klein entrega 768×2112 (≈1 % de otra proporción).
- **H3 de nuevo** (`h3.sh`, V=c): uniones placa → ida 3.6, ida → sacristía 2.98. Ida 485 KB, vuelta 486 KB. Defecto: al
  avanzar, H3 aclara el piso (luma de la mitad de abajo 29 → 46; con prompt "el piso no cambia", 50 → 46). Pasa sólo
  durante la ida, con el texto oculto.
- **Polvo en los haces de luna** (pedido del usuario, escritorio y móvil): `polvo.py`, post sobre la placa como `velas.py`.
  Mapa de luz fría de la placa (clara, B ≥ R, poco saturada) limitado al aire (arriba de `techo`: 0.62 escritorio, 0.33
  móvil); motas en órbitas cerradas (loop exacto: costura 0.039 contra 0.036 de mediana), brillo según el haz y destello
  lento; 5 % grandes y desenfocadas; el haz respira ±7 % con ruido que da la vuelta. **Escritorio r7** = r6 + polvo
  (`polvo/montar_r7.sh`): 472 KB (r6 417). Las motas sobreviven al LOOK y a H.264 crf 23. Móvil: en el loop de la nave.

Assets nuevos: `comparar.jpg`, `zoom_*.jpg`, `hoja_ref.jpg`, `hoja_ov.jpg` (maqueta al 50 % sobre cada placa),
`hoja_alto.jpg`, `hoja_sac_alto.jpg`, `zoom_33.jpg`, `hoja_luna.jpg`, `polvo/r6_r7.jpg`. r7 también en `tmp/placa-13/` (tecla 8).

### v3: zona segura de 19.5:9 y nave vertical viva (2026-10-05)
El usuario aprobó la placa con referencia y el polvo ("excelente ambas") y pidió mover la cámara y animar la nave vertical.
- **Sacristía a x 45.4** (`MOVIL["sac_fin"]`): neón en u 0.82–0.84 (con 45.3 quedaba en 0.88, sin margen para el rojo
  que pinta en la pared); tornamesa 0.28–0.48. El negro del pilar pasa a 25–31 → corte en 28 (`CUT` en `montar.sh`).
  Klein de lienzo alto otra vez (`POSE=45 klein_sac_alto.sh`, s33) y H3 de las dos mitades (`V=d`). Uniones 3.59 / 2.94;
  ida 485 KB, vuelta 492 KB. En 390×844 el neón ya se ve.
- **Nave viva** (`viva/`, el método del ticket 13 sobre la placa vertical): zonas a mano (`zonas.py`: neón fijo, vaso
  rojo y brasas del sahumador por H3, 3 cirios del altar, 3 veladoras de bancas, 2 del piso; candelero y vitrina como
  racimos; humo con el clavijero del requinto fuera); H3 704×1280, 141 cuadros, 40 pasos, canny de la placa: **1123 s,
  cabe en 12 GB** (mismos píxeles que 1280×704). Sin RTX: H3 ya sale a la resolución de móvil. Velas en post
  (`velas.py`), polvo encima, humo en loop de 60, LOOK. **236 KB por 5 s.**
- Medido (`viva/medir.py`): humo desv. 6.95; llamas 0.7–2.2 (chicas a 704 de ancho: titilan sutil, como en escritorio);
  neón 0.31 (fijo); contrabajo 0 → 60: 0.23 (quieto). Costura codificada 0.53 contra 0.09 de mediana, concentrada en el haz
  y en el humo: es el "pop" de grano del cuadro intra (sin pérdida, en el haz: 0.199 contra 0.176), el mismo del 13.
- **Bug de `velas.py`:** si el punto más brillante de una caja cae en su borde (caja corrida o una llama vecina dentro
  del margen de 10 px), la caída radial divide entre cero y mete NaN en la placa. Copia de `viva/` con `max(1, …)`; la
  causa real eran dos cajas corridas (cirios del altar en x 276/295, no 237/255).

### v4: la bocina flotaba → sub + bocina en el piso (2026-10-05)
El usuario: en vertical la bocina "pareciera que está flotando" sobre la banca. Causa: en la maqueta iba en el asiento,
detrás del respaldo (bien apoyada), pero Klein le dibuja la base con placa de marca **sobre el remate de 12 cm** y el
requinto también se para en el remate: se lee como una caja de 1 m balanceada en un riel. En escritorio pasa igual.
- **Sub en el asiento asomando 10 cm** (la idea del usuario): Klein lo ignora en 6 de 6 (negro sobre negro; la referencia r6
  arrastra la bocina vieja). `hoja_sub.jpg`.
- **Sub + bocina en el piso, frente a la primera banca** (aprobado para seguir): `instrumentos()` en `blender/transicion.py`:
  sub 0.5 × 0.75 × 0.6 m (hondo, como uno de 18"), bocina de 75 cm encima hacia atrás, requinto **parado sobre el sub** y
  recargado en la bocina (en el piso, el borde del cuadro de escritorio le cortaba el cuerpo), sahumador y vaso rojo arriba,
  dos veladoras del piso movidas. BVH: sólo contactos de apoyo. El requinto lleva material **madera clara** en la maqueta:
  en gris, delante de la bocina negra, Klein lo fundía con el woofer (y se quitó "woofer" del prompt).
- Placas (`klein_pila.sh`): escritorio sin referencia, **s22** (casi idéntica a r6 salvo la pila); vertical con la s22 como
  referencia en lienzo alto, **s33** (coincide con la maqueta). `placas_pila.jpg`, `zoom_pc3.jpg`, `hoja_pila3_h.jpg`, `hoja_pc3.jpg`.
- Antes de H3 el usuario pidió **más props y gente** en las bancas vacías (siguiente sesión, ver handoff 2026-10-05).
