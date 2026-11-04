# 03 — Layout de la UI sobre la escena
Type: prototype · Status: resolved · Blocks: 06, 07, 08, 09, 10 · Blocked by: 11 · Assignee: claude

## Question
Por sección (hero, nave, sacristía, camarín, cripta, atrio): ¿dónde vive cada bloque (titular, texto,
tarjetas de música, retratos, CTA de WhatsApp) en escritorio y en móvil, y qué hueco tiene que dejar cada
toma? ¿El panel de contenido va sobre la escena o la escena se aparta? Salida: un wireframe por sección
que la dirección de cada espacio pueda respetar. Consultar `DESIGN.md`.

## Prueba (2026-10-05)
Prototipo `tmp/layout-03/web/index.html` (ignorado). Se sirve desde la raíz: `python3 -m http.server 8803` →
`http://localhost:8803/tmp/layout-03/web/?v=A`. Usa el contenido real (`catalog.json`, integrantes, textos de
`index.astro`), los loops reales de la nave (r6) y la sacristía, y placas pendientes para camarín, cripta y atrio.
Teclas: `[` `]` variante, `M` teléfono 390×844 (container queries), `H` el hueco que tiene que dejar la toma, `1`–`6`
o rueda/swipe para la sección (un gesto, una sección; un panel con scroll propio scrollea primero y sólo en su
borde, con un gesto nuevo, cambia de sección). La caja de estado mide si el contenido cabe o cuánto desborda.

Ronda 1: A columna sobre la escena, B la escena se aparta (pantalla partida), C titular y cajón. El usuario quedó
entre **A y C**; B fuera.

Ronda 2, con sitios de referencia (capturas por scroll con Playwright; el catálogo de `ProyectoInvestigación/
research/visuales.md` no tenía este patrón): travisscott.com (Utopia: escena limpia, una sola acción → C),
white-desert.com (ficha flotante sobre la foto), paulkalkbrenner.net (archivo de video de uno en uno, "01/08"),
landonorris.com ("Helmets / Hall of fame": título a la izquierda, texto a la derecha, en franja), badomens (rejilla
de tarjetas sobre fondo oscuro ≈ A), igloo.inc (la escena es todo, casi sin UI).
- **D · Titular que se abre**: llega como C (esquina) y "más" abre la columna de A en su sitio, con velo. Sin cajón.
- **E · Pasos 01/09**: titular + una pieza a la vez (un disco, un integrante, un párrafo), ‹ › / ←→ / swipe lateral.
  Nada scrollea: el gesto vertical siempre es sección.
- **F · Franja inferior**: el tercio de abajo, con el título a la izquierda y el contenido a la derecha; discos,
  videos e integrantes en filas que se recorren de lado.

Medido a 1440×900 (desborde del panel): Música A +1481 px, D abierta +1646, F +225, E 0 (23 pasos); Quiénes cabe
en A y D; Grupo en F +6 px. En móvil todo lo largo pide scroll propio salvo E.

## Answer
Decidido por el usuario el 2026-10-05: **mezcla por sección**, `?v=X` en el prototipo (variante por defecto).
Wireframe por sección, escritorio y móvil, con el hueco marcado: `tmp/layout-03/wireframes_mezcla.jpg`.

| Sección (espacio) | Layout | Qué deja la toma oscuro y sin sujeto |
|---|---|---|
| Inicio (hero) | **C** titular y una acción en la esquina: logo, chips, CTA de WhatsApp | esquina inferior izquierda, ~46 % × 52 % (móvil: mitad de abajo) |
| Quiénes somos (nave) | **D** titular que se abre | cerrado sólo la esquina; abierto la columna izquierda entera (~50 % de ancho); móvil: mitad de abajo |
| Música (sacristía) | **E** pasos: un disco o un video a la vez, contador 01/23 | bloque inferior izquierdo, ~50 % × 66 % (móvil: dos tercios de abajo) |
| El grupo (camarín) | **E** pasos: un integrante a la vez | igual que Música |
| Contratación (cripta) | **D** titular que se abre; el CTA de WhatsApp siempre a la vista | igual que la nave |
| Cierre (atrio) | **D** sin "más": monograma M⚡T, redes, © | esquina inferior izquierda |

- **Contenido sobre la escena, la escena no se aparta.** Al llegar se ve limpia (titular, una línea y una acción).
  D abre el texto en su mismo sitio, con un velo que oscurece el lado izquierdo; E nunca scrollea.
- **D:** la barra de scroll sólo existe abierta (cerrada, `overflow: hidden`); la viñeta y el velo viven en su
  propia capa, no en la columna. Música abierta en D desbordaba +1646 px; por eso Música y El grupo van en E.
- **E:** ‹ › con 44 px, ←/→ y swipe lateral pasan la pieza; el gesto vertical siempre es sección (sin choque con
  el ticket 11). Cada pieza es HTML (portada, nombre, enlace), nunca compuesta en la escena.
- Toda la composición pide el sujeto de cada toma **a la derecha o al centro** y el tercio izquierdo/inferior oscuro.

Consecuencias para otros tickets:
- **07 guion de espacios:** cada toma respeta el hueco de la tabla; camarín, cripta y atrio se encuadran con él.
- **06 móvil:** en vertical el hueco es la mitad o dos tercios de abajo; el sujeto va arriba.
- **09 integración:** D necesita foco al botón y Escape para cerrar; E necesita `aria-live` en la pieza y el swipe
  lateral separado del vertical; `#ancla` por sección ya responde a `hashchange` en el prototipo.
- **10 acabado UI:** el velo de D y la viñeta de la esquina se miden contra AA sobre cada placa (aquí son a ojo).
