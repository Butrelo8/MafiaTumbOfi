# G63 nuevo: colocar al reparto y quitar piezas

El sitio en vivo usa ahora tu `Mercedes-Benz_G63_AMG.blend` en lugar del 6x6. El reparto quedó en una colocación de partida
(la tuya de antes, bajada 0.28 m para que las cabezas con gorra entren bajo el techo). La colocación final es tuya.

## Pasos
1. Abre en Blender `E:\tmp\mto-g63-nuevo\colocar-g63-manos.blend` (es tu `colocar-g63.blend` de las 05:19 más los controles de abajo; tus cruces,
   tu pose y tus piezas del techo no se movieron, medido). La vista arranca en la cámara «Cabina» como la dejaste; en la línea de tiempo hay
   cinco marcas (Cabina y las cuatro tomas de la banda). Los pasos también están en la pestaña **Scripting** (texto LEEME).
   Ojo: en tu archivo de las 05:19 la cámara «Cabina» quedó **afuera** del coche (5.40, 2.23, 2.47; a las 05:18 estaba en 1.47, 0.06, 1.54), y así
   la dejé; para ver las manos dentro de la cabina usa las marcas de las cámaras `cam_<nombre>_asiento`. La reconstrucción no lee las cámaras de este archivo.
2. Se pueden seleccionar: las cuatro cruces `posicion_manager`, `posicion_hector`, `posicion_alejandro`, `posicion_diego`, los controles de
   manos y codos, y las piezas del techo (abajo). Cada cruz mueve a su personaje entero, con sus manos (la botella de Héctor va con su mano).
3. **G** mueve, **R** gira (Z para girar sobre el piso), no uses **S**. Teclea un número después (`G`, `Z`, `-0.05`, Enter).
   Clic derecho o Esc cancela.
4. Revisa cada cámara (Numpad 0 y las flechas de la línea de tiempo): que nadie atraviese el techo, el asiento ni la puerta.
5. `Ctrl+S`. Avísale al dron o a la nave nodriza: «leer reparto de `<ruta de tu archivo>`».

## Manos (dentro de la cabina)
Cada personaje tiene cuatro controles, dos por mano (`izq` y `der` son la izquierda y la derecha **del personaje**, no las tuyas):

| Control | Forma | Qué hace |
|---|---|---|
| `mano_izq_<nombre>`, `mano_der_<nombre>` (`mano_izq_hector`, …) | flechas en la muñeca | **G** mueve la mano y el brazo la sigue; **R** gira la mano |
| `codo_izq_<nombre>`, `codo_der_<nombre>` | bolita cerca del codo | hacia dónde apunta el codo: súbela, bájala o ábrela |

- Los controles cuelgan de la cruz del personaje: si mueves la cruz, las manos van con él.
- Los dedos conservan tu pose. **Agarre** (opcional): selecciona la mano, abajo a la derecha Propiedades > pestaña Objeto > Propiedades
  personalizadas > `agarre` (0 = tu pose, 1 = puño; los 4 dedos y el pulgar). Las manos del modelo son tipo manopla, así que cierra como manopla.
- El brazo no se estira: si pones la mano más lejos de lo que llega, el brazo queda recto y la mano no alcanza el control. Acércala.
- La botella de Héctor cuelga del control de su mano derecha (`mano_der_hector`): se mueve con ella.
- No toques **S** en nada, ni borres controles. Los huesos del brazo no se seleccionan; todo se hace con los controles.

## Cosas del techo
Cada pieza tiene su cruz, en su centro: `techo_bajo`, `techo_docerola`, `techo_requinto`, `techo_teclado`, `techo_tarola`, `techo_dona`, `techo_alien`
(con su nombre visible). **G** mueve, **R** gira, sin **S**. La red `carga_red` no se puede seleccionar y **no sigue a las piezas** mientras acomodas
(en Blender se ve vieja): se vuelve a tender sola sobre donde las dejes cuando se reconstruye (`scripts/vivo-g63.sh` con `VOLCADO=<tu volcado>`,
o `blender/g63_red_ajustar.py` sobre tu archivo). Si quieres verla bien mientras acomodas, escóndela con el ojo del Outliner (`carga_red`);
la red solo cubre el área entre las barras: una pieza que saques de ahí queda sin red.

## Lo que pasa después
La pose del reparto en tu archivo es la tuya de `colocar-reparto-v3` (hueso por hueso, `blender/props/reparto_pose_dueno.json`). Si abres el
`reparto.glb` en Blender, el manager, Héctor y Diego salen en reposo (no en tu pose) solo porque el importador deja su clip en una pista NLA
silenciada y activa nada más el de Alejandro; el archivo y la página tienen tu pose exacta (0.0000 m en los cuatro, medido). Para verla en Blender,
asigna la acción de cada uno como activa. `blender/vivo_reparto_volcar.py` lee tu archivo (probado: sin mover
nada devuelve tu pose con 0.0000 m de error y z -0.28), el exportador viejo hornea al reparto en esa pose (`VIVO_POSE`), `scripts/vivo-g63.sh`
mete el coche nuevo y se sube un preview nuevo. Nada de esto toca producción. El volcado ahora también lleva las manos y los brazos tal como
quedan con tus controles (cada hueso evaluado), y la posición de cada pieza del techo (`props`): el coche se reconstruye con las piezas donde
las dejes y la red tendida encima.

Qué se tocó en el archivo de manos: a los huesos del brazo y antebrazo se les alargó la cola hasta el hueso siguiente (el importador los dejó
con un hueco de ~2 cm y Blender no resuelve IK así); la cabeza, la orientación y la pose de los huesos quedan iguales.

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
