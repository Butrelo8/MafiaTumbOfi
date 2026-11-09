#!/usr/bin/env bash
# One command to serve the truck prototype: mirror the repo to ext4 (a build on /mnt/e takes ~6.5 min; on ext4 ~2 s),
# install, build, preview on 0.0.0.0:${PORT:-3109} (tailnet: http://thiccpc-wsl:3109).
set -euo pipefail
cd "$(dirname "$0")/.."
M=${MIRROR:-$HOME/.cache/mto-goblindrone-site}
mkdir -p "$M"
rsync -a --delete --exclude node_modules --exclude blender --exclude dist --exclude .git --exclude research/tmp \
  --exclude research/lighthouse --exclude .astro --exclude revisar --exclude docs/prototipo-camion ./ "$M/"
cd "$M" && bun install --silent && bunx astro build >/dev/null && exec bunx astro preview --port "${PORT:-3109}" --host 0.0.0.0
