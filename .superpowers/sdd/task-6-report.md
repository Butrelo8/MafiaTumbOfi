# Task 6 report — seven-section static homepage

## Status

Complete. Rebuilt the homepage as the required seven-section composition: hero, marquee, Música, film strip, bio, Grupo, and Contratación, followed by the footer.

## Scope

- Updated `src/pages/index.astro` to load the catalog at build time, render releases and linked YouTube thumbnails, use the exact requested copy, keep three members, and replace the old standalone sections with the single WhatsApp booking CTA.
- Updated `src/data/members.ts` to retain only Héctor Báez, Alexandro Montal, and Diego Cerecer with their existing names, roles, images, and Instagram URLs.
- Added the exact WhatsApp URL to `src/data/socials.ts`.
- Updated `src/layouts/MarketingLayout.astro` navigation to target the retained homepage sections and removed obsolete CTA analytics wiring reserved for Task 7.
- Deleted `public/members/dimora.jpg`, `public/members/luis-c.jpg`, and `public/members/luis-c.webp`.
- Left `src/components/SignatureCTA.astro` unchanged and added no dependencies.

## Validation

```sh
bun run build
```

Passed: Astro generated one static route, `/index.html`. The build emitted only the existing stale `caniuse-lite` warning.

```sh
bun test
```

Passed: 20 tests, 0 failures, 26 assertions across 3 files.

Generated HTML checks confirmed:

- Required section sequence: hero → marquee → Música → film strip → bio → Grupo → Contratación → footer.
- Exact hero, bio, booking, Apple Music, WhatsApp, telephone, and footer copy is present.
- Six catalog releases render with the `Escuchar en Spotify` label; legacy non-year subtitles are suppressed, while fetched release years remain supported.
- Seven RSS video cards rendered as external YouTube links with `i.ytimg.com` thumbnails; no iframe or embedded player rendered.
- Required WhatsApp URL is exact and used by hero, Contratación, and footer links.
- No deleted fechas, trust, repertorio, testimonios, paquetes, press, form, login, admin, embedded-player, or `showPressAssets` remnants rendered.
- Build output contains no second page route.
- Required spacing tokens and `aria-labelledby` landmarks remain on authored content sections; decorative hero video remains `aria-hidden`.
- `git diff --check` passed.

## Preservation

Unrelated modified `.superpowers/sdd/task-1-report.md` and unrelated untracked files were not staged or changed. Existing similarly named member source assets outside the explicitly requested deletions were preserved.

## Concerns

- YouTube thumbnails depend on build-time RSS availability. The catalog's committed fallback intentionally contains no videos, so an upstream failure can produce an empty video row while keeping the build successful.
- Existing Browserslist data warning remains; dependency maintenance is outside Task 6 and no dependency changes were allowed.

## Commit

Commit: `feat(web): rebuild homepage as seven static sections`

## Review fixes

- Deleted the remaining `public/members/luis-c 1.jpg` asset; no `public/members/luis-c*` files remain.
- Replaced in-place mutation of `catalog.releases` with a mapped `releases` array before passing it to `ArtworkShelf`.
- Updated `MemberCard.astro` at source: member names use `--ff-body`; roles use muted body color; IG links and focus use `--accent`; social/card borders use neutral `--border`; IG touch targets are at least 44 × 44 px; hover motion is limited to `translateY(-2px)` with no scale, gold border, or shadow.
- Left member-card markup, copy, section structure, `SignatureCTA.astro`, and dependencies unchanged.

## Review fix validation

```sh
bun run build
```

Passed: Astro generated one static route, `/index.html` (1 page), with the existing stale `caniuse-lite` warning only.

```sh
bun test
```

Passed: 20 tests, 0 failures, 26 assertions across 3 files.

Generated output and source checks confirmed the required section order through the footer, three rendered member cards, release cards and linked YouTube thumbnails, no iframe/embed/object, no form/login/admin/booking route or `showPressAssets`, no remaining `luis-c*` asset, no catalog release mutation, required spacing/landmarks, and a clean `git diff --check`.

Review fix commit: `fix: align member cards with design tokens`
