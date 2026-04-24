# FilmStrip Band Photos Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **Skip all git steps — no commits.**

**Goal:** Replace the three striped placeholder divs in `FilmStrip.astro` with real band photos that render with grayscale-to-color hover treatment matching the Veracruz Noir aesthetic.

**Architecture:** Three parts: (1) drop photo files into `web/public/band/`, (2) update `FilmStrip.astro` to add `src` to each frame and swap `<div class="film-strip-placeholder">` for `<img>`, (3) update CSS in `marketing-press.css` — remove striped placeholder rule, add `img` styles with `object-fit: cover`, grayscale filter, and hover color reveal. Remove the "Fotos reales próximamente" note once photos are wired.

**Tech Stack:** Astro static HTML, CSS `filter: grayscale()`, `object-fit: cover`.

---

## File Map


| Action     | File                                                     | Responsibility                                                     |
| ---------- | -------------------------------------------------------- | ------------------------------------------------------------------ |
| **Create** | `web/public/band/band-1.jpg`, `band-2.jpg`, `band-3.jpg` | Actual band photo assets                                           |
| **Modify** | `web/src/components/FilmStrip.astro`                     | Add `src` to frames, swap placeholder div for `<img>`, remove note |
| **Modify** | `web/src/styles/marketing-press.css:1665–1687`           | Remove placeholder CSS, add real `img` styles                      |


---

### Task 1: Add photo assets

**Files:**

- Create: `web/public/band/band-1.jpg`
- Create: `web/public/band/band-2.jpg`
- Create: `web/public/band/band-3.jpg`
- **Step 1: Obtain 3 band photos**
Source options (priority order):
  1. Ask band manager for hi-res press photos — JPG, minimum 800×600px, landscape orientation (component uses `aspect-ratio: 4/3`).
  2. Download from band Instagram or Facebook — crop to landscape if needed.
  3. Screenshot from `/video/hero.mp4` — pause at good frames, crop to 4:3.
  Requirements:
  - Landscape orientation (wider than tall) — matches `aspect-ratio: 4/3`
  - Minimum 800px wide (displayed at max 280px, 2× for retina)
  - JPG, under 500KB each
  - Content: band performing, group posed, or on stage — not individual portraits (those live in `/members/`)
- **Step 2: Create directory and copy files**
  ```bash
  mkdir -p web/public/band
  cp ~/Downloads/band-photo-1.jpg web/public/band/band-1.jpg
  cp ~/Downloads/band-photo-2.jpg web/public/band/band-2.jpg
  cp ~/Downloads/band-photo-3.jpg web/public/band/band-3.jpg
  ```
  Verify:
  ```bash
  ls -lh web/public/band/
  # Expected: three .jpg files, each under 500KB
  ```

---

### Task 2: Wire photos into FilmStrip component

**Files:**

- Modify: `web/src/components/FilmStrip.astro`
- **Step 1: Replace entire file content**
  ```astro
  ---
  const frames = [
    { src: '/band/band-1.jpg', alt: 'Mafia Tumbada en tarima — imagen 1 de 3' },
    { src: '/band/band-2.jpg', alt: 'Mafia Tumbada en tarima — imagen 2 de 3' },
    { src: '/band/band-3.jpg', alt: 'Mafia Tumbada en tarima — imagen 3 de 3' },
  ]
  ---

  <section class="film-strip" aria-label="Detrás de cámaras">
    <div class="film-strip-inner">
      {
        frames.map((f) => (
          <div class="film-strip-frame">
            <img
              src={f.src}
              alt={f.alt}
              class="film-strip-img"
              loading="lazy"
              decoding="async"
              width="560"
              height="420"
            />
          </div>
        ))
      }
    </div>
  </section>
  ```
  > `width="560" height="420"` = 4:3 at 2× retina — prevents layout shift. `loading="lazy"` defers off-screen load. "Fotos reales próximamente" note removed — real photos now wired.

---

### Task 3: Update CSS

**Files:**

- Modify: `web/src/styles/marketing-press.css:1665–1687`
- **Step 1: Replace `.film-strip-placeholder` and `.film-strip-note` blocks**
Find `.film-strip-placeholder` at line 1665. Replace from that line through `.film-strip-note` closing `}` (lines 1665–1687) with:
  ```css
  .film-strip-img {
    display: block;
    width: 100%;
    height: auto;
    aspect-ratio: 4 / 3;
    object-fit: cover;
    border-radius: 4px;
    border: 1px solid var(--border);
    box-shadow: 0 12px 40px oklch(5% 0 0 / 0.5);
    filter: grayscale(100%) contrast(1.05);
    transition: filter 0.4s ease, transform 0.4s ease, box-shadow 0.4s ease;
  }

  .film-strip-frame:hover .film-strip-img {
    filter: grayscale(0%) contrast(1);
    transform: translateY(-4px) scale(1.02);
    box-shadow:
      0 20px 50px oklch(5% 0 0 / 0.7),
      0 0 30px var(--burgundy-glow);
  }
  ```
  > Grayscale at rest — editorial noir feel. Full color on hover — reveals warmth. Burgundy glow on hover ties into palette. Transition on compositor-friendly properties only (`filter`, `transform`, `box-shadow`).
- **Step 2: Start dev server and verify**
  ```bash
  cd web && bun dev
  # Open http://localhost:4321, scroll to FilmStrip section
  ```
  Checklist:
  - Three photos visible in grayscale
  - `aspect-ratio: 4/3` maintained — no distortion or squash
  - Hover: color reveals, slight lift, burgundy glow
  - No striped placeholder visible
  - No "Fotos reales próximamente" text
  - No horizontal overflow at 360px (resize DevTools)
- **Step 3: Verify production build**
  ```bash
  cd web && bun run build
  # Expected: Build complete, no errors
  ```

---

## Self-Review

**Spec coverage:**

- ✅ Photos in `web/public/band/` — Task 1
- ✅ `FilmStrip.astro` wired with `src` + real `<img>` — Task 2
- ✅ CSS updated — placeholder removed, grayscale + hover — Task 3
- ✅ Note removed from markup and CSS
- ✅ Performance — `loading="lazy"`, `decoding="async"`, explicit dimensions
- ✅ Mobile check included

**Placeholder scan:** No TBD/TODO. All paths, CSS, markup concrete.

**Type consistency:** `film-strip-img` class in Astro markup (Task 2) matches CSS selector (Task 3). Old `film-strip-placeholder` fully replaced in both markup and CSS.