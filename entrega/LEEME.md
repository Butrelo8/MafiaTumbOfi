# entrega/ — lo aprobado, congelado fuera de `tmp/` (paso 0, 2026-10-13)

`congelar.sh` copia desde `tmp/` y escribe `MANIFEST.tsv` (cuadros, KB, sha256 corto, origen). Todo es de **antes de la
pila** (camino B: G2–G7 lo reemplazan con los mismos nombres). `maestros/` no se versiona (121 MB, ffv1).

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
- **PROVISIONAL — E6, camarín → cripta (2026-10-13):** `escritorio/grupo-ida-provisional-h264.mp4` es Google Flow
  job2 (Veo 3.1 Fast): cuadros 0–184, sin audio, 1280×720 llevado a 1920×1080 con el paso RTX de los loops (×1.5).
  Sus extremos son las placas aprobadas del camarín y de la cripta. **Todavía no está en la web**: «El grupo» y
  «Contratación» siguen en negro y la ida no trae los 20 cuadros crudos del loop. El final se hace con H3 y oclusor de
  máscara y reemplaza este archivo (ticket 07).
- **PROVISIONAL — cripta → atrio (2026-10-13):** `escritorio/contratacion-ida-provisional-h264.mp4` es Google Flow
  job3 (Veo 3.1 Fast): 204 cuadros (8.5 s), sin audio, 1280×720 llevado a 1920×1080 con el paso RTX de los loops (×1.5).
  El cuadro 0 es la placa de la cripta y se funde en Flow en 10 cuadros. El teléfono es el de la placa, pegado sobre su
  propio seguimiento (cuadros 0–79), porque Flow le borra el disco. Flow 172–183 se funde en los cuadros 228–239 del
  loop del atrio y la cola son los cuadros 0–19 crudos de ese loop (`COSTURA` exacta). Pasa por negro (f116–143).
  Va antes del LOOK y de la halación; **todavía no está en la web**. Maestro y números:
  `tmp/07/flow/job3/fix/` (`job3_fix.mkv`, `veredicto.md`).
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
