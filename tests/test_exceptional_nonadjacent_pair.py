from itertools import combinations
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_exceptional_nonadjacent_pair import (
    attachments, expected_counts, find_and_verify_order, reconstruct, residue_graph,
    validate_reconstruction, verify_order,
)
from quartic_order_programs import native_interpreter


class NonadjacentPairTests(unittest.TestCase):
    def test_attachment_normalization_against_unrestricted_subsets(self):
        # Ten abstract residue vertices suffice to exercise every t and split.
        # Only row lengths are used by the attachment iterator.
        abstract = [set(range(3)) for _ in range(4)] + [set(range(4)) for _ in range(6)]
        canonical = lambda a, b: tuple(sorted((tuple(sorted(a)), tuple(sorted(b)))))
        actual = [canonical(a, b) for _, a, b in attachments(abstract)]
        self.assertEqual(len(actual), len(set(actual)))
        cubics = set(range(4))
        choices = list(map(set, combinations(range(10), 5)))
        expected = {canonical(a, b) for a, b in combinations(choices, 2)
                    if cubics <= a | b and a & b <= cubics}
        self.assertEqual(set(actual), expected)
        self.assertEqual(sum(expected_counts().values()), 3732129)

    def test_actual_inverse_and_order(self):
        residue = residue_graph()
        t, left, right = next(attachments(residue))
        graph = reconstruct(residue, left, right)
        self.assertEqual(validate_reconstruction(graph, residue), t)
        self.assertEqual(sorted(map(len, graph)), [4] * 16 + [5] * 8)
        with native_interpreter() as interpreter:
            self.assertIn(len(find_and_verify_order(graph, interpreter)), (1, 2))
        changed = [row.copy() for row in graph]
        u = next(iter(changed[0]))
        changed[0].remove(u)
        changed[u].remove(0)
        with self.assertRaises(ValueError):
            validate_reconstruction(changed, residue)
        changed = [row.copy() for row in graph]
        changed[22].add(23)
        changed[23].add(22)
        with self.assertRaises(ValueError):
            validate_reconstruction(changed, residue)

    def test_padding_requires_both_dummy_vertices(self):
        residue = residue_graph()
        _, left, right = next(attachments(residue))
        graph = reconstruct(residue, left, right)
        invalid = [list(range(24)), list(range(25)), list(range(25)) + [24],
                   [False] + list(range(1,26))]
        for order in invalid:
            with self.assertRaisesRegex(ValueError, 'padded'):
                find_and_verify_order(graph, lambda g, p, result=order: result)
        # A complete 26-permutation is still not a proof of width ten.
        clique = [set(range(12)) - {v} if v < 12 else set() for v in range(24)]
        with self.assertRaisesRegex(ValueError, 'width ten'):
            find_and_verify_order(clique, lambda g, p: list(range(26)))

    def test_finite_failure_is_not_a_proof(self):
        calls = []
        graph = [set() for _ in range(24)]
        def never(g, program):
            calls.append(program)
            return None
        with self.assertRaisesRegex(ValueError, 'No width-ten order'):
            find_and_verify_order(graph, never)
        self.assertEqual(len(calls), 26 + 26 * 25)
        self.assertEqual(len(set(calls)), len(calls))
        with self.assertRaises(ValueError):
            verify_order(graph, list(range(23)))


if __name__ == '__main__':
    unittest.main()
