#!/usr/bin/env python3
"""Enumerate the six nonempty quartic square-incidence types without graph data."""
import argparse
from itertools import combinations, permutations
import json

PAIRS = tuple(combinations(range(4), 2))
PERMUTATIONS = tuple(permutations(range(4)))


def edge_set(mask):
    return {pair for bit, pair in enumerate(PAIRS) if mask >> bit & 1}


def image(mask, permutation):
    edges = {tuple(sorted((permutation[u], permutation[v]))) for u, v in edge_set(mask)}
    return sum(1 << i for i, pair in enumerate(PAIRS) if pair in edges)


def canonical(mask):
    return min(image(mask, permutation) for permutation in PERMUTATIONS)


def triangle_free(mask):
    edges = edge_set(mask)
    return not any(all(pair in edges for pair in combinations(triple, 2))
                   for triple in combinations(range(4), 3))


def prefix(mask):
    """Root0, four neighbors1..4, shared corners, then private neighbors."""
    if type(mask) is not int or not 0 < mask < 64 or not triangle_free(mask):
        raise ValueError('Expected a nonempty triangle-free four-vertex incidence graph.')
    neighbors = [set() for _ in range(26)]
    def add(u, v):
        neighbors[u].add(v)
        neighbors[v].add(u)
    for v in range(1, 5):
        add(0, v)
    corner = {}
    next_vertex = 5
    for pair in PAIRS:
        if pair in edge_set(mask):
            corner[pair] = next_vertex
            for v in pair:
                add(v + 1, next_vertex)
            next_vertex += 1
    for v in range(1, 5):
        while len(neighbors[v]) < 4:
            add(v, next_vertex)
            next_vertex += 1
    # Disjoint square directions force their opposite corners adjacent.
    for first, second in combinations(corner, 2):
        if not set(first) & set(second):
            add(corner[first], corner[second])
    if any(len(row) > 4 for row in neighbors):
        raise ValueError('The necessary root exceeded degree four.')
    return [26, 5] + [sum(1 << u for u in row) for row in neighbors]


def catalogue():
    """Try all63 labeled graphs and all24 explicit permutations."""
    classes = {}
    for mask in range(1, 64):
        if mask.bit_count() > 4 or not triangle_free(mask):
            continue
        key = canonical(mask)
        classes.setdefault(key, []).append(mask)
    return [{'mask': key, 'edges': sorted(edge_set(key)), 'labeled_count': len(members),
             'prefix': prefix(key)} for key, members in sorted(classes.items())]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mask', type=int, help='Print the corresponding one-line root prefix.')
    args = parser.parse_args()
    if args.mask is None:
        print(json.dumps({'labeled_graphs_examined': 63, 'permutations_per_graph': 24,
                          'classes': catalogue()}, sort_keys=True))
    else:
        print(' '.join(map(str, prefix(args.mask))))


if __name__ == '__main__':
    main()
