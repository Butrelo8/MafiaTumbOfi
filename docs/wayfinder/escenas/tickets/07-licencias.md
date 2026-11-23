---
title: Licences for the manager's figure and the Tripo terms
type: grilling
status: closed
assignee:
gate: owner
blocked_by: []
closed_as: decided
gist: owner #71: keep the risk until go-live; owner accepts it for production
---

## Question

Plan v2 §0 lists three open licence items (`docs/design/escenas-plan.md`, lines 34–42; licence file:
`docs/licencias/tripo-figuras.md`):
1. **The manager's figure is outside the Tripo licence.** The licence covers exactly three files: Héctor, Diego and
   Alejandro/Alexandro. Every regenerated figure is a new file and needs adding too.
2. **The licence header still reads "[Date]".**
3. **One line from the friend** would confirm that figures shipped modified inside one scene file count as "part of a
   completed project".

The G63 also has no licence on file. The owner accepted that risk for public previews, with no credits line
(`docs/handoffs/2026-11-20-g63-nuevo-rack.md`). Production now serves it.

## Options

- The friend adds the manager's figure (and any regenerated figures), fills in the date and confirms the real-time use.
  Then close all three.
- Regenerate the manager on the friend's account, then add that file to the licence.
- Keep the risk as it is until go-live, and record the owner's acceptance for production too.

## Done-check

The owner's answer is recorded, along with the updated `docs/licencias/tripo-figuras.md`, or a note saying why it
did not change.

## Resolution

owner #71: keep the risk until go-live; owner accepts it for production
