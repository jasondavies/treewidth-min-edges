#!/usr/bin/env python3
"""Independently verify coverage of every order23 minimum counterexample.

Catalogue membership does not exclude a family. Every referenced catalogue
entry needs a separate exclusion proof. No census or canonicalizer is trusted.
"""
import argparse
from collections import Counter
import json
import lzma
from pathlib import Path

from verify_profile_refutation import Interval, require
from verify_branch_refutation import (Contradiction, choices, forbid, force,
                                     normalise, verify_reference, verify_trace)

ROOT = [23, 0] + [0] * 23
DEGREE = [5] * 12 + [4] * 11


def masks(rows):
    return tuple(sum(1 << v for v in row) for row in rows)


def verify_containment(known, possible, targets, index, permutation):
    """Every current completion maps to a completion of the target family."""
    require(type(index) is int and index in targets, 'Unknown containment target.')
    require(isinstance(permutation, list)
            and all(type(v) is int for v in permutation)
            and sorted(permutation) == list(range(23)), 'Invalid containment permutation.')
    target_known, target_possible = targets[index]
    for u, v in enumerate(permutation):
        require(DEGREE[u] == DEGREE[v], 'Containment changes a degree class.')
        mapped_known = sum(1 << permutation[w] for w in known[u])
        mapped_possible = sum(1 << permutation[w] for w in possible[u])
        require(not target_known[v] & ~mapped_known, 'Containment omits a target known edge.')
        require(not mapped_possible & ~target_possible[v], 'Containment expands target possible edges.')


def verify(data):
    version = data.get('format')
    require(version in ('order23-root-coverage-v1', 'order23-root-coverage-v2'), 'Wrong format.')
    require(data.get('prefix') == ROOT, 'Wrong order23 root.')
    require(isinstance(data.get('catalogue'), list), 'Missing catalogue.')
    targets, stats = {}, Counter()
    for index, prefix in enumerate(data['catalogue']):
        target = Interval(prefix)
        require(prefix[:2] == [23, 3] and target.upper == DEGREE,
                'Wrong target profile dimensions.')
        try:
            normalise(target.known, target.possible, DEGREE)
        except Contradiction:
            stats['locally_excluded_catalogue'] += 1
            continue
        targets[index] = (masks(target.known), masks(target.possible))

    used = set()
    def visit(known, possible, node, referenced, allow_inclusion=False):
        require(isinstance(node, list) and node, 'Invalid node.')
        try:
            normalise(known, possible, DEGREE)
        except Contradiction:
            require(node == ['x'], 'Expected local contradiction leaf.')
            stats['local_leaves'] += 1
            return
        if node[0] in ('c', 'i'):
            require(len(node) == 3, 'Invalid catalogue leaf.')
            if node[0] == 'i':
                require(allow_inclusion, 'Inclusion leaves require a v2 refinement.')
                verify_containment(known, possible, targets, node[1], node[2])
                stats['inclusion_leaves'] += 1
            else:
                verify_reference(known, possible, DEGREE, targets, node[1], node[2])
                stats['catalogue_leaves'] += 1
            referenced.add(node[1])
            return
        if node[0] == 'r':
            require(len(node) == 2, 'Invalid trace leaf.')
            verify_trace(known, possible, DEGREE, node[1])
            stats['trace_leaves'] += 1
            return
        require(node[0] == 'b' and len(node) == 3 and isinstance(node[2], list),
                'Invalid branch node.')
        vertex, children = node[1:]
        options = list(choices(known, possible, DEGREE, vertex))
        require(len(children) == len(options), 'Incomplete neighbor coverage.')
        stats['branches'] += 1
        for selected, child in zip(options, children):
            a, b = [r.copy() for r in known], [r.copy() for r in possible]
            for u in list(b[vertex] - a[vertex]):
                if u in selected:
                    force(a, b, u, vertex)
                else:
                    forbid(a, b, u, vertex)
            visit(a, b, child, referenced, allow_inclusion)

    root = Interval(ROOT)
    visit(root.known, root.possible, data['proof'], used)
    dependencies = {}
    if version == 'order23-root-coverage-v2':
        refinements = data.get('refinements')
        require(isinstance(refinements, list), 'Missing refinement list.')
        for refinement in refinements:
            require(isinstance(refinement, dict), 'Invalid refinement.')
            index = refinement.get('index')
            require(type(index) is int and index in targets, 'Unknown refinement index.')
            require(index not in dependencies, 'Duplicate refinement index.')
            family = Interval(data['catalogue'][index])
            referenced = set()
            visit(family.known, family.possible, refinement.get('proof'), referenced, True)
            dependencies[index] = referenced

    # Check every supplied refinement, including any unused one. A dependency
    # may reference a later listed refinement, but may never form a cycle.
    visiting, completed = set(), set()
    def acyclic(index):
        if index not in dependencies or index in completed:
            return
        require(index not in visiting, 'Cyclic refinement dependencies.')
        visiting.add(index)
        for target in dependencies[index]:
            acyclic(target)
        visiting.remove(index)
        completed.add(index)
    for index in dependencies:
        acyclic(index)

    terminals = set()
    expanded = set()
    def expand(index):
        if index in expanded:
            return
        expanded.add(index)
        if index in dependencies:
            for target in dependencies[index]:
                expand(target)
        else:
            terminals.add(index)
    for index in used:
        expand(index)
    result = {'counts': dict(stats), 'referenced_indices': sorted(terminals),
              'catalogue_size': len(data['catalogue'])}
    if version == 'order23-root-coverage-v2':
        result.update(initial_referenced_indices=sorted(used),
                      refined_indices=sorted(dependencies),
                      refinement_dependencies={str(i): sorted(dependencies[i])
                                               for i in sorted(dependencies)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path)
    args = parser.parse_args()
    raw = args.certificate.read_bytes()
    if args.certificate.suffix == '.xz':
        raw = lzma.decompress(raw)
    print('PASS: coverage only;', verify(json.loads(raw)))
    print('Referenced catalogue families still require separate exclusion proofs.')


if __name__ == '__main__':
    main()
