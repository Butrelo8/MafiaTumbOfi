#!/usr/bin/env bash
# Qué se vuelve viejo si cambia un input o una receta: filas del mapa (docs/assets/map.tsv) río abajo, transitivo.
#
#   assets-stale.sh <id>             descendientes de <id> (él no)
#   assets-stale.sh <receta@versión> las filas con esa receta y sus descendientes
#
# Salida: `id<TAB>status<TAB>path`, orden BFS. Códigos: 0 ok (puede ir vacío), 1 mapa/argumento inválido, 2 sin argumento.
# Formato y reglas: docs/specs/2026-10-14-asset-map-design.md. MAPA=<archivo> cambia el mapa (pruebas).
# ponytail: no filtra `superseded`; la columna status deja saltarlas con grep/awk.
set -euo pipefail
arg=${1:-}
[ -n "$arg" ] || { echo "uso: assets-stale.sh <id|receta@versión>" >&2; exit 2; }
mapa=${MAPA:-$(dirname "$0")/../docs/assets/map.tsv}
[ -r "$mapa" ] || { echo "mapa ilegible o inexistente: $mapa" >&2; exit 1; }
[ "$arg" != unversioned ] || { echo "'unversioned' no se puede consultar: no dice qué versión cambió" >&2; exit 1; }

awk -F'\t' -v arg="$arg" -v mapa="$mapa" '
function fail(msg) { printf "%s:%d: %s\n", mapa, NR, msg > "/dev/stderr"; bad = 1; exit 1 }
FNR == 1 { next }                      # cabecera
/^#/ || /^[ ]*$/ { next }
{
  if (NF != 11) fail("se esperaban 11 columnas, hay " NF)
  for (i = 1; i <= 11; i++) if ($i == "") fail("columna " i " vacía")
  id = $1
  if (id !~ /^[a-z0-9][a-z0-9._-]*$/) fail("id inválido: " id)
  if (id in row) fail("id duplicado: " id)
  if ($2 !~ /^(plate|loop|transition|still|mask|paste|entrega)$/) fail("kind inválido: " $2)
  if ($7 != "unversioned" && $7 !~ /^[a-z0-9][a-z0-9-]*@[A-Za-z0-9._-]+$/) fail("recipe inválida (nombre@versión o unversioned): " $7)
  if ($9 !~ /^(approved [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]|candidate|superseded)$/) fail("status inválido: " $9)
  if ($11 != "yes" && $11 != "unconfirmed") fail("confirmed inválido: " $11)
  row[id] = $9 "\t" $4
  order[++n] = id; recipe[id] = $7; from[id] = $6
}
END {
  if (bad) exit 1
  for (k = 1; k <= n; k++) {           # grafo: padre -> hijos; cada token id@versión se reduce a id
    id = order[k]
    if (from[id] == "-") continue
    m = split(from[id], tok, ";")
    for (j = 1; j <= m; j++) {
      p = tok[j]; sub(/@.*/, "", p)
      if (!(p in row)) { printf "%s: built_from colgante en %s: %s\n", mapa, id, p > "/dev/stderr"; exit 1 }
      kids[p] = kids[p] " " id
    }
  }
  qn = 0
  if (arg in row) { vis[arg] = 1; seed = kids[arg] }
  else {
    seed = ""
    for (k = 1; k <= n; k++) if (recipe[order[k]] == arg) seed = seed " " order[k]
    if (seed == "") { print "sin coincidencia en " mapa ": " arg > "/dev/stderr"; exit 1 }
  }
  m = split(seed, s, " ")
  for (j = 1; j <= m; j++) if (!(s[j] in vis)) { vis[s[j]] = 1; q[++qn] = s[j] }
  for (h = 1; h <= qn; h++) {
    id = q[h]; print id "\t" row[id]
    m = split(kids[id], s, " ")
    for (j = 1; j <= m; j++) if (!(s[j] in vis)) { vis[s[j]] = 1; q[++qn] = s[j] }
  }
}' "$mapa"
