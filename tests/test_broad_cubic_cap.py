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
from branch_certificate_binary import decode, encode, verify_stream
from cubic_cap_reconstruction import target_lifts
from order25_profiles import enumerate_profiles
from pack_branch_bundle import input_members
from verify_branch_refutation import (Contradiction, Interval, normalise,
    project_broad_cubic_cap, project_private_cubic_cap, verify_certificate)
from verify_cubic_neighbor_cap import check

J = [131600,65800,88,134,32773,361472,282628,265224,532482,526337,
     139424,21120,141376,38144,100416,24624,147490,70657,524512,262912]


def prefix(code):
    return enumerate_profiles()[tuple(map(int, code))]


class BroadCubicCapTests(unittest.TestCase):
    def test_finite_extension_is_opt_in(self):
        old = new = without_isolate = 0
        for _, _, graph in target_lifts(J):
            old += 1
            cubics = sum(1 << v for v, row in enumerate(graph) if row.bit_count() == 3)
            self.assertTrue(any(not graph[v] & cubics for v in range(23) if cubics >> v & 1))
        for _, _, graph in target_lifts(J, require_isolate=False):
            new += 1
            cubics = sum(1 << v for v, row in enumerate(graph) if row.bit_count() == 3)
            without_isolate += not any(not graph[v] & cubics for v in range(23) if cubics >> v & 1)
        self.assertEqual((old, new, without_isolate), (7952, 8384, 432))
        with self.assertRaises(ValueError):
            list(target_lifts(J, require_isolate=1))
        with self.assertRaises(ValueError):
            check('.', lambda graph, width: None, without_isolate=1)

    def test_nonprivate_terminal_requires_new_rule(self):
        state = Interval(prefix('001211'))
        normalise(state.known, state.possible, state.upper)
        with self.assertRaises(ValueError):
            project_private_cubic_cap(state.known, state.possible, state.upper)
        with self.assertRaises(Contradiction):
            project_broad_cubic_cap(state.known, state.possible, state.upper)
        state = Interval(prefix('001201'))
        normalise(state.known, state.possible, state.upper)
        with self.assertRaises(ValueError):
            project_broad_cubic_cap(state.known, state.possible, [4] * 25)

    def test_small_real_proofs_and_old_format_rejection(self):
        for code in ('001211', '001201'):
            path = ROOT / 'sources/eleven-order25-broad-cap' / (code + '.bin.xz')
            raw = lzma.decompress(path.read_bytes())
            stats = verify_stream(io.BytesIO(raw), prefix(code))
            self.assertGreater(stats['broad_cap_projections'] + stats['broad_cap_leaves'], 0)
            certificate = decode(io.BytesIO(raw))
            out = io.BytesIO(); encode(certificate, out)
            self.assertEqual(out.getvalue(), raw)
            self.assertEqual(verify_certificate(certificate), stats)
            for invalid in (raw[:-1], raw + b'\0', raw[:6] + b'\7' + raw[7:]):
                with self.assertRaises(ValueError):
                    verify_stream(io.BytesIO(invalid), prefix(code))
            older = copy.deepcopy(certificate)
            older['format'] = '52-edge-branch-refutation-v7'
            with self.assertRaises(ValueError):
                encode(older, io.BytesIO())
        false_terminal = {'format': '52-edge-branch-refutation-v8',
                          'scope': 'minimum-order-counterexample',
                          'prefix': prefix('001100'), 'proof': ['d']}
        with self.assertRaises(ValueError):
            verify_certificate(false_terminal)

    def test_json_v8_packing(self):
        raw = lzma.decompress((ROOT / 'sources/eleven-order25-broad-cap/001211.bin.xz').read_bytes())
        certificate = decode(io.BytesIO(raw))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'proof.json'
            path.write_text(json.dumps(certificate))
            self.assertEqual(list(input_members(path, 25)), [raw])


if __name__ == '__main__':
    unittest.main()
