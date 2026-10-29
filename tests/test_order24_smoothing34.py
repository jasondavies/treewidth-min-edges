"""Check the fixed34-edge reduction and its proof-operation boundary."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_order24_smoothing34 import check_recipe, verify

PREFIX = [24, 8, 1922, 14401, 49376, 196832, 786656, 3145756, 4194334, 8388637,
          1, 1, 1, 2, 2, 2, 4, 4, 8, 8, 16, 16, 32, 32, 64, 128]
RECIPE = {'delete': [5, 6, 7], 'eliminate': [2, 3, 4]}


class Smoothing34Tests(unittest.TestCase):
    def test_exact_reduction_and_surviving_degree_bound(self):
        result = check_recipe(PREFIX, RECIPE)
        self.assertEqual(result['edge_upper_trajectory'], [37, 36, 35, 34])
        self.assertEqual(result['nonisolated_vertices_lower'], 18)
        self.assertEqual(result['minimum_degree_lower'], 3)
        self.assertEqual(result['width_lower'], 8)

    def test_deletion_set_must_be_independent(self):
        with self.assertRaisesRegex(ValueError, 'independent'):
            check_recipe(PREFIX, {'delete': [0, 1, 2], 'eliminate': [3, 4, 5]})

    def test_degree_four_high_cannot_be_suppressed(self):
        with self.assertRaisesRegex(ValueError, 'degree greater than two'):
            check_recipe(PREFIX, {'delete': [5, 6, 7], 'eliminate': [0, 3, 4]})

    def test_duplicate_catalogue_entry_is_rejected(self):
        case = {'catalogue_index': 0, **RECIPE}
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            verify({'format': 'order24-high-smoothing34-v1', 'cases': [case, case]}, [PREFIX])


if __name__ == '__main__':
    unittest.main()
