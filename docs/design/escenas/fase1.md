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

## B. Live three.js vs the v3 Cycles frames: verdict **fallback (clips on desktop) for scene 1 and the 1→2 move**

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
- Why this is a fallback and not a no: this was a plain PBR port with no lightmap bake. What would flip it is a baked cab
  interior, glass as a simple transparent material, figure LODs from a retopo plus a normal bake instead of collapse
  decimation, and an fps number on a real GPU. That is a phase of its own, not measured here. The frame numbers on the page
  (`?f=0`) read out the GPU name and fps, so a real browser gives the number.

## C. Phone scrub of the v3 move (540×960, 24 fps)

Measured by `lab/scrub/medir-scrub.mjs` on `lab/scrub/index.html` in Playwright Chromium: 390×844 @2x, CPU 1× and 4×, the
clip held in a blob URL. Full table: `lab/scrub/resultados-2026-11-13.tsv`; the clips are git-ignored and rebuilt with the
commands in its header.
```
clip                     MB     seek p50/p95 @4x CPU   overtaken seeks   frames shown/s
-g 6, B-frames (g6b)     0.973  13.1 / 36.4 ms          3 / 240           41.1
-g 6, -bf 0 (g6)         1.031   8.4 / 16.5 ms          1 / 240           49.0
-g 240 (control)         0.776  39.8 / 98.6 ms        128 / 239           21.0
```
`-g 6` holds the scroll: about 1 overtaken seek in 240, against more than half for `-g 240`. Only the B-frame encode fits the
1 MB budget (0.97 MB), at twice the p95 of the no-B encode. Recommendation: g6b for the moves. If WebKit stutters, use no-B at
crf 24 to get back under 1 MB (not encoded). Still to do: the Mac WebKit pass and a real phone; Chromium on desktop is not a phone.
