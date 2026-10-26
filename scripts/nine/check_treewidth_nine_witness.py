"""Independently check the saved 42-edge treewidth-nine witness.

Regenerates its closed set of width-eight elimination prefixes, checks
closure using a different torso implementation, and verifies the width-nine
order with Python sets. No C executable or graph generator is needed.
"""
import json

from reference import width_reachable, verify_width_lower
from run_treewidth_edge_checks import ROOT, encode, masks, verify_order


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: assertions are verification steps.')
    certificate = json.loads((ROOT / 'sources/witness42.json').read_text())
    s = certificate['graph6']
    n = ord(s[0]) - 63
    assert n == certificate['vertices'] == 21
    a = [set() for _ in range(n)]
    bit = 0
    for j in range(1, n):
        for i in range(j):
            if (ord(s[1 + bit // 6]) - 63) >> (5 - bit % 6) & 1:
                a[i].add(j)
                a[j].add(i)
            bit += 1
    assert encode(a) == s
    assert sum(map(len, a)) // 2 == certificate['edges'] == 42
    assert all(len(ns) == 4 for ns in a)
    assert verify_order(a, certificate['width_nine_order'], 9) == 9
    adj = masks(a)
    closed, order = width_reachable(adj, 8)
    assert order is None
    assert closed == set(certificate['closed_width_eight_states'])
    assert verify_width_lower(adj, 8, closed)
    print(f'PASS: 42 edges, treewidth exactly nine; {len(closed)} closed states verified.')


if __name__ == '__main__':
    main()
