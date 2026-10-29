#!/usr/bin/env python3
"""Check order24 exclusions through a20-vertex,36-edge residual.

Premises are the written J20 packing reduction and earlier complete small-edge
classifications. All intermediate candidates are regenerated from the pinned
36-edge family; a failed order search never excludes a graph.
"""
import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import time

from cubic_cap_reconstruction import intermediate_graphs, require, verify_order
from verify_cubic_neighbor_cap import order_proposer
from verify_order24_catalogue import read_certificate, verify as verify_catalogue


def reduction(prefix, removed, suppressed):
    require(prefix[:2] == [24, 8] and len(prefix) == 26, 'Expected a full order24 high profile')
    require(isinstance(removed, list) and len(removed) == 3
            and all(type(v) is int and 0 <= v < 8 for v in removed)
            and len(set(removed)) == 3, 'Expected three distinct high deletions')
    require(type(suppressed) is int and 0 <= suppressed < 8 and suppressed not in removed,
            'Expected a fourth high vertex to suppress')
    known = [{u for u in range(24) if mask >> u & 1} for mask in prefix[2:]]
    require(all(len(known[v]) == 5 for v in range(8)), 'High neighborhoods are not exact')
    require(not any(v in known[u] for u, v in combinations(removed, 2)),
            'Deleted highs must be independent')
    deleted = set(removed)
    endpoints = known[suppressed] - deleted
    require(len(endpoints) == 2, 'Suppressed vertex must have residual degree two')
    remaining = set(range(24)) - deleted - {suppressed}
    degree = {v: (5 if v < 8 else 4) - len(known[v] & deleted) for v in remaining}
    require(sorted(degree.values()) == [3] * 8 + [4] * 12, 'Wrong residual degree profile')
    # If the endpoints were adjacent, suppression leaves20vertices/35edges
    # with minimum degree>=3, contrary to the earlier full35 classification.
    require(all(degree[v] >= 4 for v in endpoints), 'Existing-edge case needs stronger degree premises')
    u, v = sorted(endpoints)
    require(v not in known[u], 'The fixed root already has the35-edge contradiction')
    adjacency = {v: known[v] & remaining for v in remaining}
    adjacency[u].add(v)
    adjacency[v].add(u)
    highs = sorted(remaining & set(range(8)))
    require(len(highs) == 4 and all(len(adjacency[v]) == degree[v] for v in highs),
            'Surviving high rows must be exact')
    return {'high': highs, 'known': adjacency, 'degree': degree, 'endpoints': (u, v)}


def admits_high_embedding(view, graph):
    """Necessary exact-high-row embedding, exhaustive over all ordered images.

    The low-neighbor classes are compared by exact multiplicity. Ignoring
    additional low-low requirements can only retain extra candidates.
    """
    high, adjacency, degree = view['high'], view['known'], view['degree']
    low = sorted(set(adjacency) - set(high))
    classes = Counter((degree[v], sum(1 << i for i, h in enumerate(high) if h in adjacency[v]))
                      for v in low)
    target_degrees = [row.bit_count() for row in graph]
    selected = []

    def visit(depth):
        if depth == 4:
            actual = Counter((target_degrees[v], sum(1 << i for i, h in enumerate(selected)
                                                   if graph[v] >> h & 1))
                             for v in range(20) if v not in selected)
            return actual == classes
        vertex = high[depth]
        for candidate in range(20):
            if candidate in selected or target_degrees[candidate] != degree[vertex]:
                continue
            if any(bool(graph[candidate] >> selected[j] & 1) != (other in adjacency[vertex])
                   for j, other in enumerate(high[:depth])):
                continue
            selected.append(candidate)
            if visit(depth + 1):
                return True
            selected.pop()
        return False

    return visit(0)


def verify_recipes(certificate, profiles, repository, propose):
    require(certificate.get('format') == 'order24-twenty-residue-v1', 'Unknown recipe format')
    require(isinstance(certificate.get('recipes'), list) and certificate['recipes'], 'Missing recipes')
    views = {}
    for recipe in certificate['recipes']:
        require(isinstance(recipe, dict), 'Invalid recipe')
        index = recipe.get('catalogue_index')
        require(type(index) is int and 0 <= index < len(profiles) and index not in views,
                'Unknown or duplicate catalogue root')
        views[index] = reduction(profiles[index], recipe.get('deleted_highs'), recipe.get('suppressed_high'))
    statistics = Counter()
    for _, _, graph in intermediate_graphs(repository, statistics):
        order = propose(graph, 7)
        if order is not None:
            verify_order(graph, order, 7)
            statistics['checked_width7_orders'] += 1
            continue
        statistics['embedding_families'] += 1
        for index, view in views.items():
            require(not admits_high_embedding(view, graph),
                    f'Unresolved intermediate graph for catalogue root {index}')
            statistics['excluded_high_embeddings'] += 1
    return {'status': 'verified-relative-to-prior-classifications',
            'catalogue_indices': sorted(views), 'statistics': dict(statistics)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument('--recipes', type=Path, default=root / 'sources/eleven-order24-twenty-residue.json')
    parser.add_argument('--catalogue', type=Path, default=root / 'sources/eleven-order24-catalogue.bin.xz')
    parser.add_argument('--repository', type=Path, default=root)
    parser.add_argument('--native', action='store_true')
    args = parser.parse_args()
    started = time.monotonic()
    profiles = verify_catalogue(read_certificate(args.catalogue))['profiles']
    certificate = json.loads(args.recipes.read_text())
    with order_proposer(native=args.native) as propose:
        result = verify_recipes(certificate, profiles, args.repository, propose)
    result['seconds'] = time.monotonic() - started
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
