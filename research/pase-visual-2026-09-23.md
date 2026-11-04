# Pase visual — qué se ve plano o sin detalle

2026-09-23. Hecho sobre los PNG de estación a resolución completa
(`tmp/frames/escritorio/estacion-N.png`, sin el velo de la web) y el inventario
de las 285 mallas de la escena. Referencia de dirección: la maqueta generada por
otro agente (catedral gótica, retablo dorado, velas encendidas por todas
partes, negros profundos).

## El diagnóstico en tres datos

- **Sólo 7 materiales usan imagen**: los 3 retratos, las polaroids, la estampa
  y los 2 cirios de latón. Todo lo demás es color plano o ruido procedural.
- **Sólo piedra, oro, cromo y alfombra llevan relieve o suciedad** (`_tallar`,
  `_ensuciar` en `look.py`). Madera, cera, vinilo, fieltro, papel y vidrio son
  color liso.
- **La arquitectura son cajas de 6 caras**: columnas, piso, techo, altar,
  escalones, bancas y marcos. Se leen como maqueta de cartón.

## Lista, de más visible a menos

Visible = en cuántas estaciones sale y cuánto cuadro ocupa.

| # | Qué | Dónde se ve | Estado hoy | Qué haría | Fuente propuesta (por verificar licencia) |
|---|---|---|---|---|---|
| 1 | **Luz general** | Todas | Lavada, gris rosada, sombras blandas, sin negro | Bajar el relleno, más contraste, más velas como fuentes pequeñas, haces con volumen. Obliga a recalcular el velo 0.62 | — (ajuste en `look.py`) |
| 2 | **Bancas** (9) | nave, altar, retirada; primer plano en altar | Cajas de 6 caras, madera sin veta | Banca de iglesia con costados tallados + madera oscura PBR | Blend Swap / Sketchfab CC0 "church pew"; madera Poly Haven |
| 3 | **Muros de la nave** | nave, altar, retirada | Yeso liso uniforme | Sillería o revoque gastado con zócalo | Poly Haven: texturas de piedra / plaster (CC0) |
| 4 | **Columnas** (12) | nave, altar, retirada | Prismas lisos sin basa ni capitel; parecen muros | Columna gótica de haces con basa y capitel | Asset CC0 o modelado por código |
| 5 | **Sin arcos ni bóveda** | nave, altar, retirada | El techo es un plano negro | Arcos ojivales entre columnas, nervaduras | Modelado por código (curvas) o asset |
| 6 | **Piso** | nave, altar, retirada | Gris liso | Losa de piedra o mármol gastado | Poly Haven (CC0) |
| 7 | **Veladoras** (4) + **trío de velas** | sonido, hornacinas, reliquia (primer plano) | Cilindros de 18 caras, facetas visibles, cera plana, llama de esfera | Cambiar por cirios de latón (ya los tenemos) y veladoras de vaso mexicanas con estampa | Poly Haven `brass_candleholders` (en uso) |
| 8 | **Mesa del altar** | sonido, reliquia (casi todo el cuadro) | Beige liso, se lee como cartón | Mantel de encaje o tela con caída, o madera oscura | Textura de encaje/tela Poly Haven; o simulación de tela |
| 9 | **Vinilos** (3) | sonido | Cilindros sin surcos; el de la pila parece una caja; etiqueta naranja lisa | Surcos (anillos en normal/anisotropía), etiquetas con arte MT, pila de discos o fundas | Procedural en `look.py` + etiqueta generada |
| 10 | **Retablo** | nave, altar, retirada | Muro rojo liso detrás del neón | Retablo dorado tallado alrededor del neón, o tela | Asset CC0 o relieve procedural |
| 11 | **Marcos de hornacinas** (3) | hornacinas (plano entero), nave | Cajas doradas lisas | Marcos ornamentados tallados | Asset CC0 de marco barroco |
| 12 | **Altar y antependio** | nave, altar, retirada | Bloque liso con panel naranja plano | Frontal bordado, mantel que cae | Tela / textura |
| 13 | **Botella y micro** | sonido, reliquia | Superficie arrugada por la decimación ("papel aluminio") | Subir el techo de polígonos o suavizar | — (`assets.py`, techo de `_decimar`) |
| 14 | **Vaso, frasco, cerámica** | sonido, hornacinas | 14–22 polígonos, facetados | Assets de vidrio; tequila en el vaso (como la referencia) | Poly Haven (CC0) |
| 15 | **Escalones del presbiterio** | nave, altar, retirada | Cajas lisas | Piedra con canto gastado (textura + bisel) | Poly Haven |
| 16 | **Gorra, cinturón** | reliquia | Fieltro color plano | Tela con textura; cuero para el cinturón (pendiente de antes) | Poly Haven fabric/leather |
| 17 | **Vidrio de las ventanas** | nave, altar, retirada | Blanco plano | Vitral con color, o mantener la tormenta con textura | Textura de vitral |
| 18 | **Billetes, caja, cerillos** | sonido, hornacinas | Cajas de color plano | Texturas de papel impreso | Generadas |
| 19 | **Guirnalda de focos** | nave | Cubitos | Bombillas reales | Asset pequeño |

## Lo que está bien y no hay que tocar

Tracería de las ventanas, retratos, polaroids, cirios de latón, candelabros de
pie (forma), tololoche, guitarra, la fiel, el neón M⚡T y el relieve de la
gorra.

## Coste

Cualquier cambio visible obliga a re-renderizar la escena entera: **~85 min**
(336 imágenes, dos formatos). Conviene juntar todos los cambios en un solo
render. Si cambia la luz (punto 1), hay que recalcular el velo de la web y la
tabla de contraste de `DESIGN.md`.

## Dirección: capilla de pueblo, de noche, en velorio

Referencias en `tmp/ref/capillas/hoja.jpg` (Wikimedia Commons). La idea: que lo
lúgubre salga del **uso** —humedad, hollín, cera acumulada, devoción de años—
y no de efectos de feria de sustos (telarañas, calaveras que brillan). Una
capilla viva y gastada, no una casa embrujada.

| # | Qué agregar | De dónde sale | Por qué funciona aquí | Coste |
|---|---|---|---|---|
| A | **Mar de veladoras de vaso rojo** en el escalón del presbiterio y al pie del altar, encendidas | Altar de San Rafael Guízar (Veracruz), altares populares | Se vuelven la luz principal, desde abajo: negros arriba y un resplandor cálido abajo. Es exactamente lo que le falta a la luz | Medio: una veladora bien hecha e instanciada cientos de veces |
| B | **Reja de hierro forjado** (comulgatorio) delante del altar | San Rafael Guízar | Da una capa de silueta en primer plano, y otro objeto para la capa de frente que pasa por delante de los titulares | Medio: asset o curvas por código |
| C | **Cera derretida acumulada**: chorreados en candeleros, escalón y bordes de la mesa | Capilla de Béthanie | Cuenta tiempo y abandono. Quita el "recién salido de fábrica" de las velas | Bajo–medio: geometría por código |
| D | **Muros con humedad, cal descascarada y manchas de hollín** encima de cada vela | Capillas de pueblo | Lo más lúgubre por lo más barato: sólo texturas y un par de calcas | Bajo |
| E | **Retablo dorado gastado** alrededor del neón, en lugar del muro rojo liso: el oro sólo brilla donde le da la vela | Retablo de Acatepec | Es el "más detalle" de la maqueta del otro agente, pero en sombra y viejo | Alto: asset tallado o relieve |
| F | **Óleos oscurecidos en marcos dorados** en los muros laterales | Sagrario de Puebla | Rellena muros hoy vacíos; barniz amarillento, casi ilegibles | Bajo: texturas de dominio público |
| G | **Exvotos, milagritos de lámina y placas de agradecimiento** cubriendo un tramo de muro; **billetes pegados con peticiones** | Tradición de exvotos; la mecánica de las capillas populares del norte | Conecta con el corrido: historias de favores y deudas. Ya hay `EXVOTO_` y billetes: es crecerlos | Bajo–medio |
| H | **Flores**: rosas rojas marchitas y cempasúchil en botes de lata | Ofrendas | Color y textura orgánica; lo marchito es lo lúgubre | Medio: asset de flor instanciado |
| I | **Humo de copal** en los haces de luz de las ventanas (volumen real, fino) | — | Lo que la bruma quiso ser: sale de un sahumerio con fuente visible | Medio |

**Cuidado con la iconografía:** la mecánica de las capillas populares del
norte (billetes pegados, placas, veladoras apiladas) funciona sin ningún santo
concreto. Poner a Malverde u otra figura asociada al narco ligaría a la banda a
esa lectura, igual que se decidió no poner armas ni marcas reales.

**Orden sugerido para un solo render:** luz (1) + veladoras rojas (A) + muros
con hollín y humedad (D) + bancas (2) + piso (6). Es lo que más cambia la
lectura con menos assets nuevos.
