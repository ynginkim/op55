#!/usr/bin/env bash
# Publish gzip copies of the SoundFont banks as release assets (tag banks-v1), the primary source setup.mjs downloads from.
# Run once from the repo root after the GitHub repo exists. Needs gh and the banks installed locally (setup.mjs --all).
set -eu
TAG=banks-v1; DIR="${OP55_BANKS:-$HOME/.cache/op55/banks}"; OUT=.regress/release; mkdir -p "$OUT"
for f in GeneralUser-GS-2.0.3.sf2 UprightPianoKW-20220221.sf2; do   # the 1.2 GB grand stays on FreePats (tar.xz is 4x smaller than gzip)
  [ -s "$OUT/$f.gz" ] || gzip -9 -c "$DIR/$f" > "$OUT/$f.gz"
  ls -la "$OUT/$f.gz"
done
gh release view "$TAG" >/dev/null 2>&1 || gh release create "$TAG" --title "SoundFont banks v1" --notes "Mirrors of the banks op55's setup.mjs installs, gzip-compressed. Licenses: GeneralUser GS License v2.0 (free for private and commercial music), Upright Piano KW CC0 1.0. setup.mjs checks each file's SHA-256 after unpacking. The Salamander grand is fetched from FreePats directly."
gh release upload "$TAG" "$OUT"/*.gz --clobber
