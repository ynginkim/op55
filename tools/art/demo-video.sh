#!/usr/bin/env bash
# The README's inline demo: the Eroica spectrogram card plays with its music. What has played is in colour, what is still
# to come is grey, and a playhead sweeps across in time with the sound.
#   tools/art/demo-video.sh [out.mp4]      (default .regress/demo/eroica-55s.mp4)
# Needs ffmpeg, assets/eroica-spectrogram.jpg (tools/art/compose.mjs) and assets/demo/eroica-55s.mp3.
# The card's time axis is x = PAD + t / DUR * SW (compose.mjs: PAD 56, SW 1488, DUR = the render's 57 s), so the sweep
# is exact. Upload the MP4 by dragging it into a GitHub comment box; README embeds the resulting user-attachments URL.
set -eu
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CARD="$ROOT/assets/eroica-spectrogram.jpg"; AUDIO="$ROOT/assets/demo/eroica-55s.mp3"
OUT="${1:-$ROOT/.regress/demo/eroica-55s.mp4}"; mkdir -p "$(dirname "$OUT")"
PAD=56; SW=1488; DUR=57; BAND_Y=94; BAND_H=380        # the band that changes colour: section labels, spectrogram, accent marks
X="$PAD+t/$DUR*$SW"

ffmpeg -v error -y -loop 1 -framerate 30 -i "$CARD" -i "$AUDIO" -filter_complex "
  [0:v]format=gbrp,split=2[c][g0];
  [g0]hue=s=0,eq=brightness=-0.06:contrast=0.85,format=gbrp[g];
  color=c=black:s=1600x520:r=30,format=gbrp[m0];
  color=c=white:s=1600x${BAND_H}:r=30,format=gbrp[w];
  [m0][w]overlay=x='$X-1600':y=$BAND_Y:eval=frame:format=gbrp,format=gbrp[mask];
  [g][c][mask]maskedmerge,format=yuv420p[mm];
  color=c=white@0.95:s=2x${BAND_H}:r=30,format=rgba[bar];
  [mm][bar]overlay=x='$X':y=$BAND_Y:eval=frame,format=yuv420p[v]" \
  -map "[v]" -map 1:a -t "$DUR" -c:v libx264 -preset slow -crf 24 -tune stillimage -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart "$OUT"
ls -la "$OUT"
