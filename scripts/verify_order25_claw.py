#!/usr/bin/env python3
"""Check the small weighted-packing and inverse classifications for the claw.

Premises are stated in proof-eleven-order25-claw.md. No order-search failure
or archived 52-edge classification is used.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from cubic_cap_reconstruction import (FAMILY_SHA256, decode_graph6,
    inverse_triangles, require, verify_order)
from order25_profiles import enumerate_profiles
from verify_profile_refutation import Interval


def partitions(total, maximum_parts, least=1):
    if total == 0:
        yield ()
    if maximum_parts:
        for size in range(least, total + 1):
            for tail in partitions(total - size, maximum_parts - 1, size):
                yield (size,) + tail


def cubic_types():
    """All 12-vertex paths/even cycles >=6 with at most three path components."""
    for cycles in ((), (6,), (8,), (10,), (12,), (6, 6)):
        for paths in partitions(12 - sum(cycles), 3):
            graph = [0] * 12
            at = 0
            for size in paths + cycles:
                for v in range(at, at + size - 1):
                    graph[v] |= 1 << (v + 1)
                    graph[v + 1] |= 1 << v
                if at >= sum(paths):
                    graph[at] |= 1 << (at + size - 1)
                    graph[at + size - 1] |= 1 << at
                at += size
            require(at == 12, 'Wrong cubic-type order')
            yield paths, cycles, graph


def conflict_covers(graph):
    """Exhaustively hit every eligible triple, respecting all degree capacities.

A returned cover need not be maximal. Any actual full cover contains one of
these returned partial covers. The final check verifies that every surviving
partial cover already saturates all capacities.
"""
    square = []
    for v, row in enumerate(graph):
        reach = row
        for u in range(12):
            if row >> u & 1:
                reach |= graph[u]
        square.append(reach & ~(1 << v))
    edges = [(u, v) for u in range(12) for v in range(u + 1, 12)
             if not square[u] >> v & 1]
    index = {edge: i for i, edge in enumerate(edges)}
    incident = [sum(1 << i for i, edge in enumerate(edges) if v in edge)
                for v in range(12)]
    capacity = [3 - row.bit_count() for row in graph]
    clauses = []
    for triple in combinations(range(12), 3):
        if sum(1 + graph[v].bit_count() for v in triple) < 7:
            continue
        if any(square[u] >> v & 1 for u, v in combinations(triple, 2)):
            continue
        clauses.append(sum(1 << index[pair] for pair in combinations(triple, 2)))
    solutions = []
    nodes = 0

    def visit(chosen, allowed, caps):
        nonlocal nodes
        nodes += 1
        selected, size = 0, 4
        for clause in clauses:
            if chosen & clause:
                continue
            options = allowed & clause
            if not options:
                return
            if options.bit_count() < size:
                selected, size = options, options.bit_count()
        if not selected:
            solutions.append([edge for i, edge in enumerate(edges) if chosen >> i & 1])
            return
        # Partition by the first selected currently available edge in this
        # clause: earlier edges are absent, this edge is present.
        while selected:
            bit = selected & -selected
            selected ^= bit
            allowed &= ~bit
            u, v = edges[bit.bit_length() - 1]
            child_caps = caps.copy()
            child_caps[u] -= 1
            child_caps[v] -= 1
            require(child_caps[u] >= 0 and child_caps[v] >= 0, 'Capacity underflow')
            child_allowed = allowed
            if child_caps[u] == 0:
                child_allowed &= ~incident[u]
            if child_caps[v] == 0:
                child_allowed &= ~incident[v]
            visit(chosen | bit, child_allowed, child_caps)

    visit(0, (1 << len(edges)) - 1, capacity)
    return solutions, nodes


def verify_weighted_packing():
    types = nodes = exceptions = 0
    for paths, cycles, graph in cubic_types():
        types += 1
        solutions, count = conflict_covers(graph)
        nodes += count
        for solution in solutions:
            counts = Counter(v for edge in solution for v in edge)
            require(all(counts[v] == 3 - graph[v].bit_count() for v in range(12)),
                    'A partial cover has unexamined supersets')
            require(paths == () and cycles == (6, 6), 'Unexpected packing obstruction')
            expected = [(v, v + 3) for v in (0, 1, 2, 6, 7, 8)]
            require(solution == expected, 'Unexpected two-cycle conflict cover')
            exceptions += 1
    require(exceptions == 1, 'Expected exactly one saturated obstruction')
    # The three attachment vertices are made a clique, which is harmless
    # while eliminating only C. This checks the claimed width-four order.
    block = [0] * 9
    for v in range(6):
        for u in ((v + 1) % 6, 6 + v % 3):
            block[v] |= 1 << u
            block[u] |= 1 << v
    for u, v in combinations(range(6, 9), 2):
        block[u] |= 1 << v
        block[v] |= 1 << u
    verify_order(block, [0, 3, 1, 4, 2, 5, 6, 7, 8], 4)
    return {'cubic_types': types, 'cover_nodes': nodes, 'saturated_exceptions': exceptions}


def verify_prior_inverses(repository):
    """Check every necessary three-triangle inverse of the earlier 36 family."""
    raw = (Path(repository) / 'sources/nine/treewidth36-family.g6').read_bytes()
    require(sha256(raw).hexdigest() == FAMILY_SHA256, 'Wrong prior 36-edge family')
    stats = Counter()
    for code in raw.decode('ascii').splitlines():
        graph = decode_graph6(code)
        if len(graph) != 18:
            continue
        degree = [row.bit_count() for row in graph]
        cubic_count = degree.count(3)
        if cubic_count not in (3, 4, 5):
            continue
        stats[f'bases_c{cubic_count}'] += 1
        high = sum(1 << v for v in range(18) if degree[v] == 5)
        eligible = [v for v in range(18) if degree[v] >= 4]
        triangles = [triangle for triangle in combinations(eligible, 3)
                     if any(degree[v] == 5 for v in triangle)
                     and all(graph[u] >> v & 1 for u, v in combinations(triangle, 2))]
        masks = {triangle: sum(1 << v for v in triangle) for triangle in triangles}
        for selected in combinations(triangles, 3):
            a, b, c = (masks[triangle] for triangle in selected)
            if a & b or a & c or b & c or high & ~(a | b | c):
                continue
            stats['inverse_choices'] += 1
            result = inverse_triangles(graph, selected)
            cubics = [v for v, row in enumerate(result) if row.bit_count() == 3]
            require(len(result) == 21 and len(cubics) == 12
                    and all(row.bit_count() in (3, 4) for row in result),
                    'Wrong inverse degree profile')
            mask = sum(1 << v for v in cubics)
            require(any((result[v] & mask).bit_count() > 2 for v in cubics),
                    'An inverse survives the cubic maximum-degree restriction')
            stats['cubic_degree_contradictions'] += 1
    return dict(stats)


def verify_claw_prefix(prefix):
    state = Interval(prefix)
    require(prefix[0] == 25 and state.upper == [5] * 4 + [4] * 21,
            'Expected the order25 degree profile')
    high = set(range(4))
    require(all(state.known[v] == state.possible[v] and len(state.known[v]) == 5
                for v in high), 'High neighborhoods must be exact')
    centers = [v for v in high if len(state.known[v] & high) == 3]
    require(len(centers) == 1, 'Expected a high claw')
    center = centers[0]
    require(all(state.known[v] & high == {center} for v in high - {center}),
            'Expected three independent high leaves')
    require(all(len(state.known[v] & high) <= 1 for v in range(4, 25)),
            'The claw recipe requires private low attachments')
    return {'center': center, 'leaves': sorted(high - {center})}


def verify(prefix, repository):
    started = time.monotonic()
    recipe = verify_claw_prefix(prefix)
    return {'status': 'verified-relative-to-stated-earlier-premises',
            'recipe': recipe, 'packing': verify_weighted_packing(),
            'inverses': verify_prior_inverses(repository),
            'seconds': time.monotonic() - started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    prefix = enumerate_profiles()[tuple(map(int, '001011'))]
    print(json.dumps(verify(prefix, args.repository), sort_keys=True))


if __name__ == '__main__':
    main()
