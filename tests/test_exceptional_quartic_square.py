from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from marked_residue_common import EXCEPTION_G6, exception_adjacency
from quartic_order_programs import propose_program
from verify_exceptional_quartic_square import reconstructions, verify_order


class ExceptionalSquareTests(unittest.TestCase):
    def test_all_inverse_choices_and_necessary_filters(self):
        count = 0
        for graph in reconstructions():
            self.assertEqual(len(graph), 26)
            self.assertTrue(all(len(row) == 4 for row in graph))
            self.assertFalse(any(graph[u] & graph[v] for u in range(26) for v in graph[u]))
            self.assertTrue(all(len(graph[u] & graph[v]) <= 2
                                for u in range(26) for v in range(u)))
            count += 1
        self.assertEqual(count, 983)

    def test_orders_and_shared_identity_are_checked(self):
        graph = next(reconstructions())
        _, order = propose_program(graph)
        verify_order(graph, order)
        for bad in ([0] * 26, order[:-1], [False] + order[1:]):
            with self.assertRaises(ValueError):
                verify_order(graph, bad)
        dense = [set(range(12)) - {v} if v < 12 else set() for v in range(26)]
        with self.assertRaises(ValueError):
            verify_order(dense, list(range(26)))
        first, second = exception_adjacency(), exception_adjacency()
        first[0].clear()
        self.assertNotEqual(first, second)
        self.assertTrue(EXCEPTION_G6.startswith('U'))


if __name__ == '__main__':
    unittest.main()
