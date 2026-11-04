# 02 — Instrumentos como reliquias: prueba en la nave
Type: prototype · Status: resolved · Blocks: 07 · Blocked by: — · Assignee: claude

## Question
¿Klein y MiniMax sostienen instrumentos de corridos tumbados sin deformarlos? Prueba: requinto y tololoche
recargados en la primera banca de la nave, como ofrenda, con silueta en Blender para que la profundidad lleve
forma y posición. Mirar cuerdas, trastes y clavijero a lo largo del loop y de la transición. Si se deforman,
¿qué lo arregla: más cerca o más lejos, de lado, en estuche o compuesto encima?
De paso: el instrumento cerca de la cámara es el primer plano que le falta al travelling (ticket 01).

## Answer
Resuelto el 2026-10-04. **Sí: Klein y MiniMax sostienen los instrumentos.** En el loop de 124 cuadros y en la
transición, el requinto y el tololoche no se deforman: cuerdas rectas, mismo cuerpo, mismo clavijero.

- **Colocación:** tololoche de pie frente a la primera banca de la derecha, requinto en la orilla de la banca
  recargado en él; veladoras de ofrenda en el piso como luz motivada. El titular de la nave vive a la
  izquierda, así que el lado derecho es de las reliquias.
- **Klein acierta la identidad 1 de 3 veces:** con la silueta de guitarra grande, una semilla dio tololoche
  (forma de violín, cordal), otra lo volvió guitarra y otra un instrumento raro. Para la producción: 3
  semillas por cuadro de estilo y elegir; mejor aún, modelar la silueta del tololoche con hombros caídos.
- **De paso:** los instrumentos son el primer plano que le faltaba al travelling (nota de 01): ahora hay
  paralaje desde el primer cuadro. Y las veladoras le dan movimiento al loop de la nave (diferencia media
  entre cuadros 0.07 → 0.37).
- **Bug encontrado y corregido:** la bóveda de cañón nunca se había cortado a la mitad (`transform_apply` no
  surte efecto vía MCP) y su mitad de abajo tapaba bancas y piso. En la prueba 01 las bancas las inventó
  Klein; ahora están en la geometría y en la profundidad.
- **Sin probar:** el micrófono de bala de la sacristía. Va en la producción de ese espacio (ticket 07).

Assets: `tmp/transicion-2/` — `web/index.html` (página de prueba v2), `klein/hoja.jpg` (3 semillas),
`check/instA.jpg` (los instrumentos a lo largo del loop). Escena: `blender/transicion.py` (`instrumentos()`).
