"""The35-edge reduction needs both its edge and minimum-degree hypotheses."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_order24_smoothing35 import check_recipe

PREFIX = [24, 8, 1928, 6344, 24744, 98311, 393440, 1572948, 6291506, 8388631,
          1, 1, 1, 2, 2, 4, 4, 8, 8, 16, 16, 32, 32, 64, 64, 128]
RECIPE = {'delete': [0, 1, 2], 'eliminate': [3, 7]}


class Smoothing35Tests(unittest.TestCase):
    def test_exact_reduction(self):
        result = check_recipe(PREFIX, RECIPE)
        self.assertEqual(result['edge_upper_trajectory'], [37, 36, 35])
        self.assertEqual(result['nonisolated_vertices_lower'], 19)
        self.assertEqual(result['minimum_degree_lower'], 3)
        self.assertEqual(result['width_lower'], 8)

    def test_deletion_set_must_be_independent(self):
        with self.assertRaisesRegex(ValueError, 'independent'):
            check_recipe(PREFIX, {'delete': [0, 3, 4], 'eliminate': [2, 7]})

    def test_degree_five_high_cannot_be_suppressed(self):
        with self.assertRaisesRegex(ValueError, 'degree greater than two'):
            check_recipe(PREFIX, {'delete': [0, 1, 2], 'eliminate': [4, 7]})

    def test_no_missing_minimum_degree_premise(self):
        # Move high1's low11 incidence to low8. The validated prefix still
        # has exact high degrees, but low8 loses two edges on deletion.
        prefix = PREFIX[:]
        prefix[2 + 1] ^= (1 << 11) | (1 << 8)
        prefix[2 + 11] &= ~(1 << 1)
        prefix[2 + 8] |= 1 << 1
        with self.assertRaisesRegex(ValueError, 'minimum degree three'):
            check_recipe(prefix, RECIPE)


if __name__ == '__main__':
    unittest.main()
