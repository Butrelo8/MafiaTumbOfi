# Artwork Shelf CD Covers Implementation Plan

**Status:** Shipped **2026-04-21** — see `**CHANGELOG.md`** [Unreleased] and `**TODOS.md`** → **Completed** → **Frontend — ArtworkShelf CD cover art**.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show real CD cover art on each single in the ArtworkShelf instead of initials placeholders.

**Architecture:** Add optional `cover?: string` to `ShelfItem` interface; render `<img>` when present, else keep initials span as fallback. Cover URLs go directly in `artworkShelfItems` array in `index.astro` — no new data file needed.

**Tech Stack:** Astro (`.astro` components), TypeScript interface extension, static image assets or Spotify CDN URLs.

---

## File Map


| File                                    | Action | What changes                                                 |
| --------------------------------------- | ------ | ------------------------------------------------------------ |
| `web/src/components/ArtworkShelf.astro` | Modify | Add `cover?` to `ShelfItem`; render `<img>` vs initials span |
| `web/src/styles/marketing-press.css`    | Modify | Add `.artwork-shelf-img` object-fit rule                     |
| `web/src/pages/index.astro`             | Modify | Add `cover` URLs to `artworkShelfItems` (lines 36–43)        |


---

### Task 1: Extend `ShelfItem` interface and render cover image

**Files:**

- Modify: `web/src/components/ArtworkShelf.astro`
- **Step 1: Replace file content**
  ```astro
  ---
  interface ShelfItem {
    title: string
    subtitle?: string
    href: string
    label: string
    cover?: string
  }
  interface Props {
    items: ShelfItem[]
  }
  const { items } = Astro.props
  ---

  <div class="artwork-shelf" role="region" aria-label="Discografía y streaming">
    <ul class="artwork-shelf-track">
      {
        items.map((item) => (
          <li class="artwork-shelf-item">
            <a href={item.href} class="artwork-shelf-card" target="_blank" rel="noopener noreferrer">
              <div class="artwork-shelf-cover">
                {item.cover ? (
                  <img
                    src={item.cover}
                    alt={item.title}
                    width="80"
                    height="80"
                    loading="lazy"
                    decoding="async"
                    class="artwork-shelf-img"
                  />
                ) : (
                  <span class="artwork-shelf-initial" aria-hidden="true">
                    {item.title.slice(0, 2).toUpperCase()}
                  </span>
                )}
              </div>
              <div class="artwork-shelf-meta">
                <span class="artwork-shelf-title">{item.title}</span>
                {item.subtitle ? <span class="artwork-shelf-sub">{item.subtitle}</span> : null}
                <span class="artwork-shelf-cta">{item.label} →</span>
              </div>
            </a>
          </li>
        ))
      }
    </ul>
  </div>
  ```
- **Step 2: Verify build**
  ```bash
  cd web && bun run build 2>&1 | tail -20
  ```
  Expected: clean build. Shelf still shows initials (no `cover` URLs yet — correct).

---

### Task 2: Add `.artwork-shelf-img` CSS

**Files:**

- Modify: `web/src/styles/marketing-press.css`
- **Step 1: Find `.artwork-shelf-cover` block in `marketing-press.css`**
Note where the block ends so you insert immediately after it.
- **Step 2: Add rule after `.artwork-shelf-cover`**
  ```css
  .artwork-shelf-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: inherit;
    display: block;
  }
  ```
- **Step 3: Verify build**
  ```bash
  cd web && bun run build 2>&1 | tail -10
  ```
  Expected: clean.

---

### Task 3: Add cover URLs to `artworkShelfItems`

**Files:**

- Modify: `web/src/pages/index.astro` (lines 36–43)

**How to get Spotify CDN URLs:**

1. Open Spotify desktop or web.
2. Find the single.
3. Right-click cover image → "Copy image address" → gives an `https://i.scdn.co/image/...` URL.
4. These URLs are public, no auth needed.

Alternatively place square JPGs (≥160×160px) at `web/public/covers/<slug>.jpg` and use `/covers/<slug>.jpg` as the `cover` value.

- **Step 1: Obtain a cover URL for each single**
For each of the 6 entries: L.V., L.A. BUBU, No Te He Olvidado, Tal Vez, Corazón, Besos — get the Spotify CDN URL or place a local file.
Any single without a confirmed URL: omit `cover` entirely — falls back to initials automatically.
- **Step 2: Update `artworkShelfItems` in `index.astro`**
Replace lines 36–43 with (fill in real URLs):
  ```ts
  const artworkShelfItems = [
    {
      title: 'L.V.',
      subtitle: 'Corrido tumbado',
      href: bandSocialUrls.spotify,
      label: 'Spotify',
      cover: 'https://i.scdn.co/image/REAL_LV_HASH',
    },
    {
      title: 'L.A. BUBU',
      subtitle: 'Single',
      href: bandSocialUrls.spotify,
      label: 'Spotify',
      cover: 'https://i.scdn.co/image/REAL_LABUBU_HASH',
    },
    {
      title: 'No Te He Olvidado',
      subtitle: 'Regional',
      href: bandSocialUrls.appleMusic,
      label: 'Apple Music',
      cover: 'https://i.scdn.co/image/REAL_NOTEHE_HASH',
    },
    {
      title: 'Tal Vez',
      subtitle: 'Corrido tumbado',
      href: bandSocialUrls.spotify,
      label: 'Spotify',
      cover: 'https://i.scdn.co/image/REAL_TALVEZ_HASH',
    },
    {
      title: 'Corazón',
      subtitle: 'Regional',
      href: bandSocialUrls.appleMusic,
      label: 'Apple Music',
      cover: 'https://i.scdn.co/image/REAL_CORAZON_HASH',
    },
    {
      title: 'Besos',
      subtitle: 'Single',
      href: bandSocialUrls.youtube,
      label: 'YouTube',
      cover: 'https://i.scdn.co/image/REAL_BESOS_HASH',
    },
  ]
  ```
- **Step 3: Verify visually**
  ```bash
  cd web && bun dev
  ```
  Open `http://localhost:4321`. Scroll to discografía. Each card with a cover URL shows artwork. Cards without show initials.
- **Step 4: Production build check**
  ```bash
  cd web && bun run build 2>&1 | tail -10
  ```
  Expected: clean.

---

## Done When

- Each single with a `cover` URL shows CD artwork (not initials).
- Singles without `cover` still show initials fallback.
- `bun run build` in `web/` is green.
- No layout shift: `<img>` has explicit `width="80" height="80"` attributes.
- No API, drip, booking, or admin code touched.

