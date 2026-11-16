# Handoff: the band-section camera loop, built; the Workbench preview is being re-rendered (breaddrone → successor, 2026-11-16 09:45)

**Where:** worktree `/mnt/e/Cursor Projects/MTO-oopdrone-downbaddrone`, branch `cc/downbaddrone`. **Nothing is committed**,
neither downbaddrone's work nor mine. I asked buggyship at 08:52 whether to commit first; it answered the other questions but not
that one. Ask again before committing, and **never `git add -A`**: the `blender/assets/*` junctions show as `??`.

**Spec:** `docs/handoffs/2026-11-16-movimiento-banda-loop.md` (the owner's 3-move loop) and `docs/design/movimiento-plan.md`.
Read both first.

## Decisions (buggyship, relaying the owner's standing rules)

- **Scroll exit (09:04):** the default is built. While the camera is in move 2 or 3, scrolling drives the loop's clock in the
  scroll's direction until it is back on move 1, and the run takes over from there. There is no blend through metal.
  The preview has to show one scroll-out from move 2 and one from move 3.
- **(09:09) After the preview, without waiting:**
  - **(2) The cast loops,** with a period that divides 240.
  - **(1) The periodic roadside** (plan §5.1, option a, not a crossfade).
  - **Report the loop wrap's frame-diff at the seam** (last frame vs first), separately for the world and for the cast.

## Design as built (not yet in the plan doc: add a "Band loop" section there)

- **`src/lib/ruta.json` `bucles[0]`:** `desde` 647, `hasta` 743, `largo` 240, `clip` 1127, and 9 loop points with `t` from
  124 to 229, each with a `nota`.
  - Loop frame t 0–96 *is* the run's 647–743, the hood slide (move 1).
  - Moves 2 and 3 are a Hermite from the run pose at 743, through the loop points, back to the run pose at 647. Its end tangents
    are the run's own tangents, so both handovers and the wrap are C1 by construction. The test prints the velocities.
  - I chose this over the handoff's periodic-ghost-point idea because move 1 then equals the run exactly. Entering or leaving
    anywhere in move 1 is jump-free.
  - `largo` must be a **multiple** of 240, not a divisor. vibra uses 29, 47 and similar cycles per 240, so 120 would break it.
  - `clip` ≡ `desde` (mod 240), so the world, vibra and cast phases at the loop clip match the run at 647.
- **References:**
  - Move 1: Collateral 023/029 (the hood mount, looking in).
  - Move 2: Collateral 007 (the side window at night). Its key pose is variant n2a.
  - Move 3: Collateral 014 (front-seat shoulder in the foreground, rear passenger beyond). Its key poses are n3-inicio and n3-fin.
  - The variant stills are in the scratchpad (below): m2a–c, m3a–c, n2a–c, n3. m3a is rejected because the strawberry fills the
    lens; m2b and n2b because the seat backs and the window top cut the heads.
- **`src/lib/ruta.ts`:**
  - `tangentes()` was split out of `hermite()`, and `hermite` takes optional end tangents (`ext`).
  - `orientar()` was split out of `muestra()`.
  - New: `bucle(t)`, `bucleInfo`, `paso(estado, df, dt)` (the scroll/clock stepper) and `poseEstado`.
- **`blender/ruta.py`, sampler:** the same sampler, plus `bucle()`.
- **`blender/ruta.py`, cast:** `reparto_en_bucle()`.
  - The 3 stand-ins repeat their action's frames 0–80 on the NLA (an 80-frame sway, which divides 240).
  - Diego's Mixamo clip is re-anchored on his seated hips at frame 210 and ping-pongs frames 210–330 (period 240). It is also
    turned 180° about the hips when his shoulders say he faces the bed. **The turn has not been seen rendered yet.**
- **`blender/ruta.py`, keying:** the loop is keyed at 1126–1367 (one pad frame each side).
- **`blender/ruta.py`, checks:**
  - `RUTA CHOQUES BUCLE`: the wrap is included.
  - `RUTA HOLGURA BUCLE`: 26 rays per frame, skipping glass; it reports the minimum distance and the frames under 0.10 m.
  - `material()` now reads the evaluated mesh.
- **`blender/ruta.py`, bake:** `ruta.bake.json` gets `bucle`.
- **`blender/ruta.py`, Workbench:** `sin_vidrio()` deletes glass faces in the Workbench pass. Workbench drew the windshield
  opaque.
- **`blender/ruta.py`, preview:** `RUTA_PREVIA=<ticks.json>` renders the page's own stepping, one still per tick. The docstring
  has the commands; it now says `RUTA_PERIODOS=8`.
- **Periodic roadside:**
  - `blender/camino_edificios.py` `edificios()` builds one 192 m period of shops, bardas and silhouettes and copies it for k in
    -2..N_PER-1. The canopy and the oncoming car stay one-offs.
  - `blender/camino_mx140.py` `postes()` repeats one period's pole tilts.
  - **This changes the run's roadside** compared with the 08:31 Cycles preview the owner saw.

## State (measured)

- `bun test src/lib/ruta.test.ts`: **7 pass**. That covers run parity, loop parity with the bake, move 1 = run, continuous
  handovers and wrap, the loop points, and `paso` exits.
- Last bake (09:40), before Diego's turn:

  ```
  RUTA CHOQUES 0 · CHOQUES BUCLE 0 · HOLGURA BUCLE min 0.124 m (frame 1310), 0 frames < 0.10 m · ASOMADOS 0
  ```

  - The earlier flag of 3 shoulder vertices at the passenger front window was Diego's drifted clip.
  - The strawberry pass was 7.2 cm before the entry moved under it (y 1.74 at t 184).
- **Preview v1 (09:40):** `~/cc-out/mto-pantalla/3d/ruta/bucle/bucle-previa.mp4` and `bucle-previa-rotulada.mp4`.
  - 783 ticks at 24 fps, Workbench 640×360, 298 s of render.
  - It shows the loop, the forward exit from move 2 and the backward exit from move 3, all continuous by eye.
  - **Defect:** Diego faced backwards (the back of his head from inside the cab). Fixed in code; v2 is rendering.
- **Running now:** background chain `scratchpad/cadena.sh` (task `bzh85zotc`). It writes:
  1. Preview v2 into `~/cc-out/mto-pantalla/3d/ruta/bucle/previa/`; log `scratchpad/previa.log`.
  2. The loop clip, frames 1127–1367, into `scratchpad/clip/cuadros/`; log `clip.log`.
  3. The seam pairs into `scratchpad/costura/`; log `costura.log`. The pairs are named `{capo,costado,cabina}-{mundo,reparto}-{0,1}.png`:
     the same camera pose at frame CLIP+t and CLIP+t+240, once with only the world and once with only the cast.

  If the chain died with the session, re-run it: `scratchpad/cadena.sh`, in the background.

  **Update 09:54: the chain finished.**

  ```
  previa exit 0 439 s · clip exit 0 163 s · costura exit 0 53 s
  RUTA Diego hombros dx -0.083 -> girado 180
  CHOQUES 0 · CHOQUES BUCLE 0 · HOLGURA min 0.124 m, 0 frames < 0.10 m · ASOMADOS 0
  ```

  - The clip frames (241 of them) and the 12 seam pairs are on disk.
  - Step 1 below is done, except for `bun test` and the look at ticks 204 and 252. Start at step 2.

## Exact next steps

1. **Check the run logs.** For each log, `grep -E "^RUTA|Traceback"`. `previa.log` must show `RUTA Diego hombros dx ... -> girado 180`.
   Re-check `HOLGURA`, because Diego turned may sit closer to the push. Then run `bun test src/lib/ruta.test.ts`.
2. **Rebuild the labelled preview.**
   - Command: `uv run -q --with pillow python -I scratchpad/rotular.py ~/cc-out/mto-pantalla/3d/ruta/bucle/previa scratchpad/previa/ticks.json scratchpad/previa/rot`.
   - Then run the two `ffmpeg` encodes. The commands are in the transcript pattern: `-framerate 24 -i %04d.png -c:v libx264 -pix_fmt yuv420p -crf 18`.
   - Look at ticks 204 (t 158, move 2) and 252 (t 206, move 3): Diego must now face forward.
3. **Measure the seams.**
   - Pixel diff of each costura pair (mean abs diff, or `revisar.sh img --ref`), separately for the world and the cast.
   - Encode the clip frames 1127–1366 (exclude 1367) to mp4 and run `~/projects/visual-lab/scripts/eagle.sh <clip> --loop`. Its
     seam row is the number buggyship asked for.
   - Also diff frame 1367 against 1127: same camera pose, one period apart. It should be about 0.
4. **Send buggyship the preview and the numbers** (SendMessage `buggyship [38b2d7]`; the bare name matches two sessions).
   - Owner review comes before any Cycles render.
   - Send the file with SendUserFile too.
5. **Write the "Band loop" section** in `docs/design/movimiento-plan.md`, using the design and numbers above.

## Open

- **The owner's taste call on move 2.** It swings out wide and back, then tracks forward along the cab. The rear pair is
  three-quarter at t 158. Speeds peak at 15 cm/frame. Move 3's push turns at t 214, with about 0.25 s near-still.
- **Scroll speed in `paso`:** 1 scroll frame equals 1 loop frame. At 3 frames/tick, the rest of the loop plays in about 1.4 s.
  A speed factor is the owner's call.
- **Not done:** the 9:16 `alta` loop poses, page wiring, Cycles, and the pantalla's wheels. Still open from the previous
  handoff: the frame 96 head wipe and the dark frames 785–809.

## Findings: general method → report as `gotchas:` lines (they land in visual-lab)

```
gotchas:
- Workbench drew a windshield opaque: glass was a face material on a mixed object, and pase_wb hides by first material -> delete faces whose material name starts with vidrio/mica (bmesh)
- Mixamo clip with root motion, anchored at frame 0, slid 1 m out of its seat -> anchor on a seated frame's Hips; for a loop, ping-pong a stretch (2 NLA strips per period, the second use_reverse)
- A camera loop has to hand over to a linear Hermite run without a jump -> reuse the run's own stretch as move 1 and give the loop Hermite the run's tangents at both ends (C1 by construction)
- Sum-of-sines shake with integer cycles per 240 loops only for lengths that are multiples of 240, not divisors
- A ray from each camera position to the next found 0 hits while the path grazed a head -> per-frame clearance: 26 rays from the camera, skipping glass
- scene.ray_cast's face index is the evaluated mesh's -> read the material on obj.evaluated_get(dg).data
```

## Site notes (this repo's docs/)

- Diego (`mx` armature) drifts forward from frame 0 and faced the bed. Every run render before `reparto_en_bucle` had him
  inside Héctor's seat after frame ~110.

## Suggested skills

`blender` (scene work); `director` (if move 2 needs a re-block); `handoff` when stopping.

## Durable copies

The scripts and `ticks.json` are copied to `~/cc-out/mto-pantalla/3d/ruta/bucle/scripts/`. `cadena.sh` there still writes its
outputs to the scratchpad paths; change its `S=` line if the scratchpad is gone.

## Scratchpad (session-specific, may vanish)

`/tmp/claude-1001/-mnt-e-Cursor-Projects-MTO-oopdrone-downbaddrone/579b0676-9b74-4e66-b191-7441df00fb2b/scratchpad/`:
- `cadena.sh`, `costura.py`, `rotular.py`, `previa.ts` (makes `previa/ticks.json` from `paso`) and `velocidad.ts`;
- `var/`, `var2/` (variant stills);
- `orig/` (downbaddrone's ruta files before my edits).

## Report owed

When finished, write ≤3 lines plus paths to `/home/black/.cache/cc-deck/reports/all/breaddrone-1794840600.md` and include:
- a `paths:` line;
- `model: opus effort: high`;
- `verdict: ...`.

Then send buggyship one line pointing to it.
