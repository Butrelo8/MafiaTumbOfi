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
| `escritorio/nave.mp4`, `vertical/nave.mp4` | `entrega/*/nave.mp4` | AV1 y HEVC (paso 4) |
| `escritorio/ida-{av1,hevc,h264}.mp4`, `vertical/ida-*` | `entrega/*/ida-*` | G7 |
| `escritorio/vuelta-av1.mp4` | `entrega/escritorio/` | HEVC y H.264 (paso 4). Sin ellas, Safari sin AV1 cruza por negro |
| `vertical/vuelta-{av1,h264}.mp4` | `entrega/vertical/` | HEVC (paso 4) |
| `escritorio/sacristia.mp4`, `vertical/sacristia.mp4` | `entrega/*/sacristia.mp4` (loops de 10 s; la vertical es un recorte del escritorio) | AV1 y HEVC (paso 4) |
| `{escritorio,vertical}/{vestidor,cripta,atrio}{,-hevc,-av1}.mp4` | `entrega/` (07, E5 y E6 con look) | Renders finales del 07 |
| `escritorio/musica-{ida,vuelta}-{av1,hevc,h264}.mp4` (sacristía ↔ camarín) | `entrega/escritorio/` (Flow job4, provisional) | E6 final. Vuelta no exacta: salto 0.68 al seguir en el cuadro 20 |
| `escritorio/contratacion-{ida,vuelta}-{av1,hevc,h264}.mp4` (cripta ↔ atrio) | `entrega/escritorio/` (Flow job3, provisional) | E6 final. Vuelta no exacta: salto 0.80 |

Las idas, las vueltas y la nave deben copiarse juntas desde `entrega/`: el primer cuadro de cada ida es el de la nave
de su misma generación (MAD 8.1 escritorio / 5.2 vertical); con la nave de otra generación el corte salta (MAD ~20).

Cambiar un render es reemplazar el archivo con el mismo nombre. Un códec nuevo de un archivo que ya existe se añade
a la lista de su `transicion(...)` o de su `loop(...)` (en un loop el H.264 no lleva sufijo: `vestidor.mp4`).

`grupo-{ida,vuelta}-*` (camarín ↔ cripta, Flow job2) no se copia: el último cuadro de la ida no cae en ningún cuadro
del loop de la cripta (mejor media 3.12, en el f144; contra 0.75 de la vuelta nave/sacristía, medido sobre los
maestros ffv1) y la vuelta termina en otro camarín (27). Ese cambio cruza por negro hasta el E6 final.

## Decisiones tomadas aquí

- Formato por `(min-aspect-ratio: 1/1)`, como el hero. Si la pantalla cambia de proporción (girar el teléfono,
  cambiar la ventana), el juego de videos cambia en el acto, o al terminar el viaje en curso, y se precarga el nuevo.
- Fundido a negro: 0.3 s de bajada + 0.3 s de subida (los 0.6 s del 05).
- Precarga (2026-10-14): lo inmediato del 05 y, detrás, sólo los dos viajes siguientes en el sentido de la marcha;
  se rellena al llegar a cada espacio. Bajar el sitio entero pasaba de los 3 MB a 390 (3.21 MB con los loops del 07).
- Hero ↔ nave, grupo ↔ contratación, toda la vertical a partir de la sacristía y los saltos de más de una sección
  cruzan por negro; en escritorio nave ↔ sacristía ↔ grupo y contratación ↔ cierre reproducen ida o vuelta. El gesto durante un viaje se ignora; un `#ancla` pedido a medio viaje se cumple al llegar.
- Música en E con discos y videos (01/24 con el feed de YouTube de hoy), como resolvió el 03.
- Sin JS no se monta nada: la página se lee de corrido.
