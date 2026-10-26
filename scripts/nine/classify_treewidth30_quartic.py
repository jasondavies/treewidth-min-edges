"""Classify 30-edge width-seven graphs on 16 vertices with degrees 3,3,3,3,4,...,4.

This is the residue from a four-cycle in a quartic 20-vertex candidate.
The output is complete only when the core30 dependency is complete.
"""
from collections import Counter
from itertools import combinations
import argparse
import json
from pathlib import Path
import shlex
from classify_treewidth34 import decode,triangles
from run_treewidth_edge_checks import ROOT,CC,SOURCE,run,encode,verify_order,digest


def inverse(a,triple,keep):
    b=[set(t) for t in a]+[set(triple)];z=len(a)
    for v in triple:b[v].add(z)
    for u,v in combinations(triple,2):
        if (u,v) not in keep:b[u].remove(v);b[v].remove(u)
    return b


def viable(a):
    remaining=16-len(a)
    if remaining<0 or min(map(len,a))<3:return False
    if sum(len(ns)==3 for ns in a)+remaining>4:return False
    if sum(max(0,len(ns)-4) for ns in a)>3*remaining:return False
    if max(map(len,a))>4+remaining:return False
    return True


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cores',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--exploratory',action='store_true')
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    summary=json.loads((args.cores/'summary.json').read_text())
    if not args.exploratory:assert summary['status']=='complete'
    canonical=out/'canonical';checker=out/'check'
    flags=shlex.split(run(['pkg-config','--cflags','--libs','nauty']).stdout)
    run(CC+['-O3',ROOT/'scripts/nine/canonical_graph6.c',*flags,'-o',canonical])
    run(CC+['-O3','-DSTANDALONE','-DTW_MAXN=20',SOURCE,'-o',checker])
    def canon(strings):
        strings=sorted(set(strings))
        return set(run([canonical],input='\n'.join(strings)+'\n').stdout.splitlines()) if strings else set()
    tested=0
    def retain(strings):
        nonlocal tested
        strings=sorted(canon(strings))
        if not strings:return set()
        answers=run([checker,6],input='\n'.join(strings)+'\n').stdout.splitlines()
        assert len(strings)==len(answers);kept=set()
        for s,answer in zip(strings,answers):
            if answer=='NO':kept.add(s)
            else:verify_order(decode(s),list(map(int,answer.split()[1:])),6)
        tested+=len(strings);print('tested',len(strings),'retained',len(kept),flush=True)
        return kept
    seeds=[]
    for p in sorted(args.cores.glob('n*-part-*.g6')):
        if not p.with_suffix('.json').exists():continue
        for s in p.read_text().splitlines():
            if viable(decode(s)):seeds.append(s)
    for s in (ROOT/'sources/nine/treewidth34-family29.g6').read_text().splitlines():
        a=decode(s)
        for tri in triangles(a):
            for keep in combinations(tri,2):
                b=inverse(a,tri,{keep})
                if viable(b):seeds.append(encode(b))
    for a in [decode('K?bFBO{}?}Ug'),[set(range(8))-{v} for v in range(8)]]:
        for tri in triangles(a):
            edges=list(combinations(tri,2))
            for keep in combinations(edges,2):
                b=inverse(a,tri,set(keep))
                if viable(b):seeds.append(encode(b))
    found=retain(seeds);frontier=found.copy()
    while frontier:
        generated=[]
        for s in frontier:
            a=decode(s)
            if len(a)==16:continue
            for tri in triangles(a):
                b=inverse(a,tri,set())
                if viable(b):generated.append(encode(b))
        frontier=retain(canon(generated)-found);found|=frontier
    final=sorted(s for s in found if len(decode(s))==16)
    for s in final:assert sorted(map(len,decode(s)))==[3]*4+[4]*12
    (out/'family.g6').write_text('\n'.join(final)+'\n')
    report={'status':summary['status'],'core_dependency':str(args.cores),'tested':tested,
            'retained_by_order':dict(Counter(len(decode(s)) for s in found)), 'final_count':len(final),
            'source_sha256':digest(Path(__file__))}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report,flush=True)


if __name__=='__main__':main()
