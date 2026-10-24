#!/usr/bin/env bash
# Render every example score and compare the WAVs byte for byte with tools/regress.sha256.
#   tools/regress.sh            # check
#   tools/regress.sh --update   # rewrite tools/regress.sha256 (only for an intended sound change; say why in the commit)
# Sampled examples need the gm + upright banks (node skills/op55/scripts/setup.mjs). Hashes are for Node 22 on macOS arm64.
set -euo pipefail
if [ "$#" -gt 1 ] || { [ "$#" -eq 1 ] && [ "$1" != "--update" ]; }; then echo "usage: tools/regress.sh [--update]" >&2; exit 2; fi
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; S="$ROOT/skills/op55/scripts"; OUT="$ROOT/.regress"; LIST="$ROOT/tools/regress.sha256"
mkdir -p "$OUT"
fail=0; render_fail=0; new=""
shopt -s nullglob
scores=("$S"/examples/*.score.mjs)
if [ "${#scores[@]}" -eq 0 ]; then echo "no example scores found" >&2; exit 1; fi
for score in "${scores[@]}"; do
  name="$(basename "$score" .score.mjs)"
  node "$S/render.mjs" --score "$score" --out "$OUT/$name.wav" --no-analysis > "$OUT/$name.log" 2>&1 || { echo "✗ $name: render failed (see $OUT/$name.log)"; fail=1; render_fail=1; continue; }
  got="$(shasum -a 256 "$OUT/$name.wav" | cut -d' ' -f1)"
  new="$new$got  $name"$'\n'
  want="$(grep "  $name\$" "$LIST" 2>/dev/null | cut -d' ' -f1 || true)"
  if [ -z "$want" ]; then echo "✗ $name $got (no approved hash)"; fail=1; elif [ "$got" = "$want" ]; then echo "✓ $name"; else echo "✗ $name $got (approved $want)"; fail=1; fi
done
if [ "${1:-}" = "--update" ]; then
  if [ "$render_fail" -ne 0 ]; then echo "refusing to replace approved hashes after render failure" >&2; exit 1; fi
  printf '%s' "$new" > "$LIST"; echo "updated $LIST"; exit 0; fi
exit $fail
