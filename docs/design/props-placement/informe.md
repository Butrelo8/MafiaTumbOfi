# Props and placement: report (2026-11-13, run `touchgrasdrone`)

Brief: mothership `docs/queue/2026-11-13-mto-props-placement.md`. Done-check: 3 `.md` files plus this one; `stills/` holds 12
stills and `medidas.tsv`.

## Pass 2: the owner's picks applied (2026-11-13, run `nocapdrone`)

Picks (11-13 20:04): B in every scene, no PURA MT marquee, the real roof light bar, underglow stays amber, a better strawberry
in one swappable file, no cattle horns and a gold MT emblem on the hood instead. The page now shows the four B scenes, then each
new piece kept next to the variants it beat: `E:\Cursor Projects\MTO-touchgrasdrone\docs\design\props-placement\index.html`.

| still | rule 1 (zone covered, ≤ 2 %) | rules 2-3 (props that read, budget) | rule 4 (zone light vs lit prop) |
|---|---|---|---|
| pp1-b | 0.79 % PASS | 1 (P3) of 3 PASS | n/a (no lit prop) |
| pp2-b | 0.0 % PASS | 1 (P9) of 4 PASS | 223.9 vs 54.0 PASS |
| pp4-b | 0.0 % PASS | 3 (P1, P7, P9) of 4 PASS | 57.5 vs 23.1 PASS |
| pp6-b | 0.0 % PASS | 2 (P1, P2) of 3 PASS | 45.4 vs 10.4 PASS (pass 1 tied, 45.4 vs 45.1) |
| pv-6-xlp (variant) | 0.0 % PASS | 2 of 3 PASS | 45.4 vs 59.0 FAIL |

- **Light bar = the factory G 63 AMG 6×6 roof lamps** (refs [12b], [12c]): one LED lamp in each pocket of the roof spoiler, five
  reflector cups behind a clear lens, white, each throwing a spot 14 m ahead. The model already had the pockets, unlit
  (probed x ±0.515–0.695 m, z 2.156–2.198 m). The owner confirmed this over a Brabus XLP 800 two-tier copy (a W465 part), which
  out-lights the plate in scene 6.
- **Strawberry** = `blender/props/fresa.glb` from `blender/fresa_charm.py` (fruit style: 150 seeds in pits, eight sepals on the
  shoulders, clear-coated red). Kept over enamel (reads as red reflections) and felt (washes pink-white under the cab light).
  Swap contract in `props.md`; `PP_FRESA=<path>` tries a model without copying it.
- **MT emblem**: Grenze Gotisch ExtraBold (OFL, `blender/fuentes/`), brand gold as polished metal, about 14 cm letters standing
  bolted on a black plinth at the hood's front edge. At scene 6's low camera it covers 0.088 % of the frame, under rule 2's
  0.1 % read line (size 0.15 gave 0.039 %, 0.22 gave 0.09 %): there it is a gold glint, and it reads in the close-ups. A flat
  badge is edge-on from that camera (`pv-emblema-plano`).
- The probe now looks through glass: a prop behind the windshield counts as covering the road in scene 1 (the emblem is hidden
  there by the front heads).
- revisar image: 0 FAIL on all 13 stills; slop-check 0 to review; revisar web passes at 390 and 1440 (0.36 MB).
- Not done: scenes 3 and 5, 9:16. #33, #34 and the scene-4 light stay open. 16 spp previews went to the owner before the final run.

Run (an empty option list renders the picks, `FINALES` in `props_placement.py`):

```sh
/mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/props_placement.py)" \
  -- "$(wslpath -w "/mnt/e/Cursor Projects/MTO/blender/escena.py")" 'E:\Cursor Projects\MTO-touchgrasdrone\tmp\pp2-final' 64 "" 1920x1080
# variants by name: pv-barra-xlp,pv-6-xlp,pv-emblema-plano,pv-fresa-resina,pv-fresa-peluche (the last two need
# tmp/fresa/fresa-<style>.glb from blender/fresa_charm.py -- <out.glb> <style>)
uv run -q --with numpy --with pillow python -I scripts/props-medir.py tmp/pp2-final docs/design/props-placement/stills/medidas.tsv
uv run -q --with pillow python -I scripts/props-hoja.py
```

Pass 1 below is history: its A stills and close-ups were removed from `stills/` (they are in d4316ca).

## Where to look

- Side by side for the owner (A | B | close-up per scene, rule numbers under each still):
  `E:\Cursor Projects\MTO-touchgrasdrone\docs\design\props-placement\index.html`
- The same as one image per scene: `E:\Cursor Projects\MTO-touchgrasdrone\docs\design\props-placement\lado-a-lado\`
- References: `referencias.md` (22 photos looked at, the gap stated). Rules: `reglas.md`. Props: `props.md`.
  Numbers: `stills/medidas.tsv`.

## The three strongest new props

1. **P10 marquee sign "PURA MT"** on top of the roll bar. It is the bed's one lit peak, 1.0 % of the scene-2 frame, and the
   stickers stay 0 % covered with either caja3 bed.
2. **P1 two-tier LED light bar**, the part made for the G63 6×6. It caps scenes 6 and 4. In 6 it has to be a dim DRL: at amber
   2.5 it out-lit the plate (66.5 vs 45.4 total light); at 0.9 the two tie (45.1 vs 45.4).
3. **P9 outline bulbs.** They draw the black bed's shape at night without lighting its faces. On the roll bar alone (B) they frame
   the marquee.

## The rules, one line each (`reglas.md`)

1. Sight lines: new props cover ≤ 2 % of each scene's working part (stickers, windows, plate and lenses, mirror and road).
2. Scale: a prop covers ≥ 0.1 % of the frame at the scene camera, or is self-lit, or it is close-up dressing only.
3. Clutter budget: at most 3 new props that read in cab views (1, 6) and 4 in exterior views (2, 4).
4. The call to action stays brightest: the zone's total light beats every lit prop's.
5. One silhouette, one peak: the load breaks the cab line once, and the roof carries at most one item.
6. Layers from the camera: the foreground frames and is darker; the midground is the working part.
7. Two light colours per frame plus warm practicals; outline lights trace edges and do not fill faces.
8. It rides: everything is strapped or bolted; nothing sits loose on the roof or the hood.

Measured per still (`stills/medidas.tsv`). A fails where it was meant to: 1A covers 3.4 % of the road (rule 1); 4A has 6 reads
against a budget of 4 (rule 3); 6A's white bar out-lights the plate (rule 4). Every B passes 1–4. Two caveats: 6B passes rule 4 by
a tie, not a margin. In scene 2, A and B both pass 1–4, and B's gain is rule 5, which is judged.

## Questions for the owner (also on the page)

1. Per scene: A, B or a mix? Answer with one letter per scene, for example 1B 2B 4B 6B.
2. Does the PURA MT marquee go on the roll bar? (a) yes, (b) no. It works with caja3 A and B, so #34 stays open.
3. The roof light bar in scene 6: (a) off, (b) a dim amber DRL that ties with the plate, or (c) cut.
4. Underglow colour: (a) amber/gold, the brand colour, as rendered, or (b) purple, like the Renotaxi (ref 17).
5. Religious items (a rosary on the mirror, a Virgin on the dash): (a) no, the strawberry charm stays, or (b) yes, one: which?
6. Cattle horns on the hood: (a) no, or (b) yes. The searches tie them to cartel trocas.

## Departures and limits

- Scenes rendered: 1, 2, 4, 6. Scene 3 gets only a rosette on the driver's mirror, which fits both readings of #33; no still was
  made. Scene 5 sees only the hood.
- The scene-4 light pick stays open: the stills use the fill (A). The self-lit props (bar, bulbs, marquee, underglow) read under
  either choice. Judged, not rendered both ways.
- #34 stays open. The floor pile is caja3 A, and the new bed props sit on the roll bar and rails only. A probe of scene 2 with
  caja3 B (`tmp/pp-camab`, 960×540, 16 spp) also shows 0 % sticker cover.
- No 9:16 versions. The previews (16 spp, 960×540) were checked before the final run but were not shown to the owner first; the
  final run took about 15 min.
- The scene-1 close-up has a 3 cm fringe and a 7 cm charm string. The final 1B has 2.5 cm and 4.5 cm, shortened to bring the road
  cover down from 2.05 % to 1.7 %.
- P4, the dash pennant, sits behind the front heads at the scene-1 camera (0.008 % of the frame): cut by rule 2.
- The stills use Windows fonts (Impact) for the lettering, as the earlier passes did; the build needs free fonts.
- Not verified beyond the stills, the probe and revisar: revisar image is 0 FAIL on all 12 stills (banding and clipping only;
  there is no ref). slop-check is 0 to review on the page; revisar web passes at 390 and 1440 (0.39 MB).

## Run

```sh
/mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/props_placement.py)" \
  -- "$(wslpath -w "/mnt/e/Cursor Projects/MTO/blender/escena.py")" "$(wslpath -w tmp/pp-final)" 64 \
  pp1-a,pp1-b,pp1-cerca,pp2-a,pp2-b,pp2-cerca,pp4-a,pp4-b,pp4-cerca,pp6-a,pp6-b,pp6-cerca 1920x1080
uv run -q --with numpy --with pillow python -I scripts/props-medir.py tmp/pp-final docs/design/props-placement/stills/medidas.tsv
uv run -q --with pillow python -I scripts/props-hoja.py
```
Needs `tmp/utileria/calcas3/` and `placa-veracruz.png`, copied from the nerddrone worktree (or rebuilt with `calcas_arte.py` and
`placa_veracruz.py`). Never pass `all`: it renders every older utileria option, the destructive glovebox cut included.
Files are untracked on `cc/touchgrasdrone`, which was fast-forwarded to `cc/nerddrone` 6d59b26 for the scene scripts.
