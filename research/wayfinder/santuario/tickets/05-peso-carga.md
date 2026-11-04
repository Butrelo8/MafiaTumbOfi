# 05 — Presupuesto de peso y estrategia de carga
Type: grilling · Status: resolved · Blocks: 09 · Blocked by: 04, 11, 13 · Assignee: claude

## Question
`scripts/check-budget.sh` ya marca 4.6 MB contra 3 MB, sin contar video. Con los pesos reales del ticket 04:
¿qué se carga al entrar y qué se difiere por espacio? ¿Qué códec (AV1 / H.264, iPhone sin AV1)? ¿Se sube el
techo o se recorta material?

## Datos (2026-10-05)
- Hero hoy: 2.5 MB AV1 1080p / 2.7 MB H.264 720p (16 s); vertical 1.5 MB AV1 / 2.4 MB H.264.
- Loop de la nave r6 (5 s, 1080p), recodificado desde el H.264 crf 23 (`tmp/peso-05/`): H.264 406 KB, **AV1 crf 40
  305 KB** (SSIM 0.994), **HEVC crf 26 246 KB** (SSIM 0.988), H.264 a 720p 251 KB (0.979).
- Transición a 1080p (estimada, no hay ninguna aún): con movimiento ~3× los bytes por segundo de un loop quieto
  (a 864 la ida de 3.3 s pesaba lo que un loop de 10 s) → ~820 KB H.264 / ~620 KB AV1 cada ida o vuelta.
- Visita completa escritorio AV1, sólo hacia adelante: 2.5 + 5 × 0.62 + 5 × 0.3 ≈ 7.1 MB; con vueltas ≈ 10 MB.
- `check-budget.sh` suma los cuadros de `scene.json` (arquitectura vieja, 4.8 MB): ya no mide nada vigente.

## Decidido (ronda 1, 2026-10-05)
1. **Presupuesto por ventana, medido en navegador real:** entrada ≤ 3 MB y cada gesto ≤ 1 MB en móvil; escritorio
   informa. Sin techo para la visita completa. `scripts/medir-peso.mjs <url>` (playwright global, CDP
   `dataReceived`, ventana de calma de 3 s desde cada gesto). Validado contra `tmp/transicion-4/web/`: entrada
   1.03 MB = los 4 videos que ese prototipo precarga (1.09 MB en disco).
2. **Fluido siempre:** nunca corte directo por falta de archivo (sólo con `prefers-reduced-motion`). Detalle en
   la ronda 2.
3. **Códecs AV1 → HEVC → H.264.** En México pocos traen iPhone 15 Pro o posterior (único con AV1 en Safari); todos
   los iPhone desde el 7 decodifican HEVC por hardware y HEVC pesa ~40 % menos que H.264. H.264 queda de último
   recurso. Un `<source>` por códec, con `codecs=` (`av01…`, `hvc1…`, `avc1…`); el hero también gana su HEVC.
4. **Hero sin cambios** (16 s); se revisa con el tiempo.
5. **Se retira la arquitectura vieja** (cuadros de `public/scene`, `scene.json`, `check-budget.sh`) con el 09.
6. **Móvil a 720×1280.**
7. **Sin modo de ahorro de datos ni de conexión lenta:** la experiencia completa siempre (decisión del usuario: filtra
   prospectos). `prefers-reduced-motion` se queda: es accesibilidad, no peso.

## Decidido (ronda 2, 2026-10-05)
8. **Saltos del menú (1 → 5): fundido a negro de ~0.6 s** y se llega al loop destino, sin encadenar transiciones.
9. **Gesto antes de que esté lista la precarga: espera** y la transición arranca cuando puede reproducirse entera,
   con un aviso de que está cargando. Por ahora un placeholder (la línea roja bajo el número del menú se llena); su
   diseño final va con Figma en el 10.
10. **Cascada:** al estar listo lo inmediato (ida + loop de la siguiente, vuelta de la actual) se sigue bajando todo
    el sitio en orden. La página marca el arranque con `<html data-precarga="cascada">`; el medidor cuenta como
    entrada sólo lo de antes y la cascada aparte, sin techo.

Medidor ajustado (`scripts/medir-peso.mjs`): red simulada 4G (9 Mbps, 40 ms) para que la marca caiga a tiempo,
sondeo cada 50 ms. Prueba con una copia del prototipo que marca la cascada al tener el primer loop
(`tmp/peso-05/web/`): entrada 0.40 MB (loop de la nave, 0.29 MB, más ~0.1 MB que Chrome pide antes de la marca; no cambia con el sondeo), cascada 0.59 MB.
**Ojo:** con red lenta `preload="auto"` no baja los videos completos (0.98 de 1.14 MB): la cascada tiene que bajarlos
con `fetch` → `blob:` para garantizar que cada transición esté entera antes de usarla.

## Answer
Resuelto con el usuario el 2026-10-05. **Experiencia completa siempre, fluida siempre:**
- Presupuesto en navegador real (`scripts/medir-peso.mjs`): en móvil **entrada ≤ 3 MB** (hasta la marca de cascada) y
  **gesto ≤ 1 MB**; la cascada y el escritorio informan. Estimado de entrada en móvil con AV1: hero 1.5 MB + ida y
  loop de la nave a 720p ~0.5 MB ≈ 2 MB.
- **AV1 → HEVC → H.264** por cada video, un `<source>` por códec (HEVC por los iPhone anteriores al 15 Pro).
  Escritorio 1920×1056, móvil 720×1280. Hero sin cambios (16 s).
- **Carga:** lo inmediato primero, luego cascada de todo el sitio en orden por `fetch` → `blob:`. Un gesto que llega
  antes espera con aviso de carga (placeholder → Figma en el 10); los saltos del menú cruzan con fundido a negro de
  0.6 s. Corte directo sólo con `prefers-reduced-motion`. Sin modo de ahorro de datos ni de conexión lenta.
- Se retiran `public/scene`, `scene.json` y `check-budget.sh` con la integración.

Consecuencias:
- **09 integración:** cargador con cola (inmediato → cascada) por `fetch`/`blob:`, marca `data-precarga`, espera del
  gesto con aviso, fundido para saltos, `<source>` AV1/HEVC/H.264, `medir-peso.mjs` en lugar de `check-budget.sh`.
- **10 acabado UI:** diseñar el aviso de carga (hoy placeholder).
- **Producción:** cada loop y transición se codifica tres veces (AV1 crf ~40, HEVC crf ~26 con `-tag:v hvc1`,
  H.264); calibrar los crf con el primer espacio terminado.
