"""Constructive model-extension checks for the SAT encoding primitives."""
from itertools import combinations, product
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from quartic_path_cnf import Formula, formula


def satisfies(clauses, assignment):
    return all(any(assignment[abs(literal)] == (literal > 0)
                   for literal in clause) for clause in clauses)


class CounterTest(unittest.TestCase):
    def check_counter(self, size, bound, *, negative=False):
        literals = list(range(1, size + 1))
        if negative:
            literals = [-literal for literal in literals]
        cnf = Formula(size)
        thresholds = cnf.at_most(literals, bound)
        for count in range(bound + 1):
            for selected in combinations(range(size), count):
                selected = set(selected)
                truth = [i in selected for i in range(size)]
                assignment = {abs(literal): truth[i] == (literal > 0)
                              for i, literal in enumerate(literals)}
                for (k, j), variable in thresholds.items():
                    assignment[variable] = sum(truth[:j + k + 1]) >= k + 1
                self.assertTrue(satisfies(cnf.clauses, assignment))

    def test_constructive_extension_all_small_valid_patterns(self):
        for size in range(1, 8):
            for bound in range(size + 1):
                self.check_counter(size, bound)
                self.check_counter(size, bound, negative=True)

    def test_actual_degree_and_square_counter_templates(self):
        # Exact degree four uses <=4 positive and <=21 negative inputs.
        # Check the meaningful exact-degree assignments in both halves.
        literals = list(range(1, 26))
        cnf = Formula(25)
        negative = cnf.at_most([-x for x in literals], 21)
        positive = cnf.at_most(literals, 4)
        for selected in combinations(range(25), 4):
            truth = [i in selected for i in range(25)]
            assignment = {i + 1: value for i, value in enumerate(truth)}
            for mapping, values in ((negative, [not x for x in truth]),
                                    (positive, truth)):
                for (k, j), variable in mapping.items():
                    assignment[variable] = sum(values[:j + k + 1]) >= k + 1
            self.assertTrue(satisfies(cnf.clauses, assignment))
        self.check_counter(25, 3)

    def test_boolean_gates(self):
        for conjunction in (False, True):
            cnf = Formula(2)
            result = cnf.gate(1, 2, conjunction=conjunction)
            for a, b, c in product((False, True), repeat=3):
                self.assertEqual(satisfies(cnf.clauses, {1: a, 2: b, result: c}),
                                 c == ((a and b) if conjunction else (a or b)))

    def test_lex_step_truth_table(self):
        clauses = [[-1, -2, 3], [-4, 1], [-4, -2, 3], [-4, 2, -3],
                   [-1, -2, -3, 4], [-1, 2, 3, 4]]
        for previous, a, b, following in product((False, True), repeat=4):
            self.assertEqual(satisfies(clauses, dict(enumerate(
                (previous, a, b, following), 1))),
                (not previous or not a or b)
                and following == (previous and a == b))

    def test_malformed_roots(self):
        root = [30, 353, 673, 3201, 12353, 6, 18, 12, 2, 4, 8, 8,
                16, 16] + [0] * 12
        for bad in (root[:-1], [row | (1 << 26) for row in root],
                    [31] + root[1:], [False] + root[1:]):
            with self.assertRaises(ValueError):
                formula(bad)


if __name__ == '__main__':
    unittest.main()
