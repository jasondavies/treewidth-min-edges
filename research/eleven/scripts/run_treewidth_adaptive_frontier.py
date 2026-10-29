"""Checkpoint an exhaustive completion tree, splitting timed-out nodes.

Canonical prefix keys include degree classes, marked triangles (where
present), and the processed set. A partial report never proves exclusion.
The supplied completion program must implement the run/split interface.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import re
from pathlib import Path
import shlex
import subprocess
import time
from run_treewidth_edge_checks import ROOT,SOURCE,digest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['source','canonical-source','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--kind',type=int,required=True)
    p.add_argument('--workers',type=int,default=16)
    p.add_argument('--seconds',type=float,default=600)
    p.add_argument('--case-seconds',type=float,default=20)
    p.add_argument('--split-depth',type=int,default=3)
    p.add_argument('--stop-on-candidate',action='store_true')
    p.add_argument('--completed-parts',type=Path)
    p.add_argument('--prefixes',type=Path)
    args=p.parse_args()
    if min(args.workers,args.seconds,args.case_seconds)<1:p.error('Positive limits required.')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    dependencies={Path(__file__).resolve(),args.canonical_source.resolve()}
    def collect(path):
        path=path.resolve()
        if path in dependencies:return
        dependencies.add(path)
        for include in re.findall(r'^#include "([^"]+)"',path.read_text(),re.MULTILINE):collect(path.parent/include)
    collect(args.source)
    if args.prefixes:dependencies.add(args.prefixes.resolve())
    config={'kind':args.kind,'split_depth':args.split_depth,'stop_on_candidate':args.stop_on_candidate,
            'completed_parts':str(args.completed_parts.resolve()) if args.completed_parts else None,
            'prefixes':str(args.prefixes.resolve()) if args.prefixes else None,
            'sha256':{str(q):digest(q) for q in sorted(dependencies)}}
    manifest=out/'manifest.json'
    if manifest.exists():assert json.loads(manifest.read_text())==config,'Source changed: use a new output directory.'
    else:manifest.write_text(json.dumps(config,indent=2)+'\n')
    text=args.source.read_text()
    old='}else if(argc==2&&!strcmp(argv[1],"run")){'
    assert text.count(old)==1
    text=text.replace(old,'''}else if((argc==2&&!strcmp(argv[1],"run"))||(argc==3&&!strcmp(argv[1],"refine"))){
        if(argc==3){char *end;split_depth=(int)strtol(argv[2],&end,10);if(*end)return 2;}
''')
    text=text.replace('initialize(family);assert(start>=0&&start<=n);',
                      'initialize(family);assert(start>=0&&start<=n);if(argc==3)assert(split_depth>start&&split_depth<=n);')
    (out/'complete.c').write_text(text);exe=out/'complete';canonical=out/'canonical'
    flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','nauty'],text=True))
    subprocess.run(['cc','-O3','-mpopcnt','-I',str(ROOT/'scripts'),str(out/'complete.c'),*flags,'-o',str(exe)],check=True)
    subprocess.run(['cc','-O3',str(args.canonical_source.resolve()),*flags,'-o',str(canonical)],check=True)
    state_path=out/'state.json'
    state=json.loads(state_path.read_text()) if state_path.exists() else {'nodes':{},'roots':[]}
    nodes=state['nodes']
    def register(prefixes):
        if not prefixes:return []
        keys=subprocess.check_output([str(canonical)],input='\n'.join(prefixes)+'\n',text=True).splitlines()
        assert len(keys)==len(prefixes)
        result=[]
        for prefix,key in zip(prefixes,keys):
            kind,depth,*a=map(int,prefix.split())
            encoded=f'{kind}:{depth}:{key}';identifier=hashlib.sha256(encoded.encode()).hexdigest()
            if identifier in nodes:assert nodes[identifier]['key']==encoded
            else:nodes[identifier]={'key':encoded,'prefix':prefix,'depth':depth,'status':'pending'}
            result.append(identifier)
        return sorted(set(result))
    if not state['roots']:
        if args.prefixes:
            prefixes=args.prefixes.read_text().splitlines()
            assert all(int(row.split()[0])==args.kind and 0<=int(row.split()[1])<=len(row.split())-2 for row in prefixes)
            state['roots']=register(prefixes)
        else:
            q=subprocess.run([str(exe),'split',str(args.kind),str(args.split_depth)],capture_output=True,text=True,check=True)
            (out/'split.log').write_text(q.stderr);state['roots']=register(q.stdout.splitlines())
    if args.completed_parts:
        previous=json.loads((args.completed_parts/'manifest.json').read_text())
        assert previous['kind']==args.kind and previous['split_depth']==args.split_depth
        for path in dependencies-{Path(__file__).resolve()}:
            assert previous['sha256'][str(path)]==digest(path),'Imported source differs'
        prefixes=(args.completed_parts/'prefixes.txt').read_text().splitlines()
        for i,prefix in enumerate(prefixes):
            stem=args.completed_parts/f'part-{i:06d}';checkpoint=stem.with_suffix('.json')
            if not checkpoint.exists():continue
            row=json.loads(checkpoint.read_text())
            assert row['input_sha256']==hashlib.sha256(prefix.encode()).hexdigest()
            assert row['graphs_sha256']==digest(stem.with_suffix('.g6'))
            assert row['residues']==0
            identifiers=register([prefix]);assert len(identifiers)==1
            identifier=identifiers[0];assert identifier in state['roots']
            nodes[identifier].update(status='done',retained_graphs=[],imported_checkpoint=str(checkpoint),checkpoint_sha256=digest(checkpoint))
    started=time.monotonic();candidate=False
    def work(identifier):
        row=nodes[identifier];stem=out/identifier;timed_out=False
        with stem.with_suffix('.g6').open('w') as graphs,stem.with_suffix('.log').open('w') as log:
            try:
                q=subprocess.run([str(exe),'run'],input=row['prefix']+'\n',text=True,stdout=graphs,stderr=log,
                                 timeout=args.case_seconds)
            except subprocess.TimeoutExpired:timed_out=True
        data=stem.with_suffix('.g6').read_text().splitlines()
        if data and args.stop_on_candidate:return identifier,'candidate',data,None
        if not timed_out:
            if q.returncode:raise RuntimeError(f'{identifier}: exit {q.returncode}')
            return identifier,'done',data,None
        depth=row['depth'];n=len(row['prefix'].split())-2
        if depth==n:raise RuntimeError('A single completed graph exceeded the time limit; increase --case-seconds.')
        refined=subprocess.run([str(exe),'refine',str(depth+1)],input=row['prefix']+'\n',capture_output=True,text=True,
                               timeout=60,check=True)
        stem.with_suffix('.refine.log').write_text(refined.stderr)
        return identifier,'split',data,refined.stdout.splitlines()
    def save():
        # A node is certified only by a completed run or by all its children.
        for identifier in sorted(nodes,key=lambda k:nodes[k]['depth'],reverse=True):
            row=nodes[identifier]
            if row['status']=='split' and all(nodes[c]['status'] in ('done','covered') for c in row['children']):
                row['status']='covered'
        pending=sum(row['status']=='pending' for row in nodes.values())
        complete=all(nodes[k]['status'] in ('done','covered') for k in state['roots'])
        report={'status':'candidate_needs_certificate' if candidate else 'complete' if complete else 'partial',
                'nodes':len(nodes),'pending':pending,'roots':len(state['roots']),
                'covered_roots':sum(nodes[k]['status'] in ('done','covered') for k in state['roots']),
                'seconds_this_round':time.monotonic()-started}
        tmp=state_path.with_suffix('.tmp');tmp.write_text(json.dumps(state)+'\n');tmp.replace(state_path)
        (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
        return report
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        while time.monotonic()-started<args.seconds and not (out/'STOP').exists():
            pending=sorted((k for k in nodes if nodes[k]['status']=='pending'),key=lambda k:(-nodes[k]['depth'],k))
            if not pending:break
            batch=pending[:args.workers]
            for identifier,status,data,children in pool.map(work,batch):
                row=nodes[identifier];row['status']=status;row['retained_graphs']=data
                if status=='split':row['children']=register(children)
                if status=='candidate':candidate=True
            print(save(),flush=True)
            if candidate:break
    print(save(),flush=True)


if __name__=='__main__':main()
