"""Bounds have no dependency on the order-25 proof bundle or other exclusions."""
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from order_edge_bounds import GLOBAL_MINIMUM, ORDER_MINIMUM


def exact_width(adjacency):
    @lru_cache(None)
    def solve(rows, remaining):
        if not remaining:
            return 0
        best = len(rows)
        for v in range(len(rows)):
            if not remaining >> v & 1:
                continue
            neighbors = rows[v] & remaining
            filled = list(rows)
            for u in range(len(rows)):
                if neighbors >> u & 1:
                    filled[u] |= neighbors & ~(1 << u)
            best = min(best, max(neighbors.bit_count(), solve(tuple(filled), remaining ^ (1 << v))))
        return best
    return solve(tuple(adjacency), (1 << len(adjacency)) - 1)


class OrderBoundTests(unittest.TestCase):
    def test_no_unproved_order_exclusion_is_a_premise(self):
        self.assertEqual(ORDER_MINIMUM[11][21:27], (52,) * 6)
        self.assertEqual(ORDER_MINIMUM[10][14], 49)
        self.assertEqual(ORDER_MINIMUM[10][16], 48)
        for k in range(1, 12):
            for n in range(k + 1, 27):
                self.assertGreaterEqual(ORDER_MINIMUM[k][n], GLOBAL_MINIMUM[k])

    def test_all_graphs_through_five_vertices(self):
        for n in range(1, 6):
            pairs = list(combinations(range(n), 2))
            for mask in range(1 << len(pairs)):
                rows = [0] * n
                for i, (u, v) in enumerate(pairs):
                    if mask >> i & 1:
                        rows[u] |= 1 << v
                        rows[v] |= 1 << u
                width = exact_width(rows)
                for k in range(1, width + 1):
                    self.assertLessEqual(ORDER_MINIMUM[k][n], mask.bit_count())


if __name__ == '__main__':
    unittest.main()
