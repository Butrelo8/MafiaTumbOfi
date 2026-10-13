# 06 — Versión móvil 9:16
Type: prototype · Status: open · Blocks: 09 · Blocked by: 03 · Assignee: claude

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

> Nota (2026-10-10, [15](15-micro-colgado.md)): la vertical queda sin el micro colgado. Va con la misma cadena del 15
> (`MOVIL["micro"]`: foco u 0.35, v 0.24; Klein redibuja la vertical 25–47 px, así que pegar y refinar con máscara, no
> flujo; rosa desde Blender con la cámara vertical). El largo del loop vertical lo decidió el [16](16-loops-de-10s.md): 10 s, H3 a 512×928, sólo lo que se mueve.

## Estado (2026-10-11)
Lo que falta para cerrar el 06, en dos ramas que no se han decidido:
- **Vertical con el micro** (spec del micro: `MOVIL["micro"]`, foco u 0.35 / v 0.24) sobre la placa vertical vigente
  (`movil-06/viva/placa.png`, anterior a la pila) y el loop de 10 s del 16 (`micro/largo/capas240/nave_10s_240.mp4`).
- **Pila y props/gente** (handoff `docs/handoffs/2026-10-05-movil-y-props.md`): sub + bocina en el piso aprobados "para
  seguir" (v4) y la prueba de señora con rebozo, nardos, texana con rosario y joven de gorra, **nunca corridos**. Todo lo
  hecho después (v5, micro, 10 s) está sobre las placas de antes de la pila (r6 y viva): hacer la pila ahora rehace placas
  y loops de los dos formatos.
- El usuario eligió primero **el micro en la vertical** (2026-10-11); la rama de pila y props/gente queda **abierta, sin
  decidir** (no descartada), así que el 06 no cierra con el micro.
- **Decidido por el usuario (2026-10-11): pila + props/gente ahora**, con stills de escritorio y vertical antes de H3 (el
  plan del handoff del 2026-10-05); después se rehacen placas, loops y las transiciones del 17 en los dos formatos.

### v5: micro en la vertical, stills (2026-10-11)
`tmp/micro/movil/`. Maqueta vertical headless (`render_movil.py`, `build(movil=True)`): micro en u 0.35, v 0.24 como en la
spec. La maqueta trae la pila (bocina y sub en el piso) y la placa vertical vigente no: sólo se usa el alfa del micro.
- **Trasplante** en vez de rehacer la cadena de escritorio (desvío de la spec, que pedía la misma secuencia): las dos
  cámaras ven el micro casi de frente (4° y 6° de lado), así que el micro y la rosa **aprobados** de escritorio
  (`placa_micro_rosa.png` dentro de `mascara_micro_ajustada.png`) se escalan 0.598 (28 mm sobre 1280 contra 35 mm sobre
  1712; los alfas dan 45/75 = 0.60) y se anclan por la silueta del alfa (correlación 0.984) → `trasplantar.py`,
  `placa_trasplante.png`. Conserva rosa, espiral, oro viejo y la brasa dentro de la rejilla.
- **Klein encima** (`klein_v.sh`, 4 MP, 3 semillas, "integra al cuadro, misma forma") + `componer_v.py` (sólo dentro de la
  máscara dilatada; deriva del sujeto caja contra caja): s1 24 px y s2 30 px (no valen), **s3 2.4 px**. s3 integra luz y
  grano, pero aclara el oro a amarillo, quita la brasa y agranda la rosa con filo de luz. `candidatos_v_100.jpg`
  (trasplante | s3), `candidatos_v_full.jpg`. **Pendiente: que el usuario elija.** Después: `micro_viva` vertical (tope
  contra la guitarra, máscaras de humo y foco, disparidad rellenada) sobre el loop de 10 s del 16.
- **Más semillas** (pedido del usuario; `prompt_klein_v2.txt`: oro viejo oscuro, brasa visible, rosa del mismo tamaño):
  s4, s5 y s6 conservan oro viejo y brasa, pero Klein corrió el cuadro ~21–24 px (s4, s5) o el sujeto 25 px (s6). Con
  `SUJETO=1` en `componer_v.py` el sujeto de Klein se corre de vuelta a su sitio (deriva que queda ≤ 0.4 px) y se compone
  con la máscara exacta, sin dilatar (borde y fondo de la placa). `candidatos_v3_100.jpg`: trasplante | s3 | s4 | s5 | s6.
- **Elegida por el usuario: s4** (`placa_micro_vb_s4_suj.png`). Loop vertical de 10 s con el micro (`armar_micro_v.sh`:
  base de 240 "rápido" del 16, `micro_viva_v.py` con la caja de la guitarra y el corte de la rosa de la vertical, humo por
  detrás del sujeto, foco en el micro con disparidad 0.60 = guitarra 0.341 × 1.77 de escritorio, ~10 px de fondo,
  `montar_mov_v.py`, halación): `tmp/micro/movil/nave_micro_10s.mp4`, **222 KB**, costura 0.40; lado a lado sin | con
  micro `sbs_sin_con_micro_v.mp4`. Oro L p99 30.2 contra el cuerpo de la guitarra 28.6 (1.06×; en escritorio el usuario
  lo dejó ~1.4×): el anillo de luz lo bajó 0.84 y el tope no actuó (la caja vertical incluye una veladora).
  **Igualado a escritorio a pedido del usuario:** `GANA_ORO=1.26` (sólo el oro) → oro 42.7 contra guitarra 28.6, **1.49×**,
  la misma razón que escritorio medida igual (41.6 / 27.8). 222 KB, costura 0.41. Reconstruir:
  `GANA_ORO=1.26 tmp/micro/movil/armar_micro_v.sh placa_micro_vb_s4_suj.png mascara_trasplante.png nave_micro_10s.mp4`.
  Falta: que el usuario vea el loop; y la rama de pila y props/gente.
- **Visto por el usuario (2026-10-11): bien.** El micro en la vertical queda; el 06 sigue abierto sólo por la rama de pila
  y props/gente.

### v6: pila + props/gente, maqueta (2026-10-11)
`props()` en `blender/transicion.py` (asientos en `PROPS`), `tmp/props-06/`. Asientos medidos con rayos en las dos cámaras
(`medir_asientos.py`; ojo: sin fijar la resolución, la vertical se proyecta a 16:9 y da otra u). Contactos BVH en
`render_props.py`: figuras en el asiento, texana en el remate (en el asiento la tapa el respaldo: desde la cámara sólo se ve
arriba de z 0.87), rosario contra el respaldo, nardos en el brazo de las cabeceras del pasillo, filas 2–6, los dos lados.
Tonos: con rebozo 0.1 / pelo 0.07 las figuras se perdían en el muro; subidos a 0.2 / 0.15, cuerpo 0.38.
Disposición (`disposicion.py`, `hoja_disp_esc.png`, `hoja_disp_vert.png`, verde = props, con el micro):
- **A, los asientos del handoff** (señora fila 4 x 1.9, joven fila 3 x 2.3, texana fila 6 x 2.3): en escritorio quedan entre
  la bocina y el contrabajo, la cabeza del joven contra la voluta: amontona la esquina de los instrumentos. En vertical se
  leen bien, sobre el contrabajo.
- **B, bancas del fondo** (señora fila 10 x 1.4, joven fila 9 x 2.3, texana fila 7 x 1.0): diminutas (12–13 m), la señora
  detrás del sahumador y bajo el micro.
- Lo libre a la derecha lo ocupan los instrumentos; la izquierda es el hueco del texto (03). Pendiente: que el usuario elija.
- **Klein de escritorio, disposición A** (`klein_props.sh p3`, 3 semillas, sin referencia; `hoja_klein_A.jpg`: placa pila s22
  | s11 / s22 | s33). Klein toma las figuras como permiso para repartir gente: s11 corre el encuadre, agranda los nardos y
  deja la texana en una banca izquierda; **s22** conserva el encuadre de la placa vigente, pero sienta al joven en una banca
  **izquierda** (en el hueco del texto), cuelga el rosario de la bocina y añade otra figura con rebozo; s33 corre el
  encuadre e inventa 4–5 personas. La gente sí se lee creíble (de espaldas, sin cara). El usuario la vio por ssh
  (SendUserFile).
- **Ronda 2** (el usuario: "una mujer con velo y un joven con gorra, no varios", con variedad): en la maqueta la señora lleva
  velo de encaje claro (0.55, sólo cabeza y hombros) en vez del rebozo; prompt estricto ("exactly two people… the pews on
  the left side are completely empty"), semillas 22, 44, 55 sin referencia (`SEMILLAS=… klein_props.sh p4`,
  `hoja_klein_A2.jpg`). **s22** conserva el encuadre de la placa vigente y trae justo las dos figuras a la derecha, bancas
  izquierdas vacías y los nardos en el pasillo; falla en el rosario (vuelve a colgar de la bocina) y la texana no se
  distingue. s44 y s55 corren el encuadre y añaden gente (s44 deja la texana en una banca izquierda).
- **Elegida por el usuario: s44** (abajo a la izquierda en `hoja_klein_A2.jpg`), aunque corre el encuadre y deja la texana a la izquierda. Sigue la vertical con s44 de referencia.
- **Vertical** (`klein_props_v.sh p4 klein/nave13props_p4_s44_00001_.png`, lienzo alto + s44 de referencia, 3 semillas;
  `hoja_vert_A2.jpg`: placa vigente | s11 | s22 | s33). La maqueta al 50 % sobre s33 (`hoja_ov_v.jpg`) coincide en
  arquitectura, instrumentos y gente (cabezas en u 0.68 / 0.82, v 0.31): las dos figuras quedan justo detrás del
  contrabajo, como en la maqueta A; el velo toca el mástil en s11 y s22. La texana cae al piso junto al contrabajo (s11,
  s33). Ojo: el prompt base termina en "no people" (desde el 13), que contradice a la gente; Klein la dibujó igual,
  pero hay que quitarlo en la siguiente ronda.
- El usuario: la vertical tiene que ver **lo mismo que escritorio** (mismos sujetos, nada distinto; el ángulo está bien).
  s44 tiene tres personas, no dos (añadió un fiel solo en la primera banca derecha, junto al altar) y la texana en el
  remate de la 2.ª banca izquierda, junto al pasillo. La maqueta las sigue (`PROPS`: texana −0.8 / i 1, fiel 1.6 / i 11;
  medido con `medir_s44.py`: escritorio u 0.35 y 0.59 / v 0.55, como en s44; en vertical la texana queda en u 0.07, al
  borde: un 19.5:9 la recorta). Prompt vertical con esos sujetos y sin el "no people" (`klein_props_v.sh p5 …s44…`).
  `hoja_vert_p5.jpg`, `hoja_vert_p5_arriba.jpg`: las tres semillas traen texana con rosario en la banca izquierda y el
  fiel del altar; s11 deja además otra texana en el piso, s22 cuelga otro rosario de la bocina; **s33 coincide con s44**
  sin nada de más (`par_s44_v33.jpg`). Propuesta: s33.
- ~~s44 corrió el encuadre~~: falso. La maqueta al 50 % sobre s44 (`ov_s44.jpg`) coincide sin dobles (altar, bancas, pila,
  contrabajo, cruz); el error fue juzgarlo lado a lado con la placa vieja.
- El usuario: se aprueba sólo si son iguales en los dos formatos los detalles, props y personas (lo que traen puesto y su
  posición). Comparado sujeto por sujeto al 100 % (`detalle_final.jpg`): velo de encaje blanco, joven de sudadera gris y
  gorra negra, fiel de sudadera gris junto al altar, nardos, velas blanca y roja en el remate detrás de la texana:
  iguales. Única diferencia real: s33 colgaba un rosario de la texana y s44 no lo tiene. Quitado con retoque local de
  Klein (`preset_edit`, "remove the rosary…", 1.08 MP): Klein quitó también la texana, así que `pegar_zona.py` pega sólo
  la caja del hilo (x 52–104, y 503–615, alineada por correlación de fase, borde suave) → `nave06props_final.png`.
  Queda: bajo el velo, s44 se ve claro y s33 oscuro. Pendiente: aprobación del usuario.
- Bajo el velo (pedido del usuario: igualarlo): en s44 la mujer lleva un abrigo beige/camello, en s33 ropa negra. Retoque
  local de Klein ("a plain beige camel-coloured coat under the veil", semillas 7 y 8) pegado sólo en la caja de la ropa
  (x 462–528, y 468–548): s7 deja velo y contrabajo intactos; s8 ensancha el velo. `ropa_s44_v33_s7_s8.png`.
  **`nave06props_final.png` = s33 sin rosario + abrigo beige (s7).** Pendiente: aprobación del usuario.
- El usuario, viendo el par final: la texana está en otra banca en cada formato; la bocina está recargada distinto (en s44
  pegada a la banca con el requinto en su frente; en vertical sobre el sub, suelta delante de la banca); y algo "en
  textura de madera" en horizontal sale oscuro en vertical. La texana: en s44 está en la **1.ª** banca izquierda (la
  superposición la pone ahí), no en la 2.ª que estimé de la imagen; la maqueta y la vertical la llevaban una fila atrás.
  Parchar detalle por detalle no converge: dos tiradas de Klein con dos cámaras siempre difieren en algo.
- **Vertical sacada de s44 por reproyección** (elegido por el usuario; "la madera" era la bocina). `pases_reproy.py`:
  profundidad de vista en PNG de 16 bits sin el micro (escritorio 1712×944, vertical 704×1280 con shift) y las dos cámaras
  (`camaras.json`: matriz y `view_frame`, que ya trae shift y ajuste de sensor). `reproyectar.py`: cada píxel vertical al
  mundo con su Z, a la cámara de escritorio, y toma s44 sólo si escritorio ve ese punto (Z dentro del 3 %): 36.9 %
  reproyectado, 56.4 % fuera del cuadro de escritorio (sobre todo el piso de abajo), 6.7 % ocluido. Huecos con la s33
  corregida como base, un pase de Klein ("one seamless photograph… change nothing else", 1.56 MP) y `pegar_huecos.py`
  pega Klein **sólo en los huecos** (dilatados 7 px, borde suave): todo lo que ven las dos cámaras queda con los píxeles
  de s44. Texana corregida en la maqueta a la 1.ª banca izquierda. `nave06props_reproy_final.png` (s7), `par_reproy.jpg`.
  Método general: la segunda cámara de una placa aprobada se saca de ella, no de otra tirada de Klein.
- El usuario sobre `par_reproy.jpg`: fantasma en el joven junto a la del velo, y la texana tapada por la cabecera de la
  banca, "no se acomoda natural como en horizontal". Causa: Klein dibujó gente y texana un poco fuera de donde las tiene la
  maqueta; reproyectadas con la Z de la maqueta, sus orillas toman la Z del respaldo y se doblan. La texana sí está donde
  la pone la geometría: desde la cámara vertical (0.8 m a la derecha) la cabecera de la 1.ª banca izquierda queda delante.
- **Capas** (`reproyectar_capas.py`): Klein vacía s44 (gente y texana fuera, `s44_vacia_s7`, limpio); silueta = diferencia
  dentro de cada caja (texana: umbral 12, la negra sobre madera cambia poco), sin lo que en escritorio está delante (Z);
  fondo vacío reproyectado con `z_*_vacio` (`pases_reproy.py -- vacio`); cada figura como plano a su Z de maqueta (medirla
  bajo la silueta falló: asoman contrabajo y bocina), por una afín, pintada sólo donde lo de la vertical queda detrás.
  **No sirvió para el joven:** en s44 el contrabajo le tapa medio cuerpo y en la vertical eso se destapa; Klein lo inventa
  (ronda con capas antes del pase: inventó otra persona de gorra roja de frente). Antes, la base de huecos (s33) traía su
  propia gente y se colaba como fantasma: la base tiene que ir vacía (`s33_vacia_s7`).
- Retoque local del joven sobre la primera reproyección (`v1_hombre_s7/8`): s7 le quita la gorra y le pone bufanda beige;
  s8 lo vuelve otra mujer con velo. Ninguno. `hombre_fix.png`. Pendiente de decidir con el usuario.
- **Elegido por el usuario: mover a la gente donde las dos cámaras la vean entera.** `medir_libre.py` (rayos a 9 puntos de
  la figura y holgura ±0.3 m en las dos cámaras; escritorio fuera del micro, vertical en u 0.1–0.9): para el joven **sólo
  quedan bancas izquierdas** (filas 6–12, x −1.9 / −2.3: escritorio u 0.31–0.39, v 0.55–0.59; vertical u 0.12–0.28), que en
  escritorio caen en el hueco del texto (03); a la derecha todo lo tapan bocina, contrabajo o el micro. Texana: remates
  izquierdos fila 4 x −1.2 (esc. 0.35 / vert. 0.13), fila 5 x −1.2 o −1.6, fila 6 x −2.0. **Siguiente paso:** confirmar con
  el usuario el hueco del texto; luego, sobre `s44_vacia.png` (sin gente, limpio) devolver mujer y fiel de s44 y que Klein
  añada joven y texana en recortes centrados en su sitio medido; mover `PROPS` igual; reproyectar la vertical
  (`reproyectar.py`, Klein sólo en huecos con base vacía `s33_vacia_s7`).
- **Elegido por el usuario (2026-10-13, G1 del alcance):** joven en la **6.ª banca izquierda, x −1.9** (el sitio libre
  más cercano: sentado mide 138 px en escritorio a 1712 y 82 px en vertical, contra 212 / 126 donde estaba; queda dentro
  del hueco del texto de D, cerca del borde de arriba de la esquina del titular) y texana en el **remate de la 4.ª banca
  izquierda, x −1.2**. `PROPS` ya movido en `blender/transicion.py`. Hojas: `medir_libre.py` rehecho sin cambios
  (17 sitios, los mismos) y la proyección de los sitios sobre s44 y la reproyección vertical.
- **G2, placa de escritorio con gente (2026-10-13), elegida por el usuario: `tmp/props-06/nave_g2.png`**
  (= `entrega/placas/nave-esc-g2.png`). Referencia: el joven y la texana de s44 (sudadera gris, gorra negra, de espaldas;
  sudadera L* p50 20.8); cambia sólo el sitio. Cadena: `devolver.py` (mujer del velo y fiel de s44 sobre `s44_vacia.png`:
  s44_vacia sólo difiere dentro de `siluetas.png`) → `pases_reproy.py` y `-- vacio` con los `PROPS` nuevos (cámaras
  iguales; las Z anteriores quedan como `z_*_g0.png`) → `guia_g2.py` (silueta = Z con gente más cerca que la vacía, en
  gris sobre la base, recorte de 384 px) → `klein_g2.sh` (Klein a 1.56 MP sobre el recorte, 3 semillas por ronda) →
  `pegar_g2.py` → `bajar_g2.py`. Rondas: "light grey" salió casi blanco (L* 44–49, 2.3× s44); "charcoal" 9–12 y con
  la sudadera partida en luz y sombra en dos semillas; "mid grey" 30 → **c_s11 bajada en luz lineal a L* 21** (ganancia
  0.53, sólo el joven). BVH: joven sólo toca su asiento, texana su remate y respaldo.
  - El usuario vio que c_s11 y c_s22 perdían un trozo de hombro: la máscara de pegado era la silueta de la maqueta
    dilatada 9 px y Klein dibuja la figura más ancha. `pegar_g2.py` suma lo que Klein cambió (> 18) a ≤ 41 px de la
    silueta, **sólo donde la escena vacía queda detrás del joven** (si no, Klein le pinta el cuerpo encima del respaldo de
    la banca de delante); las siluetas del joven y la texana se tocan y se separan por Otsu sobre la Z; junto a la
    texana, lo que Klein no pinta más oscuro que la base sobre el respaldo vuelve a la base.
  - Siguiente: G3, vertical por reproyección desde `nave_g2.png`.
- **G3, vertical con gente (2026-10-13), aprobada por el usuario sujeto por sujeto: `tmp/props-06/nave_g3.png`**
  (= `entrega/placas/nave-vert-g3.png`). **Desvío del método del alcance:** `reproyectar.py` de la placa con gente + un
  pase global de Klein dejó al joven estirado (la Z de maqueta es una cápsula) y Klein **inventó gente** en los huecos
  (un hombre junto a la mujer, el velo hecho hombros, dos mujeres sin velo). Lo que funcionó, la cadena "Capas" de este
  ticket: fondo **vacío** reproyectado (`ZSUF=_vacio reproyectar.py s44_vacia.png`) + `klein_g3.sh` con `VACIA=1`
  (prompt sin gente: las tres semillas salen vacías) + `pegar_huecos.py` → s11; luego cada figura como plano a su Z
  (`G2=1 reproyectar_capas.py`, joven Z 10.25, texana 7.59). El usuario aprobó así la texana y el fiel. Joven ("no se
  parece a escritorio, borroso") y mujer ("sólo un velo, sin cuerpo": el 48 % de su silueta vertical lo tapa el altavoz
  en escritorio) → **paso nuevo** `figura_g3.py` + `klein_g3f.sh`: Klein de 2 imágenes (recorte vertical con lo que falta
  de la silueta en gris + la figura de escritorio como referencia), pegado dentro de la silueta de maqueta ∪ capa, sólo
  donde la escena vacía queda detrás del plano. Elegidas: mujer s22, joven s11. En la vertical la texana queda justo
  debajo del joven (la geometría de la 4.ª y la 6.ª banca desde esa cámara); el usuario la aprobó así.
- **G4, placa real v5 de los dos formatos (2026-10-13), elegida por el usuario: s2 en los dos.** Escritorio
  `tmp/props-06/nave_g4_esc.png`, vertical `nave_g4_vert.png`, disparidades de MoGe `nave_g4_*_disp.png` (todo también
  en `entrega/placas`). Cadena de v5 (ticket 14) en `tmp/props-06/g4/`: DLSS NR `--nr-color 0` de la placa → Klein 4 MP
  con el prompt de `mto_placa_real_s2b.json` **cambiando el final "no people"** por "the same people … no added people"
  (`klein_real.sh`) → vertical: `alinear_flujo.py` → `placa_real.py` con el tono del NR de la **placa nueva** (el NR
  de v5 es de la placa sin pila: su luz fina σ 8 borraría la gente) y los PROF de v5 → `moge.sh` (grafo API de v5 por
  curl). La gente sale igual (la luz fina viene del NR). Vista con foco en la guitarra (`dof.py`, FOCO_D 0.60 / 0.50);
  el foco del loop va en el micro (G5/G6). Escalas de disparidad iguales a v5 (fondo y piso), salvo la guitarra vertical,
  más cerca por la pila (0.50 contra 0.36).
  - **Guitarra vertical** (el usuario: "rara", luego "cortada abajo a la izquierda"): venía de G3, la guitarra de la
    maqueta es más grande que la de Klein; la reproyección estiraba el borde y la base de huecos añadía un segundo
    contorno. `guitarra_g3.py`: la guitarra nativa de la vertical de Klein (`s33_vacia_s7`), alineada, con media y
    desviación Lab de la de escritorio, en la cara del altavoz + franja del cuello + la guitarra de s33 dilatada (sobresale
    del altavoz por la izquierda). `nave_g3.png` es ya esa versión (la anterior, `nave_g3_v0.png`). El logo del altavoz
    vertical se pierde.
- **G5, el micro sobre las placas G4 (2026-10-13), aprobado por el usuario.** Todo en `tmp/micro/g5/` (copias en
  `entrega/placas/*-g5*`). Compuesto con `micro_viva_v.py` sobre mkv de 3 cuadros de las placas nuevas.
  - **Cúpula de la cabeza** (el usuario: "pieces off near the rose, the mic"; probablemente también el "still missing
    pieces" del 2026-10-10): la máscara cortaba la parte de arriba de la cabeza bajo la rosa (hombro izquierdo por
    `corte[320:376, :975]` de `ajustar_mascara.py`, muesca derecha por la diferencia contra la placa) y dejaba una franja
    de fondo viejo a la izquierda (x 944–949). La placa sí tiene la cúpula entera. `cupula.py`: elipse ajustada al borde
    de oro (centro 991, 397, semiejes 41 × 42) y fuera la franja → `mascara_micro_g5.png`. Vertical: Klein s4 había pintado
    fondo ahí (le llegó el trasplante con la muesca), así que `cupula_v.py` toma esos píxeles de la placa de escritorio
    escalada como `trasplantar.py` (0.598, −342, 38), con ganancia por canal contra el oro de s4; la máscara nueva sale de
    `mapear_v.py` (reproduce `mascara_trasplante.png` byte a byte con la máscara vieja).
  - **Brillo** (elegido por el usuario: el nivel aprobado, no la razón): la guitarra nueva es más oscura y con `TOPE=1.2`
    el oro quedaba 28 % más oscuro (34 contra 46). Escritorio `TOPE=1.63` → oro L p99 46.3 = aprobado (1.69× la guitarra);
    vertical `GANA_ORO=1.7` → 51.4 (aprobado 52.2). Medido antes del LOOK y la halación, igual en los dos lados.
  - **Altura vertical** (elegida: +20 px): la pila subió la veladora roja y el micro la tocaba. Placa, máscara y rosa
    corridas 20 px arriba (`vert_placa_micro_g5.png`, `vert_mascara_g5.png`, `vert_rosa_g5.png`, `ARRIBA=215`);
    maqueta `MOVIL["micro"]` z 1.62 → 1.669 (centro de la rejilla en y 281, medido con `medir.py`).
  - **Disparidad con el micro** (`disp_g5.py`, valores de las cadenas aprobadas, G4 está en la escala de v5): escritorio
    0.976 → `esc_disp_g5.png`; vertical 0.60 → `vert_disp_g5.png` (la guitarra vertical está ahora en 0.50).
  - Reconstruir desde `tmp/micro/`: `TOPE=1.63 ROSA=mascara_rosa.png GUIT=0.78,0.99,0.64,0.72 python movil/micro_viva_v.py
    placa_micro_rosa.png g5/mascara_micro_g5.png <viva_esc.mkv> <salida>`; vertical `GANA_ORO=1.7 TOPE=1.2
    ROSA=g5/vert_rosa_g5.png GUIT=0.37,0.49,0.36,0.51 ARRIBA=215 … g5/vert_placa_micro_g5.png g5/vert_mascara_g5.png`.
- **G6, loops de la nave de 10 s sobre las placas G4 (2026-10-13), aprobados por el usuario** (escritorio en la versión copal, abajo). `tmp/g6/tanda.sh`
  (cadena del 16: H3 nativo 260 cuadros, 40 pasos, semilla 7 → RTX → tmix; velas y polvo de 240 "rápido" sobre la placa de
  Klein → `llevar.py` a la real G4 → micro de G5 → H3 en humo y llamas + LOOK → foco → halación GOP 240). Salidas
  `tmp/g6/esc/nave_g6_esc.mp4` (502 KB; aprobado 345, costura 0.67, mediana 0.08) y `tmp/g6/vert/nave_g6_vert.mp4` (199 KB, costura
  0.51; aprobado 0.55). Prompts `prompts/16-loops-de-10s/h3_g6_{esc,vert}.txt`. GPU: H3 ~1090 s + RTX ~90 s por formato.
  - **Zonas nuevas por la pila** (`tmp/g6/{esc,vert}/zonas.py`): llamas halladas con `llamas_auto.py` (núcleo claro con
    halo naranja; rechaza el oro de las estatuas y las rosas blancas) y filtradas con `elegir.py`. H3 anima en escritorio el
    sahumador y la veladora roja de la bocina (el humo sube de la veladora hacia el altar); en la vertical el sahumador de la
    bocina no tiene brasas en la placa: H3 anima la veladora roja y el cuenco con fuego del altar lateral derecho.
  - Primera tanda: el cúmulo del candelero de escritorio cubría la vitrina, cuyo interior claro latía entero → el cúmulo
    sólo en las dos filas de veladoras y las velas de la vitrina como llamas. Lo que queda de movimiento en escritorio es
    la llama abierta del sahumador (H3) y el humo: por eso la costura es mayor que la aprobada (0.50).
  - **Copal real (escritorio).** Con la llama abierta de H3 el usuario pidió más calma; otra semilla (11) y un prompt de
    "llamitas bajas" dieron la misma lengua alta (H3 no obedece la altura de la llama). Sacar el sahumador de H3 y dejarlo
    de la placa con titileo tampoco: "no es como se ve un fuego o un humo en la vida real". Lo que estaba mal era la placa:
    Klein había puesto la columna de humo sobre la veladora roja, no sobre el sahumador. Arreglo: edición local de Klein
    (recorte 400×400 en 960,220 → 1 MP, `tmp/g6/copal/prompt_copal.txt`, 3 semillas, elegida s3: brasas con llamitas en el
    borde, humo que sale del cuenco, veladora sin humo; s1 brasas como de horno, s2 humo de lado como niebla) pegada sólo
    donde cambió (`pegar_copal.py`, alineada por correlación de fase, corrimiento 0) en la real y en la de Klein
    (A + (R' − R), para que velas240/llevar.py sigan igual). Zonas: brasas en CUMULOS (cada una titila por su lado), H3 en
    el humo y la llama de la veladora; prompt `h3_g6_esc_c.txt`. Salida `tmp/g6/esc/nave_g6_esc_c.mp4`, 557 KB, costura
    0.75 (el humo espeso se mueve más). Maestros ffv1 `tmp/g6/{esc,vert}/maestro_nave_*.mkv`; todo congelado en `entrega/`.
