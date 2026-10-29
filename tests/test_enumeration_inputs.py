"""The selected route must reject missing or changed enumeration inputs."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import reproduce_eleven
import replay_eleven


class EnumerationInputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / 'sources/treewidth-eleven-quartic-complete-checkpoints.tar.gz'
        self.archive.parent.mkdir()
        self.archive.write_bytes(b'original archive')
        self.source = self.root / 'checker.c'
        self.source.write_bytes(b'original source')
        inventory = {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (self.archive, self.source)}
        (self.root / 'SHA256.json').write_text(json.dumps(inventory))

    def check(self):
        with patch.object(reproduce_eleven, 'SNAPSHOT', self.root), contextlib.redirect_stdout(io.StringIO()):
            reproduce_eleven.check_bundle()

    def test_required_inputs_pass(self):
        self.check()
        with patch.object(replay_eleven, 'SNAPSHOT', self.root):
            self.assertEqual(replay_eleven.resolve_checkpoint_archive(), self.archive)

    def test_missing_source_is_rejected(self):
        self.source.unlink()
        with self.assertRaises(FileNotFoundError):
            self.check()

    def test_changed_source_is_rejected(self):
        self.source.write_bytes(b'changed')
        with self.assertRaisesRegex(RuntimeError, 'checksum mismatch'):
            self.check()

    def test_missing_archive_is_rejected(self):
        self.archive.unlink()
        with patch.object(replay_eleven, 'SNAPSHOT', self.root):
            with self.assertRaisesRegex(RuntimeError, 'Missing required checkpoint archive'):
                replay_eleven.resolve_checkpoint_archive()

    def test_changed_archive_is_rejected_before_extraction(self):
        self.archive.write_bytes(b'changed')
        with patch.object(replay_eleven, 'SNAPSHOT', self.root):
            with self.assertRaisesRegex(RuntimeError, 'checksum mismatch'):
                replay_eleven.resolve_checkpoint_archive()


if __name__ == '__main__':
    unittest.main()
