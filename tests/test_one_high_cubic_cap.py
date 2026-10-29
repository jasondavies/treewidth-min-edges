import copy
import io
import json
import lzma
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from branch_certificate_binary import (decode, encode, format_version,
                                       read_node, verify_stream)
from order25_profiles import enumerate_profiles
from pack_branch_bundle import input_members
from verify_branch_refutation import (Interval, normalise,
    project_one_high_cubic_cap, verify_certificate)
from verify_one_high_cubic_cap import one_high_lifts, verify_all

J = [131600,65800,88,134,32773,361472,282628,265224,532482,526337,
     139424,21120,141376,38144,100416,24624,147490,70657,524512,262912]


def prefix(code):
    return enumerate_profiles()[tuple(map(int, code))]


class OneHighCubicCapTests(unittest.TestCase):
    def test_canonical_multidigit_formats_and_reserved_opcodes(self):
        for version in (1, 2, 3, 4, 6, 7, 8, 9, 10):
            name = f'52-edge-branch-refutation-v{version}'
            self.assertEqual(format_version(name), version)
            certificate = {'format': name, 'scope': 'minimum-order-counterexample',
                           'prefix': prefix('000001'), 'proof': ['x']}
            raw = io.BytesIO(); encode(certificate, raw)
            self.assertEqual(raw.getvalue()[6], version)
            self.assertEqual(decode(io.BytesIO(raw.getvalue())), certificate)
        for invalid in ('52-edge-branch-refutation-v0', '52-edge-branch-refutation-v01',
                        '52-edge-branch-refutation-v010', '52-edge-branch-refutation-v11',
                        '52-edge-branch-refutation-v5', '52-edge-branch-refutation-v10x',
                        10, True, None):
            with self.assertRaises(ValueError):
                format_version(invalid)
        for version in (1, 2, 3, 4, 6, 7, 8, 9):
            for opcode in (22, 23):
                with self.assertRaises(ValueError):
                    read_node(io.BytesIO(bytes([opcode])), version, 25)

    def test_inverse_degree_scope_and_no_negative_order_claim(self):
        restored, high, matching, graph = next(one_high_lifts(J))
        self.assertEqual(sorted(row.bit_count() for row in graph), [3]*9+[4]*13+[5])
        self.assertEqual(graph[high].bit_count(), 5)
        self.assertTrue(graph[22] >> high & 1)
        self.assertEqual(graph[restored].bit_count(), 4)
        self.assertEqual(len(set(sum(matching, ()))), 4)
        self.assertTrue(all(restored not in edge and high not in edge for edge in matching))
        with self.assertRaises(ValueError):
            list(one_high_lifts([0]*20))
        with patch('verify_one_high_cubic_cap.intermediate_graphs', return_value=[(0,0,J)]):
            with self.assertRaisesRegex(ValueError, 'incomplete'):
                verify_all('.', lambda graph, width: None)
            with self.assertRaises(ValueError):
                verify_all('.', lambda graph, width: [0]*len(graph))

    def test_checked_proof_roundtrip_and_false_nodes(self):
        raw = lzma.decompress((ROOT/'sources/eleven-order25-one-high/000001.bin.xz').read_bytes())
        stats = verify_stream(io.BytesIO(raw), prefix('000001'))
        self.assertGreater(stats['one_high_cap_projections'], 0)
        self.assertGreater(stats['one_high_cap_leaves'], 0)
        certificate = decode(io.BytesIO(raw))
        self.assertEqual(certificate['format'], '52-edge-branch-refutation-v10')
        out = io.BytesIO(); encode(certificate, out)
        self.assertEqual(out.getvalue(), raw)
        self.assertEqual(verify_certificate(certificate), stats)
        for invalid in (raw[:-1], raw+b'\0', raw[:6]+b'\x09'+raw[7:]):
            with self.assertRaises(ValueError):
                verify_stream(io.BytesIO(invalid), prefix('000001'))
        older = copy.deepcopy(certificate)
        older['format'] = '52-edge-branch-refutation-v8'
        with self.assertRaises(ValueError):
            encode(older, io.BytesIO())
        with self.assertRaises(ValueError):
            verify_certificate(older)
        false_terminal = copy.deepcopy(certificate)
        false_terminal['proof'] = ['u']
        with self.assertRaises(ValueError):
            verify_certificate(false_terminal)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'proof.json'; path.write_text(json.dumps(certificate))
            self.assertEqual(list(input_members(path, 25)), [raw])

    def test_scope_does_not_expand_silently(self):
        state = Interval(prefix('000001'))
        normalise(state.known, state.possible, state.upper)
        with self.assertRaises(ValueError):
            project_one_high_cubic_cap(state.known, state.possible, [4]*25)
        state.possible[0].add(next(v for v in range(4,25) if v not in state.known[0]))
        with self.assertRaises(ValueError):
            project_one_high_cubic_cap(state.known, state.possible, state.upper)


if __name__ == '__main__':
    unittest.main()
