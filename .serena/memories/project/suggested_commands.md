## Development Commands

### API (root)
```bash
bun dev              # API dev server on :3001 (hot reload)
bun test             # Unit + integration tests
bun test --watch     # Watch mode
bun test <file.test.ts>  # Single test file
bun run lint         # Biome check
bun run format       # Biome format --write
bun run lint:fix     # Biome check --write --unsafe
```

### Database
```bash
bun run db:generate  # Generate Drizzle migrations after schema changes
bun run db:migrate   # Apply pending migrations
bun run db:studio    # Drizzle Studio GUI
```

### Frontend (web/)
```bash
cd web && bun dev            # Astro dev server on :4321
cd web && bun build          # Production build (Vercel adapter)
cd web && bun run test:e2e   # Playwright smoke test
```

### Git
```bash
git status           # Check working tree
git diff --stat      # File change summary
git diff [base]...HEAD  # All changes since base branch
git log --oneline -n 20  # Recent commits
```

### Verification at End
```bash
bun test             # Full test suite
cd web && bun run build  # Production build check
cd web && bunx playwright test  # E2E (requires API running on :3001)
```

See CLAUDE.md for full details.
