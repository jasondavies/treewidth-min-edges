import io
from itertools import islice
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from marked_residue_common import EXCEPTION_MASKS, decode_graph6
import marked_residue_reconstruction as r
from verify_marked_residue_reconstructions import regenerate


class MarkedResidueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.families = r.catalogue(ROOT)
        cls.first_graph = next(r.reconstructions(cls.families))[1]
        cls.first_order = [2, 3, 19, 0, 1, 20, 5, 4, 6, 7, 10, 8, 12, 9, 11, 13, 14, 15, 16, 17, 18, 21]

    def test_prior_family_scope_and_input_identity(self):
        self.assertEqual([sum(rvalue == value for rvalue, code in self.families)
                          for value in (2, 3, 4)], [457, 9, 1])
        for value, code in self.families:
            graph = decode_graph6(code)
            self.assertEqual(sorted(row.bit_count() for row in graph),
                             [3] * (8 - 2*value) + [4] * (13 + value))
        with patch.object(Path, 'read_bytes', return_value=b'changed classification'):
            with self.assertRaisesRegex(ValueError, 'hash changed'):
                r.catalogue(ROOT)

    def test_independent_order_and_map_checks(self):
        r.verify_order(self.first_graph, self.first_order)
        with self.assertRaises(ValueError):
            r.verify_order(self.first_graph, [0] * 22)
        clique10 = [((1 << 10) - 1) ^ (1 << v) for v in range(10)] + [0] * 12
        with self.assertRaisesRegex(ValueError, 'exceeds width8'):
            r.verify_order(clique10, list(range(22)))
        r.verify_map(EXCEPTION_MASKS, list(range(22)))
        bad = list(range(22))
        cubic = next(v for v, mask in enumerate(EXCEPTION_MASKS) if mask.bit_count() == 3)
        quartic = next(v for v, mask in enumerate(EXCEPTION_MASKS) if mask.bit_count() == 4)
        bad[cubic], bad[quartic] = bad[quartic], bad[cubic]
        with self.assertRaises(ValueError):
            r.verify_map(EXCEPTION_MASKS, bad)

    def test_record_coverage_and_framing_failures(self):
        first = b'\x00' + bytes(self.first_order)
        for raw in (r.MAGIC, r.MAGIC + first, r.MAGIC + first[:-1]):
            with self.assertRaisesRegex(ValueError, 'Missing reconstruction'):
                r.verify_stream(io.BytesIO(raw), self.families[:1])
        for raw in (r.MAGIC + b'\x02' + bytes(self.first_order),
                    r.MAGIC + b'\x00' + bytes([0] * 22),
                    r.MAGIC + b'\x01' + bytes(range(22))):
            with self.assertRaises(ValueError):
                r.verify_stream(io.BytesIO(raw), self.families[:1])
        with self.assertRaisesRegex(ValueError, 'Extra reconstruction'):
            r.verify_stream(io.BytesIO(r.MAGIC + b'\x00'), [])

    def test_invalid_decoder_and_required_marked_pair(self):
        for text in ('', '?', 'U', '~', 'A@'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                decode_graph6(text)
        self.assertFalse(r.target_family(self.first_graph, 0))

    def test_pipe_failure_cleans_owned_child_and_does_not_publish(self):
        class Child:
            def __init__(self):
                self.stdout = io.BytesIO(b'bad stream')
                self.code = None
                self.terminated = self.waited = False
            def poll(self):
                return self.code
            def terminate(self):
                self.terminated = True
                self.code = -15
            def wait(self, timeout=None):
                self.waited = True
                return self.code
            def kill(self):
                self.code = -9
        child = Child()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'must-not-exist.bin'
            with patch('verify_marked_residue_reconstructions.subprocess.run',
                       return_value=SimpleNamespace(returncode=0, stderr='')):
                with patch('verify_marked_residue_reconstructions.subprocess.Popen', return_value=child):
                    with self.assertRaises(ValueError):
                        regenerate(ROOT, output=output)
            self.assertFalse(output.exists())
            self.assertEqual(list(Path(directory).iterdir()), [])
        self.assertTrue(child.terminated and child.waited and child.stdout.closed)
        with self.assertRaisesRegex(ValueError, 'compiler command is empty'):
            regenerate(ROOT, compiler='')


if __name__ == '__main__':
    unittest.main()
