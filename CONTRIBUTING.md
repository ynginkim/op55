# Contributing to op55

Before a change, read the README, relevant local guidance, and the current issue. Keep changes focused and preserve the user's files and explicit scope. For a skillset, distinguish mode (routing), playbook (end-to-end flow), skill (reusable work), and principle (decision criteria). Do not turn a suggestion or plan into a claim of completed execution.

## Development and checks

Use Python 3.12 for standard-library checks. The pinned `skills@1.7.4` installer requires Node.js >= 22.20.0; use that version or newer, plus Git, for installation smoke tests. The op55 renderer itself requires Node.js >= 18. op55 rendering also needs its documented banks; audio analysis needs Python packages and ffmpeg described in its README. Do not install dependencies or download banks just to edit prose.

From the repository root:

```sh
find skills/resolve-op55-tools/scripts -name '*.mjs' -print0 | xargs -0 -n1 node --check
bash -n tools/regress.sh
bash -n tools/release-banks.sh
python3 tools/test_regress.py
node --test tools/test_engine.mjs tools/test_version.mjs
python3 scripts/check.py .
python3 scripts/selftest.py
```

Read the workflows in `.github/workflows/` for CI-specific checks. Installation smoke tests use a new temporary destination outside the source tree and can require network access. Run only tests relevant to the change and report commands, runtime, results, and anything not run. Structural checks do not prove model behavior, audio quality, visual quality, or license clearance.

## Pull requests

1. Use a separate branch; keep existing user changes intact.
2. Explain the problem, scope, and evidence. Avoid unrelated rewrites.
3. Test the affected contracts, examples, links, and installation resources. Update [CHANGELOG.md](CHANGELOG.md) for user-visible changes.
4. Preserve upstream copyright and license notices. List sources for added code, fonts, samples, and images; do not apply MIT to third-party assets automatically.
5. Check for secrets, local paths, generated output, large binary files, and accidental dependency changes.
6. Submit a draft PR with test evidence and remaining limits. Use a short imperative commit subject, such as `docs: clarify local installation`.

Publishing a tag, release, package, or changing repository visibility and permissions is a separate maintainer operation. See [RELEASING.md](RELEASING.md).

## Community

Follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). For vulnerabilities use [SECURITY.md](SECURITY.md), not a public bug report. For ordinary questions see [SUPPORT.md](SUPPORT.md).
