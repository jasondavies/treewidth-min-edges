#!/usr/bin/env python3
"""Check high-vertex smoothing using the complete earlier full 34/35-edge classifications."""
import argparse
from itertools import combinations
import json
from pathlib import Path

from verify_order24_catalogue import read_certificate, verify as verify_catalogue
from verify_order24_smoothing import initial, delete, eliminate, require


def check_recipe(prefix, recipe):
    adjacency = initial(prefix)
    require(isinstance(recipe, dict), 'Invalid recipe.')
    deleted, order = recipe.get('delete'), recipe.get('eliminate')
    require(isinstance(deleted, list) and isinstance(order, list)
            and len(deleted) == 3 and len(order) == 2,
            'Expected three high deletions and two high eliminations.')
    operations = deleted + order
    require(all(type(v) is int and 0 <= v < 8 for v in operations)
            and len(set(operations)) == 5, 'Operations must use five distinct highs.')
    require(all(not (adjacency[u] >> v & 1) for u, v in combinations(deleted, 2)),
            'The three deleted highs must be independent.')
    lower = [5] * 8 + [4] * 16
    live = set(range(24))
    edges = 52
    for vertex in deleted:
        for u in live:
            if adjacency[vertex] >> u & 1:
                lower[u] -= 1
        edges -= delete(adjacency, vertex)
        live.remove(vertex)
    require(edges == 37, 'The independent high deletions must leave 37 edges.')
    trajectory = [edges]
    for vertex in order:
        # High neighborhoods are exact. Debit every removed incidence and
        # give no degree credit for the possibly already-present fill edge.
        for u in live:
            if adjacency[vertex] >> u & 1:
                lower[u] -= 1
        edges += eliminate(adjacency, vertex)
        live.remove(vertex)
        trajectory.append(edges)
    require(edges <= 35, 'The smoothing does not reach at most 35 edges.')
    require(len(live) == 19, 'Expected exactly nineteen surviving vertices.')
    minimum_degree = min(lower[v] for v in live)
    require(minimum_degree >= 3, 'The full 35-edge classification needs minimum degree three.')
    nonisolated = len(live)
    return {'edges_upper': edges, 'width_lower': 8,
            'nonisolated_vertices_lower': nonisolated,
            'minimum_degree_lower': minimum_degree,
            'edge_upper_trajectory': trajectory}


def verify(certificate, profiles):
    require(isinstance(certificate, dict)
            and certificate.get('format') == 'order24-high-smoothing35-v1',
            'Unknown smoothing certificate format.')
    cases = certificate.get('cases')
    require(isinstance(cases, list), 'Missing smoothing cases.')
    seen, results = set(), []
    for case in cases:
        require(isinstance(case, dict), 'Invalid case.')
        index = case.get('catalogue_index')
        require(type(index) is int and 0 <= index < len(profiles), 'Invalid catalogue index.')
        require(index not in seen, 'Duplicate catalogue index.')
        results.append({'catalogue_index': index, **check_recipe(profiles[index], case)})
        seen.add(index)
    return {'covered_indices': sorted(seen), 'cases': results}


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path, nargs='?',
                        default=root / 'sources/eleven-order24-smoothing35.json')
    parser.add_argument('--catalogue', type=Path,
                        default=root / 'sources/eleven-order24-catalogue.bin.xz')
    args = parser.parse_args()
    profiles = verify_catalogue(read_certificate(args.catalogue))['profiles']
    result = verify(json.loads(args.certificate.read_text()), profiles)
    print(json.dumps(result, sort_keys=True))
    print('Extra premises: the full 34- and 35-edge classifications in proof.md and proofs/nine-41.md.')
    print('This verifies only the reported order-24 profiles.')


if __name__ == '__main__':
    main()
