"""Check the remaining case in the proof that treewidth nine needs >=39 edges.

The mathematical reduction depends on the earlier 28-edge classification
and f(8)=34. This script checks only the one-graph girth-five enumeration
and its width-eight upper certificate; it does not rerun those dependencies.
"""
from datetime import date
import json
from pathlib import Path
import shlex
from tempfile import TemporaryDirectory

from run_treewidth_edge_checks import (
    CC, GENG, ROOT, SOURCE, digest, encode, run, verify_order,
)


def decode(s):
    n = ord(s[0]) - 63
    assert n == 19
    assert len(s) == 1 + (n * (n - 1) // 2 + 5) // 6
    assert all(63 <= ord(c) <= 126 for c in s)
    a = [set() for _ in range(n)]
    bit = 0
    for j in range(1, n):
        for i in range(j):
            if (ord(s[1 + bit // 6]) - 63) >> (5 - bit % 6) & 1:
                a[i].add(j)
                a[j].add(i)
            bit += 1
    assert encode(a) == s
    return a


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: assertions are verification steps.')
    dependencies = [ROOT / 'sources/results.json',
                    ROOT / 'sources/uniqueness.json']
    flags = shlex.split(run(['pkg-config', '--cflags', '--libs', 'nauty']).stdout)
    result = {
        'date': date.today().isoformat(), 'lower_bound_for_treewidth_nine': 39,
        'dependencies_sha256': {str(p.relative_to(ROOT)): digest(p) for p in dependencies},
        'source_sha256': {str(p): digest(p) for p in [Path(__file__), SOURCE, GENG]},
        'compiler': run(CC + ['--version']).stdout.splitlines()[0],
        'nauty_version': run(['pkg-config', '--modversion', 'nauty']).stdout.strip(),
    }
    with TemporaryDirectory(prefix='tw9-girth5-') as directory:
        tmp = Path(directory)
        geng, checker = tmp / 'geng', tmp / 'checker'
        run(CC + ['-O3', GENG, *flags, '-o', geng])
        run(CC + ['-O3', '-DSTANDALONE', '-DTW_MAXN=19', SOURCE, '-o', checker])
        arguments = ['-c', '-t', '-f', '-d4', '-D4', '19', '38:38']
        generated = run([geng, *arguments])
        graphs = generated.stdout.splitlines()
        assert len(graphs) == 1
        a = decode(graphs[0])
        assert all(len(ns) == 4 for ns in a)
        assert sum(map(len, a)) == 76
        # No triangle, and no pair of vertices with two common neighbors.
        assert all(not (a[u] & a[v]) for u in range(19) for v in a[u])
        assert all(len(a[u] & a[v]) <= 1 for u in range(19) for v in range(u))
        reached, todo = set(), {0}
        while todo:
            v = todo.pop()
            reached.add(v)
            todo.update(a[v] - reached)
        assert len(reached) == 19
        answer = run([checker, '8'], input=graphs[0] + '\n').stdout.split()
        assert answer[0] == 'YES'
        order = list(map(int, answer[1:]))
        width = verify_order(a, order, 8)
        result.update(generator_arguments=arguments, generator_log=generated.stderr,
                      generated_count=1, graph6=graphs[0], width_eight_order=order,
                      verified_order_width=width)
    destination = ROOT / 'sources/nine/treewidth-nine-girth5.json'
    destination.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: exactly one connected quartic 19-vertex girth-five graph;')
    print('its width-eight order passes the independent Python verifier.')
    print('Together with the mathematical reduction and earlier dependencies: f(9) >= 39.')


if __name__ == '__main__':
    main()
