"""Root matching and JSON compatibility for order23 binary bundles."""
import copy
import io
import json
import lzma
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from branch_certificate_binary import encode
from branch_certificate_bundle import write_header, write_member
from verify_order23_refutations import read_json, verify_file
from verify_order23_coverage import verify as verify_coverage

CERTIFICATE = {
    'format': '52-edge-branch-refutation-v3',
    'scope': 'minimum-order-counterexample',
    'prefix': [23, 3, 126976, 917516, 1179674, 6, 4, 0, 0, 0, 0, 0, 0, 0,
               1, 1, 1, 1, 1, 6, 2, 2, 4, 0, 0],
    'proof': ['n', 2, ['r', [['delete', 0], ['eliminate', 12], ['eliminate', 1],
                           ['eliminate', 2], ['eliminate', 3], ['eliminate', 13],
                           ['eliminate', 14], ['eliminate', 15], ['eliminate', 16],
                           ['eliminate', 17]]]],
}


def binary_bundle(certificates):
    stream = io.BytesIO()
    write_header(stream, 23, len(certificates))
    for certificate in certificates:
        raw = io.BytesIO()
        encode(certificate, raw)
        write_member(stream, raw.getvalue(), 23)
    return lzma.compress(stream.getvalue())


class Order23BinaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.coverage = read_json(ROOT / 'sources/eleven-order23-coverage.json.xz')
        cls.index = cls.coverage['catalogue'].index(CERTIFICATE['prefix'])
        cls.required = set(verify_coverage(cls.coverage)['referenced_indices'])

    def test_binary_and_json_have_identical_incomplete_result(self):
        legacy = {'format': 'order23-refutations-v1',
                  'cases': [{'catalogue_index': self.index, 'certificate': CERTIFICATE}]}
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / 'proof.bin.xz'
            old = Path(temporary) / 'proof.json.xz'
            binary.write_bytes(binary_bundle([CERTIFICATE]))
            old.write_bytes(lzma.compress(json.dumps(legacy).encode()))
            result = verify_file(binary, self.coverage)
            self.assertEqual(result, verify_file(old, self.coverage))
        missing, statistics, total = result
        self.assertEqual(total, len(self.required))
        self.assertEqual(missing, sorted(self.required - {self.index}))
        self.assertEqual(statistics[0][0], self.index)
        self.assertEqual(statistics[0][1]['neighborhood_projections'], 1)

    def test_duplicate_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'proof.xz'
            path.write_bytes(binary_bundle([CERTIFICATE, CERTIFICATE]))
            with self.assertRaisesRegex(ValueError, 'duplicate catalogue root'):
                verify_file(path, self.coverage)

    def test_unlisted_root_is_rejected(self):
        altered = copy.deepcopy(CERTIFICATE)
        altered['prefix'][1] = 2
        self.assertNotIn(altered['prefix'], self.coverage['catalogue'])
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'proof.xz'
            path.write_bytes(binary_bundle([altered]))
            with self.assertRaisesRegex(ValueError, 'Unknown or duplicate catalogue root'):
                verify_file(path, self.coverage)


if __name__ == '__main__':
    unittest.main()
