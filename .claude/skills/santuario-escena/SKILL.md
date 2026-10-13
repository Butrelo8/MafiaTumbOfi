---
name: santuario-escena
description: Procedimiento de la escena 3D de MTO (santuario y maquetas de transición en Blender) — cargar altar.py/transicion.py, guardar poses antes de reconstruir, medir con blender/medir.py, puerta y tanda de render, loops con loop-vivo.sh. Úsala antes de tocar blender/ o tmp/ de la escena, cuando el usuario diga "ya moví cosas", "guarda posiciones", "renderiza", "mide si se ve", o un handoff diga cargar la skill de escena. No es la skill `blender` (Mixamo → baile).
---

# Escena del santuario (MTO)

Antes de tocar `blender/`: `docs/blender-notas.md` (decisiones y quirks de MTO) y
`/home/black/projects/visual-lab/blender/blender-notas.md` (trampas de Blender 5).

## 0. Entorno

`scripts/preflight.sh`: puerto del MCP de Blender (9877; el 9876 es de Resolve), ComfyUI y
`uv run --with numpy,pillow`. Nunca las tools `*_for_cli` del MCP de Blender: cuelgan 120 s.
Sin UI: `/mnt/e/Blender/blender.exe -b --python "$(wslpath -w script.py)"`.

## 1. Las dos escenas

| Escena | Qué es | Levantar (MCP, `execute_blender_code`) |
|---|---|---|
| `blender/altar.py` + `look.py` | El santuario del scroll (frames de la web) | `r = {}; exec(open(r"E:\Cursor Projects\MTO\blender\render.py").read(), r); r["construir"]()` |
| `blender/transicion.py` | Maquetas grises + profundidad para H3/Klein | `ns = {}; exec(open(r"E:\Cursor Projects\MTO\blender\transicion.py").read(), ns); ns["build"](movil=False)` |

`render.py` `construir()` hace `build()` + `use_nodes = False` + `look.aplicar()`, como piden las notas.

## 2. Antes de reconstruir: poses

`build()` borra lo que el usuario movió a mano. Siempre, antes de cualquier `build()`:

```python
p = {}; exec(open(r"E:\Cursor Projects\MTO\blender\poses.py").read(), p)
p["volcar"](r"E:\Cursor Projects\MTO\tmp\poses-visor-<fecha>.json")
```

Luego pasar los deltas de `p["comparar"](…)` a constantes del script, reconstruir y comparar hasta que
no quede nada; volver a volcar `tmp/poses-referencia.json`.

## 3. Medir, no mirar

```python
m = {}; exec(open(r"E:\Cursor Projects\MTO\blender\medir.py").read(), m)
m["en_cuadro"]("CANDELABRO_1", frame=1)   # caja en px, fracción dentro del cuadro
m["visible"]("CANDELABRO_1", frame=1)     # rayos desde la cámara: llegan / al aire / quién tapa
m["solapan"]("BANCA_der_0", "BANCA_izq_0") # cajas y caras cruzadas (BVH)
```

`en_cuadro` usa la resolución de la escena: fija el formato antes (`r["_escena"]("movil")`).
Mide antes de afirmar algo de un render ("s44 se había corrido" resultó falso).

## 4. Fijar → puerta → tanda

Flujo completo en la cabecera de `scripts/puerta-tanda.sh`:
1. Poses fijadas (paso 2).
2. Hoja de Cycles por estación a pocas muestras (no Eevee) + `scripts/comparar.sh hoja`; la aprueba el usuario.
3. `scripts/puerta-tanda.sh blender <formato> [volcado]`. En la escena viva, antes de renderizar desde ahí:
   `pt = {}; exec(open(r"E:\Cursor Projects\MTO\blender\puerta.py").read(), pt); pt["revisar"](volcado)`.
4. Tanda en segundo plano (la orden la imprime la puerta) y `scripts/esperar.sh log …` desde Monitor.
   Cambio tardío: `render.py -- tramos <formato> <desde> <hasta>`, sólo los tramos afectados.

## 5. Loops y revisión

- Pipeline placa → H3 → montaje → foco → halación → escalera: `scripts/loop-vivo.sh` (pasos en su cabecera);
  prompts por ticket en `prompts/<ticket>/`. `scripts/puerta-tanda.sh comfy` antes de encolar.
- Lado a lado, hojas, cuadros y costura: `scripts/comparar.sh`.
- Esperas: `scripts/esperar.sh` con `run_in_background` o Monitor, nunca `sleep` en primer plano.
