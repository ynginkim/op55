# op55 output contract

This file covers what op55 promises, what it writes, in what shape, and what a caller can rely on. It is the one home for that contract. Below, `S` is the absolute path of this skill's `scripts/` folder as confirmed by `resolve-op55-tools`.

op55 does not describe how other skillsets use these files. A video skillset that uses op55 keeps that in its own docs.

## Public interface

op55 promises the items below. Anything else can change in any release: the folder layout inside the skills, the examples, the compose procedure, the wording.

| Item | What is promised |
| --- | --- |
| Skill names | `op55-mode` for direct use. `op55-compose`, `op55-render`, `op55-verify` and `resolve-op55-tools`, which another skillset reads directly |
| Tools | `resolve-op55-tools/scripts/` holds `render.mjs`, `verify.py`, `setup.mjs` and `preview.py`. When the folder is passed as an environment variable, the name is `OP55_SCRIPTS` |
| Command-line flags | The flags shown by `render.mjs --help` and `verify.py --help` |
| Output files | The table under "Files" below |
| Version | `metadata.version` in `resolve-op55-tools/SKILL.md`. `node "$S/render.mjs" --version` prints it as `op55 <version>` |

A change to any of these is a breaking change. Before 1.0 it raises the minor version (0.2 to 0.3), and CHANGELOG describes the migration. A caller records the version it used. Whether a newer op55 still works is decided by the acceptance check at the end of this file, not by the number alone.

## Calling op55 from another skillset

- Read `op55-compose`, `op55-render` and `op55-verify` directly. Do not run `op55-mode` inside another mode.
- Pass the confirmed absolute `S`, and do not search for the scripts on your own: an old copy elsewhere renders with a different engine.
- Render inside the project, so the paths written into `analysis.json` stay relative.
- op55 does not measure voice over music. The video's mix stage measures it on every narration line.

## Files

| File | Contents |
| --- | --- |
| the WAV (`--out`, usually `audio/music/music.wav`) | 48 kHz, 24-bit, stereo. By default about -13 LUFS integrated and <= -1.3 dBTP (`master` in the score) |
| `analysis.json` (`--analysis`, default next to the WAV) | `file` (string), `duration` (s, 3 decimals), `bpm` (2 decimals), `beats`, `downbeats`, `hits` (s, 3 decimals), `energy` (`[s, dB]` pairs about every 0.5 s). `beats` and `downbeats` come from the score's grid, not from detection. `hits` are the score's section starts and accents, merged in time order |
| `<wav stem>.meta.json` (for `music.wav`, `music.meta.json`) | `grid` (`bpm`, `beat`, `t0`, `beatsPerBar`, `firstDownbeat`), sections, accents, `gaps`, onsets, the master report, `credits` |

- `analysis.file` is relative to the folder of the nearest `project.json` above the WAV. Without one it is relative to the working directory when the WAV is inside it, and absolute otherwise.
- `credits[].credit` is the line to put in the video's credits when a sampled bank requires attribution. render.mjs also prints it as `credit required: ...`.
- Use `music.meta.json` first when you need the grid back. `analysis.json` has no meter.

## What a video gives back

- Narration-free spans go into the score's `gaps` as `[[start_s, end_s]]` (`../op55-compose/references/score.md`). `compose` uses them.
- An existing grid, when the picture is already cut: see the next section.

## Matching an existing grid

Copy the grid the video already uses into `grid`. Take it from the old `music.meta.json` when it exists. Otherwise recover it from the old `analysis.json`:

- `beat`: in seconds, from the beat spacing.
- `t0`: its first beat.
- `firstDownbeat`: from its first downbeat.
- `beatsPerBar`: `analysis.json` has no meter. Confirm it from the cue sheet or the source material. Ask the user only when neither says, and never assume 4/4.

After rendering, confirm that the new beats and downbeats match the old ones within 1 ms.

The same grid is necessary, not sufficient:

- Adding a section or accent changes `hits`, so anything indexed by hit number is renumbered.
- A new WAV has a new energy curve.

Which of these the picture consumes is the video skillset's knowledge. Check it there before reusing scenes.

## Acceptance at this boundary

The files exist, the JSON parses, the required numbers and arrays are present, the length matches the score, and the paths point into the project. This is not a full schema gate. A consumer may silently accept defaults, so report a missing file as stopped or unmeasured, not as a pass.
