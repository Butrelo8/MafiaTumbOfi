# The world around the truck: Night B (2026-11-14, run yeehawdrone)

The owner picked direction B ("Húmeda, neblina") of the world audit at 19:13 (`~/cc-out/mto-world/plan.md`). This round puts
that world into the repo's scene code. `blender/mundo.py` builds it, and `escena.py`'s `mundo_render()` calls it for every
preset with a `cycles` block in `src/lib/escena.json` (only `noche` has one). So every scene script gets the world:
`utileria.py`, `caja3.py`, `props_placement.py`, `storyboard.py`, `transicion` and `temblor.py`. The GLB export does not.

## What is in it (plan fixes 1–9, B column)

- Road: asphalt_02 at 3 m per tile, with wheel paths, oil bands, 7 m patches, cracks and a 40 m macro mask (R3).
  - Shoulders in older, lighter asphalt and a gravel strip where the delineators stand.
  - Markings as geometry, to NOM-034:
    - right edge solid white, left edge solid yellow
    - lane line dashed, 13 dashes per loop (4.92 m on, 9.85 m off)
    - studs every 32 m
- Verge: green sparse_grass ground with no more darkened asphalt. Plants, by distance from the road:
  - a mowed strip 3 m wide past the gravel
  - guinea-grass height to 14 m
  - shrubs, pachira and fern to 40 m, with sparser grass
  - tree crowns from 22 to 260 m
  - nothing between 260 and 700 m, then the old hill ring under fog
- CFE pole line on the left verge: x −9, 11 m high, every 48 m, three wires (R1).
- Sky and moon: kloppenheim_07 rotated so its brightest point sits at the moon light's azimuth, strength 0.25. The moon light
  is softened to 18° for the overcast.
- Fog: a box 82 m high (Principled Volume 0.0028, warm grey, anisotropy 0.45). Its values are Cycles-only, in
  `escena.json` noche.cycles. The page's `niebla` (FogExp2) is a different unit and was left alone.

## Rules the code keeps

- **Loop.** The world moves 192 m per loop and frame 192 must equal frame 0.
  - The plant scatters are one 192 m strip copied along y.
  - The road wear reads y wrapped on a circle 192 m round, so the noise repeats with the loop.
  - Dashes (192/13), studs (32 m) and poles (48 m) all divide 192 m.
  - Not verified on a clip yet: this round made stills only. Run `eagle.sh --loop` on the first test loop.
- **Probes.** The props scripts place and measure with viewport ray casts. The new pieces the old world did not have (fog,
  plants, poles, markings) are `hide_viewport`, so those rays don't see them. Check: the `SONDA` lines of props_placement
  were identical before and after.
- **Asphalt.** The it3 values (tint 0.62, wheel-path roughness 0.42) clip scene 6's headlight pool by 0.61 %. The kept
  values are tint 0.62 with roughness 0.6.

## Asphalt (variants measured on holds 2, 4, 5, 6; `medir.py` floor, revisar clipping on scene 6)

```
variant              tint  wheel-path rough  floor 2 / 4 / 5 / 6          scene 6 clip hi
it3 (audit)          0.62  0.42              7.37 / –    / 6.02 / 5.48    0.61 % FAIL
it4 (plan)           0.50  0.60              6.97 / 9.29 / 5.56 / 5.26    0.00 %
it4, normal 2        0.50  0.60              6.95 / –    / 5.54 / 5.82    0.00 %   (cracks 0.2)
more cracks          0.50  0.60              6.96 / 9.33 / 5.59 / 5.23    0.00 %
0.56 matte           0.56  0.60              7.21 / 9.51 / 5.97 / 5.41    0.00 %
kept: 0.62 matte     0.62  0.60              7.48 / 9.70 / 6.39 / 5.53    0.00 %
audit B column       0.62  0.42              7.51 / 9.57 / 6.50 / 5.09
```

The clipping came from the glossy wheel paths, not the brightness: the matte paths alone bring it to 0.00 %. The plan's
darker tint 0.5 cost 7–14 % of the floor detail for nothing. A stronger normal map and more cracks do not register at 960 px
under the headlights.

## Placement (owner's rule, 22:36)

The pole line is a taste call. `blender/colocar.py guardar <out.blend>` saves the night scene with only `w_postes`
selectable (the wires ride on it), plus the cameras of holds 4 and 6. Move the line in X or Y, or scale it in Z, then save.
`colocar.py leer` prints the `TENDIDO` values to paste into `mundo.py`. The line stays periodic every 48 m. The default
phase is 36 m, the audit stills the owner picked from. At phase 0, a pole rose out of the bed in hold 4.

## Running it

The world's assets are CC0 Poly Haven files kept in `~/cc-out/mto-world/assets/polyhaven-2026-11-14/`
(`docs/licencias/mundo-polyhaven.md`). The holds render through props_placement:

```bash
/mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/props_placement.py)" \
  -- "$(wslpath -w blender/escena.py)" <out_dir (Windows)> 32 pp1-b,pp2-b,esc3-espejo,pp4-b,esc5-abre,pp6-b 960x540
```

A worktree needs `blender/assets/camion` and `blender/assets/reparto` from the main checkout. Use Windows junctions
(PowerShell `New-Item -ItemType Junction`) and remove them with `cmd /c rmdir`, never `rm -rf`. It also needs
`tmp/utileria` and `tmp/fresa` (the screen faces, stickers and strawberry).
