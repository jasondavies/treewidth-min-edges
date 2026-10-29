"""Parallel checking must use the verified order23 cover's required indices."""
import io
import json
import lzma
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pack_branch_bundle import pack_members
from verify_branch_bundle_parallel import verify_parallel


class ParallelOrder23CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = lzma.decompress((Path(__file__).resolve().parent / 'fixtures/source-order23-tiny.bin.xz').read_bytes())
        cls.coverage = ROOT / 'sources/eleven-order23-coverage.json.xz'

    def test_one_checked_family_is_only_one_of_the_required_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            bundle, reports = directory / 'one.bin', directory / 'reports'
            pack_members([self.raw], bundle, 23)
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/verify_branch_bundle_parallel.py'),
                                     str(bundle), '--workers', '1', '--reports', str(reports),
                                     '--coverage', str(self.coverage)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            report = json.loads((reports / 'summary.json').read_text())
            self.assertTrue(report['all_supplied_verified'])
            self.assertEqual(report['supplied_members'], 1)
            self.assertEqual(report['required_roots'], 264)
            self.assertEqual(report['required_roots_supplied'], 1)
            self.assertEqual(len(report['missing_roots']), 263)

    def test_duplicate_or_unrecognized_prefix_cannot_supply_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            unknown = bytearray(self.raw)
            unknown[8] = 4  # The coverage catalogue requires exactly three processed vertices.
            for index, members in enumerate(([self.raw, self.raw], [bytes(unknown)])):
                bundle = directory / f'bad{index}.bin'
                pack_members(members, bundle, 23)
                with self.subTest(index=index), self.assertRaises(ValueError):
                    verify_parallel(bundle, directory / f'reports{index}', 1, coverage=self.coverage)


if __name__ == '__main__':
    unittest.main()
