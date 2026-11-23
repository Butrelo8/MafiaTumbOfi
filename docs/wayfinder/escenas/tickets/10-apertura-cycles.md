---
title: The Cycles apertura clip replaces the grey previz
type: build
status: open
assignee:
gate:
blocked_by: [01]
closed_as:
gist:
---

## Question

`public/prototipo/apertura.mp4` and `apertura-f0.jpg` are still the grey Workbench previz (6.5 s at 640×360, extended to
12 s in d92fb8a). The spec is `~/projects/mothership/docs/queue/2026-11-18-mto-apertura-integrate.md`, which adds the
real clip and a Low Power Mode fallback; its status is "spawn when meltingdrone's Cycles apertura.mp4 exists".

Under the page-first rule, the clip plays as a header or background (ticket 01). It must not grow the entry weight
before the content paints.

## Done-check

- The clip's size and resolution, and a poster at 120 KB or less.
- With Low Power Mode on (or autoplay refused), the page shows the poster.
- LCP at 390 is no worse than ticket 01's "after" number, with the same script.

```sh
bun run build
```
