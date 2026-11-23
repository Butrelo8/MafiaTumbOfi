Copied 2026-11-22 from `/home/black/projects/visual-lab/docs/reviews/2026-11-22-project-specific-gotchas.md`: MTO clauses only, verbatim, grouped as in source; `(?)` = ambiguous (generic lesson, MTO example).

### from `blender/blender-notas.md`
- blender/blender-notas.md:1034 — Ray-cast camera search inside a cab: a cheap framing filter before the slow visibility test, ranked by what the rays see, not by lens. (?)
- blender/blender-notas.md:1034 — A removal box that exempts one material ("keep the headliner") also keeps that material's faces on the removed part: bound the exemption by height and list what it kept. (?)
- blender/blender-notas.md:1034 — Decimating a material soup left 1.15-1.5 m triangles coplanar with the headliner and which material won the depth test flipped between exports (pale wedge in the hero frame): delete decimated faces with all corners in the covering surface's plane and an edge over 0.4 m after checking the cover with up/down rays. (?)
- blender/blender-notas.md:1035 — - **glTF for a three.js page:** a prop built with `parent=False` "floats" live (three.js sways the truck root) but not in Cycles: any glTF root outside the swaying node floats;
- blender/blender-notas.md:1035 — reparent every root on the truck and assert the GLB roots, excluding reparented props from the body box that route tests use.
- blender/blender-notas.md:1035 — a prop group baked into the truck's per-material meshes cannot be toggled: attach its meshes (by material name) to a new Group added to the rigid set before the scene merge, then `.visible` works (+1-2 draw calls when shown).
- blender/blender-notas.md:1039 — Cameras on the cab roof looking down were all blocked by the roof edge: a grid search (clearance + sight line) found free spots only at window height just outside the glass;
- blender/blender-notas.md:1039 — the cab leaves only front-left spots for a rear-bench figure.
- blender/blender-notas.md:1039 — A ray between camera positions misses the moving world (slides 0.8 m/f): shift the ray start by the world's motion and ignore hits inside the static truck volume.
- blender/blender-notas.md:1043 — exec'ing a chain script into `globals()` clobbers your own globals (`MODO`, `F` crashed `caja3`): prefix scratch globals with `_`. (?)
- blender/blender-notas.md:1043 — A fresh worktree lacks `blender/assets/camion|reparto|reparto-v5|utileria` and `tmp/utileria|fuentes` (junctions via `powershell.exe New-Item -ItemType Junction`, since `cmd mklink` fails through WSL quoting; copies for the rest).
- blender/blender-notas.md:1048 — A RANSAC circle + "tube r 15 mm" fit of a steering wheel in a merged truck mesh describes only the rim's centre line (the real cross-section near the grip is far thicker: radial −59..+34, normal −47..+19 mm).
- blender/blender-notas.md:1053 — Workbench drew a windshield opaque because glass was a face material on a mixed object and `pase_wb` hides by first material: delete faces whose material name starts with vidrio/mica (bmesh);
- blender/blender-notas.md:1053 — a Workbench pass with glass deleted hides a camera crossing through the windshield (no tint or reflection change): name the crossings to the reviewer and check them in Cycles.
- blender/blender-notas.md:1059 — Cycles 16 spp smears brows/glasses of figures seen through the windshield (error vs 64 spp 2.43, 32 spp 1.96) and 32 spp costs the same as 16 here (1.5 vs 1.6 s/frame): use 64 (2.9 s/frame; a 481 f loop took 980 s). (?)
- blender/blender-notas.md:1064 — `montaje`/`utileria` render the options in registration order, not the order on the command line: don't read progress from your own list.
- blender/blender-notas.md:1065 — - **Framing and cast:** Tripo-rigged figures have cartoon proportions (head top 0.67-0.75 × height above the Hips bone in rest pose): derive seated cab clearance from the mesh top minus Hips z, not from the 0.52 × stature rule.
- blender/blender-notas.md:1069 — Setting `obj.location` then reading `matrix_world` gives the old transform: `view_layer.update()` before reading bound boxes (else the offset is applied twice and the prop lands off the truck). (?)
- blender/blender-notas.md:1070 — A close-up camera placed relative to the prop landed inside the dash and rendered black: check the camera position against the cab before a batch;
- blender/blender-notas.md:1074 — - **Cycles cost and crawl:** 1080p cab frames took ~28 s at both 24 and 48 spp: the time was OIDN denoising (per 72 frames: 96 spp raw 406 s, OIDN 2169 s, OptiX 438 s);
- blender/blender-notas.md:1074 — Full-mesh textured Diego renders read ~2× revisar crawl vs the decimated rig on the same motion: compare crawl only between renders on the same rig. (?)
- blender/blender-notas.md:1074 — The "texture bug" of a Diego lab render = `rig_fit`'s 40k decimation + Workbench/AgX: full mesh via Data Transfer weights (`rig_full.py`), Standard view transform.
- blender/blender-notas.md:1076 — `scene.ray_cast` follows `hide_viewport`, not `hide_render`, and `utileria` hides finished options with `hide_render`: sync `hide_viewport` to `hide_render` (and re-evaluate the depsgraph) before a probe, restore after. (?)
- blender/blender-notas.md:1076 — `utileria.py all` renders every older option, the destructive glovebox cut included: always pass the explicit option list;
- blender/blender-notas.md:1076 — `caja3.py`'s `vaciar_caja` also hides Alexandro and Diego (rear seats): override it to hide only `estuche_`/`guitarra_`.
- blender/blender-notas.md:1076 — A side ray that misses the truck returned a hit 670 m away as the "mirror": bound hits to 1.02 < |x−CX| < 1.5;
- blender/blender-notas.md:1076 — one downward ray at the G63 6×6 bed wall hit 1.97 m (another part): sample across the wall's thickness;
- blender/blender-notas.md:1076 — probing the interior mirror with forward rays from the top down hits the headliner edge first: take the contiguous run of solid hits in front of the glass and use its middle;
- blender/blender-notas.md:1076 — the G63 interior shares one mesh and material, so a mirror zone by object+material covered 43 % of the frame: define interior zones by position (a box around a probed point).
- blender/blender-notas.md:1076 — Bed-scale papel picado (24×30 cm panels) strung across the cab ceiling blankets the windshield from the 20 mm cab camera: strings along the ceiling sides, panels 8×10 cm.
- blender/blender-notas.md:1081 — - **Sticker/decal on a body:** a sticker grid ray-cast per vertex onto a car body slips through mesh seams and hits the cab 1.1 m behind (holes/dark squares): floor the hits ~12 mm under the median surface;
- blender/blender-notas.md:1082 — the Sketchfab G63 6×6 (DJS) already has the factory roof-spoiler lamp pockets (materials mica/cromo, unlit): probe them and fill them with lamps instead of floating an aftermarket bar over the visor.
- blender/blender-notas.md:1082 — A per-pixel ray probe stops at the windshield, so props behind glass never count as covering the road: keep stepping through hits whose material is glass (up to 3) and attribute the first prop hit. (?)
- blender/blender-notas.md:1082 — A plan line "looking back-left from the driver's mirror, the driver's window in the right of frame" is geometrically impossible on an LHD truck: render both readings and let the owner pick;
- blender/blender-notas.md:1082 — a camera 6 m out beside a truck in `escena.py` lands beyond the guardrail (x 5.0) and fills the bottom as a grey slab: raise it to 2.6 m and look over it.
- blender/blender-notas.md:1088 — - **Probes:** `scene.ray_cast` from inside a car cab hits the seated figures: `hide_viewport` on the figures and re-evaluate the depsgraph before casting;
- blender/blender-notas.md:1092 — - **Night cab (Cycles):** the interior of a closed car at night reads black through refractive glass: thin transparent glass + small motivated practicals (dome 4 W, dash 25 W) inside the cab;
- blender/blender-notas.md:1092 — area lights under a cab roof show as white panels in a taller 9:16 frame: `visible_camera = False` on practical lights.
- blender/blender-notas.md:1092 — The Sketchfab G63 6×6 windshield and rear window are opaque charcoal sheets (no glass material): find panes by flatness (≥ 85 % area facing one way) + fill ratio in the window band, measured along the car's own axes (a `nrm.orthogonal()` box with arbitrary in-plane axes inflates the box and missed every pane), and give them thin Transparent+Fresnel glass.
- blender/blender-notas.md:1092 — Emptying `escena.py` REPINTAR to read source material names breaks `separar_ruedas` (needs the "goma" tyre material): keep the tyre remap, clear the rest.
- blender/blender-notas.md:1092 — `blender/escena.py` fails with "Please select a file" in `import_scene.gltf` in a worktree: `blender/assets/` is untracked, copy or re-download the truck GLB first.
- blender/blender-notas.md:1093 — Exec'ing `escena.py` to reuse its scene: strip the bare trailing `main()` and set `__file__` to the main checkout so ASSETS resolve.
- blender/blender-notas.md:1102 — Sketchfab G63 windows: thin Transparent+Fresnel Glossy glass;
- blender/blender-notas.md:1102 — MTO veil-from-luminance method: guard with the contrast of the dimmest text over the object's brightest pixel.

### from `web/build-notes.md`
- web/build-notes.md:120 — one scene with two trucks offset along X hides one in the side views: two viewports (`setViewport`/`setScissor`) sharing one camera pose, one truck visible per pass.
- web/build-notes.md:132 — A fresh worktree needs MTO's scene prerequisites regenerated (`blender/calcas_arte.py`, `blender/placa_veracruz.py`; the art is random so a sticker differs slightly).
- web/build-notes.md:142 — **Small**: the MTO weight budget's "MB" is MiB (`medir-peso.mjs` MB = 1024·1024): state the unit next to any size;
- web/build-notes.md:166 — slop-check.py counts radial-gradient glows in CSS only (gradients written in TS template strings are invisible to it: grep `src/scripts` by hand) and on a coastveracruz.com URL returns HTTP 403 (curl the HTML and run it on the file); (?)

## Restored but project-only (from the audit)
- MTO, `docs/gotchas-from-visual-lab.md`: inbox 1622 — `git add -A blender` stages the Windows junctions `blender/assets/camion` and `reparto` as files: stage by explicit path.
