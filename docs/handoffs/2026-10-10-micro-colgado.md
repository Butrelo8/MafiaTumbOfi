# Handoff — micrófono colgado en la nave (2026-10-10, ~03:15 CST)

Rama `dev`. Escribir en español. Leer `CLAUDE.md` y `.wayfinder/santuario/MAP.md` antes. Commit sólo si el usuario lo pide.

## Dónde quedamos (exacto)

El usuario vio el último `tmp/micro/r7_micro.mp4` (loop de escritorio con el micro) y dijo **"still missing pieces"**:
a la rosa todavía le faltan trozos en el loop final. Es lo primero. No se identificó dónde; sospechoso principal:

- `tmp/micro/ajustar_mascara.py` recorta a mano `corte[320:376, :975] = 0` (retablo redibujado junto a la horquilla) y
  `corte[376:, :944] = 0`. Se calcularon con la rosa vieja (que acababa en y ≈ 320). La rosa nueva cuelga cabeza abajo
  y llega a y ≈ 335 y x ≈ 945 (a 1712×944): el recorte de la horquilla le come la parte de abajo a la izquierda. La
  envolvente convexa de la rosa se aplica **antes** de `corte` → arreglar el orden o limitar el corte a y ≥ 345.
- Cómo verlo: contorno de `mascara_micro_ajustada.png` sobre `placa_micro.png` (como `rosa_mask.jpg`) y
  `deform.jpg` (placa izquierda, loop final derecha, 2×). Pedir al usuario que marque el trozo si no aparece.
- Lo que está fuera de la máscara ajustada sale del cuadro v5 (sin micro) y además `dof.py` lo desenfoca.

## Hecho en esta sesión

- **v5 en la vertical:** `tmp/cine-look/nave_v5.mp4` (259 → 197 KB). Método y gotchas en `tmp/cine-look/NOTAS.md`
  (§ "v5 en la vertical"); ticket 14 actualizado. Commit `67e23f0`.
- **Spec aprobada** del sujeto al centro: `docs/specs/2026-10-10-micro-colgado-design.md` (revisión de Fable en
  `tmp/micro/fable/REVISION.md`). Lo que cambió después, a pedido del usuario, ya está en la spec: sin moño; tallo
  único, leñoso, color tierra, espinas finas, sin hojas, en espiral por el cable; nada debajo de la rosa.
- **Maqueta:** `micro()` en `blender/transicion.py` (Shure 55 colgado, rosa, espiral). Commit `5ff2014` (con moño);
  la espiral sin hojas está **sin commitear**.
- **Loop de escritorio con el micro:** `tmp/micro/r7_micro.mp4` (242 KB contra 287 de v5, costura 0.48), lado a lado
  `tmp/micro/sbs_v5_vs_micro.mp4`. Cadena completa y gotchas en `tmp/micro/NOTAS.md` (escrito antes de las últimas
  correcciones; ver abajo).

## Cambios tras `tmp/micro/NOTAS.md` (añadirlos ahí)

1. Brillo: el usuario pidió el micro "más brillante" dos veces → `TOPE=1.2` en `micro_viva.py` (oro L p99 42 contra
   guitarra 27; rompe a propósito la regla "nada más brillante que los instrumentos", decisión del usuario).
2. La atenuación (en `atenuar.py` y en el tope de `micro_viva.py`) sólo toca el oro: rosa y tallo por **posición**
   (y < 330), no por color (el naranja de la brasa también tiene a* alto y se escapaba).
3. `componer.py`: rellena huecos y suma la rosa por color (a* > 140): sus pétalos oscuros dejaban ver la placa vieja.
4. `sobre_rosa.py`: corte en y 232 (borde de arriba de la rosa) para que la espiral no le haga una muesca.
5. Rosa colgada cabeza abajo (el usuario: el tallo viene de arriba, la rosa crecía hacia arriba): guía 2D (rosa volteada
   + inpaint de la vieja, `placa_guia_rosa.png`) → Klein `mto_micro_rosa_s1.json` → compuesta en `placa_micro_vid.png`.
   Salió más rosada que el carmesí de la spec; el usuario no lo objetó.
6. Cable negro separado del tallo: con sólo prompt Klein los fundía; `guia_espiral.py` dibuja la espiral alrededor del
   cable real (x 988) y Klein la refina (`mto_micro_guia_s2.json`).

## Reconstruir el loop (desde `tmp/micro/`)

```
PY="uv run -q --with numpy --with opencv-python-headless python -I"; D="$PWD"
$PY atenuar.py placa_micro_vid.png mascara_micro.png placa_micro.png 52 ../placa-13/capillas/placa.png
$PY ajustar_mascara.py ../placa-13/capillas/placa.png placa_micro.png mascara_micro.png mascara_micro_ajustada.png
# mascara_humo_micro.png y foco_micro.png: humo × (1 − ajustada) y max(humo, ajustada), a 1920×1080 (ver NOTAS)
TOPE=1.2 $PY micro_viva.py placa_micro.png mascara_micro_ajustada.png ../cine-look/escritorio_real_s2b_nr.mkv escritorio_micro.mkv
HUMO="$D/mascara_humo_micro.png" IN="$D/escritorio_micro.mkv" OUT="$D/r7_micro_m.mkv" ../cine-look/montar_r7.sh
FOCO_D=0.97 FOCO_MASK=foco_micro.png $PY ../cine-look/dof.py r7_micro_m.mkv disp_micro.png r7_micro_dof.mkv 0.575 0.48 12.5
../cine-look/halacion.sh r7_micro_dof.mkv r7_micro.mp4
```
~4 min. Medir costura y luma oro/guitarra como en `NOTAS.md`.

## Pendiente

1. **Trozos que faltan en la rosa** (arriba).
2. **Vertical con el micro:** misma cadena con `MOVIL["micro"]` (foco u 0.35, v 0.24; probar ~10 px reales = argumento
   ≈ 27 en `dof.py` antes de 13). La placa vertical es `tmp/movil-06/viva/placa.png`; Klein redibuja la vertical
   (25–47 px): usar pegar y refinar + máscara, no flujo.
3. **Transiciones** vecinas de la nave con `micro()` antes de cualquier deploy (spec, "Fuera de alcance").
4. **Commits** cuando el usuario lo pida: míos sin commitear = `blender/transicion.py` (espiral sin hojas) y la spec.
   **No son de esta sesión** (los dejó la sesión de visual-lab con el OK del usuario): `CLAUDE.md`,
   `.claude/mpaf.lock.json`, `.claude/skills/kiln-prop`, `.claude/skills/rive/` (y `.mcp.json` según su aviso).
5. Visual-lab avisó: en `tmp/movil-06/web` hay crema sobre rojo a 4.0:1 (pide 4.5:1).

## Gotchas de esta sesión

- ComfyUI está en `172.20.96.1:8188`, no en 127.0.0.1. El MCP `comfy-mcp` `run_workflow` falló: usar
  `/mnt/e/ComfyUI/python_embeded/Scripts/comfy.exe run --workflow 'E:\…\x.json' --json` (no cortar su salida con `head`:
  mata el envío).
- ComfyUI se cuelga en "Model Initializing" con la 2.ª o 3.ª semilla en cola (pasó 4 veces). `POST /interrupt` no
  basta: `powershell.exe -File 'E:\ComfyUI\start-comfy.ps1'` lo reinicia (~1 min).
- Klein: LoadImage cachea por nombre (nombre nuevo por variante); dibuja el micro 1.4× más grande que el bloqueo y tan
  brillante como la cruz; con "keep everything" igual redibuja.
- Máscaras: oro delante del retablo dorado no se separa por color (GrabCut falló); la diferencia contra la placa deja
  fuera los pétalos oscuros; el flujo DIS da derivas falsas contra una silueta plana pegada.
- Blender MCP: no usar las tools `*_for_cli` (cuelgan 120 s, ver `CLAUDE.md`). El add-on escucha en 9877; si el MCP no
  conecta al inicio, el usuario lo reconecta con `/mcp`.

## Skills sugeridas

- `santuario-escena` + `docs/blender-notas.md` (maqueta y vertical); `kiln-prop` si el micro necesita silueta medida contra foto.
- `comfy-local` (lo invoca el usuario) para presets; `fable-review` si el usuario pide otra pasada de Fable.
- `matt-wayfinder` (mpaf) para cerrar el ticket del micro en `MAP.md`; `director`/`frameref` si se replantea el sujeto.
