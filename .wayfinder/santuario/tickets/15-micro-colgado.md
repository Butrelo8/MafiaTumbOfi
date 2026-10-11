# 15 — Micrófono colgado: un sujeto al centro para el bokeh
Type: prototype · Status: resolved · Blocks: 09 · Blocked by: — · Assignee: claude

## Question
El 14 (v5) dejó el foco de lente real sin protagonista: todo el bokeh es fondo. ¿Qué sujeto va al centro del cuadro
de la nave, se lee nítido al 100 % con el retablo hecho bokeh detrás, y aguanta el loop sin deformarse? Y, ya con el
sujeto, ¿cuánto dura el loop y a qué ritmo se mueve?

## Prueba (2026-10-10)
Spec aprobada: [`docs/specs/2026-10-10-micro-colgado-design.md`](../../../docs/specs/2026-10-10-micro-colgado-design.md)
(Shure 55 de oro viejo colgado de la bóveda, rosa con tallo leñoso en espiral por el cable, sin moño ni hojas). Cadena,
mediciones y gotchas en `tmp/micro/NOTAS.md`; handoff `docs/handoffs/2026-10-10-micro-colgado.md`. Método general en
visual-lab: `~/projects/visual-lab/comfyui/playbooks.md` › *Web loop on a locked-off plate*.

- **La rosa de Klein no aguantaba:** le pintaba la mitad de abajo casi negra (L 2–6 contra un fondo de L 10) y en el loop
  se leía como hueco ("still missing pieces"). No eran los recortes de la máscara; se midió.
- **Ritmo:** el loop de 5 s se veía apurado. FILM para alargarlo (×2, ×3) queda "muy lento" y "chopeado": en humo y fuego
  funde o avanza a tirones. Encadenar dos tomas de H3 junta sin salto, pero a 141 cuadros el prompt calmado apenas frena
  el humo. H3 nativo de 260 cuadros sí da el ritmo; a 20 pasos con tirones, a 40 pasos con `tmix` 1-2-1, fluido.

## Answer
Decidido por el usuario el 2026-10-10 (escritorio, nave):
- **Micro colgado al centro**, maqueta `micro()` en `blender/transicion.py`. Más brillante que la guitarra (`TOPE=1.2`):
  rompe a propósito la regla de "nada más brillante que los instrumentos"; decisión del usuario.
- **Rosa renderizada en Blender** (asset `rosa-roja.glb`, ya en créditos): roja, cerrada, cabeza abajo, pegada con el
  color de Klein y retocada por Klein dentro de su alfa, alineada por correlación de fase. Regla que sale: **lo que Klein
  o H3 deforman se hace en Blender y Klein sólo lo retoca**, siempre compuesto de vuelta con máscara. Si cambia la silueta
  de un sujeto, el mapa de profundidad de MoGe se rellena desde el fondo o el foco queda en la silueta vieja.
- **Loop de 10 s nativo:** H3 de 260 cuadros a 928×512, 40 pasos, prompt calmado (`largo/prompt_calmo.txt`), `tmix` 1-2-1,
  RTX ×2 → `tmp/micro/largo/r7_micro_10s_nativo_40p_suave.mp4` (383 KB, costura 0.40). Reconstruir con
  `tmp/micro/largo/reconstruir_10s.sh`. **Revisa el 04:** 10 s sí cabe en 12 GB a 928×512.
- **Humo en el periodo completo** del loop (`largo/montar_largo.sh`), no en un sub-loop de 60 fundido. **Revisa el 13.**
- Codificación: guardar PNG desde ComfyUI (`SaveImage`; `SaveVideo` baja a ~0.8 Mbps) y `GOP` = largo del loop.

No cierra (queda en otros tickets):
- **Vertical con el micro** → 06 (la vertical sigue en 5 s y sin micro).
- **Velas y polvo** siguen en loops de 120 (ciclan cada 5 s dentro del de 10 s); **10 s en los demás loops** → 16.
- **Transiciones** vecinas de la nave con `micro()` y con la v5: condición dura antes de cualquier deploy (spec) → 17.
