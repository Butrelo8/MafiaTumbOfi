---
title: Scene 1 Cabina, the radio, cassette, dash key and glovebox
type: build
status: open
assignee:
gate:
blocked_by: [04]
closed_as:
gist:
---

## Question

Build the scene 1 props from plan v2 §2.
- **The radio dial** steps through the 9 releases in `catalog.json`. The display shows the cover and title, and no sound
  plays by default.
- **The cassette and the dash key** open **Escuchar**.
- **The glovebox easter egg** spills its junk and is `aria-hidden`.
- **The manager's eyes in the mirror and Héctor's head** follow the pointer.

Each control has a DOM twin, 44 px, with the Tecla button (`docs/design/DESIGN.md` › Components). The phone behaviour is
in plan v2 §3. Respect the page-first rule.

## Done-check

- Each prop works by mouse, keyboard (through its twin) and touch.
- Screenshots at 1440 and 390.
- The radio and glovebox assets weigh 0.2 MB or less in total.
- No request goes out before the visitor taps Escuchar.

```sh
bun test && bun run build
```
