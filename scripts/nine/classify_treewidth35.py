"""Derive the 35-edge residues needed for all remaining mixed 40-edge cases.

Requires the complete 30-edge core enumeration and the earlier 28/29/34
classifications. Every discarded graph has an order verified in Python.
"""
from collections import Counter
from itertools import combinations
import argparse
import json
from pathlib import Path
import shlex
from classify_treewidth34 import decode,triangles
from classify_treewidth30_quartic import inverse
from run_treewidth_edge_checks import ROOT,CC,SOURCE,run,encode,verify_order,digest


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cores',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    dependency=json.loads((args.cores/'summary.json').read_text());assert dependency['status']=='complete'
    canonical=out/'canonical';checker=out/'check'
    flags=shlex.split(run(['pkg-config','--cflags','--libs','nauty']).stdout)
    run(CC+['-O3',ROOT/'scripts/nine/canonical_graph6.c',*flags,'-o',canonical])
    run(CC+['-O3','-DSTANDALONE','-DTW_MAXN=20',SOURCE,'-o',checker])
    logs=[]
    def canon(strings):
        strings=sorted(set(strings));result=set()
        for start in range(0,len(strings),10000):
            result.update(run([canonical],input='\n'.join(strings[start:start+10000])+'\n').stdout.splitlines())
        return result
    def retain(strings,width,label):
        strings=sorted(canon(strings));kept=set()
        for start in range(0,len(strings),5000):
            chunk=strings[start:start+5000]
            answers=run([checker,width],input='\n'.join(chunk)+'\n').stdout.splitlines()
            assert len(answers)==len(chunk)
            for s,answer in zip(chunk,answers):
                if answer=='NO':kept.add(s)
                else:verify_order(decode(s),list(map(int,answer.split()[1:])),width)
        logs.append({'label':label,'tested':len(strings),'retained':len(kept),'width':width})
        print(label,len(strings),'->',len(kept),flush=True);return kept
    def viable(a,first,last):
        n=len(a);q=sum(len(ns)==3 for ns in a);remaining=last-n
        return (remaining>=0 and min(map(len,a))>=3 and q+max(0,first-n)<=5
                and sum(max(0,len(ns)-5) for ns in a)<=3*remaining
                and max(map(len,a))<=5+remaining)
    def closure(seeds,width,first,last,label):
        found=retain(seeds,width,label+' initial');frontier=found.copy();step=0
        while frontier:
            generated=[]
            for s in frontier:
                a=decode(s)
                if len(a)>=last:continue
                for tri in triangles(a):
                    b=inverse(a,tri,set())
                    if viable(b,first,last):generated.append(encode(b))
            frontier=retain(canon(generated)-found,width,label+f' step {step}');found|=frontier;step+=1
        return found
    seeds=[]
    for p in sorted(args.cores.glob('n*-part-*.g6')):
        assert p.with_suffix('.json').exists()
        for s in p.read_text().splitlines():
            if viable(decode(s),13,16):seeds.append(s)
    family29=(ROOT/'sources/nine/treewidth34-family29.g6').read_text().splitlines()
    # Verify there are no additional order-16 minimum-degree-three residues.
    extra29=[]
    for s in family29:
        a=decode(s)
        if len(a)==15:
            for tri in triangles(a):
                b=inverse(a,tri,set())
                if min(map(len,b))>=3:extra29.append(encode(b))
    assert not retain(extra29,6,'29 order sixteen')
    for s in family29:
        a=decode(s)
        for tri in triangles(a):
            for edge in combinations(tri,2):
                b=inverse(a,tri,{edge})
                if viable(b,13,16):seeds.append(encode(b))
    f=decode('K?bFBO{}?}Ug');k8=[set(range(8))-{v} for v in range(8)]
    for a in (f,k8):
        for tri in triangles(a):
            for keep in combinations(list(combinations(tri,2)),2):
                b=inverse(a,tri,set(keep))
                if viable(b,13,16):seeds.append(encode(b))
    family30=closure(seeds,6,13,16,'30 min3')
    relevant30=sorted(s for s in family30 if 13<=len(decode(s))<=16 and max(map(len,decode(s)))<=5)
    (out/'family30.g6').write_text('\n'.join(relevant30)+'\n')
    print('30 relevant',dict(Counter(len(decode(s)) for s in relevant30)),flush=True)
    candidates=[]
    def extend(a,neighbors):
        b=[set(t) for t in a]+[set(neighbors)]
        for v in neighbors:b[v].add(len(a))
        return b
    for a in (f,k8):
        for ns in combinations(range(len(a)),7):
            b=extend(a,ns)
            if viable(b,15,18):candidates.append(encode(b))
    for s in family29:
        a=decode(s);required=[v for v in range(len(a)) if len(a[v])==3]
        optional=[v for v in range(len(a)) if 4<=len(a[v])<=6]
        if len(required)>6:continue
        for chosen in combinations(optional,6-len(required)):
            b=extend(a,required+list(chosen))
            if min(map(len,b))>=4 and max(map(len,b))<=7 and viable(b,15,18):candidates.append(encode(b))
    for s in relevant30:
        a=decode(s);required=[v for v in range(len(a)) if len(a[v])==3]
        optional=[v for v in range(len(a)) if len(a[v])==4]
        if len(required)>5:continue
        for chosen in combinations(optional,5-len(required)):
            b=extend(a,required+list(chosen))
            assert min(map(len,b))>=4 and max(map(len,b))<=5
            if viable(b,15,18):candidates.append(encode(b))
    cores35=retain(candidates,7,'35 cores')
    (out/'cores35.g6').write_text('\n'.join(sorted(cores35))+'\n')
    family35=closure(cores35,7,15,18,'35 min3')
    relevant35=sorted(s for s in family35 if 15<=len(decode(s))<=18 and max(map(len,decode(s)))<=5)
    (out/'family35.g6').write_text('\n'.join(relevant35)+'\n')
    report={'status':'complete','core_dependency':str(args.cores),'stages':logs,
            'family30_by_order':dict(Counter(len(decode(s)) for s in relevant30)),
            'cores35_by_order':dict(Counter(len(decode(s)) for s in cores35)),
            'family35_by_order':dict(Counter(len(decode(s)) for s in relevant35)),
            'source_sha256':{str(p):digest(p) for p in [Path(__file__),SOURCE]}}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report,flush=True)


if __name__=='__main__':main()
