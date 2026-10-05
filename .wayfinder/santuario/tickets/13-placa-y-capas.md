# 13 — Detalle que hierve y humo del loop: placa fija + capas
Type: prototype · Status: resolved · Blocks: 05, 09 · Blocked by: — · Assignee: claude

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

## Prueba (2026-10-04)
Ruta del anuncio de `E:\ComfyUI` (PLAYBOOKS.md "producto", `research/studio-ads.md` §6–11): control **canny** en vez
de profundidad (lleva letras y estrías), 40 pasos, `end_percent 0.5`; el detalle que aun así se cae se compone encima.
Aquí la talla no está en la maqueta (la inventa Klein), así que el canny sale **de la placa de Klein**, repetido en
los 141 cuadros (cámara quieta por construcción), con las zonas vivas en negro para que H3 las anime.
- **Zonas** (`tmp/placa-13/zonas.py`): a mano en píxeles de la placa, no desde Blender: Klein movió y añadió veladoras
  (las de la maqueta están en el suelo, fuera de cuadro). Neón, cirios, 8 veladoras, humo del sahumador menos el
  clavijero del requinto. Máscara difuminada 8 px a 1080p.
- **H3**: 1111 s (40 pasos). r1 = H3 entero; r2 = placa (Klein escalada, sin H3) + H3 sólo en las zonas.
- **Medido** (`medir.py`, diferencia media del recorte cuadro 0 → 60 / 115, tras el LOOK):

  | | santos | puente | costura | peso 5 s |
  |---|---|---|---|---|
  | v4 (profundidad, deriva) | 4.57 / 3.26 | 1.55 / 1.31 | 1.38 | 798 KB |
  | r1 (canny de la placa, quieta) | 4.98 / 3.57 | 1.39 / 1.33 | 1.49 | 881 KB |
  | r2 (placa + capas) | **0.76 / 0.68** | **0.31 / 0.36** | **0.74** | **525 KB** |

  El canny solo **no** basta: H3 repinta la talla igual aunque tenga sus bordes en cada cuadro (r1 ≈ v4). Con placa
  + capas la talla y las cuerdas no se mueven (lo residual de "santos" son los cirios dentro del recorte) y pesa un
  tercio menos. El humo sigue cambiando de densidad dentro de su zona (`humo_r2.jpg`): eso no lo arregla la placa.
- Pendiente de ver el usuario: costura placa/capas, si se extraña la deriva, el grano congelado en la placa.

Assets (`tmp/placa-13/`, ignorado): `index.html` (v4 / r1 / r2), `hoja_santos.jpg` y `hoja_puente.jpg` (filas v4, r1,
r2; columnas 0/60/115), `humo_r2.jpg`, `zonas_check.jpg`, `h3.sh`, `montar.sh`, `medir.py`.

### v2: humo en loop y bancas de verdad (2026-10-04)
El usuario vio r2: "se conservan los detalles, incluso el humo se ve más realista", pero el humo "no está tan
loopeado" y se nota la costura. Además: las bancas "parecen cajas nada más".
- **Humo (r3):** loop propio de 60 cuadros, fundido de punta a punta (cuadro t = crudo t·t/60 + crudo t+60·(1 − t/60)),
  2 veces exactas en los 120. Sin pérdida la costura del humo mide lo que un cuadro cualquiera (2.95; mediana 2.54).
  Codificado queda un salto de nitidez del grano en el cuadro intra (≈ 4–5 contra máx. 3.3): la forma es continua
  (`bancas/costura_humo.jpg`); `mbtree=0`, `-tune grain`, `ipratio` no lo quitan.
- **Bug de r2:** las imágenes con `-loop 1` entraban a 25 fps y el video a 24; `maskedmerge` sincroniza por tiempo y
  perdía 5 cuadros, así que el loop no cerraba. Ahora `-framerate 24` en cada imagen.
- **Bancas (r4):** `_banca` en `blender/transicion.py`: respaldo delgado con remate de 12 cm a 0.9 m, asiento a 0.45 m
  con hueco, costados con descansabrazos. La bocina baja al asiento (desde la cámara igual); requinto y veladoras
  sobre el remate. BVH: nada cruza (las veladoras de la 2.ª banca sólo tocan el remate); el remate no sobresale hacia
  la cámara porque el contrabajo lo cruzaba. Klein: 3 de 3 semillas pintan bancas (molduras, costados, hueco entre
  filas); elegida la 22 (la 11 y la 33 funden la guitarra con el woofer). H3 1081 s; zonas nuevas, cirios del altar con
  caja por llama para no animar la talla del banco del retablo. Costura del cuadro 0.52, santos 0 → 60 0.56, 517 KB.
- Regla que sale: **desde atrás una banca también es casi un tablero**; lo que la hace leer como banca es el remate,
  los costados con perfil y el hueco entre filas, más el prompt que la describe.

Assets: `tmp/placa-13/bancas/` (`gris_antes_ahora.jpg`, `hoja.jpg` 3 semillas, `zonas_check.jpg`, `r4_60.jpg`,
`costura_humo.jpg`, scripts). Página: tecla 4 (r3) y 5 (r4).

### v3: las velas lejanas no se movían (2026-10-04)
El usuario: r4 "10/10", pero sólo titilan las velas de la bocina. Medido en el crudo de H3 (desviación por zona en
el loop): las dos de la bocina 10.8 y 4.2; todas las demás ≤ 3.8 = ruido. **H3 no anima llamas chicas lejanas**,
aunque su zona esté libre en el canny. Ahora: H3 sólo pone el humo y esas dos velas (`H3` en `zonas.py`); las demás
titilan en post sobre la placa (`velas.py` → `placa_viva.mkv`): brillo × (1 + suma de 4 senos con periodos que dividen
120, fase propia por vela), pesado por la luminancia (llama, cera y halo). Loop exacto por construcción; el neón queda
fijo. Desviación ahora 1.6–6.9 por vela. Sin vaivén de la llama: si hace falta, siguiente paso.
- Corrección: la vela a la derecha del contrabajo (pared clara atrás) se veía con un rectángulo: el peso por luminancia
  modulaba toda la caja. Ahora el peso cae radial desde la llama hasta cero antes del borde (borde de caja: std 0.26).

### v4: muros de tezontle (2026-10-05)
El usuario pidió reelegir el tono de los muros. DESIGN.md: lienzo casi negro, oro = identidad, rojo = energía; los
muros crema eran la superficie grande más brillante (compiten con el retablo y con el texto HTML encima). Probados
con Klein editando sólo los muros de la placa (`tmp/placa-13/muros/hoja.jpg`): **tezontle** (piedra volcánica de
la región, igual que los pilares), almagre (rojo plano en superficie grande: DESIGN.md lo prohíbe, compite con el
neón) y cal ahumada (sucia, sigue clara). Tezontle v2: juntas oscuras, piedra irregular (las blancas se leían
ladrillo). Klein redibuja el cuadro entero, así que H3 se corrió de nuevo (r5). **Aprobado por el usuario.**

### v5: capillas, Vía Crucis y ventanal con luna (2026-10-05)
Investigado (catedral de Xalapa: neogótica de 1896, santos estofados XVIII–XIX, relicario de Santa Teodora; exvotos
y capillas laterales coloniales). Aprobado por el usuario: Cristo negro, urna con santo yacente, candelero de
veladoras rojas, Vía Crucis en los pilares; exvotos y milagritos fuera (2–5 px a esa distancia, se deforman).
- **Dónde se ve:** medido con rayos desde la cámara, hacia el muro del fondo de las naves laterales sólo hay una
  rendija de ~30 px; lo que se ve son los arcos 1 y 2 entre pilares. `capillas()` en `blender/transicion.py`: Cristo
  en el arco 1 derecho (3.3, 12.0, girado a cámara; en y 11 lo tapaba el pilar 1), urna en el arco 1 izquierdo,
  candelero al fondo del arco 2 izquierdo, Vía Crucis en la cara interior de los pilares 1–3 (el del pilar 3 derecho
  no: cae en la zona del humo). BVH: nada cruza pilares ni bancas. Todo fuera de la zona del humo.
- **Ventanal:** el usuario lo propuso "si es de día"; la escena es de noche (velas, neón), así que va un **rayo de
  luna**: lanceta en un tramo de muro sobre el arco del fondo izquierdo + spot frío hacia el pasillo. A esa altura
  sólo se ve de canto (el encuadre corta arriba de ~4 m en los arcos cercanos); Klein lo pinta con el prompt.
- **Klein:** 3 semillas; elegida la 22 (la 11 y la 33 funden la guitarra con el woofer otra vez). Dos haces de luna
  entre el copal. H3 1104 s. Zonas nuevas a mano; velas que H3 deja quietas titilan en post; **racimos** (candelero,
  fila roja de la urna, vitrina) con fase por píxel y peso por canal más brillante (en gris una veladora roja da
  ~0.23 y no pesaba), con el peso desvanecido 6 px al borde de la caja (si no, canto recto). r6: costura 0.37,
  santos 0 → 60 0.32, 417 KB.

Assets: `tmp/placa-13/capillas/` (`gris.png`, `hoja.jpg`, `zonas_check.jpg`, `std_izq2.png`, `std_vitrina.png`,
`r6_60.jpg`). Página: tecla 6 (r5) y 7 (r6).

## Answer
Aprobado por el usuario el 2026-10-05 (r6, "está muy bien todo, excelente"). Sí: **placa fija + capas** arregla el
detalle que hierve. Los loops de cada espacio se hacen así:
- **Cámara quieta** en el loop (sin deriva; así lo aprobó el usuario). La placa es el cuadro de Klein; H3 corre con
  control = canny de la placa repetido, pero sólo se usa **dentro de las zonas vivas** (humo y las llamas que H3 sí
  anima), con `maskedmerge` y máscaras difuminadas. Canny solo no basta (r1 ≈ v4).
- **Humo** con loop propio de 60 cuadros fundido de punta a punta; **llamas chicas** titilando en post (`velas.py`),
  racimos con fase por píxel.
- **Zonas a mano sobre cada placa** (Klein mueve objetos respecto a la maqueta): un paso por espacio en producción.
- La nave queda con bancas de verdad, muros de tezontle, capillas (Cristo negro, urna con santo yacente, candelero
  de veladoras rojas), Vía Crucis en los pilares y rayo de luna por un ventanal alto. Peso: 417 KB por 5 s a 1080p.
- Pendiente para el 08 (hero → nave): la transición llega a la pose de reposo = la placa; empalmar ahí.
