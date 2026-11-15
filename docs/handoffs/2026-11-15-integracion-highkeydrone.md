# Handoff: MTO integration branch (highkeydrone), 2026-11-15 05:05

The task brief is the mothership message of 04:18, the integration step of the props phase. The decisions are in
`/home/black/projects/mothership/docs/queue/2026-11-15-mto-props-phase-decisions.md`. Branch `cc/highkeydrone`, worktree
`/mnt/e/Cursor Projects/MTO-highkeydrone`. **Read `docs/lanes.md` first.** It holds the lane table, the inputs contract,
the measured findings and the open questions, and this handoff doesn't repeat them.

## Done (commits on cc/highkeydrone, first-parent)

| Change | Commit | Notes |
|---|---|---|
| merge yeehawdrone (Night B) | c40f941 | |
| merge nerddrone (caja5) | 4df264a | One conflict: `docs/design/references.md`. Both branches had appended a section at the end; both were kept |
| merge uncdrone (strawberry B, Pirata MT) | 23154e7 | |
| merge colddrone (Diego TRELLIS.2 and his drink) | 31a5f5d | It brings in a committed `.pyc`, left as is |
| merge skibididrone (partes2, code only) | c222142 | |
| fix: props_placement's probe no longer unhides the Night B fog | 1339acc | |
| feat: `blender/montaje.py`, the integration chain | 0d2e973 | Six options `montaje-esc1..6`, the `reparto` slot, the interim Diego, the lane and seat prints, `wb` mode |
| docs: `docs/lanes.md` | b80e3a5 | |

Done-check results so far:
- The smoke tests of `caja5.py` and `props_placement.py` ran headless with exit 0 and no traceback.
- `escena.py` still mode: exit 0.
- `montaje.blend` reopens headless with exit 0, and the reparto check passes (`~/cc-out/mto-integracion/abrir.py`).
- The rig test passes on both Diego clips.
- Six stills exist, and the sheet exists.

## Uncommitted (commit these)

- `blender/montaje.py`: an assert that the Night B viewport-hidden objects stay hidden after props_placement's body, and
  a print of Diego's bottle-to-RightHand distance (expected about 0.120 at scale 1.74).
- `blender/montaje_rig_test.py` and `blender/montaje_rig_test.sh`: the rig regression test. It passed:
  ```
  colddrone  raiz 0.000 m, crudo 1.216 m off
  skibidi    raiz 0.000 m, crudo 1.142 m off
  ```
- `docs/lanes.md`:
  - inputs now come from `~/cc-out/mto-integracion/assets/`
  - the props task reworded (props builds the function, integration wires it in)
  - a note on nerddrone's uncommitted caja5 console redo
  - the rig test
  - an "Open questions" section
- This handoff.

Suggested commits, one per logical change:
- `fix(integracion): guardia de niebla y medida de la botella en montaje.py`
- `test(integracion): montaje_rig_test, la colocación con un solo empty`
- `docs(integracion): lanes.md con insumos estables y preguntas abiertas` (with this handoff)

Use `git add <files>` only. Never commit `blender/__pycache__/` or `blender/assets/*`.

## Running when the context cap hit

A full build, `montaje.py ... 1 all 960x540 wb`, writing to `~/cc-out/mto-integracion/crudo/montaje.log`. This is the
single clean all-scenes run in one process, the done-check. The earlier full runs failed: the first on my `VIDRIO`
name clash (fixed), the second on the missing `spotify-icon.png` (now copied). Scenes 2–6 then passed in a separate run.

**Result (05:10): passed.** Exit 0, 0 Tracebacks, all six `TOMA` lines, `MONTAJE total 437.8 s`. Diego's
bottle-to-hand distance is 0.119 m (expected 0.120). The lane check prints `DERECHO`, and Héctor's bottle check
(`CAJA5 MANO`) passes in every scene. Step 1 is done: go straight to step 2.

## Exact next step

1. Check the run (done, see above):
   ```
   grep -c Traceback ~/cc-out/mto-integracion/crudo/montaje.log
   grep -n 'MONTAJE\|TOMA' ~/cc-out/mto-integracion/crudo/montaje.log
   ```
   Expect six `TOMA` lines, `MONTAJE total`, a `diego botella->mano` value near 0.120, and the `carril ... DERECHO` line.
   If it has not finished, wait with `scripts/esperar.sh log <log> 'MONTAJE total'` in the background.
   If it failed, fix the cause and rerun.
2. Rebuild the sheet:
   ```
   cd ~/cc-out/mto-integracion && uv run -q --with pillow python -I hoja.py crudo hoja-integracion.jpg "Merged into cc/highkeydrone: yeehawdrone c40f941 · nerddrone 4df264a · uncdrone 23154e7 · colddrone 31a5f5d · skibididrone c222142 (apedrone cast not yet: slot 'reparto')"
   ```
3. Commit the uncommitted files (above).
4. Write the report, at most 3 lines plus paths, to `/home/black/.cache/cc-deck/reports/all/highkeydrone-1794737999.md`.
   It must include:
   - the merged branches with their hashes (table above)
   - the conflict and how it was resolved
   - the sheet path: `\\wsl.localhost\Ubuntu\home\black\cc-out\mto-integracion\hoja-integracion.jpg`
   - the open questions (in `docs/lanes.md`)
   - a `paths:` line
   - `gotchas:` lines (below)
   - `model: opus effort: high`, then `verdict: fine`
5. Load `SendMessage` with ToolSearch. Send one line pointing at the report to exactly `mothership-10`. If the reply
   says "did you mean", check ListAgents; if that agent isn't there, don't send.

## Key decisions (with reasons)

- **Diego stays at 1.74 m in the stills.** His head passes 0.285 m through the roof, and that clash is itself the
  finding. Don't shrink him; it is an owner and cast question.
- **The lane geometry is unchanged.** The measurements show the truck is already in the right lane.
- **The glass stays opaque.** The windscreen and rear glass (`vidrio`/`mica`) are hidden in Workbench. The side windows
  still render white, which is noted and not fixed, as the brief asked.
- **uncdrone's bed pieces are dropped:** its bed B 'reglas' and the bulbs on the bed and roll bar.
- **Scene 3 uses `esc3-hombro`,** the owner's pick 3B. The raw sheet had used `esc3-espejo` by mistake.

## gotchas (for the report; general ones go to visual-lab through it)

- Moving a rigged clip by setting `matrix_world` on the parent and then on its children: bone-parented children move
  twice (about 1.1 m off). → Parent the top-level objects to one empty and move that empty (`blender/montaje_rig_test.sh`).
- A probe that ends with `hide_viewport = False` on every object brings the scene's viewport-hidden fog box back into
  ray casts. → Restore only what the probe hid.
- exec-chained scripts share a globals dict, and the same names mean different things (YT, TECHO_Z, dg, VIDRIO). → Exec
  the second script into `dict(globals())`, and check top-level name clashes with `ast` before composing.
- Workbench TEXTURE colour ignores the road's tint node, so the road reads white. → In the raw pass, swap the road,
  verges and markings for flat materials.
- Removing a drone's worktree loses its untracked inputs (assets, `tmp/`). → Keep shared inputs in
  `~/cc-out/<project>/assets`.
- `tmp/utileria/calcas3/spotify-icon.png` has no generator script. → Copy it from another worktree, or add it to
  `calcas_arte.py`.
- Cartoon-proportioned figures at real stature don't fit seated in the G63 cab: the head top is 0.697 × stature above the
  hips. → Measure the seated head height against a ray to the ceiling before choosing a scale.
- A Windows junction can't target a `\\wsl.localhost` path. → Copy the files into the worktree instead.

## Paths

- `/mnt/e/Cursor Projects/MTO-highkeydrone/blender/montaje.py`
- `/mnt/e/Cursor Projects/MTO-highkeydrone/docs/lanes.md`
- `/mnt/e/Cursor Projects/MTO-highkeydrone/blender/montaje_rig_test.sh`
- `~/cc-out/mto-integracion/`: `crudo/` (the six stills, `montaje.blend`, logs), `hoja-integracion.jpg`, `hoja.py`,
  `abrir.py`, `assets/`

## Suggested skills

None needed for steps 1–5. Load `blender` only if the build fails inside Blender.
