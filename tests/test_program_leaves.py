"""Bounded policy replay and normalization-sensitive reference snapshots."""
import copy
import io
import json
import lzma
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import verify_branch_refutation as kernel
from branch_certificate_binary import decode, encode, verify_stream


def family(case):
    n = len(case['degree'])
    return ([{v for v in range(n) if mask >> v & 1} for mask in case['known']],
            [{v for v in range(n) if mask >> v & 1} for mask in case['possible']],
            case['degree'].copy())


class ProgramLeafTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures = Path(__file__).resolve().parent / 'fixtures'
        cls.cases = json.loads((fixtures / 'program-leaf-families.json').read_text())
        cls.referenced = json.loads(lzma.decompress((fixtures / 'referenced-raw-program.json.xz').read_bytes()))

    def test_real_policies_switch_and_pure_elimination_reproduce_checked_traces(self):
        for name, case in self.cases.items():
            if name == 'nonclosing':
                continue
            a, b, degree = family(case)
            if case['program'][1]:
                kernel.normalise(a, b, degree)
            before = copy.deepcopy((a, b))
            with self.subTest(name=name):
                trace = kernel.run_program(a, b, degree, *case['program'][2:])
                self.assertEqual(trace, case['trace'])
                self.assertLessEqual(len(trace), len(degree))
                self.assertEqual((a, b), before)
                # Independently replay the resulting explicit trace as well.
                kernel.verify_trace(a, b, degree, trace)

    def test_nonclosing_program_is_rejected_within_n_operations(self):
        case = self.cases['nonclosing']
        a, b, degree = family(case)
        operations = []
        step = kernel.Bounds.step

        def tracked(state, operation, vertex):
            operations.append((operation, vertex))
            return step(state, operation, vertex)

        with patch.object(kernel.Bounds, 'step', tracked), self.assertRaises(ValueError):
            kernel.run_program(a, b, degree, *case['program'][2:])
        self.assertLessEqual(len(operations), len(degree))

    def test_invalid_parameters_and_expected_trace_mismatch_are_rejected(self):
        for arguments in ((True, 0, -1), (3, 0, -1), (0, True, -1), (0, 25, -1),
                          (2, 9, -1), (0, 0, True), (0, 0, 0), (0, 0, 25), (2, 0, 1)):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                kernel.validate_program(25, *arguments)
        case = self.cases['policy0']
        a, b, degree = family(case)
        expected = copy.deepcopy(case['trace'])
        expected[0][1] = (expected[0][1] + 1) % len(degree)
        with self.assertRaises(kernel.ProgramMismatch) as error:
            kernel.run_program(a, b, degree, *case['program'][2:], expected=expected)
        self.assertEqual(error.exception.step, 0)

    def test_referenced_raw_program_replays_before_normalized_snapshot(self):
        sequence, captured = [], {}
        program, normalise = kernel.run_program, kernel.normalise

        def tracked_program(known, possible, *args, **kwargs):
            captured['known'] = known
            captured['before'] = copy.deepcopy((known, possible))
            sequence.append('program')
            return program(known, possible, *args, **kwargs)

        def tracked_normalise(known, possible, degree):
            if known is captured.get('known'):
                sequence.append('normalize')
                result = normalise(known, possible, degree)
                captured['changed'] = captured['before'] != (known, possible)
                return result
            return normalise(known, possible, degree)

        with patch.object(kernel, 'run_program', tracked_program), patch.object(kernel, 'normalise', tracked_normalise):
            stats = kernel.verify_certificate(self.referenced)
        self.assertEqual(sequence, ['program', 'normalize'])
        self.assertTrue(captured['changed'])
        self.assertEqual(stats['program_leaves'], 1)
        self.assertEqual(stats['references'], 175)

    def test_referenced_program_binary_roundtrip_and_invalid_mode(self):
        stream = io.BytesIO()
        encode(self.referenced, stream)
        data = stream.getvalue()
        self.assertEqual(decode(io.BytesIO(data)), self.referenced)
        self.assertEqual(verify_stream(io.BytesIO(data)), kernel.verify_certificate(self.referenced))
        for mode in (True, 2, -1):
            invalid = copy.deepcopy(self.referenced)
            invalid['proof'] = ['g', mode, 0, 0, -1]
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                kernel.verify_certificate(invalid)


if __name__ == '__main__':
    unittest.main()
