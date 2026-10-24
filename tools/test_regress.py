#!/usr/bin/env python3
"""Test regression failure semantics with a fake renderer; no banks or audio claimed."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class RegressTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'tools').mkdir()
        (self.root / 'skills/resolve-op55-tools/scripts/examples').mkdir(parents=True)
        shutil.copyfile(Path(__file__).with_name('regress.sh'), self.root / 'tools/regress.sh')
        (self.root / 'skills/resolve-op55-tools/scripts/examples/demo.score.mjs').write_text('// fixture\n')
        self.approved = self.root / 'tools/regress.sha256'
        self.digest = hashlib.sha256(b'fixture audio').hexdigest()
        self.approved.write_text(self.digest + '  demo\n')
        binpath = self.root / 'bin'
        binpath.mkdir()
        node = binpath / 'node'
        node.write_text('#!/usr/bin/env python3\nimport os, sys\nfrom pathlib import Path\nif os.environ.get("FAIL_RENDER"): sys.exit(1)\nPath(sys.argv[sys.argv.index("--out")+1]).write_bytes(b"fixture audio")\n')
        node.chmod(0o755)
        self.env = dict(os.environ, PATH=str(binpath) + os.pathsep + os.environ['PATH'])

    def run_regress(self, *args):
        return subprocess.run(['bash', 'tools/regress.sh', *args], cwd=self.root,
                              env=self.env, text=True, capture_output=True)

    def test_matching_hash_passes(self):
        self.assertEqual(self.run_regress().returncode, 0)

    def test_missing_hash_fails(self):
        self.approved.write_text('')
        self.assertNotEqual(self.run_regress().returncode, 0)

    def test_changed_hash_fails(self):
        self.approved.write_text('0' * 64 + '  demo\n')
        self.assertNotEqual(self.run_regress().returncode, 0)

    def test_update_can_accept_new_hash(self):
        self.approved.write_text('')
        self.assertEqual(self.run_regress('--update').returncode, 0)
        self.assertEqual(self.approved.read_text(), self.digest + '  demo\n')

    def test_failed_update_preserves_approved_hashes(self):
        previous = self.approved.read_bytes()
        self.env['FAIL_RENDER'] = '1'
        self.assertNotEqual(self.run_regress('--update').returncode, 0)
        self.assertEqual(self.approved.read_bytes(), previous)

    def test_no_examples_fails(self):
        (self.root / 'skills/resolve-op55-tools/scripts/examples/demo.score.mjs').unlink()
        self.assertNotEqual(self.run_regress().returncode, 0)

    def test_unrecognized_argument_fails(self):
        self.assertEqual(self.run_regress('--typo').returncode, 2)


if __name__ == '__main__':
    unittest.main()
