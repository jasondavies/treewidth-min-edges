#!/usr/bin/env python3
"""Generate/check every relevant quartic square reconstruction of fixed H.

This is the finite exceptional case after the marked42 residue classification.
The optional C helper proposes orders only; Python checks every fill step.
"""
import argparse
from contextlib import nullcontext
import hashlib
from itertools import combinations
import json
import struct
import time

from marked_residue_common import EXCEPTION_G6, exception_adjacency
from quartic_order_programs import interpret_program, native_interpreter, propose_program


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reconstructions():
    base = exception_adjacency()
    cubics = [v for v in range(22) if len(base[v]) == 3]
    require(len(cubics) == 4 and sorted(map(len, base)) == [3] * 4 + [4] * 18,
            'Unexpected fixed residue.')
    edges = [(u, v) for u in range(22) for v in sorted(base[u])
             if u < v and u not in cubics and v not in cubics]
    for first, second in combinations(edges, 2):
        if set(first) & set(second):
            continue
        for partner in cubics[1:]:
            graph = [row.copy() for row in base] + [set() for _ in range(4)]
            for middle, (u, v) in zip((22, 23), (first, second)):
                graph[u].remove(v)
                graph[v].remove(u)
                for vertex in (u, v, 24, 25):
                    graph[middle].add(vertex)
                    graph[vertex].add(middle)
            for v in cubics:
                hub = 24 if v in (cubics[0], partner) else 25
                graph[v].add(hub)
                graph[hub].add(v)
            require(all(len(row) == 4 for row in graph), 'Reconstruction is not quartic.')
            if any(graph[u] & graph[v] for u in range(26) for v in graph[u]):
                continue
            if any(len(graph[u] & graph[v]) > 2 for u, v in combinations(range(26), 2)):
                continue
            yield graph


def verify_order(graph, order):
    require(isinstance(order, list) and all(type(v) is int for v in order)
            and sorted(order) == list(range(26)), 'Invalid full width10 order.')
    a = [row.copy() for row in graph]
    remaining = set(range(26))
    for v in order:
        neighbors = a[v] & remaining
        require(len(neighbors) <= 10, 'Supplied order exceeds width10.')
        for u in neighbors:
            a[u] |= neighbors - {u}
        remaining.remove(v)


def verify_all(*, native=False):
    started = time.monotonic()
    digest, count = hashlib.sha256(), 0
    with (native_interpreter() if native else nullcontext(interpret_program)) as interpreter:
        for graph in reconstructions():
            _, order = propose_program(graph, interpreter)
            verify_order(graph, order)
            digest.update(struct.pack('<26I', *(sum(1 << v for v in row) for row in graph)))
            count += 1
    require(count == 983, 'The exceptional reconstruction count changed.')
    return {'status': 'verified', 'exception_graph6': EXCEPTION_G6,
            'reconstructions': count, 'graph_stream_sha256': digest.hexdigest(),
            'seconds': time.monotonic() - started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify_all(native=args.native), sort_keys=True))


if __name__ == '__main__':
    main()
