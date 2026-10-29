import importlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from cubic_cap_reconstruction import (inverse_triangles, lift, target_lifts, universal_apex,
                                      validate_graph, verify_order)
from verify_cubic_neighbor_cap import check, order_proposer

# Small positive fixtures, not inputs or premises of the complete enumeration.
J = [458752,74752,149504,299008,330240,200960,394368,14400,35872,21520,
     834,404,680,524418,524804,524552,51,101,89,57344]
ORDER = [13,0,2,3,1,6,4,14,5,15,7,8,9,10,11,12,16,17,18,19]


class CubicCapTests(unittest.TestCase):
    def test_independent_width_and_universal_lift(self):
        verify_order(J, ORDER, 7)
        verify_order(universal_apex(J), ORDER + [20], 8)
        restored, matching, graph = next(target_lifts(J))
        validate_graph(graph)
        self.assertEqual(sum(row.bit_count() for row in graph), 84)
        verify_order(graph, [20,21] + ORDER + [22], 8)
        # Independently undo the three added vertices with adjacency sets.
        adjacency = [{u for u in range(23) if row >> u & 1} for row in graph]
        for v in adjacency[22]:
            adjacency[v].remove(22)
        for z in (20,21):
            neighbors = adjacency[z] - {22}
            self.assertEqual(len(neighbors), 2)
            u, v = sorted(neighbors)
            adjacency[u].remove(z)
            adjacency[v].remove(z)
            adjacency[u].add(v)
            adjacency[v].add(u)
        self.assertEqual([sum(1 << u for u in adjacency[v]) for v in range(20)], J)
        with self.assertRaises(ValueError):
            lift(J, restored, (matching[0], matching[0]))
        with self.assertRaises(ValueError):
            lift(J, (matching[0][0], restored[0]), matching)

    def test_inverse_triangle_validation(self):
        triangle = [6,5,3]
        self.assertEqual(inverse_triangles(triangle, [(0,1,2)]), [8,8,8,7])
        with self.assertRaises(ValueError):
            inverse_triangles([2,1,0], [(0,1,2)])
        with self.assertRaises(ValueError):
            inverse_triangles(triangle, [(0,1,2),(0,1,2)])

    def test_invalid_orders_and_graphs(self):
        for order in (ORDER[:-1], ORDER[:-1] + [ORDER[0]], [False] + ORDER[1:]):
            with self.assertRaises(ValueError):
                verify_order(J, order, 7)
        clique = [((1 << 12) - 1) ^ (1 << v) for v in range(12)]
        with self.assertRaises(ValueError):
            verify_order(clique, list(range(12)), 8)
        with self.assertRaises(ValueError):
            validate_graph([2,0])

    def test_unknown_is_not_accepted_and_false_orders_fail(self):
        module = importlib.import_module('verify_cubic_neighbor_cap')
        one_target = next(target_lifts(J))
        with patch.object(module, 'intermediate_graphs', return_value=iter([(0,(),J)])), \
             patch.object(module, 'target_lifts', return_value=iter([one_target])):
            with self.assertRaisesRegex(ValueError, 'did not find'):
                check('.', lambda graph, width: None)
        with patch.object(module, 'intermediate_graphs', return_value=iter([(0,(),J)])):
            with self.assertRaises(ValueError):
                check('.', lambda graph, width: list(range(len(graph))))

    def test_native_is_bounded_and_independently_checked(self):
        with order_proposer() as propose:
            found = propose(J, 7)
            self.assertIsNotNone(found)
            verify_order(J, found, 7)
            clique = [((1 << 12) - 1) ^ (1 << v) for v in range(12)]
            self.assertIsNone(propose(clique, 8))
        with self.assertRaises(ValueError):
            with order_proposer(compiler='   '):
                self.fail('Empty compiler command was accepted')


if __name__ == '__main__':
    unittest.main()
