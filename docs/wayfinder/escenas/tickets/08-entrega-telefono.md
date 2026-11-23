---
title: Phone delivery, pre-rendered clips (plan v2) or the live three.js scene
type: grilling
status: open
assignee:
gate: owner
blocked_by: [01]
closed_as:
gist:
---

## Question

**The conflict.**
- Plan v2 §3 says phones get pre-rendered clips scrubbed by scroll, with idle loops at 540×960. The budget is 3 MB or
  less to enter and 1 MB or less per move.
- The live home serves the real-time three.js scene to phones today, and the field LCP p75 there is 22 s.

Ticket 01's measurements show what page-first alone buys. Then the owner picks.

## Options

- Phones get the pre-rendered clips and DOM overlays, as plan v2 §3 says, and desktop keeps three.js.
- Phones keep the live three.js scene, slimmed to plan v2's 3 MB entry budget, measured on a real phone.
- Phones get the clips by default, and the live scene opens on tap.

## Done-check

The owner's pick is recorded, along with ticket 01's LCP numbers that informed it.
