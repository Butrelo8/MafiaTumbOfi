# Props phase, first pass: placement hand-off (teadrone, 2026-11-15)

The owner's rule is that drones stop at placement. This pass made a first guess for each item and built it into every montaje
scene. It then saved one locked .blend per item, and the owner places them. A follow-up drone reads the placement back and runs
the checks.

## What is in the scenes

`props_placement.camion()` runs in all six montaje scenes. It now also runs the items below, so `montaje.py` did not change.
Integration can move the calls into `montaje.py` if it prefers.

| Item | Code | Where (first guess) | Scenes where it reads |
|---|---|---|---|
| Console screen | `utileria.pantalla_consola` | The centre stack, over the G63's own small display: 0.20 m wide, 16:9, centre z 1.615, leaning about 13° | 1 |
| Console bottle | `caja5.bebidas_consola` (nerddrone's redo, `d237f62`) | Ahead of the shifter | 1 |
| r1 stickers | `utileria.calcas_r1`, `calca3(..., cara=)` | Gallo, corazón and x-holo on the tailgate, round the mix. Slogan, placa, arriba and bubu in a row on the right bed side, above the wheel-arch flare | 2 (tailgate), 4 (side) |
| Roll-bar bulbs | `props_placement.camion` (P9 on the arch, 2.5) | The roll bar's arch | 2, 4 |
| Instruments | `caja5.instrumento` | On top of the load. The tololoche lies on its back over the donut and the beer, the bajo sexto lies across it, and the requinto lies on the donut's left | 2, 4 |

All the positions are in `blender/props/colocacion.json`.

**Screen, two variants compared** in scene 1's hold:
- **B, kept.** 0.20 m at z 1.615. The stack shows one screen, and its whole face clears the console bottle.
- **A.** radio2-b's 0.17 m at z 1.52. It sat under the G63's own small display, so the stack showed two screens, and the bottle's
  cap hid its lower edge.

**Instruments.** These are our own primitives, sized from `references.md`, caja3 row. `blender/assets/guitarra.blend` and
`tololoche.blend` stay out, because their licences are unchecked: the guitar came from Blend Swap with no licence file, and the
tololoche has no recorded source.

## Placement files (the owner)

The files are in `E:\Cursor Projects\MTO-colocar\2026-11-15\`: `colocar-pantalla.blend`, `colocar-calcas.blend` and
`colocar-instrumentos.blend`.
- Only that file's empties can be selected.
- The LEEME is in the Scripting tab. A line at the bottom of the camera view points to it.
- `blender/colocacion_blend.py` rebuilds the files. `blender/colocacion_leer.py` reads one saved file back into
  `colocacion.json`, and prints each value it changed.

## For the follow-up drone (open checks)

- **r1-arriba's tent is 29.8 mm in scene 1, against 12.1 mm in scenes 2–6.**
  - Every scene prints 778–826 "pozos" for it, and 236–380 for placa and bubu.
  - The rays slip through the side panel's mesh at y −1.7..−0.9, z 1.29–1.41.
  - What lifts the tent in scene 1 was not found. Check a 100 % crop of the side at the re-render.
- **The tololoche may graze the speaker (bocina, top z 1.71).** The tololoche's body rises 0.10 rad toward the cab. No overlap
  test was run on the instruments.
- **The console bottle passes with Héctor's hand raised.** In every montaje scene it prints 0 pairs and 0 vertices inside, with a
  0.5 mm gap. The old rule that his hands must be at rest was dropped.
- **`camion()` also runs in `pp4-b` and `pp6-b`.** They now carry the screen, the r1 stickers and the arch bulbs. `pp4-b` no longer
  adds its own arch, so the bulbs aren't doubled.
