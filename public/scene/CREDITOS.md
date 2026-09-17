# Créditos de imágenes de la escena

## escapulario.jpg

Virgen de Guadalupe, imagen de 1531 conservada en la Basílica de Guadalupe.
**Dominio público** (la obra es del siglo XVI).

- Fuente: Wikimedia Commons, `File:Virgen de Guadalupe 1531.jpg`
- Licencia declarada: Public domain / `pd`
- Crédito de la reproducción: www.virgendeguadalupe.org.mx
- Descargada y reescalada a 512 px de ancho el 2026-09-17

Se usa como estampa del escapulario que cuelga del nicho central en la escena
3D. No se altera la imagen más allá del reescalado.

## Modelos 3D de la escena

### Micrófono de cinta

Generado por el propio equipo (`microfono-spot.blend`), sin derechos de
terceros. Malla única sin materiales ni UV; se importa decimada a 12.000
polígonos y se le corta el disco de escenario con el que viene.

Sustituye al "Low Poly Microphone" de **mgordon** (Blend Swap 40491, CC-0) que
usó la escena hasta el 2026-09-17. Aquel no imponía condiciones, así que su
retirada no deja nada pendiente.

### Candelabro de nueve brazos

Generado por el propio equipo (`candelabro.blend`), sin derechos de terceros.
Malla única, decimada a 14.000 polígonos.

### Botella de tequila

Generada por el propio equipo (`botella.blend`), sin derechos de terceros.
Malla única sin materiales ni UV, decimada a 9.000 polígonos: es sólo la
silueta —cuerpo cuadrado, tapón de bola, lazo— sin logo, etiqueta ni texto.

### Cenicero desbordado

Generado por el propio equipo (`cenicero.blend`), sin derechos de terceros.
Cuenco y colillas son una sola malla, decimada de 438.000 a 16.000 polígonos.

### Lentes de montura dorada

Generados por el propio equipo (`lentes.blend`), sin derechos de terceros.
Malla única, decimada a 10.000 polígonos.

### Cadena cubana

Generada por el propio equipo (`cadena.blend`), sin derechos de terceros.
Malla única enrollada con broche, decimada de 260.000 a 20.000 polígonos.

### Cigarros de papel

Generados por el propio equipo (`prerolls.blend`), sin derechos de terceros.
Malla única, decimada a 12.000 polígonos.

### Cigarros sueltos — origen: foro de videojuegos, sin licencia escrita

`cigarros.blend` (`Cigarette_01_GEO` y `Cigarette_02_GEO`) no lo generó el
equipo: venía con materiales y texturas PBR. Del archivo sólo entran las dos
mallas, sin material ni textura.

Procedencia según quien lo aportó (2026-09-17): descargado de un foro de
videojuegos. No hay archivo de licencia. **Decisión del responsable del
proyecto: se usa igual**, asumiendo el riesgo, que es bajo porque son dos
cilindros de 7 cm que aparecen a contraluz. Si algún día hace falta quitarlo,
se rehacen con `_cilindro()` en media hora.

### Gorra

Generada por el propio equipo (`gorra.glb`), sin derechos de terceros. Se
importa decimada de ~92.000 a 18.000 polígonos.

### Descartado por licencia

"sport cap" (Blend Swap 88911): CC-0 pero **marcada como Fan Art**, con la
cláusula "you can not use it for commercial purposes under any circumstance".
El sitio de una banda que busca contrataciones es uso comercial, así que no se
usa.

### Guitarra clásica

`guitarra.blend`, descargada de Blend Swap. Del archivo original se usan sólo
las 17 piezas del instrumento; quedan fuera el soporte, el foco, el entorno del
autor y el objeto `Sticker`, que lleva un material llamado `hohner` — una marca
real que no tiene por qué aparecer en la escena.

El mismo asset se reutiliza escalado a 1,85 m como tololoche apoyado en una
columna: a esa distancia y en penumbra, la silueta de un contrabajo y la de una
guitarra grande no se distinguen.

**Pendiente:** confirmar autor y licencia exacta de este blend. Se descargó sin
su archivo de licencia, así que antes de publicar hay que verificarlo en Blend
Swap y anotarlo aquí; si resultara ser CC-BY, el crédito debe aparecer también
en el sitio.

### Velas y tololoche

`velas.blend` (trío de velas) y `tololoche.blend` (contrabajo), generados por el
propio equipo, sin derechos de terceros. Vienen como malla única, sin materiales
ni UV; se decimán y se les aplican los materiales del proyecto.

El trío de velas no se puede separar en velas sueltas —es una sola malla—, así
que se usa como grupo donde la cámara se acerca, y en las posiciones lejanas se
mantienen los cilindros, que a esa distancia rinden igual y cuestan mucho menos.

El tololoche sustituye el apaño anterior, que era la guitarra clásica escalada a
1,85 m.

### Púa

`pick.blend`, aportado por el usuario el 2026-09-17. Del archivo se usa sólo la
malla `Plane`, que es la púa; quedan fuera el suelo de 21 m, los dos paneles de
luz y la cámara del estudio del autor. Se le quita el material y el Subsurf, y
entra sin texturas: sólo geometría.

**Pendiente:** confirmar origen, autor y licencia. El blend llegó sin archivo de
licencia y su fecha interna es de 2013, así que no es del equipo. Antes de
publicar hay que verificarlo; si resultara ser CC-BY, el crédito debe aparecer
también en el sitio.
