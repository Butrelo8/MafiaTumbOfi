---
title: Scene 2 Caja, our own social stickers that peel
type: build
status: open
assignee:
gate:
blocked_by: [05]
closed_as:
gist:
---

## Question

Four stickers of our own art (Instagram, TikTok, Spotify, YouTube) go on the tailgate, the bed sides and the rear window.
- **On desktop,** the corner peels on hover, and a click opens the profile.
- **On a phone,** the first tap peels the sticker and shows a 44 px "Abrir … ↗" chip.
- **Platform glyphs** follow plan v2 §2's rules: official file, unaltered, upright, and outside the part that peels.
- **The DOM twin** is the footer socials row (`src/data/socials.ts`).

Respect the page-first rule.

## Done-check

- Each brand kit is read in full, and the rules each sticker meets are listed. TikTok and Spotify are unverified in plan
  v2.
- Screenshots at 1440 and 390, with the peel recorded.
- The stickers weigh 0.1 MB or less.
- Clicks are counted in `/e` (`follow_click`).

```sh
bun test && bun run build
```
