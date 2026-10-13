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
