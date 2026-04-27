## Design System & Visual Direction

**Source of Truth:** DESIGN.md (read before any UI/CSS changes)

**Direction:** Veracruz Noir — editorial press kit × regional mexicano × gulf-coast noir

**Typography Stack:**
- Display/headlines: Cormorant (headline-only, never body text)
- Body: Inter (main reading text)
- Tabular/code: JetBrains Mono (numeric data, monospace)

**Color Palette (OKLCH):**
- `--color-surface` — oklch(98% 0 0) — background
- `--color-text` — oklch(18% 0 0) — foreground text
- `--accent` (turquoise) — oklch(68% 0.21 250) — links, focus, controls (not primary CTAs)
- `--gold` (signature) — oklch(72% 0.2 72) — primary CTAs, eyebrows, key visual elements
- `--burgundy-glow`, `--burgundy-hot` — editorial accents
- `--border`, `--focus-ring` — semantic colors

**Spacing Scale:**
- `--space-section` — major section gaps (clamp 4rem–10rem)
- `--space-lg` — editorial blocks (clamp values)
- Standard tokens: `--space-xs`, `--space-sm`, `--space-md`, `--space-lg`, `--space-xl`

**Motion:**
- `--duration-fast` — 150ms
- `--duration-normal` — 300ms
- `--ease-out-expo` — cubic-bezier(0.16, 1, 0.3, 1)

**Key Components:**
- Hero: Full-bleed background video + layered copy, grain + scrims
- Marquee: Tour dates scroll
- TourTable: Static tour dates from `tourDates.ts`
- ArtworkShelf: CD covers (Spotify/Apple CDN URLs, local image fallback)
- FilmStrip: Band photos (local `web/public/band/*.jpg`)
- SignatureCTA: Call-to-action section
- Fullscreen Mobile Menu: Numbered overlay, gold underline nav hover, social row + Clerk CTA

**Anti-Patterns (Do Not Ship):**
- Default card grids with uniform spacing
- Stock hero with centered headline + gradient blob + generic CTA
- Unmodified library defaults
- Flat layouts with no layering/depth
- Uniform radius/spacing/shadows everywhere
- Safe gray-on-white + one accent color
- Default font stacks without deliberate pairing

**Before Writing Frontend Code:**
1. Read DESIGN.md
2. Check token usage — no hardcoded colors/sizes
3. Verify layout matches direction (not centered, not uniform)
4. Confirm motion uses compositor-friendly properties only
5. Test both light theme (current) + any dark theme parity

See DESIGN.md for complete token reference.
