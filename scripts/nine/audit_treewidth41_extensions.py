"""Reconstruct every final 41-edge extension and verify its order in Python."""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from itertools import combinations
import json
from pathlib import Path
from classify_treewidth34 import decode
from run_treewidth_edge_checks import ROOT,CC,SOURCE,run,encode,verify_order,digest


def work(task):
    s,checker=task;a=decode(s);n=len(a)
    required={v for v in range(n) if len(a[v])==3}
    optional=[v for v in range(n) if len(a[v])==4]
    graphs=[]
    for extra in combinations(optional,5-len(required)):
        neighbors=required|set(extra);b=[set(ns) for ns in a]+[neighbors]
        for v in neighbors:b[v].add(n)
        assert sum(map(len,b))==82 and min(map(len,b))>=4 and max(map(len,b))<=5
        graphs.append(b)
    if not graphs:return {'seed':s,'extensions':0}
    answers=run([checker,8],input='\n'.join(encode(b) for b in graphs)+'\n').stdout.splitlines()
    assert len(answers)==len(graphs)
    for b,answer in zip(graphs,answers):
        if answer=='NO':raise RuntimeError('Candidate: '+encode(b))
        verify_order(b,list(map(int,answer.split()[1:])),8)
    return {'seed':s,'extensions':len(graphs)}


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=16)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    checker=out/'check';run(CC+['-O3','-DSTANDALONE','-DTW_MAXN=20',SOURCE,'-o',checker])
    seeds=args.family.read_text().splitlines();rows=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(work,(s,str(checker))) for s in seeds]):
            rows.append(future.result())
            if len(rows)%1024==0:print(len(rows),'/',len(seeds),'seeds verified;',sum(r['extensions'] for r in rows),'extensions',flush=True)
    report={'status':'complete','residues':len(rows),'extensions':sum(r['extensions'] for r in rows),
            'input_sha256':digest(args.family),
            'source_sha256':{str(p):digest(p) for p in [Path(__file__),SOURCE,ROOT/'scripts/nine/run_treewidth_edge_checks.py']},
            'results':sorted(rows,key=lambda r:r['seed'])}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',report['extensions'],flush=True)


if __name__=='__main__':main()
