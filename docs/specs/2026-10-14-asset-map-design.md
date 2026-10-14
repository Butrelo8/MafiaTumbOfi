# Mapa de assets visuales: diseño (2026-10-14)

Semilla: `~/projects/mothership/docs/queue/2026-10-14-mto-asset-map.md` (usuario, 10:01).

## Para qué

Un redo (mejores stills → placas → loops → transiciones → máscaras/pegados) es una cadena. Hoy cada eslabón vive en
`tmp/` (ignorado por git) y en la memoria de los handoffs; un puntero viejo (atrio v3 en vez de v5) casi manda una
transición a la placa equivocada. El mapa es el registro **rastreado** de lo que vive en `tmp/` y de qué sale de qué.
Con él, "qué se vuelve viejo si cambio X" es un comando.

## Formato: TSV (decisión)

La semilla deja elegir `map.yaml` o `.tsv`. **TSV**: el script de obsolescencia queda en `awk` sin dependencias
(no hay `yq`, y el python del sistema no trae yaml), se edita con `column -t -s$'\t'`, y los diffs son por fila.
Costo: sin saltos de línea ni tabuladores dentro de una celda; el texto largo va en `evidence` como ruta.

Archivo: `docs/assets/map.tsv`, UTF-8, primera línea = cabecera, líneas que empiezan con `#` se ignoran.

| # | columna | regla |
|---|---|---|
| 1 | `id` | único, `[a-z0-9][a-z0-9._-]*`. Una fila por asset **vigente**. Una versión vieja sólo tiene fila si otra fila aún la cita, con id sufijado (`loop-atrio-esc-v4`) |
| 2 | `kind` | `plate` `loop` `transition` `still` `mask` `paste` `entrega` |
| 3 | `chapter` | texto libre corto: `nave`, `sacristia`, `camarin`, `cripta`, `atrio`, `hero`… |
| 4 | `path` | ruta relativa a la raíz del repo **principal** (`tmp/07/...` vive en el checkout `MTO/`, no en un worktree). Glob permitido para familias (`entrega/escritorio/grupo-ida-*.mp4`). `-` si no existe archivo |
| 5 | `version` | `v5`, `s5`, `g6`… o `unconfirmed` |
| 6 | `built_from` | `;`-separado, cada token `id@version` (o `id`). Sólo ids que existen como fila. Vacío (`-`) = fuente original |
| 7 | `recipe` | `nombre@versión` (nombres de visual-lab: `transition-fasth3@1`, `mask-sam3-seeded@1`); método conocido pero sin versionar = `nombre@unversioned` (consultable); método desconocido = `unversioned` a secas (no consultable) |
| 8 | `settings` | modelo, semilla, resolución, cuadros, interpolador. Texto corto; `unconfirmed` si no consta |
| 9 | `status` | `approved YYYY-MM-DD` · `candidate` · `superseded` |
| 10 | `evidence` | ruta al veredicto/ticket/informe que prueba el status. `-` sólo si `candidate` |
| 11 | `confirmed` | `yes` · `unconfirmed`. Eje aparte de `status`: una fila puede estar aprobada y con receta sin confirmar. Se pone `unconfirmed` si **cualquier** campo de la fila es adivinado o falta; la causa va en `settings`/`evidence` |

Nada se adivina: lo que no consta se escribe `unconfirmed`.

## Interfaz: `scripts/assets-stale.sh <id|recipe@version>`

- Argumento = `recipe` de alguna fila → esas filas **y** sus descendientes. Argumento = `id` → sólo descendientes
  (el input cambió; él mismo no se lista). Si coincide con ambos, gana el id.
- Descendiente = fila cuyo `built_from` contiene el id (la versión del token se ignora: "cambió el input" vale para
  cualquier versión que citen). Cierre transitivo, BFS con conjunto de visitados (los ciclos no cuelgan).
- Salida: una línea por fila, `id<TAB>status<TAB>path`, en orden BFS. No filtra `superseded`: la columna deja saltarlas
  (`# ponytail:` en el script).
- Variable `MAPA` cambia el archivo (tests); por defecto `docs/assets/map.tsv` junto al script.

Errores explícitos (stderr + código):

| caso | código |
|---|---|
| sin argumento | 2 |
| mapa inexistente o ilegible | 1 |
| el argumento no coincide con ningún id ni recipe | 1 |
| fila con número de columnas ≠ 11, id duplicado, enum inválido, `built_from` a id inexistente | 1 (el script valida al leer; no hay modo `--check` aparte) |
| argumento con `unversioned` como recipe | no es consultable (no sabe qué versión cambió): 1 |

## Pruebas (`bun test`, `scripts/assets-stale.test.ts`)

Costura única: la CLI. Un fixture de 6 filas (placa → loop → transición → entrega, una `superseded`, dos filas que
comparten receta) y los casos: id, recipe, descendencia transitiva, id sin descendientes (salida vacía, código 0),
desconocido, sin argumento, ciclo, columnas mal, id duplicado, enum malo, `built_from` colgante. Más una prueba de
integridad sobre `docs/assets/map.tsv` real (misma validación, exit 0).

## Fuera de alcance

Generar el mapa automáticamente, hashes de archivos, y `tmp/` mismo (no se mueve nada). El mapa no sustituye a
`entrega/MANIFEST.tsv` (sha256 de lo servido): `evidence` lo cita.
