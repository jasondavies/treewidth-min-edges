"""Classify all 35-edge graphs of minimum degree three and treewidth >=8.

Unlike the earlier 40-edge-specific classifier, no prospective final-order,
degree-five, or number-of-degree-three-vertices filter is applied here.
"""
from collections import Counter
from itertools import combinations
import argparse
import json
from pathlib import Path
from treewidth_classification_support import GraphChecks,append_vertex,source_hashes
from classify_treewidth34 import decode,triangles
from run_treewidth_edge_checks import ROOT,encode,SOURCE


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();checks=GraphChecks(out)
    family29=ROOT/'sources/nine/treewidth34-family29.g6'
    family30=ROOT/'sources/nine/treewidth35-family30.g6'
    base34=ROOT/'sources/nine/treewidth34-family34.g6'
    assert all(not triangles(decode(s)) for s in base34.read_text().splitlines())
    candidates=[]
    f=decode('K?bFBO{}?}Ug');k8=[set(range(8))-{v} for v in range(8)]
    for a in (f,k8):
        for ns in combinations(range(len(a)),7):
            b=append_vertex(a,ns)
            if min(map(len,b))>=4 and max(map(len,b))<=7:candidates.append(encode(b))
    for s in family29.read_text().splitlines():
        a=decode(s);required=[v for v in range(len(a)) if len(a[v])==3]
        optional=[v for v in range(len(a)) if 4<=len(a[v])<=6]
        if len(required)>6:continue
        for chosen in combinations(optional,6-len(required)):
            b=append_vertex(a,required+list(chosen))
            if min(map(len,b))>=4 and max(map(len,b))<=7:candidates.append(encode(b))
    for s in family30.read_text().splitlines():
        a=decode(s);required=[v for v in range(len(a)) if len(a[v])==3]
        optional=[v for v in range(len(a)) if len(a[v])==4]
        assert 13<=len(a)<=16 and max(map(len,a))<=5 and len(required)<=5
        for chosen in combinations(optional,5-len(required)):
            b=append_vertex(a,required+list(chosen));assert min(map(len,b))>=4
            candidates.append(encode(b))
    cores=checks.retain(candidates,7,'35 all cores')
    family=checks.closure(cores,7,lambda a:min(map(len,a))>=3,'35 all min3')
    (out/'cores.g6').write_text('\n'.join(sorted(cores))+'\n')
    (out/'family.g6').write_text('\n'.join(sorted(family))+'\n')
    report={'status':'complete','cores':len(cores),'family':len(family),
            'family_by_order':dict(Counter(len(decode(s)) for s in family)),
            'stages':checks.logs,'inputs':source_hashes([family29,family30,base34]),
            'source_sha256':source_hashes([Path(__file__),ROOT/'scripts/nine/treewidth_classification_support.py',SOURCE])}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(report,flush=True)


if __name__=='__main__':main()
