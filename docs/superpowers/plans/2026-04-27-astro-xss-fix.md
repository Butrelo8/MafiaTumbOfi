# Astro XSS Fix (GHSA-j687-52p2-xcff) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate the `define:vars` XSS vector in MarketingLayout.astro and upgrade Astro to ≥6.1.6 to fix the upstream CVE.

**Architecture:** Two phases. Task 1 is an immediate surgical workaround — remove the unused `define:vars` attribute (zero breaking changes, deploys in minutes). Task 2 is the full Astro 4→5 upgrade that fixes the upstream CVE and requires one adapter import path update. Both tasks together fully close GHSA-j687-52p2-xcff.

**Tech Stack:** Astro 4.16.19 → 5.x, `@astrojs/vercel` (serverless adapter), `@clerk/astro`, Bun, Tailwind CSS

---

## Background

`web/src/layouts/MarketingLayout.astro` around line 77 contains:

```astro
<script is:inline define:vars={{ plausibleDataDomain }}>
  window.plausible =
    window.plausible ||
    function () {
      ;(window.plausible.q = window.plausible.q || []).push(arguments)
    }
</script>
<script defer data-domain={plausibleDataDomain} src="https://plausible.io/js/script.js"
></script>
```

**Key insight:** `plausibleDataDomain` is injected into the inline script scope via `define:vars` but is **never referenced inside the script body**. The domain only appears on `data-domain` of the second `<script>` tag, which Astro renders safely as an attribute. Removing `define:vars` eliminates the XSS surface with no functional change.

## File Map

| File | Task | Change |
|------|------|--------|
| `web/src/layouts/MarketingLayout.astro` | 1 | Remove `define:vars={{ plausibleDataDomain }}` from inline script |
| `web/package.json` | 2 | Bump `astro`, `@astrojs/vercel`, `@astrojs/node`, `@astrojs/tailwind` |
| `web/astro.config.mjs` | 2 | Fix vercel adapter import path |
| `web/bun.lockb` | 2 | Auto-updated by bun |

---

## Task 1: Remove unused `define:vars` (immediate XSS fix)

**Files:**
- Modify: `web/src/layouts/MarketingLayout.astro` (line ~77)

- [ ] **Step 1: Confirm the variable is not used inside the inline script body**

  Open `web/src/layouts/MarketingLayout.astro`. Find the block:

  ```astro
  <script is:inline define:vars={{ plausibleDataDomain }}>
    window.plausible =
      window.plausible ||
      function () {
        ;(window.plausible.q = window.plausible.q || []).push(arguments)
      }
  </script>
  ```

  Verify: `plausibleDataDomain` does **not** appear anywhere between the opening and closing `<script>` tags. If it does appear inside the body, stop and reassess before proceeding.

- [ ] **Step 2: Remove `define:vars` from the opening script tag**

  Change:
  ```astro
  <script is:inline define:vars={{ plausibleDataDomain }}>
  ```
  To:
  ```astro
  <script is:inline>
  ```

  The full surrounding block after the change:

  ```astro
  {
    plausibleDataDomain ? (
      <>
        <script is:inline>
          window.plausible =
            window.plausible ||
            function () {
              ;(window.plausible.q = window.plausible.q || []).push(arguments)
            }
        </script>
        <script defer data-domain={plausibleDataDomain} src="https://plausible.io/js/script.js"
        ></script>
      </>
    ) : null
  }
  ```

- [ ] **Step 3: Build**

  ```bash
  cd web
  bun run build
  ```

  Expected: exits 0, no errors.

- [ ] **Step 4: Smoke-test Plausible in dev**

  ```bash
  cd web
  bun dev
  ```

  Open `http://localhost:4321`. DevTools → Network → filter `plausible`. If `PUBLIC_PLAUSIBLE_DOMAIN` is set in `web/.env`, confirm `script.js` loads with correct `data-domain`. If it is not set, the block is hidden — that's expected behavior.

- [ ] **Step 5: Commit**

  ```bash
  git add web/src/layouts/MarketingLayout.astro
  git commit -m "fix(security): remove unused define:vars from Plausible snippet (GHSA-j687-52p2-xcff)"
  ```

---

## Task 2: Upgrade Astro 4 → 5 (upstream CVE fix)

**Files:**
- Modify: `web/package.json`
- Modify: `web/astro.config.mjs`
- Auto-updated: `web/bun.lockb`

Astro v5 removed the `@astrojs/vercel/serverless` sub-path export. The import becomes `@astrojs/vercel`. Everything else (`clerk()`, `tailwind()`, `output: 'server'`) stays the same.

- [ ] **Step 1: Upgrade packages**

  ```bash
  cd web
  bun add astro@latest @astrojs/vercel@latest @astrojs/node@latest @astrojs/tailwind@latest
  ```

  Then confirm the installed Astro version is ≥ 6.1.6:

  ```bash
  node -e "console.log(require('./node_modules/astro/package.json').version)"
  ```

  Expected: a version string ≥ `6.1.6` (e.g. `5.7.0` if on the v5 line, or `6.x.x`).

- [ ] **Step 2: Fix the vercel adapter import in `web/astro.config.mjs`**

  Current file:

  ```js
  import { defineConfig } from 'astro/config';
  import tailwind from '@astrojs/tailwind';
  import vercel from '@astrojs/vercel/serverless';
  import clerk from '@clerk/astro';

  export default defineConfig({
    output: 'server',
    adapter: vercel(),
    integrations: [tailwind(), clerk()],
    vite: {
      server: {
        port: 4321,
      },
    },
  });
  ```

  Change `@astrojs/vercel/serverless` → `@astrojs/vercel`:

  ```js
  import { defineConfig } from 'astro/config';
  import tailwind from '@astrojs/tailwind';
  import vercel from '@astrojs/vercel';
  import clerk from '@clerk/astro';

  export default defineConfig({
    output: 'server',
    adapter: vercel(),
    integrations: [tailwind(), clerk()],
    vite: {
      server: {
        port: 4321,
      },
    },
  });
  ```

- [ ] **Step 3: Run the build and fix any errors**

  ```bash
  cd web
  bun run build 2>&1
  ```

  **Known breakage patterns and fixes:**

  **a) `Cannot find module '@astrojs/vercel/serverless'`**
  Fixed by Step 2.

  **b) `@astrojs/tailwind has been removed`** (if it appears)
  Remove `@astrojs/tailwind` from integrations and configure Tailwind through Vite. Update `web/astro.config.mjs`:

  ```js
  import { defineConfig } from 'astro/config';
  import vercel from '@astrojs/vercel';
  import clerk from '@clerk/astro';

  export default defineConfig({
    output: 'server',
    adapter: vercel(),
    integrations: [clerk()],
    vite: {
      server: { port: 4321 },
    },
  });
  ```

  Ensure `web/src/styles/global.css` (or whichever file holds Tailwind directives) contains:
  ```css
  @tailwind base;
  @tailwind components;
  @tailwind utilities;
  ```
  And that this file is imported in a layout. Check `web/src/layouts/MarketingLayout.astro` and `web/src/layouts/Layout.astro` for existing CSS imports.

  **c) TypeScript narrowing errors** (`string | undefined` not assignable to `string`)
  Add a non-null assertion or conditional. Example:

  ```ts
  // before
  const domain: string = someAstroVar
  // after
  const domain: string = someAstroVar ?? ''
  ```

  Fix each error as it appears. Goal: `bun run build` exits 0.

- [ ] **Step 4: Smoke-test admin login in dev**

  ```bash
  cd web
  bun dev
  ```

  Navigate to `http://localhost:4321/admin`. Expected: redirects to Clerk sign-in page, not a blank page or 500. Sign in. Confirm admin dashboard loads and shows bookings.

- [ ] **Step 5: Smoke-test booking form in dev**

  Ensure the API is running:
  ```bash
  # in a separate terminal, from repo root
  bun dev
  ```

  Navigate to `http://localhost:4321/contratacion`. Fill in Name and Email fields. Submit. Expected: success response or validation error — not a 500 or CORS error.

- [ ] **Step 6: Confirm Astro version ≥ 6.1.6**

  ```bash
  node -e "const v=require('./node_modules/astro/package.json').version; const [maj,min,pat]=v.split('.').map(Number); const ok=(maj>6)||(maj===6&&min>1)||(maj===6&&min===1&&pat>=6); console.log(v, ok?'PASS':'FAIL - need >=6.1.6')"
  ```

  Expected output: version string followed by `PASS`.

  If output is `FAIL`, run:
  ```bash
  bun add astro@^6
  bun run build
  ```

- [ ] **Step 7: Commit**

  ```bash
  git add web/package.json web/bun.lockb web/astro.config.mjs
  git commit -m "fix(security): upgrade astro to v5+ closing GHSA-j687-52p2-xcff upstream"
  ```

---

## Self-Review

**Spec coverage:**
- ✅ XSS vector eliminated — Task 1 removes `define:vars`
- ✅ Astro upgraded to ≥6.1.6 — Task 2 Step 6 gates on confirmed version
- ✅ `bun build` must pass — Steps 3 and 3 both require clean build before commit
- ✅ Admin login verified — Task 2 Step 4
- ✅ Booking form verified — Task 2 Step 5
- ✅ Breaking changes documented — Task 2 Step 3 covers all known Astro v5 breakage patterns

**Placeholder scan:** None found. All steps contain exact commands or exact code.

**Type consistency:** No shared types between tasks.
