# SEO Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement foundational SEO improvements across the MTO web app: robots.txt, title/heading fixes on `/contratacion`, sitemap enhancements, and JSON-LD MusicGroup structured data.

**Architecture:** All changes are confined to the `web/` Astro app. No backend changes. Static `robots.txt` goes to `web/public/`. Schema and layout changes live in `web/src/layouts/MarketingLayout.astro` and `web/src/lib/publicSitemap.ts`. Page-level copy changes in `web/src/pages/contratacion.astro`.

**Tech Stack:** Astro (SSR, Vercel adapter), TypeScript, Bun test runner. No new dependencies.

---

## File Map

| Action | Path | What changes |
|--------|------|--------------|
| Create | `web/public/robots.txt` | Static robots directive + sitemap pointer |
| Modify | `web/src/pages/contratacion.astro` | `title` const + H1 text |
| Modify | `web/src/lib/publicSitemap.ts` | `INDEXABLE_PATHS` → richer config, add `changefreq` + `priority` |
| Modify | `web/src/lib/publicSitemap.test.ts` | Add assertions for new sitemap fields |
| Modify | `web/src/layouts/MarketingLayout.astro` | Add JSON-LD `<script>` block in `<head>` |

---

## Task 1: Add `robots.txt`

**Files:**
- Create: `web/public/robots.txt`

Static file — no tests needed; verify manually via dev server.

- [ ] **Step 1: Create the file**

Create `web/public/robots.txt` with this exact content:

```
User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/

Sitemap: https://mafiatumbada.com/sitemap.xml
```

- [ ] **Step 2: Verify Astro serves it**

```bash
cd web && bun dev
```

Open `http://localhost:4321/robots.txt` in browser. Expected: plain text file contents, no 404.

- [ ] **Step 3: Build check**

```bash
cd web && bun run build
```

Expected: exits 0 with no errors.

---

## Task 2: Fix `/contratacion` title tag + H1

**Files:**
- Modify: `web/src/pages/contratacion.astro` (title const ~line 10, H1 ~line 47)

No new test file — this is copy. Verify visually after dev server.

- [ ] **Step 1: Update the `title` const**

In `web/src/pages/contratacion.astro`, find:

```ts
const title = 'Contrataciones — Press kit — Mafia Tumbada'
```

Replace with:

```ts
const title = 'Contratar a Mafia Tumbada — Xalapa, Veracruz'
```

(46 characters — within the 50–60 target.)

- [ ] **Step 2: Update the H1 text**

In the same file, find:

```html
<h1 class="press-hero-title">Mafia Tumbada</h1>
```

Replace with:

```html
<h1 class="press-hero-title">Contratar a Mafia Tumbada</h1>
```

- [ ] **Step 3: Verify visually**

```bash
cd web && bun dev
```

Open `http://localhost:4321/contratacion`. Check: browser tab shows new title, H1 renders with no layout breaks.

- [ ] **Step 4: Build check**

```bash
cd web && bun run build
```

Expected: exits 0.

---

## Task 3: Enhance sitemap with `changefreq` + `priority`

**Files:**
- Modify: `web/src/lib/publicSitemap.ts`
- Modify: `web/src/lib/publicSitemap.test.ts`

TDD: write failing tests first, then update implementation.

- [ ] **Step 1: Write failing tests**

Open `web/src/lib/publicSitemap.test.ts`. Add these two tests inside the existing `describe('buildPublicSitemapXml', ...)` block:

```ts
test('includes changefreq and priority for homepage', () => {
  const xml = buildPublicSitemapXml('https://mafiatumbada.com')
  expect(xml).toContain('<changefreq>weekly</changefreq>')
  expect(xml).toContain('<priority>1.0</priority>')
})

test('includes changefreq and priority for contratacion', () => {
  const xml = buildPublicSitemapXml('https://mafiatumbada.com')
  expect(xml).toContain('<changefreq>monthly</changefreq>')
  expect(xml).toContain('<priority>0.8</priority>')
})
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /Users/trelo/Cursor\ Projects/MTO && bun test web/src/lib/publicSitemap.test.ts
```

Expected: 2 new tests FAIL — `changefreq` and `priority` not present in output yet.

- [ ] **Step 3: Replace `publicSitemap.ts` implementation**

Open `web/src/lib/publicSitemap.ts` and replace the entire file:

```ts
/**
 * Build `sitemap.xml` body for indexable marketing routes only (no `/admin`).
 */

/** Escape text for XML element bodies (e.g. `<loc>`). */
export function escapeXml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

interface SitemapEntry {
  /** Path segment after the public origin. `''` = homepage. */
  path: string
  changefreq: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never'
  priority: string
}

const INDEXABLE_ENTRIES: SitemapEntry[] = [
  { path: '', changefreq: 'weekly', priority: '1.0' },
  { path: '/contratacion', changefreq: 'monthly', priority: '0.8' },
]

/**
 * @param baseUrl Public site base, e.g. `https://example.com` (trailing slash optional; stripped).
 */
export function buildPublicSitemapXml(baseUrl: string): string {
  const base = baseUrl.trim().replace(/\/$/, '')
  const lines = INDEXABLE_ENTRIES.map(({ path, changefreq, priority }) => {
    const loc = path === '' ? base : `${base}${path}`
    return [
      '  <url>',
      `    <loc>${escapeXml(loc)}</loc>`,
      `    <changefreq>${changefreq}</changefreq>`,
      `    <priority>${priority}</priority>`,
      '  </url>',
    ].join('\n')
  }).join('\n')
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${lines}
</urlset>
`
}
```

- [ ] **Step 4: Run sitemap tests — expect all pass**

```bash
cd /Users/trelo/Cursor\ Projects/MTO && bun test web/src/lib/publicSitemap.test.ts
```

Expected: 4 tests pass (2 existing + 2 new).

- [ ] **Step 5: Run full test suite**

```bash
cd /Users/trelo/Cursor\ Projects/MTO && bun test
```

Expected: all tests pass, no regressions.

- [ ] **Step 6: Build check**

```bash
cd web && bun run build
```

Expected: exits 0.

---

## Task 4: Add JSON-LD `MusicGroup` structured data

**Files:**
- Modify: `web/src/layouts/MarketingLayout.astro`

JSON-LD injected once in the shared marketing layout — covers `/`, `/contratacion`, and any future marketing pages automatically. `bandSocialUrls` and `canonicalUrl` are already in scope in this file.

- [ ] **Step 1: Locate the `<Seo />` component in the layout**

Open `web/src/layouts/MarketingLayout.astro`. Find this block inside `<head>`:

```astro
    <Seo
      title={title}
      description={description}
      canonicalUrl={canonicalUrl}
      themeColor="#0a0a0c"
      robots={robots}
    />
```

- [ ] **Step 2: Insert JSON-LD script immediately after `<Seo />`**

Add the following directly after the closing `/>` of `<Seo>`, before `</head>`:

```astro
    <script type="application/ld+json" set:html={JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'MusicGroup',
      name: 'Mafia Tumbada',
      genre: ['Corridos Tumbados', 'Regional Mexicano'],
      foundingLocation: {
        '@type': 'Place',
        name: 'Xalapa, Veracruz, México',
      },
      url: canonicalUrl,
      sameAs: [
        bandSocialUrls.instagram,
        bandSocialUrls.tiktok,
        bandSocialUrls.spotify,
        bandSocialUrls.youtube,
        bandSocialUrls.appleMusic,
      ],
    })}></script>
```

Note: `set:html` is the Astro directive for injecting unescaped content into a script tag — correct and safe here since the data comes from trusted internal constants, not user input. `bandSocialUrls` is already imported at the top of this file. `canonicalUrl` is already destructured from `Astro.props`.

- [ ] **Step 3: Verify in browser dev server**

```bash
cd web && bun dev
```

Open `http://localhost:4321/`. Right-click → View Page Source. Search for `application/ld+json`. Confirm the script block appears in `<head>` with valid JSON and correct `url` value (`http://localhost:4321` or whatever `PUBLIC_SITE_URL` resolves to).

Open `http://localhost:4321/contratacion` — same check; `url` field should now show the `/contratacion` canonical.

- [ ] **Step 4: Build check**

```bash
cd web && bun run build
```

Expected: exits 0.

---

## Self-Review

### Spec Coverage

| Ticket | Task |
|--------|------|
| Add `robots.txt` with sitemap pointer | Task 1 ✓ |
| Fix `/contratacion` title tag ordering | Task 2 ✓ |
| Clarify `/contratacion` H1 | Task 2 ✓ |
| Enhance sitemap `changefreq` + `priority` | Task 3 ✓ |
| Add JSON-LD `MusicGroup` schema | Task 4 ✓ |
| OG image 1200×630 | Excluded per user request |

### Placeholder Scan

No TBD, TODO, or vague steps. All code blocks complete and copy-pasteable.

### Type Consistency

- `SitemapEntry` interface defined and used only within `publicSitemap.ts` — no cross-task leakage.
- `bandSocialUrls` keys used in Task 4 (`instagram`, `tiktok`, `spotify`, `youtube`, `appleMusic`) match exactly what `web/src/data/socials.ts` exports.
- `canonicalUrl` is `string` in both `MarketingLayout.astro` props and the JSON-LD output — no type mismatch.
