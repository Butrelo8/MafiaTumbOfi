# Handoff — tallo de espinas y rosa del micro, a medio rehacer (2026-10-13, ~05:25 CST)

Formato `matt-handoff`. Rama `dev`. Escribir en español. El detalle de G5 y G6 está en el ticket 06 (bullets G5 y G6);
aquí sólo el hilo y lo que aún no está escrito en otra parte.

## Hecho y aprobado (commits)

- **G5** `c56dbb9`: micro sobre las placas G4. La máscara cortaba la cúpula de la cabeza (los "trozos que faltan");
  oro al nivel aprobado (escritorio `TOPE=1.63`, vertical `GANA_ORO=1.7`); micro vertical +20 px; maqueta
  `MOVIL["micro"]` z 1.669.
- **G6** `1f7f602`: loops de la nave de 10 s, los dos formatos, aprobados y congelados en `entrega/`
  (`escritorio/nave.mp4` = `tmp/g6/esc/nave_g6_esc_c.mp4`, con **copal real**; `vertical/nave.mp4` =
  `tmp/g6/vert/nave_g6_vert.mp4`). Cadena: `tmp/g6/tanda.sh` (cabecera; `V=`, `SEMILLA=`, `SOLO_H3=1`, `REAL_ESC=`).
- Sin commitear y fuera de mi tarea: `blender/espacios07.py` es de la sesión del ticket 07 (youdrone); no tocar.

## A medio hacer: tallo y rosa del micro (lo pidió el usuario después de aprobar G6)

El usuario: el tallo de espinas tiene que estar **enrollado de verdad en el cable** y verse real. Todo en
`tmp/micro/tallo/` (ignorado por git). Estado:

1. **Geometría: resuelta y aceptada** ("ahora sí abraza el cable"). `tallo2.py <vueltas>`: hélice en contacto con el
   cable (radio = cable 3 px / conector 5.5 px + tallo 4.5 px), media vuelta de atrás en sombra y tapada por el cable,
   sombra de contacto, espinas triangulares, entra a los sépalos (borra el cilindro verde). Elegida **2.5 vueltas**
   (`placa_tallo_v2.5.png`, `mascara_tallo_v2.5.png`; la máscara ya trae la de G5 fuera de la zona del tallo).
2. **Pasada fotográfica de Klein** sobre tallo + rosa (recorte 240×380 en 870,0 → 720×1140, `prompt_foto.txt`,
   3 semillas, elegida **s2**): `pegar_foto.py` la pega sólo dentro de cable + tallo + rosa y mide que el tallo no se
   movió (desvío mediano ~1 px). Salida `placa_foto_s2.png`. Rosa carmesí.
3. **`micro_viva_v.py` nuevo `ROSA_GAN`** (`tmp/micro/movil/`): la ganancia del anillo es por canal (B 1.46, G 1.40,
   R 1.26 en la placa G4) y volvía **magenta** la rosa; `ROSA_GAN=lum` le da sólo la media (tono 22° contra 9° del
   aprobado). Sin la variable se comporta como antes.
4. **Lo que el usuario rechazó al final** (05:20): "las luces no van, el micrófono es más oscuro y éstos se ven sólidos,
   no pegan". Medido en `tallo/esc_foto_lum.mkv`, cuadro 0, L* (0–100) y detalle (mediana |L − blur σ1.5|):

   | | p50 | p90 | p99 | detalle |
   |---|---|---|---|---|
   | tallo | 26.3 | 62.4 | 98.8 | 5.24 |
   | rosa | 3.9 | 44.7 | 63.6 | 0.96 |
   | micro (rejilla) | 10.2 | 27.1 | 39.2 | 1.83 |
   | fondo | 10.6 | 36.1 | 56.9 | 1.66 |

   El tallo está ~2.5× más claro y ~3× más nítido que el micro; la rosa tiene altas luces (p90 45) muy por encima del
   oro (p90 27). **Siguiente paso:** igualar luz y textura a la del micro, no al revés: bajar tallo y rosa al nivel del
   micro (p90 ≈ 27, p99 ≈ 40), caída direccional de la luz como la del micro (más oscuro abajo y a la derecha), un poco
   de desenfoque (σ ~0.6) y el grano de la placa, para que dejen de verse "sólidos". Hacer 2–3 variantes lado a lado
   (`scripts/comparar.sh lado`) contra el micro y preguntar con AskUserQuestion.

## Después del visto bueno del tallo y la rosa (cascada, nada es opcional)

1. Archivos nuevos con nombre propio (no pisar `placa_micro_rosa.png`: la usan `reconstruir.sh`, `trasplantar.py`,
   NOTAS): p. ej. `tmp/micro/g5/placa_micro_tallo.png` + máscara.
2. **Disparidad**: rehacer `esc_disp_g5.png` / `vert_disp_g5.png` con `tmp/micro/g5/disp_g5.py` y la máscara nueva (la
   vieja marca "cerca" la banda de la sinusoide de ±13 px: halo nítido alrededor del tallo nuevo).
3. **Vertical**: `tmp/micro/g5/mapear_v.py` con la máscara nueva; píxeles: reemplazar **toda** la zona del tallo con la
   placa de escritorio nueva escalada × ganancia (generalizar `cupula_v.py`, que tiene `../placa_micro_rosa.png`
   fijo); después correr +20 px como en G5.
4. **Maqueta**: la espiral de `micro()` en `blender/transicion.py` tiene radio 0.016 m alrededor de un cable de 0.004
   (flota igual que la vieja): radio 0.008 y 2.5 vueltas en el mismo tramo, para que G7 siga lo que se pega.
5. **Loops**: borrar `micro240.mkv` en `tmp/g6/esc` y `tmp/g6/vert` y correr
   `V=_c REAL_ESC="$PWD/copal/nave_g6_esc_real_copal.png" ./tanda.sh esc` y `./tanda.sh vert` desde `tmp/g6/`, con las
   rutas del micro nuevas en `base_esc`/`base_vert` y `ROSA_GAN=lum`; H3 se reutiliza (sólo CPU, ~25 min). Medir costura
   (`scripts/comparar.sh costura`) y mostrar; el usuario aprobó G6 con el tallo viejo, así que es una nueva aprobación.
6. `entrega/congelar.sh` (fuentes de `nave-esc-micro.png` y de las placas/máscaras/disparidades G5), commit, y luego G7.

## Gotchas de esta sesión (específicos del sitio)

- La vertical no tiene brasas en el sahumador de la bocina: H3 anima el cuenco del altar lateral derecho
  (`tmp/g6/vert/zonas.py`).
- El copal de escritorio vive en `tmp/g6/copal/` (edición local de Klein + `pegar_copal.py`, que actualiza la real y la
  de Klein con A + (R' − R)). `tmp/g6/esc/placa.png` ya es la de Klein con copal (`placa_g2.png` es la anterior).
- H3 no obedece la altura de una llama por prompt ni por semilla.
- Ningún trabajo en segundo plano corriendo al cerrar. ComfyUI arriba en `172.20.96.1:8188`.

## Skills sugeridas

- `santuario-escena` (antes de tocar `blender/transicion.py`), `comfy-local` (Klein), `frameref` si se replantea la luz
  de la rosa contra una referencia fotográfica.
