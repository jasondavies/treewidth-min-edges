"""Coverage refinements, original-anchor fingerprints, and proof-gated finishing."""
import copy
import io
import json
import lzma
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from branch_certificate_binary import decode, encode
from branch_certificate_bundle import iter_members, member_prefix, write_header, write_member
from verify_order23_coverage import verify as verify_coverage
from verify_order23_anchor_finish import verify, verify_anchor_finish


def first_inclusion(node):
    if node[0] == 'i':
        return node
    if node[0] == 'b':
        for child in node[2]:
            found = first_inclusion(child)
            if found is not None:
                return found
    return None


class AnchorFinishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(lzma.decompress(
            (ROOT / 'sources/eleven-order23-coverage.json.xz').read_bytes()))
        indices = {tuple(p): i for i, p in enumerate(cls.data['catalogue'])}
        with lzma.open(ROOT / 'sources/eleven-order23-refutations.bin.xz', 'rb') as stream:
            cls.proved = {indices[tuple(member_prefix(data, 23))]
                          for data in iter_members(stream, 23)}
        cls.covered = verify_coverage(cls.data)

    def test_global_finish_and_partial_verifier_are_distinct(self):
        result = verify_anchor_finish(self.data, self.proved)
        self.assertEqual((result['high_vertices'], result['low_vertices']), (12, 11))
        expected = (set(self.covered['initial_referenced_indices']) - self.proved
                    - set(self.covered['refined_indices']))
        self.assertEqual(result['pigeonhole_original_indices'], sorted(expected))
        self.assertTrue(set(self.covered['referenced_indices']) - self.proved)

    def test_missing_dependency_and_nonharmless_proof(self):
        dependency = self.covered['refinement_dependencies']['18'][0]
        with self.assertRaisesRegex(ValueError, 'unproved terminal dependency'):
            verify_anchor_finish(self.data, self.proved - {dependency})
        self.assertIn(0, self.proved)
        with self.assertRaisesRegex(ValueError, 'low neighbor'):
            verify_anchor_finish(self.data, self.proved - {0})

    def test_missing_branch_wrong_map_and_unknown_refinement(self):
        changed = copy.deepcopy(self.data)
        changed['refinements'][0]['proof'][2].pop()
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            verify_coverage(changed)
        changed = copy.deepcopy(self.data)
        leaf = first_inclusion(changed['refinements'][0]['proof'])
        leaf[2][0] = leaf[2][1]
        with self.assertRaisesRegex(ValueError, 'permutation'):
            verify_coverage(changed)
        changed = copy.deepcopy(self.data)
        changed['refinements'][0]['index'] = len(changed['catalogue'])
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            verify_coverage(changed)
        changed['refinements'][0]['index'] = True
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            verify_coverage(changed)

    def test_duplicate_self_cycle_and_unused_two_index_cycle(self):
        changed = copy.deepcopy(self.data)
        changed['refinements'].append(copy.deepcopy(changed['refinements'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            verify_coverage(changed)
        changed = copy.deepcopy(self.data)
        index = changed['refinements'][0]['index']
        changed['refinements'][0]['proof'] = ['i', index, list(range(23))]
        with self.assertRaisesRegex(ValueError, 'Cyclic'):
            verify_coverage(changed)
        changed = copy.deepcopy(self.data)
        index = len(changed['catalogue'])
        changed['catalogue'].extend([copy.deepcopy(changed['catalogue'][1]) for _ in range(2)])
        changed['refinements'].extend([
            {'index': index, 'proof': ['i', index + 1, list(range(23))]},
            {'index': index + 1, 'proof': ['i', index, list(range(23))]}])
        with self.assertRaisesRegex(ValueError, 'Cyclic'):
            verify_coverage(changed)

    def test_forward_dependency_and_unresolved_inclusion_dependency(self):
        changed = copy.deepcopy(self.data)
        leaf = first_inclusion(changed['refinements'][0]['proof'])
        target = leaf[1]
        alias = len(changed['catalogue'])
        changed['catalogue'].append(copy.deepcopy(changed['catalogue'][target]))
        leaf[1] = alias
        changed['refinements'].append({'index': alias, 'proof': ['i', target, list(range(23))]})
        self.assertEqual(verify_coverage(changed)['referenced_indices'],
                         self.covered['referenced_indices'])
        verify_anchor_finish(changed, self.proved)
        with self.assertRaisesRegex(ValueError, 'unproved terminal dependency'):
            verify_anchor_finish(changed, self.proved - {target})

    def test_v1_does_not_allow_inclusion_or_silently_apply_finish(self):
        legacy = json.loads(lzma.decompress(
            (ROOT / 'tests/fixtures/source-order23-coverage-v1.json.xz').read_bytes()))
        self.assertEqual(len(verify_coverage(legacy)['referenced_indices']), 268)
        with self.assertRaisesRegex(ValueError, 'v2'):
            verify_anchor_finish(legacy, self.proved)
        legacy['proof'] = ['i', 18, list(range(23))]
        with self.assertRaisesRegex(ValueError, 'Inclusion'):
            verify_coverage(legacy)

    def test_master_rejects_an_actual_false_certificate_before_finishing(self):
        certificate = decode(io.BytesIO(lzma.decompress(
            (ROOT / 'tests/fixtures/source-order23-tiny.bin.xz').read_bytes())))
        certificate['proof'] = ['x']
        raw = io.BytesIO()
        encode(certificate, raw)
        bundle = io.BytesIO()
        write_header(bundle, 23, 1)
        write_member(bundle, raw.getvalue(), 23)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.bin.xz'
            path.write_bytes(lzma.compress(bundle.getvalue()))
            with self.assertRaises(ValueError):
                verify(path, self.data)

    @unittest.skipIf(sys.version_info < (3, 11), 'Parallel mode requires Python 3.11+')
    def test_parallel_master_requires_fresh_successful_verification(self):
        failed = {'order': 23, 'all_supplied_verified': False,
                  'supplied_members': 1, 'members': [{'code': '0', 'verified': False}]}
        with patch('verify_branch_bundle_parallel.verify_parallel', return_value=failed) as checked:
            with self.assertRaisesRegex(ValueError, 'Not all supplied'):
                verify(Path('unused.bin.xz'), self.data, workers=2)
            checked.assert_called_once()
        with self.assertRaisesRegex(ValueError, 'Worker count'):
            verify(Path('unused.bin.xz'), self.data, workers=True)


if __name__ == '__main__':
    unittest.main()
