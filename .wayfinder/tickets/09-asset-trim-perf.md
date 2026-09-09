# 09 — Asset trim + performance budget
Labels: `wayfinder:grilling` · Blocks: — · Blocked by: 01, 02 · Assignee: —

## Question
What ships in `public/`, and what number does the rebuild have to hit?

### Where it stands
Lighthouse, `www.mafiatumbada.com`, 2026-04-28 (repo root):
**performance 36** · a11y 96 · best-practices 96 · SEO 100.
FCP 3.4s · **LCP 10.1s** · TBT 1,150ms · Speed Index 12.7s · CLS 0.011.
**Total page weight 15,195 KiB**, of which three files are 14.6 MB:

| file | shipped |
|---|---|
| `video/hero.mp4` | 8,828 KB |
| `marketing-grunge-texture.png` | 4,637 KB |
| `icon/mafiatumbada.png` | 1,198 KB |

Caveat: that run predates the `perf/homepage-performance-2026-06-01` merge (`c8fb0fb`).
**Re-measure before acting** — the baseline may already be better, and optimizing against a
stale report is how effort gets spent on a solved problem.

Current `public/` on disk is 21 MB. Known fat: `video/hero.mp4` 9.8 MB · `assets/orphan/` ~7.2 MB
(a `marketing-grunge-texture.png` 4.6 MB plus two `mafiatumbada` files — is `orphan/` reachable
at all?) · `icon/mafiatumbada.png` 1.2 MB (the hero logo, `fetchpriority="high"`, likely the LCP
element) · `marketing-grunge-texture.webp` 1 MB · `members/dimora.jpg` 717 KB (a member §2 cuts).

### To decide
- Delete-by-reference: with §2 cutting 8 sections and §1 cutting the admin/booking pages, which
  files under `public/` still have a referrer? `members/` loses 2 of 5. `assets/orphan/` looks
  dead by its own name — confirm, then delete.
- The hero video: 9.8 MB for a decorative muted loop. Re-encode, poster-only until interaction,
  or cut? It is the single largest cause of the 15 MB page.
- The logo PNG at 1.2 MB when a `.webp` `<source>` already exists — is the PNG fallback still
  earning its place in 2026?
- The grunge texture ships twice (4.6 MB PNG in `assets/orphan/`, 1 MB WebP at root).
- Budget: a target, not a vibe. Proposal to react to — **< 1 MB initial load, LCP < 2.5s,
  TBT < 200ms, performance ≥ 90 on mobile**. TBT should fall out for free: §1 deletes Clerk
  (103 KB of `clerk.browser.js` + `ui.browser.js`) and every booking/admin script.
- Where the budget is enforced: CI check, a Lighthouse run in Workers Builds, or honour system.

Output: the surviving `public/` inventory + the committed budget numbers, as spec §9.
