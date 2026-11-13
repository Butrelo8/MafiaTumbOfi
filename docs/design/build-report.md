# A Carretera: tweak bar and build (spaghettidrone, 2026-11-12)

The tweak bar went to the owner, who kept A's defaults. The build is in `src/` and passes every gate below.

## Tweak bar
- Open `docs/design/directions/a-carretera.html?tweak` (from the repo root). Without `?tweak` the page is unchanged, so
  `directions/index.html` still compares A, B and C.
- The knobs are gold hue (70–95) and lightness (62–88%), with live contrast; the bounds come from the logo's bevel
  (`photo_palette.py`). The other knobs are the veil, the title face, name size, night or dusk, and loop or still.
- Title faces: Saira Condensed italic, Saira Condensed upright, and Reddit Sans Condensed 900 (the new `references.md`
  hero row, from urielurbina).
- Dusk frames (`directions/atardecer/`) come from the live three.js scene, not from Cycles. The Blender scene can't
  re-render because `blender/assets/camion/pickup-quaternius.glb` is missing from disk.
- The owner's answer: A's defaults.

## Build
- `src/pages/index.astro` holds the hero, Música, Videos, La banda, Contratación and the footer. All content comes from
  `research/contenido/`, and the contact line comes from SPEC §8.
- The working button and icon live in `src/components/Boton.astro` and `src/components/Icono.astro`, one file each, so
  the buttons-icons pair chain can swap them.
- Fonts are self-hosted with `@fontsource` (Saira, Saira Condensed). Pirata One and Archivo were removed.
- `src/scripts/escena.ts` (the live three.js scene) and the `three` dependency are now unreferenced. They were kept
  because the owner may want the live scene on desktop later.
- `docs/design/DESIGN.md` is rewritten for A, and every element traces to a row in `references.md`.

## Checks
```
revisar.sh web http://localhost:3119/   exit 0, 0 FAIL   (table: docs/design/build-revisar/table.tsv)
  390:  overflow 0 · tap 0 · contrast 0 (text on solid ground) · CLS 0.000 · weight 1.49 MB (≤ 3 MB) · fixed-over-text 0
  1440: overflow 0 · contrast 0 · CLS 0.016 · fixed-over-text 0 · glyphs 0/94 missing · reduced motion: 0 videos playing
slop-check.py src                       0 FAIL; REVIEW kept: js-intersection-reveal (play/pause of the loop, not a reveal)
refs-check.py references.md             all PASS
bun test                                10 pass, 0 fail
```
Not verified by any tool: text over the scene (hero line and contact panel on `--veil`); neither revisar nor
bg-measure measures text over images. States matrix: `check-matrix.py` 0 errors; Components sources: 0 errors.

Mac WebKit pass brief: `docs/queue/2026-11-12-mto-a-carretera-mac-webkit.md`. The `mac-webkit-pass` skill isn't
installed in this environment, so the brief copies the shape of the 11-09 truck brief.
