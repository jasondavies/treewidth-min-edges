#!/usr/bin/env python3
"""Check exhaustive 52-edge minimal-counterexample branch certificates.

Premises: the earlier edge minima through treewidth ten, and the written
minimum-order reduction. Explicit v6 cubic-cap nodes additionally use the
H23 cubic-neighbor theorem; v7 marked-residue nodes additionally use the
marked H22 theorem and its complete nonadjacent-high lift exclusion; all
include their stated earlier-classification premises;
see proof-eleven-cubic-neighbor-cap.md. Explicit v8 nodes additionally use the no-isolate H23 strengthening.
Explicit v10 nodes use the one-degree-five H23 theorem.
No C search result is trusted.
"""
import argparse
from collections import Counter
from itertools import combinations
import json
import lzma
from pathlib import Path

from verify_profile_refutation import Interval, require
from order_edge_bounds import GLOBAL_MINIMUM, ORDER_MINIMUM

MINIMUM = GLOBAL_MINIMUM
PREMISE_NOTICE = ('Premises: earlier edge minima and the minimum-order reduction; '
    'v6 cubic-cap nodes additionally require the H23 cubic-neighbor theorem '
    '(proof-eleven-cubic-neighbor-cap.md); v7 marked-residue nodes additionally require '
    'the marked H22 characterization (proof-eleven-marked-residue.md) and its complete '
    'nonadjacent-high reconstruction exclusion (proof-eleven-exceptional-nonadjacent-pair.md), '
    'including the earlier-classification premises stated in those proofs.')
PREMISE_NOTICE += ' v10 one-high nodes additionally require proof-eleven-one-high-cubic-cap.md.'
PREMISE_NOTICE += ' v8 broad-cap nodes additionally require the no-isolate strengthening (proof-eleven-cubic-neighbor-cap-extension.md).'


class Contradiction(Exception):
    """The represented family contains no hypothetical counterexample."""


def force(known, possible, u, v):
    if v not in possible[u]:
        raise Contradiction('A required edge is forbidden.')
    known[u].add(v)
    known[v].add(u)


def forbid(known, possible, u, v):
    if v in known[u]:
        raise Contradiction('A forbidden edge is required.')
    possible[u].discard(v)
    possible[v].discard(u)


def local_contradiction(known, possible, degree):
    """Necessary monotone restrictions for a minimum-order 52-edge obstruction."""
    n = len(known)
    low = {v for v in range(n) if degree[v] == 4}
    high = set(range(n)) - low
    for v, neighbors in enumerate(known):
        triangles = [(u, w) for u, w in combinations(sorted(neighbors), 2) if w in known[u]]
        if len(triangles) > (1 if v in low else 4):
            return True
        if v in low:
            if len(neighbors & high) > 2:
                return True
            for u, w in triangles:
                if (neighbors & high) - {u, w}:
                    return True
        else:
            for u, w in combinations(sorted(neighbors & high), 2):
                if w not in possible[u]:
                    others = neighbors - {u, w}
                    if any(y in known[x] for x, y in combinations(sorted(others), 2)):
                        return True
    for u, v in combinations(range(n), 2):
        if len(known[u] & known[v] & low) > (2 if u in low and v in low else 1):
            return True
    return False


def edge_local_contradiction(known, possible, degree, u, v, triangles, low, high):
    """Test only restrictions changed by the temporarily inserted edge uv.

    The graph before insertion must satisfy local_contradiction == False.
    `triangles` contains its old per-vertex triangle counts. All known/possible
    rows remain symmetric, and uv was previously optional.
    """
    common = known[u] & known[v]
    added = len(common)
    for x in (u, v):
        if triangles[x] + added > (1 if x in low else 4):
            return True
    if any(triangles[w] + 1 > (1 if w in low else 4) for w in common):
        return True
    for x, y in ((u, v), (v, u)):
        if x in low:
            if len(known[x] & high) > 2:
                return True
            # The new high neighbor cannot belong to any old triangle at x.
            if y in high and triangles[x]:
                return True
            for w in common:
                if (known[x] & high) - {y, w}:
                    return True
    for w in common & low:
        if (known[w] & high) - {u, v}:
            return True
    # A common-low-neighbor count changes only when u or v is the new
    # common neighbor. Counts here use the graph after inserting uv.
    for x, y in ((u, v), (v, u)):
        if x in low:
            for w in known[x] - {y}:
                limit = 2 if y in low and w in low else 1
                if len(known[y] & known[w] & low) > limit:
                    return True
    # A high vertex gains a neighbor only at u/v, or gains an internal
    # neighborhood edge only when it was a common neighbor of u and v.
    for center in ({u, v} | common) & high:
        neighbors = known[center]
        for x, y in combinations(sorted(neighbors & high), 2):
            if y not in possible[x]:
                others = neighbors - {x, y}
                if any(b in known[a] for a, b in combinations(sorted(others), 2)):
                    return True
    return False


def normalise(known, possible, degree):
    """Propagate only proved necessary restrictions; never search for a completion."""
    n = len(known)
    high = {v for v in range(n) if degree[v] == 5}
    low = set(range(n)) - high
    while True:
        before = (sum(map(len, known)), sum(map(len, possible)))
        for v in range(n):
            if len(known[v]) > degree[v] or len(possible[v]) < degree[v]:
                raise Contradiction('The exact degree is impossible.')
            if len(known[v]) == degree[v]:
                for u in list(possible[v] - known[v]):
                    forbid(known, possible, u, v)
            if len(possible[v]) == degree[v]:
                for u in list(possible[v] - known[v]):
                    force(known, possible, u, v)
            if degree[v] == 4:
                for u, w in combinations(sorted(known[v] & high), 2):
                    force(known, possible, u, w)
        if local_contradiction(known, possible, degree):
            raise Contradiction('A local minimal-counterexample restriction fails.')
        triangles = [sum(w in known[u] for u, w in combinations(sorted(ns), 2))
                     for ns in known]
        for u, v in combinations(range(n), 2):
            if v in possible[u] - known[u]:
                known[u].add(v)
                known[v].add(u)
                bad = edge_local_contradiction(known, possible, degree, u, v, triangles, low, high)
                known[u].remove(v)
                known[v].remove(u)
                if bad:
                    forbid(known, possible, u, v)
                    # A newly forbidden high--high edge can violate an old
                    # high-neighborhood condition without changing known edges.
                    if u in high and v in high and local_contradiction(known, possible, degree):
                        raise Contradiction('A newly forbidden high pair violates a local restriction.')
        if before == (sum(map(len, known)), sum(map(len, possible))):
            unseen = set(range(n))
            while unseen:
                todo = {min(unseen)}
                component = set()
                while todo:
                    u = todo.pop()
                    if u not in component:
                        component.add(u)
                        todo |= known[u] - component
                unseen -= component
                if len(component) < n and all(len(known[u]) == degree[u] for u in component):
                    raise Contradiction('A saturated proper component contradicts minimum order.')
            return


def project_private_cubic_cap(known, possible, degree):
    """Explicit additional H23 classification premise; never used by normalise."""
    require(len(degree) == 25 and degree == [5] * 4 + [4] * 21,
            'Private cubic-cap rule requires the order25 degree profile.')
    high = set(range(4))
    require(all(known[v] == possible[v] and len(known[v]) == 5 for v in high),
            'High neighborhoods must be exact.')
    require(all(len(known[v] & high) <= 1 and known[v] & high == possible[v] & high
                for v in range(4, 25)), 'All low attachments must be private.')
    changes = 0
    for x, y in combinations(range(4), 2):
        if y in known[x]:
            continue
        removed = {x, y}
        remaining = set(range(25)) - removed
        residual_degree = {v: degree[v] - len(known[v] & removed) for v in remaining}
        cubics = {v for v in remaining if residual_degree[v] == 3}
        if len(cubics) != 8 or any(residual_degree[v] != 4 for v in remaining - cubics):
            continue
        cubic_high = cubics & high
        if not cubic_high or any(known[v] & cubics for v in cubic_high):
            continue
        # A private low in either deleted group has <=1 neighbor within
        # its own group (triangle bound) and <=1 in the other (codegree).
        # Cubic highs are isolated, so H[C] has max degree<=2 and an isolate.
        for v in sorted(remaining - cubics):
            certain = known[v] & cubics
            if len(certain) > 1:
                raise Contradiction('H23 cubic-neighbor cap is violated.')
            if certain:
                for u in sorted((possible[v] & cubics) - certain):
                    forbid(known, possible, u, v)
                    changes += 1
    return changes


def project_broad_cubic_cap(known, possible, degree):
    """Explicit strengthened H23 premise without an isolated-cubic requirement."""
    require(len(degree) == 25 and degree == [5] * 4 + [4] * 21,
            'Broad cubic-cap rule requires the order25 degree profile.')
    high = set(range(4))
    require(all(known[v] == possible[v] and len(known[v]) == 5 for v in high),
            'High neighborhoods must be exact.')
    require(all(len(known[v] & high) <= 2 and known[v] & high == possible[v] & high
                for v in range(4, 25)), 'Low vertices may have at most two exact high attachments.')
    changes = 0
    for x, y in combinations(range(4), 2):
        if y in known[x]:
            continue
        removed = {x, y}
        remaining = set(range(25)) - removed
        residual_degree = {v: degree[v] - len(known[v] & removed) for v in remaining}
        cubics = {v for v in remaining if residual_degree[v] == 3}
        if len(cubics) != 8 or any(residual_degree[v] != 4 for v in remaining - cubics):
            continue
        if any(len(known[v] & cubics) > 2 for v in cubics & high):
            continue
        # Private low cubics have <=1 neighbor in each deleted group.
        # A shared low cubic has no same-group neighbor (its high-parent
        # triangle uses its allowance), <=1 other-group neighbor, and
        # <=1 remaining high neighbor. High cubic degrees are exact above.
        for v in sorted(remaining - cubics):
            certain = known[v] & cubics
            if len(certain) > 1:
                raise Contradiction('H23 cubic-neighbor cap is violated.')
            if certain:
                for u in sorted((possible[v] & cubics) - certain):
                    forbid(known, possible, u, v)
                    changes += 1
    return changes


def project_one_high_cubic_cap(known, possible, degree):
    """Explicit H23 premise with one degree-five vertex."""
    require(len(degree) == 25 and degree == [5] * 4 + [4] * 21,
            'One-high cubic-cap rule requires the order25 degree profile.')
    high = set(range(4))
    require(all(known[v] == possible[v] and len(known[v]) == 5 for v in high),
            'High neighborhoods must be exact.')
    require(all(len(known[v] & high) <= 2 and known[v] & high == possible[v] & high
                for v in range(4, 25)), 'Low vertices may have at most two exact high attachments.')
    changes = 0
    for x, y in combinations(range(4), 2):
        if y in known[x]:
            continue
        removed = {x, y}
        remaining = set(range(25)) - removed
        residual_degree = {v: degree[v] - len(known[v] & removed) for v in remaining}
        cubics = {v for v in remaining if residual_degree[v] == 3}
        quartics = {v for v in remaining if residual_degree[v] == 4}
        fives = {v for v in remaining if residual_degree[v] == 5}
        if len(cubics) != 9 or len(quartics) != 13 or len(fives) != 1:
            continue
        z = next(iter(fives))
        require(z in high, 'The unique residual high vertex must have an exact row.')
        if any(len(known[v] & cubics) > 2 for v in cubics & high):
            continue
        # Private low cubics have <=1 neighbor in each deleted group.
        # A shared low cubic has no same-group neighbor (its high-parent
        # triangle uses its allowance), <=1 other-group neighbor, and
        # <=1 remaining high neighbor. High cubic degrees are exact above.
        for v in sorted(quartics & known[z]):
            certain = known[v] & cubics
            if len(certain) > 1:
                raise Contradiction('The one-high H23 cubic-neighbor cap is violated.')
            if certain:
                for u in sorted((possible[v] & cubics) - certain):
                    forbid(known, possible, u, v)
                    changes += 1
    return changes


def project_marked_residue(known, possible, degree):
    """Explicit marked-H22 theorem plus its complete nonadjacent-pair exclusion."""
    require(len(degree) == 24 and degree == [5] * 8 + [4] * 16,
            'Marked residue requires the order24 degree profile.')
    require(all(known[v] == possible[v] and len(known[v]) == 5 for v in range(8)),
            'Marked residue requires exact high neighborhoods.')
    changes = 0
    for x, y in combinations(range(8), 2):
        if y in known[x]:
            continue
        removed = {x, y}
        remaining = set(range(24)) - removed
        residual_degree = {v: degree[v] - len(known[v] & removed) for v in remaining}
        cubics = {v for v in remaining if residual_degree[v] == 3}
        if len(cubics) != 4 or any(residual_degree[v] != 4 for v in remaining - cubics):
            continue
        for size in (2, 3, 4):
            for vertices in combinations(sorted(cubics), size):
                selected = set(vertices)
                if any(possible[v] & selected for v in selected):
                    continue
                if any(len(known[v] & selected) != 1
                       or known[v] & selected != possible[v] & selected
                       for v in cubics - selected):
                    continue
                # f(9)=42 forbids triangles and 4-cycles on the four cubics.
                # A cubic star has no such independent dominating set, so the
                # cubic graph is a proper K2,2 subgraph as the mark requires.
                for v in sorted(remaining - cubics):
                    certain = known[v] & selected
                    if len(certain) > 1:
                        raise Contradiction('The marked H22 residue would force an excluded lift.')
                    if certain:
                        for u in sorted((possible[v] & selected) - certain):
                            forbid(known, possible, u, v)
                            changes += 1
    return changes


class Bounds(Interval):
    @classmethod
    def from_family(cls, known, possible, degree):
        state = cls.__new__(cls)
        state.known = [row.copy() for row in known]
        state.possible = [row.copy() for row in possible]
        state.lower = list(degree)
        state.upper = list(degree)
        state.remaining = set(range(len(known)))
        state.edges, state.width = 52, 11
        return state

    def tighten(self):
        while True:
            if self.edges < ORDER_MINIMUM[self.width][len(self.remaining)] or len(self.remaining) <= self.width:
                raise Contradiction('Too few edges or vertices for the maintained treewidth.')
            before = (sum(map(len, self.known)), sum(map(len, self.possible)),
                      tuple(self.lower), tuple(self.upper), self.edges)
            cap = self.edges - ORDER_MINIMUM[self.width - 1][len(self.remaining) - 1]
            for v in sorted(self.remaining):
                self.lower[v] = max(self.lower[v], len(self.known[v]))
                self.upper[v] = min(self.upper[v], len(self.possible[v]), cap)
                if self.lower[v] > self.upper[v]:
                    raise Contradiction('A degree bound is inconsistent.')
                if self.width >= 4 and self.edges == MINIMUM[self.width]:
                    if self.upper[v] <= 2:
                        if self.lower[v] > 0:
                            raise Contradiction('A nonisolated vertex would lose an edge on elimination.')
                        self.upper[v] = 0
                    elif self.upper[v] == 3:
                        if self.lower[v] > 0:
                            self.lower[v] = 3
                        for u, w in combinations(sorted(self.known[v]), 2):
                            forbid(self.known, self.possible, u, w)
                        for u in list(self.possible[v] - self.known[v]):
                            if self.known[u] & self.known[v]:
                                forbid(self.known, self.possible, u, v)
                if self.upper[v] == len(self.known[v]):
                    for u in list(self.possible[v] - self.known[v]):
                        forbid(self.known, self.possible, u, v)
                if self.lower[v] == len(self.possible[v]):
                    for u in list(self.possible[v] - self.known[v]):
                        force(self.known, self.possible, u, v)
            self.edges = min(self.edges, sum(self.upper[v] for v in self.remaining) // 2)
            # At the global edge minimum cubic neighborhoods are independent.
            # Two cubics cannot share two neighbors: eliminate the first,
            # then the second loses an edge, violating the same edge minimum.
            if self.width >= 4 and self.edges == MINIMUM[self.width]:
                cubics = {v for v in self.remaining if self.lower[v] == self.upper[v] == 3}
                for u, v in combinations(sorted(cubics), 2):
                    common = self.known[u] & self.known[v]
                    if len(common) > 1:
                        raise Contradiction('Two cubics have two common neighbors at the edge minimum.')
                    if common:
                        for w in list(self.known[u] - common - {v}):
                            forbid(self.known, self.possible, v, w)
                        for w in list(self.known[v] - common - {u}):
                            forbid(self.known, self.possible, u, w)
                # Delete v, then suppress its cubic neighbors. Their other
                # neighbor pairs are disjoint and nonadjacent, so each
                # suppression loses one edge. Thus deg(v)+t <= E-f(k-1).
                cap = self.edges - MINIMUM[self.width - 1]
                for v in sorted(self.remaining):
                    t = len(self.known[v] & cubics)
                    self.upper[v] = min(self.upper[v], cap - t)
                    if self.lower[v] > self.upper[v]:
                        raise Contradiction('Degree plus cubic neighbors exceeds the deletion budget.')
                    if self.lower[v] + t == cap:
                        for w in list((self.possible[v] - self.known[v]) & cubics):
                            forbid(self.known, self.possible, v, w)
                # Sum the cubic-incidence capacities. Every exact cubic has
                # three neighbors, so exactly 3|C| incidences must occur.
                capacities = {v: min(cap - self.lower[v], len(self.possible[v] & cubics))
                              for v in self.remaining}
                total = sum(capacities.values())
                if total < 3 * len(cubics):
                    raise Contradiction('Insufficient total capacity for cubic incidences.')
                if total == 3 * len(cubics):
                    for v in sorted(self.remaining):
                        if capacities[v] == len(self.possible[v] & cubics):
                            for w in list((self.possible[v] - self.known[v]) & cubics):
                                force(self.known, self.possible, v, w)
            if sum(self.lower[v] for v in self.remaining) > 2 * self.edges:
                raise Contradiction('The lower degree sum exceeds the edge upper bound.')
            after = (sum(map(len, self.known)), sum(map(len, self.possible)),
                     tuple(self.lower), tuple(self.upper), self.edges)
            if before == after:
                return


def verify_trace(known, possible, degree, trace):
    require(isinstance(trace, list) and len(trace) <= len(known), 'Invalid trace length.')
    state = Bounds.from_family(known, possible, degree)
    try:
        state.tighten()
        for step in trace:
            require(isinstance(step, list) and len(step) == 2, 'Invalid trace step.')
            state.step(*step)
            state.tighten()
    except Contradiction:
        return
    raise ValueError('The supplied trace does not derive a contradiction.')


def choices(known, possible, degree, v):
    """One representative per orbit of explicitly verified twin permutations."""
    require(type(v) is int and 0 <= v < len(known), 'Invalid branch vertex.')
    need = degree[v] - len(known[v])
    require(need > 0, 'Branch vertex is already finished.')
    groups = []
    for u in sorted(possible[v] - known[v]):
        for group in groups:
            w = group[0]
            if (degree[u] == degree[w]
                    and known[u] - {w} == known[w] - {u}
                    and possible[u] - {w} == possible[w] - {u}):
                group.append(u)
                break
        else:
            groups.append([u])
    # Enumerate the same lexicographic count vectors as the Cartesian product,
    # but omit prefixes whose remaining capacity cannot meet the exact degree.
    capacity = [0] * (len(groups) + 1)
    for i in range(len(groups) - 1, -1, -1):
        capacity[i] = capacity[i + 1] + len(groups[i])

    def count_vectors(i, left, selected):
        if left > capacity[i]:
            return
        if i == len(groups):
            if left == 0:
                yield selected
            return
        for count in range(min(left, len(groups[i])) + 1):
            yield from count_vectors(i + 1, left - count, selected + groups[i][:count])

    yield from count_vectors(0, need, [])


def verify_reference(known, possible, degree, closed, reference, permutation):
    require(type(reference) is int and reference >= 0 and reference in closed,
            'Reference is not an earlier closed node.')
    n = len(known)
    require(isinstance(permutation, list) and all(type(v) is int for v in permutation)
            and sorted(permutation) == list(range(n)), 'Invalid vertex permutation.')
    target_known, target_possible = closed[reference]
    for u in range(n):
        v = permutation[u]
        require(degree[u] == degree[v], 'Permutation changes a degree class.')
        require(sum(1 << permutation[w] for w in known[u]) == target_known[v],
                'Reference does not preserve certain edges.')
        require(not sum(1 << permutation[w] for w in possible[u]) & ~target_possible[v],
                'Reference expands the certified possible edges.')


def project_neighborhood(known, possible, degree, vertex):
    """Project every feasible internal pattern of a full degree-five neighborhood.

    Each optional internal pair is fixed present or absent. No outside pair is
    guessed, and a case is discarded only by exact-degree infeasibility or
    local_contradiction. The return value describes the unanimous deductions;
    Contradiction means every one of the exhaustive cases was discarded.
    """
    require(type(vertex) is int and 0 <= vertex < len(known), 'Invalid center.')
    require(degree[vertex] == 5 and len(known[vertex]) == 5,
            'Neighborhood projection requires a full degree-five neighborhood.')
    pairs = [(u, v) for u, v in combinations(sorted(known[vertex]), 2)
             if v in possible[u] and v not in known[u]]
    intersection = (1 << len(pairs)) - 1
    union = survivors = 0
    for pattern in range(1 << len(pairs)):
        a, b = [row.copy() for row in known], [row.copy() for row in possible]
        for index, (u, v) in enumerate(pairs):
            if pattern >> index & 1:
                a[u].add(v)
                a[v].add(u)
            else:
                b[u].remove(v)
                b[v].remove(u)
        if any(len(a[u]) > degree[u] or len(b[u]) < degree[u] for u in range(len(a))):
            continue
        if local_contradiction(a, b, degree):
            continue
        survivors += 1
        intersection &= pattern
        union |= pattern
    if not survivors:
        raise Contradiction('Every internal neighborhood pattern is impossible.')
    forced = forbidden = 0
    for index, (u, v) in enumerate(pairs):
        if intersection >> index & 1:
            force(known, possible, u, v)
            forced += 1
        elif not union >> index & 1:
            forbid(known, possible, u, v)
            forbidden += 1
    return {'patterns': 1 << len(pairs), 'survivors': survivors,
            'forced': forced, 'forbidden': forbidden}


class ProgramMismatch(ValueError):
    """A converter's candidate program differs from its expected trace."""

    def __init__(self, step):
        super().__init__('Program differs from the expected trace.')
        self.step = step


def validate_program(n, policy, first, switch):
    require(type(policy) is int and policy in (0, 1, 2), 'Invalid program policy.')
    require(type(first) is int and 0 <= first < (9 if policy == 2 else n),
            'Invalid first program choice.')
    require(type(switch) is int and (switch == -1 or 1 <= switch < n),
            'Invalid program switch point.')
    require(policy != 2 or switch == -1, 'Pure elimination cannot switch.')


def run_program(known, possible, degree, policy, first, switch=-1, expected=None):
    """Execute one supplied deterministic program of at most n operations.

    Every operation uses the ordinary checked interval rules. No alternative
    policy is tried. `expected` is only used by the untrusted converter to
    reject mismatched proposals; verification leaves it unset.
    """
    n = len(known)
    validate_program(n, policy, first, switch)
    state = Bounds.from_family(known, possible, degree)
    trace = []
    try:
        for step in range(n + 1):
            state.tighten()
            if step == n:
                break
            if policy < 2 and step == 0:
                operation, vertex = 'delete', first
            elif policy == 2 or (switch >= 0 and step >= switch):
                trial = first if policy == 2 else 0
                relative = step if policy == 2 else step - switch
                skip = (trial if relative == 0 and trial < 5 else
                        trial - 4 if relative == 1 and trial >= 5 else 0)
                available = sorted((v for v in state.remaining if state.upper[v] < state.width),
                                   key=lambda v: (len(state.possible[v]), state.upper[v], v))
                require(skip < len(available), 'No eligible program elimination.')
                operation, vertex = 'eliminate', available[skip]
            else:
                available = [v for v in sorted(state.remaining)
                             if state.upper[v] < state.width and (policy or state.upper[v] <= 3)]
                if available:
                    vertex = (min(available, key=lambda v: (len(state.possible[v]), state.upper[v], v))
                              if policy else available[0])
                    operation = 'eliminate'
                else:
                    require(state.width > 1 and state.remaining, 'No eligible program deletion.')
                    vertex = max(state.remaining, key=lambda v: (len(state.known[v]), -v))
                    require(state.known[vertex], 'Program deletion would make no progress.')
                    operation = 'delete'
            chosen = [operation, vertex]
            if expected is not None and (step >= len(expected) or chosen != expected[step]):
                raise ProgramMismatch(step)
            state.step(operation, vertex)
            trace.append(chosen)
    except Contradiction:
        return trace
    raise ValueError('The supplied program does not derive a contradiction.')


def json_events(proof, version):
    pending = [proof]
    while pending:
        node = pending.pop()
        if not isinstance(node, list) or not node:
            raise ValueError('Invalid proof node.')
        if node[0] == 'x' and len(node) == 1:
            yield node
        elif node[0] == 'r' and len(node) == 2:
            yield node
        elif node[0] == 'b' and len(node) == 3 and isinstance(node[2], list):
            yield ['b', node[1], len(node[2])]
            pending.extend(reversed(node[2]))
        elif node[0] == 's' and len(node) == 3:
            require(version >= 2, 'Reference requires v2 or later format.')
            if type(node[1]) is not int or node[1] < 0:
                raise ValueError('Invalid reference node.')
            yield node
        elif node[0] == 'n' and version >= 3 and len(node) in (2, 3):
            yield ['n', node[1], len(node) - 2]
            if len(node) == 3:
                pending.append(node[2])
        elif node[0] == 'u' and version >= 10 and len(node) in (1, 2):
            yield ['u', len(node) - 1]
            if len(node) == 2:
                pending.append(node[1])
        elif node[0] == 'd' and version >= 8 and len(node) in (1, 2):
            yield ['d', len(node) - 1]
            if len(node) == 2:
                pending.append(node[1])
        elif node[0] == 'm' and version >= 7 and len(node) in (1, 2):
            yield ['m', len(node) - 1]
            if len(node) == 2:
                pending.append(node[1])
        elif node[0] == 'c' and version >= 6 and len(node) in (1, 2):
            yield ['c', len(node) - 1]
            if len(node) == 2:
                pending.append(node[1])
        elif node[0] == 'e' and (version == 4 or version >= 6) and len(node) == 5:
            yield ['e', node[1], node[2]]
            pending.append(node[4])
            pending.append(node[3])
        elif node[0] == 'g' and version >= 3 and len(node) == 5:
            require(type(node[1]) is int and node[1] in (0, 1), 'Invalid program mode.')
            yield node
        else:
            raise ValueError('Invalid proof node.')


def verify_events(events, version, prefix, needed, expected_prefix=None):
    """Shared verifier traversal; events contain branch counts, not children."""
    if expected_prefix is not None:
        require(prefix == expected_prefix, 'Wrong root profile.')
    root = Interval(prefix)
    degree = root.upper
    stats = {'branches': 0, 'local_leaves': 0, 'trace_leaves': 0}
    closed = {}
    closed_count = 0
    if version >= 2:
        stats['references'] = 0
    if version >= 3:
        stats.update(neighborhood_projections=0, neighborhood_leaves=0,
                     program_leaves=0, program_operations=0)
    if (version == 4 or version >= 6):
        stats['edge_splits'] = 0
    if version >= 6:
        stats.update(cubic_cap_projections=0, cubic_cap_leaves=0)
    if version >= 7:
        stats.update(marked_projections=0, marked_leaves=0)
    if version >= 8:
        stats.update(broad_cap_projections=0, broad_cap_leaves=0)
    if version >= 10:
        stats.update(one_high_cap_projections=0, one_high_cap_leaves=0)
    end = object()

    def register(known, possible):
        nonlocal closed_count
        if version >= 2:
            if needed[closed_count]:
                closed[closed_count] = (
                    tuple(sum(1 << v for v in row) for row in known),
                    tuple(sum(1 << v for v in row) for row in possible))
            closed_count += 1

    def visit(known, possible):
        proof = next(events, end)
        require(proof is not end, 'Truncated proof events.')
        # Unlike an explicit trace, a deterministic program can select other
        # vertices after normalization. Raw mode always uses the incoming
        # family, including at a node that later references need to retain.
        if proof[0] == 'g' and proof[1] == 0:
            require(version >= 3, 'Program leaves require v3 or later format.')
            trace = run_program(known, possible, degree, *proof[2:])
            if needed[closed_count]:
                try:
                    normalise(known, possible, degree)
                except Contradiction:
                    pass  # The raw program already proved the family empty.
            stats['program_leaves'] += 1
            stats['program_operations'] += len(trace)
            register(known, possible)
            return
        # A supplied trace can refute the larger incoming family directly.
        # Normalize first whenever a later reference needs this node's state;
        # otherwise a successful trace makes local propagation unnecessary.
        if proof[0] == 'r' and not needed[closed_count]:
            try:
                verify_trace(known, possible, degree, proof[1])
            except ValueError:
                pass
            else:
                stats['trace_leaves'] += 1
                register(known, possible)
                return
        try:
            normalise(known, possible, degree)
        except Contradiction:
            require(proof == ['x'], 'Expected a local contradiction leaf.')
            stats['local_leaves'] += 1
            register(known, possible)
            return
        if proof[0] == 'r':
            verify_trace(known, possible, degree, proof[1])
            stats['trace_leaves'] += 1
        elif proof[0] == 'g':
            require(version >= 3 and proof[1] == 1, 'Invalid normalized program leaf.')
            trace = run_program(known, possible, degree, *proof[2:])
            stats['program_leaves'] += 1
            stats['program_operations'] += len(trace)
        elif proof[0] == 'n':
            require(version >= 3, 'Neighborhood projections require v3 or later format.')
            vertex, child_count = proof[1:]
            require(type(child_count) is int and child_count in (0, 1),
                    'Invalid neighborhood child count.')
            a, b = [row.copy() for row in known], [row.copy() for row in possible]
            try:
                projected = project_neighborhood(a, b, degree, vertex)
            except Contradiction:
                require(child_count == 0, 'Expected a terminal neighborhood refutation.')
                stats['neighborhood_leaves'] += 1
            else:
                require(child_count == 1, 'Neighborhood patterns do not refute this family.')
                require(projected['forced'] + projected['forbidden'] > 0,
                        'Neighborhood projection makes no change.')
                stats['neighborhood_projections'] += 1
                visit(a, b)
        elif proof[0] == 'm':
            require(version >= 7 and len(proof) == 2, 'Invalid marked-residue node.')
            child_count = proof[1]
            require(type(child_count) is int and child_count in (0, 1), 'Invalid marked-residue arity.')
            a, b = [row.copy() for row in known], [row.copy() for row in possible]
            try:
                changed = project_marked_residue(a, b, degree)
            except Contradiction:
                require(child_count == 0, 'Expected terminal marked-residue refutation.')
                stats['marked_leaves'] += 1
            else:
                require(child_count == 1 and changed > 0, 'Marked-residue projection makes no change.')
                stats['marked_projections'] += 1
                visit(a, b)
        elif proof[0] == 'u':
            require(version >= 10 and len(proof) == 2, 'Invalid one-high cubic-cap node.')
            child_count = proof[1]
            require(type(child_count) is int and child_count in (0, 1), 'Invalid one-high cubic-cap arity.')
            a, b = [row.copy() for row in known], [row.copy() for row in possible]
            try:
                changed = project_one_high_cubic_cap(a, b, degree)
            except Contradiction:
                require(child_count == 0, 'Expected terminal one-high cubic-cap refutation.')
                stats['one_high_cap_leaves'] += 1
            else:
                require(child_count == 1 and changed > 0, 'Cubic-cap projection makes no change.')
                stats['one_high_cap_projections'] += 1
                visit(a, b)
        elif proof[0] == 'd':
            require(version >= 8 and len(proof) == 2, 'Invalid broad cubic-cap node.')
            child_count = proof[1]
            require(type(child_count) is int and child_count in (0, 1), 'Invalid broad cubic-cap arity.')
            a, b = [row.copy() for row in known], [row.copy() for row in possible]
            try:
                changed = project_broad_cubic_cap(a, b, degree)
            except Contradiction:
                require(child_count == 0, 'Expected terminal broad cubic-cap refutation.')
                stats['broad_cap_leaves'] += 1
            else:
                require(child_count == 1 and changed > 0, 'Cubic-cap projection makes no change.')
                stats['broad_cap_projections'] += 1
                visit(a, b)
        elif proof[0] == 'c':
            require(version >= 6 and len(proof) == 2, 'Invalid cubic-cap node.')
            child_count = proof[1]
            require(type(child_count) is int and child_count in (0, 1), 'Invalid cubic-cap arity.')
            a, b = [row.copy() for row in known], [row.copy() for row in possible]
            try:
                changed = project_private_cubic_cap(a, b, degree)
            except Contradiction:
                require(child_count == 0, 'Expected terminal cubic-cap refutation.')
                stats['cubic_cap_leaves'] += 1
            else:
                require(child_count == 1 and changed > 0, 'Cubic-cap projection makes no change.')
                stats['cubic_cap_projections'] += 1
                visit(a, b)
        elif proof[0] == 'e':
            require((version == 4 or version >= 6) and len(proof) == 3, 'Invalid edge split.')
            u, v = proof[1:]
            require(type(u) is int and type(v) is int and 0 <= u < v < len(degree),
                    'Invalid edge split endpoints.')
            require(v in possible[u] and v not in known[u], 'Edge split requires an optional edge.')
            stats['edge_splits'] += 1
            a, b = [row.copy() for row in known], [row.copy() for row in possible]
            forbid(a, b, u, v)
            visit(a, b)
            a, b = [row.copy() for row in known], [row.copy() for row in possible]
            force(a, b, u, v)
            visit(a, b)
        elif proof[0] == 's':
            require(version >= 2, 'Reference requires v2 or later format.')
            reference, permutation = proof[1:]
            verify_reference(known, possible, degree, closed, reference, permutation)
            needed[reference] -= 1
            if not needed[reference]:
                del closed[reference]
            stats['references'] += 1
        else:
            require(proof[0] == 'b', 'Invalid branch node.')
            vertex, count = proof[1:]
            options = list(choices(known, possible, degree, vertex))
            require(count == len(options), 'Incomplete branch coverage.')
            stats['branches'] += 1
            for selected in options:
                a = [row.copy() for row in known]
                b = [row.copy() for row in possible]
                for u in list(b[vertex] - a[vertex]):
                    if u in selected:
                        force(a, b, u, vertex)
                    else:
                        forbid(a, b, u, vertex)
                visit(a, b)
        register(known, possible)

    visit(root.known, root.possible)
    require(next(events, end) is end, 'Trailing proof events.')
    return stats


def verify_certificate(certificate, expected_prefix=None):
    """Retain the existing object API through an adapter to the same events."""
    from branch_certificate_binary import format_version
    version = format_version(certificate.get('format'))
    require(certificate.get('scope') == 'minimum-order-counterexample', 'Wrong proof scope.')
    proof = certificate['proof']
    needed = Counter()
    if version >= 2:
        needed.update(node[1] for node in json_events(proof, version)
                      if node[0] == 's')
    return verify_events(json_events(proof, version), version, certificate['prefix'],
                         needed, expected_prefix)


def verify_file(path, expected_prefix=None):
    """Check JSON or streaming binary data, optionally compressed with xz."""
    from branch_certificate_binary import MAGIC, verify_stream
    path = Path(path)
    opener = lzma.open if path.suffix == '.xz' else open
    with opener(path, 'rb') as stream:
        binary = stream.read(len(MAGIC)) == MAGIC
        stream.seek(0)
        if binary:
            return verify_stream(stream, expected_prefix)
        return verify_certificate(json.load(stream), expected_prefix)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path)
    parser.add_argument('--prefix', type=Path)
    args = parser.parse_args()
    expected = list(map(int, args.prefix.read_text().split())) if args.prefix else None
    stats = verify_file(args.certificate, expected)
    print(f'PASS: complete minimal-counterexample exclusion for the supplied profile: {stats}')
    print(PREMISE_NOTICE)
    print('This is one profile, not the full 52-edge exclusion.')


if __name__ == '__main__':
    main()
