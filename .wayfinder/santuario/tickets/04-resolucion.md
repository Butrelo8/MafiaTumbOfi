# 04 — Resolución: escalar o generar más grande
Type: task · Status: resolved · Blocks: 05 · Blocked by: — · Assignee: claude

## Question
Llevar los clips de 864×480 a 1080p (escritorio) y a vertical para móvil. Medir sobre los clips de la
prueba 01, lado a lado: RTX VSR (`preset_4k`), FlashVSR (`preset_4k_detail`) y generar en H3 a mayor
resolución. Por cada uno: calidad a ojo, tiempo y peso del all-intra. La decisión se toma con esos datos.

## Datos (2026-10-04)
Clip: nave, cuadros 0–72 del loop crudo de `transicion-4` (864×480, 3 s). Cada candidato → 1920×1080 + LOOK +
x264 crf 23 (el encode web de `montar.sh`). "Cambio" = diferencia media cuadro a cuadro (luma); más alto con
la misma cámara = detalle que tiembla.

| Método | A ojo | Tiempo (3 s) | Peso 1080p, 3 s | Cambio |
|---|---|---|---|---|
| 864 → lanczos (referencia) | blando | — | 435 KB | 0.09 |
| RTX VSR ×2.22 (`preset_4k`) | casi igual a lanczos; afila, no agrega detalle | 32 s | 458 KB | 0.09 |
| FlashVSR ×2 + RTX ×1.11 (`preset_4k_detail`) | el más nítido; **inventa** (letras en el puente de la guitarra, santos rehechos) | 117 s | 1.0 MB | **0.19** |
| H3 a 1280×704 + RTX ×1.5 | detalle real (retablo, cuerdas), estable | 264 s + 32 s | 553 KB | 0.09 |

- **Techo de 12 GB:** H3 a 1280×704 con 260 cuadros (loop de 10 s) = sin memoria. Con 140 cuadros (loop de 5 s
  + 20 de costura) sí cabe: 655 s, se sostiene hasta el final. 864×480 es justo el tamaño que admite 260.
  Las mitades de transición (~35 cuadros) caben de sobra a 704.
- H3 pide ancho y alto múltiplos de 32 (1296×720 falla).
- **Peso:** a 1080p un loop de 10 s sale ~1.5 MB (RTX) / ~1.8 MB (H3 704) / ~3.3 MB (FlashVSR), contra 292 KB
  hoy a 864. Dato para el ticket 05.
- **Móvil:** un recorte 9:16 de la horizontal deja 270 px reales de ancho (864) o 396 (704): no sirve a 1080
  de ancho. La vertical necesita generación propia (1280×704 girado = 704×1280) — eso lo decide el 06.

Assets (en `tmp/`, ignorado): `tmp/resolucion-04/index.html` (A/B, teclas 1–5, `f` = 100 %/ajustar),
`web.sh`, `out/` (crudos), `crop/hoja2_*.png` (recortes al 100 %: RTX | FlashVSR | H3 704).

## Answer
Decidido por el usuario el 2026-10-04 tras ver el A/B: **H3 a 1280×704 + RTX VSR ×1.5 → 1920×1056**, con
**loops de 5 s** (120 cuadros + 20 de costura = 140 generados; ~11 min por loop). Los 10 s de 864×480 no caben
a 704 en 12 GB; el usuario vio el loop de 5 s y lo aceptó. Las mitades de transición también a 1280×704.
FlashVSR queda fuera (inventa detalle y tiembla al doble). Vertical: lo resuelve el 06 con el mismo método.

Al verlo salió otro defecto, no de resolución: el tololoche se lee como "una guitarra gigante" → ticket 12.
