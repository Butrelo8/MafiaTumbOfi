---
title: Scenes 3 and 5, the screen truck's videos and tour dates
type: build
status: open
assignee:
gate:
blocked_by: []
closed_as:
gist:
---

## Question

The screen truck already drives and plays a video in the live scene.

**Scene 3, the side screen.** It shows the 14 videos: ‹ › changes the video with an LED wipe, and a click opens it on
YouTube. There is no embedded player. The DOM twin is the list of 14 videos.

**Scene 5, the rear screen.** It reads `public/data/fechas.json` with plan v2 §5's rules:
- Mexico City dates; past rows dropped; the next 5 on the screen and all of them in the DOM `<ul>`.
- An empty state when the file is missing or invalid, or has no future rows.

The watcher that writes the file is out of scope.

Respect the page-first rule: the thumbnails and the dates file load after first paint.

## Done-check

- Unit tests for the dates reader: past rows, null fields, a bad version, a missing file, and the empty state.
- Screenshots of both screens and of the empty state, at 1440 and 390.
- The thumbnails weigh 14 × 30 kB or less.

```sh
bun test && bun run build
```
