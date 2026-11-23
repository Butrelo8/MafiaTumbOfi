---
title: Land Héctor's D cap (cc/clowndrone) and check it against the roof
type: build
status: open
assignee:
gate:
blocked_by: [04]
closed_as:
gist:
---

## Question

Bring `cc/clowndrone` 18db209 onto `main`: `blender/vivo_gorra.py`, single-sided decals at +2 draw calls, and
`reparto.glb` at +143 KB. Its handoff found two problems:
- **The cap dome pokes through the roof** in `asiento_der_lado`.
- **The cap is not on screen at Héctor's own seat camera.**

Both depend on the seated cast, so this runs after ticket 04. The cap files are derived from band photos and stay out of
git, in `blender/assets/reparto-v5/hector/gorra_d/`.

## Done-check

- After 04, `asiento_der_lado` and the stop-4 Héctor shot show no dome through the roof: a 100 % crop plus the
  headliner distance measured in Blender.
- Draw calls per stop are +2 at most.
- The `reparto.glb` size is recorded. The page logs no errors.

```sh
bun test && bun run build
git merge-base --is-ancestor 18db209 HEAD
```
