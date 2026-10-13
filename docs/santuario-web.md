# El santuario en la web (pasos 3, 5 y 6, 2026-10-13)

Cómo está montado el santuario en `src/` y qué falta para cambiar los provisionales por los renders.

## Piezas

- `src/data/santuario.ts`: los seis espacios en orden de gesto y su fondo por formato (escritorio 16:9, vertical
  9:16): `loop`, `quieta` (imagen), `ida` (al siguiente) y `vuelta` (desde el siguiente). Sin fondo, negro.
- `src/lib/santuario.ts` (+ test): elección de códec, plan de cada viaje (transición, fundido o corte), orden de
  precarga y eje del swipe. Sin DOM.
- `src/lib/montarSantuario.ts`: gesto, reproductor, precarga `fetch` → `blob:` y aviso de carga.
- `src/lib/montarUi.ts`: D (titular que se abre) y E (una pieza a la vez) del ticket 03.
- `src/components/Santuario.astro` + `src/styles/santuario.css`: la escena, el negro y el indicador.

## Provisionales (todo de antes de la pila, copiado de `entrega/`)

| Archivo en `public/video/` | Origen | Falta |
|---|---|---|
| `escritorio/nave.mp4`, `vertical/nave.mp4` | `entrega/*/nave.mp4` | G6; AV1 y HEVC (paso 4) |
| `escritorio/ida-{av1,hevc,h264}.mp4`, `vertical/ida-*` | `entrega/*/ida-*` | G7 |
| `escritorio/vuelta-av1.mp4` | `entrega/escritorio/` | G7; HEVC y H.264 (paso 4). Sin ellas, Safari sin AV1 cruza por negro |
| `vertical/vuelta-h264.mp4` | `entrega/vertical/` | G7; AV1 y HEVC (paso 4) |
| `vertical/sacristia.mp4` | `entrega/vertical/sacristia-5s.mp4` (5 s) | paso 2 (10 s, v5) |
| `escritorio/sacristia.webp` | último cuadro de `ida-h264` | paso 1: el loop de escritorio. Al llegar, en `santuario.ts` cambiar `quieta` por `loop: loop('escritorio', 'sacristia')` |

Cambiar un render es reemplazar el archivo con el mismo nombre. Un códec nuevo de un archivo que ya existe se añade
a la lista de su `transicion(...)`; un loop en varios códecs pide pasar `loop()` a la forma de `transicion()`.

## Decisiones tomadas aquí

- Formato por `(min-aspect-ratio: 1/1)`, como el hero. Si la pantalla cambia de proporción (girar el teléfono,
  cambiar la ventana), el juego de videos cambia en el acto, o al terminar el viaje en curso, y se precarga el nuevo.
- Fundido a negro: 0.3 s de bajada + 0.3 s de subida (los 0.6 s del 05).
- Hero ↔ nave, sacristía → grupo y los saltos de más de una sección cruzan por negro; nave ↔ sacristía reproduce
  ida o vuelta. El gesto durante un viaje se ignora; un `#ancla` pedido a medio viaje se cumple al llegar.
- Música en E con discos y videos (01/24 con el feed de YouTube de hoy), como resolvió el 03.
- Sin JS no se monta nada: la página se lee de corrido.
