#!/usr/bin/env bash
# The README's inline demo video, made with the skill's own preview.py (the same tool users get on request).
#   tools/art/demo-video.sh [out.mp4]      (default .regress/demo/eroica-55s.mp4; run tools/regress.sh first)
# GitHub plays it inline only as an uploaded attachment: drag the MP4 into a GitHub comment box and put the resulting
# https://github.com/user-attachments/assets/... URL on its own line in README.md and README.ko.md.
set -eu
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$ROOT/.regress/demo/eroica-55s.mp4}"
python3 "$ROOT/skills/op55/scripts/preview.py" "$ROOT/.regress/eroica.wav" --out "$OUT" --check
