# Stickers r1 picks: calca3() decals (2026-11-15)

Owner picks, relayed by mothership at 04:02, prepared in the format `blender/calcas_arte.py` writes (02e07ce lineage).
Nothing in the scene or the Blender scripts was changed, and nothing was committed. The owner does the placement.

- `<id>.png`: RGBA at 4 px/mm (`PX`), with a die-cut WHITE vinyl border and cut line from `troquel()` (imported from
  `calcas_arte.py`, not copied), plus the same transparent margin as the 16 existing stickers.
- `<id>-n.png`: the raised-edge normal map from `normal()`.
- `calcas3.json`: a **fragment** with the same keys calca3 reads: `w`, `h` in metres (full canvas), `acabado`, and
  `glifo: null`. The integration branch merges it into the `calcas3.json` the scene loads; nothing has been written there.
- `fuentes.json`: each decal's source, native px/mm, scale and note. `hoja-picks.jpg`: one page, overview only.

| id | pick | source | finish | why this source / finish |
|---|---|---|---|---|
| r1-slogan | S01 | gemini/G01-a.png (×0.57) | brillo | owner named G01; the chrome is printed, and mat3 `cromo` would turn the whole decal metal, white rim included |
| r1-arriba | S02 | krea s22 (×1.23, 290 mm) | brillo | first choice in the report; s11's blackletter X reads as a P |
| r1-x-holo | S03 | krea s22 (×1.21) | holo | owner named Krea s22. The rainbow is baked in, so with the thin film on top it may look oversaturated; A6 uses a silver field for that reason (test in the render) |
| r1-gallo | S06 | gemini/G06-a.png (×0.77) | brillo | first choice for the gallo in the report |
| r1-corazon | S09 | gemini/G09-a.png (×0.70) | brillo | owner named G09 |
| r1-bubu | S13 | krea-fix s11fix (×1.27, 210 mm) | brillo | the FLUX 3 fix removed the dot that read as a period; s11fix has more pixels on the art than s22fix (664 vs 613 px) |
| r1-placa | S18 | vector (Saira Condensed, `letras` incl=0, `estrella` n=5) | brillo | rebuilt so the lettering is exact; the look follows krea s22 |

Raster cut (`../picks.py`): outside = dark pixels connected to the frame; rim = a 3 px band plus the light pixels
connected to it (for Gemini, lum > 100 also takes the grey drop shadow on its rim); art = silhouette minus rim. Then RGB
is resampled with Lanczos (with its background) and the mask separately, so no dark halo. Upscales stay at 1.27× or less;
no AI upscaler, since those redraw text.

```
picks_check.py   7/7 OK: RGBA, w/h == px/PX, keys {w,h,acabado,glifo=null}, acabado in brillo/mate/holo/cromo, id not in
                 the existing 16, -n.png same size, one alpha piece, no holes, light rim (2nd pct lum >= 180), clear margin
ocr.py on the decals flattened on dark (picks/ocr/)
                 PASS: S03 (no text), S06, S18
                 EYE-OK at 1:1 (OCR can't read 40 px gold / blackletter / curved text; not verified by tool): S01, S02, S09, S13
```
Rebuild: `uv run -q --with numpy --with pillow --with opencv-python-headless python -I picks.py && … picks_check.py`.
