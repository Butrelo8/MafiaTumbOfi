# Member Photos Design Spec

**Date:** 2026-04-21
**Branch:** feat/desegin-consultation-redo
**Status:** Shipped 2026-04-21 (placeholders in repo; swap JPEGs in `web/public/members/` when band has real crops).

---

## Goal

Replace `ui-avatars.com` generated initials with real member profile photos hosted locally. No external image dependency at runtime.

---

## Assets

Place square JPGs in `web/public/members/`. Minimum 180×180px (card renders 90×90, retina needs 2×).


| File                                      | Member           |
| ----------------------------------------- | ---------------- |
| `web/public/members/hector-baez.jpg`      | Héctor Báez      |
| `web/public/members/alexandro-montal.jpg` | Alexandro Montal |
| `web/public/members/diego-cerecer.jpg`    | Diego Cerecer    |
| `web/public/members/dimora.jpg`           | Dimora           |


**Manual step (operator):** Download each member's Instagram profile pic, crop to square, save to the paths above. Code changes can be made before or after this step — missing files show a broken image until assets land.

---

## Data Layer

**File:** `web/src/data/members.ts`

Replace each `image` value from `ui-avatars.com` URL to the local path:

```ts
image: '/members/hector-baez.jpg'
image: '/members/alexandro-montal.jpg'
image: '/members/diego-cerecer.jpg'
image: '/members/dimora.jpg'
```

No interface or type changes required — `image: string` already covers local paths.

---

## Component

**File:** `web/src/components/MemberCard.astro`

Switch from `<img>` to Astro's `<Image />` from `astro:assets`. Benefits: automatic WebP conversion, correct `srcset`, enforced `width`/`height`.

```astro
---
import { Image } from 'astro:assets'
---

<Image
  src={image}
  alt={name}
  width={90}
  height={90}
  loading="lazy"
  class="member-photo"
/>
```

**Note:** `astro:assets` `<Image />` with a string `src` requires the image to be imported as a module (not a string path) for full optimization, OR use `inferSize`. For local public-folder files referenced by path string, keep `<img>` with explicit `width`/`height` — Astro's `<Image />` only optimizes imported assets, not `/public` string paths.

**Revised component approach:** Keep `<img>` tag. Update `src`, add explicit `width="180" height="180"` (source size), keep `loading="lazy"`. Remove the `ui-avatars` comment. CSS handles display size (90×90).

Existing `.member-image img` CSS (`width: 100%`, `height: 100%`, `object-fit: cover`) unchanged.

---

## Build Verification

```bash
cd web && bun run build
```

Expected: clean build. Absent photo files = broken image at runtime, not a build error.

---

## Done When

- `web/public/members/*.jpg` contains 4 member photos (operator step).
- `members.ts` references `/members/<slug>.jpg` for all 4 entries.
- `MemberCard.astro` `<img>` has `width="180" height="180"` and no `ui-avatars` comment.
- `bun run build` in `web/` is green.
- No API, booking, admin, or drip code touched.

