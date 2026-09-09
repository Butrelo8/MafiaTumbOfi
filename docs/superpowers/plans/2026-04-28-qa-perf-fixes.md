# QA & Perf Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 3 QA bugs (form validation, album art, per-field errors) + optimize images for LCP + add correct OG image.

**Architecture:** All changes are isolated to `web/` — no API changes required. Image optimization uses shell tooling (cwebp/ffmpeg). Form fix is a ~20-line JS change in `BookingForm.astro`. Album art downloads go to `web/public/music/`. OG image is a new asset + `Seo.astro` update.

**Tech Stack:** Astro SSR (Vercel), TypeScript, Bun, Playwright (e2e), cwebp/ffmpeg for conversion.

---

## File Map

| File | Action | Reason |
|------|--------|--------|
| `web/src/components/BookingForm.astro` | Modify | Validate name+email before fetch(); add per-field error spans |
| `web/src/pages/index.astro` | Modify | Replace CDN cover URLs with local `/music/*.webp`; hero logo → `<picture>` |
| `web/src/components/ArtworkShelf.astro` | No change | Already renders `item.cover` correctly |
| `web/public/music/` | Create dir + 6 images | Local album art (WebP 160×160) |
| `web/public/icon/mafiatumbada.webp` | Create | Resized logo 794×530 WebP |
| `web/public/marketing-grunge-texture.webp` | Create | Compressed texture WebP ≤800 KB |
| `web/src/components/Seo.astro` | Modify | Default ogImagePath → `/og/og-default.jpg` + add dimension meta |
| `web/public/og/og-default.jpg` | Create | 1200×630 social card JPEG |
| `web/e2e/booking-form.spec.ts` | Create | E2E: empty submit fires no network request |

---

## Task 1: Fix form — block API call on empty submit + per-field errors

**Files:**
- Modify: `web/src/components/BookingForm.astro`
- Create: `web/e2e/booking-form.spec.ts`

The current flow: submit → disable button → build body → `fetch()` → server returns 400. Fix: validate `name` and `email` before calling `fetch()`. Add `<span>` per field for inline error display.

- [ ] **Step 1: Write failing E2E test**

Create `web/e2e/booking-form.spec.ts`:

```typescript
import { test, expect } from '@playwright/test'

test('empty submit fires no network request', async ({ page }) => {
  const requests: string[] = []
  page.on('request', (req) => {
    if (req.url().includes('/api/booking')) requests.push(req.url())
  })

  await page.goto('/contratacion')
  await page.click('button[type="submit"]')
  await page.waitForTimeout(500)

  expect(requests).toHaveLength(0)
})

test('empty submit shows name error immediately', async ({ page }) => {
  await page.goto('/contratacion')
  await page.click('button[type="submit"]')
  await expect(page.locator('#error-name')).toBeVisible()
  await expect(page.locator('#error-name')).toContainText('obligatorio')
})

test('invalid email shows email error immediately', async ({ page }) => {
  await page.goto('/contratacion')
  await page.fill('#name', 'Juan')
  await page.fill('#email', 'notanemail')
  await page.click('button[type="submit"]')
  await expect(page.locator('#error-email')).toBeVisible()
  await expect(page.locator('#error-email')).toContainText('válido')
})
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
cd web && bun run test:e2e -- --grep "booking-form"
```

Expected: tests FAIL (no `#error-name` element exists yet).

- [ ] **Step 3: Add per-field error spans to form HTML**

In `web/src/components/BookingForm.astro`, find the `name` input (line ~29) and `email` input (line ~33). Add `aria-describedby` and a sibling `<span>` after each:

```html
<!-- name field group — replace existing input line -->
<input
  id="name"
  name="name"
  type="text"
  required
  placeholder="Tu nombre completo"
  class="field-input"
  aria-describedby="error-name"
/>
<span id="error-name" class="field-error" role="alert" aria-live="polite"></span>

<!-- email field group — replace existing input line -->
<input
  id="email"
  name="email"
  type="email"
  required
  placeholder="correo@ejemplo.com"
  class="field-input"
  aria-describedby="error-email"
/>
<span id="error-email" class="field-error" role="alert" aria-live="polite"></span>
```

Add CSS in the `<style>` block (before closing `</style>`):

```css
.field-error {
  display: block;
  min-height: 1.25em;
  color: var(--color-error, #e53e3e);
  font-size: 0.8125rem;
  margin-top: 0.25rem;
}
.field-error:empty {
  display: none;
}
```

- [ ] **Step 4: Add client validation before fetch() in script block**

In `web/src/components/BookingForm.astro`, replace the entire `formEl.addEventListener('submit', ...)` handler (lines 321–371) with:

```typescript
formEl.addEventListener('submit', async (e) => {
  e.preventDefault()
  if (!btn) return

  // Clear previous field errors
  const errName = document.getElementById('error-name')
  const errEmail = document.getElementById('error-email')
  if (errName) errName.textContent = ''
  if (errEmail) errEmail.textContent = ''

  const fd = new FormData(formEl)
  const nameVal = (fd.get('name') as string | null)?.trim() ?? ''
  const emailVal = (fd.get('email') as string | null)?.trim() ?? ''
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  let hasError = false
  if (!nameVal) {
    if (errName) errName.textContent = 'El nombre es obligatorio'
    hasError = true
  }
  if (!emailVal || !emailRegex.test(emailVal)) {
    if (errEmail) errEmail.textContent = 'Email no válido'
    hasError = true
  }
  if (hasError) return

  btn.disabled = true
  btn.textContent = 'Enviando…'
  setStatus('loading', 'Enviando…')

  const body = {
    name: nameVal,
    email: emailVal,
    phone: fd.get('phone') || undefined,
    eventDate: fd.get('eventDate') || undefined,
    city: fd.get('city') || undefined,
    eventType: fd.get('eventType') || undefined,
    attendees: fd.get('attendees') || undefined,
    venueSound: fd.get('venueSound') || undefined,
    duration: fd.get('duration') || undefined,
    showType: fd.get('showType') || undefined,
    budget: fd.get('budget') || undefined,
    message: fd.get('message') || undefined,
    website: fd.get('website') || undefined,
  }

  try {
    const res = await fetch(`${apiUrl}/api/booking`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    const data = await res.json().catch(() => ({}))

    if (res.ok) {
      const confirmation = data?.data?.confirmation ?? data?.confirmation
      const normalized = normalizeBookingConfirmation(confirmation)
      sessionStorage.setItem(BOOKING_THANKS_SESSION_KEY, JSON.stringify({ confirmation: normalized }))
      formEl.reset()
      syncBudgetHint()
      trackPlausible('Booking Submit')
      window.location.assign('/booking/gracias')
      return
    } else {
      setStatus('error', data?.error?.message || `Error ${res.status}. Vuelve a intentar.`)
    }
  } catch {
    setStatus('error', 'Error de conexión. Revisa tu internet e intenta de nuevo.')
  } finally {
    btn.disabled = false
    btn.textContent = 'Enviar solicitud'
  }
})
```

- [ ] **Step 5: Run tests — expect PASS**

```bash
cd web && bun run test:e2e -- --grep "booking-form"
```

Expected: all 3 tests PASS.

- [ ] **Step 6: Verify build**

```bash
cd web && bun build
```

Expected: exits 0.

- [ ] **Step 7: Commit**

```bash
git add web/src/components/BookingForm.astro web/e2e/booking-form.spec.ts
git commit -m "fix(form): validate name+email client-side before fetch; add per-field error spans with aria"
```

---

## Task 2: Host album art locally (fix 6 broken CDN images)

**Files:**
- Create: `web/public/music/lv.webp`, `la-bubu.webp`, `no-te-he-olvidado.webp`, `tal-vez.webp`, `corazon.webp`, `besos.webp`
- Modify: `web/src/pages/index.astro` (lines 34–83, `artworkShelfItems` array)

- [ ] **Step 1: Download 6 album cover images**

```bash
mkdir -p web/public/music

curl -L -o web/public/music/lv.jpg \
  "https://image-cdn-ak.spotifycdn.com/image/ab67616d00001e02e6486bbb6fe87cd413317314"

curl -L -o web/public/music/la-bubu.jpg \
  "https://image-cdn-fa.spotifycdn.com/image/ab67616d00001e0255518576a807e01106d1a8a4"

curl -L -o web/public/music/no-te-he-olvidado.jpg \
  "https://image-cdn-ak.spotifycdn.com/image/ab67616d00001e022ec48e2f3aa0af92dcc2b79d"

curl -L -o web/public/music/tal-vez.jpg \
  "https://image-cdn-ak.spotifycdn.com/image/ab67616d00001e02c037fb8a3cd0c1aa9f0a6fd6"

curl -L -o web/public/music/corazon.jpg \
  "https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/ab/5b/43/ab5b432b-2af6-2bbb-40ad-1af0d02f770b/859796890896_cover.jpg/600x600bb.jpg"

curl -L -o web/public/music/besos.jpg \
  "https://image-cdn-fa.spotifycdn.com/image/ab67616d00001e029f79aa3da0cf2d9654df2ce1"

ls -lh web/public/music/
```

Expected: 6 `.jpg` files, each ~30–80 KB. If any returns 403, download manually from the Spotify/Apple Music web player at the corresponding track page and save with the same filename.

- [ ] **Step 2: Convert to WebP at 160×160 (2× display size)**

```bash
# Requires: brew install webp
for f in web/public/music/*.jpg; do
  base="${f%.jpg}"
  cwebp -q 82 -resize 160 160 "$f" -o "${base}.webp"
done
ls -lh web/public/music/*.webp
```

If `cwebp` not available, use ffmpeg:
```bash
for f in web/public/music/*.jpg; do
  base="${f%.jpg}"
  ffmpeg -i "$f" -vf scale=160:160 -c:v libwebp -quality 82 "${base}.webp" -y
done
```

Expected: 6 `.webp` files, each ≤15 KB.

- [ ] **Step 3: Update artworkShelfItems in index.astro**

In `web/src/pages/index.astro`, replace lines 34–83 with:

```typescript
const artworkShelfItems = [
  {
    title: 'L.V.',
    subtitle: 'Corrido tumbado',
    href: 'https://open.spotify.com/intl-es/album/070MvKHW6m7CV17k0EeYjz?go=1&sp_cid=0d6d738c-4142-4435-ae8f-f760b4483f00&utm_source=spotify_web_player&utm_medium=mobile&sp_cid=0d6d738c-4142-4435-ae8f-f760b4483f00&fallback=getapp',
    label: 'Spotify',
    cover: '/music/lv.webp',
  },
  {
    title: 'L.A. BUBU',
    subtitle: 'Single',
    href: 'https://open.spotify.com/intl-es/track/5djRHmBwycYgJbqtpF8FPN',
    label: 'Spotify',
    cover: '/music/la-bubu.webp',
  },
  {
    title: 'No Te He Olvidado',
    subtitle: 'Regional',
    href: 'https://music.apple.com/es/song/no-te-he-olvidado/1794933904',
    label: 'Apple Music',
    cover: '/music/no-te-he-olvidado.webp',
  },
  {
    title: 'Tal Vez',
    subtitle: 'Corrido tumbado',
    href: 'https://open.spotify.com/intl-es/track/54nPL89TjXqZ2UYRO1PvBD?si=e276a7b6475d470c',
    label: 'Spotify',
    cover: '/music/tal-vez.webp',
  },
  {
    title: 'Corazón',
    subtitle: 'Regional',
    href: 'https://music.apple.com/es/album/coraz%C3%B3n-single/1779090777',
    label: 'Apple Music',
    cover: '/music/corazon.webp',
  },
  {
    title: 'Besos',
    subtitle: 'Single',
    href: 'https://youtu.be/kAdwJ-0F8mU?si=H2Y-8VBsuOdIdtQo',
    label: 'YouTube',
    cover: '/music/besos.webp',
  },
]
```

- [ ] **Step 4: Verify build**

```bash
cd web && bun build
```

Expected: exits 0.

- [ ] **Step 5: Commit**

```bash
git add web/public/music/ web/src/pages/index.astro
git commit -m "fix(album-art): download and host 6 cover images locally; replace Spotify/Apple CDN URLs"
```

---

## Task 3: Optimize hero images for LCP

**Files:**
- Create: `web/public/marketing-grunge-texture.webp`
- Create: `web/public/icon/mafiatumbada.webp`
- Modify: `web/src/pages/index.astro` (hero logo img → `<picture>`)
- Modify: any CSS/astro file referencing `marketing-grunge-texture.png` (find in Step 1)

- [ ] **Step 1: Find all references to both images**

```bash
grep -rn "marketing-grunge-texture\|mafiatumbada\.png" \
  web/src/ --include="*.astro" --include="*.css" --include="*.ts"
```

Note every `file:line` — you will update each one in Steps 4–5.

- [ ] **Step 2: Convert marketing-grunge-texture.png → WebP**

```bash
cwebp -q 70 web/public/marketing-grunge-texture.png \
  -o web/public/marketing-grunge-texture.webp
ls -lh web/public/marketing-grunge-texture.webp
```

Expected: ≤800 KB. If still over, lower to `-q 55`.

ffmpeg fallback:
```bash
ffmpeg -i web/public/marketing-grunge-texture.png \
  -c:v libwebp -quality 70 web/public/marketing-grunge-texture.webp -y
```

- [ ] **Step 3: Convert mafiatumbada.png → WebP resized to 794×530**

Logo is 1536×1024 but displayed at ~397×264. 2× for retina = 794×530:

```bash
cwebp -q 85 -resize 794 530 web/public/icon/mafiatumbada.png \
  -o web/public/icon/mafiatumbada.webp
ls -lh web/public/icon/mafiatumbada.webp
```

Expected: ≤80 KB.

ffmpeg fallback:
```bash
ffmpeg -i web/public/icon/mafiatumbada.png \
  -vf scale=794:530 -c:v libwebp -quality 85 \
  web/public/icon/mafiatumbada.webp -y
```

- [ ] **Step 4: Update hero logo in index.astro**

Find line ~114 in `web/src/pages/index.astro`:

```html
<!-- BEFORE -->
<img src="/icon/mafiatumbada.png" alt="Mafia Tumbada" class="hero-logo-img" />

<!-- AFTER -->
<picture>
  <source srcset="/icon/mafiatumbada.webp" type="image/webp" />
  <img
    src="/icon/mafiatumbada.png"
    alt="Mafia Tumbada"
    class="hero-logo-img"
    width="397"
    height="264"
    fetchpriority="high"
    loading="eager"
  />
</picture>
```

- [ ] **Step 5: Update marketing-grunge-texture reference**

From Step 1 output, locate each reference. For CSS `background-image` usage, change the URL to `.webp`:

```css
/* BEFORE */
background-image: url('/marketing-grunge-texture.png');

/* AFTER */
background-image: url('/marketing-grunge-texture.webp');
```

For any `<img>` tag, wrap with `<picture>`:

```html
<picture>
  <source srcset="/marketing-grunge-texture.webp" type="image/webp" />
  <img src="/marketing-grunge-texture.png" alt="" aria-hidden="true" />
</picture>
```

- [ ] **Step 6: Verify sizes and build**

```bash
ls -lh web/public/marketing-grunge-texture.webp web/public/icon/mafiatumbada.webp
cd web && bun build
```

Expected: texture ≤800 KB; logo ≤80 KB; build exits 0.

- [ ] **Step 7: Commit**

```bash
git add web/public/marketing-grunge-texture.webp web/public/icon/mafiatumbada.webp \
  web/src/pages/index.astro
git commit -m "perf(images): convert hero images to WebP — 4.5MB texture + 1.2MB logo → WebP, resize logo to display dimensions"
```

---

## Task 4: SEO — Add correct OG image (1200×630)

**Files:**
- Create: `web/public/og/og-default.jpg`
- Modify: `web/src/components/Seo.astro`

- [ ] **Step 1: Create OG image asset**

Design reference: DESIGN.md Veracruz Noir — dark background (#0a0a0a), gold accent (#c9a84c), turquoise secondary (#7ec8c8). Size: 1200×630 px, JPEG quality 85.

**Option A — ImageMagick (fast):**
```bash
mkdir -p web/public/og
convert -size 1200x630 \
  gradient:'#0a0a0a-#1a1a1a' \
  -font Helvetica -fill '#c9a84c' -pointsize 80 \
  -gravity Center -annotate +0-80 'MAFIA TUMBADA' \
  -fill '#7ec8c8' -pointsize 36 \
  -annotate +0+20 'Corrido Tumbado · Regional Mexicano' \
  -fill '#666666' -pointsize 24 \
  -annotate +0+80 'mafiatumbada.com' \
  -quality 85 \
  web/public/og/og-default.jpg
ls -lh web/public/og/og-default.jpg
```

**Option B — Manual export:** Design in Figma/Canva at 1200×630 using DESIGN.md tokens. Export JPEG quality 85 → `web/public/og/og-default.jpg`.

Expected: file exists, ≤200 KB.

- [ ] **Step 2: Update Seo.astro — change default ogImagePath**

In `web/src/components/Seo.astro` line 26:

```typescript
// BEFORE
ogImagePath = '/icon/mafiatumbada.png',

// AFTER
ogImagePath = '/og/og-default.jpg',
```

- [ ] **Step 3: Add OG image dimension meta tags**

In `web/src/components/Seo.astro`, after the existing `<meta property="og:image" .../>` line (line ~59), add:

```html
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:type" content="image/jpeg" />
```

- [ ] **Step 4: Verify build + spot-check output**

```bash
cd web && bun build
grep -A6 "og:image" web/dist/index.html 2>/dev/null | head -20
```

Expected: build exits 0; `og:image` content ends with `/og/og-default.jpg`; width=1200 and height=630 tags present.

- [ ] **Step 5: Commit**

```bash
git add web/public/og/og-default.jpg web/src/components/Seo.astro
git commit -m "feat(seo): add 1200x630 OG social card image; add og:image dimension + type meta tags"
```

---

## Self-Review

### Spec Coverage

| Ticket | Task | Covered |
|--------|------|---------|
| Perf — LCP images (texture + logo) | Task 3 | ✅ WebP conversion + `<picture>` + size targets |
| QA — form validation (block API call) | Task 1 Steps 4 | ✅ validate before fetch, return early |
| QA — album art local hosting | Task 2 | ✅ download + WebP + update URLs |
| QA — per-field form errors | Task 1 Steps 3–4 | ✅ `#error-name` / `#error-email` spans + aria |
| SEO — OG image 1200×630 | Task 4 | ✅ asset + default path + dimension meta |

### Acceptance Criteria

- `marketing-grunge-texture.webp` ≤800 KB — Step 3.6 checks with `ls -lh`
- `mafiatumbada.webp` ≤80 KB — Step 3.6 checks with `ls -lh`
- Empty form submit fires 0 network requests — Task 1 E2E test asserts this
- All 6 album covers render locally — Task 2 replaces all CDN URLs
- Per-field errors under each input — Task 1 adds `#error-name`, `#error-email` spans
- OG image at `/og/og-default.jpg`, 1200×630 — Task 4 Step 4 grep verifies
- `bun build` green — each task ends with build verify
