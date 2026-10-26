"""Reuse completed construction stages only with matching inputs and code."""
import hashlib
import json
from treewidth_parallel_classification import ParallelChecks
from treewidth_classification_support import source_hashes
from run_treewidth_edge_checks import ROOT,SOURCE


class CachedParallelChecks(ParallelChecks):
    def construct(self,strings,kind,args,label):
        strings=sorted(set(strings));directory=self.out/label
        expected={'kind':kind,'args':args,'workers':self.workers,
                  'input_sha256':hashlib.sha256(('\n'.join(strings)+'\n').encode()).hexdigest(),
                  'sources':source_hashes([ROOT/'scripts/nine/treewidth_parallel_classification.py',
                       ROOT/'scripts/nine/treewidth_delta_extensions.c',ROOT/'scripts/nine/treewidth_core_extensions.c',SOURCE])}
        manifest=directory/'manifest.json';summary=directory/'summary.json'
        if manifest.exists() and summary.exists():
            recorded=json.loads(manifest.read_text())
            # A completed union is independent of how its inputs were split.
            assert {k:v for k,v in recorded.items() if k!='workers'}=={k:v for k,v in expected.items() if k!='workers'},'Use a fresh output after changing a stage.'
            found=set()
            for path in sorted(directory.glob('part-*.g6')):found.update(path.read_text().splitlines())
            report=json.loads(summary.read_text());assert len(found)==report['nonisomorphic_retained']
            self.constructions.append(report);print(label,'cached',len(found),flush=True);return found
        result=super().construct(strings,kind,args,label)
        manifest.write_text(json.dumps(expected,indent=2)+'\n');return result
