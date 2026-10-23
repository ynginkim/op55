#!/usr/bin/env bash
# Render every example score and compare the WAVs byte for byte with tools/regress.sha256.
#   tools/regress.sh            # check
#   tools/regress.sh --update   # rewrite tools/regress.sha256 (only for an intended sound change; say why in the commit)
# Sampled examples need the gm + upright banks (node skills/resolve-op55-tools/scripts/setup.mjs). Hashes are for Node 22 on macOS arm64.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; S="$ROOT/skills/resolve-op55-tools/scripts"; OUT="$ROOT/.regress"; LIST="$ROOT/tools/regress.sha256"
mkdir -p "$OUT"
fail=0; new=""
for score in "$S"/examples/*.score.mjs; do
  name="$(basename "$score" .score.mjs)"
  node "$S/render.mjs" --score "$score" --out "$OUT/$name.wav" --no-analysis > "$OUT/$name.log" 2>&1 || { echo "✗ $name: render failed (see $OUT/$name.log)"; fail=1; continue; }
  got="$(shasum -a 256 "$OUT/$name.wav" | cut -d' ' -f1)"
  new="$new$got  $name"$'\n'
  want="$(grep "  $name\$" "$LIST" 2>/dev/null | cut -d' ' -f1 || true)"
  if [ -z "$want" ]; then echo "? $name $got (no approved hash)"; elif [ "$got" = "$want" ]; then echo "✓ $name"; else echo "✗ $name $got (approved $want)"; fail=1; fi
done
if [ "${1:-}" = "--update" ]; then printf '%s' "$new" > "$LIST"; echo "updated $LIST"; exit 0; fi
exit $fail
