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
