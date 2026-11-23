---
title: Land the roof net settled by physics (cc/youdrone) and rebuild
type: build
status: open
assignee:
gate:
blocked_by: []
closed_as:
gist:
---

## Question

Bring `cc/youdrone` ce1510d onto `main`. It already holds `cc/copingdrone` 7b0db15. Its position-based rope solver
`_relajar` in `blender/g63_carga.py` replaces Blender cloth and becomes the default net; `analitica` stays as the
fallback.

The handoff (`docs/handoffs/2026-11-20-red-fisica-youdrone.md` on that branch) left two things not verified:
- the net was never run end to end through `blender/g63_rack.py`, because the prepared pieces in
  `blender/assets/carga-nueva/*.glb` were missing from that checkout;
- nothing was rebuilt into `public/vivo/`.

If ticket 04 runs first, rebuild once with both changes. `scripts/vivo-g63.sh` is touched by 04, 05 and 06.

## Done-check

- Run `g63_rack.py` end to end and record its `medir` table: mean move 0.1 mm per 10 steps or less, 0 pieces inside,
  `alien_red_encima` 0, `correa_dentro_alien` 0.
- The net's triangle count (`G63 RACK red tris`) and the `camion_extras.glb` size, before and after.
- TTFF at 390 on Fast 4G, no slower than the baseline. Stills of the stops that show the roof at 1440 and 390.

```sh
bun test && bun run build
git merge-base --is-ancestor ce1510d HEAD
```
