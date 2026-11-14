# Handoff: scene site phase 1, round 2 (owner's prop picks 2026-11-13 02:51)

From nerddrone (branch `cc/nerddrone`, worktree `/mnt/e/Cursor Projects/MTO-nerddrone`). Phase 1 results: `docs/design/escenas/fase1.md`.
I stopped here because context was past the mothership's 30 % line. Nothing in round 2 is started.

## How to run what exists
- Stills: `blender/utileria.py`. Each option is one `@opcion("name")` builder that returns (pos, look-at, lens). Run:
  `/mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/utileria.py)" -- "$(wslpath -w "/mnt/e/Cursor Projects/MTO/blender/escena.py")" "$(wslpath -w tmp/utileria)" 48 <name,name|all> 1280x720 > tmp/utileria/<log> 2>&1`
  with `run_in_background`. Point escena.py at the **main checkout**: the assets live there. Expect a 31 s build, then about 18 s per still. Convert each still with
  `ffmpeg -i x.png -q:v 3 docs/design/escenas/utileria/x.jpg`. The contact page is `docs/design/escenas/utileria/index.html`.
  Serve it with `python3 -m http.server 3108 --bind 0.0.0.0 -d docs/design/escenas/utileria` (the URL is http://thiccpc-wsl:3108/; port 3100 is taken).
- Probe points in utileria.py: `TABLERO` (centre stack, y 1.045 z 1.40), `GUANTERA` (2.14, 1.234, 1.28), `PORTON`, `DEFENSA`.
  The figures are hidden while casting (`FIGURAS`). Blender's stdout is block-buffered into the log: watch for its "Saved:" lines.
- Live proof: `blender/vivo.py` writes `tmp/vivo/vivo.glb`, which stays out of git because it carries the Tripo figures. Serve the repo on localhost with
  `python3 -m http.server 3107 --bind 127.0.0.1`. Capture with `node lab/vivo/capturar.mjs http://127.0.0.1:3107/lab/vivo/ tmp/vivo/frames`.
  The Cycles frames are `/mnt/e/Cursor Projects/MTO/blender/render/transicion/v3-1280x720/f_0NNN.png`.
- Gates before showing: `refs-check.py` (10 real-world rows FAIL by agreement), `slop-check.py` and `revisar.sh` on the page dir.

## Picks and the work they need
1. **Radio → an infotainment touchscreen** (all three options rejected). The dash screen shows the cover and title, ‹ › steps through
   the 9 releases in `catalog.json`, and "Escuchar" is an on-screen button. The cassette goes. The Tecla dash key stays only if
   it sits naturally beside the screen. Two variants:
   - (a) a floating wide screen on top of the dash, MBUX-style;
   - (b) a screen built into the centre stack where the G63's small COMAND unit sits (top centre in `radio-*.jpg`).
   The screen face is an image texture (cover + title + ‹ › + Escuchar). Make it with PIL (`uv run -q --with pillow python -I`)
   from `public/music/*.jpg`, in DESIGN.md type and colours, with no pill button.
   **References first:** 2024–26 dashboards (G-Class MBUX, Ram 1500 Uconnect 14.5", F-150 SYNC 12" or similar), photo URLs as new
   `radio` rows in `references.md`. Replace the three old radio rows and mark them rejected.
2. **Glovebox C, door cut from the truck mesh.** Find the G63 dash faces in a box around `GUANTERA` (bmesh: faces whose centres
   lie in x 1.95–2.35, y 1.15–1.30, z 1.15–1.38; check the result by eye). Separate them into their own object and set the origin
   on the lower edge, so the hinge axis is X. Rotate the door about 70°. Fill the opening with a dark inner box that meets the cut
   edges, so there are no gaps or stretched faces. Check the edges in a close still before the junk goes in.
   Replace `guantera_abierta()`, which today is a box slab and not a cut.
3. **Stickers mixed:** use A/B/C styles across the four (for example IG die-cut, Spotify round badge, YouTube bumper strip, TikTok
   die-cut), with different ages (one faded or scuffed) so they read as collected over time. Keep the §2 rules: the official glyph
   unaltered, upright, outside the peel. This one is not in the mothership's re-render list (1, 2, 6, 7); render it only if cheap.
4. **Pantalla móvil C** and 5. **Green signs B:** picked, no re-render. Record both in `DESIGN.md` › Components with their
   references rows.
6. **Plate A, matched to the current official Veracruz plate.** Sources: the Gobierno de Veracruz / SEFIPLAN reemplacamiento
   announcement (2025–26 issue), and NOM-001-SCT-2-2016 (placas metálicas: size, typeface, layout). Cite each in `references.md`.
   **Flag to the mothership before rendering an exact copy:** the state seals, the QR and the exact layout of an official plate
   may count as imitating an official document. Our text replaces the number. Recommend a clearly stylised version (official
   colours and layout, no seals and no QR) unless the mothership clears it.
7. **Bed props A, fuller and composed:** keep the donut, cooler and piñata. Add props (for example a beach ball, balloons tied to
   the roll bar, a second inflatable, maracas, a small speaker, a sombrero). Compose them as a pyramid, peaking at the piñata, with
   one strong silhouette against the road. Readability is judged from the **scene-2 camera** (`T.CAMINO[-1]`, the v3 f191 framing),
   not from the closer `VISTA_CAJA` used in round 1. Render both. Alexandro and Diego stay hidden: in the plan they ride in the
   rear seats.

Two variants each where the pick leaves room (1, 6, 7; 2 if the cut has a choice). Put them on the same contact page, then stop for the owner.

## Live port fixes (in parallel)
- **Glass:** in `lab/vivo/index.html`, after loading, override the window materials: `transparent: true`, opacity about 0.15,
  `depthWrite: false`, dark tint. Find their names with `vidrios()` in `blender/transicion.py`, or log `mesh.material.name`.
- **Pole lights and puddles:** port from `src/scripts/escena.ts`: the per-tramo `SpotLight` on the two nearest poles, lamp
  emissive at 6 when `P.postes.encendidos`, and the additive `charcoTex()` puddle planes. The tramo objects are already in `mundo`.
- **Energy match:** `transicion.luces_interior` uses area lights (dome 4 W, dash 25 W, bed 90 W). Swap the point lights for
  `RectAreaLight` (needs `RectAreaLightUniformsLib.init()`), then tune against Cycles f0.
- Re-capture f0, f96 and f191. Measure with `revisar.sh tmp/vivo/frames/vivo-fNNN.png --ref <cycles f_0NNN.png>` and with ffmpeg SSIM
  (round 1: 0.252 / 0.857 / 0.670). Rebuild `docs/design/escenas/vivo/lado-a-lado.jpg` with `vstack=inputs=3`.
- Get an fps number on a real GPU. Headless WSL Chromium is SwiftShader or llvmpipe only, so open the page in a real browser
  (its readout shows the GPU name and fps).
- Still open after the fixes: the faceted heads at 29k tris. Try a retopo plus a normal bake.

## Done-check
`bun run build` and `bun test` (19 pass at handoff), plus the gates above. Report as the mothership briefs.
