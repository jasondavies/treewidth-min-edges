"""Check quartic girth-five graphs using GENREG or a saved graph6 family.

Every positive C elimination order is independently verified with Python
sets. Saved-family mode does not establish enumeration completeness.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import subprocess
import time

from common import CC, SOURCE, run, encode, verify_order, digest, decode


def validate(a):
    n = len(a)
    assert all(len(ns) == 4 for ns in a)
    assert all(not a[v] & a[w] for v in range(n) for w in a[v])
    assert all(len(a[v] & a[w]) <= 1 for v in range(n) for w in range(v))
    reached, pending = set(), {0}
    while pending:
        v = pending.pop()
        reached.add(v)
        pending.update(a[v] - reached)
    assert len(reached) == n


def shortcode(data, n):
    previous = bytearray(2 * n)
    offset = 0
    found = []
    while offset < len(data):
        prefix = data[offset]
        offset += 1
        assert prefix <= 2 * n and (found or prefix == 0)
        length = 2 * n - prefix
        assert offset + length <= len(data)
        previous[prefix:] = data[offset:offset + length]
        offset += length
        a = [set() for _ in range(n)]
        v = 0
        for value in previous:
            while v < n and len(a[v]) == 4:
                v += 1
            w = value - 1
            assert v < n and v < w < n and w not in a[v] and len(a[w]) < 4
            a[v].add(w)
            a[w].add(v)
        validate(a)
        found.append(encode(a))
    return found


def check(task):
    strings, executable, width = task
    answers = run([executable, width], input='\n'.join(strings) + '\n').stdout.splitlines()
    assert len(answers) == len(strings)
    candidates = []
    for s, answer in zip(strings, answers):
        if answer == 'NO':
            candidates.append(s)
        else:
            assert answer.startswith('YES ')
            verify_order(decode(s), list(map(int, answer.split()[1:])), width)
    return candidates


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: assertions verify certificates.')
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--genreg', type=Path, help='unmodified GENREG executable')
    inputs.add_argument('--graphs', type=Path, help='saved graph6 family')
    parser.add_argument('--vertices', type=int, choices=(23, 24), default=23)
    parser.add_argument('--workers', type=int, default=16)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be positive')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    if args.genreg:
        with (out / 'graphs.scd').open('wb') as stream, (out / 'generator.log').open('w') as log:
            subprocess.run([str(args.genreg.resolve()), str(args.vertices), '4', '5',
                            '-s', 'stdout'], stdout=stream, stderr=log, check=True)
        graphs = shortcode((out / 'graphs.scd').read_bytes(), args.vertices)
        input_path = args.genreg
    else:
        graphs = args.graphs.read_text().splitlines()
        for s in graphs:
            a = decode(s)
            assert len(a) == args.vertices
            validate(a)
        input_path = args.graphs
    expected = {23: 3917, 24: 123859}[args.vertices]
    assert len(graphs) == expected and len(set(graphs)) == expected
    (out / 'graphs.g6').write_text('\n'.join(graphs) + '\n')
    print('Checking', len(graphs), 'graphs', flush=True)
    checker = out / 'check'
    run(CC + ['-O3', '-DSTANDALONE', f'-DTW_MAXN={args.vertices}', SOURCE, '-o', checker])
    candidates, verified = [], 0
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        tasks = [(graphs[i:i + 128], str(checker), 9) for i in range(0, len(graphs), 128)]
        for task, negative in zip(tasks, pool.map(check, tasks)):
            candidates += negative
            verified += len(task[0]) - len(negative)
    (out / 'candidates.g6').write_text('\n'.join(candidates) + ('\n' if candidates else ''))
    report = {'status': 'candidates' if candidates else 'all_verified',
              'input_mode': 'generated' if args.genreg else 'saved',
              'vertices': args.vertices, 'edges': 2 * args.vertices,
              'graphs': len(graphs), 'verified_width_nine': verified, 'candidates': len(candidates),
              'seconds': time.monotonic() - start,
              'source_sha256': {str(p): digest(p) for p in [Path(__file__), SOURCE, input_path]}}
    (out / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], verified, 'verified;', len(candidates), 'candidates', flush=True)


if __name__ == '__main__':
    main()
