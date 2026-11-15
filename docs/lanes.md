# MTO truck scene: the integration branch and its lanes

Approved by the owner on 2026-11-15 at 04:18 ("let's do it like you said"). The decisions are in the mothership queue,
`docs/queue/2026-11-15-mto-props-phase-decisions.md`. The scenes are already selected, so no lane picks new scenes.
The order is the cast first, then props and assets.

## The integration branch

`cc/highkeydrone` is the integration branch. It started from `cc/goblindrone` (439c3ca) and holds the merged scene work.

| Branch | Merge | What it brought |
|---|---|---|
| cc/yeehawdrone | c40f941 | The Night B world: `blender/mundo.py`, plus the hook in `escena.py`'s `mundo_render` |
| cc/nerddrone | 4df264a | Bed caja5, the latest bed (`caja4.py`, `caja5.py`), drink labels (`etiquetas.py`), and `ESC4_LUZ = "cabina"` (4B) |
| cc/uncdrone | 23154e7 | Strawberry B (`blender/props/strawberry-s2-oro.glb`), and the Pirata One MT emblem at 21.5 cm in `props_placement.py` |
| cc/colddrone | 31a5f5d | Diego TRELLIS.2 with a Mixamo skin, clip fixes, and his drink (`blender/partes/`) |
| cc/skibididrone | c222142 | Diego by parts (`blender/partes2/`). Code only; it is on hold for the Tripo comparison |

touchgrasdrone was already in. apedrone (the Tripo cast) was not merged, because it is still working.

**What the integration build is.** `blender/montaje.py` composes the lanes' scripts without editing any of them. It runs
the whole chain: escena (with the Night B world), then utileria, caja3, caja4 and caja5. It then loads props_placement's
body in a separate namespace, then the cast slot, then the six scene options. Its header lists, for each scene, the hold
and the picks with their sources. Run it as below; `wb` gives raw Workbench stills, and leaving it off renders in Cycles:

```
/mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/montaje.py)" \
  -- "$(wslpath -w blender/escena.py)" <out_dir (Windows)> 1 all 960x540 wb
```

The build saves `<out_dir>/montaje.blend`, which holds the truck, the world, the cast slot and the interim Diego. Each
scene's dressing is built per option, as in every chain script. The .blend is a build output: nobody hand-edits it. A
change goes into the script that owns it, and then the build is run again.

## How a lane works

1. **Branch.** Create the lane branch from the integration branch's tip:
   `git worktree add "../MTO-<drone>" -b cc/<drone> cc/highkeydrone`.
2. **Edit only your files.** Edit only the files and collections the table below gives your lane. If you need a change
   in another lane's file, ask that lane through the mothership. Don't make the edit yourself.
3. **Run the build to check.** Run `montaje.py` with `wb`, at least for the scenes you touched. The run must exit 0 and
   leave no `Traceback` in its log. Put a still or a measured number in your report.
4. **Hand back.** Commit on your branch, one logical change per commit. Then report to the mothership, which asks the
   integration branch to merge you. The merge is `git merge --no-ff cc/<drone>`. Lanes never merge into each other or
   into the main checkout's branch.
5. **Catch up.** If the integration branch moved on while you worked, merge `cc/highkeydrone` into your branch before
   you hand back, and run the build again. apedrone sits on the old base (439c3ca), so it must do this first.

**Untracked inputs.** Every worktree needs these before the build runs, because git does not carry them:

| Input | What to do |
|---|---|
| `blender/assets/camion` and `blender/assets/reparto` | Junction them to the main checkout. Windows Blender does not follow WSL symlinks, so use PowerShell: `New-Item -ItemType Junction -Path 'E:\...\MTO-<drone>\blender\assets\camion' -Target 'E:\Cursor Projects\MTO\blender\assets\camion'`. Remove one with `cmd /c rmdir`, which leaves the target alone |
| `blender/assets/utileria/alien/` (caja5's alien) | Copy it from `~/cc-out/mto-integracion/assets/utileria/alien/`. A junction can't point at a `\\wsl.localhost` path |
| `tmp/utileria` | Copy `~/cc-out/mto-integracion/assets/fuentes/*.ttf` into `tmp/fuentes/`. Then regenerate the rest with the repo's own scripts: `uv run -q --with numpy --with pillow python -I blender/calcas_arte.py`, then `uv run -q --with pillow python -I blender/etiquetas.py`, then `uv run -q --with pillow --with qrcode python -I blender/placa_veracruz.py`, then `uv run -q --with pillow --with fonttools --with brotli python -I blender/pantalla_tablero.py`. Finally copy `~/cc-out/mto-integracion/assets/calcas3/spotify-icon.png` into `tmp/utileria/calcas3/`, because no script makes it |
| The Night B assets | Nothing to do: `mundo.py` reads them from `~/cc-out/mto-world/assets/polyhaven-2026-11-14` |
| The interim Diego | Nothing to do: `~/cc-out/mto-integracion/assets/diego_clip_sitting_drinking_sip.blend`, a copy of colddrone's untracked blend. `MONTAJE_DIEGO=<path>` (through WSLENV) overrides it |

## Lanes

Each file has one owner. `utileria.py` is the exception: it is split by function blocks, as the props row below says.

| Lane | Owns (files) | Owns (scene collections and objects) | First task |
|---|---|---|---|
| **Integration** (highkeydrone) | `blender/montaje.py`, `docs/lanes.md`, the merges | `reparto` and its seat empties `asiento_*`; the `montaje-esc*` options | Wire in each lane as it hands back. The cast drop-in comes first |
| **Layout / cameras** | `blender/transicion.py` (`CAMINO`, the camera rail and the seating poses), `blender/storyboard.py`, `blender/colocar.py`, and in `utileria.py` the scene-hold block from `def v(lens)` to `esc6_flash` (the `toma(...)` tuples, `luz_costado`) | Cameras `cam_*`, `cam_transicion` | Check that each hold still frames its subject at the cast's heights (1.25 / 1.20 m, Findings › Seat clearance). Scene 6's camera currently lives in `montaje.py`'s `m_esc6` (from pp6-b); move it into a `esc6` hold in `utileria.py` so layout owns it |
| **World** (yeehawdrone's line) | `blender/mundo.py`, `escena.py`'s `mundo_render` world part, the `noche` values in `src/lib/escena.json`, `docs/mundo-noche-b.md`, `docs/licencias/mundo-polyhaven.md` | `mundo`, every `w_*`, poles, lamps, plants, fog | Loop check: frame 192 must equal frame 0 for each hold (`eagle.sh` on a short clip). The raw sheet checked stills only. The lane needs no change (Findings › Lane) |
| **Characters** (apedrone, Tripo cast) | `blender/tripo-v5/`, `docs/tripo-reparto-v5.md`, `blender/partes/`, `blender/partes2/`, `blender/reparto.py`, `blender/personaje.py`, `blender/assets/reparto*` (untracked) | The contents of `reparto/reparto_<who>` | Deliver the four Tripo figures as seated clip .blends: Mixamo rig, metres, facing −Y, scaled to `alto_m` (1.25 m Diego and Alexandro, 1.20 m Héctor and the manager). Name each rig after its figure: `cast_alturas/cast.blend` has `Armature`…`Armature.003`, in `cast.json`'s order (diego, hector, alexandro, manager). apedrone's `alexandro` is the chain's `alejandro`; the chain keeps its name, because other code finds `alejandro_rig`. Integration places each one on its `asiento_<who>` through one root empty, the way `montaje.py`'s `diego_interino` does. Measure the seated head against the ceiling (Findings › Seat clearance) |
| **Props** (teadrone, `cc/teadrone`) | `utileria.py` (everything outside layout's hold block), `caja3.py`, `caja4.py`, `caja5.py`, `props_placement.py`, `calcas_arte.py`, `etiquetas.py`, `pantalla_tablero.py`, `placa_veracruz.py`, `fresa_charm.py`, `blender/props/`, `blender/fuentes/`, `docs/design/props-placement/`, `docs/design/escenas/utileria/` | Everything built into `GRUPO` by an option: the bed load, the stickers, the cab dressing, the roof lamps, the MT emblem, the plate, the screen truck | **(1) The dashboard screen** (below). **(2) The seven sticker decals** (below) |
| **Animation** (parked) | `blender/temblor.py`, `blender/vivo.py`; the clips' motion | none yet | Parked until the cast and props are in. Then the v3 transition re-render with all four in the cab (escenas-plan §0 item 4) |

### Props lane, first task

**1. The dashboard screen.** The owner's words: "the screen on the dashboard was not in the latest or the middle dashboard
where they put the drinks".
- What exists: `pantalla_tablero.py` writes the screen faces to `tmp/utileria/pantalla-ancha.png` (3:1, MBUX style) and
  `pantalla-comand.png` (16:9).
- `utileria.py` places them in `radio2_a` (a wide screen floating on the dash top) and `radio2_b` (a screen in the
  centre stack at z 1.52, the G63's COMAND slot).
- No scene in the caja5 line calls either one. nerddrone's last commit says "sin consola".
- The task is to put the screen on the middle console, where caja5's `bebidas_consola` put the drinks: the cupholders at
  y 0.47 and 0.57, top z ≈ 1.37, between the front seats.
- Build the screen as a function in a props file, `utileria.py` or `caja5.py`. Name the scenes it belongs in. At the
  merge, integration wires it into `montaje.py` for scene 1 and any other scene where the cab shows.
- Show it to the owner as a still before you lock it.
- Start from nerddrone's **uncommitted** console redo: `MTO-nerddrone`, the `git diff blender/caja5.py` there, and
  `docs/handoffs/2026-11-14-caja5-console-redo.md` (downbaddrone, 21:10).
  - It moves the console drink to the only clear patch: in front of the shifter, x −0.03..+0.095 from the centre line,
    y 0.945..1.031.
  - It found that the old cupholder spot intersected the armrest lid.
  - It is not on any branch. Have it committed on `cc/nerddrone` first, then merged here, before the screen goes in
    beside it.

**2. The seven sticker decals.** The owner approved the picks in `/mnt/e/Cursor Projects/MTO/comfy-out/stickers-r1/picks/`
(that folder exists only in the main checkout).
- The seven: `r1-slogan`, `r1-arriba`, `r1-x-holo`, `r1-gallo`, `r1-corazon`, `r1-bubu`, `r1-placa`.
- Each has `<id>.png` and `<id>-n.png`. The fragment `calcas3.json` has the same keys that `calca3()` reads.
- Merge the fragment into the `calcas3.json` that `calcas_arte.py` writes, and copy the PNGs into
  `tmp/utileria/calcas3/`.
- Then place the decals with `calca3()` on the tailgate and the bed sides, with `ranuras_libres()` for the free slots.
  The plan's §2 rules apply: our own art, stuck on free-hand. Scene 2 is the camera that shows them.
- The picks' README says "the integration branch merges it". This brief gives the job to the props lane instead.

Other props items from the raw sheet (`~/cc-out/mto-world/crudo/hallazgos.md`):
- #8: scene 5's sign truck is a box stand-in with placeholder copy. The dates come from the watcher's file (plan §5).
- #9: the alien stands above the roll bar in scene 4. That is a taste note for the owner.

## Findings (measured 2026-11-15, integration build)

**The live rig works in the chain; the raw sheet's placement broke it (hallazgos #6).**
- The rig evaluates correctly inside the chain. I appended Diego live into the full caja5 chain, both colddrone's clip and
  skibididrone's. Skin and bone children measured the same as in an empty file.
- The raw run's error came from how it moved the clip: `matrix_world = M @ matrix_world` on every object, the armature
  and its children alike.
- A bone-parented child then reads the bone's pose before the depsgraph updates, so the move is applied to it twice. I
  reproduced this in an empty file.
- The fix is to parent the clip's top-level objects to one empty and move only that empty. With it, the clip stays live,
  so it can animate.
- The regression test is `blender/montaje_rig_test.sh [clip]`. It exits 1 if the root-empty placement leaves a bone
  child more than 1 cm off. It passes on both Diego clips (0.000 m), and the old loop measures 1.14–1.22 m off.

```
empty file, sitting_drinking f1, 1.25 scale, hips on the rear-right seat   skin z from hips   bone child z from hips
skibididrone, crudo.py's loop                                              -0.078..+0.847     shoe_R +0.743..+0.890
skibididrone, one root empty                                               -0.078..+0.847     shoe_R -0.370..-0.252
colddrone, crudo.py's loop                                                 -0.365..+0.871     bottle +0.992..+1.244
colddrone, one root empty                                                  -0.365..+0.871     bottle -0.173..+0.029
```

**Lane.** The truck already drives in the right lane, so nothing was moved. `montaje.py`'s `carril()` prints this
on every build:
- The world moves −Y (its y is 0.00 at frame 0 and −8.00 at frame 10), so the truck drives +Y. The front seats (y 0.47)
  are ahead of the rear seats (y −0.53), and the hood front is at y 2.94.
- Facing +Y, the truck's right is +X.
- The wheels span x 0.61 to 2.83 and the mirrors x 0.66 to 2.79. The lane is x 0 to 3.55: the dashed lane line is at
  x 0, the solid white right edge at +3.55, and the solid yellow left edge (NOM-034, a divided highway) at −3.55.
- The screen truck overtakes on the left, at CX − 4.0.
- The Night B sheet (`~/cc-out/mto-world/build/hoja-noche-b.jpg`) shows the same thing: in scenes 2, 5 and 6 the white
  edge is on the truck's right.
- The owner's "right lane" was a confirmation, not a report of a wrong render (mothership, 05:36).

**Seat clearance: the cast fits at the owner's truck convention (1.25 / 1.20 m).** The owner confirmed the heights at
04:34 (apedrone, `docs/tripo-reparto-v5.md` › Heights): the tallest figure is 1.25 m, as the truck build's figures always
were, and the others keep the owner's ratios. That is 1.25 m for Diego and Alexandro, and 1.25 × 1.67/1.74 = 1.20 m for
Héctor and the manager. `montaje.py`'s `ASIENTOS` now carries these heights, and the interim Diego is scaled to 1.25 m.
Each seat's ceiling was found with a ray straight up from the seated hip point (build of 2026-11-15 05:34):

```
seat               hip z   ceiling z   height   head top above hips        head top z                  room
manager  front L   1.150   2.189       1.20     0.748 x (apedrone, rest)   2.048 (estimate)            +0.141
Héctor   front R   1.150   2.190       1.20     0.748 x (apedrone, rest)   2.048 (estimate)            +0.143
Alexandro rear L   1.259   2.187       1.25     0.674 x (apedrone, rest)   2.102 (estimate)            +0.085
Diego    rear R    1.259   2.187       1.25     colddrone clip, seated     2.130 (measured, the clip)  +0.057
```

- The estimates use apedrone's v5 figures in their rest pose (`MTO-apedrone/blender/assets/reparto-v5/cast_alturas/cast.blend`,
  the mesh top above the Hips bone), with the torso upright. No seated clip of those figures exists yet. When one comes,
  the build measures it.
- Why 1.74 m failed: colddrone's Diego, seated, has his head top 0.697 × his height above his hips. At 1.74 m his head
  went 0.285 m through the roof (the 05:10 build, log `crudo/montaje-174.log`). The tallest figure that fits with 2 cm
  to spare is 1.30 m in the rear seats and 1.46 m in the front seats, so 1.25 / 1.20 m fit.
- Diego's bottle-to-hand distance scales with him: 0.086 m at 1.25 m, which is 0.069 × 1.25 from the empty-file test.

**Untracked input with no generator.** `tmp/utileria/calcas3/spotify-icon.png` (the Spotify glyph on the scene-2
sticker) is made by no script in the repo. It was copied from `MTO-nerddrone/tmp/utileria/calcas3/`. Props lane: add it
to `calcas_arte.py`, or track it.

**A merge interaction, fixed (1339acc).** `props_placement.py`'s probe ended with `hide_viewport = False` on every
object. That unhid the Night B fog box and plants, which the world keeps hidden from ray casts. It now restores only the
objects it hid. `montaje.py` asserts this on every build.

## Open questions (for the owner, through the mothership)

1. **Is the bed final?** With the owner. The build uses caja5 'elegida' (nerddrone dafaa18), the latest committed bed. nerddrone also
   has uncommitted work (`tmp/caja6`, `tmp/caja7`, the caja5 console redo). It changes the cab drinks, not the bed load. The decisions file asks to reconcile uncdrone's strawberry B and Pirata
   One MT into caja5. The build already does that: `props_placement.py`'s body puts both on the truck in every scene.
2. **Answered: the lane.** No render looked wrong. The owner's "right lane" confirmed where the truck already drives
   (mothership, 05:36), so it stays where it is.
3. **Answered: the cast's heights.** The owner confirmed 1.25 / 1.20 m at 04:34. They fit the seats
   (Findings › Seat clearance), and the build uses them.
4. **Do the roll-bar bulbs (P9) come back on caja5?** With the owner. The pp B scenes had them on the older bed; montaje leaves them out.
5. **Which interim Diego?** colddrone's TRELLIS.2 clip is in the build, and skibididrone's partes2 is merged as code only.
   Both give way to apedrone's Tripo Diego.
6. **Answered: the stickers.** The props lane places them (mothership, 05:36). teadrone (`cc/teadrone`, branched from
   this branch) owns the dashboard screen and the seven stickers; integration merges it when it hands back.
7. **Housekeeping.** colddrone committed `blender/partes/__pycache__/inspect.cpython-314.pyc`, and
   `blender/__pycache__/` shows up untracked after any run. `.gitignore` has no `__pycache__/` line. It was left as it is.
