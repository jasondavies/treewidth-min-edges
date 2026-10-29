"""Fixed identity of the exceptional marked42 residue, shared by its checks.

The34/35/36 reconstruction classifier, quartic square reconstruction, and
shared-high-edge reconstruction must all import this same graph identity.
"""
EXCEPTION_G6 = 'UqGOOICQ@GB?Oo_oCG?c@?E??c?@?o?`G?IC?@Q?'


def decode_graph6(text):
    """Strict small graph6 decoder; return symmetric integer adjacency masks."""
    if not isinstance(text, str) or not text:
        raise ValueError('Missing graph6.')
    values = [ord(c) - 63 for c in text]
    n = values[0]
    if not (0 < n <= 26 and all(0 <= x < 64 for x in values)):
        raise ValueError('Invalid graph6 characters.')
    bits = n * (n - 1) // 2
    if len(values) != 1 + (bits + 5) // 6:
        raise ValueError('Invalid graph6 length.')
    padding = -bits % 6
    if padding and values[-1] & ((1 << padding) - 1):
        raise ValueError('Invalid graph6 padding.')
    graph, bit = [0] * n, 0
    for v in range(1, n):
        for u in range(v):
            if values[1 + bit // 6] >> (5 - bit % 6) & 1:
                graph[u] |= 1 << v
                graph[v] |= 1 << u
            bit += 1
    return graph


EXCEPTION_MASKS = tuple(decode_graph6(EXCEPTION_G6))


def exception_adjacency():
    """Fresh mutable adjacency sets for code using the earlier set interface."""
    return [{u for u in range(22) if row >> u & 1} for row in EXCEPTION_MASKS]
