# Pantalla móvil 3D: the screen truck as a found model (oopdrone → sweatingdrone, 2026-11-15/16)

The owner chose the 3D road for the screen truck (board #47). The livery design, its measurements and the four open
questions are on branch `cc/rizzdrone`, in `docs/design/pantalla-movil.md`. This note covers how the 3D truck is made and
rendered.

## Source: found, not generated

- **Model:** "Mitsubishi Fuso Canter" by Raed Almaharmah (sketchfab.com/raedalmaharmah6), **CC BY 4.0**. It is a
  light-duty cabover box truck, the ELF/NPR class of the references, at real scale (tyre radius 0.38 m), with dual rear
  wheels.
- **Fetched from:** the Objaverse mirror of the Sketchfab upload,
  `huggingface.co/datasets/allenai/objaverse/resolve/main/glbs/000-063/2b58376d6aaf4641adf30d4c9044de74.glb`. It has
  129,583 triangles, the same as the Sketchfab API's faceCount for this uid. It cost $0.
- **Credit line for the site:** "Mitsubishi Fuso Canter" de Raed Almaharmah, CC BY 4.0, modificado. It is also recorded
  in `blender/assets/sketchfab-creditos.txt` and `blender/assets/pantalla3d/LICENSE.txt`.
- Since a usable model turned up, nothing was generated: no concept image and no image-to-3D step.

## Chain

1. `blender/pantalla_3d_prep.py` turns the glb into `assets/pantalla3d/canter-base.blend`. It removes the ribbed cargo
   box, turns the truck to face +Y, sorts the mesh into paint / tyre / chassis / tail lamp / headlamp slots, and puts the
   origin on the floor at the old box's back face. The .blend is untracked. Other worktrees read the shared copy at
   `~/cc-out/mto-integracion/assets/pantalla3d/`.
2. `blender/pantalla_3d.py` builds everything that sits on top of that base:
   - the matte black LED box, 2.31 × 5.26 m, from z 0.92 to 3.40;
   - the side screen, 3.6 × 2.025 m (16:9), with an LED pitch of about 11 mm;
   - the rear screen, 2.0 × 2.05 m, showing "PRÓXIMAS FECHAS / MUY PRONTO";
   - the A/B/C livery;
   - the owner's three box lights: `led` (the screens alone), `tira` (a cool-white strip outlining the box) and `ancha`
     (a wide lamp bar on top that washes the side and the road).

   The script replaces utileria's `pantalla_c` stand-in and keeps its signature and anchor.
3. `blender/montaje.py` loads it only when `MONTAJE_PANTALLA` is set (commit 31073d1). Without the variable, the build
   does not change. Each option is named `p3-<a|b|c>-<led|tira|ancha>-<esc3|esc3-adelante|esc5>`.
   `esc3-adelante` is the scene 3 hold with the truck 3.5 m further ahead, rizzdrone's stand-in for the 3→4 beat.

To render one option:

```bash
MONTAJE_PANTALLA=b WSLENV=MONTAJE_PANTALLA /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 \
  --python "$(wslpath -w blender/montaje.py)" -- "$(wslpath -w blender/escena.py)" <out_dir (Windows)> 48 \
  p3-b-led-esc3,p3-b-led-esc5 960x540        # add "wb" for Workbench
```

## Renders

These are in `~/cc-out/mto-pantalla/3d/`:
- the Workbench pass of all 15 combinations, in `wb/` (`hoja-wb.jpg`);
- the Cycles stills at 48 samples, 960×540;
- the sheet, `hoja-3d.jpg`.

The set is A/B/C with the `led` light × 3 views, plus B with `tira` and `ancha` × 3 views.

revisar.sh found no FAIL on any of the 15 stills. Banding is at most 0.3% (threshold 5%). Highlight clipping is at most
1.47%, in `p3-c-led-esc3-adelante`, from the bulbs. The per-still table is `revisar/resumen.tsv`.

The `ancha` stills went through a second pass at 192 samples. Even so, the fog that the lamp bar lights shows blotchy
denoiser patches. The time per frame did not change from the 48-sample run. Adaptive sampling stopping early would
explain it, but that cause is not verified. If `ancha` is picked, it needs a fog or sampling fix.

### What the renders show

This section is a reading of the stills by eye. No tool measured it.

- **C reads in all three views.** At the 3→4 beat, the bulbs outline the rear screen. At the scene 5 hold they still
  show as separate dots at 960×540, not as a lit line, which is better than rizzdrone predicted. This one is measured:
  in `p3-c-led-esc5` (y 121, x 386–572), the top rear row resolves into 12 bulbs, one per expected position, at about
  15 px pitch, with luma falling from 254 to about 66 between them.
- **B: the gold frame reads at the scene 5 hold**, because the G63's headlights light it. At the 3→4 beat it is a dim
  line. The rear MAFIA TUMBADA band reads at the 3→4 beat and at scene 5.
- **A's box disappears.** At the 3→4 beat it is a black slab, and at scene 5 it is a flat grey one.
- **Box light:**
  - `tira` draws the box's silhouette at the 3→4 beat and at scene 5, and leaves the night alone.
  - `ancha` washes the road and the G63 grey and flattens the night, and it brings the fog blotches described above.
- **Open questions:**
  - Question 1 (scene 3 crop): the scene 3 hold sees only the front part of the side screen, cut at the top. B's side
    header shows only as "…TUMBADA" at the top edge, while C's bulb rows read along both edges.
  - Question 4 (cab): only a sliver of the cab shows, beside the box at the scene 3 hold. The cab colour barely matters
    in these views.

## Gotchas met here

- A Cycles frame whose OIDN denoise runs out of memory is still saved, but undenoised and grainy, and the run carries
  on. Grep the log for `OIDN error` and render that frame again.
- A Windows `blender.exe` started from WSL survives a WSL crash, and then hangs with nothing written: one core busy and
  a working set of 70 MB. Check `tasklist` before rerunning.

## Road pass road1 (2026-11-16)

`MONTAJE_CAMINO=1` (with `MONTAJE_PANTALLA=b MONTAJE_PANTALLA_LUZ=ancha`) runs `blender/camino_mx140.py`: the road as México 140 in the
owner's Street View refs (`~/cc-out/mto-pantalla/refs/road/`, reference only). Stills (`p3-b-ancha-esc3`, `-esc3-adelante`, `-esc5`,
960×540, 16 samples) and the warm1-vs-road1 sheet: `~/cc-out/mto-pantalla/3d/road1/before-after.jpg`.
- Layout in x (m): our 2 lanes ±3.55 (mundo.py's lines), shoulder, NJ barrier −4.65..−5.25, oncoming 2 lanes −6.05..−13.05 with
  yellow/dashed/white lines, worn-asphalt shoulders with dirt, poles (wood right, concrete left) with sagging wires, straw clumps among the green.
- The brief implied, not named: night became overcast day (procedural sky), the road lamps are off, and the right guardrail, the
  night delineators and the cat's eyes were removed from the render.
- revisar.sh exit 0 on all three: banding 0.3 / 0.8 / 0.0 %, highlight clipping at most 0.57 %.
- Missing: gas-station canopy, pedestrian bridge, oncoming traffic; near tree crowns are lumpy icospheres, not the refs' trees; less
  dry pasture than refs 2 and 5. In daylight the `ancha` lamp barely reads. The new noise (ground, barrier, shoulders) does not repeat
  over the 192 m loop: fine for stills, breaks mundo.py's loop rule for a loop clip.

## Road pass road2 (2026-11-16): night, with a roadside

`MONTAJE_CAMINO=noche` (same other variables) keeps road1's road but skips `dia()`: the night HDRI, moon, fog and road lamps stay, the
cat's eyes come back, and the lamp poles move 1 m out of the new shoulder. The right guardrail and the left delineators stay removed.
`blender/camino_edificios.py` adds, in a seeded Python instancer with no period (kits are shared meshes; colour and lit/dark per
instance in Object Color): lit shops of one or two storeys, barda walls, one generic gas-station canopy at (15.5, 62) with the only new
area light, dark silhouettes with a few lit windows on the left, and one oncoming car with one pair of headlights beyond the barrier.
Signs and windows have `visible_volume_scatter` off. Stills and sheet: `~/cc-out/mto-pantalla/3d/road2/warm1-road1-road2.jpg`.
- Fog blotches, one still each (esc3, 16 spp): A, adaptive sampling off, changed nothing (mean pixel difference 0.011 of 255).
  B, `visible_volume_scatter` off on the two `ancha` areas, removed the blotches; it is kept, and it also drops the lamp's fog glow
  near the truck (mean luma of the sky/fog crop 69 → 59). The lamp's energy is unchanged.
- revisar.sh exit 0 on the three stills: banding 0.0 %, highlight clipping at most 0.57 %. No OIDN errors in the log.
- Missing: the curve (road3), the footbridge, vegetation work, seamless tiling; the shop windows in esc5 read near white (emission 1.3);
  the right shoulder's dirt strip is still orange under the warm lights; no traffic besides the one oncoming car.
