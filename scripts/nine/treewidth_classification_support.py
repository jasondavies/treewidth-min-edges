"""Canonicalization and independently verified orders for small classifications."""
from pathlib import Path
import shlex
from classify_treewidth34 import decode,triangles
from classify_treewidth30_quartic import inverse
from run_treewidth_edge_checks import ROOT,CC,SOURCE,run,encode,verify_order,digest


class GraphChecks:
    def __init__(self,out):
        self.out=Path(out).resolve();self.out.mkdir(parents=True,exist_ok=True)
        self.canonical=self.out/'canonical';self.checker=self.out/'check';self.logs=[]
        flags=shlex.split(run(['pkg-config','--cflags','--libs','nauty']).stdout)
        run(CC+['-O3',ROOT/'scripts/nine/canonical_graph6.c',*flags,'-o',self.canonical])
        run(CC+['-O3','-DSTANDALONE','-DTW_MAXN=20',SOURCE,'-o',self.checker])

    def canon(self,strings):
        strings=sorted(set(strings));result=set()
        for start in range(0,len(strings),10000):
            result.update(run([self.canonical],input='\n'.join(strings[start:start+10000])+'\n').stdout.splitlines())
        return result

    def retain(self,strings,width,label):
        strings=sorted(self.canon(strings));kept=set()
        for start in range(0,len(strings),5000):
            chunk=strings[start:start+5000]
            answers=run([self.checker,width],input='\n'.join(chunk)+'\n').stdout.splitlines()
            assert len(answers)==len(chunk)
            for s,answer in zip(chunk,answers):
                if answer=='NO':kept.add(s)
                else:
                    assert answer.startswith('YES ')
                    verify_order(decode(s),list(map(int,answer.split()[1:])),width)
        self.logs.append({'label':label,'tested':len(strings),'retained':len(kept),'width':width})
        print(label,len(strings),'->',len(kept),flush=True)
        return kept

    def closure(self,seeds,width,viable,label):
        found=self.retain(seeds,width,label+' initial');frontier=found.copy();step=0
        while frontier:
            generated=[]
            for s in frontier:
                a=decode(s)
                for tri in triangles(a):
                    b=inverse(a,tri,set())
                    if viable(b):
                        assert len(b)<=20,'Checker capacity exceeded; no result may be claimed.'
                        generated.append(encode(b))
            frontier=self.retain(self.canon(generated)-found,width,label+f' step {step}')
            found|=frontier;step+=1
        return found


def append_vertex(a,neighbors):
    b=[set(ns) for ns in a]+[set(neighbors)]
    for v in neighbors:b[v].add(len(a))
    return b


def source_hashes(paths):
    return {str(Path(p).resolve()):digest(Path(p)) for p in paths}
