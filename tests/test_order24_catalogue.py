"""Check catalogue coverage and rejection of malformed mapping evidence."""
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_order24_catalogue import profile_encoding, profile_prefix, read_certificate, verify


class Order24CatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = read_certificate(ROOT / 'sources/eleven-order24-catalogue.bin.xz')

    def test_complete_extension_and_attachment_coverage(self):
        result = verify(self.raw)
        self.assertEqual(result['high_graph_counts'], [1, 2, 4, 11, 34, 156, 888, 7459])
        self.assertEqual(result['extension_maps'], 89107)
        self.assertEqual(result['feasible_attachments'], 120192)
        self.assertEqual(result['profile_maps'], 1026)
        self.assertEqual(len(result['profiles']), 364)
        self.assertTrue(all(row[:2] == [24, 8] and len(row) == 26 for row in result['profiles']))
        self.assertTrue(all(profile_prefix(*profile_encoding(row)) == row for row in result['profiles']))

    def test_bad_header_target_permutation_and_count_rejected(self):
        # First level: magic, two counts, one graph, one target+permutation.
        for offset, value in [(6, 0), (10, 0), (18, 1), (22, 1)]:
            raw = bytearray(self.raw)
            struct.pack_into('<I', raw, offset, value)
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                verify(bytes(raw))
        for raw in (b'', b'WRONG!' + self.raw[6:], self.raw[:17]):
            with self.subTest(length=len(raw)), self.assertRaises(ValueError):
                verify(raw)

    def test_missing_final_mapping_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Truncated'):
            verify(self.raw[:-8])


if __name__ == '__main__':
    unittest.main()
