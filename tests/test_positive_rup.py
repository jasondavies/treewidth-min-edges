"""A propositional checker must reject missing or circular justifications."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verify_positive_rup import verify


class RUPTest(unittest.TestCase):
    def proof(self):
        return {'format': 'positive-rup-v1', 'variables': 2,
                'inputs': [[1], [-1, 2], [-2]],
                'steps': [[[2], [1, 2]], [[], [3, 4]]]}

    def test_valid_two_step_proof(self):
        self.assertEqual(verify(self.proof()), (3, 2))

    def test_a_satisfiable_premise_does_not_prove_empty(self):
        certificate = self.proof()
        certificate['inputs'] = [[1], [-1, 2]]
        certificate['steps'] = [[[], [1, 2]]]
        with self.assertRaises(ValueError):
            verify(certificate)

    def test_unit_hints_cannot_be_replaced_by_a_nonunit(self):
        certificate = self.proof()
        certificate['steps'] = [[[], [2]]]
        with self.assertRaises(ValueError):
            verify(certificate)

    def test_forward_zero_negative_and_boolean_hints(self):
        for hint in (4, 0, -1, True):
            certificate = self.proof()
            certificate['steps'][0][1] = [hint]
            with self.assertRaises(ValueError):
                verify(certificate)

    def test_invalid_literals_and_empty_premises(self):
        for premise in ([0], [3], [True], [1, 1], []):
            certificate = self.proof()
            certificate['inputs'][0] = premise
            with self.assertRaises(ValueError):
                verify(certificate)

    def test_requires_an_empty_conclusion(self):
        certificate = self.proof()
        certificate['steps'].pop()
        with self.assertRaises(ValueError):
            verify(certificate)


if __name__ == '__main__':
    unittest.main()
