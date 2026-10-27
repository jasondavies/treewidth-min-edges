"""Check all 46-edge quartic four-cycle reconstructions using saved residues."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
from pathlib import Path
from common import decode
from common import ROOT,CC,run,digest,SOURCE


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=16)
    args=parser.parse_args()
    if args.workers<1:parser.error('Positive worker count required.')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'scripts/ten/treewidth46_four_cycles.c';exe=out/'check'
    run(CC+['-O3','-Wall','-Wextra',source,'-o',exe])
    tasks=[];inputs=[]
    for r,name,expected in [(2,'treewidth36-family.g6',457),(3,'treewidth35-all-family.g6',9),(4,'treewidth34-family34.g6',1)]:
        path=ROOT/'sources/nine'/name;inputs.append(path)
        graphs=[s for s in path.read_text().splitlines() if ord(s[0])-63==21-r and max(map(len,decode(s)))<=4]
        assert len(graphs)==expected
        for i in range(args.workers):
            chunk=graphs[i::args.workers]
            if chunk:tasks.append((r,i,chunk))
    def work(task):
        r,i,graphs=task;stem=out/f'r{r}-part-{i:03d}'
        p=run([exe,r],input='\n'.join(graphs)+'\n')
        row=json.loads(next(s[7:] for s in p.stderr.splitlines() if s.startswith('RESULT ')))
        assert row['inputs']==len(graphs) and row['verified']+row['candidates']==row['graphs']
        stem.with_suffix('.g6').write_text(p.stdout);stem.with_suffix('.log').write_text(p.stderr)
        row.update(common_neighbors=r,part=i)
        stem.with_suffix('.json').write_text(json.dumps(row)+'\n');return row
    rows=[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for f in as_completed([pool.submit(work,t) for t in tasks]):
            row=f.result();rows.append(row);print(row,flush=True)
    assert sum(r['graphs'] for r in rows)==969011
    report={'status':'candidates' if any(r['candidates'] for r in rows) else 'all_verified','results':rows,
            'graphs':sum(r['graphs'] for r in rows),'candidates':sum(r['candidates'] for r in rows),
            'sha256':{str(p):digest(p) for p in [Path(__file__),source,SOURCE,*inputs]}}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['graphs'])


if __name__=='__main__':main()
