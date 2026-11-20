# G63 nuevo: colocar al reparto y quitar piezas

El sitio en vivo usa ahora tu `Mercedes-Benz_G63_AMG.blend` en lugar del 6x6. El reparto quedó en una colocación de partida
(la tuya de antes, bajada 0.28 m para que las cabezas con gorra entren bajo el techo). La colocación final es tuya.

## Pasos
1. Abre en Blender `E:\tmp\mto-g63-nuevo\colocar-g63.blend`. La vista arranca en la cámara «Cabina»; en la línea de tiempo hay cinco
   marcas (Cabina y las cuatro tomas de la banda). Los pasos también están en la pestaña **Scripting** (texto LEEME).
2. Solo se pueden seleccionar cuatro cruces: `posicion_manager`, `posicion_hector`, `posicion_alejandro`, `posicion_diego`.
   Cada cruz mueve a su personaje entero (la botella de Héctor va con Héctor).
3. **G** mueve, **R** gira (Z para girar sobre el piso), no uses **S**. Teclea un número después (`G`, `Z`, `-0.05`, Enter).
   Clic derecho o Esc cancela.
4. Revisa cada cámara (Numpad 0 y las flechas de la línea de tiempo): que nadie atraviese el techo, el asiento ni la puerta.
5. `Ctrl+S`. Avísale al dron o a la nave nodriza: «leer reparto de `<ruta de tu archivo>`».

## Lo que pasa después
La pose del reparto en tu archivo es la tuya de `colocar-reparto-v3` (hueso por hueso, `blender/props/reparto_pose_dueno.json`), no la que Blender
lee del `reparto.glb` (esa difiere de la tuya en el manager, Héctor y Diego). `blender/vivo_reparto_volcar.py` lee tu archivo (probado: sin mover
nada devuelve tu pose con 0.0000 m de error y z -0.28), el exportador viejo hornea al reparto en esa pose (`VIVO_POSE`), `scripts/vivo-g63.sh`
mete el coche nuevo y se sube un preview nuevo. Nada de esto toca producción.

## Lo que viene en el coche (cada pieza es un objeto, bórrala si no la quieres)
| Objeto (en el archivo del coche `vivo-g63.blend`) | Qué es |
|---|---|
| `rack_barra0-2`, `rack_pie*` | Las tres barras de aluminio y sus pies de plástico negro (sin estrella) |
| `k3_bajo`, `k3_docerola`, `k3_requinto`, `k3_teclado`, `k3_tarola` | Los estuches de instrumentos |
| `k3_dona`, `k3_alien` | La dona y el alien, acostado de cabeza hacia adelante |
| `carga_red` | La red que los sujeta (cuerda de 7 mm, celdas de 22 cm) |
| `vest_flecos` | Los flecos, las placas de terciopelo y la franja «MAFIA TUMBADA» del parabrisas |
| `vest_fresa`, `vest_banderin` | La fresa y el banderín |
| `vest_emblema`, `vest_placa` | El emblema MT (cofre) y la placa de Veracruz (defensa) |

No se trajeron: los focos y el alambre del barandal de la caja (los pediste fuera), la barra de LED del techo, los asientos y la consola
de Tripo, la consola del techo. El coche nuevo trae los suyos.

## Pintura y luces
El coche conserva su pintura azul marino metálico. Las luces del coche (faros DRL y calaveras) son materiales que brillan, no objetos
`luz_*` sueltos como en el 6x6; los faros de la carretera salen de los DRL.
