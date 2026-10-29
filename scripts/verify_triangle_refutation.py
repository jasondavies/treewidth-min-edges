#!/usr/bin/env python3
"""Check coverage and supplied exclusions of the quartic triangle root.

Premises are the earlier numerical edge minima and the written minimum-order
reduction. A missing catalogue case produces exit status 2, not a proof of the
triangle exclusion. Refutations are pinned to the original v1 rules so a later
rule assuming triangle-freeness cannot prove its own premise. Neither nauty nor
archived completion logs are consulted.
"""
import argparse
from collections import Counter
import json
import lzma
from pathlib import Path

from verify_profile_refutation import Interval, require
from verify_branch_refutation import (
    Contradiction, choices, forbid, force, normalise, verify_certificate,
    verify_reference, verify_trace,
)

TRIANGLE_ROOT = [26, 3, 30, 101, 387, 1, 1, 2, 2, 4, 4] + [0] * 17


def load_json(path):
    data = path.read_bytes()
    if path.suffix == '.xz':
        data = lzma.decompress(data)
    return json.loads(data)


def verify_coverage(certificate):
    require(certificate.get('format') == 'triangle-root-coverage-v1', 'Wrong coverage format.')
    require(certificate['prefix'] == TRIANGLE_ROOT, 'Wrong triangle root.')
    root = Interval(TRIANGLE_ROOT)
    targets = {}
    stats = Counter()
    for index, prefix in enumerate(certificate['catalogue']):
        target = Interval(prefix)
        require(target.upper == [4] * 26, 'Wrong target degrees.')
        normalise(target.known, target.possible, target.upper)
        targets[index] = tuple(tuple(sum(1 << v for v in row) for row in graph)
                               for graph in (target.known, target.possible))

    def visit(known, possible, node):
        require(isinstance(node, list) and node, 'Invalid coverage node.')
        try:
            normalise(known, possible, [4] * 26)
        except Contradiction:
            require(node == ['x'], 'Expected a local contradiction.')
            stats['local'] += 1
            return
        if node[0] == 'c':
            require(len(node) == 3, 'Invalid catalogue node.')
            verify_reference(known, possible, [4] * 26, targets, node[1], node[2])
            stats[f'catalogue{node[1]}'] += 1
            return
        if node[0] == 'r':
            require(len(node) == 2, 'Invalid trace node.')
            verify_trace(known, possible, [4] * 26, node[1])
            stats['traces'] += 1
            return
        require(node[0] == 'b' and len(node) == 3 and isinstance(node[2], list),
                'Invalid branch node.')
        vertex = node[1]
        options = list(choices(known, possible, [4] * 26, vertex))
        require(len(options) == len(node[2]), 'Incomplete neighbor branch.')
        stats['branches'] += 1
        for selected, child in zip(options, node[2]):
            a, b = [row.copy() for row in known], [row.copy() for row in possible]
            for u in list(b[vertex] - a[vertex]):
                if u in selected:
                    force(a, b, u, vertex)
                else:
                    forbid(a, b, u, vertex)
            visit(a, b, child)

    visit(root.known, root.possible, certificate['proof'])
    return dict(stats)


def verify_bundle(coverage, bundle):
    stats = verify_coverage(coverage)
    require(bundle.get('format') == 'triangle-certified-prefixes-v1', 'Wrong refutation bundle.')
    done = set()
    for case in bundle['cases']:
        index = case['index']
        require(type(index) is int and 0 <= index < len(coverage['catalogue']) and index not in done,
                'Invalid catalogue index.')
        require(case['certificate'].get('format') == '52-edge-branch-refutation-v1',
                'Triangle premise refutations must use the original v1 rules.')
        verify_certificate(case['certificate'], coverage['catalogue'][index])
        done.add(index)
    needed = {int(key[9:]) for key in stats if key.startswith('catalogue')}
    return stats, done, sorted(needed - done)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('coverage', type=Path)
    parser.add_argument('refutations', type=Path)
    args = parser.parse_args()
    stats, done, missing = verify_bundle(load_json(args.coverage), load_json(args.refutations))
    print('Verified triangle-root coverage:', stats)
    print(f'Verified {len(done)} explicit prefix refutations.')
    if missing:
        print(f'PARTIAL: missing required catalogue cases {missing}; triangle exclusion is NOT complete.')
        return 2
    print('PASS: no minimum-order 52-edge quartic counterexample contains a triangle.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
