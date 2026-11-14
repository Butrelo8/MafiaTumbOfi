# Scene site, phase 1: prop options, the live proof, the phone scrub (2026-11-13, nerddrone)

Brief: mothership `docs/queue/2026-11-13-mto-scenes-build-phase1.md`. Scenes 2–6 are not built.

## A. Prop looks (stills, waiting on the owner's picks)

The contact page is `docs/design/escenas/utileria/index.html`: 7 props × 3 options, 1280×720 Cycles stills, night, with the G63.
Script: `blender/utileria.py` (48 samples, about 18 s per still after a 31 s scene build). References:
`docs/design/references.md` › "Scene props, phase 1 options". Owner answer format: one letter per prop.
- `refs-check.py --sections radio,guantera,calcas,pantalla,portico,placa,caja`: `row-cites-library` FAILs on purpose on the 10
  real-world rows (radio ×3, guantera, calcas, pantalla, portico ×2, placa, caja). The library has no entry for them; the mothership
  agreed to the real-world route (00:41). The other checks PASS.
- `slop-check.py` on the page: all PASS (after replacing one near-black placeholder hex). `revisar.sh` web: every check passes at
  390 and 1440 (weight 1.21 MB, 0 overflow, 0 contrast, 0 targets under 44 px). Output: `revisar/utileria/` (ignored).
- Not final in any option: Windows fonts stand in for the lettering. The grey square on each sticker marks where the platform's
  official glyph goes, unaltered and upright. The rear screen shows the empty state ("Muy pronto"). Héctor is hidden in the
  glovebox stills; Alexandro and Diego are hidden in the bed stills (v3 seats them in the bed; the plan puts them in the rear seats).
  Stickers and bed views carry a camera-side fill light (storyboard note 4); the scene will need it.
- Weakest: stickers B and plate B (gold on black reads dim at night); bed C's bulb string drifts outside the bed.

## B. Live three.js vs the v3 Cycles frames: verdict **undecided**; a fixed port is the next measurement

The proof is `lab/vivo/index.html`, served from the repo root. It loads the camera rail (the `transicion.py` `CAMINO` +
`muestra()` port, Blender → three axes, lens → vertical FOV) driven by scroll with damping. The world streams at 19.2 m/s.
The GLB comes from `blender/vivo.py` → `tmp/vivo/vivo.glb` and stays out of git (it carries the Tripo figures):
```
GLB 1.71 MB (Draco, WebP images ≤ 1024 px; KTX2 not done, toktx is not installed)
truck 667,516 → 77,989 tris; figures 29,100 / 29,100 / 29,100 / 29,099 tris; scene total 196,188 tris
SSIM (gray) live vs Cycles, 1280x720:  f0 0.252   f96 0.857   f191 0.670
WebGL in headless Chromium on WSL: SwiftShader (11 fps at 1280x720) or llvmpipe; no GPU, so no real fps number here
```
Side by side: `docs/design/escenas/vivo/lado-a-lado.jpg` (Cycles on the left; f0, f96, f191).
- f0 (the cab, scene 1's held shot) fails by eye and by number. The windows render as flat white panes, not glass. The 29k-tri
  heads facet in a 20 mm close-up. The point lights stand in for the Cycles area lights and leave a hot dome spot.
- f96 (outside) is close: same road, framing and guardrail phase. The lamp-post light pools and the orange glow are missing.
- Why undecided and not fallback: two of the f0 failures are defects in this port, not limits of three.js.
  - The exported glass did not translate. It needs an override by material name: transparent, low opacity, `depthWrite: false`.
  - The pole `SpotLight`s, the lamp emissive and the additive puddles of `src/scripts/escena.ts` were not ported.
  - The point lights are not energy-matched to the Cycles area lights.
  - Only the faceted heads are a real budget finding: at 29k tris, collapse decimation is not enough for a 20 mm close-up. The
    fix to try is a retopo plus a normal bake.
- Next: fix those three defects, then re-capture with `ARGS= node lab/vivo/capturar.mjs …`. Compare with
  `revisar.sh vivo-fNNN.png --ref f_0NNN.png`. Get an fps number on a real GPU from the page's own readout in a real browser.
  If f0 still fails after that, the verdict is fallback.

## C. Phone scrub of the v3 move (540×960, 24 fps)

Measured by `lab/scrub/medir-scrub.mjs` on `lab/scrub/index.html` in Playwright Chromium: 390×844 @2x, CPU 1× and 4×, the
clip held in a blob URL. Full table: `lab/scrub/resultados-2026-11-13.tsv`; the clips are git-ignored and rebuilt with the
commands in its header.
```
clip                     MB (10^6)     seek p50/p95 @4x CPU   overtaken seeks   frames shown/s
-g 6, B-frames (g6b)     0.973  13.1 / 36.4 ms          3 / 240           41.1
-g 6, -bf 0 (g6)         1.031   8.4 / 16.5 ms          1 / 240           49.0
-g 240 (control)         0.776  39.8 / 98.6 ms        128 / 239           21.0
```
`-g 6` holds the scroll: about 1 overtaken seek in 240, against more than half for `-g 240`. The budget's MB is 1,048,576 bytes
(`scripts/medir-peso.mjs`: `MB = 1024 * 1024`; research C31). In that unit g6 is 0.984 MB and g6b 0.928 MB, so both fit. The plan's
"0.93 MB" was g6b. Recommendation: **g6 (-g 6, -bf 0)** for the moves; it has half g6b's p95 (16.5 vs 36.4 ms at 4×). Still to do: the Mac WebKit pass and a real phone; Chromium on desktop is not a phone.
