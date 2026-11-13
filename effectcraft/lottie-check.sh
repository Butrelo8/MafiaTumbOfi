#!/usr/bin/env bash
# Play an exported Lottie in headless Chromium (lottie-web 5.12.2 from cdnjs): prints totalFrames and the page
# errors, and screenshots frames 2 and 36. effectcraft/lottie-check.sh <dir with titulo.json>
set -euo pipefail
d=$(realpath "$1")
here=$(dirname "$(realpath "$0")")
cp "$here/lottie-test.html" "$d/index.html"
{ printf 'window.TITULO='; cat "$d/titulo.json"; } > "$d/titulo.js"
sh=$(ls -d ~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell | tail -1)
for f in 2 36; do
  "$sh" --no-sandbox --allow-file-access-from-files --virtual-time-budget=3000 --window-size=800,300 \
    --screenshot="$d/lottie-f$f.png" "file://$d/index.html?f=$f" 2>/dev/null
done
"$sh" --no-sandbox --allow-file-access-from-files --virtual-time-budget=3000 --dump-dom "file://$d/index.html?f=36" 2>/dev/null \
  | grep -o '<pre id="s"[^<]*' ; echo
echo "json bytes: $(stat -c %s "$d/titulo.json")  gzip: $(gzip -c "$d/titulo.json" | wc -c)"
