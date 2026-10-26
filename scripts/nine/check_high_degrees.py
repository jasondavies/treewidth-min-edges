"""Check the maximum-degree cases at 39, 40 and 41 edges.

Enumerates ALL neighborhoods of the indicated size, without degree pruning.
Every successful order from C is independently checked using Python sets.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations, islice
import json
from pathlib import Path
from classify_treewidth34 import decode
from treewidth_classification_support import append_vertex
from run_treewidth_edge_checks import ROOT, CC, SOURCE, run, encode, verify_order, digest


def check(task):
    s, degree, executable = task
    a = decode(s)
    subsets = iter(combinations(range(len(a)), degree))
    count = 0
    while batch := list(islice(subsets, 512)):
        graphs = [append_vertex(a, ns) for ns in batch]
        lines = run([executable, 8], input='\n'.join(map(encode, graphs))+'\n').stdout.splitlines()
        assert len(lines) == len(graphs)
        for b, line in zip(graphs, lines):
            if not line.startswith('YES '):
                raise RuntimeError('Candidate: ' + encode(b))
            verify_order(b, list(map(int, line.split()[1:])), 8)
        count += len(graphs)
    return count


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: assertions verify certificates.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=16)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be positive')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    exe = out/'check'
    run(CC+['-O3', '-DSTANDALONE', '-DTW_MAXN=20', SOURCE, '-o', exe])
    sources = ROOT/'sources/nine'
    cases = [(34,5,10556), (34,6,20384), (34,7,30888), (35,6,1126359)]
    report = {'status':'complete', 'cases':[]}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for edges, degree, expected in cases:
            path = sources/('treewidth34-family34.g6' if edges==34 else 'treewidth35-all-family.g6')
            count = sum(pool.map(check, ((s,degree,str(exe)) for s in path.read_text().splitlines())))
            assert count == expected
            report['cases'].append({'edges':edges+degree, 'degree':degree, 'extensions':count,
                                    'input_sha256':digest(path)})
            print(f'PASS: {edges+degree} edges, degree {degree}: {count:,} extensions', flush=True)
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
