import io
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from branch_certificate_binary import decode, encode, verify_stream
from verify_branch_refutation import (Contradiction, PREMISE_NOTICE, forbid, force,
                                     normalise, project_marked_residue, verify_certificate)
from verify_profile_refutation import Interval

PREFIX = [24,8,1984,14528,49328,196784,786508,3145804,4194355,8388623,
          1,1,1,2,2,2,4,4,8,8,16,16,32,32,64,128]


def family(present=None):
    state = Interval(PREFIX)
    normalise(state.known, state.possible, state.upper)
    if present is not None:
        (force if present else forbid)(state.known, state.possible, 22, 23)
        normalise(state.known, state.possible, state.upper)
    return state


class MarkedProjectionTests(unittest.TestCase):
    def test_exact_eligible_set_required_and_projected_edges(self):
        state = family()
        before = [row.copy() for row in state.possible]
        self.assertEqual(project_marked_residue(state.known, state.possible, state.upper), 0)
        self.assertEqual(state.possible, before)
        for present in (False, True):
            state = family(present)
            before_known = [row.copy() for row in state.known]
            before_possible = [row.copy() for row in state.possible]
            self.assertEqual(project_marked_residue(state.known, state.possible, state.upper), 12)
            self.assertEqual(state.known, before_known)
            removed = {(u,v) for u in range(24) for v in before_possible[u] - state.possible[u]
                       if u < v}
            self.assertEqual(removed, {(u,v) for u in range(8,14) for v in (22,23)})
            self.assertTrue(all(u in state.possible[v] for u in range(24)
                                for v in state.possible[u]))

    def test_known_violation_closes_and_scope_is_checked(self):
        state = family(False)
        force(state.known, state.possible, 8, 22)
        with self.assertRaises(Contradiction):
            project_marked_residue(state.known, state.possible, state.upper)
        state = family(False)
        with self.assertRaises(ValueError):
            project_marked_residue(state.known, state.possible, [4] * 24)
        state.possible[0].add(23)
        state.possible[23].add(0)
        with self.assertRaises(ValueError):
            project_marked_residue(state.known, state.possible, state.upper)

    def test_version_and_stream_framing(self):
        def cert(proof, version=7):
            return {'format': f'52-edge-branch-refutation-v{version}',
                    'scope': 'minimum-order-counterexample', 'prefix': PREFIX, 'proof': proof}
        for proof in (['m'], ['m', ['x']]):
            stream = io.BytesIO();encode(cert(proof), stream)
            self.assertEqual(decode(io.BytesIO(stream.getvalue())), cert(proof))
            with self.assertRaises(ValueError):
                verify_stream(io.BytesIO(stream.getvalue()), PREFIX)
            for version in (1,2,3,4,6):
                with self.assertRaises(ValueError):
                    encode(cert(proof, version), io.BytesIO())
        stream = io.BytesIO();encode(cert(['m', ['x']]), stream)
        with self.assertRaises(ValueError):
            decode(io.BytesIO(stream.getvalue()[:-1]))
        with self.assertRaises(ValueError):
            decode(io.BytesIO(stream.getvalue() + b'\0'))
        self.assertIn('marked H22', PREMISE_NOTICE)
        self.assertIn('nonadjacent-high', PREMISE_NOTICE)


if __name__ == '__main__':
    unittest.main()
