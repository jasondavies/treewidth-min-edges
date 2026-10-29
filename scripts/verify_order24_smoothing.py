#!/usr/bin/env python3
"""Check order-24 reductions using the earlier 28-edge classification.

This verifies the reductions, not the classification in proof.md, Section4.
The ordinary branch-certificate checker does not use this extra premise.
"""
import argparse
from itertools import combinations
import json
from pathlib import Path

from verify_order24_catalogue import read_certificate, verify as verify_catalogue


def require(condition, message):
    if not condition:
        raise ValueError(message)


def initial(prefix):
    """Validate an incidence root with all eight high neighborhoods fixed."""
    require(isinstance(prefix, (list, tuple)) and len(prefix) == 26,
            'Expected a 24-vertex prefix.')
    require(all(type(value) is int for value in prefix),
            'Prefix entries must be integers.')
    require(tuple(prefix[:2]) == (24, 8),
            'Expected order 24 with eight complete high neighborhoods.')
    adjacency = list(prefix[2:])
    require(all(0 <= mask < 1 << 24 and not (mask >> v & 1)
                for v, mask in enumerate(adjacency)), 'Invalid adjacency mask.')
    require(all(bool(adjacency[u] >> v & 1) == bool(adjacency[v] >> u & 1)
                for u in range(24) for v in range(24)), 'Asymmetric prefix.')
    require(all(adjacency[v].bit_count() == 5 for v in range(8)),
            'Every high neighborhood must be complete.')
    require(all(not (adjacency[v] & ~255) and adjacency[v].bit_count() <= 2
                for v in range(8, 24)),
            'Expected only high incidences, at most two per low vertex.')
    return adjacency


def delete(adjacency, vertex):
    degree = adjacency[vertex].bit_count()
    for u in range(24):
        adjacency[u] &= ~(1 << vertex)
    adjacency[vertex] = 0
    return degree


def eliminate(adjacency, vertex):
    """Return a safe upper bound on the edge-count change."""
    neighbors = [u for u in range(24) if adjacency[vertex] >> u & 1]
    require(len(neighbors) <= 2, 'An eliminated high has degree greater than two.')
    delta = -len(neighbors)
    if len(neighbors) == 2:
        u, v = neighbors
        if not (adjacency[u] >> v & 1):
            # This edge may already exist among the unknown low edges.
            # Charging a new edge is conservative in either case.
            delta += 1
            adjacency[u] |= 1 << v
            adjacency[v] |= 1 << u
    delete(adjacency, vertex)
    return delta


def check_recipe(prefix, recipe):
    adjacency = initial(prefix)
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
    trajectory = [edges]
    for vertex in order:
        edges += eliminate(adjacency, vertex)
        trajectory.append(edges)
    require(edges <= 28, 'The reduction does not reach at most 28 edges.')
    require(all(adjacency[v] == 0 for v in range(8)), 'Some high vertex remains.')
    # All sixteen lows remain. Each originally has at least two low neighbors,
    # and deleting/eliminating highs never removes an edge between two lows.
    return {'edges_upper': edges, 'width_lower': 7,
            'nonisolated_vertices_lower': 16, 'edge_upper_trajectory': trajectory}


def verify(certificate, profiles):
    """Check recipes against an independently verified catalogue."""
    require(isinstance(certificate, dict)
            and certificate.get('format') == 'order24-high-smoothing-v1',
            'Unknown smoothing certificate format.')
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
                        default=root / 'sources/eleven-order24-smoothing.json')
    parser.add_argument('--catalogue', type=Path,
                        default=root / 'sources/eleven-order24-catalogue.bin.xz')
    args = parser.parse_args()
    profiles = verify_catalogue(read_certificate(args.catalogue))['profiles']
    result = verify(json.loads(args.certificate.read_text()), profiles)
    print(f"Verified {len(result['covered_indices'])} order-24 reductions.")
    print('Covered catalogue indices:', ' '.join(map(str, result['covered_indices'])))
    print('Extra premise: the K8/F classification in proof.md, Section 4.')
    print('Other catalogue profiles require separate proofs.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
