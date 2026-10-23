# op55 and showreel: the file contract

[showreel](https://github.com/revfactory/showreel) reads what op55 writes. No showreel code changes are needed. This file is the one home for that contract. Below, `S` is the absolute path of this skill's `scripts/` folder as confirmed by `resolve-op55-tools`, and `SR` is showreel's own scripts folder.

showreel's music step reads the three work skills (`op55-compose`, `op55-render`, `op55-verify`) directly. It does not run `op55-mode` inside its own mode.

## Pass the paths explicitly

- Run showreel's preflight with `OP55_SCRIPTS="$S"`. Its fallback still looks for the old folder name: op55/scripts next to showreel, .claude/skills/op55/scripts or .agents/skills/op55/scripts above the working folder, then .claude/skills/op55/scripts in the home folder. Without the variable it can pick up an old global copy and render with a different engine.
- Give verify the mixer: `--mix-py "$SR/mix.py"`. Without it verify.py tries `$SHOWREEL_SCRIPTS`, then a showreel install in .claude/skills/ above the timeline, then the one in the home folder.

| showreel reads | op55 writes |
| --- | --- |
| `script.json` → `music.file` | `audio/music/music.wav`: 48 kHz, 24-bit, stereo. showreel picks the WAV from `music.file`, never from `analysis.file` |
| `timeline.py --music-analysis <file>` (or `script.json` → `music.analysis`; the CLI wins, a relative path is taken from the folder of script.json) | `audio/music/analysis.json` in the exact `music_tools.py analyze` shape: `file` (string), `duration` (s, 3 decimals), `bpm` (2 decimals), `beats`, `downbeats`, `hits` (s, 3 decimals), `energy` (`[s, dB]` pairs about every 0.5 s) |
| `analysis.file` | Relative to the folder of the nearest `project.json` above the WAV, else to the working directory, else absolute. Render inside the project so it stays relative |
| timeline cues | `bar1…` from `downbeats`, `music.hit1…` from `hits` (section starts and accents in time order), both shifted by `script.json` → `music.start` |
| the music envelope on screen | Not `analysis.energy`. `timeline.py` recomputes an envelope (dt 0.05 s) from the `music.file` WAV and writes it into `reel/timeline.js` |
| `mix.py` | Re-normalises the music to -16 LUFS, then applies gain, duck, start and automation. op55's -13 LUFS master is a separate target |
| credits | `music.meta.json` → `credits[].credit` goes into the video's credits |

`music.meta.json` also holds the exact grid (`beat`, `t0`, `beatsPerBar`, `firstDownbeat`), sections, accents, gaps, onsets and the master report. Use it first when you need the grid back.

Acceptance at this boundary: the files exist, the JSON parses, the required numbers and arrays are present, the length matches the score, and the paths point into the project. showreel's code accepts some defaults, so this is not a full schema gate. Report a missing file, an empty narration table, or the warning "timeline music.file is ..., not the verified WAV" as stopped or unmeasured, not as a pass.

## Order of work in a showreel project

```bash
S=<resolve-op55-tools>/scripts      # confirmed absolute path
SR=<showreel>/scripts
node "$S/render.mjs" --score audio/music/score.mjs --out audio/music/music.wav --analysis audio/music/analysis.json
python3 "$S/verify.py" audio/music/music.wav --analysis audio/music/analysis.json --waveform-png
python3 "$SR/timeline.py" script.json --music-analysis audio/music/analysis.json
# ... narration exists: copy its gaps into the score, re-render, then:
python3 "$S/verify.py" audio/music/music.wav --analysis audio/music/analysis.json --mix timeline.json --mix-py "$SR/mix.py"
```

1. Take sections from `concept.md`'s acts. Plan the grid so act boundaries land on downbeats.
2. Render; `timeline.py --music-analysis` creates cues `bar1…` (downbeats) and `music.hit1…` (section starts and accents in time order). Scenes use these cues. Prefer `barN` for scene boundaries: adding a section or accent renumbers `music.hitN`.
3. When narration is placed, read the narration-free spans from `timeline.json` (`vo` line times; pauses >= 1.2 s), write them to `gaps`, and use them in `compose` (open the pad, +1.6 dB, a bell or piano phrase). Re-render.
4. **The same grid is necessary, not sufficient.** Confirm the new `analysis.json` beats and downbeats match the old cues within 1 ms. Then check what the picture consumes: `music.hitN` numbers, `music.start`, and scenes that react to the music envelope (for example `REEL.level(t, 'music')` or pulses). Re-render only the scenes whose consumed values changed, then run `mix.py` and `finish.py` again. A changed music file always needs a new mix, finish and QA.
5. `verify.py --mix timeline.json` runs showreel's `mix.py` into `verify/mix_test.wav` and summarises voice over bed per line; every line must be ✓ (>= 9 dB).

## Replacing the music of a finished video

Copy the grid the video already uses into `grid`. Take it from the old `music.meta.json` when it exists. Otherwise recover it from the old `analysis.json` (`beat` in seconds from the beat spacing, `t0` = its first beat, `firstDownbeat` from its first downbeat) or from the cue list. `analysis.json` has no meter: confirm `beatsPerBar` from the cue sheet or the source material, ask the user only when neither says, and never assume 4/4. Write the new score on that grid, render, confirm the new beats match the old cues within 1 ms, then check the consumed hits and envelope as in step 4. This is how pstack-harness's ElevenLabs track was replaced by `pstack-harness.score.mjs` without touching a frame.

## Report additions

- Narration lines ✓ count and the minimum voice-over-bed margin from `--mix`.
- The credit line from `music.meta.json` (`credits[].credit`), to add to the video's credits.
- Which scenes were reused and why, and which need a new render.
- "The music was verified by numbers; please listen once" (Claude cannot hear).
