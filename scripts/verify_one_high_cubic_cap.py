#!/usr/bin/env python3
"""Check the cubic-neighbor cap next to the unique high vertex of H23.

Explicit premises: the earlier classifications and the general J20 packing
reduction. Every proposed positive order is independently checked.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import struct
import time

from cubic_cap_reconstruction import (intermediate_graphs, require, verify_order,
    universal_apex, cubic_neighborhoods_independent, validate_graph)
from verify_cubic_neighbor_cap import order_proposer


def one_high_lifts(graph, stats=None):
    if stats is None:
        stats = Counter()
    validate_graph(graph)
    require(len(graph) == 20 and sorted(row.bit_count() for row in graph) == [3] * 8 + [4] * 12,
            'Expected a 3^8,4^12 intermediate graph')
    cubics = [v for v, row in enumerate(graph) if row.bit_count() == 3]
    quartics = [v for v, row in enumerate(graph) if row.bit_count() == 4]
    for restored in cubics:
        for high in quartics:
            edges = [(u, v) for v in range(20) for u in range(v)
                     if graph[u] >> v & 1 and u not in (restored, high) and v not in (restored, high)]
            for first, second in combinations(edges, 2):
                if len(set(first + second)) != 4:
                    continue
                stats['inverse_choices'] += 1
                result = list(graph) + [0, 0, (1 << restored) | (1 << high)]
                for middle, (u, v) in enumerate((first, second), 20):
                    result[u] = (result[u] & ~(1 << v)) | (1 << middle)
                    result[v] = (result[v] & ~(1 << u)) | (1 << middle)
                    result[middle] = (1 << u) | (1 << v) | (1 << 22)
                    result[22] |= 1 << middle
                result[restored] |= 1 << 22
                result[high] |= 1 << 22
                require(sorted(row.bit_count() for row in result) == [3] * 9 + [4] * 13 + [5],
                        'Wrong lifted degree profile')
                lows = [v for v, row in enumerate(result) if row.bit_count() == 3]
                mask = sum(1 << v for v in lows)
                if max((result[v] & mask).bit_count() for v in lows) > 2:
                    stats['cubic_degree'] += 1
                    continue
                if not cubic_neighborhoods_independent(result, lows):
                    stats['cubic_triangle'] += 1
                    continue
                if any((result[u] & result[v]).bit_count() > 1 for u, v in combinations(lows, 2)):
                    stats['cubic_codegree'] += 1
                    continue
                stats['targets'] += 1
                yield restored, high, (first, second), result


def verify_all(repository, propose):
    started = time.monotonic()
    intermediates, stats = Counter(), Counter()
    digest = sha256()
    for _, _, graph in intermediate_graphs(repository, intermediates):
        order = propose(graph, 7)
        if order is not None:
            verify_order(graph, order, 7)
            verify_order(universal_apex(graph), list(order) + [20], 8)
            stats['universal_apex_orders'] += 1
            continue
        stats['individual_lift_families'] += 1
        for _, _, _, result in one_high_lifts(graph, stats):
            order = propose(result, 8)
            require(order is not None, 'No width-eight order found; finite check is incomplete')
            verify_order(result, order, 8)
            stats['checked_lifts'] += 1
            digest.update(struct.pack('<23I', *result))
    return {'status': 'verified-relative-to-prior-classifications',
            'intermediate': dict(intermediates), 'statistics': dict(stats),
            'graph_stream_sha256': digest.hexdigest(), 'seconds': time.monotonic() - started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--native', action='store_true')
    args = parser.parse_args()
    with order_proposer(native=args.native) as propose:
        print(json.dumps(verify_all(args.repository, propose), sort_keys=True))


if __name__ == '__main__':
    main()
