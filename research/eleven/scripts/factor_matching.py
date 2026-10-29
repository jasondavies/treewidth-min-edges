"""Exact finite reference routines for a3nm-020--022. Standard library only."""
from functools import lru_cache
from itertools import combinations, permutations
from math import comb

from posets import bits


def two_factors(adj):
    """Enumerate spanning simple 2-factors by their edge tuples."""
    n = len(adj)
    degrees = [0] * n
    chosen = []
    def rec(v):
        if v == n:
            if all(x == 2 for x in degrees):
                yield tuple(chosen)
            return
        candidates = [w for w in bits(adj[v]) if w > v and degrees[w] < 2]
        need = 2 - degrees[v]
        if need < 0:
            return
        for ns in combinations(candidates, need):
            for w in ns:
                degrees[v] += 1
                degrees[w] += 1
                chosen.append((v, w))
            yield from rec(v + 1)
            for w in reversed(ns):
                chosen.pop()
                degrees[w] -= 1
                degrees[v] -= 1
    yield from rec(0)


def factor_cycles(n, es):
    neighbors = [[] for _ in range(n)]
    for u, v in es:
        neighbors[u].append(v)
        neighbors[v].append(u)
    assert all(len(ns) == 2 for ns in neighbors)
    unseen = set(range(n))
    cycles = []
    while unseen:
        start = min(unseen)
        prev, cur = -1, start
        cycle = []
        while cur in unseen:
            unseen.remove(cur)
            cycle.append(cur)
            nxt = next(w for w in neighbors[cur] if w != prev)
            prev, cur = cur, nxt
        assert cur == start
        cycles.append(tuple(cycle))
    return tuple(cycles)


def cycle_cover_count(adj, minimum=5):
    """Independent cycle enumeration followed by exact-cover subset DP."""
    n = len(adj)
    cycle_counts = {}
    for root in range(n):
        def walk(path, used):
            v = path[-1]
            if len(path) >= minimum and adj[v] >> root & 1 and path[1] < v:
                cycle_counts[used] = cycle_counts.get(used, 0) + 1
            for w in bits(adj[v]):
                if w > root and not (used >> w & 1):
                    walk(path + (w,), used | (1 << w))
        walk((root,), 1 << root)
    by_vertex = [[] for _ in range(n)]
    for s, count in cycle_counts.items():
        for v in bits(s):
            by_vertex[v].append((s, count))
    @lru_cache(None)
    def rec(s):
        if not s:
            return 1
        v = (s & -s).bit_length() - 1
        return sum(c * rec(s ^ t) for t, c in by_vertex[v] if t & s == t)
    return rec((1 << n) - 1)


def short_cycle_branching(adj):
    """FPT branching logic, instantiated with an exponential reference oracle."""
    @lru_cache(None)
    def rec(a):
        factor = next(two_factors(a), None)
        if factor is None:
            return None
        bad = next((c for c in factor_cycles(len(a), factor) if len(c) < 5), None)
        if bad is None:
            return factor
        for i,u in enumerate(bad):
            v = bad[(i+1) % len(bad)]
            b = list(a)
            b[u] &= ~(1 << v)
            b[v] &= ~(1 << u)
            result = rec(tuple(b))
            if result is not None:
                return result
        return None
    return rec(tuple(adj))


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


def matching_support(matrix):
    """Entries -1 absent, 0 blue, 1 red; answer is a bitset of possible counts."""
    n = len(matrix)
    dp = [0] * (1 << n)
    dp[0] = 1
    for used in range(1 << n):
        row = used.bit_count()
        if row == n:
            continue
        for j in range(n):
            if not (used >> j & 1) and matrix[row][j] >= 0:
                dp[used | (1 << j)] |= dp[used] << matrix[row][j]
    return dp[-1]


def matching_support_by_scc(matrix):
    n = len(matrix)
    matched_row = [-1] * n
    def augment(i, seen):
        for j in range(n):
            if matrix[i][j] >= 0 and j not in seen:
                seen.add(j)
                if matched_row[j] < 0 or augment(matched_row[j], seen):
                    matched_row[j] = i
                    return True
        return False
    if not all(augment(i, set()) for i in range(n)):
        return 0, []
    mate = [0] * n
    for j, i in enumerate(matched_row):
        mate[i] = j
    reach = [sum(1 << j for j in range(n) if matrix[i][mate[j]] >= 0) for i in range(n)]
    for j in range(n):
        for i in range(n):
            if reach[i] >> j & 1:
                reach[i] |= reach[j]
    left = set(range(n))
    blocks = []
    answer = 1
    while left:
        i = min(left)
        block = sorted(j for j in left if reach[i] >> j & 1 and reach[j] >> i & 1)
        left.difference_update(block)
        blocks.append(block)
        local = matching_support([[matrix[r][mate[c]] for c in block] for r in block])
        answer = __convolve(answer, local)
    return answer, blocks


def __convolve(a, b):
    result = 0
    for k in bits(b):
        result |= a << k
    return result


def poly_multiply(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return out


@lru_cache(None)
def vandermonde_terms(n):
    out = []
    for p in permutations(range(n)):
        poly = [1]
        for i, j in enumerate(p):
            poly = poly_multiply(poly, [comb(j, k)*i**(j-k) for k in range(j+1)])
        sign = (-1)**sum(p[i] > p[j] for i in range(n) for j in range(i+1, n))
        out.append((sum(1 << (i*n+j) for i,j in enumerate(p)),
                    tuple(sign*x for x in poly), p))
    return tuple(out)


def vandermonde_fibers(n, present, red):
    counts = [0] * (n+1)
    polys = [[0] * (n*(n-1)//2+1) for _ in range(n+1)]
    for mask, poly, _ in vandermonde_terms(n):
        if mask & present == mask:
            k = (mask & red).bit_count()
            counts[k] += 1
            for j, x in enumerate(poly):
                polys[k][j] += x
    return counts, polys
