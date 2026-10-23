# score.mjs: the score module

A score is one ES module. It imports nothing; `render.mjs` imports it, builds the grid, and calls `compose(bgm)` with the helpers. Keep it anywhere (usually `<project>/audio/music/score.mjs`).

## Contents

- Exports
- The grid
- The `bgm` toolkit passed to `compose`
- Synth voices
- Sampled parts (`ensemble`)
- Loudness shape, automation, master, space
- CLI

## Exports

| Export | Required | Meaning |
| --- | --- | --- |
| `grid` | yes | `{ bpm \| beat, t0, beatsPerBar = 4, firstDownbeat = 0 }` |
| `duration` | yes | File length in seconds: last bar + tail of 0.1-2 s |
| `compose(bgm)` | yes | Returns `{ events, padCut?, automation?, levels? }` |
| `seed` | | Namespace for every random stream. Change it for another take with the same notes |
| `title`, `key` | | Shown in `--describe` and the meta file |
| `sections` | | `[{ bar, name, energy }]`. Section starts become `analysis.json` hits; verify compares loudness against `energy` |
| `accents` | | `[{ bar, beat?, name, strength }]`. Big hits. Also hits; verify measures each onset; the strongest gets a per-bar table |
| `gaps` | | `[[start_s, end_s]]` narration-free spans (shown as `G` by verify; use them in `compose`) |
| `levels` | | `{ points: [[bar, LU]], end: bar }`. Relative loudness per bar span. The renderer trims each span to this shape before normalising |
| `ensemble` | | Sampled parts, see below |
| `mix` | | Linear gain per instrument or part name. Synth defaults: `pad .55 bass .42 kick .5 tick .11 pluck .15 arp .075 glass .045 bell .075 piano .17 fx 1`; parts default 1 |
| `master` | | `{ lufs: -13, ceiling: -1.35, fadeIn: 0.06, fadeOut: [start, end], eq, glue }` |
| `space` | | Reverb/delay rooms: `{ plate: {...}, hall: { len, rtLow, rtMid, rtHigh, pre }, delay: { sixteenths: 3, fb: .36, lp: 3600 } }` |

## The grid

```js
export const grid = { bpm: 120, t0: 0.5, beatsPerBar: 4, firstDownbeat: 0 };
// beat n = t0 + n * 60/bpm; bar k starts on beat firstDownbeat + beatsPerBar * k
```

- Put the first beat 0.3-0.5 s in (`t0`): a downbeat at 0 s drowns in the 60 ms fade-in.
- Pickups: `firstDownbeat > 0` makes beats 0..firstDownbeat-1 a pickup (negative bars).
- Odd meters work: `beatsPerBar: 3` (see `eroica.score.mjs`, 180 BPM in 3/4 = one bar per second), 6/8 as `beatsPerBar: 6` at the eighth-note rate.
- **Matching existing picture:** copy the grid the video already uses (a previous `analysis.json`, or the cue list). Give `beat` in seconds instead of `bpm` to avoid rounding. If the new `analysis.json` beats match the old ones within 1 ms, the grid contract held. Scenes that use `music.hitN` or the music envelope still need checking: `../resolve-op55-tools/references/showreel-contract.md`.
- Plan sections in 4- or 8-bar units. At 120 BPM in 4/4 a bar is 2 s.

## The `bgm` toolkit passed to `compose`

| Name | What |
| --- | --- |
| `bar(k, b = 0)` | Seconds of bar `k`, beat `b` (fractional both). `bar(142, 3.5)` = the and of four in bar 142 |
| `beat(n)`, `barOf(t)`, `beatOf(t)`, `nearestDownbeat(t)` | Conversions |
| `BEAT`, `S16`, `S32`, `bpm`, `beatsPerBar` | Durations in seconds and the grid values |
| `table(rows)` | Bar-keyed automation `[[bar, value, glideBars = .25], ...]`, log-glides between values. Use for filter cutoffs |
| `progression(rows, voicings, { end, fromZero })` | `rows = [[bar, 'Dm'], ...]`, `voicings = { Dm: [bassMidi, [padMidi...]] }` → `{ list, at(bar) }` |
| `makeRng(name)` | Seeded stream: `r()`, `r.range(a, b)`, `r.int(a, b)`, `r.pick(arr)`, `r.chance(p)`, `r.gauss()`. One name per musical decision |
| `ccRamp(cc, t0, t1, v0, v1, { step = .02, curve = 'smooth' \| 'linear' \| 'exp' })` | Controller events for a sampled part (swells, fades) |
| `smooth`, `clamp`, `mtof`, `db`, `noise`, `seedOf`, `BASS`, `SR` | Utilities |

`compose` returns `{ events: { <name>: [event, ...] }, padCut?(t), automation?(t, g), levels? }`. Instruments render in the order their keys appear in `events`.

## Synth voices

All times in seconds (use `bar()`), `vel` 0-1, `pan` -1..1, `gain` multiplies the mix gain, `sends` = `{ plate, hall, delay }`.

| Voice | Event | Character |
| --- | --- | --- |
| `pad` | `{ t0, t1, notes, att = .5, rel = 1.2, kind: 'warm' \| 'full' \| 'soft', cut?, cutMul?, hp?, swell? }` | Detuned saws + sine through a 4-pole low-pass that follows `padCut(t)` (or `cut`). `full` = thick, `soft` = mostly sine, `swell` = reverse-like envelope, `hp: 900` = airy top layer |
| `bass` | `{ t, dur, midi, vel, style: 'sub' \| 'pulse' \| 'round' \| 'motor' \| 'drive', duck? }` | `sub` = held sub, `motor` = eighth-note motorik. `duck: .55` dips under a kick on the same beat |
| `kick` | `{ t, vel, kind: 'norm' \| 'soft' }` | Soft sine thump with a little beater click |
| `tick` | `{ t, type, vel, pan, alt?, var?, open? }` | `clock flap pencil hat step feed clunk ratchet`: mechanical clicks, mostly above 4 kHz |
| `pluck` | `{ t, midi, vel, dec = .35, bright = .45, pan }` | Kalimba / felt mallet |
| `arp` | `{ t, midi, vel, cut = 900, envAmt = 2.2, dec = .12, sq = .3, pan }` | Saw/square with a filter envelope |
| `glass` | `{ t, midi, vel, dec = .5, ratio = 2, index = 1.6, pan }` | Glassy 2-op FM; great on a dotted-eighth cross-rhythm |
| `bell` | `{ t, midi, vel, dec = 2.4, pan }` | Inharmonic glass-mallet bell |
| `piano` | `{ t, midi, vel, dur, dec = 2.6, pan }` | Synth felt piano (use a sampled part for a real piano) |
| `fx` | `boom { t, midi, dec, gain }` · `stab { t, notes, cut0, cutEnd, cutDec, dec, gain }` · `riser/air { t, t1, f0, f1, q?, curve?, tail?, hall?, gain }` · `shimmer { t, dec, gain }` | Hits: boom + closing chord stab + shimmer. Riser ends at `t1` (put `t1` on the hit) |

Chord voicings for synth beds: pads around E3-G#4 (MIDI 52-68), bass roots F#1-F2 (30-41).

## Sampled parts (`ensemble`)

```js
export const ensemble = {
  strings: { bank: 'gm', preset: 'Slow Strings', pan: 0.2, sends: { hall: 0.35 } },
  celli:   { bank: 'gm', preset: 42, pan: 0.3 },
  keys:    { bank: 'upright', preset: 0, sends: { hall: 0.24, plate: 0.05 } },
  kit:     { bank: 'gm', drums: true, kit: 40 },          // 40 = brush kit
};
// in compose: events.strings = [{ t, dur, midi, vel }, { t, cc: 'expression', value }, ...]
```

Part fields:

| Field | Meaning |
| --- | --- |
| `bank` | `gm` (default), `upright`, `grand`. Must be installed (`setup.mjs`) |
| `preset` | GM program number, `{ program, bankMSB, bankLSB }` for GS variations, or a name: exact match first, then the first preset containing it. List with `banks.mjs <bank> [query]` |
| `drums`, `kit` | A drum part on channel 10; `kit` = 0 standard, 8 room, 16 power, 24 electronic, 25 808/909, 26 dance, 32 jazz, 40 brush, 48 orchestral |
| `pan`, `gain`, `sends` | As for synth voices. Default sends `{ plate: .04, hall: .22 }` |
| `transpose` | Semitones added to every note |
| `bendRange` | Pitch-bend range in semitones (default 2) |
| `lead` | Seconds to play the whole part early (negative track delay) when its samples swell in slowly |

Part events (any order):

| Event | Fields |
| --- | --- |
| note | `{ t, dur, midi, vel = .8 }`. vel 0-1 maps to MIDI 1-127; sampled banks change timbre with velocity, not only level. Drum notes take GM keys (36 kick, 38 snare, 42 closed hat, 46 open hat, 49 crash, 51 ride) and `dur` defaults to 0.25 |
| cc | `{ t, cc, value }`; `cc` = `'expression'` (11), `'volume'` (7), `'mod'` (1), `'sustain'` (64), `'brightness'` (74), `'pan'` (10) or a number; value 0-1 |
| bend | `{ t, bend }`, -1..1 of `bendRange` |

Rendering: each part gets its own SpessaSynth instance (built-in reverb/chorus off), events are applied on their exact sample, and the dry stereo enters the same mixer as the synth voices (same sends, levels, master, stems, `--mute`). A note is cut where the same pitch is struck again in that part, so overlapping legato lines do not swallow each other. Part names must not reuse a synth voice name.

Level guide: a sampled part at `gain` 1 and vel 0.6 sits close to the synth `piano` at its default mix (about -17 LUFS as a stem); a held `sub` bass at vel 0.8 is about 5 dB louder.

## Loudness shape, automation, master, space

- `levels.points` are relative LU targets per bar span. The renderer measures each span, trims it toward the shape (clamped ±9 dB), applies `automation(t, gDb)`, then normalises the whole file. Leave room: quiet sections -8 to -10, big ones -2 to 0.
- `automation(t, g)` returns the gain (dB) at time `t` given the `levels` trim `g`. Typical: `+1.6` in narration gaps, `-3` for the eighth note before a big arrival.
- `master.lufs` -13 is the default for delivery; a dynamic orchestral cue can sit at -14 to -15 to keep its transients (showreel's mix re-normalises music to -16 anyway).
- `space.hall` sets the shared hall. Orchestral cues like a longer one (`len 4.2, rtMid 2.7`).

## CLI

```bash
node $S/render.mjs --score score.mjs --out music.wav [--analysis analysis.json | --no-analysis]
                   [--stems a,b --stems-dir DIR] [--mute a,b] [--describe]
```

- Writes the WAV, `analysis.json` (default: next to the WAV), and `<wav>.meta.json` (grid, sections, accents, gaps, onsets, master report, credits).
- `--stems` writes each named instrument/part dry with the final gains (before glue and limiter).
- `--describe` prints grid, sections, accents and ensemble as JSON without rendering.
