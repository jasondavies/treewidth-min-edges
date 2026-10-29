"""Independently enumerate the marked42 residues from prior34/35/36 families.

The source-family completeness is an explicit earlier-classification premise.
Hashes pin the exact previously classified inputs, not a new proof of that
premise. Every inverse choice and every supplied width8 order/isomorphism is
checked here without the C generator.
"""
import argparse
import hashlib
from itertools import combinations
import json
import lzma
from pathlib import Path
import sys
import time

from marked_residue_common import EXCEPTION_G6, EXCEPTION_MASKS, decode_graph6

MAGIC = b'TW42R\x01'
SOURCES = [
    (2, 'treewidth36-family.g6', '0f62f3d14d543515b12567c1d650d290a9a5369ab9931220e5d398a9d3999214', 457),
    (3, 'treewidth35-all-family.g6', '1fcf89ffba866b13dc95de22bdac1c98a284d03687b9d61b927f00daca52fca6', 9),
    (4, 'treewidth34-family34.g6', '4f0f5209e9a3cf10c88b151649742ca5485b24b56204b47a62f9e0d99a41503f', 1),
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


EXCEPTION = EXCEPTION_MASKS


def catalogue(repository):
    result = []
    for r, filename, digest, expected in SOURCES:
        raw = (Path(repository) / 'sources/nine' / filename).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, 'Prior classified family hash changed: ' + filename)
        lines = raw.decode('ascii').splitlines()
        require(len(lines) == len(set(lines)), 'Duplicated source graph.')
        selected = []
        for code in lines:
            if ord(code[0]) - 63 != 21 - r:
                continue
            graph = decode_graph6(code)
            degree = sorted(mask.bit_count() for mask in graph)
            if degree == [3] * (8 - 2*r) + [4] * (13 + r):
                require(sum(degree) == 2 * (38 - r), 'Unexpected edge count.')
                selected.append(code)
        require(len(selected) == expected, 'Prior family slice count differs.')
        result.extend((r, code) for code in sorted(selected))
    return result


def target_family(graph, new_cubics):
    lows = [v for v, row in enumerate(graph) if row.bit_count() == 3]
    require(len(lows) == 4 and all(row.bit_count() in (3, 4) for row in graph),
            'Inverse construction has incorrect degrees.')
    for v in lows:
        neighbors = graph[v]
        if any(graph[u] & neighbors for u in range(22) if neighbors >> u & 1):
            return False  # A cubic elimination would leave fewer than42 edges.
    if any((graph[u] & graph[v]).bit_count() > 1 for u, v in combinations(lows, 2)):
        return False  # Two cubic eliminations would lose an edge.
    low_set = sum(1 << v for v in lows)
    if sum((graph[v] & low_set).bit_count() for v in lows) >= 8:
        return False
    # Proper subgraph of K2,2, checked without using its historical catalogue.
    bipartite = False
    for left in combinations(lows, 2):
        side = sum(1 << v for v in left)
        if all(not graph[v] & (side if side >> v & 1 else low_set ^ side) for v in lows):
            bipartite = True
            break
    if not bipartite:
        return False
    for bits in range(1, 16):
        selected = sum(1 << lows[i] for i in range(4) if bits >> i & 1)
        if (selected & new_cubics).bit_count() < 2:
            continue
        if all(not graph[v] & selected if selected >> v & 1
               else (graph[v] & selected).bit_count() == 1 for v in lows):
            return True
    return False


def reconstructions(families, stats=None):
    for base_index, (r, code) in enumerate(families):
        base = decode_graph6(code)
        n = len(base)
        cubics = [v for v, row in enumerate(base) if row.bit_count() == 3]
        for restored in combinations(cubics, 4 - r):
            restored_mask = sum(1 << v for v in restored)
            edges = [(u, v) for u in range(n) for v in range(u + 1, n)
                     if base[u] >> v & 1 and not (restored_mask >> u & 1 or restored_mask >> v & 1)]
            for matching in combinations(edges, r):
                endpoints = {v for edge in matching for v in edge}
                if len(endpoints) != 2*r:
                    continue
                if stats is not None:
                    stats['inverse_choices'] += 1
                graph = base.copy() + [0] * (r + 1)
                new_cubics = 0
                for i, (u, v) in enumerate(matching):
                    z = n + i
                    new_cubics |= 1 << z
                    graph[u] = (graph[u] & ~(1 << v)) | (1 << z)
                    graph[v] = (graph[v] & ~(1 << u)) | (1 << z)
                    graph[z] = (1 << u) | (1 << v) | (1 << 21)
                    graph[21] |= 1 << z
                for v in restored:
                    graph[v] |= 1 << 21
                    graph[21] |= 1 << v
                if target_family(graph, new_cubics):
                    if stats is not None:
                        stats['target_choices'] += 1
                    yield base_index, graph


def verify_order(graph, order):
    require(len(order) == 22 and sorted(order) == list(range(22)), 'Invalid width8 permutation.')
    a = graph.copy()
    remaining = (1 << 22) - 1
    for v in order:
        neighbors = a[v] & remaining
        require(neighbors.bit_count() <= 8, 'Supplied order exceeds width8.')
        pending = neighbors
        while pending:
            bit = pending & -pending
            pending ^= bit
            a[bit.bit_length() - 1] |= neighbors ^ bit
        remaining ^= 1 << v


def verify_map(graph, permutation):
    require(len(permutation) == 22 and sorted(permutation) == list(range(22)),
            'Invalid exception permutation.')
    for v in range(22):
        mapped = sum(1 << permutation[u] for u in range(22) if graph[v] >> u & 1)
        require(mapped == EXCEPTION[permutation[v]], 'False exception isomorphism.')


def verify_stream(stream, families):
    require(stream.read(len(MAGIC)) == MAGIC, 'Invalid reconstruction transcript.')
    stats = {'families': len(families), 'inverse_choices': 0, 'target_choices': 0,
             'orders': 0, 'exception_maps': 0}
    started = time.monotonic()
    for base_index, graph in reconstructions(families, stats):
        record = stream.read(23)
        require(len(record) == 23, 'Missing reconstruction proof record.')
        require(record[0] in (0, 1), 'Unknown reconstruction proof tag.')
        if record[0] == 0:
            verify_order(graph, list(record[1:]))
            stats['orders'] += 1
        else:
            verify_map(graph, list(record[1:]))
            stats['exception_maps'] += 1
        if stats['target_choices'] % 100000 == 0:
            print(f"Checked {stats['target_choices']} reconstruction records (base{base_index}).", file=sys.stderr, flush=True)
    require(not stream.read(1), 'Extra reconstruction proof records.')
    stats['seconds'] = time.monotonic() - started
    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write-catalogue', type=Path)
    parser.add_argument('--certificate', type=Path)
    args = parser.parse_args()
    families = catalogue(args.repository)
    if args.write_catalogue:
        args.write_catalogue.write_text(''.join(code + '\n' for r, code in families))
    if args.certificate:
        opener = lzma.open if args.certificate.suffix == '.xz' else open
        with opener(args.certificate, 'rb') as stream:
            print(json.dumps(verify_stream(stream, families), sort_keys=True))
    elif not args.write_catalogue:
        print(json.dumps({'families': len(families)}))


if __name__ == '__main__':
    main()
