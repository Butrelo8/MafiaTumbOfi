# Inside → outside: one camera move from the cab out over the truck (2026-11-12)

Prototype quality: rough poses, rough materials, preview render. The point was a scene that builds and renders end to end.

## Run
```bash
/mnt/e/Blender/blender.exe -b --factory-startup --python-exit-code 1 --python "$(wslpath -w blender/escena.py)" \
  -- transicion "$(wslpath -w "$PWD/<out_dir>")" <w> <h> [samples=16] [first=0] [last=191] [step=1]
ffmpeg -framerate 24 -i <out_dir>/f_%04d.png -c:v libx264 -crf 16 -pix_fmt yuv420p <clip>.mp4   # encode is a separate step
```
`--python-exit-code 1` matters: without it Blender exits 0 even when the script raises.
Code: `blender/transicion.py` (called by the `transicion` mode of `blender/escena.py`). 192 frames, 8 s at 24 fps.

## The shot
- **Start (f0):** between the rear headrests, 20 mm. The manager (driving) and Héctor from behind, the road through the windshield.
  Reference: the between-the-seats car interior of *Children of Men* (2006). Kept: both front heads frame the windshield.
  Changed on purpose: the camera pushes forward instead of turning.
- **Exit (f40–f80):** between the two heads and out through the windshield just under the mirror (z 1.8–1.95).
  Reference: Fincher's camera that passes through solid things (*Panic Room*, *Fight Club*). Here it passes through glass only.
- **End (f191):** high behind the bed, 28 mm. The truck "drives on" beneath the camera, so the camera never turns
  around. Alexandro and Diego face the camera with the guitars, the cab and the headlight pool beyond them.
  Reference: a night drone tail-chase of a pickup.
- End frames compared in blocking stills: **behind (kept)** · front three-quarter high (truck small, bed hidden by the cab)
  · rear-left three-quarter (good in 16:9, but a 5.9 m truck seen side-on does not fit 9:16).

## What the build does that the plain scene does not
- **Glass:** the model's windshield, rear window and four door/quarter windows are opaque charcoal sheets (`extra_details_carcoal`).
  `vidrios()` finds them by shape (flat, ≥ 85 % of the area facing one way, filling ≥ 60 % of its box measured along the car's axes,
  inside the window band) and gives them a thin glass (transparent + Fresnel glossy). It finds 8 panes + the one real glass.
  This only runs in the `transicion` mode; the stops (`hoja`, `lote`) still have an opaque windshield.
- **Figures:** `blender/assets/reparto/*.glb` are unrigged (one mesh each, 290k–480k tris, 1 m tall, facing −Y). Each gets a
  13-bone armature and inverse-distance weights with region masks (legs, arms, head). Bone heat was not tried.
  Scale 1.25. Landmarks per figure are in `FIG` (read off horizontal slices of each mesh).
- **Poses:** cab pair face +Y (turned π), hips 0.07 m over the cushion (z 1.08). Manager's hands aim at the wheel (his arms are too
  short to reach it, so they stop short). Héctor's hands on his lap, head turned a little to the driver. Bed pair on 0.40 m cases
  (floor z 0.93, wall top 1.61), backs to the cab, guitars on their laps.
- **Idle motion (periods divide 240):** head nod 20 f, hip bob 20 f, strum 10 f, fretting hand 40 f, steering 120 f.
- **Lights:** dome light (4 W) and instrument glow (25 W) inside the cab, a roof-bar spill (90 W) over the bed.
- **No front headrests (v2):** the toy heads are ~0.55 m deep (cap brim included) and sat ~0.2 m inside the headrests on
  every frame, so the headrest wings poked through the back of both caps and changed shape with the nod (the owner's
  "artifacts on the hat"). Leaning the spine forward to −0.10 still left 1428 overlapping triangle pairs. `sin_cabeceras()`
  deletes the faces inside two boxes (x 1.15–1.52 and 1.94–2.31, y 0.05–0.50, z 1.74–2.05); the seat backs stay. Only in this mode.

## v2: what the owner's "artifacts on the hat" were, and the fix (2026-11-12)
Two separate causes on the two front figures, found by diffing the assets and the stills (`blender/render/transicion/antes-despues-v2/`).
(1) Both caps: the front headrests were inside the toy heads, so their dark wings poked through the back of each cap and changed
shape with the head nod; fixed in scene code by `sin_cabeceras()` above (no figure or camera change). (2) Héctor's cap only (the
right-hand head in the 16:9 frame): the crack-like lines on the back of the cap were thin bake lines in his normal map, not
geometry or colour. `blender/assets/reparto/hector.glb` differs from `hector-v1.glb` in that one image: mesh, UVs, colour and
roughness are byte-identical, and 18,024 of 16.8 M normal-map texels changed (0.11 %, max channel step 133), all on the back of
the head (glTF y 0.62–0.74, 850 triangles); `blender/tripo/normales.py` inpainted them (details in `docs/tripo-glb.md`). v1 clips
and `hector-v1.glb` are kept. Clips: `transicion-v2-1280x720.mp4`, `transicion-v2-720x1280.mp4` (24 samples, as v1). The 9:16 render
was resumed from frame 8 after an interrupted run with the same arguments and the same assets (untouched since 16:53).
`eagle.sh`/revisar: exit 0 on both, same table as v1 (strobe 0 runs, dark 80 % / 75 %); the only difference is the 16:9 jump events
at f41/f54 instead of f39/f52 (the heads passing the lens now read two frames later; 9:16 is unchanged at f48/f119). Not verified:
that the 16:9 shift is caused by the headrests' removal; no frame-by-frame look at the exit was done on v2.

## Measured (ray casts on the scaled G63)
```
seat cushion z ~1.07-1.10, cab floor 0.76, roof inside 2.19, seat back front y ~0.29
windshield y 1.09-1.35, z 1.62-2.06;  rear window y -1.0, z 1.78-2.05
bed floor z 0.93, inner x 0.96..2.49, y -1.09..-2.87, wall top 1.61
```

## Known rough spots
- Toy proportions: legs are 0.2–0.25 m long at this scale, so the seated figures look like they sit on their own belly.
- Guitars are primitives (two spheres and a neck), Diego's and Alexandro's instruments are both guitars.
- No phone for the manager, no glass for Héctor.
- Bed clearance (arithmetic, hip joint at z 1.40, scale 1.25): chests at z 1.67 (Diego) and 1.74 (Alexandro) clear the 1.61 wall top;
  the guitars' centre is at about z 1.56 with a 0.13 m body radius, so their lower half sits below the wall top.
  Raise the guitar offset (or the cases) when the instruments are redone.
