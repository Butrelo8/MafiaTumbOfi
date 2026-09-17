# Plan de implementación — Santuario M⚡T

> Deriva de [`docs/specs/2026-09-16-santuario-3d-scroll-design.md`](../specs/2026-09-16-santuario-3d-scroll-design.md),
> aprobado 2026-09-16. Rama `dev`.
> Cada fase termina en una puerta. No se empieza una fase sin cerrar la anterior.

## Fase 0 — Entorno (antes de modelar nada)

Barata, y evita descubrir un bloqueo a mitad de la fase 3.

| # | Tarea | Verificación |
|---|---|---|
| 0.1 | Confirmar versión de Blender y el engine EEVEE | `bpy.app.version` ≥ 4.2; en 5.x el identifier es `'BLENDER_EEVEE'` y ya **es** el motor Next |
| 0.2 | Confirmar GPU visible para Blender | Preferencias de Cycles/EEVEE listan el dispositivo NVIDIA |
| 0.3 | Resolver rutas WSL↔Windows | Escribir un PNG de prueba desde Blender a `E:\Cursor Projects\MTO\tmp\` y leerlo desde WSL en `/mnt/e/…` |
| 0.4 | Confirmar `ffmpeg` con AV1/WebM y un codificador AVIF | `ffmpeg -encoders \| grep -E 'av1\|webm'`; `avifenc --version` o `ffmpeg` con `libaom` |
| 0.5 | Medir un frame de referencia | Renderizar un still de prueba oscuro a 900×1600, convertirlo a AVIF y pesarlo |

**Puerta 0:** las cinco pasan. Si 0.4 falla, se decide el formato de salida
antes de seguir. Si 0.5 da un peso por frame muy por encima de ~15 KB, se
recalibra el presupuesto antes de renderizar 80 frames.

## Fase 1 — Greybox y rig

Archivo: `blender/altar.py`. Escena construida por código, con constantes
agrupadas arriba (dimensiones de la nave, altura del altar, posición de las
hornacinas, largo del recorrido).

| # | Tarea | Verificación |
|---|---|---|
| 1.1 | Nave, altar y tres hornacinas en gris plano | `get_objects_summary` muestra la jerarquía esperada |
| 1.2 | Proxies de las reliquias: vinilo, micro, cadena, placa M⚡T, veladoras como cilindros | Cinco proxies nombrados, ubicados |
| 1.3 | Curva del recorrido + cámara con `Follow Path` + empty `Track To` | La cámara recorre la nave sin atravesar geometría |
| 1.4 | Empty de foco y DOF activo | Cambiar el empty cambia el plano enfocado |
| 1.5 | Keyframes de las 5 estaciones sobre los tres canales | Frames de estación fijos y documentados en el script |
| 1.6 | Render de 5 stills a 480px, uno por estación | Se generan y se pueden ver |

**Puerta 1:** revisión de los cinco encuadres. Aquí se decide todo; es la fase
más barata de tirar. Cambios de encuadre se aplican y se re-renderizan los
stills hasta aprobar.

## Fase 2 — Look

Sobre el greybox aprobado, sin tocar el rig.

| # | Tarea | Verificación |
|---|---|---|
| 2.1 | Los cinco materiales, con los valores de color derivados de los tokens de `DESIGN.md` | Oro, neón y piedra leídos contra la paleta |
| 2.2 | Iluminación: velas emisivas + key dorada suave | Ningún punto quemado; los negros siguen negros |
| 2.3 | Volumen de niebla en la nave | Los haces de luz se leen sin ahogar la escena |
| 2.4 | Glare en el compositor para el neón | El rojo brilla sin halo sucio |
| 2.5 | Geometría final de las reliquias, sustituyendo proxies | Silueta reconocible en el encuadre de su estación |
| 2.6 | Cinco stills finales a resolución completa | Se generan en ambos aspect ratios |

**Puerta 2:** aprobación del look, en móvil y escritorio.

## Fase 3 — Render y assets

| # | Tarea | Verificación |
|---|---|---|
| 3.1 | `blender/render.py`: 4 tramos × 20 frames, motion blur, ambos sensores | 160 PNG (80 por aspect ratio) |
| 3.2 | Loops idle: 5 estaciones × ~2.5 s, cámara quieta, ambos sensores | 10 clips |
| 3.3 | `scripts/build-scene.sh`: PNG → AVIF, clips → WebM, `xfade` para cerrar los loops | Salida en `public/scene/{mobile,desktop}/` |
| 3.4 | Generar `src/data/scene.json` desde el script | Valida contra el contrato de abajo |
| 3.5 | `scripts/check-budget.sh` | Falla por encima de 3 MB en `public/scene/mobile/` |

**Puerta 3:** peso dentro de presupuesto y los cinco loops se ven cíclicos.

### Contrato de `scene.json`

```json
{
  "stations": [
    { "id": "nave", "frame": 0, "loop": "loop-0.webm", "loopSeconds": 2.5 }
  ],
  "legs": [
    { "from": "nave", "to": "sonido", "frames": 20, "pattern": "leg-0/%03d.avif" }
  ],
  "sets": { "mobile": { "w": 900, "h": 1600 }, "desktop": { "w": 1600, "h": 900 } }
}
```

La capa web no conoce la escena salvo por este archivo. Cambiar el número de
frames no toca TypeScript.

## Fase 4 — Capa web

| # | Tarea | Verificación |
|---|---|---|
| 4.1 | `src/components/AltarScene.astro`: canvas fijo, `<img>` frame 0, `<video>` por estación | La página pinta el frame 0 sin JS |
| 4.2 | `src/lib/scrollScene.ts`: `scrollY` → frame, `decode()` antes de dibujar | Scrub fluido, sin parpadeo |
| 4.3 | Precarga del tramo siguiente | El segundo tramo no tartamudea la primera vez |
| 4.4 | Detección de scroll detenido (~150 ms) + crossfade al loop | La escena respira al pararse |
| 4.5 | Elección de set por `matchMedia` | Móvil no descarga el set de escritorio |
| 4.6 | Reposicionar el contenido de `index.astro` sobre las estaciones | Nada de contenido añadido ni perdido |

**Puerta 4:** se ve y se siente como el storyboard, en móvil y escritorio.

## Fase 5 — Cierre

| # | Tarea | Verificación |
|---|---|---|
| 5.1 | `prefers-reduced-motion`: frames fijos con fade | Check 3 del spec |
| 5.2 | Scrim por estación + recálculo de contraste | Check 5; actualizar la tabla de `DESIGN.md` |
| 5.3 | Fallback con `/scene/*` bloqueado | Check 4 |
| 5.4 | Teclado y touch a 320/768/1280/1920 | Check 6 |
| 5.5 | Lighthouse móvil | Check 2 |
| 5.6 | Actualizar `DESIGN.md`: sección de escena, motion, IA | El documento y el código no se contradicen |

**Puerta 5:** los siete checks del spec pasan.

## Orden de commits sugerido

Un commit por puerta cerrada, no por archivo tocado:

1. `chore(3d): verify blender toolchain and paths` (fase 0)
2. `feat(3d): greybox altar scene and camera rig` (fase 1)
3. `feat(3d): materials, lighting and fog` (fase 2)
4. `feat(3d): render pipeline and scene assets` (fase 3)
5. `feat(web): scroll-driven scene layer` (fase 4)
6. `fix(a11y): scrims, reduced motion and fallbacks` (fase 5)

## Qué NO se hace en este plan

- Tocar `main`. Todo vive en `dev` hasta que la fase 5 cierre.
- Añadir dependencias npm. La capa web es canvas y video nativos.
- Versionar el `.blend` ni los PNG intermedios: van a `.gitignore`. Sí se
  versionan los scripts y los assets finales de `public/scene/`.

## Resultado de la fase 0 — 2026-09-16

Ejecutada. Puerta 0 cerrada con dos correcciones al plan.

| # | Resultado |
|---|---|
| 0.1 | **Blender 5.2.2.** El identifier del engine es `BLENDER_EEVEE`, que en 5.x ya es el motor reescrito (el antiguo "Next"). No existe `BLENDER_EEVEE_NEXT`. Cycles no aparece en la enum de engines en esta instalación — irrelevante para el plan, pero descarta un cambio de opinión hacia Cycles sin habilitarlo antes |
| 0.2 | **RTX 4070 Ti** visible, con CUDA y OPTIX. `compute_device_type` está en `NONE`, que solo afecta a Cycles; EEVEE usa la GPU igualmente |
| 0.3 | **Rutas resueltas.** Blender (win32) escribe en `E:\Cursor Projects\MTO\tmp\` y WSL lo lee en `/mnt/e/…`. Sin capa de traducción |
| 0.4 | **`avifenc` no está instalado**, pero `ffmpeg 6.1.1` trae `libaom-av1`, `libsvtav1`, `av1_nvenc`, `libvpx-vp9` y `libwebp`. Se codifica AVIF con `ffmpeg -c:v libaom-av1 -still-picture 1`, verificado sobre un PNG real. No se añade dependencia |
| 0.5 | **No concluyente, se difiere.** El still de prueba (cubo dorado sobre casi-negro) pesó ~1 KB en AVIF: es un piso, no una medida. El peso real depende de la niebla y las velas, que aún no existen. La calibración del presupuesto se mueve a la **puerta 2**, cuando haya un still final: se convierte, se pesa, y se fija el CRF y el número de frames por tramo con ese dato |

Consecuencias para las fases siguientes:

- Fase 2 gana una tarea: **2.7 — calibrar CRF y frames por tramo** contra un
  still final convertido a AVIF, y confirmar el presupuesto antes de renderizar
  los 160 frames de la fase 3.
- Fase 2 debe activar explícitamente `use_raytracing` y
  `use_volumetric_shadows` en EEVEE: vienen apagados por defecto y son lo que
  da reflejo creíble al oro y haces a la niebla.
- `.gitignore` ya excluye `tmp/`, `blender/*.blend` y `blender/render-out/`.

## Resultado de la fase 1 — 2026-09-16

Puerta 1 cerrada: los cinco encuadres aprobados. Tres decisiones que modifican
el diseño original.

**Seis canales por estación, no tres.** `Follow Path` resultó ser aditivo sobre
la posición del objeto, no sustitutivo, así que la cámara puede elevarse por
encima del riel. A los tres canales del spec (recorrido, encuadre, enfoque) se
suman distancia focal, altura de cámara y apertura. La grúa de la retirada y el
picado de la estación del sonido salen de ahí, y ninguno estaba previsto.

**Los offsets se miden, no se estiman.** Se barre la curva en 41 muestras, se
registra la posición real de cámara en cada una y se elige la más cercana al
punto de observación deseado. Los valores en `ESTACIONES` vienen de esa medición
y hay que rehacerla si `RECORRIDO` cambia.

**El recorrido no es monotónico.** Entrada larga hasta el altar, tres estaciones
que trabajan cerca con lente y foco en vez de desplazamiento, y una retirada de
casi ocho metros. A 65-70 mm, 80 cm de dolly es un movimiento amplio.

**Estación del sonido: cenital.** Los vinilos van acostados sobre la mesa del
altar, vistos en picado a 70 mm desde 1.95 m sobre el riel. Es la única toma que
no está a la altura de los ojos, y esa variedad es justamente lo que aporta.

### Decisiones para la fase 2

- **Props (tarea 2.5):** ceniceros, cigarros consumiéndose, botella, cera
  escurrida, billetes. Regla: todo prop debe caer dentro del encuadre de alguna
  estación; fuera de cuadro es tiempo de render tirado. Los cigarros pagan doble
  porque el humo anima los loops.
- **Motor (tarea 2.7, antes 2.6):** se comparan EEVEE y Cycles sobre el mismo
  still, **después** de tener oro, velas y niebla — compararlos sobre gris plano
  no informa nada. Cycles no está habilitado como engine en esta instalación y
  hay que activar el add-on. Si gana, se usa OptiX para denoise.
- **DLSS queda descartado y conviene dejarlo escrito:** es escalado en tiempo
  real para videojuegos, no un pase de realismo aplicable a un render offline.
  El realismo aquí sale de Cycles, de imperfecciones en los materiales (polvo,
  huellas, cera, rugosidad variable) y de grano y aberración en el compositor.

### Qué se anima, confirmado

- **Tramos:** solo la cámara, con motion blur horneado. Los elementos vivos que
  avanzan cuadro a cuadro se limitan a los de movimiento ambiguo — llama y polvo
  — porque el scroll inverso los reproduce al revés y ahí no se nota.
- **Loops de estación:** llama respirando y temblando sobre el oro, humo de
  cigarro subiendo, polvo cruzando el haz, parpadeo irregular del neón, reflejo
  del oro desplazándose. El humo va solo aquí: es direccional y hacia atrás se
  vería mal.
