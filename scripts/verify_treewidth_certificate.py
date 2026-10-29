#!/usr/bin/env python3
"""Independently check an exact-treewidth certificate using only the stdlib.

The XZ payload is TWCP1\\n, one JSON header line, and a bitset indexed by
eliminated-vertex masks. A set bit means that the prefix belongs to a closed
set. It must contain the empty prefix, omit the full prefix, and contain
every successor obtainable by eliminating a vertex of degree < treewidth.
Fill after eliminating a subset is independent of its elimination order.
No search program, checkpoint, saved success report, or hash is trusted.
"""
import argparse
import json
import lzma
from pathlib import Path

MAGIC = b'TWCP1\n'
MAX_N = 26
MAX_HEADER = 16384


def require(condition, message):
    if not condition:
        raise ValueError(message)


def decode_graph6(text):
    require(isinstance(text, str) and bool(text), 'Missing graph6 encoding.')
    n = ord(text[0]) - 63
    require(1 <= n <= MAX_N, 'Only 1–26 vertices are supported.')
    length = n * (n - 1) // 2
    require(len(text) == 1 + (length + 5) // 6 and all(63 <= ord(c) <= 126 for c in text), 'Invalid graph6 encoding.')
    if length % 6:
        require((ord(text[-1]) - 63) & ((1 << (6 - length % 6)) - 1) == 0, 'Nonzero graph6 padding.')
    adjacency = [0] * n
    bit = 0
    for v in range(n):
        for u in range(v):
            if (ord(text[1 + bit // 6]) - 63) >> (5 - bit % 6) & 1:
                adjacency[u] |= 1 << v
                adjacency[v] |= 1 << u
            bit += 1
    return adjacency


def read_certificate(path):
    decoder = lzma.LZMADecompressor(memlimit=256 << 20)
    payload = decoder.decompress(Path(path).read_bytes(), max_length=(1 << (MAX_N - 3)) + MAX_HEADER + len(MAGIC))
    require(decoder.eof and not decoder.unused_data, 'Truncated, oversized, or concatenated XZ certificate.')
    require(payload.startswith(MAGIC), 'Unknown certificate format.')
    end = payload.find(b'\n', len(MAGIC), len(MAGIC) + MAX_HEADER)
    require(end >= 0, 'Missing or oversized certificate header.')
    header = json.loads(payload[len(MAGIC):end])
    require(isinstance(header, dict), 'Invalid certificate header.')
    adjacency = decode_graph6(header.get('graph6'))
    n = len(adjacency)
    data = payload[end + 1:]
    require(len(data) == ((1 << n) + 7) // 8, 'Wrong bitset length.')
    if n < 3:
        require(data[-1] >> (1 << n) == 0, 'Nonzero bitset padding.')
    require(header.get('vertices') == n and header.get('edges') == sum(row.bit_count() for row in adjacency) // 2, 'Wrong graph size.')
    return header, data


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def eliminate(adjacency, remaining, vertex):
    neighbors = adjacency[vertex] & remaining & ~(1 << vertex)
    for other in bits(neighbors):
        adjacency[other] |= neighbors & ~(1 << other)
    return remaining ^ (1 << vertex), neighbors.bit_count()


def verify(header, data, expected_graph6=None):
    if expected_graph6 is not None:
        require(header['graph6'] == expected_graph6, 'Certificate is for a different graph.')
    original = decode_graph6(header['graph6'])
    n = len(original)
    width = header.get('treewidth')
    require(type(width) is int and 0 <= width < n, 'Invalid treewidth.')
    order = header.get('order')
    require(isinstance(order, list) and all(type(v) is int for v in order) and sorted(order) == list(range(n)), 'Invalid upper-bound order.')
    require(len(data) == ((1 << n) + 7) // 8, 'Wrong bitset length.')
    full = (1 << n) - 1
    current, remaining, maximum = original.copy(), full, 0
    for v in order:
        remaining, degree = eliminate(current, remaining, v)
        maximum = max(maximum, degree)
    require(maximum == width, 'Upper-bound order has the wrong width.')
    contains = lambda mask: bool(data[mask >> 3] & (1 << (mask & 7)))
    require(contains(0) and not contains(full), 'Closed set must contain empty and omit full prefix.')
    count = 0
    for index, byte in enumerate(data):
        for low in bits(byte):
            prefix = 8 * index + low
            require(prefix <= full, 'Prefix outside graph.')
            count += 1
            current, remaining = original.copy(), full
            for v in bits(prefix):
                remaining, _ = eliminate(current, remaining, v)
            for v in bits(remaining):
                if (current[v] & remaining).bit_count() < width:
                    require(contains(prefix | (1 << v)), f'Closed-set violation at prefix {prefix}, vertex {v}.')
    require(type(header.get('closed_states')) is int and count == header['closed_states'], 'Wrong closed-state count.')
    return {'vertices': n, 'edges': sum(row.bit_count() for row in original) // 2,
            'treewidth': width, 'closed_states': count, 'graph6': header['graph6']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path)
    parser.add_argument('--graph6', type=Path, help='Also require this graph6 identity.')
    args = parser.parse_args()
    expected = args.graph6.read_text().strip() if args.graph6 else None
    result = verify(*read_certificate(args.certificate), expected_graph6=expected)
    print(f'PASS: {result["vertices"]} vertices, {result["edges"]} edges, treewidth exactly {result["treewidth"]}; {result["closed_states"]:,} closed states.')
    print(result['graph6'])


if __name__ == '__main__':
    main()
