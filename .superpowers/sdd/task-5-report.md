# Task 5 report — catalog snapshot fallback

## Scope

Created `src/data/catalog.json`, `src/lib/catalog.ts`, and `src/lib/catalog.test.ts`.
Exported the existing `ShelfItem` interface from `src/components/ArtworkShelf.astro` so the catalog uses the UI card contract directly. No page or UI changes.

## TDD evidence

Red command:

```sh
bun test src/lib/catalog.test.ts
```

Red result: failed as expected before implementation: `Cannot find module './catalog'`; 0 pass, 1 fail.

Green command:

```sh
bun test src/lib/catalog.test.ts
```

Green result: 5 pass, 0 fail, 8 assertions. Tests inject `fetch`; no test makes a network request. Coverage includes Spotify rejection, YouTube rejection, malformed Spotify JSON, Spotify album mapping, RSS video mapping, and missing-credentials snapshot retention.

## Build, fallback, and secret evidence

```sh
export SPOTIFY_CLIENT_ID=task5-scan-only-id
export SPOTIFY_CLIENT_SECRET=task5-scan-only-secret
bun run build
grep -rn "$SPOTIFY_CLIENT_SECRET" dist/ || echo clean
```

Result: pass. Astro built 1 page and completed successfully. The catalog module retains six committed snapshot releases when credentials or Spotify data are unavailable.

The scan result was `clean`. Scan output was captured while checking, and no secret value was printed. Returned catalog data contains mapped public album/video fields only; credentials are not returned.

## Implementation notes

- Spotify token and album requests use `AbortSignal.timeout(10_000)`.
- YouTube playlist RSS request uses `AbortSignal.timeout(10_000)`.
- Each source has an independent fallback: Spotify uses snapshot releases; YouTube uses snapshot videos.
- No dependency, page rewrite, image caching, or runtime worker added.

## Concerns

- Build emitted an existing Browserslist warning that `caniuse-lite` data is 6 months old; unrelated to Task 5.
