"""Check coverage replay and rejection of incomplete branches or false maps."""
import copy
import json
import lzma
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_order23_coverage import verify


class Order23CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(lzma.decompress(
            (ROOT / 'tests' / 'fixtures' / 'source-order23-coverage-v1.json.xz').read_bytes()))

    def test_complete_cover(self):
        result = verify(self.data)
        self.assertEqual(result['catalogue_size'], 425)
        self.assertEqual(len(result['referenced_indices']), 268)
        self.assertEqual(result['counts']['branches'], 66)

    def test_missing_branch_and_wrong_root(self):
        data = copy.deepcopy(self.data)
        data['proof'][2].pop()
        with self.assertRaises(ValueError):
            verify(data)
        data = copy.deepcopy(self.data)
        data['prefix'][0] = 24
        with self.assertRaises(ValueError):
            verify(data)

    def test_false_catalogue_map(self):
        data = copy.deepcopy(self.data)
        stack = [data['proof']]
        while stack:
            node = stack.pop()
            if node[0] == 'b':
                stack.extend(node[2])
            elif node[0] == 'c':
                node[2][0] = node[2][1]
                break
        else:
            self.fail('Fixture contains no catalogue map.')
        with self.assertRaises(ValueError):
            verify(data)


if __name__ == '__main__':
    unittest.main()
