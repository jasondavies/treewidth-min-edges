import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from full35_compatibility import TemplateFamily
from quartic_path_cnf import formula
from verify_quartic_path_refutation import root_prefix,verify,verify_graph_clause,graph_results

class QuarticPathCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=json.loads((ROOT/'tests/fixtures/p4-small-clauses.json').read_text())
        cls.family=TemplateFamily(ROOT)
        cls.cnf,cls.edges,_=formula(root_prefix()[2:])

    def test_small_checked_terminals(self):
        self.assertEqual(self.fixture['root'],root_prefix())
        for item in self.fixture['cases']:
            result=verify_graph_clause(item['clause'],item['proof'],root_prefix(),self.edges,self.family)
            self.assertIn(result['kind'],('q','35','b'))

    def test_no_false_premise_or_missing_binding(self):
        rup={'format':'positive-rup-v1','variables':self.cnf.variables,
             'inputs':[[1],[-1]],'steps':[[[],[1,2]]]}
        # The logical root fixes edge1 present. A fabricated proof of its
        # absence must not turn this propositional contradiction into a proof.
        theory={'format':'quartic-p4-theory-v1','root':root_prefix(),'proofs':[]}
        with self.assertRaisesRegex(ValueError,'lack'):verify(rup,theory,ROOT)
        theory['proofs']=[{'input':1,'proof':{'q':0,'terminal':['q']}}]
        with self.assertRaises(ValueError):verify(rup,theory,ROOT)
        theory['root'][2]^=1<<25
        with self.assertRaisesRegex(ValueError,'root'):verify(rup,theory,ROOT)

    def test_fallback_versions_and_root_are_checked(self):
        item=copy.deepcopy(next(x for x in self.fixture['cases']if x['proof']['terminal'][0]=='b'))
        certificate=item['proof']['terminal'][1]
        certificate['format']='52-edge-branch-refutation-v11'
        with self.assertRaisesRegex(ValueError,'original independent'):
            verify_graph_clause(item['clause'],item['proof'],root_prefix(),self.edges,self.family)
        certificate['format']='52-edge-branch-refutation-v4'
        certificate['prefix'][2]^=1<<25
        with self.assertRaisesRegex(ValueError,'root'):
            verify_graph_clause(item['clause'],item['proof'],root_prefix(),self.edges,self.family)

    def test_parallel_replays_exactly_the_requested_proofs(self):
        inputs=[item['clause']for item in self.fixture['cases']]
        proofs={i:item['proof']for i,item in enumerate(self.fixture['cases'])}
        serial=dict(graph_results(range(3),inputs,proofs,ROOT,root_prefix(),self.edges,1))
        parallel=dict(graph_results(range(3),inputs,proofs,ROOT,root_prefix(),self.edges,2))
        self.assertEqual(serial,parallel)
        with self.assertRaises(ValueError):
            list(graph_results([0],[[-1]],{0:{'q':0,'terminal':['q']}},
                               ROOT,root_prefix(),self.edges,2))
        with self.assertRaises(ValueError):
            list(graph_results(range(3),inputs,proofs,ROOT,root_prefix(),self.edges,0))

    def test_full35_positive_padding_and_budget(self):
        edges,graph,_=self.family.graphs[0];n=len(graph)+2
        known=[{u for u in range(len(graph))if row>>u&1}for row in graph]+[set(),set()]
        state=SimpleNamespace(width=8,edges=edges,remaining=set(range(n)),known=known,
                              possible=[row.copy()for row in known],
                              lower=list(map(len,known)),upper=list(map(len,known)))
        self.assertTrue(self.family.possible(state)[0])
        with self.assertRaisesRegex(ValueError,'incomplete'):self.family.possible(state,node_limit=1)
        state.width=7
        with self.assertRaisesRegex(ValueError,'width8'):self.family.possible(state)

if __name__=='__main__':unittest.main()
