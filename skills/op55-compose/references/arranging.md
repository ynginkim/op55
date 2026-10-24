# Arranging for picture

## Contents

- Sections and energy
- Under narration
- Big hits and finales
- Sampled instruments: idioms
- Preset picks (GeneralUser GS)
- Palettes by brief

## Sections and energy

- Sections follow the picture's acts. When the picture changes material (a paper desk, a subway map, a printer), the sound changes material too. pstack-harness: split-flap board → clock ticks and flap clicks; paper desk → hesitant plucks and pencil taps; thermal printer → 32nd-note stepper chirps.
- Energy (0-1) decides how many layers play and how loud. Plan contrast: peak (>= 0.85) for at most a quarter of the cue, one breather of 0.3-0.45 near the middle (when a hit sits at the middle, put the breather right before it as the dip into the hit), and an instrument change a listener notices at every boundary.
- Section starts sit on downbeats. If a picture cut already sits on a downbeat near the planned start, follow the cut.
- Make each section its own harmonic world: change the progression (I-vi-IV-V families, sus chords, pedal points, deceptive cadences), add or drop layers on section downbeats, and put a fill (tick roll, a dropped kick, a timpani roll) at the end of every 8 bars. Swing and humanize only where the picture hesitates; machine-like scenes stay exactly on the grid.
- Quiet sections: a sub drone at gain 0.5-0.65. At 1.0 the 55 Hz region swallows everything.

pstack-harness (300 s, 120 BPM, A major) as a worked plan:

| Section | Bar (s) | Energy | Arrangement |
| --- | --- | --- | --- |
| Departure Board | pickup (0.1) | 0.30 | Clock tick on every beat, flap clicks, low pad, sub. No drums |
| Title | 7 (15.59) | 0.50 | One warm hit on the downbeat, eighth bass pulse, sixteenth ticks |
| Problem | 14 (29.59) | 0.40 | Swung, humanized syncopated plucks, late bass, unresolved chords |
| Map Builds | 31 (63.57) | 0.60 | Motorik kick and eighth bass, a layer added every 8 bars |
| Routing | 55 (111.54) | 0.72 | Sixteenth arpeggio, dotted-eighth FM glass, high bells |
| Front Door | 71 (143.53) | 0.80 | Thermal-printer stepper, 3-3-2 arpeggio, pedal A |
| Breath | 87 (175.51) | 0.35 | Drums and pulse out, pad and eighth ticks only |
| Finale | 138 (277.46) | 0.75 → 0.85 | One step up per stroke-group downbeat, LOCK on bar 143, end-card resolve |

## Under narration

A video's mix stage may duck the music under speech. Clear the speech band in the score anyway.

- Under a voice: no busy lead between 300 and 4000 Hz. Drive with bass, sub, kick and ticks above 4 kHz. Pads low-passed at 500-1200 Hz; bells and glass rare and quiet. Sampled strings: low register (celli, violas, low violins) at expression 0.3-0.5, `Slow Strings` rather than `Fast Strings`.
- In the gaps (`gaps`, pauses >= 1.2 s): open the pad cutoff 2x, `automation` +1.6 dB, a bell motif or a piano phrase. Even a 1.2 s pause should visibly rise in the numbers.
- Music-only stretches (cold open, finale, end card) are the face of the cue: melody, brightness and layers are free.
- Target: in the video's mix, the voice is at least 9 dB over the bed on every narration line. op55 does not measure this itself. pstack-harness: 41/41 lines, minimum 13.0 dB.

## Big hits and finales

- **Build:** step up one thing per downbeat: the bass climbs (D-E-F#-G#-A), the pad's top note climbs with it, the filter opens, a layer joins, `levels` +1 dB per bar. A riser ends exactly on the hit.
- **Arrival:** the hit comes with a harmonic resolution (V → I). Dip 3-3.5 dB for the eighth note before it (`automation`), come back on the hit. Layers: low boom + bright chord stab (or a sampled tutti) + bell + shimmer.
- **Keep the limiter off the hit:** booms, kicks, timpani, saw stabs and stacked sampled-piano chords are peaky; keep them small (boom gain 0.2-0.4, kick vel 0.35-0.6 under a sampled tutti). If verify reports more than 4 dB of limiting, find the peaky stem (`--stems`) and lower it. Do not lower the loudness target to hide it.
- **Resolve:** in the end card take the pulse out (one last kick), bring back the opening's sound as a bookend, end on IV/I → I (add9) or a plain tonic with a soft bell. Size tails to die before `fadeOut`. The final still frame should be nearly silent.
- **Numbers:** the strongest accent's bar is the loudest bar of the cue and at least 2 dB above the bar before it.

## Sampled instruments: idioms

GM samples are short loops of real players. They sound real when you write the way the players would play.

- **Velocity is timbre.** Banks switch samples by velocity: ff brass blares, p brass is round. Write dynamics with velocity (0.35 soft, 0.6 normal, 0.85+ loud) and shape long notes with `expression`.
- **Swells, not steps.** A held string or horn chord without an expression curve sounds like an organ. Use `ccRamp('expression', t0, t1, from, to)` across a phrase: 0.5 → 1 into a climax, 0.9 → 0.3 on a final chord.
- **Legato:** overlap consecutive notes by 20-50 ms in lines (`dur = beats * BEAT + 0.03`). Same-pitch repeats are cut automatically at the new note.
- **Re-pedal piano each harmony:** `{ cc: 'sustain', value: 0 }` 20 ms before the new chord, `value: 1` 10 ms after its notes. Without re-pedalling, chords smear.
- **Register:** strings and horns are most convincing in their middle register. Avoid exposed solo violin above E6, horns above F5, and anything at velocity 1.0 sustained for bars.
- **Ensembles beat solos:** `Fast Strings` / `Slow Strings` / `Brass Section` hide the sample loop; exposed solo instruments reveal it. Double a solo line with the section an octave apart.
- **Humanize** lines by ±4-8 ms and ±0.04 velocity with a named `makeRng`; keep sync points (hits, stabs, kick) exact.
- **Sync points:** sampled attacks reach half level 2-8 ms after note-on (bowed strings and brass are slowest). Strike sync notes ~5 ms early (eroica's `LEAD`) or set the part's `lead`; confirm on verify's onset lines.
- **Split a part when one line must not touch another:** two parts on the same preset are fine (eroica's `violins` and `violas` are both `Fast Strings`).
- **Timpani rolls:** sixteenths or faster at rising velocity (0.35 → 0.75) for one bar into an arrival; keep the peak below the arrival's velocity.
- **Hybrid weight:** a synth `sub` doubling the sampled basses an octave below, a soft `kick` on the downbeat and a small `boom` under a tutti make an orchestra feel modern without hiding it.

## Preset picks (GeneralUser GS, bank `gm`)

| Role | Preset (program) | Notes |
| --- | --- | --- |
| String bed | `Slow Strings` (49) | Soft attack; under narration |
| String lines, stabs, pulses | `Fast Strings` (48) | Quick attack, works staccato |
| Tremolo | `Tremolo Strings` (44) | Finales, tension |
| Pizzicato | `Pizzicato Strings` (45) | Playful, light pulse |
| Cello / bass lines | `Cello` (42), `Double Bass` (43) | Themes and roots |
| Horns | `French Horns` (60) | Heroic themes, warm pads |
| Brass hits | `Brass Section` (61) | Stabs, tutti |
| Timpani | `Timpani` (47) | Hits, rolls; pitch it to the root (D2-A3) |
| Woodwinds | `Flute` (73), `Oboe` (68), `Clarinet` (71), `Bassoon` (70) | Short solos, countermelodies |
| Harp | `Orchestral Harp` (46) | Arpeggios, glissandi as fast note runs |
| Mallets | `Vibraphone` (11), `Celeste` (8), `Glockenspiel` (9), `Tubular Bells` (14) | Sparkle, end cards |
| Choir | `Concert Choir` (52) | Sparingly, low velocity |
| Pianos | bank `upright` (warm, close), bank `grand` (concert), `gm` `Grand Piano` (0) | Upright suits lo-fi and explainers |
| Drums | `drums: true` with `kit` 0 / 8 / 16 / 24 / 25 / 32 / 40 / 48 | Brush (40) under narration; orchestral (48) for cinematic percussion |

Find more: `node $S/banks.mjs gm <word>` (e.g. `pad`, `guitar`, `bass`, `bell`).

## Palettes by brief

| Brief | Start from |
| --- | --- |
| Tech explainer, product walk-through | Synth: motorik bass, ticks, glass, warm pad. `pstack-harness.score.mjs` |
| Emotional story, people, brand film | Upright or grand piano + `Slow Strings` swells + sub; brush kit if it needs a pulse |
| Trailer, launch, epic reveal | Sampled tutti hits on downbeats + timpani + synth boom/riser; hemiola or ostinato under the build. `eroica.score.mjs` |
| Lo-fi, cozy, study | Upright piano with re-pedalled 7th chords, brush kit, synth sub, light swing (humanize 8-12 ms) |
| Playful, kids, food | Pizzicato + mallets + light kit, major key, 110-130 BPM |
| Corporate minimal | Synth pad + pluck + soft kick, few chord changes, generous gaps |
