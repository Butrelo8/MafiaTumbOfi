# Mafia Tumbada: content brief (step 1)

2026-11-12. Seed: `/home/black/projects/mothership/docs/queue/2026-11-12-mto-direction.md`. Unknowns are marked `[ask: …]`.
Every fact below comes from `research/contenido/` (catalog, members, socials) or `research/wayfinder/SPEC.md` on the main
checkout. Nothing here is invented.

## Why the site exists

- The band just signed with **ONErpm** `[ask: date and the band's own announcement post, to link it]`.
- The site is unpaid. Its value is as a **showcase**: it should bring views and credibility to the band, and indirectly
  to the label.
- It is also the owner's second portfolio case, after StageDanza.
- **Benchmark:** eptosuno.com, an artist on the same label (`docs/design/benchmark.md`). The page has to beat it
  measurably, not by taste.

## Goals, in order

1. A fan reaches a song or video in one tap from the first screen.
2. A booker or promoter writes on WhatsApp with the date and city already in the message.
3. The label, press, and the owner's potential clients see a band that looks signed and serious: real releases, real
   members, a crafted page.

## Who visits and what each one needs

| Visitor | Arrives from | Must find | The one action |
|---|---|---|---|
| Fan (phone, from IG/TikTok bio) | social link | latest release, Spotify / YouTube / Apple links, videos | **Escuchar** (open the latest release on Spotify) |
| Booker / promoter (event, palenque, private party) | search, a shared link | that they play live, where they're based, how to book | **Contratar por WhatsApp** |
| Label / press (ONErpm, media) | the band's link | releases, members, photos, socials | none required; credibility, plus press assets `[ask: press kit or photos they may share]` |
| Owner's potential clients | the owner's portfolio | the craft of the page itself | none on this page; the portfolio case links back |

The page asks one thing per visitor. The primary call to action is **Escuchar** for fans and **Contratar** for bookers.
Both stay visible: Escuchar in the hero, Contratar in the nav and in the closing section.

## Untouchable (brand facts)

- **Name:** La Mafia Tumbada / Mafia Tumbada.
- **Logo:** the beveled black-and-gold "MT" with a lightning bolt (`public/icon/mafiatumbada.webp`). It is not
  blackletter. Its colours (black, bronze-gold bevel, green-bronze patina on the bolt) are the brand's own.
- **Base and genre:** Xalapa, Veracruz. Corridos tumbados, regional mexicano, norteño. "Desde 2021".
- **Contact:** WhatsApp only, no form, no tour dates (both decided in the old SPEC §2 and §4).
- **Members:** Héctor Báez (Vocal Principal), Alexandro Montal (Requintista & Vocal), Diego Cerecer (Guitarra & Coros).

## Needs convincing / open

- `[ask: WhatsApp number]` The sources disagree. SPEC §4 says +52 228 835 1464. `socials.ts` and the old DESIGN.md say
  +52 228 353 8827. Prototypes use the `socials.ts` link.
- `[ask: who is in the 5-person band photo]` `public/band/cover.jpg` shows five people, but `members.ts` lists three.
  The page shows the three in `members.ts` until the band confirms the line-up.
- `[ask: release dates and the newest single]` The catalog has no dates. Prototypes lead with PUTIFRESA, the first entry
  in the catalog.
- `[ask: bio]` The only approved text is SPEC §8: "La Mafia Tumbada es un grupo de corridos tumbados y regional mexicano
  con base en Xalapa, Veracruz. Canciones propias, covers con actitud y cuatro años de tarima."
- `[ask: raw live footage]` We only have YouTube links. A video hero needs the band's own files of the Plaza Lerdo show.
- `[ask: logo source file]` We only have a 790 px webp. A vector or large PNG with alpha is needed.

## Sections in order (one page)

| id | Section (es) | Content | Asset |
|---|---|---|---|
| `hero` | Inicio | logo / name, one line (genre + Xalapa), **Escuchar** + **Contratar** | depends on the direction (3D loop, photo, live footage) |
| `musica` | Música | 9 releases (cover, title, type, link out), Spotify / Apple / YouTube artist links | `public/music/*.webp` |
| `video` | Videos | Plaza Lerdo live video first, then official videos as thumbnails that link out (no embedded players, SPEC §3) | YouTube thumbnails |
| `integrantes` | La banda | 3 members: photo, name, role, Instagram | `public/members/*` |
| `contacto` | Contratación | one line + WhatsApp button with a prefilled message, socials | — |

## Copy skeleton (es first)

- **hero:** `La Mafia Tumbada` · `Corridos tumbados desde Xalapa, Veracruz.` · buttons `Escuchar` / `Contratar`
- **musica:** heading `Música` · each card: title, `Single` / `Corrido tumbado` / `Regional`, the platform name ·
  row `Spotify` `Apple Music` `YouTube`
- **video:** heading `Videos` · first: `En vivo · Plaza Lerdo, Xalapa` (from the video title "MAFIA TUMBADA EN VIVO - PLAZA
  LERDO - MUNDIAL 2026 EN XALAPA") · then the official video titles as they appear on YouTube
- **integrantes:** heading `La banda` · name, role, `@instagram`
- **contacto:** heading `Contratación` · body: the SPEC §8 line "Canciones propias, covers con actitud y cuatro años de
  tarima." · button `Escribir por WhatsApp` (prefilled: "Hola Mafia Tumbada, quiero información para contratarlos. Mi
  evento es el [fecha] en [ciudad].") · socials row

No eyebrows, kickers or numbering above headings (slop tells, tier A). Section names are plain words.

## Directions: the owner's pick

Three directions in `docs/design/directions.md`, compared in `docs/design/directions/index.html`.
`[pending: owner's pick and feedback]`
