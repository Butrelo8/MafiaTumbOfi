# entrega/ — lo aprobado, congelado fuera de `tmp/` (paso 0, 2026-10-13)

`congelar.sh` copia desde `tmp/` y escribe `MANIFEST.tsv` (cuadros, KB, sha256 corto, origen). Todo es de **antes de la
pila** (camino B: G2–G7 lo reemplazan con los mismos nombres). `maestros/` no se versiona (1.7 GB desde el 07, ffv1).

- **Nombres:** los de los prototipos web (`nave`, `ida`, `vuelta`, `sacristia`) + códec. `vuelta` = `ida` al revés.
- **Maestros sin pérdida:** ida de escritorio (`ida_master_mezcla.mkv`; el AV1 de la vuelta es su reverso, SSIM igual
  que la ida, 0.963) e ida vertical (`cod/ida_master.mkv`; su H.264 crf 23 es byte a byte `ida_micro.mp4`). Loops de
  la nave (G6): `halacion.sh` `VC=ffv1` sobre `tmp/g6/<f>/dof240.mkv`.
- **Faltan para el paso 4:** vuelta de escritorio en HEVC/H.264, vuelta vertical en AV1/HEVC, loops en AV1/HEVC.
- **Rosa (defecto del 2026-10-10, "still missing pieces"):** no está. Medido en los 240 cuadros dentro de la máscara de
  la rosa: escritorio L* media 15.2, |ΔL| contra la placa 2.0 constante (ningún cuadro abre huecos); vertical entera en
  todos los cuadros, más oscura (L* 5.6) por el grado y el foco, no por huecos. Para G5: la rosa vertical queda bastante
  más oscura que la de escritorio.
- **G5 (2026-10-13):** los trozos que faltaban eran de la cabeza del micro, no de la rosa: la máscara cortaba la cúpula
  bajo la rosa en los dos formatos. Arreglado en `placas/*-g5*` (ticket 06, bullet G5); los loops de aquí siguen con el
  corte hasta que G6 los rehaga.
- **G6 (2026-10-13):** `escritorio/nave.mp4` y `vertical/nave.mp4` son los loops de 10 s sobre las placas G4 con el
  micro de G5; escritorio con el copal real (`placas/nave-esc-g6-copal-*.png`). Ticket 06, bullet G6.
- **Tallo y rosa (2026-10-13, después de G6):** los dos loops se rehicieron con el tallo de espinas enrollado en el cable
  y la luz C (igualada al micro de oro): `placas/nave-esc-micro.png` es ya `g5/placa_micro_tallo.png`, con sus máscaras,
  la vertical y las disparidades en `placas/*-tallo*`. Mismo fondo y mismo H3 que G6; costura igual (0.75 / 0.51).
- **E5 y E6 provisional con LOOK + halación (07, 2026-10-14; OK del usuario 00:35).** Todo pasó por el mismo LOOK y
  la misma halación que la nave y la sacristía, con **`vignette=PI/5:dither=0`**, porque el dither por omisión no es
  determinista por cuadro (`tmp/07/look/armar.sh`, `veredicto.md`; queda ~0.5 de luma más oscuro). Escalera
  `tmp/07/look/escalera07.sh`: H.264 crf 23, HEVC crf 26, AV1 crf 40; GOP 240 en los loops y 60 en las transiciones.
  - **Loops (10 s, 240 cuadros), escritorio y vertical:** `vestidor` (El grupo), `cripta` (Contratación), `atrio`
    (Cierre). `<lugar>.mp4` es H.264 (como `nave.mp4`) y `<lugar>-hevc.mp4` y `<lugar>-av1.mp4` son los otros
    peldaños. Las verticales del vestidor y la cripta son un recorte del escritorio con look, como la sacristía; la del
    atrio lleva grade propio (su neblina baja sólo existe en la vertical). Maestros: `maestros/{esc,vert}-<lugar>.mkv`.
  - **PROVISIONAL — las dos idas son Google Flow (Veo 3.1 Fast), sólo escritorio (Flow no da 9:16; la vertical cruza
    por negro).** `vuelta` = `ida` al revés, AV1/HEVC/H.264.
    - `escritorio/grupo-{ida,vuelta}-*.mp4`, camarín → cripta = Flow job2, 185 cuadros, 1920 desde la salida RTX
      ×1.5. **Sin `COSTURA` en ninguno de los dos sentidos:** la ida termina en la cripta según Flow (contra el cuadro
      20 del loop: media 3.7, 12 % de píxeles > 8) y la vuelta en el camarín de antes de las placas de producción
      (contra el cuadro 20 del loop del vestidor: media 27.5, 54 %). No se inventa costura: en la web este cambio
      cruza por negro hasta que el E6 final (H3 con oclusor de máscara) reemplace estos archivos con el mismo nombre.
    - `escritorio/contratacion-{ida,vuelta}-*.mp4`, cripta → atrio = Flow job3 con el teléfono arreglado
      (`tmp/07/flow/job3/fix/veredicto.md`), 204 cuadros, pasa por negro (f106–147). **Ida: `COSTURA` exacta** (la
      cola son los cuadros 0–19 del atrio con look, byte a byte en el maestro). **Vuelta: no exacta.** Termina en la
      placa de la cripta (0.000), no en los cuadros 0–19 del loop; al seguir en el cuadro 20 el salto es de media 0.80
      (3.4 % de píxeles > 8, sólo en velas y polvo).
    - Maestros: `maestros/esc-{grupo,contratacion}-ida.mkv`. Las anteriores `*-ida-provisional-h264.mp4` (sin look)
      se retiraron.
- **G7 (2026-10-13):** las idas y vueltas de los dos formatos son las del 17 rehechas sobre la nave con la gente (placa
  G4; escritorio con el copal real del loop) y el micro con el tallo nuevo; la mitad de la sacristía es la del 17
  (profundidad idéntica desde el corte). Ticket 17, sección G7; cadenas `tmp/g7/{esc,vert}/armar.sh`.
- **Sacristía, escritorio (paso 1, 2026-10-13):** `escritorio/sacristia.mp4`, loop de 10 s sobre la placa real s3 (Klein
  4 MP con el tono del NR de s11) con un aplique de latón bajo el cuadro (fuente del charco de luz). Se mueve: el disco, el
  polvo en la luz, la lámpara de mesa (±9 %), el aplique (±4 %) y el neón; sin H3, ciclos enteros en 240. La ida de
  escritorio (`ida-*`, `vuelta-av1`) es la de G7 con el aplique pegado en su mitad de la sacristía y los últimos 12 cuadros
  fundidos al loop: su último cuadro es el cuadro 0 del loop. Cadena `tmp/sac10/esc/armar.sh` + `tmp/sac10/empalme.py`.
- **Sacristía, vertical (paso 2, 2026-10-13):** `vertical/sacristia.mp4` es un recorte 9:16 del loop de escritorio
  (x 1020, ancho 900 de 1920, a 704×1280) con una banda oscura abajo (34 %): el mismo cuarto y el mismo movimiento. La
  ida vertical (`ida-*`, `vuelta-*`) es la nave de G7 hasta el cuadro 29 y la sacristía de escritorio recortada igual
  desde el 30 (negro del jambaje en las dos); su último cuadro es el cuadro 0 del loop. Sustituye a `sacristia-5s.mp4`.
  Cadena `tmp/sac10/vert2/armar.sh`; ticket 16.
