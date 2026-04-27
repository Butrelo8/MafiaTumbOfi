## Testing & Verification Protocol

**Minimum Coverage:** 80%

**Test Types:**
- Unit: Functions, utilities, components
- Integration: API endpoints, DB operations
- E2E: Critical user flows (Playwright)

**At Task Completion:**
1. Run full test suite: `bun test` (repo root)
2. Run production build: `cd web && bun run build`
3. Optional E2E (requires both services running): `cd web && bunx playwright test`
4. Check `git status` — review uncommitted changes before committing
5. Scope commits intentionally (one feature per PR or cohesive set)

**Last Verified (2026-04-22):**
- `cd web && bun run build` green
- Targeted `bun test` (homepageHero, adminPageTheme) green
- Full `bun test` should be re-run after major edits

**Test Locations:**
- Backend: `src/**/*.test.ts`
- Frontend: `web/src/**/*.test.ts`
- E2E: `web/tests/`

**Test Structure:** AAA pattern (Arrange-Act-Assert). Descriptive names that explain behavior.

See ~/.claude/rules/common/testing.md and ~/.claude/rules/web/testing.md for detail.
