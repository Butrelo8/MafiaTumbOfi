# Plan de implementación — Profundidad, pop-in y estación *altar*

> Deriva de [`docs/specs/2026-09-17-santuario-profundidad-design.md`](../specs/2026-09-17-santuario-profundidad-design.md),
> aprobado 2026-09-17. Rama `dev`.
> Cada fase termina en una puerta. No se empieza una fase sin cerrar la anterior.
>
> **Lee antes de tocar `blender/`:** [`docs/blender-notas.md`](../blender-notas.md).

## Fase 0 — La guitarra y el encoder

Barata, y las dos pueden obligar a cambiar algo **antes** de renderizar 35 min.

| # | Tarea | Verificación |
|---|---|---|
| 0.1 | ~~Resolver la licencia de `guitarra.blend`~~ | **Hecho 2026-09-17: CC0** (https://blendswap.com/blend/31078). Sin atribución obligatoria. Anotado en `CREDITOS.md` |
| 0.2 | ~~Sustituirla~~ | No hace falta: CC0 |
| 0.3 | Confirmar encoder con alfa | `avifenc --version`. Si no está: `cwebp -version` y la salida pasa a WebP |

**Puerta 0:** 0.1 y 0.2 cerradas el 2026-09-17. Queda 0.3.

## Fase 1 — Encuadres

Archivo: `blender/altar.py`, tabla `ESTACIONES` (línea 43).

| # | Tarea | Verificación |
|---|---|---|
| 1.1 | Lente de *hornacinas* 34 → 28 mm | Still a 800×450: el retablo entra entero |
| 1.2 | Insertar fila `altar` como segunda estación, frames 1/21/41/61/81/101 | `render_stills` escribe seis, no cinco |
| 1.3 | Renderizar candidatos de *altar*: 24 / 28 / 20 mm × 3-4 offsets de curva | Stills a 800×450 en `tmp/`, en los **dos** formatos |
| 1.4 | Ajustar altura y distancia de foco del elegido | El retablo enfocado, la nave en desenfoque |

**Puerta 1: la elige el usuario mirando.** Es la fase más barata de tirar.
Ojo en 1.3: un 24 mm frontal en 9:16 mete mucho techo y mucho piso; si el
formato móvil sale vacío, la salida es otro offset en la curva para ese formato,
**no** otra lente.

## Fase 2 — Render

Una sola tanda. Volver a lanzarla cuesta 35 min.

| # | Tarea | Verificación |
|---|---|---|
| 2.1 | Decidir frames por tramo: 20 o 30 (spec §4b) | Se decide **antes** de lanzar, no después |
| 2.2 | Decidir resolución desktop: 1600×900 o 1920×1080 | Ídem |
| 2.3 | Tramos nave→altar y altar→sonido | 2 × N frames, sustituyen al `tramo-0` actual |
| 2.4 | Tramos 1 y 2 (los toca el cambio de lente) | Re-renderizados |
| 2.5 | Las 6 estaciones | 6 stills por formato |
| 2.6 | `render_capa_frontal()` a resolución real, los dos formatos | 12 PNG RGBA |
| 2.7 | Revisar `margen` (0.78) estación por estación | Si en alguna entra de más —la banca completa, por ejemplo— baja para esa |

**Puerta 2:** componer cada capa de frente sobre el frame plano de su estación y
comparar contra el frame plano original: **idénticos**. Si difieren, hay un
objeto renderizado dos veces con bordes distintos. Esto se comprueba antes de
encodear nada.

## Fase 3 — Encode y datos

| # | Tarea | Verificación |
|---|---|---|
| 3.1 | `scripts/build-scene.sh`: rama de capas con alfa vía `avifenc`/`cwebp` | Las 12 capas encodean y **conservan el alfa** al abrirlas |
| 3.2 | CRF de capa, más agresivo que el 30 de estaciones | Medido, no estimado: mirar una y pesarla |
| 3.3 | `scripts/scene-json.py`: `capaFrente: { imagen, bytes }` por estación | `scene.json` valida contra el tipo `FormatoEscena` |
| 3.4 | `scripts/check-budget.sh` | Peso por formato anotado en el commit |

**Puerta 3:** `bun run build` pasa y la página sigue viéndose **como hoy** — sin
capas todavía, porque nadie las lee aún.

## Fase 4 — Capa web

| # | Tarea | Verificación |
|---|---|---|
| 4.1 | `scrollScene.ts`: callback opcional `alCambiarFrame` donde ya se escribe `canvas.dataset.frame` | Una línea. `bun test` sigue verde |
| 4.2 | `src/lib/capasEstacion.ts`: `cercania()` pura + montaje | Test propio al lado de `scrollScene.test.ts`: casos en la estación, a media ventana, y fuera |
| 4.3 | `AltarScene.astro`: los `<img data-capa-frente>` desde `scene.json` | Si falta `capaFrente`, no se pinta nada y la página queda como hoy |
| 4.4 | `filter: brightness(0.38)` atado por variable CSS al velo 0.62 | Un solo sitio define el velo; cambiarlo mueve los dos |
| 4.5 | Pop-in por `data-cerca` + transición CSS | Con `data-cerca` ausente el titular es **visible** |
| 4.6 | `prefers-reduced-motion` | Capa opaca y fija, pop-in sin animar |

**Puerta 4:** en el navegador, la capa de frente entra y sale sin que se vea el
desencaje con el fondo en movimiento. Aquí se mide `VENTANA`: arranca en 4
frames, sube hasta que el fundido se sienta suave y baja en cuanto la vela
flote sobre un fondo que ya se movió.

## Fase 5 — Contenido

| # | Tarea | Verificación |
|---|---|---|
| 5.1 | `bio-section` sube antes de Música y pasa a `data-estacion="1"` | Orden: logo → quiénes son → música → integrantes → contratar |
| 5.2 | Renumerar `data-estacion` a 0-5 | Centrar cada sección da su frame exacto, las seis |
| 5.3 | Patrón titular incrustado + panel opaco (z:3) en las seis | El panel tapa la capa de frente al subir |
| 5.4 | Hero: logo + metadatos en una línea + CTA. `hero-blurb` se muda al panel de *altar* | La bio deja de estar duplicada |
| 5.5 | Footer: monograma incrustado, socials y copyright en panel | Ningún enlace detrás de una vela |
| 5.6 | Borrar `Marquee.astro` y su uso | — |
| 5.7 | Borrar `hero-video` y `src/lib/heroVideo.ts` | Y sus imports; `bun run build` sin avisos |
| 5.8 | Borrar `.hero::before` / `::after` de su hoja y las anulaciones de `AltarScene.astro` | Se borran en origen, no se anulan desde otro archivo |
| 5.9 | Mirar `hero-grain` junto al grano de Cycles | Si se nota doble, se quita |

**Puerta 5:** con JS desactivado se lee la página entera, en orden y con sus
enlaces.

## Fase 6 — Medición y cierre

| # | Tarea | Verificación |
|---|---|---|
| 6.1 | Recalcular el velo sobre la composición final, por estación, en la zona del texto | Percentil 95, el método que ya usa el repo |
| 6.2 | Si *altar* obliga a subir el velo, sube **para todas** | Un velo por estación no vale lo que cuesta |
| 6.3 | Rehacer la tabla de contraste de `DESIGN.md` | AA en las seis |
| 6.4 | Revisar oclusión del titular en las seis | La capa **rodea** el titular, no lo cruza. Si cae encima, el titular cambia de columna |
| 6.5 | Altura de página (~970vh) | Si se ve largo: `.tramo-espacio` 50svh → 25svh, sabiendo que acelera la cámara |
| 6.6 | Actualizar `docs/HANDOFF.md` | Estado, pendientes y bloqueos al día |

**Puerta 6:** los siete criterios de aceptación de la spec.

## Qué NO entra

Parallax `translateZ`, botones de navegación por estación y los loops de vídeo
—que con seis estaciones ahora son 6, no 5—. Están en "Fuera de alcance" de la
spec con su motivo.
