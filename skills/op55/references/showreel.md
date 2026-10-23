# op55 as showreel's music step

[showreel](https://github.com/revfactory/showreel) already reads everything op55 writes. No showreel code changes are needed.

| showreel reads | op55 writes |
| --- | --- |
| `script.json` → `music.file` | `audio/music/music.wav` |
| `timeline.py --music-analysis <file>` (or `script.json` → `music.analysis`) | `audio/music/analysis.json` in the exact `music_tools.py analyze` shape: `file, duration, bpm, beats, downbeats, hits, energy` |
| `mix.py`: re-normalises music to -16 LUFS, ducks it under narration | a -13 LUFS master with the speech band already cleared |

## Order of work in a showreel project

```bash
S=<op55 skill dir>/scripts
node $S/render.mjs --score audio/music/score.mjs --out audio/music/music.wav --analysis audio/music/analysis.json
python3 $S/verify.py audio/music/music.wav --analysis audio/music/analysis.json --waveform-png
python3 <showreel>/scripts/timeline.py script.json --music-analysis audio/music/analysis.json
# ... narration exists: copy its gaps into the score, re-render, then:
python3 $S/verify.py audio/music/music.wav --analysis audio/music/analysis.json --mix timeline.json
```

1. Take sections from `concept.md`'s acts. Plan the grid so act boundaries land on downbeats.
2. Render; `timeline.py --music-analysis` creates cues `bar1…` (downbeats) and `music.hit1…` (section starts + accents in time order). Scenes use these cues. Prefer `barN` for scene boundaries: adding a section or accent renumbers `music.hitN`.
3. When narration is placed, read the narration-free spans from `timeline.json` (`vo` line times; pauses >= 1.2 s), write them to `gaps`, and use them in `compose` (open the pad, +1.6 dB, a bell or piano phrase). Re-render.
4. **The grid did not change → the picture does not need re-rendering.** Only `mix.py` and `finish.py` run again. If the new `analysis.json` beats match the old cues within 1 ms, you are safe.
5. `verify.py --mix timeline.json` runs showreel's `mix.py` into `verify/mix_test.wav` and summarises voice-over-bed per line; every line must be ✓ (>= 9 dB). `mix.py` is found through `--mix-py`, `$SHOWREEL_SCRIPTS`, or a showreel install in `.claude/skills/` above the project or in `~/.claude/skills/`.

## Replacing the music of a finished video

Copy the grid the video already uses into `grid` (`beat` in seconds from the old `analysis.json`, `t0` = its first beat, `firstDownbeat` from its first downbeat). Write the new score on that grid, render, and confirm the new beats match the old cues within 1 ms. Then only re-mix and re-finish. This is how pstack-harness's ElevenLabs track was replaced by `pstack-harness.score.mjs` without touching a frame.

## Report additions

- Narration lines ✓ count and the minimum voice-over-bed margin from `--mix`.
- The credit line from `music.meta.json` (`credits[].credit`), to add to the video's credits.
- "The music was verified by numbers; please listen once" (Claude cannot hear).
