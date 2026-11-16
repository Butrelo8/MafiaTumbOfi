# Handoff: MTO motion pass. Next: the band-section camera loop (downbaddrone → successor, 2026-11-16 08:50)

**Where:**
- Worktree `/mnt/e/Cursor Projects/MTO-oopdrone-downbaddrone`, branch `cc/downbaddrone`, based on `cc/oopdrone` at 23cabfc.
- **Nothing is committed.** The work is in the working tree; `git status` lists it. The brief never asked for a commit;
  ask buggyship whether to commit before you build on it.

**Read first:**
- `docs/design/movimiento-plan.md`: how the page consumes the scene, the shared path source, the owner's answers, step 3
  as built, the 06:40 changes, the preview and every number.
- The spec: `~/projects/mothership/docs/queue/2026-11-16-mto-motion.md`.

## Your task (owner 08:45, decided; relayed by buggyship)

The band section (`integrantes`) becomes a **3-move camera loop** that repeats while the visitor stays on that station.
1. **Hood slide.** Look in through the windshield at the manager and Héctor, as now (`ruta.json` frames 647–743).
2. **Outside, passenger side.** Track along the cab, with the rear pair (Alexandro, Diego) seen through the rear side
   window and the road streaming behind.
3. **Inside the cab.** A slow push between the front seats, looking back at the rear pair, easing back into (1).

Rules:
- Each move ends on the next one's start pose, so the loop is seamless. Characters keep animating.
- `ruta.ts` cycles the loop while the scroll holds at the station and leaves it on scroll.
- **Your first deliverable is a Workbench preview of the loop for the owner, before any Cycles render.**

The owner's question that led here (08:43): "how do we show the backseat? the scene can be a camera loop as well, doing
the same movement and repeating, combining maybe 2-3 at that same section/station".

What the loop needs, as the code stands. These are my reading, not built.
- **`ruta.json`.**
  - Today it is one linear path: `camara` points with `fr`, plus `secciones`. A loop needs its own block, for example
    `bucles: [{seccion: "integrantes", puntos: [...]}]`.
  - Its last point must equal its first, and its tangent there must be periodic. The current sampler takes one-sided
    tangents at the ends, so a closed loop needs a wrap-around tangent. Change `hermite` in **both** `src/lib/ruta.ts`
    and `blender/ruta.py`, then extend `ruta.test.ts`.
  - Vibration sines use integer cycles per 240 frames. Make the loop length divide 240, or 240 itself, so the sines loop
    too.
- **The linear run's entry and exit** must meet the loop's pose (1), at frames 647 and 743 today.
- **Render.** For the video consumer, the loop renders as its own clip (`ruta.py` keys one range today). One option is
  to key the loop after the run (frames 1104 and on) and render that range separately.
- **Collisions.** Move (3) goes inside the cab, between the front headrests (transicion's `sin_cabeceras` removes the
  headrests). `RUTA CHOQUES` (camera-to-camera ray, glass excepted) will tell you if it cuts a seat or a head. Diego's
  clip moves its arm (bottle).

## State (all checks passed; numbers in the plan doc)

- `bun test src/lib/ruta.test.ts`: parity between `ruta.ts` and Blender's keyed camera, the pantalla and the flash is
  within 1e-3 on 552 frames.
- `RUTA CHOQUES 0`: the camera crosses no surface along the whole run.
- **Roof check (owner 06:40, the hair).** `asomados()` ran on every rendered frame (`RUTA_PASO_ASOM=2`). It finds no
  figure out through the roof. The only flag is 3 shoulder vertices of `Body` at the passenger front window (x 2.5,
  y 0.56, z 1.85, frame 300). Alexandro is lowered 4 cm and scaled 0.92 about the hip in `ruta.py` `encoger()`; he was
  at z 2.288 under a 2.187 ceiling.
- **Preview:** `~/cc-out/mto-pantalla/3d/ruta/preview/`.
  - `ruta-preview.mp4`: 46 s at 24 fps, 640×360, 16 spp, every 2nd frame doubled.
  - `hoja-preview.jpg`: every 32 frames, labelled.
  - `ruta-preview-12fps.mp4`: the checked file. `eagle.sh` exits 0; it measured only strobe (pass) and dark (83 %,
    info). Morph, hidden-cut, crawl and flicker are n/a (they need `--inicio`/`--fin` or a static area). eagle-eye was
    not run: the skill is off by default.
- **GPU used this session:** about 62 min. 18.2 min was measured (the final preview is 11.0 of it). 35.3 min was a run
  slowed by ComfyUI's VRAM, and about 8 min was an earlier stopped run (estimated).

## Open (in order)

1. **The band section shows only the front two.** This is your task above.
2. **Frame 96 head wipe.** The v3 move passes a rear passenger's head at a few centimetres, because the 12 cm sidestep
   around the hanging strawberry starts at frame 112. Fix identified, **not applied:** stay centred to about frame 100,
   then sidestep. Edit the 112/144 points, then CPU re-bake, parity test, about 11 GPU min to re-render.
3. **Frames 800 and 960 are dark** (the turn off the hood, the fly-forward). That is my reading, not measured.
4. **The pantalla's wheels don't turn.**
5. Not checked: whether Diego's clip keeps playing past its last key.
6. Still to do: the 9:16 `alta` framings, the page wiring (`escena.ts` → `ruta.ts`, video scrubbing per section) and
   the 64 spp finals.

## Gotchas for this worktree

- **Untracked inputs.**
  - `blender/assets/camion` and `blender/assets/reparto` are Windows junctions (`cmd.exe /c mklink /J`) to the main
    checkout. A WSL symlink is invisible to Windows Blender.
  - They show as `??`. **Never `git add -A`**, or the G63 model and the cast get committed.
  - `tmp/fuentes` and `tmp/utileria` were copied from `MTO-oopdrone` (ignored).
- **GPU.**
  - Before a GPU run, POST `/free` `{"unload_models":true,"free_memory":true}` to ComfyUI on an empty queue. With about
    9 GB of idle models in VRAM, Cycles ran 26 s/frame instead of 1.2. `gpu-busy` does not see idle VRAM.
  - Owner 08:13: the Flechas drone goes first on the GPU. Ask buggyship before a long GPU run, and send an ETA measured
    on frames from every section (`RUTA_CUADROS`).
- **Foreground waits.** The hook blocks a foreground `sleep`, and also any Bash text containing `blender.exe` while
  Blender is running. Use Edit/Write for docs that mention it.
- **Commands.**
  - `blender/ruta.py`'s docstring has the run command.
  - `RUTA_RENDER=0` (with `GPU=0`) keys and bakes on the CPU in about 1 min.
  - `RUTA_PASO_ASOM=1000` skips the roof check; at 2 it takes about 11 min on the CPU.
  - `RUTA_CUADROS="a,b,c"` renders a frame list.
  - `RUTA_PASO`, `RUTA_DESDE` and `RUTA_HASTA` set the step and range.
- **`ruta.json` is hand-edited data now.** I generated it once from Blender-space values; the per-point `nota` fields
  carry where each point came from (utileria's holds).
- **`bun test`:** `toggleDom.test.ts` fails in this worktree only because there is no `node_modules`/`dist`. It needs
  `bun run build` first.

## Who waits on whom

- buggyship relays the owner and gates the GPU.
- The owner reviews the Workbench loop before any Cycles render.

## Suggested skills

- `blender`, for scene work in this repo.
- `director`, for the loop's three moves (framing and lens per move).
- `eagle-eye` only if a clip's `eagle.sh` FAILs or the owner asks.
- `handoff`, when you stop.
