"""Exclude codegree three in a minimum quartic 20-vertex counterexample.

Deleting the two nonadjacent vertices and smoothing their three common
neighbors gives a 29-edge, 15-vertex graph with degrees 3,3,4,...,4.
Reconstruct every possibility from the earlier 29-edge classification.
"""
from itertools import combinations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from classify_treewidth34 import decode
from run_treewidth_edge_checks import ROOT,CC,SOURCE,run,digest,encode,verify_order


def check(exe):
    if not __debug__:raise RuntimeError('Run without -O.')
    family=ROOT/'sources/nine/treewidth34-family29.g6'
    seeds=[]
    for s in family.read_text().splitlines():
        a=decode(s)
        if len(a)==15 and sorted(map(len,a))==[3,3]+[4]*13:seeds.append((s,a))
    assert len(seeds)==3
    run(CC+['-O3','-DSTANDALONE','-DTW_MAXN=20',SOURCE,'-o',exe])
    count=0;records=[]
    for s,a in seeds:
        low=[v for v in range(15) if len(a[v])==3]
        edges=[(v,w) for v in range(15) for w in a[v] if v<w]
        graphs=[]
        for chosen in combinations(edges,3):
            b=[set(t) for t in a]+[set() for _ in range(5)]
            for z,(v,w) in enumerate(chosen,15):
                b[v].remove(w);b[w].remove(v)
                for x in [v,w,18,19]:b[z].add(x);b[x].add(z)
            for x,y in zip([18,19],low):b[x].add(y);b[y].add(x)
            assert all(len(t)==4 for t in b)
            graphs.append(b)
        answers=run([exe,8],input='\n'.join(encode(b) for b in graphs)+'\n').stdout.splitlines()
        assert len(answers)==len(graphs)
        for b,answer in zip(graphs,answers):
            if answer=='NO':raise RuntimeError('Candidate: '+encode(b))
            verify_order(b,list(map(int,answer.split()[1:])),8)
        count+=len(graphs);records.append({'seed':s,'extensions':len(graphs)})
    report={'graphs':count,'verified':count,'cases':records,'family_sha256':digest(family),
            'source_sha256':{str(p):digest(p) for p in [Path(__file__),SOURCE]}}
    (ROOT/'sources/nine/treewidth40-quartic-codegree.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',count,'extensions')


def main():
    with TemporaryDirectory(prefix='treewidth-codegree-') as directory:
        check(Path(directory)/'check')


if __name__=='__main__':main()
