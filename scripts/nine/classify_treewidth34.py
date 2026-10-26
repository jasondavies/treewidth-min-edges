"""Derive all 34-edge width-eight graphs of minimum degree >=3, up to order 19.

Dependencies: the completed 29-edge core enumeration, the 21- and 28-edge
classifications, and the complete quartic order-17 enumeration. Every
discarded graph has a positive order checked independently in Python.
"""
from collections import Counter
from itertools import combinations
import argparse
import json
from pathlib import Path
import shlex

from run_treewidth_edge_checks import ROOT,CC,SOURCE,run,digest,encode,verify_order


def decode(s):
    n=ord(s[0])-63;a=[set() for _ in range(n)];bit=0
    for w in range(1,n):
        for v in range(w):
            if (ord(s[1+bit//6])-63)>>(5-bit%6)&1:a[v].add(w);a[w].add(v)
            bit+=1
    return a


def triangles(a):
    return [(u,v,w) for u in range(len(a)) for v in a[u] for w in a[u]&a[v] if u<v<w]


def replace_triangle(a,triple,keep=None):
    b=[set(t) for t in a]+[set(triple)];z=len(a)
    for v in triple:b[v].add(z)
    for u,v in combinations(triple,2):
        if keep!=(u,v):b[u].remove(v);b[v].remove(u)
    return b


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cores29',type=Path,required=True)
    parser.add_argument('--quartic17',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    core_summary=json.loads((args.cores29/'summary.json').read_text())
    seed_summary=json.loads((args.quartic17/'summary.json').read_text())
    assert core_summary['status']=='complete' and core_summary['retained']==124
    assert seed_summary['status']=='complete' and seed_summary['leaves']==86221634 and seed_summary['negative']==1
    flags=shlex.split(run(['pkg-config','--cflags','--libs','nauty']).stdout)
    canonical=out/'canonical';checker=out/'check'
    run(CC+['-O3',ROOT/'scripts/nine/canonical_graph6.c',*flags,'-o',canonical])
    run(CC+['-O3','-DSTANDALONE','-DTW_MAXN=20',SOURCE,'-o',checker])
    logs=[]
    def canon(graphs):
        graphs=sorted(set(graphs))
        if not graphs:return set()
        return set(run([canonical],input='\n'.join(graphs)+'\n').stdout.splitlines())
    def retain(graphs,width,label):
        graphs=sorted(canon(graphs))
        if not graphs:return set()
        answers=run([checker,width],input='\n'.join(graphs)+'\n').stdout.splitlines()
        assert len(answers)==len(graphs)
        kept=set()
        for s,answer in zip(graphs,answers):
            if answer=='NO':kept.add(s)
            else:
                assert answer.startswith('YES ')
                verify_order(decode(s),list(map(int,answer.split()[1:])),width)
        logs.append({'label':label,'tested':len(graphs),'retained':len(kept),'width':width})
        print(label,len(graphs),'->',len(kept),flush=True)
        return kept
    def closure(initial,width,limit,label):
        found=retain(initial,width,label+'-initial');frontier=found.copy();level=0
        while frontier:
            generated=set()
            for s in frontier:
                a=decode(s)
                if len(a)>=limit:continue
                for triple in triangles(a):
                    if all(len(a[v])>=4 for v in triple):generated.add(encode(replace_triangle(a,triple)))
            generated=canon(generated)-found
            if not generated:break
            level+=1;frontier=retain(generated,width,f'{label}-step-{level}');found|=frontier
        return found
    cores29=[]
    for p in sorted(args.cores29.glob('n*-part-*.g6')):cores29+=p.read_text().splitlines()
    assert len(cores29)==124
    f=decode('K?bFBO{}?}Ug');k8=[set(range(8))-{v} for v in range(8)]
    extra=[]
    for a in (f,k8):
        for triple in triangles(a):
            for keep in combinations(triple,2):extra.append(encode(replace_triangle(a,triple,keep)))
    family29=closure(cores29+extra,6,15,'29-min3')
    (out/'family29.g6').write_text('\n'.join(sorted(family29))+'\n')
    print('29 by order',dict(sorted(Counter(len(decode(s)) for s in family29).items())),flush=True)
    candidates34=[]
    for a in (f,k8):
        for neighbors in combinations(range(len(a)),6):
            b=[set(t) for t in a]+[set(neighbors)]
            for v in neighbors:b[v].add(len(a))
            candidates34.append(encode(b))
    for s in family29:
        a=decode(s)
        if not 13<=len(a)<=15 or max(map(len,a))>5:continue
        required=[v for v in range(len(a)) if len(a[v])==3]
        optional=[v for v in range(len(a)) if len(a[v])==4]
        if len(required)>5 or len(required)+len(optional)<5:continue
        for chosen in combinations(optional,5-len(required)):
            neighbors=required+list(chosen);b=[set(t) for t in a]+[set(neighbors)]
            for v in neighbors:b[v].add(len(a))
            assert min(map(len,b))>=4 and max(map(len,b))<=5
            candidates34.append(encode(b))
    for p in sorted(args.quartic17.glob('part-*.g6')):candidates34+=p.read_text().splitlines()
    cores34=retain(candidates34,7,'34-cores')
    (out/'cores34.g6').write_text('\n'.join(sorted(cores34))+'\n')
    family34=closure(cores34,7,19,'34-min3')
    (out/'family34.g6').write_text('\n'.join(sorted(family34))+'\n')
    report={'core29_dependency':str(args.cores29),'quartic17_dependency':str(args.quartic17),
            'family29_count':len(family29),'core34_count':len(cores34),'family34_count':len(family34),
            'family34_by_order':dict(sorted(Counter(len(decode(s)) for s in family34).items())),
            'all_positive_orders_verified_in_python':True,'stages':logs,
            'source_sha256':{str(p):digest(p) for p in [Path(__file__),SOURCE,ROOT/'scripts/nine/canonical_graph6.c']}}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print('34-edge family',report['family34_by_order'],flush=True)


if __name__=='__main__':main()
