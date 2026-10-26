"""Verify the small 21-edge classification used by the 29/30-edge reductions."""
import argparse
import json
from pathlib import Path
import shlex
from classify_treewidth34 import replace_triangle
from run_treewidth_edge_checks import ROOT,CC,SOURCE,GENG,run,digest,encode,verify_order


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    flags=shlex.split(run(['pkg-config','--cflags','--libs','nauty']).stdout)
    geng=out/'geng-check';checker=out/'check'
    run(CC+['-O3','-DOUTPROC=tw_out','-DSUMMARY=tw_summary','-DTW_MAXN=10','-DTW_TARGET=5',GENG,SOURCE,*flags,'-o',geng])
    run(CC+['-O3','-DSTANDALONE','-DTW_MAXN=10',SOURCE,'-o',checker])
    rows=[];retained=[]
    for n,expected in [(7,1),(8,32),(9,1382),(10,1188)]:
        p=run([geng,'-c','-d4','-D6',n,'21:21'])
        row=json.loads(next(s[10:] for s in p.stderr.splitlines() if s.startswith('TW_RESULT ')))
        assert row['total']==expected
        rows.append(row);retained+=p.stdout.splitlines()
    k7=[set(range(7))-{v} for v in range(7)]
    assert retained==[encode(k7)]
    a=replace_triangle(k7,(0,1,2))
    answer=run([checker,5],input=encode(a)+'\n').stdout.strip()
    assert answer.startswith('YES ')
    order=list(map(int,answer.split()[1:]));verify_order(a,order,5)
    report={'status':'complete','core_results':rows,'delta_y_graph':encode(a),'delta_y_order':order,
            'source_sha256':{str(p):digest(p) for p in [Path(__file__),SOURCE,GENG]}}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: only K7; its delta-to-Y expansion has width at most five.')


if __name__=='__main__':main()
