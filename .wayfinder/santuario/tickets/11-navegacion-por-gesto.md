# 11 — Navegación: un gesto, una sección
Type: grilling · Status: resolved · Blocks: 03, 05, 09 · Blocked by: — · Assignee: claude

## Question
¿La transición avanza con el scroll (estados intermedios) o un gesto de scroll la reproduce entera hasta la
siguiente sección?

## Answer
Decidido por el usuario el 2026-10-04: **un gesto = una sección**, sin estados intermedios. La transición se
reproduce completa a su velocidad (2.5 s); hacia atrás se reproduce un archivo invertido (`vuelta.mp4`).
Prototipo v3: `tmp/transicion-3/web/index.html` (rueda, flechas/PageDown/espacio, swipe, botones; con
`prefers-reduced-motion` corta directo sin transición).

Arreglos que vinieron con la decisión ("se deforma un poco en el cambio"), medidos:
- **Salto al negro:** MiniMax pinta el pilar como piedra iluminada, así que el negro forzado entraba de golpe
  (diferencia 18.7 en un cuadro). Ahora un pase `mascara` de Blender (alfa de `OCLUSORES`) pinta de negro
  exactamente lo que tapan pilar y jambaje: el negro barre con el pilar en 3 cuadros (11.6 → 7.1 → 1.8).
- **Loop → transición:** son generaciones distintas (diferencia 3.7–6.9 según el punto del loop); se cubre
  con 0.15 s de mezcla dentro del mismo lugar, durante el arranque lento del travelling.
- **Humo disparejo en la costura:** loops de 10 s (`PERIODO` 240) generados con 260 cuadros; los 20 de más
  se funden sobre el inicio (0.83 s). Sin comprimir, la costura queda como un cuadro más (1.02 contra 0.83);
  comprimida queda el "pop" de cuadro intra (~1.9), el mismo que aparece en cada keyframe de cualquier MP4.
  MiniMax tarda ~7.7 min por loop de 10 s a 864×480.
- **Peso:** sin avance por scroll ya no hace falta all-intra: ida o vuelta ~230 KB (antes 750 KB).

Consecuencias para otros tickets:
- **03 layout:** con un gesto por sección, el contenido de cada sección tiene que caber en una pantalla o
  vivir en un panel con su propio scroll (Música tiene tarjetas y videos).
- **05 peso:** el all-intra sale de la cuenta; se suma el archivo de vuelta.
- **09 integración:** secuestrar el scroll pide teclado, swipe, foco, lector de pantalla e historial
  (`#ancla` por sección) resueltos; con movimiento reducido, corte directo.

### Seguimiento (v4, mismo día)
El usuario vio un salto al llegar a la sacristía. Tres causas, corregidas y medidas
(`tmp/transicion-4/web/index.html`):
- **Contenido:** el cuadro 0 del loop es la mezcla de costura, no el cuadro donde acaba la transición. La ida
  (y la vuelta) llevan pegados los cuadros 0–19 crudos del loop, y el loop arranca en su cuadro 20.
- **Movimiento:** la deriva del loop arrancaba a velocidad máxima (`sin`); ahora sale de quieta (`1 − cos`).
- **Tartamudeo:** el montaje repetía cuadros (bases de tiempo distintas en `maskedmerge`); renumerado a 24 fps.
Unión transición → loop: 0.87 / 1.5, al nivel del ruido entre dos encodes.

> Nota (2026-10-04): el ticket 04 bajó los loops a 5 s (140 cuadros a 1280×704); la costura de 20 cuadros se mantiene.
