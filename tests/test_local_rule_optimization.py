"""Differential checks of the optional-edge shortcut against full local rules."""
from itertools import combinations, product
from pathlib import Path
import random
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_branch_refutation import edge_local_contradiction, local_contradiction


def graph(n, edges):
    result = [set() for _ in range(n)]
    for u, v in edges:
        result[u].add(v)
        result[v].add(u)
    return result


class LocalRuleOptimizationTests(unittest.TestCase):
    def compare_optional_edges(self, known, possible, degree):
        # The shortcut's contract requires a locally consistent starting
        # graph. The full checker tests this before its optional-edge loop.
        if local_contradiction(known, possible, degree):
            return 0, 0
        n = len(known)
        low = {v for v in range(n) if degree[v] == 4}
        high = set(range(n)) - low
        triangles = [sum(w in known[u] for u, w in combinations(sorted(ns), 2))
                     for ns in known]
        checked = rejected = 0
        for u, v in combinations(range(n), 2):
            if v not in possible[u] - known[u]:
                continue
            known[u].add(v)
            known[v].add(u)
            try:
                expected = local_contradiction(known, possible, degree)
                actual = edge_local_contradiction(known, possible, degree,
                                                  u, v, triangles, low, high)
                self.assertEqual(actual, expected,
                                 (known, possible, degree, u, v, triangles))
                checked += 1
                rejected += int(expected)
            finally:
                known[u].remove(v)
                known[v].remove(u)
        return checked, rejected

    def test_all_four_vertex_intervals_and_degree_classes(self):
        # An edge is absent, optional, or certain. Try every such pair of
        # graphs, and every assignment of the low/high target-degree class.
        pairs = list(combinations(range(4), 2))
        checked = rejected = 0
        for labels in product(range(3), repeat=len(pairs)):
            known = graph(4, [edge for edge, label in zip(pairs, labels) if label == 2])
            possible = graph(4, [edge for edge, label in zip(pairs, labels) if label != 0])
            for degree in product((4, 5), repeat=4):
                count, failures = self.compare_optional_edges(known, possible, degree)
                checked += count
                rejected += failures
        self.assertGreater(checked, 10000)
        self.assertGreater(rejected, 1000)
        self.assertGreater(checked - rejected, 1000)

    def test_seeded_larger_intervals(self):
        # Larger neighborhoods exercise common-low-neighbor limits and the
        # nonadjacent-high-neighbor rule, which four vertices cannot cover.
        rng = random.Random(1162026)
        checked = rejected = 0
        for _ in range(6000):
            n = rng.randrange(6, 16)
            pairs = list(combinations(range(n), 2))
            degree = [rng.choice((4, 5)) for _ in range(n)]
            known = graph(n, [edge for edge in pairs if rng.random() < 2 / n])
            possible = graph(n, [(u, v) for u, v in pairs
                                 if v in known[u] or rng.random() < 0.7])
            count, failures = self.compare_optional_edges(known, possible, degree)
            checked += count
            rejected += failures
        self.assertGreater(checked, 50000)
        self.assertGreater(rejected, 10000)
        self.assertGreater(checked - rejected, 10000)


if __name__ == '__main__':
    unittest.main()
