# Task 7 Report — WhatsApp CTAs and analytics

## Result

Implemented CTA target/event wiring in `src/pages/index.astro` only. Existing CTA URLs, target/rel attributes, telephone fallback, and layout were preserved.

- Hero WhatsApp CTA emits `whatsapp_hero`.
- `#contratacion` WhatsApp CTA emits `whatsapp_contratacion`.
- Footer WhatsApp link emits `whatsapp_footer`.
- All three CTAs use `bandSocialUrls.whatsapp`, `target="_blank"`, and `rel="noopener noreferrer"`.
- Telephone fallback remains `tel:+522288351464` with rendered text `+52 228 835 1464`.
- Existing `trackPlausible` helper reused from the browser script.
- No sticky/floating bar added.

## Validation

- `bun run build && bun test` — PASS; build completed; 20 tests passed, 0 failed.
- `grep -c "wa.me/5212288351464" dist/index.html` — `1` because Astro emits minified HTML on one line.
- `grep -o "wa.me/5212288351464" dist/index.html | wc -l` — `3`.
- Emitted HTML inspection — 3 WhatsApp anchors; exact URL, target, and rel present; telephone fallback present; all event names present.
- `git diff --check` — PASS.
- Self-review — only `src/pages/index.astro` changed for implementation; unrelated files preserved.

## Concerns

The required `grep -c` check cannot return `3` against Astro's one-line minified `dist/index.html`; occurrence-based check confirms the required three links. No source/config change was added solely to defeat that artifact-format mismatch.
