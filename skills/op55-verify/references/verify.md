# Verifying a render

You cannot hear the music, so you prove it. `verify.py` measures the WAV against its own score (from `<wav>.meta.json`).

```bash
python3 $S/verify.py audio/music/music.wav --analysis audio/music/analysis.json \
  --waveform-png --spec 0,30,60 [--bars 36-44] [--out-dir audio/music/verify]
```

## Pass criteria

| Line | Pass |
| --- | --- |
| `[loudness]` | Integrated = `master.lufs` ± 0.5 ✓, true peak <= -1.0 dBTP ✓ (the master ceiling is -1.35, so renders land at about -1.3), 0 clipped samples, DC < 1e-4, silence after the fade |
| `[loudness] limiter` | ✓ = no second above 4 dB of gain reduction; ✗ (> 4 dB) is a fail. If it is the biggest hit, lower its peaky layers or narrow the `levels` spread, not the target |
| `[grid]` | `analysis.json` beats/downbeats within 0.6 ms of the grid ✓ |
| `[onsets] kick` | Every kick within 5 ms of its grid time ✓ (averaged template + per-hit cross-correlation). Only the synth `kick` and `boom` are measured; sampled drum-kit kicks are not |
| `[onsets] accent` | Each accent's 50% rise within 5 ms ✓. `△ late attack` (5-10 ms) means sampled layers swell in: strike them earlier or set `lead`. `soft` = no sharp attack (a swell), acceptable if intended |
| `[energy]` section table | Rank correlation between declared energy and measured loudness >= 0.8 ✓. The quiet sections must keep their rank order too: an intro and an outro at the same level as the breather drag it down; give the breather the highest `levels` of the three quiet ones |
| `[energy]` bar table | The strongest accent's bar is the loudest and >= 2 dB above the bar before |
| `--waveform-png` | One panel per accent: red = grid time, green = measured attack, blue = downbeats, grey = beats. Red and green coincide. All panels share one vertical scale, so hit sizes compare |
| `--spec` | 20-s spectrograms from each listed second (a start at or past the end of a short cue is skipped with a note; use `--spec 0` for a cue under 30 s) (Read them): no vertical stripes (aliasing), no clicks, no holes; under narration 1.3-4 kHz stays dark |

Example: `eroica.score.mjs` passes with -14.5 LUFS, -1.3 dBTP, LRA 9.2 LU, limiter max 3.7 dB, 52 kicks within 1.2 ms, 6 accents within 3.4 ms, rank correlation +0.96.

## Common problems

| Symptom | Cause and fix |
| --- | --- |
| The biggest hit sounds smaller than expected | The limiter took 5-6 dB off it. Find the peaky stem with `--stems` (kick, boom, timpani roll, ff brass, a stacked sampled-piano chord at velocity ~0.9) and lower it; a wide `levels` spread also raises the trim on the hit's section, so narrow it (hit section about -1.5, the others -3.5 to -8.5); stagger bell hits by 10-25 ms. Lowering the LUFS target only makes everything quieter |
| Sections lose their contrast (LRA 3-4 LU) | Bus glue too strong or `levels` too flat. Default glue is gentle (-15 dB, 1.35:1); widen `levels` (quiet -8 to -10, loud -2 to 0) |
| The whole bed pumps on every tick | Clicks have peaks 40 dB above their RMS. `tick` soft-clips at +9 dB over its 3 ms RMS; give any new click voice the same treatment |
| An accent onset is late (`△ late attack`) | Find the layer: `render.mjs --mute <name> --no-analysis --out dbg/x.wav`, then `verify.py` on each muted WAV. A synth bass note or a sampled chord on the same downbeat is often the cause, not the `fx` boom. Start it 5-10 ms early (no humanise on that chord). Muting shifts the balance, so read the offset only |
| Muddy low end | Sub too loud or kick tails too long. Quiet-section sub gain 0.5-0.65; `duck` bass notes under kicks |
| The start is inaudible | First downbeat near 0 s inside the fade-in. Set `grid.t0` to 0.3-0.5 s |
| Renders differ between runs | `Math.random` or a clock was used. Only `makeRng(name)`. Same Node + same banks = same bytes |
| An accent is `△ late attack` | Sampled ff attack: trigger 5 ms early or `lead: 0.005` on the part |
| A sampled chord loses notes | Two notes of the same pitch overlapped in one part; the later one cuts the earlier (by design). Split the line into another part or shorten the first note |
| A long tail of broadband hiss on the last chord | The `shimmer` fx through a long hall. Lower its gain (0.02-0.03) and `dec` |
| `bank "x" is not installed` | `node $S/setup.mjs x` |
| A narration line is △ or ✗ | Reduce 300-4000 Hz layers under it (plucks, arps, bells, sampled leads) or lower the pad cutoff; then nearby sound effects |
| Beats re-detected from the WAV by another tool drift | Do not re-detect beats on op55 renders. Use the `analysis.json` op55 wrote; it is exact |

## Regression test (when changing `lib/`)

Approved renders must stay identical byte for byte. Changing the order of floating-point operations changes bytes.

```bash
tools/regress.sh        # from the repo root: renders the examples and compares SHA-256 with tools/regress.sha256
```

If a hash changes, decide whether the sound change was intended; if it was, update the hash file in the same commit.
