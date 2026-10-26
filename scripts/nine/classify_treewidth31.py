"""Classify the 31-edge residues for degree-five 36-edge cores.

The final class has order 14--16, maximum degree five, minimum degree
three, and at most five degree-three vertices. It is closed backwards
under degree-three elimination using the saved 28/29/30-edge families.
"""
from collections import Counter
import argparse
import json
from pathlib import Path
from treewidth_parallel_classification import ParallelChecks
from treewidth_classification_support import source_hashes
from classify_treewidth34 import decode
from run_treewidth_edge_checks import ROOT,encode,SOURCE


def viable(a):
    n=len(a);remaining=16-n
    return (remaining>=0 and min(map(len,a))>=3
            and sum(len(ns)==3 for ns in a)+max(0,14-n)<=5
            and sum(max(0,len(ns)-5) for ns in a)<=3*remaining
            and max(map(len,a))<=5+remaining)


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cores',type=Path,required=True)
    parser.add_argument('--family30',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=16)
    args=parser.parse_args();out=args.output.resolve();checks=ParallelChecks(out,args.workers)
    summary=json.loads((args.cores/'summary.json').read_text());assert summary['status']=='complete'
    core_graphs=[]
    for p in sorted(args.cores.glob('n*-part-*.g6')):
        assert p.with_suffix('.json').exists()
        for s in p.read_text().splitlines():
            if viable(decode(s)):core_graphs.append(s)
    cores=checks.canon(core_graphs);print('viable cores',len(cores),flush=True)
    family30=args.family30.read_text().splitlines()
    family29=(ROOT/'sources/nine/treewidth34-family29.g6').read_text().splitlines()
    f='K?bFBO{}?}Ug';k8=encode([set(range(8))-{v} for v in range(8)])
    seeds=cores.copy()
    for lower,keep,label in [(family30,1,'from30'),(family29,2,'from29'),([f,k8],3,'from28')]:
        seeds|=checks.construct(lower,'delta',[keep,6,14,16,5,5],label)
    found=checks.delta_closure(seeds,6,14,16,5,5,'full')
    final=sorted(s for s in found if 14<=len(decode(s))<=16 and max(map(len,decode(s)))<=5)
    (out/'family.g6').write_text('\n'.join(final)+'\n')
    report={'status':'complete','viable_cores':len(cores),'family':len(final),
            'family_by_order':dict(Counter(len(decode(s)) for s in final)),
            'stages':checks.constructions,'inputs':source_hashes([args.cores/'summary.json',args.family30,ROOT/'sources/nine/treewidth34-family29.g6']),
            'source_sha256':source_hashes([Path(__file__),ROOT/'scripts/nine/treewidth_parallel_classification.py',
                ROOT/'scripts/nine/treewidth_delta_extensions.c',SOURCE])}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(report['family_by_order'],flush=True)


if __name__=='__main__':main()
