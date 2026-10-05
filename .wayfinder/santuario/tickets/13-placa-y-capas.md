# 13 — Detalle que hierve y humo del loop: placa fija + capas
Type: prototype · Status: open · Blocks: 05, 09 · Blocked by: — · Assignee: —

## Question
En el loop de la nave (ticket 12, v4) el usuario ve deformarse el detalle fino: el puente de la guitarra (donde
van las cuerdas) y la talla alrededor de los santos. Medido etapa por etapa (`tmp/contrabajo-12/diag/`): el
cuadro de Klein lo tiene nítido; **el cuadro 0 de H3 ya lo pierde** y del 0 al 115 la talla y las caras cambian
de forma (H3 repinta todo el cuadro en cada cuadro: lo menor que su retícula latente lo reinventa). RTX sólo
afila lo que H3 entrega; no es la compresión. El humo, además, cambia de forma y densidad dentro del loop y en
la costura se ven dos columnas fundidas (lo mismo que el ticket 11 llamó "humo disparejo").

¿Se arreglan los dos con **placa fija + capas**? Cámara quieta en el loop (sin la deriva de ±3 cm), la placa es
el cuadro de Klein (más megapíxeles, sin escalar) y sólo lo que vive se anima encima con máscaras exactas de
Blender: llamas y neón desde H3 en zonas pequeñas, y el humo desde H3 en su zona o de stock CC0 en loop (el
"plan B" del mapa). Probar en la nave: ¿se nota la costura entre placa y capas? ¿se extraña la deriva? ¿cómo
empalma con la llegada de la transición? Comparar contra el loop v4.
