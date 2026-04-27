## Code Style & Conventions

**Linting:** Biome applies to `src/**/*.ts`, `scripts/**/*.ts`, `web/src/**/*.ts`. Astro `.astro` files excluded.

**Style:** Single quotes, no semicolons, 100-char line width, `noExplicitAny: error`.

**Naming:**
- Variables/functions: `camelCase`
- Components: `PascalCase`
- Classes/types: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Hooks: `use` prefix (`useReducedMotion`)
- CSS classes: kebab-case

**TypeScript:** Strict mode. Named exports preferred over default.

**Patterns:**
- Immutable updates (never mutate in-place)
- Typed errors — never swallow silently
- Parameterized queries always — never string interpolation in SQL
- Migrations always reversible, never destructive without backup
- Validate inputs at route handler level before business logic

**Frontend (Astro + CSS):**
- Semantic HTML first
- CSS Custom Properties for design tokens (see DESIGN.md)
- Animate only compositor-friendly properties (transform, opacity, clip-path)
- Avoid animating layout properties (width, height, margin, padding, font-size)

**Design System:**
DESIGN.md is source of truth. Read before UI/CSS changes. No hardcoded palette/typography/spacing.

See ~/.claude/rules/ and CLAUDE.md for full details.
