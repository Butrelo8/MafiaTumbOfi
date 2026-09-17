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
| 4.7 | Capa de primer plano por encima del texto en las estaciones, oculta durante el scrub | Una columna pasa frente al título; el texto sigue legible debajo |

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

## Resultado parcial de la fase 2 — 2026-09-17

Materiales, luz y atmósfera en pie; **puerta 2 aún abierta**.

**Cycles gana el duelo y pasa a ser el motor.** Mismo still, mismos materiales:
en EEVEE los marcos dorados y el micro cromado se ven negros; en Cycles el oro
recibe la luz de las velas y el cromo refleja la llama y el neón. Coste medido:
1.2–1.5 s/frame a 640×360 con 128 muestras y OptiX, frente a 0.2–0.4 s de EEVEE.
Proyectado a 1600×900 son unos 5 s/frame, así que los 320 frames de los dos
juegos caben en menos de una hora. EEVEE queda para vista previa.

**Corrección a la fase 0.** Allí quedó escrito que Cycles no aparecía entre los
motores; era un artefacto del método. El enum de `RenderSettings.bl_rna` no
lista los motores registrados por add-on. Cycles estaba disponible todo el
tiempo y se selecciona asignando `render.engine = "CYCLES"` directamente.

**Los tokens de DESIGN.md no son albedos.** Son colores de pantalla, ya
iluminados. Usados como color base dejaron la escena en negro absoluto. La
piedra tiene ahora albedos propios de render; el oro y el rojo siguen saliendo
de los tokens, convertidos de OKLCH a sRGB lineal dentro del script.

**Niebla a 0.012, no 0.05.** Cycles resuelve dispersión múltiple y con la
densidad que en EEVEE apenas se notaba, lava la escena entera y mata los negros.

**Compositor fuera.** En Blender 5 el árbol vive en un node group cuya entrada
no recibe la imagen del render: incluso un grupo en passthrough devuelve negro.
El glow del neón se hará en post con ffmpeg en la fase 3, lo que además permite
ajustarlo sin re-renderizar.

**Lección de método.** Medir la luminancia con `image.pixels` dentro de Blender
dio el mismo resultado en todas las pruebas y apuntó al problema equivocado. La
medición fiable fue externa, con ffmpeg, más comparar los md5 de los renders:
ahí se vio que cinco pruebas distintas eran byte-idénticas y que el estado de
escena se arrastraba entre ellas. `build()` no resetea los ajustes de escena;
cualquier prueba A/B tiene que limpiarlos explícitamente.

### Pendiente para cerrar la puerta 2

- Props: ceniceros, cigarros, botella, cera escurrida, billetes (tarea 2.5).
- Vinilos con etiqueta y brillo: hoy son discos negros planos.
- Hornacinas como huecos reales con boolean, no marcos salientes.
- Imperfecciones: polvo, huellas en el oro, rugosidad variable.
- Stills finales en los dos aspect ratios (tarea 2.6) y calibración de CRF y
  frames por tramo contra un AVIF real (tarea 2.7, heredada de la fase 0).

### Cierre de la fase 2 — 2026-09-17

Props ampliados a petición: bancas a ambos lados de la nave y candelabros de pie
(dan escala a los planos generales), sombrero y requinto recostado (identidad de
la banda), rosario, vaso y cerillos para los planos cercanos, además del
cenicero con cigarros encendidos, la botella, los billetes y la cera de la
primera tanda. La escena pasa de 80 a 148 objetos y el render sigue en 9,5 s
para las cinco estaciones a 800×450.

**Capa de primer plano con alfa**, decidida al revisar el workflow de
blender-skills. De ese workflow no aplica ni ProRes 4444 (códec de edición que
ningún navegador reproduce; nuestro máster son PNG de 16 bits) ni el fondo
transparente como salida principal (nuestra escena es un interior completo, no
un producto recortado) ni la salida a `~/Desktop`. Sí aplica el alfa para una
capa que va **delante** del texto, y 24 fps para los loops de estación; los
tramos no tienen fps porque su velocidad la pone el scroll.

### Ronda de dirección de arte externa — 2026-09-17

Se consultó a Gemini con las hojas de contactos. Dos rondas; lo aceptado ya está
modelado. Queda constancia de qué se descartó y por qué, para no reabrirlo.

**Aceptado e implementado.** Caja/estuche de micrófono con marcador grueso en la
estación de contratación (convierte "aquí hay un micrófono" en "aquí se firma");
polaroids entre los discos, **con las fotos reales de `public/band/`** en vez de
siluetas inventadas; exvotos de latón en la repisa de los nichos; tapete bajo
los vinilos; frasco tallado; piedra con relieve procedural; confeti y colillas
en el piso; billetes desordenados y oscurecidos; tololoche apoyado en columna;
gorra colgada de un nicho; lentes, púas, anillos de plata y botella de cerámica;
guirnalda de focos al fondo; y ruido en el halo del neón.

**El mejor consejo de las dos rondas: contraluz frío.** Dos áreas laterales en
azul frío a baja potencia. Sin ellas, el vinilo, el micro y el tololoche son
siluetas negras sobre fondo negro. Es luz de cámara, no color de marca: define
bordes sin teñir la escena ni contradecir `DESIGN.md`.

**Descartado.** Placas numeradas en las bancas: a 28 mm y diez metros no se leen,
son polígonos invisibles. Vidrio roto en el suelo: se pisa con el confeti y las
colillas sin añadir nada. Pluma de tintero: pertenece a otra película, la
sustituye el marcador.

**Advertencia sobre la segunda ronda.** Gemini afirmó haber analizado los videos
de la banda y describió detalles concretos (gorra de parches del cantante, una
marca de tequila mencionada en una canción, vapes en el set). No hay forma de
confirmar que los viera, y en la primera ronda ya criticó objetos que no
aparecían en las imágenes enviadas —dijo que el requinto estaba en la toma
cenital cuando no sale ahí—, señal de que describía una imagen propia. Las ideas
se adoptaron porque funcionan como dirección de arte, **no** como identidad
documentada de la banda. Antes de darlas por buenas, que alguien que conozca su
material las verifique.
