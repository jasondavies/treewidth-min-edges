#!/usr/bin/env python3
"""Enumerate the forty necessary order-25 high-incidence profiles without nauty.

Each of the six high-vertex pairs has three states: no edge, an edge,
or an edge with one shared degree-four neighbor. Try all 3**6 assignments
and all 4! permutations. The accompanying proof justifies completeness.
"""
import argparse
from itertools import combinations, permutations, product
from pathlib import Path

PAIRS = tuple(combinations(range(4), 2))
PERMUTATIONS = tuple(permutations(range(4)))
PERMUTED_INDICES = tuple(tuple(PAIRS.index(tuple(sorted((p[u], p[v])))) for u, v in PAIRS)
                         for p in PERMUTATIONS)


def canonical(colors):
    return min(tuple(colors[i] for i in indices) for indices in PERMUTED_INDICES)


def make_prefix(colors):
    known = [set() for _ in range(25)]
    next_vertex = 4
    for (u, v), color in zip(PAIRS, colors):
        if color:
            known[u].add(v)
            known[v].add(u)
        if color == 2:
            known[u].add(next_vertex)
            known[v].add(next_vertex)
            known[next_vertex] |= {u, v}
            next_vertex += 1
    if any(len(known[v]) > 5 for v in range(4)):
        return None
    for v in range(4):
        for _ in range(5 - len(known[v])):
            if next_vertex >= 25:
                return None
            known[v].add(next_vertex)
            known[next_vertex].add(v)
            next_vertex += 1
    for v, neighbors in enumerate(known):
        triangles = sum(w in known[u] for u, w in combinations(sorted(neighbors), 2))
        if triangles > (4 if v < 4 else 1):
            return None
        if v < 4:
            for u, w in combinations(sorted(neighbors & set(range(4))), 2):
                if w not in known[u]:
                    if any(y in known[x] for x, y in combinations(sorted(neighbors - {u, w}), 2)):
                        return None
    return [25, 4] + [sum(1 << u for u in neighbors) for neighbors in known]


def enumerate_profiles():
    representatives = {}
    for colors in product(range(3), repeat=6):
        if make_prefix(colors) is not None:
            key = canonical(colors)
            representatives[key] = make_prefix(key)
    return dict(sorted(representatives.items()))


def profile_key(prefix):
    """Validate a full high-incidence root and identify its isomorphism class."""
    if (not isinstance(prefix, list) or len(prefix) != 27 or prefix[:2] != [25, 4]
            or any(type(x) is not int for x in prefix)):
        raise ValueError('Expected an order-25 high-incidence root.')
    masks = prefix[2:]
    if any(a < 0 or a >= 1 << 25 for a in masks):
        raise ValueError('Invalid adjacency mask.')
    known = [{u for u in range(25) if a >> u & 1} for a in masks]
    for v in range(25):
        if v in known[v] or any(v not in known[u] for u in known[v]):
            raise ValueError('Root is not a simple undirected graph.')
        if v < 4:
            if len(known[v]) != 5:
                raise ValueError('High neighborhood is incomplete.')
        elif not known[v] <= set(range(4)) or len(known[v]) > 2:
            raise ValueError('Root contains extra low edges or a forbidden high attachment.')
    colors = []
    for u, v in PAIRS:
        shared = len((known[u] & known[v]) - set(range(4)))
        if shared > 1 or (shared and v not in known[u]):
            raise ValueError('Invalid shared-low attachment.')
        colors.append(int(v in known[u]) + shared)
    key = canonical(colors)
    if make_prefix(key) is None:
        raise ValueError('Profile violates the elementary necessary restrictions.')
    return key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Write the canonical prefixes, one per line.')
    parser.add_argument('--key', help='Select one six-digit ternary profile code.')
    args = parser.parse_args()
    profiles = enumerate_profiles()
    if args.key is not None:
        if len(args.key) != 6 or any(c not in '012' for c in args.key):
            parser.error('--key must be six digits from 0, 1, 2')
        key = tuple(map(int, args.key))
        if key not in profiles:
            parser.error('the requested key is not a canonical necessary profile')
        profiles = {key: profiles[key]}
    if args.output:
        args.output.write_text(''.join(' '.join(map(str, p)) + '\n' for p in profiles.values()))
    print(f'{len(profiles)} selected profiles from all 729 labeled assignments and all 24 high-vertex permutations.')
    print('This proves coverage of the necessary order-25 roots, not their exclusion.')


if __name__ == '__main__':
    main()
