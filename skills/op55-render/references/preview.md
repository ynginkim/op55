# Preview video (only on request)

A preview is an MP4 of the rendered cue for people to listen to while they see its structure. It is **not** part of the normal delivery. Make one only when the user asks for a video, a preview, something to share, or a way to review the track with its sections.

## What it shows

- The cue's spectrogram across the frame, with section lines and names, red accent marks, light bars for narration gaps, and a bar ruler (seconds if there is no `music.meta.json`).
- While the sound plays, a playhead sweeps left to right. What has played is in colour; what is still to come is grey.
- Above it: the title, the facts (key, meter, BPM, length, LUFS), the current section ("NOW 04 HEMIOLA") and a timecode.

## Make it

```bash
python3 $S/preview.py audio/music/music.wav --check [--title "Product launch BGM"] [--out audio/music/music.preview.mp4]
```

- Reads `music.meta.json` next to the WAV (written by `render.mjs`). Without it, there are no sections, accents or bars.
- Default 1920 px wide, 24 fps, AAC 160 kbps. The height follows the content (about 800 px; about 860 px when the sections need three label rows). `--size 1920x1080` fixes the height. A one-minute cue is about 2.5 MB and takes about 20 s.
- `--check` writes stills at 25, 50 and 75 % next to the MP4. Read them. You cannot watch the video, so check these stills:
  - Colour stops exactly at the playhead.
  - The NOW label names the section that contains that moment.
  - The labels do not collide or run off the frame. Where sections are too close for a readable label, only the section line is drawn. The playhead starts below the label rows, so it never covers a label.
  - The title renders. Hangul or other CJK text needs a system font: Pretendard, Apple SD Gothic Neo or Noto Sans CJK are found automatically, or set `OP55_CJK_FONT`.
- Needs Pillow (`python3 -m pip install pillow`) and ffmpeg. The fonts are bundled in `../resolve-op55-tools/assets/fonts` (OFL).

## Sharing

- GitHub plays an MP4 inline only when it is uploaded as an attachment. Dragging the file into an issue, PR or comment box gives a `https://github.com/user-attachments/assets/...` URL. Put that URL on its own line in Markdown and GitHub draws a player. A video file committed to a repo does not play inline.
- The attachment limit is 10 MB on free plans. The script warns when the file is bigger. Long cues fit with `--size 1280 --fps 12 --abr 128k` (300 s comes to 6.6 MB).
- Audio files (MP3/WAV) do not play on GitHub's file page, and raw links download them. To make a plain audio link play in the browser, use a CDN URL: `https://cdn.jsdelivr.net/gh/<owner>/<repo>@<branch>/<path>`.
