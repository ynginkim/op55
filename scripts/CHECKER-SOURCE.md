# Checker source

These files are unmodified copies of the meta-harness checker kit. They check this repository's skillset structure; no runtime skill reads them.

| File here | Source | SHA-256 |
| --- | --- | --- |
| `check.py` | meta-harness `skills/check-skillset/scripts/check.py` | `24cb1401310b10f29612f55c2cf5d3286e5e708bed7f6cb8659291b7125be280` |
| `selftest.py` | meta-harness `skills/check-skillset/scripts/selftest.py` | `d8a9af469ae173ffaa0cac91e55b51562e8a421b92b19dbc64474538a50b7c0f` |
| `install_smoke.py` | meta-harness `skills/check-skillset/scripts/install_smoke.py` | `2c91646abd23bd881cebf5d1c0d90ffae7527b5fcf10411a6b54baaf68c9ea0b` |
| `../.github/workflows/check.yml` | meta-harness `skills/scaffold-skillset/assets/check.yml` | `e9a9279aa1ee08c24d9f1a414d59400ee9aa88aa4aeb56435dcd20e63df8d7e9` |

Copied on 2026-10-23 from meta-harness commit `1aef56e1061ee8727a1b62039d9f6df4a7eaf84a` (the last commit touching these paths; the local checkout was at `dab5f3f`). The installed project copy under `.agents/skills/` had the same bytes.

To update: diff the new meta-harness files against these, copy them unchanged, update the hashes above, then run `python3 scripts/check.py .` and `python3 scripts/selftest.py`. No local edits have been made. If one is ever needed, record the reason here and the condition for merging it back upstream.
