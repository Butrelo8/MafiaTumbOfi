# Tripo figures: usage licence (summary)

The original is plain text and is kept **outside git**, beside the GLBs it covers, because it carries both parties' full legal
names and this repository is public:
`blender/assets/reparto/LICENCIA-tripo-original.txt` (git-ignored, main checkout), copied from the owner's Downloads on 2026-11-13.
Names are replaced by roles below; the original is the authority.

- **Title:** 3D Asset Usage Authorization & License.
- **Licensor:** the friend who made the figures on his Tripo AI Pro account (a games 3D artist).
- **Licensee:** the band's site owner.
- **Covers exactly three files**, "No other assets are included":
  1. `cartoon character 3d model hector.glb` → our `blender/assets/reparto/hector.glb` (and `hector-v1.glb`)
  2. `3d cartoon character Diego.glb` → `diego.glb`
  3. `cartoon character 3d model Alejandro.glb` → `alejandro.glb` (the member Alexandro Montal)
- **Grant:** non-exclusive, worldwide, royalty-free, perpetual; personal and commercial use. It allows modifying, texturing and
  rigging the files, and "rendering, displaying, reproducing, and distributing the assets as part of completed projects". Files may
  be shared with collaborators.
- **Restrictions:** no resale or redistribution "as standalone 3D models or asset packs"; no claim to have generated them; no
  use in a product that competes with Tripo. Usage rights only, ownership stays with the licensor.
- **Effective:** on electronic delivery; no signature required.

## Open points

1. **Date.** The header still reads "**Date of Authorization:** [Date]"; the closing line reads "Date: 11/13/2026." Ask the
   licensor to fill the header with the same date so the two agree.
2. **Not covered:**
   - `manager.glb`, from the Downloads original `cartoon character 3d model.glb` (El Manco, the manager). He now gets a name plate,
     a card, a head grid and a pose, so his figure needs to be **added to the licence** (a second authorization or an amended list),
     or regenerated on the licensor's account and then added.
   - `alexandro_v4.glb` (65 MB, in `blender/assets/reparto/`): not used by any script; not covered. Leave it out of the build.
   - The three covered figures are covered **as those files**. A regenerated figure is a new file and needs adding.
3. **Real-time on desktop and "standalone models".** The live scene serves the figures to every visitor's browser. The licence
   allows distribution "as part of completed projects" and bars it "as standalone 3D models". How the site stays on the right
   side of that:
   - The figures ship only inside one scene file with the truck, the road and the props (`escena.glb`), never as `hector.glb` or
     any per-figure file, and never under the original file names.
   - They are modified before they ship: decimated to ≤ 30k triangles, rigged, posed, and compressed with Draco or meshopt
     and KTX2 textures.
   - There is no download link, no viewer for a figure alone, and the scene file is not listed anywhere.
   - What remains is that anyone with dev tools can pull the scene file out of the network tab. That is the visitor
     extracting it, not the licensee redistributing a model. The phone version ships no GLB at all, only rendered video.
   - To close the remaining doubt, one line from the licensor would settle it: "serving the assets to website visitors
     inside a real-time 3D scene is a use as part of a completed project". Not legal advice.
