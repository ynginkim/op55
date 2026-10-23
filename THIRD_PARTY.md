# Third-party code and sounds

The op55 code is MIT (see `LICENSE`). These parts come from elsewhere. The vendored code and the fonts ship inside the `resolve-op55-tools` skill, so installing the skillset brings their license files along.

## Vendored code

| Component | Version | License | Where |
| --- | --- | --- | --- |
| [spessasynth_core](https://github.com/spessasus/spessasynth_core) by spessasus | 4.3.22 | Apache-2.0 | `skills/resolve-op55-tools/scripts/vendor/spessasynth_core.mjs`, license in `spessasynth_core.LICENSE` |
| [stb-vorbis](https://www.npmjs.com/package/stb-vorbis) (bundled inside the above, decodes SF3) | 0.0.6 | Apache-2.0 | same bundle, license in `stb-vorbis.LICENSE` |

The bundle is an unmodified esbuild bundle of the npm package (see `skills/resolve-op55-tools/scripts/vendor/README.md`).

## Fonts (used by `preview.py`)

| Font | License | Where |
| --- | --- | --- |
| [Instrument Serif](https://github.com/Instrument/instrument-serif) Italic | SIL Open Font License 1.1 | `skills/resolve-op55-tools/assets/fonts/InstrumentSerif-Italic.ttf`, `OFL-InstrumentSerif.txt` |
| [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) (variable weight) | SIL Open Font License 1.1 | `skills/resolve-op55-tools/assets/fonts/JetBrainsMono-wght.ttf`, `OFL-JetBrainsMono.txt` |

## SoundFont banks (downloaded by `setup.mjs`, never committed)

| Bank | Author | License | Use in your videos |
| --- | --- | --- | --- |
| GeneralUser GS 2.0.3 | S. Christian Collins | GeneralUser GS License v2.0 | Free for private and commercial music. The author asks redistributors to serve their own copy, which is why op55's release hosts one (with the CC0 upright) |
| Upright Piano KW (2022-02-21) | FreePats project | CC0 1.0 | Free, no attribution needed |
| Salamander Grand Piano V3 (2020-06-02) | Alexander Holm | CC BY 3.0 | Free, **credit required**: "Salamander Grand Piano by Alexander Holm (CC BY 3.0)". `music.meta.json` lists it when a cue uses it |

Music rendered with op55 belongs to whoever made it; the bank licenses above are the only conditions that travel with it.

## Art

`assets/art/*` were generated with Codex's built-in imagegen from the prompts in `tools/art/prompts/`. Typography and the spectrogram card are composited by `tools/art/compose.mjs`.

## Music

The *Eroica* example quotes the opening idea of Ludwig van Beethoven's Symphony No. 3 in E-flat, Op. 55 (1804), which is in the public domain. The arrangement is new.
