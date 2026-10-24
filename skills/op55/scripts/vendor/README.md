# vendor/

`spessasynth_core.mjs` is [spessasynth_core](https://github.com/spessasus/spessasynth_core) 4.3.22 (Apache-2.0) with its one dependency, stb-vorbis 0.0.6 (Apache-2.0), bundled into a single ES module so the skill runs without `npm install` (skills are installed by copying files).

Rebuild:

```bash
mkdir -p /some/scratch && cd /some/scratch && npm init -y && npm install spessasynth_core@4.3.22
npx esbuild@0.25 node_modules/spessasynth_core/dist/index.js --bundle --format=esm --platform=node --minify \
  --legal-comments=inline --outfile=<repo>/skills/op55/scripts/vendor/spessasynth_core.mjs
```

After an upgrade, run `tools/regress.sh`: the sampled example's hash will tell you whether the sound changed.

The published spessasynth_core 4.3.22 also embeds fflate. Preserve fflate.LICENSE (MIT, Arjun Barrett) alongside both Apache-2.0 license files when rebuilding.
