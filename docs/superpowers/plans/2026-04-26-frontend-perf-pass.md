# Frontend Performance Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate four homepage performance regressions: render-blocking Google Fonts CDN, blocking SSR tour-dates fetch, AOS library in critical CSS path, and uncompressed member images.

**Architecture:** All changes confined to the Astro frontend (`web/`). No API changes. Tasks are fully independent — implement in any order, but Tasks 1–2 (P1) before Tasks 3–4 (P2). The tour-dates client hydration (`tourTableHydrate.ts`) is already fully implemented; Task 2 only removes the SSR await.

**Tech Stack:** Astro SSR (Vercel adapter), Bun, `@fontsource/*` npm packages, native `IntersectionObserver`, `cwebp` (libwebp CLI).

---

## File Map

| File | Change |
|------|--------|
| `web/src/layouts/MarketingLayout.astro` | Remove googleapis `<link>` tags; add `@fontsource` imports |
| `web/src/pages/index.astro` | Remove SSR `loadTourDates` await; remove AOS import + init; replace `data-aos` with `data-reveal` |
| `web/src/components/MemberCard.astro` | Replace `data-aos` with `data-reveal`; wrap `<img>` in `<picture>` with WebP `<source>` |
| `web/src/styles/marketing-press.css` | Add `[data-reveal]` initial + `.is-visible` rules; add `prefers-reduced-motion` guard |
| `web/public/members/*.webp` | New files — converted from existing JPEGs |

---

## Task 1: Self-host Google Fonts (P1)

**Files:**
- Modify: `web/src/layouts/MarketingLayout.astro:46-49`
- Install: `web/package.json` (new deps)

### Context

`MarketingLayout.astro` L46–49 loads three font families from `fonts.googleapis.com` via a synchronous `<link rel="stylesheet">`. This blocks rendering until external DNS + RTT + download completes. Fonts loaded: Cormorant Garamond (wght 300/600/700, italic 300), Inter (wght 400/500/600/700), JetBrains Mono (wght 400/500).

- [ ] **Step 1: Install @fontsource packages**

```bash
cd web && bun add @fontsource/cormorant-garamond @fontsource/inter @fontsource/jetbrains-mono
```

Expected: packages added to `web/package.json`. No errors.

- [ ] **Step 2: Verify available weight files**

```bash
ls node_modules/@fontsource/cormorant-garamond/*.css | grep -E "300|600|700" | head -10
ls node_modules/@fontsource/inter/*.css | grep -E "400|500|600|700" | head -10
ls node_modules/@fontsource/jetbrains-mono/*.css | grep -E "400|500" | head -5
```

Expected: files like `300.css`, `300-italic.css`, `600.css`, `700.css` for Cormorant; `400.css`, `500.css`, `600.css`, `700.css` for Inter; `400.css`, `500.css` for JetBrains Mono.

- [ ] **Step 3: Add fontsource imports to MarketingLayout.astro**

In `web/src/layouts/MarketingLayout.astro`, inside the `---` frontmatter block (after existing imports), add:

```astro
---
// ... existing imports above ...
import '@fontsource/cormorant-garamond/300.css'
import '@fontsource/cormorant-garamond/300-italic.css'
import '@fontsource/cormorant-garamond/600.css'
import '@fontsource/cormorant-garamond/700.css'
import '@fontsource/inter/400.css'
import '@fontsource/inter/500.css'
import '@fontsource/inter/600.css'
import '@fontsource/inter/700.css'
import '@fontsource/jetbrains-mono/400.css'
import '@fontsource/jetbrains-mono/500.css'
---
```

- [ ] **Step 4: Remove the three googleapis link tags**

In `web/src/layouts/MarketingLayout.astro`, delete lines 46–49:

```html
<!-- DELETE these three elements: -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
  href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,600;0,700;1,300&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
  rel="stylesheet"
/>
```

- [ ] **Step 5: Build and verify**

```bash
cd web && bun run build
```

Expected: build succeeds, no TypeScript errors.

Then open `cd web && bun dev`, visit `http://localhost:4321`, open DevTools → Network → filter `fonts.goo`. Expected: zero requests to `fonts.googleapis.com` or `fonts.gstatic.com`. Fonts render identically to before.

---

## Task 2: Defer Tour Dates to Client-Side (P1)

**Files:**
- Modify: `web/src/pages/index.astro:20,24,145`

### Context

`index.astro:24` — `const tourDates = await loadTourDates(import.meta.env.PUBLIC_API_URL)` — blocks HTML delivery until the Render API responds. On cold start, Render free tier takes up to 30s. The client-side hydration that replaces `<tbody>` after paint is **already fully implemented** in `web/src/lib/tourTableHydrate.ts` and wired into `TourTable.astro` — it fires when the `apiBase` prop is set. The fix is only removing the SSR await.

- [ ] **Step 1: Read tourTableHydrate.ts to confirm it works**

Read `web/src/lib/tourTableHydrate.ts`. Confirm `hydrateTourTablesFromApi()` reads `[data-tour-upcoming-api]` from the DOM and replaces `<tbody>` rows after a successful fetch. No changes needed to that file.

- [ ] **Step 2: Remove SSR loadTourDates from index.astro**

In `web/src/pages/index.astro`, remove these two lines from the `---` frontmatter:

```diff
- import { loadTourDates } from '../lib/tourDates'
```

```diff
- const tourDates = await loadTourDates(import.meta.env.PUBLIC_API_URL)
```

- [ ] **Step 3: Pass empty rows to TourTable**

In `web/src/pages/index.astro`, find the `<TourTable>` JSX (around line 145) and change:

```diff
- <TourTable rows={tourDates} showAllHref="/contratacion" apiBase={apiBase} />
+ <TourTable rows={[]} showAllHref="/contratacion" apiBase={apiBase} />
```

Keep `apiBase={apiBase}` — this is what sets `data-tour-upcoming-api` on the wrapper div and triggers `hydrateTourTablesFromApi()` after paint.

- [ ] **Step 4: Build and verify**

```bash
cd web && bun run build
```

Expected: build succeeds. `TourDateRow[]` accepts `[]`, so no type errors.

- [ ] **Step 5: Manual browser verification**

```bash
cd web && bun dev
```

Open `http://localhost:4321`. DevTools → Network. Confirm **no** request to `/api/tours/upcoming` fires during initial page load. After `DOMContentLoaded`, observe a client-initiated request to `{PUBLIC_API_URL}/api/tours/upcoming`. TourTable shows "No hay fechas anunciadas por ahora." until the fetch resolves, then populates.

If `PUBLIC_API_URL` is not set in `web/.env.local`, add `PUBLIC_API_URL=http://localhost:3001` and start the API with `bun dev` from the repo root.

---

## Task 3: Remove AOS → Native IntersectionObserver (P2)

**Files:**
- Modify: `web/src/pages/index.astro` (L21 import, L722 AOS block, five `data-aos` attrs)
- Modify: `web/src/components/MemberCard.astro:6` (one `data-aos` attr)
- Modify: `web/src/styles/marketing-press.css` (add `[data-reveal]` rules)

### Context

`import 'aos/dist/aos.css'` is in the critical CSS path — it blocks rendering. DESIGN.md explicitly bans AOS zoom/flip. `@keyframes fadeUp` **already exists** in `marketing-press.css` at L1351 and is used for hero elements — the scroll-reveal styles can reuse the same keyframe shape.

`data-aos="fade-up"` appears in 6 places:
- `index.astro:205` — `.bio-sidebar`
- `index.astro:217` — `.bio-body`
- `index.astro:249` — `.repertoire-card`
- `index.astro:575` — check context when editing
- `MemberCard.astro:6` — `.member-card` wrapper (also present on each rendered member card)

- [ ] **Step 1: Add reveal styles to marketing-press.css**

In `web/src/styles/marketing-press.css`, append after the existing `@keyframes fadeUp` block (around L1365):

```css
/* ─── Scroll reveal (replaces AOS) ───────────────────────── */
[data-reveal] {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.8s ease, transform 0.8s ease;
}

[data-reveal].is-visible {
  opacity: 1;
  transform: translateY(0);
}

@media (prefers-reduced-motion: reduce) {
  [data-reveal],
  [data-reveal].is-visible {
    opacity: 1;
    transform: none;
    transition: none;
    animation: none;
  }
}
```

Using `transition` instead of `animation: fadeUp` so elements already in viewport on load render immediately once JS adds `.is-visible`.

- [ ] **Step 2: Replace data-aos with data-reveal in index.astro**

In `web/src/pages/index.astro`, replace all `data-aos="fade-up"` attributes with `data-reveal` at lines 205, 217, 249, 575:

```diff
- data-aos="fade-up"
+ data-reveal
```

After editing, confirm zero remain:

```bash
grep -n 'data-aos' web/src/pages/index.astro
```

Expected: no output.

- [ ] **Step 3: Replace data-aos in MemberCard.astro**

In `web/src/components/MemberCard.astro:6`:

```diff
- <div class={`member-card ${featured ? "featured" : ""}`} data-aos="fade-up">
+ <div class={`member-card ${featured ? "featured" : ""}`} data-reveal>
```

- [ ] **Step 4: Remove AOS CSS import from index.astro**

In `web/src/pages/index.astro`, remove line 21:

```diff
- import 'aos/dist/aos.css'
```

- [ ] **Step 5: Replace AOS.init script block with IntersectionObserver**

In `web/src/pages/index.astro`, find the `<script>` block around line 722 containing `import AOS from 'aos'` and `AOS.init(...)`. Replace the entire block:

```astro
<script>
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
          observer.unobserve(entry.target)
        }
      }
    },
    { threshold: 0.1 },
  )
  document.querySelectorAll('[data-reveal]').forEach((el) => observer.observe(el))
</script>
```

The observer fires when 10% of the element is visible, adds `.is-visible` (triggering the transition), then stops watching (equivalent to AOS `once: true`).

- [ ] **Step 6: Uninstall AOS packages**

```bash
cd web && bun remove aos @types/aos
```

Expected: both removed from `web/package.json`.

- [ ] **Step 7: Build and check bundle size**

```bash
cd web && bun run build 2>&1 | grep -E "kB|chunk|dist"
```

Expected: build succeeds. AOS JS (~7KB gzipped) and its CSS no longer in output.

- [ ] **Step 8: Manual scroll and motion verification**

```bash
cd web && bun dev
```

Open `http://localhost:4321`. Scroll slowly — bio sidebar, bio body, repertoire cards, testimonial cards, and member cards should all fade+rise as they enter the viewport. DevTools → Network: confirm no `aos.js` or `aos.css` request.

Test reduced motion: DevTools → Rendering → Emulate `prefers-reduced-motion: reduce`. Elements should appear immediately without any animation.

---

## Task 4: Convert Member Images to WebP (P2)

**Files:**
- Create: `web/public/members/hector-baez.webp`, `alexandro-montal.webp`, `diego-cerecer.webp`, `luis-c.webp`, `dimora.webp`
- Modify: `web/src/components/MemberCard.astro`

### Context

Five JPEGs in `web/public/members/`: `hector-baez.jpg` (41KB), `diego-cerecer.jpg` (84KB), `luis-c.jpg` (104KB), `alexandro-montal.jpg` (192KB), `dimora.jpg` (717KB). Total ~1.14MB. WebP at q82 yields ~30–50% reduction.

There are also five `* 1.jpg` files (1.4KB each, filenames contain a space) — these are not referenced by `members.ts` and should **not** be converted.

`MemberCard.astro` already has `loading="lazy"`, `width="180"`, `height="180"`, `decoding="async"` — those attrs do not change.

- [ ] **Step 1: Install cwebp if not present**

```bash
which cwebp || brew install webp
cwebp -version
```

Expected: version string printed (e.g. `1.4.0`).

- [ ] **Step 2: Convert the five member JPEGs to WebP**

```bash
for f in hector-baez alexandro-montal diego-cerecer luis-c dimora; do
  cwebp -q 82 "web/public/members/${f}.jpg" -o "web/public/members/${f}.webp"
done
```

Run from repo root (`/Users/trelo/Cursor Projects/MTO`). Expected: five `.webp` files created. Verify sizes:

```bash
ls -lh web/public/members/*.webp
```

Expected: `dimora.webp` under 400KB (was 717KB). All others proportionally smaller.

- [ ] **Step 3: Update MemberCard.astro to use `<picture>`**

In `web/src/components/MemberCard.astro`, replace:

```astro
<img src={image} alt={name} loading="lazy" width="180" height="180" decoding="async" />
```

With:

```astro
<picture>
  <source srcset={image.replace(/\.jpg$/, '.webp')} type="image/webp" />
  <img src={image} alt={name} loading="lazy" width="180" height="180" decoding="async" />
</picture>
```

The `image` prop is a string like `/members/dimora.jpg`. The regex replace produces `/members/dimora.webp` for the `<source>`. Browsers that support WebP (Chrome, Firefox, Safari 14+) pick the `<source>`; others fall back to the `<img>` JPEG.

- [ ] **Step 4: Build and verify**

```bash
cd web && bun run build
```

Expected: build succeeds, no type errors.

- [ ] **Step 5: Manual browser verification**

```bash
cd web && bun dev
```

Open `http://localhost:4321`. DevTools → Network → filter `members`. Scroll to the members section. Confirm:
- Each request URL ends in `.webp`
- Transfer sizes are smaller than the original JPEGs

JPEG fallback test: in DevTools console, run `document.querySelectorAll('source[type="image/webp"]').forEach(s => s.remove())` — images should still load from `.jpg` sources.

- [ ] **Step 6: Stage WebP files for commit**

```bash
git status web/public/members/
```

Expected: five `.webp` files shown as untracked. They are not gitignored (binary assets in `public/` are tracked). Stage them with the rest of the performance pass commit.

---

## Final Verification Checklist

After all four tasks:

- [ ] `bun test` from repo root — all existing tests pass
- [ ] `cd web && bun run build` — no errors
- [ ] DevTools Network audit on `http://localhost:4321`:
  - [ ] Zero requests to `fonts.googleapis.com` or `fonts.gstatic.com`
  - [ ] No `aos.js` or `aos.css` in requests
  - [ ] Tour API fetch fires **after** page load, not during HTML delivery
  - [ ] Member images served as `.webp`
- [ ] Scroll animations work on bio, repertoire, testimonials, members sections
- [ ] `prefers-reduced-motion` disables all scroll animations
- [ ] No CLS from member images (width/height already set)
