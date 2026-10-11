# 17 — Transiciones con el micro y la v5
Type: prototype · Status: open · Blocks: 09 · Blocked by: — · Assignee: —

## Question
El loop de la nave ya tiene el micro colgado (15) y la v5 (placa real + foco de lente, 14); las transiciones vecinas
(nave → sacristía de ida y vuelta, y la llegada desde el hero del 08) no tienen ninguno de los dos, así que el micro
aparecería de golpe en el corte. La spec del micro lo pone como condición dura antes de cualquier deploy. ¿Cómo se
llevan las dos cosas a una toma con cámara en movimiento?
- **Micro y rosa** en una toma que se mueve: `micro()` en la maqueta y H3 + ControlNet como en el 01, o el sujeto
  compuesto aparte (render de Blender por cuadro, como la rosa del 15), porque H3/Klein lo deforman.
- **Foco de lente** por cuadro: MoGe por cuadro o profundidad desde Blender; ¿tiembla el foco entre cuadros?
- Orden con el obturador de 180° del 14 (FILM ×8 antes del LOOK) y empalme con el loop de 10 s (mezcla de 0.15 s del 11).
