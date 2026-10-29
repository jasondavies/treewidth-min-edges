#!/usr/bin/env python3
"""Check order-24 reductions using the earlier 29-edge classification.

Extra premise: no graph on sixteen vertices with minimum degree at least
three, at most 29 edges, and treewidth at least seven exists. This is a
consequence of the 28/29-edge classifications in proof.md and proof-nine.md.
This command checks reductions; it does not rerun those classifications.
"""
import argparse
from itertools import combinations
import json
from pathlib import Path

from verify_order24_catalogue import read_certificate, verify as verify_catalogue
from verify_order24_smoothing import delete, initial, require


def eliminate(adjacency, vertex):
    """Eliminate a high vertex, conservatively charging all unknown fills."""
    neighbors = [u for u in range(24) if adjacency[vertex] >> u & 1]
    require(len(neighbors) < 7,
            'Elimination does not preserve the treewidth-seven lower bound.')
    delta = -len(neighbors)
    for u, v in combinations(neighbors, 2):
        if not (adjacency[u] >> v & 1):
            delta += 1
            adjacency[u] |= 1 << v
            adjacency[v] |= 1 << u
    delete(adjacency, vertex)
    return delta, len(neighbors)


def check_recipe(prefix, recipe):
    adjacency = initial(prefix)
    # Every low has total degree four. Its induced-low degree is therefore
    # at least three, and no operation below removes an original low edge.
    require(all(adjacency[v].bit_count() <= 1 for v in range(8, 24)),
            'The induced low graph is not guaranteed minimum degree three.')
    require(isinstance(recipe, dict), 'Invalid recipe.')
    deleted, order = recipe.get('delete'), recipe.get('eliminate')
    require(isinstance(deleted, list) and isinstance(order, list)
            and len(deleted) == len(order) == 4,
            'Expected four deletions and four eliminations.')
    require(all(type(v) is int for v in deleted + order)
            and sorted(deleted + order) == list(range(8)),
            'The operations must partition the eight high vertices.')
    require(all(not (adjacency[u] >> v & 1)
                for u, v in combinations(deleted, 2)),
            'The deleted high vertices must be independent.')
    edges = 52
    for vertex in deleted:
        edges -= delete(adjacency, vertex)
    require(edges == 32, 'The four high deletions must leave 32 edges.')
    trajectory, degrees = [edges], []
    for vertex in order:
        delta, degree = eliminate(adjacency, vertex)
        edges += delta
        trajectory.append(edges)
        degrees.append(degree)
    require(edges <= 29, 'The reduction does not reach at most 29 edges.')
    require(all(adjacency[v] == 0 for v in range(8)), 'Some high vertex remains.')
    return {'edges_upper': edges, 'width_lower': 7, 'vertices': 16,
            'minimum_degree_lower': 3, 'elimination_degrees': degrees,
            'edge_upper_trajectory': trajectory}


def verify(certificate, profiles):
    """Check recipes against an independently verified order-24 catalogue."""
    require(isinstance(certificate, dict)
            and certificate.get('format') == 'order24-high-smoothing29-v1',
            'Unknown 29-edge smoothing format.')
    cases = certificate.get('cases')
    require(isinstance(cases, list), 'Missing smoothing cases.')
    seen, results = set(), []
    for case in cases:
        require(isinstance(case, dict), 'Invalid case.')
        index = case.get('catalogue_index')
        require(type(index) is int and 0 <= index < len(profiles),
                'Invalid catalogue index.')
        require(index not in seen, 'Duplicate catalogue index.')
        results.append({'catalogue_index': index,
                        **check_recipe(profiles[index], case)})
        seen.add(index)
    return {'covered_indices': sorted(seen), 'cases': results}


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path, nargs='?',
                        default=root / 'sources/eleven-order24-smoothing29.json')
    parser.add_argument('--catalogue', type=Path,
                        default=root / 'sources/eleven-order24-catalogue.bin.xz')
    args = parser.parse_args()
    profiles = verify_catalogue(read_certificate(args.catalogue))['profiles']
    result = verify(json.loads(args.certificate.read_text()), profiles)
    print(f"Verified {len(result['covered_indices'])} order-24 reductions.")
    print('Covered catalogue indices:', ' '.join(map(str, result['covered_indices'])))
    print('Extra premise: the 28/29-edge classifications in proof.md and proof-nine.md.')
    print('Classification completeness and other profiles are not checked by this command.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
