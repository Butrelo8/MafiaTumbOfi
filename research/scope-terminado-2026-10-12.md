# Alcance de "terminado" — MTO en mafiatumbada.com (2026-10-12)

Documento de planeación. Define qué tiene que estar hecho para dar el santuario por **terminado**, en qué orden, cuánto
cuesta cada paso y qué se deja para después. No hay renders ni cambios al sitio en esta sesión.

**Terminado** significa: en vivo en mafiatumbada.com, con (1) una secuencia de scroll completa en escritorio y en móvil
(la pantalla que ya está hecha más las mínimas a su alrededor), (2) la capa de UI (texto, CTA, botón de WhatsApp para
contratar) y (3) desplegado. Fecha objetivo: antes del **2026-10-25**, porque después de esa fecha la técnica de MTO pasa
a ser la base del rediseño del portafolio (ver el último apartado).

Fuentes: `docs/HANDOFF.md`, `docs/handoffs/2026-10-11-gente-reproyeccion.md` (y los dos anteriores),
`.wayfinder/santuario/MAP.md` con sus tickets, `DESIGN.md` y `STATE.md`. `STATE.md` describe el sitio de abril
(Veracruz Noir, carpeta `web/`, admin con Turso y Clerk) y ya no corresponde al repo: no se usó para nada de lo de abajo.

## La decisión que fija la fecha: la gente de la nave (ticket 06 v6)

El ticket 06 está a medio camino de mover al joven de gorra y la texana a bancas que vean las dos cámaras. El handoff
del 2026-10-11 lo dice sin rodeos: todo lo aprobado después (placa v5, micro colgado, loops de 10 s y las transiciones del
17, en los dos formatos) está hecho sobre las placas y la profundidad **de antes de la pila**. Meter la gente obliga a
rehacer, en escritorio y en vertical: las placas, el micro compuesto encima, los loops de la nave y las dos mitades de las
transiciones. Es más trabajo que todo lo demás de esta lista junto, y el 06 lleva abierto desde el 2026-10-05 con el
usuario todavía iterando.

Lo aprobado hoy es coherente entre sí: las transiciones de escritorio se rehicieron con la maqueta de `cccf32c`, que
coincide con las placas r6/v5 sin dobles, y la vertical con micro también está sobre la profundidad de antes de la pila.

| Camino | Qué sale en la versión 1 | Fecha |
|---|---|---|
| A | La nave tal como está aprobada: placa v5, micro colgado, sin gente ni ofrendas nuevas. El 06 v6 pasa a "después" | **2026-10-25**, sólo con todos los recortes de abajo; con margen, **2026-11-01** |
| **B (elegido)** | La nave con la gente del 06 v6, y todo lo de la nave rehecho encima | **~2026-11-15** (7–10 sesiones más) |

**Actualización del 2026-10-13:** el usuario devolvió el ticket 07 a la versión 1 (camarín, cripta y atrio con sus loops
y transiciones; decisiones en `.wayfinder/santuario/tickets/07-guion-espacios.md`). Son los pasos E1–E9 de abajo; la
fecha y el total nuevos están en *Fecha*.

La recomendación de este documento era A. **El usuario eligió B el 2026-10-12 a las 21:25 ("despacio pero seguro"):** la
gente entra en la versión 1 y la fecha es **~2026-11-15**. Todo lo que sigue supone el camino B; los pasos de la gente
(G1–G7) van entre el paso 0 y el 1.

## Qué está hecho

Todo lo de esta tabla vive en `tmp/`, que está ignorado por git. Del pipeline nuevo sólo están versionados los scripts de
Blender (`blender/transicion.py`), los tickets y las notas.

| Pieza | Estado | Dónde |
|---|---|---|
| Hero (video de 16 s, AV1 y H.264, horizontal y vertical) | En producción hoy en `main` | `public/video/` |
| Loop de la nave, escritorio, 10 s, v5 + micro, velas y polvo de 240 | Aprobado (15, 16) — 354 KB | `tmp/micro/largo/capas240/r7_micro_10s_240.mp4` |
| Loop de la nave, vertical, 10 s, con micro | Aprobado (06 v5, 16) — 262 KB | `tmp/micro/largo/capas240/nave_10s_240.mp4`; con micro, `tmp/micro/movil/nave_micro240.mkv` (el paso 0 confirma cuál es el final) |
| Transición nave ↔ sacristía, escritorio (ida y vuelta) | Aprobada (17): H3 a 1080p + detalle de la placa, difusión ligera al moverse; AV1 189 / 194 KB, HEVC 375, H.264 794 | `tmp/micro/trans_esc/hd_det/ida_final_*.mp4` |
| Transición nave ↔ sacristía, vertical (ida y vuelta) | Aprobada (17): micro seguido, foco por cuadro, obturador; 397 / 380 KB en H.264, AV1 ~107 KB | `tmp/micro/trans/` |
| Placa de la sacristía, escritorio | Elegida (17): Klein s11. **Sin loop** | `tmp/micro/trans_esc/klein/` |
| Loop de la sacristía, vertical | Sólo uno de **5 s** del 2026-10-05, antes de la v5 y del 16 | `tmp/movil-06/web/sacristia.mp4` (155 KB) |
| Decisiones de navegación, peso y layout | Cerradas: 11 (un gesto, una sección), 05 (AV1 → HEVC → H.264, entrada ≤ 3 MB, gesto ≤ 1 MB, cascada por `fetch` → `blob:`), 03 (C en el hero, D en texto, E en Música) | tickets |
| Prototipos web en HTML plano | Funcionan: navegación por gesto, empalme loop → transición, precarga | `tmp/transicion-4/web/`, `tmp/movil-06/web/`, `tmp/cine-look/web/` |
| Medidor de peso en navegador real | Hecho | `scripts/medir-peso.mjs` |
| Integración en Astro | **No empezada.** `dev` todavía sirve la arquitectura vieja: 80 AVIF en `<canvas>` (`AltarScene.astro`, `scrollScene.ts`, `public/scene`, 10 MB) | `src/` |

`dev` va 124 commits por delante de `main`, y `main` tiene arreglos propios (astro 6.4.8, monograma y velo del hero para
WebKit) que no están en `dev`.

## Lo mínimo que falta, en orden

"Sesión" = una sesión de trabajo de 3–4 horas con el usuario. El ritmo real de los tickets es de una pieza aprobada por
sesión (tres semillas, el usuario elige, retoque), aunque el cómputo de un loop sea de ~27 minutos (~18 de H3, ~1.5 de RTX,
~7 de CPU, ticket 16). Por eso las estimaciones van en sesiones y no en minutos de GPU.

| # | Paso | Quién / herramienta | Esfuerzo |
|---|---|---|---|
| 0 | **Inventario y congelado.** Copiar los videos aprobados a una carpeta de entrega fuera de `tmp/` (los maestros sin pérdida donde existan) con nombres finales; comprobar que el loop de la nave ya no tiene el defecto de la rosa del 2026-10-10 ("still missing pieces"). | web / ffmpeg | **Hecho** 2026-10-13 (`d4ff452`) |
| G1 | **Confirmar con el usuario el sitio del joven.** Medido (`tmp/props-06/medir_libre.py`): sólo le quedan bancas izquierdas, filas 6–12, que en escritorio caen en el hueco del texto del 03. | conversación | **Hecho** (`dd32e44`) |
| G2 | **Placa de escritorio con gente.** Sobre `tmp/props-06/s44_vacia.png`, devolver la mujer del velo y el fiel de s44; Klein añade joven y texana en recortes centrados en su sitio medido, pegando sólo la caja (`pegar_zona.py`). Mover `PROPS` en `blender/transicion.py` a esos sitios y sacar la profundidad (`pases_reproy.py`, también `-- vacio`). | ComfyUI (Klein) + Blender | **Hecho** (`2b1d93d`) |
| G3 | **Vertical por reproyección** desde la placa nueva (`reproyectar.py`, base de huecos sin gente `s33_vacia_s7` a 704×1280, un pase de Klein, `pegar_huecos.py` sólo en los huecos). El usuario compara sujeto por sujeto al 100 % y aprueba sólo si gente, ropa y props coinciden. | Blender + ComfyUI | **Hecho** (`68b37ae`) |
| G4 | **Placa real v5 de los dos formatos** (Klein 4 MP con el tono de la placa NR + foco de lente). | ComfyUI | **Hecho** (`adcdcce`) |
| G5 | **El micro encima**, re-pegado y re-retocado contra cada placa nueva (máscaras, rosa, espiral, brillo `TOPE=1.2`; cadena de `docs/handoffs/2026-10-10-micro-colgado.md`). | ComfyUI + ffmpeg | **Hecho** (`c56dbb9`) |
| G6 | **Loops de la nave de 10 s**, escritorio y vertical, con la cadena del 16 sobre las placas nuevas. | ComfyUI | **Hecho** (`1f7f602`; rehechos con el tallo nuevo, `2e0c611`) |
| G7 | **Transiciones nave ↔ sacristía del 17 rehechas**, escritorio (H3 a 1080p + detalle de la placa, difusión ligera al moverse) y vertical (micro seguido, foco por cuadro, obturador), con los pases de Blender de la maqueta con la pila y la gente. | Blender + ComfyUI | **Hecho** (`8d0a729`; sólo la mitad de la nave cambió, la vertical sigue con el método del 17) |
| 1 | **Loop de la sacristía, escritorio, 10 s, v5** desde la placa s11: placa real (Klein 4 MP + NR), zonas vivas, H3 nativo a 928×512, RTX ×2, velas y polvo de 240, foco de lente, LOOK y halación (cadena del 15/16). Revisar el empalme con el final de la ida aprobada; si la placa v5 se separa de lo que la ida dibujó, rehacer sólo la segunda mitad de la ida desde la placa nueva. | ComfyUI (H3, Klein) + Blender (pases) | **Hecho** 2026-10-13 (sin H3; ticket 16, sección Sacristía) |
| 2 | **Loop de la sacristía, vertical, 10 s, v5** con la cadena vertical del 16 (H3 a 512×928, sólo lo que se mueve, RTX ×1.375). Plan de emergencia si no da el tiempo: salir con el de 5 s del 2026-10-05, sabiendo que contradice el 16 y que no tiene el look v5. | ComfyUI | 1 sesión |
| E1 | **Maquetas de producción del 07** (decisiones en el ticket 07): vestidor (ropero, espejo, tocador, arbotantes), cripta (bóveda, altar, reja de la clave) y atrio (fachada, reja, banqueta, el poste a la derecha del portal para que la esquina quede negra); la guitarra con su asset, el teléfono de disco de oro modelado con su silueta real; pases de profundidad. Parte de `tmp/07/blockout.py`. | Blender (`kiln-prop`) | 1–1.5 sesiones |
| E2 | **La troca**: pickup doble cabina negra estilo Lobo, cromo y calaveras verticales, sin emblemas, medida contra `tmp/07/tablero/atrio_C2_lobo_elegida.png` (o la maqueta `troca2` mejorada). | Blender (`kiln-prop`) | 0.5–1 sesión |
| E3 | **Placas de escritorio de camarín, cripta y atrio**: Klein 4 MP + tono NR + foco de lente, tres semillas por espacio; muros a cal/almagre, nada de caras inventadas, la esquina del atrio a negro. | ComfyUI (Klein) | 1.5 sesiones |
| E4 | **Placas verticales por reproyección** (método de G3, sin gente) desde las tres placas de E3. | Blender + ComfyUI | 1–1.5 sesiones |
| E5 | **Loops de 10 s de los tres espacios, escritorio y vertical** (cadena del 16): arbotantes y su reflejo en el espejo, el polvo del haz y las dos velas, la neblina y el sodio. Seis loops, ~27 min de cómputo cada uno. | ComfyUI (H3) + RTX | 2–3 sesiones, ~3 h de GPU |
| E6 | **Transición sacristía ↔ camarín**: empujar hacia el cuadro de s11, que se abre como puerta (bisagra en la maqueta de la sacristía, sin tocar sus placas); empalma con el loop del paso 1 y con la placa de E3; escritorio y vertical. | Blender + ComfyUI | 2 sesiones |
| E7 | **Transición camarín ↔ cripta**: oclusor de la puerta del ropero y bajada por la escalera, con el método del 17 sin micro; escritorio y vertical. | Blender + ComfyUI | 1–1.5 sesiones |
| E8 | **Transición cripta ↔ atrio, el único umbral**: subir y salir por el portal a la neblina, de lo oscuro a la noche abierta. Es la primera vez que una transición cambia de interior a exterior: puede pedir una ronda más. Escritorio y vertical. | Blender + ComfyUI | 1.5–2 sesiones |
| E9 | **El 07 en la página**: los tres loops y las tres transiciones entran en la lista de espacios del reproductor del paso 5 (sustituyen el fondo negro de El grupo, Contratación y Cierre); `medir-peso.mjs` con los gestos nuevos. | web | 0.5 sesión |
| 3 | **Hero → nave (ticket 08) por el negro, sin render.** El hero ya termina en un fundido de 1.5 s; la nave entra desde negro con su loop, que ya trae el micro (cumple la nota del 08 y la condición de la spec del micro). Es el mismo fundido que el 05 aprobó para los saltos del menú. | web | 0.5 sesión |
| 4 | **Cascada de códecs y pósters.** Cada loop y transición en AV1 crf ~40, HEVC crf ~26 con `-tag:v hvc1` y H.264 (`halacion.sh` con `VC=` para el maestro, `ladder.sh` para la escalera); un póster por espacio para `prefers-reduced-motion`. Con el 07 son seis loops y seis transiciones más. | ffmpeg | 1 sesión |
| 5 | **Integración (ticket 09).** Sustituir `AltarScene.astro` y `scrollScene.ts` por: controlador de gesto (rueda, teclado, swipe, botones, `#ancla` con `hashchange`, foco), reproductor de loop + ida/vuelta con la costura de 20 cuadros y la mezcla de 0.15 s, cola de precarga inmediato → cascada por `fetch` → `blob:` con `data-precarga`, `<source>` por códec, espera con aviso cuando el gesto llega antes que el archivo, corte directo con movimiento reducido. Es portar los prototipos de `tmp/`, no diseñar. Se retiran `public/scene`, `scene.json`, `check-budget.sh`, `scrollScene.test.ts` y el test roto `capasEstacion.test.ts`; `bun test` en verde. | web | 3–4 sesiones |
| 6 | **Capa de UI** según el 03: C en el hero (logo, chips, WhatsApp), D en Quiénes somos sobre la nave, E en Música sobre la sacristía (un disco a la vez, 01/N; faltan 5 de las 9 portadas), el aviso de carga (placeholder del 05: la línea roja bajo el número del menú) y el indicador de sección. El Grupo, Contratación y Cierre sobre negro provisional hasta que lleguen E5–E8 (ver abajo). | web | 1–2 sesiones |
| 7 | **Contraste AA sobre la escena.** Medir el velo de D y la viñeta de E contra el cuadro más claro de cada loop (la tabla de `DESIGN.md` está contra negro plano y el 0.62 del velo era para la escena AVIF vieja); corregir el crema sobre rojo a 4.0:1 que marcó impeccable; correr `npx -y impeccable@4.5.2 detect --json` sobre `dist/`. | web | 0.5 sesión |
| 8 | **QA en teléfonos reales**: un iPhone anterior al 15 Pro (HEVC), uno reciente (AV1), un Android de gama media; modo de bajo consumo de iOS; `scripts/medir-peso.mjs` con red 4G para confirmar entrada ≤ 3 MB y gesto ≤ 1 MB; Lighthouse móvil (`cloudflare:web-perf`). | QA | 1 sesión |
| 9 | **Merge y deploy.** `/code-review` de `dev`, merge a `main` resolviendo los arreglos que sólo están en `main`, `bun run build`, `npx wrangler deploy` (antes, las skills `cloudflare:wrangler` y `workers-best-practices`, como pide `CLAUDE.md`), prueba de humo en mafiatumbada.com y `www`. | deploy | 1 sesión |

**Lo que queda, contado el 2026-10-13** (paso 0 y G1–G5 hechos, G6 en curso):

| Pista | Pasos | Sesiones |
|---|---|---|
| Escena con la GPU sola | resto de G6, G7, 1, 2, E5, E6, E7, E8, 4 | 12–15.5 |
| Escena que se mete entre tandas | E1, E2, E3, E4 | 4–5.5 |
| Web, en paralelo (otro worktree) | 3, 5, 6, E9 | 5–7 |
| Final, en serie | 7, 8, 9 | 2.5 |
| **Total** | | **23.5–30.5** |

El 07 suma 11.5–15 sesiones (E1–E9 más la media sesión de más del paso 4). El camino crítico es la pista de la GPU sola
más el final: **14.5–18 sesiones** si E1–E4 se hacen entre tandas y la web va por su lado; **18.5–23.5** si el usuario no
puede aprobar dos pistas a la vez y E1–E4 quedan en serie. Los pasos web no usan la GPU: avanzan con los videos de antes
de la pila como provisionales, y al final se reemplazan los archivos con los mismos nombres.

Calibración: G1–G5 estaban en 4.25–7.25 sesiones y se hicieron la noche del 2026-10-12 al 13 en unas dos horas, con
varios roles a la vez. Las sesiones de esta tabla son la unidad de antes (una pieza aprobada por sesión); el ritmo real
puede ser bastante más rápido, y la fecha de abajo es un techo, no una promesa.

### Qué del 07 puede ir a la vez que G6/G7 y qué pide la GPU sola

Una sola GPU de 12 GB: H3, Cycles y RTX no corren juntos.

- **Se solapa con G6/G7:** E1 y E2 (modelado y maquetas en Blender con workbench o CPU; los pases de profundidad en Cycles
  son de segundos y entran entre tandas), E3 y E4 (Klein, ~20–50 s por semilla, sólo con la cola de ComfyUI vacía, una
  semilla a la vez, como se hizo con las previas del 07), E9 y la parte web del 4 (CPU).
- **Pide la GPU sola:** E5 (seis loops con H3, ~3 h de GPU), E6–E8 (H3 a 1080p, FILM ×8, pases de Cycles por cuadro) y
  los códecs AV1 del 4 si se hacen en la GPU. Van después de G7 y de los loops de la sacristía (1, 2): E6 empalma con el
  loop de escritorio del paso 1, así que no puede ir antes.

### Cómo quedan El grupo, Contratación y Cierre

Con el 07 de vuelta, la secuencia con escena es **hero → nave → sacristía → camarín → cripta → atrio**. Mientras no
lleguen E5–E8, las tres últimas secciones se integran sobre negro con la viñeta (el gesto después de la sacristía funde a
negro en 0.6 s, lo decidido en el 05), con los layouts del 03: El grupo en E (un integrante a la vez, fotos de
`public/members/`), Contratación en D con el botón de WhatsApp siempre a la vista, y Cierre con el monograma, redes y ©.
El contenido ya existe en `index.astro`; cuando lleguen los loops y las transiciones, E9 cambia el fondo negro por su
espacio. Si la fecha aprieta, se puede desplegar así y cambiar los archivos después.

El botón de WhatsApp para contratar queda, entonces, en el hero (primera pantalla), en Contratación y en el enlace de
Contratación del menú, que salta con el fundido. **No** propongo un botón flotante permanente: no está en el 03 y
tapa la escena; si después el usuario lo pide, es una pieza pequeña.

## Lo que se recorta a "después"

- **Hero → nave renderizado** (una transición real en vez del fundido por negro).
- **Ticket 10, lo que queda abierto**: las cinco reglas de gusto para `DESIGN.md` y la elección entre las variantes A/B/C
  de la pieza E en Claude Design. Para la versión 1 se usa la variante A del prototipo y `DESIGN.md` tal como está.
- **Vertical de la transición con el método de 1080p** (H3 grande + detalle de la placa): la vertical aprobada ya está
  bien.
- **Parpadeo de la brasa del micro** con periodo de 120 dentro del loop de 240.
- Pendientes heredados del mapa: el escudo en la camiseta del hero y el permiso de los directores de los videos (si este
  último bloquea algo publicado, hay que resolverlo antes del deploy, no después).

## Riesgos

- **Todo lo aprobado está en `tmp/`, sin versionar.** Un borrado o un disco que falla se lleva semanas. El paso 0 va
  primero por eso.
- **Tiempo de render y fallos de ComfyUI.** Una sola GPU de 12 GB: Blender y H3 no corren a la vez. ComfyUI se cuelga en
  "Model Initializing" con la segunda o tercera semilla en cola (pasó cuatro veces; se reinicia con `start-comfy.ps1`,
  ~1 min). El cómputo no es el problema; lo es que cada pieza pida dos o tres rondas de aprobación. Si los loops de la
  sacristía piden más de una ronda, se come el margen.
- **Empalme de la sacristía de escritorio.** La ida aprobada termina en la placa s11 de Klein; el loop nuevo sale de su
  versión v5. Si no empalman (el umbral de los tickets ronda 5–7 de diferencia), hay que rehacer la segunda mitad de la ida.
- **Móvil:**
  - iPhone anterior al 15 Pro no decodifica AV1: depende del HEVC con `hvc1`; sin él cae a H.264 y el gesto pasa de 1 MB.
  - El modo de bajo consumo de iOS bloquea el autoplay: hace falta el póster y que el primer toque arranque el video.
  - Memoria: con el 07 la cascada pasa de unos ocho videos en `blob:` a unos veinte; en un Android de gama media puede
    haber descartes de pestaña. Medirlo en el paso 8 y, si pasa, liberar los `blob:` de espacios lejanos.
  - El swipe vertical choca con el pull-to-refresh y con la barra de direcciones: `overscroll-behavior` y `100svh`.
  - El video del hero en teléfonos ya dio problemas en `main` (se quitó y se revirtió): el merge tiene que conservar los
    arreglos de WebKit de `main`.
- **Peso y rendimiento.** En papel, la entrada móvil en AV1 queda en ~2 MB (hero 1.5 MB + loop y transición de la nave) y
  cada gesto muy por debajo de 1 MB, pero sólo `medir-peso.mjs` sobre el sitio integrado lo confirma. El LCP es el póster
  del hero. `worker.js` sólo resuelve Range para `/video/*`: los videos nuevos tienen que vivir ahí o ampliar
  `run_worker_first`.
- **El umbral del 07 (E8) es técnica nueva.** Ninguna transición ha pasado todavía de interior a exterior; el salto de
  exposición al salir a la neblina puede pedir una ronda más de lo estimado.
- **`dev` y `main` divergen** (124 commits contra varios hotfixes): reservar parte de la sesión 9 para el merge.

## Fecha

**Con el 07 en la versión 1 (2026-10-13): ~2026-11-22.** Al ritmo que este documento ya suponía (23 sesiones en 34 días,
~0.68 por día), el camino crítico en serie (18.5–23.5 sesiones) termina entre el 2026-11-09 y el 2026-11-17; se dejan cinco
días de margen para las rondas de aprobación de tres espacios nuevos y del umbral. Si E1–E4 caben entre las tandas de
G6/G7 (camino crítico de 14.5–18), el ~2026-11-15 de antes se sostiene. Con el ritmo medido la noche del 12 al 13, puede
ser antes.

Antes era **~2026-11-15, camino B** (17–23 sesiones en 34 días, sin el 07). El 2026-10-25 sólo era posible con el camino A
(9.5–13 sesiones en 13 días, con margen hasta el 2026-11-01); queda como referencia.

Si hiciera falta algo en vivo antes, el orden permite desplegar sin el 07 (El grupo, Contratación y Cierre sobre negro) o
incluso sin gente (pasos 0, 3–9 con los videos de antes de la pila) y cambiar los archivos después. No está decidido; lo
decide el usuario si llega el caso.

## Qué del pipeline sirve para el portafolio

El rediseño del portafolio va a mostrar mosaicos en vivo de los sitios del usuario dentro de la escena. Lo que se lleva de
MTO tal cual:

- **El reproductor web**: un gesto = una sección, loop + ida/vuelta con la costura de 20 cuadros y la mezcla de 0.15 s,
  cola de precarga inmediato → cascada por `fetch` → `blob:`, `<source>` AV1/HEVC/H.264 y corte directo con movimiento
  reducido. Hecho bien en el paso 5, es un componente que sólo cambia la lista de espacios.
- **`scripts/medir-peso.mjs`** y el presupuesto por ventana del 05 (entrada ≤ 3 MB, gesto ≤ 1 MB).
- **La escalera de códecs** (`halacion.sh` con `VC=`, `ladder.sh`) y los crf calibrados.
- **Los layouts C/D/E del 03**: contenido sobre la escena, la escena no se aparta, y el hueco oscuro que cada toma deja.
- **La cadena de imagen**: maqueta gris de Blender → Klein → H3 con ControlNet de profundidad → RTX → LOOK, los loops
  sobre placa fija (sólo las zonas vivas), el obturador con FILM ×8 y el corte escondido tras un oclusor con la máscara de
  Blender.
- **La segunda cámara sacada de una placa aprobada por reproyección** con la Z de Blender, en vez de otra tirada de Klein.
- **La pieza clave para los mosaicos en vivo: la capa 2D seguida con la cámara de Blender** (`tmp/micro/trans/pista_micro.py`,
  ticket 17). Hoy proyecta un punto del micro por cuadro; extendido a las cuatro esquinas de una pantalla, da por cuadro
  la posición de un plano en el video, y el navegador puede poner encima un mosaico HTML real (iframe o video del sitio)
  con `matrix3d`, sincronizado al cuadro con `requestVideoFrameCallback`. Eso **no está probado**: la sincronía al cuadro
  en Safari y el desenfoque de movimiento del mosaico (que el micro resolvió en el render, no en el navegador) son el
  primer experimento después del 25.

Lo que **no** se reutiliza: la maqueta de la iglesia, los prompts de Klein del santuario y la dirección de arte Gótico
Tumbado. El LOOK (2383 + halación) se puede llevar como punto de partida, no como regla.
