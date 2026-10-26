"""Checkpointed parallel GENREG search with verified width certificates."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
from pathlib import Path
import subprocess
import time
from build_genreg_treewidth import build
from run_treewidth_edge_checks import digest


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--vertices',type=int,required=True)
    parser.add_argument('--degree',type=int,required=True)
    parser.add_argument('--girth',type=int,default=3)
    parser.add_argument('--width',type=int,default=8)
    parser.add_argument('--cap',type=int,default=-1)
    parser.add_argument('--cover',action='store_true')
    parser.add_argument('--parts',type=int,default=256)
    parser.add_argument('--workers',type=int,default=16)
    parser.add_argument('--case-seconds',type=float,default=90)
    parser.add_argument('--round-seconds',type=float,default=120)
    parser.add_argument('--expected-count',type=int)
    args=parser.parse_args()
    if min(args.vertices,args.degree,args.parts,args.workers,args.case_seconds,args.round_seconds)<=0:parser.error('Positive arguments required.')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    stop=args.width==8 and args.vertices*args.degree==80
    exe=build(args.source,out/'build',args.width,args.cap,args.cover,stop)
    config={'vertices':args.vertices,'degree':args.degree,'girth':args.girth,'parts':args.parts,
            'runner_sha256':digest(Path(__file__)),'build':json.loads((out/'build/build.json').read_text())}
    manifest=out/'manifest.json'
    if manifest.exists():assert json.loads(manifest.read_text())==config,'Use a new output after source changes.'
    manifest.write_text(json.dumps(config,indent=2)+'\n')
    started=time.monotonic()
    def work(i):
        stem=out/f'part-{i:05d}';path=stem.with_suffix('.json')
        if path.exists():return json.loads(path.read_text())
        if time.monotonic()-started>=args.round_seconds:return None
        command=[str(exe),str(args.vertices),str(args.degree),str(args.girth),'-m',str(i+1),str(args.parts)]
        with stem.with_suffix('.g6').open('w') as graphs,stem.with_suffix('.log').open('w') as log:
            try:p=subprocess.run(command,stdout=graphs,stderr=log,text=True,timeout=args.case_seconds)
            except subprocess.TimeoutExpired:return None
        if p.returncode==10:raise RuntimeError(f'Candidate at {stem}.g6; independently verify it.')
        if p.returncode:raise RuntimeError(f'Partition {i} exited {p.returncode}')
        row={'part':i,**json.loads(next(s[10:] for s in stem.with_suffix('.log').read_text().splitlines() if s.startswith('GENREG_TW ')))}
        assert row['leaves']==row['verified']+row['negative']
        assert len(stem.with_suffix('.g6').read_text().splitlines())==row['negative']
        tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(row)+'\n');tmp.replace(path)
        return row
    rows=[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(work,i) for i in range(args.parts)]):
            row=future.result()
            if row is not None:
                rows.append(row)
                if len(rows)%64==0:print(len(rows),'/',args.parts,'complete; retained',sum(r['negative'] for r in rows),flush=True)
    report={'status':'complete' if len(rows)==args.parts else 'partial','parts':args.parts,'completed_parts':len(rows),
            'leaves':sum(r['leaves'] for r in rows),'verified':sum(r['verified'] for r in rows),
            'negative':sum(r['negative'] for r in rows),'covers':sum(r['covers'] for r in rows),
            'results':sorted(rows,key=lambda r:r['part'])}
    if report['status']=='complete' and args.expected_count is not None:
        assert not args.cover and args.cap<0 and report['leaves']==args.expected_count
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],len(rows),'/',args.parts,'retained',report['negative'],flush=True)


if __name__=='__main__':main()
