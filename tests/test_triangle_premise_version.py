from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_triangle_refutation import load_json,verify_bundle

class TrianglePremiseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[1]
        cls.coverage=load_json(root/'sources/eleven-quartic-triangle-coverage.json.xz')
        cls.bundle=load_json(root/'sources/eleven-quartic-triangle-refutations.json.xz')

    def test_actual_original_bundle(self):
        _,done,missing=verify_bundle(self.coverage,self.bundle)
        self.assertEqual(len(done),9)
        self.assertEqual(missing,[])

    def test_triangle_free_rule_cannot_prove_its_own_premise(self):
        changed=deepcopy(self.bundle)
        changed['cases'][0]['certificate']['format']='52-edge-branch-refutation-v9'
        changed['cases'][0]['certificate']['proof']=['q']
        with self.assertRaisesRegex(ValueError,'original v1'):
            verify_bundle(self.coverage,changed)

if __name__=='__main__':unittest.main()
