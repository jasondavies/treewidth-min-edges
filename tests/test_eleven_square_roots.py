import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from verify_eleven_square_roots import verify


class RootCoverageTests(unittest.TestCase):
    def test_missing_duplicate_and_overrestricted_roots_are_rejected(self):
        original = json.loads((ROOT/'research/eleven/sources/treewidth-eleven-quartic-complete-audit.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'roots.json'
            path.write_text(json.dumps(original))
            self.assertEqual(verify(path), [1, 3, 7, 12, 13])
            variants = [dict(original, roots=original['roots'][:-1]),
                        dict(original, roots=original['roots']+[original['roots'][0]])]
            extra = copy.deepcopy(original)
            prefix = list(map(int, extra['roots'][0]['prefix'].split()))
            # An arbitrary extra required edge would omit valid completions.
            prefix[2+24] |= 1 << 25
            prefix[2+25] |= 1 << 24
            extra['roots'][0]['prefix'] = ' '.join(map(str, prefix))
            variants.append(extra)
            for variant in variants:
                path.write_text(json.dumps(variant))
                with self.assertRaises(RuntimeError):
                    verify(path)


if __name__ == '__main__':
    unittest.main()
