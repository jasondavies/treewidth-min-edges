"""Audit GENREG callbacks, supergraph pruning and modulo partitioning."""
import argparse
import json
from pathlib import Path
import shlex
from tempfile import TemporaryDirectory
from build_genreg_treewidth import build
from run_treewidth_edge_checks import ROOT,CC,SOURCE,GENG,digest,run


def graph(s):
    n=ord(s[0])-63;a=[set() for _ in range(n)];bit=0
    for w in range(1,n):
        for v in range(w):
            if (ord(s[1+bit//6])-63)>>(5-bit%6)&1:a[v].add(w);a[w].add(v)
            bit+=1
    return a


def cap_ok(s,cap):
    g=graph(s)
    return all(sum(len(g[v]&g[w]) for w in g[v])<=2*cap for v in range(len(g)))


def same_graphs(left,right,canonical):
    assert len(left)==len(right)
    a=run([canonical],input='\n'.join(left)+'\n').stdout.splitlines()
    b=run([canonical],input='\n'.join(right)+'\n').stdout.splitlines()
    assert sorted(a)==sorted(b)


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    args=parser.parse_args()
    flags=shlex.split(run(['pkg-config','--cflags','--libs','nauty']).stdout)
    rows=[]
    with TemporaryDirectory(prefix='genreg-tw-audit-') as directory:
        directory=Path(directory)
        canonical_source=directory/'canonical.c'
        canonical_source.write_text('''#include <assert.h>
#include <nauty.h>
#include <gtools.h>
int main(void) {
 char line[256]; graph g[20],canon[20]; int lab[20],ptn[20],orbits[20];
 DEFAULTOPTIONS_GRAPH(options); statsblk stats; options.getcanon=TRUE;
 while(fgets(line,sizeof line,stdin)) {
  if(line[0]=='\\n')continue;
  int n=graphsize(line);assert(n>=1 && n<=20);stringtograph(line,g,1);
  densenauty(g,lab,ptn,orbits,&options,&stats,1,n,canon);
  fputs(ntog6(canon,1,n),stdout);
 }
 return 0;
}
''')
        canonical=directory/'canonical'
        run(CC+['-O2',canonical_source,*flags,'-o',canonical])
        for d,width,cap,total in [(4,5,1,1544),(5,6,4,7848)]:
            plain=build(args.source,directory/f'plain-{d}',width,-1,False,False)
            p=run([plain,'12',str(d)])
            counts=json.loads(next(s[10:] for s in p.stderr.splitlines() if s.startswith('GENREG_TW ')))
            assert counts['leaves']==total
            expected=[s for s in p.stdout.splitlines() if cap_ok(s,cap)]
            pruned=build(args.source,directory/f'pruned-{d}',width,cap,True,False)
            p=run([pruned,'12',str(d)])
            actual=p.stdout.splitlines();same_graphs(expected,actual,canonical)
            geng=directory/f'geng-{d}'
            run(CC+['-O3','-DOUTPROC=tw_out','-DSUMMARY=regular_summary','-DPRUNE=regular_tw_prune',
                    '-DCOVER_LAST=-1','-DTW_MAXN=20',f'-DTW_TARGET={width}',f'-DREGULAR_DEGREE={d}',
                    GENG,ROOT/'scripts/nine/treewidth40_regular_geng.c',*flags,'-o',geng])
            independent=run([geng,'-c',f'-d{d}',f'-D{d}','12',f'{6*d}:{6*d}']).stdout.splitlines()
            same_graphs(independent,actual,canonical)
            combined=[]
            for i in range(1,9):combined+=run([pruned,'12',str(d),'-m',str(i),'8']).stdout.splitlines()
            assert len(combined)==len(actual) and set(combined)==set(actual)
            rows.append({'n':12,'degree':d,'width':width,'cap':cap,'full_count':total,
                         'negative_graphs':len(actual),'complete_and_pruned_agree':True,
                         'independent_geng_agrees':True,'eight_parts_agree':True})
    report={'cases':rows,'source_sha256':{str(p):digest(p) for p in [Path(__file__),
            ROOT/'scripts/nine/build_genreg_treewidth.py',ROOT/'scripts/nine/genreg_treewidth_adapter.c',SOURCE]}}
    (ROOT/'sources/nine/genreg-treewidth-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',rows)


if __name__=='__main__':main()
