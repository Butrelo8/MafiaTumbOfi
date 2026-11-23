---
title: Scene 6 Placa, the licence plate books by WhatsApp
type: build
status: open
assignee:
gate:
blocked_by: []
closed_as:
gist:
---

## Question

**What it does.** On hover, the headlights flash twice (120 ms pulses). On a click or tap, the horn sounds, but only if
the visitor turned sound on in the header. Then WhatsApp opens through the existing `/wa` counter route.

**The twin.** The DOM twin is the Tecla "Escribir por WhatsApp". **Contratar** stays in the fixed header the whole
time, so a booker never has to ride to the end.

Plan v2 §2, scene 6 row. Respect the page-first rule.

## Done-check

- A tap reaches `/wa` and is counted in `/e` (`wa_click`).
- With sound off, the horn never plays.
- The horn weighs 40 kB or less, or is synthesized.
- Screenshots at 1440 and 390.

```sh
bun test && bun run build
```
