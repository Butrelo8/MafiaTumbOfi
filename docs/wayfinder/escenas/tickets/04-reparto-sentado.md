---
title: Land the seated cast (cc/deaddrone) and rebuild the live files
type: build
status: open
assignee:
gate:
blocked_by: [02, 03]
closed_as:
gist:
---

## Question

Bring `cc/deaddrone` 27afeee onto `main`. It already holds `cc/atedrone` 4457d2d and `cc/laggingdrone` 58dc35d: the
seated-pose solver, the hip and leg controls, Diego's wrist twist bones, and the lowered seats in `blender/g63_nuevo.py`.

1. Apply ticket 02's fix and ticket 03's file.
2. Run the whole `scripts/vivo-g63.sh` chain. The handoff warns that `g63-listo`, `g63-rack` and `vivo-g63` were not
   redone.
3. Fix the seatbelt (Mesh.261), which does not lower with the seats.
4. Redo the stop cameras that follow the cast, such as Diego's stop-4 shot cropping his head
   (`docs/handoffs/2026-11-20-g63-nuevo-rack.md`).
5. Upload to the `vivo` preview alias, then go to `main` with the owner's OK to merge.

Respect the page-first rule (map Notes).

## Done-check

- Solver table rerun: heads against the roof, 0 for all four; heads against the wheel or dashboard per ticket 02's
  pick; shins at 1 cm or less.
- Stills from the seat cameras and the stop cameras, before and after, at 1440 and 390, with `revisar` numbers.
- `public/vivo/` file sizes and draw calls per stop, before and after.
- TTFF on Fast 4G at 390, as the median of five, in the same session as the baseline (`scripts/medir-vivo.mjs`).
- The page logs no errors. `bun test && bun run build` passes.

```sh
bun test && bun run build
git merge-base --is-ancestor 27afeee HEAD
```
