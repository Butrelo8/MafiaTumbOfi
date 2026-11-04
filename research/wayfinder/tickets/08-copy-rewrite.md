# 08 — Copy rewrite for the 7-section page
Labels: `wayfinder:prototype` · Blocks: — · Blocked by: 02, 03 · Assignee: —

## Question
What does each section of `SPEC.md` §2 actually say, in Spanish?

The current copy was written for a promoter funnel — a booking form, `paquetes`, `testimonios`,
a trust-strip and "respondemos cotizaciones en menos de 24 horas". Fans lead now and the only
conversion is one WhatsApp button, so the pitch changes from *hire us* to *listen to us*, with
hiring as the closing move rather than the spine.

Per section (§2 order): hero headline + lede + CTA label · marquee strings · `#musica`
eyebrow/heading + how an auto-fetched release is captioned (§3 supplies title + date only) ·
`#grupo` heading + the 3 member blurbs · bio "El sonido de Xalapa" (survives largely intact?) ·
`#contratacion` headline + the urgency line that replaces the 24h promise · footer.

Salvage vs rewrite: name which existing strings survive verbatim — `index.astro` already holds
usable bio and hero copy, and deleting good Spanish to regenerate worse Spanish is the failure
mode here.

Constraints: Spanish (MX), no English fallback. `DESIGN.md` type rules cap headline length —
`--fs-h1` at `clamp(3.5rem, 2rem + 8vw, 9rem)` means a hero headline is 2–4 words, and Cormorant
italic is allowed on one word max. Eyebrows are ALL CAPS, tracked, short.

Output: the full string set in the spec as §8, keyed by section, ready to paste into `index.astro`.
