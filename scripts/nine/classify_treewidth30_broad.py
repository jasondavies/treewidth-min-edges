"""All needed 30-edge min-degree-three residues through order 16.

Retain up to six degree-three vertices, with no maximum-degree filter.
This supplies both degree-six extensions and the 31-edge classification.
"""
from collections import Counter
from itertools import combinations
import argparse
import json
from pathlib import Path
from treewidth_classification_support import GraphChecks,source_hashes
from classify_treewidth34 import decode,triangles
from classify_treewidth30_quartic import inverse
from run_treewidth_edge_checks import ROOT,encode,SOURCE


def viable(a):
    return len(a)<=16 and min(map(len,a))>=3 and sum(len(ns)==3 for ns in a)<=6


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();checks=GraphChecks(out)
    cores=ROOT/'sources/nine/treewidth30-cores.g6';family29=ROOT/'sources/nine/treewidth34-family29.g6'
    summary=json.loads((ROOT/'sources/nine/treewidth30-core-results.json').read_text());assert summary['status']=='complete'
    seeds=[s for s in cores.read_text().splitlines() if viable(decode(s))]
    for s in family29.read_text().splitlines():
        a=decode(s)
        for tri in triangles(a):
            for edge in combinations(tri,2):
                b=inverse(a,tri,{edge})
                if viable(b):seeds.append(encode(b))
    for a in [decode('K?bFBO{}?}Ug'),[set(range(8))-{v} for v in range(8)]]:
        for tri in triangles(a):
            for keep in combinations(list(combinations(tri,2)),2):
                b=inverse(a,tri,set(keep))
                if viable(b):seeds.append(encode(b))
    family=checks.closure(seeds,6,viable,'30 broad')
    (out/'family.g6').write_text('\n'.join(sorted(family))+'\n')
    report={'status':'complete','family':len(family),'by_order':dict(Counter(len(decode(s)) for s in family)),
            'stages':checks.logs,'inputs':source_hashes([cores,family29]),
            'source_sha256':source_hashes([Path(__file__),ROOT/'scripts/nine/treewidth_classification_support.py',SOURCE])}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(report,flush=True)


if __name__=='__main__':main()
