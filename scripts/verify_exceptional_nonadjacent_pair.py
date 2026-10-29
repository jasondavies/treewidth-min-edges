#!/usr/bin/env python3
"""Exhaust all 24-vertex degree-4/5 lifts of the fixed marked residue.

The two added vertices are nonadjacent and have degree five. Every supplied
order is checked independently; the optional native finder is untrusted.
"""
import argparse
from collections import Counter
from contextlib import nullcontext
from hashlib import sha256
from itertools import combinations
import json
from math import comb
import struct
import time

from marked_residue_common import EXCEPTION_G6, exception_adjacency
from quartic_order_programs import interpret_program, native_interpreter, propose_program

X, Y = 22, 23


def require(condition, message):
    if not condition:
        raise ValueError(message)


def residue_graph():
    graph = exception_adjacency()
    require(len(graph) == 22 and sorted(map(len, graph)) == [3] * 4 + [4] * 18,
            'The fixed residue has the wrong degree profile.')
    require(sum(map(len, graph)) == 84, 'The fixed residue must have 42 edges.')
    return graph


def attachments(residue):
    """All attachments, modulo exchanging the two added vertices."""
    cubics = [v for v, row in enumerate(residue) if len(row) == 3]
    quartics = [v for v, row in enumerate(residue) if len(row) == 4]
    for shared_count in range(5):
        for shared_tuple in combinations(cubics, shared_count):
            shared = set(shared_tuple)
            single = [v for v in cubics if v not in shared]
            if not single:
                for left, right in combinations(quartics, 2):
                    yield shared_count, shared | {left}, shared | {right}
                continue
            # Fix the first nonshared cubic on the left; exchanging X,Y
            # gives exactly one representative satisfying this condition.
            for left_count in range(1, len(single) + 1):
                for extra in combinations(single[1:], left_count - 1):
                    left_c = {single[0], *extra}
                    right_c = set(single) - left_c
                    left_q_count = 5 - shared_count - left_count
                    right_q_count = 1 + left_count
                    for left_tuple in combinations(quartics, left_q_count):
                        left_q = set(left_tuple)
                        remaining = [v for v in quartics if v not in left_q]
                        for right_tuple in combinations(remaining, right_q_count):
                            yield (shared_count, shared | left_c | left_q,
                                   shared | right_c | set(right_tuple))


def reconstruct(residue, left, right):
    graph = [set(row) for row in residue] + [set(left), set(right)]
    for v in left:
        graph[v].add(X)
    for v in right:
        graph[v].add(Y)
    return graph


def validate_reconstruction(graph, residue):
    require(len(graph) == 24, 'Expected a 24-vertex reconstruction.')
    for v, row in enumerate(graph):
        require(isinstance(row, set) and all(type(u) is int and 0 <= u < 24 for u in row)
                and v not in row, 'Invalid simple graph.')
        require(all(v in graph[u] for u in row), 'Asymmetric graph.')
    require(sorted(map(len, graph)) == [4] * 16 + [5] * 8
            and len(graph[X]) == len(graph[Y]) == 5, 'Wrong reconstructed degree profile.')
    require(sum(map(len, graph)) == 104, 'Expected 52 edges.')
    require(Y not in graph[X], 'The added vertices must be nonadjacent.')
    require([row - {X, Y} for row in graph[:22]] == residue,
            'Deleting the two added vertices does not restore the residue.')
    return len(graph[X] & graph[Y])


def verify_order(graph, order):
    require(isinstance(order, list) and len(order) == 24
            and all(type(v) is int for v in order) and sorted(order) == list(range(24)),
            'Invalid 24-vertex elimination permutation.')
    adjacency = [set(row) for row in graph]
    live = set(range(24))
    for v in order:
        neighbors = adjacency[v] & live
        require(len(neighbors) <= 10, 'Order exceeds width ten.')
        for u in neighbors:
            adjacency[u].update(neighbors - {u})
        live.remove(v)


def find_and_verify_order(graph, interpreter=interpret_program):
    padded = [set(row) for row in graph] + [set(), set()]
    program, order = propose_program(padded, interpreter)
    require(isinstance(order, list) and len(order) == 26
            and all(type(v) is int for v in order) and sorted(order) == list(range(26)),
            'Invalid padded 26-vertex elimination permutation.')
    verify_order(graph, [v for v in order if v < 24])
    return program


def expected_counts():
    return {t: comb(4, t) * sum(comb(4-t, a) * comb(18, 5-t-a)
            * comb(13+t+a, 1+a) for a in range(5-t)) // 2 for t in range(5)}


def verify_all(interpreter=interpret_program, progress=None):
    residue = residue_graph()
    counts, programs = Counter(), Counter()
    digest = sha256()
    for index, (shared, left, right) in enumerate(attachments(residue), 1):
        graph = reconstruct(residue, left, right)
        require(validate_reconstruction(graph, residue) == shared, 'Wrong shared-neighbor count.')
        try:
            program = find_and_verify_order(graph, interpreter)
        except ValueError as error:
            raise ValueError(f'Reconstruction {index}, shared={shared}, left={sorted(left)}, '
                             f'right={sorted(right)}: {error}') from error
        counts[shared] += 1
        programs[len(program)] += 1
        digest.update(struct.pack('<24I', *(sum(1 << v for v in row) for row in graph)))
        if progress is not None and index % 100000 == 0:
            progress(index)
    require(dict(counts) == expected_counts(), 'Incomplete reconstruction enumeration.')
    return {'status': 'PASS', 'residue': EXCEPTION_G6, 'reconstructions': sum(counts.values()),
            'by_shared_cubics': dict(counts), 'program_lengths': dict(programs),
            'ordered_graph_sha256': digest.hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', action='store_true', help='Use the optional untrusted C finder.')
    parser.add_argument('--cc', help='Compiler command, optionally including -march=native.')
    args = parser.parse_args()
    started = time.monotonic()
    context = native_interpreter(args.cc) if args.native else nullcontext(interpret_program)
    with context as interpreter:
        result = verify_all(interpreter, lambda count: print(json.dumps(
            {'checked': count, 'seconds': time.monotonic() - started}), flush=True))
    result['seconds'] = time.monotonic() - started
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
