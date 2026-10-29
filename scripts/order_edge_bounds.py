"""Proved edge lower bounds depending on treewidth and remaining order.

This deliberately uses no 52-edge exclusions and no 34/35-edge graph lists.
See proof-eleven-order-bounds.md for the two elementary recurrences.
"""
from math import comb

GLOBAL_MINIMUM = (0, 1, 3, 6, 10, 15, 21, 28, 34, 42, 47, 52)


def build_table(max_order=26):
    table = [[0] * (max_order + 1)]
    for k in range(1, len(GLOBAL_MINIMUM)):
        row = []
        for n in range(max_order + 1):
            if n <= k:
                row.append(comb(max_order, 2) + 1)  # Impossible order.
                continue
            bound = GLOBAL_MINIMUM[k]
            if n <= k + 3:
                bound = max(bound, comb(k + 1, 2))
            if n > 2:
                # Every deletion leaves >= b edges; summing gives (n-2)m >= nb.
                b = table[k - 1][n - 1]
                bound = max(bound, (n * b + n - 3) // (n - 2))
            row.append(bound)
        table.append(row)
    return tuple(tuple(row) for row in table)


ORDER_MINIMUM = build_table()
