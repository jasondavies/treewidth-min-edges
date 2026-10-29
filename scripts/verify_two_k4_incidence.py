"""Enumerate the two-K4 incidence model and check width-seven orders.

This finite lemma is independent of the earlier large graph classifications.
The bit-mask greedy routine proposes only; the set-based checker verifies
each full elimination order. No graph or proof data files are required.
"""
from itertools import combinations
import hashlib
import json
import struct
import time

PAIRS = list(combinations(range(4), 2))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matrices(row_degrees, column_degrees):
    rows = []
    def visit(row, remaining):
        if row == 6:
            require(not any(remaining), 'Unfinished column.')
            yield tuple(rows)
            return
        # Fixed numeric order makes the diagnostic graph hash reproducible.
        choices = sorted(sum(1 << v for v in selected)
                         for selected in combinations(range(6), row_degrees[row]))
        for mask in choices:
            after = [remaining[v] - ((mask >> v) & 1) for v in range(6)]
            if min(after) < 0 or max(after) > 5 - row:
                continue
            rows.append(mask)
            yield from visit(row + 1, after)
            rows.pop()
    yield from visit(0, column_degrees)


def graphs():
    for internal in range(4):
        base = [set() for _ in range(20)]
        def edge(graph, u, v):
            graph[u].add(v)
            graph[v].add(u)
        for side in range(2):
            for i, pair in enumerate(PAIRS):
                for cubic in pair:
                    edge(base, side * 4 + cubic, 8 + side * 6 + i)
        degrees = [2] * 6
        for i in range(internal):
            u, v = i, 5 - i
            degrees[u] = degrees[v] = 1
            edge(base, 8 + u, 8 + v)
            edge(base, 14 + u, 14 + v)
        for rows in matrices(degrees, degrees):
            graph = [row.copy() for row in base]
            for u, mask in enumerate(rows):
                for v in range(6):
                    if mask >> v & 1:
                        edge(graph, 8 + u, 14 + v)
            require([len(row) for row in graph] == [3] * 8 + [4] * 12,
                    'Unexpected candidate degrees.')
            yield internal, graph


def verify_order(graph, order):
    require(len(order) == 20 and all(type(v) is int for v in order)
            and sorted(order) == list(range(20)),
            'Invalid elimination permutation.')
    remaining = set(range(20))
    a = [row.copy() for row in graph]
    for vertex in order:
        neighbors = a[vertex] & remaining
        require(len(neighbors) <= 7, 'Order exceeds width7.')
        for u in neighbors:
            a[u].update(neighbors - {u})
        remaining.remove(vertex)


def propose_order(graph):
    """A greedy heuristic; its output is checked independently below."""
    adjacency = [sum(1 << v for v in row) for row in graph]
    remaining = (1 << 20) - 1
    order = []
    while remaining:
        best = score = None
        for vertex in range(20):
            if not remaining >> vertex & 1:
                continue
            neighbors = adjacency[vertex] & remaining
            degree = neighbors.bit_count()
            if degree > 7:
                continue
            missing_twice, pending = 0, neighbors
            while pending:
                bit = pending & -pending
                pending ^= bit
                missing_twice += (neighbors & ~adjacency[bit.bit_length() - 1] & ~bit).bit_count()
            candidate = 8 * missing_twice + degree
            if score is None or candidate < score:
                score, best = candidate, vertex
        require(best is not None, 'Greedy order search failed; no exclusion claimed.')
        order.append(best)
        neighbors = adjacency[best] & remaining
        pending = neighbors
        while pending:
            bit = pending & -pending
            pending ^= bit
            adjacency[bit.bit_length() - 1] |= neighbors ^ bit
        remaining ^= 1 << best
    return order


def verify_all():
    started = time.monotonic()
    counts = [0] * 4
    digest = hashlib.sha256()
    for internal, graph in graphs():
        verify_order(graph, propose_order(graph))
        counts[internal] += 1
        digest.update(struct.pack('<20I', *(sum(1 << v for v in row) for row in graph)))
    require(counts == [67950, 9876, 2172, 720], 'Enumeration count changed.')
    return {'status': 'verified', 'counts': counts, 'total': sum(counts),
            'graph_stream_sha256': digest.hexdigest(),
            'seconds': time.monotonic() - started}


if __name__ == '__main__':
    print(json.dumps(verify_all(), sort_keys=True))
