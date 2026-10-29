from functools import lru_cache
from itertools import combinations, permutations
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import verify_two_k4_incidence as k


class TwoK4Tests(unittest.TestCase):
    def test_four_matrix_counts_against_independent_degree_dp(self):
        counts = []
        for internal in range(4):
            touched = {v for i in range(internal) for v in (i, 5-i)}
            degrees = tuple(1 if v in touched else 2 for v in range(6))
            @lru_cache(None)
            def count(row, remaining):
                if row == 6:
                    return int(not any(remaining))
                return sum(count(row + 1, tuple(value - (v in chosen)
                           for v, value in enumerate(remaining)))
                           for chosen in combinations([v for v in range(6) if remaining[v]], degrees[row]))
            expected = count(0, degrees)
            actual = sum(1 for _ in k.matrices(degrees, degrees))
            self.assertEqual(actual, expected)
            counts.append(actual)
        self.assertEqual(counts, [67950, 9876, 2172, 720])

    def test_internal_matching_normalization(self):
        pairs = k.PAIRS
        opposite = {frozenset((i, 5-i)) for i in range(3)}
        for chosen_size in range(4):
            target = {frozenset((i, 5-i)) for i in range(chosen_size)}
            for chosen in combinations(opposite, chosen_size):
                found = False
                for permutation in permutations(range(4)):
                    edge_map = [pairs.index(tuple(sorted(permutation[v] for v in edge))) for edge in pairs]
                    mapped = {frozenset(edge_map[v] for v in pair) for pair in chosen}
                    if mapped == target:
                        found = True
                        break
                self.assertTrue(found)

    def test_orders_and_bad_certificates(self):
        _, graph = next(k.graphs())
        order = k.propose_order(graph)
        k.verify_order(graph, order)
        for bad in ([0] * 20, order[:-1], [False] + list(range(1, 20))):
            with self.assertRaises(ValueError):
                k.verify_order(graph, bad)
        clique9 = [set(range(9)) - {v} if v < 9 else set() for v in range(20)]
        with self.assertRaisesRegex(ValueError, 'exceeds width7'):
            k.verify_order(clique9, list(range(20)))
        with self.assertRaisesRegex(ValueError, 'no exclusion claimed'):
            k.propose_order(clique9)


if __name__ == '__main__':
    unittest.main()
