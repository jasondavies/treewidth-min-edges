"""Exact small-instance graph tools for attempts a3nm-008 through a3nm-012.

Undirected graphs use adjacency bitmasks; directed paths use adjacency lists.
These exponential reference routines are not scalable research algorithms.
"""
from collections import deque
from functools import lru_cache
from itertools import combinations, permutations, product

from posets import bits


def graph(n, edges):
    adj = [0] * n
    for u, v in edges:
        assert u != v
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return tuple(adj)


def graph_from_mask(n, mask):
    pairs = list(combinations(range(n), 2))
    return graph(n, [e for i, e in enumerate(pairs) if mask >> i & 1])


def edges(adj):
    return [(u, v) for u in range(len(adj)) for v in bits(adj[u]) if u < v]


def pathwidth(adj):
    n = len(adj)
    full = (1 << n) - 1
    dp = [0] * (full + 1)
    for subset in range(1, full + 1):
        boundary = sum(bool(adj[v] & (full ^ subset)) for v in bits(subset))
        dp[subset] = max(boundary, min(dp[subset ^ (1 << v)] for v in bits(subset)))
    return dp[full]


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


def width_by_permutations(adj, path=False):
    best = len(adj)
    for order in permutations(range(len(adj))):
        current = list(adj)
        remaining = (1 << len(adj)) - 1
        maximum = 0
        done = 0
        for v in order:
            if path:
                done |= 1 << v
                maximum = max(maximum, sum(bool(adj[x] & ~done) for x in bits(done)))
            else:
                neighbors = current[v] & remaining
                maximum = max(maximum, neighbors.bit_count())
                for x in bits(neighbors):
                    current[x] |= neighbors & ~(1 << x)
                remaining ^= 1 << v
        best = min(best, maximum)
    return best


def two_factors_off_cycle(n):
    """Every labeled simple 2-factor disjoint from the fixed cycle, exactly once."""
    allowed = [set(range(n)) - {v, (v - 1) % n, (v + 1) % n} for v in range(n)]
    degree = [0] * n
    chosen = []
    def rec(v):
        if v == n:
            if all(d == 2 for d in degree):
                yield tuple(chosen)
            return
        candidates = [w for w in sorted(allowed[v]) if w > v and degree[w] < 2]
        for neighbors in combinations(candidates, 2 - degree[v]):
            for w in neighbors:
                degree[v] += 1
                degree[w] += 1
                chosen.append((v, w))
            yield from rec(v + 1)
            for w in reversed(neighbors):
                chosen.pop()
                degree[v] -= 1
                degree[w] -= 1
    yield from rec(0)


def hamiltonian_cycles(adj):
    """Undirected Hamiltonian cycle count, fixing start=0 and dividing orientations."""
    n = len(adj)
    full = (1 << n) - 1
    @lru_cache(None)
    def count(used, last):
        if used == full:
            return int(bool(adj[last] & 1))
        return sum(count(used | (1 << v), v) for v in bits(adj[last] & ~used))
    return count(1, 0) // 2 if n >= 3 else 0


def two_switch_exists(n, chords):
    chords = {tuple(sorted(e)) for e in chords}
    for i in range(n):
        for j in range(i + 1, n):
            if len({i, (i + 1) % n, j, (j + 1) % n}) < 4:
                continue
            if tuple(sorted((i, j))) in chords and tuple(sorted(((i+1) % n, (j+1) % n))) in chords:
                return True
    return False


def distances(out, start):
    dist = [None] * len(out)
    dist[start] = 0
    queue = deque([start])
    while queue:
        u = queue.popleft()
        for v in out[u]:
            if dist[v] is None:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


def tight_graphs(out, pairs):
    reverse = [[] for _ in out]
    for u, ns in enumerate(out):
        for v in ns:
            reverse[v].append(u)
    result = []
    for s, t in pairs:
        ds, dt = distances(out, s), distances(reverse, t)
        if ds[t] is None:
            return None
        result.append(tuple(tuple(v for v in out[u] if ds[u] is not None and dt[v] is not None
                                  and ds[u] + 1 + dt[v] == ds[t]) for u in range(len(out))))
    return result


def topo(out):
    degree = [0] * len(out)
    for ns in out:
        for v in ns:
            degree[v] += 1
    queue = deque(v for v in range(len(out)) if degree[v] == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in out[u]:
            degree[v] -= 1
            if degree[v] == 0:
                queue.append(v)
    return order if len(order) == len(out) else None


def disjoint_shortest_acyclic(out, pairs):
    terminals = [v for pair in pairs for v in pair]
    assert len(set(terminals)) == len(terminals), "Distinct terminals required by this reference routine"
    tight = tight_graphs(out, pairs)
    if tight is None:
        return False
    union = [set().union(*(set(g[v]) for g in tight)) for v in range(len(out))]
    order = topo(union)
    if order is None:
        return None  # Outside the proved acyclic-union slice, not a NO answer.
    rank = {v: i for i, v in enumerate(order)}
    @lru_cache(None)
    def rec(state):
        active = [i for i, v in enumerate(state) if v != -1]
        if not active:
            return True
        i = min(active, key=lambda j: rank[state[j]])
        u = state[i]
        if u == pairs[i][1]:
            new = list(state)
            new[i] = -1
            return rec(tuple(new))
        for v in tight[i][u]:
            if v in state:
                continue
            new = list(state)
            new[i] = v
            if rec(tuple(new)):
                return True
        return False
    return rec(tuple(s for s, _ in pairs))


def brute_disjoint_shortest(out, pairs):
    tight = tight_graphs(out, pairs)
    if tight is None:
        return False
    def masks(g, u, t, used):
        if u == t:
            yield used
        for v in g[u]:
            if not used >> v & 1:
                yield from masks(g, v, t, used | (1 << v))
    paths = [list(masks(g, s, t, 1 << s)) for g, (s, t) in zip(tight, pairs)]
    return any(sum(mask.bit_count() for mask in choice) == _union(choice).bit_count()
               for choice in product(*paths))


def _union(masks):
    value = 0
    for mask in masks:
        value |= mask
    return value


def diameter_two(adj):
    full = (1 << len(adj)) - 1
    return all((adj[v] | (1 << v) | _union(adj[u] for u in bits(adj[v]))) == full
               for v in range(len(adj)))


def brute_three_colorable(adj):
    order = sorted(range(len(adj)), key=lambda v: -adj[v].bit_count())
    colors = [-1] * len(adj)
    def rec(i):
        if i == len(order):
            return True
        v = order[i]
        forbidden = {colors[u] for u in bits(adj[v])}
        for c in range(3):
            if c not in forbidden:
                colors[v] = c
                if rec(i+1):
                    return True
        colors[v] = -1
        return False
    return rec(0)


def two_list_colorable(adj, lists):
    """Reduce lists of size <=2 to 2-SAT; decide by implication reachability."""
    if any(not choices for choices in lists):
        return False
    n = len(adj)
    out = [set() for _ in range(2*n)]
    for v, choices in enumerate(lists):
        assert len(choices) <= 2
        if len(choices) == 1:
            out[2*v+1].add(2*v)
    for u, v in edges(adj):
        for a, cu in enumerate(lists[u]):
            for b, cv in enumerate(lists[v]):
                if cu == cv:
                    out[2*u+a].add(2*v+(1-b))
                    out[2*v+b].add(2*u+(1-a))
    reach = []
    for v in range(2*n):
        seen = {v}
        stack = [v]
        while stack:
            for w in out[stack.pop()]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        reach.append(seen)
    return all(not (2*v+1 in reach[2*v] and 2*v in reach[2*v+1]) for v in range(n))


def neighborhood_coloring(adj, pivot=0):
    assert diameter_two(adj)
    side = {}
    components = []
    for start in bits(adj[pivot]):
        if start in side:
            continue
        side[start] = 0
        queue = deque([start])
        comp = []
        while queue:
            u = queue.popleft()
            comp.append(u)
            for v in bits(adj[u] & adj[pivot]):
                if v in side and side[v] == side[u]:
                    return False, None
                if v not in side:
                    side[v] = 1-side[u]
                    queue.append(v)
        components.append(comp)
    for flips in product(range(2), repeat=len(components)):
        assigned = {pivot: 0}
        for comp, flip in zip(components, flips):
            for v in comp:
                assigned[v] = 1+(side[v] ^ flip)
        lists = []
        for v in range(len(adj)):
            if v in assigned:
                lists.append([assigned[v]])
            else:
                forbidden = {assigned[u] for u in bits(adj[v]) if u in assigned}
                lists.append(sorted({0,1,2}-forbidden))
        if two_list_colorable(adj, lists):
            return True, len(components)
    return False, len(components)
