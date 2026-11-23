---
title: Scene 4 Costado, windows that lower, name plates and poses
type: build
status: open
assignee:
gate:
blocked_by: [04, 07]
closed_as:
gist:
---

## Question

On hover, each of the four windows lowers and a name plate rises, with the name, the role and a gold Instagram link. A
click plays one pre-baked pose: a wave, a hat tip or an air-strum. The heads follow the pointer, or the tilt behind
"Activar movimiento" on iOS.
- Plan v2 §2, scene 4 rows; the phone version is four stops, one per window (§3).
- The member cards are the DOM twins.
- The manager, "El Manco", is added to `src/data/members.ts` with his card. That needs ticket 07, and his photo is still
  missing.

Respect the page-first rule.

## Done-check

- Each window and pose works by mouse, keyboard and touch.
- Pose clips are 0.4 MB or less each.
- Screenshots of the four shots at 1440 and 390.
- Reduced motion turns off the head-follow.

```sh
bun test && bun run build
```
