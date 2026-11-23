---
title: The phone version of the ride, per the owner's pick
type: build
status: open
assignee:
gate:
blocked_by: [08, 09]
closed_as:
gist:
---

## Question

Build what ticket 08 picks for phones.

**If it is the clips:**
- Moves use `-g 6` H.264 at 540×960, 1 MB or less each.
- Idle loops use normal H.264.
- Cuts are hidden behind the gantries.
- Dates and other overlays are DOM elements on the video.

**If it is the live scene:** slim it to plan v2's 3 MB entry budget.

Plan v2 §3 holds the per-scene changes and the weight table. Respect the page-first rule.

## Done-check

- Entry weight is 3 MB or less, and each move is 1 MB or less, measured in a real browser with
  `scripts/medir-peso.mjs`.
- LCP at 390 uses ticket 01's script.
- A `-g 6` seek is checked on a real phone. Plan v2 marks it unproven.

```sh
bun test && bun run build
```
