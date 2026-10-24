// starter.score.mjs: a 32-second all-synth BGM template. Copy it to <project>/audio/music/score.mjs and rewrite it.
//
//   node $S/render.mjs --score audio/music/score.mjs --out audio/music/music.wav --analysis audio/music/analysis.json
//   python3 $S/verify.py audio/music/music.wav --analysis audio/music/analysis.json --waveform-png
//
// Form: Intro (low pad, clock ticks) -> Build (kick, bass, plucks enter) -> Main (hit on bar 8, arpeggio, bells) -> Resolve (last chord + bell)
// The file imports nothing: render.mjs hands compose(bgm) the grid helpers and utilities.
// Same file + same seed = the same samples, every time (all randomness comes from named seed streams).

export const title = 'starter';
export const seed = 'starter-v1';          // change it for another take: only the random choices (humanize, random patterns) differ
export const key = 'D major';

// ---- 1) The grid comes first. The picture's cuts and hits sit on its downbeats ----
// beat n = t0 + n*(60/bpm); bar k starts on beat firstDownbeat + 4k. A first beat at 0.5 s keeps the first downbeat out of the 60 ms fade-in.
export const grid = { bpm: 120, t0: 0.5, beatsPerBar: 4, firstDownbeat: 0 };
export const duration = 33.0;              // file length (s): 16 bars = 32 s + 0.5 s lead-in + tail

// ---- 2) Sections and accents: analysis.json's hits (a video's hit cues) and verify.py's tables come from these ----
export const sections = [
  { bar: 0, name: 'Intro', energy: 0.3 },
  { bar: 4, name: 'Build', energy: 0.55 },
  { bar: 8, name: 'Main', energy: 0.85 },
  { bar: 12, name: 'Resolve', energy: 0.35 },
];
export const accents = [
  { bar: 8, name: 'Main hit', strength: 1 },            // the biggest hit (verify.py prints a per-bar table around it)
  { bar: 13, name: 'Final chord', strength: 0.4 },
];
export const gaps = [];                    // narration-free spans [[start, end], ...] copied from the timeline (marked G in verify's table)

// ---- 3) Section loudness shape (LU, relative): render.mjs trims each bar span to this shape, then normalises to -13 LUFS ----
export const levels = { points: [[0, -7], [4, -4], [8, 0], [12, -5], [13, -6]], end: 14 };
export const master = { fadeOut: [31.2, 32.9] };   // everything else (-13 LUFS, -1.35 dBTP, EQ, glue) stays default
// export const mix = { arp: 0.06 };       // per-instrument balance (linear); defaults in lib/instruments.mjs DEFAULT_MIX

// chords: name -> [bass MIDI, [pad MIDI...]]. Pads around E3-G#4 (52-68) cover less of the speech band
const CH = {
  'D': [38, [54, 57, 62, 66]], 'Bm': [35, [54, 59, 62, 66]], 'G': [31, [55, 59, 62, 67]],
  'A': [33, [52, 57, 61, 64]], 'Asus4': [33, [52, 57, 62, 64]], 'Dadd9': [38, [54, 57, 62, 64, 69]],
};
const PROG = [[0, 'D'], [1, 'Bm'], [2, 'G'], [3, 'Asus4'], [3.5, 'A'],
  [4, 'D'], [5, 'Bm'], [6, 'G'], [7, 'A'], [8, 'D'], [9, 'Bm'], [10, 'G'], [11, 'A'], [12, 'G'], [13, 'Dadd9']];

export function compose(bgm) {
  // bgm: bar(k, b) / beat(n) / barOf(t) / BEAT / S16 / S32 / table(rows) / progression(rows, voicings)
  //      makeRng(name) / smooth / clamp / mtof / db
  const { bar, S16, makeRng, table } = bgm;
  const chords = bgm.progression(PROG, CH, { end: 16 });
  const E = { pad: [], bass: [], kick: [], tick: [], pluck: [], arp: [], glass: [], bell: [], piano: [], fx: [] };
  const sec = k => (k < 4 ? 'intro' : k < 8 ? 'build' : k < 12 ? 'main' : 'resolve');

  // pad: one block per chord; the section sets attack and colour; padCut below moves the filter over time
  for (const c of chords.list) {
    const s = sec(c.k0), last = c.name === 'Dadd9';
    E.pad.push({ t0: c.t0, t1: last ? bar(15) : c.t1, notes: c.pad, att: s === 'main' ? 0.05 : 0.6, rel: last ? 2.4 : 1.2,
      gain: s === 'intro' ? 0.7 : 0.85, kind: s === 'main' ? 'full' : s === 'intro' || s === 'resolve' ? 'soft' : 'warm' });
  }
  const padCut = table([[0, 600], [4, 900], [8, 2200, 0.1], [12, 1000, 1], [13, 800, 2]]);

  const rng = makeRng('starter-pluck');
  for (let k = 0; k < 16; k++) {
    const s = sec(k), c = chords.at(k), root = c.bass;
    // bass: a long sub in the intro, eighth-note motorik in build/main (notes under a kick duck out of its way)
    if (s === 'intro' && k % 2 === 0) E.bass.push({ t: bar(k), dur: bgm.BEAT * 8 - 0.1, midi: root, vel: 0.8, style: 'sub', gain: 0.6 });
    if (s === 'build' || s === 'main') for (let i = 0; i < 8; i++) {
      const cc = chords.at(k + i / 8);
      E.bass.push({ t: bar(k, i / 2), dur: bgm.BEAT / 2 * 0.72, midi: cc.bass + (s === 'main' && i % 4 === 3 ? 12 : 0), vel: i % 2 ? 0.7 : 0.9,
        style: 'motor', duck: i % 2 === 0 ? 0.55 : 0 });
    }
    if (s === 'resolve' && k === 12) E.bass.push({ t: bar(k), dur: bgm.BEAT * 4 - 0.05, midi: root, vel: 0.7, style: 'round' });
    if (k === 13) E.bass.push({ t: bar(13), dur: bgm.BEAT * 6, midi: 38, vel: 0.75, style: 'sub' });

    // kick: four on the floor from the build; the last beat before the hit is left empty so the hit can breathe
    if (s === 'build' || s === 'main') for (let b = 0; b < 4; b++) if (!(k === 7 && b === 3)) E.kick.push({ t: bar(k, b), vel: b ? 0.85 : 1 });

    // ticks: clock on the beat in the intro, offbeat hats in the build, sixteenth hats (offbeat accent) in main
    for (let i = 0; i < 16; i++) {
      const t = bar(k, i / 4);
      if (s === 'intro' && i % 4 === 0) E.tick.push({ t, type: 'clock', vel: i === 0 ? 0.9 : 0.6, pan: 0.15, alt: (i / 4) % 2 });
      if (s === 'build' && i % 4 === 2) E.tick.push({ t, type: 'hat', vel: 0.55, pan: 0.1 });
      if (s === 'main') E.tick.push({ t, type: 'hat', vel: i % 4 === 2 ? 0.6 : 0.3, pan: i % 2 ? 0.25 : -0.15 });
      if (s === 'resolve' && k < 14 && i % 8 === 0) E.tick.push({ t, type: 'clock', vel: 0.5, pan: 0.15 });
    }

    // plucks: eighth-note chord walk in the build (a little human: ±6 ms)
    if (s === 'build') for (let i = 0; i < 8; i++) {
      const tones = chords.at(k + i / 8).pad.map(m => m + 12);
      E.pluck.push({ t: bar(k, i / 2) + rng.range(-0.006, 0.006), midi: tones[[0, 1, 2, 3, 2, 1, 2, 3][i] % tones.length], vel: i % 2 ? 0.5 : 0.65,
        pan: i % 2 ? 0.25 : -0.25 });
    }
    // sixteenth arpeggio and glassy FM on a dotted-eighth cross-rhythm: main only
    if (s === 'main') {
      for (let i = 0; i < 16; i++) {
        const t = bar(k, i / 4), tn = chords.at(k + i / 16).pad;
        E.arp.push({ t, midi: tn[i % tn.length] + 12, vel: i % 4 === 0 ? 0.8 : 0.55, cut: 1400, dec: 0.1, pan: i % 2 ? 0.3 : -0.3 });
      }
      for (const [j, pos] of [0, 3, 6, 9, 12].entries()) {
        const tn = chords.at(k + pos / 16).pad.map(m => m + 24);
        E.glass.push({ t: bar(k, pos / 4), midi: tn[(j + k) % tn.length], vel: 0.6, pan: j % 2 ? 0.5 : -0.5 });
      }
    }
    // piano: felt-piano broken chord in the resolve
    if (s === 'resolve' && k === 12) [0, 1, 2, 3].forEach(b => E.piano.push({ t: bar(k, b), midi: c.pad[b % c.pad.length] + 12, vel: 0.5, dur: bgm.BEAT * 1.6 }));
  }

  // the hit (bar 8, beat 1): low boom + closing chord stab + bells + cymbal-like shimmer; a one-bar riser pulls into it
  E.fx.push({ type: 'riser', t: bar(7), t1: bar(8), f0: 400, f1: 8000, q: 1.4, gain: 0.08 });
  E.fx.push({ type: 'boom', t: bar(8) + 0.004, midi: 38, dec: 1.0, gain: 0.28 });      // keep peaky layers (boom, kick) small so the limiter does not flatten the hit
  E.fx.push({ type: 'stab', t: bar(8), notes: [50, 57, 62, 66, 69, 74], cut0: 6000, cutEnd: 900, cutDec: 0.5, dec: 1.6, gain: 0.3 });
  E.fx.push({ type: 'shimmer', t: bar(8), dec: 1.2, gain: 0.07 });
  E.bell.push({ t: bar(8), midi: 86, vel: 0.9 }, { t: bar(8) + 0.012, midi: 90, vel: 0.6, pan: 0.3 });
  // last chord: soft bell and piano; size the tails so they die away before fadeOut
  E.bell.push({ t: bar(13), midi: 81, vel: 0.4, dec: 2.6 }, { t: bar(13, 0.5), midi: 86, vel: 0.25, dec: 2.2, pan: 0.3 });
  E.piano.push({ t: bar(13), midi: 50, vel: 0.4, dur: bgm.BEAT * 6 }, { t: bar(13, 0.02), midi: 57, vel: 0.3, dur: bgm.BEAT * 6 });

  return {
    events: E, padCut,
    // receives the levels trim g (dB) and adjusts it over time: here, hold 3 dB of breath for the eighth before the hit
    automation: (t, g) => (t >= bar(7, 3.5) && t < bar(8) ? g - 3 : g),
  };
}
