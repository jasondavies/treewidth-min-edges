"""Classify the 36-edge residues for 41-edge, maximum-degree-five candidates.

Omitting --family31 is an exploratory subset only. A complete result also
requires the 31-edge family and the complete quartic order-18 enumeration.
"""
from collections import Counter
import argparse
import json
from pathlib import Path
from treewidth_cached_classification import CachedParallelChecks
from treewidth_classification_support import source_hashes
from classify_treewidth34 import decode,triangles
from run_treewidth_edge_checks import ROOT,encode,SOURCE


def viable(a):
    n=len(a);remaining=19-n
    return (remaining>=0 and min(map(len,a))>=3
            and sum(len(ns)==3 for ns in a)+max(0,16-n)<=5
            and sum(max(0,len(ns)-5) for ns in a)<=3*remaining
            and max(map(len,a))<=5+remaining)


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family30',type=Path,required=True)
    parser.add_argument('--family31',type=Path)
    parser.add_argument('--quartic18',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=16)
    args=parser.parse_args();out=args.output.resolve();checks=CachedParallelChecks(out,args.workers)
    inputs=[args.family30,args.quartic18/'summary.json',ROOT/'sources/nine/treewidth34-family29.g6',ROOT/'sources/nine/treewidth35-all-family.g6']
    quartic_summary=json.loads((args.quartic18/'summary.json').read_text());assert quartic_summary['status']=='complete'
    quartic=[]
    for p in sorted(args.quartic18.glob('part-*.g6')):
        assert p.with_suffix('.json').exists();quartic+=p.read_text().splitlines()
    assert len(quartic)==quartic_summary['negative']
    for s in quartic:assert len(decode(s))==18 and all(len(ns)==4 for ns in decode(s))
    family29=(ROOT/'sources/nine/treewidth34-family29.g6').read_text().splitlines()
    family30=args.family30.read_text().splitlines()
    f='K?bFBO{}?}Ug';k8=encode([set(range(8))-{v} for v in range(8)])
    cores=checks.canon(quartic)
    for bases,degree,label in [([f,k8],8,'degree8'),(family29,7,'degree7'),(family30,6,'degree6')]:
        cores|=checks.construct(bases,'extend',[degree,36,7],label)
    if args.family31:
        assert json.loads((args.family31.parent/'summary.json').read_text())['status']=='complete'
        inputs.append(args.family31)
        cores|=checks.construct(args.family31.read_text().splitlines(),'extend',[5,36,7],'degree5')
    cores={s for s in cores if viable(decode(s))}
    (out/'cores.g6').write_text('\n'.join(sorted(cores))+'\n')
    family35=(ROOT/'sources/nine/treewidth35-all-family.g6').read_text().splitlines()
    seeds=cores|checks.construct(family35,'delta',[1,7,16,19,5,5],'from35')
    # The full-closure input changes when the degree-five core stage is added.
    label='full' if args.family31 else 'exploratory-full'
    found=checks.delta_closure(seeds,7,16,19,5,5,label)
    final=sorted(s for s in found if 16<=len(decode(s))<=19 and max(map(len,decode(s)))<=5)
    (out/'family.g6').write_text('\n'.join(final)+'\n')
    report={'status':'complete' if args.family31 else 'partial','cores':len(cores),'family':len(final),
            'family_by_order':dict(Counter(len(decode(s)) for s in final)),
            'stages':checks.constructions,'inputs':source_hashes(inputs),
            'source_sha256':source_hashes([Path(__file__),ROOT/'scripts/nine/treewidth_parallel_classification.py',
                ROOT/'scripts/nine/treewidth_cached_classification.py',ROOT/'scripts/nine/treewidth_core_extensions.c',
                ROOT/'scripts/nine/treewidth_delta_extensions.c',SOURCE])}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['family_by_order'],flush=True)


if __name__=='__main__':main()
