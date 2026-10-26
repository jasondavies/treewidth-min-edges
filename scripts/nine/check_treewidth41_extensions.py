"""Check every degree-five extension of the complete 36-edge residue family."""
import argparse
import json
from pathlib import Path
from treewidth_parallel_classification import ParallelChecks
from treewidth_classification_support import source_hashes
from classify_treewidth34 import decode
from run_treewidth_edge_checks import ROOT,SOURCE


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=16)
    args=parser.parse_args();out=args.output.resolve();checks=ParallelChecks(out,args.workers)
    dependency=args.family.parent/'summary.json';assert json.loads(dependency.read_text())['status']=='complete'
    seeds=args.family.read_text().splitlines()
    for s in seeds:
        a=decode(s)
        assert 16<=len(a)<=19 and sum(map(len,a))==72
        assert min(map(len,a))>=3 and max(map(len,a))<=5 and sum(len(ns)==3 for ns in a)<=5
    candidates=checks.construct(seeds,'extend',[5,41,8],'extensions')
    (out/'candidates.g6').write_text('\n'.join(sorted(candidates))+ ('\n' if candidates else ''))
    report={'status':'candidate' if candidates else 'no_counterexample','residues':len(seeds),
            'candidates':len(candidates),'stages':checks.constructions,
            'inputs':source_hashes([args.family,dependency]),
            'source_sha256':source_hashes([Path(__file__),ROOT/'scripts/nine/treewidth_core_extensions.c',SOURCE])}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],checks.constructions[0]['graphs'],'extensions',flush=True)


if __name__=='__main__':main()
