#!/usr/bin/env bash
# Generate the README art with Codex's built-in imagegen skill (no API key needed).
#
#   tools/art/gen.sh               # every prompt in tools/art/prompts/ that has no image yet
#   tools/art/gen.sh hero maelzel  # just these
#
# Each prompts/<name>.txt becomes assets/art/<name>.png (kept out of git) and <name>.jpg (committed). Existing images are
# skipped, so re-run to retry failures.
# Runs up to 3 at a time; each takes about a minute. Logs go to assets/art/.logs/.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PROMPTS="$ROOT/tools/art/prompts"; OUT="$ROOT/assets/art"; LOGS="$OUT/.logs"
mkdir -p "$OUT" "$LOGS"
TAIL="$(cat "$PROMPTS/_style.txt")"
names=("$@"); [ ${#names[@]} -eq 0 ] && names=($(ls "$PROMPTS" | grep -v '^_' | sed 's/\.txt$//'))

one() {
  local name="$1" start=$(date +%s)
  { [ -s "$OUT/$name.png" ] || [ -s "$OUT/$name.jpg" ]; } && { echo "SKIP $name"; return 0; }
  codex exec --sandbox workspace-write --skip-git-repo-check --cd "$OUT" -o "$LOGS/$name.md" \
    "Use your imagegen skill (built-in image_gen tool) to generate exactly one image.

$(cat "$PROMPTS/$name.txt")

$TAIL

Save the final image as ./$name.png (PNG) in the current directory, then reply with the file path only." \
    > "$LOGS/$name.out" 2>&1 < /dev/null
  if [ -s "$OUT/$name.png" ]; then
    sips -s format jpeg -s formatOptions 84 "$OUT/$name.png" --out "$OUT/$name.jpg" >/dev/null   # the README uses the JPG
    echo "OK   $name $(( $(date +%s) - start ))s"
  else echo "FAIL $name (see $LOGS/$name.out)"; fi
}

if [ "${1:-}" = "--one" ]; then one "$2"; exit; fi
printf '%s\n' "${names[@]}" | xargs -P 3 -I{} "$0" --one {}   # macOS bash 3.2 has no `wait -n`
