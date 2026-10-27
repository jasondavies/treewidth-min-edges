"""Independently rebuild all 46-edge four-cycle extensions with Python sets."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations,islice
import json
from pathlib import Path
from common import decode
from common import ROOT,CC,SOURCE,run,encode,verify_order,digest


def extensions(a,r):
    n=len(a);low=[v for v in range(n) if len(a[v])==3]
    edges=[(u,v) for v in range(n) for u in sorted(a[v]) if u<v]
    for chosen in combinations(edges,r):
        for first in ([{low[0],v} for v in low[1:]] if r==2 else [{low[0]}] if r==3 else [set()]):
            b=[set(ns) for ns in a]+[set() for _ in range(r+2)]
            for z,(u,v) in enumerate(chosen,n):
                b[u].remove(v);b[v].remove(u)
                for w in (u,v,21,22):b[z].add(w);b[w].add(z)
            for v in low:
                w=21 if v in first else 22
                b[w].add(v);b[v].add(w)
            assert len(b)==23 and all(len(ns)==4 for ns in b)
            yield b


def work(task):
    r,s,exe=task;iterator=iter(extensions(decode(s),r));count=0
    while graphs:=list(islice(iterator,128)):
        answers=run([exe,9],input='\n'.join(map(encode,graphs))+'\n').stdout.splitlines()
        assert len(answers)==len(graphs)
        for a,answer in zip(graphs,answers):
            assert answer.startswith('YES '),(encode(a),answer)
            verify_order(a,list(map(int,answer.split()[1:])),9)
        count+=len(graphs)
    return {'common_neighbors':r,'seed':s,'extensions':count}


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=16)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    exe=out/'check';run(CC+['-O3','-DSTANDALONE','-DTW_MAXN=23',SOURCE,'-o',exe])
    tasks=[];inputs=[]
    for r,name in [(2,'treewidth36-family.g6'),(3,'treewidth35-all-family.g6'),(4,'treewidth34-family34.g6')]:
        p=ROOT/'sources/nine'/name;inputs.append(p)
        tasks.extend((r,s,str(exe)) for s in p.read_text().splitlines() if ord(s[0])-63==21-r and max(map(len,decode(s)))<=4)
    rows=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for row in pool.map(work,tasks):
            rows.append(row)
            if len(rows)%64==0:print(len(rows),'/',len(tasks),flush=True)
    count=sum(r['extensions'] for r in rows);assert count==969011
    report={'status':'complete','graphs':count,'results':rows,
            'sha256':{str(p):digest(p) for p in [Path(__file__),SOURCE,*inputs]}}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',count)


if __name__=='__main__':main()
