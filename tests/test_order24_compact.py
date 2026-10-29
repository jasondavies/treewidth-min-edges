"""The aggregate must establish exact root coverage, including overlap handling."""
from pathlib import Path
import io
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_order24_compact import coverage_summary, verify_binary_bundle, verify_marked_member
from branch_certificate_binary import encode
from branch_certificate_bundle import write_header, write_member


PREFIX = [24, 0] + [0] * 24
OTHER_PREFIX = [24, 0, 2, 1] + [0] * 22


def incomplete_proof(prefix):
    stream = io.BytesIO()
    encode({'format': '52-edge-branch-refutation-v1',
            'scope': 'minimum-order-counterexample', 'prefix': prefix,
            'proof': ['x']}, stream)
    return stream.getvalue()


def bundle(path, members):
    with path.open('wb') as stream:
        write_header(stream, 24, len(members))
        for member in members:
            write_member(stream, member, 24)


class CompactCoverageTests(unittest.TestCase):
    def test_union_is_complete_and_each_component_is_well_formed(self):
        result = coverage_summary(3, [('first', [0, 1]), ('second', [1, 2])])
        self.assertEqual(result['covered_roots'], 3)
        self.assertEqual(result['components'][1]['newly_covered_roots'], 1)
        for components, reason in (
            ([('only', [0, 1])], 'Incomplete'),
            ([('duplicate', [0, 1, 1, 2])], 'Duplicate root'),
            ([('unknown', [0, 1, 2, 3])], 'Unknown'),
            ([('repeated', [0, 1]), ('repeated', [2])], 'Duplicate component'),
        ):
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                coverage_summary(3, components)

    def test_only_previously_proved_roots_can_skip_an_invalid_old_body(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'proofs.bin'
            bundle(path, [incomplete_proof(PREFIX)])
            result = verify_binary_bundle(path, [PREFIX], {0})
            self.assertEqual(result['replayed_indices'], [])
            self.assertEqual(result['skipped_indices'], [0])
            with self.assertRaises(ValueError):
                verify_binary_bundle(path, [PREFIX], set())
            with self.assertRaises(ValueError):
                verify_binary_bundle(path, [PREFIX], {0}, replay_redundant=True)

    def test_redundancy_cannot_hide_duplicate_or_mismatched_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'proofs.bin'
            data = incomplete_proof(PREFIX)
            bundle(path, [data, data])
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                verify_binary_bundle(path, [PREFIX], {0})
            bundle(path, [incomplete_proof(OTHER_PREFIX)])
            with self.assertRaisesRegex(ValueError, 'Unknown'):
                verify_binary_bundle(path, [PREFIX], {0})
            path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, 'Wrong marked-residue root'):
                verify_marked_member(path, OTHER_PREFIX, already_proved=True)


if __name__ == '__main__':
    unittest.main()
