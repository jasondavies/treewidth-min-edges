import copy
import io
import json
import lzma
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from branch_certificate_binary import decode, encode, read_header, verify_stream
from order25_profiles import enumerate_profiles
from pack_branch_bundle import input_members
from verify_branch_refutation import (Contradiction, Interval, normalise,
                                      project_private_cubic_cap, verify_certificate)


def profile(code):
    return enumerate_profiles()[tuple(map(int, code))]


def initial(code):
    state = Interval(profile(code))
    normalise(state.known, state.possible, state.upper)
    return state


class PrivateCubicCapTests(unittest.TestCase):
    def test_exact_initial_deductions_and_forbidden_two_neighbors(self):
        for code, expected in (('001101', 33), ('001111', 20)):
            state = initial(code)
            before = [row.copy() for row in state.possible]
            self.assertEqual(project_private_cubic_cap(state.known, state.possible, state.upper), expected)
            self.assertEqual(project_private_cubic_cap(state.known, state.possible, state.upper), 0)
            removed = next((u, v) for u in range(25) for v in before[u] - state.possible[u])
            other = initial(code)
            u, v = removed
            other.known[u].add(v)
            other.known[v].add(u)
            with self.assertRaises(Contradiction):
                project_private_cubic_cap(other.known, other.possible, other.upper)

    def test_scope_and_false_terminal_are_rejected(self):
        state = initial('001101')
        with self.assertRaises(ValueError):
            project_private_cubic_cap(state.known, state.possible, [4] * 25)
        state.possible[0].add(24)
        state.possible[24].add(0)
        with self.assertRaises(ValueError):
            project_private_cubic_cap(state.known, state.possible, state.upper)
        certificate = {'format': '52-edge-branch-refutation-v6',
                       'scope': 'minimum-order-counterexample',
                       'prefix': profile('001101'), 'proof': ['c']}
        with self.assertRaises(ValueError):
            verify_certificate(certificate)

    def test_real_certificates_roundtrip_and_framing(self):
        for code in ('001101', '001111'):
            path = ROOT / 'sources/eleven-order25-private-cap' / (code + '.bin.xz')
            raw = lzma.decompress(path.read_bytes())
            stats = verify_stream(io.BytesIO(raw), profile(code))
            self.assertGreater(stats['cubic_cap_projections'], 0)
            certificate = decode(io.BytesIO(raw))
            encoded = io.BytesIO()
            encode(certificate, encoded)
            self.assertEqual(encoded.getvalue(), raw)
            self.assertEqual(verify_certificate(certificate), stats)
            for bad in (raw[:-1], raw + b'\0', raw[:6] + b'\4' + raw[7:]):
                with self.assertRaises(ValueError):
                    verify_stream(io.BytesIO(bad), profile(code))
            legacy = copy.deepcopy(certificate)
            legacy['format'] = '52-edge-branch-refutation-v4'
            with self.assertRaises(ValueError):
                encode(legacy, io.BytesIO())
            wrong = profile('001111' if code == '001101' else '001101')
            with self.assertRaises(ValueError):
                verify_stream(io.BytesIO(raw), wrong)

    def test_json_v6_packing(self):
        raw = lzma.decompress((ROOT / 'sources/eleven-order25-private-cap/001101.bin.xz').read_bytes())
        certificate = decode(io.BytesIO(raw))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'proof.json'
            path.write_text(json.dumps(certificate))
            self.assertEqual(list(input_members(path, 25)), [raw])


if __name__ == '__main__':
    unittest.main()
