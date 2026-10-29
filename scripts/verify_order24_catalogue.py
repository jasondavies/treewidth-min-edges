#!/usr/bin/env python3
"""Verify exhaustive order-24 incidence-profile coverage using explicit maps.

No graph generator or isomorphism library is used. This proves catalogue
coverage, not exclusion of any profile. The written minimum-counterexample
lemmas justify the local restrictions applied during enumeration.
"""
import argparse
from itertools import combinations
import lzma
from pathlib import Path
import struct

MAGIC = b'O24C1\n'
MAX_RAW = 4 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def position(u, v):
    if u > v:
        u, v = v, u
    return v * (v - 1) // 2 + u


def decode(code, n):
    require(type(code) is int and 0 <= code < 1 << (n * (n - 1) // 2), 'Invalid graph encoding.')
    return [{u for u in range(n) if u != v and code >> position(u, v) & 1}
            for v in range(n)]


def relabel(code, n, permutation):
    return sum(1 << position(permutation[u], permutation[v])
               for u, v in combinations(range(n), 2) if code >> position(u, v) & 1)


def valid_profile(high, shared):
    a, b = decode(high, 8), decode(shared, 8)
    if shared & ~high:
        return False
    capacity = [5 - len(row) for row in a]
    if any(capacity[v] < len(b[v]) for v in range(8)):
        return False
    if any(b[v] and capacity[v] < 2 for v in range(8)):
        return False
    if sum(capacity) - shared.bit_count() > 16:
        return False
    for v in range(8):
        high_triangles = sum(y in a[x] for x, y in combinations(sorted(a[v]), 2))
        if high_triangles + len(b[v]) > 4:
            return False
        for x, y in combinations(sorted(a[v]), 2):
            if y not in a[x]:
                others = a[v] - {x, y}
                if b[v] - {x, y} or any(w in a[u] for u, w in combinations(sorted(others), 2)):
                    return False
    return True


def profile_prefix(high, shared):
    require(valid_profile(high, shared), 'Invalid profile.')
    a, b = decode(high, 8), decode(shared, 8)
    known = [row.copy() for row in a] + [set() for _ in range(16)]
    next_vertex = 8
    for u, v in combinations(range(8), 2):
        if v in b[u]:
            known[u].add(next_vertex)
            known[v].add(next_vertex)
            known[next_vertex] |= {u, v}
            next_vertex += 1
    for v in range(8):
        for _ in range(5 - len(known[v])):
            require(next_vertex < 24, 'Too many low vertices.')
            known[v].add(next_vertex)
            known[next_vertex].add(v)
            next_vertex += 1
    return [24, 8] + [sum(1 << u for u in row) for row in known]


def profile_encoding(prefix):
    """Recover high/marked edges from a complete incidence root, without canonization."""
    require(isinstance(prefix, list) and len(prefix) == 26 and prefix[:2] == [24, 8]
            and all(type(x) is int for x in prefix), 'Invalid order-24 incidence root.')
    masks = prefix[2:]
    require(all(0 <= value < 1 << 24 for value in masks), 'Invalid adjacency mask.')
    a = [{u for u in range(24) if masks[v] >> u & 1} for v in range(24)]
    for v in range(24):
        require(v not in a[v] and all(v in a[u] for u in a[v]), 'Invalid graph.')
        if v < 8:
            require(len(a[v]) == 5, 'Unfinished high neighborhood.')
        else:
            require(a[v] <= set(range(8)) and len(a[v]) <= 2, 'Extra low edge or high attachment.')
    high = sum(1 << position(u, v) for u, v in combinations(range(8), 2) if v in a[u])
    shared = 0
    for row in a[8:]:
        if len(row) == 2:
            u, v = sorted(row)
            edge = 1 << position(u, v)
            require(not shared & edge, 'Repeated shared-low neighbor.')
            shared |= edge
    require(valid_profile(high, shared), 'Profile violates a necessary restriction.')
    return high, shared


class Reader:
    def __init__(self, data):
        require(isinstance(data, bytes) and len(data) <= MAX_RAW, 'Invalid or oversized certificate.')
        require(data.startswith(MAGIC), 'Unknown format.')
        self.data, self.offset = data, len(MAGIC)

    def integer(self, bits=32):
        size = bits // 8
        require(self.offset + size <= len(self.data), 'Truncated certificate.')
        value, = struct.unpack_from('<I' if bits == 32 else '<Q', self.data, self.offset)
        self.offset += size
        return value

    def mapping(self, n, total):
        target, packed = self.integer(), self.integer()
        require(target < total and packed < 1 << (3 * n), 'Invalid map encoding.')
        permutation = [(packed >> (3 * i)) & 7 for i in range(n)]
        require(sorted(permutation) == list(range(n)), 'Map is not a permutation.')
        return target, permutation


def verify(data):
    stream = Reader(data)
    previous = [0]
    total_extensions = 0
    level_counts = []
    for n in range(1, 9):
        count, expected_maps = stream.integer(), stream.integer()
        require(0 < count <= (len(data) - stream.offset) // 4, 'Invalid representative count.')
        representatives = [stream.integer() for _ in range(count)]
        require(len(set(representatives)) == count, 'Duplicate graph encoding.')
        for code in representatives:
            require(all(len(row) <= 5 for row in decode(code, n)), 'High graph exceeds degree five.')
        seen_maps = 0
        for code in previous:
            a = decode(code, n - 1)
            for neighbors in range(1 << (n - 1)):
                selected = [v for v in range(n - 1) if neighbors >> v & 1]
                if len(selected) > 5 or any(len(a[v]) == 5 for v in selected):
                    continue
                extended = code | sum(1 << position(v, n - 1) for v in selected)
                target, permutation = stream.mapping(n, count)
                require(relabel(extended, n, permutation) == representatives[target], 'Incorrect extension isomorphism.')
                seen_maps += 1
        require(seen_maps == expected_maps, 'Incomplete extension coverage.')
        total_extensions += seen_maps
        level_counts.append(count)
        previous = representatives

    count, expected_maps = stream.integer(), stream.integer()
    require(0 < count <= (len(data) - stream.offset) // 8, 'Invalid profile count.')
    profiles = [stream.integer(64) for _ in range(count)]
    require(len(set(profiles)) == count, 'Duplicate profile encoding.')
    mask = (1 << 28) - 1
    for code in profiles:
        require(valid_profile(code >> 28, code & mask), 'Invalid profile representative.')
    seen_maps = feasible_attachments = 0
    for high in previous:
        a = decode(high, 8)
        capacity = [5 - len(row) for row in a]
        # Same explicit ordering as the format: increasing high endpoint,
        # then increasing low endpoint. No isomorphism search occurs here.
        pairs = [(u, v) for v in range(1, 8) for u in range(v)
                 if v in a[u] and capacity[u] >= 2 and capacity[v] >= 2]
        for selected in range(1 << len(pairs)):
            if sum(capacity) - selected.bit_count() > 16:
                continue
            used = [0] * 8
            shared = 0
            for i, (u, v) in enumerate(pairs):
                if selected >> i & 1:
                    used[u] += 1
                    used[v] += 1
                    shared |= 1 << position(u, v)
            if any(used[v] > capacity[v] for v in range(8)):
                continue
            feasible_attachments += 1
            if not valid_profile(high, shared):
                continue
            target, permutation = stream.mapping(8, count)
            code = profiles[target]
            require(relabel(high, 8, permutation) == code >> 28
                    and relabel(shared, 8, permutation) == code & mask,
                    'Incorrect profile isomorphism.')
            seen_maps += 1
    require(seen_maps == expected_maps, 'Incomplete attachment coverage.')
    require(stream.offset == len(data), 'Trailing certificate data.')
    return {'high_graph_counts': level_counts, 'extension_maps': total_extensions,
            'feasible_attachments': feasible_attachments, 'profile_maps': seen_maps,
            'profiles': [profile_prefix(code >> 28, code & mask) for code in profiles]}


def read_certificate(path):
    raw = path.read_bytes()
    if path.suffix == '.xz':
        decoder = lzma.LZMADecompressor(memlimit=256 * 1024 * 1024)
        raw = decoder.decompress(raw, max_length=MAX_RAW + 1)
        require(decoder.eof and not decoder.unused_data, 'Truncated, concatenated, or oversized XZ stream.')
    require(len(raw) <= MAX_RAW, 'Certificate exceeds the size limit.')
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path)
    parser.add_argument('--output', type=Path, help='Write the covered order-24 prefixes.')
    args = parser.parse_args()
    result = verify(read_certificate(args.certificate))
    if args.output:
        args.output.write_text(''.join(' '.join(map(str, row)) + '\n' for row in result['profiles']))
    print(f"PASS: {len(result['profiles'])} representatives cover every necessary order-24 incidence profile.")
    print({key: value for key, value in result.items() if key != 'profiles'})
    print('This establishes root coverage only; every profile still needs an exclusion proof.')


if __name__ == '__main__':
    main()
