# Handoff: caja5 console drinks redo + bottle in Héctor's grip, 2026-11-14 21:10, downbaddrone on `cc/nerddrone`

The spec is the seed `/home/black/projects/mothership/docs/queue/2026-11-14-mto-caja5-console-redo.md`. Read it first. The
previous round is `docs/handoffs/2026-11-14-caja5-props.md` (commit `dafaa18`).

The whole state is the uncommitted diff of `blender/caja5.py` (`git diff blender/caja5.py`). Nothing is committed yet. Scratch
files are in `tmp/caja7/` (probes, preview logs and PNGs).

## Cause lines (for the report: what made the old console still look off)
- **Can:** one ray at x CX−0.05, y 0.47 hit the armrest lid's sloped flank at z 1.321. The lid top 1 cm over is 1.376, and
  1 cm the other way the flank drops to 1.228. So the can sat about 5.5 cm inside the lid and half over the drop:
  intersecting.
- **Bottle:** the same failure at y 0.57 (z 1.312 against a lid top of 1.358): about 4.6 cm inside the lid, on a padded armrest.
- **"Cupholder":** the black torus was a fake ring on the slope. The G63 mesh has no cupholder well anywhere
  (`tmp/caja7/sonda.log`, `cubierta.log`).
- **Lighting:** a 6 W area lamp 0.55 m straight above the drinks blew out the can top and left the cab black around them.
- **Amber water** (in both stills): the label cylinder had end caps. The Generated mapping painted them with the label's gold
  band, which put two gold discs inside the clear bottle. Fixed: the label is an open tube with a pale back face. The previews
  show clear water.
- **Scale is not a cause.** The cab is 1.5 m wide inside (±0.72–0.78), the can is 66×122 mm and the bottle 66×230 mm, both
  real size.
- **Hand, "beside":** the old search centred on the `mano_n` bone. That bone sits about 12 cm outboard of the hand mesh
  (bone x 2.32, mesh x 2.14–2.25), so the search could only reach spots between the hand and the window.

## Decisions (made with the advisor's review)
- **Console: one drink, in front of the shifter.** Behind the shifter, the controller step (y 0.80–0.81) and the shifter boot's
  back lip (y 0.875–0.882, z 1.26–1.28) leave less than 66 mm. Every spot there crossed them (12–70 BVH pairs, upright or
  tilted). In front, the clear patch is x −0.03..+0.095 by y 0.945..1.031, room for one Ø 66 mm drink. The stack's lower lip
  is at y 1.031, z 1.33. These near-vertical faces are invisible to rays cast straight down; only the BVH overlap found them.
  - Variants `caja5-bebidas-consola-lata` and `caja5-bebidas-consola-agua`, plus the default `caja5-bebidas-consola`
    (`CAJA5_CONSOLA`, default `lata`, still to be confirmed by comparing).
  - Say this limit in the report and on the page.
  - If two console drinks are wanted, that is a new holder prop: ask mothership-10. Don't build it unasked.
- **Console gate:** contact gap ≤ 3 mm (the base over the highest support point, the same definition as CAJA5 MANO), BVH
  pairs 0, vertices inside 0 (in the drink's own tilted frame), tilt ≤ 6°. The hollow under the base (the deck's 2–5 mm
  relief) is reported separately, not gated. Then check a 100 % crop of the base edge for a dark sliver.
- **Drinks stand square to the deck,** which falls about 4° toward the dash. They have modelled standing rings: can feet
  Ø 52 mm, bottle feet Ø 54 mm (`PIE`).
- **Console light:** scene 4B's own cab lamps (`luz_costado("cabina", 1)`) plus a 1.5 W soft fill. The camera sits between the
  headrests: (CX+0.03, 0.28, 1.80) → (CX+0.03, 0.97, 1.30), 35 mm.
- **Hand: wrist bone `puno_n`.** It is created at the hand mesh's own wrist, and Héctor's `mano_n` vertex group is renamed onto
  it. The fist is then yawed about the wrist (`girar_puno`).
  - The search tries `GIROS` (0, 20, 35, 50, 65) × `BANDAS` (0.5, 0.6).
  - It keeps the smallest yaw that passes the coverage threshold. The previews picked +50, banda 0.5: middle covered 56 %, cap
    100 %, base 63 %, gap 2.4 mm, 0 pairs, 0 inside, PASS.
  - The threshold is my own, labelled as such in `cubre()`: from the window camera, the middle band is at least 50 % covered
    and the cap and base are at least 50 % visible.
  - For the gap, the hand is its group at any weight plus every vertex within 6 cm of the centroid, because the thumb stands up
    on the palm side.
  - Only `puno()` looks up the `mano_n` group (grepped), so the rename breaks nothing.
- **Console and hand render in separate Blender runs.** `bebidas_consola` raises an error if the hand was already raised
  (`ALZADA`).

## In flight when this was written
Background preview run (16 spp, 960×540, out `tmp/caja7/prev/`, logs `tmp/caja7/prev-consola.log` and `prev-mano.log`):
- run 1: `caja5-bebidas-consola-lata`, `-consola-agua`, `-consola-esc1`;
- run 2: `caja5-bebidas-esc1`, `-esc4`, `-mano`.

Read the `CAJA5 (CONSOLA|MANO|AGARRE|CAMARA|MEDIDA)` lines. The new `CAJA5 MANO` line also prints the hand weight of the vertex
nearest the bottle.

## Preview results (finished 21:11; PNGs in `tmp/caja7/prev/`, not looked at yet)
- **Console, can:** x +0.020, y 0.995, tilt 2.0°, contact gap 0.5 mm, hollow 3.3 mm, 0 pairs, 0 inside: PASS.
- **Console, bottle:** the same spot, tilt 1.7°, gap 0.5 mm, hollow 3.5 mm, 0 pairs, 0 inside: PASS.
- **Scene 1 with the console can:** road 0.00 % covered, r1 PASS; the can shows in 25 px.
- **Hand (+50°, banda 0.5):** gap 2.4 mm to a vertex of hand weight 0.50, so held by the hand, not by the cuff. 0 pairs, 0 inside:
  PASS.
- **Scene 1 with the hand:** r1 0.00 %, PASS; the bottle shows in 0 px.
- **Scene 4:** r1 0.00 %, PASS; the bottle shows in 17 px.
- **Grip coverage:**
  - close-up camera: 56 % of the middle covered, PASS;
  - scene 4's camera: 49 % of the middle covered, cap 100 %, base 78 %, so one point under my own 50 % threshold: FAIL.
  - Options: report it as is, or try yaw +65 for both cameras. In the search log, +65 covered 70–78 % from the close-up camera,
    with the cap 70–100 % visible.
- **Remaining checks:** the wrist crop at +50° and the side-by-side comparison of the two console variants.

## Next steps, in order
1. **Check the preview logs.** If a console variant prints FAIL with no spot, widen `apoyo`'s `busca` or move the start
   (centres x 0.003–0.062, y 0.978–0.998).
   - Compare the can and the bottle side by side (`tmp/caja7/lado.py out.png "label=path" ...`) and keep one, with a reason.
   - The advisor noted that the bottle leans about 18 mm at the cap at a 4–5° tilt; the can leans about 9 mm. The hand variant
     already shows the bottle.
   - Set `CONSOLA_VAR` to the one kept.
2. **Hand checks (advisor):**
   - Look at a 100 % crop of the wrist for a seam or pinch at the cuff at +50°.
   - Confirm the nearest vertex is the hand (weight ≥ 0.1), not the sleeve cuff.
   - Report `CAJA5 AGARRE caja5-bebidas-esc4` from scene 4's camera too.
   - Rerun scene 1 r1 for the hand: the bottle moved about 18 cm inboard.
   - The old `consola-esc1` PASS (0 px) was empty because no drink had been placed; rerun it.
3. **Show the owner frames** before the finals (stance: frames before any long render).
4. **Finals at 64 spp.** Find the resolution and samples the earlier finals used from `tmp/caja6/final.log` or the
   `caja5-props` handoff (probably 1920×1080).
   - Run A: `caja5-bebidas-consola`, `caja5-bebidas-consola-esc1`.
   - Run B: `caja5-bebidas-mano`, `caja5-bebidas-esc1`, `caja5-bebidas-esc4`.
   - Command:
     `/mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/caja5.py)" -- "$(wslpath -w '/mnt/e/Cursor Projects/MTO/blender/escena.py')" <out> <spp> <options> <WxH>`
     (escena.py from the main checkout, which has the assets).
   - Encode the JPGs and minis at the repo's convention (q88 full, q70 mini; see `tmp/caja5/publicar.py`) into
     `docs/design/escenas/utileria/`.
5. **Close crops for the done-check:** a 100 % crop of each drink (console base edge; bottle in the fist). List their paths in
   the report.
6. **Page:** `docs/design/escenas/utileria/index.html`, section `s-caja5`, lines about 50–56. Show the console again as a
   figure next to the hand, and the owner picks. Rewrite the text: the console holds one drink and why; the bottle is in his
   fist now. Spanish, no AI tells.
7. **Checks** (all from the last round):
   - CAJA5 MANO;
   - scene 1 r1 for hand and console;
   - scene 2 r1 and r3: run `caja5-elegida-esc2`, `CAJA5 MEDIDA` lines;
   - `~/projects/visual-lab/scripts/revisar.sh <still>` on each new still;
   - `python3 -I ~/projects/visual-lab/web/scripts/slop-check.py docs/design/escenas/utileria`;
   - `revisar.sh docs/design/escenas/utileria` (web, ≤ 3 MB at 390). If it goes over 3 MB, ask mothership-10 which image to
     demote; don't decide.
8. **Add a references.md row** (`docs/design/references.md`, caja5 rows around line 221). Reference named: a real W463 console
   with a drink on the tray ahead of the selector; a passenger seen through a car window holding a bottle at the chest, fist
   round its middle.
9. **Commit on `cc/nerddrone`** (guide `~/.claude/guides/commits.md`). Merge only on the owner's word.
10. **Report:** `/home/black/.cache/cc-deck/reports/all/downbaddrone-1794707689.md`, at most 3 lines plus paths, `gotchas:`
    lines, `paths:` line, `model: opus effort: high`, `verdict: …`. Then SendMessage to exactly "mothership-10", one line
    pointing at it.

## Open questions for the owner (on the page)
- Console (one drink: can or bottle) or the hand.
- Whether one console drink is enough, or a clip-on holder prop is worth building.

## Findings
Site-specific notes are above (console geometry, wrist bone). For visual-lab, these go in the report as `gotchas:` lines:
- Rays cast straight down to find a resting spot miss near-vertical faces (a shifter boot lip, a dash lip) → a BVH overlap of the
  prop's outline against the faces in a box round the spot found them (12–112 pairs).
- A label made with `primitive_cylinder_add` plus Generated-coordinate wrap gets caps painted with the label's edge band, which
  tints a clear bottle → delete the cap faces (bmesh) and mix in a pale Backfacing colour.
- A rig whose hand mesh sits about 12 cm from its hand bone → add a child bone at the mesh's own wrist (centroid of the
  half-weighted vertices) and move the vertex group onto it; then rotating it turns the hand in place.
- A fingerless paddle hand reads as gripping when the fist covers the bottle's middle band from the camera → rays from the camera
  over the bottle's silhouette, per height band, measure it (yaw 0: 24 % → yaw +50: 56 %).
- A rest-flatness test on the full 66 mm disc failed on a 4° deck with 2–5 mm relief → stand the drink square to a fitted plane on
  its real standing ring (Ø 52–54 mm), and gate on the contact gap with the hollow reported apart.
- The PreToolUse hook denies any Bash command containing `sleep`, Monitor commands included → wait with
  `scripts/esperar.sh --tope N log <file> <regex>` under `run_in_background`.

## Suggested skills
`director` (still framing), `frameref` (look), and `eagle-eye` only if a revisar FAIL needs a look
(`~/projects/visual-lab/cross-tool/skills/eagle-eye/SKILL.md`).

## Round 2, bussindrone, 2026-11-14 22:05: steps 1-3 done, stopped before the finals
Still uncommitted (`git diff blender/caja5.py`). Logs: `tmp/caja7/g65.log`, `tmp/caja7/cam.log`.
- **Console drink kept: the bottle** (`CONSOLA_VAR` default `agua`). In the 16 spp previews its body reads at luma 92 against
  the console's 14. The black can reads at 43, its lower tenth at 0 (merged with the console), and its silver lid reads as a
  second shift knob (`tmp/caja7/lado-consola.png`).
- **Console camera now `alta`** (`CAM_CONSOLA`, `cerca_consola(cam="alta")`): (CX+0.03, 0.58, 1.86) → (CX+0.02, 0.99, 1.27),
  30 mm. The old camera between the headrests hid the drink's base behind the shifter, so no crop could show the contact.
  With `alta` the bottle's rounded base shows on the left of the knob (judgment, not verified by a tool); `lado` hid more of it (`tmp/caja7/lado-cam.png`,
  `lado-base.png`). revisar on the `alta` still: banding 0.8 % pass.
- **Scene 1 r1 with the console bottle:** road covered 0.00 %, PASS; the bottle shows in 44 px.
- **Hand yaw, one extra try (+65) as the brief allowed. Neither yaw passes from both cameras, so the code keeps the
  search's +50:**
  - +50: close-up middle 56 %, cap 100 %, base 63 % PASS; scene 4 middle 49 %, cap 100 %, base 78 % FAIL.
  - +65: close-up middle 68 %, cap 100 %, base 33 % FAIL; scene 4 middle 63 %, cap 100 %, base 56 % PASS.
  - +65 CAJA5 MANO: gap 2.2 mm to a vertex of hand weight 0.50, 0 pairs, 0 inside, PASS; scene 1 r1 0.00 % PASS.
  - Pinning +65 would need `GIRO = os.environ.get("CAJA5_GIRO", "65")`: the search's own estimate passes +50 first.
- **Wrist crops** (`tmp/caja7/crop-puno-g50.png`, `crop-puno-g65.png`): no tear or pinch at the cuff at either yaw. A
  skin-coloured patch shows between the thumb and the bottle at both yaws; not identified (palm or another body part).
  Not verified by a tool.
- **Frames sent to mothership-10 for the owner.** Next: steps 4-10 above, once the owner answers. Run A's console stills now
  use the bottle and the `alta` camera by default.
