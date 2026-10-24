#!/usr/bin/env python3
"""`levels.end` past the file's length must not poison the render with NaN (#8).

Renders an all-synth variant of the starter score whose `levels.end` bar lands
after `duration`, and asserts the render stays finite. Needs Node 22; no banks
(the starter score is all-synth).
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / 'skills/op55/scripts/render.mjs'
SCORE = ROOT / 'skills/op55/scripts/examples/starter.score.mjs'


class LevelsEndTests(unittest.TestCase):
    def render(self, score_text):
        """Render in a throwaway directory; everything is asserted inside, before the cleanup."""
        with tempfile.TemporaryDirectory() as temp:
            score = Path(temp) / 'score.mjs'
            score.write_text(score_text, encoding='utf-8')
            wav = Path(temp) / 'out.wav'
            run = subprocess.run(['node', str(RENDER), '--score', str(score), '--out', str(wav)],
                                 text=True, capture_output=True, timeout=300)
            size = wav.stat().st_size if wav.exists() else 0
            return run.returncode, run.stdout + run.stderr, size

    def assert_finite_render(self, score_text):
        code, output, size = self.render(score_text)
        self.assertEqual(code, 0, output)
        self.assertNotIn('NaN', output)
        self.assertGreater(size, 0)

    def test_an_end_past_the_duration_does_not_poison_the_render(self):
        late = SCORE.read_text(encoding='utf-8').replace('export const duration = 33.0;', 'export const duration = 30.4;')
        late = late.replace('end: 14 }', 'end: 15 }')  # grid.bar(15) = 30.5 s > 30.4 s
        self.assert_finite_render(late)

    def test_the_unmodified_starter_still_renders_finite(self):
        self.assert_finite_render(SCORE.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
