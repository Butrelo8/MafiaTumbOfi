# Handoff — hero nuevo y transiciones con movimiento

> 2026-10-04, 16:15 CST. Rama `dev`. Formato de la skill `matt-handoff` (mpaf).
> Se guarda en el repo, como el anterior (`2026-09-18-profundidad.md`), para que
> sobreviva entre sesiones.

## Dónde quedó

**Hecho en esta sesión, sin commit** (el usuario no lo ha pedido):

| Archivo | Qué |
|---|---|
| `scripts/build-hero.sh` | Corte del hero: 8 tomas de 2 videos del canal, look con LUT, salidas web. Se lee de arriba abajo; las decisiones van comentadas ahí |
| `public/video/hero{,.av1}.mp4`, `hero-v{,.av1}.mp4`, `hero-poster.jpg` | Lo que produce el script. `hero.mp4` reemplaza al de 10 MB |
| `src/pages/index.astro` | `<video>` de fondo en el hero (vertical si `max-aspect-ratio: 1/1`), play/pausa por `IntersectionObserver`, nada con movimiento reducido, velo medido |
| `src/components/AltarScene.astro` | `.marketing-main > .hero { z-index: 3 }`: el hero tapa la capa de frente de la nave |

**No son de esta sesión** y no van en sus commits: `.claude/settings.json`,
`.gitignore`, `CLAUDE.md`, `.claude/skills/`, `.claude/mpaf.lock.json`,
`blender/assets/*`, `blender/pase.py`, `docs/pase-visual-2026-09-23.md`.

`.mcp.json` (gitignored) ahora registra el puente de **Resolve** y pasa
`BLENDER_MCP_PORT=9877`, copiado de `Davincy Resolve/.mcp.json`: el add-on de
Blender tiene que estar en 9877 porque CursorBridge de Resolve ocupa el 9876.

## Lo primero que hay que hacer

1. **Verlo en el navegador.** No está verificado a ojo. Las capturas de
   browsermcp sólo muestran la escena, ni el texto ni el encabezado, **también
   en la versión de HEAD**: el fallo es de la herramienta. chrome-devtools se
   desconectó. Exponer el dev server a `0.0.0.0` lo bloquea el permiso; `astro
   preview` en localhost sí llega al Chrome de Windows. Revisar: el video corre,
   el texto se lee, el loop no salta, móvil vertical, y que al subir el hero se
   destape la nave sin que las columnas de la capa de frente se peguen encima.
2. **Commits**, si el usuario los pide: uno para `scripts/build-hero.sh` + los
   videos, otro para el marcado (`index.astro`, `AltarScene.astro`).

## Pendientes y decisiones abiertas

- **Presupuesto de peso.** `scripts/check-budget.sh` ya daba **4.6 MB** contra
  3 MB de techo *antes* de esta sesión, y no cuenta el video. El hero suma 2.5 MB
  (AV1 1080p), 2.7 MB (H.264 720p), 1.5 MB (AV1 vertical) o 2.4 MB (H.264
  vertical, el de los iPhone sin AV1, anteriores al A17). Hay que decidir con el
  usuario.
- **Test roto anterior a esta sesión:** `capasEstacion.test.ts` → "una estación
  sin capa no rompe el resto" (`src/lib` no se tocó). 49 de 50 pasan.
- **Marcas a la vista:** el escudo de la selección en la camiseta de Héctor en
  las tomas del en vivo. El usuario no ha dicho nada; preguntar.
- **Permiso de los directores** de los videos de YouTube: se le preguntó y no
  respondió. La banda no tiene los originales.
- **Roster:** sólo los tres de `src/data/members.ts` salen en primer plano. El
  bajista de la sesión ya no toca con ellos; al fondo de la toma `S 197.2` se le
  ve desenfocado, y se le ofreció cambiarla.
- **Fallo en otro repo, sin tocar:** `Davincy Resolve/scripts/luts_hoja.sh`
  toma `T=1` por defecto y con una imagen fija no saca el cuadro base. Arreglo:
  `T=0` si la entrada es imagen.

## Lo que sigue: rehacer la escena con transiciones con movimiento

Decidido con el usuario en esta sesión:

- **La animación actual es débil.** Tres razones medidas: las estaciones son la
  misma capilla con la cámara avanzando (nave, altar y retirada casi iguales),
  dentro de la escena no se mueve nada (la fase 3.3 sigue pendiente) y se lee como
  maqueta (ver `docs/pase-visual-2026-09-23.md`).
- **Se queda el concepto de la capilla y cambia la ejecución.** Cada sección es
  un **espacio distinto del santuario**, conectado físicamente: nave → sacristía
  (sonido) → camarín de las hornacinas → cripta (reliquia) → atrio exterior de
  noche (retirada). Las mismas secciones de hoy. Que el atrio sea la calle con
  la troca del videoclip original se propuso; no está aprobado.
- **Transiciones sin fundidos, con movimiento.** Base: **corte escondido tras un
  oclusor oscuro** (la cámara pasa tras una columna, banca o marco, el cuadro va a
  negro y de ahí sale el lugar siguiente). Una sola vez, atravesar un umbral
  (arco, humo de copal) y empujar hacia un retrato que se abre. Por qué funciona:
  cada lugar se genera por separado y la unión cae en negro, así que la IA no
  tiene que mantener coherencia entre lugares.
- **Hero → capilla:** el hero termina en negro (fundido de 1.5 s en la última
  toma). Hoy el hero sólo sube con el scroll y destapa la nave; el corte por el
  negro avanzado con el scroll queda para esta fase.

**Herramientas** (método en
`ProyectoInvestigación/research/render-3d-calidad-2026-10-01.md`, ya probado en
el repo de Resolve):

1. **Blender:** sólo la maqueta gris y la cámara, más el pase de profundidad
   (`Davincy Resolve/tools/blender/pases.py` y `profundidad.py`).
2. **ComfyUI:** Flux 2 Klein para el cuadro de estilo de cada lugar; MiniMax H3
   Fun ControlNet (instalado, ~1.5 min por 5 s a 864×480) para pasar de la
   profundidad al look. La referencia manda el look y la profundidad, la geometría.
   El neón M⚡T y cualquier texto se componen encima, nunca se dejan a la IA.
3. **DepthFlow** (`Davincy Resolve/tools/depthflow`, `scripts/parallax.py`): ruta
   barata, imagen de Klein con parallax 2.5D, para lugares sin movimiento propio.
4. **Resolve / ffmpeg:** el mismo LUT del hero para que todo case (ver
   `scripts/build-hero.sh`).
5. **Web:** la transición, un video all-intra avanzado con el scroll (ficha
   verificada `ProyectoInvestigación/research/visuales-fichas/video-que-avanza.md`);
   el loop del lugar, cuando el scroll se detiene. Inspiración: white-desert.com
   (transiciones entre destinos), en `visuales.md`.

**Primera prueba propuesta y aceptada** (~2–3 h): una sola transición, nave →
sacristía pasando tras una columna, con los dos loops y el avance con el scroll
en la página. Probar las dos rutas del lugar (DepthFlow y MiniMax) lado a lado
antes de rehacer el resto.

## Trampas de esta sesión

- **Gemini inventa** lo que dice ver en YouTube: del en vivo describió escenario,
  humo y contraluz, y es una plaza con luz blanca. Sirve como primer barrido;
  verificar siempre con frames (`ffmpeg -skip_frame nokey`, 23 s para 46 min en
  4K, y `tmp/hero/hoja.py` para hojas con timestamp).
- **YouTube cortó yt-dlp con 403** a mitad de la descarga; `yt-dlp -c` la retoma.
- Las fuentes 4K (3.6 GB) están en `tmp/hero/src/` (ignorado). El script las
  necesita para re-renderizar.
- Melara y las *Film Looks* esperan log: sin CST salen quemadas (ver
  `Davincy Resolve/luts/README.md`). Por eso se usó `film/print`, que va directo
  sobre Rec709.

## Cómo hablar con el usuario

Español, conciso. Decide rápido, quiere ver renders, no descripciones: se dejan
en `tmp/` y se le da la ruta de Windows (`E:\Cursor Projects\MTO\...`). Prefiere
que se le contradiga con datos.

## Skills sugeridas

- `frameref` — referencias de cine para el look de cada espacio del santuario
  antes de generar en ComfyUI.
- `brainstorm` — si hay que cerrar qué espacio es cada sección.
- `run` — para levantar la página y verla.
- `cloudflare:web-perf` — la decisión del presupuesto, con LCP y peso reales.
- `design:accessibility-review` — el velo del hero se midió (0.44 en móvil); la
  tabla de contraste de `DESIGN.md` sigue sin rehacerse.
- `code-review` — antes de mezclar `dev` en `main`.
