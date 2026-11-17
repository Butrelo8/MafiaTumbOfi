# MTO: the whole site as one moving 3D scene: motion plan (downbaddrone, 2026-11-16)

Spec: `~/projects/mothership/docs/queue/2026-11-16-mto-motion.md`. Earlier draft: `~/cc-out/mto-pantalla/3d/motion-plan.md`
(the owner's correction at its top: every page stop is a moving shot, and the camera moves continuously between stops,
with no cuts). This file covers steps 1 and 2, and the owner's answers that start step 3.

## Owner's answers (2026-11-16 06:02, relayed by buggyship)

1. **No holds.** Every section keeps moving: the truck drives, the world slides, the camera drifts even inside the cab,
   and character animations keep playing. Section to section is one continuous move, and Gira is a transition move.
2. **Option A:** the road is straight in the moving clips.
3. **Yes:** `src/lib/ruta.ts` and its parity test land with step 3.
4. **About 3 s of continuous motion per section** in the preview, with nothing frozen.
5. **Signs:** "La X we" only on the signs that point to Xalapa. Every other sign names real places on México 140,
   westbound from about 19.438 N, 96.690 W (Cerro Gordo).

What changed from the proposal below:
- There are no holds and no idle loops. The run is one path through timed points (`src/lib/ruta.json` `camara`), sampled
  by a cubic Hermite with tangents taken over frame time.
- Sections are frame ranges on that path (`secciones`).
- The world never wraps: the road is built 7 periods ahead (`RUTA_PERIODOS=7`), so the roadside's lack of periodicity
  stops mattering.
- The section signs stand in the world, `adelante_m` ahead at frame 0.
- `alta` (9:16) framings are left for later.

Real places, as road distances from OSRM on OSM data from Cerro Gordo (queried 2026-11-16):
- Dos Ríos 12.5 km;
- El Lencero 16.0 km;
- Las Trancas 21.1 km;
- Xalapa 26.1 km (the city's first exit).

The road3 guide sign now reads "La X we 26 km". A new distance board, `camino_letreros.tablero`, at y 270 lists
Dos Ríos 12, El Lencero 16 and La X we 26. The section gantries carry MÚSICA (Cerro Gordo 1 km), VIDEOS (Dos Ríos 12 km)
and LA BANDA (El Lencero 16 km).

## 1. How the page consumes the scene today

- The shipped page (`src/pages/index.astro`) shows one poster and one pre-rendered Cycles loop (`#loop`, an mp4 at
  1600×900 and 720×1280) in the hero only. `src/scripts/loop.ts` plays and pauses it. The page has no stops and no camera.
- `src/scripts/escena.ts` is a live three.js scene with a two-point eased camera move between the four `paradas`. It is
  **unreferenced** since the A Carretera build (`docs/design/build-report.md:22`), and it is built on the old pickup GLB.
  Those four stops (alta, cabina, lado, cenit) frame the old pickup, not the G63 and pantalla móvil scene.
- The current scene (G63, the four figures, pantalla móvil, road3 fog and signs) exists only in Blender and Cycles. Nobody
  has exported a GLB of it.
- The approved scene plan (`escenas-plan.md` §1 and §3) gives the moves two consumers:
  - desktop: a live three.js camera rail driven by scroll, with pre-rendered clips as the fallback if the lightmap bake
    fails the look;
  - phone: pre-rendered moves scrubbed by scroll, plus idle loops at each stop.
- **Consequence:** the moves are rendered now, for the phone and the fallback. They must also be reproducible live later.
  So the path is **data that Blender keys from**, not keyframes exported out of Blender.

## 2. Reference: what we match and what we change

The stop framings and their references are the approved holds in `blender/utileria.py`:
- 2: Collateral 004;
- 3: owner pick 3B;
- 4: owner pick 4B;
- 5: Drive 014;
- 6: Collateral 028.

The 1→2 move is the approved v3 move (`transicion.py` `CAMINO`).

We match the car-mount grammar of those films: the camera rides the vehicle, the road and the lamps stream through every
frame, and the camera has a small amount of mount vibration.

We change one thing on purpose: those films cut between setups, and here every change of setup is one continuous camera
move. The gantries still pass overhead at the end of a move, and on the phone the gantry is where one clip hands over to
the next.

## 3. Shared path source

**File:** `src/lib/ruta.json`, a sibling of `escena.json`.
- `escena.json` keeps the world sizes and presets.
- Its old `paradas` stay untouched until the page is rewired, because `escena.ts` still reads them.

**Conventions:**
- Axes are escena.json's three.js axes: Y up, the truck faces −Z. Blender converts them with `escena.b()`.
- The lens is in mm on a 36 mm horizontal sensor, the same as utileria (`sensor_fit = HORIZONTAL`). The page derives its
  vertical fov from the aspect: `fov = 2·atan(18 / (mm · aspect))`.
- Every pose has two framings, `ancha` (16:9) and `alta` (9:16), because `toma(ancha, alta)` uses different positions.
  The portrait lens goes through `v(mm)`, which keeps 75 % of the horizontal angle.

```jsonc
{
  "fps": 24, "periodo": 240,                       // world period: 192 m per 240 f (escena.json mundo)
  "paradas": [                                     // holds, in page order
    { "id": "cabina", "seccion": "inicio", "fr": 72,
      "ancha": { "pos": [..], "mira": [..], "mm": 20 }, "alta": { .. },
      "deriva": { "pos": [0.04, 0.02, 0.03], "mira": [0.05, 0.03, 0], "ciclos": [1, 2] },   // periodic drift, integer cycles per 240 f
      "vibra":  { "grados": 0.12, "ciclos": [29, 47, 83] } }                                  // sum of sines: loops, and Python = TS
  ],
  "movimientos": [                                 // between consecutive holds
    { "de": "cabina", "a": "caja", "fr": 192,
      "puntos": [ { "u": 0.21, "ancha": { "pos": [..], "mira": [..], "mm": 18 }, "alta": { .. } } ] }  // inner control points
  ],
  "actores": [                                     // anything that moves besides the camera, keyed on the same clock
    { "id": "pantalla", "pistas": [ { "t": "caja>pantalla", "u": [0, 1], "y": [-18, 1.6] } ] },
    { "id": "portico_videos", "pasa": { "t": "caja>pantalla", "u": 0.92 } },
    { "id": "flash", "en": { "t": "placa", "fr": 60 } }
  ]
}
```

**Sampler, written once in each language, about 30 lines each:**
- Inside a move, the path is uniform Catmull-Rom through the points `[hold A, inner points…, hold B]`, the curve
  `transicion.py` already uses. The parameter is `u = smoothstep(t)` with `t ∈ [0, 1]`.
- A hold's pose is its base pose plus `deriva` and `vibra`, which are sums of sines with integer cycles per 240 frames.
- Both are periodic, so a hold is a seamless idle loop, and noise is not needed.
- A move starts and ends at the base pose. Each hold's offsets are zero at frame 0 of its 240-frame loop.
- The page maps scroll progress to `t`, and Blender maps frames to `t`.

Blender side: a new `blender/ruta.py`.
- It reads `ruta.json` and keys the camera on every frame from the sampler. `transicion.py` does the same through `muestra()`.
- It keys the actors.
- After it keys, it writes `ruta.bake.json`, which holds `matrix_world` and the lens per frame, read back from the camera
  as rendered.

Page side: `src/lib/ruta.ts`. It is pure, with no three.js import, and it needs the owner's OK.

**Parity check, done-check for step 3:** `bun test src/lib/ruta.test.ts` samples `ruta.ts` at every baked frame and
compares the result with `ruta.bake.json`. The tolerance is 1 mm in position and 0.05° in rotation.

## 4. The run: stops, moves, motion

Stops follow `escenas-plan.md` §1. They are mapped to the page's five sections as a **proposal; the owner decides.**

| # | Stop (hold, from) | Page section | Hold motion | Move to next (frames, from) |
|---|---|---|---|---|
| 1 | cabina (`CAMINO[0]`, 20 mm) | inicio | drift forward 4 cm, mount vibration | v3 move: through the windshield, up, settles behind the bed (192, `CAMINO`) |
| 2 | caja (`esc2-abre`, 28 mm) | música (stickers = platforms) | slow crane ±10 cm | drops into the gap; pantalla overtakes left; VIDEOS gantry passes (144; via `esc2-fin`) |
| 3 | pantalla (`esc3-hombro`, 24 mm) | video | lateral sway ±6 cm; pantalla rides level ±0.3 m | pantalla eases ahead; the camera rounds the rear corner and dollies forward on the passenger side; LA BANDA passes (144; via `esc3-fin`) |
| 4a | costado (`esc4-cabina`, 24 mm, passenger side) | integrantes | 6.2 m track, ±8 cm bob | over the roof to the driver's side (96; via an apex 2 m over the roof) |
| 4b | costado-conductor (`esc4-fin`) | integrantes, 2nd half | same | climbs onto the hood; pantalla is back ahead (120) |
| 5 | gira (`esc5-abre`, 30 mm) | none today | over-the-hood bob | pantalla exits; the camera overtakes and turns to face the truck (144; via `esc5-fin`) |
| 6 | placa (`esc6-abre`, 32 mm) | contacto | backwards travel ±5 cm, headlight flash at the end | end |

Preview length:
- 7 holds of 72 frames each, plus 840 frames of moves.
- That is about 1344 frames, or 56 s.
- The final hold loops are 240 frames, one world period, and render separately after the run.

## 5. What has to change in Blender

1. **A periodic world, so the run can be any length and the holds loop.**
   - road3's roadside is random over the length `Y0..Y1 = −384..768 m` (`camino_edificios.py`, seeded once), while
     `mundo` wraps every 192 m. A 10 s loop pops at the wrap, and a 56 s run (1075 m) drives off the end of the built road.
   - Fix: generate one 192 m period of the roadside and copy it, as `camino_mx140` already does with `copias`. The lamps
     (64 m) and the glints (32 m) already divide 192.
   - The section gantries leave the periodic world and become one-shot `actores`.
   - Cost: about half a day.
2. **One timeline instead of per-option rebuilds.**
   - The montaje rebuilds the dressing for each option, and two options are destructive: `esc6-flash` boosts the lamp
     material, and glovebox C cuts the G63 mesh.
   - `ruta.py` builds the union once: bed caja5 'elegida', the stickers, the pantalla, placa3, the cast and Diego.
   - It keys visibility per segment: bed off for 5 and 6, as `cama=False` does today. It keys the flash as an emission
     and spot energy curve.
   - Glovebox C stays out.
   - Cost: about a day.
3. **Motion blur on** (`motor()`'s shutter 0.5); the stills had it off.
4. **Depth of field:** postponed to the finals. It costs samples, and the preview is for timing.

## 6. road3's curve versus the sliding world (the owner decides)

The bend is a fixed remap of the built geometry (`camino_curva.py`). It holds for a still only: when `mundo` scrolls, bent
objects slide straight. Whatever is chosen must also work on the page's endless stream and in the idle loops.

| Option | What it looks like | Blender cost | Page (live) cost |
|---|---|---|---|
| **A. No bend in the moving clips** (recommended for the preview) | straight México 140; the stills keep their bend | none | none |
| B. Treadmill bend: the bend is re-applied every frame after the slide, so the road always turns 40 m ahead | the road ahead always bends away and never arrives; fine over 3–5 s, odd if a visitor idles | a frame-change handler that remaps origins, plus a GN deform on the long meshes: about 1 day | a curved-world vertex shader: small |
| C. The truck drives a real curved road (the world stands, the truck and camera follow a path) | physically true | a new road layout, no periodic loops, the holds cannot loop | the page has to stream a long road: large |

## 7. Step 3 order, after the OK

1. Run `ruta.py`, then a **Workbench render of the whole run** at 640×360 to check timing: minutes on the GPU, sent as a
   frame strip.
2. **Cycles at 16 spp**, 960×540, with `denoising_input_passes=RGB` (road3's fog fix) and motion blur.
   - Measure 10 frames first and send the projected GPU minutes before launching.
   - road3 stills took about 25–31 s each, including the build, so the full run could take hours.
   - If the projection is more than about 90 min, render at 12 fps and frame-double for the preview only.
3. Run `eagle.sh` on the preview mp4 (revisar exits 0) and make a frame sheet.
4. Run the parity test.
5. The 64 spp finals and the 240-frame hold loops come after the owner sees the preview.

## Open questions

1. Stop list and mapping: is it the seven holds above? Gira has no page section yet, so it could be a pass-through move
   with no hold. The old `paradas` (alta, cabina, lado, cenit) would retire once the page is rewired.
2. The curve: option A for now, or B?
3. Page code: may `src/lib/ruta.ts` and its test land with step 3? It is a pure sampler, with no change to `index.astro`
   or `escena.ts`. Without it, the parity check waits for the page work.
4. Preview hold length: 3 s per hold, or longer?

All four were answered on 2026-11-16; see "Owner's answers" at the top.

## Step 3 as built (2026-11-16)

**Files:**
- `src/lib/ruta.json` is the run. It has 25 timed camera points, 5 sections, the vibration sines, the pantalla's track,
  the signs and the flash.
- `src/lib/ruta.ts` is the page's sampler.
- `src/lib/ruta.test.ts` checks that the path passes through every point and matches Blender within 1e-3.
- `src/lib/ruta.bake.json` is written by Blender.
- `blender/ruta.py` builds the scene, keys it, bakes and renders. Its docstring has the command.
- Run one Blender at a time, and run `~/.claude/scripts/gpu-busy` first, in its own command.
- After each bake, run `bun test src/lib/ruta.test.ts`.
- `RUTA_RENDER=0` keys and bakes on the CPU in about 1 min; give it the `GPU=0` prefix.
- `RUTA_PASO`, `RUTA_DESDE` and `RUTA_HASTA` set the frame step and range.

**Measured:**
- Bake: 610 frames.
- `RUTA CHOQUES 0`: a ray from each camera position to the next hits no surface except glass.
- Workbench, 640×360, every 2nd frame: 180 s.
- Cycles at 16 spp, 960×540, with persistent data: about 1.8 s per frame, measured on 10 frames.
- The world slides 976 m over the run, and the road is built 1344 m ahead (`RUTA_PERIODOS=7`).

**What the build changes:**
- The section signs are `portico_b` children of `mundo`, so they slide with the world.
- The pantalla is one empty keyed every frame.
- road3's chevrons are hidden, because they belong to the bend.
- The bed light `luces3` is left out: it is a fixed fill that would sit in the fog.

**Two path fixes found by the ray check:**
- Plain finite-difference tangents let the fast fly-forward pull the slow gira section backwards, into the roof (frames
  1003 and 1012). The samplers now use monotone tangents.
- The v3 points at frames 112 and 144 sit 12 cm left of the centre line, so the camera passes beside the hanging
  strawberry instead of through it.

**A worktree needs the untracked inputs before the first run:**
- Windows junctions (`cmd.exe /c mklink /J`) for `blender/assets/camion` and `blender/assets/reparto`. A WSL symlink is
  invisible to Windows Blender.
- Copies of `tmp/fuentes` and `tmp/utileria`.

**Open after the preview:**
- The pantalla's wheels don't turn.
- Whether Diego's clip keeps playing past its last key is not checked.
- The 9:16 `alta` framings.
- The page wiring: `escena.ts` → `ruta.ts`, and video scrubbing per section.
- The 64 spp finals.

## Owner notes 06:40 and what changed

> "the top of the hair is coming out of the truck, and also a more manageable scene for when the band section is on is
> on the inside of the truck. Camera position sitting on the hood pointing at the inside of the truck"

**The hair.**
- `ruta.py` `asomados()` runs every 24 frames. From each figure's top vertices (up to about 300 per figure and frame), it
  casts a ray straight up, passing through the figures themselves (60 hops). A vertex whose ray meets no truck surface
  within 1.5 m is outside the cab.
- The first run found Alexandro's stand-in at z 2.288 under a ceiling at 2.187: 6758 vertices out at frame 36.
- `encoger("alejandro", 0.04, 0.92)` lowers him 4 cm and scales him 0.92 about the hip, through the armature only.
- After that, the check finds 2 vertices of `Body` out at the passenger front window (x 2.51, y 0.56, z 1.84,
  frame 312): shoulder height at the window, not the roof. Not fixed.
- Diego's bottle showed as out only while the ray hop limit was 6. That was a false positive.

**The band section.** Integrantes (frames 647–743) is now the camera on the hood, looking back into the cab through the
windshield. It slides 30 cm across the hood with a slight push, and the world streams through the side windows.
- The move in from the screen-truck section runs forward along the gap on the driver's side and rounds the front corner.
  LA BANDA passes at frame 575.
- The move out rises off the hood, turns left, then forward to gira.
- The run is now 1104 frames (46 s); contacto is frames 1031–1103, with the flash at frames 1070–1088.
- `RUTA CHOQUES 0` and the parity test pass (552 baked frames).

## Preview (2026-11-16 08:31)

The preview is Cycles at 16 spp, 640×360, every 2nd frame, with the 552 frames doubled to 24 fps, 46 s long. It is in
`~/cc-out/mto-pantalla/3d/ruta/preview/`:
- `ruta-preview.mp4` (24 fps);
- `ruta-preview-12fps.mp4` (the checked file);
- `hoja-preview.jpg` (every 32 frames, labelled with frame and section);
- `revisar/`.

Cost: 657.7 s on the GPU. The 66-frame sample measured 1.1–1.2 s per frame in every section once ComfyUI had freed its
VRAM. While ComfyUI held about 9 GB next to Blender, the same frames took about 26 s each.

`eagle.sh` exits 0 and has no FAIL row:
- strobe passes;
- dark is 83 % (a night scene; info only);
- it lists 6 events.

At run frames 1072 and 1086, the events are the headlight flash, as planned. At 774 it is the lit shopfront sweeping in on
the right turn off the hood. At 96 it is a wipe: the camera passes a rear passenger's head at a few centimetres, because
the 12 cm sidestep around the strawberry starts at frame 112 and pulls the path toward Alexandro. The fix is to stay
centred to about frame 100 and sidestep after that. 394 and 592 (the screen truck sweeping in, the front corner) were not
stripped.

Seen by eye, not measured:
- Frames 800 and 960 (the right turn off the hood and the fly-forward) look onto a dark verge, so they are weak frames
  inside moves.
- From the hood only the manager and Héctor read; the rear two are hidden behind them.

## Band loop (2026-11-16, breaddrone → validdrone)

Spec: `docs/handoffs/2026-11-16-movimiento-banda-loop.md` (the owner's 3-move loop). While the page sits on integrantes,
the camera loops through three moves instead of running on. Scrolling leaves the loop and hands over to the run.

**References, matched shot by shot:**
- Move 1: Collateral 023/029 (the hood mount, looking in).
- Move 2: Collateral 007 (the side window at night). Its key pose is variant n2a.
- Move 3: Collateral 014 (front-seat shoulder in the foreground, rear passenger beyond). Its key poses are n3-inicio and
  n3-fin.

Rejected variants:
- m3a: the strawberry fills the lens.
- m2b and n2b: the seat backs and the window top cut the heads.

**Data:** `src/lib/ruta.json` `bucles[0]`. Its fields are `desde` 647, `hasta` 743, `largo` 240 and `clip` 1127, plus 9 loop
points (t 124–229), each with a `nota`.
- Loop frames t 0–96 *are* the run's frames 647–743, the hood slide (move 1). Entering or leaving anywhere in move 1 is
  jump-free.
- Moves 2 and 3 are one Hermite from the run pose at 743, through the loop points, back to the run pose at 647. Its end
  tangents are the run's own, so both handovers and the wrap are C1 by construction. The test prints the velocities.
- `largo` must be a **multiple** of 240, not a divisor, because vibra uses 29, 47 and similar cycles per 240.
- `clip` ≡ `desde` (mod 240), so the world, vibra and cast phases at the loop clip match the run at 647.

**Scroll exit (default, decided 09:04):**
- In move 1, the run takes over directly.
- In move 2 or 3, scrolling drives the loop clock in the scroll's direction until it is back on move 1, and the run takes
  over there. There is no blend through metal.
- 1 scroll frame = 1 loop frame (`paso(estado, df, dt)` in `ruta.ts`).

**Code:**
- `ruta.ts`: `tangentes()` is split out of `hermite()` (which takes optional end tangents), and `orientar()` out of
  `muestra()`. New: `bucle(t)`, `bucleInfo`, `paso` and `poseEstado`.
- `blender/ruta.py` mirrors the sampler and `bucle()`. It keys the loop at 1126–1367, with one pad frame each side.
  `ruta.bake.json` gets `bucle`.
- `RUTA_PREVIA=<ticks.json>` renders the page's own stepping, one still per tick.

**The cast loops** (`reparto_en_bucle()`):
- The 3 stand-ins repeat their action's frames 0–80 on the NLA, an 80-frame sway.
- Diego's Mixamo clip is re-anchored on his seated hips at frame 210 and ping-pongs frames 210–330, a period of 240.
- He is turned 180° about the hips when his shoulders face the bed. The log reads `dx -0.083 -> girado 180`.
- Seen at loop t 158 and t 206: he faces forward.

**The roadside is periodic (plan §5.1 a):**
- `camino_edificios.edificios()` builds one 192 m period of shops, bardas and silhouettes, and copies it for
  k = −2..N_PER−1. The canopy and the oncoming car stay one-offs.
- `camino_mx140.postes()` repeats one period's pole tilts.
- **This changes the run's roadside** compared with the 08:31 Cycles preview the owner saw.

**Measured (09:54 chain, Workbench 640×360):**

```
bun test src/lib/ruta.test.ts       7 pass (run parity, loop parity, move 1 = run, C1 handovers + wrap, paso exits)
RUTA CHOQUES 0 · CHOQUES BUCLE 0 · HOLGURA BUCLE min 0.124 m (frame 1310 = t 183), 0 frames < 0.10 m · ASOMADOS 0
seam, same pose one period apart (frame CLIP+t vs CLIP+t+240), mean abs diff /255 · px > 8:
  world  t0 0.009 · 0.011 %   t140 0.020 · 0.034 %   t200 0.011 · 0.020 %   (only on the roadside shrub band)
  cast   t0 0.000 · 0 %       t140 0.000 · 0 %       t200 0.000 · 0 %
  frame 1367 vs 1127 (whole frame)  0.008 · 0.011 %
eagle.sh bucle-clip.mp4 --loop  exit 0 · seam 5.71 <= 31.03 pass (median step 5.98, max 28.65) · strobe pass
  events f182, f230 = the windshield crossings (in past the driver's face, back out to the hood)
revisar.sh bucle-previa.mp4  exit 0 · strobe pass · 10 events, every one on a ramp of steps, none a one-tick spike:
  the windshield crossings at 1× and at the 3× scroll clock, the run's fast stretches, and the clock-rate change at scroll start
```

Outputs are in `~/cc-out/mto-pantalla/3d/ruta/bucle/`:
- `bucle-previa.mp4` and `bucle-previa-rotulada.mp4`: 783 ticks. They show the loop, the forward exit from move 2 and the
  backward exit from move 3.
- `bucle-clip.mp4`: frames 1127–1366.

**What the Workbench preview hides:** `sin_vidrio()` deletes the glass faces, so the two windshield crossings (t ≈ 182 in,
t ≈ 230 out) show no tint or reflection change. Cycles will show them.

**Open, for the owner:**
- Move 2 swings out wide and back, then tracks forward along the cab. The rear pair is three-quarter at t 158. Speeds peak at
  15 cm/frame.
- Move 3 enters past the driver's face. The closest pass is 12.4 cm, at t 183, and it is the largest image step in the
  loop (about 29 against a median of 6). Its push turns at t 214, with about 0.25 s near-still.
- Scroll speed: at 3 frames/tick, the rest of the loop plays in about 1.4 s. A speed factor would change that.
- Not done:
  - the 9:16 `alta` loop poses;
  - the page wiring;
  - Cycles;
  - the pantalla's wheels;
  - the run's frame 96 head wipe;
  - the dark frames 785–809.

### Moves 2–3 eased and lengthened: `largo` 480 (2026-11-16 18:40, spaghettidrone)

The owner (16:25) asked for moves 2 and 3 to be "smooth like 1", with the shots eased out. At 16:46 the owner added: "it's the
duration of the shots ... the other 2 are really fast".

**Diagnosis:** the roughness was in the path, not the encode.
- The old moves 2 and 3 covered 7.4 m / 202° and 3.7 m in 80 f and 64 f. Move 1 covers 0.32 m in 96 f.
- The monotone Hermite's acceleration jumped 0.013–0.079 m/f² at every knot.
- The render's frame-to-frame jump had a median of 11–12.5, against 1.7 in move 1.

**What changed:**
- `largo` is now 480, the next multiple of 240. Vibra, the world and the cast all loop at 240, so 288 would not close the
  loop. Moves 2 and 3 now last 8 s each; move 1 stays 4 s. `clip` is still 1127, and the loop is keyed at 1126–1607.
- `scripts/bucle-suave.py` writes `bucles[0].suave`. Those are points on the approved curve:
  - every authored pose;
  - a point about every 4 of its frames;
  - a point every frame in the first and last stretch.
- The script also sets each pose's `reloj`, the loop frame when the camera reaches that pose. Each point's `t` still places
  it on the approved, 240-frame curve.
- `ruta.ts` and `ruta.py` sample `suave` with a clamped C2 spline (`tangentesC2` / `tangentes_c2`). So the acceleration
  never jumps, including at both handovers: the 2nd and 2nd-to-last points are solved so that the spline matches the run's
  acceleration there.
- The generator chose the knot times for the lowest combined acceleration, under these constraints:
  - the hood pose fixed at t 288, the move 2/3 split;
  - the push between the front heads at about 80 f, its old share of move 3;
  - at most 2 cm off the approved path (5 cm for the look target).
- New test: no acceleration jump at any knot or handover (under 5e-4 m/f²; the old code fails it).
- The points test now checks `reloj`. The scroll test was rescaled to 480.

**Measured:**

```
path (scratchpad medir.ts; interior peaks)    old 240 f             eased 480 f
  move 2  peak a / a·T²/D                     0.0305 / 26.4         0.0041 / 19.8
  move 3  peak a / a·T²/D                     0.0570 / 62.5         0.0052 / 53.6     (move 1: 0.0005 / 14.8)
  peak speed m/f (2, 3)                       0.149, 0.155          0.065, 0.056
  handovers, max a ±1 f                       0.035                 0.006
render (revisar jump per frame)               median · max step-change
  move 2                                      11.0 · 2.9            6.7 · 1.1          (move 1: 1.7 · 1.1)
  move 3                                      12.5 · 5.3            5.3 · 1.9
bun test src/lib/ruta.test.ts  8 pass
RUTA CHOQUES 0 · CHOQUES BUCLE 0 · HOLGURA BUCLE min 0.104 m (frame 1427 = t 300, past the manager), 0 < 0.10 · ASOMADOS 0
eagle.sh bucle480/bucle-clip.mp4 --loop  exit 0 · seam 4.44 <= 19.91 pass · strobe pass · 0 events (old: 2)
frame 1607 vs 1127  mean abs 0.005 (0–255) · 0.012 % px > 8
eagle.sh bucle480/bucle-previa.mp4  exit 0 · strobe pass · 5 events, all in the 3× scroll-outs (ticks 736–875, 1222)
```

**The a·T²/D bar is not met for moves 2 and 3.**
- The approved path has two hard corners, and keeping the poses and the path means they stay. One is the front-right
  turn-in; the other is the turn onto the hood at run speed, just before the wrap.
- Move 3's slow push sits between faster stretches, which inflates that move's a·T²/D.
- Rounding the corners is the owner's call, together with a tighter move 2 (option B, held by buggyship).

Outputs are in `~/cc-out/mto-pantalla/3d/ruta/bucle480/`:
- `bucle-previa-rotulada.mp4`: 1341 ticks, the same scenario as the 240-frame preview, with the hold points scaled.
- `bucle-previa-lado-a-lado.mp4`: the old and new previews side by side.
- `bucle-clip.mp4`: the 480 f loop.
- `velocidad-viejo-vs-nuevo.png`: the speed and acceleration plot, old vs new.
- `scripts/`: the render chain, ticks, labels, measure and plot.

Render commands:
- Use `RUTA_PERIODOS` ≥ last world frame / 240 + 2: 9 for the clip, 11 for the preview.
- The clip renders with `RUTA_DESDE=1127 RUTA_HASTA=1607`.

### Cycles pass of the run and the 480 f loop (2026-11-16 22:00, meltingdrone)

`scripts/render-ruta-cycles.sh <out>` renders both clips in Cycles (night, road3, straight road, OptiX) at 640×360 and writes
`public/prototipo/{ruta,bucle}.mp4` and the two `-f0.jpg` posters. The 9:16 `alta` loop was not rendered: its poses do not exist.

- **64 spp, not 16.** On the same 24 frames (loop frames 1127–1150), error against the 64 spp render was 2.43 at 16 spp and
  1.96 at 32 spp (0–255, mean abs), and the brows and glasses of the front figures smear behind the windshield at 16 and 32.
  Render time per frame (build excluded) was 1.6 s at 16, 1.5 s at 32 and 2.9 s at 64; the full run was shorter than that (2.0 s).
- **Encode:** x264 crf 26, keyframe every 4 (loop) and 3 (run) frames, as the page scrubs them. The run is 3.9 MB and the loop 1.6 MB
  (the Workbench pair was 2.9 MB and 1.8 MB).
- **The windshield crossings are now at loop frames 301 and 442** (the eased path moved them from 182 and 230). Each is a one-frame
  step bump (step 31 against 21 before it, and 25 against 18): the glass veils or doubles one frame. revisar lists them as `jump`.
