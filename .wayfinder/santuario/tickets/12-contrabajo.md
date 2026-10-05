# 12 — Que el tololoche se lea como contrabajo
Type: prototype · Status: resolved · Blocks: 09 · Blocked by: — · Assignee: claude

## Question
En la nave el tololoche sale como "una guitarra gigante" (el usuario, 2026-10-04). Causa: en Blender,
`_instrumento` (`blender/transicion.py`) lo arma con los mismos dos discos que la guitarra, y la profundidad
de ControlNet y Klein siguen esa silueta. ¿Qué maqueta lo lee como contrabajo: hombros caídos que entran al
mástil, cintura en C con efes, voluta, pica, ~1.8 m — modelado a mano o el asset
`tmp/Midnight_Upright_Bass_0917081601_generate.blend` (revisar su licencia, ver commit d628b12)? Prueba:
cuadro de estilo de Klein (3 semillas) y un loop de 5 s a 1280×704 (ticket 04). Referencia del usuario:
https://search.brave.com/images?q=contrabajo

## Prueba (2026-10-04)
- **Maqueta:** el tololoche ya es el asset de contrabajo del proyecto (`blender/assets/tololoche.blend`, el mismo
  archivo que `Midnight_Upright_Bass…`; "generado por el equipo" en `public/scene/CREDITOS.md`), cargado con
  `assets.tololoche()` en `instrumentos()`. Apoyo medido con BVH: en y 5.85 cruzaba la banca (475 triángulos)
  y rozaba el requinto; en **y 5.69** queda recargado sin cruzar nada. El requinto sigue con discos.
- **Encuadre:** a 1.6 m de alto y 35 mm, lo que está debajo de ~0.55 m sale de cuadro: el contrabajo se ve de la
  cintura para arriba (igual que antes). Los hombros caídos, las efes, la voluta y las clavijas bastan para leerlo.
- **Klein:** 3 de 3 semillas dan contrabajo (antes 1 de 3), con el prompt describiendo hombros caídos, efes,
  cordal y voluta. Elegida la 33 (el bajo mejor iluminado).
- **Loop de 5 s a 1280×704** (ticket 04): 141 cuadros en 636 s; el contrabajo no se deforma en todo el loop.
  Costura 1.10 (dentro del loop ≤ 0.47; el ticket 11 aceptó el salto de cuadro intra, ~1.9). 858 KB por 5 s a
  1080p.
- De paso `transicion.py` queda en `PERIODO` 120 / `N_LOOP` 141 (ticket 04). H3 entrega 17n+5 cuadros: pedir
  140 da 141; la costura toma sólo 120–139.

Assets (en `tmp/`, ignorado): `tmp/contrabajo-12/` — `index.html` (antes / ahora), `klein/hoja.jpg` y
`klein/hoja_bajo.jpg` (3 semillas), `check_bajo.jpg` (cuadros 0/60/110), `klein.sh`, `h3.sh`, `montar.sh`.

### v2: el requinto flotaba (2026-10-04)
El usuario: la guitarra "desafía la gravedad". Al adelantar el contrabajo a y 5.69 el requinto quedó parado en
la orilla de la banca sin nada que lo sostuviera, inclinado hacia atrás (−8°) donde no hay respaldo. Búsqueda
con BVH (x, y, inclinación atrás/de lado) del primer contacto con el bajo: casi todos los contactos caían a
z ≈ 1.0 (la base rozando el bajo, no lo sostiene); uno sólo apoya alto. Ahora el requinto está **de pie en la
banca (1.1, 6.1, 0.9), 22° de lado, con el clavijero recargado en la voluta del contrabajo**: contacto a
z 1.49, sobre su centro de masa (~1.2), sin cruzar la banca. Klein 3 de 3 semillas lo pintan así (prompt:
"headstock rests against the scroll of the double bass"); elegida la 33. Loop de 5 s: 642 s, costura 1.11,
849 KB. Ambos instrumentos firmes en todo el loop (`check_bajo_v2.jpg`). En la página: botón 3 (`web/nave2.mp4`).

### v3: el requinto en una bocina (2026-10-04)
El usuario pidió algo que lo sostenga: stand, acostado en la banca o un objeto de la música (bocina). Tres
maquetas (`tmp/contrabajo-12/variantes.py`): **acostado no se ve** (a 1.6 m de alto queda de canto, tapado por
la banca); el stand y la bocina sí, y tienen que ir **en el asiento**: lo que esté debajo de ~0.6 m sale de
cuadro. El usuario eligió **la bocina, semilla 22**. En `instrumentos()`: bocina de pie en el asiento
(0.58–0.98 × 6.2–6.48 × 0.9–1.52) y el requinto delante, recargado 9° atrás en su frente (último ángulo sin
cruzarla, BVH). El script reproduce la maqueta exacta (diferencia 0). Loop de 5 s: 616 s, costura 1.13,
837 KB; los tres objetos firmes en todo el loop (`check_bajo_v3.jpg`). Página: botón 4 (`web/nave3.mp4`).

### v4: el humo con fuente (2026-10-04)
El usuario: el humo "sale de la guitarra" (en v3 brotaba junto al clavijero, sin fuente). Decidido (el usuario
dejó elegir): **sahumador de copal de barro sobre la bocina, a la derecha del clavijero** — justo donde ya
aparecía el humo — con una luz de brasa; y **veladoras nuevas con humo tenue**: una en la bocina y dos en la
segunda banca (la de x 0.8 quedaba tapada por la bocina; en x 0.6 se ve). Sahumador modelado con primitivas
(el asset `sahumerio.glb` es un incensario colgante con cadena, no va apoyado). Prompt: "a thin ribbon of copal
smoke rises from the clay burner… the votive candles give off only faint wisps". Klein: semilla 22 (la 11 pintó
dos sahumadores; la 33 metió la rejilla en la guitarra otra vez). Loop: 650 s, costura 1.01, 798 KB; la columna
sale del sahumador en todo el loop y las veladoras sólo dan hilos (`humo_v4.jpg`). Página: botón 5 (`nave4`).

## Answer
Aprobado por el usuario el 2026-10-04 (v4, "sí queda bien"). La nave queda: **contrabajo = asset** recargado en la
primera banca (y 5.69), **requinto recargado en una bocina** de pie sobre el asiento, **sahumador de copal** en la
bocina como fuente del humo y **veladoras** extra con humo tenue (bocina y segunda banca). Todo en
`instrumentos()` de `blender/transicion.py`, medido con BVH. Reglas que salen para los demás espacios:
- Las reliquias tienen que ir en la maqueta con su silueta real; Klein copia la silueta que le dan.
- A esta altura de cámara lo que esté debajo de ~0.6 m no sale: los apoyos van a la altura del asiento o más.
- Cada humo necesita una fuente visible (sahumador, vela); si no, el modelo lo saca de donde sea.
Lo que el usuario vio después (detalle que se deforma y humo del loop) no es de este ticket → ticket 13.
