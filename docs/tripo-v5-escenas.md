# The Tripo v5 cast in the scenes (caughtdrone, 2026-11-18)

Owner, 11-18 08:22: "change the 3d figures we have on the scenes for the tripo ones and render them as they is"; 08:24:
"also the band scenes, not just the truck". Spec: `~/projects/mothership/docs/queue/2026-11-18-mto-tripo-cast-swap-render.md`.

## What was in frame before
Nothing imports `blender/reparto.py`. The figures in the run, the loop and the six page-stop scenes were:
- manager, Héctor and Alexandro: `transicion.py` `figura()` (the old Tripo GLBs in `blender/assets/reparto/`, a 13-bone
  procedural rig posed by `sentar()`, moved to the rear seats by `utileria.asientos_traseros()`);
- Diego: colddrone's interim clip (`sitting_drinking`, `mx` under `diego_raiz`), placed by `montaje.diego_interino()`.

## How the swap works
`blender/reparto_v5.py`, called at the end of `montaje.montar_reparto()`, so `ruta.py` (run and loop) and `montaje.py`
(montaje-esc1..6) both get it. Each Tripo rig (apedrone's `reparto-v5/<name>/rig/tripo-out/*/model.fbx`, copied to
`blender/assets/reparto-v5/<name>/rig.fbx`, git-ignored) is scaled by `cast_alturas/cast.json` and driven live by the figure
it replaces:
- Hips: Copy Location to the driver's hip point (plus the Tripo Hips' height above its hip joints);
- every mapped bone: Damped Track toward an empty 10 units past the driver bone's tail (direction, whatever the lengths);
- forearms: IK (chain 2) to the driver's wrist, or to caja5's fist bone `puno_n` when it exists (Héctor's water).
The drivers stay animated and hidden from render (`ocultar_dobles()` from `viejo_diego()`), so the NLA cycles, Diego's
ping-pong, caja5's grip search and the ray probes run unchanged. Nothing is baked.

## Stand-ins (no Tripo seated clips exist yet)
- Poses: the old stand-ins' procedural poses and colddrone's Diego clip, retargeted by direction. Twist is not carried.
- Alexandro's left hand ends 25 mm short of the stand-in's wrist (arm reach); Héctor's right hand 6 mm.
- Hand tattoos (apedrone's decals) are not applied: at 640×360 and 960×540 they are under a pixel.
- caja5's grip search now sees the Tripo meshes in its rays: Héctor's fist turns +65° instead of +50° (CAJA5 MANO, PASS).
- Not re-rendered (superseded builders, buggyship 08:4x): storyboard.py, escena.py `transicion`, the utileria/caja* pick
  rounds. vivo.py's live GLB: no page loads it (`src/scripts/escena.ts` reads `/escena/escena.glb` from escena.py and is
  itself unreferenced), so it was skipped.

## Measured
```
heights (rest, m)      manager 1.199  hector 1.204  alejandro 1.250  diego 1.250     (owner's: 1.20 / 1.20 / 1.25 / 1.25)
head room under roof   manager +0.085 hector +0.070 alejandro +0.038 diego +0.083
hand -> driver wrist   manager 0/4 mm  hector 6/0  alejandro 0/25  diego 0/0       (right/left)
drink gap to mesh      hector bottle body 4-6 mm   diego bottle 6 mm
ruta.bake.json         unchanged (camera untouched); RUTA CHOQUES 0, HOLGURA min 0.104 m (same as before), ASOMADOS 0
cost                   bake step 94 s -> 550 s per build; render 2.9 -> 3.4 s/frame at 64 spp, 640x360
```

## Render, encode and check (oopdrone, 2026-11-18)
caughtdrone's Blender died with it at run frame 0833 (cc-deck ended the session while it rendered). oopdrone rendered the rest
with `RUTA_DESDE=834 RUTA_HASTA=1103` (same settings as `scripts/render-ruta-cycles.sh`). Blender then failed once, writing 0983
over the WSL share (`Render error (No error) cannot save`, a 0-byte PNG); that file was deleted and 983..1103 re-rendered.
Run: 1104 frames 0000..1103, none missing, none under 50 kB. Loop 1127..1607 from caughtdrone's earlier pass (481 f, complete).
Encoded with the script's own ffmpeg lines (24 fps, 640×360, crf 26): `public/prototipo/ruta.mp4` (1104 f, 3.8 MB, g 3),
`bucle.mp4` (480 f, 1.5 MB, g 4) and the two `-f0.jpg` posters; copies and revisar folders in `~/cc-out/mto-tripo-v5/{mp4,revisar}/`.
```
GPU while rendering   mean 29.8 %, max 98 % (40 samples at 0.5 s; bursts per frame, the rest is the CPU: denoise, file write)
eagle.sh bucle.mp4 --loop   seam 4.66 (<= 20.25) pass; strobe 0 runs pass; exit 0
revisar ruta.mp4            strobe 0 runs pass
handover (mean abs diff, 0-255)
  run 647 -> loop 1127      1.39    (the real handover: ruta.json bucles[0] desde 647; a normal step is 1.4-4)
  run 743 -> loop 1223      0.93    (the loop's own 96th frame against the run's 743)
  run 1103 -> loop 1127     56.3    (literal last-vs-first; not a handover, the run goes on past the band station)
  loop 1607 -> loop 1127    1.64    (wrap frame against the first)
resume seam 833 -> 834      8.84    (steps 826..842 run 6.5-9.0, so no discontinuity); 982 -> 983 2.76 (steps 2.5-3.3)
```
Not verified: eagle-eye (off by default; no FAIL to explain). The loop's events f301/f442 are "jump" infos from revisar.
