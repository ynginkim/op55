---
name: op55
description: Compose, render, master and verify original background music (BGM) for a video, end to end, in code. Claude writes the score as a JS module; op55 renders it offline with synth voices plus sampled SoundFont instruments (orchestra, pianos, drum kits), masters it to -13 LUFS / -1 dBTP, and writes a sample-exact beat grid (analysis.json) so picture cuts land on downbeats. Deterministic, no paid music APIs, no audio you cannot license. Use for "make BGM / background music / a score / a cue for this video", "music bed under narration", "track that hits on 0:12", "orchestral / cinematic / lo-fi / piano / electronic background track", "배경음악 만들어줘", "BGM 작곡", "영상 음악", and the music step of showreel or any video pipeline. Not for songs with vocals or lyrics, remixing or editing existing recordings, or calling music-generation services.
---

# op55

You are the composer, the orchestrator and the mastering engineer, and you cannot hear. op55 is how you work anyway: you write the music as code, op55 renders it the same way every time, and you check the result by numbers and pictures (loudness per section, onsets against the grid, spectrograms) before anyone listens.

`S=<this skill's base directory>/scripts` below. Every command runs from the project folder.

## 0. Setup (once per machine)

```bash
node $S/setup.mjs --check     # Node >= 18, ffmpeg and python3 + numpy are also needed (verify.py)
node $S/setup.mjs             # default banks: gm (GeneralUser GS, 32 MB) + upright (CC0 piano, 56 MB)
node $S/setup.mjs grand       # optional concert grand (Salamander, ~300 MB download, 1.2 GB on disk, credit required)
node $S/banks.mjs gm strings  # find presets in a bank (bankMSB:program name); --drums lists kits
```

Banks go to `~/.cache/op55/banks` (override with `OP55_BANKS`). They are never copied into a project.

## 1. The contract

| In (ask only what you cannot decide) | Out (in the project, default `audio/music/`) |
| --- | --- |
| Length or the picture's timeline; where it must hit (cuts, logo, final frame) | `music.wav`: 48 kHz 24-bit stereo, -13 LUFS integrated, <= -1.3 dBTP |
| Narration: yes/no, and its line timings if they exist | `analysis.json`: `bpm, beats, downbeats, hits, energy` on the exact grid |
| Mood or references, if the user has them | `music.meta.json`: grid, sections, accents, gaps, onsets, master report, **credits** |
| | `score.mjs`: the source. Re-rendering it reproduces the WAV byte for byte |

You decide genre, palette, tempo, key, form and length of sections yourself. State the choices in one line each when you report.

## 2. Workflow

1. **Cue sheet.** Write `audio/music/cue.md`: sections with start bar, energy (0-1), what changes in the sound, accents (bar + why), narration gaps. Pick the palette (below). Energy needs contrast: peak (>= 0.85) for at most a quarter of the cue, one breather (0.3-0.45) near the middle, and an audible instrument change at every section boundary.
2. **Grid first.** Choose `bpm`, `beatsPerBar`, `t0` so the picture's anchor points fall on downbeats. If a picture already exists, copy its grid (see `references/score.md` → grid). Everything is placed with `bar(k, beat)`, never with raw seconds.
3. **Write `score.mjs`.** Copy an example to start: `$S/examples/starter.score.mjs` (32 s, synth), `$S/examples/eroica.score.mjs` (55 s, sampled orchestra + synth layers), `$S/examples/pstack-harness.score.mjs` (300 s narrated explainer, synth). API: `references/score.md`. Arranging craft: `references/arranging.md`.
4. **Render.**
   ```bash
   node $S/render.mjs --score audio/music/score.mjs --out audio/music/music.wav --analysis audio/music/analysis.json
   ```
   About 5 s for a minute of orchestra, 35 s for five minutes of dense synth. Add `--stems a,b --stems-dir DIR` to inspect layers, `--mute a,b` to isolate a problem.
5. **Verify, then fix and re-render** until every line passes. Details and fixes: `references/verify.md`.
   ```bash
   python3 $S/verify.py audio/music/music.wav --analysis audio/music/analysis.json --waveform-png --spec 0,30
   ```
   Read the PNGs with the Read tool. Required: loudness ✓, grid ✓, every kick/accent onset ✓, section rank correlation ✓ (>= 0.8), limiter gain reduction < 4 dB, clean spectrogram (no stripes, clicks, holes; speech band 1.3-4 kHz quiet under narration).
6. **Deliver.** Report: the files, the one-line choices (genre, palette, tempo/key, form), the verify numbers, the credit line if `music.meta.json` lists one, and ask the user to listen once on speakers or earphones. You verified it by numbers; a human has not heard it yet. Make a preview video only if the user asks for one (`references/preview.md`).

## 3. Palette: synth, sampled, or both

| The cue is... | Use |
| --- | --- |
| Tech, explainer, motion graphics, minimal, electronic, ticking/mechanical textures | Synth voices (`pad bass kick tick pluck arp glass bell piano fx`). Precise, light, no banks needed |
| Orchestral, cinematic, emotional, piano-led, acoustic, jazz, anything a listener knows the real instrument of | Sampled parts (`ensemble`): strings, brass, winds, timpani, pianos, drum kits |
| Most video work | Both: a sampled lead/bed for warmth and realism, synth sub, kick, ticks, risers and booms for weight and sync |

General MIDI samples are honest but not lush. They sound best in their middle register, at medium velocities, in ensembles rather than exposed solos, with expression swells and some room. `references/arranging.md` has the idioms.

## 4. Rules

- **Never** call music-generation services, download loops or sample packs, or use any audio whose license you have not checked. Only the banks in `lib/banks.mjs` and the synth voices.
- **Determinism:** no `Math.random`, no clocks. Use `makeRng('<name>')` for every random choice. Same score + same seed + same banks = same bytes.
- **Narration owns 300-4000 Hz.** Under a voice: no busy lead in that band; carry the motion with bass, sub, kick and ticks above 4 kHz; pads low-passed (500-1200 Hz). Open up in the gaps and in music-only sections.
- **Big hits arrive on downbeats** with a harmonic resolution, after a short dip (`automation`), with peaky layers kept small so the limiter does not flatten them.
- **Sampled sync points:** sampled attacks reach half level 2-8 ms after note-on. Strike sync notes ~5 ms early or give the part `lead`, then confirm with verify's onset lines.
- **Credits:** if `music.meta.json` has a `credits[].credit`, the video's credits must include it (the Salamander grand needs "Salamander Grand Piano by Alexander Holm (CC BY 3.0)").
- When the same problem bites twice, write it into `references/verify.md` → common problems.

## 5. With showreel

op55 plugs into [showreel](https://github.com/revfactory/showreel) through two files it already reads: `script.json` → `music.file = "audio/music/music.wav"` and `timeline.py --music-analysis audio/music/analysis.json`. Narration gaps, re-render rules and the test mix: `references/showreel.md`.

## References

| File | When |
| --- | --- |
| `references/score.md` | Writing `score.mjs`: exports, grid helpers, every synth voice and sampled-part field, CLI flags |
| `references/arranging.md` | Sections and energy, writing under narration, hits and finales, sampled-instrument idioms, GM preset picks |
| `references/verify.md` | Reading verify.py output, the pass criteria, common problems and fixes, regression test |
| `references/showreel.md` | Using op55 as showreel's music step |
| `references/preview.md` | Only when the user asks for a video or preview of the track: `preview.py`, a spectrogram video that turns from grey to colour as it plays |
