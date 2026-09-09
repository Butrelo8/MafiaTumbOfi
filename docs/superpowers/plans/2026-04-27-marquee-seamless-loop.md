# Marquee Seamless Loop Fix

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the abrupt jump in the marquee banner so the scroll loops seamlessly without a visible reset.

**Architecture:** Pure CSS fix — one file, two property changes. Root cause: `gap: 2rem` on `.marquee-track` makes `translateX(-50%)` land 1rem short of the second span's start, causing a jump at loop reset. Moving spacing from `gap` on the track to `padding-inline-end` on each span makes both halves equal, so `-50%` is a perfect seamless jump point.

**Tech Stack:** CSS only (`web/src/styles/marketing-press.css`). No JS. No new files. No new dependencies.

---

## Why the bug happens

```
Current DOM:  [span1][──2rem gap──][span2]
Total width:  S + 2rem + S  =  2S + 2rem

translateX(-50%)  =  -(S + 1rem)   ← stops 1rem BEFORE start of span2
Loop reset snaps back to 0          → viewer sees a 1rem jump every cycle
```

**After fix:**

```
Fixed DOM:    [span1 + 2rem padding][span2 + 2rem padding]
Total width:  (S+2rem) + (S+2rem)  =  2(S+2rem)

translateX(-50%)  =  -(S + 2rem)   ← lands EXACTLY at start of span2 ✓
```

---

## File Map

| Action | Path | What changes |
|--------|------|--------------|
| Modify | `web/src/styles/marketing-press.css` | `.marquee-track` gap → 0; `.marquee-text` + padding-inline-end; reduced-motion reset |

---

## Task 1: Fix marquee CSS

**Files:**
- Modify: `web/src/styles/marketing-press.css` (lines ~1742–1788)

- [ ] **Step 1: Remove `gap` from `.marquee-track`**

Find (around line 1742):

```css
.marquee-track {
  display: flex;
  width: max-content;
  gap: 2rem;
  padding-block: 0.65rem;
  animation: marquee-scroll 42s linear infinite;
}
```

Replace with:

```css
.marquee-track {
  display: flex;
  width: max-content;
  gap: 0;
  padding-block: 0.65rem;
  animation: marquee-scroll 42s linear infinite;
}
```

- [ ] **Step 2: Add `padding-inline-end` to `.marquee-text`**

Find (around line 1750):

```css
.marquee-text {
  font-family: var(--ff-mono);
  font-size: 0.72rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--burgundy-hot);
  white-space: nowrap;
}
```

Replace with:

```css
.marquee-text {
  font-family: var(--ff-mono);
  font-size: 0.72rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--burgundy-hot);
  white-space: nowrap;
  padding-inline-end: 2rem;
}
```

- [ ] **Step 3: Reset padding inside reduced-motion block**

Find the `@media (prefers-reduced-motion: reduce)` block (around line 1769). The `.marquee-text` rule inside it currently looks like:

```css
  .marquee-text {
    white-space: normal;
    text-align: center;
    letter-spacing: 0.12em;
  }
```

Replace it with:

```css
  .marquee-text {
    white-space: normal;
    text-align: center;
    letter-spacing: 0.12em;
    padding-inline-end: 0;
  }
```

This prevents the 2rem right padding from misaligning the wrapped reduced-motion layout.

- [ ] **Step 4: Verify seamless loop in dev server**

```bash
cd web && bun dev
```

Open `http://localhost:4321/`. Watch the marquee for at least 3 full cycles (~42s each, or resize window to speed visual check). Expected: text scrolls left continuously with no jump or blank gap at the loop boundary.

- [ ] **Step 5: Verify reduced-motion fallback**

In Chrome DevTools → Rendering tab → "Emulate CSS media feature" → set `prefers-reduced-motion: reduce`. Expected: banner shows text wrapped, no extra horizontal padding on items, layout identical to before this change.

- [ ] **Step 6: Build check**

```bash
cd web && bun run build
```

Expected: exits 0.

---

## Self-Review

### Spec Coverage

| Requirement | Task |
|-------------|------|
| Banner scrolls without abrupt jump/reset | Task 1 Steps 1–2 ✓ |
| Reduced-motion fallback unaffected | Task 1 Step 3 ✓ |

### Placeholder Scan

No TBD, TODO, or vague steps. All CSS blocks are complete and copy-pasteable.

### Type Consistency

CSS-only — no types.
