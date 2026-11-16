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

## Road pass road3 (2026-11-16): the curve, the fog back, highway signs

`MONTAJE_CAMINO=road3` = road2 + three modules, all exec'd by `camino_mx140.py` in its namespace (road2 stays reproducible as `noche`):
- `blender/camino_curva.py`: ref 2's left bend as one post-build pass, only beyond S0 = 40 m ahead of the truck, so the truck, the cameras, the
  lane and `escena.json` do not change (y < 40 maps to itself bit for bit). An arc of R = 220 m from y 40 to 260 (57 degrees), straight after;
  x stays the offset along the normal, so lanes keep their width. Long strips are cut to 4 m along y and their vertices mapped; the shaders read
  Object-space x and y, so every bent mesh carries its straight position in a `p0` attribute and its materials read that instead; wires map
  their points; buildings, signs and lamp empties move and take the heading as yaw; the geometry-nodes scatters get a rotate-then-move node
  group after their join, and drop instances on the inside of the bend beyond 0.45 R. Check, CPU only: `blender.exe -b --python
  blender/camino_curva_test.py` (maps y < S0 to itself, keeps lane width, continuous at S1, and the node group agrees with the mapping; it
  caught a first version that rotated the instances about the world origin). Holds for stills: `mundo` scrolls 192 m over a loop, so a clip
  would need the bend to scroll with it (not done).
- `blender/camino_letreros.py` (everything is `e3_*`, built straight, bent with the rest): an overhead sign over our lanes at y 44 (up arrow,
  "La X we") and a roadside two-post guide sign at (8.6, 33) ("La X we", "12 km"), SCT style (green, white border and letters, Blender's
  built-in font, no logos, weak emission as retroreflection, no fog scatter); yellow chevron squares with a black "<" on the outside of the
  bend from y 58 every 12 m (1.7 m, oversized so they read at 100 m); the road lamp collection instanced again 32 m after each existing lamp
  (every 32 m from y 104) with a glowing ball on each far lamp head; a plain footbridge at y 128. Everything built here is hidden in the
  viewport like road1/2's objects (the placement ray probes skip it).
- `blender/camino_niebla.py`: the fog's density and every Cycles setting that was tried, overridable for one still with
  `NIEBLA_PRUEBA="dens=0.006;pasadas=RGB"`; a render_pre handler prints the settings in force before each render (the log line `CAMINO render:`).

Fog (esc3, one still per variant, `~/cc-out/mto-pantalla/3d/road3/`): the blotches are the denoiser's, not sampling noise. Kept: fog density
0.0028 → 0.005, the `ancha` areas scatter in the fog again (glow back, no twin lights needed), and `denoising_input_passes = RGB` (no
albedo/normal guides: in fog they are the surface behind it and mislead the denoiser).
- Tried and did nothing: volume sampling MIS → equiangular, clamp indirect 10, 16 → 64 spp with the guides (the blotches stayed). A fog-only twin
  spot instead of the areas had less blotching and a weaker glow (that branch is removed from the code).
- Raw (no denoise) the fog is sparse fireflies, so RGB-only works from a clean input. Its cost: at 16 spp it smears the road's cracks and the
  Mercedes; at 64 spp it is sharp (a still takes 25-31 s either way, the time is the scene build). 64 spp is the recommended quality (`road3/final-64spp/`; the 16 spp like-for-like set is `final-16spp/`; the sheet
`road2-vs-road3.jpg` has road2 16 spp, road3 16 spp and road3 64 spp; the variants side by side: `fog-variantes-esc3.jpg`, whose panels 2 and 6
are the older scene at density 0.0075, before the signs).
- OptiX with all guides (`dnr=OPTIX;pasadas=RGB_ALBEDO_NORMAL`) keeps the detail and the glow but leaves mottling on the Mercedes in esc3
  (road3/t2-optix); OptiX RGB_ALBEDO adds fireflies; OptiX RGB smears like the OIDN one.
- Two Blender "hangs" (one of 30+ min) were Blender and ComfyUI sharing the GPU, not the scene: run `~/.claude/scripts/gpu-busy` first.

Reading the three views (not measured; the sheet is `~/cc-out/mto-pantalla/3d/road3/road2-vs-road3.jpg`): the overhead sign and the guide sign
read at 16 spp (computed from the lens, not measured on the image: "La X we" caps are about 13 px on the gantry in esc3 at 46 m and about 14 px on
the guide sign in esc5 at 32 m); the chevrons read as a yellow
row in esc3 and esc3-adelante; in esc5 the truck hides the road beyond 40 m, so the bend shows only as the median and the left lines turning
away and the lamp balls. The lamp row and chevrons beyond 120 m sit behind the truck in every hold: the curve is a background cue, as the
holds are framed.
- revisar.sh exit 0 on the three stills: banding at most 0.2 %, highlight clipping at most 0.58 %; no OIDN errors in the log.

To render road3 (one Blender at a time; run `~/.claude/scripts/gpu-busy` first, ComfyUI shares the card):

```bash
MONTAJE_PANTALLA=b MONTAJE_PANTALLA_LUZ=ancha MONTAJE_CAMINO=road3 WSLENV=MONTAJE_PANTALLA:MONTAJE_PANTALLA_LUZ:MONTAJE_CAMINO \
  /mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/montaje.py)" -- \
  "$(wslpath -w blender/escena.py)" <out_dir (Windows)> 64 p3-b-ancha-esc3,p3-b-ancha-esc3-adelante,p3-b-ancha-esc5 960x540
```

Add `CURVA_PRUEBA=recta` (and to WSLENV) for the straight road, `CURVA_PRUEBA=vista` + the option `curva-arriba` + `wb` for a top-down layout
check (not used for the final: Workbench takes the GPU too).
- Missing: the curve in a clip (the bend does not scroll with `mundo`); vegetation along the outside of the bend is the old scatter; the footbridge
  is a box silhouette at 128 m that none of the three views shows; fog-lit shop windows in esc5 still read near white.
