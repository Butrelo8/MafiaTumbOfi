# 16 — Loops de 10 s en todo el santuario
Type: prototype · Status: resolved · Blocks: 09 · Blocked by: — · Assignee: claude

## Question
El 15 eligió para la nave de escritorio un loop de 10 s con H3 nativo (260 cuadros a 928×512, 40 pasos, `tmix`, RTX ×2).
¿Pasa a ser el largo de todos los loops (vertical y los demás espacios), o sólo de la nave? Si sí:
- **Vertical:** a qué tamaño corre H3 (lados múltiplos de 32 y cuadros × MP ≈ 127 para caber en 12 GB, p. ej. 512×928)
  y con qué escalado llega a la resolución de móvil (hoy 704×1280 sin RTX, ticket 06).
- **Velas y polvo** con periodo 240 en vez de 120 (`velas.py`, `polvo.py` con N=240 y el paso de NR de DLSS que hoy
  viene horneado): ¿se nota que ciclan cada 5 s dentro del de 10 s, o basta con dejarlos así?
- Peso contra el presupuesto del 05 (escritorio: 383 KB por 10 s) y tiempo de producción por loop (~17 min de H3 +
  RTX).

Método y números: `tmp/micro/NOTAS.md` § "Loop de 10 s con movimiento real"; visual-lab `comfyui/playbooks.md` ›
*Web loop on a locked-off plate*, paso 5.

## Avance (2026-10-10)
- **Alcance, decidido por el usuario:** 10 s en **todos** los loops, escritorio y vertical, en todos los espacios.
  Queda por resolver aquí cómo: tamaño de H3 en vertical y periodo de velas y polvo.
- **Velas y polvo a 240** (`tmp/micro/largo/capas240/`, `comparar.sh`; sin NR ni LOOK, sólo para elegir tempo, placa r6):
  `velas.py` y `polvo.py` usan ciclos enteros por loop, así que con N=240 y los mismos ciclos van **a media velocidad**,
  y con el doble exacto el loop de 240 sería el de 120 dos veces. Tres columnas en `sbs_hoy_lento_rapido.mp4`: hoy
  (120 ×2), lento (240, mismos ciclos) y rápido (240, ciclos ~2× no todos pares). Medido en la franja de los haces:
  paso por cuadro 0.060 / 0.031 / 0.049; cuadro t contra t+120: 0 / 1.15 / 1.15 (hoy se repite exacto a los 5 s).
  Motas: escritorio `0.62 260` (reproduce exacto el polvo aprobado), vertical `0.33 90`; `comparar.sh` ya usa 260. **No hace falta correr el NR otra vez:** el NR
  va sólo en la placa fija y las capas se llevan como `placa_NR + (cuadro − placa)` (visual-lab
  `comfyui/dlss5-video-2026-10-09.md`, *Plate-first*); `placa_real.py` ya lo hace con cualquier largo de loop. **Pendiente: que el usuario elija tempo.**
- **H3 vertical de 10 s** a 512×928 (`tmp/movil-06/largo/reconstruir_10s_v.sh`, prompt `prompt_calmo_v.txt`): cabe en
  12 GB, 1064 s de H3 + 77 s de RTX ×1.375 → 704×1276 (se escala a 704×1280), `tmix` 1-2-1. Contra el de 5 s nativo a
  704×1280 (`h3viva06`), crudos, en la zona del humo (`comparar_v.sh`, `sbs_5s704_vs_10s512.mp4`, `humo_30_200.jpg`):
  - ritmo: humo 0.68 por cuadro contra 1.23 (más calmado, como pidió el usuario); cadencia pareja (1 salto > 2× el
    vecino contra 6; 2 cuadros casi repetidos contra 0);
  - **pero** más blando (Laplaciano 569 contra 1402) y con un **velo gris** sobre el retablo dentro de la zona del humo:
    al componer sólo esa zona sobre la placa, el velo se vería como una mancha. Si se sigue por aquí, igualar luz y
    contraste del H3 contra la placa dentro de la máscara antes de componer. **Pendiente: que el usuario lo vea.**
- **Elegido por el usuario (2026-10-11):** velas y polvo **rápido** (240 cuadros, mismo tempo que hoy, sin repetirse a
  los 5 s); vertical de 10 s con el H3 a 512×928, **igualando el velo** contra la placa dentro de la máscara.
- **Velo igualado** (`igualar_velo.py`: mapa afín por canal, ajustado en lo quieto de la máscara contra el cuadro 0 de
  la base que queda alrededor, `nave_real.mkv`; error 15.7 → 12.5) y loop vertical de 10 s armado con la cadena v5
  (`armar_10s_v.sh`, base provisional `nave_real.mkv` ×2 con velas y polvo de 120): `nave10_igual.mp4` 272 KB (sin
  igualar 279; el de 5 s 197), costura 0.45 (v5 0.42), humo 0.32 por cuadro con 4 saltos (v5: 0.33 con 14). Tras el foco
  de lente la blandura del H3 a 512 casi no se nota; el retablo dentro de la zona del humo queda algo más gris que en
  v5. Lado a lado v5 | sin igualar | igualado: `sbs_v5_crudo_igual.mp4`, recorte `velo_cmp.jpg`.
  Medido con honestidad: el mapa afín (ganancia ~0.75, desplazamiento ~+24) dice que el H3 tiene **más** contraste que
  la base, no un velo levantado; lo que queda gris es el H3 redibujando el retablo, y eso un mapa por canal no lo arregla.
  Además baja las llamas de la bocina (L p99 225 en v5 → 213). Alternativa sin probar: componer sólo lo que **se mueve**
  del H3 (cuadro − mediana temporal, sumado sobre la placa), así el retablo dentro de la zona del humo sale de la placa.
- **Sólo lo que se mueve** (`movil-06/largo/montar_mov_v.py`): la zona del humo queda de la base y se le suma la
  desviación del H3 respecto a su mediana temporal; las llamas de la bocina se reemplazan enteras. Retablo de la placa
  (sin el gris del H3), llamas L p99 224 (v5 225), humo 0.34 por cuadro con 1 salto (v5: 0.34 con 14). Defecto visible al
  100 %: donde el humo se aparta de su mediana la desviación es negativa y deja bordes un poco oscuros en la columna.
  Arreglado a pedido del usuario: sólo se suma la parte que aclara (`humo_pos.jpg`: antes | ahora); vertical 276 → 262 KB.
- **Reconstruido con velas y polvo de 240 "rápido"** (`tmp/micro/largo/capas240/construir.sh`, ~15 min, sin ComfyUI):
  escritorio con micro `r7_micro_10s_240.mp4` (354 KB; el de 120 ×2, 383), vertical `nave_10s_240.mp4` (262 KB con el humo sólo aclarando).
  Cuadro t contra t+120: escritorio 0.43 → 1.02, vertical 0.45 → 0.89 (ya no se repite a los 5 s); costuras 0.40 y 0.47.
  Lado a lado: `capas240/sbs_escritorio_120x2_vs_240.mp4`, `capas240/sbs_vertical_v5_igual_mov240.mp4`, recorte `velo3.jpg`.

## Answer
Decidido por el usuario el 2026-10-11 (cerrado a su pedido; el último montaje vertical lo revisa al verlo):
- **10 s en todos los loops**, escritorio y vertical, en todos los espacios: 240 cuadros + 20 de fundido = 260 de H3.
- **Escritorio:** H3 nativo a 928×512, 40 pasos, prompt calmado, `tmix` 1-2-1, RTX ×2 (el 15).
- **Vertical:** H3 nativo a 512×928 (1064 s), RTX ×1.375 → 704×1280, `tmix`; del H3 sólo lo que se mueve en la zona del
  humo, sólo la parte que aclara (el retablo sale de la placa), y las llamas enteras. Igualar color por canal no basta: el H3 redibuja el retablo.
- **Velas y polvo de 240, "rápido":** mismo tempo que el de 120 con ciclos que no se repiten a los 5 s (`velas240.py`,
  `polvo240.py` con `RAPIDO=1`; motas 260 escritorio, 90 vertical). El NR no se vuelve a correr: las capas se llevan
  sobre la placa real con NR (`llevar.py`).
- **Peso:** 354 KB escritorio y 262 KB vertical por 10 s, dentro del presupuesto del 05. Tiempo por loop: ~18 min de H3
  + ~1.5 min de RTX + ~7 min de CPU.
- Queda fuera: el parpadeo de la brasa del micro sigue con periodo de 120 (`micro_viva.py`); el micro en la vertical va
  con el 06; las transiciones con el 17.
