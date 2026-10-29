"""Audit coverage accounting in an adaptive completion checkpoint.

--verify-splits regenerates every reachable split and checks all child keys.
A partial checkpoint remains partial even when its accounting is consistent.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from run_treewidth_edge_checks import digest


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path);p.add_argument('--verify-splits',action='store_true')
    args=p.parse_args();out=args.directory.resolve()
    config=json.loads((out/'manifest.json').read_text());state_bytes=(out/'state.json').read_bytes();state=json.loads(state_bytes);nodes=state['nodes']
    for path,expected in config['sha256'].items():assert digest(Path(path))==expected,(path,'source changed')
    prefix_keys={}
    def identifiers(prefixes):
        if not prefixes:return set()
        missing=list(dict.fromkeys(p for p in prefixes if p not in prefix_keys))
        if missing:
            keys=subprocess.check_output([str(out/'canonical')],input='\n'.join(missing)+'\n',text=True).splitlines()
            assert len(keys)==len(missing)
            prefix_keys.update(zip(missing,keys))
        result=set()
        for prefix in prefixes:
            key=prefix_keys[prefix]
            kind,depth,*a=map(int,prefix.split());encoded=f'{kind}:{depth}:{key}'
            identifier=hashlib.sha256(encoded.encode()).hexdigest()
            assert identifier in nodes and nodes[identifier]['key']==encoded
            result.add(identifier)
        return result
    prefixes=[r['prefix'] for r in nodes.values()]
    for offset in range(0,len(prefixes),4096):identifiers(prefixes[offset:offset+4096])
    if config.get('prefixes'):
        initial=Path(config['prefixes']).read_text().splitlines()
    else:
        result=subprocess.run([str(out/'complete'),'split',str(config['kind']),str(config['split_depth'])],capture_output=True,text=True,check=True)
        initial=result.stdout.splitlines()
    assert identifiers(initial)==set(state['roots'])
    visited=set();done=split=pending=0
    def visit(identifier):
        nonlocal done,split,pending
        if identifier in visited:return nodes[identifier]['status'] in ('done','covered')
        visited.add(identifier);row=nodes[identifier]
        assert hashlib.sha256(row['key'].encode()).hexdigest()==identifier
        assert identifiers([row['prefix']])=={identifier}
        if row['status']=='done':
            assert row.get('retained_graphs',[])==[]
            if 'imported_checkpoint' in row:
                path=Path(row['imported_checkpoint']);assert digest(path)==row['checkpoint_sha256']
                record=json.loads(path.read_text());assert record['residues']==0
                assert record['input_sha256']==hashlib.sha256(row['prefix'].encode()).hexdigest()
                assert record['graphs_sha256']==digest(path.with_suffix('.g6'))
                if 'certificate_manifest' in row:
                    certificate_path=Path(row['certificate_manifest'])
                    assert digest(certificate_path)==row['certificate_manifest_sha256']
                    certificate=json.loads(certificate_path.read_text());checker=Path(certificate['source_run'])
                    assert digest(checker/'manifest.json')==certificate['source_manifest_sha256']
                    assert digest(checker/'complete')==certificate['executable_sha256']
                    for name,expected in json.loads((checker/'manifest.json').read_text())['sha256'].items():
                        assert digest(Path(name))==expected
                    assert record['log_sha256']==digest(path.with_suffix('.log'))
                    reports=[json.loads(s.removeprefix('TEMPLATE_RESULT ')) for s in path.with_suffix('.log').read_text().splitlines() if s.startswith('TEMPLATE_RESULT ')]
                    assert len(reports)==1 and all(record[k]==v for k,v in reports[0].items())
                    assert path.with_suffix('.g6').read_text()==''

            else:
                assert (out/identifier).with_suffix('.g6').read_text()==''
                text=(out/identifier).with_suffix('.log').read_text()
                record=json.loads(next(line.removeprefix('TEMPLATE_RESULT ') for line in text.splitlines() if line.startswith('TEMPLATE_RESULT ')))
                assert record['residues']==0
            done+=1;return True
        if row['status'] in ('split','covered'):
            children=set(row['children']);split+=1
            assert all(nodes[c]['depth']==row['depth']+1 for c in children)
            if args.verify_splits:
                result=subprocess.run([str(out/'complete'),'refine',str(row['depth']+1)],input=row['prefix']+'\n',capture_output=True,text=True,check=True,timeout=60)
                assert identifiers(result.stdout.splitlines())==children
            answers=[visit(child) for child in sorted(children)]
            complete=all(answers)
            if row['status']=='covered':assert complete
            return complete
        assert row['status']=='pending',row['status'];pending+=1;return False
    answers=[visit(root) for root in state['roots']]
    report={'status':'complete_supplied_family' if all(answers) else 'partial_accounting_consistent','roots':len(answers),'covered_roots':sum(answers),
            'reachable_nodes':len(visited),'completed_terminal_nodes':done,'split_nodes':split,'pending_nodes':pending,
            'splits_regenerated':args.verify_splits,'state_sha256':hashlib.sha256(state_bytes).hexdigest()}
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
