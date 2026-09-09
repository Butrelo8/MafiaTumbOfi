# Task 9 Report

## Scope

Verified the static rebuild performance budget without changing site code or
hero assets. Updated only `.wayfinder/SPEC.md` §9 and this report. Preserved
unrelated tracked and untracked worktree files.

## Build and serve

- `bun run build` — passed; generated `dist/`.
- `bun run preview -- --host 127.0.0.1 --port 4321` — served the production
  build at `http://127.0.0.1:4321/`.

## Mobile-throttled Lighthouse baseline

Run date: 2026-09-09.

Chrome launch command used before Lighthouse:

```text
/usr/bin/chromium-browser --headless=new --no-sandbox --disable-dev-shm-usage --remote-debugging-port=9222 --user-data-dir=/tmp/mto-task-9-chrome-profile about:blank > /tmp/mto-task-9-chrome.log 2>&1 & CHROME_PID=$!
```

Stopped after Lighthouse with `kill "$CHROME_PID"`.

Lighthouse command:

```text
bunx lighthouse@13.1.0 http://127.0.0.1:4321/ --port=9222 --only-categories=performance,accessibility --form-factor=mobile --throttling-method=simulate --screenEmulation.mobile=true --output=json --output-path=/tmp/mto-task-9-lighthouse.json --quiet
```

Chrome was launched headlessly with `--no-sandbox --disable-dev-shm-usage` on
debug port 9222. Lighthouse reported mobile form factor, simulated throttling:
150 ms RTT, 1,638.4 Kbps throughput, and 4× CPU slowdown.

| Metric | Target | Observed | Status |
| --- | --- | --- | --- |
| Initial load / total transfer | < 1 MB | 9,279 KiB (9,502,187 bytes) | Miss — 8,255 KiB above 1 MiB |
| LCP | < 2.5 s | 8.909 s | Miss — 6.409 s above target |
| TBT | < 200 ms | 150 ms | Pass |
| Performance score | ≥ 90 | 73 | Miss — 17 points short |
| Accessibility score | ≥ 96 | 96 | Pass |

## Output-size check

`dist/` totals 13 MB. Largest relevant generated asset:

| Asset | Bytes |
| --- | ---: |
| `dist/video/hero.mp4` | 10,036,145 |
| `dist/marketing-grunge-texture.webp` | 1,056,016 |

`hero.mp4` was inspected for size only and not modified, as required.

## Validation

- `bun run build` — passed.
- Mobile throttled Lighthouse run — completed; results recorded in
  `.wayfinder/SPEC.md` §9.
- Generated output and relevant asset sizes — checked.
- `git diff --check` — passed before baseline/report edits; rerun after edits
  before commit.

## Concerns

The baseline misses the initial-load, LCP, and performance-score targets.
The unchanged 10,036,145-byte hero video is the dominant transfer; no asset
work, redesign, or CI performance gate was added because all are out of scope.
