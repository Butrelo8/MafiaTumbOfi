# entrega/ — lo aprobado, congelado fuera de `tmp/` (paso 0, 2026-10-13)

`congelar.sh` copia desde `tmp/` y escribe `MANIFEST.tsv` (cuadros, KB, sha256 corto, origen). Todo es de **antes de la
pila** (camino B: G2–G7 lo reemplazan con los mismos nombres). `maestros/` no se versiona (121 MB, ffv1).

- **Nombres:** los de los prototipos web (`nave`, `ida`, `vuelta`, `sacristia`) + códec. `vuelta` = `ida` al revés.
- **Maestros sin pérdida:** ida de escritorio (`ida_master_mezcla.mkv`; el AV1 de la vuelta es su reverso, SSIM igual
  que la ida, 0.963) e ida vertical (`cod/ida_master.mkv`; su H.264 crf 23 es byte a byte `ida_micro.mp4`). Loop
  vertical: rehecho con `halacion.sh` `VC=ffv1` sobre `nave_micro240_dof.mkv` (SSIM 0.990 contra el aprobado). **Loop de
  escritorio sin maestro** (`esc240_dof.mkv` se borró); reconstruible con `tmp/micro/largo/capas240/construir.sh`
  (las entradas siguen en `tmp/`), pero G6 lo rehace igual.
- **Faltan para el paso 4:** vuelta de escritorio en HEVC/H.264, vuelta vertical en AV1/HEVC, loops en AV1/HEVC.
- **Rosa (defecto del 2026-10-10, "still missing pieces"):** no está. Medido en los 240 cuadros dentro de la máscara de
  la rosa: escritorio L* media 15.2, |ΔL| contra la placa 2.0 constante (ningún cuadro abre huecos); vertical entera en
  todos los cuadros, más oscura (L* 5.6) por el grado y el foco, no por huecos. Para G5: la rosa vertical queda bastante
  más oscura que la de escritorio.
