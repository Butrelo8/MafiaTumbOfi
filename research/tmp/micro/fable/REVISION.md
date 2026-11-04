# Revisión de Fable (2026-10-10) — micrófono colgado

Veredicto: aprueba el micro colgado (cable no es problema; oro deslustrado bien; altura de boca bien) y pegar y refinar.
Arreglos que pidió (todos aceptados por el usuario, ya en docs/specs/2026-10-10-micro-colgado-design.md):
1. Rejilla colgada hacia abajo: la cámara ve capuchón y costillas, no la cara. Brasa "por las costillas" + mancha cálida
   abajo; cable sale del capuchón; rosa al capuchón (estaba a la altura de la cruz, peleaba con el neón), sin listón.
2. Klein con gris iluminado (no alfa plano); brasa en post (medible); componer Klein sólo dentro de la máscara del sujeto
   (sin flujo); FOCO_MASK del alfa de Blender; dof.py toma df antes de la máscara (línea 22) → df explícito; humo con
   recorte del alfa.
3. Las transiciones vecinas de la nave se rehacen con micro() antes de cualquier deploy.
Además: escritorio a u 0.57–0.58 (a 0.55 tocaba el halo de la cruz y el borde del panel); vertical 13 px es igualar en
pantalla, no física: probar 10 primero.
