"""Triangle-root coverage must retain every required unresolved family."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_triangle_refutation import load_json, verify_bundle, verify_coverage


class TriangleCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.coverage = load_json(ROOT / 'sources/eleven-quartic-triangle-coverage.json.xz')
        cls.bundle = load_json(ROOT / 'sources/eleven-quartic-triangle-refutations.json.xz')

    def test_complete_coverage_and_all_exclusions(self):
        stats, done, missing = verify_bundle(self.coverage, self.bundle)
        self.assertEqual(stats['branches'], 37)
        self.assertEqual(stats['local'], 118)
        self.assertEqual(stats['traces'], 384)
        self.assertEqual(done, set(range(9)))
        self.assertEqual(missing, [])
        partial = copy.deepcopy(self.bundle)
        partial['cases'] = [case for case in partial['cases'] if case['index'] != 3]
        _, _, missing = verify_bundle(self.coverage, partial)
        self.assertEqual(missing, [3])

    def test_deleted_branch_and_invalid_permutation_rejected(self):
        for mutation in ('missing', 'permutation'):
            coverage = copy.deepcopy(self.coverage)
            if mutation == 'missing':
                coverage['proof'][2].pop()
            else:
                pending = [coverage['proof']]
                while pending:
                    node = pending.pop()
                    if node[0] == 'b':
                        pending.extend(node[2])
                    elif node[0] == 'c':
                        node[2][0] = node[2][1]
                        break
                else:
                    self.fail('A catalogue reference is required in this fixture.')
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                verify_coverage(coverage)

    def test_wrong_root_proof_cannot_fill_a_missing_case(self):
        bundle = copy.deepcopy(self.bundle)
        case = copy.deepcopy(bundle['cases'][0])
        case['index'] = 3
        bundle['cases'] = [c for c in bundle['cases'] if c['index'] != 3]
        bundle['cases'].append(case)
        with self.assertRaisesRegex(ValueError, 'Wrong root'):
            verify_bundle(self.coverage, bundle)


if __name__ == '__main__':
    unittest.main()
