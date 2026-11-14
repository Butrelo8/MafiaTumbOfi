# New props for the truck scenes (2026-11-13, run `touchgrasdrone`)

Fourteen props that are not in the scenes yet (the scenes hold: bed B or caja3's twelve, piñata, balloons, donut, cooler,
speaker, the sticker mix, the plate, the dash screen). Source numbers point at `referencias.md`. Build routes: **P** procedural
in `blender/props_placement.py` (built for these stills), **PH** Poly Haven (CC0), **T** Tripo. Costs are for a game-ready
version in the live build (modelled, textured, decimated), not for the still. Rules are in `reglas.md`; whether each one
"reads" is measured per still (`index.md`).

| # | Prop | Source | Scene · zone | Why it reads at that camera | Route · cost | In stills |
|---|---|---|---|---|---|---|
| P1 | **Two-tier LED light bar** across the roof's front edge, black housing, 24 pods | [12] (made for the G63 6×6) | 6 roof front; 4 roof line | Self-lit: the brightest horizontal line in 6, a hard cap on the silhouette in 4. Off or at amber in B so the plate stays brightest (rule 4) | P · 1 h, ~3 k tris, emissive per pod | 4, 6 |
| P2 | **Name strip** "MAFIA TUMBADA" across the top of the rear window and the windshield | [8], Sinaloa windshield-strip rule (T) | 2 rear cab window; 6 windshield top | A pale band across dark glass; at 2 px/cm the letters are 9 cm tall, so it reads as a band of type | P (decal, PIL) · 20 min, 2 tris | 2, 6 |
| P3 | **Fringe valance** across the inside of the windshield top, gold fringe, phrase "PURA MT" embroidered | [15] | 1 windshield top (foreground frame); 6 through the glass | The top frame of scene 1 over the road; dark against the night sky with a gold edge | P (strip + alpha fringe card) · 40 min | 1, 6 |
| P4 | **Dash pennant on a desk stand** (MT, not a national flag) + air-freshener bottle | [9] | 1 dash, passenger corner | Low on the dash against the bright glass and the road | P · 30 min, ~800 tris | 1 |
| P5 | **Strawberry charm** hanging under the mirror (the PUTIFRESA joke) | [9] | 1 under the mirror | Small, centred, swings: a single red dot over the road | P · 15 min | 1 |
| P6 | **Roof horn speakers** (two trompetas de perifoneo on a bar) | [6], Radox listing (T) | 4 roof; 6 roof | A second silhouette on the roof, says "the band announces itself" | P · 30 min, ~1 k tris | 4 A, 6 A |
| P7 | **Ribbon rosettes** with tails on the mirrors | [13] | 3 driver's mirror (works under either #33 reading); 4 passenger mirror; 6 both mirrors | White on a black truck: the only white shape at the cab's edges | P · 30 min | 4, 6 |
| P8 | **Papel picado across the cab ceiling** | [16] | 1 ceiling (foreground frame) | Colour along the top of frame; only in A, B drops it for the budget | P (alpha panels, reuses caja3's punch) · 15 min | 1 A |
| P9 | **Outline bulbs** along the bed rails and the roll bar | [1], [19], [20], [22] | 2 bed edges; 4 bed line | Traces the bed's shape in warm dots: the truck stays black and the shape reads | P (instanced emissive spheres) · 40 min, instanced | 2, 4 |
| P10 | **Marquee sign** on top of the roll bar, facing back: bulb letters "PURA MT" on a black panel | [2], [3], [11], [22] | 2 the bed's peak; 4 the silhouette's peak | The lit title of the truck, like the float's ring sign; the one peak (rule 5) | P · 1 h | 2, 4 |
| P11 | **Underglow**: amber light pools on the road under the body | [17] | 4 road under the truck; 6 road under the bumper | A colour pool that separates the black truck from the black road | light only · 15 min, no geometry | 4, 6 |
| P12 | **Roof rack with a strapped spare tyre and a road case** | [12] (the Brabus has a rack), [7] (load above the cab) | 4 roof | A touring silhouette; only in A, B drops it (the roof carries one item) | P · 1 h, ~4 k tris | 4 A |
| P13 | **Band pennants** on short poles at the bed's rear corners | [18] (flags on cars; ours never national) | 2 bed corners; 4 bed's back | Two small vertical accents that mark the bed's corners | P · 20 min | 2 A |
| P14 | **Cattle horns on the hood** | TV Tropes (T only, no photo) | 6 hood | Strong silhouette, but no photo seen and the cartel-troca reading | not built: owner question | — |
| — | Rosary or Virgin statuette (dash, mirror) | Cronista, AP (T) | 1 | Common in Mexican cabs; religious | not built: owner question | — |

## What the probe found (`stills/medidas.tsv`, % of the frame at the scene camera; reads = ≥ 0.1 % or self-lit)

- **Read at their scene camera:** P1 light bar (0.3 % in 6, 0.11 % in 4), P10 marquee (0.8–1.0 % in 2), P9 bulbs (lit), P3
  fringe (0.36–0.53 % in 1), P8 ceiling papel picado (1.2 % in 1 A), P12 roof rack and P6 horns (4 A), P7 rosette (4), P2 strip
  (0.23 % in 6).
- **Cut by rule 2 at the scene camera:** P4 dash pennant (0.008 % in 1: the front heads hide the dash; close-up dressing at
  most), P2 on the rear window in scene 2 (0.014 % behind caja3 A's pile; 0.217 % behind caja3 B's lower pile, so it depends on
  #34), P6 horns in 6 (0.08 %), P7 rosettes in 6 (0.014 %), P5 charm (0.04 %: below the line, kept as a single red dot because it
  sits over the road, judged).
- **P11 underglow** is light only, so the probe cannot see it; in the stills it is the strongest colour block in 4 and 6 (judged).

## The three strongest

1. **P10 marquee sign:** the bed's one lit peak; it reads at the scene-2 camera (1.0 % of the frame) and keeps the stickers at
   0 % covered with either caja3 bed.
2. **P1 light bar:** made for our truck; it caps scene 6 (0.3 %) and scene 4. In 6 it must stay dim (amber at 2.5 out-lit the
   plate, 66.5 vs 45.4 total light; at 0.9 they tie, 45.1 vs 45.4), so the build should treat it as a dim DRL or keep it off.
3. **P9 outline bulbs:** they draw the black bed's shape at night without lighting its faces; on the roll bar alone (B) they frame
   the marquee instead of competing with it.

Not verified beyond the stills and the probe numbers.
