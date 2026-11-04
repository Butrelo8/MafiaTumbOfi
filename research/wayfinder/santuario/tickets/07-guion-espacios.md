# 07 — Guion de camarín, cripta y atrio
Type: grilling · Status: closed · Blocks: 10 · Blocked by: 02, 03 · Assignee: —

## Question
Con la skill `director`: por espacio restante, qué muestra, su reliquia, su luz y su referencia
(`frameref`), y su transición (qué oclusor; dónde va el único "atravesar un umbral" y el "empujar hacia un
retrato que se abre"). Incluye decidir el atrio (¿la calle con la troca?) y cómo entran los retratos de
El grupo.

## Answer
Decidido por el usuario el 2026-10-13, en una pasada sobre los tableros de `tmp/07/tablero/` (detalle de cada opción
en la propuesta de abajo):

| Espacio | Elegido | Reliquia | Luz | Referencias |
|---|---|---|---|---|
| Camarín (El grupo, E) | **B · El vestidor**: ropero abierto con la ropa de escenario colgada como ornamentos, texana, espejo grande de marco dorado, tocador con tres veladoras | La guitarra de Diego recargada en el tocador | Dos arbotantes de 2200 K y las veladoras | `silence 007`, `jessejames 015` |
| Cripta (Contratación, D) | **B · La línea directa**: altar de piedra bajo la bóveda de tezontle | Teléfono de disco de oro (excepción aceptada: no es un instrumento) | Un haz frío de luna por la reja de la clave, con polvo; dos veladoras | `silence 002`, `jessejames 008` |
| Atrio (Cierre, D esquina) | **C · La fachada desde la calle**, con la troca: sí | La troca: **pickup negra estilo Lobo**, doble cabina, cromo, calaveras verticales rojas, sin emblemas | Luz cálida del portal abierto, sodio, calaveras, neblina | `sicario 034`, `sicario 015` |

- **Transiciones, plan 1.** Sacristía → camarín: empujar hacia el cuadro que cuelga sobre el tocadiscos en s11, que se
  abre como puerta (vuelta: se cierra). Camarín → cripta: oclusor con la puerta del ropero y bajar la escalera.
  Cripta → atrio: el único umbral, subir y salir por el portal a la neblina, el mismo portal que el atrio ve desde la
  calle. Ninguna toca placas de la nave ni de la sacristía.
- **Retratos de El grupo:** HTML en el hueco de E, uno a la vez; la escena del vestidor no cambia por integrante.
- **La troca la eligió Claude a pedido del usuario** ("que se vea más real, saca alguna que se vea con la estética"):
  tres variantes sobre una maqueta con proporciones de pickup real (`blockout.py › troca2`, 5.9 × 2.0 × 2.0 m,
  estacionada junto a la banqueta, vista de tres cuartos por detrás), `tmp/07/tablero/tablero_troca.jpg`. La negra
  porque mantiene el negro sobre negro, el cromo toma el oro del sodio y las calaveras son el rojo de la paleta; la
  blanca es lo más claro del cuadro y le quita el ojo al portal; la gris estilo Raptor repite la firma de calaveras de
  Ford y se lee fría. Placa elegida: `tmp/07/tablero/atrio_C2_lobo_elegida.png` (semilla 22).
- **Para la producción** (cuando el espacio entre a la cola): las previas son de una semilla y sirven de dirección,
  no de placa. Corregir el muro verde menta del vestidor a cal/almagre en el prompt; modelar la guitarra y el
  teléfono en Blender con su silueta real (lección del 12); la troca con un asset o la maqueta `troca2` mejorada,
  nunca la caja del primer tablero. Prompts: `prompts/07-guion-espacios/`.
- **Placas de escritorio (E3, 2026-10-13).** Tres semillas por espacio desde las maquetas de producción de
  `blender/espacios07.py` (`tmp/07/tablero/tablero_e3.jpg`, el hueco medido en luma media): el usuario eligió
  **cripta s22** (hueco 10.5, el haz cae entero sobre el teléfono), **atrio s22** (esquina 22.5, la más oscura) y
  **vestidor s11** (hueco 42.5), éste con una corrección: la guitarra recargada en el tocador queda en una postura
  imposible. Con la misma semilla se probaron cinco soportes en la maqueta: atril de piso y gancho en el muro
  (descartados: el gancho quedó sobre el clavijero y la guitarra parecía recargada) y luego silla, dentro del ropero y
  estuche abierto (`tmp/07/tablero/tablero_guitarra2.jpg`). **El usuario eligió la silla**: una silla de madera junto
  al tocador, el cuerpo en el asiento de tule y el cuello en el respaldo, a la luz de las velas. Placa:
  `tmp/07/e3/out/e3_vestidor_silla_s11_00001_.png`; prompt `prompts/07-guion-espacios/e3_vestidor_silla.txt`. El muro
  blanco del vestidor todavía aclara el hueco (luma media 47): lo baja la placa real (Klein 4 MP + tono NR).
- **Verticales (E4), primer intento rechazado por el usuario (2026-10-13 05:20):** "pixeleado donde Klein rellenó",
  la cripta "se ve horrible", el teléfono no se lee, la guitarra se ve rota; el atrio, el menos malo. Causa, medida en
  `tmp/07/e4/lado_*.jpg` y `detalle_*.jpg`: **la cámara vertical de `espacios07.py` (28 mm, más atrás, shift −0.25) es
  demasiado abierta**: todo sale a ~40–50 % del tamaño de escritorio (el teléfono en ~25 px) y el 53–56 % del cuadro cae
  fuera de lo que vio la placa de escritorio, así que lo inventa Klein. Además, Klein con una sola imagen vertical
  **reencuadra** (base y pase: bajó el contenido 150–300 px y lo escaló): la correlación de fase de `pegar_huecos.py`
  no lo alinea (respuesta 0.05); `tmp/07/e4/pegar_alineado.py` (SIFT + RANSAC, semejanza) sí. Las placas de escritorio
  sí coinciden con su maqueta (superpuestas al 50 %). Siguiente: cámara vertical medida, con lente más larga desde la
  posición de escritorio, el sujeto arriba y entero dentro del cuadro de escritorio (prueba gris → gris de
  `reproyectar.py`, que imprime `fuera del cuadro`), un tablero de 2–3 encuadres para que el usuario elija; la banda de
  abajo (el hueco vertical, que el escritorio nunca vio) como extensión oscura y no con Klein; si pide contenido real,
  el método de dos imágenes del 17 (maqueta + placa aprobada como referencia, `prompts/17-transiciones-micro-v5/sac17.txt`).
- **Verticales (E4) re-encuadradas, elegidas por el usuario (2026-10-13 05:45).** La cámara vertical ahora comparte
  posición y rotación con la de escritorio y sólo cambia lente y shift, así que la vertical es un **recorte exacto** de
  la placa aprobada (afín, sin Klein) más una banda abajo que la placa no vio. Nueve candidatos medidos (48–63 mm;
  `tmp/07/e4/encuadre/medidas.txt`: gris → gris dif. 0.8–2.5, ningún hueco fuera de la banda salvo los bordes de la
  prueba de profundidad en la reja del atrio) y tableros `tmp/07/tablero/e4_encuadre_*.jpg`. Elegidos: **vestidor
  amplio 48 mm** (el único con el sujeto entero: espejo, arbotantes, tocador y guitarra en la silla; ×1.04, banda 24 %),
  **cripta cerrado 63 mm** (sin banda, nada inventado; teléfono ×1.36; el frente oscuro del altar es la zona de la UI,
  luma 7) y **atrio amplio 48 mm** (portal con reja y las calaveras rojas de la troca; ×1.04, banda 24 %). Valores en
  `CAMARAS[...]["movil"]` de `blender/espacios07.py`. La banda es extensión oscura (media de las últimas filas que cae a
  negro, con el grano medido): `tmp/07/e4/encuadre/verticales.py` → `tmp/07/e4/v2/out/vertical_*.png` (720×1280), pares
  al mismo alto en `tmp/07/tablero/e4_vertical_*.jpg`. Con la placa de producción (Klein 4 MP) la escala ×1.36 de la
  cripta deja de ser ampliación.
- **A/B con Google Flow, camarín → cripta (job1, Veo 3.1 Fast, 20 créditos, 2026-10-13).** Los extremos sí coinciden:
  el cuadro 0 = la placa del camarín y el 184 = la de la cripta; los cuadros 185–191 se arrastran (escala 1.025), así
  que se corta en 184. El oclusor **no** tapa el cambio: la tela nunca llena el cuadro (luma mínima 17.6) y la cripta
  aparece detrás de los sacos todavía colgados, o sea un morph. Además inventa un perchero suelto con dos sacos, una luz
  blanca con destello cian y muro más allá del ropero. No sirve como E6 final; sí como referencia de velocidad de cámara
  y de movimiento de la tela. Tablero `tmp/07/tablero/flow_job1_ab.jpg`, veredicto `tmp/07/flow/job1/veredicto.md`.
  **job2** (reintento con OK del usuario; negro forzado, cámara lateral, sin luces nuevas): mucho mejor. No hay morph
  (la cripta se descubre más allá del oclusor), no hay destello, cian ni luces nuevas; se corta otra vez en 184. Pero
  tampoco llega a negro: luma mínima 11.9 y como máximo 86 % del cuadro bajo luma 20. Además, en 82–85 se ven los dos
  cuartos en los bordes, y la cripta llega más fría y sus velas suben hasta ~176. Veredicto: **E6 provisional (0–184,
  sin audio); el final por H3** con oclusor de máscara, salvo que el usuario lo acepte al verlo a velocidad
  (`tmp/07/tablero/flow_job1_vs_job2.{jpg,mp4}`, `tmp/07/flow/job2/veredicto.md`).
  **Upscale 1080p de Flow (job2):** no mueve los extremos (0 px) ni cambia el color (< 1 nivel), pero sobreafila: el
  laplaciano queda en 2.3–2.5× el de las placas, inventa relieve en el yeso y el tezontle, deja halo en el teléfono, y
  la textura se arrastra 1.8× más que en el 720p + lanczos. Al empalmar con los loops de E5 se notaría el salto de
  textura: fundir ~8–12 cuadros con la placa en cada extremo o suavizarlo (`tmp/07/flow/upscale_job2.md`).
- **E6 provisional = Flow job2 (decisión de meltingship, delegada por el usuario, 2026-10-13 06:17).** Es el 720p
  original (no el upscale de Flow), cuadros 0–184, sin audio, llevado a 1920×1080 con nuestro paso RTX
  (`scripts/loop-vivo.sh rtx`, ×1.5 por medir 1280 de ancho), y está en `entrega/escritorio/grupo-ida-provisional-h264.mp4`.
  **Por qué:** los extremos son las placas aprobadas (cuadro 0 = camarín, 184 = cripta), no hay morph, la cámara es
  lateral y creíble, y salió a la segunda generación en Flow (40 créditos en total). Mientras tanto, la sección queda con
  una transición que sí lleva de un espacio al otro.
  **Defectos que se aceptan por ahora:** nunca llega a negro (como máximo 86 % del cuadro oscuro), los dos cuartos se ven
  en los bordes en 82–85 y la cripta llega más fría con sus velas subiendo hasta ~176.
  **No está en la web:** `src/data/santuario.ts` tiene `ida` por espacio, pero «El grupo» y «Contratación» están en
  negro (aún no hay loops) y el reproductor espera que cada ida traiga los 20 cuadros crudos del loop al principio
  (`COSTURA` en `src/lib/montarSantuario.ts`). Conectarla pide loops o quietas de los dos espacios y es otra decisión.
  No hay vertical: Flow dio 16:9; la vertical cruza por negro.
  **Lo que pide el E6 final (H3, en su turno de GPU):**
  - el oclusor como máscara: la puerta del ropero o tela animada en la maqueta, presente en el control de
    profundidad y en la máscara, que tape ≥ 90 % del cuadro durante ~5–6 cuadros, con el empalme por `maskedmerge`;
  - la geografía del plan 1 (la puerta del ropero y bajar la escalera);
  - los extremos exactos con los loops de E5 de camarín y cripta, incluidos sus 20 cuadros crudos;
  - su vertical con las cámaras de E4.
- **Cripta → atrio provisional = Flow job3, arreglado (OK del usuario y nombre de vibeship, 2026-10-13).** Está en
  `entrega/escritorio/contratacion-ida-provisional-h264.mp4`: 204 cuadros, H.264 crf 23, 1920 con el paso RTX ×1.5.
  Flow sí llega a negro (28 cuadros ≥ 90 %, f116–143) y la cola no se arrastra. Lo que estaba mal era el teléfono:
  pierde el disco desde ~f24 (correlación del detalle con la placa 0.73 → −0.01 en f68). Se volvió a pegar el de la
  placa sobre un seguimiento afín de su silueta dorada (Lab b*), con desenfoque de movimiento corto y nitidez igualada
  (0.82–0.98). Cuadro 0 = placa de la cripta; la cola = loop del atrio 228–239 fundido y 0–19 crudos (`COSTURA` exacta).
  **No arreglado:** la escalera y la piedra del movimiento (f60–120) son de Flow y no tienen placa; el teléfono pegado
  es plano, no gira con la cámara. Veredicto y números: `tmp/07/flow/job3/fix/veredicto.md`.
- **Sacristía → camarín = Flow job4, montado; el usuario lo queda como provisional con el cuadro inventado (2026-10-14).** Flow no empuja hacia el cuadro
  del tocadiscos: inventa un **segundo** cuadro (una mujer de rojo con una vela) que entra girando por la izquierda,
  hace de puerta y del negro (20 cuadros ≥ 90 %, f67–86) y se queda a la izquierda del camarín hasta ~f158. Se
  sostiene en cada lado del negro (correlación del detalle entre cuadros 0.52–0.88) pero al salir de cuadro
  (f118–~135) la cara se borra y la vela se vuelve un brillo; entre los dos lados parece redibujado dentro del negro (cara ≈14 % y ≈19 % del lienzo, leído a ojo; el ECC no engancha). Sin
  neón ni luces inventadas en el camarín (0 píxeles en f67–191). La cámara sigue empujando en el corte (escala 0.987 en
  f172, 1.007 en f191), así que la cola funde también la geometría hacia la placa (hueco del fundido 3.4–3.8 contra
  3.8–7.8 sin alinear). Cuadro 0 = cuadro 0 del loop de la sacristía; la cola = loop del vestidor 228–239 fundido y
  0–19 crudos (diferencia máxima 0). Máster FFV1, vista previa y lado a lado en `tmp/07/flow/job4/fix/`; veredicto y
  números en su `veredicto.md`.
  **Congelado en `entrega/escritorio/musica-{ida,vuelta}-*.mp4` (2026-10-14)** con el cambio en f67 (vibeship, 01:08):
  f0–66 = `job4_fix.mkv` tal cual (su cabeza ya está graduada: `start.png` es el cuadro 0 del maestro graduado de la
  sacristía, 0.000), f67–203 = cadena de `armar.sh`; el cambio queda oculto en el corte a negro de Flow. Un re-grade
  nunca debe correr sobre el clip entero (graduaría dos veces la cabeza). Ida con `COSTURA` exacta; vuelta no (salto 0.68 al cuadro 20).
- **El atrio elegido todavía no deja limpia la esquina** (`tmp/07/tablero/atrio_C2_lobo_hueco.jpg`: luma media 24 en
  el hueco contra 46 en el cuadro): el poste, el muro que alumbra el sodio y el canto izquierdo del portal caen dentro.
  En la placa de producción el poste se mueve a la derecha del portal o el muro bajo la lámpara cae a negro, para que
  el monograma y las redes queden sobre oscuro. Klein además dibujó un emblema en el costado de la troca: se quita.
- **Placas de producción (decisión del usuario 2026-10-13 06:59: primero las placas, luego E5; middrone, 07:30).**
  Cadena de G4/v5 en los tres espacios (`tmp/07/produccion/real07.sh pre|nr|klein|placa`): DLSS NR `--nr-color 0` →
  Klein 4 MP (`prompts/07-guion-espacios/real_<e>.txt`, semillas 2 y 3) → `alinear_flujo.py` → `placa_real.py` con el
  tono del NR → `arreglos.py`. Klein redibuja la geometría también en escritorio (vestidor s3: +20 px arriba, 0 abajo):
  la fase global de `placa_real.py` no basta, el flujo deja residuo ~0 px por cuadrante. Arreglos:
  - **Muro del vestidor:** la placa real **no** lo baja (G4: ±1–2 de luma, el tono se fija a la referencia), así que
    `arreglos.py` le da caída de luz desde los dos arbotantes, sólo sobre el muro (fuera el cristal del espejo, el
    ropero y la cómoda), después de Klein. Hueco 47 → A 31 / **B 26 (por omisión)** / C 24; el espejo solo aporta ~12.
  - **Troca:** fuera las letras de la salpicadera, el óvalo de la tapa y las letras de la placa (inpaint + grano medido
    por MAD lejos del borde), antes y después de Klein; ninguna semilla las volvió a escribir. La pintura sale muy
    granulada en las dos semillas **por el prompt** (`real_atrio.txt` pide "raindrops and road dust low on the body"):
    si el usuario la rechaza, quitar esa frase (un Klein más) o, sin GPU, tomar la carrocería del tono NR con una
    máscara (la mezcla de `PROF` en `placa_real.py`). Alineación medida en la troca (flujo DIS sobre bordes): mediana
    0.5 px en s3, 0.7 en s2; el poste 0.55 en s3 y 2.4 en s2.
  - **Adoquines:** el prompt pide piedras separadas con juntas oscuras y una película de agua (lectura del drone: al
    100 % se veían como CG embarrado); el usuario lo juzga en los recortes al 100 %.
  - **Esquina del atrio (opcional, meltingship 07:23):** caída de luz desde el portal sobre el muro bajo y la calle,
    `ESQUINA=0.5|0.3` (hueco 22 → 17 / 14), sin GPU.
  - **El NR oscurece la cripta 15 %** (cuadro 19 → 15.6, haz de luna 104 → 86); variante con el tono de la E3.
  Tableros `tmp/07/produccion/tablero_{vestidor,cripta,atrio}.jpg` (E3 | s2 | s3, recortes al 100 %, variantes y
  verticales con los mismos encuadres), enviados al usuario. s2 del atrio borró la montaña. **Elegido por el usuario
  (07:40): s3 en los tres**, muro B, cripta con el tono de la E3 (sin NR), atrio con esquina 0.5 y la carrocería de
  la troca desde el tono NR (máscara de la maqueta de E2, `carroceria.py`); el s2 del atrio, rechazado (la puerta
  deformada). Placas finales `tmp/07/produccion/placa_<e>.png`, verticales `tmp/07/produccion/vertical/`. La
  vertical del atrio no ve la lámpara ni la neblina: lleva neblina baja sobre los adoquines (decisión del usuario).
- **E5, loops de 10 s (smoldrone, 2026-10-13 15:00).** Zonas aprobadas por el usuario (`tmp/07/e5/tablero_final.jpg`;
  lo azul es la zona de humo/neblina, no la placa). Prompts `prompts/07-guion-espacios/h3_<e>_{esc,movil}.txt`,
  lanzador `tmp/07/e5/e5.sh <h3|rtx> <e> <esc|movil>`. **Sin grade por ahora (vibeship, 15:02):** los loops se montan
  con `LOOK=` (`loop-vivo.sh montar` sin look), sin halación y sin foco, para que fuera de las zonas el cuadro sea la
  placa y las costuras con E6 queden exactas. **Pendiente, no olvidar:** el plan de transiciones del usuario pide para
  E5 el mismo look que los loops aprobados de nave y sacristía, así que LOOK y halación van **después**, en un solo pase
  sobre E5 y E6 juntos, cuando exista el E6 final. Verticales: el humo con el método del 16 (`montar_mov_v.py`, sólo
  lo que se mueve y sólo lo que aclara); RTX ×2 y luego escala.
  **Primer loop, vestidor escritorio: falla (15:20).** H3 (928×512, 260 cuadros, 40 pasos, `end_percent=0.5`, semilla
  7, 1013 s; `tmp/07/e5/vestidor/loop/e5_vestidor_esc_00001_.mp4`) redibuja la cómoda con **cuatro** veladoras en otras
  posiciones desde el cuadro ~30, y las velas de los arbotantes quedan unos píxeles corridas. Montado sin look sobre la
  placa (`crudo_esc.mkv`, sin RTX), dentro de las cajas de llamas las veladoras salen como manchas rojas sin llama y los
  arbotantes con la vela doble. `revisar.sh` no lo ve en el video (las zonas son ~1 % del cuadro: costura 0.25, crawl
  0.00, flicker 0.00, nitidez 0.97 con `--ref` a 1920); en el cuadro 120 con `--mask mascara_llamas_esc.png` marca las
  cinco zonas cambiadas (dE > 10, 0.50 % del cuadro) y los recortes muestran la vela perdida. Tablero a velocidad:
  `tmp/07/e5/vestidor/loop/revision_defecto_esc.mp4` (placa | loop). Alto sin reintentar (regla de la tanda); la
  ruta siguiente la decide el usuario: H3 otra vez con más control (`end_percent` 1.0, "exactly three votive
  candles", otra semilla) o titileo procedural de las llamas sobre la placa sin GPU (`velas240.py` del 16).
  Ojo: con `--ref` a 1696 px (la placa nativa) `revisar.sh` da nitidez 0.36–0.38 aun con la placa quieta como video;
  comparar contra la placa escalada al tamaño del clip (`vestidor/placa_vestidor_1920.png`).
  **Ruta (b), vibeship 15:29:** todas las llamas (vestidor, cripta, candelabro del atrio) con titileo procedural sobre
  la placa, sin GPU; H3 sólo para humo/neblina (haz de la cripta primero, `end_percent` 1.0; si redibuja geometría,
  alto y proponer polvo procedural). **Vestidor escritorio, procedural (15:36):** `tmp/07/e5/velas_e5.py` (la fórmula
  de `velas240.py` con RAPIDO; además la llama y su reflejo en la cómoda comparten fase y cada parte tiene su radio:
  arbotantes 60 px, veladoras 22) con `vestidor/velas_esc.json`. Tres amplitudes (0.10 / 0.16 / 0.24,
  `variantes_amp_esc.mp4`); **0.16**, la de las velas aprobadas del 13/16. Medido: costura 239→0 dentro del paso normal
  (arbotantes 0.92 y 0.73 contra pasos de mediana 0.53–0.61), fuera de las cajas la placa salvo ≤ 5 niveles de halo en
  el muro junto a los arbotantes; `revisar.sh` video: costura 0.01, crawl/flicker 0.00, nitidez 1.00; cuadro 100 con
  máscara: 0 regiones cambiadas, color dE 0.01, halo 0 % (el `mask-notch` 11.6 % es la forma de la máscara, igual con
  cualquier cuadro). Loop `vestidor/loop/loop_esc.mkv` (240), revisión `revision_esc.mp4`. **OK del usuario (15:38,
  amplitud 0.16).** Vestidor vertical igual (`velas_movil.json`): costura 0.03, crawl/flicker 0.00, nitidez 1.00.
  - **Cripta (16:20).** Llamas procedurales (`velas_<f>.json`, dos veladoras). Haz: el H3 de prueba (`FIN=1.0`, 1073 s,
    nuevo `FIN` en `loop-vivo.sh h3`) **no redibuja la piedra** (alineación 0 px, escala 0.999 entre los cuadros 0, 130 y
    259), pero no da polvo: el haz se ensancha y, con "sólo lo que se mueve", suma un segundo haz que deriva al lado
    del de la placa (+2.7 niveles de media, p99 20). Contra el polvo procedural de `polvo240.py` (`techo` 0.55;
    `haz_variantes_esc.mp4`): **el usuario eligió polvo 260** (16:15). Vertical: el encuadre es ~3× más cerrado, así
    que `polvo240.py` lleva un `K` nuevo (escala de tamaño; por omisión W/1712): con `K=1.2` y 260 motas la energía de
    motas (pasa-altos en la máscara) da 0.51 contra 0.50 del escritorio; el calibrado de la nave vertical (90) da 0.37
    (`haz_variantes_movil.mp4`). Derrame fuera de la máscara: 0.07 % / 0.24 % de píxeles > 3 niveles, en el borde del
    altar (escritorio) y en la piedra junto a la reja (vertical). revisar: costura 0.01 / 0.05, crawl 0.00, flicker
    ≤ 0.01, nitidez 1.00 / 1.01. Loops `cripta/loop/loop_{esc,movil}.mkv`; el compuesto H3 queda en `loop_esc_h3.mkv`.
  - **Atrio (17:00).** El H3 de escritorio (`FIN=1.0`, 1147 s) no mueve la geometría (0.2 px) pero **se va a noche**:
    la luma de la zona de niebla baja de 89 a 17.5 y el resto de 26 a 11 en 260 cuadros; la niebla desaparece. Alto sin
    más GPU (regla de vibeship) y niebla procedural: `tmp/07/e5/niebla_e5.py` (ruido periódico fractal estirado ASP
    veces en x, dos capas a media fase con pesos en triángulo para derivar a VEL px/s y cerrar el loop exacto, contraste
    normalizado; más niebla = hacia su color, menos = sólo más oscuro). Primera versión con ruido de banda: celdas
    redondas y manchas rojas (alejarse del color azul) → corregido. Escritorio: `DENS=0.3 VEL=8` (ESCALA 200, ASP 3),
    color de la placa; zona 1–2 niveles bajo la placa, sesgo de color neutro (−1.4/−1.2/−1.2), costura 0.03 contra
    pasos de 0.06–0.08, fuera de la máscara 0 (`niebla_variantes_esc.mp4`: 0.5 deja manchas oscuras en el cielo, sin
    estirar parece humo). Vertical: neblina baja `ESCALA=150 ASP=4`, color gris cálido `84,92,118` (el automático da
    el rojo oscuro de los adoquines y casi no se ve; `niebla_variantes_movil.mp4`); aclara la banda 15.7 → 19.4.
    Llamas: candelabro (tres llamas) y lámpara de sodio con zumbido 0.04 (`velas_<f>.json`). revisar: costura
    0.00 / 0.01, crawl 0.00, flicker ≤ 0.01, nitidez 0.98 / 0.96. Loops `atrio/loop/loop_{esc,movil}.mkv`.
  - Tras un H3, ComfyUI se queda con ~3.5 GB de VRAM y la puerta (< 4000 MiB) no abre: `POST /free`
    `{"unload_models":true,"free_memory":true}` entre trabajos (ya va al final de cada lanzamiento).
  - **Atrio v3 (pedidos del usuario 16:50–17:45; todo en `tmp/07/e5/charcos/`, se rehace con `armar_atrio.sh`).**
    - **Lluvia congelada:** Klein pintó rayas de lluvia en el cielo de la placa; en el loop quedaban fijas. Se quitan de
      la placa (`quitar_rayas.py`: top-hat de líneas finas verticales > 3 niveles y ≥ 12 px, inpaint y el grano de
      vuelta; 0.86 % de la zona, grano 598.5 → 599.4).
    - **Camioneta → SUV tipo G (referencia del usuario):** Klein `prompts/07-guion-espacios/camioneta_atrio.txt`,
      semillas 2 3 5; **eligió s2**, sin emblemas. Se registra sólo con desplazamiento (≈ +3.7, +0.7 px):
      `alinear_flujo.py` derrite un objeto que cambió (empuja el coche nuevo hacia los bordes del viejo). Pintura
      **atenuada a gris oscuro** (usuario): máscara GrabCut + envolvente convexa, −65 % en la pintura sin tocar los
      focos rojos ni los brillos (luma 40 → 19; la camioneta vieja: 26). La rueda deforme que vio el usuario estaba en
      la placa aprobada (Klein de producción), no en los efectos (0–4 niveles), y se fue con la camioneta.
    - **Charco:** Klein `prompts/07-guion-espacios/charcos_atrio.txt` sobre la placa con el SUV, s3 (s7 dibujó una
      fuente de luz falsa), pegado sólo el charco (`pegar_charco.py`, 1.31 % del cuadro).
      **Placa v3 = `tmp/07/e5/final/placa_atrio_v3.png`: es el extremo del E6 final.**
    - **Lluvia con dirección** (usuario: "needs direction"): referencia con frameref, *Prisoners* 005 (Deakins,
      gasolinera bajo lluvia; `/mnt/e/ComfyUI/storyboards/mto-atrio/shotspec.md`). `lluvia_e5.py`: rayas largas y
      finas casi verticales (3° a la derecha, la deriva de la niebla), lejos 1400 + cerca 120, sólo a contraluz; el
      adoquín mojado que hierve de salpicaduras de 1–2 px donde refleja luz; muchos anillos chicos y rápidos en el
      charco y su reflejo temblando. Antes (sin referencia) el charco se movía 0.18 niveles por cuadro y el usuario lo
      vio falso; las gotas sueltas blancas parecían brillantina.
    - **Gotas en los vidrios** (`vidrio_e5.py`, máscara `vidrios.png`): 45 que resbalan con rastro (cruzan su vidrio un
      número entero de veces por loop y se apagan junto a los bordes) y 140 que caen y se apagan; especular cálido.
    - revisar: escritorio costura 0.49 / crawl 0.12 / nitidez 1.01; vertical 0.42 / 0.10 / 0.98 (el crawl es la lluvia).
    - **"Muy calma" (usuario 18:07: "look off, need realism calmer and subtler"; eligió entre actual | calma | muy
      calma, `calma_variantes_esc.mp4`):** lluvia 350 + 20 rayas, más lenta y corta (`KESC=0.4`, lluvia fina),
      `BRILLO=0.09 HERVOR=150 IMPACTOS=8 ONDA=0.7 TEMBLOR=0.3`; vidrio 12 que resbalan despacio (`KMAX=1`) y 35 que
      caen, `VBR=0.4` (valores en `armar_atrio.sh`). Movimiento por cuadro contra la v3 anterior: charco 34 %, suelo
      14 %, vidrio 8 %, cuadro 7 %. revisar: costura 0.03 / 0.04, crawl 0.01, nitidez 0.98 / 0.96.
  - **Verticales = recorte del escritorio (usuario 17:05: "¿coinciden?")**, como la sacristía (`tmp/sac10/vert2`):
    `tmp/07/e5/reencuadre_e5.py` compone la afín de `verticales.py` (marco.json) con 1696 → 1920 y rehace la banda por
    cuadro con el grano fijo (con semilla por cuadro la banda hervía: crawl 0.07–0.14). Contra las placas verticales
    aprobadas: 0.00 px, |dif| 0.5, nitidez 0.86–0.90 (un remuestreo más). Llamas, polvo, lluvia y anillos son los mismos
    píxeles en los dos formatos; sólo la neblina baja del atrio es de la vertical (decisión del usuario).
  - **Final (17:55): `tmp/07/e5/final/{vestidor,cripta,atrio}_{esc,movil}.mkv`** (240 cuadros, ffv1, sin grade;
    `MANIFIESTO.tsv`). Pendiente: el pase de LOOK + halación sobre E5 y E6 juntos, la escalera de códecs y llevarlos a
    `entrega/` y a la web; el E6 final termina en la placa v3 del atrio.
- **Flow, trabajos listos (copingdrone, 2026-10-13 18:35; sin créditos gastados).** `tmp/07/flow/job3` = cripta → atrio
  (arco oscuro y escalones a la derecha como oclusor, termina en la placa v3) y `job4` = sacristía → camarín (empujar al
  cuadro que se abre como puerta); los dos con copia en `Downloads\flow-job{3,4}\`, 20 créditos cada uno, orden job3 y luego
  job4, saldo esperado 50 → 30. Cuadros extremos y números del empalme en `job{3,4}/frames_check.txt` (fuera de las zonas
  vivas el cuadro 0 del loop es la placa: 0.00 % de píxeles > 8; dentro, 3–31 %); variantes y riesgos en `notes.md`.
- **LOOK + halación sobre E5 y el E6 provisional (seethingdrone, 2026-10-14; decisiones de vibeship).** Hecho antes del
  E6 final, así que el pase tiene que ser determinista por cuadro. El LOOK aprobado no lo es: `vignette` difumina
  (dither) por omisión con estado que pasa de un cuadro a otro (el mismo cuadro sale distinto según su posición: ±1
  nivel en ~70 % de los píxeles; `tmp/07/look/determinismo/`). **Cadena para E5, E6 y el E6 final:** `ffmpeg -vf
  "format=gbrp,$LOOK,format=bgr0" -c:v ffv1` y luego `VC="-c:v ffv1" scripts/loop-vivo/halacion.sh` con sus valores por
  omisión (HAL 0.8, MIST 0.45), donde `$LOOK` es el de `loop-vivo.sh` con **`vignette=PI/5:dither=0`**, puesto sólo en
  `tmp/07/look/armar.sh` (el valor por omisión de `loop-vivo.sh` no se toca: rehacer la nave o la sacristía no cambia).
  Queda ~0.5 de luma más oscuro que la nave y la sacristía (el dither sumaba [0,1)); se acepta. Verticales: vestidor y
  cripta = escritorio con look recortado con `reencuadre_e5.py` (marcos `c_vestidor_amplio` y `c_cripta_cerrado`, byte
  a byte iguales a los finales sin look), como la sacristía; **el atrio es la única vertical con grade propio** (su
  neblina baja sólo existe en la vertical). job2 no tenía maestro 1920 sin pérdida: `look/fuentes/job2_rtx_1920.mkv` es
  la salida RTX ×1.5 en FFV1, la misma fuente que usó job3. Maestros FFV1 en `tmp/07/look/maestros/` (6 loops,
  `grupo_ida_job2.mkv`, `contratacion_ida_job3.mkv`). Costuras: la cola de job3 (f184–203) es **idéntica byte a byte**
  a los cuadros 0–19 del atrio con look (20/20) y su cuadro 0 = la placa de la cripta con el mismo pase (0.000). job2
  sigue sin `COSTURA` (cola contra la cripta 8.4 → 6.2) y empieza en el camarín anterior a las placas de producción;
  eso lo arregla el E6 final. revisar, costura de los loops: 0.01–0.04, cripta móvil 0.11 (≤ 1.00; parpadeo 0.33 sobre
  7 % estático: el halo de las velas llena el recorte cerrado). job2 ahora llega a negro (14 cuadros ≥ 90 %, antes
  86 % como máximo). Números completos: `tmp/07/look/veredicto.md`. Pendiente: la escalera de códecs, `entrega/` y la web.
- **Camarín → cripta con FastH3 local, primer + último cuadro (apedrone, 2026-10-14; OK del usuario 03:27).** Extremos =
  cuadro 0 de los loops E5 graduados; 192 cuadros, 8 pasos. En 12 GB cabe **1440×832** (376 s); 1920×1088 y 1600×928 dan
  OOM. Elegida `tmp/07/fasth3/clips/f1440_A_puerta_s2.mkv`: la puerta del ropero se cierra, negro y la cámara baja hacia
  la bóveda (geografía del plan 1). Contra job2 con los mismos extremos: inicio 1.8 vs **27.2**, fin 1.6 vs 2.2, cola
  contra la cripta 0–19 4.25 vs 6.18, negro 29 cuadros (f73–101) vs 14, morph 0 en los dos, novel 3.5 % vs 6.9 %.
  **Falta:** el negro dura ~1.2 s (pedido ~5–6 cuadros), la bóveda se ilumina de más al bajar (f119–133) y los extremos
  quedan blandos a 1440 (0.46–0.52 × placa). No es el E6 final del ticket (sin oclusor de máscara ni `maskedmerge`) y aún
  sin `COSTURA`. A/B a velocidad `tmp/07/fasth3/ab/ab_job2_vs_fasth3_s2.mp4`, enviado al usuario; grade, RTX, `COSTURA`,
  escalera y `public/` sólo con su OK. **Licencia:** la de MiniMax H3 prohíbe usar las salidas para público de EE. UU.,
  UE, Reino Unido o Corea del Sur sin permiso escrito; el público de MTO es México, pero si la web apunta también a EE. UU.
  hay que pedirlo antes de publicar. Veredicto y números: `tmp/07/fasth3/veredicto.md`.
  **Textura en movimiento (usuario: «pixelea la textura al moverse, pero es mejor transición»).** A 1440 el modelo
  redibuja yeso y piedra con poco detalle mientras la cámara se mueve; no es el códec ni VSA (la atención densa da lo
  mismo). Arreglo: **1920×1088 nativo, 107 cuadros (383 s, sin OOM) + FILM ×2** (plan de memoria de las 06:22): detalle en
  movimiento 0.96 / 0.85 × placa contra 0.46 / 0.34, extremos 1.6 / 1.7 con nitidez 0.95 / 0.91, morph 0, novel 0.7 %.
  El negro de 51 cuadros se acelera ×2–3 en lo oscuro → 24 cuadros (`tmp/07/fasth3/clips/f1080_film2_rampa.mkv`,
  186 cuadros). Cola contra la cripta nueva (06:29) 0–19: 4.79; la cabeza deriva 3.1 del loop también a 1080, así que
  la `COSTURA` tiene que fundirla. A/B enviados: `tmp/07/fasth3/ab/{textura_1440_vs_1080_1a1,ab_job2_vs_fasth3_1080}.mp4`.
  **Guitarra (usuario: «la parte de arriba se deforma al pasar»).** El modelo redibuja el clavijero en movimiento. Se
  pega la guitarra de la placa con seguimiento afín del cuerpo, ganancia de luz, desenfoque de 180° y, mientras pasa la
  puerta, cortada en su canto (`tmp/07/fasth3/guitarra.py`): mástil y clavijero contra la placa NCC 0.77 → 0.99 (mín.
  0.45 → 0.98); sólo cambian f0–61. Clip vigente: `tmp/07/fasth3/clips/f1080_rampa_guitarra.mkv`.

## Propuesta (2026-10-13)
Vuelve en la versión 1 a pedido del usuario. Tres opciones por espacio, cada una con dos fotogramas de referencia,
su maqueta gris (Blender workbench, `tmp/07/blockout.py`) y una previa de Klein de **una sola semilla** (s22,
orientativa: sirve para elegir dirección, no es placa). El hueco del ticket 03 va marcado en rojo sobre cada maqueta y
cada previa. Tableros: `tmp/07/tablero/tablero_{camarin,cripta,atrio,transiciones}.jpg`; prompts en `tmp/07/prompts/`.

**Idea que manda.** Después de la sacristía el visitante entra más hondo y más abajo en el santuario (camarín, cripta)
y el único umbral es la salida a la noche de Xalapa: cuatro interiores cerrados y oscuros sostienen la afinidad y el
exterior con neblina es el contraste del final. El atrio mira hacia atrás, a la iglesia que se deja, y cierra el
círculo con la plaza del hero.

**Reglas que respetan todas las opciones.** Sujeto a la derecha o al centro y el hueco oscuro (03); la reliquia con su
silueta real desde Blender, nunca inventada por Klein (12); un loop por espacio con placa fija y sólo las zonas vivas
(13, 16); el retrato de cada integrante es HTML en el hueco de E, uno a la vez, y la escena no cambia por integrante.
El camarín no puede ser otro retablo de tres nichos: la nave ya lo tiene (`prompts/13-placa-y-capas/nave13c.txt`).

### Camarín (El grupo, layout E)
| Opción | Qué muestra | Reliquia y props | Luz | Referencias: qué se iguala / qué cambia a propósito |
|---|---|---|---|---|
| A · Camarín octagonal dorado | El cuarto detrás del retablo donde se viste la imagen (modelo: Tepotzotlán); paneles tallados y dorados, columnas salomónicas, repisa corrida de veladoras, linternilla | La docerola de pie en la peana, vestida con un manto de terciopelo rojo bordado y un resplandor dorado | 1900 K de las veladoras subiendo por el oro; un hilo frío de la linternilla | `silence 039` (el oro sólo vive donde lo toca la vela) / arquitectura tallada en vez de tela; `jessejames 036` (la fila de luces chicas abajo) / sin figura |
| **B · El vestidor (recomendada)** | El vestidor de la imagen convertido en el de la banda: ropero abierto con la ropa de escenario colgada como ornamentos, texana en la repisa, espejo grande con marco dorado | La guitarra de Diego recargada en el tocador; tres veladoras; el espejo refleja el ropero | Dos arbotantes de 2200 K y las veladoras; el ropero cae a sombra | `silence 007` (un retrato flotando en negro) / es un espejo, y lo que se ve es la ropa de ellos; `jessejames 015` (una puerta que se abre a la luz) / la abre el espejo |
| C · Muro de exvotos | Pared cubierta de retablitos de lámina, milagros en listón rojo y fotos; tres marcos dorados mayores vacíos | Guitarra colgada con milagros atados al mástil; banco de veladoras | Vela rasante de 1900 K desde abajo | `silence 023` (relieve de metal en muro de cal, luz rasante) / cientos de piezas y vela en vez de día; `amoresperros 010` (interior mexicano con crucifijo y lámparas) / sin gente |

Por qué B: es el único que no vuelve a ser un interior de iglesia dorado (A repite el oro del retablo de la nave en otra
forma) y su función real, vestir la imagen, se vuelve la de la sección: la gente de la banda. El espejo es el retrato
que se abre. C es la imagen más mexicana, pero llena la pared de caras de desconocidos inventadas por la IA en la
sección de los integrantes reales y compite con el retrato HTML. Defectos de la semilla: B y C salen con muros verde
menta (el LOOK y el prompt los llevan a cal/almagre); A da guitarra de seis cuerdas, no docerola; C inventa caras.

### Cripta (Contratación, layout D con el CTA de WhatsApp siempre a la vista)
| Opción | Qué muestra | Reliquia y props | Luz | Referencias |
|---|---|---|---|---|
| A · Estuche-relicario | Bóveda baja de tezontle y cantera con nichos de entierro; losa de piedra | Estuche negro abierto forrado de terciopelo rojo con una trompeta de oro (la trompeta sale en el hero); veladoras en el piso | Veladoras de piso, 1900 K desde abajo | `silence 015` (luz de vela baja, desde el piso) / sin gente; `sicario 029` (lámpara ámbar en bóveda de roca) / piedra labrada |
| **B · La línea directa (recomendada)** | La misma bóveda; un altar de piedra al centro-derecha | Teléfono de disco de oro con su cordón; dos veladoras | Un solo haz frío de luna por una reja de la clave, con polvo; el resto negro | `silence 002` (un haz de ventana en una nave abovedada) / cripta baja y reja; `jessejames 008` (contraluz en niebla) / sin figura |
| C · Bodega de gira | La bóveda como bodega: estuches de gira negros con cantos de aluminio | Un estuche abierto con la cadena de oro; foco desnudo al fondo | Foco de 2400 K y dos veladoras | `sicario 029` / igual; `sicario 015` (unidades repetidas bajo un techo bajo) / estuches en vez de trocas |

Por qué B: es la imagen más fuerte de las nueve y la más literal a la sección ("¿Tienes una fecha disponible?": el
teléfono es la línea; el CTA de WhatsApp es contestarlo), y ya deja la mitad izquierda negra que pide D abierto.
**Se aparta de la definición de reliquia** (`CONTEXT.md`: un instrumento): el teléfono no es un instrumento. A la
cumple (la trompeta, que necesita su asset de Blender: Klein la dibujó sin pistones) y C tampoco la cumple. El foco
de C cae dentro del hueco.

### Atrio (Cierre, layout D en la esquina)
| Opción | Qué muestra | Reliquia y props | Luz | Referencias |
|---|---|---|---|---|
| A · La reja y la troca | Desde dentro del atrio, a través de la reja de hierro, la troca estacionada en la calle empedrada | La troca, oscura, con las calaveras rojas encendidas; fachadas de enfrente | Lámpara de sodio, calaveras rojas, ventanas cálidas, neblina | `nocountry 022` (reja en primer plano, luces de noche detrás) / reja colonial; `sicario 032` (calaveras rojas en el negro) / calle de Xalapa |
| B · Cruz atrial en la neblina | La cruz atrial de piedra (s. XVI) con veladoras y una rosa roja al pie, la fachada perdida en la niebla. **Sin troca** | La cruz; la rosa repite la del micro | Veladoras al pie, 1900 K; la niebla iluminada de lejos | `silence 019` (la niebla que se traga todo) / piedra en vez de figuras; `jessejames 008` (contraluz en niebla) |
| **C · La fachada desde la calle (recomendada)** | La retirada: desde la calle se ve la iglesia que se deja, con el portal abierto y la luz de las velas saliendo; la troca estacionada a la derecha | La troca vista de atrás, calaveras rojas; reja abierta; poste con lámpara de sodio | Luz cálida del portal, sodio, calaveras, neblina de Xalapa | `sicario 034` (pórtico cálido de noche enmarcado en negro) / fachada colonial y portal abierto; `sicario 015` (calaveras de una troca bajo luz cenital) |

Por qué C: es la retirada de la spec original contada en una imagen: el portal abierto es el lugar del que se sale, la
troca es la banda que se va, y el monograma M⚡T y las redes caben en la esquina libre. Repite la plaza del hero de noche
(fachada iluminada, Xalapa) y cierra el recorrido. **La troca sale en A y en C**: si se elige, falta saber cuál es
(modelo y color del videoclip); las maquetas usan una pickup genérica. La troca tampoco es un instrumento.

### Transiciones (las dos de la sacristía salen de lo que ya está en la placa s11; todas se leen de ida y de vuelta)
| Plan | Sacristía → camarín | Camarín → cripta | Cripta → atrio |
|---|---|---|---|
| **1 (recomendado)** | **Empujar hacia un retrato que se abre**: la cámara empuja hacia el cuadro que cuelga sobre el tocadiscos y el cuadro se abre como puerta (los camarines se alcanzan por una puerta detrás del altar); su revés oscuro tapa el cuadro y del negro sale el camarín. Vuelta: el cuadro se cierra | Oclusor: la puerta del ropero (B), una pilastra (A) o el muro oscuro (C) barre el cuadro y la cámara baja por la escalera | **El único umbral**: sube la escalera y sale por el portal a la neblina; en C es el mismo portal que se ve desde la calle. Vuelta: se entra de la noche a lo oscuro |
| 2 | Oclusor: el muro negro de la izquierda de s11 | Empujar hacia el espejo (B) o el marco central (C), que se abre a la escalera | Umbral, como en el 1 |
| 3 | Retrato que se abre, como en el 1 | Umbral de humo de copal bajo un arco al bajar a la cripta | Oclusor: la hoja del portal o la reja |

Por qué el 1: el cuadro ya está en la placa aprobada (se planta en el loop de la sacristía y paga en el gesto
siguiente), el umbral queda al final como contraste mayor, y nada obliga a tocar las placas de la nave ni de la
sacristía. Anotado sobre s11: `tmp/07/tablero/s11_salidas.jpg`.

### Qué se mueve en cada loop (placa fija, zonas vivas)
Camarín B: las llamas de los arbotantes y las veladoras, su reflejo en el espejo. Cripta B: el polvo dentro del haz
y las dos velas. Atrio C: la neblina que corre, la lámpara de sodio, las velas del portal. Ninguno pide cámara.

### Abierto
- Integrantes: `members.ts` tiene 3 (Héctor, Alexandro, Diego); la spec del 2026-09-17 hablaba de 5 y
  `public/members/` tiene también `dimora`. La escena de B no depende del número.
