"""Independent small-graph reference algorithms; Python standard library only.

Graphs are adjacency lists of sets for the explicit-filling verifier and
tuples of bitmasks for the subset algorithms.
"""
from functools import lru_cache
import itertools


def decode(s):
    n = ord(s[0]) - 63
    assert 1 <= n <= 17
    assert len(s) == 1 + (n * (n - 1) // 2 + 5) // 6
    a = [set() for _ in range(n)]
    bit = 0
    for j in range(1, n):
        for i in range(j):
            if (ord(s[1 + bit // 6]) - 63) >> (5 - bit % 6) & 1:
                a[i].add(j)
                a[j].add(i)
            bit += 1
    return a


def encode(a):
    bits = [int(j in a[i]) for j in range(1, len(a)) for i in range(j)]
    bits += [0] * ((-len(bits)) % 6)
    return chr(len(a) + 63) + "".join(
        chr(63 + sum(bits[i + j] << (5 - j) for j in range(6)))
        for i in range(0, len(bits), 6))


def masks(a):
    return tuple(sum(1 << w for w in ns) for ns in a)


def edges(a):
    return [(u, v) for v in range(len(a)) for u in sorted(a[v]) if u < v]


def triangles(a):
    return [t for t in itertools.combinations(range(len(a)), 3)
            if all(y in a[x] for x, y in itertools.combinations(t, 2))]


def reductions(core):
    """Every single-edge deletion and every triangle-to-star replacement."""
    for u, v in edges(core):
        a = [set(ns) for ns in core]
        a[u].remove(v)
        a[v].remove(u)
        yield {"deleted_edge": [u, v]}, a
    for t in triangles(core):
        a = [set(ns) for ns in core] + [set(t)]
        for x, y in itertools.combinations(t, 2):
            a[x].remove(y)
            a[y].remove(x)
        for x in t:
            a[x].add(len(core))
        yield {"replaced_triangle": list(t)}, a


def verify_order(a, order, bound):
    """Set-based fill verifier, independent of the C path-based verifier."""
    assert sorted(order) == list(range(len(a)))
    current = [set(ns) for ns in a]
    remaining = set(range(len(a)))
    width = 0
    for v in order:
        ns = current[v] & remaining
        width = max(width, len(ns))
        assert len(ns) <= bound
        for w in ns:
            current[w].update(ns - {w})
        remaining.remove(v)
    return width


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def treewidth(adj):
    n = len(adj)
    full = (1 << n) - 1

    @lru_cache(None)
    def solve(eliminated):
        if eliminated == full:
            return 0
        best = n
        remaining = full ^ eliminated
        for v in bits(remaining):
            seen = 1 << v
            frontier = adj[v] & eliminated
            while frontier:
                x = (frontier & -frontier).bit_length() - 1
                frontier ^= 1 << x
                seen |= 1 << x
                frontier |= adj[x] & eliminated & ~seen
            neighborhood = adj[v]
            for x in bits(seen & eliminated):
                neighborhood |= adj[x]
            degree = (neighborhood & remaining & ~(1 << v)).bit_count()
            best = min(best, max(degree, solve(eliminated | (1 << v))))
        return best
    return solve(0)


def torso_neighbors(adj, eliminated, v):
    """Original edges plus paths whose internal vertices were eliminated."""
    seen = 0
    todo = adj[v] & eliminated
    result = adj[v]
    while todo:
        w = (todo & -todo).bit_length() - 1
        todo ^= 1 << w
        seen |= 1 << w
        result |= adj[w]
        todo |= adj[w] & eliminated & ~seen
    full = (1 << len(adj)) - 1
    return result & (full ^ eliminated) & ~(1 << v)


def width_reachable(adj, width):
    """All feasible elimination prefixes, encoded by eliminated vertex sets."""
    n = len(adj)
    full = (1 << n) - 1
    reached = {0}
    parent = {}
    for s in range(full + 1):
        if s not in reached:
            continue
        for v in bits(full ^ s):
            if torso_neighbors(adj, s, v).bit_count() <= width:
                nxt = s | (1 << v)
                if nxt not in reached:
                    reached.add(nxt)
                    parent[nxt] = (s, v)
    if full not in reached:
        return reached, None
    order = []
    s = full
    while s:
        s, v = parent[s]
        order.append(v)
    return reached, tuple(reversed(order))


def verify_width_lower(adj, width, closed_states):
    """Independent verifier: fill vertices in increasing order to get each torso.

    A set containing the empty prefix, closed under all width-feasible steps,
    but excluding the full prefix proves treewidth > width.
    """
    n = len(adj)
    full = (1 << n) - 1
    if 0 not in closed_states or full in closed_states:
        return False
    for s in closed_states:
        if s < 0 or s > full:
            return False
        current = list(adj)
        remaining = full
        for v in bits(s):
            ns = current[v] & remaining
            for w in bits(ns):
                current[w] |= ns & ~(1 << w)
            remaining ^= 1 << v
        for v in bits(remaining):
            if (current[v] & remaining).bit_count() <= width:
                if s | (1 << v) not in closed_states:
                    return False
    return True
