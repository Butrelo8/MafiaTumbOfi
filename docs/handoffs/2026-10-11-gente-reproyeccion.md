# Handoff — gente y ofrendas en la nave, vertical sacada de escritorio (2026-10-11)

Formato `matt-handoff`. El detalle está en los tickets; aquí sólo el hilo y lo que no está escrito en otra parte.

## Dónde retomar

**Ticket 06, último punto ("Siguiente paso")**: `.wayfinder/santuario/tickets/06-movil.md`, sección *v6*. El usuario eligió
mover al joven de gorra y la texana a donde **las dos cámaras los vean enteros**. Medido (`tmp/props-06/medir_libre.py`):
para el joven sólo quedan **bancas izquierdas** (filas 6–12, x −1.9 / −2.3), que en escritorio caen en el **hueco del
texto** del ticket 03. Primero confirmar eso con el usuario (AskUserQuestion); si acepta:

1. Sobre `tmp/props-06/s44_vacia.png` (escritorio sin gente ni texana, limpio) devolver la mujer del velo y el fiel desde
   s44 (`klein/nave13props_p4_s44_00001_.png`, siluetas en `reproyectar_capas.py`) y que Klein añada joven y texana en
   recortes centrados en el sitio medido (pegar sólo la caja: `pegar_zona.py`).
2. Mover `PROPS` en `blender/transicion.py` a esos sitios; `pases_reproy.py` (y `-- vacio`) para la profundidad.
3. Vertical = `reproyectar.py` desde la placa de escritorio nueva, base de huecos **sin gente** (`klein/s33_vacia_s7_00001_.png`
   reescalada a 704×1280), un pase de Klein y `pegar_huecos.py` sólo en los huecos.
4. Enseñar el par (SendUserFile: el usuario estuvo por ssh) y comparar sujeto por sujeto al 100 %: el usuario aprueba
   sólo si gente, ropa y props coinciden en los dos formatos.

Después de aprobar (orden en el 06): placa real v5 de las dos, el micro encima (re-pegado y re-retocado contra la placa
nueva), H3, loops de 10 s y las transiciones del 17 sobre las placas nuevas.

## Lo que quedó decidido hoy

- **Ticket 17, detalle:** base de las transiciones = H3 a 1920×1056 desde la placa v5 + detalle reproyectado de la placa;
  difusión ligera sólo al moverse; cascada AV1 / HEVC / H.264 (ida 189 KB AV1). Todo en el 17, *Detalle* y *Peso*.
- **Ticket 06:** gente = **una mujer con velo y un joven de gorra** (más el fiel junto al altar que Klein añadió y el
  usuario aceptó con s44); texana negra en el remate de una banca; nardos en las cabeceras del pasillo, filas 2–6.
  Placa de escritorio elegida: **s44**. La vertical se **saca de la de escritorio** (reproyección), no de otra tirada de Klein.

## Trampas (no están en otro lado)

- El prompt base de la nave (`placa-13/capillas/klein.sh`) termina en **"no people"**: quitarlo siempre que haya gente
  (`klein_props_v.sh` ya lo hace; `klein_props.sh` todavía no).
- Klein **inventa y reparte gente**: pide "exactly N people … the pews on the left are empty"; aun así revisa cuántas hay.
- Retoques locales de Klein: casi nunca respetan "change nothing else" (quitó la texana al quitar el rosario, cambió la
  ropa del joven); por eso siempre se pega sólo una caja o una silueta, nunca la imagen entera.
- Medir posiciones en cuadro con `world_to_camera_view` **fijando la resolución** de la cámara vertical; sin eso se
  proyecta a 16:9 y da otra u.
- Juzgar si una placa "corrió el encuadre" sólo con la maqueta al 50 % encima, nunca lado a lado con otra placa (hoy
  dije que s44 se había corrido y era falso).
- Lo que el contrabajo tapa en escritorio no existe para la vertical: Klein lo inventa mal (el joven). Por eso la gente
  va donde las dos cámaras la vean.
- `gen.sh` no copia salidas cuyo prefijo tiene subcarpeta (FileNotFoundError esperado); los scripts copian de `output/`.

## Sin commit / fuera del repo

- `tmp/` está ignorado: todos los prototipos de hoy viven en `tmp/micro/trans_esc/` (`hd_det/`, `detalle_web/`, `cod/`) y
  `tmp/props-06/`.
- visual-lab: `comfyui/comfyui-notes.md` lleva dos filas nuevas (H3 no sigue el tiempo del control; SeedVR2 en placas
  oscuras), sin commit; los métodos de hoy se le pasaron a meltingship para visual-lab.

## Skills sugeridas

- `santuario-escena` + leer `docs/blender-notas.md` antes de tocar `blender/`.
- `comfy-local` para Klein (`preset_edit`, `preset_edit_ref`).
- `director` si hay que decidir el peso visual de la gente en el encuadre (está en `.claude/skills/director` desde el
  preset `produccion-visual`).
