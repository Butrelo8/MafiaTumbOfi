# Benchmark: sites of other label artists (2026-11-12)

These are lab numbers from one machine with no CDN advantage. Sources: `speed.mjs` / `tokens.mjs` (visual-lab diseccion
scripts) and the Apple copyright line for each artist's label. Screenshots are in `docs/design/benchmark/`. They are
evidence for this reading only, never material for the page.

## The bar, one line per site

| Site | Label evidence | Look | Motion | Weight (1440, lab) |
|---|---|---|---|---|
| **eptosuno.com** (best of the set) | owner says ONErpm; Apple lines read "Nunca Muere Records" (2026), not confirmed | black ground, Anton/Oswald condensed, UnifrakturCook + Pirata One blackletter, red `#e01f12`, a giant name over a B&W portrait with outlined "UNO" | GSAP + ScrollTrigger + Lenis, mouse-follow, a marquee; no video, no 3D | 41 KB at load, **363 KB** after scroll, LCP 1.46 s (median of 3, the h1). 390 throttled: not measured, the page navigates during load and the script loses its context |
| ozomatli.com | former ONErpm (2019), now Blue Elan | hand-coded, full-screen autoplay video with "Tap for sound" | hero video | 284 KB, LCP 1.44 s |
| anabarbara.com | ONErpm, confirmed ("Bajo Licencia Exclusiva a ONErpm") | single-release one-pager, Bebas Neue / DM Sans, a YouTube embed, a newsletter | none | 43 KB, LCP 1.36 s |
| carlosbaute.com | ONErpm, confirmed (2022 press release) | WordPress + Elementor template: loader, carousels | template carousels | **8.15 MB**, 134 requests, LCP 2.93 s |
| noelschajris.fan | signed 2024 with Dynamo; current lines show Dynamo only | WordPress Divi + WooCommerce shop | template | 3.38 MB, 372 requests, LCP 2.20 s |

Every artist confirmed on ONErpm today runs a template or a one-release page. The only hand-built sites with real motion
are eptosuno and ozomatli, and neither has a confirmed current ONErpm deal. **eptosuno.com is the bar.**

## eptosuno.com, measured

- **Stack:** hand-written static HTML, GSAP 3.12.5 + ScrollTrigger, Lenis from a CDN, served by `hcdn` with `no-store`
  cache headers (so every visit downloads it again). Built with Claude by Alexander Oliva (alexander-oliva.com).
- **Type:** Oswald 300 for body (13–16 px), Space Mono 9–11 px for labels, Anton for display (up to 115 px), and
  UnifrakturCook + Pirata One for the blackletter accents. That is five families.
- **`revisar.sh` web (live, 390 + 1440):** 5 FAIL rows: 91 elements under 4.5:1, 33 tap targets under 44 px, overflow
  from `div.grain`, CLS 0.120 at 1440, 2.53 MB at 390 until idle (`directions/shots/rv-eptosuno.tsv`).
- **Contrast pairs:** `tokens.mjs` measured 11 text/ground pairs under 4.5:1. For example, grey `#6f6a61` on `#121110` is 3.51,
  and the red `#e01f12` on `#121110` is 3.93. Body text is 13 px light Oswald.
- **slop-check:** passes every automated row on the live URL (rerun 2026-11-12, `grep -v PASS` empty). By eye, it shows tier-A tells the script misses: an eyebrow
  above the hero name ("MC · OBREGÓN, SONORA · DESDE EL BARRIO AL MUNDO"), numbered tabs ("01 Drop / 02 Música /
  03 Batalla"), a "SCROLL" cue with a line, a marquee band, and the same album block repeated eight times.
- **What it does well:** real content in depth (eight albums with full tracklists, battles, dates). A clear voice. A
  light page.

## Anti-patterns the owner reads as generic, with crops

From alexander-oliva.com (the anti-reference) and eptosuno.com. None of the three directions uses any of these. Checked
by eye on our screenshots, and by `slop-check.py` where a row exists.

| Pattern | Crop | Seen on | Our directions instead |
|---|---|---|---|
| Pill / fully rounded buttons (30 px radius ×36, 50 % ×35 measured) | `benchmark/ao-pill-buttons.jpg`, `benchmark/ao-pill-icon-cta.jpg` | alexander-oliva | square controls; the hover is a fill wipe or a lean, never a colour swap on a pill |
| Arrow-in-a-circle icon on a pill | `benchmark/ao-pill-icon-cta.jpg` | alexander-oliva | icons drawn for the band (play, WhatsApp) that morph in Rive (row `botones`) |
| Eyebrow / numbered kicker over the heading ("/ 01 — QUIEN FIRMA ESTO") + one accent-coloured word in the headline | `benchmark/ao-eyebrow-accent-word.jpg`, `benchmark/ep-eyebrow-hollow-type.jpg` | both | plain section names, no kicker, no accent word |
| Rounded dark cards with a logo chip, one border, the same height | `benchmark/ao-rounded-cards.jpg` | alexander-oliva | no cards: covers, photos and type sit on the ground or on printed rules |
| Service cards with "01 / 02" numerals, tag chips and a full-width pill CTA | `benchmark/ao-service-cards-chips.jpg` | alexander-oliva | none |
| Carousel with arrow circles and dots | `benchmark/ao-carousel-dots.jpg` | alexander-oliva | native scroll (A) or a full grid (B, C) |
| Outlined / hollow display type for the second word | `benchmark/ao-hollow-type.jpg`, `benchmark/ep-eyebrow-hollow-type.jpg` | both | solid type; contrast comes from width (B) or the logo's gold (A) |
| Marquee ticker band | `benchmark/ep-marquee.jpg` | eptosuno | none |
| Numbered tabs | `benchmark/ep-numbered-tabs.jpg` | eptosuno | none |
| "SCROLL" cue with a line | `benchmark/ep-scroll-cue.jpg` | eptosuno | none (the page's point is in the first screen) |
| The same album block repeated with alternating sides | `benchmark/ep-repeated-album-block.jpg` | eptosuno | one release leads; the rest share one grid or strip |

alexander-oliva.com uses the same tools we do (GSAP, Lenis, three.js, View Transitions). So our edge has to come from the
assets (a rendered scene, the band's own photos and footage) and the craft of each control, not from the stack.

## Weights

The other sites were measured with `speed.mjs --runs 1` at 1440, unthrottled, so treat them as single samples. The values are in the table above.
