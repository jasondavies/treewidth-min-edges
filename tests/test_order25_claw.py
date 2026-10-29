import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from order25_profiles import enumerate_profiles
from verify_order25_claw import (verify, verify_claw_prefix, verify_prior_inverses,
                                 verify_weighted_packing)
from verify_order25_complete import (canonical_mapping, finish_coverage, verify_private_cycle,
                                    verify as verify_complete)


class Order25ClawTests(unittest.TestCase):
    def test_full_finite_checks(self):
        profiles = enumerate_profiles()
        result = verify(profiles[tuple(map(int, '001011'))], ROOT)
        self.assertEqual(result['packing'], {'cubic_types': 34, 'cover_nodes': 342,
                                            'saturated_exceptions': 1})
        self.assertEqual(result['inverses']['inverse_choices'], 8)
        self.assertEqual(result['inverses']['cubic_degree_contradictions'], 8)
        self.assertEqual(result['inverses']['bases_c3'], 2815)

    def test_partial_conflict_cover_is_not_silently_accepted(self):
        with patch('verify_order25_claw.conflict_covers', return_value=([[]], 1)):
            with self.assertRaisesRegex(ValueError, 'unexamined supersets'):
                verify_weighted_packing()

    def test_noncanonical_root_mapping_is_checked_explicitly(self):
        target = enumerate_profiles()[tuple(map(int, '000001'))]
        relabel = list(range(4)) + list(reversed(range(4, 25)))
        rows = [0]*25
        for v in range(25):
            rows[relabel[v]] = sum(1 << relabel[u] for u in range(25)
                                   if target[2+v] >> u & 1)
        source = [25, 4] + rows
        mapping = canonical_mapping(source, target)
        self.assertEqual(sorted(mapping), list(range(25)))
        self.assertEqual(set(mapping[:4]), set(range(4)))
        for v in range(25):
            mapped = sum(1 << mapping[u] for u in range(25) if rows[v] >> u & 1)
            self.assertEqual(mapped, target[2+mapping[v]])
        with self.assertRaises(ValueError):
            canonical_mapping(source, enumerate_profiles()[tuple(map(int, '001011'))])

    def test_source_identity_and_root_scope(self):
        profiles = enumerate_profiles()
        with self.assertRaises(ValueError):
            verify_claw_prefix(profiles[tuple(map(int, '000001'))])
        with self.assertRaises(ValueError):
            verify_private_cycle(profiles[tuple(map(int, '001011'))])
        self.assertEqual(verify_private_cycle(profiles[tuple(map(int, '011110'))]),
                         {'cubic_boundary_minimum': 18, 'quartic_boundary_maximum': 15})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'sources/nine/treewidth36-family.g6'
            path.parent.mkdir(parents=True)
            path.write_text('invalid\n')
            with self.assertRaisesRegex(ValueError, 'Wrong prior'):
                verify_prior_inverses(directory)

    def test_master_requires_every_branch_and_replays_supplied_proofs(self):
        profiles = enumerate_profiles()
        hand = {tuple(map(int, code)) for code in ('001011', '011110')}
        proved = set(profiles)-hand
        self.assertEqual(len(finish_coverage(profiles, proved)), 40)
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            finish_coverage(profiles, proved-{tuple(map(int, '000001'))})
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            finish_coverage(profiles, proved|{(9,)*6})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'false.json'
            path.write_text(json.dumps({'format':'52-edge-branch-refutation-v10',
                'scope':'minimum-order-counterexample',
                'prefix':profiles[tuple(map(int, '000001'))], 'proof':['x']}))
            with self.assertRaises(ValueError):
                verify_complete(ROOT, [path])
        with self.assertRaises(ValueError):
            verify_complete(ROOT, [], workers=True)


if __name__ == '__main__':
    unittest.main()
