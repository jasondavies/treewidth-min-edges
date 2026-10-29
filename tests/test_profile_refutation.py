"""Check soundness of the interval rules against all four-vertex graphs."""
import copy
from itertools import combinations, product
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_profile_refutation import Interval, verify_certificate


def graph(n, pairs):
    result = [set() for _ in range(n)]
    for u, v in pairs:
        result[u].add(v)
        result[v].add(u)
    return result


class ProfileRefutationTests(unittest.TestCase):
    def setUp(self):
        self.certificate = json.loads((ROOT / 'sources/eleven-profile20-refutation.json').read_text())

    def test_complete_profile_and_identity(self):
        prefix = list(map(int, (ROOT / 'sources/eleven-profile20.txt').read_text().split()))
        trace = verify_certificate(self.certificate, prefix)
        self.assertEqual([(r['treewidth_at_least'], r['edges_at_most']) for r in trace],
                         [(10, 47), (9, 43), (9, 42), (9, 41)])
        wrong = prefix.copy()
        wrong[-1] = 1
        with self.assertRaises(ValueError):
            verify_certificate(self.certificate, wrong)

    def test_incomplete_or_invalid_proofs_rejected(self):
        for steps in ([], self.certificate['steps'][:-1],
                      [['delete', 0], ['delete', 0]],
                      [['delete', 0], ['delete', 2], ['eliminate', 3]],
                      [['delete', 0], ['delete', 2], ['eliminate', 24]],
                      [['unknown', 0]], [['delete', True]], [['delete', 25]]):
            certificate = copy.deepcopy(self.certificate)
            certificate['steps'] = steps
            with self.subTest(steps=steps), self.assertRaises(ValueError):
                verify_certificate(certificate)
        for prefix in ([], [25, 4], [25, 26] + [0] * 25,
                       [25, 4] + [0] * 25, [25, 0] + [1 << 25] * 25,
                       [25, 0, 1] + [0] * 24, [25, 0, 2] + [0] * 24):
            with self.subTest(prefix=prefix), self.assertRaises(ValueError):
                Interval(prefix)

    def test_interval_steps_against_every_four_vertex_completion(self):
        # Each edge is absent, optional absent, optional present, or certain.
        # Thus all A subset G subset B triples occur. Test both exact degree
        # information and the weakest bounds implied by A and B.
        pairs = list(combinations(range(4), 2))
        checked = 0
        for labels in product(range(4), repeat=len(pairs)):
            known = graph(4, [e for e, label in zip(pairs, labels) if label == 3])
            actual = graph(4, [e for e, label in zip(pairs, labels) if label >= 2])
            possible = graph(4, [e for e, label in zip(pairs, labels) if label >= 1])
            for exact in (False, True):
                for operation in ('delete', 'eliminate'):
                    for v in range(4):
                        state = Interval.__new__(Interval)
                        state.remaining = set(range(4))
                        state.known = [row.copy() for row in known]
                        state.possible = [row.copy() for row in possible]
                        state.lower = [len(row) for row in (actual if exact else known)]
                        state.upper = [len(row) for row in (actual if exact else possible)]
                        state.edges = sum(map(len, actual)) // 2
                        state.width = 5  # Every possible eliminated degree is < 5.
                        state.step(operation, v)
                        result = [row.copy() for row in actual]
                        if operation == 'eliminate':
                            for u, w in combinations(actual[v], 2):
                                result[u].add(w)
                                result[w].add(u)
                        for u in state.remaining:
                            result[u].discard(v)
                            self.assertLessEqual(state.known[u], result[u])
                            self.assertLessEqual(result[u], state.possible[u])
                            self.assertLessEqual(state.lower[u], len(result[u]))
                            self.assertLessEqual(len(result[u]), state.upper[u])
                        result[v].clear()
                        self.assertLessEqual(sum(map(len, result)) // 2, state.edges)
                        checked += 1
        self.assertEqual(checked, 65536)


if __name__ == '__main__':
    unittest.main()
