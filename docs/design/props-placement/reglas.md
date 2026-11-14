# Placement rules for the truck scenes (2026-11-13, run `touchgrasdrone`)

From the photos in `referencias.md` (numbers in brackets) and set-dressing practice (the text rows there). Rules 1–4 are measured
per still by `blender/props_placement.py`: it casts one ray per pixel at 1/5 of the still's size from the scene camera, once with
the new props hidden and once with them shown, and writes the numbers to `stills/medidas.tsv` (`scripts/props-medir.py` turns them
into the table in `index.md`). Rules 5–8 are judged from the stills and say so.

| # | Rule | Threshold (measured) | From |
|---|---|---|---|
| 1 | **Sight lines.** A prop never covers a scene's working part: the tailgate stickers (2), the four windows where the name plates rise (4), the side screen and the manager's window (3), the plate and both headlight lenses (6), the mirror glass and the road through the windshield centre (1). | ≤ 2 % of each protected zone's pixels covered by new props | Every float keeps its title and its people clear [1, 2, 3]; the plan's interactions |
| 2 | **Scale: read or cut.** At the scene camera a prop must cover at least 0.1 % of the frame (about 45 × 45 px at 1920 × 1080) or be self-lit. Below that it is close-up dressing only. Scene 2 sees about 2 px/cm, so a prop under ~25 cm is a dot there. | visible px ≥ 0.1 % of the frame, or emissive | Dash props read only against the bright glass [9]; at night only lit things read [5] |
| 3 | **Clutter budget.** At most 3 new props that read (rule 2) per cab view (1, 6) and 4 per exterior view (2, 4), on top of the owner's picks. Leave negative space around the scene's working part. | count of new props over the rule-2 line | Floats run two colour blocks, not five [2]; "don't fill every open area" (set-dressing guides) |
| 4 | **The call to action stays brightest.** After the headlights, the scene's working part is the brightest thing in frame. A self-lit prop dimmer than it frames it; brighter steals it. | total light of the zone > total light of every lit new prop: linear luminance summed over each one's pixels (render at 1/5, by the ray-cast id map). A first version compared p95 brightness and failed every preview by construction (an emissive bulb clips to 1.0), so area has to count | The lit sign names the float [2]; the bumper name on the Renotaxi [17] |
| 5 | **One silhouette, one peak.** The load breaks the cab line once, as one mass, highest toward the back of the bed and at its centre; the roof carries at most one item. | judged | [7], [4], [11], [19], [22] |
| 6 | **Layers from the camera.** Foreground frames (partly out of frame, darker: fringe, papel picado, a mirror ribbon), midground is the working part, background is the road and lamps. Nothing in the foreground is brighter than the midground. | judged | [15], [16]; set-dressing guides (value separation) |
| 7 | **Colour blocks at night.** Two light colours per frame plus the warm practicals: gold/amber (brand) and one accent. Outline lights trace edges rather than fill faces, so the truck stays black (the DESIGN direction). | judged | [1], [19], [20], [21] |
| 8 | **It rides.** The truck never parks: everything is strapped, zip-tied or bolted, and nothing loose sits on the roof or the hood. Ribbons and fringe hang and can flutter; that motion is for later, not these stills. | judged | [13] (ribbons tied), [6] (bolted roof box) |

What the rules mean per scene (protected zone, budget, where new things may go):

| Scene | Camera (from `utileria.py`) | Protected | Budget | Free zones |
|---|---|---|---|---|
| 1 Cabina | `CAMINO[0]`, 20 mm, between the rear heads | mirror glass, windshield centre (the road); the dash screen is not in the base scene, so it was not measured | 3 | windshield top band either side of the mirror; dash corners; the ceiling |
| 2 Caja | `VISTA_ESC2` (v3 f191), 28 mm | tailgate stickers | 4 | roll bar and its top; the bed rails' top edges; the rear cab window's top band |
| 3 Pantalla | `esc3-espejo` / `esc3-hombro` | side screen, manager's window | 2 | the driver's mirror (a ribbon) only: works under either reading of #33 |
| 4 Costado | `esc4` passenger side, 6.2 m out, 24 mm | the four windows | 4 | roof (one item), under the body (light), mirror, bed rails, roll bar |
| 5 Gira | over the hood, 30 mm | the rear screen ahead | 1 | the hood's front edge; no new props rendered (hood only) |
| 6 Placa | ahead, low, 32 mm | the plate, both headlight lenses | 3 | windshield top band, roof front edge, under the body, mirrors |

How each protected zone is found in the probe (`blender/props_placement.py`, `ZONA`):
- mirror: a box around the probed interior mirror (±16 cm in x, ±8 cm in y, its z run); the mirror shares one mesh and material
  with the whole interior, so the zone is a position, not an object;
- road: the windshield glass objects, hits in the lower 70 % of the glass height (the sky over the road does not count);
- stickers: any `c3_` material. This also counts the band decals on caja3's road case, cooler and hat box; no verdict changes
  (B 0 %, A 0.2 %);
- windows: `vidrio*` materials; plate: `u_placa*`; headlights: `faros`.

Close-ups (`ppN-cerca`) show a prop and are reported as "detalle": the rules hold at the scene camera only. In scene 2 the numbers
do not separate A from B (both pass rules 1–4); the difference there is rule 5, judged: in A the flag covers the marquee and two
balloon bunches make two more peaks.
