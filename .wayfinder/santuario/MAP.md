# Map: Santuario en movimiento

Label: `wayfinder:map`

## Destination

Una **especificación** de la página en movimiento: los cinco espacios del santuario, sus transiciones,
el layout de la UI sobre cada escena (escritorio y móvil), la resolución, el peso y la integración web.
Lista para producir sin decisiones pendientes. Llegamos cuando no queda ningún ticket abierto.

## Notes

- Dominio: sitio de una banda de corridos tumbados de Xalapa. Vocabulario en [`CONTEXT.md`](../../CONTEXT.md).
- **Excepción a "plan, don't do"** (decidido 2026-10-04): los tickets de prototipo producen renders reales,
  porque aquí las decisiones se toman viéndolos. La producción completa va después de cerrar el mapa.
- Skills por sesión: `director` (planos, notas sobre cortes), `frameref` (look de cada espacio),
  `santuario-escena` + `docs/blender-notas.md` antes de tocar `blender/`, `matt-grilling` en los tickets de conversación.
- UI (ticket 10): `frontend-design` como única skill general de diseño; `review-animations` y `animation-vocabulary`
  (Emil Kowalski, en `.claude/skills/`) para el movimiento; auditoría anti-slop con `npx -y impeccable@4.5.2 detect --json`
  sobre cada prototipo; variantes de UI en un lienzo de Claude Design (`/design`). Avance del 2026-10-10 en el ticket 10.
- Método probado: transiciones como en el ticket 01 (maqueta gris → Klein → H3 + ControlNet de profundidad → LOOK);
  loops con cámara quieta como en `~/projects/visual-lab/comfyui/playbooks.md` › *Web loop on a locked-off plate*
  (placa fija + H3 en máscaras, sujeto difícil desde Blender, 10 s nativo, foco, codificación). Tickets 13, 14 y 15.
  Con un sujeto compuesto en una toma que se mueve (ticket 17, aprobado): el sujeto es una capa 2D seguida con la
  cámara de Blender (H3 no lo toca), foco de lente por cuadro con la profundidad de Blender, y FILM ×8 + obturador de
  180° sólo en el fondo, antes del RTX y del LOOK.
- El usuario: español, conciso, decide rápido y quiere ver renders. Rutas Windows (`E:\Cursor Projects\MTO\...`).
- Mapa de secciones: hero (video) → nave = Quiénes somos → sacristía = Música → camarín de las hornacinas =
  El grupo → cripta = Contratación → atrio = cierre.

## Decisions so far

- [01 Prueba nave → sacristía](tickets/01-prueba-nave-sacristia.md): el corte escondido tras un pilar funciona;
  MiniMax (ruta M) sobre DepthFlow (ruta D); 864×480 se queda corto de resolución.
- [02 Instrumentos como reliquias](tickets/02-instrumentos-nave.md): Klein y MiniMax los sostienen sin
  deformar; 3 semillas por cuadro (acierta 1 de 3); veladoras de ofrenda dan luz y movimiento al loop.
- [11 Navegación: un gesto, una sección](tickets/11-navegacion-por-gesto.md): la transición se reproduce
  entera (ida/vuelta), oclusor enmascarado desde Blender, loops con costura de 0.83 s (de nuevo 10 s desde el 15).
- [04 Resolución](tickets/04-resolucion.md): H3 a 1280×704 + RTX ×1.5 → 1080p; FlashVSR descartado (inventa); loops
  de 5 s, revisado en el 15 y el 16: 10 s en todo (928×512 / 512×928 nativo + RTX).
- [12 Que el tololoche se lea como contrabajo](tickets/12-contrabajo.md): asset de contrabajo, requinto en una
  bocina, sahumador como fuente del humo; las reliquias van con su silueta real y a la altura del asiento o más.
- [13 Placa fija + capas](tickets/13-placa-y-capas.md): cámara quieta en los loops; placa de Klein fija y H3 sólo en
  zonas vivas (canny solo no basta); humo por el periodo completo (desde el 15), llamas chicas en post; muros de tezontle, bancas de verdad,
  capillas y rayo de luna en la nave.
- [03 Layout de la UI sobre la escena](tickets/03-layout-ui.md): el contenido va sobre la escena, mezclado por sección: C en el hero,
  D (titular que se abre) en texto, E (una pieza a la vez, sin scroll) en Música y El grupo; hueco oscuro abajo a la izquierda.
- [05 Peso y carga](tickets/05-peso-carga.md): experiencia completa siempre; entrada ≤ 3 MB y gesto ≤ 1 MB en móvil medidos con
  `scripts/medir-peso.mjs`; AV1 → HEVC → H.264; lo inmediato y luego cascada de todo el sitio; saltos con fundido a negro.
- [14 Look de cine](tickets/14-look-de-cine.md): transiciones a 24p con obturador de 180° (FILM ×8, 20 % menos
  peso); halación + difusión fuerte sobre el LOOK 2383; loops a 24p sin obturador; grano en HTML; sin recorte.
  v5: placa real (Klein 4 MP con tono de la placa NR) + foco de lente T2.8 desde profundidad MoGe (510 → 287 KB).
- [15 Micrófono colgado](tickets/15-micro-colgado.md): Shure 55 de oro al centro de la nave, más brillante que la
  guitarra (decisión del usuario); rosa roja renderizada en Blender y retocada por Klein; loop de 10 s con H3 nativo
  a 928×512, 40 pasos y `tmix` (383 KB); FILM y tomas encadenadas descartados. La vertical con el micro quedó aprobada
  en el [06](tickets/06-movil.md) (v5, 222 KB); las transiciones con el micro van en el [17](tickets/17-transiciones-micro-v5.md).
- [16 Loops de 10 s en todo el santuario](tickets/16-loops-de-10s.md): 10 s en todos los loops; vertical con H3 a
  512×928 tomando sólo lo que se mueve; velas y polvo de 240 al mismo tempo sin repetirse; 354 / 262 KB por 10 s.

## Not yet specified

- **Pila y props/gente en la nave** ([06](tickets/06-movil.md) v4): sub y bocina en el piso aprobados "para seguir";
  la señora con rebozo, los nardos, la texana con rosario y el joven de gorra nunca se corrieron. Todo lo hecho después
  (v5, micro, loops de 10 s y las transiciones del 17, en los dos formatos) está sobre placas y profundidad de antes de
  la pila: hacerla rehace placas, loops y transiciones. El usuario la pidió ahora (2026-10-11), stills antes de H3.
- **Atrio con la troca del videoclip.** Propuesto, sin aprobar; se decide al guionizar los espacios.
- **Los retratos de El grupo en el camarín**: entran como HTML encima, uno a la vez (ticket 03); queda si la toma
  "empuja hacia un retrato que se abre" (handoff) o no.
- **El texto y el neón M⚡T** compuestos sobre la escena (nunca generados): dónde aparecen.
- **Pendientes heredados** que pueden tocar la especificación: el escudo de la selección en la camiseta del
  hero, el permiso de los directores de los videos y el test roto `capasEstacion.test.ts` (puede morir con la
  integración web).

## Out of scope

- La producción final de todos los espacios, el merge a `main` y el deploy. Van con el mapa cerrado.
