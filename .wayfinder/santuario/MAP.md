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
  `blender` + `docs/blender-notas.md` antes de tocar `blender/`, `matt-grilling` en los tickets de conversación.
- Método probado: maqueta gris y cámara en Blender → cuadro de estilo con Klein → MiniMax H3 + ControlNet de
  profundidad → LOOK de `scripts/build-hero.sh`. Detalle en el ticket 01.
- El usuario: español, conciso, decide rápido y quiere ver renders. Rutas Windows (`E:\Cursor Projects\MTO\...`).
- Mapa de secciones: hero (video) → nave = Quiénes somos → sacristía = Música → camarín de las hornacinas =
  El grupo → cripta = Contratación → atrio = cierre.

## Decisions so far

- [01 Prueba nave → sacristía](tickets/01-prueba-nave-sacristia.md): el corte escondido tras un pilar funciona;
  MiniMax (ruta M) sobre DepthFlow (ruta D); 864×480 se queda corto de resolución.
- [02 Instrumentos como reliquias](tickets/02-instrumentos-nave.md): Klein y MiniMax los sostienen sin
  deformar; 3 semillas por cuadro (acierta 1 de 3); veladoras de ofrenda dan luz y movimiento al loop.
- [11 Navegación: un gesto, una sección](tickets/11-navegacion-por-gesto.md): la transición se reproduce
  entera (ida/vuelta), oclusor enmascarado desde Blender, loops con costura de 0.83 s (10 s → 5 s por el 04).
- [04 Resolución](tickets/04-resolucion.md): H3 a 1280×704 + RTX ×1.5 → 1080p; loops de 5 s (10 s no cabe en
  12 GB); FlashVSR descartado (inventa); a 1080p un loop pesa ~1 MB por 5 s.
- [12 Que el tololoche se lea como contrabajo](tickets/12-contrabajo.md): asset de contrabajo, requinto en una
  bocina, sahumador como fuente del humo; las reliquias van con su silueta real y a la altura del asiento o más.
- [13 Placa fija + capas](tickets/13-placa-y-capas.md): cámara quieta en los loops; placa de Klein fija y H3 sólo en
  zonas vivas (canny solo no basta); humo en loop propio, llamas chicas en post; muros de tezontle, bancas de verdad,
  capillas y rayo de luna en la nave.
- [03 Layout de la UI sobre la escena](tickets/03-layout-ui.md): el contenido va sobre la escena, mezclado por sección: C en el hero,
  D (titular que se abre) en texto, E (una pieza a la vez, sin scroll) en Música y El grupo; hueco oscuro abajo a la izquierda.

## Not yet specified

- **Atrio con la troca del videoclip.** Propuesto, sin aprobar; se decide al guionizar los espacios.
- **Los retratos de El grupo en el camarín**: entran como HTML encima, uno a la vez (ticket 03); queda si la toma
  "empuja hacia un retrato que se abre" (handoff) o no.
- **El texto y el neón M⚡T** compuestos sobre la escena (nunca generados): dónde aparecen.
- **Pendientes heredados** que pueden tocar la especificación: el escudo de la selección en la camiseta del
  hero, el permiso de los directores de los videos y el test roto `capasEstacion.test.ts` (puede morir con la
  integración web).

## Out of scope

- La producción final de todos los espacios, el merge a `main` y el deploy. Van con el mapa cerrado.
