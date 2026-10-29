from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_order24_twenty_residue import reduction, admits_high_embedding, verify_recipes

PREFIX = [24, 8, 992, 3280, 12456, 49236, 196650, 786453, 3145739,
          12582919, 1, 1, 2, 2, 4, 4, 8, 8, 16, 16, 32, 32, 64, 64, 128, 128]


class TwentyResidueTests(unittest.TestCase):
    def test_reduction_degree_scope_and_invalid_recipes(self):
        view = reduction(PREFIX, [0, 1, 2], 7)
        self.assertEqual(sorted(view['degree'].values()), [3] * 8 + [4] * 12)
        self.assertEqual(view['high'], [3, 4, 5, 6])
        self.assertEqual(view['endpoints'], (22, 23))
        for deleted, suppressed in (([0, 5, 1], 7), ([0, 1, 2], 0),
                                    ([0, 0, 2], 7), ([False, 1, 2], 7)):
            with self.assertRaises(ValueError):
                reduction(PREFIX, deleted, suppressed)

    def test_embedding_accepts_actual_maps_and_rejects_wrong_degrees(self):
        graph = [0] * 20
        for v in range(20):
            for distance in (1, 2):
                u = (v + distance) % 20
                graph[v] |= 1 << u
                graph[u] |= 1 << v
        adjacency = {v: {u for u in range(20) if graph[v] >> u & 1} for v in range(20)}
        view = {'high': [0, 1, 2, 3], 'known': adjacency,
                'degree': {v: 4 for v in range(20)}, 'endpoints': (4, 5)}
        self.assertTrue(admits_high_embedding(view, graph))
        relabeled = [sum(1 << (19-u) for u in range(20) if graph[19-v] >> u & 1)
                     for v in range(20)]
        self.assertTrue(admits_high_embedding(view, relabeled))
        self.assertFalse(admits_high_embedding(view, [0] * 20))

    def test_unknown_duplicate_roots_and_false_order_are_rejected(self):
        recipe = {'catalogue_index': 0, 'deleted_highs': [0, 1, 2], 'suppressed_high': 7}
        for rows in ([], [recipe, recipe], [{**recipe, 'catalogue_index': 1}],
                     [{**recipe, 'catalogue_index': False}]):
            with self.assertRaises(ValueError):
                verify_recipes({'format': 'order24-twenty-residue-v1', 'recipes': rows},
                               [PREFIX], ROOT, lambda graph, width: None)
        clique9 = [((1 << 9) - 1) ^ (1 << v) if v < 9 else 0 for v in range(20)]
        with patch('verify_order24_twenty_residue.intermediate_graphs',
                   return_value=iter([(0, (), clique9)])):
            with self.assertRaisesRegex(ValueError, 'exceeds width'):
                verify_recipes({'format': 'order24-twenty-residue-v1', 'recipes': [recipe]},
                               [PREFIX], ROOT, lambda graph, width: list(range(20)))


if __name__ == '__main__':
    unittest.main()
