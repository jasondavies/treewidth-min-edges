"""Finite inverse coverage for the 23-vertex, 42-edge cubic-neighbor cap.

The earlier complete 36-edge family is an explicit classification premise.
No graph is removed because an order proposer failed to find an order.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path

from marked_residue_common import decode_graph6

FAMILY_SHA256 = '0f62f3d14d543515b12567c1d650d290a9a5369ab9931220e5d398a9d3999214'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_graph(graph):
    n = len(graph)
    require(1 <= n <= 23, 'Graph order outside 1..23')
    require(all(type(row) is int and 0 <= row < 1 << n for row in graph),
            'Invalid adjacency masks')
    require(all(not (row >> v & 1) for v, row in enumerate(graph)), 'Loop')
    require(all((graph[u] >> v & 1) == (graph[v] >> u & 1)
                for u in range(n) for v in range(u)), 'Asymmetric graph')


def verify_order(graph, order, width):
    """Independent set-based fill check, including the complete permutation."""
    validate_graph(graph)
    n = len(graph)
    require(type(width) is int and 0 <= width < n, 'Invalid width')
    require(isinstance(order, (list, tuple)) and len(order) == n
            and all(type(v) is int for v in order)
            and sorted(order) == list(range(n)), 'Invalid elimination permutation')
    adjacency = [{u for u in range(n) if row >> u & 1} for row in graph]
    live = set(range(n))
    for v in order:
        neighbors = adjacency[v] & live
        require(len(neighbors) <= width, 'Proposed order exceeds width bound')
        for u in neighbors:
            adjacency[u].update(neighbors - {u})
        live.remove(v)


def cubic_neighborhoods_independent(graph, cubics):
    return all(not (graph[u] & graph[v]) for v in cubics
               for u in range(len(graph)) if graph[v] >> u & 1)


def inverse_triangles(graph, triangles):
    """Replace vertex-disjoint triangles with new cubic centers."""
    n = len(graph)
    result = list(graph) + [0] * len(triangles)
    used = set()
    for i, triangle in enumerate(triangles):
        require(len(triangle) == 3 and len(set(triangle)) == 3
                and all(type(v) is int and 0 <= v < n for v in triangle),
                'Invalid inverse triangle')
        require(not used.intersection(triangle), 'Overlapping inverse triangles')
        require(all(graph[u] >> v & 1 for u, v in combinations(triangle, 2)),
                'Inverse triangle is not complete')
        used.update(triangle)
        mask = sum(1 << v for v in triangle)
        for v in triangle:
            result[v] = (result[v] & ~mask) | (1 << (n + i))
            result[n + i] |= 1 << v
    return result


def intermediate_graphs(repository, stats=None):
    """Enumerate every necessary J20 inverse; duplicates are retained."""
    if stats is None:
        stats = Counter()
    path = Path(repository) / 'sources/nine/treewidth36-family.g6'
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == FAMILY_SHA256, 'Wrong prior 36-edge family')
    for index, code in enumerate(raw.decode('ascii').splitlines()):
        graph = decode_graph6(code)
        n = len(graph)
        degrees = [row.bit_count() for row in graph]
        cubic_count = degrees.count(3)
        r = 20 - n
        require(not (r == 3 and cubic_count == 5),
                'Unexpected 17-vertex residue with five cubics')
        if r not in (1, 2) or cubic_count not in (4, 5):
            continue
        stats[f'bases_{r}'] += 1
        high = sum(1 << v for v, d in enumerate(degrees) if d == 5)
        eligible = [v for v, d in enumerate(degrees) if d >= 4]
        triangles = [t for t in combinations(eligible, 3)
                     if all(graph[u] >> v & 1 for u, v in combinations(t, 2))]
        if r == 2:
            triangles = [t for t in triangles if sum(degrees[v] == 4 for v in t) <= 1]
        masks = {t: sum(1 << v for v in t) for t in triangles}
        for selected in combinations(triangles, r):
            used = 0
            for triangle in selected:
                if used & masks[triangle]:
                    break
                used |= masks[triangle]
            else:
                if high & ~used:
                    continue
                stats[f'inverses_{r}'] += 1
                result = inverse_triangles(graph, selected)
                cubics = [v for v, row in enumerate(result) if row.bit_count() == 3]
                cmask = sum(1 << v for v in cubics)
                require(len(result) == 20 and len(cubics) == 8
                        and all(row.bit_count() in (3, 4) for row in result),
                        'Unexpected intermediate degree profile')
                if not cubic_neighborhoods_independent(result, cubics):
                    stats['cubic_triangle'] += 1
                    continue
                if r == 2:
                    if any((result[v] & cmask).bit_count() > 1 for v in cubics):
                        stats['wrong_matching_branch'] += 1
                        continue
                    if any((result[u] & result[v]).bit_count() > 1
                           for u, v in combinations(cubics, 2)):
                        stats['cubic_codegree'] += 1
                        continue
                    if any((row & cmask).bit_count() > 2 for row in result
                           if row.bit_count() == 4):
                        stats['quartic_incidence'] += 1
                        continue
                stats['intermediate_graphs'] += 1
                yield index, selected, result


def lift(graph, restored, matching):
    """Subdivide two matching edges and attach their centers to a new vertex."""
    require(len(graph) == 20, 'Expected a 20-vertex intermediate graph')
    require(len(restored) == 2 and len(set(restored)) == 2
            and all(type(v) is int and 0 <= v < 20 and graph[v].bit_count() == 3
                    for v in restored), 'Expected two distinct cubic vertices')
    require(len(matching) == 2 and all(len(edge) == 2 for edge in matching),
            'Expected two matching edges')
    endpoints = [v for edge in matching for v in edge]
    require(all(type(v) is int and 0 <= v < 20 for v in endpoints)
            and len(set(endpoints)) == 4 and not set(restored).intersection(endpoints),
            'Matching intersects itself or the restored vertices')
    require(all(graph[u] >> v & 1 for u, v in matching), 'Missing subdivided edge')
    result = list(graph) + [0, 0, sum(1 << v for v in restored)]
    for z, (u, v) in enumerate(matching, 20):
        result[u] = (result[u] & ~(1 << v)) | (1 << z)
        result[v] = (result[v] & ~(1 << u)) | (1 << z)
        result[z] = (1 << u) | (1 << v) | (1 << 22)
        result[22] |= 1 << z
    for v in restored:
        result[v] |= 1 << 22
    return result


def target_lifts(graph, stats=None, *, require_isolate=True):
    require(type(require_isolate) is bool, 'require_isolate must be a boolean')
    if stats is None:
        stats = Counter()
    cubics = [v for v, row in enumerate(graph) if row.bit_count() == 3]
    for restored in combinations(cubics, 2):
        rmask = sum(1 << v for v in restored)
        edges = [(u, v) for v in range(20) for u in range(v)
                 if graph[u] >> v & 1 and not rmask & ((1 << u) | (1 << v))]
        for matching in combinations(edges, 2):
            if len(set(matching[0] + matching[1])) != 4:
                continue
            stats['inverse_choices'] += 1
            result = lift(graph, restored, matching)
            lows = [v for v, row in enumerate(result) if row.bit_count() == 3]
            lmask = sum(1 << v for v in lows)
            require(len(lows) == 8 and all(row.bit_count() in (3, 4) for row in result)
                    and sum(row.bit_count() for row in result) == 84,
                    'Unexpected lifted degree profile')
            low_degrees = [(result[v] & lmask).bit_count() for v in lows]
            if max(low_degrees) > 2 or (require_isolate and min(low_degrees) > 0):
                stats['cubic_induced'] += 1
                continue
            if not cubic_neighborhoods_independent(result, lows):
                stats['cubic_triangle'] += 1
                continue
            if any((result[u] & result[v]).bit_count() > 1 for u, v in combinations(lows, 2)):
                stats['cubic_codegree'] += 1
                continue
            stats['target_graphs'] += 1
            yield restored, matching, result


def universal_apex(graph):
    n = len(graph)
    return [row | (1 << n) for row in graph] + [(1 << n) - 1]
