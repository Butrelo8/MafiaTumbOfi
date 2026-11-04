# 04 — Tour dates without a DB

> VOID — section `#fechas` cut in SPEC §2 (ticket 02). Tour dates are not on the page.
Labels: `wayfinder:grilling` · Blocks: 02 · Blocked by: — · Assignee: —

## Question
`TourTable` fetches `{apiBase}/api/tours/upcoming`. With no backend, where do dates live?
Options: a committed JSON/MD file edited by hand, a hosted sheet/Airtable read at build time,
or drop the section entirely. Who updates it and how often decides this.
