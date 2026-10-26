"""Classify, with verified prefix pruning, connected 31-edge cores of minimum degree four and width >=7.

The separately checked 21-edge classification bounds maximum degree by
nine. Retained graphs supply the 31-edge residue classification, not final witnesses.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
from pathlib import Path
import shlex
import subprocess
import time
from run_treewidth_edge_checks import ROOT,CC,SOURCE,GENG,digest,run
WRAPPER=ROOT/"scripts/nine/treewidth_core_prune.c"


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=16)
    parser.add_argument('--parts',type=int,default=64)
    parser.add_argument('--case-seconds',type=float,default=90)
    parser.add_argument('--round-seconds',type=float,default=120)
    args=parser.parse_args()
    if min(args.workers,args.parts,args.case_seconds,args.round_seconds)<=0:parser.error('Positive arguments required.')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    flags=shlex.split(run(['pkg-config','--cflags','--libs','nauty']).stdout)
    config={'parts':args.parts,'source_sha256':{str(p):digest(p) for p in [Path(__file__),SOURCE,GENG,WRAPPER]},
            'compiler':run(CC+['--version']).stdout.splitlines()[0]}
    manifest=out/'manifest.json'
    if manifest.exists():assert json.loads(manifest.read_text())==config,'Use a new output after changes.'
    manifest.write_text(json.dumps(config,indent=2)+'\n')
    exe=out/'geng-check'
    run(CC+['-O3','-DOUTPROC=tw_out','-DSUMMARY=prefix_summary','-DPRUNE=prefix_prune','-DPREFIX_BUDGET=128','-DTW_MAXN=15','-DTW_TARGET=6',GENG,WRAPPER,*flags,'-o',exe])
    tasks=[(n,i) for n in range(9,16) for i in range(args.parts)];started=time.monotonic()
    def work(task):
        n,i=task;stem=out/f'n{n}-part-{i:04d}';path=stem.with_suffix('.json')
        if path.exists():return json.loads(path.read_text())
        if time.monotonic()-started>=args.round_seconds:return None
        with stem.with_suffix('.g6').open('w') as graphs,stem.with_suffix('.log').open('w') as log:
            try:p=subprocess.run([str(exe),'-c','-d4','-D9',str(n),'31:31',f'{i}/{args.parts}'],stdout=graphs,stderr=log,text=True,timeout=args.case_seconds)
            except subprocess.TimeoutExpired:return None
        if p.returncode:raise RuntimeError((n,i,p.returncode))
        lines=stem.with_suffix('.log').read_text().splitlines()
        row={'order':n,'part':i,**json.loads(next(s[10:] for s in lines if s.startswith('TW_RESULT '))),
             **json.loads(next(s[14:] for s in lines if s.startswith('PREFIX_RESULT ')))}
        assert row['total']==row['verified']+row['counterexamples']
        assert len(stem.with_suffix('.g6').read_text().splitlines())==row['counterexamples']
        tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(row)+'\n');tmp.replace(path);return row
    rows=[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(work,t) for t in tasks]):
            row=future.result()
            if row is not None:
                rows.append(row)
                if len(rows)%32==0:print(len(rows),'/',len(tasks),'cores',sum(r['total'] for r in rows),'retained',sum(r['counterexamples'] for r in rows),flush=True)
    report={'status':'complete' if len(rows)==len(tasks) else 'partial','completed_parts':len(rows),'parts':len(tasks),
            'graphs':sum(r['total'] for r in rows),'covered_branches':sum(r['covers'] for r in rows),'retained':sum(r['counterexamples'] for r in rows),
            'results':sorted(rows,key=lambda r:(r['order'],r['part']))}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],len(rows),'/',len(tasks),'retained',report['retained'],flush=True)


if __name__=='__main__':main()
