"""Independently reconstruct the final extensions using Python sets.

For each graph, obtain an order from the C solver and verify it in Python.
This checks all extensions, not a random sample. The pure-C exhaustive
drivers use bit masks and different neighborhood/subset iteration.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from itertools import combinations
import json
from pathlib import Path
from classify_treewidth34 import decode
from run_treewidth_edge_checks import ROOT,CC,SOURCE,run,encode,verify_order,digest


def work(task):
    kind,s,checker=task;a=decode(s);graphs=[]
    if kind=='five':
        n=len(a);required={v for v in range(n) if len(a[v])==3}
        optional=[v for v in range(n) if len(a[v])==4]
        for extra in combinations(optional,5-len(required)):
            neighbors=required|set(extra);b=[set(ns) for ns in a]+[neighbors]
            for v in neighbors:b[v].add(n)
            assert sum(map(len,b))==80 and min(map(len,b))>=4 and max(map(len,b))<=5
            graphs.append(b)
    else:
        assert len(a)==16
        low=[v for v in range(16) if len(a[v])==3];assert len(low)==4
        edges=[(v,w) for v in range(16) for w in a[v] if v<w];assert len(edges)==30
        for selected in combinations(edges,2):
            for partner in low[1:]:
                b=[set(ns) for ns in a]+[set() for _ in range(4)]
                for z,(v,w) in enumerate(selected,16):
                    b[v].remove(w);b[w].remove(v)
                    for u in (v,w,18,19):b[z].add(u);b[u].add(z)
                for v in low:
                    u=18 if v in (low[0],partner) else 19
                    b[u].add(v);b[v].add(u)
                assert all(len(ns)==4 for ns in b)
                graphs.append(b)
    if not graphs:return {'kind':kind,'seed':s,'extensions':0}
    answers=run([checker,8],input='\n'.join(encode(b) for b in graphs)+'\n').stdout.splitlines()
    assert len(answers)==len(graphs)
    for b,answer in zip(graphs,answers):
        if answer=='NO':raise RuntimeError('Candidate: '+encode(b))
        verify_order(b,list(map(int,answer.split()[1:])),8)
    return {'kind':kind,'seed':s,'extensions':len(graphs)}


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family35',type=Path,required=True)
    parser.add_argument('--quartic',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=16)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    checker=out/'check';run(CC+['-O3','-DSTANDALONE','-DTW_MAXN=20',SOURCE,'-o',checker])
    tasks=[(kind,s,str(checker)) for kind,path in [('five',args.family35),('four-cycle',args.quartic)]
           for s in path.read_text().splitlines()]
    rows=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(work,t) for t in tasks]):
            rows.append(future.result())
            if len(rows)%64==0:print(len(rows),'/',len(tasks),'seeds verified',flush=True)
    report={'status':'complete','families':{kind:sum(r['extensions'] for r in rows if r['kind']==kind)
                                          for kind in ('five','four-cycle')},
            'inputs':{str(p):digest(p) for p in [args.family35,args.quartic]},
            'source_sha256':{str(p):digest(p) for p in [Path(__file__),SOURCE,ROOT/'scripts/nine/run_treewidth_edge_checks.py']},
            'results':sorted(rows,key=lambda r:(r['kind'],r['seed']))}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['families'],flush=True)


if __name__=='__main__':main()
