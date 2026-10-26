"""Parallel, verified C constructions followed by nauty isomorphism rejection."""
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
from pathlib import Path
from treewidth_classification_support import GraphChecks
from run_treewidth_edge_checks import ROOT,CC,run


class ParallelChecks(GraphChecks):
    def __init__(self,out,workers=16):
        super().__init__(out);self.workers=workers;self.constructions=[]
        self.delta=self.out/'delta';self.extend=self.out/'extend'
        run(CC+['-O3',ROOT/'scripts/nine/treewidth_delta_extensions.c','-o',self.delta])
        run(CC+['-O3',ROOT/'scripts/nine/treewidth_core_extensions.c','-o',self.extend])

    def construct(self,strings,kind,args,label):
        strings=sorted(set(strings));directory=self.out/label;directory.mkdir(exist_ok=True)
        executable,prefix=(self.delta,'DELTA_EXTENSIONS ') if kind=='delta' else (self.extend,'CORE_EXTENSIONS ')
        def work(i):
            data='\n'.join(strings[i::self.workers]);stem=directory/f'part-{i:03d}'
            if not data:
                stem.with_suffix('.g6').write_text('');return {'inputs':0,'graphs':0,'verified':0,'retained':0},set()
            p=run([executable,*args],input=data+'\n')
            row=json.loads(next(s[len(prefix):] for s in p.stderr.splitlines() if s.startswith(prefix)))
            assert row['graphs']==row['verified']+row['retained']
            graphs=p.stdout.splitlines();assert len(graphs)==row['retained']
            stem.with_suffix('.log').write_text(p.stderr)
            stem.with_suffix('.json').write_text(json.dumps(row)+'\n')
            canonical=self.canon(graphs)
            stem.with_suffix('.g6').write_text('\n'.join(sorted(canonical))+ ('\n' if canonical else ''))
            return row,canonical
        found=set();rows=[]
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            for future in as_completed([pool.submit(work,i) for i in range(self.workers)]):
                row,graphs=future.result();rows.append(row);found|=graphs
        report={'label':label,'inputs':len(strings),'graphs':sum(r['graphs'] for r in rows),
                'verified':sum(r['verified'] for r in rows),'raw_retained':sum(r['retained'] for r in rows),
                'nonisomorphic_retained':len(found),'parts':rows}
        self.constructions.append(report)
        (directory/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
        print(label,report['graphs'],'->',len(found),flush=True);return found

    def delta_closure(self,seeds,width,first,last,cap,threes,label):
        found=set(seeds);frontier=found.copy();step=0
        while frontier:
            generated=self.construct(frontier,'delta',[0,width,first,last,cap,threes],f'{label}-{step}')
            frontier=generated-found;found|=frontier;step+=1
        return found
